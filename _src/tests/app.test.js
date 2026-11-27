'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const L = require('../../assets/landing.js');

const SITE = path.join(__dirname, '..', '..');
const html = fs.readFileSync(path.join(SITE, 'app', 'index.html'), 'utf8');
const UA = {
  iphone: ['Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)', 'iPhone', 5],
  ipad: ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'MacIntel', 5],
  android: ['Mozilla/5.0 (Linux; Android 14)', 'Linux', 5],
  desktop: ['Mozilla/5.0 (Macintosh)', 'MacIntel', 0],
};

function run(device, search) {
  const code = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];
  const replaced = [];
  const [userAgent, platform, maxTouchPoints] = UA[device];
  const location = {search, pathname: '/app/', href: 'https://calcalou.com/app/' + search, replace: (u) => replaced.push(u)};
  const navigator = {userAgent, platform, maxTouchPoints};
  const anchors = ['ios', 'android'].map((store) => ({href: L.storeLinks('web-app')[store], getAttribute: () => store}));
  const document = {referrer: '', documentElement: {setAttribute() {}}, querySelectorAll: (sel) => sel === '[data-store]' ? anchors : [],
    querySelector: (sel) => sel === '[data-store="ios"]' ? anchors[0] : null};
  vm.runInNewContext(code, {window: {CalcalouStores: L, URL, URLSearchParams, location, navigator},
    navigator, location, document, URLSearchParams, setTimeout() {}});
  return {replaced, badges: anchors.map((a) => a.href)};
}

test('/app/ is a noindex page with a link preview and real assets', () => {
  assert.match(html, /<meta name="robots" content="noindex">/);
  assert.match(html, /<meta property="og:image" content="https:\/\/calcalou.com\/assets\/img\/og.jpg">/);
  assert.doesNotMatch(html, /not found/i);
  for (const m of html.matchAll(/(?:src|href)="(\/assets\/[^"' ]+)"/g)) assert.ok(fs.existsSync(path.join(SITE, m[1])), m[1]);
});

test('phones go to their store with the link ct (Apple ct+pt, Play utm_campaign)', () => {
  const ios = run('iphone', '?ct=share-ach').replaced;
  assert.deepEqual(ios, [L.storeLinks('share-ach').ios]);
  assert.match(ios[0], /[?&]pt=128407090&ct=share-ach&/);
  assert.deepEqual(run('ipad', '?ct=iae-weekly').replaced, [L.storeLinks('iae-weekly').ios]);
  const play = run('android', '?ct=share-ach').replaced;
  assert.deepEqual(play, [L.storeLinks('share-ach').android]);
  assert.match(decodeURIComponent(play[0]), /utm_campaign=share-ach/);
});

test('no or unsafe ct falls back to web-app; desktop stays on the badges', () => {
  assert.deepEqual(run('iphone', '').replaced, [L.storeLinks('web-app').ios]);
  assert.deepEqual(run('android', '?ct=%3Cx%3E').replaced, [L.storeLinks('x').android]);
  const desk = run('desktop', '?ct=share-ach');
  assert.deepEqual(desk.replaced, []);
  assert.deepEqual(desk.badges, [L.storeLinks('share-ach').ios, L.storeLinks('share-ach').android]);
});
