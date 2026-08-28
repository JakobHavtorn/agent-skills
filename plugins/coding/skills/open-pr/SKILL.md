---
name: open-pr
description: >
  Create or update a pull request on the current branch. Lints and tests the change,
  commits and pushes, then opens or updates the PR with a Linear-linked description.
  Prefers `gh pr` commands (simpler, auto-resolves owner/repo), falls back to `gh api`
  (REST) if needed. Triggers: "open a pr", "create pull request", "submit for review",
  "push and pr", "make a pr", "pr this", "pr my branch", "put up a pr", "put this up",
  "send for review", "send it", "ready for review", "ship this", "create pr", "update pr",
  "push my changes for review". Also triggers when a user says "this is ready", "can you
  review this", "let's get this merged", or "open a review". Auto-detects lint and test
  commands for Go, Python, and JS/TS repos.
metadata:
  requires_toolsets: [terminal]
---

## Overview

Drive a pull request on the current branch to a review-ready state: linted, tested, committed, pushed, and either freshly opened or updated. Prefers `gh pr` commands (auto-resolves owner/repo, handles fork detection); falls back to `gh api` (REST) if `gh pr` is unavailable. Never uses `--project` — GraphQL Projects mutations hit deprecation errors on classic Projects fields.

## Defaults

| Parameter | Default if not provided | Rationale |
|---|---|---|
| Base branch | Auto-detected from remote HEAD, falls back to `main` | Matches repo's actual default branch |
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

```bash
gh pr view --json number,url,state 2>/dev/null && echo "GH_PR_AVAILABLE" || echo "GH_PR_UNAVAILABLE"
```

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "DEFAULT_BRANCH_UNKNOWN"
```

**Decision tree:**

1. If `NOT_A_GIT_REPO` → **stop here**. Tell the user to run this skill from within a git repository.
2. If `GH_NOT_INSTALLED` → ask the user to install `gh` (`brew install gh` on macOS). Proceed with Steps 2-4 (lint, test, commit, push) only — no PR creation. Tell the user to create the PR manually via the GitHub URL printed after push.
3. If `GH_NOT_AUTHENTICATED` → guide the user through `gh auth login`, then re-run detection.
4. If `gh` available and authenticated but `GH_PR_UNAVAILABLE` → **Method B** (`gh api` REST fallback) for PR creation/update in Step 7.
5. If `gh` available, authenticated, and `GH_PR_AVAILABLE` → **Method A** (`gh pr` commands, preferred) for PR creation/update in Step 7. Auto-resolves owner/repo, handles fork detection.

Use the detected base branch (from `git symbolic-ref`) in Step 7's `--base` flag. If `DEFAULT_BRANCH_UNKNOWN`, fall back to `main`.

---

## Step 2: Lint the changed files

Pick the linter that matches the repo's language and tooling. If the repo has multiple languages, run each linter that applies to the changed files. See `references/lint-test-commands.md` for the full auto-detection table (Go, Python, JS/TS, pnpm, yarn, env-managed variants, linter-not-installed handling).

**Gate:** Fix every reported issue before moving on. Do not silence rules to make the linter pass. If the linter is not installed (e.g., `golangci-lint: command not found`), surface this to the user — do not skip linting silently.

---

## Step 3: Run the test suite

Run the repo's full test command and confirm it passes. See `references/lint-test-commands.md` for env-managed variants and pre-existing failure handling.

**Gate:** If a test fails because of the change, fix the code — not the test. If a test is unrelated and pre-existing red, surface it to the user before proceeding rather than opening a PR on top of a broken main. Do not push until all relevant tests pass.

---

## Step 4: Commit and push

Before staging, check for unrelated uncommitted changes:

```bash
git status --porcelain
```

**Gate:** If `git status --porcelain` shows files that are unrelated to this change (e.g., modified files you didn't touch as part of the work), surface them to the user. Do not stage files you didn't change — stage only the files relevant to this change (`git add <files>` — avoid `git add -A` so stray local files like `.env`, dumps, or scratch recordings don't sneak in).

Write a conventional-commit-style message (`feat:`, `fix:`, `refactor:`, etc.).

Before pushing, check if the branch already has unpushed commits:

```bash
git log origin/$(git rev-parse --abbrev-ref HEAD)..HEAD --oneline 2>/dev/null
```

**Gate:** If there are no unpushed commits AND the remote is already up to date, surface this to the user — there may be nothing new to push. Proceed only if the user confirms.

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

**Gate:** If the branch has no ticket suffix, ask the user for the ID before drafting the description. Do not guess or omit the Linear section without confirming.

---

## Step 6: Draft the PR description

Use the template from `references/pr-template.md` verbatim. The core structure:

```markdown
## Summary

