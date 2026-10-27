/* Utilidades (semana, días hábiles, cambio de hora). Funciones puras arriba (node las prueba: test_utilidades.py);
   abajo, el código de cada página, que lee su configuración de #u-data. Fechas siempre en UTC a medianoche. */
(function () {
  'use strict';
  var DAY = 864e5;

  function parse(s) { var p = s.split('-'); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])); }
  function iso(d) { return d.toISOString().slice(0, 10); }
  function add(d, n) { return new Date(d.getTime() + n * DAY); }
  function today() { var n = new Date(); return new Date(Date.UTC(n.getFullYear(), n.getMonth(), n.getDate())); }

  /* [año ISO, semana ISO 8601]: la semana 1 es la del primer jueves */
  function isoWeek(d) {
    var t = add(d, 3 - (d.getUTCDay() + 6) % 7), y = t.getUTCFullYear();
    return [y, 1 + Math.floor((t - Date.UTC(y, 0, 1)) / DAY / 7)];
  }

  var api = { parse: parse, iso: iso, add: add, isoWeek: isoWeek };
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;

  /* ------------------------------------------------------------ página */
  var doc = document, $ = function (id) { return doc.getElementById(id); };
  var el = $('u-data');
  if (!el) return;
  var C = JSON.parse(el.textContent);

  function dshort(d, withYear) {
    var w = C.wd3[(d.getUTCDay() + 6) % 7], m = C.mon3[d.getUTCMonth()], s = C.eu ? m + ' ' + d.getUTCDate() + ', ' + w : w + ' ' + d.getUTCDate() + ' ' + m;
    return withYear ? (C.eu ? d.getUTCFullYear() + ' ' + s : s + ' ' + d.getUTCFullYear()) : s;
  }
  function rng(a, b) {
    if (a.getUTCMonth() === b.getUTCMonth() && a.getUTCFullYear() === b.getUTCFullYear() && !C.eu)
      return C.wd3[(a.getUTCDay() + 6) % 7] + ' ' + a.getUTCDate() + ' – ' + dshort(b, true);
    return dshort(a, true) + ' – ' + dshort(b, true);
  }
  function plural(v, n, kw) {
    var s = n === 1 ? v.one : v.other;
    s = s.replace('{n}', n);
    for (var k in kw) s = s.replace('{' + k + '}', kw[k]);
    return s;
  }

  if (C.page === 'week') {
    var t = today(), yw = isoWeek(t), mon = add(t, -((t.getUTCDay() + 6) % 7)), y = t.getUTCFullYear();
    $('wn').textContent = yw[1];
    $('wr').textContent = rng(mon, add(mon, 6));
    $('wl').textContent = plural(C.left, Math.round((Date.UTC(y, 11, 31) - t) / DAY), { y: y });
    Array.prototype.forEach.call(doc.querySelectorAll('tr[data-w]'), function (tr) {
      tr.classList.toggle('on', tr.getAttribute('data-w') === yw[0] + '-' + yw[1]);
    });
  }
})();
