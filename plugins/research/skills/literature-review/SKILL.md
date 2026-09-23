---
name: literature-review
description: Use when the user wants a systematic literature review, survey, or synthesis across multiple academic papers on a topic. Also covers annotated bibliographies and cross-paper comparisons. Searches OpenAlex (relevance-sorted, date-filtered, with reverse-citation lookup) and outputs reports in APA, IEEE, or BibTeX format. Not for single-paper tasks.
allowed-tools: Bash(python:*) Bash(python3:*) Read
---

# Literature Review Skill

## Overview

This skill produces a structured **systematic literature review (SLR)** across multiple academic papers on a research topic. Given a topic query, it searches OpenAlex, extracts structured metadata (research question, methodology, key findings, limitations) from each paper in parallel, synthesizes themes across the full set, and emits a final report with consistent citations.

OpenAlex provides citation counts, date filtering, reverse-citation lookup, topic clustering, and rich metadata (DOIs, open-access PDF links, concepts) — all in a single free API with no key required.

## When to Use This Skill

Use this skill when the user wants any of the following:

- A literature survey on a topic ("survey transformer attention variants", "review the literature on diffusion models")
- A synthesis across multiple papers ("what do recent papers say about X", "compare methodologies across papers on Y")
- A systematic review with consistent citation format ("do an SLR on Z in APA format")
- An annotated bibliography on a topic
- An overview of research trends in a field over a time window
- A citation-network review starting from a seed paper ("find papers citing X")

Do **not** use this skill when:

- The user provides exactly one paper and asks to review it
- The user asks a factual question that does not require synthesizing multiple sources (answer directly)
- The user wants general web research without academic rigor (use standard web search)

## Workflow

The workflow has five phases. Follow them in order.

### Phase 1: Plan

Before doing any retrieval, confirm the following with the user. If any of these are unclear, ask **one** clarifying question that covers the missing pieces. Do not ask one question at a time.

- **Topic**: the research area in plain English (e.g. "transformer attention variants").
- **Scope**: how many papers (default 20, hard upper bound 50), optional time window (e.g. "last 2 years").
- **Search mode**: default is relevance-sorted search (most topically relevant papers). Alternatives:
  - **Citation-sorted**: user wants "most influential" or "most cited" papers — use `--sort-by cited_by_count`.
  - **Seed expansion**: user gives a seed paper (title or OpenAlex ID) and wants papers citing it — use `--cites`.
  - **Topic clustering**: user wants to see sub-areas before diving in — use `--group-by primary_topic.id` first, then search within the most relevant cluster.
- **Citation format**: APA, IEEE, or BibTeX (default APA if the user does not specify and does not seem to be writing for a specific venue).
- **Output location**: where to save the final report (default: current working directory).

If the user says "50+ papers", politely cap it at 50 and explain that synthesis quality degrades quickly past that — for larger surveys they should split by sub-topic.

### Phase 2: Search OpenAlex

Call the bundled search script. Do **not** try to query OpenAlex by other means and do **not** write your own HTTP client — this script handles URL encoding, abstract reconstruction from inverted index, and metadata extraction correctly.

#### Default search (relevance-sorted)

```bash
python3 ~/.config/opencode/skills/literature-review/scripts/openalex_search.py \
  "<topic>" \
  --max-results <N> \
  --sort-by relevance \
  [--start-date YYYY-MM-DD] \
  [--end-date YYYY-MM-DD] \
  [--concept "<concept name or ID>"] \
  > /tmp/literature-review-search.json
```

**Redirect output to a file** — the JSON can be 30-50 KB and will bloat your context if printed to stdout. After saving, read a quick summary to plan batching:

```bash
python3 -c "
import json
with open('/tmp/literature-review-search.json') as f:
    data = json.load(f)
print(f'Total: {data[\"meta\"][\"count\"]} papers, retrieved: {len(data[\"results\"])}')
for i, r in enumerate(data['results'], 1):
    print(f'{i}. [{r[\"cited_by_count\"]} cites] {r[\"published\"]} | {r[\"title\"][:80]}')
"
```

