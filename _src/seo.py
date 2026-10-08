#!/usr/bin/env python3
"""Write /sitemap.xml: every landing locale with its hreflang alternates, plus the other indexable pages.

Usage: python3 _src/seo.py [--check]   (--check fails if sitemap.xml is out of date)
Run after build.py whenever a locale or an indexable page is added.
"""
import subprocess
import sys
from datetime import date
from xml.sax.saxutils import quoteattr

from build import BASE, CALC_LOCALES, LOCALES, SITE

OTHER_PAGES = [("/press/", "press/index.html"), ("/privacy/", "privacy/index.md"),
               ("/support/", "support/index.md"), ("/delete-account/", "delete-account/index.html")]


def lastmod(rel_path):
    out = subprocess.run(["git", "-C", str(SITE), "log", "-1", "--format=%cs", "--", rel_path],
                         capture_output=True, text=True).stdout.strip()
    return out or date.today().isoformat()


def landing_rel(path):
    return (path.strip("/") + "/index.html").lstrip("/")


def cluster(pages):
    alternates = [(code, BASE + path) for code, path, *_ in pages] + [("x-default", BASE + pages[0][1])]
    links = "".join(f"\n    <xhtml:link rel=\"alternate\" hreflang={quoteattr(c)} href={quoteattr(u)}/>"
                    for c, u in alternates)
    return [f"  <url>\n    <loc>{BASE}{path}</loc>\n    <lastmod>{lastmod(landing_rel(path))}</lastmod>{links}\n  </url>"
            for _, path, *_ in pages]


def render():
    urls = cluster(LOCALES) + cluster(CALC_LOCALES)
    urls += [f"  <url>\n    <loc>{BASE}{path}</loc>\n    <lastmod>{lastmod(src)}</lastmod>\n  </url>"
             for path, src in OTHER_PAGES if (SITE / src).exists()]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "\n".join(urls) + "\n</urlset>\n")


def main():
    target = SITE / "sitemap.xml"
    xml = render()
    if "--check" in sys.argv:
        if not target.exists() or target.read_text(encoding="utf-8") != xml:
            print("sitemap.xml out of date (run python3 _src/seo.py)", file=sys.stderr)
            return 1
        print("checked sitemap.xml")
        return 0
    target.write_text(xml, encoding="utf-8")
    print(f"wrote sitemap.xml ({xml.count('<loc>')} urls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
