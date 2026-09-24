# Agent Skills

A version-controlled catalog of agent skills covering software engineering, personal finance, and project management. Installable into any `SKILL.md`-compatible harness (Claude Code, Codex CLI, OpenCode, Cursor, and others) without per-harness forks of the content.

Conforms to the [Agent Skills](https://agentskills.io) and [Agent Plugins 1.0.0](https://agent-plugins.org) standards.

## Quick Start

**One-liner** (clones and links all skills to OpenCode):

```bash
curl -fsSL https://raw.githubusercontent.com/JakobHavtorn/agent-skills/main/install.sh | bash
```

Customize with flags:

```bash
curl ... | bash -s -- --agent claude        # link to Claude Code
curl ... | bash -s -- --all                # link everything to all harnesses
curl ... | bash -s -- --plugin coding       # link only the coding plugin
```

**Manual** (if you prefer to clone yourself):

```bash
git clone git@github.com:JakobHavtorn/agent-skills.git ~/.agent-skills
~/.agent-skills/bin/setup --agent opencode
```

Clone once, link many — `git pull && bin/setup` updates every harness at once.

Verify your installation:

```bash
~/.agent-skills/bin/skillctl doctor   # check links, orphans, broken symlinks
```

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
skillctl link --all --agent <a>        # symlink every plugin into a harness
skillctl unlink --plugin <p> --agent <a>  # remove a plugin's links
skillctl test                          # run trigger detection tests for all skills
skillctl test --skill <name> --verbose # test a single skill with per-case output
skillctl doctor                        # report links, orphans, broken symlinks
skillctl help                          # show detailed help with examples
```

## Plugins

### `coding`

Software engineering skills — Linear tickets, pull requests, code review.

| Skill | Description |
|---|---|
| [code-review](plugins/coding/skills/code-review) | Two-axis diff review — standards and spec, in parallel sub-agents |
| [codebase-design](plugins/coding/skills/codebase-design) | Shared vocabulary for deep-module design |
| [find-skills](plugins/coding/skills/find-skills) | Discover and install skills from the open agent skills ecosystem |
| [frontend-design](plugins/coding/skills/frontend-design) | Distinctive, intentional visual design for new or reshaped UI |
| [grill-me](plugins/coding/skills/grill-me) | Relentless interview to sharpen a plan or design (user-invoked) |
| [grill-with-docs](plugins/coding/skills/grill-with-docs) | Grilling that also creates docs — ADRs and glossary (user-invoked) |
| [grilling](plugins/coding/skills/grilling) | Stress-test a plan or decision via a design-tree interview in rounds |
| [linear-ticket](plugins/coding/skills/linear-ticket) | Create a Linear issue with proper template, fields, and metadata |
| [open-pr](plugins/coding/skills/open-pr) | Create or update a PR — lints, tests, commits, pushes, Linear-linked description |
| [skill-creator](plugins/coding/skills/skill-creator) | Create, evaluate, and iterate on agent skills |
| [tdd](plugins/coding/skills/tdd) | Test-driven development — red-green-refactor with tests worth keeping |

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
