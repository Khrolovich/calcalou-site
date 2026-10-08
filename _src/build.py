#!/usr/bin/env python3
"""Render the landing page for every locale: _src/template.html + _src/i18n/<code>.json -> /<path>/index.html.

Usage: python3 _src/build.py [--check]   (--check fails if a generated page is out of date)
"""
import datetime
import json
import sys
from pathlib import Path
from urllib.parse import quote

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

# code, path, default units
CALC_LOCALES = [
    ("en", "/bmr-calculator/", "imperial"),
    ("de", "/de/grundumsatz-rechner/", "metric"),
    ("pl", "/pl/kalkulator-zapotrzebowania-kalorycznego/", "metric"),
]
CALC_FACTORS = ["1.2", "1.375", "1.55", "1.725", "1.9"]
CALC_FAQ = ["bmr", "tdee", "formula", "accuracy", "activity"]


def store_links(ct):
    """Mirror of storeLinks() in /assets/landing.js, for pages that do not load it."""
    return {
        "ios": f"https://apps.apple.com/app/apple-store/id6757434158?pt=128407090&ct={quote(ct, safe='')}&mt=8",
        "android": "https://play.google.com/store/apps/details?id=com.khrolovich.calorietracker&referrer="
                   + quote(f"utm_source={ct}&utm_medium=social&utm_campaign=launch", safe=""),
    }


def load_calc_strings():
    folder = SRC / "i18n" / "calc"
    english = json.loads((folder / "en.json").read_text(encoding="utf-8"))
    result = {}
    for code, *_ in CALC_LOCALES:
        strings = json.loads((folder / f"{code}.json").read_text(encoding="utf-8"))
        if set(strings) != set(english) or not all(str(v).strip() for v in strings.values()):
            raise SystemExit(f"calc/{code}.json: keys differ from calc/en.json or a value is empty")
        result[code] = strings
    return result


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
    calc_strings = load_calc_strings()
    calc_paths = {code: path for code, path, _ in CALC_LOCALES}
    landing = {code: (path, name, og_locale, gp_code) for code, path, name, og_locale, gp_code, _ in LOCALES}
    locales = [{"code": c, "path": p, "name": n, "short": c.split("-")[0]} for c, p, n, *_ in LOCALES]
    calc_locales = [{"code": c, "path": p, "name": landing[c][1], "short": c} for c, p, _ in CALC_LOCALES]
    year = datetime.date.today().year
    pages = {}
    for code, path, name, og_locale, gp_code, sep in LOCALES:
        gp_w, gp_h = assets["googlePlay"][gp_code]
        calc = {"path": calc_paths[code], "label": calc_strings[code]["link.footer"]} if code in calc_paths else None
        html = template.render(
            lang=code, path=path, base=BASE, og_locale=og_locale, t=strings[code], locales=locales,
            current={"name": name, "short": code.split("-")[0]}, shots=assets["shots"],
            gp={"code": gp_code, "w": gp_w}, calc=calc,
            num=lambda n, s=sep: f"{n:,}".replace(",", s), year=year)
        pages[SITE / path.strip("/") / "index.html"] = html
    calc_template = env.get_template("calc.html")
    for code, path, units in CALC_LOCALES:
        home, name, og_locale, gp_code = landing[code]
        html = calc_template.render(
            lang=code, path=path, home=home, base=BASE, og_locale=og_locale, t=strings[code], c=calc_strings[code],
            locales=calc_locales, current={"name": name, "short": code}, units=units, factors=CALC_FACTORS,
            faq_keys=CALC_FAQ, links=store_links(f"calc-{code}"),
            gp={"code": gp_code, "w": assets["googlePlay"][gp_code][0]}, year=year)
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
