# Linear Cycle and Ticket Queries

## Team

- Team name: Speech Recognition
- Team ID: `70db986a-d0a7-40fe-8894-132948e77ebe`

## Get cycles

Fire all three `list_cycles` calls in parallel — no dependency on Notion:

| Call | Returns |
|---|---|
| `list_cycles(teamId: "70db986a-d0a7-40fe-8894-132948e77ebe", type: "previous")` | Outgoing cycle |
| `list_cycles(teamId: "70db986a-d0a7-40fe-8894-132948e77ebe", type: "current")` | Current cycle (may equal outgoing) |
| `list_cycles(teamId: "70db986a-d0a7-40fe-8894-132948e77ebe", type: "next")` | Upcoming cycle |

If the user named the cycle explicitly (e.g. "draft goals for Juno"), query that cycle by name instead of using previous/current/next.

## List issues per cycle

```python
list_issues(
  team: "Speech Recognition",
  cycle: "<cycle name>",
  limit: 250,
  fields: ["title", "status", "statusType", "priority",
           "assignee", "project", "labels", "url", "completedAt"]
)
```

Run this for both the outgoing cycle (required) and the upcoming cycle (optional — tickets already scoped tell you what's planned vs. aspirational).

## Interpreting results

Group outgoing cycle's issues by `project` — that grouping maps to goal-level themes on the Sprint Planning page. For each theme, note:

| Status type | Meaning for goal drafting |
|---|---|
| Done | Shipped — carry forward only if flagged as ongoing |
| In Progress / In Review / In QA | Still active — carry forward phrased as what's still needed |
| Todo | Planned but not started — carry forward as-is or merge into a broader theme |

Cross-reference against the outgoing cycle's Notion `Goals` text. Where they diverge — something planned but never started, or something shipped that wasn't originally a stated goal — surface it.
