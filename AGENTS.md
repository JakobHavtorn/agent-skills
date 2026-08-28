# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project overview

A collection of personal agent skills for developer workflow and team productivity, following the [Agent Skills](https://agentskills.io) open standard. Skills are installable into Claude Code, OpenCode, and other supported agents (Codex, Gemini CLI, GitHub Copilot, etc.).

## Repository structure

This repo is a **Claude Code plugin marketplace** (`.claude-plugin/marketplace.json` + `plugins/`) and an **Agent Skills** repository (the `SKILL.md` files inside `plugins/<group>/skills/`).

```
.claude-plugin/
  marketplace.json          # Marketplace definition — lists all plugin groups
plugins/
  dev-workflow/             # Developer workflow tools
    plugin.json             # Plugin manifest for this group
    skills/
      linear-ticket/        # Create Linear issues with proper template
        SKILL.md
      open-pr/              # Create/update PRs with lint, test, Linear linking
        SKILL.md
      review-pr-comments/   # Address PR review comments via gh api
        SKILL.md
  team-productivity/        # Team productivity tools
    plugin.json
    skills/
      prioritize-tasks/     # Prioritized task list from Linear + Slack + To-do
        SKILL.md
        parse_slack_overflow.py
      standup-summary/      # Standup recap from Linear activity and Slack
        SKILL.md
        parse_slack_overflow.py
      speechrec-weekly-update/  # Weekly Speech Recognition sync pre-read
        SKILL.md
        extract_recent_standups.py
        summarize_linear_issues.py
  meta/                     # Meta-skills for skill authoring
    plugin.json
    skills/
      skill-creator/        # Create, evaluate, and iterate on agent skills
        SKILL.md
        references/         # 6 reference files (dynamic-calling, writing-guide, etc.)
.github/workflows/
  release-skills.yml        # Zips each skill and publishes as GitHub release on tag
  skill-lint.yml            # Lints all SKILL.md files
```

## How skills work

Each skill is a self-contained directory under `plugins/<group>/skills/`. The `SKILL.md` file is what the agent reads at runtime — it tells the model when to activate, what steps to follow, and where to find reference details.

### SKILL.md format

```markdown
---
name: skill-name
description: >
  Multi-line description that doubles as the trigger definition.
  Include specific phrases, keywords, and scenarios that should activate this skill.
---

# Skill Title

Step-by-step instructions organized as ## Step N sections.
```

**Required frontmatter fields:** `name`, `description`

The `description` field is critical — it controls when the skill activates. Write it as a comprehensive trigger list, not a summary.

## Creating a new skill

1. Choose the appropriate plugin group (`dev-workflow`, `team-productivity`, or `meta`)
2. Create `plugins/<group>/skills/<skill-name>/` directory
3. Write `SKILL.md` with YAML frontmatter (`name`, `description`) and step-by-step instructions
4. Add a `README.md` for the skill's GitHub page (description, triggers, platform, setup)
5. Update the root `README.md` to list the new skill in the appropriate plugin group table
6. The skill will be auto-zipped and released on tag push via GitHub Actions

### Platform considerations

Skills that require shell access, network calls, or external binaries (e.g., `gh`, `python`) only work on **CLI-based agents** like Claude Code and OpenCode. They do **not** work on Claude.ai, which runs in a sandboxed environment that restricts network access and binaries.

## Plugin system

This repo ships as a Claude Code plugin marketplace containing 3 plugins:

| Plugin | Description |
|---|---|
| `dev-workflow` | Create Linear issues, open PRs, address review comments |
| `team-productivity` | Prioritize tasks, summarize standups, compose weekly updates |
| `meta` | Create, evaluate, and iterate on agent skills |

- `.claude-plugin/marketplace.json` — marketplace listing with all plugin entries.
- `plugins/<group>/plugin.json` — per-plugin manifest (name, version, keywords). Skills under `plugins/<group>/skills/` with SKILL.md frontmatter are auto-discovered by the plugin loader.

Users run `npx plugins add JakobHavtorn/agent-skills` and select one or more plugin groups interactively; `--yes` installs every discovered group. Individual skills can be installed via `npx skills add JakobHavtorn/agent-skills --skill <name>`.

## CI/CD

- **Release workflow** (`.github/workflows/release-skills.yml`): On tag push (`v*`), zips each skill from `plugins/*/skills/*/` and publishes them as a GitHub release.
- **Lint workflow** (`.github/workflows/skill-lint.yml`): Lints all `SKILL.md` files across all plugin groups. The linter caps `description` at 1024 chars and rejects angle brackets (`<` / `>`).

## Important constraints

- All changes must be merged to `main` via a pull request — do not push directly to `main`.
- This is primarily a documentation/reference repository — most of the codebase is `SKILL.md` files with no build step. Helper Python scripts (`parse_slack_overflow.py`, `extract_recent_standups.py`, `summarize_linear_issues.py`) are small utilities called by skills at runtime.
