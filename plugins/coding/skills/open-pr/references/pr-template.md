# PR Description Template

The exact template for PR descriptions created or updated by this skill.

## Template

```markdown
## Summary

- <bullet describing what changed and why>
- <bullet describing what changed and why>
- <bullet describing what changed and why>

## Linear

Closes <TICKET-ID>
```

## Rules

- **Summary**: 2-5 bullets. Focus on the *why*, not a file-by-file recap — the diff already covers the *what*.
- **Linear section**: Use the closing word `Closes` by default (moves issue through full status pipeline on merge). See `linear-linking.md` for non-closing alternatives.
- **No "Test plan" section**: This org's PR conventions don't include one for routine changes.
- **Reference the ticket inline** in Summary bullets, e.g., "Addresses SR-2522 by refactoring the auth proxy layer."

## Example

```markdown
## Summary

- Refactor auth proxy to use connection pooling, reducing p99 latency by 40%
- Add retry logic for transient upstream failures (Addresses SR-2522)
- Update integration tests to cover pooled connection teardown

## Linear

Closes SR-2522
```

## Multiple Tickets

If the change spans multiple Linear tickets, use multiple closing words on separate lines:

```markdown
## Linear

Closes SR-2522
Closes SR-2518
```

Each ticket moves independently through the status pipeline.
