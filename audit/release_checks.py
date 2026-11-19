"""Verify the release inventory, relative links, privacy and bilingual publications."""
from hashlib import file_digest
from html.parser import HTMLParser
from io import StringIO
import json
from pathlib import Path
import re
import tokenize
import unicodedata
from urllib.parse import unquote, urlsplit

import fitz
from markdown_it import MarkdownIt
from PIL import Image

from trade_audit.phase5_data import fact_values, load, localized_number


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release_manifest.json"
MD = MarkdownIt()
FORBIDDEN_DIRS = {".git", ".pytest_cache", "__pycache__", "raw", "dist", "build", "credentials"}
FORBIDDEN_SUFFIXES = {".zip", ".exe", ".dll", ".pem", ".key", ".p12", ".pfx", ".pyc", ".part", ".tmp"}
SENSITIVE = {
    "machine path": r"(?:/Users/|/private/tmp/|/home/[a-z][a-z0-9_-]+/|[A-Z]:[\\]Users[\\])",
    "credential or private key": (
        r"(?:BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY"
        r"|[g]h[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,}"
        r"|(?:AKIA|ASIA)[0-9A-Z]{16}|[s]k-(?:proj-)?[A-Za-z0-9_-]{24,}"
        r"|[x]ox[bpars]-[A-Za-z0-9-]{14,}|AIza[0-9A-Za-z_-]{35}"
        r"|[?&](?:X-Amz-Signature|AWSAccessKeyId)=[^&\s]+)"
    ),
    "credential assignment": (
        r"(?im)^\s*(?:password|api_?key|client_secret|access_?token)\s*=\s*"
        r"['\"][^'\"]{12,}"
    ),
    "email address": r"(?i)\b[A-Z0-9_.+%-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
}
README_FACTS = {
    "US24": ("US24", 1), "US25": ("US25", 1), "MONTH25": ("MONTH25", 1), "MONTH26": ("MONTH26", 1),
    "GOLD_CRUDE_PCT": ("GOLD_CRUDE_PCT", 1), "NON_US_CHANGE": ("NON_US_CHANGE", 3),
    "HHI24": ("HHI24", 5), "HHI25": ("HHI25", 5), "EX_GOLD24": ("EX_GOLD24", 5), "EX_GOLD25": ("EX_GOLD25", 5),
    "SCALED": ("SCALED", 6), "LOW": ("LOW", 5), "HIGH": ("HIGH", 5), "P": ("P", 4), "N": ("N", 0),
}
TITLES = {
    "en": "Canada Is Trading Less with the U.S. — But Is It Really Becoming Less Dependent?",
    "fr": "Le Canada commerce moins avec les États-Unis. Sa dépendance diminue-t-elle vraiment ?",
}


def digest(path):
    with path.open("rb") as source:
        return file_digest(source, "sha256").hexdigest()


def normalize(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text.replace("−", "-")))


class HTMLLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.anchors = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag in {"a", "link", "img"}:
            field = "src" if tag == "img" else "href"
            if attributes.get(field):
                self.links.append(attributes[field])
        if attributes.get("id"):
            self.anchors.add(attributes["id"])


def markdown_links(page):
    body = MD.parse(page.read_text())
    links = [child.attrGet("href") for token in body for child in token.children or []
             if child.type == "link_open"]
    anchors = {re.sub(r"[^\w-]", "", body[i + 1].content.lower().replace(" ", "-"))
               for i, token in enumerate(body) if token.type == "heading_open"}
    return links, anchors


def check_links(paths):
    references = {}
    for page in paths:
        if page.suffix == ".md":
            references[page] = markdown_links(page)
        elif page.suffix == ".html" and page.parent.name == "rendered":
            parser = HTMLLinks()
            parser.feed(page.read_text())
            references[page] = (parser.links, parser.anchors)
    count = 0
    for page, (links, _) in references.items():
        for link in links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page
            assert target.is_relative_to(ROOT) and target.exists(), (page.relative_to(ROOT), link)
            if parsed.fragment and target in references:
                assert unquote(parsed.fragment) in references[target][1], (page.relative_to(ROOT), link)
            count += 1
    return count


def scan(paths):
    findings = []
    for path in paths:
        relative = path.relative_to(ROOT)
        forbidden = (any(part in FORBIDDEN_DIRS or part.startswith(".venv") for part in relative.parts[:-1])
                     or path.name in {".DS_Store", ".netrc", "secrets.toml"}
                     or path.name.startswith(".env")
                     or path.suffix.lower() in FORBIDDEN_SUFFIXES)
        if path.is_symlink() or forbidden:
            findings.append((relative.as_posix(), "excluded file or symbolic link"))
            continue
        if path.suffix == ".pdf":
            with fitz.open(path) as pdf:
                payload = "\n".join([str(pdf.metadata), *(page.get_text() for page in pdf)])
        elif path.suffix == ".png":
            with Image.open(path) as img:
                payload = repr(img.info)
        else:
            payload = path.read_bytes().decode("utf-8", errors="ignore")
        text_for_email = payload
        if path.suffix == ".py":
            text_for_email = "\n".join(token.string for token in tokenize.generate_tokens(StringIO(payload).readline)
                                       if token.type in {tokenize.COMMENT, tokenize.STRING})
        for category, pattern in SENSITIVE.items():
            subject = text_for_email if category == "email address" else payload
            if re.search(pattern, subject) and relative.as_posix() != "audit/release_checks.py":
                findings.append((relative.as_posix(), category))
    assert not findings, findings


def verify_papers():
    keys = fact_values(load(ROOT))
    for lang, pages in (("en", 20), ("fr", 21)):
        pdf_path = ROOT / f"paper/rendered/canada_us_trade_{lang}.pdf"
        readme = normalize((ROOT / ("README.md" if lang == "en" else "README.fr.md")).read_text())
        with fitz.open(pdf_path) as pdf:
            assert len(pdf) == pages
            assert pdf.metadata["author"] == "Manau Salaun"
            assert normalize(pdf.metadata["title"]) == normalize(TITLES[lang])
            assert sum(len(p.get_images()) for p in pdf) == 11
            combined = normalize("\n".join(p.get_text() for p in pdf))
            assert all(normalize(localized_number(*v, lang)) in combined for v in keys.values())
            for name, (fact, decimals) in README_FACTS.items():
                expected = normalize(localized_number(keys[fact][0], decimals, lang))
                assert expected in readme, (lang, name, expected)
            assert all(page.get_text() and all(0 <= x0 <= x1 <= page.rect.width + 1 and
                       0 <= y0 <= y1 <= page.rect.height + 1 for x0, y0, x1, y1, *_ in page.get_text("words"))
                       for page in pdf)
    return len(keys)


def manifest_records(paths):
    return [{"path": p.relative_to(ROOT).as_posix(), "size_bytes": p.stat().st_size, "sha256": digest(p)}
            for p in paths if p != MANIFEST]


def main():
    paths = sorted(p for p in ROOT.rglob("*") if p.is_file() or p.is_symlink())
    scan(paths)
    facts = verify_papers()
    link_count = check_links(paths)
    if MANIFEST.exists():
        expected = json.loads(MANIFEST.read_text())["files"]
        observed = manifest_records(paths)
        assert observed == expected
        print(f"Verified path, size and SHA-256 for {len(expected)} payload files")
    print(f"Static hygiene scan passed for {len(paths)} files")
    print(f"Verified 41 PDF pages, 22 figure instances, {facts} locked values per language and both README summaries")
    print(f"Verified {link_count} relative Markdown and paper HTML links")


if __name__ == "__main__":
    main()
