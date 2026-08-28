# Test Cases: standup-summary

## Should trigger

1. "Give me a standup summary for today"
2. "What have I been doing since Monday?"
3. "Recap my recent work from the last 2 days"

## Should NOT trigger

1. "Prioritize my tasks" — that's prioritize-tasks
2. "What did the team do this week?" — team-wide, not personal standup
3. "Create a Linear ticket for the bug I found" — that's linear-ticket

## Expected behavior

- Pulls Linear issue activity for the user since the last standup
- Searches Slack for the user's recent messages and commits
- Combines into a concise report grouped by theme or project
- Honors a user-provided timespan or defaults to the last 3 workdays
- Output is terminal-formatted, ready to paste into a standup channel
