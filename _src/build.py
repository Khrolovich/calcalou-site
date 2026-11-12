#!/usr/bin/env python3
"""Render every page set in every site locale: the landing (_src/template.html + i18n/<code>.json), the
calculators (_src/calc.html + i18n/calc/<code>.json) and the pilot food pages in FOOD_LOCALES (_src/food.html +
foods/foods.json + the USDA snapshot foods/fdc.json + i18n/food/<code>.json). _src/check_locales.py enforces that each set covers LOCALES.

Usage: python3 _src/build.py [--check]   (--check fails if a generated page is out of date)
"""
import datetime
import json
import re
import subprocess
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
    ("es", "/es/calculadora-metabolismo-basal/", "metric"),
    ("fr", "/fr/calcul-metabolisme-de-base/", "metric"),
    ("it", "/it/calcolo-metabolismo-basale/", "metric"),
    ("pl", "/pl/kalkulator-bmr/", "metric"),
    ("pt-BR", "/pt-br/calculadora-tmb/", "metric"),
    ("ru", "/ru/kalkulyator-osnovnogo-obmena/", "metric"),
    ("tr", "/tr/bazal-metabolizma-hesaplama/", "metric"),
]
CALC_FACTORS = ["1.2", "1.375", "1.55", "1.725", "1.9"]
TDEE_PATHS = {
    "en": "/tdee-calculator/", "de": "/de/kalorienbedarf-rechner/", "es": "/es/calculadora-de-calorias/",
    "fr": "/fr/calcul-besoin-calorique/", "it": "/it/calcolo-fabbisogno-calorico/",
    "pl": "/pl/kalkulator-zapotrzebowania-kalorycznego/", "pt-BR": "/pt-br/calculadora-tdee/",
    "ru": "/ru/kalkulyator-kaloriy/", "tr": "/tr/gunluk-kalori-ihtiyaci-hesaplama/",
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
    "calculator": ("bmr", None, "web-calc", ["bmr", "tdee", "formula", "accuracy", "activity"], None),
    "tdee": ("tdee", "tdee", "web-tdee", ["tdee", "difference", "activity", "use", "accuracy"], TDEE_PATHS),
    "deficit": ("deficit", "deficit", "web-deficit", ["deficit", "maintenance", "size", "floor", "accuracy"],
                DEFICIT_PATHS),
}

FOODS = json.loads((SRC / "foods" / "foods.json").read_text(encoding="utf-8"))
# The food pages are a pilot in these languages only; check_locales.py holds them to this list instead of LOCALES.
FOOD_LOCALES = FOODS["locales"]


def food_paths(food):
    return {code: hub + food["slug"][code] + "/" for code, hub in FOOD_LOCALES.items()}


def page_sets():
    """Every localized page set: name -> {locale code: path}."""
    sets = {"landing": {code: path for code, path, *_ in LOCALES}}
    for name, (_, _, _, _, paths) in CALC_PAGES.items():
        sets[name] = paths or {code: path for code, path, _ in CALC_LOCALES}
    sets["foods"] = dict(FOOD_LOCALES)
    for food in FOODS["foods"]:
        sets["food-" + food["key"]] = food_paths(food)
    return sets


def set_locales(name):
    return set(FOOD_LOCALES) if name == "foods" or name.startswith("food-") else {code for code, *_ in LOCALES}


def r0(x):
    return int(x + 0.5)


def r1(x):
    return int(x * 10 + 0.5) / 10


def portion_values(per100, grams):
    return {"kcal": r0(per100["kcal"] * grams / 100),
            **{k: r1(per100[k] * grams / 100) for k in ("protein", "carbs", "fat")}}


