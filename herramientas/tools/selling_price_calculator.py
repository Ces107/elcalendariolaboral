"""Selling price from cost with a target margin or markup, sales tax / VAT and marketplace fee, rounded to .99.
Spanish twin: precio_venta_margen.py (same core)."""
from herramientas.tools.precio_venta_margen import CORE_JS, price

HMRC = "https://www.gov.uk/guidance/rates-of-vat-on-different-goods-and-services"


def usd(x):
    return f"${x:,.2f}"


def blocks(ctx):
    m = price(10, "margen", 40, 0)
    k = price(10, "recargo", 40, 0)
    f = price(10, "margen", 40, 0, 11)
    uk = price(10, "margen", 40, 20)
    return [
        ("Margin and markup are not the same", f"""
<p>An item that costs you $10, sold at a <b>40% margin</b>: margin is a share of the selling price, so the price is
10 ÷ (1 − 0.40) = <b>{usd(m["net"])}</b> and you make {usd(m["profit"])}, which is 40% of {usd(m["net"])}. Apply a <b>40%
markup</b> instead and the price is 10 × 1.40 = {usd(k["net"])}: you make {usd(k["profit"])}, a margin of only 28.6%. Mixing
the two up is the most common pricing mistake in small shops: a 40% markup sounds generous and leaves little.</p>
<p>The conversion never changes: margin = markup ÷ (1 + markup), and markup = margin ÷ (1 − margin). A 50% margin is a 100%
markup (selling at twice the cost); a 25% markup is a 20% margin.</p>"""),
        ("With marketplace fees", f"""
<p>When a marketplace takes a percentage of the final price, that percentage eats margin too. Keep the $10 item and add 11%
in fees (about what Etsy takes in the US on a $30 order): to keep a true 40% margin the price rises to {usd(f["net"])}.
Fees are charged on what the customer pays, tax included, so the formula is price = cost ÷ (1 − margin − fee × (1 + tax)).
Tick "End in .99" to round the final price up ($16.67 becomes $16.99); the margin shown is recalculated on the rounded
price.</p>"""),
        ("Sales tax and VAT", f"""
<p>In the US, prices are usually shown before sales tax, so leave tax at 0% and let the checkout add it. In the UK and EU,
consumer prices include VAT: a UK business charging 20% VAT needs {usd(uk["gross"]).replace("$", "£")} on the shelf for
the same 40% margin on a £10 cost, because the VAT part ({usd(uk["gross"] - uk["net"]).replace("$", "£")}) is not yours.
Reduced rates exist for some goods (in the UK, 5% for things like children's car seats and 0% for most food and books;
<a href="{HMRC}" rel="noopener">HMRC's list</a>). Margin is always worked out on the price before tax.</p>"""),
    ]


FAQ = [
    ("How do I calculate a selling price from a margin?",
     "Divide the cost by (1 − margin). With a $10 cost and a 30% margin: 10 ÷ 0.70 = $14.29."),
    ("What is the difference between margin and markup?",
     "Margin is profit as a share of the selling price; markup is profit as a share of the cost. A 50% margin equals a 100% "
     "markup."),
    ("Is margin calculated before or after tax?",
     "Before. Sales tax and VAT are collected for the government, so they are not part of your revenue or your margin."),
    ("What margin should a handmade product have?",
     "It depends on overheads, but below a 30% true margin after fees it is hard to pay for your time, returns and ads."),
    ("How do I turn a margin into a markup?",
     "Markup = margin ÷ (1 − margin). A 40% margin is a 66.7% markup."),
]

JS = r"""
function (v, H, C) {
""" + CORE_JS + r"""
  var c = v.cost, fee = isNaN(v.fee) ? 0 : v.fee, tax = isNaN(v.tax) ? 0 : v.tax;
  if (isNaN(c) || c <= 0) return { err: 'Enter the cost.' };
  if (isNaN(v.pct) || v.pct < 0) return { err: 'Enter the percentage.' };
  if (fee < 0 || fee >= 100 || tax < 0 || tax > 100) return { err: 'Check the tax and fee percentages.' };
  if (v.mode === 'margen' && v.pct >= 100) return { err: 'Margin must be below 100%.' };
  var r = price(c, v.mode, v.pct, tax, fee, v.r99);
  if (!r) return { err: 'That margin is not reachable with that fee.' };
  var e = function (x) { var a = Math.abs(x).toFixed(2).split('.'); return (x < -0.004 ? '−' : '') + a[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '.' + a[1]; };
  var rows = [['Price before tax', e(r.net)]];
  if (tax) rows.push(['Tax ' + tax + '%', e(r.tax)]);
  if (fee) rows.push(['Fees ' + fee + '%', '−' + e(r.fee)]);
  rows.push(['Profit', e(r.profit), 'tot'], ['True margin', r.margin.toFixed(1) + '%'], ['Markup on cost', r.markup.toFixed(1) + '%']);
  return { label: tax ? 'Selling price with tax' : 'Selling price', big: e(r.gross), sub: 'Profit ' + e(r.profit) + ' per unit',
    rows: rows, n: { net: r.net, gross: r.gross, profit: r.profit, margin: r.margin } };
}
"""

TOOL = {
    "slug": "selling-price-calculator",
    "lang": "en",
    "twin": "precio-venta-margen",
    "cat": "sellers",
    "icon": "tag",
    "order": 70,
    "name": "Selling price calculator",
    "k": "margin markup price cost profit vat sales tax",
    "title": "Selling Price Calculator: From Cost, Margin or Markup",
    "desc": "Work out the selling price from your cost and the margin or markup you want, with sales tax or VAT and marketplace fees, rounded to .99.",
    "h1": "Selling price calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "cost", "type": "number", "label": "Cost", "value": "10", "step": "0.01"},
        {"id": "mode", "type": "seg", "label": "Based on", "value": "margen", "options": [("margen", "Margin"), ("recargo", "Markup")]},
        {"id": "pct", "type": "number", "label": "Percentage", "value": "40", "unit": "%", "step": "0.1", "w": "s"},
        {"id": "tax", "type": "number", "label": "Sales tax / VAT", "value": "0", "unit": "%", "step": "0.1", "w": "s"},
        {"id": "r99", "type": "check", "label": "End in .99", "value": False},
        {"id": "fee", "type": "number", "label": "Marketplace fee", "value": "0", "unit": "%", "step": "0.1", "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("HMRC · VAT rates on goods and services", HMRC)],
    "related": ["break-even-calculator", "etsy-fee-calculator", "kdp-royalty-calculator"],
    "tests": [
        ({}, {"n.net": 16.666667, "n.gross": 16.666667, "n.profit": 6.666667, "n.margin": 40}),
        ({"mode": "recargo"}, {"n.net": 14}),
        ({"r99": "1"}, {"n.gross": 16.99}),
        ({"tax": "20"}, {"n.gross": 20}),
        ({"pct": "120"}, {"err": "Margin must be below 100%."}),
        ({"fee": "11", "pct": "40"}, {"n.margin": 40}),
    ],
}
