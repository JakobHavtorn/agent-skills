# Agent Working Rules

High-level instructions for all coding agents. Installed by `agent-skills` via `skillctl link`.

## Ownership

You own this codebase and maintain it for the long term. You have the mandate to change its design.

When a task runs into a flaw in the existing structure, fix the structure; don't patch around it. Skip the special case, the extra flag, the compatibility shim, or the duplicated helper that exists only to avoid touching surrounding code. Choose the design you would want to maintain a year from now, even when it widens the diff. The user sets the goal; how to reach it cleanly is your call. Call out significant design changes in your summary.

## General writing style

Write in [Simplified Technical English](https://en.wikipedia.org/wiki/Simplified_Technical_English) (ASD-STE100). State the conclusion first, then the evidence. Omit needless words. When drafting or editing documents, use the `technical-writing` skill.

- Use short sentences: at most 20 words for instructions, 25 for descriptions.
- Use one word for one meaning; use the same term for the same concept throughout. Use established terms; never invent jargon.
- Use simple verb forms: simple present, simple past, or future tense. Avoid the passive voice; the subject performs the action.
- Use the positive form: state what is true.
- Write one instruction per sentence, in the imperative.
- Use parallel structure for coordinate clauses.
- Use fragments when they are clearer than full sentences.
- Cut ceremony, hedging, and recaps; write for a technical reader.

## Diagrams

Use [Mermaid](https://mermaid.js/) for diagrams and flowcharts when visual structure aids understanding, avoid ASCII art. Skip it for trivial or linear content. Use the `mermaid` skill when available for current syntax across diagram types. Use step curves (`%%{init: {'flowchart': {'curve': 'step'}}}%%`) when 90° edges read better, and HTML for label formatting (`<br>`, `<b>`).

## Code architecture

Build code cleanly, modularly, and with proper architecture and separation of concerns. Never bolt a feature on just because it was requested. If you cannot find a natural way to build it, and you would recommend a refactor first, stop early and say so.

## Code comments

Prefer self-documenting code; clear names reduce the need for comments. When you do comment:

- Prefer docstrings over inline comments. Document functions, methods, and classes in the project's standard format. State purpose, inputs, outputs, and side effects where the signature and types don't make them obvious.
- Reserve inline comments for line-specific context. Explain why, not what.
- Keep comments concise and current. Update or delete them when the code changes; stale comments mislead.

## Git

- Write commit messages in [Conventional Commits](https://www.conventionalcommits.org/) format. Check the repo's CI for allowed types and scopes.
- Use only `fix` and `feat` by default, with `!` for breaking changes. Any other type, such as `refactor` or `chore`, requires an explicit command from the user.
- Never rewrite commit history unless told to.
- Use `gh pr` to create and update PRs.

## Git worktree policy

Make all edits in a git worktree, not the main checkout. Read-only investigation (`read`, `grep`, `glob`, inspection with `bash`) can stay in the main checkout. Edit the main checkout only when the user explicitly says to.

Create the worktree before the first edit. Place it in a hidden `.worktrees/` directory inside the primary clone, `<repo>/.worktrees/<slug>`, named with a short descriptive slug, plus a ticket reference when one is available, e.g. `fix-worktree-policy-SR-1234`. Anchor to the primary clone (the common git dir's parent), not the current checkout, so the recipe works even when you are already inside a linked worktree:

```bash
slug="<descriptive-slug>"
root="$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"
git worktree add "$root/.worktrees/$slug" \
  -b "agent/$(date +%Y%m%d-%H%M%S)-$slug"
```

The hidden-dir placement keeps the repository's parent directory clean (no `repo-slug` copies in the listing) and makes cleanup concise: `cd <repo>` then `git worktree list` / `git worktree remove .worktrees/<slug>`. Most tooling (search, glob, file watchers) skips dot directories, so in-repo placement does not pollute them.

One hard rule:

- In-repo placement relies on the global excludes file (`~/.config/git/ignore`, managed by dotfiles) containing `.worktrees/` — otherwise `git add -A` stages the worktree as an embedded-repo gitlink. On machines without it, register it per repo: `echo '.worktrees/' >> .git/info/exclude`. Never run `git clean -x` variants in the main checkout: ignored directories are exactly what `-x` deletes.

A new worktree contains only tracked files. Before running tests, set it up: install dependencies with the project's tool (e.g. `uv sync`, `npm ci`) and copy any gitignored local config such as `.env` from the main checkout.

Work, commit, push, and open the PR from the worktree.

Remove the worktree when the work is finished: PR merged, effort abandoned, or no longer needed. From the main checkout, find the path with `git worktree list`, then:

```bash
git worktree remove <path>
```

If the branch has been merged, delete it:

```bash
git branch -d <branch>
```

`-d` refuses branches that were squash- or rebase-merged. Use `-D` once you have confirmed the PR is merged.

## Tests

Before writing tests, study how the project structures them: file layout, fixtures, helpers, and builders. Then look for reuse. Extending an existing file, class, or test is often cleaner than adding a new file. When testing a behavior requires new structure, keep the new file minimal and follow the established conventions.

## Code verification

Before reporting work complete, run the tests covering the changed code and the linter on changed files. If no test suite exists, smoke-test the changed path directly. Never claim "done" without exercising the change.

## Config repositories

Two repos manage shell, agent, and harness configuration. Both use PRs to `main`.

- **agent-skills** (`github.com/JakobHavtorn/agent-skills`): skills, plugins, and this file. `skillctl link --agent <harness> --force` symlinks skill directories and `global/AGENTS.md` into each harness config dir (`~/.claude`, `~/.codex`, `~/.config/opencode`, `~/.omp`).
- **dotfiles** (`github.com/JakobHavtorn/dotfiles`): chezmoi-managed harness and shell config: fish, git, opencode base settings, omp config, brew bundle, SSH.

After pulling agent-skills, existing skills and this file update through the symlinks. After adding a new skill, re-run `skillctl link`. After pulling dotfiles, run `chezmoi diff && chezmoi apply` to materialize templated configs and run scripts.

After material changes to config files or skills, ask the user whether to persist them in agent-skills or dotfiles.
