# Phases in detail

Each phase: inputs → work → artifact → gate. One iteration = one scoped unit of work followed by a checkpoint report.

## 1. brief
Inputs: user's topic and constraints.
Work: fill `00-brief.md`: working title, level, genre (`genres.md`), discipline, language, target length (words), citation style (APA 7, Chicago, IEEE, ISNAD, MLA…), deadline, institution/course/journal rules, required/forbidden sources, the author's prior knowledge, AI-use policy of the institution (ask; if unknown, record "unknown").
Gate: supervisor confirms the brief.

## 2. question
Work: do a fast scoping search (10–20 abstracts). Propose 2–3 candidate research questions or thesis statements, each with: why it matters, what is already known, the gap, feasibility at this level/length, and the expected type of contribution (synthesis, argument, empirical analysis, case study, replication). Recommend one.
Artifact: `01-question.md` with the chosen RQ, sub-questions, scope in/out, key terms with working definitions.
Gate: supervisor picks or edits the RQ.

## 3. sources
Work: systematic search. Record search strings, databases, date, and counts in `sources/search-log.md` (this is what makes a literature review reproducible). Screen by title/abstract, then read the selected items. For each retained source add a ledger row and a `references.bib` entry with DOI/URL. Write a one-paragraph note per core source in `sources/notes/<key>.md`: argument, method, evidence, limitations, page references for quotable claims.
Targets (guidance, adjust to discipline): undergrad 10–25 sources; master's 30–60; doctoral/journal 50+; mostly peer-reviewed; include seminal and recent (last 5 years) work; include at least one strong opposing view.
Gate: supervisor reviews the ledger summary (counts by type/year, core 5–10 sources, known gaps).

## 4. outline (argument map)
Work: build `02-outline.md`:
- Thesis / main claim in one sentence.
- Sections with target word counts that sum to the brief.
- For each section: its claim, the sub-claims, which ledger sources support each, the counter-argument it must address, and how it hands off to the next section.
Check: every sub-claim has at least one source or is marked as the author's own analysis; nothing in the outline lacks a role in answering the RQ.
Gate: supervisor approves the argument, not just headings.

## 5. voice
Work: ask the author for 1–3 samples of their own writing (any prior essay, thesis, report; ideally same language). Build `voice/profile.md` per `voice.md`. If none are available, build a profile from the discipline/level register and say so.
Gate: supervisor confirms the profile reads like the author.

## 6. draft
Order: usually body sections first, then method/results if empirical, then discussion, then introduction, conclusion, abstract last.
Per iteration: draft one section into `draft/NN-slug.md` from the outline, citing with `[@key]`. Then run `cite_check.py` and `prose_lint.py`, fix, and report. Mark any sentence you could not source with `[[SOURCE?]]` and list them in the report — never paper over them.
Gate: per section.

## 7. revise
Run passes in this order, each as its own iteration, logged in `revisions/log.md`:
1. Structure: does the order serve the argument; are sections proportionate; any repetition across sections.
2. Argument: is each claim warranted; are counter-arguments addressed fairly; is the conclusion earned by the body and no larger than it.
3. Evidence: re-open the ledger; check each citation supports exactly the sentence it is attached to; quotes are verbatim with page numbers.
4. Prose: `style.md` checklist, voice profile, terminology consistency, transitions, paragraph unity. Read paragraphs aloud mentally; cut what a tired examiner would skip.
5. Format: citation style, headings, figures/tables numbering, abstract/keywords, length.
Gate: after each pass.

## 8. audit
Run `arf.py audit <dir>`. Fill `audit.md` with results. Draft `disclosure.md` (see `integrity.md`). Build `paper.md`. Final report to supervisor.
