# Slack Channels

Four SR channels, each serving a different purpose in sprint goal drafting.

## Channel reference

| Channel ID | Name | Type | What to extract |
|---|---|---|---|
| `C08SF3A0B4L` | #team-speech-recognition | Public, main engineering | Goals/priorities posts, technical decisions, open questions |
| `C08S4B4H5DL` | internal SR team | Private, secondary | PR/API-council threads, naming debates, escalation coordination |
| `C0BSN5L3FR8` | #feed-speech-recognition-deploys | Automated feed | Deploy confirmations — cross-check against Linear ticket statuses |
| `C0AMEADK2UX` | #feed-speech-rec-feedback | Automated feed | Customer-feedback intake — mostly noise, watch for process changes or escalations |

## Reading strategy

Fire all four `slack_read_channel` calls in parallel with `oldest` set to a Unix timestamp ~14 days before today.

Compute the timestamp via shell — don't guess:
```bash
date -d '14 days ago' +%s   # Linux
date -v-14d +%s              # macOS
```

## Handling large responses

These channels can exceed the single-response token budget. When that happens, the result is saved to a file instead of returning inline. Don't try to read that file directly with the Read tool — lines are too long.

Use `scripts/slice_file.py` to chunk the file into ~80,000-character spans:

```bash
N=$(python3 scripts/slice_file.py <file> --count)    # get number of spans
python3 scripts/slice_file.py <file> --index $i       # print span i (1-based)
```

Launch N subagents in parallel, one per span. Each subagent calls `slice_file.py --index $i`, reads only its span, and reports back a factual summary scoped to the last two weeks.

## What to extract from each channel

For the given channel and time window, ask the subagent (or yourself, if the result fits in context) to extract:

1. Active engineering topics/projects being discussed
2. Any explicit statement of goals, priorities, decisions, or things being pushed to next cycle
3. Customer-driven issues or escalations
4. Open questions or unresolved disagreements as of the most recent messages

The first channel (`C08SF3A0B4L`) is the highest-value source — look hard for any message that already states cycle goals or priorities. Someone on the team (e.g. the tech lead) sometimes posts this proactively, and if so it's your strongest signal, not just supporting color.
