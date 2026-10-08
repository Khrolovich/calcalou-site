'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const C = require('../../assets/calc.js');
const L = require('../../assets/landing.js');

const SITE = path.join(__dirname, '..', '..');
const PAGES = { en: 'bmr-calculator', de: 'de/grundumsatz-rechner', pl: 'pl/kalkulator-zapotrzebowania-kalorycznego' };

function appBaseBurn(male, age, heightCm, weightKg) {
  const bmrBase = 10 * weightKg + 6.25 * heightCm - 5 * age;
  return Math.round((male ? bmrBase + 5 : bmrBase - 161) * 1.2);
}

test('Mifflin-St Jeor reference values', () => {
  assert.equal(C.bmr('male', 30, 180, 80), 1780);
  assert.equal(C.bmr('female', 30, 165, 60), 1320.25);
  const r = C.calculate({ sex: 'male', age: '30', units: 'metric', heightCm: '180', weightKg: '80' });
  assert.deepEqual(r, { errors: [], bmr: 1780, levels: [2136, 2448, 2759, 3071, 3382] });
});

test('sedentary level equals the app base burn for the same inputs', () => {
  for (const [sex, age, h, w] of [['male', 13, 100, 30], ['female', 120, 250, 300], ['female', 41, 167.5, 63.4], ['male', 25, 172.3, 70.8]]) {
    const r = C.calculate({ sex, age: String(age), units: 'metric', heightCm: String(h), weightKg: String(w) });
    assert.equal(r.levels[0], appBaseBurn(sex === 'male', age, h, w), `${sex} ${age} ${h} ${w}`);
  }
});

test('comma decimals are accepted, like the app', () => {
  const r = C.calculate({ sex: 'female', age: '35', units: 'metric', heightCm: '170,5', weightKg: '65,2' });
  assert.equal(r.bmr, Math.round(C.bmr('female', 35, 170.5, 65.2)));
});

test('imperial converts to metric before the formula', () => {
  const m = C.toMetric({ units: 'imperial', heightFt: '5', heightIn: '11', weightLb: '176' });
  assert.ok(Math.abs(m.heightCm - 180.34) < 1e-9);
  assert.ok(Math.abs(m.weightKg - 79.83225712) < 1e-6);
  const r = C.calculate({ sex: 'male', age: '30', units: 'imperial', heightFt: '6', heightIn: '', weightLb: '160' });
  assert.equal(r.bmr, Math.round(C.bmr('male', 30, 182.88, 160 * 0.45359237)));
  assert.deepEqual(C.calculate({ sex: 'male', age: '30', units: 'imperial', heightFt: '5', heightIn: '12', weightLb: '160' }).errors, ['height']);
});

test('the app limits: age 13-120 whole years, 100-250 cm, 30-300 kg', () => {
  const ok = { sex: 'male', age: '30', units: 'metric', heightCm: '180', weightKg: '80' };
  const errors = (patch) => C.calculate({ ...ok, ...patch }).errors;
  assert.deepEqual(errors({}), []);
  for (const age of ['12', '121', '30.5', '', 'abc', '-30']) assert.deepEqual(errors({ age }), ['age'], age);
  for (const heightCm of ['99.9', '250.1', '', '1e2', '18O']) assert.deepEqual(errors({ heightCm }), ['height'], heightCm);
  for (const weightKg of ['29.9', '300.1', '', '-80']) assert.deepEqual(errors({ weightKg }), ['weight'], weightKg);
  assert.deepEqual(errors({ age: '13', heightCm: '100', weightKg: '30' }), []);
  assert.deepEqual(errors({ age: '120', heightCm: '250', weightKg: '300' }), []);
  assert.deepEqual(errors({ sex: '' }), ['sex']);
  assert.deepEqual(errors({ units: 'imperial', weightLb: '66', heightFt: '5', heightIn: '11' }), ['weight']);
  assert.deepEqual(errors({ units: 'imperial', weightLb: '67', heightFt: '3', heightIn: '3' }), ['height']);
});

test('calculator pages: store links carry ct=calc-<lang>, no landing.js, assets exist', () => {
  for (const [lang, dir] of Object.entries(PAGES)) {
    const html = fs.readFileSync(path.join(SITE, dir, 'index.html'), 'utf8');
    const links = L.storeLinks('calc-' + lang);
    const amp = (u) => u.replace(/&/g, '&amp;');
    assert.ok(html.includes(`data-store="ios" href="${amp(links.ios)}"`), `${lang}: ios link`);
    assert.ok(html.includes(`data-store="android" href="${amp(links.android)}"`), `${lang}: android link`);
    assert.ok(!html.includes('landing.js'), `${lang}: landing.js would rewrite the ct and redirect ?ct= visitors`);
    assert.ok(html.includes('src="/assets/calc.js"'));
    assert.ok(!/\{\{|\}\}/.test(html), `${lang}: unrendered placeholder`);
    for (const m of html.matchAll(/\/assets\/[^"\s,]+/g)) assert.ok(fs.existsSync(path.join(SITE, m[0])), `${lang}: missing ${m[0]}`);
    for (const id of ['err-age', 'err-height', 'err-weight']) assert.ok(html.includes(`id="${id}"`));
  }
});

test('trailing decimal separator is accepted, like Dart double.tryParse in the app', () => {
  assert.equal(C.parseNumber('180.'), 180);
  assert.equal(C.parseNumber('80,'), 80);
});
