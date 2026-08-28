# prioritize-tasks

Builds a single prioritized task list by combining active Linear tickets, tasks committed to in Slack, and a Slack To-do doc. Output is grouped into Now/Next/Later tiers and delivered in the terminal and as a Slack DM.

## What it does

Pulls from three sources — Linear (active assigned issues), Slack (messages where the user committed to do something), and a Slack To-do document — then deduplicates, ranks, and groups them into Now/Next/Later tiers. Sends the result as a Slack DM to the user. Items without a Linear ticket can be turned into issues via the `linear-ticket` skill.

## Triggers

- "prioritize tasks", "what should I work on"
- "task list", "prioritize my work"
- "what's on my plate"

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
npx skills add JakobHavtorn/agent-skills --skill prioritize-tasks
```

See the [main README](../../../../README.md) for more installation options.
