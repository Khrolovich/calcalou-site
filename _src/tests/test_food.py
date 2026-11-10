"""Food pages: the USDA snapshot, the claims in each note, and the rendered pages.
Run: python3 -m unittest discover -s _src/tests -p 'test_*.py'"""
import copy
import datetime
import json
import re
import sys
import unittest
from html import unescape
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
SITE = SRC.parent
sys.path.insert(0, str(SRC))
from build import (BASE, DEFICIT_PATHS, FOOD_LOCALES, FOODS, TDEE_PATHS, food_model, load_fdc,  # noqa: E402
                   page_sets, portion_values)

FDC = load_fdc()
MODELS = food_model(FDC)


def per100(key, nutrient="kcal"):
    return MODELS[key]["per100"][nutrient]


def portion(key, pid):
    return next(p for p in MODELS[key]["portions"] if p["id"] == pid)


def variant(key, fdc_id):
    return FDC[str(fdc_id)]["per_100g"]["kcal"]


def description(key):
    return MODELS[key]["entry"]["description"].lower()


class Snapshot(unittest.TestCase):
    def test_every_entry_came_from_the_api(self):
        for fid, entry in FDC.items():
            with self.subTest(fdc=fid):
                self.assertIn(entry["data_type"], ("SR Legacy", "Foundation", "Survey (FNDDS)"))
                self.assertRegex(entry["fetched_at"], r"^20[2-9]\d-\d\d-\d\d$")
                self.assertNotIn("SYNTHETIC", entry["description"])

    def test_portion_math(self):
        values = portion_values({"kcal": 89, "protein": 1.09, "carbs": 22.84, "fat": 0.33}, 118)
        self.assertEqual(values, {"kcal": 105, "protein": 1.3, "carbs": 27.0, "fat": 0.4})

    def test_a_wrong_portion_weight_fails(self):
        broken = copy.deepcopy(FDC)
        food = FOODS["foods"][0]
        broken[str(food["fdc"])]["portions"] = [[label, g + 5] for label, g in broken[str(food["fdc"])]["portions"]]
        with self.assertRaises(SystemExit):
            food_model(broken)

    def test_a_missing_nutrient_fails(self):
        broken = copy.deepcopy(FDC)
        broken[str(FOODS["foods"][0]["fdc"])]["per_100g"]["protein"] = None
        with self.assertRaises(SystemExit):
            food_model(broken)


class NoteClaims(unittest.TestCase):
    """Each note states facts; these tests hold them to the USDA numbers they rely on."""

    def test_banana_size_beats_ripeness(self):
        self.assertGreater(portion("banana", "large")["kcal"], 1.5 * portion("banana", "xs")["kcal"])

    def test_cup_of_strawberries_under_medium_apple(self):
        self.assertLess(portion("strawberries", "cup")["kcal"], portion("apple", "medium")["kcal"])

    def test_egg_cooking(self):
        raw = per100("egg")
        self.assertLess(abs(variant("egg", 173424) - raw) / raw, 0.1)
        self.assertGreater(variant("egg", 173423), raw)
        self.assertGreater(variant("egg", 172187), raw)

    def test_popcorn_oil_and_microwave_add_fat(self):
        for fid in (170247, 167549):
            self.assertGreater(variant("popcorn", fid), 1.2 * per100("popcorn"))

    def test_rice(self):
        white = per100("white-rice")
        self.assertLess(abs(variant("white-rice", 2708414) - white) / white, 0.1)
        self.assertGreater(variant("white-rice", 2708404), white)
        self.assertIn("no added fat", description("white-rice"))

    def test_toasting_bagel_raises_value_per_100g(self):
        self.assertGreater(variant("bagel", 174900), per100("bagel"))

    def test_raisins_concentrate_grapes(self):
        self.assertGreater(per100("raisins"), 3 * per100("grapes"))

    def test_orange_juice_has_under_half_a_gram_of_fibre(self):
        self.assertLess(per100("orange-juice", "fiber"), 0.5)

    def test_olive_oil_is_almost_pure_fat(self):
        self.assertGreaterEqual(per100("olive-oil", "fat"), 99)

    def test_avocado_calories_mostly_from_fat(self):
        self.assertGreater(9 * per100("avocado", "fat"), per100("avocado") / 2)

    def test_notes_match_the_usda_entry(self):
        expected = {"banana": "raw", "apple": "with skin", "dark-chocolate": "70-85%", "cheddar": "cheddar",
                    "chicken-breast": "roasted", "peanut-butter": "smooth", "potato-chips": "plain, salted",
                    "orange-juice": "raw", "croissant": "butter", "bagel": "plain", "almonds": "almonds"}
        for key, text in expected.items():
            with self.subTest(food=key):
                self.assertIn(text, description(key))
        self.assertIn("meat only", description("chicken-breast"))


