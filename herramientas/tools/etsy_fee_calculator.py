"""Etsy fee calculator for sellers worldwide (US, UK, Canada, Australia, EU countries): listing, transaction, payment
processing, regulatory operating fee, Offsite Ads, VAT/GST on fees, net payout, profit, break-even price.
Spanish twin: comisiones_etsy.py."""
from herramientas.tools import _sellers as S

# shop country -> currency, processing %, fixed, regulatory operating fee %, tax on fees %, listing fee in that currency
SHOPS = [
    ("us", "United States", "USD", 3, "0.25", "0", "0", "0.20"),
    ("uk", "United Kingdom", "GBP", 4, "0.20", "0.48", "20", "0.15"),
    ("ca", "Canada", "CAD", 3, "0.25", "1.15", "5", "0.28"),
    ("au", "Australia", "AUD", 3, "0.25", "0", "10", "0.31"),
    ("de", "Germany", "EUR", 4, "0.30", "0", "19", "0.17"),
    ("fr", "France", "EUR", 4, "0.30", "1.14", "20", "0.17"),
    ("es", "Spain", "EUR", 4, "0.30", "0.88", "21", "0.17"),
    ("it", "Italy", "EUR", 4, "0.30", "0.80", "22", "0.17"),
    ("nl", "Netherlands", "EUR", 4, "0.30", "0", "21", "0.17"),
]


def blocks(ctx):
    us = S.etsy(25, 5, list_=0.20, pp=3, pf=0.25, rof=0, vat=0, cost=8, post=4.5)
    usa = S.etsy(25, 5, list_=0.20, pp=3, pf=0.25, rof=0, vat=0, cost=8, post=4.5, ads=15)
    uk = S.etsy(25, 5, list_=0.15, pp=4, pf=0.20, rof=0.48, vat=20, cost=8, post=4.5)
    m = lambda x, c="USD": S.fm(x, c, True)  # noqa: E731
    f = us["f"]
    return [
        ("What Etsy takes from a sale", f"""
<p>On a $25 item with $5 shipping, a US shop pays Etsy <b>{m(us["fees"])}</b>, or {S.pc(us["pct"], True)} of what the buyer
pays: {m(f["list"])} listing fee, {m(f["tx"])} transaction fee (6.5% of $30) and {m(f["proc"])} payment processing (3% +
$0.25). Etsy deposits {m(us["net"])}; with an $8 product and a $4.50 label, the profit is <b>{m(us["profit"])}</b>. If the
order came through Offsite Ads at 15%, fees jump to {m(usa["fees"])} and the profit falls to {m(usa["profit"])}.</p>
<p>The same £25 + £5 sale from a UK shop that is not VAT-registered costs {m(uk["fees"], "GBP")}: processing is 4% + £0.20,
the regulatory operating fee is 0.48% and Etsy adds 20% VAT to every fee. Pick your shop country and the presets change;
every number stays editable under "More options".</p>"""),
        ("Every fee, as of November 2026", """
<ul>
<li><b>Listing</b>: $0.20 per listing, billed in your currency at the day's rate. It lasts four months and renews on each
sale of a multi-quantity listing.</li>
<li><b>Transaction</b>: 6.5% of the item price plus the shipping and gift wrap you charge.</li>
<li><b>Payment processing</b> (Etsy Payments), by the country of your bank account: US 3% + $0.25, Canada 3% + C$0.25
(4% for international orders), Australia 3% + A$0.25 (4% international), UK 4% + £0.20, euro countries 4% + €0.30. It is
charged on the order total, shipping and sales tax included.</li>
<li><b>Regulatory operating fee</b>, since 22 June 2026: France 1.14%, Spain 0.88%, Italy 0.80%, UK 0.48%, Canada 1.15%;
none in the US, Germany, the Netherlands or Australia.</li>
<li><b>Offsite Ads</b>: 15% of a sale that comes from an Etsy ad on Google, Instagram or Pinterest, or 12% and mandatory once
your shop has made $10,000 in the last 12 months, capped at $100 per order.</li>
<li><b>Currency conversion</b>: 2.5% when the listing currency differs from your payment account currency.</li>
</ul>"""),
        ("Tax on Etsy fees", """
<p>Etsy charges VAT or GST on its own fees in many countries: 20% in the UK, the local rate in EU countries, 10% GST in
Australia and GST/HST in Canada. A VAT-registered seller in the UK or EU who adds a valid VAT number to the shop is billed
without it (reverse charge) and accounts for it in the VAT return; everyone else pays it as a cost. Set "Tax on fees" to 0
if that is your case. US sellers pay no tax on fees.</p>"""),
        ("Break-even price", f"""
<p>All percentage fees add up to k = (6.5% + processing + regulatory + ads) × (1 + tax on fees), and the fixed ones to
(listing + fixed processing) × (1 + tax). The price that leaves zero profit is (cost + postage + fixed) ÷ (1 − k), minus the
shipping you charge. For the US example that is {m(us["be"])}, or {m(usa["be"])} with Offsite Ads. Anything below it loses
money on every order.</p>"""),
    ]


