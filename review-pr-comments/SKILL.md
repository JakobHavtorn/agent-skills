---
name: review-pr-comments
description: Address PR review comments by fetching all review comments via gh api, assessing which warrant code changes, implementing those changes, and running the linter. Does not commit or push.
---

# /review-pr-comments - Address PR Review Comments
1. Fetch ALL review comments using `gh api repos/{owner}/{repo}/pulls/{pr}/comments`
2. Also fetch review-level comments via `gh api repos/{owner}/{repo}/pulls/{pr}/reviews`
3. For each comment, report to the user with an assessment of whether the comment warrants code changes
4. For comments that do warrant code changes, implement the requested changes in the codebase, ensuring to:
   - Only change what's necessary to address the comment, avoiding unrelated refactors or improvements
   - Preserve existing code style and formatting
   - Avoid changing error messages, logging, or behavior beyond what's requested
5. Run linter after all changes
6. Do not commit or push changes; just prepare the code locally for review by the user before they decide to commit and push.
