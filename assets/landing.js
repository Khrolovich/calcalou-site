(function (root, factory) {
  var api = factory(root);
  if (typeof module === 'object' && module.exports) module.exports = api;
  else {
    root.CalcalouStores = api;
    var script = root.document.currentScript;
    if (!script || !script.hasAttribute('data-no-init')) api.init(root.document, root);
  }
})(typeof self !== 'undefined' ? self : this, function (root) {
  'use strict';

  var APP_STORE_ID = '6757434158';
  var APP_STORE_PROVIDER = '128407090';
  var PLAY_PACKAGE = 'com.khrolovich.calorietracker';
  var DEFAULT_CAMPAIGN = 'web-site';
  var PLAY_ENABLED = true;
  var AI_HOSTS = {
    'chatgpt.com': 'chatgpt', 'chat.openai.com': 'chatgpt', 'gemini.google.com': 'gemini',
    'claude.ai': 'claude', 'perplexity.ai': 'perplexity', 'copilot.microsoft.com': 'copilot',
    'you.com': 'you', 'poe.com': 'poe', 'meta.ai': 'meta', 'deepseek.com': 'deepseek'
  };
  var AI_ASSISTANTS = ['chatgpt', 'gemini', 'claude', 'perplexity', 'copilot', 'you', 'poe', 'meta', 'deepseek'];

  function assistantName(raw) {
    var name = String(raw || '').toLowerCase();
    return AI_ASSISTANTS.indexOf(name) !== -1 ? name :
      Object.prototype.hasOwnProperty.call(AI_HOSTS, name) ? AI_HOSTS[name] : null;
  }

  function aiSource(search, referrer, pathname) {
    var params = new URLSearchParams(search || '');
    var pathSource = /^\/go\/ai-([a-z]+)\/?$/.exec(pathname || '');
    var explicit = assistantName(params.get('utm_source')) ||
      (/^\/go\/ai\/?$/.test(pathname || '') && assistantName(params.get('src'))) ||
      (/^ai_/.test(params.get('ct') || '') && assistantName(params.get('ct').slice(3))) ||
      (pathSource && assistantName(pathSource[1]));
    if (explicit) return explicit;
    try {
      var url = new URL(referrer);
      if (!/^https?:$/.test(url.protocol)) return null;
      var host = url.hostname.replace(/^www\./, '');
      if (host === 'bing.com') return /^\/(chat|copilot)(\/|$)/.test(url.pathname) ? 'copilot' : null;
      if (host === 'chat.deepseek.com') return 'deepseek';
      return Object.prototype.hasOwnProperty.call(AI_HOSTS, host) ? AI_HOSTS[host] : null;
    } catch (_) { return null; }
  }

  function sanitizeCampaign(raw, fallback) {
    fallback = fallback || DEFAULT_CAMPAIGN;
    var clean = String(raw || fallback).replace(/[^A-Za-z0-9_-]/g, '').slice(0, 40);
    return clean || fallback;
  }

  var CHANNELS = {
    web: ['calcalou.com', 'referral'],
    yt: ['youtube', 'social'],
    tt: ['tiktok', 'social'],
    ig: ['instagram', 'social'],
    fb: ['facebook', 'social'],
    reddit: ['reddit', 'social'],
    cr: ['creator', 'social'],
    links: ['linkinbio', 'social'],
    share: ['app-share', 'referral'],
    invite: ['app-invite', 'referral'],
    doctor: ['doctor', 'referral']
  };

  function channel(ct) {
    if (ct.indexOf('ai_') === 0 && assistantName(ct.slice(3))) return [ct.slice(3), 'ai_assistant'];
    var prefix = ct.split('-')[0];
    return CHANNELS[prefix] || [prefix, 'other'];
  }

  function storeLinks(ct) {
    if (root.location && root.document) {
      var ai = aiSource(root.location.search, root.document.referrer, root.location.pathname);
      if (ai) ct = 'ai_' + ai;
    }
    var utm = channel(ct);
    return {
      ios: 'https://apps.apple.com/app/apple-store/id' + APP_STORE_ID + '?pt=' + APP_STORE_PROVIDER +
        '&ct=' + encodeURIComponent(ct) + '&mt=8',
      android: 'https://play.google.com/store/apps/details?id=' + PLAY_PACKAGE + '&referrer=' +
        encodeURIComponent('utm_source=' + utm[0] + '&utm_medium=' + utm[1] + '&utm_campaign=' + ct) +
        (utm[1] === 'ai_assistant' ? '&utm_source=' + utm[0] + '&utm_medium=ai_assistant&utm_campaign=' + ct : '')
    };
  }

  function detectPlatform(ua, platform, maxTouchPoints) {
    ua = ua || '';
    if (/iPhone|iPad|iPod/.test(ua) || (platform === 'MacIntel' && maxTouchPoints > 1)) return 'ios';
    if (/Android/.test(ua)) return 'android';
    return 'other';
  }

  function wireStores(doc, links, platform) {
    var anchors = doc.querySelectorAll('[data-store]');
    for (var i = 0; i < anchors.length; i++) {
      var store = anchors[i].getAttribute('data-store');
      if (links[store]) anchors[i].href = links[store];
      if (store === 'android' && !PLAY_ENABLED) anchors[i].hidden = true;
    }
    doc.documentElement.setAttribute('data-platform', platform);
  }

  function wireStickyCta(doc, win) {
    var bar = doc.querySelector('[data-sticky-cta]');
    var hero = doc.querySelector('[data-hero-cta]');
    if (!bar || !hero || !('IntersectionObserver' in win)) return;
    new win.IntersectionObserver(function (entries) {
      bar.classList.toggle('is-visible', !entries[0].isIntersecting);
    }).observe(hero);
  }

  function init(doc, win) {
    if (!doc || !win) return;
    var params = new win.URLSearchParams(win.location.search);
    var raw = params.get('ct');
    var fallback = DEFAULT_CAMPAIGN;
    var current = doc.querySelector('[data-store="ios"]');
    if (current && current.href) {
      try { fallback = new URL(current.href).searchParams.get('ct') || fallback; } catch (_) {}
    }
    var ai = aiSource(win.location.search, doc.referrer, win.location.pathname);
    var links = storeLinks(ai ? 'ai_' + ai : sanitizeCampaign(raw, fallback));
    var nav = win.navigator || {};
    var platform = detectPlatform(nav.userAgent, nav.platform, nav.maxTouchPoints);

    var landing = /^\/(?:(?:de|es|fr|it|pl|pt-br|ru|tr)\/?)?$/.test(win.location.pathname || '/');
    if (raw && landing) {
      if (platform === 'ios') { win.location.replace(links.ios); return; }
      if (platform === 'android' && PLAY_ENABLED) { win.location.replace(links.android); return; }
    }

    wireStores(doc, links, platform);
    wireStickyCta(doc, win);
    if (ai && win.URL) {
      var internal = doc.querySelectorAll('a[href]');
      for (var i = 0; i < internal.length; i++) {
        try {
          var target = new win.URL(internal[i].href, win.location.href);
          var currentUrl = new win.URL(win.location.href);
          if (target.origin !== currentUrl.origin) continue;
          if (target.hash && target.pathname === currentUrl.pathname && target.search === currentUrl.search) continue;
          target.searchParams.set('utm_source', ai);
          internal[i].href = target.href;
        } catch (_) {}
      }
    }
  }

  return {
    sanitizeCampaign: sanitizeCampaign,
    CHANNELS: CHANNELS,
    AI_ASSISTANTS: AI_ASSISTANTS,
    aiSource: aiSource,
    storeLinks: storeLinks,
    detectPlatform: detectPlatform,
    init: init
  };
});
