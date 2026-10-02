# Agent Working Rules

High-level instructions for all coding agents. Installed by `agent-skills` via `skillctl link`.

## Git worktree policy

Before making any file edits, create a git worktree for your changes:

```bash
git worktree add "../$(basename "$(pwd)")-work-$(git rev-parse --abbrev-ref HEAD)" \
  -b "agent/$(date +%Y%m%d-%H%M%S)"
```

Work in the worktree, not the main checkout. Commit there, push from there, open the PR from there.

Never edit files in the main checkout directly. The only exception is read-only investigation — `read`, `grep`, `glob`, `bash` for inspection — which stays in the original directory, or when explicitly instructed by the user to do so.

## Code verification

Before reporting work complete, run the project's test suite or linter on changed files. If no suite exists, smoke-test the changed path directly. Never claim "done" without exercising the change.

## General writing style

Follow the spirit of Strunk and White's *The Elements of Style*. Omit needless words. State the conclusion first, then the evidence.

- Write in active voice. The agent does the verb.
- Prefer the positive form. Say what is true, not what isn't.
- Use parallel structure for coordinate clauses.
- Place the emphatic word last in the sentence.
- Fragments are fine when clearer than a full sentence.
- Cut ceremony, hedging, and recaps. The reader is technical.

## Code comments

Prefer self-documenting code. Clear names reduce the need for comments. When you do comment:

- Document API surfaces — functions, classes, modules — in the project's standard format (docstrings, Go doc comments, etc.). State purpose, inputs, outputs, side effects.
- Use inline comments for decisions, constraints, business rules, workarounds, and external dependencies. Explain why, not what. Don't restate the code.
- Keep comments concise and current. Update or delete when the code changes. Stale comments mislead.
- Skip trivial or self-explanatory code. Don't comment the obvious.
