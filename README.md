# Agent Skills

A version-controlled catalog of agent skills covering software engineering, personal finance, and project management. Installable into any `SKILL.md`-compatible harness (Claude Code, Codex CLI, OpenCode, Cursor, and others) without per-harness forks of the content.

Conforms to the [Agent Skills](https://agentskills.io) and [Agent Plugins 1.0.0](https://agent-plugins.org) standards.

## Quick Start

```bash
git clone git@github.com:JakobHavtorn/agent-skills.git ~/.agent-skills
~/.agent-skills/bin/skillctl link --plugin coding  --agent claude
~/.agent-skills/bin/skillctl link --plugin finance --agent opencode
~/.agent-skills/bin/skillctl link --plugin pm      --agent claude
```

Clone once, link many — `git pull` updates every harness at once.

### Supported harnesses

| Harness | User scope | Project scope |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` | `.claude/skills/` |
| Codex CLI | `~/.codex/skills/<name>/` | `.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/<name>/` | `.opencode/skills/` |
| Cursor | `~/.cursor/skills/<name>/` | `.cursor/skills/` |

### Commands

```bash
skillctl list                          # list all plugins and skills
skillctl link --plugin <p> --agent <a> # symlink a plugin's skills into a harness
skillctl unlink --plugin <p> --agent <a>  # remove a plugin's links
skillctl doctor                        # report links, orphans, broken symlinks
```

## Plugins

### `coding`

Software engineering skills — Linear tickets, pull requests, code review.

| Skill | Description |
|---|---|
| [linear-ticket](plugins/coding/skills/linear-ticket) | Create a Linear issue with proper template, fields, and metadata |
| [open-pr](plugins/coding/skills/open-pr) | Create or update a PR — lints, tests, commits, pushes, Linear-linked description |
| [review-pr-comments](plugins/coding/skills/review-pr-comments) | Address PR review comments fetched via `gh api` |
| [skill-creator](plugins/coding/skills/skill-creator) | Create, evaluate, and iterate on agent skills |

### `finance`

Personal finance skills.

| Skill | Description |
|---|---|
| [taxhelper](plugins/finance/skills/taxhelper) | Danish tax assessment lookup, rubric search, and PDF worksheet flows |

### `pm`

Project management and team productivity skills.

| Skill | Description |
|---|---|
| [prioritize-tasks](plugins/pm/skills/prioritize-tasks) | Prioritized task list from Linear, Slack, and To-do doc |
| [standup-summary](plugins/pm/skills/standup-summary) | Standup recap from Linear activity and Slack messages |
| [speechrec-weekly-update](plugins/pm/skills/speechrec-weekly-update) | Pre-read status update for the weekly Speech Recognition sync call |
| [speechrec-sprint-goals](plugins/pm/skills/speechrec-sprint-goals) | Draft SR team sprint goals from Notion, Linear, and Slack |

## License

MIT — see [LICENSE](LICENSE).