The full JSON stays in the file — do not load it into your context. You only need the summary (count, titles, citation counts) to plan Phase 3 batching. Subagents read the batch files directly.

**Sort strategy**:

- **`--sort-by relevance` (default)** — OpenAlex's text-matching score. Surfaces papers most topically relevant to the query, regardless of citation count. Best for most searches.
- **`--sort-by cited_by_count`** — ranks by impact. Use when the user explicitly asks for "most influential" or "most cited" papers. Combine with `--start-date` to find impactful papers within a time window.
- **`--sort-by publication_date`** — newest first. Use when the user explicitly asks for chronological order or "the latest papers on X".

**Query phrasing**:

OpenAlex full-text search handles multi-word queries naturally — pass the user's topic description more or less as-is. If results seem off-topic, add `--concept` to narrow the field (e.g. `--concept "Artificial intelligence"`).

**Date filtering**:

Always apply a date range when the user mentions "recent" work or a time window. Use `--start-date` and `--end-date` to constrain results. When the user says "last N years", compute the start date from today. Combine with `--sort-by relevance` (default) for on-topic results within the window, or `--sort-by cited_by_count` for the most impactful papers in the window.

**Concept filtering**:

Use `--concept` to narrow results to a field. Accepts either a concept ID (e.g. `C41008148` for Computer science) or a display name (e.g. `"Natural language processing"`). This is analogous to arXiv category filtering but uses OpenAlex's concept taxonomy, which spans all academic disciplines.

#### Seed expansion (reverse-citation lookup)

When the user provides a seed paper and wants to find papers citing it:

```bash
python3 ~/.config/opencode/skills/literature-review/scripts/openalex_search.py \
  --cites <OpenAlex-work-ID-or-URL> \
  --max-results <N> \
  [--sort-by cited_by_count] \
  > /tmp/literature-review-search.json
```

The work ID can be either a bare ID (e.g. `W4403944333`) or a full OpenAlex URL (e.g. `https://openalex.org/W4403944333`). If the user gives a paper title, search for it first to get the OpenAlex ID, then run the reverse-citation lookup.

#### Topic clustering (optional pre-step)

To identify sub-areas within a topic before committing to a full search:

```bash
python3 ~/.config/opencode/skills/literature-review/scripts/openalex_search.py \
  "<topic>" \
  --group-by primary_topic.id \
  [--start-date YYYY-MM-DD]
```

This returns cluster counts instead of paper listings. Use it to help the user decide which sub-area to focus on, or to split a large survey into sub-topics.

#### Output format

Each paper in the JSON has: `id`, `title`, `authors`, `abstract`, `published`, `cited_by_count`, `doi`, `arxiv_id`, `pdf_url`, `concepts`, `related_works`, `referenced_works_count`.

**Run the search exactly once.** Do not retry with modified queries if the results seem imperfect — OpenAlex's ranking is what it is. If results are genuinely empty (0 papers), tell the user and suggest they broaden their topic or remove filters.

**If the script fails** (network error, non-200 from OpenAlex), tell the user which error and stop. Do not try to fabricate paper metadata.

### Phase 3: Extract metadata in parallel

**You MUST delegate extraction to subagents via the `task` tool — do not extract metadata yourself.** This is non-negotiable. Specifically, do NOT do any of the following:

- ❌ Write `python -c "papers = [...]"` or any Python/bash script to process papers
- ❌ Extract metadata inline in your own context by reading abstracts one by one
- ❌ Use any tool other than `task` for this phase

Instead, you MUST call the `task` tool to spawn subagents. The reason: extracting 10-50 papers in your own context consumes too many tokens and degrades synthesis quality in Phase 4. Each subagent runs in an isolated context with only its batch of papers, producing cleaner extractions.

