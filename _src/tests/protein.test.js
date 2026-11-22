'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { execFileSync } = require('node:child_process');
const path = require('node:path');
const P = require('../../assets/protein.js');
const L = require('../../assets/landing.js');

const SITE = path.join(__dirname, '..', '..');
const SETS = JSON.parse(execFileSync('python3', ['-c',
  'import json, sys; sys.path.insert(0, "_src"); from build import page_sets; print(json.dumps(page_sets()))'],
  { cwd: SITE, encoding: 'utf8' }));
const en = (n) => new Intl.NumberFormat('en').format(n);

test('grams = round(perKg x min(weight, 100 kg)), like the app goal', () => {
  assert.equal(P.grams(72, 1.2), 86);
  assert.equal(P.grams(72, 0.83), 60);
  assert.equal(P.grams(72, 1.2), 86);
  assert.equal(P.grams(72, 2.2), 158);
  assert.equal(P.grams(100, 1.2), 120);
  assert.equal(P.grams(130, 1.2), 120);
  assert.equal(P.grams(60, 1.2), 72);
});

test('ranges: EFSA 0.83, ISSN 2026 weight loss 1.2-1.6 and resistance training 1.6-2.2, capped at 100 kg', () => {
  const r = P.calculate({ units: 'metric', weightKg: '72' });
  assert.deepEqual(r.goals.map((g) => [g.low, g.high]), [[60, 60], [86, 115], [115, 158]]);
  assert.equal(r.capped, false);
  const heavy = P.calculate({ units: 'metric', weightKg: '130' });
  assert.deepEqual([heavy.capped, heavy.usedKg, heavy.goals[1].low, heavy.goals[1].high], [true, 100, 120, 160]);
});

test('imperial converts to kg first; comma decimals accepted', () => {
  const lb = P.calculate({ units: 'imperial', weightLb: '158.7' });
  const kg = P.calculate({ units: 'metric', weightKg: '71,98' });
  assert.deepEqual(lb.goals, kg.goals);
  assert.equal(P.calculate({ units: 'metric', weightKg: '72,5' }).errors.length, 0);
});

test('weight limits are the app limits: 30-300 kg', () => {
  const bad = (kg) => P.calculate({ units: 'metric', weightKg: kg }).errors;
  assert.deepEqual([bad('29.9'), bad('30'), bad('300'), bad('300.1'), bad(''), bad('abc')],
    [['weight'], [], [], ['weight'], ['weight'], ['weight']]);
  assert.deepEqual(P.calculate({ units: 'imperial', weightLb: '66' }).errors, ['weight']);
});

test("EN copy examples are the calculator's own numbers", () => {
  const strings = JSON.parse(fs.readFileSync(path.join(SITE, '_src/i18n/protein/en.json'), 'utf8'));
  assert.ok(strings['faq.how.a'].includes(`${P.grams(72, 0.83)} g`) && strings['faq.how.a'].includes(`${P.grams(72, 1.2)} g`) && strings['faq.how.a'].includes(`${P.grams(72, 2.2)} g`));
  assert.ok(strings['app.text'].includes(`72 kg × 1.2 g/kg = ${P.grams(72, 1.2)} g`));
  const landing = JSON.parse(fs.readFileSync(path.join(SITE, '_src/i18n/en.json'), 'utf8'));
  assert.ok(landing['protein.c1.d'].includes(`72 kg × 1.2 g/kg = ${P.grams(72, 1.2)} g`));
  assert.ok(strings['method.r0'].includes('0.83'));
  assert.ok(strings['method.r1'].includes('1.2–1.6') && strings['method.r2'].includes('1.6–2.2'));
  assert.ok(!/advisory|GLP|RDA/i.test(JSON.stringify(strings)), 'no advisory/drug/RDA wording');
  assert.equal(en(P.WEIGHT_CAP_KG), '100');
});

