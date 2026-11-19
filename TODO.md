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
- [ ] **Investigate a CLI framework for `skillctl`** — `click` or `typer` instead of argparse: better subcommand groups, help text, and typed options. Trade-off to weigh: `skillctl` currently has zero dependencies — `python3 bin/skillctl` runs from a fresh clone with stdlib only (yaml is a lazy import on the test path), and CI plus the weekly sync workflow rely on that.

## CI

- [ ] Pin `skills-ref` version in `validate.yml` instead of `npm install -g @anthropic/skills-ref`
- [x] Add `shellcheck` as a hard fail (currently `|| true` in validate.yml)
- [x] Add `py_compile` syntax check as a hard fail for `scripts/` and `bin/` (was `|| true` in validate.yml)

## New skills

- [ ] **Yahoo Finance data puller** — Fetch historical prices, fundamentals, and portfolio metrics from Yahoo Finance for personal finance tracking. Resolve tickers at runtime from `$SKILLS_DATA_DIR` (no personal data in repo).

## Considerations

- [ ] **External skill sources vs. pinned vendoring** — Could agent-skills own `npx skills add`-style sourcing of third-party skills, so the dotfiles repo no longer carries installation calls? Upstream-maintained skills (e.g. grafana/skills) could then flow in without our controlling updates — acceptable for Grafana, not for the Pocock skills, which stay pin-controlled via `metadata.vendored-from`. Open question: is this a clean addition (a skillctl subcommand or sources manifest that materializes upstream skills at link time) or a dirty one (a second update paradigm that fights the vendored-from pins, `vendor-status`, and CI validation)?
- [ ] **Observability skill routing overlap** — The synapse, incident-trace, and grafana skills overlap on triggers: "why is this query slow" matches promql, prometheus-cardinality-troubleshooter, and synapse; "find slow requests" matches tempo, promql, and synapse; "which service is responsible for a failure" matches incident-trace and synapse. Rethink whether synapse is needed at all, whether incident-trace keeps its broad triggers, and whether the grafana skills should be gated or trimmed (their descriptions dominate the context budget). Candidate shape: synapse reduced to the Synapse MCP tool interface (task-to-tool map, discovery discipline, response quirks) with language questions routed to promql/loki; incident-trace narrowed to incident entry points. Deciding factor: what the model actually invokes when several skills match one prompt.
