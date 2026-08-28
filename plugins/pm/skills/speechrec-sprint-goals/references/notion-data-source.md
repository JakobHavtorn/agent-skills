# Notion Sprint Planning Data Source

## Sprint Planning page

- URL: `https://www.notion.so/cortihome/Sprint-Planning-20dbef65b3ab800c85dbd99368164e20`
- Data source: `collection://20dbef65-b3ab-8076-8351-000b245ea82b`
- Title: "Team Speech Rec - Sprint Planning"

## Query

Query via `notion-query-data-sources` (SQL mode):

```sql
SELECT * FROM "collection://20dbef65-b3ab-8076-8351-000b245ea82b"
ORDER BY "date:Dates:start" DESC LIMIT 6
```

Returns the most recent 6 cycle entries, newest first.

## Interpreting results

Each row is a cycle entry with these key properties:

| Property | What it contains |
|---|---|
| `Cycle Name` | Mythological name (e.g. "Io", "Juno") — matches Linear cycle title exactly |
| `Dates` | Start/end date range for the cycle |
| `Goals` | Text field with numbered sprint goals — may be blank, partially drafted, or fully filled in |
| `Cycle - Linear link` | URL to the corresponding Linear cycle |

## Identifying cycles

- **Outgoing cycle**: the row whose `Dates` range contains today (or the most recently ended if none is currently active).
- **Upcoming cycle**: the row starting right after the outgoing cycle. This is the page you're drafting goals for.
- **Older completed cycles**: 1-2 rows before the outgoing cycle. Their `Goals` property is your style reference.

## Style reference

Match the exact formatting of older completed cycles' `Goals` property:
- Numbered bold titles per goal
- One-line factual bodies (ticket IDs, what shipped vs. pending)
- Blank bodies where nothing concrete existed

The team edits these down to remove commentary. Mirror the leanest, most recently-edited example you can find — not your own instinct for how detailed it should be.

## Writing goals back (only when user asks)

If the user explicitly asks to write the draft into Notion, use `notion-update-page` on the upcoming cycle's page:
- Replace the `Goals` property with the agreed text
- Use `<br>` between numbered items to match existing formatting
