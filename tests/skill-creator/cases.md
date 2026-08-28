# Test Cases: skill-creator

## Should trigger

1. "Create a skill for generating commit messages from git diff"
2. "I want a skill to automate monthly invoice reconciliation"
3. "I keep doing this deployment checklist manually, can you remember how to do it?"
4. "Improve this skill — the triggers are too broad and it fires on unrelated prompts"
5. "Run evals on the open-pr skill to see how it performs"

## Should NOT trigger

1. "Write me a bash script that generates commit messages" — wants a script, not a skill
2. "What skills are installed?" — listing, not creating
3. "Fix the bug in the linear-ticket skill" — code fix, not skill authoring

## Expected behavior

- Guides through planning, writing, scoring, and iterating on a skill
- Produces SKILL.md with proper frontmatter (name, description, allowed-tools)
- Creates reference files for heavy material, keeps body under ~500 lines
- Scores quality against the rubric in references/quality-rubric.md
- Detects available tools/libraries at runtime rather than hardcoding
- Produces a structured output template for the skill
