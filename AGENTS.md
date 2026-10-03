# AGENTS.md

Guidance for AI agents working **on** this repository. Not a skill — no harness loads this file.

## Standards

This repo conforms to two upstream standards:

- [Agent Skills](https://agentskills.io) — individual skill folders: `SKILL.md` frontmatter, bundled resources, progressive disclosure.
- [Agent Plugins 1.0.0](https://agent-plugins.org) — packaging layer: `plugin.json`, fixed `skills/` and `mcp.json` locations.

## Layout

```
plugins/<plugin>/plugin.json          # manifest ($schema + name, both required)
plugins/<plugin>/skills/<skill>/      # immediate children only — SKILL.md discovered at this depth
plugins/<plugin>/skills/<skill>/SKILL.md
plugins/<plugin>/skills/<skill>/scripts/   # executable helpers
plugins/<plugin>/skills/<skill>/references/  # loaded on demand
plugins/<plugin>/skills/<skill>/assets/      # templates, lookup tables
plugins/<plugin>/skills/<skill>/agents/     # per-skill sub-agent definitions (e.g. openai.yaml)
bin/skillctl                          # install / link / test / doctor
bin/validate-skill                    # spec validation wrapper
bin/setup                              # convenience wrapper for skillctl link
global/AGENTS.md                      # shared context file — symlinked into harnesses by skillctl link
agents/title.md                       # hidden omp-specific title generator agent
tests/<skill>/cases.json              # trigger detection test cases
tests/<skill>/results.json            # last test run output (gitignored)
tests/test_skillctl.py                # unit tests for skillctl pure functions
```

When adding or changing features tracked in `TODO.md`, update the corresponding checklist item before opening the PR.

Skills are discovered only from immediate children of `skills/`. Nested subdirectories would break discovery. CI rejects any `SKILL.md` not at exactly `plugins/<plugin>/skills/<skill>/SKILL.md`.

## Authoring skills

For frontmatter rules, detection flows, step structure, reference file organization, and quality scoring, use the `skill-creator` skill (`plugins/coding/skills/skill-creator/`). It covers the full authoring lifecycle and is the single source of truth for how to write a SKILL.md.

## README.md

When adding a new skill, update `README.md` to include it in the relevant plugin's skill table. The `global/` directory holds the shared `AGENTS.md` context file symlinked into harnesses by `skillctl link`; the `agents/` directory holds standalone agent definitions (e.g. `title.md`). When adding a new agent to `agents/`, update `README.md` to document it.

## Skill name uniqueness

Skill directory names must be unique across the whole repository, not just within a plugin. Harnesses install into a single flat directory; two plugins shipping the same name collide on install.

## Data rule

Never write personal data — account numbers, balances, transaction exports, employer data, client names — into any file in this repo. Skills that operate on personal data resolve it at runtime from `$SKILLS_DATA_DIR` or equivalent. CI rejects IBAN-shaped strings, long digit runs, and `.csv`/`.ofx`/`.qif` files.

## Validation

Run `python3 bin/skillctl list` to see the current layout. Before opening a PR, ensure:

1. `skills-ref validate` passes on every skill directory.
2. Plugin manifest `name` matches the directory name.
3. Skill names are globally unique.
4. Skills follow the design spec and criteria of the `skill-creator` skill.
5. No personal data patterns (see above).

CI runs all of these automatically in `.github/workflows/validate.yml`.

## Constraints

- All changes merged to `main` via pull request. No direct pushes to `main`.
- Commit titles follow [Conventional Commits](https://www.conventionalcommits.org/).
- A single skill directory must remain a valid drop-in copy: `cp -r plugins/<plugin>/skills/<skill> ~/.claude/skills/` works with zero repo tooling.
