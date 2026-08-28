# Annotated Skill Examples

Real excerpts from well-structured skills, with annotations explaining why specific patterns work.

## Example 1: Exhaustive Description (deploy-app)

```yaml
description: >
  Deploy an app through a gated CI/CD pipeline with build, test, staging,
  and production promotion steps. Use this skill whenever the user mentions
  deploy, ship, promote, rollback, canary release, smoke test, blue-green
  deployment, or asks about promoting a build to production. Also triggers
  when the user wants to verify a deployment is safe, check if staging tests
  passed, create a release from a branch, or roll back a failed deployment.
  Use this skill even when the user simply asks "is it safe to deploy" or
  "put this in production" in the context of a release, or when they share
  a build URL and want to know the next step.
```

**Why this works:**
- Starts with the formal workflow name (expert trigger)
- Lists 8+ domain-specific terms (canary, blue-green, smoke test, rollback)
- Describes behavioral triggers ("verify a deployment is safe")
- Includes sideways entries ("is it safe to deploy", "put this in production")
- Covers input modalities ("share a build URL")

---

## Example 2: Comprehensive Defaults Table (options-payoff)

```markdown
| Field | Where to find it | Default if missing |
|---|---|---|
| Strategy type | Title bar / leg description | "custom" |
| Underlying | Ticker symbol | SPX |
| Strike(s) | K1, K2, K3... in title or leg table | nearest round number |
| Premium paid/received | Filled price or avg price | 5.00 |
| Quantity | Position size | 1 |
| Multiplier | 100 for equity options, 100 for SPX | 100 |
| Expiry | Date in title | 30 DTE |
| Spot price | Current underlying price (NOT strike) | middle strike |
| IV | Shown in greeks panel, or estimate from vega | 20% |
| Risk-free rate | — | 4.3% |
```

**Why this works:**
- Three columns: Field, Where to find it (extraction guidance), Default
- Covers EVERY parameter — the skill never stalls
- Defaults are reasonable (SPX is the most common underlying, 30 DTE is standard)
- Includes a critical warning: "spot price is NOT the strike"

---

## Example 3: Pass/Fail Gate (deploy-app, Step 2)

```markdown
## Step 2: Build — Verify the Build Passes

| Build Status | Characteristics | Action |
|---|---|---|
| **Pass** | Exit code 0, no warnings | Proceed to Step 3 |
| **Pass with warnings** | Exit code 0, deprecation warnings | Proceed, flag warnings |
| **Fail** | Non-zero exit code | Stop — fix build errors before deploying |
| **Timeout** | Build exceeds 10 min | Stop — investigate CI pipeline |

If the build FAILS, stop here and tell the user. No further steps needed.
```

**Why this works:**
- Clear classification table (4 options, each with characteristics and action)
- **Hard gate**: "stop here" — prevents deploying a broken build
- The gate is explicit and non-negotiable, not a suggestion
- Saves tokens and produces more accurate results

---

## Example 4: Router Pattern (csv-analysis, Step 2)

```markdown
## Step 2: Route to the Correct Sub-Skill

| User Request | Route To | Examples |
|---|---|---|
| Wants summary stats | **Sub-Skill A** | "describe this CSV", "what's in this data" |
| Wants to filter/transform | **Sub-Skill B** | "filter rows where X > 100", "group by category" |
| Wants a chart/visualization | **Sub-Skill C** | "plot revenue over time", "bar chart by region" |
| Wants correlations | **Sub-Skill D** | "which columns correlate", "correlation matrix" |

If ambiguous, default to **Sub-Skill A** for broad requests, **Sub-Skill B** for specific operations.
```

**Why this works:**
- Routing table with concrete examples for each path
- Default behavior for ambiguous cases — the skill never stalls
- Each sub-skill is self-contained with its own sub-steps (A1, A2, A3)

---

## Example 5: Detection Flow with Decision Tree (github-auth)

```markdown
## Detection Flow

` ` `bash
git --version
gh --version 2>/dev/null || echo "gh not installed"
gh auth status 2>/dev/null || echo "gh not authenticated"
git config --global credential.helper 2>/dev/null || echo "no git credential helper"
` ` `

**Decision tree:**
1. If `gh auth status` shows authenticated → use `gh` for everything
2. If `gh` is installed but not authenticated → use "gh auth" method
3. If `gh` is not installed → use "git-only" method (no sudo needed)
```

**Why this works:**
- Detects 4 dimensions in one block: git, gh, gh auth, credential helper
- Decision tree has 3 clear paths — skill works for everyone
- Each path leads to a self-contained method section
- Never assumes — always checks first

---

## Example 5b: Dual-Method with Runtime Awareness (duckduckgo-search)

