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

  /* días hábiles: off = { 'AAAA-MM-DD': ... } festivos; sat = el sábado es hábil. Igual que utilidades.py */
  function isOff(d, off, sat) { var w = d.getUTCDay(); return w === 0 || (w === 6 && !sat) || Object.prototype.hasOwnProperty.call(off, iso(d)); }
  /* de a a b, los dos incluidos (si a > b, se cambian) */
  function countWorkdays(a, b, off, sat) {
    if (a > b) { var x = a; a = b; b = x; }
    var n = 0;
    for (var d = a; d <= b; d = add(d, 1)) if (!isOff(d, off, sat)) n++;
    return n;
  }
  /* el n-ésimo día hábil después de a (se empieza a contar al día siguiente, Ley 39/2015 art. 30); n = 0 devuelve a */
  function addWorkdays(a, n, off, sat) {
    var d = a;
    while (n > 0) { d = add(d, 1); if (!isOff(d, off, sat)) n--; }
    return d;
  }

  var api = { parse: parse, iso: iso, add: add, isoWeek: isoWeek, isOff: isOff, countWorkdays: countWorkdays, addWorkdays: addWorkdays };
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

  if (C.page === 'dh') dh();

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function dm(d) { var n = d.getUTCDate(), m = C.mof[d.getUTCMonth()]; return C.eu ? m + ' ' + (n === 11 || n === 31 ? n : n + 'a') : n + ' ' + m; }
  function dmy(d) { return C.eu ? d.getUTCFullYear() + 'ko ' + dm(d) : dm(d) + ' de ' + d.getUTCFullYear(); }
  function byDate(x, y) { return x[0] < y[0] ? -1 : x[0] > y[0] ? 1 : 0; }

  function dh() {
    var reg = $('dreg'), mun = $('dmun'), sat = $('dsat'), mode = 'a';
    function holidays() {
      var r = reg.value, m = mun.value, list = (r ? C.reg[r] : C.nat).slice(), city = null, zone = null;
      if (r && m) {
        city = (C.cit[r] || []).filter(function (c) { return c[0] === m; })[0] || null;
        var zs = m.indexOf('z:') === 0 ? m.slice(2) : city && city[2];
        zone = (C.zon[r] || []).filter(function (z) { return z[0] === zs; })[0] || null;
      }
      if (zone) list = list.filter(function (h) { return zone[3].indexOf(h[0]) < 0; }).concat(zone[2]);
      if (city) list = list.concat(city[3].map(function (h) { return [h[0], h[1], 'l']; }));
      return { list: list.sort(byDate), city: !!city };
    }
    function fillMun() {
      var r = reg.value, zs = r ? C.zon[r] || [] : [], cs = r ? C.cit[r] || [] : [], kind = r === 'canarias' ? C.s.isla : C.s.zona;
      $('dmun-f').hidden = !zs.length && !cs.length;
      mun.innerHTML = '<option value="">' + esc(C.s.all_region) + '</option>' +
        zs.map(function (z) { return '<option value="z:' + z[0] + '">' + esc(z[1]) + ' (' + kind + ')</option>'; }).join('') +
        cs.map(function (c) { return '<option value="' + c[0] + '">' + esc(c[1]) + '</option>'; }).join('');
    }
    function val(id) {
      var v = $(id).value;
      if (!/^\d{4}-\d\d-\d\d$/.test(v)) return null;
      return parse(v < C.min ? C.min : v > C.max ? C.max : v);
    }
    function hlItem(h, multi) {
      var d = parse(h[0]), we = d.getUTCDay() % 6 === 0 ? ' we' : '';
      return '<li class="k-' + h[2] + '"><span class="d"><time datetime="' + h[0] + '">' + (multi ? dmy(d) : dm(d)) + '</time> <span class="m' + we + '">' +
        C.wd[(d.getUTCDay() + 6) % 7] + '</span></span><span class="h">' + esc(h[1]) + '</span><span class="s"><i class="sw ' + h[2] +
        '" aria-hidden="true"></i>' + C.k[h[2]] + '</span></li>';
    }
    function render() {
      var H = holidays(), off = {}, s6 = sat.value === '1', a, b, from, sub, inr;
      H.list.forEach(function (h) { if (!off[h[0]]) off[h[0]] = h; });
      var big = $('dres'), lab = $('dres-t');
      if (mode === 'a') {
        a = val('da'); b = val('db');
        if (!a || !b) return;
        if (a > b) { var x = a; a = b; b = x; }
        from = a;
        var n = countWorkdays(a, b, off, s6);
        inr = Object.keys(off).sort().filter(function (k) { return k >= iso(a) && k <= iso(b); }).map(function (k) { return off[k]; });
        var k = inr.filter(function (h) { var w = parse(h[0]).getUTCDay(); return w !== 0 && (w !== 6 || s6); }).length;
        big.textContent = n;
        lab.textContent = plural(C.s.res_a, n);
        sub = rng(a, b) + ' · ' + plural(C.s.nat_days, Math.round((b - a) / DAY) + 1) + ' · ' + plural(C.s.n_hol_in, k);
      } else {
        a = val('dc');
        var nn = Math.max(0, Math.min(999, parseInt($('dn').value, 10) || 0));
        if (!a) return;
        b = addWorkdays(a, nn, off, s6);
        from = a;
        if (iso(b) > C.max) {
          big.textContent = '–'; lab.textContent = C.s.out; $('dsub').textContent = ''; $('dhl').innerHTML = ''; $('dnone').hidden = true;
          return;
        }
        inr = Object.keys(off).sort().filter(function (k) { return k > iso(a) && k <= iso(b); }).map(function (k) { return off[k]; });
        big.textContent = b.getUTCDate();
        lab.textContent = C.eu ? b.getUTCFullYear() + 'ko ' + C.months[b.getUTCMonth()] : C.months[b.getUTCMonth()] + ' ' + b.getUTCFullYear();
        sub = C.wd[(b.getUTCDay() + 6) % 7] + ' · ' + plural(C.s.after, nn, { d: dshort(a, true) });
      }
      if (H.city && iso(from) < C.loc) sub += ' · ' + C.s.no_loc;
      $('dsub').textContent = sub;
      var multi = inr.length && inr[0][0].slice(0, 4) !== inr[inr.length - 1][0].slice(0, 4);
      $('dhl').innerHTML = inr.map(function (h) { return hlItem(h, multi); }).join('');
      $('dnone').hidden = inr.length > 0;
    }
    var t = today(), ti = iso(t);
    if (ti >= C.min && ti <= C.max) {
      $('da').value = ti; $('dc').value = ti;
      $('db').value = t.getUTCFullYear() + '-12-31';
    }
    try { var saved = localStorage.getItem('cl27.region'); if (saved && C.reg[saved]) reg.value = saved; } catch (e) { /* sin almacenamiento */ }
    fillMun();
    reg.addEventListener('change', function () { fillMun(); render(); });
    [mun, sat, $('da'), $('db'), $('dc'), $('dn')].forEach(function (x) { x.addEventListener('change', render); x.addEventListener('input', render); });
    function step(k) { var x = $('dn'); x.value = Math.max(0, Math.min(999, (parseInt(x.value, 10) || 0) + k)); render(); }
    $('dnm').addEventListener('click', function () { step(-1); });
    $('dnp').addEventListener('click', function () { step(1); });
    Array.prototype.forEach.call(doc.querySelectorAll('[data-mode]'), function (bt) {
      bt.addEventListener('click', function () {
        mode = bt.getAttribute('data-mode');
        Array.prototype.forEach.call(doc.querySelectorAll('[data-mode]'), function (o) {
          var on = o === bt; o.classList.toggle('on', on); o.setAttribute('aria-pressed', String(on));
        });
        $('dpa').hidden = mode !== 'a'; $('dpb').hidden = mode !== 'b';
        render();
      });
    });
    render();
  }
})();
