# IEEE Citation Template

Use this template when the user targets an IEEE conference or journal, or explicitly asks for IEEE format. IEEE uses **numeric citations** — references are numbered in the order they first appear in the text, and in-text citations use bracketed numbers.

## Citation Format Rules

### In-text citations

- **Single reference**: `[1]` — use the number assigned in the References section.
- **Multiple references**: `[1], [3], [5]` or `[1]–[3]` for consecutive ranges.
- **Citation as a noun**: "As shown in [1], ..." or "Reference [1] demonstrated...".
- **Author attribution**: "Vaswani et al. [1] introduced..." — author names are optional in IEEE; use them when it improves readability, always followed by the bracketed number.

Numbers are assigned in **order of first appearance in the text**, not alphabetically. The first reference you cite is `[1]`, the second new reference is `[2]`, and so on.

### Reference list entry — published paper (has DOI)

When the paper has a DOI (formally published):

```
[N] A. A. Author, B. B. Author, and C. C. Author, "Title of the paper," Journal Name, vol. X, no. Y, pp. Z, Year. doi: DOI.
```

**Real example**:

```
[1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, "Attention is all you need," 2017. doi: 10.48550/arXiv.1706.03762.
```

Formatting rules for published papers:

- **Author names**: `FirstInitial. LastName` — initials before the last name, opposite of APA. Join with commas; last author gets `and` (no Oxford comma before it in strict IEEE, but accepted).
- **Title**: in double quotes, sentence case. No italics.
- **Journal/venue**: when OpenAlex metadata includes a `primary_location.source.display_name`, include it in italics before the year.
- **DOI**: `doi: <bare_doi>` (no `https://` prefix in IEEE style). This is the preferred form for published papers.

### Reference list entry — preprint (no DOI, has arXiv ID)

When the paper has no DOI but has an arXiv ID:

```
[N] A. A. Author, B. B. Author, and C. C. Author, "Title of the paper," arXiv:ARXIV_ID, Year.
```

**Real example**:

```
[1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, "Attention is all you need," arXiv:1706.03762, 2017.
```

Formatting rules for preprints:

- Same author and title rules as published papers.
- **Source**: `arXiv:<bare_id>` — the literal prefix `arXiv:` followed by the bare id (e.g. `arXiv:1706.03762`, not the full URL).
- **Year**: at the end, after a comma.
- **URL**: optional in IEEE. The `arXiv:<id>` identifier is sufficient and is the IEEE-preferred form.

### Reference list entry — no DOI, no arXiv ID

When the paper has neither (rare):

```
[N] A. A. Author, "Title of the paper," Source Name, Year.
```

Use the OpenAlex `primary_location.source.display_name` or the OpenAlex URL as the source.

### Special cases

- **More than 6 authors**: IEEE allows listing the first author followed by `et al.`: `A. Vaswani et al., "Attention is all you need," arXiv:1706.03762, 2017.` Use this for papers with many authors to keep reference entries readable.
- **DOI takes priority over arXiv**: if a paper has both, cite the published version with the DOI. The published version is canonical.

## Report structure

Follow the shared skeleton in `report-structure.md`. For IEEE, in-text citations use bracketed numbers `[N]` assigned in order of first appearance in the text (not alphabetically). Per-paper annotation headers use `[N] Author et al., "Title" (Year)` form and are ordered by reference number. The References section is a numbered list formatted per the rules above.

## Quality checks before finalizing

Before saving the report, verify:

- [ ] Every paper in the surveyed set has a unique reference number.
- [ ] Reference numbers are assigned in order of **first appearance in the text**, not alphabetically.
- [ ] Every bracketed number in the text has a matching entry in the References section.
- [ ] Every entry in References is cited at least once in the text.
- [ ] Author names use `FirstInitial. LastName` format (initials before last name).
- [ ] Titles are in double quotes and sentence case.
- [ ] Papers with DOIs use the `doi: <bare_doi>` form; preprints use `arXiv:<bare_id>`.
- [ ] Per-paper annotations are ordered by reference number, matching the References section order.
