# Agent Skills

A version-controlled catalog of agent skills covering software engineering and project management. Installable into any `SKILL.md`-compatible harness (Claude Code, Codex CLI, OpenCode, Oh My Pi, Cursor, and others) without per-harness forks of the content.

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

### Developer setup

For local development (installs pre-commit hooks for ruff, formatting, and file checks):

```bash
make install    # installs pre-commit, ruff, and wires git hooks
make test       # runs skillctl unit tests
make pre-commit # runs all hooks on all files
```

### Supported harnesses

| Harness | User scope | Project scope |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` | `.claude/skills/` |
| Codex CLI | `~/.codex/skills/<name>/` | `.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/<name>/` | `.opencode/skills/` |
| Cursor | `~/.cursor/skills/<name>/` | `.cursor/skills/` |
| Oh My Pi | `~/.omp/agent/skills/<name>/` | `.omp/skills/` |
| Pi | `~/.pi/agent/skills/<name>/` | `.pi/skills/` |

### Commands

```bash
skillctl list                          # list all plugins and skills
skillctl link --plugin <p> --agent <a> # symlink a plugin's skills into a harness
skillctl link --agent <a>              # symlink every plugin into a harness
skillctl unlink --plugin <p> --agent <a>  # remove a plugin's links
skillctl prune --agent <a>             # dry-run: report stale links and orphans
skillctl prune --agent <a> --apply     # remove links whose source skill was deleted
skillctl test                          # run trigger detection tests for all skills
skillctl test --skill <name> --verbose # test a single skill with per-case output
skillctl doctor                        # report links, orphans, broken symlinks
skillctl help                          # show detailed help with examples
```


## Context file

`skillctl link` also symlinks `global/AGENTS.md` into each harness's top-level config directory as `AGENTS.md`. This file contains high-level agent working rules (worktree policy, verification) that apply across all projects. It is linked at user scope only and lives alongside per-harness files like `~/.claude/CLAUDE.md` without replacing them.

| Harness | Context file path |
|---|---|
| Claude Code | `~/.claude/AGENTS.md` |
| Codex CLI | `~/.codex/AGENTS.md` |
| OpenCode | `~/.config/opencode/AGENTS.md` |
| Cursor | `~/.cursor/AGENTS.md` |
| Oh My Pi | `~/.omp/agent/AGENTS.md` |
| Pi | `~/.pi/agent/AGENTS.md` |

## Agents

The `agents/` directory holds standalone agent definitions that are not tied to a specific skill. `skillctl link` symlinks the entire `agents/` directory into each harness's config tree (user scope only), alongside the context file.

| Harness | Agents path |
|---|---|
| Claude Code | `~/.claude/agents/` |
| Codex CLI | `~/.codex/agents/` |
| OpenCode | `~/.config/opencode/agents/` |
| Cursor | `~/.cursor/agents/` |
| Oh My Pi | `~/.omp/agent/agents/` |
| Pi | `~/.pi/agent/agents/` |

| Agent | Description |
|---|---|
| [title.md](agents/title.md) | Hidden title generator — produces short session titles from conversation content |

## Plugins
### `coding`
Software engineering skills — Linear tickets, pull requests, code review.

| Skill | Description |
|---|---|
| [api-designer](plugins/coding/skills/api-designer) | Design REST/GraphQL APIs with OpenAPI 3.1 specs — resource modeling, versioning, pagination, RFC 7807 errors (vendored from Jeffallan/claude-skills) |
| [code-review](plugins/coding/skills/code-review) | Two-axis diff review — standards and spec, in parallel sub-agents (vendored from mattpocock/skills) |
| [codebase-design](plugins/coding/skills/codebase-design) | Shared vocabulary for deep-module design (vendored from mattpocock/skills) |
| [find-skills](plugins/coding/skills/find-skills) | Discover and install skills from the open agent skills ecosystem |
| [frontend-design](plugins/coding/skills/frontend-design) | Distinctive, intentional visual design for new or reshaped UI |
| [grill-me](plugins/coding/skills/grill-me) | Relentless interview to sharpen a plan or design (user-invoked, vendored from mattpocock/skills) |
| [grilling](plugins/coding/skills/grilling) | Stress-test a plan or decision via a design-tree interview in rounds (vendored from mattpocock/skills) |
| [incident-trace](plugins/coding/skills/incident-trace) | Trace incidents through backend services from Loki logs — receipts, negative evidence, verdicts |
| [linear-ticket](plugins/coding/skills/linear-ticket) | Create a Linear issue with proper template, fields, and metadata |
| [mermaid](plugins/coding/skills/mermaid) | Generate Mermaid diagrams — 32 types via lookup table linking to official docs |
| [open-pr](plugins/coding/skills/open-pr) | Create or update a PR — lints, tests, commits, pushes, Linear-linked description |
| [resolving-merge-conflicts](plugins/coding/skills/resolving-merge-conflicts) | Resolve merge/rebase conflicts hunk by hunk, traced to each side's intent |
| [review-pr-comments](plugins/coding/skills/review-pr-comments) | Address PR review comments fetched via `gh api` |
| [skill-creator](plugins/coding/skills/skill-creator) | Create, evaluate, and iterate on agent skills |
| [tdd](plugins/coding/skills/tdd) | Test-driven development — red-green-refactor with tests worth keeping (vendored from mattpocock/skills) |
| [technical-writing](plugins/coding/skills/technical-writing) | Draft and edit prose with Orwell's rules and ASD-STE100 Simplified Technical English |
| [to-spec](plugins/coding/skills/to-spec) | Turn the current conversation into a spec as a markdown document (vendored from mattpocock/skills) |
| [to-tickets](plugins/coding/skills/to-tickets) | Decompose a plan into tracer-bullet tickets with blocking edges, published to Linear (vendored from mattpocock/skills) |

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
