---
name: incident-trace
description: >-
  Trace a reported production incident end-to-end through backend services
  using Grafana/Synapse Loki logs. This skill should be used when the user
  reports a missing, empty, or wrong output for a specific session ("no
  transcript", "zero words", "dropped messages", "missing events", "silent
  recording"), when they ask to look into a Slack thread or permalink about
  an incident, when they hand over an interaction/session/recording/user id
  with a time window and ask to debug or look into it, when they ask which
  service is responsible for a failure or whether a component ever received
  or processed something, and when they need a session timeline with
  evidence, reproduction queries, and remaining unknowns.
---

# Incident tracing from Loki logs

Trace a user-reported failure forward through the service stack, using only
log evidence, until the first stage whose expected behavior is missing. The
deliverable is a verdict with per-stage evidence, explicitly separating what
was verified from what was inferred, plus reproduction queries and the
minimal set of artifacts that would settle whatever remains unknown.

Mental model: every pipeline hop is a **claim** with an evidence class —
VERIFIED (explicit log or count evidence), INFERRED (deduced, no direct
line), UNKNOWN (undecidable with current access). Tag every claim in the
report. An investigation is done when each stage claim has a class, not
when a story sounds plausible.

Core discipline:

- Trace every stage by **its own receipt or completion logs**, never by
  absence-of-errors or by inference from the previous stage's logs.
- Absence of a log line is only evidence if the line is emitted
  unconditionally on occurrence (verified in source, on the deployed
  version). Otherwise absence proves nothing. See Step 5.
- Some log lines in the same service carry identifiers and some do not.
  Never attribute an id-less line by plausible timing alone when adjacency
  or uniqueness proofs are available. See Step 5.

## Step 1: Fix the inputs and detect access

Collect what is already known before querying:

| Input | Default when missing |
|---|---|
| Incident identifiers (interaction/session/recording/user/job id) | Search session context first (shared links, pasted ids); if still missing, ask the user for one concrete id + approximate time; never sweep by time alone on the first pass |
| Time window | Derive from id-bearing logs once found; until then use the reported time ±2 hours |
| Tenant / namespace label | Look up in recent session history or memory before asking; ask only if undecidable |
| Reported anomaly | One sentence: "expected X, got Y at/around T" |

Detect log access: check whether the synapse MCP server exposes a Loki
query tool and a label/list tool in this session's tool catalog (OpenCode
code mode: `search("query_loki")`, `search("loki")`). If synapse is absent
or the tenant's cluster has no datasource listed, stop and tell the user
what is missing — do not improvise a substitute log source for modelling
the flow before the workflow's first queries.

Note compute-access boundaries now, for the report: kubeconfig cluster
coverage vs the incident's tenants, whether service repos are checked out
locally (needed for Step 5), and standing rules such as never posting
findings externally without explicit user approval.

## Step 2: Discover streams, never assume them

1. List the `service_name` values under the tenant's namespace label
   (`k8s_namespace_name` or equivalent). Never carry over a service list
   or topic names from another session — listing is cheap and caches your
   assumptions against drift and renames.
2. Confirm which Loki datasource uid serves this tenant's cluster.
3. A missing expected service in the list is already a finding (deployment
   absent — a real cause of "nothing happened").

Then build the stage map for THIS incident from the observed services plus
the repos: each repo's pipelines/config/stores name its inputs, outputs,
consumers, and upstream services. The purpose of the map is to know whose
logs are receipt evidence for each hop; filling it in per-incident from
observed data is the discipline — not a memorized topology.

## Step 3: Sweep by identifier, bounded

Query the identifier (most-unique id available) per service, in a bounded
window with a limit high enough to cover peak traffic:

```logql
{k8s_namespace_name="<tenant-namespace>", service_name="<svc>"} |= "<id>"
```

