#!/usr/bin/env python3
"""arf project manager: init, status, gate, log, audit, build.

  arf.py init DIR --title T --level undergrad|masters|doctoral --lang CODE [--words N]
  arf.py status DIR
  arf.py gate DIR PHASE (--approve | --reopen) [--note TEXT]
  arf.py log DIR PHASE --feedback TEXT [--change TEXT]
  arf.py audit DIR [--online]
  arf.py build DIR [--docx] [--pdf] [--csl FILE]
"""

import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import arftext  # noqa: E402
import cite_check  # noqa: E402
import prose_lint  # noqa: E402

SKILL = os.path.dirname(HERE)
TEMPLATES = os.path.join(SKILL, "templates")
PHASES = ["brief", "question", "sources", "outline", "voice", "draft", "revise", "audit"]
LEVELS = {"undergrad": 5000, "masters": 8000, "doctoral": 9000}
STATE = "arf.json"
# Artifacts that must be filled in before a phase's gate can be approved.
ARTIFACTS = {
    "brief": ("00-brief.md",),
    "question": ("01-question.md",),
    "sources": ("sources/ledger.md", "references.bib"),
    "outline": ("02-outline.md",),
    "voice": ("voice/profile.md",),
}
PLACEHOLDER = re.compile(r"<[^<>\n]+>")


def today():
    return datetime.date.today().isoformat()