FAQ = [
    ("How much does Etsy take per sale?",
     "In the US, 6.5% transaction plus 3% + $0.25 processing, plus the $0.20 listing fee: about 11% of the order total "
     "on a typical $30 order. Offsite Ads add 12% or 15% on the orders they bring."),
    ("Does Etsy charge fees on shipping?",
     "Yes. The transaction fee, payment processing, the regulatory operating fee and Offsite Ads all apply to the item price "
     "plus shipping. Moving money from price to shipping does not lower the fees."),
    ("Can I turn off Offsite Ads?",
     "Only while your shop has sold less than $10,000 in the past 12 months: Shop Manager, Settings, Offsite Ads. Above that "
     "they are mandatory at 12%."),
    ("Why do I pay VAT on Etsy fees?",
     "Etsy sells you a service, so it charges the VAT or GST of your shop's country on its fees. A VAT-registered business "
     "that gives Etsy its VAT number is billed without it and handles it through the reverse charge."),
    ("What is Etsy's regulatory operating fee?",
     "A percentage of each order that Etsy charges in a few countries to cover digital services taxes. Since 22 June 2026 it is "
     "1.14% in France, 0.88% in Spain, 0.80% in Italy and 0.48% in the UK."),
]

JS = r"""
function (v, H, C) {
""" + S.FMT_JS + S.ETSY_JS + r"""
  var n = ['price', 'ship', 'cost', 'post', 'wrap', 'list', 'pp', 'pf', 'rof', 'vat'];
  for (var i = 0; i < n.length; i++) {
    if (n[i] !== 'price' && isNaN(v[n[i]])) v[n[i]] = 0;
    else if (isNaN(v[n[i]]) || v[n[i]] < 0) return { err: n[i] === 'price' ? 'Enter the item price.' : 'Amounts cannot be negative.' };
  }
  if (v.price <= 0) return { err: 'Enter the item price.' };
  var cur = v.cur || 'USD', e = function (x) { return fm(x, cur, true); };
  var r = etsy({ price: v.price, ship: v.ship, wrap: v.wrap, list: v.list, pp: v.pp, pf: v.pf, rof: v.rof, ads: +v.ads,
    vat: v.vat, conv: v.conv, cost: v.cost, post: v.post }), f = r.f;
  var rows = [['Listing', e(f.list)], ['Transaction 6.5%', e(f.tx)], ['Processing ' + pc(v.pp, true, 0) + ' + ' + e(v.pf), e(f.proc)]];
  if (f.rof) rows.push(['Regulatory ' + pc(v.rof, true, 2), e(f.rof)]);
  if (f.ads) rows.push(['Offsite Ads ' + v.ads + '%', e(f.ads)]);
  if (f.conv) rows.push(['Conversion 2.5%', e(f.conv)]);
  if (r.vat) rows.push(['Tax on fees ' + pc(v.vat, true, 0), e(r.vat)]);
  rows.push(['Fees · ' + pc(r.pct, true), e(r.fees), 'tot']);
  rows.push(['Etsy pays you', e(r.net), 'sub']);
  var hasCost = v.cost || v.post;
  if (hasCost) rows.push(['Profit · ' + pc(r.margin, true), e(r.profit), r.profit < 0 ? 'z' : 'tot']);
  rows.push(['Break-even price', isNaN(r.be) ? '—' : e(Math.max(0, r.be))]);
  return {
    label: hasCost ? 'Profit per sale' : 'You keep', big: e(hasCost ? r.profit : r.net),
    sub: 'Buyer pays ' + e(r.sale) + ' · Etsy ' + e(r.fees),
    rows: rows,
    n: { fees: r.fees, net: r.net, profit: r.profit, be: r.be }
  };
}
"""

