# Agent Working Rules

High-level instructions for all coding agents. Installed by `agent-skills` via `skillctl link`.

## General writing style

Follow the spirit of Strunk and White's *The Elements of Style*. Omit needless words. State the conclusion first, then the evidence.

- Use simple language. Use established terms; never invent jargon.
- Prefer active voice: the subject performs the action.
- Use the positive form: state what is true.
- Use parallel structure for coordinate clauses.
- Use fragments when they are clearer than full sentences.
- Cut ceremony, hedging, and recaps; write for a technical reader.

## Diagrams

Use [Mermaid](https://mermaid.js/) for diagrams and flowcharts when visual structure aids understanding; skip it for trivial or linear content. Use the `mermaid` skill when available for current syntax across diagram types.

## Code comments

Prefer self-documenting code; clear names reduce the need for comments. When you do comment:

- Prefer docstrings over inline comments. Document functions, methods, and classes in the project's standard format. State purpose, inputs, outputs, and side effects where the signature and types don't make them obvious.
- Reserve inline comments for line-specific context. Explain why, not what/
- Keep comments concise and current. Update or delete them when the code changes; stale comments mislead.

## Git worktree policy

Make all edits in a git worktree, not the main checkout. Read-only investigation (`read`, `grep`, `glob`, inspection with `bash`) can stay in the main checkout. Edit the main checkout only when the user explicitly says to.

Create the worktree before the first edit. Name the branch with a short descriptive slug, plus a ticket reference when one is available, e.g. `fix-worktree-policy-SR-1234`:

```bash
slug="<descriptive-slug>"
root="$(git rev-parse --show-toplevel)"
git worktree add "$root/../$(basename "$root")-$slug" \
  -b "agent/$(date +%Y%m%d-%H%M%S)-$slug"
```

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