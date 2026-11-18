import json
import re
import sys
import unittest
from html import unescape
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
SITE = SRC.parent
sys.path.insert(0, str(SRC))
import acquisition
import build

LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
KNOWN_TYPES = {"Organization", "MobileApplication", "WebApplication", "FAQPage", "VideoObject", "BreadcrumbList"}


def visible_text(html):
    return unescape(re.sub(r"<script\b.*?</script>", "", html, flags=re.S))


class ProteinLanding(unittest.TestCase):
    def test_landing_in_every_product_locale_with_visible_schema(self):
        self.assertEqual(set(acquisition.PROTEIN), set(acquisition.PRODUCT))
        paths = [p["path"] for p in acquisition.PROTEIN.values()]
        self.assertEqual(len(set(paths)), len(paths), "each locale needs its own slug")
        for code, p in acquisition.PROTEIN.items():
            with self.subTest(locale=code):
                html = (SITE / p["path"].strip("/") / "index.html").read_text()
                text = visible_text(html)
                graph = json.loads(LD.search(html).group(1))["@graph"]
                self.assertEqual([e["@type"] for e in graph], ["MobileApplication", "FAQPage"])
                self.assertEqual(graph[1]["inLanguage"], code)
                self.assertEqual(len(graph[1]["mainEntity"]), len(p["faq"]))
                for q, a in p["faq"]:
                    self.assertIn(q, text)
                    self.assertIn(a, text)
                for feature in p["features"]:
                    self.assertIn(feature, text)
                for title, body in p["sections"]:
                    self.assertIn(title, text)
                    self.assertIn(body, text)
                self.assertIn(f'<link rel="alternate" hreflang="{code}" href="{build.BASE}{p["path"]}">', html)
                if code in acquisition.PROTEIN_CALC_PATHS:
                    self.assertIn(f'href="{acquisition.PROTEIN_CALC_PATHS[code]}"', html)

    def test_product_guides_list_the_same_nine_features_in_every_locale(self):
        for code, t in acquisition.PRODUCT.items():
            with self.subTest(locale=code):
                self.assertEqual(len(t["features"]), 9)

    def test_every_page_has_valid_json_ld_and_visible_faq(self):
        pages = [f for f in SITE.rglob("index.html") if "_src" not in f.parts and ".git" not in f.parts]
        self.assertGreater(len(pages), 100)
        for f in pages:
            html = f.read_text()
            blocks = LD.findall(html)
            text = visible_text(html)
            for raw in blocks:
                data = json.loads(raw)
                self.assertEqual(data["@context"], "https://schema.org", f)
                for entity in data["@graph"]:
                    self.assertIn(entity["@type"], KNOWN_TYPES, f)
                    if entity["@type"] == "FAQPage":
                        self.assertTrue(entity["mainEntity"], f)
                        for question in entity["mainEntity"]:
                            self.assertIn(question["name"], text, f"{f}: FAQ question not visible")
                            self.assertIn(question["acceptedAnswer"]["text"], text, f"{f}: FAQ answer not visible")


if __name__ == "__main__":
    unittest.main()
