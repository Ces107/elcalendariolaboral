"""KDP royalty calculator: paperback (printing cost, 60 % / 50 % by list price, expanded distribution) and eBook (70 % /
35 %, delivery cost per MB, VAT). Spanish twin: regalias_kdp.py. Tables in _sellers.py."""
from herramientas.tools import _sellers as S
from herramientas.tools.regalias_kdp import data

INK = [("bw", "Black & white"), ("sc", "Standard color"), ("pc", "Premium color")]


def blocks(ctx):
    m = lambda x, c="USD": S.fm(x, c, True)  # noqa: E731
    a = S.kdp_pb("com", "bw", 120, False, 9.99)
    b = S.kdp_pb("com", "bw", 120, False, 9.98)
    c = S.kdp_pb("com", "bw", 300, False, 14.99)
    uk = S.kdp_pb("uk", "bw", 120, False, 7.99)
    col = S.kdp_pb("com", "pc", 100, True, 19.99)
    eb7 = 0.7 * (4.99 - 0.15 * 2)
    eb3 = 0.35 * 4.99
    return [
        ("What you earn per copy", f"""
<p>A 6 × 9 in paperback with 120 black-and-white pages, listed at $9.99 on Amazon.com, costs {m(a["cost"])} to print ($1.00
fixed + 120 × $0.012). KDP pays 60% of the list price minus printing: <b>{m(a["roy"])}</b> a copy. Drop the price one cent to
$9.98 and the rate falls to 50%, leaving {m(b["roy"])}, which is {m(a["roy"] - b["roy"])} less per sale. At 300 pages and
$14.99 printing is {m(c["cost"])} and the royalty {m(c["roy"])}. On Amazon.co.uk the same book at £7.99 earns
{m(uk["roy"], "GBP")}.</p>
<p>Color is where margins vanish: an 8.5 × 11 in premium-color book with 100 pages costs {m(col["cost"])} to print and at
$19.99 earns {m(col["roy"])}. Check the "Minimum price" line before you set a price: KDP will not publish below it.</p>"""),
        ("The 60% threshold", """
<p>For paperbacks, KDP pays <b>60%</b> only when the list price is at least <b>$9.99</b> on Amazon.com, <b>£7.99</b> on
Amazon.co.uk, <b>€9.99</b> on the euro stores, C$13.99 / A$13.99 in Canada and Australia, ¥1,000 in Japan, 40 zł in Poland and
110 kr in Sweden. Below that it pays <b>50%</b>. The formula is the same either way: royalty = rate × list price − printing.
In the UK and EU the list price you enter is before VAT; Amazon adds the local VAT on books on top (zero in the UK, 7% in
Germany, 4% in Spain).</p>
<p><b>Expanded Distribution</b> (US bookstores and libraries) pays 40% of the Amazon.com list price minus printing. For thin,
cheap books it is often zero or negative, and KDP then asks for a higher price.</p>"""),
        ("How printing cost works", """
<p>On Amazon.com a black-and-white book of 24 to 110 pages costs a flat $2.30 ($2.84 for large trim); above 110 pages,
$1.00 plus $0.012 per page ($0.017 large). Premium color is $3.60 up to 40 pages, then $1.00 + $0.065 per page ($0.08
large); standard color, 72 to 600 pages, $1.00 + $0.0255 per page ($0.0402 large). In the UK: £0.85 + £0.010 per page in
black and white. A trim counts as large when it is wider than 6.12 in or taller than 9 in, so 6.14 × 9.21 already is. Cream
and white paper cost the same.</p>"""),
        ("eBooks: 70% or 35%", f"""
<p>A $4.99 eBook on Amazon.com at 70% pays 70% of the price minus a delivery fee of $0.15 per MB: with a 2 MB file that is
<b>{m(eb7)}</b>; at 35% it would be {m(eb3)}, with no delivery fee. The 70% option applies only between $2.99 and $12.99
(£1.77–£12.99 in the UK, €2.69–€12.99 in euro stores), and the eBook must be at least 20% cheaper than the print edition.
In the UK, EU and Australia the price you enter includes VAT or GST, and KDP removes it first. Image-heavy books get heavy:
from about 10 MB the 35% rate can pay more.</p>"""),
    ]


