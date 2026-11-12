"""SKU generator: reference codes for every combination of variants (color, size, material), collision-free, with CSV
to copy. Spanish twin: generador_sku.py (same core)."""
from herramientas.tools import _sellers as S
from herramientas.tools.generador_sku import CORE_JS, CSS, GS1


def blocks(ctx):
    return [
        ("How each code is built", """
<p>Type the product and, for each variant, its values separated by commas. The generator makes one SKU per combination:
"Basic tee" with three colors (Red, Blue, Black) and four sizes (S, M, L, XL) gives 12 codes, from
<code>BAST-RED-S</code> to <code>BAST-BLA-XL</code>. Each value is cut to its first letters, with accents and symbols
removed; later words add their initial ("Navy blue" → <code>NAVB</code>), and sizes or measures with digits
(<code>XL</code>, <code>3XL</code>, <code>11OZ</code>) stay whole. If two values would produce the same code, the prefix
grows until they differ, so no two SKUs are ever the same: with two letters, Blue and Black would both be
<code>BL</code>, so they become <code>BLU</code> and <code>BLA</code>.</p>
<p>Below the table you get the list as CSV (SKU plus variants), ready to paste into a spreadsheet or a bulk import: Etsy,
Shopify, WooCommerce and Amazon Seller Central all have a SKU field per variant.</p>"""),
        ("Good SKU habits", """
<ul>
<li><b>General to specific</b>: product, model, color, size. Sorted alphabetically, all variants of a product then sit
together.</li>
<li><b>Short, no spaces</b>: 8 to 16 characters fit every field and every warehouse label.</li>
<li><b>Never start with zero</b>: Excel and Google Sheets turn <code>0012</code> into <code>12</code>.</li>
<li><b>Avoid look-alikes</b>: O and 0, I and 1 get mixed up when someone reads a label by hand.</li>
<li><b>Never reuse a SKU</b> from a retired product, or your sales reports will merge the two.</li>
</ul>"""),
        ("A SKU is not a barcode", f"""
<p>A SKU is internal: you make it up and it only means something in your shop and your stockroom. The barcode Amazon or a
retailer asks for is a <a href="{GS1}" rel="noopener">GTIN (UPC in North America, EAN-13 elsewhere)</a>, issued by GS1 and
unique worldwide. Most sellers use both: the GTIN identifies the product to everyone else, the SKU helps you find it, count
it and read sales by variant.</p>"""),
    ]


FAQ = [
    ("What is a SKU?",
     "A stock keeping unit: an internal code for each variant of a product (say, the red T-shirt in size M) used to track "
     "inventory and sales."),
    ("How do I create SKUs?",
     "Join fixed abbreviations for product and variants in the same order, separated by hyphens: BAST-RED-M. This generator "
     "does it for every combination at once."),
    ("Do I need SKUs on Etsy or Amazon?",
     "On Etsy they are optional; on Amazon Seller Central every offer has a seller SKU, and Amazon creates one if you leave it "
     "blank."),
    ("Is a SKU the same as a UPC or EAN?",
     "No. UPC and EAN are GS1 barcodes, unique worldwide; a SKU is your own code and only works inside your business."),
    ("How long should a SKU be?",
     "There is no standard, but 8 to 16 characters of letters, digits and hyphens works on every platform."),
]

JS = r"""
function (v, H, C) {
""" + CORE_JS + r"""
  var lists = [split(v.a1), split(v.a2), split(v.a3)].filter(function (l) { return l.length; });
  if (!clean(v.base || '') && !lists.length) return { err: 'Type the product or at least one variant.' };
  var total = lists.reduce(function (a, l) { return a * l.length; }, 1);
  if (total > 500) return { err: total + ' combinations: the limit is 500.' };
  var sep = v.sep === 'n' ? '' : v.sep, r = skus(v.base || '', lists, +v.len, sep, v.num), long = 0;
  r.forEach(function (x) { long = Math.max(long, x[0].length); });
  var rows = r.map(function (x) { return '<tr><td><code>' + H.esc(x[0]) + '</code></td><td>' + H.esc(x[1].join(' · ')) + '</td></tr>'; }).join('');
  var csv = 'sku,product' + lists.map(function (l, i) { return ',variant' + (i + 1); }).join('') + '\n' +
    r.map(function (x) { return [x[0], v.base || ''].concat(x[1]).map(csvq).join(','); }).join('\n');
  return {
    label: 'SKUs generated', big: r.length, sub: 'Up to ' + long + ' characters · ' + H.esc(r[0][0]),
    html: '<table class="tbl sku"><thead><tr><th>SKU</th><th>Variant</th></tr></thead><tbody>' + rows + '</tbody></table>' +
      '<label class="flabel" for="sku-csv">CSV</label><textarea id="sku-csv" class="sku-csv" readonly rows="6">' + H.esc(csv) + '</textarea>',
    n: { count: r.length, first: r[0][0], last: r[r.length - 1][0], long: long }
  };
}
"""

TOOL = {
    "slug": "sku-generator",
    "lang": "en",
    "twin": "generador-sku",
    "cat": "sellers",
    "icon": "barcode",
    "order": 100,
    "name": "SKU generator",
    "k": "sku code product variants inventory csv shopify etsy",
    "title": "SKU Generator: Codes for Every Product Variant",
    "desc": "Create SKU codes for every combination of color, size and material, with no duplicates, and copy them as CSV for Etsy, Shopify or Amazon.",
    "h1": "SKU generator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "base", "type": "text", "label": "Product", "value": "Basic tee", "w": "l", "maxlength": 60},
        {"id": "a1", "type": "text", "label": "Variant 1", "value": "Red, Blue, Black", "w": "l"},
        {"id": "a2", "type": "text", "label": "Variant 2", "value": "S, M, L, XL", "w": "l"},
        {"id": "a3", "type": "text", "label": "Variant 3", "value": "", "w": "l", "more": True},
        {"id": "len", "type": "seg", "label": "Letters", "value": "3", "options": [("2", "2"), ("3", "3"), ("4", "4")]},
        {"id": "sep", "type": "seg", "label": "Separator", "value": "-", "options": [("-", "-"), ("_", "_"), ("n", "None")]},
        {"id": "num", "type": "check", "label": "Running number", "value": False, "more": True},
    ],
    "js": JS,
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("GS1 · Global Trade Item Number (GTIN)", GS1), ("Etsy Open API v3 · inventory (sku)", S.ETSY_API)],
    "related": ["etsy-listing-checker", "size-conversion-chart", "selling-price-calculator"],
    "tests": [
        ({}, {"n.count": 12, "n.first": "BAST-RED-S", "n.last": "BAST-BLA-XL"}),
        ({"a1": "Navy blue, Blue", "a2": ""}, {"n.first": "BAST-NAVB", "n.last": "BAST-BLU"}),
        ({"a1": "Blue, Black, Blush", "a2": "", "len": "2"}, {"n.first": "BAT-BLUE", "n.last": "BAT-BLUS"}),
        ({"base": "Mug 11 oz", "a1": "White", "a2": "", "sep": "_"}, {"n.first": "MUG11O_WHI"}),
        ({"base": "", "a1": "", "a2": ""}, {"err": "Type the product or at least one variant."}),
    ],
}
