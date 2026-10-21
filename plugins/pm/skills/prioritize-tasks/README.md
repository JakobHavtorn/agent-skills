# prioritize-tasks

Builds a single prioritized task list by combining active Linear tickets, tasks committed to in Slack, and the user's Obsidian task dashboard. Output is grouped into Now/Next/Later tiers and delivered in the terminal and as a Slack DM.

## What it does

Pulls from three sources — Linear (active assigned issues), Slack (messages where the user committed to do something), and the Obsidian vault (tasks managed with the Tasks plugin) — then deduplicates, ranks, and groups them into Now/Next/Later tiers. Sends the result as a Slack DM to the user. Items without a Linear ticket can be turned into issues via the `linear-ticket` skill.

## Triggers

- "prioritize tasks", "what should I work on"
- "task list", "prioritize my work"
- "what's on my plate"

## Prerequisites

- Linear MCP server configured
- Slack MCP server configured
- Obsidian vault with Tasks plugin (vault path configured in the skill)
- `parse_slack_overflow.py` and `extract_obsidian_tasks.py` helper scripts (bundled)

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
