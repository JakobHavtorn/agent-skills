# TODO

Future changes and improvements tracked in-repo. No external standard governs this file.

## Testing

- [ ] Add `skillctl test` subcommand — parse `tests/*/cases.md`, send prompts to agent CLI, record pass/fail with model + harness versions to `tests/<skill>/results.md`

## Infrastructure

- [ ] Verify `skillctl` target paths against current client docs (spec §7 notes they drift)
- [ ] Consider `skillctl link --all` flag for installing every plugin at once
- [ ] Add `skillctl doctor --json` output for CI integration

## CI

- [ ] Pin `skills-ref` version in `validate.yml` instead of `npm install -g @anthropic/skills-ref`
- [ ] Add `shellcheck` as a hard fail (currently `|| true` in validate.yml)
- [ ] Add `ruff` as a hard fail for `scripts/` (currently only syntax errors fail)

## New skills

- [ ] **Performance review assistant** — Draft a performance review from transcribed voice notes (via Corti STT) and a submitted self-review. Cross-reference self-assessed goals against Linear ticket activity and Slack updates for evidence of what was actually delivered.
- [ ] **Yahoo Finance data puller** — Fetch historical prices, fundamentals, and portfolio metrics from Yahoo Finance for personal finance tracking. Resolve tickers at runtime from `$SKILLS_DATA_DIR` (no personal data in repo).
