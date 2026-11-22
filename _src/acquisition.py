import json
from pathlib import Path

from locales import extra_locales, prefix

SRC = Path(__file__).resolve().parent
PRODUCT = json.loads((SRC / "acquisition.json").read_text(encoding="utf-8"))
for _m in extra_locales():
    PRODUCT[_m["code"]] = {"name": _m["name"], "path": prefix(_m["code"]) + _m["slugs"]["what_is"] + "/", "home": prefix(_m["code"]),
                           **json.loads((SRC / "i18n" / "acq" / f"{_m['code']}.json").read_text(encoding="utf-8"))}
PROTEIN = {code: json.loads((SRC / "i18n" / "protein-landing" / f"{code}.json").read_text(encoding="utf-8"))
           for code in PRODUCT}
for _m in extra_locales():
    PROTEIN[_m["code"]]["path"] = prefix(_m["code"]) + _m["slugs"]["protein_landing"] + "/"
PROTEIN_CALC_PATHS = {
    "en": "/protein-calculator/", "de": "/de/proteinrechner/", "es": "/es/calculadora-de-proteinas/",
    "fr": "/fr/calculateur-proteines/", "it": "/it/calcolo-proteine/", "pl": "/pl/kalkulator-bialka/",
    "pt-BR": "/pt-br/calculadora-de-proteinas/", "ru": "/ru/kalkulyator-belka/",
    "tr": "/tr/gunluk-protein-ihtiyaci-hesaplama/",
}
PROTEIN_CALC_PATHS.update({m["code"]: prefix(m["code"]) + m["slugs"]["protein"] + "/" for m in extra_locales()})


def protein_calc_label(code):
    path = SRC / "i18n" / "protein" / f"{code}.json"
    return json.loads(path.read_text(encoding="utf-8"))["link.footer"] if path.exists() else None


def protein_links(code):
    """Localized protein landing and calculator, as (label, href, is_english) related links for any page."""
    links = [(PROTEIN[code]["title"], PROTEIN[code]["path"], False)]
    if code in PROTEIN_CALC_PATHS:
        links.append((protein_calc_label(code), PROTEIN_CALC_PATHS[code], False))
    return links


def english_links(exclude=None):
    return [(v, k, True) for k, v in ENGLISH_PATHS.items() if k != exclude]
MFP = "https://support.myfitnesspal.com/hc/en-us/articles/34889191368077-The-difference-between-Free-Premium-and-Premium"
LOSE = "https://loseit.zendesk.com/hc/en-us/articles/47771695186580-How-to-Use-Snap-It"
CRONO = "https://cronometer.com/features/free-nutrition-tracking-app.html"
CALAI = "https://www.calai.app/"

