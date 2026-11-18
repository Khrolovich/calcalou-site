'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const L = require('../../assets/landing.js');

const SITE = path.join(__dirname, '..', '..');
const GO = JSON.parse(fs.readFileSync(path.join(SITE, '_src', 'go.json'), 'utf8'));
const UA = {
  iphone: ['Mozilla/5.0 (iPhone; CPU iPhone OS 18_0)', 'iPhone', 5],
  android: ['Mozilla/5.0 (Linux; Android 14)', 'Linux', 5],
  desktop: ['Mozilla/5.0 (Macintosh)', 'MacIntel', 0],
};

function run(channel, device, beacon, search = '') {
  const html = fs.readFileSync(path.join(SITE, 'go', channel, 'index.html'), 'utf8');
  const code = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];
  const replaced = [];
  const timers = [];
  const listeners = {};
  const el = { addEventListener: (type, fn) => { listeners[type] = fn; } };
  const [userAgent, platform, maxTouchPoints] = UA[device];
  const location = {search, pathname: '/go/' + channel + '/', href: 'https://calcalou.com/go/' + channel + '/' + search,
    replace: (u) => replaced.push(u)};
  const navigator = {userAgent, platform, maxTouchPoints};
  const anchors = ['ios', 'android'].map((store) => ({href: L.storeLinks(GO[channel])[store], getAttribute: () => store}));
  const qr = {};
  const document = {referrer: '', documentElement: {setAttribute() {}}, querySelectorAll: (sel) => sel === '[data-store]' ? anchors : [],
    querySelector: (sel) => sel === '[data-store="ios"]' ? anchors[0] : sel === '.qr' ? qr : sel === 'script[data-cf-beacon]' && beacon ? el : null};
  vm.runInNewContext(code, {
    window: {CalcalouStores: L, URL, URLSearchParams, location, navigator},
    navigator, location, document,
    setTimeout: (fn) => timers.push(fn),
  });
  return { replaced, timers, listeners, anchors, qr };
}

test('go pages send phones to their store with the channel ct, desktop stays', () => {
  for (const [channel, ct] of Object.entries(GO)) {
    assert.deepEqual(run(channel, 'iphone', false).replaced, [L.storeLinks(ct).ios], channel);
    assert.deepEqual(run(channel, 'android', false).replaced, [L.storeLinks(ct).android], channel);
    const desk = run(channel, 'desktop', true);
    assert.deepEqual([desk.replaced, desk.timers.length], [[], 0], channel);
  }
});

test('with the beacon, the redirect waits for it once, with a timeout fallback', () => {
  const [channel, ct] = Object.entries(GO)[0];
  const r = run(channel, 'iphone', true);
  assert.deepEqual(r.replaced, []);
  r.listeners.load();
  r.timers.forEach((fn) => fn());
  r.listeners.error();
  assert.deepEqual(r.replaced, [L.storeLinks(ct).ios]);
});

test('generic AI smart links preserve the chosen assistant in redirect, badges and desktop QR', () => {
  const phone = run('ai', 'android', false, '?src=claude');
  assert.deepEqual(phone.replaced, [L.storeLinks('ai_claude').android]);
  const desk = run('ai', 'desktop', false, '?src=claude');
  assert.equal(desk.anchors[0].href, L.storeLinks('ai_claude').ios);
  assert.match(desk.qr.innerHTML, /ai-claude\.svg/);
});
