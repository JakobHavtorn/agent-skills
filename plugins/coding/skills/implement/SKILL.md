---
name: implement
description: Implement a piece of work based on a spec or a set of tickets. This skill should be used when the user asks to build the work described by a spec or tickets, e.g. "implement this spec", "build this ticket", "work through these tickets".
disable-model-invocation: true
---

Implement the work described by the user in the spec or tickets.

If the user passes a ticket reference, fetch it from the issue tracker (this setup uses Linear via MCP) and state its title before starting. If the reference is ambiguous, ask.

Call the Skill tool with "tdd" where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, call the Skill tool with "code-review" to review the work.

Commit your work to the current branch.

---

[Vendored from mattpocock/skills](https://github.com/mattpocock/skills/tree/5863806dd4e15c63174bee4e7515a4256792ecfa/skills/engineering/implement) at commit `5863806` (MIT).
