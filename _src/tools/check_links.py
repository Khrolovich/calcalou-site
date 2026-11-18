#!/usr/bin/env python3
"""Offline link check for the built site: every internal href/src resolves to a file, every #fragment to an id.

Usage: python3 _src/tools/check_links.py [--external]   (--external also prints the distinct external URLs and
their HTTP status with curl; needs network)
"""
import re
import subprocess
import sys
from html import unescape
from pathlib import Path
from urllib.parse import urlparse

SITE = Path(__file__).resolve().parents[2]
ATTR = re.compile(r'(?:href|src)="([^"]+)"')
IDS = re.compile(r'\sid="([^"]+)"')
pages = [p for p in SITE.rglob("*.html") if not {"_src", ".git", "node_modules"} & set(p.parts)]
errors, external = [], set()
for page in pages:
    html = page.read_text(encoding="utf-8")
    for raw in ATTR.findall(html):
        if "'" in raw or "{" in raw:  # URL fragments inside inline scripts
            continue
        url = urlparse(unescape(raw))
        if url.scheme in ("mailto", "tel", "data", "javascript", "itms-apps", "intent"):
            continue
        if url.netloc and url.netloc not in ("calcalou.com", "www.calcalou.com"):
            external.add(unescape(raw))
            continue
        path = url.path or "/" + str(page.parent.relative_to(SITE)).strip(".") + "/"
        target = SITE / path.lstrip("/")
        if target.is_dir():
            target = target / "index.html" if (target / "index.html").exists() else target / "index.md"  # Jekyll pages
        if not target.exists() and not target.with_suffix(".html").exists():
            errors.append(f"{page.relative_to(SITE)}: {raw} -> missing")
            continue
        if url.fragment and target.suffix == ".html" and url.fragment not in IDS.findall(target.read_text(encoding="utf-8")):
            errors.append(f"{page.relative_to(SITE)}: {raw} -> no #{url.fragment}")
print(f"checked {len(pages)} pages, {len(errors)} broken internal links, {len(external)} external urls")
print("\n".join(errors[:50]))
if "--external" in sys.argv:
    for url in sorted(external):
        code = subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "-m", "20", "-A", "Mozilla/5.0", "-w", "%{http_code}", url],
                              capture_output=True, text=True).stdout
        print(code, url)
sys.exit(1 if errors else 0)
