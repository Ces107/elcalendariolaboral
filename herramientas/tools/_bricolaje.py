"""Shared code of pack F (bricolaje y vivienda / DIY and home): number formatting for the Spanish and English twins,
the "cheapest set of tins / boxes" helper and the category names.

Ignored by the registry (leading underscore). Each tool's compute must be self-contained, so the JS lives here as
strings pasted into each compute function (make_js(en) in every tool file). The Python twins compute the worked
examples of the explanation blocks at build time, with the same formulas, so text and tool agree.
"""
import math

CAT_ES = ("bricolaje", "Bricolaje y reformas")
CAT_EN = ("diy", "DIY and home")

# number formatting: Spanish 1.234,5 · English 1,234.5 (same rule as h.js num(), plus English)
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

# cheapest set of packs (tins, boxes, bags) that covers `need`: sizes in descending order, price of a pack assumed to
# grow as size^0.8 (the litre is cheaper in big tins). Returns [[size, count], ...] (count > 0) and the total.
PACKS_JS = r"""
  function packs(need, sizes) {
    var best = null;
    function go(k, rest, used, cost, cnt) {
      if (k === sizes.length) {
        if (rest > 1e-9) return;
        var vol = need - rest;
        if (!best || cost < best.cost - 1e-9 || (Math.abs(cost - best.cost) < 1e-9 && vol < best.vol)) best = { cost: cost, vol: vol, used: used.slice() };
        return;
      }
      var s = sizes[k], max = k === 0 ? Math.ceil(need / s) : Math.ceil(sizes[k - 1] / s);
      if (k === sizes.length - 1) max = Math.max(0, Math.ceil(rest / s));
      for (var n = 0; n <= max; n++) { used.push([s, n]); go(k + 1, rest - n * s, used, cost + n * Math.pow(s, 0.8), cnt + n); used.pop(); }
    }
    if (!(need > 0)) return { list: [], total: 0 };
    go(0, need, [], 0, 0);
    var list = best.used.filter(function (x) { return x[1] > 0; });
    return { list: list, total: list.reduce(function (a, x) { return a + x[0] * x[1]; }, 0) };
  }
"""


def n(x, dec=0, en=False):
    """Python twin of fx(): Spanish (1.234,5) or English (1,234.5) grouping."""
    s = f"{abs(x) + 1e-9:,.{dec}f}"
    if not en:
        s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return ("−" if x < 0 and round(abs(x), dec) else "") + s


def packs(need, sizes):
    """Python twin of packs() (same search and cost rule)."""
    best = None

    def go(k, rest, used, cost):
        nonlocal best
        if k == len(sizes):
            if rest > 1e-9:
                return
            vol = need - rest
            if not best or cost < best[0] - 1e-9 or (abs(cost - best[0]) < 1e-9 and vol < best[1]):
                best = (cost, vol, list(used))
            return
        s = sizes[k]
        mx = math.ceil(need / s) if k == 0 else math.ceil(sizes[k - 1] / s)
        if k == len(sizes) - 1:
            mx = max(0, math.ceil(rest / s))
        for c in range(mx + 1):
            used.append((s, c))
            go(k + 1, rest - c * s, used, cost + c * s ** 0.8)
            used.pop()

    go(0, need, [], 0)
    return [(s, c) for s, c in best[2] if c]


def make(src, en):
    """Paste the shared helpers into a compute function: %EN% -> true/false, %FMT% -> FMT_JS, %PACKS% -> PACKS_JS."""
    return src.replace("%EN%", "true" if en else "false").replace("%FMT%", FMT_JS).replace("%PACKS%", PACKS_JS)
