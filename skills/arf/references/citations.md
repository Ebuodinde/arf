# Citation discipline

Fabricated or misattributed references are the single fastest way a paper fails review, and the most common failure of AI-assisted writing. Treat this file as hard rules.

## Rules
1. **Exists.** Every entry in `references.bib` has a resolvable identifier: DOI, ISBN, PMID, arXiv id, or a stable URL. Set `note = {verified: <how>, <date>}` or the `verified` column in the ledger only after you actually resolved it in this session (tool output, API result, or a user-supplied PDF).
2. **Says it.** Cite a source only for claims you read in that source (full text or, at minimum, the abstract for a claim the abstract makes). Record the location (page, section, table) in the ledger.
3. **Verbatim quotes** are copied exactly from text you have, with page numbers. If you do not have the text, paraphrase from the abstract or do not quote.
4. **No secondary laundering.** If you only know source A through source B's description, cite as "A (as cited in B)" or find A.
5. **Unknowns are visible.** Unsourced sentences get `[[SOURCE?]]` in the draft and are reported to the supervisor.
6. **Metadata from the record, not memory.** Authors, year, title, venue, volume, pages come from the resolved record.

## Ledger format (`sources/ledger.md`)
| key | type | year | verified | role | claim(s) used | location |
|-----|------|------|----------|------|---------------|----------|
| smith2021 | article | 2021 | doi:10.xxxx (Crossref, 2026-10-23) | core / support / counter / method | "…" | p. 14 |

## Tools
- Search: OpenAlex, Crossref, Europe PMC, PubMed, arXiv, bioRxiv, Google Scholar via web search, publisher sites, DergiPark/TR Dizin (Turkish), YÖK Tez Merkezi (Turkish theses).
- Check: `python3 scripts/cite_check.py <project> [--online]`
  - offline: every `[@key]` in `draft/` exists in `references.bib`; every bib entry has an identifier and a verified note; reports unused entries and `[[SOURCE?]]` markers.
  - online: resolves DOIs against Crossref and compares title/year.

## Styles
Write with Pandoc keys; the citation style is applied at build time with a CSL file (`--csl apa.csl`, etc.). Keep the CSL file in the project if the institution requires a specific one.
