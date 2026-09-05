# APA 7th Edition Citation Template

Use this template when the user requests APA format, or when they do not specify a format. APA 7th is the default for social sciences and most CS journals outside of IEEE venues.

## Citation Format Rules

### In-text citations

- **Single author**: `(Vaswani, 2017)` or `Vaswani (2017) showed that...`
- **Two authors**: `(Vaswani & Shazeer, 2017)` — use `&` inside parentheses, "and" in running text.
- **Three or more authors**: `(Vaswani et al., 2017)` — use `et al.` from the first citation onward (APA 7th changed this from APA 6th).
- **Multiple citations**: `(Vaswani et al., 2017; Devlin et al., 2018)` — alphabetical order, separated by semicolons.

### Reference list entry — published paper (has DOI)

When the paper has a DOI (formally published in a journal or conference proceedings):

```
Author, A. A., Author, B. B., & Author, C. C. (Year). Title of the paper. Journal Name, Volume(Issue), pages. https://doi.org/DOI
```

**Real example** (DOI `10.48550/arXiv.1706.03762`):

```
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. https://doi.org/10.48550/arXiv.1706.03762
```

Formatting rules for published papers:

- **Author names**: `LastName, FirstInitial.` (middle initial optional). Join with commas; last author gets an `&`.
- **Year**: the `published` field's year, in parentheses.
- **Title**: sentence case (only first word and proper nouns capitalized). Italicize titles in typeset output; in plain markdown, leave plain.
- **Journal/venue**: when the OpenAlex metadata includes a `primary_location.source.display_name`, include it in italics before the DOI.
- **DOI**: the full URL `https://doi.org/<DOI>`. This is the preferred citation form for published papers.

### Reference list entry — preprint (no DOI, has arXiv ID)

When the paper has no DOI but has an arXiv ID (preprint only):

```
Author, A. A., & Author, B. B. (Year). Title of the paper. arXiv. https://arxiv.org/abs/ARXIV_ID
```

**Real example**:

```
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). Attention is all you need. arXiv. https://arxiv.org/abs/1706.03762
```

Formatting rules for preprints:

- Same author and year rules as published papers.
- **Source**: the literal word `arXiv`, then the full abs URL.
- **No DOI** — the arXiv URL serves as the locator.

### Reference list entry — no DOI, no arXiv ID

When the paper has neither a DOI nor an arXiv ID (rare — usually older or non-CS papers):

```
Author, A. A. (Year). Title of the paper. Retrieved from <primary_location.source.display_name or OpenAlex URL>
```

### Special cases

- **Up to 20 authors**: list all of them separated by commas, with `&` before the last.
- **21 or more authors**: list the first 19, then `...`, then the final author.
- **DOI takes priority over arXiv**: if a paper has both (e.g. published in a journal but also on arXiv), cite the published version with the DOI. The arXiv version is the preprint; the published version is the canonical one.

## Report structure

Follow the shared skeleton in `report-structure.md`. For APA, in-text citations use parenthetical author-date form as described above, per-paper annotation headers use `Author (Year)` form, and the References section is an alphabetical list formatted per the rules above.

## Quality checks before finalizing

Before saving the report, verify:

- [ ] Every paper in the surveyed set appears **both** in "Per-Paper Annotations" **and** in "References".
- [ ] Every in-text citation matches a reference entry (no dangling citations).
- [ ] Authors are formatted `LastName, FirstInitial.` — not `FirstName LastName`.
- [ ] Years are in parentheses inline, and at the start of reference entries.
- [ ] Titles are in sentence case in references (only first word + proper nouns capitalized).
- [ ] Papers with DOIs use the `https://doi.org/...` URL; preprints use the `https://arxiv.org/abs/...` URL.
- [ ] References are alphabetized by first author's last name.
