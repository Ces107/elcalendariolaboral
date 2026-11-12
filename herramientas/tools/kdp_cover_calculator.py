"""KDP paperback cover size and spine width by trim, page count and paper, with a to-scale sketch.
Spanish twin: portada_kdp_lomo.py. Formula: KDP help G201953020 (see _sellers.py)."""
from herramientas.tools import _sellers as S

PAPER = [("bw", "White · black ink"), ("cr", "Cream · black ink"), ("sc", "Standard color"), ("pc", "Premium color")]


def blocks(ctx):
    a = S.cover(6, 9, 120, "bw")
    b = S.cover(5.5, 8.5, 200, "cr")
    c = S.cover(8.5, 11, 24, "pc")
    return [
        ("Full cover dimensions", f"""
<p>A KDP paperback cover is one PDF holding back cover, spine and front cover, plus <b>0.125 in (3.2 mm) of bleed</b> on the
top, bottom and both outside edges. Width = bleed + back + spine + front + bleed; height = bleed + trim height + bleed. For a
6 × 9 in book with 120 pages on white paper the spine is {a["sp"]:.3f} in ({a["sp"] * 25.4:.1f} mm) and the full cover
<b>{a["W"]:.3f} × {a["H"]:.2f} in</b> ({a["W"] * 25.4:.1f} × {a["H"] * 25.4:.1f} mm). At 300 DPI that is a
{round(a["W"] * 300):,} × {round(a["H"] * 300):,} px canvas.</p>
<p>With 200 pages of cream paper at 5.5 × 8.5 in the spine grows to {b["sp"]:.3f} in and the cover to
{b["W"]:.3f} × {b["H"]:.2f} in. An 8.5 × 11 in color notebook with only 24 pages has a {c["sp"]:.3f} in spine: too thin for
any text.</p>"""),
        ("Spine width by paper", """
<ul>
<li><b>White paper, black ink</b>: pages × 0.002252 in (0.0572 mm per page).</li>
<li><b>Cream paper, black ink</b>: pages × 0.0025 in (0.0635 mm). Cream is thicker, so the same book gets a spine about 11%
wider.</li>
<li><b>Standard color</b>: pages × 0.002252 in (0.0572 mm).</li>
<li><b>Premium color</b>: pages × 0.002347 in (0.0596 mm).</li>
</ul>
<p>"Pages" means page sides, not sheets: a 120-page interior PDF is 60 sheets. If the page count changes after you design the
cover, the spine changes and KDP rejects the file, so rebuild the cover from the final count.</p>"""),
        ("Safe areas and spine text", """
<p>KDP allows text on the spine only from <b>79 pages</b> (its Cover Creator asks for 80), and that text needs at least
0.0625 in (1.6 mm) of space from each spine edge. On the front and back, keep important text 0.125 in (3.2 mm) inside the
trim, the dashed line in the sketch: anything in the pink band is cut off. The bottom-right corner of the back cover is where
KDP prints its barcode if you do not supply one, so keep it clear.</p>
<p>Export a single PDF with images at 300 DPI or more. Hardcovers use a different template with a wrap margin; this
calculator is for paperbacks.</p>"""),
    ]


FAQ = [
    ("How wide is the spine of a 100-page KDP book?",
     "0.2252 in (5.7 mm) on white paper, 0.25 in (6.4 mm) on cream and 0.2347 in (6 mm) in premium color."),
    ("What size is the cover of a 6 × 9 book?",
     "Width = 12.25 in plus the spine; height = 9.25 in. With 120 white pages, 12.52 × 9.25 in (318 × 235 mm)."),
    ("How many pages do I need for spine text on KDP?",
     "At least 79 (80 with Cover Creator). Below that, leave the spine plain or just colored."),
    ("How much bleed does a KDP cover need?",
     "0.125 in (3.2 mm) on the top, bottom and both outside edges. There is no bleed at the spine."),
    ("What resolution should a KDP cover be?",
     "300 DPI. Multiply width and height in inches by 300 to get the canvas size in pixels."),
]

