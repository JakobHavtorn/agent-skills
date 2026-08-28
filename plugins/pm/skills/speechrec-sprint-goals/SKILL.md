---
name: speechrec-sprint-goals
description: >-
  Draft the sprint goals for the Speech Recognition (SR) team's upcoming Linear
  cycle by reviewing the outgoing cycle's goals and ticket status in Linear plus
  the last two weeks of relevant Slack discussion. Use this whenever the user
  wants to fill in, draft, or update the "Goals" for a new cycle entry on the
  Team Speech Rec Sprint Planning Notion page, wants help preparing for
  cycle/sprint planning, asks "what should our goals be for [cycle name]", or
  references drafting sprint goals biweekly / every two weeks / for the next
  cycle. Always draft the goals for the user to review — never write them into
  Notion unless the user explicitly asks you to update the page.
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

## Step 1 — Gather all data in parallel

Fire all three data sources at once. They have no dependencies on each other:

### 1a. Notion — Sprint Planning database

- Sprint Planning page: `https://www.notion.so/cortihome/Sprint-Planning-20dbef65b3ab800c85dbd99368164e20`
- Data source: `collection://20dbef65-b3ab-8076-8351-000b245ea82b` ("Team Speech Rec - Sprint Planning")
- Query (via `notion-query-data-sources`, SQL mode): `SELECT * FROM "collection://20dbef65-b3ab-8076-8351-000b245ea82b" ORDER BY "date:Dates:start" DESC LIMIT 6`
- From the results, identify:
  - The **outgoing cycle** entry (Dates range contains today, or most recently ended). Read its `Goals` property — that's what the team intended.
  - The **upcoming cycle** entry (starts right after outgoing). Check its `Goals` property — someone may have already sketched a draft. Treat existing content as a draft to verify and refresh, not overwrite.
  - Note the upcoming cycle's page URL — that's where the draft is destined if the user later asks to write it in.
  - 1-2 **older completed** cycle entries — their `Goals` property is your **style reference**. Match the exact formatting (numbered bold titles, one-line factual bodies, blank bodies where nothing concrete existed). Mirror the leanest, most recently-edited example, not your own instinct for detail level.

### 1b. Linear — Cycle and ticket status

Query Linear directly for cycle and ticket data — no dependency on Notion for the cycle name:

- Get the current cycle: `list_cycles(teamId: "70db986a-d0a7-40fe-8894-132948e77ebe", type: "current")` — returns the cycle name, number, start/end dates.
- Get the previous cycle: `list_cycles(teamId: "70db986a-d0a7-40fe-8894-132948e77ebe", type: "previous")` — this is the outgoing cycle whose tickets you need.
- Get the next cycle: `list_cycles(teamId: "70db986a-d0a7-40fe-8894-132948e77ebe", type: "next")` — this is the upcoming cycle you're drafting goals for. Note its name for matching against the Notion Sprint Planning entry.
- List the outgoing cycle's issues:
  ```
  list_issues(team: "Speech Recognition", cycle: "<previous cycle name>", limit: 250,
    fields: ["title","status","statusType","priority","assignee","project","labels","url","completedAt"])
  ```
- Optionally, list issues already scoped to the upcoming cycle — some tickets may already be pulled in, which tells you what's already planned vs. what's aspirational:
  ```
  list_issues(team: "Speech Recognition", cycle: "<next cycle name>", limit: 250,
    fields: ["title","status","statusType","priority","assignee","project","labels","url","completedAt"])
  ```
- Group the outgoing cycle's issues by `project` — that grouping maps back to the goal-level themes on the Sprint Planning page (e.g. "LLM-based text-entity tagging on streamed ASR transcripts" → the entity tagger goal, "Model Patching POC: Domain Vocabulary Expansion" → the vocab endpoint goal). For each theme, note what's Done, what's still In Progress/In Review/In QA, and what's untouched (Todo).
- If the user named the cycle explicitly (e.g. "draft goals for Juno"), query that cycle by name instead of using current/previous/next.

### 1c. Slack — Last two weeks of discussion

Compute the `oldest` timestamp via shell: `date -d '14 days ago' +%s` (Linux) or `date -v-14d +%s` (macOS).

Four channels, each for a different reason:

- **`C08SF3A0B4L`** (#team-speech-recognition, public) — main engineering channel. Look hard for any message already stating cycle goals or priorities — someone on the team sometimes posts this proactively, and if so it's your strongest signal.
- **`C08S4B4H5DL`** (internal SR team channel) — secondary discussion, PR/API-council threads, naming debates, escalations.
- **`C0BSN5L3FR8`** (#feed-speech-recognition-deploys) — automated deploy notifications. Cross-check against Linear ticket statuses to confirm what actually reached prod.
- **`C0AMEADK2UX`** (#feed-speech-rec-feedback) — customer-feedback intake. Mostly noise unless there's a recent process change or escalation.

Fire all four `slack_read_channel` calls in parallel. Channels can exceed the single-response token budget — when that happens the result is saved to a file. Don't read that file directly with the Read tool (lines too long); hand it off to a subagent with instructions to slice it in ~80,000-character spans via Python and report back a factual summary. Running one subagent per channel in parallel is fastest.

Ask each subagent (or yourself, if the result fits in context) to extract:
1. Active engineering topics/projects being discussed
2. Any explicit statement of goals, priorities, decisions, or things being pushed to next cycle
3. Customer-driven issues or escalations
4. Open questions or unresolved disagreements as of the most recent messages

## Step 2 — Draft the goals

Synthesize all gathered data into a numbered list. For each goal:

1. **Bold title** — short, action-oriented (e.g. "Ship word-level timestamps to prod", "Decide on decoder keyterm biasing (GPU-PB) approach", "Initiate the vocabulary endpoint").
2. Optionally, one or two factual sentences: concrete ticket IDs (plain text, e.g. `SR-2864`, not hyperlinked — that's the house style on this page), what's shipped vs. pending, and a target date if one was actually stated somewhere (don't invent one). Leave this blank if you don't have anything concrete — a title-only goal is normal and expected when work is just starting.

What to leave out, because the team consistently edits it out when it appears: recommendations ("worth flagging", "your call on whether..."), hedging about whether something belongs on the list, meta-commentary about sequencing or dependencies between goals, and any framing of an item as a "decision point" rather than just stating what the decision is and what it's waiting on (compare "TBD — waiting on NVIDIA vs. building in-house" to "this needs a decision from the team on whether to partner with NVIDIA"). Say only what is currently true. If Slack surfaced an explicit next-cycle goal that Notion/Linear don't yet reflect, include it as a normal numbered goal — don't caveat it as new or uncertain, and don't second-guess whether it belongs.

Carry forward goals from the outgoing cycle whose underlying Linear tickets aren't Done yet, phrased as what's still needed to finish them. Add new goals surfaced from Slack discussion (especially anything explicitly framed as a next-cycle goal). Leave out anything that's fully Done in Linear and wasn't otherwise flagged as ongoing.

Cross-reference the outgoing cycle's Notion `Goals` text (what the team intended) against the Linear ticket states (what actually happened). Where they diverge — something planned but never started, or something shipped that wasn't originally a stated goal — surface it.

## Step 3 — Return the draft

Post the numbered list in the conversation for review. Don't write it to the Notion page's `Goals` property unless the user explicitly asks — they'll typically want to edit it (usually by tightening it further) before it's final. If they do ask you to write it in, use `notion-update-page` on the upcoming cycle's page, replacing the `Goals` property with the agreed text (use `<br>` between numbered items, matching the existing property's formatting).
