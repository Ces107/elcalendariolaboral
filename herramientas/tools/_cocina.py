"""Shared bits of the kitchen pack (pack E, batch b1112): the number formatter both languages use inside a compute
function, and the category of the pack. Not a tool (leading underscore: the registry skips it).

A compute function of this pack is written once (in the Spanish module) as the body of `function (v, H, C)`;
`js(body)` prepends the helpers below. Strings come from C.d.t, and C.d.en switches the number format:
    nf(x, d)  fixed decimals, 1.234,5 (es) or 1,234.5 (en)
    nz(x, d)  same, trailing zeros dropped
    gr(x)     a weight in grams the way a cook reads it: 1 decimal below 10, whole numbers above
    hm(min)   minutes -> "2 h 05 min"
"""

CAT = {"es": ("cocina", "Cocina y bebidas"), "en": ("kitchen", "Kitchen and drinks")}

HELPERS = r"""
  var D = C.d || {}, T = D.t || {}, EN = !!D.en;
  function nf(x, d) {
    if (d === undefined) d = 0;
    if (!EN) return H.num(x, d);
    var neg = x < 0, s = Math.abs(x).toFixed(d).split('.'), i = s[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    return (neg && +s.join('') !== 0 ? '−' : '') + i + (s[1] ? '.' + s[1] : '');
  }
  function nz(x, d) { var s = nf(x, d); return d ? s.replace(EN ? /\.?0+$/ : /,?0+$/, '') : s; }
  function gr(x) { return Math.abs(x) < 10 ? nz(x, 1) : nf(Math.round(x)); }
  function hm(m) { m = Math.round(m); var h = Math.floor(m / 60), r = m % 60; return (h ? h + ' h ' : '') + (h && r < 10 ? '0' : '') + r + ' min'; }
  function ok(x) { return typeof x === 'number' && !isNaN(x); }
"""


def js(body):
    return "function (v, H, C) {" + HELPERS + body + "}"
