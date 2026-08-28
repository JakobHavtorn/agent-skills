---
name: speechrec-weekly-update
description: >-
  Composes the pre-read status update for the weekly Speech Recognition sync
  call, ready to post in the team Slack channel. Gathers context from the
  previous status post, Notion sprint planning, Linear project updates,
  recent standup notes, and recent messages in the internal Speech
  Recognition channel. Use when the user asks for the weekly Speech
  Recognition status update, sync call pre-read, or weekly status post.
allowed-tools: Bash(python:*) Bash(python3:*) Read
metadata:
  dk.jakob.category: pm
  dk.jakob.version: "1.0"
  dk.jakob.status: stable
---

## Overview

Generate a pre-read status update for the weekly Speech Recognition sync call, ready to post in the team Slack channel. The message covers: status on cycle items in progress, goals for the next cycle, and priority topics for discussion.

---

## Step 1 — Determine the meeting date

Today's date is available as `currentDate` in the system context.

The weekly call is on Tuesday afternoons. If today is not Tuesday, the meeting date is this coming Tuesday. If today is Tuesday, the meeting date is today. Calculate the exact next meeting date and use it in the message title.

---

## Step 2 — Fetch context

Run the following steps to gather context for the status update. Run each step (2a-d) in parallel with independent agents. 

### 2a. Previous status message and message history (Slack)

**Used for:** contextualization of this update – allows this update to build on (not repeat) the previous one.

**Part 1:** Read the most recent status update thread from the public Speech Recognition team channel using MCPs `slack_search_public_and_private` and `slack_read_thread`:
- `channel_id`: `C08SF3A0B4L`
- Run a single search with `slack_search_public_and_private`, sorted by `timestamp` descending, limit 3:
  - `Preparation Weekly SpeechRec in:#team-speech-recognition`
- From the results, pick the single most recent message that reads like a weekly pre-read (contains a status update section and discussion topics). Fetch that thread with `slack_read_thread`. Echo the thread back to the user as well as a link to the message.
- If no results are found, stop the job and return to the user letting them know and asking them to provide the status message content directly, or continue without the message.

