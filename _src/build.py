#!/usr/bin/env python3
"""Render every page set in every site locale: the landing (_src/template.html + i18n/<code>.json) and the
BMR calculator (_src/calc.html + i18n/calc/<code>.json). _src/check_locales.py enforces that each set covers LOCALES.

Usage: python3 _src/build.py [--check]   (--check fails if a generated page is out of date)
"""
import datetime
import json
import sys
from pathlib import Path
from urllib.parse import quote


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
    ("es", "/es/calculadora-de-calorias/", "metric"),
    ("fr", "/fr/calcul-metabolisme-de-base/", "metric"),
    ("it", "/it/calcolo-metabolismo-basale/", "metric"),
    ("pl", "/pl/kalkulator-zapotrzebowania-kalorycznego/", "metric"),
    ("pt-BR", "/pt-br/calculadora-tmb/", "metric"),
    ("ru", "/ru/kalkulyator-kaloriy/", "metric"),
    ("tr", "/tr/bazal-metabolizma-hesaplama/", "metric"),
]
CALC_FACTORS = ["1.2", "1.375", "1.55", "1.725", "1.9"]
TDEE_PATHS = {
    "en": "/tdee-calculator/", "de": "/de/tdee-rechner/", "es": "/es/calculadora-tdee/", "fr": "/fr/calcul-tdee/",
    "it": "/it/calcolo-tdee/", "pl": "/pl/kalkulator-tdee/", "pt-BR": "/pt-br/calculadora-tdee/",
    "ru": "/ru/kalkulyator-tdee/", "tr": "/tr/tdee-hesaplama/",
}
DEFICIT_PATHS = {
    "en": "/calorie-deficit-calculator/", "de": "/de/kaloriendefizit-rechner/",
    "es": "/es/calculadora-deficit-calorico/", "fr": "/fr/calcul-deficit-calorique/",
    "it": "/it/calcolo-deficit-calorico/", "pl": "/pl/kalkulator-deficytu-kalorycznego/",
    "pt-BR": "/pt-br/calculadora-deficit-calorico/", "ru": "/ru/kalkulyator-deficita-kaloriy/",
    "tr": "/tr/kalori-acigi-hesaplama/",
}
DEFICITS = [250, 500, 750, 1000]
# Thousands separator as Intl.NumberFormat(lang) prints it in calc.js (es and pl do not group 4-digit numbers).
CALC_SEP = {"en": ",", "de": ".", "es": "", "fr": "\u202f", "it": ".", "pl": "", "pt-BR": ".", "ru": "\u00a0", "tr": "."}
# page set: (mode, i18n folder for strings over i18n/calc, store ct prefix, FAQ keys, {code: path})
CALC_PAGES = {
    "calculator": ("bmr", None, "calc", ["bmr", "tdee", "formula", "accuracy", "activity"], None),
    "tdee": ("tdee", "tdee", "calc-tdee", ["tdee", "difference", "activity", "use", "accuracy"], TDEE_PATHS),
    "deficit": ("deficit", "deficit", "calc-deficit", ["deficit", "maintenance", "size", "floor", "accuracy"],
                DEFICIT_PATHS),
}


def page_sets():
    """Every localized page set: name -> {locale code: path}."""
    sets = {"landing": {code: path for code, path, *_ in LOCALES}}
    for name, (_, _, _, _, paths) in CALC_PAGES.items():
        sets[name] = paths or {code: path for code, path, _ in CALC_LOCALES}
    return sets


def store_links(ct):
    """Mirror of storeLinks() in /assets/landing.js, for pages that do not load it."""
    return {
        "ios": f"https://apps.apple.com/app/apple-store/id6757434158?pt=128407090&ct={quote(ct, safe='')}&mt=8",
        "android": "https://play.google.com/store/apps/details?id=com.khrolovich.calorietracker&referrer="
                   + quote(f"utm_source={ct}&utm_medium=social&utm_campaign=launch", safe=""),
    }


def load_calc_strings(name="calc"):
    folder = SRC / "i18n" / name
    english = json.loads((folder / "en.json").read_text(encoding="utf-8"))
    result = {}
    for code, *_ in CALC_LOCALES:
        strings = json.loads((folder / f"{code}.json").read_text(encoding="utf-8"))
        if set(strings) != set(english) or not all(str(v).strip() for v in strings.values()):
            raise SystemExit(f"{name}/{code}.json: keys differ from {name}/en.json or a value is empty")
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
    # Imported here so check_locales.py (pre-push hook) runs on a bare python3 without jinja2.
    from jinja2 import Environment, FileSystemLoader, StrictUndefined

    env = Environment(loader=FileSystemLoader(SRC), autoescape=True, undefined=StrictUndefined,
                      trim_blocks=False, lstrip_blocks=False)
    template = env.get_template("template.html")
    assets = json.loads((SRC / "assets.json").read_text(encoding="utf-8"))
    strings = load_strings()
    calc_strings = load_calc_strings()
    sets = page_sets()
    page_strings = {name: {code: {**calc_strings[code], **extra[code]} for code in calc_strings}
                    for name, extra in ((name, load_calc_strings(folder) if folder else {c: {} for c in calc_strings})
                                        for name, (_, folder, *_rest) in CALC_PAGES.items())}
    landing = {code: (path, name, og_locale, gp_code) for code, path, name, og_locale, gp_code, _ in LOCALES}
    locales = [{"code": c, "path": p, "name": n, "short": c.split("-")[0]} for c, p, n, *_ in LOCALES]
    year = datetime.date.today().year
    pages = {}
    for code, path, name, og_locale, gp_code, sep in LOCALES:
        gp_w, gp_h = assets["googlePlay"][gp_code]
        calcs = [{"path": sets[name][code], "label": page_strings[name][code]["link.footer"]} for name in CALC_PAGES]
        html = template.render(
            lang=code, path=path, base=BASE, og_locale=og_locale, t=strings[code], locales=locales,
            current={"name": name, "short": code.split("-")[0]}, shots=assets["shots"],
            gp={"code": gp_code, "w": gp_w}, calcs=calcs,
            num=lambda n, s=sep: f"{n:,}".replace(",", s), year=year)
        pages[SITE / path.strip("/") / "index.html"] = html
    calc_template = env.get_template("calc.html")
    units_by_code = {code: units for code, _, units in CALC_LOCALES}
    for name, (mode, _, ct, faq_keys, _) in CALC_PAGES.items():
        locales = [{"code": c, "path": p, "name": landing[c][1], "short": c.split("-")[0]} for c, p in sets[name].items()]
        for code, path in sets[name].items():
            home, lang_name, og_locale, gp_code = landing[code]
            html = calc_template.render(
                mode=mode, lang=code, path=path, home=home, base=BASE, og_locale=og_locale, t=strings[code],
                c=page_strings[name][code], locales=locales, current={"name": lang_name, "short": code.split("-")[0]},
                units=units_by_code[code], factors=[f if code == "en" else f.replace(".", ",") for f in CALC_FACTORS],
                deficits=DEFICITS, num=lambda n, s=CALC_SEP[code]: f"{n:,}".replace(",", s),
                others=[{"path": sets[o][code], "label": page_strings[o][code]["link.footer"]}
                        for o in CALC_PAGES if o != name],
                tdee_page={"path": sets["tdee"][code], "label": page_strings["tdee"][code]["link.footer"]},
                faq_keys=faq_keys, links=store_links(f"{ct}-{code.lower()}"),
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
