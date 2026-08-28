---
name: review-pr-comments
description: >
  Address PR review comments by fetching all review comments via gh api, assessing
  which warrant code changes, implementing those changes, and running the linter.
  Does not commit or push. Triggers: "address pr review comments", "fix review
  comments", "respond to pr feedback", "handle review comments", "address review
  feedback", "fix pr comments", "reply to review comments", "handle pr feedback",
  "resolve review comments", "process review comments", "review comments",
  "pr comments", "address feedback on pr".
metadata:
  requires_toolsets: [terminal]
---

## Overview

Fetch all review comments and review-level comments on a PR via GitHub's REST API, present an assessment of each comment to the user, and implement code changes for comments that warrant them. Runs the linter after changes but does not commit or push — the user reviews locally before deciding to commit.

---

## Step 1: Detection and prerequisites

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

1. If `NOT_A_GIT_REPO` → stop and tell the user to run this skill from within a git repository.
2. If `GH_NOT_INSTALLED` → stop and ask the user to install `gh` (`brew install gh` on macOS).
3. If `GH_NOT_AUTHENTICATED` → guide the user through `gh auth login`, then re-run detection.

---

## Step 2: Resolve the PR

Auto-detect the PR for the current branch:

```bash
gh pr view --json number,url,state,headRefName 2>/dev/null
```

**Gate:** If no PR is found for the current branch, ask the user for the PR number or URL. Do not guess.

**Gate:** If the PR `state` is `MERGED` or `CLOSED`, surface this to the user. Ask whether they still want to address comments on a merged/closed PR before proceeding.

Note the PR number and the repo's `owner/repo` for API calls:

```bash
gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null
```

---

## Step 3: Fetch all review comments

Fetch both inline review comments and review-level comments in parallel:

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments --paginate
```

```bash
gh api repos/{owner}/{repo}/pulls/{pr}/reviews --paginate
```

- **Inline comments** (`pulls/{pr}/comments`): Line-by-line comments on specific code. Each has `path`, `line`, `body`, `user`, and `state` (whether resolved/dismissed).
- **Review-level comments** (`pulls/{pr}/reviews`): Summary comments left at the review level. Each has `body`, `user`, and `state` (approved, changes_requested, commented, dismissed).

**Gate:** If both endpoints return empty arrays, tell the user there are no review comments to address and stop.

---

## Step 4: Assess each comment

For each comment, present an assessment to the user:

```
### Comment N: <author> on <file:line>

> <comment body excerpt>

**Assessment:** <warrants changes / informational / already addressed / bot-generated / out of scope>
**Reasoning:** <one sentence explanation>
```

Assessment categories:

- **Warrants changes**: The comment identifies a real issue (bug, style violation, missing test, etc.) that requires a code change.
- **Informational**: The comment is a suggestion or question that doesn't require a code change. Note it for the user.
- **Already addressed**: The comment's concern has already been fixed in a previous commit or by another change.
- **Bot-generated**: Comments from bots (dependabot, renovate, codeql, etc.) — usually don't warrant manual code changes.
- **Out of scope**: The comment is valid but unrelated to the current PR's purpose. Surface it but don't change code.

**Gate:** Present all assessments to the user before implementing any changes. Ask the user to confirm which comments they want addressed. Do not silently skip comments.

---

## Step 5: Implement code changes

For each comment the user confirms, implement the requested change:

- Only change what's necessary to address the comment — avoid unrelated refactors or improvements
- Preserve existing code style and formatting
- Avoid changing error messages, logging, or behavior beyond what's requested
- If a comment requests a change that would break existing behavior, surface this to the user before implementing

**Gate:** If a comment is ambiguous or the requested change is unclear, ask the user for clarification rather than guessing.

---

## Step 6: Run the linter

Pick the linter that matches the repo's language and tooling. If the repo has multiple languages, run each linter that applies to the changed files.

| Language | Detection signal | Lint command |
|---|---|---|
| Go | `go.mod` present, or `*.go` files changed | `golangci-lint run ./...` (or scope to changed packages) |
| Python | `pyproject.toml` / `setup.py` present | `ruff check .` (or `ruff check <changed files>`) |
| Python (uv) | `uv.lock` present | `uv run ruff check .` |
| Python (poetry) | `poetry.lock` present | `poetry run ruff check .` |
| JS/TS | `package.json` present | Check for `lint`, `format.fix`, `typecheck` scripts. Typical: `npm run format.fix && npm run typecheck` |
| JS/TS (pnpm) | `pnpm-lock.yaml` present | `pnpm run lint && pnpm run typecheck` |
| JS/TS (yarn) | `yarn.lock` present | `yarn lint && yarn typecheck` |

**Gate:** Fix every reported issue before moving on. Do not silence rules to make the linter pass. If the linter is not installed, surface this to the user — do not skip linting silently.

---

## Step 7: Respond to the user

Do not commit or push changes — prepare the code locally for the user to review before they decide to commit and push.

### If comments were addressed

```
1. **PR**: <PR URL>
2. **Comments assessed**: <total count>
3. **Comments addressed**:

   | # | File | Comment summary | Change made |
   |---|---|---|---|
   | 1 | <file:line> | <excerpt> | <one-line description of change> |
   | 2 | <file:line> | <excerpt> | <one-line description of change> |

4. **Comments skipped**:

   | # | Reason | Comment summary |
   |---|---|---|
   | 3 | Informational | <excerpt> |
   | 4 | Bot-generated | <excerpt> |

5. **Quality checks**:

   | Check | Result |
   |---|---|
   | Lint | pass / fail / skipped (reason) |
   | Files changed | <N> |

6. **Next steps**:
   - Review the changes locally with `git diff`
   - Commit and push when ready
   - Reply to resolved comments on the PR
```

### If no comments warranted changes

```
1. **PR**: <PR URL>
2. **Comments assessed**: <total count>
3. **Result**: No comments required code changes
4. **Next steps**: All comments are informational or already addressed
```

### If a gate stopped the process early

```
1. **Status**: blocked
2. **Step failed**: <step number and name>
3. **Error**: <what went wrong>
4. **Next steps**: <action to resolve>
```

---

## Key rules

- **Do not commit or push** — the user reviews changes locally before deciding to commit.
- **Only change what's necessary** to address each comment — avoid unrelated refactors.
- **Preserve existing code style** and formatting.
- **Present all assessments before implementing** — let the user confirm which comments to address.
