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
bin/skillctl                          # install / link / doctor
tests/<skill>/cases.md                # trigger + behavior test cases
```

Skills are discovered only from immediate children of `skills/`. Nested subdirectories would break discovery. CI rejects any `SKILL.md` not at exactly `plugins/<plugin>/skills/<skill>/SKILL.md`.

## Frontmatter rules

Only the six spec-defined fields may appear at top level: `name`, `description` (required), `license`, `compatibility`, `metadata`, `allowed-tools` (optional). Custom properties go inside `metadata` (string-to-string map, reverse-DNS keys).

- `name` must match the parent directory name exactly and be unique across the entire repo.
- `description` must state both *what* the skill does and *when* to use it (a "use when" clause). This field controls activation.
- No `license` field — the root `LICENSE` file governs everything.

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

- All changes merged to `main` via pull request.
- Commit titles follow [Conventional Commits](https://www.conventionalcommits.org/).
- A single skill directory must remain a valid drop-in copy: `cp -r plugins/<plugin>/skills/<skill> ~/.claude/skills/` works with zero repo tooling.
