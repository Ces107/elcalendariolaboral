"""Sourdough starter calculator (English twin of masa-madre): same compute, English strings."""
from herramientas.tools._cocina import CAT
from herramientas.tools.masa_madre import JS, KAS, KAY, T_EN, inputs

FAQ = [
    ("What does a 1:1:1 or 1:5:5 feeding mean?",
     "Parts by weight of starter, flour and water. 1:1:1 is, say, 50 g starter, 50 g flour and 50 g water. 1:5:5 is 20 g starter "
     "with 100 g flour and 100 g water: the culture is more diluted, so it takes longer to peak, which suits an overnight feed."),
    ("How much starter replaces yeast in a recipe?",
     "Most bakers use 15 to 25 % active starter on the flour weight. More starter ferments faster and tastes tangier; less gives a "
     "longer, milder rise. The calculator takes the flour and water inside the starter out of the recipe so the dough feels the same."),
    ("How do I convert instant yeast to active dry or fresh?",
     "By leavening power, instant ≈ fresh ÷ 3 and active dry ≈ fresh × 0.4. One US packet (¼ oz, 7 g) of instant yeast is about "
     "21 g of fresh yeast or 8.4 g of active dry."),
    ("Why isn't my starter rising after feeding?",
     "Usually it is too cold (below 68 °F / 20 °C everything slows right down), the feed is too diluted for the time you give it, or "
     "the starter is still young. Try 1:1:1 somewhere warm and use it once it has doubled."),
    ("What is starter hydration?",
     "Water divided by flour, times 100. A 100 % starter has equal weights of water and flour; a stiff starter at 50-60 % has about "
     "half as much water. Change it under «More options» if yours is not 100 %."),
]


def blocks(ctx):
    return [
        ("Feeding: how much starter, flour and water", """
<p>Choose how much starter you need and the feeding ratio; the calculator splits the weight. For 200 g at 1:1:1 that is
<b>67 g starter, 67 g flour and 67 g water</b>. If tomorrow's dough needs 150 g of levain, build a little more than that (200 g)
so some is left to keep the culture going.</p>
<p>The ratio sets the timing. With wheat flour in a 75-79 °F (24-26 °C) kitchen, a healthy starter typically doubles in roughly
4 to 6 hours at 1:1:1 and needs considerably longer at 1:5:5 or 1:10:10, the ratios people use for an overnight build. Treat those
times as a rough guide: every culture, flour and kitchen runs at its own pace, and the reliable sign is volume doubled with bubbles
all through.</p>"""),
        ("Converting a yeasted recipe to sourdough", """
<p>Under «Swap yeast», enter the recipe's flour and water and the starter percentage you want (on the flour). For 500 g flour and
350 g water with 20 % starter at 100 % hydration you use <b>100 g of starter</b> and add only 450 g flour and 300 g water, because
the starter already brings 50 g of each. Hydration stays at 70 % and the salt stays the same (about 10 g, 2 %). All the commercial
yeast goes.</p>
<p>What does change is time: a naturally leavened dough ferments noticeably slower than a yeasted one and usually benefits from a
long cold retard in the fridge. Watch the dough, not the clock.</p>"""),
        ("Fresh, active dry and instant yeast", """
<p>All three are the same baker's yeast (<i>Saccharomyces cerevisiae</i>) with different moisture. For the same rise: <b>active dry
= fresh × 0.4</b> and <b>instant = fresh ÷ 3</b>. 25 g of fresh yeast is 10 g of active dry or 8.3 g of instant. Active dry is
traditionally proofed in warm water first; instant (rapid-rise, bread machine yeast) goes straight into the flour. There is no fixed
yeast-to-starter equivalent, because a starter's strength depends on how active it is; that is why it is measured as a percentage
of the flour.</p>"""),
    ]


TOOL = {
    "slug": "sourdough-starter-calculator",
    "lang": "en",
    "twin": "masa-madre",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "baguette",
    "order": 20,
    "name": "Sourdough starter",
    "k": "levain feeding ratio yeast conversion fresh instant active dry",
    "title": "Sourdough Starter Calculator: Feeding Ratio and Levain",
    "desc": "Work out starter feedings (1:1:1, 1:5:5), how much levain replaces yeast in a recipe, and fresh, active dry and instant yeast equivalents.",
    "h1": "Sourdough starter calculator",
    "crumb": "Sourdough starter",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("King Arthur Baking · Yeast conversions", KAY), ("King Arthur Baking · Sourdough starter", KAS)],
    "related": ["bakers-percentage-calculator", "recipe-scaler-pan-size", "oven-temperature-conversion", "cups-to-grams"],
    "tests": [
        ({}, {"n.starter": 66.67, "n.hyd": 100}),
        ({"modo": "c"}, {"n.levain": 100, "n.addFlour": 450, "n.addWater": 300}),
        ({"modo": "y", "cant": "7", "desde": "i"}, {"n.f": 21, "n.s": 8.4}),
        ({"obj": ""}, {"err": T_EN["e_obj"]}),
    ],
}
