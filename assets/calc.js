(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else api.init(root.document, root);
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var ACTIVITY = [1.2, 1.375, 1.55, 1.725, 1.9];
  var CM_PER_IN = 2.54;
  var KG_PER_LB = 0.45359237;

  function parseNumber(raw) {
    var text = String(raw == null ? '' : raw).trim().replace(',', '.');
    return /^\d+(\.\d*)?$/.test(text) ? Number(text) : null;
  }

  // Same formula and limits as the app's base-burn calculator (calcaloo-app lib/widgets/passive_burn_calculator_dialog.dart).
  function bmr(sex, age, heightCm, weightKg) {
    var base = 10 * weightKg + 6.25 * heightCm - 5 * age;
    return sex === 'male' ? base + 5 : base - 161;
  }

  function toMetric(input) {
    if (input.units !== 'imperial') {
      return { heightCm: parseNumber(input.heightCm), weightKg: parseNumber(input.weightKg) };
    }
    var ft = parseNumber(input.heightFt);
    var inches = input.heightIn === '' || input.heightIn == null ? 0 : parseNumber(input.heightIn);
    var lb = parseNumber(input.weightLb);
    return {
      heightCm: ft == null || inches == null || inches >= 12 ? null : (ft * 12 + inches) * CM_PER_IN,
      weightKg: lb == null ? null : lb * KG_PER_LB
    };
  }

  function calculate(input) {
    var age = /^\s*\d+\s*$/.test(String(input.age == null ? '' : input.age)) ? Number(input.age) : null;
    var m = toMetric(input);
    var errors = [];
    if (age == null || age < 13 || age > 120) errors.push('age');
    if (m.heightCm == null || m.heightCm < 100 || m.heightCm > 250) errors.push('height');
    if (m.weightKg == null || m.weightKg < 30 || m.weightKg > 300) errors.push('weight');
    if (input.sex !== 'male' && input.sex !== 'female') errors.push('sex');
    if (errors.length) return { errors: errors };
    var exact = bmr(input.sex, age, m.heightCm, m.weightKg);
    return {
      errors: [],
      bmr: Math.round(exact),
      levels: ACTIVITY.map(function (factor) { return Math.round(exact * factor); })
    };
  }

  function init(doc, win) {
    var form = doc && doc.querySelector('[data-calc]');
    if (!form) return;
    var fmt = new win.Intl.NumberFormat(doc.documentElement.lang);
    var out = doc.querySelector('[data-calc-result]');
    var rows = doc.querySelectorAll('[data-level]');
    var activity = form.elements.activity;

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

    function render(showErrors) {
      var r = calculate({
        sex: value('sex'), age: value('age'), units: value('units'),
        heightCm: value('heightCm'), weightKg: value('weightKg'),
        heightFt: value('heightFt'), heightIn: value('heightIn'), weightLb: value('weightLb')
      });
      var fields = { age: ['age'], height: ['heightCm', 'heightFt', 'heightIn'], weight: ['weightKg', 'weightLb'] };
      Object.keys(fields).forEach(function (key) {
        var bad = r.errors.indexOf(key) >= 0;
        var note = doc.getElementById('err-' + key);
        var touched = fields[key].some(function (n) { return value(n) !== ''; });
        var shown = bad && (showErrors || touched);
        note.hidden = !shown;
        fields[key].forEach(function (n) {
          var el = form.elements[n];
          if (el) el.setAttribute('aria-invalid', shown ? 'true' : 'false');
        });
      });
      var ok = !r.errors.length;
      out.hidden = !ok;
      if (!ok) return;
      out.querySelector('[data-out="tdee"]').textContent = fmt.format(r.levels[Number(value('activity'))]);
      out.querySelector('[data-out="bmr"]').textContent = fmt.format(r.bmr);
      out.querySelector('[data-out="base"]').textContent = fmt.format(r.levels[0]);
      for (var i = 0; i < rows.length; i++) {
        var level = Number(rows[i].getAttribute('data-level'));
        rows[i].querySelector('td').textContent = fmt.format(r.levels[level]);
        rows[i].classList.toggle('is-current', String(level) === value('activity'));
      }
    }

    form.addEventListener('input', function () { syncUnits(); render(false); });
    form.addEventListener('change', function () { syncUnits(); render(false); });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      render(true);
      var invalid = form.querySelector('[aria-invalid="true"]:not(:disabled)');
      (invalid || (out.hidden ? null : out) || form.elements.sex[0]).focus();
    });
    if (activity && !activity.value) activity.value = '0';
    form.querySelector('[type="submit"]').disabled = false;
    syncUnits();
    render(false);
  }

  return { ACTIVITY: ACTIVITY, parseNumber: parseNumber, bmr: bmr, toMetric: toMetric, calculate: calculate, init: init };
});
