# Test Cases: prioritize-tasks

## Should trigger

1. "Prioritize my tasks for this week"
2. "What should I work on next?"
3. "Give me a task list"
4. "What's on my plate?"

## Should NOT trigger

1. "Create a Linear ticket for the auth bug" — that's linear-ticket
2. "Summarize my standup for today" — that's standup-summary
3. "List all issues in the Backlog milestone" — a query, not prioritization

## Expected behavior

- Pulls active Linear tickets (Todo, In Progress, In Review, In QA — never Backlog, Triage, Done, Canceled)
- Searches Slack for tasks the user has committed to ("I'll do X", "I'll handle Y")
- Reads the user's Slack To-do doc
- Deduplicates across all three sources
- Ranks into Now/Next/Later tiers, continuously numbered
- Ticket-less tasks can be turned into Linear issues via the linear-ticket skill
- Delivers output in terminal and as a Slack DM to the user
- Honors a user-provided lookback window or defaults to 14 days for Slack search
