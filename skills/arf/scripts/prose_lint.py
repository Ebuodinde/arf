#!/usr/bin/env python3
"""Prose quality reviewer for academic drafts.

Flags generic filler phrases (language packs in ../patterns/<lang>.txt),
monotony (uniform sentence/paragraph length, repeated openers), very long
sentences, stacked connectives, list-heavy argument, em-dash overuse, and
[[SOURCE?]] markers. It is a reviewer for the writer, not a score to game:
fix real problems, keep meaning intact.

Usage: prose_lint.py FILE [FILE...] --lang tr|en|<code> [--extra phrases.txt] [--json]
"""

import argparse
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arftext  # noqa: E402

PATTERN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "patterns")


def load_phrases(lang, extra=None):
    phrases = []
    paths = [os.path.join(PATTERN_DIR, lang + ".txt")]
    if extra:
        paths.append(extra)
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#"):
                    phrases.append(arftext.lower(s, lang))
    return phrases


def first_word(s, lang):
    w = arftext.words(s)
    return arftext.lower(w[0], lang) if w else ""


def cv(values):
    if len(values) < 2:
        return None
    m = statistics.mean(values)
    return statistics.pstdev(values) / m if m else None


def lint_text(text, lang="en", phrases=None, long_sentence=45):
    phrases = phrases if phrases is not None else load_phrases(lang)
    findings = []

    # Phrase hits with line numbers (on raw lines, skipping code blocks).
    in_code = False
    for ln, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        low = arftext.lower(line, lang)
        for ph in phrases:
            if ph in low:
                findings.append({"line": ln, "kind": "phrase", "detail": ph})
        if arftext.SOURCE_MARK in line:
            findings.append({"line": ln, "kind": "unsourced", "detail": "[[SOURCE?]]"})

    prose = arftext.strip_markdown(text)
    paras = arftext.paragraphs(prose)
    sent_lens, all_sents = [], []
    for p in paras:
        for s in arftext.sentences(p):
            n = len(arftext.words(s))
            if n:
                sent_lens.append(n)
                all_sents.append(s)
                if n > long_sentence:
                    findings.append({"line": None, "kind": "long_sentence", "detail": "%d words: %s…" % (n, s[:80])})

    para_lens = [len(arftext.words(p)) for p in paras]
    total_words = len(arftext.words(prose))

    # Repeated paragraph openers.
    openers = [first_word(p, lang) for p in paras]
    for i in range(1, len(openers)):
        if openers[i] and openers[i] == openers[i - 1]:
            findings.append({"line": None, "kind": "repeated_paragraph_opener", "detail": openers[i]})

    # Same sentence opener 3 times in a row.
    sopen = [first_word(s, lang) for s in all_sents]
    for i in range(2, len(sopen)):
        if sopen[i] and sopen[i] == sopen[i - 1] == sopen[i - 2]:
            findings.append({"line": None, "kind": "repeated_sentence_opener", "detail": sopen[i]})

    # Triads "a, b, and c" / "a, b ve c".
    conj = {"tr": r"(?:ve|ile|veya)", "en": r"(?:and|or)"}.get(lang, r"(?:and|or|ve)")
    triads = len(re.findall(r"\b[\w-]+, [\w-]+(?: [\w-]+)?,? " + conj + r" [\w-]+", prose, re.I))

    lines = [l for l in text.splitlines() if l.strip()]
    bullets = sum(1 for l in lines if re.match(r"^\s*([-*+]|\d+[.)])\s", l))
    dashes = prose.count("—") + prose.count(" – ")

    stats = {
        "words": total_words,
        "sentences": len(sent_lens),
        "paragraphs": len(paras),
        "sentence_len_mean": round(statistics.mean(sent_lens), 1) if sent_lens else 0,
        "sentence_len_cv": round(cv(sent_lens), 2) if cv(sent_lens) is not None else None,
        "paragraph_len_cv": round(cv(para_lens), 2) if cv(para_lens) is not None else None,
        "triads_per_1k": round(1000.0 * triads / total_words, 1) if total_words else 0,
        "dashes_per_1k": round(1000.0 * dashes / total_words, 1) if total_words else 0,
        "bullet_line_ratio": round(bullets / float(len(lines)), 2) if lines else 0,
        "phrase_hits": sum(1 for f in findings if f["kind"] == "phrase"),
    }

    # Advisory thresholds (heuristics, tuned for academic prose).
    if stats["sentence_len_cv"] is not None and len(sent_lens) >= 8 and stats["sentence_len_cv"] < 0.25:
        findings.append({"line": None, "kind": "monotone_sentences", "detail": "sentence lengths very uniform (cv=%.2f)" % stats["sentence_len_cv"]})
    if stats["paragraph_len_cv"] is not None and len(para_lens) >= 4 and stats["paragraph_len_cv"] < 0.15:
        findings.append({"line": None, "kind": "uniform_paragraphs", "detail": "paragraph lengths very uniform (cv=%.2f)" % stats["paragraph_len_cv"]})
    if stats["triads_per_1k"] > 6:
        findings.append({"line": None, "kind": "triads", "detail": "%.1f 'X, Y and Z' lists per 1k words" % stats["triads_per_1k"]})
    if stats["dashes_per_1k"] > 4:
        findings.append({"line": None, "kind": "dashes", "detail": "%.1f dashes per 1k words" % stats["dashes_per_1k"]})
    if stats["bullet_line_ratio"] > 0.2:
        findings.append({"line": None, "kind": "lists", "detail": "%.0f%% of lines are list items; argue in prose" % (100 * stats["bullet_line_ratio"])})

    return {"stats": stats, "findings": findings}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--extra", help="extra phrase file (one per line)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    phrases = load_phrases(a.lang, a.extra)
    results = {}
    for path in a.files:
        with open(path, encoding="utf-8") as f:
            results[path] = lint_text(f.read(), a.lang, phrases)
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    for path, r in results.items():
        s = r["stats"]
        print("== %s" % path)
        print("   words %(words)d · sentences %(sentences)d · paragraphs %(paragraphs)d · mean sent %(sentence_len_mean)s · sent cv %(sentence_len_cv)s · para cv %(paragraph_len_cv)s" % s)
        for f in r["findings"]:
            loc = ("L%d" % f["line"]) if f["line"] else "--"
            print("   %-5s %-26s %s" % (loc, f["kind"], f["detail"]))
        if not r["findings"]:
            print("   no findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
