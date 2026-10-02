# Agent Working Rules

High-level instructions for all coding agents. Installed by `agent-skills` via `skillctl link`.

## Worktree policy

Before making any file edits, create a git worktree for your changes:

```bash
git worktree add "../$(basename "$(pwd)")-work-$(git rev-parse --abbrev-ref HEAD)" \
  -b "agent/$(date +%Y%m%d-%H%M%S)"
```

Work in the worktree, not the main checkout. Commit there, push from there, open the PR from there.

Never edit files in the main checkout directly. The only exception is read-only investigation — `read`, `grep`, `glob`, `bash` for inspection — which stays in the original directory, or when explicitly instructed by the user to do so.

## Verification

Before reporting work complete, run the project's test suite or linter on changed files. If no suite exists, smoke-test the changed path directly. Never claim "done" without exercising the change.
