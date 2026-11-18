# incident-trace

Trace reported production incidents end-to-end through backend services from Grafana/Synapse Loki logs: find which streams carried the session, check per-hop receipts (counts, totals, completion markers), apply the negative-evidence gate for "never happened" claims, attribute id-less log lines properly, and report a verdict with evidence classes and reproduction queries.

- `SKILL.md` — the 6-step method.
- `references/query-discipline.md` — concrete LogQL recipes and the flake/load rules for the query wrapper.
- `references/case-example.md` — one real incident traced step by step.
- The `synapse` skill owns the general Grafana/Loki/Mimir query mechanics; this skill calls it for the querying layer.
