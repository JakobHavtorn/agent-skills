# Test Cases: speechrec-sprint-goals

## Should trigger

1. "Draft the sprint goals for the next SR cycle"
2. "What should our goals be for Juno?"
3. "Help me prepare for cycle planning — draft the goals"
4. "Fill in the Goals for the new cycle entry on the Sprint Planning page"
5. "Draft sprint goals biweekly for the next cycle"

## Should NOT trigger

1. "Summarize my standup" — that's standup-summary
2. "Compose the weekly Speech Recognition status update" — that's speechrec-weekly-update
3. "Prioritize my tasks" — that's prioritize-tasks

## Expected behavior

- Step 1: Tests Notion, Linear, Slack MCP availability; fails if any missing
- Step 2: Fires all three sources in parallel (Notion query, Linear cycles + issues, Slack reads)
- Step 2a: Identifies outgoing + upcoming cycle from Notion; checks for existing Goals draft
- Step 2b: Gets cycles from Linear via list_cycles; lists outgoing cycle's issues grouped by project
- Step 2c: Reads 4 Slack channels in parallel; uses scripts/slice_file.py for large responses
- Step 3: Synthesizes into numbered bold-title goals with factual one-line bodies
- Step 4: Returns draft in conversation with structured output (cycle names, goals, sources consulted, next steps)
- Does not write to Notion unless explicitly asked
- Fails completely (not gracefully degrades) if any data source is unavailable or returns no data