**Part 2:** Read messages posted in the internal Speech Recognition team channel since the last sync meeting using MCP `slack_read_channel`:
- `channel_id`: `C08S4B4H5DL`
- `oldest`: Unix timestamp of last Tuesday 00:00 (compute from `currentDate`; if today is Tuesday, use last week's Tuesday). Compute it with the shell rather than guessing: `date -j -f "%Y-%m-%d %H:%M:%S" "YYYY-MM-DD 00:00:00" "+%s"` on macOS.
- `limit`: 100 (the channel rarely exceeds this between syncs)
- Skim for: customer issues raised, blockers surfaced, decisions made, PR/release announcements — anything that should appear in the status update or as a discussion topic. Skip the previous status thread itself (already fetched in Part 1).
- For any parent message that has replies (`reply_count > 0`) and looks substantive (customer feedback, bug reports, blockers, decisions, anything you might cite), follow up with `slack_read_thread` on that message's `ts` to read the replies. Run these thread fetches in parallel where possible. Resolutions, additional context, and decisions often live in the thread rather than the parent message.

### 2b. Current and upcoming cycle goals (Notion)

**Used for:** primary source for the **forward-looking goals** section, and frames which items count as "this cycle" for the status section.

Fetch the Sprint Planning page and find the relevant cycle entries:
- Sprint Planning page: `https://www.notion.so/cortihome/Sprint-Planning-20dbef65b3ab800c85dbd99368164e20`
- Search the data source `collection://20dbef65-b3ab-8076-8351-000b245ea82b` using MCP `notion-search` to find recent cycle pages (e.g. query: "cycle sprint goals dates"). Fetch the top 3–4 results individually using `notion-fetch` on each page URL.
- From the fetched pages, identify the **current cycle** (today's date is between its `Dates` start and end) and the **next cycle** (start date is after the current cycle's end). Extract each cycle's `Goals` property.

**Pick which cycle's goals are "forward-looking" using this heuristic:**
- Compute `days_elapsed` (today − current cycle start) and `days_remaining` (current cycle end − today) for the current cycle.
- If `days_remaining > days_elapsed` (today is in the **first half** of the current cycle) → forward-looking goals = **current cycle's** goals. The step-3 section header is **`Goals for this cycle ([CYCLE NAME], ending [DATE])`**.
- Otherwise (today is in the **second half** of the current cycle) → forward-looking goals = **next cycle's** goals. The step-3 section header is **`Goals for next cycle — [CYCLE NAME] (starting [DATE])`**.
- Always surface a forward-looking goals section — never drop it. If today is in the second half but no next cycle is planned in Notion, fall back to the current cycle's still-open goals and label the section **`Goals for the rest of this cycle ([CYCLE NAME], ending [DATE])`**.

The cycle name in the **status update** section header (step 3) is always the **current cycle**, independent of which cycle's goals are being surfaced as forward-looking.

Echo back to the user: both cycles' names + dates, which cycle was chosen as forward-looking (and why, in one line), and the goals for both cycles.

### 2c. Fetch selected Linear projects and tickets:

**Used for:** primary source of truth for the **Status update on key items in progress** section — project `get_status_updates` give the authoritative current state, and recent tickets surface concrete progress, blockers, and candidates for **Priority topics**.

Run the following two Linear fetches in parallel:

**Part 1 - Tickets:** Call `list_issues` for the Speech Recognition team, filtered to issues updated in the last 7 days (`updatedAt: "-P7D"`), ordered by `updatedAt` descending, limit 200. The result might exceed the token budget and spill to disk. In that case, run the bundled summarizer to get a categorized listing:

```bash
python3 ~/.config/opencode/skills/speechrec-weekly-update/summarize_linear_issues.py <FILE_PATH>
```

It groups issues into Recently Completed (last 7 days; override with `--days N`), In Progress, and In Review, with one line per issue (`updatedAt | status | SR-id | title | [project]`).

Note any items representing meaningful progress, blockers, or newly completed work for the status update.

**Part 2 - Projects:** Call MCP `list_projects` for the Speech Recognition team with `state: "in_progress"`, plus a second call with no state filter but `updatedAt: "-P14D"` to catch projects recently moved to paused, blocked, or completed. Deduplicate. For each project returned, call MCP `get_status_updates` to retrieve the two most recent project updates and read them. Use these updates (not just the project name) as the source of truth for current project status (if it is recent).

### 2d. Fetch standup notes (Slack Canvas)

**Used for:** granular ground truth — adds week-level detail (what shipped, what's still in flight) to the status section and surfaces blockers and follow-ups that become **Priority topics** or **Other notes**.

The canvas is too large to fit in context, so Claude Code's harness automatically saves the full result to a temp file instead. This is expected — not an error. Follow these steps:

**Part 1**: Call MCP `slack_read_canvas` with `canvas_id: F09LCH57KRQ`. The harness will intercept the oversized result, write it to a file, and return a message like "result exceeds maximum allowed tokens, output saved to `<FILE_PATH>`". Note that file path.

**Part 2**: Run the extractor script that ships with this skill, passing the file path from the error:

```bash
python3 ~/.config/opencode/skills/speechrec-weekly-update/extract_recent_standups.py <FILE_PATH>
```

It parses the JSON dump, splits the canvas markdown on `## ![](slack_date:YYYY-MM-DD)` headers, and prints only the sections from the last 10 days.

**Part 3**: Parse the printed sections. The canvas uses `## ![](slack_date:YYYY-MM-DD)` as section headers. Each section lists team members by Slack user ID with their standup update. Extract:
- Items completed or newly deployed
- Items still in progress and their current state
- Blockers, questions, and follow-up items

User ID → name mappings:
- `<@U04G8U5SVJL>` = Michael
- `<@U04TXHY5MMJ>` = Simas
- `<@U067BQ11M7A>` = Jerome
- `<@U074ZNDHQTV>` = Lana
- `<@U07JMB1EHRD>` = Robert
- `<@U082WUUQQAV>` = Chit
- `<@U086V4A6JB0>` = Dan Engel
- `<@U08BGBWSWU8>` = Arne
- `<@U09LZ64UL5P>` = Anna
- `<@UBCF2ADNE>` = Jakob
- `<@UHEN7TDNG>` = Gedas

---

## Step 3 — Compose the status update

Here you will synthesize the information gathered in Step 2 into a concise status update message for the team Slack channel. Follow the exact structure and formatting rules outlined below to ensure consistency with prior messages.

**Part 1**: Review all the gathered context and identify the most important updates, progress, and discussion topics to include in the message. Prioritize clarity and brevity. Think about how items relate to each other. Focus on what the team needs to know for the upcoming sync meeting.

**Part 2**: Write the Slack message using this exact structure:

```md
**Preparation for Weekly SpeechRec Sync Meeting - [DD Month]**

<@UBCF2ADNE|Jakob> <@U086V4A6JB0|Dan Engel> <@UC93DK477|Henrik> <@U07HFSS28MR|Kevin> <@U1B9GHW8L|Lars> <@U04G8U5SVJL|Michael> <@U090GQJ004F|James Kane> <@U08EY8UDKS6|Nicklas Frahm>

——————————————————————————

**Status update on key items in progress this cycle ([CURRENT CYCLE NAME], ending [DATE]):**
1. **[Item name](Linear URL)** – [concise status: what's done, what's in progress, what's next]
2. ...

——————————————————————————

**[FORWARD-LOOKING GOALS HEADER — pick the exact form from step 2b based on cycle position]:**
1. **[Item name](Linear URL)** – [one-line goal]
2. ...

——————————————————————————

**Priority topics for discussion Tuesday:**
1. **[Topic](Linear URL)** – [why it needs discussion / who should weigh in]
2. ...

——————————————————————————

**Other notes:**
1. **[Topic](Linear URL)** – [any additional notes, follow-ups, or reminders for the team]
```

Rules:
- Keep each status line to 1–2 sentences. Be specific about state: what shipped, what's in flight, what's blocked.
- Discussion topics should be actionable: things that need a decision, alignment, or visibility — not general FYIs.
- Each enumerated list item's bold name should itself be a hyperlink to the relevant Linear project or ticket when one exists. Use the format `**[Item name](URL)**`. Only omit the link if no directly relevant Linear URL is available.

Message formatting:
- The @mention format uses `<@USERID|name>` — preserve the user IDs from the previous message.
- Use `**double asterisks**` for ALL bold text — section headers, item names within lists, and topic names. Single asterisks render as italic via `slack_send_message` and must not be used for bold.
- Use numbered lists for items and topics, not bullet points.
- Use markdown links (e.g. `[text](url)`) for any references to Notion pages, Linear tickets, or other resources.
- Use ticks `` for any inline code references (e.g. tool names, service names, endpoints, specific commands, language codes, or data source identifiers).
- Add a `——————————————————————————` line (em-dashes) between each major section (after the preamble, after the status update list, after the goals list, after the topics list).

---

## Step 4 — Send the update

Once the message is composed, send it to the user as a Slack DM.

1. The Slack MCP tool descriptions already expose the authenticated user's Slack ID (e.g. `slack_search_public_and_private` and `slack_send_message` state it as "Current logged in user's user_id is …"). Use that ID directly — no profile lookup is needed.
2. Send the message with `slack_send_message`, using that Slack user ID as the `channel_id` (Slack treats a user ID as a DM channel).
3. After sending, echo the returned message link back to the user in the conversation.

## Step 5 — Follow up

Report any issues encountered during the process of executing this skill (e.g. missing context, fetch errors).
