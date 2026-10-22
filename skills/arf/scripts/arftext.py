"""Shared text and bibliography helpers for the arf scripts (stdlib only)."""

import re

CODE_BLOCK = re.compile(r"```.*?```", re.S)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
CITATION = re.compile(r"\[[^\[\]]*@[^\[\]]*\]")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
SOURCE_MARK = "[[SOURCE?]]"
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n", re.S)

# Pandoc citation keys: inside [...] or narrative @key preceded by start/space.
CITE_KEY = re.compile(r"(?:(?<=[\[\s;])|^)-?@([A-Za-z0-9_][A-Za-z0-9_:.#$%&+?<>~/-]*)", re.M)


def lower(text, lang="en"):
    if lang == "tr":
        text = text.replace("I", "ı").replace("İ", "i")
    return text.lower()


def strip_markdown(text):
    """Return prose-only text: no front matter, code, comments, citations, headings marks."""
    text = FRONT_MATTER.sub("", text)
    text = CODE_BLOCK.sub("", text)
    text = HTML_COMMENT.sub("", text)
    text = text.replace(SOURCE_MARK, "")
    text = CITATION.sub("", text)
    text = LINK.sub(r"\1", text)
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|"):  # tables
            continue
        s = re.sub(r"^#{1,6}\s+", "", s)
        s = re.sub(r"^>\s?", "", s)
        lines.append(s)
    text = "\n".join(lines)
    text = re.sub(r"[*_`]", "", text)
    return text


def paragraphs(text):
    """Split prose into paragraphs, excluding headings and list items."""
    out = []
    for block in re.split(r"\n\s*\n", text):
        b = block.strip()
        if not b:
            continue
        first = b.lstrip()
        if re.match(r"^(#{1,6}\s|[-*+]\s|\d+[.)]\s|\|)", first):
            continue
        out.append(" ".join(b.split()))
    return out


ABBREV = re.compile(
    r"\b(e\.g|i\.e|et al|vs|cf|pp|p|vol|no|ed|eds|Fig|Dr|Prof|Doç|Yrd|vb|vd|bkz|örn|s|yy)\.$",
    re.I,
)


def sentences(paragraph):
    parts = re.split(r"(?<=[.!?…])\s+(?=[\"'“‘(\[]?[A-ZÇĞİÖŞÜÂÎÛ0-9])", paragraph)
    merged = []
    for p in parts:
        if merged and ABBREV.search(merged[-1]):
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return [s.strip() for s in merged if s.strip()]


WORD = re.compile(r"[\w’'-]+", re.U)


def words(text):
    return WORD.findall(text)


def count_words(markdown_text):
    return len(words(strip_markdown(markdown_text)))


def parse_bib(text):
    """Minimal BibTeX parser -> {key: {"type": str, field: value}}."""
    entries = {}
    i = 0
    n = len(text)
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[at:])
        if not m:
            i = at + 1
            continue
        etype, key = m.group(1).lower(), m.group(2)
        j = at + m.end()
        depth = 1
        k = j
        while k < n and depth:
            if text[k] == "{":
                depth += 1
            elif text[k] == "}":
                depth -= 1
            k += 1
        body = text[j:k - 1]
        fields = {"type": etype}
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            name = fm.group(1).lower()
            p = fm.end()
            if p >= len(body):
                continue
            if body[p] == "{":
                d, q = 1, p + 1
                while q < len(body) and d:
                    if body[q] == "{":
                        d += 1
                    elif body[q] == "}":
                        d -= 1
                    q += 1
                val = body[p + 1:q - 1]
            elif body[p] == '"':
                q = body.find('"', p + 1)
                val = body[p + 1:q]
            else:
                val = re.match(r"[^,\n]*", body[p:]).group(0)
            fields.setdefault(name, " ".join(val.split()))
        if etype not in ("comment", "preamble", "string"):
            entries[key] = fields
        i = k
    return entries


def cite_keys(markdown_text):
    text = CODE_BLOCK.sub("", markdown_text)
    text = HTML_COMMENT.sub("", text)
    keys = []
    for m in CITE_KEY.finditer(text):
        key = m.group(1).rstrip(".:;,")
        keys.append(key)
    return keys
