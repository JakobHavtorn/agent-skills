---
name: open-pr
description: Create or update a pull request on the current branch. Lints and tests the change, commits and pushes, then uses `gh api` (REST) to open or update the PR with a Linear-linked description.
---

## Overview

Drive a pull request on the current branch to a review-ready state: linted, tested, committed, pushed, and either freshly opened or updated. The skill is intentionally specific about which `gh` surface it uses — `gh api` (REST) works reliably across this org's GitHub projects, while `gh pr edit --project` and the GraphQL-backed Projects mutations hit deprecation errors on classic Projects fields.

---

## Step 1 — Lint the changed files

Pick the linter that matches the repo. If the repo has multiple languages, run each linter that applies to the changed files.

| Repo | Lint command |
| --- | --- |
| Go | `golangci-lint run ./...` (or scope to changed packages) |
| Python | `ruff check .` (or `ruff check <changed files>`; via `uv run ruff check` / `poetry run ruff check` if that's how the repo manages its env) |
| JS/TS | Prefer the repo's own script — check `package.json` for `lint`, `format.fix`, `typecheck`. Typical combo: `npm run format.fix && npm run typecheck`. |

Fix every reported issue before moving on. Do not silence rules to make the linter pass.

---

## Step 2 — Run the test suite

Run the repo's full test command and confirm it passes:

- Go: `go test ./...`
- Python: `pytest` (or `uv run pytest` / `poetry run pytest`, matching how the repo manages its env)
- JS/TS: `npm run test` (or the script declared in `package.json`)

If a test fails because of the change, fix the code — not the test. If a test is unrelated and pre-existing red, surface it to the user before proceeding rather than opening a PR on top of a broken main.

---

## Step 3 — Commit and push

Stage only the files relevant to this change (`git add <files>` — avoid `git add -A` so stray local files like `.env`, dumps, or scratch recordings don't sneak in). Write a conventional-commit-style message (`feat:`, `fix:`, `refactor:`, etc.).

Push the branch, setting upstream if it isn't tracked yet:

```bash
git push -u origin HEAD
```

---

## Step 4 — Resolve the Linear ticket ID

Branch names in this org typically encode the Linear ticket, e.g. `improve-transcripts-ux-debug-tooling-and-auth-proxying-in-sr-2522` → `SR-2522`. Extract the trailing `[A-Z]+-\d+` token from the current branch:

```bash
git rev-parse --abbrev-ref HEAD | grep -oE '[A-Z]+-[0-9]+$' | tr '[:lower:]' '[:upper:]'
```

If the branch has no ticket suffix, ask the user for the ID before drafting the description rather than guessing or omitting it.

---

## Step 5 — Draft the PR description

Use this template verbatim (GitHub-flavored Markdown):

```markdown
## Summary

<2–5 bullets describing what changed and why. Reference the Linear ticket inline, e.g. "Addresses SR-2522 by ...">

## Linear

Closes SR-2522
```

Rules:

- **Use the `Closes` magic word** (e.g. `Closes [SR-2522](https://linear.app/corti/issue/SR-2522)`). Closing words move the issue to *In Progress* when the branch is pushed and to *Done* or *QA* when the PR merges to the default branch. The full set of closing words: close, closes, closed, closing, fix, fixes, fixed, fixing, resolve, resolves, resolved, resolving, complete, completes, completed, completing, implement, implements, implemented, implementing.
- **Use a non-closing word if asked** (e.g. `Refs [SR-2522](https://linear.app/corti/issue/SR-2522)`). These create the link and move the issue through configured statuses but do **not** move it to QA status on merge. Non-closing words: ref, refs, references, part of, related to, relates to, contributes to, toward, towards.
- A magic word + full URL (e.g. `Closes https://linear.app/corti/issue/SR-2522`) or plain ticket (e.g. `Closes SR-2522`) works too.
- **No "Test plan" section.** Leave it out entirely — this org's PR conventions don't include one for routine changes.
- Focus the summary on the *why*, not a file-by-file recap. The diff already covers the *what*.
- **PR titles must follow conventional commit format.** Many repos in this org gate the PR title with a `pr_title_check` GitHub Action (`corticph/actions/verify-commit-message`), so a non-conventional title fails CI. Check `.github/workflows/pr_title_check.yml` in the target repo for the exact valid `scopes` (it defines an `env.scope` regex) and match it — the action only enforces scopes, not types, but prefer the standard `feat:`, `fix:`, `refactor:`, `chore:`, `docs:` etc. Also keep the title under 70 chars and imperative ("Add X", "Fix Y").

---

## Step 6 — Create or update the PR via `gh api`

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
<description from Step 5>
EOF
)"
```

### If a PR exists — update it

```bash
gh api repos/{owner}/{repo}/pulls/<number> \
  --method PATCH \
  -f title="<PR title>" \
  -f body="$(cat <<'EOF'
<description from Step 5>
EOF
)"
```

Print the PR URL at the end so the user can click straight through.

---

## Key rules

- **Use `gh api` (REST), never GraphQL.** `gh pr edit --project ...` and the GraphQL Projects mutations hit deprecation errors on classic Projects fields.
- **Never pass `--project`** to any `gh pr` command.
- **Don't skip hooks** (`--no-verify`) on the commit or push.
- **Don't rewrite history** (no `--amend`, no `git rebase -i`) unless the user explicitly asks.
