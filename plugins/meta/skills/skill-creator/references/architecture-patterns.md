# Architecture Patterns for Skills

Choosing the right structural pattern is the most impactful decision in skill design. The wrong pattern creates friction; the right one makes the skill feel natural.

## Linear Pattern

**When to use:** The skill has a single workflow with no branching. User provides input, skill processes it sequentially, skill returns output.

**Structure:** 5-7 numbered steps, executed in order.

**Example:** `open-pr`
```
Step 1: Detection flow (gh CLI, auth, lint tools)
Step 2: Run linters and tests
Step 3: Stage and commit changes
Step 4: Push branch and open PR via gh api
Step 5: Respond with PR link and summary
```

**Strengths:** Simple to follow, easy to debug, low token cost.
**Weaknesses:** Cannot handle diverse user intents within the same domain.

**Design rules:**
- Each step should produce a concrete intermediate result
- Include an early exit if prerequisites fail (Step 1)
- Keep the total under 7 steps; if you need more, consider Router or Methodology

---

## Router Pattern

**When to use:** The skill covers multiple related sub-tasks. The user's intent determines which path to take.

**Structure:** Step 1 (setup) + Step 2 (route) + Sub-Skill sections + Final step (respond).

**Example:** `csv-analysis`
```
Step 1: Check dependencies (pandas, numpy)
Step 2: Route based on intent
  - Summarize data → Sub-Skill A: Summary Statistics
  - Filter/transform → Sub-Skill B: Data Transformation
  - Visualize → Sub-Skill C: Chart Generation
  - Find correlations → Sub-Skill D: Correlation Analysis
Step 3: Respond to user
```

**Strengths:** Handles diverse intents cleanly, each sub-path stays focused.
**Weaknesses:** More complex to write, routing table must be exhaustive.

**Design rules:**
- The routing table MUST have a default for ambiguous requests
- Each sub-skill should be self-contained (A1, A2, A3 sub-steps)
- Shared defaults go in Step 1, sub-skill-specific defaults go in each sub-skill
- Limit to 4-6 sub-skills; more means the skill should be split into separate skills

---

## Methodology Pattern

**When to use:** The skill implements a known framework or methodology with sequential validation gates. Each step builds on the previous one, and failure at any gate stops the process.

**Structure:** 7-9 numbered steps, each with explicit pass/fail criteria.

**Example:** `deploy-app`
```
Step 1: Detect deploy tools and environment
Step 2: Build (STOP if build fails)
Step 3: Run tests (STOP if tests fail)
Step 4: Lint and type check (grade A/B/C/D)
Step 5: Create staging deployment
Step 6: Smoke test staging (STOP if critical checks fail)
Step 7: Promote to production
Step 8: Post-deploy verification
Step 9: Respond with deployment report
```

**Strengths:** Thorough, educational, produces high-quality results, prevents premature conclusions.
**Weaknesses:** Highest token cost, requires deep domain knowledge to write.

**Design rules:**
- Every step MUST have a clear pass/fail gate or a grading system
- Failed gates must stop analysis with a clear message ("Build failed — no further steps needed")
- Use tables for checklists and criteria
- Defer ALL detailed criteria to reference files; SKILL.md shows the checklist, reference shows the rubric
- Always end with a verdict system (Deployed / Rollback / Blocked)
- The final step output template should mirror the step structure (9 steps → 8 output sections)

---

## Widget Pattern

**When to use:** The skill generates an interactive HTML/SVG widget as output.

**Structure:** 4-5 steps: extract parameters → identify type → compute → render → explain.

**Example:** `options-payoff`
```
Step 1: Extract strategy from user input (with comprehensive defaults table)
Step 2: Identify strategy type (lookup matrix)
Step 3: Compute payoffs (mathematical formulas)
Step 4: Render the widget (UI spec + code template)
Step 5: Respond with brief explanation
```

**Strengths:** Produces tangible, interactive output.
**Weaknesses:** Requires detailed code templates, hard to test without rendering.

**Design rules:**
- Step 1 MUST have a defaults table covering every parameter (the skill should NEVER stall asking for info)
- The extraction step needs "Where to find it" guidance for each field
- Include a code template skeleton in SKILL.md (not full implementation — that goes in references)
- The render step must specify: controls, stats cards, chart axes, colors, tooltips
- The final step should be SHORT — "the chart speaks for itself"

---

## API Wrapper Pattern

**When to use:** The skill wraps an external API with many endpoints. The user's request maps to one or more API calls.

**Structure:** 3-5 steps + heavy reference files (one per endpoint category).

**Example:** `github-api`
```
Step 1: Check auth (GITHUB_TOKEN)
Step 2: Identify what user needs (mega routing table)
Step 3: Make the API call
Step 4: Handle common patterns (pagination, rate limits, errors)
Step 5: Respond to user
```

**Strengths:** Comprehensive API coverage, reference files serve as living documentation.
**Weaknesses:** Step 2 routing table can become unwieldy, reference files need maintenance.

**Design rules:**
- The routing table in SKILL.md should be a high-level category map, not every endpoint
- Each reference file covers one endpoint category (repos, issues, pull-requests, etc.)
- Reference files should include: endpoint URL, parameters, example curl/code, response format
- Always include a "common patterns" step for things like pagination, rate limits, error codes
- API keys should use environment variables in frontmatter, not inline instructions

---

## Choosing Between Patterns

| Signal | Recommended Pattern |
|---|---|
| "Fetch X data and show it" | Linear |
| "It depends on what the user asks" | Router |
| "There's a formal framework with criteria" | Methodology |
| "Generate a chart/widget/visualization" | Widget |
| "Wrap this API's 20+ endpoints" | API Wrapper |
| Multiple signals | Combine: Router with Linear sub-skills, Methodology with Widget output |

## Anti-Patterns to Avoid

### The Wall of Text
A single massive step with 50+ lines of instructions. **Fix:** Split into multiple steps with clear boundaries.

### The Premature Reference
Linking to a reference file for 3 lines of content. **Fix:** Keep short content inline; references are for 50+ lines of depth.

### The Missing Exit Gate
Steps that always proceed regardless of result. **Fix:** Add "If X fails, stop here" at every decision point.

### The Vague Output
"Summarize the results for the user." **Fix:** Number every output section, specify what data goes in each.

### The Hardcoded Universe
Static data lists or values that will go stale. **Fix:** Build data dynamically at runtime using APIs or detection flows.
