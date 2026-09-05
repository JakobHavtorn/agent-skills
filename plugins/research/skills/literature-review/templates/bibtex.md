# BibTeX Citation Template

Use this template when the user mentions BibTeX, LaTeX, wants machine-readable references, or is writing a paper that will be typeset with a LaTeX citation style (natbib, biblatex, etc.).

## Entry type: `@article` vs `@misc`

OpenAlex indexes both published papers and preprints. Choose the entry type based on what metadata is available:

- **`@article`** — use when the paper has a DOI and was formally published in a journal or conference proceedings. This is the canonical entry type for published work.
- **`@misc`** — use when the paper has no DOI and is only available as a preprint (e.g. arXiv-only). This is the correct entry type for preprints, technical reports, and other non-journal publications.
- **`@inproceedings`** — use when the paper was published in a conference (if the OpenAlex metadata includes a venue name that is clearly a conference, not a journal).

**DOI takes priority**: if a paper has both a DOI and an arXiv ID, it was published — use `@article` (or `@inproceedings`) with the DOI. Do not use `@misc` for a paper that has been formally published.

## Citation Format Rules

### Entry structure — published paper (`@article`)

```bibtex
@article{citekey,
  author  = {LastName1, FirstName1 and LastName2, FirstName2 and ...},
  title   = {Title of the Paper},
  journal = {Journal or Venue Name},
  year    = {YYYY},
  volume  = {VOLUME},
  number  = {ISSUE},
  pages   = {PAGE_RANGE},
  doi     = {DOI}
}
```

**Real example**:

```bibtex
@article{vaswani2017attention,
  author  = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, {\L}ukasz and Polosukhin, Illia},
  title   = {Attention Is All You Need},
  year    = {2017},
  doi     = {10.48550/arXiv.1706.03762}
}
```

### Entry structure — preprint (`@misc`)

```bibtex
@misc{citekey,
  author        = {LastName1, FirstName1 and LastName2, FirstName2 and ...},
  title         = {Title of the Paper},
  year          = {YYYY},
  eprint        = {ARXIV_ID},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/ARXIV_ID}
}
```

**Real example**:

```bibtex
@misc{vaswani2017attention,
  author        = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, {\L}ukasz and Polosukhin, Illia},
  title         = {Attention Is All You Need},
  year          = {2017},
  eprint        = {1706.03762},
  archivePrefix = {arXiv},
  url           = {https://arxiv.org/abs/1706.03762}
}
```

### Field rules

- **Cite key**: `<firstauthorlast><year><firstwordoftitle>`, all lowercase, no punctuation. Example: `vaswani2017attention`. Keys must be unique within the report.
- **`author`**: `LastName, FirstName and LastName, FirstName and ...` — note the literal word `and` between authors, not a comma. LaTeX requires this exact separator. LastName comes first, then a comma, then the given names.
- **Special characters**: escape or wrap LaTeX-sensitive characters. For example, `Łukasz` becomes `{\L}ukasz`, `é` becomes `{\'e}` (or wrap the whole name in braces to preserve casing: `{Łukasz}`). If unsure, wrap the problematic name in curly braces.
- **`title`**: preserve the paper's capitalization by wrapping it in double braces if it contains acronyms or proper nouns you need to keep capitalized: `title = {{BERT}: Pre-training of Deep Bidirectional Transformers}`. Otherwise plain braces are fine.
- **`year`**: the 4-digit year from the paper's `published` field.
- **`doi`**: the bare DOI (e.g. `10.48550/arXiv.1706.03762`), without the `https://doi.org/` prefix.
- **`journal`**: the venue name from OpenAlex's `primary_location.source.display_name`, when available. Omit if not present.
- **`eprint`**: the **bare arXiv id** (e.g. `1706.03762`), **without** the `arXiv:` prefix and **without** the version suffix. Only present for preprints.
- **`archivePrefix`**: literal string `{arXiv}`. Only for `@misc` preprint entries.
- **`url`**: for preprints, the full `https://arxiv.org/abs/<id>` URL. For published papers with DOIs, the `doi` field is sufficient — `url` is optional.

## Report structure

Follow the shared skeleton in `report-structure.md`, with these BibTeX-specific deviations:

- In-text citations use `\cite{key}` form instead of parenthetical or numeric citations.
- Per-paper annotation headers use `\cite{key} — "Title" (Year)` form.
- The final section is titled **BibTeX Bibliography** (not "References") and contains `@article`, `@inproceedings`, and `@misc` entries inside a fenced ```` ```bibtex ```` code block so users can copy-paste into a `.bib` file.

## Quality checks before finalizing

Before saving the report, verify:

- [ ] Published papers (with DOI) use `@article` or `@inproceedings`; preprints (no DOI) use `@misc`.
- [ ] Cite keys are unique within the report.
- [ ] Cite keys follow the `<firstauthorlast><year><firstword>` pattern, all lowercase.
- [ ] `author` field uses ` and ` (the literal word) between authors, not commas.
- [ ] LaTeX special characters in author names are escaped or brace-wrapped.
- [ ] DOI field (when present) is the bare DOI, no `https://doi.org/` prefix.
- [ ] `eprint` (for preprints) is the bare arXiv id (no `arXiv:` prefix, no version suffix).
- [ ] Every `\cite{key}` in the text has a matching entry in the bibliography.
- [ ] The bibliography is emitted inside a fenced ```` ```bibtex ```` code block so users can copy-paste directly into a `.bib` file.
