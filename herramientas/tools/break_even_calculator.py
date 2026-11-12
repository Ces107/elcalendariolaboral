"""Break-even calculator: units and revenue to cover fixed costs, with selling fees and a target profit.
Spanish twin: punto_equilibrio.py (same core)."""
import math

from herramientas.tools.punto_equilibrio import CORE_JS, OPENSTAX, be


def usd(x):
    return f"${x:,.2f}"


def blocks(ctx):
    a = be(600, 25, 9)
    b = be(600, 25, 9, 13)
    c = be(600, 25, 9, 13, 400)
    p = be(600, 27.5, 9)
    return [
        ("How many sales you need", f"""
<p>An online shop with <b>$600 a month in fixed costs</b> (platform subscription, software, insurance, storage) sells an
item at $25 that costs $9 to make and ship. Each sale leaves $16 to cover the fixed costs: the <b>contribution margin</b>.
600 ÷ 16 = {a["u"]:.1f}, so the shop needs <b>{a["uc"]} sales a month</b>, about {math.ceil(a["uc"] / 30 * 7)} a week, to stop
losing money. From sale {a["uc"] + 1} on, every order adds $16 of profit.</p>
<p>Sell through a marketplace that keeps 13% of the price and the contribution margin drops to {usd(b["cm"])}, pushing
break-even to <b>{b["uc"]} sales</b>; earning $400 a month on top takes {c["uc"]}. Raising the price 10% to $27.50, with no
fees, cuts break-even to {p["uc"]} sales: a 10% price change moves the target by {100 - p["u"] / a["u"] * 100:.0f}%.</p>"""),
        ("The formula", f"""
<p>Break-even units = fixed costs ÷ (price − variable cost per unit). Break-even revenue = fixed costs ÷ contribution margin
ratio, where the ratio is (price − variable cost) ÷ price. In the example, 16 ÷ 25 = 0.64 and 600 ÷ 0.64 =
{usd(a["revx"])} of sales a month. For a target profit, add it to the fixed costs: (600 + 400) ÷ margin. This is standard
cost-volume-profit analysis, as taught in <a href="{OPENSTAX}" rel="noopener">OpenStax's Principles of Managerial
Accounting</a>.</p>"""),
        ("What goes in each box", """
<ul>
<li><b>Fixed costs</b>: what you pay in a month even with zero sales: rent, subscriptions, insurance, an accountant, the
fixed part of your ad budget.</li>
<li><b>Price</b>: the selling price before sales tax or VAT, which you only collect for the government.</li>
<li><b>Cost per unit</b>: materials, packaging, postage you pay, print-on-demand cost; anything that grows with each sale.</li>
<li><b>Fees</b>: the share of the price that the marketplace or payment processor keeps (Etsy, Amazon, PayPal, Stripe).</li>
</ul>
<p>Not sure whether a cost is fixed or variable? Ask whether it would double if your sales doubled. If yes, it is
variable.</p>"""),
    ]


FAQ = [
    ("What is the break-even point?",
     "The sales volume at which revenue exactly covers all costs, so you neither make nor lose money. Below it you lose; above "
     "it each sale's contribution margin is profit."),
    ("How do I calculate break-even units?",
     "Fixed costs ÷ (price − variable cost per unit). With $600 of fixed costs, a $25 price and a $9 cost: 37.5, so 38 units."),
    ("Should the price include sales tax or VAT?",
     "No. Use the price before tax: the tax is collected for the government and does not pay your costs."),
    ("How can I lower my break-even point?",
     "Raise the price, cut the cost per unit or trim fixed costs. Price usually moves it most, because every extra dollar goes "
     "straight to contribution margin."),
    ("Does my own salary count as a fixed cost?",
     "If the business is meant to pay you, yes: add it to fixed costs or enter it as the target profit."),
]

JS = r"""
function (v, H, C) {
""" + CORE_JS + r"""
  var F = v.fixed, P = v.price, V = isNaN(v.unit) ? 0 : v.unit, fee = isNaN(v.fee) ? 0 : v.fee, T = isNaN(v.target) ? 0 : v.target;
  if (isNaN(F) || F < 0) return { err: 'Enter your monthly fixed costs.' };
  if (isNaN(P) || P <= 0) return { err: 'Enter the selling price.' };
  if (V < 0 || T < 0 || fee < 0 || fee >= 100) return { err: 'Check the amounts.' };
  var r = be(F, P, V, fee, T);
  if (!r) return { err: 'The price does not cover the cost per unit: every sale loses money.' };
  var e = function (x) { var a = Math.abs(x).toFixed(2).split('.'); return (x < -0.004 ? '−' : '') + a[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '.' + a[1]; };
  var tb = '<table class="tbl"><thead><tr><th>Units</th><th class="num">Revenue</th><th class="num">Profit</th></tr></thead><tbody>' +
    r.at.map(function (x) { return '<tr><td>' + x[0] + '</td><td class="num">' + e(x[1]) + '</td><td class="num"' + (x[2] < 0 ? ' style="color:var(--red)"' : '') + '>' + e(x[2]) + '</td></tr>'; }).join('') +
    '</tbody></table>';
  return {
    label: T ? 'Units to make ' + e(T) : 'Break-even point', big: r.uc + ' ' + (r.uc === 1 ? 'unit' : 'units'),
    sub: 'Revenue ' + e(r.rev) + ' · about ' + Math.ceil(r.uc / 30) + ' a day',
    rows: [['Margin per unit', e(r.cm)], ['Margin ratio', (r.ratio * 100).toFixed(1) + '%'], ['Break-even revenue', e(r.revx), 'tot']],
    html: tb, n: { uc: r.uc, cm: r.cm, revx: r.revx }
  };
}
"""

TOOL = {
    "slug": "break-even-calculator",
    "lang": "en",
    "twin": "punto-equilibrio",
    "cat": "sellers",
    "icon": "chart-line",
    "order": 80,
    "name": "Break-even calculator",
    "k": "break even units sales fixed costs contribution margin",
    "title": "Break-Even Calculator: Units and Revenue to Cover Costs",
    "desc": "Find how many units you must sell each month to cover fixed costs, from your price, cost per unit and marketplace fees, plus a target profit.",
    "h1": "Break-even calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "fixed", "type": "number", "label": "Fixed costs / month", "value": "600", "step": "0.01"},
        {"id": "price", "type": "number", "label": "Price before tax", "value": "25", "step": "0.01"},
        {"id": "unit", "type": "number", "label": "Cost per unit", "value": "9", "step": "0.01"},
        {"id": "fee", "type": "number", "label": "Fees", "value": "0", "unit": "%", "step": "0.1", "w": "s"},
        {"id": "target", "type": "number", "label": "Target profit", "value": "0", "step": "0.01", "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("OpenStax · Principles of Managerial Accounting, 3.2 Break-even point", OPENSTAX)],
    "related": ["selling-price-calculator", "etsy-fee-calculator", "kdp-royalty-calculator"],
    "tests": [
        ({}, {"n.uc": 38, "n.cm": 16, "n.revx": 937.5}),
        ({"fee": "13"}, {"n.uc": 48}),
        ({"target": "400"}, {"n.uc": 63}),
        ({"price": "8"}, {"err": "The price does not cover the cost per unit: every sale loses money."}),
        ({"price": ""}, {"err": "Enter the selling price."}),
    ],
}
