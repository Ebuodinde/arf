# Voice profile

The paper belongs to its author. Arf is open source and used by many people, so there is no default voice: each project builds its own profile from the author who will sign the paper.

## Inputs
Ask for 1–3 samples of the author's own writing (prior essays, reports, thesis chapters, even long emails on a technical topic). Store them in `voice/samples/`. More samples in the paper's language are better.

## Build `voice/profile.md`
Describe, with short quoted examples from the samples:
- Person and stance: I / we / impersonal; how directly they disagree.
- Sentence habits: typical length, use of subordinate clauses, questions, parentheses.
- Paragraph habits: topic-sentence first or build-up; typical length.
- Connectives they actually use (and ones they never use).
- Vocabulary: register, favourite precise terms, field jargon level, words to avoid.
- Citation integration: narrative ("Smith (2020) argues") vs parenthetical; quotation frequency.
- Characteristic moves: examples, analogies, numbers, historical framing.
- Known weaknesses the supervisor wants corrected (e.g. run-on sentences) — improve these rather than imitate them.

Run `python3 scripts/prose_lint.py voice/samples/<file> --lang <code> --json` to get baseline statistics (sentence length distribution, connective frequency) and record them in the profile as a reference point, not a quota.

## Use
- Before each section, re-read the profile.
- After each section, compare: does it read like the samples? Note mismatches in the checkpoint report.
- The supervisor may edit the profile at any time; treat edits as authoritative.

## The author must own it
Encourage the author to rewrite passages in their own words, add their own examples and judgments, and be able to explain and defend every claim orally. A paper the author cannot defend is a failed paper regardless of how it reads.
