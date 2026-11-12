"""Coffee ratio calculator (English twin of ratio-cafe): same compute, English strings."""
from herramientas.tools._cocina import CAT
from herramientas.tools.ratio_cafe import JS, SCA, T_EN, inputs

FAQ = [
    ("How many grams of coffee per cup?",
     "For pour-over, about 15-16 g of coffee per 250 ml (8.5 fl oz) of water, a 1:16 ratio. The Specialty Coffee Association's Golden "
     "Cup reference is 55 g per litre, or 8.25 g per 150 ml, slightly milder. French press is usually a bit stronger, around 17 g per "
     "250 ml."),
    ("What does a 1:16 coffee ratio mean?",
     "One gram of coffee for every 16 grams (or millilitres) of water. 30 g of coffee to 480 ml of water is 1:16. The smaller the second "
     "number, the stronger the brew."),
    ("How much coffee for a 12-cup coffee maker?",
     "A «cup» on a drip machine is usually 5 to 6 fl oz, so 12 cups is roughly 1.8 litres of water. At 1:16 that is about 110 g of "
     "coffee, about 4 oz. Use the «Cups» option with your machine's cup size."),
    ("What is the espresso brew ratio?",
     "A double espresso typically uses 16-20 g of coffee and yields 32-40 g in the cup (1:2) in about 25-30 seconds. A ristretto stops "
     "earlier (1:1.5) and a lungo runs longer (1:3). Weigh the drink, not the water."),
    ("What ratio for cold brew?",
     "Coarse coffee and cold water at about 1:8 for a concentrate, 12 to 24 hours in the fridge, strained and served cut 1:1 with "
     "water or milk. For ready-to-drink cold brew, use 1:15 or 1:16."),
]


def blocks(ctx):
    return [
        ("How the amounts are worked out", """
<p>Pick a method, then enter the water you will use (or the coffee you have, or how many cups you want) and the ratio. Coffee is
<b>water ÷ ratio</b>: 500 ml of water at 1:16 needs <b>31 g of coffee</b>. Going the other way, 30 g of coffee at 1:15 in a French
press takes 450 ml of water. Water can be measured in millilitres or grams, since a millilitre of water weighs a gram; a kitchen
scale under the brewer is the easiest way to pour accurately.</p>
<p>Not all the water reaches the cup: spent grounds keep about 2 g of water per gram of coffee, so those 500 ml give about 440 ml
of coffee. Espresso is the exception: its ratio is measured on the beverage weight, so 18 g of coffee at 1:2 means 36 g of espresso
in the cup.</p>"""),
        ("Reference ratios", """
<table class="tbl"><thead><tr><th>Method</th><th>Ratio</th><th>For 500 ml water</th></tr></thead><tbody>
<tr><td>Pour-over, V60, Chemex</td><td class="num">1:15 to 1:17</td><td class="num">29-33 g</td></tr>
<tr><td>SCA Golden Cup</td><td class="num">1:18.2 (55 g/L)</td><td class="num">27.5 g</td></tr>
<tr><td>French press</td><td class="num">1:12 to 1:15</td><td class="num">33-42 g</td></tr>
<tr><td>Moka pot</td><td class="num">≈ 1:10</td><td class="num">50 g</td></tr>
<tr><td>Cold brew concentrate</td><td class="num">1:8</td><td class="num">62.5 g</td></tr>
<tr><td>Espresso</td><td class="num">1:2 (by yield)</td><td class="num">—</td></tr>
</tbody></table>
<p>These are starting points. Weak or sour coffee: lower the ratio (more coffee) or grind finer. Bitter and harsh: raise it or grind
coarser. Change one thing at a time and note what you did.</p>"""),
    ]


TOOL = {
    "slug": "coffee-ratio-calculator",
    "lang": "en",
    "twin": "ratio-cafe",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "coffee",
    "order": 90,
    "name": "Coffee ratio",
    "k": "coffee to water ratio grams pour over v60 chemex french press espresso cold brew moka",
    "title": "Coffee to Water Ratio Calculator (Grams)",
    "desc": "How many grams of coffee and water for pour-over, Chemex, French press, moka pot, cold brew or espresso, from any brew ratio or number of cups.",
    "h1": "Coffee ratio calculator",
    "crumb": "Coffee ratio",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Specialty Coffee Association · Coffee standards", SCA)],
    "related": ["homebrew-calculator", "cups-to-grams", "party-food-calculator", "oven-temperature-conversion"],
    "tests": [
        ({}, {"n.coffee": 31.25}),
        ({"base": "tazas", "tazas": "12", "ml": "150"}, {"n.coffee": 112.5}),
        ({"met": "cold", "rat": "8", "agua": "1000"}, {"n.coffee": 125}),
        ({"base": "cafe", "cafe": ""}, {"err": T_EN["e_cafe"]}),
    ],
}
