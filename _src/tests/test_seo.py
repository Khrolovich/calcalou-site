"""SEO checks for the published files. Run: python3 -m unittest discover -s _src/tests -p 'test_*.py'"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
SITE = SRC.parent
sys.path.insert(0, str(SRC))
from build import BASE, LOCALES  # noqa: E402


class LandingHead(unittest.TestCase):
    def page(self, path):
        return (SITE / path.strip("/") / "index.html").read_text(encoding="utf-8")

    def test_canonical_and_hreflang(self):
        expected = {code: BASE + path for code, path, *_ in LOCALES} | {"x-default": BASE + "/"}
        for _, path, *_ in LOCALES:
            html = self.page(path)
            self.assertEqual(re.findall(r'rel="canonical" href="([^"]+)"', html), [BASE + path])
            alternates = dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html))
            self.assertEqual(alternates, expected, path)

    def test_jsonld(self):
        for code, path, *_ in LOCALES:
            raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', self.page(path), re.S).group(1)
            graph = json.loads(raw)["@graph"]
            self.assertEqual([g["@type"] for g in graph], ["Organization", "MobileApplication", "FAQPage"])
            app = graph[1]
            self.assertEqual(app["inLanguage"], code)
            self.assertEqual(app["offers"]["price"], "0")
            self.assertNotIn("aggregateRating", app)
            self.assertTrue(all(q["name"] and q["acceptedAnswer"]["text"] for q in graph[2]["mainEntity"]))


class StaticFiles(unittest.TestCase):
    def test_sitemap_up_to_date(self):
        result = subprocess.run([sys.executable, str(SRC / "seo.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_robots_points_to_sitemap(self):
        self.assertIn(f"Sitemap: {BASE}/sitemap.xml", (SITE / "robots.txt").read_text())

    def test_well_known_published_by_jekyll(self):
        self.assertIn('".well-known"', (SITE / "_config.yml").read_text())
        self.assertFalse((SITE / ".nojekyll").exists(), "privacy/ and support/ are Markdown rendered by Jekyll")

    def test_aasa(self):
        aasa = json.loads((SITE / ".well-known" / "apple-app-site-association").read_text())
        details = aasa["applinks"]["details"]
        self.assertTrue(all(app_id.startswith("55A76299CP.") for d in details for app_id in d["appIDs"]))
        paths = [c["/"] for d in details for c in d["components"]]
        self.assertTrue(paths and all(p == "/app" or p.startswith("/app/") for p in paths), paths)

    def test_assetlinks_if_present(self):
        target = SITE / ".well-known" / "assetlinks.json"
        if not target.exists():
            self.skipTest("assetlinks.json not published yet")
        statements = json.loads(target.read_text())
        for s in statements:
            self.assertEqual(s["target"]["package_name"], "com.khrolovich.calorietracker")
            self.assertTrue(all(re.fullmatch(r"([0-9A-F]{2}:){31}[0-9A-F]{2}", f)
                                for f in s["target"]["sha256_cert_fingerprints"]))

    def test_app_paths_fall_back_to_landing(self):
        self.assertIn(r"/^\/app(\/|$)/.test(location.pathname)", (SITE / "404.html").read_text())
        self.assertFalse((SITE / "app").exists(), "/app/* must reach 404.html, which forwards to the landing")


if __name__ == "__main__":
    unittest.main()
