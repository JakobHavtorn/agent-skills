# Lint and Test Auto-Detection

How to detect and run the correct linter and test suite for a repository based on its tooling.

## Lint Commands

If the repo has multiple languages, run each linter that applies to the changed files (not the entire repo).

| Language | Detection signal | Lint command |
|---|---|---|
| Go | `go.mod` present, or `*.go` files changed | `golangci-lint run ./...` (or scope to changed packages) |
| Python | `pyproject.toml` / `setup.py` present, or `*.py` files changed | `ruff check .` (or `ruff check <changed files>`) |
| Python (env-managed) | `uv.lock` present | `uv run ruff check .` |
| Python (env-managed) | `poetry.lock` present | `poetry run ruff check .` |
| JS/TS | `package.json` present | Check for `lint`, `format.fix`, `typecheck` scripts. Typical combo: `npm run format.fix && npm run typecheck` |
| JS/TS (pnpm) | `pnpm-lock.yaml` present | `pnpm run lint && pnpm run typecheck` |
| JS/TS (yarn) | `yarn.lock` present | `yarn lint && yarn typecheck` |

## Test Commands

| Language | Detection signal | Test command |
|---|---|---|
| Go | `go.mod` present | `go test ./...` |
| Python | `pyproject.toml` / `setup.py` present | `pytest` |
| Python (env-managed) | `uv.lock` present | `uv run pytest` |
| Python (env-managed) | `poetry.lock` present | `poetry run pytest` |
| JS/TS | `package.json` present | `npm run test` (or the script declared in `package.json`) |
| JS/TS (pnpm) | `pnpm-lock.yaml` present | `pnpm test` |
| JS/TS (yarn) | `yarn.lock` present | `yarn test` |

## Linter Not Installed

If the detected linter is not installed (e.g. `golangci-lint: command not found`):

1. Surface this to the user — do not skip linting silently.
2. Provide the install command: `brew install golangci-lint` (Go), `pip install ruff` or `uv add ruff` (Python).
3. If the user declines to install, proceed but note the lint gap in the output.

## Pre-Existing Test Failures

If tests fail but the failures are unrelated to the current change:

1. Run `git stash && <test command> && git stash pop` to confirm the failure exists on the base branch.
2. If the failure is pre-existing, surface it to the user before proceeding.
3. Do not proceed on top of a broken main — ask the user whether to proceed anyway.
