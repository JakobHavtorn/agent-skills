# Test Cases: linear-ticket

## Should trigger

1. "Create a Linear ticket for a bug where the login button doesn't work on Safari"
2. "File a bug in Linear for the API returning 500 on empty payloads"
3. "Add a ticket to Linear for the missing pagination on the users endpoint"
4. "Make a Linear story for adding dark mode to the settings page"
5. "Create a task in Linear for updating the CI pipeline to use Node 22"

## Should NOT trigger

1. "What's the status of the login bug ticket?" — asking about an existing ticket, not creating one
2. "Summarize my Linear tickets for the week" — that's the standup-summary skill
3. "Create a Jira ticket for the login bug" — wrong tracker, not Linear

## Expected behavior

- Resolves team, user, labels, statuses, cycles, and projects from workspace metadata before creating
- Drafts title, description, and fields from context without asking a series of questions
- Only asks when critical information is truly missing
- Calls `linear_save_issue` with resolved metadata
- Reports the created issue URL back to the user
