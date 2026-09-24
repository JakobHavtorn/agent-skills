---
name: speechrec-sprint-goals
description: >-
  Draft the sprint goals for the Speech Recognition (SR) team's upcoming
  Linear cycle by reviewing the outgoing cycle's goals and ticket status in
  Linear plus the last two weeks of relevant Slack discussion. This skill
  should be used when the user wants to fill in, draft, or update the
  "Goals" for a new cycle entry on the Team Speech Rec Sprint Planning
  Notion page, wants help preparing for cycle/sprint planning, asks "what
  should our goals be for [cycle name]", or references drafting sprint goals
  biweekly / every two weeks / for the next cycle. Always draft the goals
  for the user to review — never write them into Notion unless the user
  explicitly asks you to update the page.
allowed-tools: Bash(date:*) Read
---

## What this produces

A numbered list of sprint goals for the upcoming SR cycle, written in the same lean, factual style the team already uses on the Sprint Planning page: a bold title line per goal, followed by at most one or two sentences of concrete status (ticket IDs, what shipped vs. what's pending, target dates) — no commentary, no hedging, no "this might be worth considering" framing. If there's nothing concrete to report yet for a goal, leave it as a title with no body rather than inventing filler.

Return the drafted list in the conversation for the user to review. Do not write it into Notion unless they explicitly ask you to — treat this as a draft they'll edit (they often will, e.g. cutting explanatory commentary down to bare facts) before it goes on the page.

## Why this workflow

Sprint goals for the next cycle are really a synthesis of three things that don't live in one place: what the previous cycle's plan said it would do (Notion), what actually happened to the tickets underlying that plan (Linear), and what the team has been discussing, deciding, and hitting friction on in the last couple weeks (Slack) — including any informal "goals for next cycle" post someone on the team may have already written up. Pulling only from Notion or only from Linear misses either the intent or the ground truth; pulling only from Slack misses the structure. This skill exists to triangulate all three quickly, biweekly, at the start of each cycle.

## Defaults

| Parameter | Default | Notes |
|---|---|---|
| Slack lookback | 14 days | Compute via `date -d '14 days ago' +%s` (Linux) or `date -v-14d +%s` (macOS) |
| Linear team | Speech Recognition (ID `70db986a-d0a7-40fe-8894-132948e77ebe`) | Hardcoded — this skill is SR-only |
| Linear issue limit | 250 | Covers a full cycle's worth of issues |
| Notion query limit | 6 rows | Current + previous + 3-4 older for style reference |
| Cycle selection | Current cycle = outgoing; next after it = upcoming | Override if user names the cycle explicitly |
| Output | Draft in conversation, not written to Notion | User must explicitly ask to write it in |

## Step 1 — Detection flow

Check that all three MCP integrations are available. If any is missing, fail immediately and report the failure — all three sources are required, no degradation.

Attempt one lightweight call per source:

| Source | Test call | Pass condition |
|---|---|---|
| Notion | `notion-fetch` with `id: "self"` | Returns workspace info without error |
| Linear | `linear_list_cycles(teamId: "70db986a-d0a7-40fe-8894-132948e77ebe", type: "current")` | Returns a cycle object without error |
| Slack | `slack_search_channels` with `query: "speech-recognition"` | Returns results without error |

If any call fails, stop and return the failure template (see Output — failure).

## Step 2 — Gather all data in parallel

Fire all three data sources in parallel — dispatch a subagent per source. They have no dependencies on each other. If any source returns no data or errors, fail completely and report.

### 2a. Notion — Sprint Planning database

See `references/notion.md` for the data source URL, query, and how to interpret results.

Query the Sprint Planning data source. Identify the outgoing cycle (Goals = what team intended), upcoming cycle (check if Goals already has a draft), and 1-2 older cycles (Goals = style reference). Note the upcoming cycle's page URL for potential write-back.

**Gate:** If the query returns zero rows, fail — report "Notion Sprint Planning database returned no cycle entries."

### 2b. Linear — Cycle and ticket status

See `references/linear.md` for team ID, cycle query calls, issue listing, and how to interpret results.

Query Linear directly — no dependency on Notion for the cycle name. Get cycles (previous, current, next in parallel), then list issues for the outgoing cycle (optionally the upcoming cycle too). Group outgoing cycle's issues by `project` to map them to goal-level themes.

**Gate:** If `list_cycles` returns no cycles or `list_issues` returns zero issues, fail — report "Linear returned no cycle or issue data for the outgoing cycle."

### 2c. Slack — Last two weeks of discussion

See `references/slack.md` for channel descriptions, reading strategy, and subagent instructions.

Fire all four `slack_read_channel` calls in parallel with a 14-day lookback. For large responses, use `scripts/slice_file.py` to chunk and dispatch subagents — one per channel, run in parallel.

**Gate:** If all four channels return zero messages, fail — report "Slack returned no messages in any of the four SR channels for the last 14 days."

## Step 3 — Draft the goals

Synthesize all gathered data into a numbered list. For each goal:

1. **Bold title** — short, action-oriented (e.g. "Ship word-level timestamps to prod", "Decide on decoder keyterm biasing (GPU-PB) approach", "Initiate the vocabulary endpoint").
2. Optionally, one or two factual sentences: concrete ticket IDs hyperlinked to their Linear URL (e.g. [SR-2864](https://linear.app/corti/issue/SR-2864/return-and-store-word-level-transcripts-when-returnatomic-is-true)), what's shipped vs. pending, and a target date if one was actually stated somewhere (don't invent one). Leave this blank if you don't have anything concrete — a title-only goal is normal and expected when work is just starting. The Linear `list_issues` response includes a `url` field per issue — use it.

What to leave out, because the team consistently edits it out when it appears: recommendations ("worth flagging", "your call on whether..."), hedging about whether something belongs on the list, meta-commentary about sequencing or dependencies between goals, and any framing of an item as a "decision point" rather than just stating what the decision is and what it's waiting on. Say only what is currently true. If Slack surfaced an explicit next-cycle goal that Notion/Linear don't yet reflect, include it as a normal numbered goal — don't caveat it as new or uncertain, and don't second-guess whether it belongs.

Carry forward goals from the outgoing cycle whose underlying Linear tickets aren't Done yet, phrased as what's still needed to finish them. Add new goals surfaced from Slack discussion (especially anything explicitly framed as a next-cycle goal). Leave out anything that's fully Done in Linear and wasn't otherwise flagged as ongoing.

Cross-reference the outgoing cycle's Notion `Goals` text (what the team intended) against the Linear ticket states (what actually happened). Where they diverge — something planned but never started, or something shipped that wasn't originally a stated goal — surface it.

## Step 4 — Return the draft

### Output — success

```
1. **Outgoing cycle**: <cycle name>
2. **Upcoming cycle**: <cycle name>
3. **Draft sprint goals**:

   <numbered list — bold title per goal, optionally 1-2 factual sentences>

4. **Sources consulted**:
   - Notion: <N> cycle entries fetched, outgoing Goals reviewed, <N> older entries used as style reference
   - Linear: <N> issues in outgoing cycle, grouped into <N> project themes; <N> issues already scoped to upcoming cycle
   - Slack: 4 channels read over 14 days; <summary of key signals found>
5. **Next steps**:
   - Review and edit the draft above
   - Ask me to write it to the Notion page when you're happy with it
   - Or tell me what to change
```

### Output — failure

```
1. **Status**: failed
2. **Step failed**: <step number and name>
3. **Error**: <what went wrong — which source failed and why>
4. **What was gathered**: <brief summary of any data retrieved before the failure>
5. **Next steps**: <action to resolve — e.g. "Check that the Notion MCP integration is connected and the workspace is accessible">
```

Do not write to Notion unless the user explicitly asks. If they do, use `notion-update-page` on the upcoming cycle's page, replacing the `Goals` property with the agreed text (use `<br>` between numbered items, matching the existing property's formatting).

## Reference Files

- `references/notion.md` — Notion data source URL, query, cycle identification, style reference, and write-back instructions
- `references/linear.md` — Linear team ID, cycle query calls, issue listing, and result interpretation
- `references/slack.md` — Slack channel descriptions, reading strategy, large-response handling, and subagent extraction instructions
