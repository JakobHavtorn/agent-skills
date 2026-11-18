# TODO

Future changes and improvements tracked in-repo. No external standard governs this file.

## Testing

- [x] Add `skillctl test` subcommand — parse `tests/*/cases.json`, send prompts to agent CLI, record pass/fail with model + harness versions to `tests/<skill>/results.json`

## Infrastructure

- [ ] Verify `skillctl` target paths against current client docs (spec §7 notes they drift)
- [ ] Consider `skillctl link --all` flag for installing every plugin at once
- [ ] Add `skillctl doctor --json` output for CI integration
- [x] Add `skillctl prune` — dry run by default; `--apply` removes dangling links whose
  target was deleted from this repo; `--apply --orphans` also removes stale copies
- [ ] Standardize harness-spill JSON envelope unwrapping across plugin scripts (each handles `[{type, text}]` differently)

## CI

- [ ] Pin `skills-ref` version in `validate.yml` instead of `npm install -g @anthropic/skills-ref`
- [x] Add `shellcheck` as a hard fail (currently `|| true` in validate.yml)
- [x] Add `py_compile` syntax check as a hard fail for `scripts/` and `bin/` (was `|| true` in validate.yml)

## New skills

- [ ] **Performance review assistant** — Draft a performance review from transcribed voice notes (via Corti STT) and a submitted self-review. Cross-reference self-assessed goals against Linear ticket activity and Slack updates for evidence of what was actually delivered.
- [ ] **Yahoo Finance data puller** — Fetch historical prices, fundamentals, and portfolio metrics from Yahoo Finance for personal finance tracking. Resolve tickers at runtime from `$SKILLS_DATA_DIR` (no personal data in repo).

## Considerations

- [ ] **External skill sources vs. pinned vendoring** — Could agent-skills own `npx skills add`-style sourcing of third-party skills, so the dotfiles repo no longer carries installation calls? Upstream-maintained skills (e.g. grafana/skills) could then flow in without our controlling updates — acceptable for Grafana, not for the Pocock skills, which stay pin-controlled via `metadata.vendored-from`. Open question: is this a clean addition (a skillctl subcommand or sources manifest that materializes upstream skills at link time) or a dirty one (a second update paradigm that fights the vendored-from pins, `vendor-status`, and CI validation)?
