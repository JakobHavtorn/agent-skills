---
name: open-pr
description: >
  Create or update a pull request on the current branch. Lints and tests the change,
  commits and pushes, then uses `gh api` (REST) to open or update the PR with a
  Linear-linked description. Triggers: "open a pr", "create pull request", "submit for
  review", "push and pr", "make a pr", "pr this", "put up a pr", "send for review",
  "ready for review", "ship this", "create pr", "update pr", "push my changes for review".
  Also triggers when a user says "this is ready", "can you review this", or "let's get
  this merged". Auto-detects lint and test commands for Go, Python, and JS/TS repos.
---

## Overview

Drive a pull request on the current branch to a review-ready state: linted, tested, committed, pushed, and either freshly opened or updated. Uses `gh api` (REST) which works reliably across this org's GitHub projects, while `gh pr edit --project` and GraphQL-backed Projects mutations hit deprecation errors on classic Projects fields.

## Defaults

| Parameter | Default if not provided | Rationale |
|---|---|---|
| Base branch | `main` | Standard default branch in this org |
| PR title | Derived from commit message subject | Conventional commit format already enforced |
| Draft mode | No (ready for review) | Skill targets review-ready PRs |
| Lint command | Auto-detected from repo tooling | Matches repo's own configuration |
| Test command | Auto-detected from repo tooling | Matches repo's own configuration |
| Commit style | Conventional commits | Org convention, enforced by CI |
| Linear ticket | Auto-extracted from branch name | Branches typically encode ticket ID |
| Linear close word | `Closes` | Moves issue through full status pipeline on merge |

---

## Step 1: Detection Flow

Run these checks before doing anything else:

```bash
command -v gh 2>/dev/null && gh --version 2>&1 | head -1 || echo "GH_NOT_INSTALLED"
```

```bash
gh auth status 2>&1 | head -3 || echo "GH_NOT_AUTHENTICATED"
```

```bash
git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "NOT_A_GIT_REPO"
```

**Decision tree:**

1. If `NOT_A_GIT_REPO` → **stop here**. Tell the user to run this skill from within a git repository.
2. If `GH_NOT_INSTALLED` → ask the user to install `gh` (`brew install gh` on macOS). Proceed with Steps 2-4 (lint, test, commit, push) only — no PR creation. Tell the user to create the PR manually via the GitHub URL printed after push.
3. If `GH_NOT_AUTHENTICATED` → guide the user through `gh auth login`, then continue with the full path.
4. If `gh` available and authenticated → **full path** (all steps). Preferred.

---

## Step 2: Lint the changed files

Pick the linter that matches the repo. If the repo has multiple languages, run each linter that applies to the changed files.

| Repo | Lint command |
| --- | --- |
| Go | `golangci-lint run ./...` (or scope to changed packages) |
| Python | `ruff check .` (or `ruff check <changed files>`; via `uv run ruff check` / `poetry run ruff check` if that's how the repo manages its env) |
| JS/TS | Prefer the repo's own script — check `package.json` for `lint`, `format.fix`, `typecheck`. Typical combo: `npm run format.fix && npm run typecheck`. |

**Gate:** Fix every reported issue before moving on. Do not silence rules to make the linter pass. If the linter is not installed (e.g., `golangci-lint: command not found`), surface this to the user — do not skip linting silently.

---

## Step 3: Run the test suite

Run the repo's full test command and confirm it passes:

- Go: `go test ./...`
- Python: `pytest` (or `uv run pytest` / `poetry run pytest`, matching how the repo manages its env)
- JS/TS: `npm run test` (or the script declared in `package.json`)

**Gate:** If a test fails because of the change, fix the code — not the test. If a test is unrelated and pre-existing red, surface it to the user before proceeding rather than opening a PR on top of a broken main. Do not push until all relevant tests pass.

---

## Step 4: Commit and push

Stage only the files relevant to this change (`git add <files>` — avoid `git add -A` so stray local files like `.env`, dumps, or scratch recordings don't sneak in). Write a conventional-commit-style message (`feat:`, `fix:`, `refactor:`, etc.).

Push the branch, setting upstream if it isn't tracked yet:

```bash
git push -u origin HEAD
```

**Gate:** If the push fails (e.g., no remote configured, permission denied), surface the error to the user. Do not attempt to force-push or rewrite history.

---

## Step 5: Resolve the Linear ticket ID

Branch names in this org typically encode the Linear ticket, e.g. `improve-transcripts-ux-debug-tooling-and-auth-proxying-in-sr-2522` → `SR-2522`. Extract the trailing `[A-Z]+-\d+` token from the current branch (case-insensitive match since branch names are lowercase):

```bash
git rev-parse --abbrev-ref HEAD | grep -oiE '[A-Z]+-[0-9]+$' | tr '[:lower:]' '[:upper:]'
```

If the branch has no ticket suffix, ask the user for the ID before drafting the description rather than guessing or omitting it.

---

## Step 6: Draft the PR description

Use this template verbatim (GitHub-flavored Markdown):

```markdown
## Summary

<2–5 bullets describing what changed and why. Reference the Linear ticket inline, e.g. "Addresses SR-2522 by ...">

## Linear

Closes SR-2522
```

Read `references/linear-linking.md` for the complete Linear linking rules: closing vs non-closing words, URL formats, and PR title conventions for this org.

---

## Step 7: Create or update the PR via `gh api`

First, check whether a PR already exists for the current branch:

```bash
gh pr view --json number,url,state 2>/dev/null
```

### If no PR exists — create one

```bash
gh api repos/{owner}/{repo}/pulls \
  --method POST \
  -f title="<PR title>" \
  -f head="<branch>" \
  -f base="main" \
  -f body="$(cat <<'EOF'
<description from Step 6>
EOF
)"
```

### If a PR exists — update it

```bash
gh api repos/{owner}/{repo}/pulls/<number> \
  --method PATCH \
  -f title="<PR title>" \
  -f body="$(cat <<'EOF'
<description from Step 6>
EOF
)"
```

**Gate:** If the API call fails (e.g., 401 auth error, 422 validation error), surface the full error to the user. Do not retry silently or fall back to `gh pr create` without informing the user.

---

## Step 8: Respond to the user

Present results with these sections:

1. **PR URL**: The GitHub URL of the created or updated PR
2. **Summary**: What was changed (2-5 bullets mirroring the PR description)
3. **Quality checks**: Lint result (pass/fail), test result (pass/fail), files changed count
4. **Linear link**: The ticket ID and closing word used (e.g., "Closes SR-2522")
5. **Next steps**: What the user should do next (request reviewers, address CI feedback, etc.)

---

## Key rules

- **Use `gh api` (REST), never GraphQL.** `gh pr edit --project ...` and the GraphQL Projects mutations hit deprecation errors on classic Projects fields.
- **Never pass `--project`** to any `gh pr` command.
- **Don't skip hooks** (`--no-verify`) on the commit or push.
- **Don't rewrite history** (no `--amend`, no `git rebase -i`) unless the user explicitly asks.

## Reference Files

- `references/linear-linking.md` -- Linear closing words, non-closing words, URL formats, and PR title conventions for this org
