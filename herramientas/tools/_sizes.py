"""Shared size tables of pack H (tallas-ropa-calzado / size-conversion-chart). Ignored by the registry.

Shoes are computed from the historical unit definitions, not copied from any chart:
- EU (Paris point) = 2/3 cm of shoe last: last_cm = EU / 1.5.
- UK adult = 3 x last_in - 25 (barleycorn = 1/3 in, adult size 0 = 8 1/3 in); UK child = 3 x last_in - 12.33 (child 0 = 4 in).
- US men = UK + 1, US women = UK + 2, US kids = UK child + 1 (the usual retail offsets; brands vary by half a size).
- Foot length = last - 1.5 cm (adults) / 1 cm (kids): the typical toe allowance, as in ISO 9407 Mondopoint (foot-based).
Clothing uses the usual label equivalences (Spain/France = Germany + 2, Italy = Germany + 6, UK = Germany - 26,
US = UK - 4 for women; EU chest = UK/US chest in inches + 10 for men; trousers waist in = EU / 2 + 8; collar in = cm / 2.54).
"""

ISO9407 = "https://www.iso.org/standard/71594.html"


def r2(x):
    return round(x * 2) / 2


def shoes(kind):
    rows = []
    if kind == "nino":
        for eu in range(16, 33):
            li = eu / 1.5 / 2.54
            uk = r2(3 * li - 12.33)
            us = uk + 1  # US kids' scale ends at 13.5, then youth sizes start again at 1Y
            rows.append([eu, uk, us if us <= 13.5 else f"{us - 13:g}Y", round(eu / 1.5 - 1, 1)])
        return rows
    lo, hi, us = (35, 43, 2) if kind == "mujer" else (39, 48, 1)
    for eu in range(lo, hi + 1):
        li = eu / 1.5 / 2.54
        uk = r2(3 * li - 25)
        rows.append([eu, uk, uk + us, round(eu / 1.5 - 1.5, 1)])
    return rows


LET_W = {32: "XXS", 34: "XS", 36: "S", 38: "M", 40: "M", 42: "L", 44: "XL", 46: "XL", 48: "XXL", 50: "XXL", 52: "3XL"}
LET_M = {44: "XS", 46: "S", 48: "M", 50: "M", 52: "L", 54: "XL", 56: "XXL", 58: "3XL", 60: "3XL"}
KIDS = [(56, "0-1 m", "0-3 M"), (62, "3 m", "0-3 M"), (68, "6 m", "3-6 M"), (74, "9 m", "6-9 M"), (80, "12 m", "12 M"),
        (86, "18 m", "18 M"), (92, "2", "2T"), (98, "3", "3T"), (104, "4", "4T"), (110, "5", "5"), (116, "6", "6"),
        (122, "7", "7"), (128, "8", "8"), (134, "9", "8-9"), (140, "10", "10"), (146, "11", "10-12"), (152, "12", "12"),
        (158, "13", "14"), (164, "14", "14-16")]


