import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "arf", "scripts")
sys.path.insert(0, SCRIPTS)

import arftext  # noqa: E402
import cite_check  # noqa: E402
import prose_lint  # noqa: E402

ARF = [sys.executable, os.path.join(SCRIPTS, "arf.py")]

BIB = """
@article{smith2021,
  author = {Smith, Jane},
  title = {A {Study} of Things},
  year = {2021},
  doi = {10.1000/xyz123},
  note = {verified: Crossref, 2026-10-23}
}
@book{ok2020, title = "Kitap", year = 2020, isbn = {978-0-00-000000-0}, note = {verified: publisher page, 2026-10-23}}
@misc{nolink, title = {Ghost}, note = {verified: memory}}
"""


def run(*args):
    return subprocess.run(ARF + list(args), capture_output=True, text=True)


class TestBib(unittest.TestCase):
    def test_parse(self):
        b = arftext.parse_bib(BIB)
        self.assertEqual(set(b), {"smith2021", "ok2020", "nolink"})
        self.assertEqual(b["smith2021"]["title"], "A {Study} of Things")
        self.assertEqual(b["ok2020"]["year"], "2020")

    def test_cite_keys(self):
        t = "As [@smith2021, p. 4; @ok2020] show, and @smith2021 argues. mail a@b.com"
        self.assertEqual(arftext.cite_keys(t), ["smith2021", "ok2020", "smith2021"])


class TestLint(unittest.TestCase):
    def test_tr_phrases_and_case(self):
        r = prose_lint.lint_text("GÜNÜMÜZDE bu konu önemli bir rol oynamaktadır.\n", "tr")
        hits = {f["detail"] for f in r["findings"] if f["kind"] == "phrase"}
        self.assertIn("günümüzde", hits)
        self.assertIn("önemli bir rol oynamaktadır", hits)

    def test_en_clean_text(self):
        text = ("Smith measured attrition in 412 rural schools between 2009 and 2014. "
                "Rates fell. The decline was steepest where bus routes were shortened, "
                "which suggests that travel time, not curriculum, drove the earlier losses.\n")
        r = prose_lint.lint_text(text, "en")
        self.assertEqual([f for f in r["findings"] if f["kind"] == "phrase"], [])
        self.assertEqual(r["stats"]["sentences"], 3)

    def test_monotone(self):
        para = " ".join(["This sentence has exactly eight words in it."] * 10)
        r = prose_lint.lint_text(para, "en")
        kinds = {f["kind"] for f in r["findings"]}
        self.assertIn("monotone_sentences", kinds)
        self.assertIn("repeated_sentence_opener", kinds)


class TestProject(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.p = os.path.join(self.tmp, "paper")
        r = run("init", self.p, "--title", "Deneme", "--level", "undergrad", "--lang", "tr", "--words", "30")
        self.assertEqual(r.returncode, 0, r.stderr)

    def write(self, rel, text):
        path = os.path.join(self.p, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def test_layout(self):
        for rel in ("arf.json", "00-brief.md", "sources/ledger.md", "references.bib", "voice/profile.md", "draft", "disclosure.md"):
            self.assertTrue(os.path.exists(os.path.join(self.p, rel)), rel)
        with open(os.path.join(self.p, "00-brief.md"), encoding="utf-8") as f:
            self.assertIn("Deneme", f.read())

    def test_gate_order(self):
        r = run("gate", self.p, "outline", "--approve")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(run("gate", self.p, "brief", "--approve").returncode, 0)
        self.assertIn("question", run("status", self.p).stdout)

    def test_citation_check(self):
        self.write("references.bib", BIB)
        self.write("draft/01-giris.md", "Bulgu [@smith2021] ve [@missing]. [[SOURCE?]]\n")
        res = cite_check.check(self.p)
        joined = "\n".join(res["errors"])
        self.assertIn("@missing", joined)
        self.assertIn("no identifier", joined)
        self.assertIn("[[SOURCE?]]", joined)
        self.assertNotIn("smith2021", joined)

    def test_draft_gate_blocked_by_citations(self):
        for ph in ("brief", "question", "sources", "outline", "voice"):
            self.assertEqual(run("gate", self.p, ph, "--approve").returncode, 0)
        self.write("draft/01-giris.md", "Bulgu [@missing].\n")
        r = run("gate", self.p, "draft", "--approve")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("citation check failed", r.stderr)

    def test_audit_and_build(self):
        self.write("references.bib", BIB.split("@misc")[0])
        body = ("Smith (2021) kırsal okullarda devamsızlığı beş yıl boyunca izledi [@smith2021]. "
                "Servis güzergâhları kısaldığında kayıplar azaldı; müfredat değişikliği ise belirgin bir fark yaratmadı. "
                "Bu sonuç, ulaşım süresinin asıl belirleyici olduğunu düşündürüyor [@ok2020].\n")
        self.write("draft/01-giris.md", body)
        r = run("audit", self.p)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("disclosure not filled", r.stdout)
        self.write("disclosure.md", "Yapay zekâ desteği beyan edilmiştir.\n")
        r = run("audit", self.p)
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertEqual(run("build", self.p).returncode, 0)
        with open(os.path.join(self.p, "paper.md"), encoding="utf-8") as f:
            paper = f.read()
        self.assertIn("bibliography: references.bib", paper)
        self.assertIn("Kaynakça", paper)


if __name__ == "__main__":
    unittest.main()
