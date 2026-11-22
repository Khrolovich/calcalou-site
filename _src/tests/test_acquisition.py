import json
import re
import sys
import unittest
from html import unescape
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

SRC = Path(__file__).resolve().parent.parent
SITE = SRC.parent
sys.path.insert(0, str(SRC))
import acquisition
from locales import extra_locales
import build


class Acquisition(unittest.TestCase):
    def test_product_locales_and_visible_schema(self):
        self.assertEqual(set(acquisition.PRODUCT), {'en', 'pl', 'de', 'es', 'fr', 'it', 'pt-BR', 'ru', 'tr', 'uk'} | {m['code'] for m in extra_locales()})
        for code, t in acquisition.PRODUCT.items():
            with self.subTest(locale=code):
                html = (SITE / t['path'].strip('/') / 'index.html').read_text()
                visible = unescape(re.sub(r'<script\b.*?</script>', '', html, flags=re.S))
                raw = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
                data = json.loads(raw)
                self.assertEqual(data['@context'], 'https://schema.org')
                app, faq = data['@graph']
                self.assertEqual(app['@type'], 'MobileApplication')
                self.assertEqual(app['name'], 'Calcalou')
                self.assertEqual(app['offers']['price'], '0')
                self.assertEqual(app['offers']['priceCurrency'], 'USD')
                self.assertNotIn('aggregateRating', app)
                self.assertEqual(faq['@type'], 'FAQPage')
                self.assertEqual(faq['inLanguage'], code)
                self.assertEqual(len(faq['mainEntity']), len(t['faq']))
                for question, answer in t['faq']:
                    self.assertIn(question, visible)
                    self.assertIn(answer, visible)
                for feature in t['features']:
                    self.assertIn(feature, visible)
                self.assertIn(t['version'], visible)

    def test_comparisons_have_disclosure_and_sources(self):
        sitemap = (SITE / 'sitemap.xml').read_text()
        for path in acquisition.ENGLISH_PATHS:
            html = (SITE / path.strip('/') / 'index.html').read_text()
            self.assertIn('Written by the Calcalou Team.', html)
            self.assertIn('Official sources', html)
            self.assertIn(build.BASE + path, sitemap)
            self.assertIn('src="/assets/landing.js"', html)

    def test_every_internal_link_in_new_content_resolves(self):
        paths = [t['path'] for t in acquisition.PRODUCT.values()] + list(acquisition.ENGLISH_PATHS)
        for path in paths:
            html = (SITE / path.strip('/') / 'index.html').read_text()
            for raw in re.findall(r'(?:href|src)="([^"]+)"', html):
                url = urlparse(unescape(raw))
                if url.netloc and url.netloc != 'calcalou.com' or not url.path:
                    continue
                target = SITE / url.path.lstrip('/')
                self.assertTrue(target.is_file() or (target / 'index.html').is_file() or (target / 'index.md').is_file(), (path, raw))

    def test_llms_and_crawler_access(self):
        parser = RobotFileParser()
        parser.parse((SITE / 'robots.txt').read_text().splitlines())
        for bot in ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot',
                    'Claude-User', 'PerplexityBot', 'Perplexity-User', 'Googlebot', 'Google-Extended', 'Bingbot']:
            self.assertTrue(parser.can_fetch(bot, build.BASE + '/what-is-calcalou/'), bot)
        for name in ['llms.txt', 'llms-full.txt']:
            text = (SITE / name).read_text()
            self.assertTrue(text.startswith('# Calcalou\n'))
            self.assertIn('version 1.7', text)
            self.assertIn('Sign-in is required', text)
            self.assertNotIn('no account needed', text.lower())
            self.assertNotIn('Gemini', text)
            for t in acquisition.PRODUCT.values():
                self.assertIn(build.BASE + t['path'], text)

    def test_python_ai_campaigns_match_contract(self):
        for assistant in ['chatgpt', 'gemini', 'claude', 'perplexity', 'copilot', 'you', 'poe', 'meta', 'deepseek']:
            links = build.store_links('ai_' + assistant)
            self.assertIn('ct=ai_' + assistant, links['ios'])
            self.assertIn('utm_source%3D' + assistant + '%26utm_medium%3Dai_assistant', links['android'])

    def test_all_store_pages_load_attribution(self):
        for p in SITE.rglob('*.html'):
            if any(part.startswith(('_', '.')) for part in p.relative_to(SITE).parts):
                continue
            html = p.read_text()
            if re.search(r'<a\b[^>]*href="https://(?:apps\.apple\.com|play\.google\.com)', html):
                self.assertIn('src="/assets/landing.js"', html, str(p))
