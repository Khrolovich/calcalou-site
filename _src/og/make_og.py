#!/usr/bin/env python3
"""Render the share images (/assets/img/og.jpg for en, og-<code>.jpg for the other home locales) from _src/og/og.html
with headless Chrome. Fails when a headline does not fit the centre column or the font did not load.

Usage: python3 _src/og/make_og.py [code ...]   (needs jinja2, macOS sips, Google Chrome and the Calcalou design folder)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import HOME_LOCALES, SITE, SRC, og_image  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DESIGN = SITE.parents[1] / "design"
FONTS = DESIGN / "store-1.7" / "assets" / "fonts"
LOU = DESIGN / "mascot" / "reference" / "3d-png" / "mascot_happy.png"
SIZE = (1200, 630)


def chrome(html, *args):
    return subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                           "--allow-file-access-from-files", f"--window-size={SIZE[0]},{SIZE[1]}",
                           "--virtual-time-budget=6000", *args, html.as_uri()],
                          capture_output=True, text=True, check=True).stdout


def main(codes):
    template = Environment(loader=FileSystemLoader(SRC / "og"), autoescape=True,
                           undefined=StrictUndefined).get_template("og.html")
    failed = []
    with tempfile.TemporaryDirectory() as tmp:
        for code, _, _, _, _, sep in HOME_LOCALES:
            if codes and code not in codes:
                continue
            h = json.loads((SRC / "i18n" / "home2" / f"{code}.json").read_text(encoding="utf-8"))
            page = Path(tmp) / f"{code}.html"
            page.write_text(template.render(lang=code, h=h, num=lambda n, s=sep: f"{n:,}".replace(",", s),
                                            fonts=FONTS.as_uri(), lou=LOU.as_uri(), site=SITE.as_uri()),
                            encoding="utf-8")
            root = re.search(r"<html[^>]*>", chrome(page, "--dump-dom")).group(0)
            if 'data-fit="ok"' not in root or 'data-font="ok"' not in root:
                failed.append(f"{code}: {root}")
                continue
            png = Path(tmp) / f"{code}.png"
            chrome(page, f"--screenshot={png}")
            dims = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", png], capture_output=True, text=True).stdout
            if tuple(int(x) for x in re.findall(r"pixel\w+: (\d+)", dims)) != SIZE:
                failed.append(f"{code}: screenshot is not {SIZE}: {dims}")
                continue
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "88", png,
                            "--out", SITE / og_image(code).lstrip("/")], capture_output=True, check=True)
            print(code, re.search(r'data-size="(\d+)"', root).group(1) + "px", og_image(code))
    if failed:
        sys.exit("og images failed:\n" + "\n".join(failed))


if __name__ == "__main__":
    main(sys.argv[1:])