COMPARISONS = {
    "myfitnesspal": {
        "name": "MyFitnessPal", "summary": "Calcalou focuses on calories, protein and a daily habit with Lou. MyFitnessPal offers a broad food diary, integrations and several paid planning tools.",
        "choose": "Consider Calcalou 1.7 if free barcode scanning and manual protein logging with a weight-based protein goal are your priorities. Consider MyFitnessPal if its food database, existing partner connections or Premium+ meal planning fit the way you already track.",
        "rows": [
            ["Manual logging", "Free calorie and protein entries.", "Free food and exercise logging, recipes and macro tracking."],
            ["Barcodes", "Free; product coverage and nutrition data vary.", "The official plan guide lists the barcode scanner under Premium."],
            ["Photos", "AI estimates, including per-food macros when available, in 1.7. Premium; age and region limits apply.", "Meal Scan is listed under Premium."],
            ["Targets and planning", "Weight-based protein goal; calories and protein shown together.", "Premium adds macros by gram and different goals by day; Premium+ adds meal planning and grocery lists."]
        ], "sources": [("MyFitnessPal plan comparison", MFP)]
    },
    "lose-it": {
        "name": "Lose It!", "summary": "Calcalou and Lose It! both help you log food. Calcalou 1.7 pairs calorie and protein tracking with Lou; Lose It! offers a diary with search and camera logging.",
        "choose": "Consider Calcalou 1.7 for free manual protein entries, a weight-based protein goal and free barcode scanning (Calcalou's barcode scanning is free; check Lose It!'s current plan). Consider Lose It! if you prefer its diary or already have foods and routines saved there. Try foods you eat often before moving your routine.",
        "rows": [
            ["Logging workflow", "Manual calorie and protein entries; barcode and AI photo options.", "Official help lists food search, Scan It barcodes, Snap It photos and Say It voice search; check plan eligibility."],
            ["Barcodes", "Free; verify the product and portion.", "Scan It is documented as a way to log packaged food; check the current plan in Lose It!."],
            ["Photos", "AI estimates calories and per-food macros when available in 1.7; review before saving.", "Snap It suggests database matches from a photo. Official help says Premium and English device language are required."],
            ["Choosing", "A daily calorie and protein view with Lou, water and streaks.", "A food diary with searchable foods and editable photo matches."]
        ], "sources": [("Lose It! Snap It guide", LOSE), ("Lose It! food logging guide", "https://loseit.zendesk.com/hc/en-us/articles/49210381551380-How-to-Log-Food-in-Lose-It")]
    },
    "cronometer": {
        "name": "Cronometer", "summary": "Calcalou 1.7 focuses on calories, protein and a habit with Lou. Cronometer fits better for detailed vitamin and nutrient records. Both have free barcodes.",
        "choose": "Consider Calcalou 1.7 if you want calories and protein together, water tracking and a friendly daily routine. Choose Cronometer if detailed micronutrient analysis is central to your decision. Free barcodes are not unique to Calcalou: Cronometer Basic includes them too.",
        "rows": [
            ["Free food tracking", "Manual calories and protein, plus barcodes.", "Calories, macros, vitamins and minerals in Basic."],
            ["Barcodes", "Free; coverage depends on the product data.", "Unlimited barcode scanning is included in Basic."],
            ["Nutrient depth", "Calories, protein, fat and carbs; no claim of a full micronutrient database.", "The Basic page advertises up to 95 nutrients and compounds."],
            ["Routine", "Lou, streaks, water and platform-dependent widgets.", "Basic includes custom meals, recipes and connections to other apps and devices."]
        ], "sources": [("Cronometer Basic features", CRONO)]
    },
    "cal-ai": {
        "name": "Cal AI", "summary": "Calcalou 1.7 and Cal AI both offer photo calorie and macro estimates. Calcalou adds free manual calorie and protein logging, free barcodes and Lou.",
        "choose": "Consider Calcalou 1.7 if free manual entries and barcodes, a weight-based protein goal and Lou appeal to you. Consider Cal AI if its photo-first workflow fits your routine. The Calcalou Team has not run a controlled head-to-head accuracy test and do not claim either app is more accurate.",
        "rows": [
            ["Photo estimates", "Calories and per-food protein, fat and carbs when available in 1.7.", "The official site describes photo estimates of calories, protein, carbs and fat."],
            ["Other entry methods", "Free manual calorie and protein entry and free barcodes.", "The official site lists barcodes, meal descriptions, custom foods and recipes."],
            ["Payment", "Free core tracking; AI is Premium; where offered, an account can try up to 3 free scans once. AI and Premium purchases are 18+ in 1.7.", "Check the current store subscription and eligibility screen; this guide does not assert a universal price or free tier."],
            ["Accuracy", "Review portions, hidden oils and missing values before saving.", "Photo nutrition values should also be treated as estimates, not measurements."]
        ], "sources": [("Cal AI official product page", CALAI)]
    }
}

ENGLISH_PATHS = {f"/compare/calcalou-vs-{key}/": f"Calcalou vs {value['name']}" for key, value in COMPARISONS.items()}
ENGLISH_PATHS["/best-protein-tracker/"] = "How to choose the best protein tracker for you"
PROTEIN_GUIDE = "/best-protein-tracker/"


