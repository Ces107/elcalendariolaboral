"""Clothing and shoe size converter: US, UK, EU, Germany, Italy, France/Spain, cm, letters; women, men and kids.
Spanish twin: tallas_ropa_calzado.py. Tables and method in _sizes.py."""
from herramientas.tools import _sizes as Z

FROM = [("us", "US"), ("uk", "UK"), ("eu", "EU"), ("cm", "cm"), ("let", "Letter"), ("de", "Germany"), ("it", "Italy")]


def n(x):
    return f"{x:g}" if isinstance(x, (int, float)) else x


def blocks(ctx):
    T = Z.tables("en")
    w = {r[0]: r for r in T["calz-mujer"]["rows"]}
    m = {r[0]: r for r in T["calz-hombre"]["rows"]}
    return [
        ("Shoe size equivalents", f"""
<p>A women's US 7 is a <b>UK {n(w[38][1])}</b> and an <b>EU 38</b>, for a foot of about {n(w[38][3])} cm. A men's US 9 is a
UK {n(m[42][1])} and an EU 42. The systems come from old units: the EU size (Paris point) counts the shoe last in 2/3 cm
steps, so last length in cm = size × 2 ÷ 3; the UK size counts thirds of an inch from 8 1/3 in for adults (4 in for
children); and US sizes add a fixed offset to the UK number, one for men and two for women. That is why the same US number
means a different shoe for men and women.</p>
<p>The tables here are built from those definitions, so they are right for comparing systems, but every brand rounds its own
way and can be half a size off. The most reliable method is to measure your foot standing, heel to longest toe, and look the
length up in the cm column. ISO 9407 (Mondopoint) labels footwear exactly like that, by foot length in millimetres.</p>"""),
        ("Clothing: the EU is not one system", """
<p>Women's sizes in France and Spain run <b>two numbers above</b> Germany's and most of northern Europe's: a German 36 is a
French or Spanish 38, an Italian 42, a UK 10 and a US 6. So from a US size, add 30 for Germany and 32 for France and Spain;
from a UK size, add 26 for Germany. Men's jackets and sweaters go by chest: a 40 in chest in the UK and US is a European 50.
Men's trousers go by waist in inches: W32 is a European 48.</p>
<p>Kids' clothes in Europe are labelled by the child's height in centimetres (92, 98, 104…), while US sizes use age: 2T, 3T
and 4T for toddlers. Buy by height, not age: height is what EU sizes measure.</p>"""),
        ("If you sell clothes or shoes", """
<p>On Etsy, eBay or your own shop, always state the system (US, UK, EU) and give flat garment measurements: chest width,
length, waist and inseam, in both inches and centimetres. That does more to cut returns than any size chart. Selling into
Europe, add the EU size to a tag; selling to the US, put the US size in the title, since that is what buyers search for.</p>"""),
    ]


FAQ = [
    ("What is a US 7 women's shoe in EU size?",
     "About an EU 38, which is a UK 5. Brands can differ by half a size."),
    ("How do I convert UK clothing sizes to US?",
     "For women, subtract 4: a UK 10 is a US 6. For men's jackets, the chest number is the same in both."),
    ("Is EU clothing sizing the same in every country?",
     "No. For women, France and Spain run two sizes above Germany, and Italy four above France."),
    ("How do I find my child's shoe size?",
     "Measure the foot standing, heel to longest toe, and add about 1 cm of room. A 13 cm foot is roughly an EU 21 or a US 5."),
    ("What does W mean on jeans?",
     "Waist in inches. W32 matches a European men's 48; the L is the inside leg length."),
]

JS = r"""
function (v, H, C) {
""" + Z.SIZES_JS + r"""
  var f = findRow(C.d.t, v.kind, v.from, v.size, H.val);
  if (f.err) return { err: 'This chart does not use that system: pick another one in "From".' };
  var t = f.t, fmt = function (c) { return typeof c === 'number' ? String(c) : H.esc(c); };
  var tb = '<table class="tbl tl"><thead><tr>' + t.head.map(function (h) { return '<th>' + H.esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' +
    t.rows.map(function (r, i) { return '<tr' + (i === f.row ? ' class="on"' : '') + '>' + r.map(function (c) { return '<td>' + fmt(c) + '</td>'; }).join('') + '</tr>'; }).join('') +
    '</tbody></table>';
  if (f.row < 0) return f.miss ? { err: 'That size is not in the chart.' } : { html: tb, n: { row: -1 } };
  var r = t.rows[f.row], parts = [];
  r.forEach(function (c, i) { if (i !== f.col && parts.length < 3) parts.push(H.esc(t.head[i].split(' ')[0]) + ' ' + fmt(c)); });
  return { label: H.esc(t.head[f.col]) + ' ' + fmt(r[f.col]), big: parts.join(' · '),
    rows: r.map(function (c, i) { return [H.esc(t.head[i]), fmt(c), i === f.col ? 'sub' : '']; }),
    html: tb, note: 'A guide: brands can differ by half a size.', n: { row: f.row, v: r } };
}
"""

TOOL = {
    "slug": "size-conversion-chart",
    "lang": "en",
    "twin": "tallas-ropa-calzado",
    "cat": "sellers",
    "icon": "shirt",
    "order": 110,
    "name": "Size converter",
    "k": "shoe size clothing size us uk eu conversion kids women men",
    "title": "Shoe & Clothing Size Converter: US, UK, EU Charts",
    "desc": "Convert shoe and clothing sizes between US, UK, EU, Germany, Italy and France/Spain for women, men and kids, with the full chart highlighted.",
    "h1": "Shoe and clothing size converter",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "kind", "type": "select", "label": "Type", "value": "calz-mujer", "options": Z.KINDS_EN},
        {"id": "from", "type": "select", "label": "From", "value": "us", "options": FROM},
        {"id": "size", "type": "text", "label": "Size", "value": "7", "w": "s", "maxlength": 8},
    ],
    "data": lambda ctx: {"t": Z.tables("en")},
    "js": JS,
    "css": Z.SIZES_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ISO 9407:2019 · Shoe sizes, Mondopoint", Z.ISO9407)],
    "related": ["sku-generator", "etsy-listing-checker", "social-media-image-sizes"],
    "tests": [
        ({}, {"n.v.0": 38, "n.v.1": 5}),
        ({"kind": "calz-hombre", "size": "9"}, {"n.v.0": 42}),
        ({"kind": "ropa-mujer", "from": "uk", "size": "10"}, {"n.v.0": 38, "n.v.1": 36, "n.v.4": 6}),
        ({"kind": "pantalon", "from": "us", "size": "32"}, {"n.v.0": 48}),
        ({"kind": "calz-nino", "from": "eu", "size": "32"}, {"n.v.2": "1Y"}),
        ({"kind": "calz-mujer", "from": "let"}, {"err": 'This chart does not use that system: pick another one in "From".'}),
    ],
}
