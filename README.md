# Agent Skills

Personal collection of [Agent Skills](https://agentskills.io) for AI coding agents. Each skill is a folder with a `SKILL.md` file following the open standard — portable across OpenCode, Claude Code, Cursor, and other compatible agents.

## Skills

| Skill | Description |
|---|---|
| `linear-ticket` | Create a Linear issue with proper template, fields, and metadata |
| `open-pr` | Create or update a PR — lints, tests, commits, pushes, opens with Linear-linked description |
| `review-pr-comments` | Address PR review comments fetched via `gh api` |
| `prioritize-tasks` | Build a prioritized task list from Linear, Slack messages, and Slack To-do doc |
| `standup-summary` | Summarize Linear activity and Slack messages since the last standup |
| `speechrec-weekly-update` | Compose the pre-read status update for the weekly Speech Recognition sync call |

## Install

### Clone directly (recommended)

```bash
git clone git@github.com:JakobHavtorn/agent-skills.git ~/.config/opencode/skills
```

Update with `git pull`.

### Via `npx skills`

```bash
npx skills add JakobHavtorn/agent-skills --agent opencode -g
```

Update with:

```bash
npx skills update -g
```

## License

MIT