def load(project):
    p = os.path.join(project, STATE)
    if not os.path.exists(p):
        sys.exit("no %s in %s — run: arf.py init %s ..." % (STATE, project, project))
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(project, state):
    with open(os.path.join(project, STATE), "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def current_phase(state):
    for ph in PHASES:
        if state["gates"].get(ph, {}).get("status") != "approved":
            return ph
    return "done"


def log(project, phase, feedback, change):
    path = os.path.join(project, "revisions", "log.md")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    clean = lambda s: (s or "").replace("|", "\\|").replace("\n", " ")
    with open(path, "a", encoding="utf-8") as f:
        f.write("| %s | %s | %s | %s |\n" % (today(), phase, clean(feedback), clean(change)))


def draft_words(project):
    total = 0
    for p in cite_check.draft_files(project):
        with open(p, encoding="utf-8") as f:
            total += arftext.count_words(f.read())
    return total


def template_subs(title, level, lang, words):
    return {"{title}": title, "{level}": level, "{lang}": lang, "{words}": str(words)}


def unfilled(project, st, phase):
    """Objective reasons a phase artifact is not ready: missing, untouched, or placeholders left."""
    problems = []
    subs = template_subs(st["title"], st["level"], st["lang"], st["target_words"])
    for rel in ARTIFACTS.get(phase, ()):
        path = os.path.join(project, rel)
        if not os.path.exists(path):
            problems.append("%s missing" % rel)
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        tpath = os.path.join(TEMPLATES, rel)
        if not os.path.exists(tpath):
            continue
        with open(tpath, encoding="utf-8") as f:
            tmpl = f.read()
        for k, v in subs.items():
            tmpl = tmpl.replace(k, v)
        if text.strip() == tmpl.strip():
            problems.append("%s is still the empty template" % rel)
        elif rel.endswith(".md"):
            left = sorted(t for t in set(PLACEHOLDER.findall(tmpl)) if t in text)
            if left:
                problems.append("%s still has template placeholders: %s" % (rel, ", ".join(left)))
    return problems


def cmd_init(a):
    project = a.dir
    if os.path.exists(os.path.join(project, STATE)):
        sys.exit("already an arf project: %s" % project)
    words = a.words or LEVELS[a.level]
    subs = template_subs(a.title, a.level, a.lang, words)
    for root, _dirs, files in os.walk(TEMPLATES):
        rel = os.path.relpath(root, TEMPLATES)
        dest_dir = os.path.normpath(os.path.join(project, rel))
        os.makedirs(dest_dir, exist_ok=True)
        for name in files:
            if name.startswith("."):
                continue
            with open(os.path.join(root, name), encoding="utf-8") as f:
                text = f.read()
            for k, v in subs.items():
                text = text.replace(k, v)
            dest = os.path.join(dest_dir, name)
            if not os.path.exists(dest):
                with open(dest, "w", encoding="utf-8") as f:
                    f.write(text)
    for d in ("draft", "sources/notes", "voice/samples"):
        os.makedirs(os.path.join(project, d), exist_ok=True)
    state = {
        "title": a.title,
        "level": a.level,
        "lang": a.lang,
        "target_words": words,
        "created": today(),
        "gates": {ph: {"status": "open"} for ph in PHASES},
    }
    save(project, state)
    print("arf project created: %s" % os.path.abspath(project))
    print("next: fill 00-brief.md, then ask the supervisor to approve the 'brief' gate")
    return 0


def cmd_status(a):
    st = load(a.dir)
    cur = current_phase(st)
    print("%s  [%s · %s · target %d words]" % (st["title"], st["level"], st["lang"], st["target_words"]))
    for ph in PHASES:
        g = st["gates"].get(ph, {})
        mark = {"approved": "x", "open": " "}.get(g.get("status"), "?")
        arrow = "  <- current" if ph == cur else ""
        date = (" " + g["date"]) if g.get("date") else ""
        print("  [%s] %-9s%s%s" % (mark, ph, date, arrow))
    cc = cite_check.check(a.dir)
    print("draft words: %d / %d" % (draft_words(a.dir), st["target_words"]))
    print("bib entries: %d · cited keys: %d · [[SOURCE?]]: %d · citation errors: %d"
          % (cc["entries"], cc["cited"], cc["markers"], len(cc["errors"])))
    return 0


def cmd_gate(a):
    st = load(a.dir)
    if a.phase not in PHASES:
        sys.exit("unknown phase %r; phases: %s" % (a.phase, ", ".join(PHASES)))
    idx = PHASES.index(a.phase)
    if a.approve:
        missing = [p for p in PHASES[:idx] if st["gates"][p].get("status") != "approved"]
        if missing:
            sys.exit("cannot approve %s: earlier gates open: %s" % (a.phase, ", ".join(missing)))
        problems = unfilled(a.dir, st, a.phase)
        if problems:
            for p in problems:
                print("ERROR  " + p)
            sys.exit("cannot approve %s: artifact not filled in (write 'unknown' / 'n/a' where that is the honest answer)" % a.phase)
        if a.phase == "draft":
            cc = cite_check.check(a.dir)
            if cc["errors"]:
                for e in cc["errors"]:
                    print("ERROR  " + e)
                sys.exit("cannot approve %s: citation check failed" % a.phase)
        if a.phase == "audit":
            lines, blocking = run_audit(a.dir, st)
            if blocking:
                print("\n".join(lines))
                sys.exit("cannot approve audit: " + "; ".join(blocking))
        st["gates"][a.phase] = {"status": "approved", "date": today()}
        log(a.dir, a.phase, a.note or "approved", "gate approved")
        print("approved: %s · next: %s" % (a.phase, current_phase(st)))
    else:
        for p in PHASES[idx:]:
            st["gates"][p] = {"status": "open"}
        log(a.dir, a.phase, a.note or "reopened", "gate reopened with all later gates")
        print("reopened: %s (and later gates)" % a.phase)
    save(a.dir, st)
    return 0


def cmd_log(a):
    st = load(a.dir)
    if a.phase not in PHASES:
        sys.exit("unknown phase %r; phases: %s" % (a.phase, ", ".join(PHASES)))
    log(a.dir, a.phase, a.feedback, a.change or "")
    print("logged: %s · current phase: %s" % (a.phase, current_phase(st)))
    return 0


def run_audit(project, st, online=False):
    """Return (report lines, blocking reasons)."""
    lines = ["# Audit", "", "Date: %s" % today(), ""]
    blocking = []

    cc = cite_check.check(project, online=online)
    lines += ["## Citations%s" % (" (online)" if online else " (offline)"), "",
              "entries %d · cited %d · markers %d" % (cc["entries"], cc["cited"], cc["markers"]), ""]
    lines += ["- ERROR " + e for e in cc["errors"]] + ["- warn " + w for w in cc["warnings"]] + [""]
    if cc["errors"]:
        blocking.append("citation errors: %d" % len(cc["errors"]))

    lines += ["## Prose review (advisory)", ""]
    phrases = prose_lint.load_phrases(st["lang"])
    for p in cite_check.draft_files(project):
        with open(p, encoding="utf-8") as f:
            r = prose_lint.lint_text(f.read(), st["lang"], phrases)
        kinds = {}
        for fd in r["findings"]:
            kinds[fd["kind"]] = kinds.get(fd["kind"], 0) + 1
        summary = ", ".join("%s %d" % kv for kv in sorted(kinds.items())) or "no findings"
        lines.append("- %s: %d words; %s" % (os.path.relpath(p, project), r["stats"]["words"], summary))
    lines.append("")

    words = draft_words(project)
    lo, hi = int(st["target_words"] * 0.9), int(st["target_words"] * 1.1)
    ok = lo <= words <= hi
    lines += ["## Length", "", "%d words (target %d, accepted %d–%d): %s" % (words, st["target_words"], lo, hi, "ok" if ok else "OUT OF RANGE"), ""]
    if not ok:
        blocking.append("length out of range")

    disc = os.path.join(project, "disclosure.md")
    filled = False
    if os.path.exists(disc):
        with open(disc, encoding="utf-8") as f:
            filled = "TODO" not in f.read()
    lines += ["## Disclosure", "", "filled" if filled else "MISSING (disclosure.md still has TODO)", ""]
    if not filled:
        blocking.append("disclosure not filled")

    lines += ["## Result", "", "PASS" if not blocking else "BLOCKED: " + "; ".join(blocking), ""]
    return lines, blocking


def cmd_audit(a):
    st = load(a.dir)
    lines, blocking = run_audit(a.dir, st, online=a.online)
    with open(os.path.join(a.dir, "audit.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))
    return 1 if blocking else 0


def cmd_build(a):
    st = load(a.dir)
    parts = ["---", "title: \"%s\"" % st["title"].replace('"', '\\"'), "lang: %s" % st["lang"],
             "bibliography: references.bib", "link-citations: true", "---", ""]
    for p in cite_check.draft_files(a.dir):
        with open(p, encoding="utf-8") as f:
            parts.append(f.read().strip())
            parts.append("")
    parts += ["# References" if st["lang"] != "tr" else "# Kaynakça", "", "::: {#refs}", ":::", ""]
    out = os.path.join(a.dir, "paper.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print("wrote %s" % out)
    for fmt in [f for f in ("docx", "pdf") if getattr(a, f)]:
        if not shutil.which("pandoc"):
            print("pandoc not installed; install it to export DOCX/PDF")
            return 1
        cmd = ["pandoc", "paper.md", "--citeproc", "-o", "paper." + fmt]
        if a.csl:
            # pandoc runs inside the project dir; resolve the CSL from the caller's cwd first.
            csl = a.csl if os.path.isabs(a.csl) or not os.path.exists(a.csl) else os.path.abspath(a.csl)
            cmd += ["--csl", csl]
        subprocess.check_call(cmd, cwd=a.dir)
        print("wrote %s" % os.path.join(a.dir, "paper." + fmt))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("init")
    s.add_argument("dir")
    s.add_argument("--title", required=True)
    s.add_argument("--level", required=True, choices=sorted(LEVELS))
    s.add_argument("--lang", required=True, help="ISO code of the paper's language, e.g. tr, en, de")
    s.add_argument("--words", type=int)
    s = sub.add_parser("status")
    s.add_argument("dir")
    s = sub.add_parser("gate")
    s.add_argument("dir")
    s.add_argument("phase")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--approve", action="store_true")
    g.add_argument("--reopen", action="store_true")
    s.add_argument("--note")
    s = sub.add_parser("log", help="record supervisor feedback in revisions/log.md")
    s.add_argument("dir")
    s.add_argument("phase")
    s.add_argument("--feedback", required=True, help="supervisor feedback, verbatim")
    s.add_argument("--change", help="what was changed in response")
    s = sub.add_parser("audit")
    s.add_argument("dir")
    s.add_argument("--online", action="store_true")
    s = sub.add_parser("build")
    s.add_argument("dir")
    s.add_argument("--docx", action="store_true")
    s.add_argument("--pdf", action="store_true", help="needs pandoc plus a LaTeX engine")
    s.add_argument("--csl")
    a = ap.parse_args(argv)
    if not a.cmd:
        ap.print_help()
        return 2
    cmds = {"init": cmd_init, "status": cmd_status, "gate": cmd_gate, "log": cmd_log,
            "audit": cmd_audit, "build": cmd_build}
    return cmds[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