```markdown
## Detection Flow

` ` `bash
command -v ddgs >/dev/null && echo "DDGS_CLI=installed" || echo "DDGS_CLI=missing"
` ` `

Decision tree:
1. If `ddgs` CLI is installed → prefer `terminal` + `ddgs`
2. If `ddgs` CLI is missing → do not assume `execute_code` can import `ddgs`
3. If the user wants DuckDuckGo specifically → install `ddgs` first
4. Otherwise → fall back to built-in web/browser tools

**Important runtime note:**
- Terminal and `execute_code` are separate runtimes
- A successful shell install does not guarantee `execute_code` can import `ddgs`
```

**Why this works:**
- Explicitly warns about the terminal vs execute_code runtime boundary
- 4-level degradation chain: CLI → Python → install → built-in fallback
- `fallback_for_toolsets: [web]` in frontmatter auto-hides when web toolset is configured
- Combines frontmatter-level activation control with runtime-level method selection

---

## Example 6: Runtime Dependency Check with Algorithm Fallback (csv-analysis)

```markdown
## Step 1: Ensure Dependencies Are Available

**Current environment status:**

` ` `
!`python3 -c "exec('try:\n import pandas, numpy, matplotlib\n print(f\'pandas={pandas.__version__} numpy={numpy.__version__} matplotlib={matplotlib.__version__}\')\nexcept Exception:\n print(\'DEPS_MISSING\')')"`
` ` `

If `DEPS_MISSING`, install required packages before running any code:

` ` `python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "pandas", "numpy", "matplotlib"])
` ` `

If all dependencies are already installed, skip the install step and proceed directly.
```

**Why this works:**
- Checks at runtime, not static instructions
- Reports actual versions (useful for debugging)
- Graceful fallback (`|| echo "DEPS_MISSING"`)
- Conditional action: only install if needed, skip otherwise
- Includes the exact install command — no guessing

---

## Example 7: Structured Output Template (deploy-app, Step 9)

```markdown
## Step 9: Respond to the User

Present a structured deployment report with these sections:

1. **Build & Test**: Build status, test results, lint grade
2. **Staging Verification**: Smoke test results, health check status
3. **Production Deployment**: Deployed version, deployment time, strategy used
4. **Post-Deploy Checks**: Uptime, error rate, response time
5. **Rollback Plan**: How to roll back, current state if rolled back
6. **Warnings**: Any warnings from build, staging, or post-deploy
7. **Overall Verdict**: Deployed / Rolled Back / Blocked

Always end with the disclaimer that manual verification is still recommended.
```

**Why this works:**
- 7 numbered sections — output is always structured identically
- Each section specifies exactly what data to include
- Verdict system with 3 clear options (not a spectrum, a decision)
- Mirrors the step structure (steps 2-8 → output sections 1-7)
- Ends with required disclaimer

---

## Example 8: Reference File Pointer Pattern (release-notes)

```markdown
## Reference Files

- `references/changelog-format.md` — Conventional commit parsing, changelog templates
- `references/version-bumping.md` — SemVer rules, pre-release tagging, version comparison
- `references/github-release.md` — GitHub release API, asset upload, release notes formatting
- `references/breaking-changes.md` — How to detect, classify, and document breaking changes
- `references/automated-changelog.md` — Generating changelogs from git log, commit conventional
```

**Why this works:**
- Each reference file is listed with a one-line description
- Descriptions tell you what's in the file without opening it (saves tokens)
- Files are organized by concept-cluster, not by step
- 5 files is a good count for a linear-pattern skill

---

## Example 9: Edge Cases in Reference File (open-pr, lint-rules.md)

```markdown
## Edge Cases

- **No staged changes**: warn user, prompt for files to stage before committing
- **Pre-commit hooks fail**: stop, show hook output, do not skip hooks
- **Branch name conflicts**: if branch exists, append issue number or prompt for new name
- **PR title exceeds 72 chars**: warn but proceed — GitHub allows longer titles
- **Multiple commits on branch**: squash by default, use `--no-squash` to preserve history
```

**Why this works:**
- Specific conditions, not vague "handle errors"
- Each edge case has an exact resolution
- Placed in the reference file (not SKILL.md) to keep main instructions lean
- These are the cases that would cause bugs without explicit handling

---

## Anti-Example: Vague Output (avoid this)

```markdown
## Respond to the User

Summarize the analysis results in a clear and readable format.
Include relevant metrics and insights.
```

**Why this fails:**
- "Clear and readable" means different things every time
- "Relevant metrics" — which ones? All of them? Top 3?
- No numbered sections → inconsistent output across runs
- No verdict → user must interpret everything themselves
