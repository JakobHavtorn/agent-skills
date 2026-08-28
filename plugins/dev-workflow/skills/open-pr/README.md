# open-pr

Create or update a pull request on the current branch — lints, tests, commits, pushes, then opens or updates the PR with a Linear-linked description.

## What it does

Drives a pull request on the current branch to a review-ready state: linted, tested, committed, pushed, and either freshly opened or updated. Uses `gh api` (REST) for PR operations to avoid deprecation errors with classic GitHub Projects fields. Links the PR to a Linear issue in the description.

## Triggers

- "open a PR", "create a pull request"
- "update the PR"
- "push and create a PR"

## Prerequisites

- `gh` CLI authenticated
- Git repository on current branch
- Linear MCP server (for issue linking)

## Platform

Works on **CLI-based agents** (Claude Code, OpenCode, etc.).

## Setup

```bash
# Choose dev-workflow when prompted.
npx plugins add JakobHavtorn/agent-skills

# Or install just this skill
npx skills add JakobHavtorn/agent-skills --skill open-pr
```

See the [main README](../../../../README.md) for more installation options.