FAQ = [
    ("How much does KDP pay for a paperback?",
     "60% of the list price minus printing if the price is at least $9.99 (£7.99, €9.99), otherwise 50%. A 120-page "
     "black-and-white book at $9.99 earns about $3.55 on Amazon.com."),
    ("Why can't I price my paperback at $4.99?",
     "KDP will not accept a price whose royalty does not cover printing. The minimum is printing ÷ 0.5; if that is above the "
     "60% threshold, printing ÷ 0.6."),
    ("Does KDP's list price include VAT?",
     "For paperbacks on UK and EU stores, no: Amazon adds VAT on top. For eBooks, yes: the price includes VAT and KDP removes "
     "it before calculating the royalty."),
    ("How much does it cost to print a book on KDP?",
     "On Amazon.com, $1.00 plus $0.012 per page in black and white ($2.30 flat up to 110 pages). A 200-page book costs $3.40."),
    ("When does KDP pay royalties?",
     "About 60 days after the end of the month of the sale, once you pass each marketplace's payment threshold."),
]

JS = r"""
function (v, H, C) {
""" + S.FMT_JS + S.KDP_JS + r"""
  var D = C.d, mk = D.mk[v.mk], cur = mk.cur, e = function (x) { return fm(x, cur, true); };
  if (isNaN(v.price) || v.price <= 0) return { err: 'Enter the list price.' };
  if (v.fmt === 'eb') {
    var g = mk.g;
    if (!D.eb[g]) return { err: 'eBook: choose Amazon.com, .co.uk, .ca, .com.au or a euro store.' };
    var E = D.eb[g], vat = E.vat === null ? D.ebvat[v.mk] : E.vat, mb = isNaN(v.mb) || v.mb < 0 ? 0 : v.mb;
    var min35 = E.min35[mb < 3 ? 0 : mb < 10 ? 1 : 2];
    if (v.price < min35) return { err: 'Minimum price for ' + mb + ' MB: ' + e(min35) + '.' };
    if (v.price > E.max) return { err: 'Maximum price: ' + e(E.max) + '.' };
    var net = v.price / (1 + vat / 100), del = Math.max(0.01, mb * E.mb), in70 = v.price >= E.band[0] && v.price <= E.band[1];
    var r70 = 0.7 * (net - del), r35 = 0.35 * net, best = in70 && r70 > r35 ? r70 : r35;
    var rows = [];
    if (vat) rows.push(['Price before VAT ' + pc(vat, true, vat % 1 ? 1 : 0), e(net)]);
    rows.push(['Delivery ' + mb + ' MB', in70 ? '−' + e(del) : '—']);
    rows.push(['70% royalty', in70 ? e(r70) : 'only ' + e(E.band[0]) + '–' + e(E.band[1]), in70 && r70 >= r35 ? 'tot' : '']);
    rows.push(['35% royalty', e(r35), in70 && r70 >= r35 ? '' : 'tot']);
    return { label: 'Royalty per eBook', big: e(best), sub: (best === r35 ? '35%' : '70%') + ' · ' + mk.lab,
      rows: rows, n: { roy: best, r35: r35 } };
  }
  var pages = v.pages, lim = D.pages[v.ink];
  if (isNaN(pages) || pages % 1) return { err: 'Enter the page count.' };
  if (pages < lim[0] || pages > lim[1]) return { err: 'With this ink: ' + lim[0] + ' to ' + lim[1] + ' pages.' };
  if (v.ink === 'sc' && !D.cost[mk.g].sc) return { err: 'Standard color is not offered on this marketplace.' };
  var large = !!D.trims[v.trim], r = kdpPb(D, mk.g, v.ink, pages, large, v.price);
  if (r.roy < 0) return { err: 'At this price you do not cover printing (' + e(r.cost) + '). Minimum: ' + e(r.min) + '.' };
  var rows2 = [['Printing' + (large ? ' · large trim' : ''), e(r.cost)], [(r.rate * 100) + '% royalty', e(r.roy), 'tot']];
  if (r.rate < 0.6) rows2.push(['At ' + e(r.t60) + ' (60%)', e(r.at60), 'sub']);
  rows2.push(['Minimum price', e(r.min)]);
  if (mk.vat !== null) rows2.push(['Shop price with VAT ' + pc(mk.vat, true, mk.vat % 1 ? 1 : 0), e(v.price * (1 + mk.vat / 100))]);
  if (v.mk === 'com') rows2.push(['Expanded Distribution 40%', r.ed > 0 ? e(r.ed) : 'raise the price']);
  return { label: 'Royalty per copy', big: e(r.roy), sub: 'Printing ' + e(r.cost) + ' · ' + (r.rate * 100) + '% of ' + e(v.price),
    rows: rows2, n: { roy: r.roy, cost: r.cost, min: r.min, rate: r.rate } };
}
"""

