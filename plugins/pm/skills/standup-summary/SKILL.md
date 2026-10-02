---
name: standup-summary
description: >-
  Summarize Linear activity and Slack messages since the last standup.
  Accepts a timespan (e.g. "since Monday", "last 2 days") or defaults to the
  last 3 workdays. This skill should be used when the user asks for a
  standup summary, a recap of recent work, or what they've been doing.
allowed-tools: Bash(python:*) Bash(python3:*) Read
---

If the user provided a timespan in their message (e.g. "since Monday", "last 2 days", "since Friday"), use it in Step 1. If none was provided, default to the last 3 workdays.

## Overview

Generate a standup-style summary of the user's recent work by pulling Linear issue activity and relevant Slack messages. Combine them into a concise report grouped by theme or project.

---

## Step 1 — Determine the time window

Today's date is available as `currentDate` in the system context.

If the user provided a timespan (e.g. "since Monday", "last 2 days", "since Friday"), parse it into an absolute start datetime in ISO 8601 (UTC).

If no timespan was provided, default to **the last 3 workdays ending now, including today**. Skip weekends when counting back (e.g. if today is Monday, the window starts last Wednesday).

---

## Step 2 — Gather activity (run both parts in parallel)

Issue **Part A** and **Part B** in the same tool-call batch to run in parallel so Linear and Slack data arrive together. The two parts have no dependency on each other.

Resolve the current user at runtime:
- **Linear**: `get_user` with `query: "me"` returns the authenticated user (ID, name, email). Do **not** pass the `telemetry` parameter — it causes validation errors.
- **Slack**: `slack_read_user_profile` with no arguments returns the authenticated user's profile (Slack ID and display name).

Cache both results for the rest of the conversation; do not re-resolve on retries.

### Part A — Linear activity

Use the Linear MCP tools to collect the user's recent activity, scoped by the Linear user ID resolved above.

> **⚠ Known issue**: Do **not** pass the `telemetry` parameter to any Linear MCP tool — it causes `Invalid input` validation errors. Omit it entirely from all Linear tool calls.

- **Assigned issues updated**: `list_issues` filtered by `assignee` (use `"me"` or the user's email), sorted by `updatedAt` descending. Filter client-side to only include issues whose `updatedAt` falls within the time window.
- **Comments made**: `list_comments` for each issue updated in the window (pass `issueId`). The tool does not support a global "comments by user" query — fetch per-issue and filter by author if needed.
- **Status snapshot**: Linear's `list_issues` returns each issue's *current* status, not its transition history. Use the current status of issues updated in the window as a proxy — e.g. if an issue is currently `Done` and its `updatedAt` is within the window, treat it as completed in the window. This is imperfect (an issue could have changed twice) but it's what the MCP exposes. Don't claim transitions you can't see.

### Part B — Slack messages

Search Slack for messages the user sent or was mentioned in during the time window.

- Use `slack_search_public_and_private` with query `from:me after:<start-date>` to find messages sent by the user.
- Run a second search for mentions using `@<your-handle> after:<start-date>`, where `<your-handle>` comes from the `slack_read_user_profile` call. Slack search has no `to:me` operator — `@<handle>` is the way to find mentions.
- Prefer `response_format: "concise"` and `include_context: false` to keep the payload small.
- Ignore automated bot messages or noise (CI notifications, etc.).

If the Slack tool result overflows (returns an error pointing to a file under `tool-results/mcp-claude_ai_Slack-slack_search_public_and_private-*.txt`), do not read the file directly with `Read` — it will blow context. Instead, run the helper script that ships with this skill:

```bash
python3 <skill-dir>/scripts/parse_slack_overflow.py <dumped-file-path> --max-text 240
```

Resolve `<skill-dir>` from this skill's installed location (the directory containing this `SKILL.md` — e.g. `~/.claude/skills/standup-summary/`, `~/.omp/agent/skills/standup-summary/`, `~/.config/opencode/skills/standup-summary/`).

The script strips bot noise by default, keeps only the fields needed for a standup (time, channel, author, text), and prints one compact line per message so the whole window fits in context. Add `--include-bots` only if bot messages are relevant; use `--raw` to fall back to the full unparsed `results` blob.

---

## Step 3 — Synthesize the summary (standard markdown)

The summary is sent to Slack via `slack_send_message`, which renders **standard (CommonMark-style) markdown** — its own description lists `**bold**`, `_italic_`, `` `code` ``, and `[text](url)` links. Author the summary in standard markdown.

| You want | Use (standard markdown) |
| --- | --- |
| Section header | `**Heading**` (bold, on its own line) |
| Bold | `**bold**` |
| Italic | `_italic_` |
| Hyperlink | `[text](url)` |
| Bullet | `- item` (or `• item`) |
| Inline code | `` `code` `` |

> This Slack workspace's `slack_send_message` takes standard markdown, **not** legacy Slack `mrkdwn`. Do **not** use `*single-asterisk*` for bold or `<url|text>` links — those are the older `mrkdwn` dialect and render wrong in this tool (`*x*` shows as italic). Verified by live sends.

Combine the Linear and Slack signals into a standup-style summary using this template:

```
**Standup Summary — <date range>**

**Done / Completed**
- <issue title or task> [XY-1234](https://linear.app/<workspace>/issue/XY-1234)
- ...

**In Progress**
- <issue title or task> [XY-1234](https://linear.app/<workspace>/issue/XY-1234)
- ...

**Blocked / Needs attention**
- <anything flagged as blocked, or threads awaiting response>
- ...

**Notable discussions**
- <key Slack discussions, decisions, or async threads worth surfacing>
- ...

**Executive summary**
<2–4 sentence narrative synthesizing the week's work: the main themes, what landed, what's in flight, and anything noteworthy. No bullet lists, no ticket IDs.>
```

Rules:
- Keep each bullet to one line.
- Group related items together rather than listing every minor comment.
- Prefer Linear issue titles over paraphrasing — they are already concise.
- If a Slack thread corresponds to a Linear issue, merge them into one bullet.
- Do not include items that are clearly outside the user's direct involvement.
- Produce the Executive summary last, after all other sections are drafted — it should reflect the full picture. Write it as flowing prose that a busy reader could skim in 10 seconds to understand the week at a high level; skip ticket IDs and per-item detail since those live in the sections above.

### Linear ticket links

When referencing a Linear issue, use the canonical `url` returned by the MCP tool (`issue.url`) — do not hand-construct URLs. Use the actual identifier (e.g. `SR-2621`, `PLAT-17`) — never invent or abbreviate. Format the link as standard markdown: `[SR-2621](url)`.

---

## Step 4 — Send the summary as a Slack DM

After producing the summary, send it to the user as a Slack direct message.

1. Use the Slack user ID resolved in Step 2 as the `channel_id` argument (Slack treats a user ID as a DM channel).
2. Send the standard-markdown summary from Step 3 verbatim with `slack_send_message`. `**bold**` and `[text](url)` are correct for this tool — don't convert them to `*…*`/`<url|text>` (that legacy `mrkdwn` dialect renders wrong here).
3. Add a `——————————————————————————` line (em-dashes) between major sections: after the preamble line, and between each of **Done / Completed**, **In Progress**, **Blocked / Needs attention**, **Notable discussions**, and **Executive summary**.
4. After sending, confirm to the user in the terminal that the DM was delivered (include the message timestamp or permalink if returned).

If the Slack send fails, surface the error to the user and still print the summary in the terminal so nothing is lost.
