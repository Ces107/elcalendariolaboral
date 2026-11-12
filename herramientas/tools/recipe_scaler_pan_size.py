"""Recipe scaler and pan size converter (English twin of escalar-receta): same compute, inches or cm."""
from herramientas.tools._cocina import CAT
from herramientas.tools.escalar_receta import JS, T_EN, inputs

FAQ = [
    ("How do I convert a recipe from an 8-inch to a 9-inch round pan?",
     "Scale by the ratio of the areas, not the diameters: (9 ÷ 8)² = 1.27. A 9-inch round has 27 % more surface than an 8-inch, so "
     "multiply every ingredient by about 1.27 for the same depth. From 9 to 10 inches the factor is 1.23."),
    ("Can I bake a two-layer 9-inch cake in a 9 × 13 pan?",
     "Almost: two 9-inch rounds are 127 square inches and a 9 × 13 is 117, so the batter fills it a little deeper. It works for most "
     "butter cakes; bake at the same temperature and start checking about 10 minutes later than the layer time."),
    ("How do I halve a recipe with 3 eggs?",
     "That is 1.5 eggs. Beat two eggs and use three quarters of it, or use one egg plus one yolk. A large US egg is about 50 g without the "
     "shell, so you can also weigh 75 g of beaten egg."),
    ("Does the baking time change when I scale a recipe?",
     "If the batter depth stays the same, the time changes little. Deeper batter (a smaller pan for the same amount) needs longer, and "
     "sometimes 25 °F less so the outside does not overbake before the middle sets. Use a toothpick test."),
    ("Can I paste my ingredient list?",
     "Yes: start each ingredient with its quantity and separate them with semicolons («2 1/4 cups flour; 2 eggs; 1/2 tsp salt»). "
     "Fractions like 1/2, mixed numbers like 1 1/2 and characters like ½ all work."),
]


def blocks(ctx):
    return [
        ("How the scaling works", """
<p>For servings, the factor is simply <b>servings you need ÷ servings in the recipe</b>: from 4 to 6, × 1.5. For pans, what matters
is the surface area. An 8-inch round is 50.3 square inches and a 9-inch round is 63.6, so the factor is <b>1.27</b>, not 1.125. That
is why a cake written for an 8-inch pan comes out thin and dry when baked unchanged in a 9-inch one. Inches or centimetres both work,
as long as both pans use the same unit.</p>
<p>Paste the ingredient list and every quantity is multiplied. At × 1.27, a recipe with 1½ cups of flour, 1 cup of sugar, 2 eggs and
½ cup of milk becomes <b>1.9 cups of flour, 1.27 cups of sugar, 2.53 eggs (call it 2 large plus a yolk) and 0.63 cup of milk</b>.
For exact baking, convert the cups to grams first.</p>"""),
        ("Common pan sizes", """
<table class="tbl"><thead><tr><th>Pan</th><th>Area</th><th>Factor from 9-inch round</th></tr></thead><tbody>
<tr><td>8-inch round</td><td class="num">50 sq in</td><td class="num">0.79</td></tr>
<tr><td>9-inch round</td><td class="num">64 sq in</td><td class="num">1</td></tr>
<tr><td>10-inch round</td><td class="num">79 sq in</td><td class="num">1.23</td></tr>
<tr><td>8-inch square</td><td class="num">64 sq in</td><td class="num">1.01</td></tr>
<tr><td>9-inch square</td><td class="num">81 sq in</td><td class="num">1.27</td></tr>
<tr><td>9 × 13 inch</td><td class="num">117 sq in</td><td class="num">1.84</td></tr>
<tr><td>Half sheet, 13 × 18 inch</td><td class="num">234 sq in</td><td class="num">3.68</td></tr>
</tbody></table>
<p>An 8-inch square and a 9-inch round hold almost exactly the same batter, which is the most useful swap to remember. Salt,
spices and baking powder usually scale fine in small steps; beyond doubling, taste and adjust.</p>"""),
    ]


TOOL = {
    "slug": "recipe-scaler-pan-size",
    "lang": "en",
    "twin": "escalar-receta",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "tools-kitchen-2",
    "order": 80,
    "name": "Recipe scaler",
    "k": "servings pan size round square 9x13 8 inch 9 inch convert recipe cake",
    "title": "Recipe Scaler and Cake Pan Size Converter",
    "desc": "Scale a recipe up or down by servings or by pan size (round, square or 9 × 13), and multiply your pasted ingredient list automatically.",
    "h1": "Recipe scaler and pan size converter",
    "crumb": "Recipe scaler",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("NIST · Unit conversion", "https://www.nist.gov/pml/owm/metric-si/unit-conversion")],
    "related": ["cups-to-grams", "bakers-percentage-calculator", "oven-temperature-conversion", "party-food-calculator"],
    "tests": [
        ({"modo": "m"}, {"n.k": 1.27}),
        ({"modo": "m", "a1": "9", "f2": "x", "a2": "9", "b2": "13"}, {"n.k": 1.84}),
        ({"ing": "2 1/4 cups flour; 2 eggs; ½ tsp salt; 1/2 cup milk", "r1": "2", "r2": "4"}, {"n.items": [4.5, 4, 1, 1]}),
        ({"modo": "m", "a2": ""}, {"err": T_EN["e_m2"]}),
    ],
}
