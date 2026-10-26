/* Calendario laboral 2027 - app. Datos: BOE-A-2026-21254 (embebidos en la página). */
(function () {
  'use strict';
  var doc = document, html = doc.documentElement;
  html.classList.add('js');
  var $ = function (id) { return doc.getElementById(id); };
  var D = JSON.parse($('cal-data').textContent);
  var Y = D.year, N = 365, BASE = html.getAttribute('data-base') || '/';
  var ASSETS = html.getAttribute('data-assets') || BASE;
  var HOST = location.host || 'elcalendariolaboral.es';
  var PAGE = doc.body.getAttribute('data-region') || '', HOME = !PAGE;
  /* textos: build.py los incrusta en #cal-i18n desde su tabla T[idioma] */
  var T = JSON.parse($('cal-i18n').textContent);
  var f = function (s, o) { return s.replace(/\{(\w+)\}/g, function (m, k) { return o[k] != null ? o[k] : m; }); };
  var sun = function (a) { return [a[6]].concat(a.slice(0, 6)); }; // T trae la semana de lunes a domingo; getUTCDay() empieza en domingo
  var MON3 = T.mon3, MONL = T.months, WD3 = sun(T.wd3), WDL = sun(T.wd), WD1 = sun(T.wd1.split('')).join('');
  var ISO = [], WDAY = [], MON = [], DOM = [];
  for (var i = 0; i < N; i++) {
    var dd = new Date(Date.UTC(Y, 0, 1 + i));
    ISO.push(dd.toISOString().slice(0, 10)); WDAY.push(dd.getUTCDay()); MON.push(dd.getUTCMonth()); DOM.push(dd.getUTCDate());
  }
  var IDX = {}; ISO.forEach(function (s, k) { IDX[s] = k; });
  var REG = {}; D.regions.forEach(function (r) { REG[r.slug] = r; });
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var weekend = function (i) { return WDAY[i] === 0 || WDAY[i] === 6; };
  var tn = function (k, n) { return f(n === 1 && T[k + '1'] ? T[k + '1'] : T[k], { n: n }); };
  var SEP = '<span class="sep" aria-hidden="true"> · </span>';
  var smooth = function () { return matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth'; };

  function get(k) { try { return localStorage.getItem('cl27.' + k); } catch (e) { return null; } }
  function put(k, v) { try { if (v == null) localStorage.removeItem('cl27.' + k); else localStorage.setItem('cl27.' + k, v); } catch (e) { /* sin almacenamiento */ } }

  var S = { region: null, zone: null, locals: ['', ''], n: 4, sel: null, vac: {}, vmode: false };
  var key = function () { return S.region || 'es'; };

  /* ------------------------------------------------------------ datos */
  function holidays() {
    var out = [];
    D.holidays.forEach(function (h) {
      var all = h.regions === 'all';
      if (all || (S.region && h.regions.indexOf(S.region) >= 0)) out.push({ date: h.date, name: h.name, kind: all ? 'n' : 'r' });
    });
    var z = S.region && D.zones[S.region];
    if (z && S.zone) {
      var o = z.options.filter(function (x) { return x.slug === S.zone; })[0];
      if (o && o.remove) out = out.filter(function (h) { return h.date !== o.remove; });
      if (o && o.add) out.push({ date: o.add.date, name: o.add.name, kind: 'r' });
    }
    var boe = out.length;
    if (S.region) S.locals.forEach(function (d) { if (d && IDX[d] != null && !out.some(function (h) { return h.date === d; })) out.push({ date: d, name: T.local_name, kind: 'l' }); });
    out.sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
    out.boe = boe;
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

  /* Todos los tramos: fines de semana largos (0 días) y huecos de 1-2 laborables junto a un festivo. Igual que build.py. */
  function bridgeItems(hols) {
    var o = offDays(hols), rs = runs(o.off), items = [], covered = {};
    function hasHol(r) { for (var i = r[0]; i <= r[1]; i++) if (o.hd[ISO[i]]) return true; return false; }
    rs.forEach(function (r, k) {
      if (r[2] && hasHol(r) && r[1] - r[0] + 1 >= 3) { items.push({ s: r[0], e: r[1], cost: 0, take: [] }); covered[k] = 1; }
    });
    rs.forEach(function (r, k) {
      if (!r[2] && r[1] === r[0] && k > 0 && k < rs.length - 1) {
        var a = rs[k - 1], b = rs[k + 1];
        if (hasHol(a) || hasHol(b)) {
          items.push({ s: a[0], e: b[1], cost: 1, take: [r[0]] });
          if (hasHol(a)) covered[k - 1] = 1;
          if (hasHol(b)) covered[k + 1] = 1;
        }
      }
    });
    rs.forEach(function (r, k) {
      if (!r[2] && r[1] - r[0] === 1 && k > 0 && k < rs.length - 1) {
        var hk = [k - 1, k + 1].filter(function (x) { return hasHol(rs[x]); });
        if (hk.length && !hk.every(function (x) { return covered[x]; })) {
          items.push({ s: rs[k - 1][0], e: rs[k + 1][1], cost: 2, take: [r[0], r[0] + 1] });
          hk.forEach(function (x) { covered[x] = 1; });
        }
      }
    });
    items.sort(function (a, b) { return a.s - b.s || a.e - b.e; });
    items.forEach(function (it) { it.len = it.e - it.s + 1; });
    return items;
  }
  /* Puentes de verdad: cuestan 1 o 2 laborables (build.py: puentes) */
  function bridges(hols) { return bridgeItems(hols).filter(function (it) { return it.cost > 0; }); }
  /* Fines de semana largos sin coste, salvo los que caen dentro de un puente (build.py: long_weekends) */
  function longWeekends(hols) {
    var all = bridgeItems(hols), pts = all.filter(function (it) { return it.cost > 0; });
    return all.filter(function (it) { return !it.cost && !pts.some(function (p) { return p.s <= it.s && it.e <= p.e; }); });
  }

  /* Vacaciones: cada ventana de n laborables seguidos (sin contar los ya marcados) se extiende a los libres de
     alrededor; se ordenan por días libres y se toman las mejores sin solaparse. */
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
    for (var j = 0; j < c.length && out.length < (max || 5); j++) {
      if (!out.some(function (x) { return c[j].s <= x.e && x.s <= c[j].e; })) out.push(c[j]);
    }
    return out;
  }

  /* ------------------------------------------------------------ formato */
  function fday(i) { return WD3[WDAY[i]] + ' ' + DOM[i] + ' ' + MON3[MON[i]]; }
  function frange(a, b) {
    return MON[a] === MON[b] ? WD3[WDAY[a]] + ' ' + DOM[a] + ' – ' + WD3[WDAY[b]] + ' ' + DOM[b] + ' ' + MON3[MON[b]] : fday(a) + ' – ' + fday(b);
  }
  function longDay(i) { return f(T.long_day, { wd: WDL[WDAY[i]], d: DOM[i], m: MONL[MON[i]] }); }
  function names(hols, it) {
    return hols.filter(function (h) { return h.date >= ISO[it.s] && h.date <= ISO[it.e]; }).map(function (h) { return h.name; }).join(' · ');
  }
  function takeTxt(take) {
    var d = take.map(function (x) { return WD3[WDAY[x]] + ' ' + DOM[x]; });
    return d.length === 1 ? f(T.take1, { a: d[0] }) : f(T.take2, { a: d[0], b: d[1] });
  }
  function takeRange(take) {
    var a = take[0], b = take[take.length - 1];
    if (a === b) return f(T.take1, { a: WD3[WDAY[a]] + ' ' + DOM[a] });
    return MON[a] === MON[b] ? f(T.take_r, { a: DOM[a], b: DOM[b] + ' ' + MON3[MON[b]] }) : f(T.take_rx, { a: DOM[a] + ' ' + MON3[MON[a]], b: DOM[b] + ' ' + MON3[MON[b]] });
  }
  function same(a, b) { return !!(a && b && a.s === b.s && a.e === b.e && a.cost === b.cost); }
  function taken(it) { return it.take.length > 0 && it.take.every(function (x) { return S.vac[ISO[x]]; }); }
  function trade(cost, n) {
    var c = tn('cost', cost);
    return '<span class="z"><span class="c">' + c + ' →</span><span class="g2"><b>' + n + '</b> ' + T.free + '</span><span class="sr">' +
      f(T.trade_sr, { c: c, n: n }) + '</span></span>';
  }

  /* Una fila: fechas, qué coger y lo que ganas. Abierta: los días en pequeño, los festivos y el botón de añadir. */
  function item(it, sub, id, hols, hd) {
    var on = same(S.sel, it), x = '';
    if (on) {
      var tk = {}, cells = '';
      it.take.forEach(function (d) { tk[d] = 1; });
      for (var d = it.s; d <= it.e; d++) {
        var c = hd[ISO[d]] ? 'h' : (S.vac[ISO[d]] && !weekend(d) ? 'vac' : tk[d] ? 'pk' : weekend(d) ? 'we' : '');
        cells += '<i class="' + c + '"><span>' + WD1.charAt(WDAY[d]) + '</span>' + DOM[d] + '</i>';
      }
      var nm = names(hols, it);
      x = '<div class="x"><div class="strip" aria-hidden="true">' + cells + '</div>' + (nm ? '<p class="nm">' + esc(nm) + '</p>' : '') +
        (taken(it) ? '<button class="btn" type="button" data-rm="' + id + '">' + T.rm_vac + '</button>'
          : '<button class="btn p" type="button" data-add="' + id + '">' + T.add_vac + '</button>') + '</div>';
    }
    return '<li' + (on ? ' class="on"' : '') + '><button type="button" class="it" data-k="' + id + '" aria-expanded="' + on + '">' +
      '<span class="a"><time>' + frange(it.s, it.e) + '</time><small>' + esc(sub) + '</small></span>' + trade(it.cost, it.len) + '</button>' + x + '</li>';
  }

  /* ------------------------------------------------------------ render */
  var CELLS = [];
  Array.prototype.forEach.call(doc.querySelectorAll('.g b[data-d]'), function (el) { CELLS[IDX[el.getAttribute('data-d')]] = el; });
  var NOW = new Date();
  var TODAY = NOW.getFullYear() + '-' + ('0' + (NOW.getMonth() + 1)).slice(-2) + '-' + ('0' + NOW.getDate()).slice(-2);
  var PITEMS = [], VITEMS = [], HD = {}, icsUrl = null;
  var markable = function (i) { return !weekend(i) && !HD[ISO[i]]; };

  function paintYear(hols) {
    var hd = {}; hols.forEach(function (h) { if (!hd[h.date]) hd[h.date] = h; });
    var sel = S.sel, tk = {}, lab = 0;
    if (sel) sel.take.forEach(function (x) { tk[x] = 1; });
    for (var i = 0; i < N; i++) {
      var el = CELLS[i], h = hd[ISO[i]], c = [], v = !!S.vac[ISO[i]] && !weekend(i) && !h;
      if (weekend(i)) c.push('we');
      if (h) c.push(h.kind); else if (v) c.push('vac');
      if (sel && i >= sel.s && i <= sel.e) {
        c.push('sel');
        if (i === sel.s || WDAY[i] === 1 || DOM[i] === 1) c.push('s0');
        if (i === sel.e || WDAY[i] === 0 || i === N - 1 || MON[i + 1] !== MON[i]) c.push('s1');
        if (tk[i] && !v) c.push('pk');
      }
      if (ISO[i] === TODAY) c.push('today');
      el.className = c.join(' ');
      var tip = h ? h.name : v ? T.vac_event : '';
      if (tip) el.title = tip; else el.removeAttribute('title');
      if (!weekend(i) && !h) lab++;
      if (S.vmode) {
        if (markable(i)) { el.setAttribute('role', 'button'); el.setAttribute('aria-pressed', String(v)); el.setAttribute('aria-label', longDay(i)); if (!el.hasAttribute('tabindex')) el.tabIndex = -1; }
        else { el.removeAttribute('role'); el.removeAttribute('aria-pressed'); el.removeAttribute('aria-label'); el.removeAttribute('tabindex'); }
      }
    }
    if (S.vmode && !doc.querySelector('.g b[tabindex="0"]')) {
      var first = 0; while (first < N && !markable(first)) first++;
      if (first < N) CELLS[first].tabIndex = 0;
    }
    return lab;
  }

  function vacCount() {
    return Object.keys(S.vac).filter(function (d) { return S.vac[d] && IDX[d] != null && markable(IDX[d]); }).length;
  }

  function hlist(hols) {
    var hasLoc = false;
    var out = hols.map(function (h) {
      var i = IDX[h.date], k = h.kind === 'l' ? S.locals.indexOf(h.date) : -1, lbl = [];
      if (h.kind === 'r') lbl.push(T.lbl_r);
      if (h.kind === 'l') { lbl.push(T.lbl_l); hasLoc = true; }
      if (weekend(i)) lbl.push(WDAY[i] === 6 ? T.lbl_6 : T.lbl_7);
      var rm = k >= 0 ? '<button type="button" class="rm" data-rmloc="' + k + '" aria-label="' + esc(f(T.local_rm_aria, { d: longDay(i) })) + '">×</button>' : '';
      return '<li class="' + h.kind + (weekend(i) ? ' wk' : '') + '"><time datetime="' + h.date + '">' + DOM[i] + ' ' + MON3[MON[i]] + '</time><span>' + esc(h.name) +
        (lbl.length ? '<small>' + lbl.join(' · ') + '</small>' : '') + '</span><em>' + WD3[WDAY[i]] + '</em>' + rm + '</li>';
    }).join('');
    if (S.region === 'canarias' && !S.zone) out += '<li class="z"><time>+1</time><span><button type="button" class="lnk" data-zone>' + T.island_feast + '</button></span><em></em></li>';
    var free = S.locals.filter(function (d) { return !d; }).length;
    if (S.region && free) out += '<li class="z"><time>+' + free + '</time><span><button type="button" class="lnk" data-addloc>' + T.loc_more + '</button></span><em></em></li>';
    $('hlist').classList.toggle('hl-x', hasLoc);
    return out;
  }

  function keepLast(s) { var k = s.lastIndexOf(' '); return k < 0 ? '<span class="nw">' + esc(s) + '</span>' : esc(s.slice(0, k + 1)) + '<span class="nw">' + esc(s.slice(k + 1)) + '</span>'; }
  function zoneText(o) { return !o ? T.zone_prompt : o.slug === 'general' ? T.zone_general : o.name; }

  /* el selector invisible cubre solo el nombre de la comunidad y la flecha, no todo el título */
  function placePick() {
    var sel = $('region'), rn = $('rn');
    if (!sel || !rn) return;
    var box = $('reg-f').getBoundingClientRect(), r = rn.getBoundingClientRect();
    sel.style.left = (r.left - box.left) + 'px'; sel.style.top = (r.top - box.top) + 'px';
    sel.style.width = r.width + 'px'; sel.style.height = r.height + 'px';
  }

  function meta(hols, isCan, lab) {
    return '<a href="#festivos">' + f(T.meta_fest, { n: hols.boe }) + (isCan ? ' ' + T.meta_isle : '') + ' ' + T.meta_loc + '</a>' + SEP +
      '<a href="#puentes">' + tn('meta_pts', PITEMS.length) + '</a>' + SEP + '<span>' + f(T.meta_lab, { n: lab }) + '</span>';
  }

  function render() {
    var hols = holidays(), r = S.region && REG[S.region], z = r && D.zones[S.region];
    HD = offDays(hols).hd;
    var lab = paintYear(hols), isCan = S.region === 'canarias' && !S.zone;
    var zn = z && S.zone ? z.options.filter(function (o) { return o.slug === S.zone; })[0] : null;

    $('hlist').innerHTML = hlist(hols);
    var used = vacCount();
    $('k-v').hidden = !used && !S.vmode;
    $('vcount').textContent = used && !S.vmode ? ' · ' + used : '';
    $('vlabel').textContent = S.vmode ? T.done : T.vmode;
    $('vstat').textContent = used ? tn('vac_days', used) : T.vhint;
    $('vclear').hidden = !used;
    if (!r) return;

    $('rn').innerHTML = keepLast(r.name);
    $('region').value = S.region;
    if (z) {
      $('zone').setAttribute('aria-label', z.label);
      $('zone').innerHTML = (S.region === 'canarias' ? '<option value="">' + T.zone_prompt + '</option>' : '') +
        z.options.map(function (o) { return '<option value="' + o.slug + '"' + (S.zone === o.slug ? ' selected' : '') + '>' + esc(o.name) + '</option>'; }).join('');
      $('zt').innerHTML = keepLast(zoneText(zn));
      $('zone-f').hidden = false;
    } else $('zone-f').hidden = true;
    placePick();

    PITEMS = bridges(hols);
    $('meta').innerHTML = meta(hols, isCan, lab - (isCan ? 1 : 0));
    $('plist').innerHTML = PITEMS.map(function (it, k) { return item(it, takeTxt(it.take), 'p' + k, hols, HD); }).join('') || '<li class="none">' + T.no_bridges + '</li>';
    var lw = longWeekends(hols);
    $('lw').innerHTML = lw.length ? '<h3 class="sub">' + T.h_lw + '</h3><ul class="lw">' + lw.map(function (it) {
      return '<li><time>' + frange(it.s, it.e) + '</time><span>' + it.len + ' ' + T.days + '</span></li>';
    }).join('') + '</ul>' : '';
    VITEMS = plan(hols, S.n, 4);
    $('vlist').innerHTML = VITEMS.map(function (it, k) { return item(it, takeRange(it.take), 'v' + k, hols, HD); }).join('');

    // exportar: la descarga lleva tus locales y vacaciones; las suscripciones, solo lo oficial
    if (icsUrl) URL.revokeObjectURL(icsUrl);
    var label = r.name + (zn && zn.slug !== 'general' ? ' · ' + zn.name : '');
    var suffix = S.zone && S.zone !== 'general' ? '-' + S.zone : '';
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
    hols.forEach(function (h) { var i = IDX[h.date]; ev(h.date.replace(/-/g, '') + '-' + h.kind + '-' + (S.region || 'es'), i, i, h.name); });
    // mis vacaciones: un evento por tramo (dos días de vacaciones con solo fines de semana o festivos en medio son el mismo tramo)
    var hd = offDays(hols).hd, blocks = [];
    Object.keys(S.vac).filter(function (d) { return S.vac[d] && IDX[d] != null; }).map(function (d) { return IDX[d]; })
      .sort(function (a, b) { return a - b; }).forEach(function (d) {
        var last = blocks[blocks.length - 1], joined = !!last;
        if (last) for (var g = last.e + 1; g < d; g++) if (!weekend(g) && !hd[ISO[g]]) joined = false;
        if (joined) last.e = d; else blocks.push({ s: d, e: d });
      });
    blocks.forEach(function (b) { ev('vac-' + ymd(b.s) + '-' + (S.region || 'es'), b.s, b.e, T.vac_event); });
    L.push('END:VCALENDAR');
    return L.join('\r\n') + '\r\n';
  }

  /* ------------------------------------------------------------ estado */
  function loadRegionState() {
    var z = D.zones[S.region];
    S.zone = z ? get('zone.' + S.region) : null;
    if (z && !z.options.some(function (o) { return o.slug === S.zone; })) S.zone = S.region === 'cataluna' ? 'general' : null;
    var l = [];
    try { l = JSON.parse(get('loc.' + S.region) || '[]') || []; } catch (e) { l = []; }
    S.locals = [l[0] || '', l[1] || ''].map(function (d) { return IDX[d] != null ? d : ''; });
    $('l0').value = S.locals[0]; $('l1').value = S.locals[1];
    loadVac();
  }
  function loadVac() {
    S.vac = {};
    try { (JSON.parse(get('vac.' + key()) || '[]') || []).forEach(function (d) { if (IDX[d] != null) S.vac[d] = 1; }); } catch (e) { S.vac = {}; }
  }
  function saveVac() { put('vac.' + key(), JSON.stringify(Object.keys(S.vac).filter(function (d) { return S.vac[d]; }))); }

  function setRegion(slug, push) {
    if (!REG[slug]) return;
    S.region = slug; S.sel = null;
    put('region', slug);
    loadRegionState();
    if (push !== false) {
      try { history.replaceState(null, '', BASE + slug + '/'); } catch (e) { /* file:// */ }
      doc.title = f(T.title_region, { name: REG[slug].name });
    }
    render();
  }

  var toastT = null;
  function toast(msg) {
    var t = $('toast'); t.textContent = msg; t.classList.add('on');
    clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('on'); }, 2400);
  }

  function openPicker(sel) {
    sel.focus();
    try { if (sel.showPicker) sel.showPicker(); } catch (e) { /* sin showPicker o sin gesto */ }
  }

  /* lleva a la vista el mes de la fila elegida, si el calendario está al lado y ese mes no se ve */
  function showSel() {
    if (!S.sel || innerWidth < 1100) return;
    var m = $('m' + (MON[S.sel.s] + 1)), box = $('mainc').getBoundingClientRect(), r = m.getBoundingClientRect();
    if (r.top < Math.max(0, box.top) || r.bottom > Math.min(innerHeight, box.bottom)) m.scrollIntoView({ block: 'nearest', behavior: smooth() });
  }

  /* ------------------------------------------------------------ eventos */
  if (!HOME) {
    $('region').addEventListener('change', function () {
      if (!this.value) { location.href = BASE; return; }
      setRegion(this.value);
    });
    $('zone').addEventListener('change', function () {
      S.zone = this.value || null; S.sel = null;
      put('zone.' + S.region, S.zone);
      render();
    });
    addEventListener('resize', placePick);
    if (doc.fonts && doc.fonts.ready) doc.fonts.ready.then(placePick);
  }

  // festivos locales: "+2 de tu municipio" abre el selector de fecha; fuera de 2027 se avisa
  function addLocal() {
    var k = S.locals[0] ? 1 : 0, inp = $('l' + k);
    try { if (inp.showPicker) { inp.showPicker(); return; } } catch (e) { /* sin showPicker: se enseña el campo */ }
    $('locin').classList.add('show');
    inp.removeAttribute('tabindex'); inp.removeAttribute('aria-hidden');
    inp.focus();
  }
  $('hlist').addEventListener('click', function (e) {
    if (e.target.closest('[data-zone]')) { openPicker($('zone')); return; }
    if (e.target.closest('[data-addloc]')) { addLocal(); return; }
    var b = e.target.closest('[data-rmloc]');
    if (!b) return;
    var k = +b.getAttribute('data-rmloc');
    S.locals[k] = ''; $('l' + k).value = '';
    put('loc.' + S.region, JSON.stringify(S.locals));
    render();
    var add = doc.querySelector('[data-addloc]'); if (add) add.focus();
  });
  [0, 1].forEach(function (k) {
    $('l' + k).addEventListener('change', function () {
      var v = this.value;
      if (v && IDX[v] == null) { this.value = ''; toast(T.loc_out); return; }
      S.locals[k] = v || '';
      if (S.locals[k] && S.vac[v]) { delete S.vac[v]; saveVac(); }
      put('loc.' + S.region, JSON.stringify(S.locals));
      $('locin').classList.remove('show');
      this.setAttribute('tabindex', '-1'); this.setAttribute('aria-hidden', 'true');
      render();
      if (S.locals[k]) toast(f(T.toast_local, { d: longDay(IDX[v]) }));
      var add = doc.querySelector('[data-addloc]'); if (add) add.focus();
    });
  });

  function onPick(list) {
    return function (e) {
      var b = e.target.closest('[data-add],[data-rm]');
      if (b) {
        var add = b.hasAttribute('data-add'), it = list()[+(b.getAttribute('data-add') || b.getAttribute('data-rm')).slice(1)];
        it.take.forEach(function (x) { if (add) S.vac[ISO[x]] = 1; else delete S.vac[ISO[x]]; });
        saveVac(); render();
        toast(f(add ? T.toast_add : T.toast_rm, { t: tn('vac_days', vacCount()) }));
        var again = doc.querySelector('[data-' + (add ? 'rm' : 'add') + ']'); if (again) again.focus();
        return;
      }
      var k = e.target.closest('[data-k]');
      if (!k) return;
      var x = list()[+k.getAttribute('data-k').slice(1)], id = k.getAttribute('data-k');
      S.sel = same(S.sel, x) ? null : x;
      render();
      var back = doc.querySelector('[data-k="' + id + '"]'); if (back) back.focus();
      showSel();
    };
  }
  $('plist').addEventListener('click', onPick(function () { return PITEMS; }));
  $('vlist').addEventListener('click', onPick(function () { return VITEMS; }));

  function setN(v) {
    v = Math.max(1, Math.min(30, parseInt(v, 10) || 1));
    S.n = v; $('vn').value = v; put('n', String(v)); S.sel = null;
    render();
  }
  $('vm').addEventListener('click', function () { setN(S.n - 1); });
  $('vp').addEventListener('click', function () { setN(S.n + 1); });
  $('vn').addEventListener('change', function () { setN(this.value); });

  // marcar vacaciones en el calendario
  function setVmode(on) {
    S.vmode = on;
    if (on) S.sel = null;
    doc.body.classList.toggle('vmode', on);
    $('vhint').hidden = !on;
    if (on) $('year').removeAttribute('aria-hidden'); else $('year').setAttribute('aria-hidden', 'true');
    if (!on) Array.prototype.forEach.call(doc.querySelectorAll('.g b[role]'), function (el) {
      el.removeAttribute('role'); el.removeAttribute('aria-pressed'); el.removeAttribute('aria-label'); el.removeAttribute('tabindex');
    });
    render();
    if (on && innerWidth < 1100) $('ano').scrollIntoView({ behavior: smooth(), block: 'start' });
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
    var c = e.target.closest('b[data-d]');
    if (c) toggleDay(IDX[c.getAttribute('data-d')]);
  });
  $('year').addEventListener('keydown', function (e) {
    if (!S.vmode) return;
    var c = e.target.closest('b[data-d]');
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
  $('vclear').addEventListener('click', function () { S.vac = {}; saveVac(); render(); if (!S.vmode) toast(T.toast_cleared); });
  doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && S.vmode) { setVmode(false); $('vmode').focus(); } });

  $('pr').addEventListener('click', function () { window.print(); });
  $('sh').addEventListener('click', function () {
    var url = location.origin + BASE + (S.region ? S.region + '/' : ''), title = doc.title;
    if (navigator.share) { navigator.share({ title: title, url: url }).catch(function () { /* cancelado */ }); return; }
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { toast(T.toast_copied); }, function () { toast(url); });
    else toast(url);
  });

  /* ------------------------------------------------------------ inicio */
  var n0 = parseInt(get('n'), 10);
  if (n0 >= 1 && n0 <= 30) { S.n = n0; $('vn').value = n0; }
  if (HOME) {
    var q = null;
    try { q = new URLSearchParams(location.search).get('ccaa'); } catch (e) { q = null; }
    if (REG[q]) { location.replace(BASE + q + '/'); return; } // enlaces antiguos ?ccaa=
    var mine = REG[get('region')] && doc.querySelector('#ccaa [data-slug="' + get('region') + '"]');
    if (mine) mine.classList.add('mine');
    loadVac();
    render();
  } else setRegion(PAGE, false);

  // para pruebas automáticas
  window.CL27 = { plan: function (n) { return plan(holidays(), n, 5); }, bridges: function () { return bridges(holidays()); },
    longWeekends: function () { return longWeekends(holidays()); }, holidays: holidays, iso: ISO, ics: function () { return ics(holidays(), 'test'); } };
})();