JS = r"""
function (v, H, C) {
""" + S.COVER_JS + r"""
  var w = v.w, h = v.h, p = v.pages, lim = PGL[v.paper];
  if (!(w >= 4 && w <= 8.5) || !(h >= 6 && h <= 11.69)) return { err: 'KDP trim: width 4 to 8.5 in, height 6 to 11.69 in.' };
  if (isNaN(p) || p % 1) return { err: 'Enter the page count.' };
  if (p < lim[0] || p > lim[1]) return { err: 'With this paper: ' + lim[0] + ' to ' + lim[1] + ' pages.' };
  var r = cover(w, h, p, v.paper), mm = function (x) { return (x * 25.4).toFixed(1) + ' mm'; }, inch = function (x, d) { return x.toFixed(d || 3) + ' in'; };
  return {
    label: 'Full cover', big: r.W.toFixed(3) + ' × ' + r.Ht.toFixed(3) + ' in',
    sub: mm(r.W) + ' × ' + mm(r.Ht) + ' · ' + Math.round(r.W * 300) + ' × ' + Math.round(r.Ht * 300) + ' px at 300 DPI',
    rows: [['Spine', inch(r.sp) + ' · ' + mm(r.sp), 'tot'], ['Spine text', r.text ? 'Yes' : 'No (under 79 pages)'],
      ['Bleed', '0.125 in · 3.2 mm'], ['Front safe area', inch(w - 0.25, 2) + ' × ' + inch(h - 0.25, 2)]],
    html: coverSvg(w, h, r, { back: 'Back', front: 'Front', spine: 'Spine', alt: 'Cover layout' }) +
      '<ul class="kc-leg"><li><i style="background:#f6d5d9"></i>Bleed</li><li><i style="background:#e8eef6"></i>Spine</li>' +
      '<li><i style="border:1px dashed #0b4f8c"></i>Safe area</li></ul>',
    n: { sp: r.sp, W: r.W, H: r.Ht }
  };
}
"""

TOOL = {
    "slug": "kdp-cover-calculator",
    "lang": "en",
    "twin": "portada-kdp-lomo",
    "cat": "sellers",
    "icon": "ruler-measure",
    "order": 40,
    "name": "KDP cover calculator",
    "k": "kdp spine width cover size bleed template paperback",
    "title": "KDP Cover Size & Spine Width Calculator",
    "desc": "Get the full KDP paperback cover size and spine width from trim size, page count and paper, in inches, mm and pixels at 300 DPI, with bleed.",
    "h1": "KDP cover size and spine width calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "trim", "type": "select", "label": "Trim size", "value": "6x9", "custom": "x",
         "options": [(S.trim_value(w, h), S.trim_label(w, h, True), {"w": f"{w:g}", "h": f"{h:g}"}) for w, h in S.TRIMS] + [("x", "Custom")]},
        {"id": "w", "type": "number", "label": "Width", "value": "6", "unit": "in", "step": "0.01", "w": "s"},
        {"id": "h", "type": "number", "label": "Height", "value": "9", "unit": "in", "step": "0.01", "w": "s"},
        {"id": "pages", "type": "number", "label": "Pages", "value": "120", "w": "s"},
        {"id": "paper", "type": "select", "label": "Paper", "value": "bw", "options": PAPER},
    ],
    "js": JS,
    "css": S.COVER_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("KDP · Create a paperback cover", S.KDP_COVER), ("KDP · Paperback printing cost and trim sizes", S.KDP_PRINT)],
    "related": ["kdp-royalty-calculator", "social-media-image-sizes", "selling-price-calculator"],
    "tests": [
        ({}, {"n.sp": 0.27024, "n.W": 12.52024, "n.H": 9.25}),
        ({"w": "5.5", "h": "8.5", "pages": "200", "paper": "cr"}, {"n.sp": 0.5, "n.W": 11.75}),
        ({"w": "8.5", "h": "11", "pages": "100", "paper": "pc"}, {"n.W": 17.4847}),
        ({"pages": "830"}, {"err": "With this paper: 24 to 828 pages."}),
        ({"h": "12"}, {"err": "KDP trim: width 4 to 8.5 in, height 6 to 11.69 in."}),
    ],
}
