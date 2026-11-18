# LogQL on Synapse

LogQL is Loki's query language: a stream selector plus an optional pipeline of filters, parsers, and aggregations. Run it through the Synapse Loki tools: `query_loki_logs` (queries), `query_loki_stats` (stream volume), `query_loki_patterns` (line shapes), `list_loki_label_names` / `list_loki_label_values` (discovery).

Sources: the [LogQL docs](https://grafana.com/docs/loki/latest/query/), cross-checked with Grafana's official [loki skill](https://github.com/grafana/skills) and field use through Synapse.

## Selectors

```logql
{service_name="transcription", k8s_namespace_name="base"}   # exact matchers
{service_name=~"ingress|gateway", env!="dev"}               # regex and negative
```

- At least one non-empty positive matcher is required; `!=` alone is invalid.
- Matchers combine with `,` (AND). Operators: `=`, `!=`, `=~`, `!~`.
- Build selectors from labels this datasource actually has — run `list_loki_label_names` first. Label vocabularies differ per datasource generation; an invented-but-plausible selector returns the same empty result as no data.

## Line filters

```logql
{...} |= "interaction_1234"                        # contains
{...} |~ "timeout|deadline"                        # regex
{...} != "healthcheck" |~ "level=(error|warn)"      # negation, chaining
```

Filters chain left to right; each narrows. Prefer a label matcher over a line filter wherever one exists (index lookup vs full scan). Anchor regex matches to the real format's delimiters: plain `"0 words"` also substring-matches `"260 words"`.

## Parsers and extracted labels

```logql
{...} | json                                       # structured logs
{...} | logfmt
{...} | pattern `<ip> - <method> <path> <status>`
```

After a parser, filter on extracted fields (`| status >= 500`, `| level="error"`) and aggregate over them. `query_loki_patterns` shows the recurring line shapes in a stream — use it to pick a parser or pattern.

## Metric queries

```logql
count_over_time({service_name="x"} |= "err" [5m])                          # line counts
sum by (service_name) (count_over_time({k8s_namespace_name="base"} [1h]))  # grouped
quantile_over_time(0.99, {...} | json | unwrap latency [1m])                 # numeric field
```

- `count_over_time` counts matching lines per stream. For exact totals, run one instant query with the window in the selector (`[<window-s>]`), not a range scan.
- `unwrap` pulls a numeric field out of parsed lines for `quantile_over_time`, `avg_over_time`, and `sum_over_time`.
- Group with `sum by (label)` before returning; `topk` for the noisiest streams.

## Instant vs range (tool parameters)

`query_loki_logs` takes `startRfc3339` / `endRfc3339` (or relative, e.g. `now-1h`), `queryType`, and `stepSeconds`:

- `range` (default): log queries return entries; metric queries return per-step series.
- `instant` with `count_over_time`: one value per stream — the window total. Each point of a range metric series is the count for ONE step, not the window total; sum the points or use a single window-width bucket.
- `direction`: `backward` (newest first, default) or `forward` (oldest first — use when line order matters, e.g. adjacency).
- `limit`: default 10; results are capped (~100 rows). Never assume a capped return is everything.

## Stats and patterns

- `query_loki_stats` takes a bare label selector only — no line filters, parsers, or aggregations. It returns approximate storage-level counts (streams, chunks, entries, bytes): good for "does this stream exist / have volume", not for counting lines.
- `query_loki_patterns` takes a stream selector only. It returns detected patterns with occurrence counts.

## Field notes

- The series label set in the tool's JSON sits under `labels` (with `values` the point list), where raw Grafana HTTP responses use `metric`. Inspect the first series' keys before writing a parser; a series consumed by an outer aggregation legitimately carries empty `{}` labels.
- Oversized results spill to a file and the response carries a preview: read the spillover file, do not re-request the same query.
- Sub-second windows can false-empty and window edges can shift silently: widen (at least one second, then several) and re-run before concluding absence.
- Serialize production queries (one or two at a time); back off briefly after a 5xx.
