# Test Cases: open-pr

## Should trigger

1. "Open a PR for this branch" — after making code changes
2. "Push and PR this" — after completing a feature
3. "Ship this to review" — when code is ready
4. "This is ready, can you review this?" — signaling readiness
5. "Put this up for review" — after finishing a bugfix

## Should NOT trigger

1. "Review the code in this PR" — that's review-pr-comments, not opening a PR
2. "What's the CI status on my PR?" — checking status, not creating
3. "Merge this PR" — merging, not opening

## Expected behavior

- Runs lint and tests appropriate to the repo (Go, Python, JS/TS)
- Commits uncommitted changes and pushes to remote
- Creates or updates the PR using `gh pr create` / `gh pr edit`
- Falls back to `gh api` (REST) if `gh pr` is unavailable
- Links Linear issues in the PR description
- Never uses `--project` (GraphQL Projects deprecation)
- Reports the PR URL back to the user
