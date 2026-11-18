'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const L = require('../../assets/landing.js');
const fs = require('node:fs');
const vm = require('node:vm');

test('AI referrers match hosts, and Bing chat requires a chat path', () => {
  for (const [url, source] of [
    ['https://chatgpt.com/c/123', 'chatgpt'], ['https://chat.openai.com/', 'chatgpt'],
    ['https://gemini.google.com/', 'gemini'], ['https://claude.ai/', 'claude'],
    ['https://www.perplexity.ai/', 'perplexity'], ['https://copilot.microsoft.com/', 'copilot'],
    ['https://www.bing.com/chat', 'copilot'], ['https://you.com/', 'you'],
    ['https://poe.com/', 'poe'], ['https://www.meta.ai/', 'meta'],
    ['https://chat.deepseek.com/', 'deepseek']
  ]) assert.equal(L.aiSource('', url, '/'), source, url);
  for (const url of ['', 'broken', 'https://bing.com/search?q=food', 'https://bing.com/',
    'https://chatgpt.com.evil.test/', 'https://evil.test/?chatgpt.com']) {
    assert.equal(L.aiSource('', url, '/'), null, url);
  }
});

test('explicit AI UTM wins; src is scoped to AI smart links; unknown values cannot become campaigns', () => {
  assert.equal(L.aiSource('?utm_source=chatgpt.com', 'https://claude.ai/', '/'), 'chatgpt');
  assert.equal(L.aiSource('?src=gemini', '', '/go/ai/'), 'gemini');
  assert.equal(L.aiSource('?src=gemini', '', '/go/ai'), 'gemini');
  assert.equal(L.aiSource('?src=gemini', '', '/'), null);
  assert.equal(L.aiSource('?ct=claude', '', '/'), null);
  assert.equal(L.aiSource('?src=private-email@example.com', '', '/go/ai/'), null);
  assert.equal(L.aiSource('?ct=ai_perplexity', '', '/'), 'perplexity');
  assert.equal(L.aiSource('', '', '/go/ai-copilot/'), 'copilot');
  assert.equal(L.aiSource('', '', '/go/ai-fake/'), null);
  for (const name of ['constructor', '__proto__', 'toString']) {
    assert.equal(L.aiSource('?utm_source=' + name, '', '/'), null);
    assert.equal(L.aiSource('?src=' + name, '', '/go/ai/'), null);
    assert.equal(L.aiSource('', 'https://' + name.toLowerCase() + '/', '/'), null);
  }
});

test('every assistant has matching Apple campaign and Play install UTM', () => {
  for (const assistant of L.AI_ASSISTANTS) {
    const links = L.storeLinks('ai_' + assistant);
    const ios = new URL(links.ios), play = new URL(links.android);
    assert.equal(ios.searchParams.get('ct'), 'ai_' + assistant);
    assert.equal(ios.searchParams.get('pt'), '128407090');
    const utm = new URLSearchParams(play.searchParams.get('referrer'));
    assert.equal(utm.get('utm_source'), assistant);
    assert.equal(utm.get('utm_medium'), 'ai_assistant');
    assert.equal(utm.get('utm_campaign'), 'ai_' + assistant);
    assert.equal(play.searchParams.get('utm_source'), assistant);
  }
});

test('AI visit rewrites stores and internal navigation without redirecting the article or using storage', () => {
  let redirects = 0;
  const stores = [{getAttribute: () => 'ios'}, {getAttribute: () => 'android'}];
  const internal = [{href: 'https://calcalou.com/what-is-calcalou/?x=1#faq'},
    {href: 'https://example.com/'}, {href: 'mailto:support@calcalou.com'},
    {href: 'https://calcalou.com/best-protein-tracker/#faq'}];
  const doc = {referrer: 'https://claude.ai/', documentElement: {setAttribute() {}},
    querySelectorAll: (selector) => selector === '[data-store]' ? stores : internal,
    querySelector: () => null};
  const win = {URLSearchParams, URL, location: {href: 'https://calcalou.com/best-protein-tracker/',
    search: '', pathname: '/best-protein-tracker/', replace() { redirects++; }},
    navigator: {userAgent: 'iPhone'}};
  L.init(doc, win);
  assert.equal(redirects, 0);
  assert.equal(new URL(stores[0].href).searchParams.get('ct'), 'ai_claude');
  assert.equal(new URL(internal[0].href).searchParams.get('utm_source'), 'claude');
  assert.equal(new URL(internal[0].href).searchParams.get('x'), '1');
  assert.equal(new URL(internal[0].href).hash, '#faq');
  assert.equal(internal[1].href, 'https://example.com/');
  assert.equal(internal[2].href, 'mailto:support@calcalou.com');
  assert.equal(internal[3].href, 'https://calcalou.com/best-protein-tracker/#faq');
  win.location.search = '?ct=ai_claude';
  L.init(doc, win);
  assert.equal(redirects, 0);
});

test('ordinary calculator and food visits preserve the page campaign', () => {
  const stores = [{href: L.storeLinks('web-food-egg-pl').ios, getAttribute: () => 'ios'}, {getAttribute: () => 'android'}];
  const doc = {querySelectorAll: () => stores, querySelector: (sel) => sel === '[data-store="ios"]' ? stores[0] : null,
    documentElement: {setAttribute() {}}};
  L.init(doc, {URLSearchParams, location: {search: ''}, navigator: {}});
  assert.equal(stores[0].href, L.storeLinks('web-food-egg-pl').ios);
});

test('browser storeLinks also attributes callers using data-no-init', () => {
  const root = {location: {search: '?src=perplexity', pathname: '/go/ai/'},
    document: {referrer: '', currentScript: {hasAttribute: () => true}}};
  vm.runInNewContext(fs.readFileSync(require.resolve('../../assets/landing.js'), 'utf8'), {self: root, URL, URLSearchParams});
  assert.equal(new URL(root.CalcalouStores.storeLinks('web-go').ios).searchParams.get('ct'), 'ai_perplexity');
});
