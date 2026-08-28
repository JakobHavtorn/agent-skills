# Linear Linking Rules

How to link Linear tickets in PR descriptions so that Linear's GitHub integration moves issues through the correct statuses automatically.

## Closing Words

These words move the issue to *In Progress* when the branch is pushed and to *Done* or *QA* when the PR merges to the default branch.

| Base word | Present tense | Past tense | Gerund |
|---|---|---|---|
| close | closes | closed | closing |
| fix | fixes | fixed | fixing |
| resolve | resolves | resolved | resolving |
| complete | completes | completed | completing |
| implement | implements | implemented | implementing |

Use `Closes` by default unless the user explicitly asks for a non-closing word.

## Non-Closing Words

These create the link and move the issue through configured statuses but do **not** move it to QA status on merge. Use when the PR is partial or related but not the complete fix.

`ref`, `refs`, `references`, `part of`, `related to`, `relates to`, `contributes to`, `toward`, `towards`

## URL Formats

All of these work — the GitHub integration parses them equally:

- `Closes [SR-2522](https://linear.app/corti/issue/SR-2522)` — markdown link (preferred for readability)
- `Closes https://linear.app/corti/issue/SR-2522` — full URL
- `Closes SR-2522` — plain ticket ID

## PR Title Conventions

- **Conventional commit format required.** Many repos in this org gate the PR title with a `pr_title_check` GitHub Action (`corticph/actions/verify-commit-message`).
- Check `.github/workflows/pr_title_check.yml` in the target repo for the exact valid `scopes` (it defines an `env.scope` regex).
- The action only enforces scopes, not types, but prefer the standard: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`, `ci:`.
- Keep titles under 70 chars and imperative ("Add X", "Fix Y").
- No "Test plan" section in the PR body — this org's PR conventions don't include one for routine changes.
- Focus the summary on the *why*, not a file-by-file recap. The diff already covers the *what*.

## Edge Cases

- **Multiple tickets**: Use multiple closing words on separate lines, e.g. `Closes SR-2522\nCloses SR-2518`. Each ticket moves independently.
- **No ticket**: If the branch has no ticket suffix and the user can't provide one, omit the `## Linear` section entirely rather than guessing.
- **Cross-repo PRs**: The Linear URL format stays `https://linear.app/corti/issue/<ID>` regardless of which repo the PR targets.
