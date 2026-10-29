# Arf

**Supervised academic paper writing for AI agents.** Named after the mathematician [Cahit Arf](https://en.wikipedia.org/wiki/Cahit_Arf).

Arf turns a coding agent (Antigravity, Claude Code, Codex, …) into a disciplined academic writer. The **agent** does the work — literature search, source verification, argument mapping, drafting, revision. The **human** acts as supervisor and approves each step. Works at undergraduate, master's and doctoral/journal level, in any language (Turkish and English phrase packs included).

> Türkçe özet: Arf, verilen konuda akademik makaleyi ajan araştırıp yazarken kullanıcının danışman (supervisor) gibi her aşamayı onayladığı, kaynakları doğrulanmış, yazarın kendi sesine uyarlanmış, iteratif bir yazım iş akışıdır. Lisans, yüksek lisans ve doktora düzeyini destekler; makale hangi dilde olursa olsun çalışır.

## Why

AI-assisted papers fail in predictable ways: invented references, citations that don't say what the sentence claims, generic padded prose, arguments that don't answer the question, and authors who can't defend their own text. Arf is built around those failure modes:

- **Gated pipeline** — brief → question → sources → outline → voice → draft → revise → audit. Nothing is drafted before the argument is approved, and no gate passes on an unfilled template.
- **Verified citations** — every reference needs a resolvable identifier and a verification note; `cite_check.py` blocks the draft gate on missing or unverified keys and `[[SOURCE?]]` markers, and can resolve DOIs against Crossref.
- **Author's voice** — a voice profile built from the author's own writing samples; no house style.
- **Prose review** — `prose_lint.py` flags filler phrases, overused connectives, monotone rhythm, repeated openers, list-heavy argument and over-long sentences (TR/EN packs; add your language in `skills/arf/patterns/`, prefix a line with `~` to flag it only when overused).
- **Editorial log + disclosure** — every supervisor decision is logged, and an AI-use disclosure is drafted for the author's institution.

Arf aims for papers that hold up on their merits. It does not fabricate data or sources and does not include tooling to evade AI or plagiarism detectors — see [integrity.md](skills/arf/references/integrity.md).

## Install

```sh
git clone https://github.com/Ebuodinde/arf.git && cd arf
./install.sh            # antigravity + claude + codex (symlinks)
./install.sh claude     # just one host
```

Then in your agent: `/arf <topic>` (Antigravity, Claude Code) or `$arf <topic>` (Codex).

Requirements: Python 3.10+ (stdlib only). Optional: `pandoc` for DOCX/PDF export (PDF also needs a LaTeX engine); network access for literature search and `--online` DOI checks (set `ARF_MAILTO=you@example.org` to identify yourself to Crossref).

## Use

```
/arf Türkiye'de kırsal okullarda taşımalı eğitimin devamsızlığa etkisi — yüksek lisans, 8000 kelime, APA 7
```

The agent creates a project folder and walks the gates with you. At each checkpoint it reports what it did, the files, and the decisions it needs. Reply `devam`/`continue` to approve, or give feedback.

Project layout:

```
my-paper/
  arf.json             phase + gate state
  00-brief.md          constraints, level, style, institution AI policy
  01-question.md       research question, scope, key terms
  02-outline.md        argument map with sources per claim
  sources/ledger.md    claim → source → location trail
  sources/search-log.md
  sources/notes/       per-source reading notes
  references.bib       verified bibliography
  voice/profile.md     author's voice profile (+ samples/)
  draft/NN-*.md        sections, Pandoc citations [@key]
  revisions/log.md     supervisor feedback and responses
  audit.md             final checks
  disclosure.md        AI-use statement
  paper.md             assembled paper
```

CLI (the agent runs these; you can too):

```sh
python3 skills/arf/scripts/arf.py init my-paper --title "…" --level masters --lang tr
python3 skills/arf/scripts/arf.py status my-paper
python3 skills/arf/scripts/arf.py gate my-paper outline --approve
python3 skills/arf/scripts/arf.py log my-paper outline --feedback "2. bölüm çok uzun" --change "1200 → 800 kelime"
python3 skills/arf/scripts/cite_check.py my-paper --online
python3 skills/arf/scripts/prose_lint.py my-paper/draft/03-bulgular.md --lang tr
python3 skills/arf/scripts/arf.py audit my-paper
python3 skills/arf/scripts/arf.py build my-paper --docx --csl apa.csl
```

## Repository

```
plugin.json                  Antigravity plugin manifest
skills/arf/SKILL.md          the skill (entry point for all hosts)
skills/arf/references/       phases, levels, genres, citations, style, voice, supervisor, integrity
skills/arf/templates/        project templates
skills/arf/patterns/         phrase packs per language
skills/arf/scripts/          arf.py, cite_check.py, prose_lint.py (+ shared arftext.py)
tests/                       python3 tests/test_arf.py
```

## Contributing

Phrase packs for more languages, CSL presets, discipline-specific genre notes and better heuristics are welcome. Keep scripts stdlib-only.

## License

MIT
