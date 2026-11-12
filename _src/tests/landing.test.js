'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const L = require('../../assets/landing.js');

const SITE = path.join(__dirname, '..', '..');
const PAGES = ['', 'de', 'es', 'fr', 'it', 'pl', 'pt-br', 'ru', 'tr'].map((p) => path.join(SITE, p, 'index.html'));

test('sanitizeCampaign keeps the previous site rules', () => {
  assert.equal(L.sanitizeCampaign(null), 'web-site');
  assert.equal(L.sanitizeCampaign('tiktok_oct-1'), 'tiktok_oct-1');
  assert.equal(L.sanitizeCampaign('a b<script>'), 'abscript');
  assert.equal(L.sanitizeCampaign('!!!'), 'web-site');
  assert.equal(L.sanitizeCampaign('x'.repeat(60)).length, 40);
  assert.equal(L.sanitizeCampaign('%%%', 'links'), 'links');
  assert.equal(L.sanitizeCampaign(null, 'links'), 'links');
});

test('storeLinks: App Store pt+ct, Play referrer utm_source/medium from the ct prefix and campaign = ct', () => {
  const links = L.storeLinks('yt-r1-ep07');
  assert.equal(links.ios, 'https://apps.apple.com/app/apple-store/id6757434158?pt=128407090&ct=yt-r1-ep07&mt=8');
  assert.equal(links.android, 'https://play.google.com/store/apps/details?id=com.khrolovich.calorietracker&referrer=' +
    encodeURIComponent('utm_source=youtube&utm_medium=social&utm_campaign=yt-r1-ep07'));
  assert.ok(L.storeLinks('web-calc-en').android.endsWith(encodeURIComponent('utm_source=calcalou.com&utm_medium=referral&utm_campaign=web-calc-en')));
  assert.ok(L.storeLinks('reels').android.endsWith(encodeURIComponent('utm_source=reels&utm_medium=other&utm_campaign=reels')));
});

test('build.py store_links mirrors storeLinks for every channel and an unknown one', () => {
  const cts = Object.keys(L.CHANNELS).map((p) => p + '-x-1').concat(['reels', 'web-site', 'invite']);
  const py = JSON.parse(execFileSync('python3', ['-c',
    'import json, sys; sys.path.insert(0, "_src"); from build import store_links; print(json.dumps([store_links(c) for c in sys.argv[1:]]))',
    ...cts], { cwd: SITE, encoding: 'utf8' }));
  assert.deepEqual(py, cts.map((ct) => L.storeLinks(ct)));
});

test('every store link on every page carries attribution', () => {
  const files = execFileSync('git', ['ls-files', '-co', '--exclude-standard', '*.html'], { cwd: SITE, encoding: 'utf8' })
    .split('\n').filter((f) => f && !f.startsWith('_src/'));
  let seen = 0;
  for (const file of files) {
    const html = fs.readFileSync(path.join(SITE, file), 'utf8');
    for (const [, raw] of html.matchAll(/<a\b[^>]*\bhref="(https:\/\/(?:apps\.apple\.com|play\.google\.com)[^"]*)"/g)) {
      seen++;
      const url = new URL(raw.replace(/&amp;/g, '&'));
      if (url.hostname === 'apps.apple.com') {
        assert.equal(url.searchParams.get('pt'), '128407090', `${file}: ${raw}`);
        assert.ok(url.searchParams.get('ct'), `${file}: ${raw}`);
      } else {
        const ref = new URLSearchParams(url.searchParams.get('referrer') || '');
        for (const k of ['utm_source', 'utm_medium', 'utm_campaign']) assert.ok(ref.get(k), `${file}: ${k} in ${raw}`);
      }
    }
  }
  assert.ok(seen > 100, `only ${seen} store links found`);
});

test('detectPlatform', () => {
  assert.equal(L.detectPlatform('Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)', 'iPhone', 5), 'ios');
  assert.equal(L.detectPlatform('Mozilla/5.0 (Macintosh)', 'MacIntel', 5), 'ios');
  assert.equal(L.detectPlatform('Mozilla/5.0 (Macintosh)', 'MacIntel', 0), 'other');
  assert.equal(L.detectPlatform('Mozilla/5.0 (Linux; Android 14)', 'Linux', 5), 'android');
  assert.equal(L.detectPlatform(undefined), 'other');
});

function runInit(search, ua) {
  const anchors = [{ getAttribute: () => 'ios' }, { getAttribute: () => 'android' }];
  let replaced = null;
  const doc = {
    documentElement: { setAttribute(k, v) { this[k] = v; } },
    querySelectorAll: () => anchors,
    querySelector: () => null
  };
  const win = { URLSearchParams, location: { search, replace: (u) => { replaced = u; } }, navigator: { userAgent: ua } };
  L.init(doc, win);
  return { anchors, replaced, platform: doc.documentElement['data-platform'] };
}

test('?ct= on iPhone and Android goes straight to the store', () => {
  assert.equal(runInit('?ct=reels', 'iPhone').replaced, L.storeLinks('reels').ios);
  assert.equal(runInit('?ct=reels', 'Android').replaced, L.storeLinks('reels').android);
});

test('?ct= on desktop stays and tags both badges', () => {
  const r = runInit('?ct=reels', 'Windows');
  assert.equal(r.replaced, null);
  assert.equal(r.anchors[0].href, L.storeLinks('reels').ios);
  assert.equal(r.anchors[1].href, L.storeLinks('reels').android);
});

test('no campaign: no redirect, default ct', () => {
  const r = runInit('', 'iPhone');
  assert.equal(r.replaced, null);
  assert.equal(r.anchors[0].href, L.storeLinks('web-site').ios);
  assert.equal(r.platform, 'ios');
});

test('generated pages are up to date with template and translations', () => {
  execFileSync('python3', [path.join(SITE, '_src', 'build.py'), '--check'], { stdio: 'pipe' });
});

test('every locale page: required links, store hooks, assets exist, approved mascot only', () => {
  const approved = /^lou-(happy|celebrating|curious|encouraging|surprised|shy)-\d+\.(webp|avif)$/;
  for (const file of PAGES) {
    const html = fs.readFileSync(file, 'utf8');
    for (const needle of ['href="/privacy/"', 'href="/support/"', 'href="/delete-account/"', 'data-store="ios"',
      'data-store="android"', 'data-hero-cta', 'data-sticky-cta', 'src="/assets/landing.js"', 'property="og:image"']) {
      assert.ok(html.includes(needle), `${file}: missing ${needle}`);
    }
    assert.ok(!/\{\{|\}\}/.test(html), `${file}: unrendered placeholder`);
    for (const m of html.matchAll(/\/assets\/[^"\s,]+/g)) {
      assert.ok(fs.existsSync(path.join(SITE, m[0])), `${file}: missing ${m[0]}`);
      const name = path.basename(m[0]);
      if (name.startsWith('lou-')) assert.match(name, approved, `${file}: unapproved mascot asset ${name}`);
    }
  }
});

test('legal and ads files are untouched', () => {
  execFileSync('git', ['--no-optional-locks', '-C', SITE, 'diff', '--quiet', 'HEAD', '--', 'privacy', 'support', 'delete-account', 'app-ads.txt', 'CNAME']);
});
