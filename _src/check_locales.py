#!/usr/bin/env python3
"""Every localized page set must exist in every site language, and its pages must link to each other.

For each set in build.page_sets(): one page per code in build.LOCALES, <html lang> matches, the hreflang
cluster and both language switchers (header and footer) list exactly that set's pages, and sitemap.xml lists
them. Any other published HTML/Markdown page must be in SINGLE_LANGUAGE, so a page added in one language fails.

Usage: python3 _src/check_locales.py   (pre-push hook: .githooks/pre-push; also run by the unit tests)
"""
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import BASE, LOCALES, SITE, page_sets  # noqa: E402

SINGLE_LANGUAGE = {"/press/", "/privacy/", "/support/", "/delete-account/", "/links/", "/get/", "/i/", "/404.html"}
DEFAULT_LOCALE = "en"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang, self.alternates, self.switchers, self._in = None, [], {"header": [], "footer": []}, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "link" and a.get("rel") == "alternate" and "hreflang" in a:
            self.alternates.append((a["hreflang"], a.get("href")))
        elif tag == "details" and "lang" in a.get("class", "").split():
            self._in.append(("header", tag))
        elif tag == "ul" and "langs" in a.get("class", "").split():
            self._in.append(("footer", tag))
        elif tag in ("details", "ul") and self._in:
            self._in.append((None, tag))
        elif tag == "a" and self._in and self._in[0][0] and "hreflang" in a:
            self.switchers[self._in[0][0]].append((a["hreflang"], a.get("href")))

    def handle_endtag(self, tag):
        if self._in and self._in[-1][1] == tag:
            self._in.pop()


def page_file(path):
    folder = SITE / path.strip("/")
    for name in ("index.html", "index.md"):
        if (folder / name).exists():
            return folder / name
    return None


def sitemap_locs(errors):
    try:
        root = ET.parse(SITE / "sitemap.xml").getroot()
    except (ET.ParseError, OSError) as e:
        errors.append(f"sitemap.xml: {e}")
        return set()
    return {loc.text for loc in root.iter(SITEMAP_NS + "loc")}


def check():
    errors = []
    codes = {code for code, *_ in LOCALES}
    sets = page_sets()
    locs = sitemap_locs(errors)
    for name, pages in sets.items():
        if set(pages) != codes:
            errors.append(f"{name}: locales {sorted(pages)} != site locales {sorted(codes)}")
        expected = sorted([(code, BASE + path) for code, path in pages.items()]
                          + [("x-default", BASE + pages.get(DEFAULT_LOCALE, ""))])
        switcher = sorted(pages.items())
        for code, path in pages.items():
            target = page_file(path)
            if not target:
                errors.append(f"{name}/{code}: {path} does not exist")
                continue
            links = PageLinks()
            links.feed(target.read_text(encoding="utf-8"))
            if links.lang != code:
                errors.append(f"{name}/{code}: <html lang> is {links.lang!r}")
            if sorted(links.alternates) != expected:
                errors.append(f"{name}/{code}: hreflang cluster differs from the {name} set")
            for where, found in links.switchers.items():
                if sorted(found) != switcher:
                    errors.append(f"{name}/{code}: {where} language switcher does not list exactly the {name} pages")
            if BASE + path not in locs:
                errors.append(f"{name}/{code}: {path} missing from sitemap.xml")
    stale = [p for p in SINGLE_LANGUAGE if not (page_file(p) or (SITE / p.strip("/")).is_file())]
    if stale:
        errors.append(f"SINGLE_LANGUAGE lists pages that do not exist: {sorted(stale)}")
    known = {path for pages in sets.values() for path in pages.values()} | SINGLE_LANGUAGE
    for page in sorted(SITE.rglob("*")):
        rel = page.relative_to(SITE)
        if page.suffix not in (".html", ".md") or rel.parts[0].startswith((".", "_")) or rel.parts[0] == "assets":
            continue
        path = "/" + "".join(part + "/" for part in rel.parts[:-1]) + ("" if page.stem == "index" else page.name)
        if path not in known:
            errors.append(f"{path}: page in no localized set; add it to build.page_sets() in every language "
                          "or to SINGLE_LANGUAGE")
    return errors


def main():
    errors = check()
    for error in errors:
        print(error, file=sys.stderr)
    print(f"{'FAILED' if errors else 'ok'}: {len(page_sets())} page sets x {len(LOCALES)} locales in {SITE}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
