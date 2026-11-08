'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const C = require('../../assets/calc.js');
const L = require('../../assets/landing.js');

const SITE = path.join(__dirname, '..', '..');
const SETS = JSON.parse(execFileSync('python3', ['-c',
  'import json, sys; sys.path.insert(0, "_src"); from build import page_sets; print(json.dumps(page_sets()))'],
  { cwd: SITE, encoding: 'utf8' }));
const CT = { calculator: 'calc', tdee: 'calc-tdee', deficit: 'calc-deficit' };

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

test('calculator pages: store links carry the set ct + lang, no landing.js, assets exist', () => {
  assert.deepEqual(Object.keys(CT), Object.keys(SETS).filter((name) => name !== 'landing'));
  for (const [name, prefix] of Object.entries(CT)) {
    for (const [lang, page] of Object.entries(SETS[name])) {
      const html = fs.readFileSync(path.join(SITE, page, 'index.html'), 'utf8');
      const links = L.storeLinks(prefix + '-' + lang.toLowerCase());
      const amp = (u) => u.replace(/&/g, '&amp;');
      assert.ok(html.includes(`data-store="ios" href="${amp(links.ios)}"`), `${page}: ios link`);
      assert.ok(html.includes(`data-store="android" href="${amp(links.android)}"`), `${page}: android link`);
      assert.ok(!html.includes('landing.js'), `${page}: landing.js would rewrite the ct and redirect ?ct= visitors`);
      assert.ok(html.includes('src="/assets/calc.js"'));
      assert.ok(!/\{\{|\}\}|\{n\}/.test(html), `${page}: unrendered placeholder`);
      for (const m of html.matchAll(/\/assets\/[^"\s,]+/g)) assert.ok(fs.existsSync(path.join(SITE, m[0])), `${page}: missing ${m[0]}`);
      for (const id of ['err-age', 'err-height', 'err-weight']) assert.ok(html.includes(`id="${id}"`));
      for (const other of Object.keys(CT).filter((o) => o !== name)) {
        assert.ok(html.includes(`href="${SETS[other][lang]}"`), `${page}: no link to the ${other} calculator`);
      }
      if (name === 'deficit') {
        for (const d of C.DEFICITS) assert.ok(html.includes(`data-deficit="${d}"`), `${page}: row ${d}`);
        assert.ok(html.includes('data-floor hidden'), `${page}: floor warning`);
      }
    }
  }
});

test('deficit plan: the app limits (goal_limits.dart: 1,000 kcal max deficit, 1,200 kcal floor)', () => {
  assert.equal(C.MAX_DEFICIT, 1000);
  assert.equal(C.MIN_INTAKE, 1200);
  assert.deepEqual(C.DEFICITS, [250, 500, 750, 1000]);
  assert.deepEqual(C.deficitPlan(2400, 500), { deficit: 500, intake: 1900, belowFloor: false });
  assert.deepEqual(C.deficitPlan(2200, 1000), { deficit: 1000, intake: 1200, belowFloor: false });
  assert.deepEqual(C.deficitPlan(2199, 1000), { deficit: 1000, intake: 1199, belowFloor: true });
  assert.deepEqual(C.deficitPlan(2400, 1500), { deficit: 1000, intake: 1400, belowFloor: false });
  assert.deepEqual(C.deficitPlan(600, 1000), { deficit: 600, intake: 0, belowFloor: true });
  const r = C.calculate({ sex: 'male', age: '30', units: 'metric', heightCm: '180', weightKg: '80' }, 18);
  assert.equal(C.deficitPlan(r.levels[2], 500).intake, 2759 - 500);
});

test('deficit mode is for adults: minimum age 18, BMR and TDEE keep 13', () => {
  const input = { sex: 'female', age: '17', units: 'metric', heightCm: '165', weightKg: '60' };
  assert.deepEqual(C.calculate(input, 18).errors, ['age']);
  assert.deepEqual(C.calculate(input).errors, []);
  assert.deepEqual(C.calculate({ ...input, age: '18' }, 18).errors, []);
});

test('trailing decimal separator is accepted, like Dart double.tryParse in the app', () => {
  assert.equal(C.parseNumber('180.'), 180);
  assert.equal(C.parseNumber('80,'), 80);
});

function stubPage(mode) {
  const el = (attrs = {}) => {
    const kids = {};
    return {
      attrs, hidden: false, textContent: '', value: '', disabled: false, focused: false, classes: new Set(), kids,
      getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; },
      setAttribute(k, v) { this.attrs[k] = String(v); },
      classList: { toggle() {} },
      querySelector(sel) { return kids[sel] || null; },
      querySelectorAll(sel) { return kids[sel] || []; },
      focus() { page.focused = this; },
      addEventListener(type, fn) { (this.listeners = this.listeners || {})[type] = fn; }
    };
  };
  const page = { focused: null };
  const names = ['age', 'heightCm', 'weightKg', 'heightFt', 'heightIn', 'weightLb'];
  const inputs = Object.fromEntries(names.map((n) => [n, el({ name: n })]));
  const form = el({ 'data-calc': mode });
  form.elements = { ...inputs, sex: { value: 'female', 0: el() }, units: { value: 'metric' }, activity: el(), deficit: el() };
  form.elements.activity.value = '0';
  form.elements.deficit.value = '500';
  const metric = el({ 'data-units': 'metric' }); metric.kids.input = [inputs.heightCm, inputs.weightKg];
  const imperial = el({ 'data-units': 'imperial' }); imperial.kids.input = [inputs.heightFt, inputs.heightIn, inputs.weightLb];
  form.kids['[data-units]'] = [metric, imperial];
  form.kids['[type="submit"]'] = el();
  form.querySelector = (sel) => sel.startsWith('[aria-invalid')
    ? names.map((n) => inputs[n]).find((i) => i.attrs['aria-invalid'] === 'true' && !i.disabled) || null
    : form.kids[sel] || null;
  const out = el();
  for (const k of ['tdee', 'bmr', 'base', 'intake', 'deficit']) out.kids[`[data-out="${k}"]`] = el();
  out.kids['[data-floor]'] = el();
  const rows = C.DEFICITS.map((d) => { const r = el({ 'data-deficit': String(d) }); r.kids['[data-intake]'] = el(); r.kids['[data-under]'] = el(); return r; });
  const errs = Object.fromEntries(['age', 'height', 'weight'].map((k) => [`err-${k}`, el()]));
  const doc = {
    documentElement: { lang: 'en' },
    getElementById: (id) => errs[id],
    querySelector: (sel) => ({ '[data-calc]': form, '[data-calc-result]': out })[sel] || null,
    querySelectorAll: (sel) => (sel === '[data-deficit]' ? rows : [])
  };
  C.init(doc, { Intl });
  const set = (values) => { for (const [k, v] of Object.entries(values)) (form.elements[k] || inputs[k]).value = v; };
  const submit = () => form.listeners.submit({ preventDefault() {} });
  return { form, out, rows, errs, set, submit, page };
}

test('runtime: deficit page rejects age 17, accepts 18; TDEE page accepts 17', () => {
  const p = stubPage('deficit');
  p.set({ age: '17', heightCm: '165', weightKg: '60' });
  p.submit();
  assert.equal(p.errs['err-age'].hidden, false);
  assert.equal(p.out.hidden, true);
  assert.equal(p.page.focused.attrs.name, 'age');
  p.set({ age: '18' });
  p.submit();
  assert.equal(p.errs['err-age'].hidden, true);
  assert.equal(p.out.hidden, false);
  assert.equal(p.page.focused, p.out);
  const t = stubPage('tdee');
  t.set({ age: '17', heightCm: '165', weightKg: '60' });
  t.submit();
  assert.equal(t.out.hidden, false);
});

test('runtime: floor warning and under-1,200 rows follow the chosen deficit', () => {
  const p = stubPage('deficit');
  p.set({ age: '30', heightCm: '165', weightKg: '60', activity: '0', deficit: '250' });
  p.submit();
  const tdee = Math.round(C.bmr('female', 30, 165, 60) * 1.2);
  assert.equal(p.out.kids['[data-out="intake"]'].textContent, new Intl.NumberFormat('en').format(tdee - 250));
  assert.equal(p.out.kids['[data-floor]'].hidden, tdee - 250 >= 1200);
  p.set({ deficit: '1000' });
  p.form.listeners.change();
  assert.equal(p.out.kids['[data-floor]'].hidden, false);
  assert.deepEqual(p.rows.map((r) => r.kids['[data-under]'].hidden), C.DEFICITS.map((d) => tdee - d >= 1200));
});

test('runtime: a deficit larger than TDEE is shown as the real difference, never a negative intake', () => {
  const p = stubPage('deficit');
  p.set({ age: '80', heightCm: '145', weightKg: '40', activity: '0', deficit: '1000' });
  p.submit();
  const tdee = Math.round(C.bmr('female', 80, 145, 40) * 1.2);
  assert.ok(tdee < 1000);
  assert.equal(p.out.kids['[data-out="intake"]'].textContent, '0');
  assert.equal(p.out.kids['[data-out="deficit"]'].textContent, new Intl.NumberFormat('en').format(tdee));
});
