/* Calendario laboral 2027 - app. Datos: BOE-A-2026-21254 (embebidos en la página). */
(function () {
  'use strict';
  var doc = document, html = doc.documentElement;
  html.classList.add('js');
  var $ = function (id) { return doc.getElementById(id); };
  var all = function (sel, root) { return Array.prototype.slice.call((root || doc).querySelectorAll(sel)); };

  /* ------------------------------------------------------------ menús (details) y menú móvil */
  var dds = all('details.dd');
  dds.forEach(function (d) {
    d.addEventListener('toggle', function () { if (d.open) dds.forEach(function (o) { if (o !== d) o.open = false; }); });
  });
  doc.addEventListener('click', function (e) { dds.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; }); });
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    dds.forEach(function (d) { if (d.open) { d.open = false; d.querySelector('summary').focus(); } });
  });
  all('.menu-cal a').forEach(function (a) { a.addEventListener('click', function () { var d = a.closest('details'); if (d) d.open = false; }); });
  var burger = $('burger');
  if (burger) burger.addEventListener('click', function () {
    var on = burger.getAttribute('aria-expanded') !== 'true';
    burger.setAttribute('aria-expanded', String(on));
    doc.body.classList.toggle('nav-open', on);
  });
  all('[data-print]').forEach(function (b) { b.addEventListener('click', function () { window.print(); }); });

  if (!$('cal-data')) return;
  var D = JSON.parse($('cal-data').textContent);
  var T = JSON.parse($('cal-i18n').textContent);
  var Y = D.year, N = 365, BASE = html.getAttribute('data-base') || '/';
  var ASSETS = html.getAttribute('data-assets') || BASE;
  var HOST = location.host || 'elcalendariolaboral.es';
  var PAGE = doc.body.getAttribute('data-region') || '';
  var CITY = doc.body.getAttribute('data-city') || '', CITYNAME = doc.body.getAttribute('data-cityname') || '';
  var FIX = CITY ? JSON.parse(doc.body.getAttribute('data-locals') || '[]') : null, FZONE = doc.body.getAttribute('data-zone') || null;
  var f = function (s, o) { return s.replace(/\{(\w+)\}/g, function (m, k) { return o[k] != null ? o[k] : m; }); };
  var tn = function (k, n) { var v = T[k]; return f(typeof v === 'string' ? v : (n === 1 ? v.one : v.other), { n: n }); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  /* fechas: lunes = 0 */
  var ISO = [], WD = [], MON = [], DOM = [];
  for (var i = 0; i < N; i++) {
    var dd = new Date(Date.UTC(Y, 0, 1 + i));
    ISO.push(dd.toISOString().slice(0, 10)); WD.push((dd.getUTCDay() + 6) % 7); MON.push(dd.getUTCMonth()); DOM.push(dd.getUTCDate());
  }
  var IDX = {}; ISO.forEach(function (s, k) { IDX[s] = k; });
  var weekend = function (i) { return WD[i] >= 5; };
  /* mismos formatos que build.py: dm, dlong, dshort, drange, dlist */
  function da(n) { return n === 11 || n === 31 ? String(n) : n + 'a'; }
  function dm(i) { return T.eu ? T.mof[MON[i]] + ' ' + da(DOM[i]) : DOM[i] + ' ' + T.mof[MON[i]]; }
  function dlong(i) { return T.eu ? dm(i) + ', ' + T.wd[WD[i]] : T.wd[WD[i]] + ' ' + dm(i); }
  function dshort(i) { return T.eu ? T.mon3[MON[i]] + ' ' + DOM[i] + ', ' + T.wd3[WD[i]] : T.wd3[WD[i]] + ' ' + DOM[i] + ' ' + T.mon3[MON[i]]; }
  function drange(a, b) { return MON[a] === MON[b] && !T.eu ? T.wd3[WD[a]] + ' ' + DOM[a] + ' – ' + dshort(b) : dshort(a) + ' – ' + dshort(b); }
  function dlist(x) {
    if (x.length === 2 && MON[x[0]] === MON[x[1]] && !T.eu) return T.wd3[WD[x[0]]] + ' ' + DOM[x[0]] + ', ' + dshort(x[1]);
    return x.map(dshort).join(', ');
  }

  function get(k) { try { return localStorage.getItem('cl27.' + k); } catch (e) { return null; } }
  function put(k, v) { try { if (v == null) localStorage.removeItem('cl27.' + k); else localStorage.setItem('cl27.' + k, v); } catch (e) { /* sin almacenamiento */ } }

  var S = { region: PAGE || null, zone: null, locals: [], lnames: [], n: 4, vac: {}, vmode: false };

  /* ------------------------------------------------------------ datos */
  function holidays() {
    var out = [];
    D.holidays.forEach(function (h) {
      var a = h.regions === 'all';
      if (a || (S.region && h.regions.indexOf(S.region) >= 0)) out.push({ date: h.date, name: h.name, kind: a ? 'n' : 'r' });
    });
    var z = S.region && D.zones[S.region];
    if (z && S.zone) {
      var o = z.options.filter(function (x) { return x.slug === S.zone; })[0];
      if (o && o.remove) out = out.filter(function (h) { return h.date !== o.remove; });
      if (o && o.add) out.push({ date: o.add.date, name: o.add.name, kind: 'r' });
    }
    S.locals.forEach(function (d, k) {
      if (d && IDX[d] != null && !out.some(function (h) { return h.date === d; })) out.push({ date: d, name: S.lnames[k] || T.local_holiday, kind: 'l', k: k });
    });
    out.sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
    return out;
  }
  function offDays(hols, withVac) {
    var hd = {}; hols.forEach(function (h) { hd[h.date] = h.kind; });
    var off = [];
    for (var i = 0; i < N; i++) off.push(weekend(i) || !!hd[ISO[i]] || (!!withVac && !!S.vac[ISO[i]]));
    return { off: off, hd: hd };
  }
  function runs(off) {
    var res = [], s = 0;
    for (var i = 1; i <= off.length; i++) if (i === off.length || off[i] !== off[s]) { res.push([s, i - 1, off[s]]); s = i; }
    return res;
  }
  /* Igual que _bridge_items() en build.py */
  function bridgeItems(hols) {
    var o = offDays(hols), rs = runs(o.off), items = [], covered = {};
    function hasHol(r) { for (var i = r[0]; i <= r[1]; i++) if (o.hd[ISO[i]]) return true; return false; }
    rs.forEach(function (r, k) { if (r[2] && hasHol(r) && r[1] - r[0] + 1 >= 3) { items.push({ s: r[0], e: r[1], cost: 0, take: [] }); covered[k] = 1; } });
    rs.forEach(function (r, k) {
      if (!r[2] && r[1] === r[0] && k > 0 && k < rs.length - 1) {
        var a = rs[k - 1], b = rs[k + 1];
        if (hasHol(a) || hasHol(b)) { items.push({ s: a[0], e: b[1], cost: 1, take: [r[0]] }); if (hasHol(a)) covered[k - 1] = 1; if (hasHol(b)) covered[k + 1] = 1; }
      }
    });
    rs.forEach(function (r, k) {
      if (!r[2] && r[1] - r[0] === 1 && k > 0 && k < rs.length - 1) {
        var hk = [k - 1, k + 1].filter(function (x) { return hasHol(rs[x]); });
        if (hk.length && !hk.every(function (x) { return covered[x]; })) { items.push({ s: rs[k - 1][0], e: rs[k + 1][1], cost: 2, take: [r[0], r[0] + 1] }); hk.forEach(function (x) { covered[x] = 1; }); }
      }
    });
    items.sort(function (a, b) { return a.s - b.s || a.e - b.e; });
    items.forEach(function (it) { it.len = it.e - it.s + 1; });
    return items;
  }
  function bridges(hols) { return bridgeItems(hols).filter(function (it) { return it.cost > 0; }); }
  function breaks(hols) {
    var a = bridgeItems(hols), pts = a.filter(function (it) { return it.cost > 0; });
    return a.filter(function (it) { return it.cost > 0 || !pts.some(function (p) { return p.s <= it.s && it.e <= p.e; }); });
  }
  /* Vacaciones: cada ventana de n laborables seguidos se extiende a los libres de alrededor; las mejores sin solaparse. */
  function plan(hols, n, max) {
    var off = offDays(hols, true).off, W = [];
    for (var i = 0; i < N; i++) if (!off[i]) W.push(i);
    n = Math.max(1, Math.min(n, W.length));
    var c = [];
    for (var k = 0; k + n <= W.length; k++) {
      var s = k > 0 ? W[k - 1] + 1 : 0, e = k + n < W.length ? W[k + n] - 1 : N - 1;
      c.push({ s: s, e: e, len: e - s + 1, cost: n, take: W.slice(k, k + n) });
    }
    c.sort(function (a, b) { return b.len - a.len || a.s - b.s; });
    var out = [];
    for (var j = 0; j < c.length && out.length < (max || 4); j++) if (!out.some(function (x) { return c[j].s <= x.e && x.s <= c[j].e; })) out.push(c[j]);
    return out;
  }

  /* ------------------------------------------------------------ marcado (igual que build.py) */
  var sw = function (k) { return '<i class="sw ' + k + '" aria-hidden="true"></i>'; };
  var scope = function (k) { return T['k_' + k]; };
  function holRow(h) {
    var i = IDX[h.date], we = weekend(i) ? ' we' : '', wd = T.wd[WD[i]], k = h.kind;
    var rm = h.kind === 'l' && !FIX ? ' <button type="button" class="x" data-rmloc="' + h.k + '" aria-label="' + esc(T.remove_local + ': ' + dlong(i)) + '">×</button>' : '';
    return '<tr class="k-' + k + '"><td class="c-d"><time datetime="' + h.date + '">' + dm(i) + '</time><span class="m' + we + '">' + wd + '</span></td>' +
      '<td class="c-w' + we + '">' + wd + '</td><td class="c-h">' + esc(h.name) + '<span class="m">' + sw(k) + scope(k) + rm + '</span></td>' +
      '<td class="c-s">' + sw(k) + scope(k) + rm + '</td></tr>';
  }
  function islandRow() {
    return '<tr class="k-z"><td class="c-d">+1</td><td class="c-w"></td><td class="c-h">' + T.island_holiday +
      ' <button type="button" class="lnk" data-zone>' + T.pick_island + '</button><span class="m">' + sw('r') + T.k_r + '</span></td>' +
      '<td class="c-s">' + sw('r') + T.k_r + '</td></tr>';
  }
  function names(hols, it) { return hols.filter(function (h) { return h.date >= ISO[it.s] && h.date <= ISO[it.e]; }).map(function (h) { return h.name; }).join(' · '); }
  function ptsRow(it, hols) {
    var vac = it.cost ? '<b>' + it.cost + '</b> <span class="m">' + esc(dlist(it.take)) + '</span>' : '<b>0</b> <span class="m">' + T.no_vac + '</span>';
    return '<tr' + (it.cost ? '' : ' class=lw') + '><td><span class="rng">' + drange(it.s, it.e) + '</span><span class="m">' + esc(names(hols, it)) + '</span></td>' +
      '<td class="num"><b>' + it.len + '</b></td><td>' + vac + '</td></tr>';
  }
  function taken(it) { return it.take.every(function (x) { return S.vac[ISO[x]]; }); }
  function planRow(it, k) {
    var on = taken(it);
    return '<tr' + (on ? ' class="on"' : '') + '><td><span class="rng">' + (it.take.length > 1 ? drange(it.take[0], it.take[it.take.length - 1]) : dshort(it.take[0])) + '</span></td>' +
      '<td class="num"><b>' + it.len + '</b></td><td class="fr m">' + drange(it.s, it.e) + '</td>' +
      '<td class="c-a"><button type="button" class="btn sm" data-' + (on ? 'rm' : 'add') + '="' + k + '">' + (on ? T.rm_vac : T.add_vac) + '</button></td></tr>';
  }

  /* ------------------------------------------------------------ render */
  var CELLS = [];
  all('#year td[data-d]').forEach(function (el) { CELLS[IDX[el.getAttribute('data-d')]] = el; });
  var NOW = new Date();
  var TODAY = NOW.getFullYear() + '-' + ('0' + (NOW.getMonth() + 1)).slice(-2) + '-' + ('0' + NOW.getDate()).slice(-2);
  var HD = {}, VITEMS = [], icsUrl = null;
  var markable = function (i) { return !weekend(i) && !HD[ISO[i]]; };

  function nextLine(hols) {
    var el = $('next');
    if (!el) return;
    var h = hols.filter(function (x) { return x.date >= TODAY; })[0];
    if (!h) { el.hidden = true; return; }
    var days = Math.round((Date.UTC(+h.date.slice(0, 4), +h.date.slice(5, 7) - 1, +h.date.slice(8)) -
      Date.UTC(NOW.getFullYear(), NOW.getMonth(), NOW.getDate())) / 864e5);
    var when = days === 0 ? T.today : days === 1 ? T.tomorrow : tn('days_left', days);
    var d = dlong(IDX[h.date]);
    el.innerHTML = '<span class="m">' + T.next_hol + ':</span> <b>' + esc(d.charAt(0).toUpperCase() + d.slice(1)) + '</b> · ' + esc(h.name) + ' <span class="m">· ' + when + '</span>';
    el.hidden = false;
  }

  function paint(hols) {
    var hd = {}; hols.forEach(function (h) { if (!hd[h.date]) hd[h.date] = h; });
    for (var i = 0; i < N; i++) {
      var el = CELLS[i];
      if (!el) continue;
      var h = hd[ISO[i]], c = [], v = !!S.vac[ISO[i]] && !weekend(i) && !h;
      if (weekend(i)) c.push('we');
      if (h) c.push(h.kind); else if (v) c.push('v');
      if (ISO[i] === TODAY) c.push('today');
      el.className = c.join(' ');
      var tip = h ? h.name : v ? T.vac_event : '';
      if (tip) el.title = tip; else el.removeAttribute('title');
      if (S.vmode && markable(i)) {
        el.setAttribute('role', 'button'); el.setAttribute('aria-pressed', String(v)); el.setAttribute('aria-label', dlong(i));
        if (!el.hasAttribute('tabindex')) el.tabIndex = -1;
      } else { el.removeAttribute('role'); el.removeAttribute('aria-pressed'); el.removeAttribute('aria-label'); el.removeAttribute('tabindex'); }
    }
    if (S.vmode && !doc.querySelector('#year td[tabindex="0"]')) {
      var first = 0; while (first < N && !markable(first)) first++;
      if (first < N) CELLS[first].tabIndex = 0;
    }
  }
  function vacCount() { return Object.keys(S.vac).filter(function (d) { return S.vac[d] && IDX[d] != null && markable(IDX[d]); }).length; }

  function render() {
    var hols = holidays();
    nextLine(hols);
    if (!S.region) return;
    HD = offDays(hols).hd;
    paint(hols);
    var isCan = S.region === 'canarias' && !S.zone && !CITY;
    $('hlist').innerHTML = hols.map(holRow).join('') + (isCan ? islandRow() : '');
    var addb = $('addloc');
    if (addb) addb.hidden = S.locals.filter(Boolean).length >= 2;
    var n = hols.length + (isCan ? 1 : 0), pts = bridges(hols).length;
    $('c-n').textContent = tn('n_hol', n); $('c-p').textContent = tn('n_pts', pts);
    $('plist').innerHTML = breaks(hols).map(function (it) { return ptsRow(it, hols); }).join('') || '<tr><td colspan="3">' + T.no_bridges + '</td></tr>';
    VITEMS = plan(hols, S.n, 4);
    $('vlist').innerHTML = VITEMS.map(planRow).join('');
    var used = vacCount();
    $('k-v').hidden = !used && !S.vmode;
    $('vstat').hidden = !used;
    $('vcount').textContent = used ? tn('vac_days', used) : '';
    $('vmode').setAttribute('aria-pressed', String(S.vmode));

    // exportar: la descarga lleva tus locales y vacaciones; las suscripciones, solo lo oficial
    var z = D.zones[S.region], zn = z && S.zone ? z.options.filter(function (o) { return o.slug === S.zone; })[0] : null;
    var rname = (D.regions.filter(function (r) { return r.slug === S.region; })[0] || {}).name || S.region;
    var label = CITY ? CITYNAME : rname + (zn && zn.slug !== 'general' ? ' · ' + zn.name : '');
    var suffix = CITY ? '-' + CITY : (zn && zn.add ? '-' + zn.slug : '');
    if (icsUrl) URL.revokeObjectURL(icsUrl);
    icsUrl = URL.createObjectURL(new Blob([ics(hols, label)], { type: 'text/calendar;charset=utf-8' }));
    $('dl').href = icsUrl; $('dl').download = T.ics_file + '-' + S.region + suffix + '.ics';
    var webcal = 'webcal://' + HOST + ASSETS + 'ics/' + S.region + suffix + '.ics';
    $('gc').href = 'https://calendar.google.com/calendar/r?cid=' + encodeURIComponent(webcal);
    $('wc').href = webcal;
  }

  function ics(hols, label) {
    var p = function (n) { return ('0' + n).slice(-2); };
    var ymd = function (i) { var d = new Date(Date.UTC(Y, 0, 1 + i)); return d.getUTCFullYear() + p(d.getUTCMonth() + 1) + p(d.getUTCDate()); };
    var L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//' + HOST + '//Calendario laboral 2027//ES', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH', 'X-WR-CALNAME:' + f(T.ics_calname, { label: label })];
    function ev(uid, s, e, name) {
      L.push('BEGIN:VEVENT', 'UID:' + uid + '@' + HOST, 'DTSTAMP:20261026T000000Z', 'DTSTART;VALUE=DATE:' + ymd(s), 'DTEND;VALUE=DATE:' + ymd(e + 1),
        'SUMMARY:' + name.replace(/[\\,;]/g, function (c) { return '\\' + c; }), 'TRANSP:TRANSPARENT', 'END:VEVENT');
    }
    hols.forEach(function (h) { var i = IDX[h.date]; ev(h.date.replace(/-/g, '') + '-' + h.kind + '-' + S.region, i, i, h.name); });
    var hd = offDays(hols).hd, blocks = [];
    Object.keys(S.vac).filter(function (d) { return S.vac[d] && IDX[d] != null; }).map(function (d) { return IDX[d]; })
      .sort(function (a, b) { return a - b; }).forEach(function (d) {
        var last = blocks[blocks.length - 1], joined = !!last;
        if (last) for (var g = last.e + 1; g < d; g++) if (!weekend(g) && !hd[ISO[g]]) joined = false;
        if (joined) last.e = d; else blocks.push({ s: d, e: d });
      });
    blocks.forEach(function (b) { ev('vac-' + ymd(b.s) + '-' + S.region, b.s, b.e, T.vac_event); });
    L.push('END:VCALENDAR');
    return L.join('\r\n') + '\r\n';
  }

  var toastT = null;
  function toast(msg) {
    var t = $('toast'); t.textContent = msg; t.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('on'); }, 2400);
  }

  /* ------------------------------------------------------------ estado */
  var vkey = function () { return S.region; };
  function loadVac() {
    S.vac = {};
    try { (JSON.parse(get('vac.' + vkey()) || '[]') || []).forEach(function (d) { if (IDX[d] != null) S.vac[d] = 1; }); } catch (e) { S.vac = {}; }
  }
  function saveVac() { put('vac.' + vkey(), JSON.stringify(Object.keys(S.vac).filter(function (d) { return S.vac[d]; }))); }
  function saveLoc() { put('loc.' + S.region, JSON.stringify(S.locals)); }

  if (!S.region) { render(); return; } // portada: solo la línea del próximo festivo

  if (FIX) { S.zone = FZONE; S.locals = FIX.map(function (x) { return x.date; }); S.lnames = FIX.map(function (x) { return x.name; }); }
  else {
    var z = D.zones[S.region];
    S.zone = z ? get('zone.' + S.region) : null;
    if (z && !z.options.some(function (o) { return o.slug === S.zone; })) S.zone = S.region === 'cataluna' ? 'general' : null;
    var l = [];
    try { l = JSON.parse(get('loc.' + S.region) || '[]') || []; } catch (e) { l = []; }
    S.locals = l.filter(function (d) { return IDX[d] != null; }).slice(0, 2);
    if ($('zone')) $('zone').value = S.zone || '';
  }
  loadVac();
  var n0 = parseInt(get('n'), 10);
  if (n0 >= 1 && n0 <= 30) { S.n = n0; $('vn').value = n0; }
  put('region', S.region);

  /* ------------------------------------------------------------ eventos */
  if ($('region')) $('region').addEventListener('change', function () { location.href = BASE + this.value + '/'; });
  if ($('zone')) $('zone').addEventListener('change', function () { S.zone = this.value || null; put('zone.' + S.region, S.zone); render(); });

  var locin = $('locin');
  if ($('addloc')) $('addloc').addEventListener('click', function () {
    try { if (locin.showPicker) { locin.showPicker(); return; } } catch (e) { /* sin showPicker */ }
    locin.classList.remove('vh'); locin.removeAttribute('tabindex'); locin.focus();
  });
  if (locin) locin.addEventListener('change', function () {
    var v = this.value;
    this.value = ''; locin.classList.add('vh'); locin.setAttribute('tabindex', '-1');
    if (!v || IDX[v] == null || S.locals.indexOf(v) >= 0 || S.locals.length >= 2) return;
    S.locals.push(v); S.locals.sort();
    if (S.vac[v]) { delete S.vac[v]; saveVac(); }
    saveLoc(); render();
    toast(f(T.local_toast, { date: dlong(IDX[v]) }));
  });
  $('hlist').addEventListener('click', function (e) {
    if (e.target.closest('[data-zone]')) { var zs = $('zone'); zs.focus(); try { if (zs.showPicker) zs.showPicker(); } catch (x) { /* foco basta */ } return; }
    var b = e.target.closest('[data-rmloc]');
    if (!b) return;
    S.locals.splice(+b.getAttribute('data-rmloc'), 1);
    saveLoc(); render();
    if ($('addloc')) $('addloc').focus();
  });

  $('vlist').addEventListener('click', function (e) {
    var b = e.target.closest('[data-add],[data-rm]');
    if (!b) return;
    var add = b.hasAttribute('data-add'), k = +(b.getAttribute('data-add') || b.getAttribute('data-rm')), it = VITEMS[k];
    it.take.forEach(function (x) { if (add) S.vac[ISO[x]] = 1; else delete S.vac[ISO[x]]; });
    saveVac(); render();
    toast(add ? tn('vac_added', vacCount()) : T.vac_removed);
    var again = doc.querySelector('#vlist [data-' + (add ? 'rm' : 'add') + '="' + k + '"]'); if (again) again.focus();
  });
  function setN(v) { v = Math.max(1, Math.min(30, parseInt(v, 10) || 1)); S.n = v; $('vn').value = v; put('n', String(v)); render(); }
  $('vm').addEventListener('click', function () { setN(S.n - 1); });
  $('vp').addEventListener('click', function () { setN(S.n + 1); });
  $('vn').addEventListener('change', function () { setN(this.value); });

  function setVmode(on) {
    S.vmode = on;
    doc.body.classList.toggle('vmode', on);
    if (on) $('year').removeAttribute('aria-hidden'); else $('year').setAttribute('aria-hidden', 'true');
    render();
  }
  $('vmode').addEventListener('click', function () { setVmode(!S.vmode); });
  function toggleDay(i) {
    if (!markable(i)) return;
    var d = ISO[i];
    if (S.vac[d]) delete S.vac[d]; else S.vac[d] = 1;
    saveVac(); render();
  }
  $('year').addEventListener('click', function (e) {
    if (!S.vmode) return;
    var c = e.target.closest('td[data-d]');
    if (c) toggleDay(IDX[c.getAttribute('data-d')]);
  });
  $('year').addEventListener('keydown', function (e) {
    if (!S.vmode) return;
    var c = e.target.closest('td[data-d]');
    if (!c) return;
    var i = IDX[c.getAttribute('data-d')], step = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: 7, ArrowUp: -7 }[e.key];
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleDay(i); return; }
    if (!step) return;
    e.preventDefault();
    var j = i + step;
    while (j >= 0 && j < N && !markable(j)) j += step > 0 ? 1 : -1;
    if (j < 0 || j >= N) return;
    c.tabIndex = -1; CELLS[j].tabIndex = 0; CELLS[j].focus();
  });
  $('vclear').addEventListener('click', function () { S.vac = {}; saveVac(); render(); toast(T.vac_cleared); $('vmode').focus(); });
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && S.vmode) setVmode(false); });

  render();

  // para pruebas automáticas
  window.CL27 = { plan: function (n) { return plan(holidays(), n, 5); }, bridges: function () { return bridges(holidays()); },
    holidays: holidays, iso: ISO, ics: function () { return ics(holidays(), 'test'); } };
})();