#### Step 1: Split search results into batch files

Use a Python one-liner to split the search results file into batches of ~5 papers each, each written to its own file:

```bash
python3 -c "
import json
with open('/tmp/literature-review-search.json') as f:
    data = json.load(f)
results = data['results']
batch_size = 5
for i in range(0, len(results), batch_size):
    batch = results[i:i+batch_size]
    batch_num = i // batch_size + 1
    with open(f'/tmp/literature-review-batch-{batch_num}.json', 'w') as bf:
        json.dump(batch, bf, ensure_ascii=False, indent=2)
total = (len(results) + batch_size - 1) // batch_size
print(f'Split {len(results)} papers into {total} batches')
"
```

#### Step 2: Dispatch subagents

For each batch, call the `task` tool with `subagent_type: "general"`. Each subagent reads its batch file and writes its extraction to a unique output file — this avoids returning large JSON through the subagent's response and prevents context bloat.

**Concurrency limit: at most 3 subagents per turn.** Dispatch at most 3 `task` calls in a single response — wait for them to complete before dispatching the next round. Strictly follow the round strategy below.

**Round strategy — use this decision table, do not compute the split yourself**:

| Paper count | Batches of ~5 papers | Rounds | Per-round subagent count |
|---|---|---|---|
| 1–5 | 1 batch | 1 round | 1 subagent |
| 6–10 | 2 batches | 1 round | 2 subagents |
| 11–15 | 3 batches | 1 round | 3 subagents |
| 16–20 | 4 batches | 2 rounds | 3 + 1 |
| 21–25 | 5 batches | 2 rounds | 3 + 2 |
| 26–30 | 6 batches | 2 rounds | 3 + 3 |
| 31–35 | 7 batches | 3 rounds | 3 + 3 + 1 |
| 36–40 | 8 batches | 3 rounds | 3 + 3 + 2 |
| 41–45 | 9 batches | 3 rounds | 3 + 3 + 3 |
| 46–50 | 10 batches | 4 rounds | 3 + 3 + 3 + 1 |

**Never dispatch more than 3 subagents in the same turn.** When a row says "2 rounds (3 + 1)", that means: first turn dispatches 3 subagents in parallel, wait for all 3 to complete, then second turn dispatches 1 subagent. Rounds are strictly sequential at the main-agent level.

If the paper count lands between rows (e.g. 23 papers), round up to the next row's layout but only dispatch as many batches as you actually need — the decision table gives you the shape, not a rigid prescription.

**What each subagent receives**, as a structured prompt (replace `<N>` with the batch number):

```
Execute this task: extract structured metadata and key findings from
academic papers stored in a JSON file.

Read the file /tmp/literature-review-batch-<N>.json. It contains an
array of paper objects, each with: id, title, authors, abstract,
published, cited_by_count, doi, arxiv_id, pdf_url, concepts.

For each paper, produce a JSON object with these fields:
- id (string — the OpenAlex work ID or DOI)
- title (string)
- authors (list of strings)
- published_date (string, YYYY-MM-DD)
- cited_by_count (integer — citation count from the metadata)
- research_question (1 sentence, what problem the paper tackles)
- methodology (1-2 sentences, how they tackle it)
- key_findings (3-5 bullet points, what they actually found)
- limitations (1-2 sentences, what they acknowledge or what is obviously missing)

Write the result as a JSON array to /tmp/literature-review-extraction-<N>.json.
Write only the JSON file — do not return the JSON in your response.
Confirm in your response that the file has been written.
```

Each subagent uses a unique batch number N (1, 2, 3, ...) so there is no file overlap. The subagent reads its batch file, extracts metadata, and writes to its own extraction file.

#### Step 3: Aggregate extraction files

After all subagents complete, read all extraction files and flatten them into a single list:

