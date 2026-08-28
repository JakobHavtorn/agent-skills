# Agent Skills

A collection of personal agent skills for developer workflow and team productivity, following the [Agent Skills](https://agentskills.io) open standard.

## Quick Start

### Plugin Groups (Claude Code, OpenCode, Cursor, and More)

```bash
npx plugins add JakobHavtorn/agent-skills
```

The installer prompts you to select one or more plugin groups. To install every group non-interactively:

```bash
npx plugins add JakobHavtorn/agent-skills --yes
```

### Individual Skills

```bash
npx skills add JakobHavtorn/agent-skills --skill linear-ticket
```

### Other Agents

```bash
npx skills add JakobHavtorn/agent-skills -a <agent-name>
```

## Available Skills

### Developer Workflow (`dev-workflow`)

Developer workflow tools — create Linear issues, open PRs, and address review comments.

| Skill | Description |
|---|---|
| [linear-ticket](plugins/dev-workflow/skills/linear-ticket) | Create a Linear issue with proper template, fields, and metadata |
| [open-pr](plugins/dev-workflow/skills/open-pr) | Create or update a PR — lints, tests, commits, pushes, opens with Linear-linked description |
| [review-pr-comments](plugins/dev-workflow/skills/review-pr-comments) | Address PR review comments fetched via `gh api` |

### Team Productivity (`team-productivity`)

Team productivity tools — prioritize tasks, summarize standups, and compose weekly status updates.

| Skill | Description |
|---|---|
| [prioritize-tasks](plugins/team-productivity/skills/prioritize-tasks) | Build a prioritized task list from Linear, Slack messages, and Slack To-do doc |
| [standup-summary](plugins/team-productivity/skills/standup-summary) | Summarize Linear activity and Slack messages since the last standup |
| [speechrec-weekly-update](plugins/team-productivity/skills/speechrec-weekly-update) | Compose the pre-read status update for the weekly Speech Recognition sync call |

### Meta (`meta`)

Meta-skills for creating, evaluating, and iterating on agent skills.

| Skill | Description |
|---|---|
| [skill-creator](plugins/meta/skills/skill-creator) | Create, evaluate, and iterate on high-quality agent skills with quality scoring and best-practice enforcement |

## License

MIT
