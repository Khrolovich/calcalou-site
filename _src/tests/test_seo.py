"""SEO checks for the published files. Run: python3 -m unittest discover -s _src/tests -p 'test_*.py'"""
import json
import re
import subprocess
import sys
import shutil
import tempfile
import unittest
from html import unescape
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
SITE = SRC.parent
sys.path.insert(0, str(SRC))
from build import BASE, CALC_LOCALES, LOCALES  # noqa: E402


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


class CalculatorHead(unittest.TestCase):
    def test_canonical_hreflang_faq(self):
        expected = {code: BASE + path for code, path, _ in CALC_LOCALES} | {"x-default": BASE + CALC_LOCALES[0][1]}
        for code, path, _ in CALC_LOCALES:
            html = (SITE / path.strip("/") / "index.html").read_text(encoding="utf-8")
            self.assertEqual(re.findall(r'rel="canonical" href="([^"]+)"', html), [BASE + path])
            self.assertEqual(dict(re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', html)), expected)
            self.assertIn(f'<html lang="{code}">', html)
            raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
            faq = json.loads(raw)["@graph"][0]
            self.assertEqual(faq["@type"], "FAQPage")
            visible = re.findall(r"<summary>(.*?)</summary>", html)
            self.assertEqual([q["name"] for q in faq["mainEntity"]], [unescape(v) for v in visible])

    def test_in_sitemap_with_alternates(self):
        sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
        for _, path, _ in CALC_LOCALES:
            self.assertIn(f"<loc>{BASE}{path}</loc>", sitemap)
            self.assertIn(f'hreflang="x-default" href="{BASE}{CALC_LOCALES[0][1]}"', sitemap)


class LocaleCoverage(unittest.TestCase):
    def test_every_page_set_in_every_locale(self):
        import check_locales
        self.assertEqual(check_locales.check(), [])

    def broken(self, rel, old, new, last=False):
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(SITE, tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "img"))
            target = Path(tmp) / rel
            if old is None:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(new, encoding="utf-8")
            else:
                html = target.read_text(encoding="utf-8")
                self.assertIn(old, html)
                at = html.rfind(old) if last else html.find(old)
                target.write_text(html[:at] + new + html[at + len(old):], encoding="utf-8")
            result = subprocess.run([sys.executable, str(Path(tmp) / "_src" / "check_locales.py")],
                                    capture_output=True, text=True)
            return result.returncode, result.stderr

    def test_breakages_are_caught(self):
        es = "es/calculadora-de-calorias/index.html"
        es_link = '<a href="/es/calculadora-de-calorias/" hreflang="es" lang="es"'
        cases = [
            (es, '<html lang="es">', '<html lang="en"><!-- <html lang="es"> -->'),
            (es, '<link rel="alternate" hreflang="fr" href="', '<!-- <link rel="alternate" hreflang="fr" href="'),
            (es, '<li>' + es_link, '<li><a href="/" hreflang="es" lang="es"></a>' + es_link),
            ("sitemap.xml", "<loc>https://calcalou.com/es/calculadora-de-calorias/</loc>",
             "<!-- <loc>https://calcalou.com/es/calculadora-de-calorias/</loc> --><loc>x</loc>"),
            ("es/articulo.html", None, "<html lang=es></html>"),
            ("de/neu/index.html", None, "<html lang=de></html>"),
        ]
        for rel, old, new in cases:
            with self.subTest(rel=rel, new=new[:40]):
                code, _ = self.broken(rel, old, new)
                self.assertEqual(code, 1)

    def test_footer_switcher_is_checked(self):
        es_footer = '<li><a href="/es/calculadora-de-calorias/" hreflang="es" lang="es" aria-current="page">'
        code, err = self.broken("es/calculadora-de-calorias/index.html", es_footer,
                                '<li><a href="/es/" hreflang="es" lang="es" aria-current="page">', last=True)
        self.assertEqual(code, 1)
        self.assertIn("footer language switcher", err)

    def test_a_missing_locale_fails(self):
        import check_locales
        original = check_locales.page_sets
        check_locales.page_sets = lambda: {**original(), "calculator": {"en": "/bmr-calculator/"}}
        try:
            self.assertTrue(any("site locales" in e for e in check_locales.check()))
        finally:
            check_locales.page_sets = original


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
