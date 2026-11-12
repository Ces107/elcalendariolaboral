"""Shared code of pack J (coche y viaje / car and travel): category names, number formatting for the Spanish and
English twins, duration parsing and the unit constants.

Ignored by the registry (leading underscore). Each compute function must be self-contained, so the JS helpers live
here as strings pasted into each compute (make(src, en)): %EN% -> true/false, %FMT% -> FMT_JS, %TIME% -> TIME_JS.
"""

CAT_EN = ("car", "Car and travel")

# exact definitions: international mile (1959), US gallon (231 in³), imperial gallon (Weights and Measures Act 1985)
MILE_KM = 1.609344
GAL_US = 3.785411784
GAL_UK = 4.54609

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

# durations: '3:30' | '3:30:15' | '3h30' | '3h' | '90min' | '2,5' (hours) -> seconds (NaN if junk); seconds -> '3:30:00'
TIME_JS = r"""
  function tp(s) {
    s = String(s == null ? '' : s).trim().toLowerCase().replace(/\s+/g, '');
    if (!s) return NaN;
    var m = s.match(/^(\d+(?:[.,]\d+)?)(min|m)$/);
    if (m) return parseFloat(m[1].replace(',', '.')) * 60;
    m = s.match(/^(\d+)h(\d{1,2})?(?:min|m)?$/);
    if (m) return +m[1] * 3600 + (m[2] ? +m[2] * 60 : 0) + (m[2] && +m[2] >= 60 ? NaN : 0);
    if (/^\d+(?:[.,]\d+)?h?$/.test(s)) return parseFloat(s.replace('h', '').replace(',', '.')) * 3600;
    var p = s.split(':');
    if (p.length < 2 || p.length > 3) return NaN;
    var t = 0;
    for (var i = 0; i < p.length; i++) {
      if (!/^\d+$/.test(p[i])) return NaN;
      if (i > 0 && +p[i] >= 60) return NaN;
      t = t * 60 + +p[i];
    }
    return p.length === 2 ? t * 60 : t;
  }
  function ft(sec) {
    if (!isFinite(sec)) return '–';
    var t = Math.round(sec), h = Math.floor(t / 3600), m = Math.floor((t - h * 3600) / 60), s = t - h * 3600 - m * 60;
    return h + ':' + (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  }
"""


def make(src, en):
    """Paste the shared helpers into a compute function."""
    return (src.replace("%EN%", "true" if en else "false").replace("%FMT%", FMT_JS).replace("%TIME%", TIME_JS))


def n(x, dec=2, en=False):
    """Python twin of fx(): number text for the worked examples."""
    s = f"{abs(x):,.{dec}f}"
    if not en:
        s = s.replace(",", "_").replace(".", ",").replace("_", ".")
    return ("−" if x < 0 and float(f"{abs(x):.{dec}f}") else "") + s
