---
name: resolve-merge-conflicts
description: "Work through an in-progress git merge or rebase conflict hunk by hunk, resolving by intent traced to each side's primary source, then finish the operation (never `--abort`). This skill should be used when the user needs to resolve merge or rebase conflicts, or asks for help with a conflicted working tree."
---

## Step 1: See the current state

See the current state of the merge/rebase. Check git history, and the conflicting files.

## Step 2: Find the primary sources

Find the primary sources for each conflict. Understand deeply why each change was made, and what the original intent was. Read the commit messages, check the PRs, check original issues/tickets.

## Step 3: Resolve each hunk

Preserve both intents where possible. Where incompatible, pick the one matching the merge's stated goal and note the trade-off. Do **not** invent new behaviour. Always resolve; never `--abort`.

## Step 4: Run the automated checks

Discover the project's automated checks and run them, typically typecheck, then tests, then format. Fix anything the merge broke.

## Step 5: Finish the merge/rebase

Stage everything and commit. If rebasing, continue the rebase process until all commits are rebased.
