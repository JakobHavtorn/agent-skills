# Test Cases: speechrec-weekly-update

## Should trigger

1. "Compose the weekly Speech Recognition status update"
2. "Prepare the pre-read for the sync call"
3. "Write the weekly status post for the Speech Recognition channel"

## Should NOT trigger

1. "Write a standup summary" — that's standup-summary, not the weekly update
2. "What's the status of the speech recognition project?" — a query, not composing a post
3. "Summarize the sprint planning notes" — one source, not the full weekly update

## Expected behavior

- Gathers context from the previous status post in the team Slack channel
- Pulls Notion sprint planning data
- Checks Linear project updates for cycle items in progress
- Reviews recent standup notes
- Scans recent messages in the internal Speech Recognition Slack channel
- Output covers: status on cycle items in progress, goals for the next cycle, priority topics for discussion
- Ready to post directly in the team Slack channel
