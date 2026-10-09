'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const L = require('../../assets/landing.js');

const SITE = path.join(__dirname, '..', '..');
const read = (p) => fs.readFileSync(path.join(SITE, p), 'utf8');
const html = read('i/index.html');
const unescape = (s) => s.replace(/&amp;/g, '&');

test('invite page is noindex and its store badges are storeLinks("invite")', () => {
  assert.match(html, /<meta name="robots" content="noindex">/);
  const href = (store) => unescape(new RegExp(`data-store="${store}" href="([^"]+)"`).exec(html)[1]);
  assert.equal(href('ios'), L.storeLinks('invite').ios);
  assert.equal(href('android'), L.storeLinks('invite').android);
  for (const m of html.matchAll(/\/assets\/[^"\s,]+/g)) assert.ok(fs.existsSync(path.join(SITE, m[0])), m[0]);
});

function render(search) {
  const els = {};
  const node = (name) => (els[name] ??= { hidden: true, textContent: '', href: '', addEventListener() {} });
  const invite = [node('card'), node('steps')];
  const doc = {
    querySelector: (sel) => node(sel),
    querySelectorAll: (sel) => (sel === '[data-invite]' ? invite : []),
  };
  node('[data-store="android"]').href = L.storeLinks('invite').android;
  const script = /<script>([\s\S]*?)<\/script>/.exec(html)[1];
  vm.runInNewContext(script, { document: doc, location: { search }, URLSearchParams, navigator: {}, Promise });
  return { code: node('[data-code]').textContent, shown: !invite[0].hidden, play: node('[data-store="android"]').href };
}

test('a code in ?c= is shown in two halves and handed to Play through the install referrer', () => {
  const r = render('?c=k7q2m9');
  assert.equal(r.code, 'K7Q 2M9');
  assert.ok(r.shown);
  assert.equal(r.play, L.storeLinks('invite').android + encodeURIComponent('&invite=K7Q2M9'));
});

test('a missing or malformed code shows only the badges', () => {
  for (const search of ['', '?c=', '?c=<script>', '?c=UUUUUU', '?c=K7Q2M9X']) {
    const r = render(search);
    assert.equal(r.shown, false, search);
    assert.equal(r.play, L.storeLinks('invite').android, search);
  }
});

test('404.html forwards /i/<CODE> to the invite page and still forwards /app', () => {
  const script = /<script>([\s\S]*?)<\/script>/.exec(read('404.html'))[1];
  const go = (pathname) => {
    let to = null;
    vm.runInNewContext(script, { location: { pathname, search: '', replace: (u) => { to = u; } } });
    return to;
  };
  assert.equal(go('/i/K7Q2M9'), '/i/?c=K7Q2M9');
  assert.equal(go('/i/K7Q2M9/'), '/i/?c=K7Q2M9');
  assert.equal(go('/app/scan'), '/');
  assert.equal(go('/i/'), null);
  assert.equal(go('/nope'), null);
});

test('apple-app-site-association claims /i/<CODE>, keeps /app, and leaves the web page alone', () => {
  const components = JSON.parse(read('.well-known/apple-app-site-association')).applinks.details[0].components;
  assert.deepEqual(components.map((c) => [c['/'], !!c.exclude]), [
    ['/app', false], ['/app/*', false], ['/i/', true], ['/i/*', false],
  ]);
});
