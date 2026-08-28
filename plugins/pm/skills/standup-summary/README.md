# standup-summary

Summarize Linear activity and Slack messages since the last standup. Accepts a timespan (e.g. "since Monday", "last 2 days") or defaults to the last 3 workdays.

## What it does

Pulls Linear issue activity (created, updated, completed issues) and relevant Slack messages for the given timespan, then combines them into a concise standup-style report grouped by theme or project. Uses the `parse_slack_overflow.py` helper to handle Slack pagination.

## Triggers

- "standup summary", "standup recap"
- "what did I do recently", "what have I been working on"
- "recap of recent work"

## Prerequisites

- Linear MCP server configured
- Slack MCP server configured
- `parse_slack_overflow.py` helper script (bundled)

## Platform

Works on **CLI-based agents** (Claude Code, OpenCode, etc.) with Linear and Slack MCP access.

## Setup

```bash
# Choose team-productivity when prompted.
npx plugins add JakobHavtorn/agent-skills

# Or install just this skill
npx skills add JakobHavtorn/agent-skills --skill standup-summary
```

See the [main README](../../../../README.md) for more installation options.
