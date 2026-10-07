(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else api.init(root.document, root);
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var APP_STORE_ID = '6757434158';
  var APP_STORE_PROVIDER = '128407090';
  var PLAY_PACKAGE = 'com.khrolovich.calorietracker';
  var DEFAULT_CAMPAIGN = 'web-site';
  var PLAY_ENABLED = true;

  function sanitizeCampaign(raw) {
    var clean = String(raw || DEFAULT_CAMPAIGN).replace(/[^A-Za-z0-9_-]/g, '').slice(0, 40);
    return clean || DEFAULT_CAMPAIGN;
  }

  function storeLinks(ct) {
    return {
      ios: 'https://apps.apple.com/app/apple-store/id' + APP_STORE_ID + '?pt=' + APP_STORE_PROVIDER +
        '&ct=' + encodeURIComponent(ct) + '&mt=8',
      android: 'https://play.google.com/store/apps/details?id=' + PLAY_PACKAGE + '&referrer=' +
        encodeURIComponent('utm_source=' + ct + '&utm_medium=social&utm_campaign=launch')
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
    var links = storeLinks(sanitizeCampaign(raw));
    var nav = win.navigator || {};
    var platform = detectPlatform(nav.userAgent, nav.platform, nav.maxTouchPoints);

    if (raw) {
      if (platform === 'ios') { win.location.replace(links.ios); return; }
      if (platform === 'android' && PLAY_ENABLED) { win.location.replace(links.android); return; }
    }

    wireStores(doc, links, platform);
    wireStickyCta(doc, win);
  }

  return {
    sanitizeCampaign: sanitizeCampaign,
    storeLinks: storeLinks,
    detectPlatform: detectPlatform,
    init: init
  };
});