def food_model(fdc):
    """foods.json joined with the USDA snapshot (_src/foods/fdc.json). Fails when they disagree: a missing entry or
    nutrient, or a portion whose `match` names no USDA portion of that weight."""
    errors, models = [], {}
    keys = {f["key"] for f in FOODS["foods"]}
    for food in FOODS["foods"]:
        key, entry = food["key"], fdc.get(str(food["fdc"]))
        if not entry:
            errors.append(f"{key}: FDC {food['fdc']} missing from fdc.json (run _src/foods/fetch_fdc.py)")
            continue
        per100 = entry["per_100g"]
        missing = [k for k in ("kcal", "protein", "fat", "carbs") if per100.get(k) is None]
        if missing:
            errors.append(f"{key}: FDC {food['fdc']} has no {missing}")
            continue
        portions = []
        for p in food["portions"]:
            if "match" in p:
                hits = [g for label, g in entry["portions"] if p["match"].lower() in label.lower()]
                if not any(abs(g - p["g"]) <= 0.5 for g in hits):
                    errors.append(f"{key}/{p['id']}: USDA portions matching {p['match']!r} weigh {hits}, "
                                  f"foods.json says {p['g']}")
            portions.append({"id": p["id"], "g": p["g"], "usda": "match" in p,
                             "label": {code: p[code] for code in FOOD_LOCALES}, **portion_values(per100, p["g"])})
        if food["headline"] not in {p["id"] for p in portions}:
            errors.append(f"{key}: headline {food['headline']!r} is not one of its portions")
        unknown = [c for c in food["compare"] if c not in keys or c == key]
        if unknown:
            errors.append(f"{key}: compare lists {unknown}")
        variants = []
        for v in food["variants"]:
            ventry = fdc.get(str(v["fdc"]))
            if not ventry or ventry["per_100g"].get("kcal") is None:
                errors.append(f"{key}: variant FDC {v['fdc']} missing from fdc.json")
                continue
            variants.append({"fdc": v["fdc"], "kcal100": r0(ventry["per_100g"]["kcal"]),
                             "label": {code: v[code] for code in FOOD_LOCALES}})
        models[key] = {"food": food, "entry": entry, "per100": per100, "portions": portions, "variants": variants}
    if errors:
        raise SystemExit("food pages: " + "; ".join(errors))
    return models


def load_fdc():
    path = SRC / "foods" / "fdc.json"
    if not path.exists():
        raise SystemExit("_src/foods/fdc.json missing: run python3 _src/foods/fetch_fdc.py")
    return json.loads(path.read_text(encoding="utf-8"))


def fill(text, **values):
    for name, value in values.items():
        text = text.replace("{" + name + "}", str(value))
    return text


def short_label(label):
    return re.sub(r"\s*\([^)]*\)$", "", label)


CHANNELS = {"web": ("calcalou.com", "referral"), "yt": ("youtube", "social"), "tt": ("tiktok", "social"),
            "ig": ("instagram", "social"), "fb": ("facebook", "social"), "reddit": ("reddit", "social"),
            "cr": ("creator", "social"), "links": ("linkinbio", "social"), "share": ("app-share", "referral"),
            "invite": ("app-invite", "referral"), "doctor": ("doctor", "referral")}
LANDING_CT = "web-site"
CF_BEACON_TOKEN = ""
STATIC_PAGES = ("links/index.html", "i/index.html", "press/index.html", "404.html")
ANALYTICS_BLOCK = re.compile(r"<!-- analytics -->.*?<!-- /analytics -->", re.S)


def analytics_block():
    tag = ('<script defer src="https://static.cloudflareinsights.com/beacon.min.js" '
           f"data-cf-beacon='{{\"token\": \"{CF_BEACON_TOKEN}\"}}'></script>") if CF_BEACON_TOKEN else ""
    return f"<!-- analytics -->{tag}<!-- /analytics -->"


def static_pages():
    pages = {}
    for rel in STATIC_PAGES:
        html = (SITE / rel).read_text(encoding="utf-8")
        if not ANALYTICS_BLOCK.search(html):
            raise SystemExit(f"{rel}: no <!-- analytics --> block")
        pages[SITE / rel] = ANALYTICS_BLOCK.sub(lambda _: analytics_block(), html)
    return pages


