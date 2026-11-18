# PR Description Template

The exact template for PR descriptions created or updated by this skill. The body's shape comes from the `pr` skill — Summary as the smallest visual, before/after Evidence, Merge Danger — and this file adds the org's Linear section and shows how the pieces combine.

## Template

````markdown
## Summary

<the smallest visual that makes the change clear — a diff, call tree, file tree, or Mermaid diagram; see the pr skill for the menu and when to use each>

## Evidence

- **Before:** <screenshot / output / failing test run>
  **After:** <screenshot / output / passing test run>

## Merge Danger

**Door:** <one-way or two-way>

**Blast Radius:** <one-word description>

## Linear

Closes <TICKET-ID>
````

## Rules

- **Summary**: lead with the visual, not prose. The `pr` skill holds the menu of visuals (pseudocode, call trees, component trees, file trees, Mermaid, diffs) and the placement guidance.
- **Evidence**: screenshots when the change is visual and the environment supports them; otherwise test results or command output. Show the exact test that failed before and passes after.
- **Merge Danger**: cheap to roll back is a two-way door; destructive or hard-to-reverse changes are one-way doors. Blast radius covers layout shift, consumer breakage, data migrations, mobile responsiveness.
- **Linear section**: Use the closing word `Closes` by default (moves issue through full status pipeline on merge). See `linear-linking.md` for non-closing alternatives.
- **No "Test plan" section**: This org's PR conventions don't include one for routine changes — the Evidence section carries the verification.
- **Reference the ticket inline** in Summary text, e.g., "Addresses SR-2522 by refactoring the auth proxy layer."

## Example

````markdown
## Summary

```diff
 proxy/
-└── client.go            # single upstream connection
+├── pool.go              # connection pool, N idle conns
+└── client.go            # acquires from pool, retries idempotent verbs
```

Pooling reuses warm upstream connections instead of dialing per request (SR-2522).

## Evidence

- **Before:** `TestProxyP99` — p99 480ms, fails the 300ms budget
  **After:** `TestProxyP99` — p99 210ms, passes

## Merge Danger

**Door:** two-way (revert restores the single-connection path)

**Blast Radius:** every upstream call through the proxy

## Linear

Closes SR-2522
````

## Multiple Tickets

If the change spans multiple Linear tickets, use multiple closing words on separate lines:

````markdown
## Linear

Closes SR-2522
Closes SR-2518
````

Each ticket moves independently through the status pipeline.