test('protein calculator pages: every locale, campaign links, script, sources, no placeholders', () => {
  assert.ok(SETS.protein && Object.keys(SETS.protein).length >= 9);
  for (const [lang, page] of Object.entries(SETS.protein)) {
    const html = fs.readFileSync(path.join(SITE, page, 'index.html'), 'utf8');
    const links = L.storeLinks('web-protein-' + lang.toLowerCase());
    const amp = (u) => u.replace(/&/g, '&amp;');
    assert.ok(html.includes(`data-store="ios" href="${amp(links.ios)}"`), `${page}: ios link`);
    assert.ok(html.includes(`data-store="android" href="${amp(links.android)}"`), `${page}: android link`);
    assert.ok(html.includes('src="/assets/protein.js"') && !html.includes('src="/assets/calc.js"'), page);
    assert.ok(html.includes('data-calc="protein"') && html.includes('id="err-weight"') && html.includes('data-capped'), page);
    assert.ok(html.includes('10.1080/15502783.2026.2740266') && html.includes('10.2903/j.efsa.2012.2557'), `${page}: sources`);
    assert.ok(!/\{\{|\}\}|\{n\}|None/.test(html), `${page}: unrendered placeholder`);
    for (const m of html.matchAll(/\/assets\/[^"\s,]+/g)) assert.ok(fs.existsSync(path.join(SITE, m[0])), `${page}: missing ${m[0]}`);
    for (const other of ['calculator', 'tdee', 'deficit']) assert.ok(html.includes(`href="${SETS[other][lang]}"`), `${page}: no link to ${other}`);
    const ld = JSON.parse(html.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)[1]);
    assert.deepEqual(ld['@graph'].map((e) => e['@type']), ['FAQPage', 'WebApplication']);
    assert.equal(ld['@graph'][0].mainEntity.length, 5);
  }
});

test('landing pages link the protein landing and calculator, and carry the protein FAQ in schema', () => {
  for (const [lang, page] of Object.entries(SETS.landing)) {
    const html = fs.readFileSync(path.join(SITE, page, 'index.html'), 'utf8');
    assert.ok(html.includes(`href="${SETS['protein-landing'][lang]}"`), `${page}: protein landing link`);
    if (SETS.protein[lang]) assert.ok(html.includes(`href="${SETS.protein[lang]}"`), `${page}: protein calculator link`);
    else assert.ok(!html.includes('href="undefined"') && !html.includes('href="None"'), `${page}: no calculator, no dead link`);
    const faq = JSON.parse(html.match(/<script type="application\/ld\+json">(.*?)<\/script>/s)[1])['@graph'].find((e) => e['@type'] === 'FAQPage');
    assert.equal(faq.mainEntity.length, 6, page);
    for (const q of faq.mainEntity) assert.ok(html.includes(`<summary>${q.name.replace(/&/g, '&amp;').replace(/'/g, '&#39;')}</summary>`) || html.includes(q.name), `${page}: FAQ ${q.name} not visible`);
  }
});

function stubPage() {
  const el = (attrs = {}) => ({
    attrs, hidden: false, textContent: '', value: '', disabled: false, kids: {},
    getAttribute(k) { return k in this.attrs ? this.attrs[k] : null; },
    setAttribute(k, v) { this.attrs[k] = String(v); },
    classList: { toggle() {} },
    querySelector(sel) { return this.kids[sel] || null; },
    querySelectorAll(sel) { return this.kids[sel] || []; },
    focus() {}, addEventListener(type, fn) { (this.listeners = this.listeners || {})[type] = fn; }
  });
  const kg = el({ name: 'weightKg' }), lb = el({ name: 'weightLb' });
  const form = el({ 'data-calc': 'protein' });
  form.elements = { weightKg: kg, weightLb: lb, goal: { value: '1' }, units: { value: 'metric', 0: el() } };
  const unit = (t) => { const u = el(); u.textContent = t; const g = el({ 'data-units': t === 'kg' ? 'metric' : 'imperial' }); g.kids['.unit'] = u; g.kids.input = [t === 'kg' ? kg : lb]; return g; };
  const metric = unit('kg'), imperial = unit('lb');
  form.kids['[data-units]'] = [metric, imperial];
  form.kids['[data-units="metric"] .unit'] = metric.kids['.unit'];
  form.kids['[data-units="imperial"] .unit'] = imperial.kids['.unit'];
  form.kids['[type="submit"]'] = el();
  form.querySelector = (sel) => form.kids[sel] || (sel.startsWith('[aria-invalid') ? null : null);
  const out = el();
  for (const k of ['range', 'gkg', 'weight']) out.kids[`[data-out="${k}"]`] = el();
  out.kids['[data-capped]'] = el();
  out.kids['[data-goal]'] = [0, 1, 2].map((i) => { const r = el({ 'data-goal': String(i) }); r.kids['[data-gkg]'] = el(); r.kids['[data-grams]'] = el(); return r; });
  const err = el();
  const doc = { documentElement: { lang: 'en' }, getElementById: () => err,
    querySelector: (s) => ({ '[data-calc="protein"]': form, '[data-calc-result]': out })[s] || null };
  P.init(doc, { Intl });
  return { form, out, err, set: (k, v) => { form.elements[k].value = v; form.listeners.input(); } };
}

test('runtime: result, cap note, error', () => {
  const p = stubPage();
  assert.equal(p.out.hidden, true);
  p.set('weightKg', '72');
  assert.equal(p.out.hidden, false);
  assert.equal(p.out.kids['[data-out="range"]'].textContent, '86–115');
  assert.equal(p.out.kids['[data-out="gkg"]'].textContent, '1.2–1.6');
  assert.equal(p.out.kids['[data-out="weight"]'].textContent, '72 kg');
  assert.equal(p.out.kids['[data-capped]'].hidden, true);
  assert.equal(p.out.kids['[data-goal]'][0].kids['[data-grams]'].textContent, '60');
  p.set('weightKg', '130');
  assert.equal(p.out.kids['[data-capped]'].hidden, false);
  assert.equal(p.out.kids['[data-out="weight"]'].textContent, '100 kg');
  p.set('weightKg', '20');
  assert.equal(p.out.hidden, true);
  assert.equal(p.err.hidden, false);
});
