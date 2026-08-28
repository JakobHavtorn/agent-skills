---
name: prioritize-tasks
description: Builds a single prioritized task list for the user by combining their active Linear tickets, tasks they've committed to in Slack, and their Slack To-do doc. Output is grouped into Now/Next/Later tiers, continuously numbered so any item can be referred to by number, and ticket-less tasks can be turned into Linear issues via the linear-ticket skill. Delivered in the terminal and as a Slack DM to the user. Use when the user asks to prioritize tasks, wants to know what to work on, or needs a task list.
---

If the user provided a lookback window in their message (e.g. "last week", "since Monday"), use it in Step 1 for the Slack search. If none was provided, default to the last 14 days.

## Overview

Produce one ranked, deduplicated list of the things the user should be working on, drawn from three sources:

1. **Linear** — the user's currently *active* tickets (statuses `Todo`, `In Progress`, `In Review`, `In QA` — never `Backlog`, `Triage`, `Done`, or `Canceled`).
2. **Slack messages** — tasks the user has committed to in messages they sent or threads they engaged in.
3. **Slack To-do doc** — the user's personal To-do canvas, which captures what they currently have conscious focus on.

Every task in the output is an enumerated line. If a Linear ticket exists for the task, the line links to it; if not, the task is listed plainly and tagged `(no ticket)` so it can later be refined into a ticket with the **`linear-ticket`** skill.

The list is grouped into **🔴 Now / 🟡 Next / 🟢 Later** tiers, ranked **commitments-and-deadlines-first** (see Step 4). It is printed in the terminal and sent to the user as a Slack DM.

---

## Step 1 — Determine the lookback window

Today's date is available as `currentDate` in the system context.

The Slack search for committed tasks needs a lookback window. If the user gave one (e.g. "last week", "since Monday"), parse it into an absolute ISO 8601 date. Otherwise default to **the last 14 days** — long enough to catch standing commitments without dredging up stale ones. Compute the `after:` date from `currentDate` (skip the weekend-counting logic; a plain 14-day calendar lookback is fine).

Linear and the To-do doc are *not* time-windowed — fetch the full current state of both.

---

## Step 2 — Resolve identity (cache for the rest of the run)

- **Linear**: `get_user` with `query: "me"` → the authenticated user's `id`, `name`, `email`.
- **Slack**: `slack_read_user_profile` with no arguments → the authenticated user's Slack ID and display handle. (The Slack MCP tool descriptions also state the current user's ID directly — either source is fine.)

Cache both. Do not re-resolve on retries.

---

## Step 3 — Gather the three sources (run all parts in parallel)

Issue 3a, 3b, and 3c in the **same tool-call batch** — they have no dependencies on each other.

### 3a. Active Linear tickets

**Filter to active states server-side — do not pull the whole assignee history.** A `list_issues assignee:"me", limit:200` call returns mostly `Done`/`Canceled` issues (an active engineer easily has 100+ closed) and reliably overflows to a file while *still* paginating. Instead, scope the fetch to the two active status *types*:

- Call `list_issues` with `assignee: "me"`, `state: "started"`, `limit: 100` → `In Progress`, `In Review`, `In QA`.
- Call `list_issues` with `assignee: "me"`, `state: "unstarted"`, `limit: 100` → `Todo`.
- Run both in the same batch and merge. This excludes `Backlog`/`Triage`/`Done`/`Canceled` at the source, so the result is small enough to read inline.

