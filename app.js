/* Calendario laboral 2027 - app. Datos: BOE-A-2026-21254 (embebidos en la página). */
(function () {
  'use strict';
  var doc = document, html = doc.documentElement;
  html.classList.add('js');
  var $ = function (id) { return doc.getElementById(id); };
  var all = function (sel, root) { return Array.prototype.slice.call((root || doc).querySelectorAll(sel)); };
  var BASE = html.getAttribute('data-base') || '/';
  var burger = $('burger');
  function closeBurger() { if (burger) { burger.setAttribute('aria-expanded', 'false'); doc.body.classList.remove('nav-open'); } }

  /* ------------------------------------------------------------ menús (details) y menú móvil */
  var dds = all('details.dd');
  dds.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      dds.forEach(function (o) { if (o !== d && !o.contains(d)) o.open = false; });
      if (d.classList.contains('dd-lang')) closeBurger();
    });
  });
  doc.addEventListener('click', function (e) { dds.forEach(function (d) { if (d.open && !d.contains(e.target)) d.open = false; }); });
  doc.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    dds.forEach(function (d) { if (d.open) { d.open = false; d.querySelector('summary').focus(); } });
  });
  all('.menu-cal a').forEach(function (a) { a.addEventListener('click', function () { var d = a.closest('details'); if (d) d.open = false; }); });
  if (burger) burger.addEventListener('click', function () {
    var on = burger.getAttribute('aria-expanded') !== 'true';
    burger.setAttribute('aria-expanded', String(on));
    doc.body.classList.toggle('nav-open', on);
    if (on) dds.forEach(function (d) { if (d.classList.contains('dd-lang')) d.open = false; });
  });
  all('[data-print]').forEach(function (b) { b.addEventListener('click', function () { window.print(); }); });
  /* ------------------------------------------------------------ instalar como app (PWA) */
  var inst = $('inst'), deferred = null;
  var standalone = (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone === true;
  if (inst && !standalone) {
    var ios = /iphone|ipad|ipod/i.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    all('[data-os]', inst).forEach(function (p) { p.hidden = (p.getAttribute('data-os') === 'ios') !== ios; });
    inst.hidden = false;
    all('[data-install]').forEach(function (a) { a.hidden = false; });
    var install = function (e) {
      if (!deferred) return false;
      if (e) e.preventDefault();
      deferred.prompt();
      deferred.userChoice.then(function (c) { if (c.outcome === 'accepted') inst.hidden = true; });
      deferred = null;
      return true;
    };
    window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); deferred = e; });
    window.addEventListener('appinstalled', function () { inst.hidden = true; all('[data-install]').forEach(function (a) { a.hidden = true; }); });
    inst.querySelector('summary').addEventListener('click', install);
    all('[data-install]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        if (install(e)) return;
        e.preventDefault();
        window.scrollTo(0, 0);
        inst.open = true;
      });
    });
  }

  if ($('region')) $('region').addEventListener('change', function () { if (this.value) location.href = BASE + this.value + '/'; });
  if ($('city')) $('city').addEventListener('change', function () { location.href = this.value; });

  if (!$('cal-data')) return;
  var D = JSON.parse($('cal-data').textContent);
  var T = JSON.parse($('cal-i18n').textContent);
  var Y = D.year, N = 365;
  var ASSETS = html.getAttribute('data-assets') || BASE;
  var HOST = location.host || 'elcalendariolaboral.es';
  var PAGE = doc.body.getAttribute('data-region') || '';
  var CITY = doc.body.getAttribute('data-city') || '', CITYNAME = doc.body.getAttribute('data-cityname') || '';
  var FIX = CITY ? JSON.parse(doc.body.getAttribute('data-locals') || '[]') : null, FZONE = doc.body.getAttribute('data-zone') || null;
  var f = function (s, o) { return s.replace(/\{(\w+)\}/g, function (m, k) { return o[k] != null ? o[k] : m; }); };
  var tn = function (k, n) { var v = T[k]; return f(typeof v === 'string' ? v : (n === 1 ? v.one : v.other), { n: n }); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var cap = function (s) { return s.charAt(0).toUpperCase() + s.slice(1); };

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

  var S = { region: PAGE || null, zone: null, locals: [], lnames: [], n: 4, vac: {} };
  var APP = !!S.region;

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
      if (o && o.add) out.push({ date: o.add.date, name: o.add.name, kind: S.region === 'canarias' ? 'i' : 'r' });
    }
    S.locals.forEach(function (d, k) {
      if (d && IDX[d] != null && !out.some(function (h) { return h.date === d; })) out.push({ date: d, name: S.lnames[k] || T.local_holiday, kind: 'l', k: k });
    });
    out.sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
    return out;
  }
  function offDays(hols) {
    var hd = {}; hols.forEach(function (h) { hd[h.date] = h.kind; });
    var off = [];
    for (var i = 0; i < N; i++) off.push(weekend(i) || !!hd[ISO[i]]);
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
  /* Vacaciones: cada ventana de n laborables seguidos se extiende a los libres de alrededor; las mejores sin solaparse.
     No cuenta lo ya marcado, para que una opción añadida siga en la lista (con "Quitar"). */
  function plan(hols, n, max) {
    var off = offDays(hols).off, W = [];
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
  function monthItems(m, hols) {
    return hols.filter(function (h) { return MON[IDX[h.date]] === m - 1; }).map(function (h) {
      var i = IDX[h.date];
      return '<li class="k-' + h.kind + (weekend(i) ? ' we' : '') + '"><b>' + DOM[i] + '</b> ' + esc(h.name) + '</li>';
    }).join('');
  }
  function holItem(h) {
    var i = IDX[h.date], we = weekend(i) ? ' we' : '', k = h.kind;
    var rm = k === 'l' && !FIX ? '<button type="button" class="x" data-rmloc="' + h.k + '" aria-label="' + esc(T.remove_local + ': ' + dlong(i)) + '">×</button>' : '';
    return '<li class="k-' + k + '"><span class="d"><time datetime="' + h.date + '">' + dm(i) + '</time> <span class="m' + we + '">' + T.wd[WD[i]] + '</span></span>' +
      '<span class="h">' + esc(h.name) + '</span><span class="s">' + sw(k) + scope(k) + rm + '</span></li>';
  }
  function islandItem() {
    return '<li class="k-z"><span class="d">+1</span><span class="h">' + T.island_holiday + ' <button type="button" class="lnk" data-zone>' + T.pick_island +
      '</button></span><span class="s">' + sw('i') + T.k_i + '</span></li>';
  }
  function names(hols, it) { return hols.filter(function (h) { return h.date >= ISO[it.s] && h.date <= ISO[it.e]; }).map(function (h) { return h.name; }).join(' · '); }
  function ptsRow(it, hols) {
    var vac = it.cost ? '<span class="mo">' + tn('vac_days', it.cost) + ': </span><b class="dk">' + it.cost + '</b> <span class="m">' + esc(dlist(it.take)) + '</span>'
      : '<b class="dk">0</b> <span class="m">' + T.no_vac + '</span>';
    return '<tr' + (it.cost ? '' : ' class=lw') + '><td class="c-p"><span class="rng">' + drange(it.s, it.e) + '</span><span class="m nm">' + esc(names(hols, it)) + '</span></td>' +
      '<td class="num">' + tn('n_days', it.len) + '</td><td class="c-v">' + vac + '</td></tr>';
  }
  function taken(it) { return it.take.every(function (x) { return S.vac[ISO[x]]; }); }
  function planRow(it, k) {
    var on = taken(it);
    return '<tr' + (on ? ' class="on"' : '') + '><td class="c-t"><span class="rng">' + (it.take.length > 1 ? drange(it.take[0], it.take[it.take.length - 1]) : dshort(it.take[0])) + '</span></td>' +
      '<td class="num"><b>' + f(T.free_n, { n: it.len }) + '</b></td><td class="fr m">' + drange(it.s, it.e) + '</td>' +
      '<td class="c-a"><button type="button" class="btn sm' + (on ? ' on' : '') + '" data-' + (on ? 'rm' : 'add') + '="' + k + '" aria-label="' + esc(on ? T.rm_vac : T.add_vac) + '">' +
      (on ? T.rm_short : '+ ' + T.add_short) + '</button></td></tr>';
  }

  /* ------------------------------------------------------------ render */
  var CELLS = [];
  all('#year td[data-d]').forEach(function (el) { CELLS[IDX[el.getAttribute('data-d')]] = el; });
  var GRID = CELLS.length > 0;
  if (GRID) all('#year table').forEach(function (tb) { tb.setAttribute('role', 'grid'); });
  var NOW = new Date();
  var TODAY = NOW.getFullYear() + '-' + ('0' + (NOW.getMonth() + 1)).slice(-2) + '-' + ('0' + NOW.getDate()).slice(-2);
  var HD = {}, HOLS = [], VITEMS = [], icsUrl = null, focusIdx = null;
  var markable = function (i) { return APP && !weekend(i) && !HD[ISO[i]]; };

  function nextLine(hols) {
    var el = $('next');
    if (!el) return;
    var h = hols.filter(function (x) { return x.date >= TODAY; })[0];
    if (!h) { el.hidden = true; return; }
    var days = Math.round((Date.UTC(+h.date.slice(0, 4), +h.date.slice(5, 7) - 1, +h.date.slice(8)) - Date.UTC(NOW.getFullYear(), NOW.getMonth(), NOW.getDate())) / 864e5);
    var when = days === 0 ? T.today : days === 1 ? T.tomorrow : tn('days_left', days);
    el.innerHTML = '<span class="m">' + T.next_hol + ':</span> <b>' + esc(cap(dlong(IDX[h.date]))) + '</b> · ' + esc(h.name) + ' <span class="m">· ' + when + '</span>';
    el.hidden = false;
  }

  function paint(hols) {
    var hd = {}; hols.forEach(function (h) { if (!hd[h.date]) hd[h.date] = h; });
    if (focusIdx == null) { focusIdx = IDX[TODAY] != null ? IDX[TODAY] : 0; }
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
      el.setAttribute('aria-label', cap(dlong(i)) + (tip ? ' · ' + tip : ''));
      el.tabIndex = i === focusIdx ? 0 : -1;
    }
    for (var m = 1; m <= 12; m++) { var ul = $('mh' + m); if (ul) ul.innerHTML = monthItems(m, hols); }
  }
  function vacCount() { return Object.keys(S.vac).filter(function (d) { return S.vac[d] && IDX[d] != null && markable(IDX[d]); }).length; }

  function render() {
    var hols = holidays();
    HOLS = hols;
    HD = offDays(hols).hd;
    nextLine(hols);
    if (GRID) paint(hols);
    if (!APP) return;
    var isCan = S.region === 'canarias' && !S.zone && !CITY;
    $('hlist').innerHTML = hols.map(holItem).join('') + (isCan ? islandItem() : '');
    var addb = $('addloc');
    if (addb) addb.hidden = S.locals.filter(Boolean).length >= 2;
    var lab = 0; for (var i = 0; i < N; i++) if (!weekend(i) && !HD[ISO[i]]) lab++;
    $('c-n').textContent = tn('n_hol', hols.length + (isCan ? 1 : 0)); $('c-l').textContent = tn('n_lab', lab - (isCan ? 1 : 0));
    $('plist').innerHTML = breaks(hols).map(function (it) { return ptsRow(it, hols); }).join('') || '<tr><td colspan="3">' + T.no_bridges + '</td></tr>';
    VITEMS = plan(hols, S.n, 4);
    $('vlist').innerHTML = VITEMS.map(planRow).join('');
    var used = vacCount();
    $('k-v').hidden = !used;
    $('vcount').textContent = used ? tn('vac_days', used) : '';

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
    var pk = S.region + suffix;
    all('[data-pdf]').forEach(function (a) {
      var fn = 'calendario-laboral-2027-' + pk + a.getAttribute('data-pdf') + '.pdf';
      a.href = ASSETS + 'pdf/' + pk + '/' + fn; a.download = fn;
    });
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
  function toast(msg, goto) {
    var t = $('toast');
    t.innerHTML = esc(msg) + (goto != null ? ' <button type="button" class="lnk" data-goto="' + goto + '">' + esc(T.see_cal) + '</button>' : '');
    t.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('on'); }, goto != null ? 6000 : 2600);
  }
  $('toast').addEventListener('click', function (e) {
    var b = e.target.closest('[data-goto]');
    if (!b) return;
    var i = +b.getAttribute('data-goto'), m = $('m' + (MON[i] + 1));
    $('toast').classList.remove('on');
    if (m) { m.scrollIntoView({ block: 'center', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); m.classList.add('flash'); setTimeout(function () { m.classList.remove('flash'); }, 1600); }
    if (CELLS[i]) { focusIdx = i; CELLS[i].tabIndex = 0; CELLS[i].focus({ preventScroll: true }); }
  });

  /* ------------------------------------------------------------ popover del día */
  var pop = $('pop'), popIdx = null;
  function closePop(back) {
    if (!pop || pop.hidden) return;
    pop.hidden = true;
    if (back && popIdx != null && CELLS[popIdx]) CELLS[popIdx].focus();
    popIdx = null;
  }
  function openPop(i) {
    if (!pop) return;
    popIdx = i;
    var h = HOLS.filter(function (x) { return x.date === ISO[i]; })[0], v = !!S.vac[ISO[i]];
    $('pop-d').textContent = cap(dlong(i));
    $('pop-h').innerHTML = h ? sw(h.kind) + esc(h.name) + ' <span class="m">· ' + scope(h.kind) + '</span>' : v ? sw('v') + esc(T.vac_event) : '';
    $('pop-h').hidden = !h && !v;
    var a = '';
    if (h && h.kind === 'l' && !FIX && APP) a += '<button type="button" class="btn" data-p="rmloc">' + esc(T.remove_local) + '</button>';
    if (markable(i)) {
      a += '<button type="button" class="btn' + (v ? '' : ' p') + '" data-p="vac">' + esc(v ? T.rm_vac : T.add_vac) + '</button>';
      if (!FIX && !v && S.locals.length < 2) a += '<button type="button" class="btn" data-p="loc">+ ' + esc(T.add_local) + '</button>';
    }
    $('pop-a').innerHTML = a;
    $('pop-a').hidden = !a;
    pop.setAttribute('aria-label', cap(dlong(i)));
    pop.hidden = false;
    if (innerWidth > 640) {
      var r = CELLS[i].getBoundingClientRect(), w = pop.offsetWidth, hgt = pop.offsetHeight;
      var left = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), innerWidth - w - 8);
      var top = r.bottom + 6 + hgt > innerHeight ? r.top - hgt - 6 : r.bottom + 6;
      pop.style.left = (left + scrollX) + 'px'; pop.style.top = (top + scrollY) + 'px';
    } else { pop.style.left = ''; pop.style.top = ''; }
    var first = pop.querySelector('button'); if (first) first.focus({ preventScroll: true });
  }
  if (pop) {
    pop.addEventListener('click', function (e) {
      e.stopPropagation(); // the buttons are re-rendered: the target leaves the popover before the document sees the click
      var b = e.target.closest('[data-p]'), i = popIdx;
      if (!b || i == null) return;
      var act = b.getAttribute('data-p'), d = ISO[i];
      if (act === 'vac') { if (S.vac[d]) delete S.vac[d]; else S.vac[d] = 1; saveVac(); }
      if (act === 'loc') { addLocal(d); }
      if (act === 'rmloc') { var k = S.locals.indexOf(d); if (k >= 0) { S.locals.splice(k, 1); saveLoc(); } }
      render();
      openPop(i);
    });
    doc.addEventListener('click', function (e) { if (!pop.hidden && !pop.contains(e.target) && !e.target.closest('#year td[data-d]')) closePop(false); });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePop(true); });
    addEventListener('resize', function () { closePop(false); });
  }
  if (GRID) {
    $('year').addEventListener('click', function (e) {
      var c = e.target.closest('td[data-d]');
      if (!c) return;
      var i = IDX[c.getAttribute('data-d')];
      if (popIdx === i && !pop.hidden) { closePop(false); return; }
      setFocus(i, false); openPop(i);
    });
    $('year').addEventListener('keydown', function (e) {
      var c = e.target.closest('td[data-d]');
      if (!c) return;
      var i = IDX[c.getAttribute('data-d')], step = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: 7, ArrowUp: -7 }[e.key];
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openPop(i); return; }
      if (e.key === 'Home') step = -WD[i];
      if (e.key === 'End') step = 6 - WD[i];
      if (!step) return;
      e.preventDefault();
      var j = Math.max(0, Math.min(N - 1, i + step));
      closePop(false); setFocus(j, true);
    });
  }
  function setFocus(i, move) {
    if (CELLS[focusIdx]) CELLS[focusIdx].tabIndex = -1;
    focusIdx = i; CELLS[i].tabIndex = 0;
    if (move) CELLS[i].focus();
  }

  /* ------------------------------------------------------------ estado */
  function loadVac() {
    S.vac = {};
    try { (JSON.parse(get('vac.' + S.region) || '[]') || []).forEach(function (d) { if (IDX[d] != null) S.vac[d] = 1; }); } catch (e) { S.vac = {}; }
  }
  function saveVac() { put('vac.' + S.region, JSON.stringify(Object.keys(S.vac).filter(function (d) { return S.vac[d]; }))); }
  function saveLoc() { put('loc.' + S.region, JSON.stringify(S.locals)); }
  function addLocal(v) {
    if (!v || IDX[v] == null || S.locals.indexOf(v) >= 0 || S.locals.length >= 2 || HD[v]) return;
    S.locals.push(v); S.locals.sort();
    if (S.vac[v]) { delete S.vac[v]; saveVac(); }
    saveLoc();
    toast(f(T.local_toast, { date: dlong(IDX[v]) }));
  }

  if (!APP) { render(); return; }

  var params = null;
  try { params = new URLSearchParams(location.search); } catch (e) { params = null; }
  var zparam = S.region === 'canarias' ? 'isla' : 'zona';
  if (FIX) { S.zone = FZONE; S.locals = FIX.map(function (x) { return x.date; }); S.lnames = FIX.map(function (x) { return x.name; }); }
  else {
    var z = D.zones[S.region];
    var fromUrl = params && params.get(zparam);
    S.zone = z ? (fromUrl || get('zone.' + S.region)) : null;
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
  function zoneUrl() {
    try {
      var u = new URL(location.href);
      if (S.zone && !(S.region === 'cataluna' && S.zone === 'general')) u.searchParams.set(zparam, S.zone); else u.searchParams.delete(zparam);
      history.replaceState(null, '', u.pathname + u.search + u.hash);
    } catch (e) { /* file:// */ }
  }
  if ($('zone')) $('zone').addEventListener('change', function () { S.zone = this.value || null; put('zone.' + S.region, S.zone); zoneUrl(); render(); });

  var locin = $('locin');
  if ($('addloc')) $('addloc').addEventListener('click', function () {
    try { if (locin.showPicker) { locin.showPicker(); return; } } catch (e) { /* sin showPicker */ }
    locin.classList.remove('vh'); locin.removeAttribute('tabindex'); locin.focus();
  });
  if (locin) locin.addEventListener('change', function () {
    var v = this.value;
    this.value = ''; locin.classList.add('vh'); locin.setAttribute('tabindex', '-1');
    addLocal(v); render();
  });
  $('hlist').addEventListener('click', function (e) {
    if (e.target.closest('[data-zone]')) { var zs = $('zone'); zs.scrollIntoView({ block: 'center' }); zs.focus(); try { if (zs.showPicker) zs.showPicker(); } catch (x) { /* foco basta */ } return; }
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
    if (add) toast(tn('vac_added', vacCount()), it.take[0]); else toast(T.vac_removed);
    var again = doc.querySelector('#vlist [data-' + (add ? 'rm' : 'add') + '="' + k + '"]'); if (again) again.focus();
  });
  function setN(v) { v = Math.max(1, Math.min(30, parseInt(v, 10) || 1)); S.n = v; $('vn').value = v; put('n', String(v)); render(); }
  $('vm').addEventListener('click', function () { setN(S.n - 1); });
  $('vp').addEventListener('click', function () { setN(S.n + 1); });
  $('vn').addEventListener('change', function () { setN(this.value); });
  $('vclear').addEventListener('click', function () { S.vac = {}; saveVac(); render(); toast(T.vac_cleared); });

  render();

  // para pruebas automáticas
  window.CL27 = { plan: function (n) { return plan(holidays(), n, 5); }, bridges: function () { return bridges(holidays()); },
    holidays: holidays, iso: ISO, ics: function () { return ics(holidays(), 'test'); } };
})();
