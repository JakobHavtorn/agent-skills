# Shared Report Structure

Read this file alongside the format-specific citation template (APA, IEEE, or BibTeX). The structure below is the same for all formats — only the citation style changes. The format template tells you how to format in-text citations and reference entries; this file tells you how to organize the report.

## Report skeleton

```markdown
# Literature Review: <Topic>

**Date**: <YYYY-MM-DD>
**Papers surveyed**: <N>
**Scope**: <OpenAlex search query, concept filter, time window, sort order>
**Citation format**: <APA 7th edition | IEEE | BibTeX>

## Executive Summary

<3-5 sentences summarizing the state of the literature on this topic. What do the surveyed papers collectively tell us? What is the shape of the field? Avoid listing papers — synthesize.>

## Methodology

This review surveyed <N> papers retrieved on <YYYY-MM-DD> from OpenAlex using the query `<query>`<, filtered to concept <concept>><, published between <start_date> and <end_date>>. Papers were sorted by <citation count | relevance | publication date> and the top <N> were included. Metadata extraction (research question, methodology, key findings, limitations) was performed by language-model agents, with cross-paper synthesis performed by the lead agent.

**Limitations of this review**: Coverage is limited to papers indexed in OpenAlex; papers in venues not indexed by OpenAlex may be missing. Citation counts reflect OpenAlex's citation graph as of the retrieval date. Preprints are included alongside published papers — some preprints may not reflect their final published form.

## Themes

<3-6 thematic sections. Each theme is a recurring research direction, problem framing, or methodological approach across the surveyed papers. Use the `concepts` field from the search results to help identify themes — papers sharing high-scoring concepts often cluster into the same theme.>

### Theme 1: <Theme name>

<2-4 paragraphs describing this theme. Cite papers inline as you discuss them, using the citation style specified in the format template. Do not just list papers — describe the intellectual thread that connects them. Note highly cited papers (`cited_by_count`) when their influence is relevant to the theme.>

### Theme 2: <Theme name>

<...>

## Convergences and Disagreements

**Convergences**: <findings that multiple papers agree on — e.g. "Most surveyed papers agree that X is necessary, citing evidence from Y and Z.">

**Disagreements**: <where papers reach different conclusions — e.g. "Paper A argues that X, while Paper B finds the opposite under condition Y.">

## Gaps and Open Questions

<What the collective literature does not yet address. Pull from the "limitations" field of your Phase 3 extraction and identify patterns — if 5 papers all mention the same missing piece, that is a gap worth flagging.>

## Per-Paper Annotations

<One subsection per paper, ordered by citation count (most cited first) or by year then first author. Each subsection is a mini-summary of that paper's contribution.>

### <Paper citation header>

**Citations**: <cited_by_count>

**Research question**: <1 sentence from Phase 3 metadata>
**Methodology**: <1-2 sentences>
**Key findings**:
- <bullet>
- <bullet>
- <bullet>
**Limitations**: <1-2 sentences>

### <Next paper>

<...>

## References

<Format the reference list according to the format-specific citation template. Published papers (with DOI) and preprints (with arXiv ID) may both appear — format each according to its type.>
```