def tables(lang):
    es = lang == "es"
    yrs = (lambda a: a.replace(" m", " meses") + ("" if " m" in a else " años")) if es else (lambda a: a.replace(" m", " months") + ("" if " m" in a else " yrs"))  # noqa: E731
    T = {
        "calz-mujer": {"head": ["EU", "UK", "US", "cm" if es else "Foot cm"], "rows": shoes("mujer"), "from": {"eu": 0, "uk": 1, "us": 2, "cm": 3}},
        "calz-hombre": {"head": ["EU", "UK", "US", "cm" if es else "Foot cm"], "rows": shoes("hombre"), "from": {"eu": 0, "uk": 1, "us": 2, "cm": 3}},
        "calz-nino": {"head": ["EU", "UK", "US", "cm" if es else "Foot cm"], "rows": shoes("nino"), "from": {"eu": 0, "uk": 1, "us": 2, "cm": 3}},
        "ropa-mujer": {"head": ["España / Francia" if es else "France / Spain", "Alemania" if es else "Germany", "Italia" if es else "Italy",
                                "UK", "US", "Letra" if es else "Letter"],
                       "rows": [[de + 2, de, de + 6, de - 26, de - 30, LET_W[de]] for de in range(32, 54, 2)],
                       "from": {"eu": 0, "de": 1, "it": 2, "uk": 3, "us": 4, "let": 5}},
        "ropa-hombre": {"head": ["EU / Italia" if es else "EU / Italy", "UK / US", "Letra" if es else "Letter"],
                        "rows": [[eu, eu - 10, LET_M[eu]] for eu in range(44, 62, 2)], "from": {"eu": 0, "uk": 1, "us": 1, "let": 2}},
        "camisa": {"head": ["Cuello cm" if es else "Collar cm", "Cuello pulgadas" if es else "Collar in", "Letra" if es else "Letter"],
                   "rows": [[cm, r2(cm / 2.54), {37: "S", 38: "S", 39: "M", 40: "M", 41: "L", 42: "L", 43: "XL", 44: "XL", 45: "XXL", 46: "XXL"}[cm]]
                            for cm in range(37, 47)], "from": {"eu": 0, "cm": 0, "uk": 1, "us": 1, "let": 2}},
        "pantalon": {"head": ["EU", "W (pulgadas)" if es else "Waist W (in)", "Letra" if es else "Letter"],
                     "rows": [[eu, eu // 2 + 8, LET_M.get(eu, "XS" if eu < 44 else "3XL")] for eu in range(40, 62, 2)],
                     "from": {"eu": 0, "uk": 1, "us": 1, "let": 2}},
        "ropa-nino": {"head": ["Altura cm (EU)" if es else "Height cm (EU)", "Edad" if es else "Age", "US"],
                      "rows": [[cm, yrs(a), us] for cm, a, us in KIDS], "from": {"eu": 0, "cm": 0, "us": 2}},
    }
    return T


KINDS_ES = [("calz-mujer", "Calzado mujer"), ("calz-hombre", "Calzado hombre"), ("calz-nino", "Calzado infantil"),
            ("ropa-mujer", "Ropa mujer"), ("ropa-hombre", "Chaquetas y jerséis hombre"), ("camisa", "Camisas hombre"),
            ("pantalon", "Pantalones hombre"), ("ropa-nino", "Ropa infantil")]
KINDS_EN = [("calz-mujer", "Women's shoes"), ("calz-hombre", "Men's shoes"), ("calz-nino", "Kids' shoes"),
            ("ropa-mujer", "Women's clothing"), ("ropa-hombre", "Men's jackets & tops"), ("camisa", "Men's shirts"),
            ("pantalon", "Men's trousers"), ("ropa-nino", "Kids' clothing")]

SIZES_JS = r"""
  /* tables: {kind: {head, rows, from}}; finds the row whose 'from' column matches the size (numbers: nearest within
     half a step; text: same label, first row) */
  function findRow(T, kind, from, raw, val) {
    var t = T[kind], col = t.from[from];
    if (col === undefined) return { err: 1 };
    var s = String(raw || '').trim();
    if (!s) return { t: t, col: col, row: -1 };
    var x = val(s), best = -1, bd = 1e9;
    t.rows.forEach(function (r, i) {
      var c = r[col];
      if (typeof c === 'number') { if (!isNaN(x)) { var d = Math.abs(c - x); if (d < bd - 1e-9) { bd = d; best = i; } } }
      else if (String(c).toUpperCase().replace(/\s+/g, '') === s.toUpperCase().replace(/\s+/g, '') && best < 0) { best = i; bd = 0; }
    });
    var step = t.rows.length > 1 && typeof t.rows[0][col] === 'number' ? Math.abs(t.rows[1][col] - t.rows[0][col]) : 1;
    if (best < 0 || bd > Math.max(step, 0.5) * 0.75) return { t: t, col: col, row: -1, miss: 1 };
    return { t: t, col: col, row: best };
  }
"""
SIZES_CSS = ".tl tr.on td{background:#fff3c4;font-weight:700}.tl td,.tl th{text-align:center}"
