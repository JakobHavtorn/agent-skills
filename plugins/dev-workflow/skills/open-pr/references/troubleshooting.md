# Troubleshooting

Common errors encountered during the PR workflow and how to resolve them.

## Merge Conflicts During Push

If `git push` is rejected because the remote branch has commits you don't have:

1. Fetch and rebase:
   ```bash
   git fetch origin
   git rebase origin/$(git rev-parse --abbrev-ref HEAD)
   ```
2. Resolve conflicts in each file, then `git add <resolved files>` and `git rebase --continue`.
3. Push again with `git push` (no force needed after rebase).

Do NOT use `git push --force` or `git push -f` unless the user explicitly asks. If the rebase gets stuck, surface the conflict files to the user and let them resolve manually.

## Branch Protection Rules

If `gh pr create` or `gh pr edit` fails with a 422 error mentioning "protected branch":

- The base branch may have protection rules requiring reviews, status checks, or linear history.
- The PR can still be created — the error is about merging, not creating.
- Surface the protection rules to the user so they know what's required before merge.

If `git push` is rejected with "protected branch" or "required status checks":

- You are likely pushing directly to the base branch. The skill should push to a feature branch, not `main`.
- Check the current branch: `git rev-parse --abbrev-ref HEAD`. If it's `main` or `master`, ask the user to create a feature branch first.

## CI Failures After PR Creation

If CI checks fail on the newly created PR:

1. Check which checks failed:
   ```bash
   gh pr checks <PR number>
   ```
2. Surface the failing checks to the user.
3. Do not attempt to fix CI failures automatically — the user should decide whether to fix code, update CI config, or ignore the failure.
4. If the failure is a lint or type error that the local linter missed, note the discrepancy.

## gh Auth Token Expiry

If `gh` commands fail with 401 or "authentication required":

1. Check token status:
   ```bash
   gh auth status
   ```
2. If the token is expired, guide the user through:
   ```bash
   gh auth refresh
   ```
3. If `gh auth refresh` fails, the user may need to re-login from scratch:
   ```bash
   gh auth login
   ```

## No Remote Configured

If `git push` fails with "No configured upstream remote" or "fatal: 'origin' does not appear to be a git repository":

1. Check remotes:
   ```bash
   git remote -v
   ```
2. If no remote exists, ask the user for the repository URL and add it:
   ```bash
   git remote add origin <URL>
   ```
3. If a remote exists but isn't named `origin`, note the actual name and use it in the push command.

## Pre-Commit Hooks Fail

If the commit is rejected by a pre-commit hook:

1. Surface the hook output to the user.
2. Do NOT use `--no-verify` to bypass hooks — the skill's Key Rules explicitly forbid this.
3. Fix the issues the hook identified, re-stage, and commit again.
