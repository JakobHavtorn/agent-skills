# linear-ticket

Create a Linear issue with proper template, fields, and metadata for the Speech Recognition team.

## What it does

Gathers workspace metadata (teams, users, labels, statuses, cycles) and creates a Linear issue with the correct team, project, assignee, labels, priority, and cycle fields. Uses the Linear MCP tools to ensure all metadata is resolved properly before issue creation.

## Triggers

- "create a Linear ticket", "create a Linear issue"
- "add a ticket to Linear"
- "file a bug in Linear"

## Prerequisites

- Linear MCP server configured and authenticated

## Platform

Works on **CLI-based agents** (Claude Code, OpenCode, etc.) with Linear MCP access.

## Setup

```bash
# Choose dev-workflow when prompted.
npx plugins add JakobHavtorn/agent-skills

# Or install just this skill
npx skills add JakobHavtorn/agent-skills --skill linear-ticket
```

See the [main README](../../../../README.md) for more installation options.
