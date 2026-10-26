/* Vacaciones 2027: optimizador (el mismo algoritmo que vacopt.py, paso a paso) y la página /vacaciones-2027/<comunidad>/. */
(function (root) {
  'use strict';
  var Y = 2027, N = 365, MIN_BREAK = 5, MAX_DAYS = 30;
  var ISO = [], MON = [], WD = [], DOM = [];
  for (var i0 = 0; i0 < N; i0++) {
    var d0 = new Date(Date.UTC(Y, 0, 1 + i0));
    ISO.push(d0.toISOString().slice(0, 10)); MON.push(d0.getUTCMonth()); WD.push((d0.getUTCDay() + 6) % 7); DOM.push(d0.getUTCDate());
  }
  var IDX = {}; ISO.forEach(function (s, k) { IDX[s] = k; });

  function offDays(dates) {
    var hd = {}, o = [];
    dates.forEach(function (x) { hd[x] = 1; });
    for (var i = 0; i < N; i++) o.push(WD[i] >= 5 || !!hd[ISO[i]]);
    return o;
  }

  /* Breaks that can start at day i, shortest first: [end, cost, length]. Same as candidates() in vacopt.py. */
  function candidates(off, i, taken, blocked, cap, minLen, n) {
    var out = [], c = 0, tk = 0;
    for (var e = i; e < N; e++) {
      if (!off[e]) {
        if (taken[e]) tk++;
        else if (blocked[MON[e]]) break;
        c++;
        if (c > n) break;
      }
      var ln = e - i + 1, nw = c - tk;
      if (nw > 0 && ln > cap) break;
      if (c >= 1 && (e + 1 >= N || (!off[e + 1] && !taken[e + 1])) &&
          ((tk > 0 && nw === 0) || (ln <= cap && (ln >= minLen || tk > 0)))) out.push([e, c, ln]);
    }
    return out;
  }

  /* Exact DP: f[i][u] = best total for days before i using u days, day i-1 a working day left as working. */
  function optimize(off, n, takenList, blockedMonths, maxLen, minLen) {
    var taken = {}, nt = 0, m, u, k;
    (takenList || []).forEach(function (x) { if (x >= 0 && x < N && !off[x] && !taken[x]) { taken[x] = 1; nt++; } });
    n = Math.max(n, nt);
    var blocked = []; for (m = 0; m < 12; m++) blocked.push(false);
    (blockedMonths || []).forEach(function (x) { blocked[x] = true; });
    var cap = maxLen > 0 ? maxLen : N;
    minLen = Math.min(minLen == null ? MIN_BREAK : minLen, cap);
    var W = n + 1, S = (N + 2) * W;
    var f = new Int32Array(S).fill(-1), bi = new Int32Array(S), bu = new Int32Array(S), be = new Int32Array(S);
    f[0] = 0;
    for (var i = 0; i < N; i++) {
      var cands = null, canStart = i === 0 || !off[i - 1];
      for (u = 0; u <= n; u++) {
        var v = f[i * W + u];
        if (v < 0) continue;
        k = (i + 1) * W + u;
        if (!taken[i] && f[k] < v) { f[k] = v; bi[k] = i; bu[k] = u; be[k] = -1; }
        if (!canStart) continue;
        if (!cands) cands = candidates(off, i, taken, blocked, cap, minLen, n);
        for (var q = 0; q < cands.length; q++) {
          var e = cands[q][0], c = cands[q][1];
          if (u + c > n) break;
          k = (e + 1 >= N ? N + 1 : e + 2) * W + u + c;
          if (f[k] < v + cands[q][2]) { f[k] = v + cands[q][2]; bi[k] = i; bu[k] = u; be[k] = e; }
        }
      }
    }
    var best = -1, BU = 0, BJ = 0;
    for (u = 0; u <= n; u++) for (var j = N; j <= N + 1; j++) if (f[j * W + u] > best) { best = f[j * W + u]; BU = u; BJ = j; }
    if (best < 0) return null;
    var breaks = [], jj = BJ, uu = BU;
    while (jj > 0) {
      k = jj * W + uu;
      if (be[k] >= 0) {
        var s = bi[k], t = [];
        for (var x = s; x <= be[k]; x++) if (!off[x]) t.push(x);
        breaks.push({ s: s, e: be[k], len: be[k] - s + 1, take: t });
      }
      jj = bi[k]; uu = bu[k];
    }
    breaks.reverse();
    return { total: best, used: BU, breaks: breaks };
  }

  var SHORT = { 'Lunes siguiente a la Asunción de la Virgen': 'Asunción', 'Sustitución del 15 de agosto': 'Asunción',
    'Fiesta Nacional de España': 'Fiesta Nacional', 'Día de la Constitución Española': 'Constitución', 'Inmaculada Concepción': 'Inmaculada' };
  var MONTHS = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var cap1 = function (s) { return s.charAt(0).toUpperCase() + s.slice(1); };
  /* Same as break_name() in vacopt.py. hols: [{date, name}] */
  function breakName(b, hols) {
    var s = ISO[b.s], e = ISO[b.e];
    if (s <= '2027-03-29' && e >= '2027-03-25') return 'Semana Santa';
    if (s <= '2027-01-06' || e >= '2027-12-24') return 'Navidad';
    var seen = {}, names = [];
    hols.forEach(function (h) {
      if (h.date >= s && h.date <= e && WD[IDX[h.date]] < 5) { var nm = SHORT[h.name] || h.name; if (!seen[nm]) { seen[nm] = 1; names.push(nm); } }
    });
    if (names.length) return names.join(' · ');
    var a = MON[b.s], z = MON[b.e];
    return a === z ? cap1(MONTHS[a]) : cap1(MONTHS[a]) + '-' + MONTHS[z];
  }

  var API = { optimize: optimize, offDays: offDays, breakName: breakName, iso: ISO, N: N, MIN_BREAK: MIN_BREAK };
  if (typeof module !== 'undefined' && module.exports) { module.exports = API; return; }
  root.VAC = API;
  if (typeof document === 'undefined' || !document.getElementById('vac-data')) return;

  /* ------------------------------------------------------------ página */
  var doc = document, $ = function (id) { return doc.getElementById(id); };
  var all = function (sel, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(sel)); };
  var D = JSON.parse($('vac-data').textContent);
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var wd3 = D.wd3, mon3 = D.mon3;
  function dshort(i) { return wd3[WD[i]] + ' ' + DOM[i] + ' ' + mon3[MON[i]]; }
  function drange(a, b) { return MON[a] === MON[b] ? wd3[WD[a]] + ' ' + DOM[a] + ' – ' + dshort(b) : dshort(a) + ' – ' + dshort(b); }
  function ndays(n) { return n === 1 ? '1 día' : n + ' días'; }
  var mmdd = function (i) { return ISO[i].slice(5, 7) + ISO[i].slice(8, 10); };

  /* estado: URL > valores por defecto. Nada en localStorage: un enlace compartido muestra lo mismo a todos */
  var P = null; try { P = new URLSearchParams(location.search); } catch (e) { P = null; }
  var gp = function (k) { return P ? P.get(k) : null; };
  if (D.hub) { // /vacaciones-2027/?c=...: a la página de la comunidad, con el resto de parámetros
    var c0 = gp('c');
    if (c0 && D.regions.indexOf(c0) >= 0) { P.delete('c'); var q0 = P.toString(); location.replace(D.base + c0 + '/' + (q0 ? '?' + q0 : '')); return; }
    var rs = $('vreg');
    if (rs) rs.addEventListener('change', function () { if (this.value) location.href = D.base + this.value + '/' + (S0n() !== 22 ? '?d=' + S0n() : ''); });
    var S0n = function () { var v = parseInt(($('dn') || {}).value, 10); return v >= 1 && v <= MAX_DAYS ? v : 22; };
    stepper(function () {});
    return;
  }
  function stepper(onChange) {
    var inp = $('dn');
    if (!inp) return;
    function set(v) { v = Math.max(1, Math.min(MAX_DAYS, parseInt(v, 10) || 1)); inp.value = v; onChange(v); }
    $('dm').addEventListener('click', function () { set(+inp.value - 1); });
    $('dp').addEventListener('click', function () { set(+inp.value + 1); });
    inp.addEventListener('change', function () { set(inp.value); });
  }

  var S = { n: 22, m: '', x: [], min: MIN_BREAK, max: 0, t: {} };
  var pn = parseInt(gp('d'), 10); if (pn >= 1 && pn <= MAX_DAYS) S.n = pn;
  var pm = gp('m') || '';
  if (D.zones.some(function (z) { return z[0] === pm; }) || D.cities.some(function (c) { return c[0] === pm; })) S.m = pm;
  (gp('x') || '').split('.').forEach(function (v) { var m = parseInt(v, 10); if (m >= 1 && m <= 12 && S.x.indexOf(m - 1) < 0) S.x.push(m - 1); });
  var pmin = parseInt(gp('min'), 10); if (pmin >= 1 && pmin <= 30) S.min = pmin;
  var pmax = parseInt(gp('max'), 10); if (pmax >= 1 && pmax <= 60) S.max = pmax;
  (gp('t') || '').split('.').forEach(function (v) { var k = IDX[Y + '-' + v.slice(0, 2) + '-' + v.slice(2, 4)]; if (v.length === 4 && k != null) S.t[k] = 1; });

  function holidays() {
    var out = D.hols.map(function (h) { return { date: h[0], name: h[1], kind: h[2] }; });
    var zone = null, city = null;
    D.cities.forEach(function (c) { if (c[0] === S.m) city = c; });
    var zs = city ? city[2] : S.m;
    D.zones.forEach(function (z) { if (z[0] === zs) zone = z; });
    if (zone) {
      if (zone[4]) out = out.filter(function (h) { return h.date !== zone[4]; });
      if (zone[2]) out.push({ date: zone[2], name: zone[3], kind: D.region === 'canarias' ? 'i' : 'r' });
    }
    if (city) city[3].forEach(function (l) { out.push({ date: l[0], name: l[1], kind: 'l' }); });
    out.sort(function (a, b) { return a.date < b.date ? -1 : a.date > b.date ? 1 : 0; });
    return out;
  }
  function place() {
    var nm = D.name;
    D.cities.forEach(function (c) { if (c[0] === S.m) nm = c[4] || c[1]; });
    D.zones.forEach(function (z) { if (z[0] === S.m && z[2]) nm = z[1]; });
    return nm;
  }

  function shareUrl() {
    var q = [];
    if (S.m) q.push('m=' + S.m);
    if (S.n !== 22) q.push('d=' + S.n);
    if (S.x.length) q.push('x=' + S.x.slice().sort(function (a, b) { return a - b; }).map(function (m) { return m + 1; }).join('.'));
    if (S.min !== MIN_BREAK) q.push('min=' + S.min);
    if (S.max) q.push('max=' + S.max);
    var t = Object.keys(S.t).map(Number).sort(function (a, b) { return a - b; });
    if (t.length) q.push('t=' + t.map(mmdd).join('.'));
    return D.base + D.region + '/' + (q.length ? '?' + q.join('&') : '');
  }

  var CELLS = [];
  all('#year td[data-d]').forEach(function (el) { CELLS[IDX[el.getAttribute('data-d')]] = el; });
  var R = null, HOLS = [], OFF = [], focusIdx = null;

  function render() {
    HOLS = holidays();
    OFF = offDays(HOLS.map(function (h) { return h.date; }));
    Object.keys(S.t).forEach(function (k) { if (OFF[k]) delete S.t[k]; });
    var tl = Object.keys(S.t).map(Number);
    if (tl.length > S.n) { S.n = tl.length; }
    $('dn').value = S.n;
    var t0 = (typeof performance !== 'undefined' ? performance.now() : 0);
    R = optimize(OFF, S.n, tl, S.x, S.max, S.min) || { total: 0, used: 0, breaks: [] };
    API.ms = (typeof performance !== 'undefined' ? performance.now() : 0) - t0;
    paint();
    var nm = place();
    $('vtot').textContent = R.total;
    $('vsub').textContent = 'con ' + ndays(R.used) + ' de vacaciones · ' + nm;
    var rows = R.breaks.slice().sort(function (a, b) { return b.len - a.len || a.s - b.s; });
    $('blist').innerHTML = rows.map(row).join('') || '<tr><td colspan="3">–</td></tr>';
    var nt = Object.keys(S.t).length;
    $('k-tk').hidden = !nt;
    all('[data-m]').forEach(function (b) { b.setAttribute('aria-pressed', String(S.x.indexOf(+b.getAttribute('data-m')) >= 0)); });
    for (var m = 1; m <= 12; m++) { var mc = $('m' + m); if (mc) mc.classList.toggle('mx', S.x.indexOf(m - 1) >= 0); }
    try { history.replaceState(null, '', shareUrl()); } catch (e) { /* file:// */ }
    var wa = $('swa');
    if (wa) wa.href = 'https://wa.me/?text=' + encodeURIComponent(challenge());
    scheduleCard();
  }
  function row(b) {
    var take = b.take.length > 1 ? drange(b.take[0], b.take[b.take.length - 1]) : dshort(b.take[0]);
    return '<tr><td class="c-p"><span class="rng">' + drange(b.s, b.e) + '</span><span class="m nm">' + esc(breakName(b, HOLS)) + '</span></td>' +
      '<td class="num">' + ndays(b.len) + '</td><td class="c-v"><span class="mo">' + ndays(b.take.length) + ' de vacaciones: </span><b class="dk">' +
      b.take.length + '</b> <span class="m">' + take + '</span></td></tr>';
  }
  function paint() {
    var hd = {}, vac = {}, br = {};
    HOLS.forEach(function (h) { if (!hd[h.date]) hd[h.date] = h; });
    R.breaks.forEach(function (b) { for (var x = b.s; x <= b.e; x++) { br[x] = 1; if (!OFF[x]) vac[x] = 1; } });
    if (focusIdx == null) focusIdx = R.breaks.length ? R.breaks[0].take[0] : 0;
    for (var i = 0; i < N; i++) {
      var el = CELLS[i];
      if (!el) continue;
      var h = hd[ISO[i]], c = [];
      if (WD[i] >= 5) c.push('we');
      if (h) c.push(h.kind); else if (S.t[i]) c.push('v', 'tk'); else if (vac[i]) c.push('v');
      if (br[i]) c.push('br');
      el.className = c.join(' ');
      var tip = h ? h.name : S.t[i] ? D.k_tk : vac[i] ? D.k_v : '';
      if (tip) el.title = tip; else el.removeAttribute('title');
      el.setAttribute('aria-label', cap1(D.wd[WD[i]] + ' ' + DOM[i] + ' de ' + MONTHS[MON[i]]) + (tip ? ' · ' + tip : ''));
      el.tabIndex = i === focusIdx ? 0 : -1;
    }
    for (var m = 1; m <= 12; m++) {
      var ul = $('mh' + m);
      if (ul) ul.innerHTML = HOLS.filter(function (h) { return MON[IDX[h.date]] === m - 1; }).map(function (h) {
        return '<li class="k-' + h.kind + (WD[IDX[h.date]] >= 5 ? ' we' : '') + '"><b>' + DOM[IDX[h.date]] + '</b> ' + esc(h.name) + '</li>';
      }).join('');
    }
  }

  /* ------------------------------------------------------------ eventos */
  stepper(function (v) { S.n = v; render(); });
  if ($('vreg')) $('vreg').addEventListener('change', function () {
    var q = []; if (S.n !== 22) q.push('d=' + S.n);
    location.href = D.base + this.value + '/' + (q.length ? '?' + q.join('&') : '');
  });
  if ($('vmun')) { $('vmun').value = S.m; $('vmun').addEventListener('change', function () { S.m = this.value; render(); }); }
  all('[data-m]').forEach(function (b) {
    b.addEventListener('click', function () {
      var m = +b.getAttribute('data-m'), k = S.x.indexOf(m);
      if (k >= 0) S.x.splice(k, 1); else S.x.push(m);
      render();
    });
  });
  if ($('vmin')) { $('vmin').value = String(S.min); $('vmin').addEventListener('change', function () { S.min = +this.value; render(); }); }
  if ($('vmax')) { $('vmax').value = String(S.max); $('vmax').addEventListener('change', function () { S.max = +this.value; render(); }); }
  if (S.x.length || S.min !== MIN_BREAK || S.max) { var od = $('vopt'); if (od) od.open = true; }
  function toggleDay(i) {
    if (OFF[i]) return;
    if (S.t[i]) delete S.t[i]; else S.t[i] = 1;
    focusIdx = i;
    render();
    if (CELLS[i]) CELLS[i].focus({ preventScroll: true });
  }
  if ($('year')) {
    $('year').addEventListener('click', function (e) { var c = e.target.closest('td[data-d]'); if (c) toggleDay(IDX[c.getAttribute('data-d')]); });
    $('year').addEventListener('keydown', function (e) {
      var c = e.target.closest('td[data-d]');
      if (!c) return;
      var i = IDX[c.getAttribute('data-d')], step = { ArrowRight: 1, ArrowLeft: -1, ArrowDown: 7, ArrowUp: -7 }[e.key];
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleDay(i); return; }
      if (!step) return;
      e.preventDefault();
      var j = Math.max(0, Math.min(N - 1, i + step));
      if (CELLS[focusIdx]) CELLS[focusIdx].tabIndex = -1;
      focusIdx = j; CELLS[j].tabIndex = 0; CELLS[j].focus();
    });
  }
  if ($('tkclear')) $('tkclear').addEventListener('click', function () { S.t = {}; render(); });

  /* ------------------------------------------------------------ tarjeta para compartir */
  var FONT = '"Public Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
  var COL = { ink: '#1b1f24', mut: '#5b6472', line: '#d5dae1', we: '#eef0f3', red: '#c8102e', bg: '#fff',
    n: '#f4b8b1', r: '#f6d27a', i: '#a9dfd6', l: '#cbbdf5', v: '#5f93d3', br: '#b9d3f2' };
  function headline() { return 'Con ' + ndays(R.used) + ' de vacaciones tengo ' + R.total + ' días libres en 2027 · ' + place(); }
  function absUrl() { return D.site + shareUrl(); }
  function challenge() { return '¿Cuántos días libres sacas tú en 2027? Yo ' + R.total + ' con ' + R.used + ' de vacaciones 👉 ' + absUrl(); }

  function strip(g, x0, y0, w, rows, maxH) {
    /* the year as weeks (columns) x weekdays (rows), split in `rows` bands; returns the height used */
    var kind = {}, vac = {}, br = {};
    HOLS.forEach(function (h) { kind[IDX[h.date]] = h.kind; });
    R.breaks.forEach(function (b) { for (var x = b.s; x <= b.e; x++) { br[x] = 1; if (!OFF[x]) vac[x] = 1; } });
    var start = WD[0], weeks = Math.ceil((N + start) / 7), per = Math.ceil(weeks / rows);
    var c = Math.min(Math.floor(w / per), Math.floor(maxH / (rows * 8.7))), gap = Math.max(2, Math.round(c * 0.14)), lab = Math.round(c * 0.9), y = y0;
    for (var band = 0; band < rows; band++) {
      var wk0 = band * per;
      g.font = '600 ' + Math.round(c * 0.62) + 'px ' + FONT; g.textBaseline = 'alphabetic';
      for (var i = 0; i < N; i++) {
        var p = i + start, wk = Math.floor(p / 7) - wk0, dw = p % 7;
        if (wk < 0 || wk >= per) continue;
        var x = x0 + wk * c, yy = y + lab + dw * c;
        if (DOM[i] === 1) { g.fillStyle = COL.mut; g.fillText(cap1(mon3[MON[i]].replace('.', '')), x + gap / 2, y + lab - Math.round(c * 0.3)); }
        var k = kind[i];
        g.fillStyle = vac[i] ? COL.v : (k && WD[i] < 5) ? COL[k] : br[i] ? COL.br : WD[i] >= 5 ? COL.we : COL.bg;
        g.fillRect(x + gap / 2, yy + gap / 2, c - gap, c - gap);
        if (!vac[i] && !br[i] && !(k && WD[i] < 5) && WD[i] < 5) { g.strokeStyle = COL.line; g.lineWidth = 1.5; g.strokeRect(x + gap / 2 + .75, yy + gap / 2 + .75, c - gap - 1.5, c - gap - 1.5); }
      }
      y += lab + 7 * c + Math.round(c * 0.8);
    }
    return y - y0;
  }
  function brand(g, x, y, s) {
    g.fillStyle = COL.red; g.fillRect(x, y - s * 0.62, s * 0.5, s * 0.5);
    g.textBaseline = 'alphabetic'; g.font = '700 ' + s + 'px ' + FONT; g.fillStyle = COL.ink;
    var t = 'elcalendariolaboral'; g.fillText(t, x + s * 0.8, y);
    var w = g.measureText(t).width; g.font = '400 ' + s + 'px ' + FONT; g.fillStyle = COL.mut; g.fillText('.es', x + s * 0.8 + w, y);
  }
  function fit(g, text, weight, size, maxW) {
    g.font = weight + ' ' + size + 'px ' + FONT;
    while (g.measureText(text).width > maxW && size > 12) { size -= 2; g.font = weight + ' ' + size + 'px ' + FONT; }
    return size;
  }
  function drawCard(w, h) {
    var cv = doc.createElement('canvas'); cv.width = w; cv.height = h;
    var g = cv.getContext('2d'), tall = h > w, M = tall ? 80 : 64;
    g.fillStyle = COL.bg; g.fillRect(0, 0, w, h);
    brand(g, M, M + 40, tall ? 44 : 34);
    var nm = place(), used = ndays(R.used), big = String(R.total);
    g.textBaseline = 'alphabetic';
    if (tall) {
      fit(g, 'Con ' + used + ' de vacaciones tengo', '600', 54, w - 2 * M); g.fillStyle = COL.mut; g.fillText('Con ' + used + ' de vacaciones tengo', M, 262);
      g.font = '700 290px ' + FONT; g.fillStyle = COL.ink; g.fillText(big, M - 12, 535);
      var bw = g.measureText(big).width;
      g.font = '700 76px ' + FONT; g.fillText('días', M + bw + 16, 452); g.fillText('libres', M + bw + 16, 533);
      fit(g, 'en 2027 · ' + nm, '700', 60, w - 2 * M); g.fillStyle = COL.ink; g.fillText('en 2027 · ' + nm, M, 630);
      strip(g, M, 690, w - 2 * M, 2, h - 150 - 690);
      g.font = '700 38px ' + FONT; g.fillStyle = COL.ink; g.fillText(D.host + '/vacaciones-2027', M, h - 72);
    } else {
      fit(g, 'Con ' + used + ' de vacaciones tengo', '600', 40, w - 2 * M); g.fillStyle = COL.mut; g.fillText('Con ' + used + ' de vacaciones tengo', M, 190);
      g.font = '700 170px ' + FONT; g.fillStyle = COL.ink; g.fillText(big, M - 8, 345);
      var bw2 = g.measureText(big).width;
      g.font = '700 60px ' + FONT; g.fillText('días libres', M + bw2 + 20, 345);
      fit(g, 'en 2027 · ' + nm, '700', 44, w - 2 * M - 300); g.fillText('en 2027 · ' + nm, M, 408);
      strip(g, M, 440, w - 2 * M, 1, h - 440 - 24);
      g.font = '700 28px ' + FONT; g.fillStyle = COL.ink;
      var u = D.host + '/vacaciones-2027'; g.fillText(u, w - M - g.measureText(u).width, M + 40);
    }
    return cv;
  }
  var cardT = null, cardBlob = null, cardUrl = null, fontsReady = null;
  function fonts() {
    if (!fontsReady) fontsReady = doc.fonts && doc.fonts.load ? Promise.all(['700 100px "Public Sans"', '600 50px "Public Sans"', '400 40px "Public Sans"'].map(function (f) { return doc.fonts.load(f); })).catch(function () {}) : Promise.resolve();
    return fontsReady;
  }
  function scheduleCard() {
    clearTimeout(cardT);
    cardT = setTimeout(function () {
      fonts().then(function () {
        var cv = drawCard(1080, 1350);
        cv.toBlob(function (b) {
          cardBlob = b;
          if (cardUrl) URL.revokeObjectURL(cardUrl);
          cardUrl = URL.createObjectURL(b);
          var im = $('vcard'); if (im) { im.src = cardUrl; im.alt = headline(); im.hidden = false; }
        }, 'image/png');
      });
    }, 120);
  }
  API.card = drawCard; API.state = S; API.result = function () { return R; }; API.headline = function () { return headline(); }; API.challenge = function () { return challenge(); };

  var toastT = null;
  function toast(msg) { var t = $('toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(function () { t.classList.remove('on'); }, 2400); }
  function copy(text, msg) {
    function old() { var a = doc.createElement('textarea'); a.value = text; doc.body.appendChild(a); a.select(); try { doc.execCommand('copy'); toast(msg); } catch (e) { /* nada */ } a.remove(); }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(function () { toast(msg); }, old); else old();
  }
  function download(w, h) {
    fonts().then(function () {
      drawCard(w, h).toBlob(function (b) {
        var a = doc.createElement('a'), u = URL.createObjectURL(b);
        a.href = u; a.download = 'vacaciones-2027-' + D.region + (S.m ? '-' + S.m : '') + '-' + w + 'x' + h + '.png';
        doc.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(u); }, 4000);
      }, 'image/png');
    });
  }
  var sh = $('sshare');
  if (sh) {
    if (!navigator.share) sh.hidden = true;
    sh.addEventListener('click', function () {
      var data = { text: challenge() };
      if (cardBlob && typeof File !== 'undefined') {
        var file = new File([cardBlob], 'vacaciones-2027.png', { type: 'image/png' });
        if (navigator.canShare && navigator.canShare({ files: [file] })) data.files = [file];
      }
      navigator.share(data).catch(function () { /* cancelado */ });
    });
  }
  if ($('slink')) $('slink').addEventListener('click', function () { copy(absUrl(), 'Enlace copiado'); });
  if ($('sreto')) $('sreto').addEventListener('click', function () {
    if (navigator.share) navigator.share({ text: challenge() }).catch(function () { /* cancelado */ });
    else copy(challenge(), 'Reto copiado');
  });
  all('[data-img]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var s = a.getAttribute('data-img').split('x'); download(+s[0], +s[1]);
      var dd = a.closest('details'); if (dd) dd.open = false;
    });
  });

  render();
})(this);
