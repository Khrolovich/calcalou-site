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

function run(channel, device, beacon) {
  const html = fs.readFileSync(path.join(SITE, 'go', channel, 'index.html'), 'utf8');
  const code = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].pop()[1];
  const replaced = [];
  const timers = [];
  const listeners = {};
  const el = { addEventListener: (type, fn) => { listeners[type] = fn; } };
  const [userAgent, platform, maxTouchPoints] = UA[device];
  vm.runInNewContext(code, {
    window: { CalcalouStores: L },
    navigator: { userAgent, platform, maxTouchPoints },
    location: { replace: (u) => replaced.push(u) },
    document: { querySelector: () => (beacon ? el : null) },
    setTimeout: (fn) => timers.push(fn),
  });
  return { replaced, timers, listeners };
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
