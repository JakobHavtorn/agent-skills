---
name: synapse
description: "Answer observability questions through the Synapse MCP server over our Grafana stack: metrics in Mimir via PromQL, logs in Loki via LogQL, profiles in Pyroscope, plus dashboards, alert rules, and datasource discovery. This skill should be used when the user asks anything that needs metrics, logs, profiles, or Grafana data: latency, error-rate, or saturation questions; whether something changed or is down; which service is slow; finding or reading a dashboard; why an alert fired; writing or fixing a PromQL or LogQL query; or exploring labels, metric names, and datasources."
---

# Synapse: querying Grafana, Loki, and Mimir

Synapse is the read-only MCP server over our Grafana instance. Behind it: **Mimir** (metrics, Prometheus-compatible, query with PromQL), **Loki** (logs, query with LogQL), **Pyroscope** (profiles), plus Grafana itself (dashboards, alert rules, contact points, snapshots).

This skill is the querying layer: how to discover what exists, how to shape queries, and how to report answers. Application skills (`incident-trace` is one) call it for mechanics and keep their own method.

Each tool's own description in the session catalog is authoritative for its parameters; tools change between Synapse releases, so read it before the tool's first use in a session.

## Principles

1. **Discover, never guess.** Query from observed names, in order: `list_datasources` → label/metric name lists → label values → query. A well-formed but invented label selector returns the same empty result as no data, so zero hits under an unverified selector is not evidence of absence. Verify the label vocabulary of the datasource you are querying before the first sweep.
2. **Bound every query in time.** Start narrow (the last hour, or the window the question names), widen deliberately. Unbounded or time-only raw scans on busy production streams can overload the query path.
3. **Label matchers before line content.** Select the smallest stream set first (`{service_name="x", ...}`), then filter lines (`|= "id"`).
4. **Aggregate before returning.** A `sum by (...)` or `topk` beats hundreds of raw series. Count matching lines with a `count_over_time` metric query, not an eyeballed list — list results are capped (~100 rows) and a capped return is not the total.
5. **Serialize production queries.** Run one or two at a time; back off briefly after a 5xx instead of re-firing.
6. **Treat tight-window empties as suspect.** Sub-second windows can return false empties, and window boundaries can shift silently; widen and re-run before concluding absence.
7. **Spend context deliberately.** `get_dashboard_summary` / `get_dashboard_property` over full dashboard JSON; steal proven queries from existing dashboards with `get_dashboard_panel_queries`; check stream volume cheaply with `query_loki_stats` before an expensive logs query.

## Task-to-tool map

| Question | Tools |
|---|---|
| Which datasource serves this? | `list_datasources` (filter by type), `get_datasource`, `check_datasources_health` |
| What log labels exist? | `list_loki_label_names`, `list_loki_label_values` |
| What metric labels exist? | `list_prometheus_label_names`, `list_prometheus_label_values` |
| What metrics exist? | `list_prometheus_metric_names` (regex), `list_prometheus_metric_metadata` |
| Metric value now or over time | `query_prometheus` (instant / range), `query_prometheus_histogram` for percentiles |
| Which log lines match? | `query_loki_logs`; `query_loki_stats` first for volume; `query_loki_patterns` for line shapes |
| Does this stream exist at all? | `query_loki_stats` (bare label selector, approximate index counts) |
| Is there a dashboard for X? | `search_dashboards`, then `get_dashboard_summary` / `get_dashboard_property` / `get_dashboard_panel_queries` |
| Why did this alert fire? | `alerting_manage_rules` (list / get / versions), `alerting_manage_routing` for where it went |
| Which functions burn CPU? | `list_pyroscope_profile_types`, then `query_pyroscope` |
| Is this entity healthy? | `get_assertions` |
| A link for a human | `generate_deeplink` (dashboard, panel, or Explore query) |
| Anything else Grafana-side | `grafana_api_request` (GET only) |

## Worked patterns

### A metric question (latency, error rate)

1. `list_datasources` with type `prometheus` → the datasource uid (Mimir presents as type `prometheus`).
2. Discover: `list_prometheus_metric_names` with a regex; `list_prometheus_label_values` for the labels you will filter on.
3. Query: `query_prometheus` — instant for now, range with a step for a trend; `query_prometheus_histogram` builds the `histogram_quantile` expression for you. See `references/promql.md`.
4. Report: datasource, window, the query, the numbers, and a deeplink.

### A log question

1. Datasource: type `loki`.
2. `list_loki_label_names` — build the selector from labels this instance actually has; confirm values with `list_loki_label_values`.
3. Volume check: `query_loki_stats` on the bare selector (cheap, approximate).
4. `query_loki_logs`, time-bounded, limit set; counts via `count_over_time` as an instant query. See `references/logql.md`.

### An alert question

`alerting_manage_rules` with a states filter → get the rule → reproduce its queries against their datasources. The `versions` operation shows what changed and when; `alerting_manage_routing` shows where notifications went.

## Answer shape

Every answer states: the datasource (uid and name), the time window, the exact queries as reproducible LogQL/PromQL blocks, and the numbers read from the results. Separate observed facts from inference. When a human will look at the same data, hand them a `generate_deeplink` link instead of describing navigation.

## Reference files

- `references/logql.md` — LogQL for Synapse: selectors, filters, parsers, metric queries, and the tool's response quirks.
- `references/promql.md` — PromQL on Mimir: the discovery workflow, rate and histogram patterns, instant vs range, Mimir-specific notes.

## Sources

The tool surface mirrors [grafana/mcp-grafana](https://github.com/grafana/mcp-grafana). Query guidance is distilled from the [Loki query docs](https://grafana.com/docs/loki/latest/query/), the [Prometheus querying docs](https://prometheus.io/docs/prometheus/latest/querying/basics/), [Grafana Mimir](https://grafana.com/docs/mimir/latest/), and Grafana's official [grafana/skills](https://github.com/grafana/skills) repository (Apache-2.0).