- Bound by time — unbounded or time-only raw scans on busy production
  streams can overload the query path (serialization rules: "Query load
  discipline" in the discipline reference).
- Absence is not zero-proof (Step 5 gate before any "never reached this
  service" claim).
- If an id should be on every message but appears nowhere, trace it via
  upstream relations and timestamp windows rather than declaring the flow
  broken.
- Some flows carry the id in metadata only, not in message text. If the
  first sweep shows nothing for a plausible service, retry with the
  bounded-window metadata search before concluding.

Record per service: first/last line, hit count, distinct event kinds.
These become the receipt table of Step 4.

## Step 4: Per-hop receipts and verification

For each hop, locate the lines (or record counts) that serve as receipt
or completion evidence, and check:

| Check | Method |
|---|---|
| Received the input at all? | The service's own receipt log line, per chunk/message/event |
| Count complete? | Count receipt lines; compare to expected count from line cadence, topic batching, or the upstream's own totals |
| Bytes/durations accounted? | Compare accumulated totals (e.g. received-seconds) between adjacent services and against ground truth (upstream metering or the client's own artifact) |
| Processing executed? | The service's own processing-start/completion marker — never assumed from another service |
| Output delivered? | Its own publish/send line, and the downstream service's receipt line |

Deliverable: the stage table (stage / expected receipt / observed: count,
total, first-last times / verdict class). Read source for any marker you
cannot find, and confirm it fires per-occurrence (not once per session).

When a hop's upstream stream looks healthy but its input processed
empty or not at all, the next target is the hop's internal decision
logic: did the input carry something the transform would ignore (silence,
wrong format/channel, wrong route)? That distinguishes "upstream data
problem" from "this stage failed to act".

## Step 5: The negative-evidence gate

Claims of the form "X never received/processed/happened" must pass:

1. **Unconditional-logger test.** Find the code path's logger. If it logs
   every occurrence unconditionally, absence is proof. If it is
   conditional (some only log batches received via one path, or only when
   errors fire), absence proves nothing.
2. **Deployment-version-vs-local check.** Verify the deployment's version
   against the checked-out repo (startup logs often report image tags;
   anchor line numbers or compare release notes). Log formats shift
   between versions; a local main-branch logger may not exist in the
   deployment, or vice versa.
3. **Id-less line attribution.** When a decisive line lacks the session or
   interaction id, attribute by at least one and prefer more of:
   (a) adjacency sandwich — the line sits within milliseconds between two
   owning-session lines from the same worker (e.g. Received → event →
   Sending), (b) start-instant uniqueness — enumerate every session that
   began in a ±1s window and show only one candidate, (c) a timestamp
   fingerprint derived from the tracker's state machine (e.g. a fixed
   event timing proves the session had received exactly N seconds of
   audio at that moment). State which methods were used.
4. **Tool flake discipline.** Tight (sub-second) query windows can return
   empty even when matching lines exist, and window boundaries can be
   silently adjusted by the wrapper. Re-run surprising empties with wider
   windows and verify before concluding absence.
5. **Anchored patterns.** Anchor keyword matches to a boundary unique to
   the real format: plain `"0 words"` also substring-matches `"260
   words"`; prefer `"s audio, 0 words,"`-style anchors with the delimiters
   that exist in the actual format.
6. **Word-order drift between services.** Adjacent services in the same
   project may emit the same fact with different word orders (e.g.
   "Received 0.30s audio of shape ..." vs "Received audio of shape (1,
   4800) for 0.30s ..."). Search per-service exact patterns, or broad
   common stems (`|~ "Received"`) then filter.

## Step 6: Report

Numbered sections, no emojis, every claim tagged with its evidence class.

```markdown
# <Anomaly title>

**Session:** <ids> — **time:** <range> — **tenant/namespace:** <name>
**Reported:** <one-sentence claim>

## Verdict

<2-4 sentences: which stage claim chain breaks, what that implies>

## Stage evidence

| Stage | Receipt checked | Observed | Class |
|---|---|---|---|
| ... | ... | ... | VERIFIED / INFERRED / UNKNOWN |

## What was verified

- <each "verified" row with its method>

## Unknowns and how to settle them

- <artifact / probe / access required>

## Reproduction queries

<logql blocks>
```

If a stage is UNKNOWN and settling it requires prod-cluster access (blob
retrieval, raw topic consumption, metric dashboards), say so explicitly as
the next action for someone with that access — a clean boundary is better
than a hand-waved verdict.

---

## Reference files

- `references/query-discipline.md` — concrete recipes: stream discovery,
  receipt-pattern counting, quantity-parity math, id-less attribution
  procedures, wrapper-flake handling, and rate/load discipline.
- `references/case-example.md` — worked end-to-end example: showing every
  check above performed on one real incident.