```bash
python3 -c "
import json, glob
all_papers = []
files = sorted(glob.glob('/tmp/literature-review-extraction-*.json'))
for f in files:
    with open(f) as bf:
        all_papers.extend(json.load(bf))
with open('/tmp/literature-review-aggregated.json', 'w') as f:
    json.dump(all_papers, f, ensure_ascii=False, indent=2)
print(f'Aggregated {len(all_papers)} papers from {len(files)} batches')
"
```

Use `/tmp/literature-review-aggregated.json` for Phase 4 synthesis. If the file is large, read it in sections rather than loading the full content into your context.

### Phase 4: Synthesize and format

Now produce the final SLR report. Two things happen here: cross-paper synthesis (thematic analysis) and citation formatting.

**Cross-paper synthesis**: the report must do more than list papers. At minimum, identify:

- **Themes**: 3-6 recurring research directions, approaches, or problem framings across the set. Use the `concepts` field from the search results to help identify themes — papers sharing high-scoring concepts often cluster into the same theme.
- **Convergences**: findings that multiple papers agree on.
- **Disagreements**: where papers reach different conclusions or use incompatible methodologies.
- **Gaps**: what the collective literature does not yet address (often stated explicitly in the "limitations" fields).
- **Impact weighting**: when discussing themes, note which papers are most cited (`cited_by_count`). Highly cited papers that converge on a finding make a stronger claim than low-cite papers. But do not dismiss low-cite papers outright — recent high-quality work may simply not have accumulated citations yet.

If the paper set is too small or too heterogeneous to support thematic synthesis (e.g. 5 papers on wildly different sub-topics), say so explicitly in the report — do not force themes that are not there.

**Citation formatting**: the exact format depends on user preference. Read **only** the template file that matches the user's requested format, not all three:

- `~/.config/opencode/skills/literature-review/templates/apa.md` — APA 7th edition. Default for social sciences and most CS journals. Use when the user requests APA or does not specify a format.
- `~/.config/opencode/skills/literature-review/templates/ieee.md` — IEEE numeric citations. Use when the user targets an IEEE conference or journal, or explicitly asks for IEEE.
- `~/.config/opencode/skills/literature-review/templates/bibtex.md` — BibTeX entries. Use when the user mentions BibTeX, LaTeX, or wants machine-readable references.
- `~/.config/opencode/skills/literature-review/templates/report-structure.md` — Shared report skeleton (Executive Summary, Methodology, Themes, etc.). Read this alongside the format-specific template.

Each template contains the citation rules and quality checks for its format. The shared report skeleton lives in `report-structure.md` — read that alongside the format template, then fill in content from your Phase 3 metadata.

**Papers may be published or preprints.** OpenAlex indexes both. The `doi` field tells you if a paper has been formally published; `arxiv_id` tells you if it has an arXiv preprint version. Cite the published version when available (DOI), and the preprint version otherwise. The templates cover both cases.

### Phase 5: Save and present

Save the full report to `./literature-review-<topic-slug>-<YYYYMMDD>.md` where `<topic-slug>` is a lowercased hyphenated version of the topic (e.g. `transformer-attention`). Then tell the user the file path.

**In the chat message**, show a short preview so the user immediately sees value without opening the file:

1. **Executive summary** — the 3–5 sentence paragraph from the top of the report, verbatim.
2. **Themes list** — bullet list of the themes you identified in Phase 4 synthesis (just the theme names + one-line gloss, not the full theme sections).
3. **Paper count + a pointer to the file** — e.g. "Full report with 20 papers, per-paper annotations, and formatted references saved to `literature-review-transformer-attention-20260905.md`."

Do **not** dump the full 2000+ word report inline — per-paper annotations, references, and methodology belong in the file. The preview is there to let the user judge the report at a glance and decide whether to open it.

## Examples

**Example 1: Typical SLR request**

User: "Do a systematic literature review of recent transformer attention variants, 20 papers, APA format."

