---
name: linear-ticket
description: >
  Create a Linear issue with proper template, fields, and metadata. Resolves
  team, labels, status, cycle, and project from workspace metadata before
  creating the issue. Triggers: "create a linear ticket", "create a linear
  issue", "add a ticket to linear", "file a bug in linear", "make a linear
  ticket", "open a linear issue", "create a ticket", "add a ticket", "file
  a ticket", "log a ticket in linear", "create a bug ticket", "create a
  story in linear", "create a task in linear".
---

## Overview

Create a well-structured Linear issue by resolving all workspace metadata (team, user, labels, statuses, cycles, projects) upfront, then calling `save_issue` with the correct parameters. Uses Linear MCP tools throughout.

---

## Step 1: Detection and prerequisites

Check that Linear MCP is available before doing anything else.

**Gate:** If Linear MCP tools are not available (e.g., `list_teams` fails), stop and tell the user to configure the Linear MCP server. Do not proceed without workspace access.

---

## Step 2: Gather workspace metadata (run in parallel)

Call these Linear MCP tools in parallel to resolve IDs:

- **Teams**: `linear_list_teams` → find the target team, note its `id`
- **User**: `linear_list_users` → find the user to assign (or use `"me"`), note their `id`
- **Labels**: `linear_list_issue_labels` → collect `id` for each relevant label
- **Statuses**: `linear_list_issue_statuses` (requires team) → find status by name (e.g. "Todo"), note its `id`

**Gate:** If the target team is not found, ask the user which team to use. Do not guess.
**Gate:** If the assignee is not found, ask the user. Default to `"me"` if the user says "assign to me" or doesn't specify.

---

## Step 3: Gather issue details from the user

Ask the user for (or infer from context):

- **Title**: concise, imperative (required)
- **Body**: problem, approach, and definition of done (see Step 4)
- **Priority**: `0`=None, `1`=Urgent, `2`=High, `3`=Medium, `4`=Low (default: `0` if unspecified)
- **Estimate**: points where `1` ≈ half day, `2` ≈ 1 day, `3` ≈ 2 days (optional)
- **Labels**: names or IDs from Step 2 (optional)
- **Cycle**: name, number, or ID (optional — ask if the user mentions a sprint/cycle)
- **Project**: name, ID, or identifier like `PROJ-123` (optional — ask if the user mentions a project)

**Gate:** If the user hasn't provided enough context for the title or body, ask clarifying questions before proceeding. Do not fabricate issue content.

---

## Step 4: Draft the issue body

Use the following template:

```markdown
## What does this solve (and why)?

<problem statement and motivation>

## How will this solve it?

<approach taken or planned>

## Definition of done

- [ ] <checkable criterion 1>
- [ ] <checkable criterion 2>
- [ ] <checkable criterion 3>
```

The Linear MCP tools accept real newlines in markdown; do not use `\n` literals.

---

## Step 5: Create the issue

Call `linear_save_issue` with:

| Field | Notes |
|---|---|
| `team` | Team ID from Step 2 |
| `title` | Concise, imperative title from Step 3 |
| `description` | Markdown body from Step 4 |
| `state` | Status name or ID from Step 2 (optional) |
| `assignee` | User ID, name, email, or `"me"` from Step 2 (optional) |
| `priority` | `0`=None `1`=Urgent `2`=High `3`=Medium `4`=Low |
| `estimate` | Points: `1` ≈ half day, `2` ≈ 1 day, `3` ≈ 2 days (optional) |
| `labels` | Array of label names or IDs from Step 2 (optional) |
| `cycle` | Cycle name, number, or ID (optional — omit if no cycle) |
| `project` | Project name, ID, or identifier (optional — omit if no project) |

Omit optional fields entirely if the user hasn't specified them — do not pass `null`.

---

## Step 6: Confirm and respond

Call `linear_get_issue` on the returned issue ID to verify creation.

### If all steps succeeded

```
1. **Issue URL**: <Linear issue URL>
2. **Title**: <issue title>
3. **Fields set**:

   | Field | Value |
   |---|---|
   | Team | <team name> |
   | Status | <status name> |
   | Assignee | <assignee name> |
   | Priority | <priority> |
   | Estimate | <estimate or "—"> |
   | Labels | <labels or "—"> |
   | Cycle | <cycle or "—"> |
   | Project | <project or "—"> |
4. **Next steps**:
   - Review the issue description for accuracy
   - Add sub-issues or links if needed
   - Move to the appropriate cycle/sprint
```

### If a gate stopped the process early

```
1. **Status**: blocked
2. **Step failed**: <step number and name>
3. **Error**: <what went wrong>
4. **Next steps**: <action to resolve>
```

---

## Key facts

- Priority `4` = Low (counter-intuitive — higher number = lower priority)
- `linear_list_documents` rarely surfaces issue templates; always verify via a recent issue
- Omitting optional fields (`cycle`, `project`) is fine — do not pass `null`
- The Linear MCP tools accept real newlines in markdown; do not use `\n` literals
- `linear_save_issue` accepts names or IDs for `team`, `state`, `assignee`, `labels`, `cycle`, `project` — no need to resolve everything to IDs first
