# MCP Tool Parameter Shapes

Concrete parameter shapes for the MCP tools used by this skill. Captured from
validation errors and successful calls — the skill's prose describes the
intent, this file captures the exact shapes that the APIs accept.

## Slack

### `slack_search_public_and_private`

Uses three structured fields, not a single query string:

```json
{
  "keywords": ["Preparation", "Weekly", "SpeechRec"],
  "filters": "in:<#C08SF3A0B4L>",
  "natural_language_query": ""
}
```

- `keywords`: array of single words or `"quoted phrases"`, all AND'd.
- `filters`: Slack search modifiers as a single string (e.g. `"in:<#CHANNEL_ID>"`).
- `natural_language_query": ""` for filter-only queries.
- At least one of `keywords` or `filters` is required.
- Results are sorted by timestamp descending by default.

### `slack_read_channel`

```json
{
  "channel_id": "C08S4B4H5DL",
  "oldest": "1791237600",
  "limit": 100
}
```

- `oldest` must be a **string** (quoted), not a number. Passing an integer
  fails type validation.
- `channel_id` can also be a user ID to read DM history.

### `slack_read_thread`

```json
{
  "channel_id": "C08SF3A0B4L",
  "message_ts": "1791916853.580939"
}
```

- The parameter is `message_ts`, NOT `thread_ts`.
- `message_ts` is the timestamp of the **parent** message, in Slack ts format
  (a string with a decimal point, e.g. `"1234567890.123456"`).

### `slack_read_canvas`

```json
{
  "canvas_id": "F09LCH57KRQ"
}
```

- The result is typically too large for inline context. The harness saves it
  to a temp file automatically — this is expected, not an error. The file path
  is in the returned message.

### `slack_send_message`

```json
{
  "channel_id": "UBCF2ADNE",
  "message": "..."
}
```

- Use the user's own Slack ID as `channel_id` to send a DM.
- The authenticated user's ID appears in the `slack_search_public_and_private`
  and `slack_send_message` tool descriptions.

## Notion

### `notion_query_data_sources`

All parameters are nested inside a single `data` object:

```json
{
  "data": {
    "mode": "rows",
    "data_source_url": "collection://20dbef65-b3ab-8076-8351-000b245ea82b",
    "limit": 5,
    "sort": [{"property": "Dates", "direction": "descending"}]
  }
}
```

- The top-level argument is `data` (required). Passing `mode`, `data_source_url`,
  etc. as top-level keys fails with "missing required argument: data".
- `data_source_url` (singular), not `data_source_id`.
- `sort` is an array of `{"property": "...", "direction": "..."}` objects.
- `direction` values are `"ascending"` / `"descending"` (not `"asc"` / `"desc"`).
- To get cycles that include or precede today, filter with
  `{"type": "group", "operator": "and", "filters": [{"type": "property",
  "property": "Dates", "propertyType": "date", "operator": "date_is_on_or_before",
  "value": {"type": "relative", "value": "today"}}]}` — sorting by `Dates`
  descending with limit 5 alone returns the 5 *upcoming* cycles, which often
  have empty goals.

## Linear

### `list_issues`

All parameters are flat top-level keys (no nested `filter` object):

```json
{
  "team": "Speech Recognition",
  "updatedAt": "-P7D",
  "orderBy": "updatedAt",
  "limit": 200
}
```

- `updatedAt` is an ISO-8601 duration string (e.g. `"-P7D"`).
- `orderBy` is `"updatedAt"` or `"createdAt"` (not `orderDirection`).
- `state` filters by state type/name/ID (e.g. `"in_progress"`).
- `additionalProperties: false` — any unexpected key fails validation.

### `list_projects`

Same flat structure as `list_issues`:

```json
{
  "team": "Speech Recognition",
  "state": "in_progress",
  "limit": 50,
  "updatedAt": "-P14D"
}
```

- Same constraints: no nested `filter`, no `orderDirection`,
  `additionalProperties: false`.

### `get_status_updates`

```json
{
  "type": "project",
  "project": "P-SR-1947",
  "limit": 2
}
```

- `type` is **required** — must be `"project"` or `"initiative"`.
- `project` is the project ID, identifier, name, or slug.
- Many projects return empty `statusUpdates` arrays — fall back to inferring
  status from `list_issues` results.

## tool_call batching

- `tool_call` accepts only ONE entry per invocation for local/MCP tools.
- Multiple `tool_call` invocations can be issued in parallel within a single
  assistant turn — use separate `tool_call` calls, not a single call with
  multiple entries.