(`state` accepts a status type, name, or ID. If the type filter ever misses a status, fall back to `list_issue_statuses` for the team to confirm each status's `type`, then filter client-side to `type` ∈ {`started`, `unstarted`}.)

The fields come back under `status` (name, e.g. `In Review`), `statusType` (e.g. `started`), `priority` (a `{value, name}` object — `value` 0 None / 1 Urgent / 2 High / 3 Normal / 4 Low), `project` (a string), `dueDate`, `cycleId`, and `url`. There is no top-level `identifier` field — derive the `SR-####` identifier from the `url` (`/issue/(SR-\d+)/`). Use `url` verbatim for links; never hand-construct one.

If a fetch still overflows to a file, that file is JSON with an `issues` array; slice it with `python3 -c "import json; d=json.load(open(PATH)); ..."` rather than `Read`-ing it.

> **Heads-up on due dates:** in practice these tickets carry **no `dueDate`** and Slack rarely contains a hard calendar deadline. When that's the case, "commitments and deadlines first" (Step 4) leans on **open PRs / in-review work** and the To-do doc rather than dates — see Step 4b.

### 3b. Committed tasks from Slack messages

Search Slack for what the user sent, then mine it for commitments.

- `slack_search_public_and_private` with query `from:me after:<start-date>` (start date from Step 1), `sort: timestamp` descending, `response_format: "concise"`, `include_context: false` to keep the payload small.
- Skim the user's own messages for **commitment language** — first-person statements that imply a task the user owns. Examples: "I'll …", "I'll take care of …", "I can pick that up", "on it", "I'll have it done by …", "let me …", "I'll ship …", "I'll follow up on …", "I owe you …".
- For a message that reads like a commitment *and* sits in a thread (it's a reply, or it has replies), follow up with `slack_read_thread` on that message's `ts` to recover the surrounding ask, any **deadline**, and whether it was later resolved. Run these thread reads in parallel. Deadlines and "actually nevermind" resolutions usually live in the thread, not the standalone line.
- For each surviving commitment capture: a short task title (imperative, paraphrased from the message), any deadline mentioned, the channel/thread permalink, and the date committed. Drop anything already clearly done or rescinded.

**Overflow handling:** if the search result overflows (the MCP returns an error pointing to a file under `tool-results/mcp-claude_ai_Slack-slack_search_public_and_private-*.txt`), do **not** `Read` the file directly — run the bundled parser:

```bash
python3 ~/.config/opencode/skills/prioritize-tasks/parse_slack_overflow.py <dumped-file-path> --max-text 280
```

It strips bot noise and prints one compact line per message (time, channel, author, text) so the whole window fits in context.

### 3c. The Slack To-do doc

This is the user's personal To-do canvas — the source for what they have *conscious focus* on right now.

**The canvas is a dated daily-snapshot doc.** It is organised newest-first into per-day sections headed `## ![](slack_date:YYYY-MM-DD)`, each section being that day's to-do list (largely carried forward from the day before with items added/checked off). The full doc is large (100KB+) and mostly history. **Only the single most recent dated section is the current focus** — ignore all earlier sections.

- Call `slack_read_canvas` with `canvas_id: F0AJGTXJ1EE`. It will almost certainly overflow ("result exceeds maximum allowed tokens, output saved to `<FILE_PATH>`"). The dump is a JSON object with a `markdown_content` field (the whole canvas as markdown) and a `section_id_mapping`. **Do not `Read` the dump** — extract just the latest section with the shell:

```bash
python3 - "$FILE_PATH" <<'PY'
import json, re, sys
md = json.load(open(sys.argv[1]))["markdown_content"]
lines = md.split("\n")
hdr = [i for i, l in enumerate(lines) if "slack_date:" in l]      # date-section headers, newest first
start, end = hdr[0], (hdr[1] if len(hdr) > 1 else len(lines))     # first section = most recent
print(re.search(r"slack_date:([0-9-]+)", lines[start]).group(1))  # the section date
for l in lines[start + 1:end]:                                    # its items
    if l.strip().startswith("* ["):
        print(l.rstrip())
PY
```

- From that latest section, take only the **open** items (`* [ ]`); **skip checked ones** (`* [x]`). Indented sub-items (e.g. per-language PRs under a parent) belong to their parent task.
- Each item may already name a Linear ticket (`SR-####` / a `linear.app/...` link), a GitHub PR, or be free text. Capture the text plus any linked ticket/PR and inline note — these feed the dedup and the PR-as-commitment signal in Step 4.

---

## Step 4 — Merge, deduplicate, and prioritize

### 4a. Build the unified task set

Pool the items from 3a + 3b + 3c into one list, then **deduplicate** — the same task often appears in more than one source:

- A Slack commitment or To-do item that names or clearly maps to a Linear ticket → merge into that ticket's entry; record the extra source(s) and any deadline the Slack/canvas side added.
- Match on explicit ticket IDs (`SR-2621`), linked Linear URLs, GitHub PR links shared in both places, and clear title/topic overlap. When unsure whether two items are the same, keep them separate — a false merge hides a task; a false split is just mild redundancy.
- The result is one entry per real task, each carrying: title, Linear ticket (or none), current status, deadline (if any), the set of sources it came from, and a one-line rationale.

### 4b. Rank — commitments and deadlines first

Sort the unified set with this precedence (earlier criteria dominate):

1. **Hard deadlines / explicit promises, by urgency.** A task with an explicit deadline (a Linear `dueDate`, a date in Slack or the To-do doc) or an explicit promise to a named person ranks by how soon it's due: overdue → today/tomorrow → this week → later. Reputation-affecting promises to named people rank above un-promised work of the same urgency.
2. **Open PR / in-review work = a commitment.** In this workspace dates are almost always absent, so this is usually the *real* top signal. A task with an **open pull request**, or sitting in **`In Review` / `In QA`**, is work already done and awaiting landing — treat it as a standing commitment and rank it at the top alongside (1). Prefer getting these over the line before starting anything new.
3. **Linear priority.** Among items not separated by (1)–(2), `Urgent` > `High` > `Normal` > `Low` > none. A `High` ticket outranks a `Normal`/`Low` one even if the latter is on the To-do doc.
4. **Finish-line bias.** Tie-breaker among equal-priority items: `In Review` / `In QA` > `In Progress` > `Todo`.
5. **Conscious focus.** Final nudge: items present on the latest To-do section edge ahead of otherwise-equal items not on it.

### 4c. Bucket into tiers

- **🔴 Now** — overdue or due within ~2 days; `Urgent`; an actively-expected promise to someone; **or a committed item per 4b(2): an open PR / `In Review` / `In QA`, *especially* when it's also on the To-do doc.** The "land it / do it today" set.
- **🟡 Next** — `High` priority not yet committed; in-progress work without a PR; or items on the latest To-do section that are still early-stage. Due this week.
- **🟢 Later** — the rest of the active backlog: `Normal` / `Low` `Todo` tickets not in current focus, and un-scoped ideas.

**Keep 🟢 Later grouped, not exhaustive.** The active backlog can run to dozens of tickets; enumerating every `Low` `Todo` buries the signal. In the Later tier, collapse the long tail into a handful of summary lines — group multi-ticket epics into one line (e.g. "*`participants` decoupling epic* — 9 Low tickets SR-2529→2541"), cluster related work, and gather loose ideas under one "*Ideas to scope*" line. Each grouped line still gets one continuous number. Always enumerate 🔴 Now and 🟡 Next fully; only Later is condensed. Close with a one-line tally of total active tickets by status so nothing is hidden.

Number the items **continuously across all three tiers** (Now starts at 1 and Later keeps counting up), so the user can say "turn #4 into a ticket" unambiguously.

---

## Step 5 — Compose the output (standard markdown)

The list is delivered both to the terminal and as a Slack DM. The `slack_send_message` tool used in Step 6 renders **standard (CommonMark-style) markdown** — its own description lists `**bold**`, `_italic_`, `` `code` ``, and `[text](url)` links. Author the list once in standard markdown and use the same text for both the terminal echo and the DM.

| You want | Use (standard markdown) |
| --- | --- |
| Bold (headers + item titles) | `**bold**` |
| Italic | `_italic_` |
| Link | `[label](url)` |
| Inline code | `` `code` `` |

> This Slack workspace's `slack_send_message` takes standard markdown, **not** legacy Slack `mrkdwn`. Do **not** use `*single-asterisk*` for bold or `<url|label>` links here — those are for the older `mrkdwn` send path and will render wrong in this tool. (Verified by a live send: `**bold**` + `[text](url)` deliver correctly.)

Keep the numbered list as literal text (`1. `, `2. `…).

Template:

```
**My Prioritized Tasks — <DD Month YYYY>**

——————————————————————————

**🔴 NOW**
1. [SR-2621](linear-url) **Enable spelling corrector for `/transcripts`**
   In Review · To-do + Linear · PR open
   → On the finish line; land it.
2. **Draft Q3 capacity plan** `(no ticket)`
   To-do doc · conscious focus
   → refine into a ticket?

——————————————————————————

**🟡 NEXT**
3. [SR-2023](linear-url) **Refactor voice commands state handling**
   In Progress · Linear(High)

——————————————————————————

**🟢 LATER**
4. **`participants` decoupling epic** — 9 Low Todo tickets (SR-2529→2541)
```

Line rules:
- Line 1 of each item: the number, then — if a ticket exists — `[IDENTIFIER](url)` followed by the `**bold title**`; if no ticket, the `**bold title**` followed by `` `(no ticket)` ``.
- Line 2 (meta): `status · source(s) · deadline` — only the parts that apply. Sources read like `Linear(High)`, `Slack`, `To-do doc`, combined with `+` when a task came from several.
- Line 3 (optional `→` rationale): include only when it adds something — the commitment/PR/finish-line reason it's ranked where it is, or `→ refine into a ticket?` for ticket-less items.
- Omit any tier that has no items (don't print an empty `🔴 NOW`).
- Use the canonical Linear `url` from the MCP; never hand-build it.
- Put a `——————————————————————————` em-dash divider between tiers.

---

## Step 6 — Deliver

1. Print the composed list in the terminal so the user sees it immediately.
2. Send it as a Slack DM: call `slack_send_message` with the user's own Slack ID (from Step 2) as the `channel_id` — Slack treats a user ID as a DM channel — passing the standard-markdown text from Step 5 verbatim.
3. If the send fails, surface the error and still print the list in the terminal so nothing is lost. (`**bold**` and `[text](url)` are correct for this tool — don't "fix" them into `*…*`/`<url|label>`, which is the legacy `mrkdwn` dialect this send path does not use.)
4. After sending, confirm delivery in the terminal (include the returned permalink/timestamp if present).

---

## Step 7 — Offer to turn ticket-less tasks into Linear issues

After delivering, list the item numbers that are `(no ticket)` and offer to refine any of them into a proper Linear ticket using the **`linear-ticket`** skill.

When the user picks one (by number), invoke the `linear-ticket` skill, seeding it with that task's title, whatever context was gathered for it (the originating Slack thread, deadline, To-do note), and a sensible default status (`Todo`) and priority inferred from the tier it landed in. Don't create tickets unprompted — wait for the user to choose which ones are worth tracking.

---

## Step 8 — Follow up

Report any issues encountered (e.g. the To-do canvas couldn't be read, a Slack search overflowed, ambiguous merges you had to guess on). Note any tasks you were unsure how to rank or whether to include, so the user can correct the list.
