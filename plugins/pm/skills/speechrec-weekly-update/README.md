# speechrec-weekly-update

Composes the pre-read status update for the weekly Speech Recognition sync call, ready to post in the team Slack channel.

## What it does

Gathers context from the previous status post, Notion sprint planning, Linear project updates, recent standup notes, and recent messages in the internal Speech Recognition Slack channel. Combines everything into a pre-read status update covering cycle items in progress, goals for the next cycle, and priority topics for discussion.

## Triggers

- "weekly update", "speechrec weekly update"
- "status update for the sync call"
- "pre-read for the weekly meeting"

## Prerequisites

- Linear MCP server configured
- Slack MCP server configured
- Notion MCP server configured
- `extract_recent_standups.py` and `summarize_linear_issues.py` helper scripts (bundled)

## Platform

Works on **CLI-based agents** (Claude Code, OpenCode, etc.) with Linear, Slack, and Notion MCP access.

## Setup

```bash
# Choose team-productivity when prompted.
npx plugins add JakobHavtorn/agent-skills

# Or install just this skill
npx skills add JakobHavtorn/agent-skills --skill speechrec-weekly-update
```

See the [main README](../../../../README.md) for more installation options.