TOOL = {
    "slug": "kdp-royalty-calculator",
    "lang": "en",
    "twin": "regalias-kdp",
    "cat": "sellers",
    "icon": "book",
    "order": 30,
    "name": "KDP royalty calculator",
    "k": "amazon kdp royalties printing cost paperback ebook self publishing",
    "title": "KDP Royalty Calculator: Paperback Printing Cost & eBook",
    "desc": "Work out your Amazon KDP royalty: printing cost by pages and ink, 60% from $9.99 or 50% below, eBook 70% or 35% with delivery fee and VAT.",
    "h1": "KDP royalty calculator",
    "intro": "KDP rates as of November 2026.",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "fmt", "type": "seg", "label": "Format", "value": "pb", "options": [("pb", "Paperback"), ("eb", "eBook")]},
        {"id": "mk", "type": "select", "label": "Marketplace", "value": "com",
         "options": [(k, lab) for k, lab, *_ in sorted(S.KDP_MK, key=lambda x: x[0] not in ("com", "uk", "ca", "au"))]},
        {"id": "price", "type": "number", "label": "List price", "value": "9.99", "step": "0.01", "w": "s"},
        {"id": "ink", "type": "select", "label": "Ink", "value": "bw", "options": INK, "show": ("fmt", ["pb"])},
        {"id": "trim", "type": "select", "label": "Trim size", "value": "6x9", "show": ("fmt", ["pb"]),
         "options": [(S.trim_value(w, h), S.trim_label(w, h, True)) for w, h in S.TRIMS]},
        {"id": "pages", "type": "number", "label": "Pages", "value": "120", "w": "s", "show": ("fmt", ["pb"])},
        {"id": "mb", "type": "number", "label": "File size", "value": "2", "unit": "MB", "step": "0.1", "w": "s", "show": ("fmt", ["eb"])},
    ],
    "data": data,
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("KDP · Paperback printing cost", S.KDP_PRINT), ("KDP · Paperback royalty", S.KDP_ROY),
                ("KDP · eBook list price requirements", S.KDP_EB), ("KDP · Digital pricing and delivery costs", S.KDP_DEL)],
    "related": ["kdp-cover-calculator", "selling-price-calculator", "break-even-calculator", "etsy-fee-calculator"],
    "tests": [
        ({}, {"n.roy": 3.554, "n.cost": 2.44, "n.rate": 0.6}),
        ({"price": "9.98"}, {"n.roy": 2.55, "n.rate": 0.5}),
        ({"mk": "uk", "price": "7.99"}, {"n.roy": 2.744, "n.cost": 2.05}),
        ({"price": "3"}, {"err": "At this price you do not cover printing ($2.44). Minimum: $4.88."}),
        ({"fmt": "eb", "price": "4.99", "mb": "2"}, {"n.roy": 3.283}),
        ({"fmt": "eb", "mk": "uk", "price": "0.5"}, {"err": "Minimum price for 2 MB: £0.77."}),
    ],
}
