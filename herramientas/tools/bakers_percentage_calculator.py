"""Baker's percentage calculator (English twin of porcentaje-panadero): same compute, English strings."""
from herramientas.tools._cocina import CAT
from herramientas.tools.porcentaje_panadero import JS, KA, KAY, T_EN, inputs

FAQ = [
    ("What is baker's percentage?",
     "A way of writing bread formulas where the total flour is always 100 % and every other ingredient is a percentage of the "
     "flour weight. That is why the numbers add up to more than 100: 70 % water, 2 % salt and 1.5 % fresh yeast make 173.5 %."),
    ("How do I work out the hydration of my dough?",
     "Divide the water by the flour and multiply by 100: 650 g of water to 1,000 g of flour is 65 % hydration. With a sourdough "
     "starter, add the flour and water inside the starter to both sides first; that is the true (total) hydration."),
    ("How much salt goes in bread?",
     "Most lean breads use 1.8 to 2.2 % of the flour weight, 18 to 22 g per kilo. Under 1.5 % tastes flat; above 2.5 % salt starts "
     "to slow the yeast noticeably."),
    ("Is the yeast percentage fresh or dry yeast?",
     "Professional formulas (Hamelman, the Bread Bakers Guild) usually quote fresh compressed yeast. Multiply by 0.4 for active "
     "dry and by about one third for instant: 1.5 % fresh is 0.6 % active dry or 0.5 % instant. Pick the type you use and the "
     "note under the result shows the other two."),
    ("Can I use cups instead of grams?",
     "Baker's percentages only work by weight, because a cup of flour can weigh anything from 115 to 150 g depending on how it is "
     "scooped. If your recipe is in cups, convert it first with the cups to grams tool."),
    ("What is the loss field for?",
     "Some dough always stays in the bowl, on the bench and on your hands. Adding 2 to 3 % makes each divided piece come out at "
     "the target weight instead of a few grams short."),
]


def blocks(ctx):
    return [
        ("How it works", """
<p>Enter the flour you have, the dough weight you want, or the number and weight of loaves, then your formula in percentages. The
calculator returns grams for every ingredient. Everything is relative to <b>total flour = 100 %</b>: 70 % water means 700 g of
water for every 1,000 g of flour. Bakers write formulas this way because they scale instantly: twice the bread, twice the flour,
same percentages.</p>
<p>Going from dough weight back to flour is a single division: flour = dough ÷ (sum of percentages ÷ 100). For 1,600 g of dough at
70 % water, 2 % salt and 1.5 % fresh yeast you need 1,600 ÷ 1.735 = <b>922 g of flour</b>, 646 g of water, 18 g of salt and 14 g of
yeast. Grams are far more reliable than cups for this: a level cup of all-purpose flour is 125 g in the USDA tables, but a packed
one easily reaches 150 g.</p>"""),
        ("Sourdough and true hydration", """
<p>A starter is flour and water too. «20 % starter at 100 % hydration» on 1,000 g of flour is 200 g of starter holding 100 g of
flour and 100 g of water. To keep the whole dough at 70 %, you add only 900 g of flour and 600 g of water. The calculator does that
subtraction and shows what the starter contributes, so a formula written in total hydration does not turn into a soup. If you keep
a stiff starter (50-60 %), change it under «More options».</p>"""),
        ("Worked examples", """
<ul>
<li><b>Country loaf, 1,000 g flour</b>: 75 % water (750 g), 2 % salt (20 g), 20 % starter (200 g, so you add 900 g flour and
650 g water). Total dough 1,770 g: two loaves of about 885 g.</li>
<li><b>Six sandwich rolls of 120 g</b>: 720 g of dough. At 65 % water, 2 % salt and 0.5 % instant yeast, that is 430 g of flour
and 279 g of water.</li>
<li><b>Neapolitan-style pizza</b>: four 250 g balls at 62 % water, 2.8 % salt and 0.2 % instant yeast need 606 g of flour and
376 g of water. Add 2 % loss so the last ball is not light.</li>
</ul>"""),
    ]


TOOL = {
    "slug": "bakers-percentage-calculator",
    "lang": "en",
    "twin": "porcentaje-panadero",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "bread",
    "order": 10,
    "name": "Baker's percentage",
    "k": "bread hydration flour water salt yeast formula dough",
    "title": "Baker's Percentage Calculator with Dough Hydration",
    "desc": "Turn a bread formula in baker's percentages into grams of flour, water, salt and yeast, from flour, total dough weight or number of loaves.",
    "h1": "Baker's percentage calculator",
    "crumb": "Baker's percentage",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("King Arthur Baking · Baker's percentage", KA), ("King Arthur Baking · Yeast conversions", KAY)],
    "related": ["sourdough-starter-calculator", "recipe-scaler-pan-size", "cups-to-grams", "oven-temperature-conversion"],
    "tests": [
        ({}, {"n.flour": 1000, "n.water": 700, "n.dough": 1735}),
        ({"modo": "p", "piezas": "4", "peso": "250", "hid": "62", "sal": "2.8", "levt": "i", "lev": "0.2"}, {"n.flour": 606.06, "n.water": 375.76}),
        ({"hid": "75", "mm": "20", "lev": "0"}, {"n.addFlour": 900, "n.water": 650, "n.dough": 1770}),
        ({"sal": "12"}, {"err": T_EN["e_sal"]}),
    ],
}