def store_links(ct):
    """Mirror of storeLinks() in /assets/landing.js (scheme: _src/ATTRIBUTION.md), for pages that do not load it."""
    prefix = ct.split("-")[0]
    source, medium = CHANNELS.get(prefix, (prefix, "other"))
    return {
        "ios": f"https://apps.apple.com/app/apple-store/id6757434158?pt=128407090&ct={quote(ct, safe='')}&mt=8",
        "android": "https://play.google.com/store/apps/details?id=com.khrolovich.calorietracker&referrer="
                   + quote(f"utm_source={source}&utm_medium={medium}&utm_campaign={ct}", safe=""),
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


def load_guide(page_set, code):
    """Optional extra sections for one page in one language (_src/i18n/guides/<set>/<code>.json), or None."""
    path = SRC / "i18n" / "guides" / page_set / f"{code}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


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
    from markupsafe import Markup

    env = Environment(loader=FileSystemLoader(SRC), autoescape=True, undefined=StrictUndefined,
                      trim_blocks=False, lstrip_blocks=False)
    env.globals["analytics"] = Markup(analytics_block())
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
        if code in FOOD_LOCALES:
            calcs.append({"path": FOOD_LOCALES[code], "label": load_food_strings()[code]["hub.link"]})
        html = template.render(
            lang=code, path=path, base=BASE, og_locale=og_locale, t=strings[code], locales=locales,
            current={"name": name, "short": code.split("-")[0]}, shots=assets["shots"],
            gp={"code": gp_code, "w": gp_w}, calcs=calcs, links=store_links(LANDING_CT),
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
                guide=load_guide(name, code),
                faq_keys=faq_keys, links=store_links(f"{ct}-{code.lower()}"),
                gp={"code": gp_code, "w": assets["googlePlay"][gp_code][0]}, year=year)
            pages[SITE / path.strip("/") / "index.html"] = html
    pages.update(render_foods(env, strings, page_strings, assets, landing, year))
    return pages


def load_food_strings():
    english = json.loads((SRC / "i18n" / "food" / "en.json").read_text(encoding="utf-8"))
    result = {}
    for code in FOOD_LOCALES:
        strings = json.loads((SRC / "i18n" / "food" / f"{code}.json").read_text(encoding="utf-8"))
        if set(strings) != set(english) or not all(str(v).strip() for v in strings.values()):
            raise SystemExit(f"food/{code}.json: keys differ from food/en.json or a value is empty")
        result[code] = strings
    return result


def food_formatters(code):
    sep, point = CALC_SEP[code], "." if code == "en" else ","
    num = lambda n: f"{n:,}".replace(",", sep)  # noqa: E731
    dec = lambda x: f"{x:.1f}".replace(".", point)  # noqa: E731
    grams = lambda g: dec(g) if g != int(g) else num(int(g))  # noqa: E731
    return num, dec, grams


def localize_food(model, models, code, sets):
    food, entry, per100 = model["food"], model["entry"], model["per100"]
    lc = (lambda s: s[:1].lower() + s[1:]) if code == "en" else (lambda s: s)
    portions = [{**p, "label": p["label"][code], "short": short_label(p["label"][code]),
                 "short_lc": lc(short_label(p["label"][code]))} for p in model["portions"]]
    compare = [model["food"]["key"]] + food["compare"]
    return {
        "key": food["key"], "name": food["name"][code], "name_lc": lc(food["name"][code]), "h1": food["h1"][code],
        "title": food["title"][code], "note": food["note"][code], "video": food["video"],
        "per100": {k: (r0(v) if k == "kcal" else r1(v)) if v is not None else None for k, v in per100.items()},
        "portions": portions, "head": next(p for p in portions if p["id"] == food["headline"]),
        "variants": [{**v, "label": v["label"][code]} for v in model["variants"]],
        "compare": [{"name": models[k]["food"]["name"][code], "path": sets["food-" + k][code],
                     "kcal100": r0(models[k]["per100"]["kcal"]), "protein100": r1(models[k]["per100"]["protein"]),
                     "current": k == food["key"]} for k in compare],
        "fdc": {"id": food["fdc"], "data_type": entry["data_type"], "description": entry["description"],
                "fetched_at": entry["fetched_at"]},
    }


def food_ld(food, f, faq, crumbs, lang):
    graph = [{"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": c["name"], "item": BASE + c["path"]}
        for i, c in enumerate(crumbs)]}]
    if food:
        graph.append({"@type": "FAQPage", "inLanguage": lang, "mainEntity": [
            {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in faq]})
        if food["video"]:
            v = food["video"]
            graph.append({"@type": "VideoObject", "name": v["title"], "description": f["video.text"],
                          "thumbnailUrl": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg", "uploadDate": v["date"],
                          "embedUrl": f"https://www.youtube.com/embed/{v['id']}"})
    return {"@context": "https://schema.org", "@graph": graph}


def render_foods(env, strings, page_strings, assets, landing, year):
    template = env.get_template("food.html")
    models = food_model(load_fdc())
    sets = page_sets()
    food_strings = load_food_strings()
    pages = {}
    for code, hub in FOOD_LOCALES.items():
        f, t = food_strings[code], strings[code]
        home, lang_name, og_locale, gp_code = landing[code]
        num, dec, grams = food_formatters(code)
        in_sentence = (lambda s: s if s.split()[0].isupper() else s[:1].lower() + s[1:]) if code == "en" else str
        calcs = {name: {"path": sets[name][code], "label": in_sentence(page_strings[name][code]["link.footer"])}
                 for name in ("tdee", "deficit")}
        common = dict(lang=code, home=home, base=BASE, og_locale=og_locale, t=t, f=f, fill=fill, num=num, dec=dec,
                      grams=grams, calcs=calcs, hub={"path": hub, "label": f["hub.link"]}, year=year,
                      current={"name": lang_name, "short": code.split("-")[0]},
                      gp={"code": gp_code, "w": assets["googlePlay"][gp_code][0]})
        foods = sorted((localize_food(m, models, code, sets) for m in models.values()),
                       key=lambda x: x["name"].casefold().translate(str.maketrans("ąćęłńóśźż", "acelnoszz")))
        hub_crumbs = [{"name": f["crumb.home"], "path": home}, {"name": f["hub.link"], "path": hub}]
        pages[SITE / hub.strip("/") / "index.html"] = template.render(
            **common, food=None, path=hub, rows=[{**x, "path": sets["food-" + x["key"]][code],
                                                  "kcal100": x["per100"]["kcal"]} for x in foods],
            locales=[{"code": c, "path": p, "name": landing[c][1], "short": c.split("-")[0]}
                     for c, p in sets["foods"].items()],
            meta_title=f["hub.title"], meta_description=f["hub.description"], crumbs=hub_crumbs,
            ld=food_ld(None, f, [], hub_crumbs, code), links=store_links(f"web-food-hub-{code.lower()}"))
        for food in foods:
            path, head = sets["food-" + food["key"]][code], food["head"]
            p100 = food["per100"]
            faq = [{"q": food["h1"], "a": fill(f["faq.portion.a"], portion=head["short"], g=grams(head["g"]),
                                               kcal=num(head["kcal"]), protein=dec(head["protein"]),
                                               carbs=dec(head["carbs"]), fat=dec(head["fat"]))},
                   {"q": fill(f["faq.per100.q"], name=food["name_lc"]),
                    "a": fill(f["faq.per100.a"], kcal100=num(p100["kcal"]), protein=dec(p100["protein"]),
                              carbs=dec(p100["carbs"]), fat=dec(p100["fat"]))},
                   {"q": fill(f["faq.vary.q"], name=food["name_lc"]), "a": food["note"]},
                   {"q": f["faq.source.q"], "a": fill(f["faq.source.a"], fdc=food["fdc"]["id"],
                                                      type=food["fdc"]["data_type"],
                                                      description=food["fdc"]["description"],
                                                      date=food["fdc"]["fetched_at"])}]
            crumbs = hub_crumbs + [{"name": food["name"], "path": path}]
            pages[SITE / path.strip("/") / "index.html"] = template.render(
                **common, food=food, path=path, faq=faq, crumbs=crumbs,
                locales=[{"code": c, "path": p, "name": landing[c][1], "short": c.split("-")[0]}
                         for c, p in sets["food-" + food["key"]].items()],
                meta_title=fill(f["meta.title"], title=food["title"]),
                meta_description=fill(f["meta.description"], name=food["name"], kcal100=num(p100["kcal"]),
                                      portion=head["short_lc"], g=grams(head["g"]), kcal=num(head["kcal"])),
                ld=food_ld(food, f, faq, crumbs, code), links=store_links(f"web-food-{food['key']}-{code.lower()}"))
    return pages | go_pages(env, strings["en"], assets["googlePlay"]["en"][0]) | static_pages()


def qr_svg(text, name):
    from markupsafe import Markup

    cached = SRC / "qr" / f"{name}.svg"
    if not cached.exists() or f'data-text="{text}"' not in cached.read_text(encoding="utf-8"):
        cached.parent.mkdir(exist_ok=True)
        cached.write_text(subprocess.check_output(["swift", str(SRC / "tools" / "qr.swift"), text], text=True),
                          encoding="utf-8")
    return Markup(cached.read_text(encoding="utf-8").strip())


def go_pages(env, t, gp_w):
    """Smart links /go/<channel>/ from _src/go.json (scheme: _src/ATTRIBUTION.md)."""
    template = env.get_template("go.html")
    pages = {}
    for channel, ct in json.loads((SRC / "go.json").read_text(encoding="utf-8")).items():
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", channel) or not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", ct):
            raise SystemExit(f"go.json: bad channel or ct: {channel!r}: {ct!r}")
        url = f"{BASE}/go/{channel}/"
        pages[SITE / "go" / channel / "index.html"] = template.render(
            t=t, gp_w=gp_w, ct=ct, links=store_links(ct), qr=qr_svg(url, channel))
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
