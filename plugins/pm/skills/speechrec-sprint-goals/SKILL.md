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

## Step 1 — Identify the outgoing and upcoming cycle

Fetch the Sprint Planning database and find the two relevant cycle entries:

- Sprint Planning page: `https://www.notion.so/cortihome/Sprint-Planning-20dbef65b3ab800c85dbd99368164e20`
- Data source: `collection://20dbef65-b3ab-8076-8351-000b245ea82b` ("Team Speech Rec - Sprint Planning")
- Query it (via `notion-query-data-sources`, SQL mode) for the most recent rows, e.g. `SELECT * FROM "collection://20dbef65-b3ab-8076-8351-000b245ea82b" ORDER BY "date:Dates:start" DESC LIMIT 6`.
- The **outgoing cycle** is the one whose `Dates` range contains today (or the one most recently ended if none is currently active). The **upcoming cycle** is the one starting right after it — this is the page you're drafting goals for. If the user names the cycle directly (e.g. "draft goals for Juno"), match on `Cycle Name` instead of computing by date.
- Note the upcoming cycle's page URL — that's where the draft is destined (if the user later asks you to write it in).
- Check the upcoming cycle's own `Goals` property before assuming it's blank — someone may have already sketched a draft there (possibly stale, possibly already edited down by the team). If it has content, treat it as an existing draft to verify and refresh against Steps 2-3, not as something to ignore or blindly overwrite.
- Also grab 1-2 **older, already-completed** cycle entries and look at their `Goals` property. This is your style reference: match the exact formatting (numbered bold titles, one-line factual bodies, blank bodies where nothing concrete existed) rather than re-deriving a format from scratch. The team edits these down to remove commentary, so mirror the leanest, most recently-edited example you can find, not your own instinct for how detailed it should be.

## Step 2 — Pull the outgoing cycle's ticket status from Linear

The Notion `Cycle - Linear link` property points to the cycle in Linear (e.g. `https://linear.app/corti/team/SR/cycle/36`). The Linear cycle's title matches the Notion `Cycle Name` exactly (both use the same mythological-name convention), so you can query by name directly:

```
list_issues(team: "Speech Recognition", cycle: "<outgoing cycle name>", limit: 250,
  fields: ["title","status","statusType","priority","assignee","project","labels","url","completedAt"])
```

The Speech Recognition team ID is `70db986a-d0a7-40fe-8894-132948e77ebe` if you need it directly. Group the returned issues by `project` — that grouping is what maps back to the goal-level themes on the Sprint Planning page (e.g. "LLM-based text-entity tagging on streamed ASR transcripts" → the entity tagger goal, "Model Patching POC: Domain Vocabulary Expansion" → the vocab endpoint goal). For each theme, note what's Done, what's still In Progress/In Review/In QA, and what's untouched (Todo) — this tells you what's genuinely finished vs. what needs to carry into the upcoming cycle as a goal.

Cross-reference this against the outgoing cycle's own `Goals` text from Notion (fetched in Step 1) — that text tells you what the team *intended*; the Linear ticket states tell you what actually happened. Where they diverge (something was planned but never started, or something shipped that wasn't originally a stated goal), that's worth surfacing.

## Step 3 — Pull the last two weeks of Slack discussion

Four channels matter here, each for a different reason:

- **`C08SF3A0B4L`** (#team-speech-recognition, public) — the main engineering discussion channel. This is where explicit "goals for next cycle" posts, technical decisions, and open questions actually get written out. Check here first and look hard for any message that already states cycle goals or priorities — someone on the team (e.g. the tech lead) sometimes posts this proactively, and if so it's your strongest signal, not just supporting color.
- **`C08S4B4H5DL`** (internal SR team channel) — secondary internal discussion, PR/API-council threads, naming debates, customer-escalation coordination.
- **`C0BSN5L3FR8`** (#feed-speech-recognition-deploys) — automated deploy notifications only, no human discussion. Useful only to confirm exactly which tickets actually reached prod/staging and when — cross-check this against what Linear ticket statuses claim.
- **`C0AMEADK2UX`** (#feed-speech-rec-feedback) — automated customer-feedback intake (Intercom/Fillout) plus occasional process updates about the feedback pipeline. Mostly noise unless there's a recent process change or a customer escalation worth naming.

Use `slack_read_channel` with `oldest` set to a Unix timestamp ~14 days before today (compute via shell, don't guess). These channels can easily exceed the single-response token budget — when that happens the result is saved to a file instead of an error. **Don't try to read that file directly with the Read tool** (lines are too long); either grep it for date strings, or better, hand it off to a subagent with instructions to slice it in ~80,000-character spans via Python and report back a factual summary scoped to the last two weeks (see the field notes below for what to ask it to extract). Running one subagent per channel in parallel is faster than reading them serially.

Ask each subagent (or ask yourself, if the result fits in context) to extract, for the given channel and time window:
1. Active engineering topics/projects being discussed
2. Any explicit statement of goals, priorities, decisions, or things being pushed to next cycle
3. Customer-driven issues or escalations
4. Open questions or unresolved disagreements as of the most recent messages

## Step 4 — Draft the goals

Synthesize Steps 1-3 into a numbered list. For each goal:

1. **Bold title** — short, action-oriented (e.g. "Ship word-level timestamps to prod", "Decide on decoder keyterm biasing (GPU-PB) approach", "Initiate the vocabulary endpoint").
2. Optionally, one or two factual sentences: concrete ticket IDs (plain text, e.g. `SR-2864`, not hyperlinked — that's the house style on this page), what's shipped vs. pending, and a target date if one was actually stated somewhere (don't invent one). Leave this blank if you don't have anything concrete — a title-only goal is normal and expected when work is just starting.

What to leave out, because the team consistently edits it out when it appears: recommendations ("worth flagging", "your call on whether..."), hedging about whether something belongs on the list, meta-commentary about sequencing or dependencies between goals, and any framing of an item as a "decision point" rather than just stating what the decision is and what it's waiting on (compare "TBD — waiting on NVIDIA vs. building in-house" to "this needs a decision from the team on whether to partner with NVIDIA"). Say only what is currently true. If Slack surfaced an explicit next-cycle goal that Notion/Linear don't yet reflect, include it as a normal numbered goal — don't caveat it as new or uncertain, and don't second-guess whether it belongs.

Carry forward goals from the outgoing cycle whose underlying Linear tickets aren't Done yet, phrased as what's still needed to finish them. Add new goals surfaced from Slack discussion (especially anything explicitly framed as a next-cycle goal). Leave out anything that's fully Done in Linear and wasn't otherwise flagged as ongoing.

## Step 5 — Return the draft

Post the numbered list in the conversation for review. Don't write it to the Notion page's `Goals` property unless the user explicitly asks — they'll typically want to edit it (usually by tightening it further) before it's final. If they do ask you to write it in, use `notion-update-page` on the upcoming cycle's page, replacing the `Goals` property with the agreed text (use `<br>` between numbered items, matching the existing property's formatting).
