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
