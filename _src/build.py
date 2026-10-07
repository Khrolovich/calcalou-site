#!/usr/bin/env python3
"""Render the landing page for every locale: _src/template.html + _src/i18n/<code>.json -> /<path>/index.html.

Usage: python3 _src/build.py [--check]   (--check fails if a generated page is out of date)
"""
import datetime
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

SRC = Path(__file__).resolve().parent
SITE = SRC.parent
BASE = "https://calcalou.com"

# code, path, native name, og:locale, Google Play badge code, thousands separator
LOCALES = [
    ("en", "/", "English", "en_US", "en", " "),
    ("de", "/de/", "Deutsch", "de_DE", "de", "."),
    ("es", "/es/", "Español", "es_ES", "es", ""),
    ("fr", "/fr/", "Français", "fr_FR", "fr", " "),
    ("it", "/it/", "Italiano", "it_IT", "it", "."),
    ("pl", "/pl/", "Polski", "pl_PL", "pl", " "),
    ("pt-BR", "/pt-br/", "Português (Brasil)", "pt_BR", "pt-br", "."),
    ("ru", "/ru/", "Русский", "ru_RU", "ru", " "),
    ("tr", "/tr/", "Türkçe", "tr_TR", "tr", "."),
]


def load_strings():
    english = json.loads((SRC / "i18n" / "en.json").read_text(encoding="utf-8"))
    result = {}
    for code, *_ in LOCALES:
        strings = json.loads((SRC / "i18n" / f"{code}.json").read_text(encoding="utf-8"))
        missing, extra = set(english) - set(strings), set(strings) - set(english)
        if missing or extra:
            raise SystemExit(f"{code}.json: missing {sorted(missing)} extra {sorted(extra)}")
        empty = [k for k, v in strings.items() if not str(v).strip()]
        if empty:
            raise SystemExit(f"{code}.json: empty values {empty}")
        result[code] = strings
    return result


def render_all():
    env = Environment(loader=FileSystemLoader(SRC), autoescape=True, undefined=StrictUndefined,
                      trim_blocks=False, lstrip_blocks=False)
    template = env.get_template("template.html")
    assets = json.loads((SRC / "assets.json").read_text(encoding="utf-8"))
    strings = load_strings()
    locales = [{"code": c, "path": p, "name": n, "short": c.split("-")[0]} for c, p, n, *_ in LOCALES]
    pages = {}
    for code, path, name, og_locale, gp_code, sep in LOCALES:
        gp_w, gp_h = assets["googlePlay"][gp_code]
        html = template.render(
            lang=code, path=path, base=BASE, og_locale=og_locale, t=strings[code], locales=locales,
            current={"name": name, "short": code.split("-")[0]}, shots=assets["shots"],
            gp={"code": gp_code, "w": gp_w},
            num=lambda n, s=sep: f"{n:,}".replace(",", s), year=datetime.date.today().year)
        pages[SITE / path.strip("/") / "index.html"] = html
    return pages


def main():
    pages = render_all()
    stale = []
    for target, html in pages.items():
        if "--check" in sys.argv:
            if not target.exists() or target.read_text(encoding="utf-8") != html:
                stale.append(str(target.relative_to(SITE)))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
    if stale:
        print("out of date: " + ", ".join(stale) + " (run python3 _src/build.py)", file=sys.stderr)
        return 1
    print(f"{'checked' if '--check' in sys.argv else 'built'} {len(pages)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
