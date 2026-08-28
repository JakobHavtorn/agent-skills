# Test Cases: review-pr-comments

## Should trigger

1. "Address the review comments on PR #42"
2. "Fix the code review feedback on my pull request"
3. "Work through the review comments on this PR"

## Should NOT trigger

1. "Open a PR for this branch" — that's open-pr, not reviewing comments
2. "Review this code for me" — the user wants a review, not to address existing comments
3. "What did the reviewer say about my PR?" — just reading, not acting on comments

## Expected behavior

- Fetches all review comments via `gh api repos/{owner}/{repo}/pulls/{pr}/comments`
- Also fetches review-level comments via `gh api repos/{owner}/{repo}/pulls/{pr}/reviews`
- Reports each comment with an assessment of whether it warrants code changes
- For comments warranting changes: implements only what's necessary, preserving existing style
- Runs the linter after all changes
- Does NOT commit or push — prepares code locally for user review
