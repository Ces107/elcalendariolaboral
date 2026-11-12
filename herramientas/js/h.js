/* Runtime of the tools (herramientas/): ONE script for every tool. A tool is a declarative definition in
   herramientas/tools/<slug>.py; its compute function becomes utilidades/a/t-<slug>.js, which calls H.run(fn).
   Pure helpers first (node runs them in herramientas/test_herramientas.py), then the browser runtime: it reads the
   input spec from #h-data, wires the form, calls compute(v, H, C) on every change, renders the result and keeps the
   form in the URL (shareable). Dates are UTC midnight. */
(function (root) {
  'use strict';
  var DAY = 864e5;

  function parse(s) {
    if (!/^\d{4}-\d\d-\d\d$/.test(s || '')) return null;
    var p = s.split('-'), d = new Date(Date.UTC(+p[0], +p[1] - 1, +p[2]));
    return isNaN(d) || d.getUTCDate() !== +p[2] ? null : d;
  }
  function iso(d) { return d.toISOString().slice(0, 10); }
  function add(d, n) { return new Date(d.getTime() + n * DAY); }
  function diff(a, b) { return Math.round((b - a) / DAY); } /* b - a in days */
  function leap(y) { return (y % 4 === 0 && y % 100 !== 0) || y % 400 === 0; }
  function yearDays(y) { return leap(y) ? 366 : 365; }
  function monthDays(y, m) { return new Date(Date.UTC(y, m, 0)).getUTCDate(); } /* m: 1..12 */
  function wd(d) { return (d.getUTCDay() + 6) % 7; } /* 0 = Monday ... 6 = Sunday */
  function r2(x) { return Math.round((x + (x >= 0 ? 1e-9 : -1e-9)) * 100) / 100; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  /* 1234.5 -> '1.234,50' (dot every 3 digits, comma for decimals) */
  function num(x, dec) {
    if (dec === undefined) dec = 2;
    var neg = x < 0, s = Math.abs(x).toFixed(dec).split('.'), i = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    return (neg && +s.join('') !== 0 ? '−' : '') + i + (s[1] ? ',' + s[1] : '');
  }
  function eur(x) { return num(x, 2) + ' €'; }
  /* Typed number -> Number; empty or junk -> NaN. Currency symbols/codes, %, spaces are stripped; '−' is a minus.
     Both separators present: the LAST one is the decimal mark ('1.234,56' = '1,234.56' = 1234.56) in any language.
     lang 'es' (default; H.lang = page language): ',' decimal; '.' thousands only as full groups ('36.000' = 36000,
       '1.234.567'), otherwise decimal ('12.5', '1.25').
     lang 'en': '.' decimal; ',' thousands as full groups ('1,234' = 1234, '$1,234.50'); a single comma that is not
       a full group is read as a decimal comma ('12,5' = 12.5). */
  function val(s, lang) {
    s = String(s == null ? '' : s).replace(/[\s  €£¥₹%]|(?:US|CA|AU|C|A)?\$|EUR|USD|GBP|CAD|AUD/gi, '').replace(/^\+/, '').replace(/^[−–]/, '-');
    var en = (lang || H.lang) === 'en', c = s.indexOf(','), d = s.indexOf('.');
    if (c >= 0 && d >= 0) s = s.lastIndexOf(',') > s.lastIndexOf('.') ? s.replace(/\./g, '').replace(',', '.') : s.replace(/,/g, '');
    else if (c >= 0) s = (en || s.indexOf(',', c + 1) >= 0) && /^-?\d{1,3}(,\d{3})+$/.test(s) ? s.replace(/,/g, '') : s.replace(',', '.');
    else if (d >= 0 && /^-?\d{1,3}(\.\d{3})+$/.test(s) && (!en || s.indexOf('.', d + 1) >= 0)) s = s.replace(/\./g, '');
    if (!/^-?\d*\.?\d+$/.test(s)) return NaN;
    return parseFloat(s);
  }
  function plural(n, one, other) { return n === 1 ? one : other; }

  /* Holidays of a place, as /dias-habiles/ (util.js): hol = {nat, reg, zon, cit}; r = comunidad slug or '';
     m = municipality slug, 'z:<zone>' or ''. Returns [[iso, name, kind]] sorted; kind n|r|i|l. */
  function holidays(hol, r, m) {
    var list = (r && hol.reg[r] ? hol.reg[r] : hol.nat).slice(), city = null, zone = null;
    if (r && m) {
      city = (hol.cit[r] || []).filter(function (c) { return c[0] === m; })[0] || null;
      var zs = m.indexOf('z:') === 0 ? m.slice(2) : city && city[2];
      zone = (hol.zon[r] || []).filter(function (z) { return z[0] === zs; })[0] || null;
    }
    if (zone) list = list.filter(function (h) { return zone[3].indexOf(h[0]) < 0; }).concat(zone[2]);
    if (city) list = list.concat(city[3].map(function (h) { return [h[0], h[1], 'l']; }));
    return list.sort(function (x, y) { return x[0] < y[0] ? -1 : x[0] > y[0] ? 1 : 0; });
  }
  function holidayMap(list) { var o = {}; list.forEach(function (h) { if (!o[h[0]]) o[h[0]] = h; }); return o; }

  /* RFC 5545 */
  function icsEsc(s) { return String(s).replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\n/g, '\\n'); }
  function icsDate(d) { return iso(d).replace(/-/g, ''); }

  /* raw form value -> what compute() gets, by input type (spec from the tool definition). For 'place', raw is
     {r, m} and the value is the holiday list of that place. */
  function read(spec, raw, C) {
    switch (spec.type) {
      case 'number': case 'money': return val(raw);
      case 'date': return parse(raw);
      case 'check': return raw === true || raw === '1' || raw === 'on';
      case 'place': raw = raw || {}; return holidays(C.hol, raw.r || '', raw.m || '');
      default: return raw == null ? '' : String(raw);
    }
  }

  var H = { DAY: DAY, parse: parse, iso: iso, add: add, diff: diff, leap: leap, yearDays: yearDays, monthDays: monthDays, wd: wd,
    r2: r2, esc: esc, num: num, eur: eur, val: val, plural: plural, holidays: holidays, holidayMap: holidayMap, icsEsc: icsEsc,
    icsDate: icsDate, read: read, lang: 'es' /* page language: how val() reads separators (run() sets it) */ };
  if (typeof module === 'object' && module.exports) { module.exports = H; return; }
  root.H = H;
  if (typeof document === 'undefined') return;
  H.lang = (document.documentElement.lang || 'es').slice(0, 2);

  /* ------------------------------------------------------------ browser */
  var doc = document, $ = function (id) { return doc.getElementById(id); };
  var each = function (xs, fn) { Array.prototype.forEach.call(xs, fn); };
  H.$ = $;
  H.today = function () { var n = new Date(); return new Date(Date.UTC(n.getFullYear(), n.getMonth(), n.getDate())); };

  /* hub: filter the cards as you type (accents and case ignored) */
  var hq = $('hub-q');
  if (hq) {
    var norm = function (s) { return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); };
    hq.addEventListener('input', function () {
      var q = norm(hq.value.trim()), any = false;
      each(doc.querySelectorAll('.hcat'), function (sec) {
        var n = 0;
        each(sec.querySelectorAll('.hgrid li'), function (li) {
          var ok = !q || norm(li.getAttribute('data-k') || li.textContent).indexOf(q) >= 0;
          li.hidden = !ok; if (ok) n++;
        });
        sec.hidden = !n; if (n) any = true;
      });
      $('hub-none').hidden = any;
    });
  }

  H.run = function (compute) {
    var el = $('h-data');
    if (!el) return;
    var C = JSON.parse(el.textContent), S = C.s, specs = C.inputs, out = $('out'), touched = false;
    if (C.lang) H.lang = C.lang;
    var q = new URLSearchParams(location.search);

    /* place pickers */
    function fillMun(id) {
      var reg = $(id + '-r'), mun = $(id + '-m'), r = reg.value, hol = C.hol;
      var zs = r ? hol.zon[r] || [] : [], cs = r ? hol.cit[r] || [] : [], kind = r === 'canarias' ? S.isla : S.zona;
      $(id + '-mf').hidden = !zs.length && !cs.length;
      mun.innerHTML = '<option value="">' + esc(S.all_region) + '</option>' +
        zs.map(function (z) { return '<option value="z:' + z[0] + '">' + esc(z[1]) + ' (' + kind + ')</option>'; }).join('') +
        cs.map(function (c) { return '<option value="' + c[0] + '">' + esc(c[1]) + '</option>'; }).join('');
    }
    function rawOf(s) {
      if (s.type === 'place') return { r: $(s.id + '-r').value, m: $(s.id + '-m').value };
      if (s.type === 'seg') { var on = doc.querySelector('[data-seg="' + s.id + '"] .on'); return on ? on.getAttribute('data-v') : ''; }
      if (s.type === 'check') return $(s.id).checked;
      return $(s.id).value;
    }
    function setRaw(s, v) {
      if (s.type === 'place') {
        var reg = $(s.id + '-r');
        if (v.r !== undefined && (v.r === '' || C.hol.reg[v.r])) { reg.value = v.r; fillMun(s.id); }
        if (v.m) $(s.id + '-m').value = v.m;
      } else if (s.type === 'seg') {
        each(doc.querySelectorAll('[data-seg="' + s.id + '"] button'), function (b) {
          var on = b.getAttribute('data-v') === v; b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on));
        });
      } else if (s.type === 'check') $(s.id).checked = v === true || v === '1';
      else $(s.id).value = v;
    }
    function applySets(s) { /* an option may set other inputs (presets) */
      var v = rawOf(s), o = (s.options || []).filter(function (x) { return x[0] === v; })[0];
      if (o && o[2]) Object.keys(o[2]).forEach(function (k) { var t = specs.filter(function (x) { return x.id === k; })[0]; if (t) setRaw(t, o[2][k]); });
    }
    function presetOf(id) { /* a field a preset fills was edited by hand: show the matching preset, or the 'custom' one */
      specs.forEach(function (s) {
        var opts = (s.options || []).filter(function (o) { return o[2] && id in o[2]; });
        if (!opts.length) return;
        var hit = opts.filter(function (o) {
          return Object.keys(o[2]).every(function (k) { var t = specs.filter(function (x) { return x.id === k; })[0]; return t && String(rawOf(t)) === String(o[2][k]); });
        })[0];
        var v = hit ? hit[0] : s.custom;
        if (v !== undefined) setRaw(s, v);
      });
    }
    function visible() {
      specs.forEach(function (s) {
        if (!s.show) return;
        var f = $(s.id + '-f'), cur = rawOf(specs.filter(function (x) { return x.id === s.show[0]; })[0]);
        if (f) f.hidden = s.show[1].indexOf(String(cur)) < 0;
      });
    }
    function values() {
      var v = {};
      specs.forEach(function (s) {
        var raw = rawOf(s);
        v[s.id] = read(s, raw, C);
        if (s.type === 'place') {
          var reg = $(s.id + '-r'), mun = $(s.id + '-m');
          v[s.id + '_label'] = raw.r ? (raw.m ? mun.options[mun.selectedIndex].text + ' · ' : '') + reg.options[reg.selectedIndex].text : S.nat_only;
          v[s.id + '_r'] = raw.r; v[s.id + '_m'] = raw.m;
        }
      });
      return v;
    }
    function share() {
      var p = new URLSearchParams();
      specs.forEach(function (s) {
        var raw = rawOf(s);
        if (s.type === 'place') { if (raw.r) p.set(s.id + 'r', raw.r); if (raw.m) p.set(s.id + 'm', raw.m); }
        else if (s.type === 'check') { if (raw) p.set(s.id, '1'); }
        else if (raw !== '' && String(raw) !== String(s.value)) p.set(s.id, raw);
      });
      var t = p.toString();
      try { history.replaceState(null, '', location.pathname + (t ? '?' + t : '') + location.hash); } catch (e) { /* file:// */ }
      return location.origin + location.pathname + (t ? '?' + t : '');
    }
    var icsUrl = null;
    function render() {
      visible();
      var v = values(), r;
      try { r = compute(v, H, C) || {}; } catch (e) { r = { err: S.err }; }
      var url = touched ? share() : location.href, h = '';
      if (r.err) h = '<p class="herr">' + r.err + '</p>';
      else {
        if (r.big !== undefined) h += '<div class="hbig">' + (r.label ? '<p class="hbig-l">' + r.label + '</p>' : '') + '<p class="hbig-n">' + r.big + '</p>' +
          (r.sub ? '<p class="hbig-s">' + r.sub + '</p>' : '') + '</div>';
        if (r.rows && r.rows.length) h += '<table class="tbl hrows"><tbody>' + r.rows.map(function (x) {
          return '<tr' + (x[2] ? ' class="' + x[2] + '"' : '') + '><th scope="row">' + x[0] + '</th><td class="num">' + x[1] + '</td></tr>';
        }).join('') + '</tbody></table>';
        if (r.html) h += r.html;
        if (r.note) h += '<p class="hnote">' + r.note + '</p>';
        var act = [];
        if (r.print) act.push('<button type="button" class="btn p" id="h-print">' + S.print + '</button>');
        if (r.ics) act.push('<a class="btn" id="h-ics" href="#">' + S.ics + '</a>');
        if (C.link) act.push('<button type="button" class="btn" id="h-link">' + S.link + '</button>');
        if (act.length) h += '<div class="tools hact">' + act.join('') + '</div>';
      }
      out.innerHTML = h;
      if (r.print) $('h-print').addEventListener('click', function () { window.print(); });
      if (r.ics) {
        if (icsUrl) URL.revokeObjectURL(icsUrl);
        icsUrl = URL.createObjectURL(new Blob([r.ics.text], { type: 'text/calendar' }));
        var a = $('h-ics'); a.href = icsUrl; a.download = r.ics.name;
      }
      var lb = $('h-link');
      if (lb) lb.addEventListener('click', function () {
        var u = share();
        var done = function () { lb.textContent = S.copied; setTimeout(function () { lb.textContent = S.link; }, 1600); };
        if (navigator.share && /Android|iPhone|iPad/.test(navigator.userAgent)) navigator.share({ url: u }).catch(function () { /* closed */ });
        else if (navigator.clipboard) navigator.clipboard.writeText(u).then(done, function () { /* blocked */ });
      });
    }

    /* initial state: query string, else defaults ('today' dates, saved comunidad) */
    specs.forEach(function (s) {
      if (s.type === 'place') {
        var r = q.get(s.id + 'r');
        try { if (r === null) r = localStorage.getItem('cl27.region') || ''; } catch (e) { r = r || ''; }
        fillMun(s.id); setRaw(s, { r: r || '', m: q.get(s.id + 'm') || '' });
        $(s.id + '-r').addEventListener('change', function () {
          fillMun(s.id);
          try { if ($(s.id + '-r').value) localStorage.setItem('cl27.region', $(s.id + '-r').value); } catch (e) { /* no storage */ }
        });
        return;
      }
      if (q.has(s.id)) setRaw(s, q.get(s.id));
      else if (s.today && s.type === 'date') $(s.id).value = iso(H.today());
      else if (s.today && s.type === 'month') $(s.id).value = iso(H.today()).slice(0, 7);
      if (s.type === 'seg') each(doc.querySelectorAll('[data-seg="' + s.id + '"] button'), function (b) {
        b.addEventListener('click', function () { setRaw(s, b.getAttribute('data-v')); applySets(s); touched = true; render(); });
      });
    });
    var form = $('hform');
    ['input', 'change'].forEach(function (ev) {
      form.addEventListener(ev, function (e) {
        var s = specs.filter(function (x) { return x.id === e.target.id; })[0];
        if (s && s.options && ev === 'change') applySets(s);
        else if (s) presetOf(s.id);
        touched = true; render();
      });
    });
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    render();
  };
})(typeof window !== 'undefined' ? window : this);