class Pages(unittest.TestCase):
    def html(self, path):
        return (SITE / path.strip("/") / "index.html").read_text(encoding="utf-8")

    def ld(self, html):
        return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))["@graph"]

    def test_food_pages(self):
        sets, sitemap = page_sets(), (SITE / "sitemap.xml").read_text(encoding="utf-8")
        titles = []
        for food in FOODS["foods"]:
            pages = sets["food-" + food["key"]]
            expected = {code: BASE + path for code, path in pages.items()} | {"x-default": BASE + pages["en"]}
            head = portion(food["key"], food["headline"])
            for code, path in pages.items():
                with self.subTest(page=path):
                    html = self.html(path)
                    self.assertIn(f'<html lang="{code}">', html)
                    self.assertEqual(re.findall(r'rel="canonical" href="([^"]+)"', html), [BASE + path])
                    self.assertEqual(dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"',
                                                     html)), expected)
                    title = unescape(re.search(r"<title>(.*?)</title>", html).group(1))
                    titles.append(title)
                    self.assertLessEqual(len(title), 70)
                    self.assertLessEqual(len(unescape(re.search(r'name="description" content="([^"]+)"',
                                                                html).group(1))), 160)
                    graph = self.ld(html)
                    types = [g["@type"] for g in graph]
                    self.assertEqual(types, ["BreadcrumbList", "FAQPage"] + (["VideoObject"] if food["video"] else []))
                    visible = [unescape(q) for q in re.findall(r"<summary>(.*?)</summary>", html)]
                    self.assertEqual([q["name"] for q in graph[1]["mainEntity"]], visible)
                    self.assertIn(f'<div class="display"><b>{head["kcal"]:,}</b>'.replace(",", "," if code == "en"
                                                                                           else ""), html)
                    self.assertIn(f'href="{TDEE_PATHS[code]}"', html)
                    self.assertIn(f'href="{DEFICIT_PATHS[code]}"', html)
                    self.assertIn(f"ct=food-{food['key']}-{code}&", html)
                    self.assertEqual("data-yt=" in html, bool(food["video"]))
                    for p in MODELS[food["key"]]["portions"]:
                        if p["g"] != int(p["g"]):
                            self.assertIn(f'{p["g"]:.1f} g'.replace(".", "." if code == "en" else ","), html)
                    self.assertIn(f"<loc>{BASE}{path}</loc>", sitemap)
        self.assertEqual(len(titles), len(set(titles)))

    def test_videos_are_public(self):
        today = datetime.date.today().isoformat()
        for food in FOODS["foods"]:
            if food["video"]:
                self.assertLessEqual(food["video"]["date"], today, food["key"])

    def test_hub_links_every_food(self):
        sets = page_sets()
        for code, hub in FOOD_LOCALES.items():
            html = self.html(hub)
            for food in FOODS["foods"]:
                self.assertIn(f'href="{sets["food-" + food["key"]][code]}"', html)
            self.assertEqual([g["@type"] for g in self.ld(html)], ["BreadcrumbList"])
            self.assertIn(f'href="{hub}"', self.html("/" if code == "en" else f"/{code}/"))


if __name__ == "__main__":
    unittest.main()
