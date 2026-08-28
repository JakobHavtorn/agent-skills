---
name: linear-ticket
description: Create a Linear issue with proper template, fields, and metadata for the Speech Recognition team
---

## Workflow

### 1. Gather workspace metadata (run in parallel)

- **Teams**: `list_teams` → find target team, note its `id`
- **User**: `list_users` → find the user to assign, note their `id`
- **Labels**: `list_issue_labels` → collect `id` for each relevant label
- **Statuses**: `list_issue_statuses` → find status by name (e.g. "Todo"), note its `id``

### 2. Draft the issue body

Use the below issue template:

```markdown 
## What does this solve (and why)?

## How will this be solved?

## Definition of done
```

Fill in each section with:
- **What does this solve**: problem statement and motivation
- **How will this be solved**: approach taken or planned
- **Definition of done**: concrete, checkable criteria (use `- [ ]` checkboxes)

### 3. Create the issue

Call `save_issue` with:

| Field | Notes | 
|---|---|
| `teamId` | From step 1 |
| `title` | Concise, imperative |
| `description` | Markdown body from step 3 |
| `stateId` | Status ID from step 1 |
| `assigneeId` | User ID from step 1 |
| `priority` | `0`=None `1`=Urgent `2`=High `3`=Normal `4`=Low |
| `estimate` | Points: `1` ≈ half day, `2` ≈ 1 day, `3` ≈ 2 days, etc. | 
| `labelIds` | Array of label IDs from step 1 | 
| `cycleId` | Omit if no cycle mentioned |
| `projectId` | Omit if no project mentioned |

### 4. Confirm

`get_issue` on the returned ID and print the URL to the user.

## Key facts

- Priority `4` = Low (counter-intuitive — higher number = lower priority)
- `list_documents` rarely surfaces issue templates; always verify via a recent issue
- Omitting optional fields (`cycleId`, `projectId`) is fine — do not pass `null`
- The Linear MCP tools accept real newlines in markdown; do not use `\n` literals
