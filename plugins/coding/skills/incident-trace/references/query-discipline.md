# Query discipline for Loki incident tracing

Concrete recipes for the checks in SKILL.md steps 3-5. All examples assume a Grafana-backed Loki accessed through an MCP log-query tool that takes a LogQL expression, a datasource uid, and an explicit time window.

## Stream discovery

```logql
# service list under a tenant namespace (never carry across sessions)
sum by (service_name) (count_over_time({k8s_namespace_name="<ns>"} [1h]))
```

- Run this once per investigation; treat the result as the service inventory for the stage map (Step 2 of SKILL.md).
- Pick time windows relative to the incident; short, recent hours give a quick inventory; widen only if a service is expected but absent.
- Label roles: a location string from the run context (`staging-eu`, `prd-par01`) is a *cluster* value; the tenant (e.g. `base`) is the namespace value. Confirm both from any id-bearing line's labels, not from memory — a plausible-but-wrong tenant still matches some real, busy namespace and the id sweep then burns a multi-million-line scan for zero hits.
- Bound stage sweeps with the cluster label — the same service and tenant names recur across clusters — so the bounded shape is: `{k8s_cluster_name="<cluster>", service_name="<svc>"} |= "<id>"`.
- Label vocabularies differ per datasource generation: some Loki setups expose the tenant as `k8s_namespace_name`, others carry `environment` + `k8s_cluster_name` (+ `service_namespace`) and no tenant-namespace label at all. Run `list_loki_label_names` once per investigation and build the selector from labels this instance actually has — a well-formed-but-invented label selector returns exactly the same empty result as "no logs for this id", so zero hits under an unverified selector is NOT evidence of absence.

## Bounded identifier sweep

```logql
{k8s_namespace_name="<ns>", service_name="<svc>"} |= "<id>"
```

- Bound the window to the incident hour (or the local span). Serialize and back off after failures — see "Query load discipline" below.
- If identifiers appear in metadata but not message text, a text match misses; verify by inspecting one raw line's full structure (message + metadata fields) before trusting a text-only sweep.

## Anchored patterns

- Build anchors by copying the exact phrase from one real log line, then trimming only the most variable parts.
- When a number can be adjacent to keywords, put a delimiter from the format on both sides of the match (worked case in SKILL.md Step 5).
- Per-service anchoring guards against word-order drift (SKILL.md Step 5 rule 6): build each service's pattern from that service's own lines; a shared pattern silently misses the variant phrasing on the other side.

## Receipt counting and quantity parity

Volume assertions are counts, not vibes:

```logql
sum(count_over_time({k8s_namespace_name="<ns>", service_name="<svc>"} |= "<id>" |~ "<receipt-pattern>" [<window-s>]))   # instant query
```

- Expected count math: derive from the format itself (first-chunk size + n × cadence == total duration; receipt lines include start/stop markers that carry empty payloads — count them in or exclude them consistently).
- Quantity parity: compare accumulated totals between adjacent services (received-seconds at the consumer vs stored-seconds at the storage service). Equal to measurement precision means no content was lost between them; unequal means something was dropped/duplicated — that difference is your lead.
- Use per-stage counts rather than eyeballing timelines: counts turn "it looked like it all arrived" into VERIFIED.

## Metric-query envelopes (reading count/range results)

- The label set of each series sits under `labels` in the MCP log-query tool's JSON (`values` = the point list), while raw Grafana HTTP responses put it under `metric` — inspect the first series' keys before writing any parser, because a parser reading the wrong key silently yields no per-service numbers. A series whose grouping label was consumed by an outer aggregation legitimately carries empty `{}` labels.
- Each point in `values` is the count for ONE step interval, not a rate or a window total: the total is the sum of the values, or use a single bucket the width of the window when only the total matters.
- Oversized results spill to a file and the response carries only a preview — do not re-request the same query to see the rest; read the spillover file and aggregate from disk.

## Negative-evidence recipe

The gate itself (unconditional emission; deployed version known) is SKILL.md Step 5. The procedure for passing it:

1. Read S's source for the exact statement that would fire on occurrence, then enumerate its suppressors: log-level filters, sampling, exception paths that bypass the statement.
2. Reconcile the deployed version against your local checkout: startup or version logs, image tags in deployment config; beware line-number drift when matching local code to deployed behavior.
3. Only when the statement is unconditional (SKILL.md Step 5 rule 1) is absence over the id's whole lifetime proof; a conditional line's absence is proof only within the mode it fires in.
4. Convert to an explicit claim: "no occurrence, PROVEN, because logger L (v<ver>, unconditional) never fired for <id> in <window>".

Never let absence of a *different* line stand in for direct checks; if no receipt line exists for what you want to know, the correct answer is that the service did not log it — say so instead of asserting the negative.

## Id-less line attribution

When the decisive line carries no session/id (internal trackers, batch utilities, aggregated markers do this even in the same service as lines that do carry ids), attribute with at least one and preferably two of:

1. **Adjacency sandwich**: the line is emitted synchronously inside the owning session's processing call, so it sits within a few milliseconds between that session's receipt line and that session's subsequent send/publish line from the same worker. Fetch a few lines around the event line and confirm the is-sandwich.
2. **Start-instant uniqueness**: enumerate ALL sessions whose first input lands in ±1s of the event (the event's internal timestamp usually tracks elapsed audio/elapsed business time since the start). If exactly one session's start matches the event's implied start time, attribution follows.
3. **Timestamp fingerprint**: derive from the tracker's state machine what event timestamps are possible for a given session shape (for instance: an event only fires at a fixed threshold after zero prior of its own kind, or only X seconds after its kind last occurred). Restrict which sessions could produce the observed value.

When the service exposes a downstream consumer (the event is re-emitted with ids somewhere), prefer verifying there; the sandwich is the fallback when only source-side logs exist.

## Tool flake handling (query wrapper)

Symptoms observed in the field with sub-second/very tight time windows:

- Empty results although matching lines provably exist (verified by a wider-window re-run).
- Result set start earlier than the requested window start (window silently broadened).

Rules:

1. Treat tight-window empties as suspect: widen (≥1s, then ≥couple of seconds) and re-run. Only then conclude absence.
2. Verify the window edges by checking the returned first/last timestamps are inside the requested range; if not, re-run.
3. Repeated empty re-runs on the same window deserve a different query shape (session-filtered instead of all-lines, or a wider window with client-side filtering) — the flake is window-boundary-sensitive.
4. Result caps: many query tools cap results (~100). For counts use count_over_time; for lists split windows; never assume a 100-row return is the total.

## Load discipline

- Serialize production queries (1-2 at a time). Back off briefly after a 5xx rather than re-firing immediately — several back-to-back broad queries have tripped transient query-path failures.
- Prefer stream-filtered, time-bounded instant queries for counting, and range queries only where line order matters (adjacency work).
- The wider the window and the looser the filter, the more expensive: add `service_name` and as tight a time range as the question allows.
