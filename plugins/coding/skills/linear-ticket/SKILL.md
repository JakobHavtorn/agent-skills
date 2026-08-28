---
name: linear-ticket
description: >-
  Create a Linear issue with proper template, fields, and metadata. Resolves
  team, labels, status, cycle, and project from workspace metadata before
  creating the issue. Use when the user asks to create a Linear ticket, file a
  bug, open a story, or add a task to Linear. Triggers: "create a linear
  ticket", "create a linear issue", "add a ticket to linear", "file a bug in
  linear", "make a linear ticket", "open a linear issue", "create a ticket",
  "add a ticket", "file a ticket", "log a ticket in linear", "create a bug
  ticket", "create a story in linear", "create a task in linear".
allowed-tools: Bash(gh:*) Read
metadata:
  dk.jakob.category: coding
  dk.jakob.version: "1.0"
  dk.jakob.status: stable
---

## Overview

Create a well-structured Linear issue by resolving workspace metadata (team, user, labels, statuses) and drafting the issue body from context, then calling `linear_save_issue`. Be assumptive — infer the title, body, and fields from the user's request and surrounding context rather than asking a series of questions. Only ask when critical information is truly missing.

---

## Step 1: Detection and prerequisites

Check that Linear MCP is available before doing anything else.

**Gate:** If Linear MCP tools are not available (e.g., `linear_list_teams` fails), stop and tell the user to configure the Linear MCP server. Do not proceed without workspace access.

---

## Step 2: Resolve the user's team

Call `linear_get_user` with `"me"` to get the authenticated user. Note their `team` affiliation(s).

Default the team to the user's team. If the user belongs to multiple teams, pick the most likely one from context (e.g., the team mentioned in conversation) or default to the first one. Only ask if the choice is genuinely ambiguous.

Call `linear_list_issue_statuses` for the resolved team to find the default status (e.g. "Todo" or "Backlog").

---

## Step 3: Draft the issue from context

Infer as much as possible from the user's request and surrounding context. Write the title and body directly — do not ask the user to fill in sections.

### Title

Concise, imperative. Derive from the user's request.

### Body

Use this template:

```
What does this solve (and why)?

TODO

How will this be solved?

TODO

Definition of done

TODO
```

Fill in each `TODO` section from context. If a section cannot be reasonably inferred, leave it as `TODO` for the user to fill in later — but try to fill all sections.

### Other fields

Infer from context where possible:

- **Priority**: `0`=None, `1`=Urgent, `2`=High, `3`=Medium, `4`=Low. Default: `0` if not inferable.
- **Estimate**: `1` ≈ half day, `2` ≈ 1 day, `3` ≈ 2 days. Omit if not inferable.
- **Labels**: Match from `linear_list_issue_labels` if the user mentioned keywords (e.g. "bug" → Bug label). Omit if none apply.
- **Cycle**: If the user mentions a sprint or cycle, resolve it. Omit otherwise.
- **Project**: If the user mentions a project or the context makes it obvious, include it. Omit otherwise.
- **Assignee**: Default to `"me"` unless the user specifies someone else.

The Linear MCP tools accept real newlines in markdown; do not use `\n` literals.

---

## Step 4: Create the issue

Call `linear_save_issue` with:

| Field | Notes |
|---|---|
| `team` | Team ID from Step 2 |
| `title` | Concise, imperative title from Step 3 |
| `description` | Body from Step 3 |
| `state` | Status name or ID from Step 2 |
| `assignee` | `"me"` (default) or user-specified |
| `priority` | `0`=None `1`=Urgent `2`=High `3`=Medium `4`=Low (optional) |
| `estimate` | Points: `1` ≈ half day, `2` ≈ 1 day, `3` ≈ 2 days (optional) |
| `labels` | Array of label names or IDs (optional) |
| `cycle` | Cycle name, number, or ID (optional) |
| `project` | Project name, ID, or identifier (optional) |

Omit optional fields entirely if not inferred from context — do not pass `null`.

---

## Step 5: Confirm and respond

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
   | Priority | <priority or "—"> |
   | Estimate | <estimate or "—"> |
   | Labels | <labels or "—"> |
   | Cycle | <cycle or "—"> |
   | Project | <project or "—"> |
4. **Next steps**:
   - Review the issue description for accuracy
   - Fill in any TODO sections
   - Add sub-issues or links if needed
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
- Omitting optional fields (`cycle`, `project`) is fine — do not pass `null`
- The Linear MCP tools accept real newlines in markdown; do not use `\n` literals
- `linear_save_issue` accepts names or IDs for `team`, `state`, `assignee`, `labels`, `cycle`, `project` — no need to resolve everything to IDs first
- Be assumptive: infer fields from context, draft the body yourself, and only ask the user when critical information is truly missing
