"""Smart links /go/<channel>/: one page per _src/go.json entry, noindex, attributed store links, QR, analytics.
Run: python3 -m unittest discover -s _src/tests -p 'test_*.py'"""
import json
import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent
SITE = SRC.parent
sys.path.insert(0, str(SRC))
from build import BASE, store_links  # noqa: E402

GO = json.loads((SRC / "go.json").read_text(encoding="utf-8"))


class GoLinks(unittest.TestCase):
    def test_every_channel_has_a_page(self):
        built = {p.parent.name for p in (SITE / "go").glob("*/index.html")}
        self.assertEqual(built, set(GO))

    def test_pages(self):
        sitemap = (SITE / "sitemap.xml").read_text(encoding="utf-8")
        for channel, ct in GO.items():
            with self.subTest(channel=channel):
                html = (SITE / "go" / channel / "index.html").read_text(encoding="utf-8")
                links = store_links(ct)
                self.assertIn('<meta name="robots" content="noindex">', html)
                self.assertIn(f'data-store="ios" href="{links["ios"].replace("&", "&amp;")}"', html)
                self.assertIn(f'data-store="android" href="{links["android"].replace("&", "&amp;")}"', html)
                self.assertIn(f"storeLinks({json.dumps(ct)})", html)
                self.assertLess(html.index("<!-- analytics -->"), html.index("</head>"))
                self.assertIn(f'<svg xmlns="http://www.w3.org/2000/svg" data-text="{BASE}/go/{channel}/"', html)
                self.assertTrue((SRC / "qr" / f"{channel}.svg").is_file())
                self.assertNotIn(f"{BASE}/go/", sitemap)


if __name__ == "__main__":
    unittest.main()
