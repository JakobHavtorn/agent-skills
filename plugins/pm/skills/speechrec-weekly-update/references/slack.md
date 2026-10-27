# Slack Channels and Canvas

Channel IDs, canvas IDs, and user-ID-to-name mappings for the Speech Recognition team.

## Channels

| Channel ID | Name | Type | Purpose |
|---|---|---|---|
| `C08SF3A0B4L` | #team-speech-recognition | Public, main engineering | Previous status posts, goals/priorities, technical decisions |
| `C08S4B4H5DL` | internal SR team | Private | Messages since last sync — customer issues, blockers, PR/release announcements |

## Canvas

| Canvas ID | Purpose |
|---|---|
| `F09LCH57KRQ` | Standup notes canvas — too large for inline context, harness saves to temp file |

## User ID → Name Mappings

Standup canvas uses Slack user IDs. Map them to names:

| Slack User ID | Name |
|---|---|
| `<@U04G8U5SVJL>` | Michael |
| `<@U04TXHY5MMJ>` | Simas |
| `<@U074ZNDHQTV>` | Lana |
| `<@U07JMB1EHRD>` | Robert |
| `<@U086V4A6JB0>` | Dan Engel |
| `<@U08BGBWSWU8>` | Arne |
| `<@U09LZ64UL5P>` | Anna |
| `<@UBCF2ADNE>` | Jakob |
| `<@UHEN7TDNG>` | Gedas |
| `<@U0BKBBYK3ME>` | Maha |
| `<@U0C4NF49QKS>` | Sindri |

## Status Message Recipients

The status update Slack message mentions these team members in the preamble:

`<@UBCF2ADNE|Jakob> <@U086V4A6JB0|Dan Engel> <@UC93DK477|Henrik> <@U07HFSS28MR|Kevin> <@U1B9GHW8L|Lars> <@U04G8U5SVJL|Michael> <@U090GQJ004F|James Kane> <@U08EY8UDKS6|Nicklas Frahm>`

## Sending the weekly message

### The 5000-char limit

`slack_send_message` (MCP) rejects any single message over 5000 characters with `msg_too_long`. A complete pre-read (15+ linked status items) runs ~12–15k chars and always exceeds the limit.

- Compose the full message first, then split it into chunks of <5000 chars, keeping list numbering continuous across chunks. A typical split: preamble + status items 1–7 / items 8–12 / remaining items + section divider / topics + notes.
- Verify each chunk's length programmatically (e.g. `len()` in Python) BEFORE calling Slack — a `msg_too_long` rejection wastes a round-trip and sends nothing.

### Sending the chunks as one thread

1. Send chunk 1 to the user's Slack ID as `channel_id` (Slack treats a user ID as a DM channel), without `thread_ts`. Note the returned `message_ts`.
2. Send the remaining chunks with `thread_ts` set to that timestamp. For the thread replies, both the raw user ID and the DM channel ID returned with the first message work as `channel_id` (verified empirically 2026-10-27).
3. End the main chunk with `*(continued in thread)*` so readers know to expand the thread.
4. Echo the returned message link back to the user in the conversation.

The threaded MCP send is what makes the `@` mentions in the preamble actually notify the recipients.

### Paste-ready single-message fallback

The 5000-char cap applies only to the MCP rich-text posting path; the Slack client accepts a pasted message of the full pre-read length. If the user asks why the message was split or prefers a single message, offer a paste-ready file instead of the split send:

- Convert `**bold**` → `*bold*` (pasted `**` is not mrkdwn bold).
- Convert `[label](url)` → `label (url)` (pasted markdown links render literally; bare URLs auto-linkify).
- Convert `<@ID|name>` → the plain display name (pasted mention syntax does not notify anyone).
- Write the converted text to a file and hand it over as a `MEDIA:` path for the user to paste.

Driving the Slack web client to post it as the user is possible but heavyweight — prefer the paste file.
