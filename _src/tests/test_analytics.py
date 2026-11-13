"""The Cloudflare Web Analytics beacon: off without a token, exactly once on every built page with one.
Run: python3 -m unittest discover -s _src/tests -p 'test_*.py'"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import build  # noqa: E402

BEACON = "https://static.cloudflareinsights.com/beacon.min.js"


class Beacon(unittest.TestCase):
    def test_no_token_no_beacon(self):
        with mock.patch.object(build, "CF_BEACON_TOKEN", ""):
            pages = build.render_all()
        for target, html in pages.items():
            with self.subTest(page=str(target)):
                self.assertNotIn(BEACON, html)
                self.assertEqual(html.count("<!-- analytics -->"), 1)

    def test_token_puts_one_beacon_on_every_page(self):
        with mock.patch.object(build, "CF_BEACON_TOKEN", "0123abcd"):
            pages = build.render_all()
        self.assertGreater(len(pages), 80)
        for target, html in pages.items():
            with self.subTest(page=str(target)):
                self.assertEqual(html.count(BEACON), 1)
                self.assertIn("""data-cf-beacon='{"token": "0123abcd"}'""", html)


if __name__ == "__main__":
    unittest.main()
