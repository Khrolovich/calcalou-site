(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else api.init(root.document, root);
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var KG_PER_LB = 0.45359237;
  // g/kg: EFSA adult reference intake 0.83 (2012); ISSN 2026 position stand (Aragon et al.): 1.2-1.6 weight loss, 1.6-2.2 with resistance training.
  var GOALS = [[0.83, 0.83], [1.2, 1.6], [1.6, 2.2]];
  // calcaloo-app lib/core/goals: only the first 100 kg of body weight count toward a per-kg protein goal.
  var WEIGHT_CAP_KG = 100;

  function parseNumber(raw) {
    var text = String(raw == null ? '' : raw).trim().replace(',', '.');
    return /^\d+(\.\d*)?$/.test(text) ? Number(text) : null;
  }

  function grams(weightKg, perKg) {
    return Math.round(Math.min(weightKg, WEIGHT_CAP_KG) * perKg);
  }

  function calculate(input) {
    var kg = input.units === 'imperial'
      ? (parseNumber(input.weightLb) == null ? null : parseNumber(input.weightLb) * KG_PER_LB)
      : parseNumber(input.weightKg);
    if (kg == null || kg < 30 || kg > 300) return { errors: ['weight'] };
    return {
      errors: [],
      capped: kg > WEIGHT_CAP_KG,
      usedKg: Math.min(kg, WEIGHT_CAP_KG),
      goals: GOALS.map(function (g) { return { perKg: g, low: grams(kg, g[0]), high: grams(kg, g[1]) }; })
    };
  }

  function init(doc, win) {
    var form = doc && doc.querySelector('[data-calc="protein"]');
    if (!form) return;
    var fmt = new win.Intl.NumberFormat(doc.documentElement.lang);
    var fmt2 = new win.Intl.NumberFormat(doc.documentElement.lang, { maximumFractionDigits: 2 });
    var out = doc.querySelector('[data-calc-result]');

    function value(name) {
      var el = form.elements[name];
      return el ? el.value : '';
    }

    function syncUnits() {
      var imperial = value('units') === 'imperial';
      var groups = form.querySelectorAll('[data-units]');
      for (var i = 0; i < groups.length; i++) {
        var on = groups[i].getAttribute('data-units') === (imperial ? 'imperial' : 'metric');
        groups[i].hidden = !on;
        var inputs = groups[i].querySelectorAll('input');
        for (var j = 0; j < inputs.length; j++) inputs[j].disabled = !on;
      }
    }

    function range(a, b, f) { return a === b ? f.format(a) : f.format(a) + '–' + f.format(b); }

    function render(showErrors) {
      var r = calculate({ units: value('units'), weightKg: value('weightKg'), weightLb: value('weightLb') });
      var bad = r.errors.length > 0;
      var note = doc.getElementById('err-weight');
      var touched = value('weightKg') !== '' || value('weightLb') !== '';
      var shown = bad && (showErrors || touched);
      note.hidden = !shown;
      ['weightKg', 'weightLb'].forEach(function (n) {
        var el = form.elements[n];
        if (el) el.setAttribute('aria-invalid', shown ? 'true' : 'false');
      });
      out.hidden = bad;
      if (bad) return;
      var goal = Number(value('goal'));
      var chosen = r.goals[goal];
      out.querySelector('[data-out="range"]').textContent = range(chosen.low, chosen.high, fmt);
      out.querySelector('[data-out="gkg"]').textContent = range(chosen.perKg[0], chosen.perKg[1], fmt2);
      var imperial = value('units') === 'imperial';
      var unit = form.querySelector('[data-units="' + (imperial ? 'imperial' : 'metric') + '"] .unit').textContent;
      out.querySelector('[data-out="weight"]').textContent =
        fmt.format(Math.round((imperial ? r.usedKg / KG_PER_LB : r.usedKg) * 10) / 10) + ' ' + unit;
      out.querySelector('[data-capped]').hidden = !r.capped;
      var rows = out.querySelectorAll('[data-goal]');
      for (var i = 0; i < rows.length; i++) {
        var idx = Number(rows[i].getAttribute('data-goal'));
        rows[i].querySelector('[data-gkg]').textContent = range(r.goals[idx].perKg[0], r.goals[idx].perKg[1], fmt2);
        rows[i].querySelector('[data-grams]').textContent = range(r.goals[idx].low, r.goals[idx].high, fmt);
        rows[i].classList.toggle('is-current', idx === goal);
      }
    }

    form.addEventListener('input', function () { syncUnits(); render(false); });
    form.addEventListener('change', function () { syncUnits(); render(false); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      render(true);
      var invalid = form.querySelector('[aria-invalid="true"]:not(:disabled)');
      (invalid || (out.hidden ? null : out) || form.elements.units[0]).focus();
    });
    form.querySelector('[type="submit"]').disabled = false;
    syncUnits();
    render(false);
  }

  return { GOALS: GOALS, WEIGHT_CAP_KG: WEIGHT_CAP_KG, parseNumber: parseNumber, grams: grams, calculate: calculate, init: init };
});
