# PromQL on Mimir

Mimir is long-term, horizontally scalable Prometheus: PromQL is identical. Query it through `query_prometheus`, and discover first with the `list_prometheus_*` tools.

Sources: the [Prometheus querying docs](https://prometheus.io/docs/prometheus/latest/querying/basics/), the [Grafana Mimir docs](https://grafana.com/docs/mimir/latest/), and Grafana's official [promql skill](https://github.com/grafana/skills).

## Discovery workflow

1. `list_datasources` with type `prometheus` → the datasource uid (Mimir presents as type `prometheus`).
2. `list_prometheus_metric_names` with a `regex` (e.g. `.*_bucket$`, or `.*latency.*|.*duration.*`) — call this before writing any expression.
3. `list_prometheus_label_values` for the labels you will filter on (`service_name`, `cluster`, `job`).
4. `list_prometheus_metric_metadata` for a metric's type and help text.

Never query a metric name you have not seen in a listing — the empty result is indistinguishable from a typo.

## Core expressions

```promql
up == 0                                                   # target down (instant)
rate(http_requests_total[5m])                             # per-second rate of a counter
sum by (service_name) (rate(http_requests_total[5m]))
sum(rate(errors_total[5m])) / sum(rate(requests_total[5m]))   # error ratio
histogram_quantile(0.95, sum by (le) (rate(http_duration_seconds_bucket[5m])))
avg_over_time(memory_usage_bytes[10m])                    # gauge, not counter
topk(5, sum by (pod) (rate(http_requests_total[5m])))
```

- Counters (names ending `_total`, `_count`, or the `le`-bucket form) need `rate` or `increase` with a window; gauges are read directly or with `avg_over_time` / `max_over_time`.
- For percentiles, prefer `query_prometheus_histogram`: it builds the `histogram_quantile` expression from the base metric name (without `_bucket`), a percentile, and label selectors.
- Aggregate before returning series: `sum by (...)` and `topk` keep answers readable; hundreds of raw series waste context.

## Instant vs range

- Instant (`queryType: instant`, `endTime` only): one value per series — for now, or for one window when the expression embeds the window (`rate(x[5m])`).
- Range (`queryType: range`, `startTime` + `endTime` + `stepSeconds`): a time series per step. Step the query, not the window: a 24h span at `stepSeconds: 3600` is 24 points.

## Mimir-specific notes

- PromQL is unchanged; Mimir adds a query frontend that splits and caches queries. Repeated identical range queries may come back from cache, and a 5xx from the frontend deserves a brief back-off and retry, not a re-fire storm.
- Retention is long-term: months-old data is queryable, so bound time ranges explicitly rather than relying on defaults.
- High-cardinality exploration is expensive: use the narrowest label matchers and the shortest useful window while exploring; widen only what the question needs.