Your flow:
1. Phase 1: confirm topic (transformer attention variants), scope (20 papers, default time window), format (APA). Ask **one** clarification only if something is missing.
2. Phase 2: `openalex_search.py "transformer attention variants" --max-results 20 --sort-by relevance --start-date 2024-01-01 > /tmp/literature-review-search.json`, then read summary.
3. Phase 3: split into 4 batch files, round 1 = 3 subagents × 5 papers = 15 covered, round 2 = 1 subagent × 5 papers = 5 covered. Aggregate extraction files.
4. Phase 4: read `templates/apa.md` and `templates/report-structure.md`, write the report, fill in themes + per-paper annotations from Phase 3 metadata.
5. Phase 5: save to `literature-review-transformer-attention-20260905.md`, tell the user the path.

**Example 2: Seed expansion request**

User: "Find papers citing 'Attention Is All You Need' and review them, 20 papers."

Your flow:
1. Phase 1: confirm scope (20 papers), format (default APA). The seed paper is clear.
2. Phase 2: first search for the seed to get its OpenAlex ID: `openalex_search.py "Attention Is All You Need" --max-results 1`. Then run `openalex_search.py --cites W2963598320 --max-results 20 --sort-by cited_by_count > /tmp/literature-review-search.json`, then read summary.
3. Phase 3–5: same as Example 1.

**Example 3: Small-set request with ambiguity**

User: "Survey a few papers on diffusion models for me."

Your flow:
1. Phase 1: "a few" is ambiguous. Ask one question: "How many papers would you like — 10, 20, or 30? And any citation format preference (APA is the default)?"
2. User responds "10, BibTeX".
3. Phase 2: `openalex_search.py "diffusion models" --max-results 10 --sort-by relevance --concept "Computer vision" > /tmp/literature-review-search.json`, then read summary.
4. Phase 3: split into 2 batch files, single round, 2 subagents × 5 papers. Aggregate.
5. Phase 4: read `templates/bibtex.md`, format with `@misc` for preprints and `@article` for published papers.
6. Phase 5: save and tell the user the path.

**Example 4: Out-of-scope request**

User: "Here's one paper (https://arxiv.org/abs/1706.03762). Can you review it?"

This is a single-paper peer review, not a literature survey. Do not use this skill.

## Notes

- **OpenAlex only, by design**. This skill queries OpenAlex, which indexes papers across all academic disciplines — not just CS/ML preprints. For multi-source search (PubMed, Google Scholar, Semantic Scholar), use a dedicated MCP server, not this skill.
- **Hard upper bound of 50 papers**. This is tied to the Phase 3 concurrency strategy (max 3 subagents per round, ~5 papers each, at most ~4 rounds). Surveys larger than 50 papers degrade in synthesis quality and are better done by splitting into sub-topics.
- **The `id` field is an OpenAlex work ID** (e.g. `https://openalex.org/W4402952320`). The `doi` field (when present) has the full DOI URL. The `arxiv_id` field (when present) is a bare arXiv ID. Use the DOI for citation when available; fall back to the arXiv ID for preprint-only papers.
- **Abstracts may be empty.** OpenAlex stores abstracts as an inverted index; the search script reconstructs them, but some works have no abstract (empty string). If a paper has no abstract, the subagent should note this and extract what it can from the title and concepts.
- **Citation counts are a signal, not a filter.** High `cited_by_count` means a paper has been influential, but recent papers will have low counts simply because they are new. When sorting by citation count, consider whether the user wants "most influential ever" or "most influential recently" — for the latter, add `--start-date` to constrain the time window.
- **File-based data flow.** Search results, batch files, and extraction files all live in `/tmp/`. This prevents context bloat at both the main-agent and subagent levels. The only output that matters to the user is the final report in Phase 5.
- **Synthesis, not listing**. The final report must identify themes and compare findings across papers. A report that only lists papers one after another is a failure mode — if you cannot find themes, say so explicitly instead of faking them.
