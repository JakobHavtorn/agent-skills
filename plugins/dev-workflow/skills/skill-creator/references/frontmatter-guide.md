# SKILL.md Frontmatter Reference

Complete field reference for the YAML frontmatter block that starts every SKILL.md file.

## Required Fields

### `name`
- **Type:** string
- **Max length:** 64 characters
- **Pattern:** `^[a-z0-9][a-z0-9._-]*$` (lowercase alphanumeric, hyphens, dots, underscores)
- **Purpose:** Unique identifier used in slash commands, file paths, and skill references

```yaml
name: my-skill-name
```

### `description`
- **Type:** string (multi-line with `>` recommended)
- **Max length:** 1024 characters
- **Purpose:** Controls when the skill activates. This is the most important field for skill quality.

```yaml
description: >
  [What it does] Deploy an app through a gated CI/CD pipeline.
  [Expert triggers] deploy, staging, promote, rollback, smoke test, canary.
  [Beginner triggers] "ship this", "put it in production", "is it safe to deploy".
  [Context triggers] When user mentions a release, a build, or a merge to main.
```

**Writing a high-quality description:**

1. Start with a concrete action verb: "Analyze", "Generate", "Fetch", "Evaluate" (not "Use" or "Handle")
2. Name specific tools/APIs: "via gh CLI", "using the GitHub API"
3. List 5+ explicit trigger phrases in quotes
4. Include 2+ sideways entry points (unexpected phrasings)
5. End with context triggers ("also when the user...")

**Common mistakes:**
- Too short: "Deploy apps" — won't trigger on specific requests
- Too generic: "DevOps tool" — triggers on everything, useful for nothing
- Missing beginner terms: Only expert jargon excludes most users

## Optional Fields

### `version`
Semantic version for the skill. Useful for tracking changes.
```yaml
version: 1.0.0
```

### `author`
Creator name or handle.
```yaml
author: your-name
```

### `license`
License identifier.
```yaml
license: MIT
```

### `platforms`
Restrict to specific operating systems. Omit to load on all platforms (default).
```yaml
platforms: [macos, linux]   # Valid values: macos, linux, windows
```

### `required_environment_variables`
Declare API keys or tokens the skill needs. Store secrets as environment variables or in your platform's credential system.

```yaml
required_environment_variables:
  - name: GITHUB_TOKEN
    prompt: "GitHub personal access token"
    help: "Create one at https://github.com/settings/tokens"
    required_for: "GitHub API access"
```

Fields per entry:
- `name` (required) — environment variable name
- `prompt` (optional) — text shown when asking the user
- `help` (optional) — URL or help text for obtaining the value
- `required_for` (optional) — which feature needs this variable

### `required_credential_files`
Declare file-based credentials (OAuth tokens, certificates).

```yaml
required_credential_files:
  - path: google_token.json
    description: Google OAuth2 token (created by setup script)
```

### `metadata`
Arbitrary key-value mapping for additional metadata. Some agent implementations define product-specific keys under `metadata` for discovery, activation, and configuration. Check your platform's documentation for supported fields.

```yaml
metadata:
  tags: [DevOps, Deployment, CI/CD]
  related_skills: [open-pr, release-notes]
  category: devops
```

### Conditional Activation

Some agent implementations support conditional activation via frontmatter. These control when the skill appears in the system prompt:

```yaml
metadata:
  requires_toolsets: [terminal]              # Hide if terminal toolset NOT active
  fallback_for_toolsets: [browser]            # Hide if browser IS active
```

| Field | Logic |
|---|---|
| `requires_toolsets` | Hidden when ANY listed toolset is unavailable |
| `fallback_for_toolsets` | Hidden when ANY listed toolset IS available |

Note: These fields are product-specific extensions, not part of the core Agent Skills spec. Not all implementations support them.

### Config Settings

Non-secret settings can be declared in metadata for some implementations:

```yaml
metadata:
  config:
    - key: deploy.target
      description: Default deployment target
      default: "staging"
      prompt: "Deployment target (staging or production)"
```

## Complete Frontmatter Example

```yaml
---
name: deploy-app
description: >
  Deploy an app through a gated CI/CD pipeline with build, test, staging,
  and production promotion steps. Triggers: deploy, ship, promote, rollback,
  canary, smoke test, "put it in production", "is it safe to deploy",
  release pipeline, CD pipeline, staging deployment.
version: 1.0.0
author: your-name
license: MIT
metadata:
  tags: [DevOps, Deployment, CI/CD]
  related_skills: [open-pr, release-notes]
---
```

## Size Constraints Summary

| Field | Limit |
|---|---|
| `name` | 64 characters |
| `description` | 1024 characters |
| SKILL.md total content | 100,000 characters |
| Supporting files | 1 MiB each |
| Category name | 64 characters, single directory level |
