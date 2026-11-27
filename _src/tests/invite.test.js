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
    referrer: '', documentElement: {setAttribute() {}},
    querySelector: (sel) => node(sel),
    querySelectorAll: (sel) => sel === '[data-invite]' ? invite : sel === '[data-store]' ? [
      Object.assign(node('[data-store="ios"]'), {getAttribute: () => 'ios'}),
      Object.assign(node('[data-store="android"]'), {getAttribute: () => 'android'})] : [],
  };
  node('[data-store="ios"]').href = L.storeLinks('invite').ios;
  node('[data-store="android"]').href = L.storeLinks('invite').android;
  const script = /<script>([\s\S]*?)<\/script>/.exec(html)[1];
  const location = {search, pathname: '/i/', href: 'https://calcalou.com/i/' + search,
    replace() {throw new Error('Unexpected invite-page redirect');}};
  const window = {CalcalouStores: L, URL, URLSearchParams, location, navigator: {userAgent: 'Android'}};
  vm.runInNewContext(script, { window, document: doc, location, URL, URLSearchParams, navigator: {}, Promise });
  return { code: node('[data-code]').textContent, shown: !invite[0].hidden, apple: node('[data-store="ios"]').href, play: node('[data-store="android"]').href };
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

test('AI attribution and an invite code both survive inside the Play install referrer', () => {
  const r = render('?c=k7q2m9&utm_source=claude&ct=ai_claude');
  const url = new URL(r.play);
  const referrer = new URLSearchParams(url.searchParams.get('referrer'));
  assert.equal(referrer.get('utm_source'), 'claude');
  assert.equal(referrer.get('utm_medium'), 'ai_assistant');
  assert.equal(referrer.get('utm_campaign'), 'ai_claude');
  assert.equal(referrer.get('invite'), 'K7Q2M9');
});

test('404.html forwards /i/<CODE> to the invite page and deeper /app/* to /app/', () => {
  const go = redirect;
  assert.equal(go('/i/K7Q2M9'), '/i/?c=K7Q2M9');
  assert.equal(go('/i/K7Q2M9/'), '/i/?c=K7Q2M9');
  assert.equal(go('/app/scan'), '/app/');
  assert.equal(go('/app/scan?ct=share-day-v1'), '/app/?ct=share-day-v1');
  assert.equal(go('/apple'), null);
  assert.equal(go('/i/'), null);
  assert.equal(go('/nope'), null);
});

test('apple-app-site-association claims /i/<CODE>, keeps /app, and leaves the web page alone', () => {
  const components = JSON.parse(read('.well-known/apple-app-site-association')).applinks.details[0].components;
  assert.deepEqual(components.map((c) => [c['/'], !!c.exclude]), [
    ['/app', false], ['/app/*', false], ['/i/', true], ['/i/*', false],
  ]);
});

function redirect(input) {
  const url = new URL(input, 'https://calcalou.com');
  let to = null;
  const script = /<script>([\s\S]*?)<\/script>/.exec(read('404.html'))[1];
  vm.runInNewContext(script, { URLSearchParams, location: {
    pathname: url.pathname, search: url.search, replace: (value) => { to = value; },
  } });
  return to;
}

const cases = [
  ['/i/ABC123', '/i/?c=ABC123', 'invite'],
  ['/i/ABC123?ct=share-day-v1', '/i/?c=ABC123&ct=share-day-v1', 'share-day-v1'],
  ['/i/ABC123?ct=<script>', '/i/?c=ABC123&ct=invite', 'invite'],
  ['/i/abc123?ct=share-day-v1', '/i/?c=abc123&ct=share-day-v1', 'share-day-v1'],
  ['/i/ABC123/?ct=share-day-v1', '/i/?c=ABC123&ct=share-day-v1', 'share-day-v1'],
  ['/i/ABC123?ct=share-day-v1&foo=bar&c=ZZZZZZ', '/i/?c=ABC123&ct=share-day-v1', 'share-day-v1'],
];

for (const [input, destination, campaign] of cases) {
  test(`invite campaign survives redirect and store links: ${input}`, () => {
    assert.equal(redirect(input), destination);
    const result = render(new URL(destination, 'https://calcalou.com').search);
    const apple = 'https://apps.apple.com/app/apple-store/id6757434158?pt=128407090&ct=' + campaign + '&mt=8';
    const play = 'https://play.google.com/store/apps/details?id=com.khrolovich.calorietracker&referrer=' +
      encodeURIComponent('utm_source=app-invite&utm_medium=referral&utm_campaign=' + campaign + '&invite=ABC123');
    assert.equal(result.apple, apple);
    assert.equal(result.play, play);
    assert.equal(result.code, 'ABC 123');
    assert.ok(result.shown);
    console.log(JSON.stringify({input, redirect: destination, apple: result.apple, play: result.play}));
  });
}

test('direct invite landing validates the whole campaign, including length boundaries', () => {
  for (const token of ['', '<script>', 'bad token', 'x'.repeat(41), 'trailing\n']) {
    const result = render('?c=ABC123&ct=' + encodeURIComponent(token));
    assert.equal(new URL(result.apple).searchParams.get('ct'), 'invite', JSON.stringify(token));
    const referrer = new URLSearchParams(new URL(result.play).searchParams.get('referrer'));
    assert.equal(referrer.get('utm_campaign'), 'invite');
    assert.equal(referrer.get('invite'), 'ABC123');
    assert.equal(redirect('/i/ABC123?ct=' + encodeURIComponent(token)), '/i/?c=ABC123&ct=invite');
  }
  for (const token of ['a', 'AZaz09_-', 'x'.repeat(40)]) {
    const result = render('?c=ABC123&ct=' + token);
    assert.equal(new URL(result.apple).searchParams.get('ct'), token);
    assert.equal(new URLSearchParams(new URL(result.play).searchParams.get('referrer')).get('utm_campaign'), token);
    assert.equal(redirect('/i/ABC123?ct=' + token), '/i/?c=ABC123&ct=' + token);
  }
});