- <2-5 bullets describing what changed and why>

## Linear

Closes <TICKET-ID>
```

Read `references/pr-template.md` for the full template with examples, multiple-ticket handling, and summary guidelines. Read `references/linear-linking.md` for closing vs non-closing words, URL formats, and PR title conventions.

**Gate:** If the ticket ID from Step 5 is unresolved (user couldn't provide one) AND no Linear section can be written, confirm with the user that they want to proceed without a Linear link before continuing. Do not silently omit the section.

---

## Step 7: Create or update the PR

First, check whether a PR already exists for the current branch (works with both methods):

```bash
gh pr view --json number,url,state 2>/dev/null
```

**Gate:** If the PR `state` is `MERGED` or `CLOSED`, surface this to the user. Do not attempt to update a merged or closed PR — ask whether to create a new PR or reopen (if closed and reopenable).

### Method A — `gh pr` (preferred, if detected in Step 1)

If no PR exists — create one:

```bash
gh pr create \
  --title "<PR title>" \
  --body "$(cat <<'EOF'
<description from Step 6>
EOF
)" \
  --base <base branch>
```

If a PR exists — update it:

```bash
gh pr edit <number> \
  --title "<PR title>" \
  --body "$(cat <<'EOF'
<description from Step 6>
EOF
)"
```

### Method B — `gh api` REST fallback (if `gh pr` unavailable)

If no PR exists — create one:

```bash
gh api repos/{owner}/{repo}/pulls \
  --method POST \
  -f title="<PR title>" \
  -f head="<branch>" \
  -f base="<base branch>" \
  -f body="$(cat <<'EOF'
<description from Step 6>
EOF
)"
```

If a PR exists — update it:

```bash
gh api repos/{owner}/{repo}/pulls/<number> \
  --method PATCH \
  -f title="<PR title>" \
  -f body="$(cat <<'EOF'
<description from Step 6>
EOF
)"
```

**Gate:** If the PR creation or update fails (e.g., 401 auth error, 422 validation error), surface the full error to the user. Do not retry silently or switch methods without informing the user.

---

## Step 8: Respond to the user

### If all steps succeeded

```
1. **PR URL**: <PR URL>
2. **Summary**:
   - <bullet mirroring PR description bullet 1>
   - <bullet mirroring PR description bullet 2>
3. **Quality checks**:

   | Check | Result |
   |---|---|
   | Lint | pass / fail / skipped (reason) |
   | Tests | pass / fail / skipped (reason) |
   | Files changed | <N> |
4. **Linear link**: <TICKET-ID> — <closing word> (e.g., "Closes SR-2522")
5. **Next steps**:
   - Request reviewers on the PR
   - Address CI feedback if checks fail
   - <any other relevant follow-up>
```

If any quality check was skipped or failed, the Next steps section must call this out explicitly.

### If a gate stopped the process early

```
1. **Status**: blocked
2. **Step failed**: <step number and name>
3. **Error**: <what went wrong>
4. **Files changed**: <N> (if any before the gate)
5. **Next steps**: <action to resolve> — see `references/troubleshooting.md`
```

---

## Key rules

- **Prefer `gh pr` over `gh api`** — auto-resolves owner/repo, handles fork detection. Use `gh api` only as fallback.
- **Never pass `--project`** to any `gh pr` command — GraphQL Projects mutations hit deprecation errors.
- **Don't skip hooks** (`--no-verify`) or **rewrite history** (`--amend`, `rebase -i`) unless the user explicitly asks.

## Reference Files
- `references/lint-test-commands.md` — Auto-detection table for lint/test commands (Go, Python, JS/TS, env-managed variants, linter-not-installed, pre-existing failures)
- `references/pr-template.md` — PR description template with examples, multiple-ticket handling, and summary guidelines
- `references/linear-linking.md` — Linear closing/non-closing words, URL formats, PR title conventions
- `references/troubleshooting.md` — Merge conflicts, branch protection, CI failures, gh auth expiry, no remote, pre-commit hook failures
