#!/usr/bin/env python3
"""Citation integrity check for an arf project.

Offline (default):
  - every [@key] in draft/*.md exists in references.bib
  - every bib entry has an identifier (doi/isbn/url/pmid/eprint)
  - every bib entry carries a 'verified' note
  - reports unused entries and [[SOURCE?]] markers
Online (--online): resolves DOIs via Crossref and compares title/year.

Exit 1 if any error.
"""

import argparse
import difflib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arftext  # noqa: E402

ID_FIELDS = ("doi", "isbn", "url", "pmid", "eprint", "issn")


def draft_files(project):
    d = os.path.join(project, "draft")
    if not os.path.isdir(d):
        return []
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".md"))


def norm(s):
    return re.sub(r"[^\w]+", " ", arftext.lower(s or "")).strip()


def crossref(doi, timeout=15):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi.strip(), safe="/")
    req = urllib.request.Request(url, headers={"User-Agent": "arf-cite-check/1.0 (mailto:arf@example.org)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)["message"]


def check(project, online=False):
    errors, warnings = [], []
    bib_path = os.path.join(project, "references.bib")
    bib = {}
    if os.path.exists(bib_path):
        with open(bib_path, encoding="utf-8") as f:
            bib = arftext.parse_bib(f.read())
    else:
        errors.append("references.bib missing")

    used = {}
    markers = []
    for path in draft_files(project):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        rel = os.path.relpath(path, project)
        for key in arftext.cite_keys(text):
            used.setdefault(key, set()).add(rel)
        for ln, line in enumerate(text.splitlines(), 1):
            if arftext.SOURCE_MARK in line:
                markers.append("%s:%d" % (rel, ln))

    for key, files in sorted(used.items()):
        if key not in bib:
            errors.append("cited but not in references.bib: @%s (%s)" % (key, ", ".join(sorted(files))))
    for key, e in sorted(bib.items()):
        if not any(e.get(fld) for fld in ID_FIELDS):
            errors.append("no identifier (doi/isbn/url/pmid/eprint): %s" % key)
        note = " ".join(e.get(fld, "") for fld in ("note", "verified", "annote"))
        if "verified" not in note.lower():
            errors.append("not marked verified: %s" % key)
        if key not in used:
            warnings.append("in bib but not cited: %s" % key)
    for m in markers:
        errors.append("unsourced claim marker [[SOURCE?]] at %s" % m)

    if online:
        for key, e in sorted(bib.items()):
            doi = e.get("doi")
            if not doi:
                continue
            doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip(), flags=re.I)
            try:
                msg = crossref(doi)
            except urllib.error.HTTPError as ex:
                errors.append("DOI does not resolve (%s): %s doi:%s" % (ex.code, key, doi))
                continue
            except Exception as ex:  # network unavailable etc.
                warnings.append("could not reach Crossref for %s: %s" % (key, ex))
                continue
            titles = msg.get("title") or [""]
            ratio = difflib.SequenceMatcher(None, norm(titles[0]), norm(e.get("title", ""))).ratio()
            if ratio < 0.8:
                errors.append("title mismatch for %s (%.2f): bib=%r crossref=%r" % (key, ratio, e.get("title"), titles[0]))
            parts = (msg.get("issued") or {}).get("date-parts") or [[None]]
            cyear = parts[0][0]
            byear = re.sub(r"\D", "", e.get("year", "") or e.get("date", "")[:4])
            if cyear and byear and str(cyear) != byear:
                warnings.append("year differs for %s: bib=%s crossref=%s" % (key, byear, cyear))

    return {"errors": errors, "warnings": warnings, "cited": len(used), "entries": len(bib), "markers": len(markers)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--online", action="store_true", help="resolve DOIs via Crossref")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = check(a.project, a.online)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("entries: %d  cited keys: %d  [[SOURCE?]]: %d" % (res["entries"], res["cited"], res["markers"]))
        for e in res["errors"]:
            print("ERROR  " + e)
        for w in res["warnings"]:
            print("warn   " + w)
        print("OK" if not res["errors"] else "FAIL (%d errors)" % len(res["errors"]))
    return 1 if res["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
