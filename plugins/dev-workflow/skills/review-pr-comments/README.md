# review-pr-comments

Address PR review comments by fetching all review comments via `gh api`, assessing which warrant code changes, implementing those changes, and running the linter. Does not commit or push.

## What it does

Fetches all review comments and review-level comments on a PR via GitHub's REST API, presents an assessment of each comment to the user, and implements code changes for comments that warrant them. Runs the linter after changes but does not commit or push.

## Triggers

- "address PR review comments", "fix review comments"
- "respond to PR feedback"
- "handle review comments"

## Prerequisites

- `gh` CLI authenticated
- Git repository with an open PR

## Platform

Works on **CLI-based agents** (Claude Code, OpenCode, etc.).

## Setup

```bash
# Choose dev-workflow when prompted.
npx plugins add JakobHavtorn/agent-skills

# Or install just this skill
npx skills add JakobHavtorn/agent-skills --skill review-pr-comments
```

See the [main README](../../../../README.md) for more installation options.
