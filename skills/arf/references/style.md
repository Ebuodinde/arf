# Style discipline

Generic machine-flavoured prose is bad academic prose: vague, padded, evenly hedged, symmetric, and empty of specifics. Examiners penalize it whoever wrote it. This checklist targets those weaknesses. `scripts/prose_lint.py` flags many of them automatically; the rest need judgment.

## 1. Content before form
- Each paragraph makes one point that advances the outline. If you cannot state its point in one clause, rewrite it.
- Replace abstractions with the concrete thing: which study, which year, what number, what mechanism, which author disagrees and on what.
- Prefer one precise claim with a citation over three vague ones.
- Cut sentences that only announce ("This section will discuss…") unless the genre requires a roadmap (then do it once, in the introduction).

## 2. Patterns to remove
English:
- Filler openers/closers: "In today's world", "It is important to note that", "In conclusion, it can be said", "plays a crucial/pivotal role", "a testament to", "navigate the complexities", "delve into", "shed light on", "in the realm of", "rich tapestry", "multifaceted", "ever-evolving landscape".
- Reflexive triads (X, Y, and Z) in every other sentence.
- Stacked hedges ("may potentially suggest"); blanket "various/numerous/several studies" without citations.
- Paragraphs that end by restating themselves ("Overall, this shows that…").
- Em-dash and colon overuse as a rhythm device; bolded mini-headings inside prose; bullet lists where argument is needed.
Turkish:
- "Günümüzde", "Son yıllarda büyük önem kazanmıştır", "önemli bir rol oynamaktadır", "büyük önem arz etmektedir", "Bu bağlamda" / "Bu doğrultuda" every paragraph, "Sonuç olarak söylenebilir ki", "göz ardı edilmemelidir", "çok boyutlu bir yapıya sahiptir", "ele alınacaktır" chains.
- Every sentence ending in "-mektedir/-maktadır" in long nominal chains; break with verbal predicates and active constructions where the field allows.
- Mechanical "Birincisi… İkincisi… Üçüncüsü…" where the argument is not actually enumerative.
Other languages: build an equivalent list in `voice/profile.md` and pass it to the linter with `--extra`.

## 3. Rhythm follows meaning
- Sentence length varies because ideas vary: short for a claim or turn, longer for qualification or synthesis. Do not engineer variation; let the content drive it.
- Paragraphs differ in length. A one-sentence paragraph is allowed when it carries a pivot.
- Vary how paragraphs open; avoid starting consecutive paragraphs with the same connective.

## 4. Stance
- Use the discipline's conventions for "I/we", passive, and evaluative language.
- Take a position when evidence supports it; name the opposing view and its best version.
- Hedge proportionally and specifically ("in the two samples studied", "for pre-2010 data") rather than with generic modal verbs.

## 5. Terminology
- Define key terms once; use them consistently (do not cycle synonyms for a technical term).
- Keep an author-specific glossary in `voice/profile.md`.

## 6. Final read
- Would a specialist learn something from each paragraph?
- Is every number, name, and quote traceable to the ledger?
- Does the conclusion claim no more than the body shows?