def graph(base, path, lang, description, faq, product):
    entities = [{"@type": "FAQPage", "@id": base + path + "#faq", "inLanguage": lang,
                 "mainEntity": [{"@type": "Question", "name": q,
                                 "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]
    if product:
        entities.insert(0, {
            "@type": "MobileApplication", "@id": base + "/#app", "name": "Calcalou",
            "url": base + path, "description": description,
            "applicationCategory": "HealthApplication", "operatingSystem": "iOS, iPadOS, Android",
            "inLanguage": list(PRODUCT), "image": base + "/assets/img/og.jpg",
            "installUrl": ["https://apps.apple.com/app/id6757434158", "https://play.google.com/store/apps/details?id=com.khrolovich.calorietracker"],
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free download with optional in-app purchases."},
            "publisher": {"@type": "Organization", "name": "Calcalou", "url": base + "/"}
        })
    return {"@context": "https://schema.org", "@graph": entities}


def render(env, base, store_links):
    template = env.get_template("acquisition.html")
    pages = {}
    for code, t in PRODUCT.items():
        path = t["path"]
        pages[path] = template.render(lang=code, base=base, path=path, t=t, title=t["title"],
            description=t["summary"], product=True, locales=PRODUCT, faq=t["faq"],
            ld=graph(base, path, code, t["summary"], t["faq"], True), sections=[],
            links=store_links(f"web-about-{code.lower()}"), related=protein_links(code) + english_links())
    for code, p in PROTEIN.items():
        t = {**PRODUCT[code], **{k: p[k] for k in ("title", "summary", "features_title", "features", "faq")}}
        pages[p["path"]] = template.render(lang=code, base=base, path=p["path"], t=t, title=p["title"],
            description=p["summary"], product=True, locales={c: {"path": v["path"], "name": PRODUCT[c]["name"]}
                                                           for c, v in PROTEIN.items()},
            faq=p["faq"], ld=graph(base, p["path"], code, p["summary"], p["faq"], True),
            sections=[{"title": a, "text": b} for a, b in p["sections"]],
            links=store_links(f"web-protein-{code.lower()}"),
            related=[(PRODUCT[code]["title"], PRODUCT[code]["path"], False)]
                    + protein_links(code)[1:] + english_links())
    t = PRODUCT["en"]
    for key, c in COMPARISONS.items():
        path = f"/compare/calcalou-vs-{key}/"
        title = f"Calcalou vs {c['name']}: calories and protein"
        faq = [("Which app should I choose?", c["choose"]),
               ("Is this an independent review?", "No. This comparison is written by the Calcalou Team using the official sources linked on this page. It does not establish an accuracy or health-outcome advantage.")]
        pages[path] = template.render(lang="en", base=base, path=path, t=t, title=title,
            description=c["summary"], product=False, locales={}, competitor=c["name"], rows=c["rows"],
            sections=[{"title": "Which fits your routine?", "text": c["choose"]},
                      {"title": "Review the result", "text": "Food data and photos can be incomplete. Check portions and nutrition labels. Do not treat a missing macro as zero. A logging app is not a medical device."}],
            faq=faq, sources=c["sources"] + [("Calcalou 1.7 product guide", base + t["path"])],
            ld=graph(base, path, "en", c["summary"], faq, False), links=store_links(f"web-vs-{key}"),
            related=[(t["title"], t["path"], True)] + protein_links("en") + english_links(path))
    path = "/best-protein-tracker/"
    title = ENGLISH_PATHS[path]
    summary = "The best protein tracker is one that fits how you log food. Compare free manual entry, barcodes, editable photo estimates, protein goals and nutrient detail."
    sections = [
        {"title": "Start with the foods you actually eat", "text": "Test your usual breakfast, a packaged snack and a home-cooked meal. Check the label, serving size and protein units. A large database is useful only if the entries you use are complete and correct."},
        {"title": "Keep protein visible beside calories", "text": "Look for a daily protein target in grams and a clear daily total alongside calories. Calcalou 1.7 can suggest a protein goal from body weight. A target is a starting point for tracking, not a personal medical recommendation."},
        {"title": "Decide what must be free", "text": "Calcalou 1.7 offers free manual calorie and protein logging and free barcodes. Cronometer Basic also has free barcodes and adds detailed vitamins and minerals. MyFitnessPal's official plan guide puts barcode scanning and gram-based macro targets in Premium. Check the current plan in your country."},
        {"title": "Use photos as editable estimates", "text": "Photo logging can reduce typing, but it cannot reliably see every ingredient or portion. Calcalou 1.7 and Cal AI describe photo macro estimates; Lose It! Snap It suggests food database matches. Correct the result, and enter missing macros yourself instead of counting them as zero."},
        {"title": "Choose by the job you need done", "text": "Try Calcalou 1.7 for a daily calorie and protein routine with Lou, water and widgets. Try Cronometer when detailed nutrients matter most. Consider MyFitnessPal for its diary, integrations and paid planning tools, or Lose It! and Cal AI if you prefer their logging flow. This guide awards no universal winner."},
        {"title": "Check language, age and availability", "text": "Calcalou 1.7 has 41 interface languages. The app is 13+ subject to local requirements; AI scans and Premium purchases in 1.7 are 18+ and region-dependent. Sign-in is required. Verify the store version before relying on a feature."}
    ]
    faq = [("What should I check in a protein tracker?", "Check daily protein grams, an editable target, portion controls, barcode data quality, clear missing values and the cost of the logging tools you will use."),
           ("Is an AI photo a measurement of protein?", "No. It is an estimate. Portion size, ingredients and food preparation affect the result. Verify labels or weighed ingredients when accuracy matters."),
           ("Does free barcode scanning make Calcalou unique?", "No. Calcalou and Cronometer Basic both offer it. Choose using your whole workflow, not one feature.")]
    pages[path] = template.render(lang="en", base=base, path=path, t=t, title=title, description=summary,
        product=False, locales={}, rows=[], competitor="", sections=sections, faq=faq,
        sources=[("Cronometer Basic", CRONO), ("MyFitnessPal plans", MFP), ("Lose It! Snap It", LOSE), ("Cal AI", CALAI)],
        ld=graph(base, path, "en", summary, faq, False), links=store_links("web-protein-guide"),
        related=[(t["title"], t["path"], True)] + protein_links("en") + english_links(path))
    return pages


def llms(base):
    t = PRODUCT["en"]
    text = "# Calcalou\n\n> " + t["summary"] + "\n\n" + t["version"] + "\n\n"
    text += "## Product facts\n\n" + "\n".join("- " + s for s in t["features"]) + "\n\n"
    text += "## Questions\n\n" + "\n\n".join("### " + q + "\n\n" + a for q, a in t["faq"]) + "\n\n"
    text += "## Pages\n\n" + "\n".join(f"- [{v}]({base}{p})" for p, v in [(t["path"], t["title"]), (PROTEIN["en"]["path"], PROTEIN["en"]["title"]),
                 (PROTEIN_CALC_PATHS["en"], protein_calc_label("en")), *ENGLISH_PATHS.items()]) + "\n"
    text += f"- [Privacy policy]({base}/privacy/)\n- [Support]({base}/support/)\n- [App Store](https://apps.apple.com/app/id6757434158)\n- [Google Play](https://play.google.com/store/apps/details?id=com.khrolovich.calorietracker)\n"
    text += "\n## Localized product guides\n\n" + "\n".join(f"- [{v['name']}]({base}{v['path']})" for v in PRODUCT.values()) + "\n"
    text += "\n## Localized protein tracker pages\n\n" + "\n".join(f"- [{PRODUCT[c]['name']}]({base}{v['path']})" for c, v in PROTEIN.items()) + "\n"
    text += "\nChecked 2026-11-17. Published by the Calcalou Team. This summary does not establish independent ratings or comparative accuracy.\n"
    return text