TOOL = {
    "slug": "etsy-fee-calculator",
    "lang": "en",
    "twin": "comisiones-etsy",
    "cat": "sellers",
    "icon": "building-store",
    "order": 10,
    "name": "Etsy fee calculator",
    "k": "etsy fees profit offsite ads vat seller",
    "title": "Etsy Fee Calculator 2026: Fees, Profit and Payout",
    "desc": "See what Etsy takes from each sale in the US, UK, Canada, Australia or the EU: 6.5% transaction, processing, Offsite Ads, VAT on fees and profit.",
    "h1": "Etsy fee calculator",
    "intro": "Fees as of November 2026, by shop country.",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "shop", "type": "select", "label": "Shop country", "value": "us", "custom": "x",
         "options": [(k, lab, {"cur": c, "pp": str(pp), "pf": pf, "rof": rof, "vat": vat, "list": li}) for k, lab, c, pp, pf, rof, vat, li in SHOPS]
         + [("x", "Other")]},
        {"id": "price", "type": "number", "label": "Item price", "value": "25", "step": "0.01"},
        {"id": "ship", "type": "number", "label": "Shipping charged", "value": "5", "step": "0.01"},
        {"id": "cost", "type": "number", "label": "Item cost", "value": "8", "step": "0.01"},
        {"id": "post", "type": "number", "label": "Postage paid", "value": "4.50", "step": "0.01"},
        {"id": "ads", "type": "seg", "label": "Offsite Ads", "value": "0", "options": [("0", "No"), ("15", "15%"), ("12", "12%")]},
        {"id": "cur", "type": "select", "label": "Currency", "value": "USD", "more": True,
         "options": [("USD", "USD $"), ("GBP", "GBP £"), ("EUR", "EUR €"), ("CAD", "CAD C$"), ("AUD", "AUD A$")]},
        {"id": "list", "type": "number", "label": "Listing fee", "value": "0.20", "step": "0.01", "more": True, "w": "s"},
        {"id": "pp", "type": "number", "label": "Processing", "value": "3", "unit": "%", "step": "0.1", "more": True, "w": "s"},
        {"id": "pf", "type": "number", "label": "Processing fixed", "value": "0.25", "step": "0.01", "more": True, "w": "s"},
        {"id": "rof", "type": "number", "label": "Regulatory fee", "value": "0", "unit": "%", "step": "0.01", "more": True, "w": "s"},
        {"id": "vat", "type": "number", "label": "Tax on fees", "value": "0", "unit": "%", "more": True, "w": "s"},
        {"id": "wrap", "type": "number", "label": "Gift wrap", "value": "0", "step": "0.01", "more": True, "w": "s"},
        {"id": "conv", "type": "check", "label": "Currency conversion", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Etsy · Payment processing fees by country", S.ETSY_FEES),
                ("Etsy · Fees & Payments Policy", "https://www.etsy.com/legal/fees/"),
                ("Etsy · Regulatory operating fee updates (22 Jun 2026)", S.ETSY_ROF)],
    "related": ["etsy-listing-checker", "selling-price-calculator", "break-even-calculator", "kdp-royalty-calculator"],
    "tests": [
        ({}, {"n.fees": 3.30, "n.net": 26.70, "n.profit": 14.20}),
        ({"ads": "15"}, {"n.fees": 7.80}),
        ({"shop": "uk", "cur": "GBP", "pp": "4", "pf": "0.20", "rof": "0.48", "vat": "20", "list": "0.15"}, {"n.fees": 4.3728}),
        ({"price": ""}, {"err": "Enter the item price."}),
        ({"cost": "-1"}, {"err": "Amounts cannot be negative."}),
    ],
}
