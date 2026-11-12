"""Shared code of pack G (deporte y aire libre / sports and outdoors): category names, number and time formatting for
the Spanish and English twins, a seeded PRNG.

Ignored by the registry (leading underscore). Each compute function must be self-contained, so the JS helpers live
here as strings pasted into each compute (make(src, en)): %EN% -> true/false, %FMT% -> FMT_JS, %TIME% -> TIME_JS,
%RND% -> RND_JS. The Python twins compute the worked examples of the explanation blocks at build time.
"""

CAT_ES = ("deporte", "Deporte y aire libre")
CAT_EN = ("sports", "Sports and outdoors")

# numbers: Spanish 1.234,5 · English 1,234.5
FMT_JS = r"""
  function fx(x, dec) {
    if (dec === undefined) dec = 2;
    var a = (Math.abs(x) + 1e-9).toFixed(dec).split('.'), i = a[0].replace(/\B(?=(\d{3})+(?!\d))/g, EN ? ',' : '.');
    var z = +a.join('') === 0;
    return (x < 0 && !z ? '−' : '') + i + (a[1] ? (EN ? '.' : ',') + a[1] : '');
  }
  function fv(x, dec) { var s = fx(x, dec === undefined ? 2 : dec); return s.indexOf(EN ? '.' : ',') >= 0 ? s.replace(/0+$/, '').replace(/[.,]$/, '') : s; }
  function r(x, d) { var k = Math.pow(10, d === undefined ? 2 : d); return Math.round((x + (x >= 0 ? 1e-9 : -1e-9)) * k) / k; }
"""

# durations: '1:23:45' | '45:30' | '45' (minutes) | '45,5' -> seconds (NaN if junk); seconds -> '1:23:45' / '4:05'
TIME_JS = r"""
  function tp(s) {
    s = String(s == null ? '' : s).trim().replace(/\s+/g, '').replace(/[hH]/, ':').replace(/''|"/g, '').replace(/['mM]/g, ':').replace(/[sS]$/, '').replace(/:$/, '');
    if (!s) return NaN;
    var p = s.split(':');
    if (p.length === 1) return /^\d+([.,]\d+)?$/.test(p[0]) ? parseFloat(p[0].replace(',', '.')) * 60 : NaN;
    if (p.length > 3) return NaN;
    var t = 0;
    for (var i = 0; i < p.length; i++) {
      if (!/^\d+([.,]\d+)?$/.test(p[i])) return NaN;
      var x = parseFloat(p[i].replace(',', '.'));
      if (i > 0 && x >= 60) return NaN;
      t = t * 60 + x;
    }
    return t;
  }
  function ft(sec, dec) {
    if (!isFinite(sec)) return '–';
    var k = dec ? 10 : 1, t = Math.round(sec * k) / k, h = Math.floor(t / 3600), m = Math.floor((t - h * 3600) / 60), s = t - h * 3600 - m * 60;
    var ss = dec ? (s < 10 ? '0' : '') + s.toFixed(1).replace('.', EN ? '.' : ',') : (s < 10 ? '0' : '') + Math.round(s);
    return h ? h + ':' + (m < 10 ? '0' : '') + m + ':' + ss : m + ':' + ss;
  }
"""

# seeded PRNG (FNV-1a of a string -> Mulberry32), deterministic so a shared link rebuilds the same draw
RND_JS = r"""
  function rng(str) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    return function () { h = (h + 0x6D2B79F5) >>> 0; var t = h; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  }
  function shuf(a, rnd) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(rnd() * (i + 1)), t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
"""

MULBERRY = ("Mulberry32 PRNG (Tommy Ettinger)", "dominio público (CC0)", "https://gist.github.com/tommyettinger/46a874533244883189143505d203312c")
MULBERRY_EN = ("Mulberry32 PRNG (Tommy Ettinger)", "public domain (CC0)", "https://gist.github.com/tommyettinger/46a874533244883189143505d203312c")


def make(src, en):
    return (src.replace("%EN%", "true" if en else "false").replace("%FMT%", FMT_JS).replace("%TIME%", TIME_JS)
            .replace("%RND%", RND_JS))


def n(x, dec=0, en=False):
    """Python twin of fx(): Spanish (1.234,5) or English (1,234.5)."""
    s = f"{abs(x) + 1e-9:,.{dec}f}"
    if not en:
        s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return ("−" if x < 0 and round(abs(x), dec) else "") + s


def t(sec):
    """Python twin of ft(): seconds -> '1:23:45' or '4:05'."""
    sec = round(sec)
    h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
