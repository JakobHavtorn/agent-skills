# synapse

Answer observability questions through the Synapse MCP server over the Grafana stack: Mimir metrics (PromQL), Loki logs (LogQL), Pyroscope profiles, dashboards, and alert rules. Discovery-first querying: verify labels, metric names, and datasources before interpreting an empty result.

- `SKILL.md` — principles, the task-to-tool map, and worked patterns.
- `references/logql.md` — LogQL syntax and the Loki tool quirks.
- `references/promql.md` — PromQL on Mimir and the discovery workflow.

`incident-trace` calls this skill for query mechanics; this skill stays general.
