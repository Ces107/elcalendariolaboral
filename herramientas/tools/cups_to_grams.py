"""Cups to grams (English twin of tazas-a-gramos): same compute and USDA cup weights, English strings."""
from herramientas.tools._cocina import CAT
from herramientas.tools.tazas_a_gramos import FDC, FDC_DL, ING, JS, NIST, T_EN, data, inputs

FAQ = [
    ("How many grams is 1 cup of flour?",
     "About 125 g for all-purpose flour spooned into the cup and leveled, per USDA FoodData Central. Scooping straight from the bag "
     "packs it down and can push a cup past 150 g, which is why baking recipes that list grams turn out more consistently. Bread flour "
     "is about 137 g a cup, whole wheat 120 g."),
    ("How many grams in a cup of sugar?",
     "200 g of granulated sugar, 220 g of brown sugar packed firmly, 120 g of powdered sugar straight from the box (100 g sifted)."),
    ("How many grams is a cup of butter?",
     "227 g, which is two US sticks (113.5 g each) or half a pound. One tablespoon of butter is 14.2 g."),
    ("Is a US cup the same as a metric cup?",
     "No. A US customary cup is 236.6 ml (nutrition labels round it to 240 ml); Australia, Canada and New Zealand use a 250 ml metric "
     "cup, about 6 % bigger. A UK recipe in «cups» usually means the 250 ml metric cup too. Pick the unit your recipe was written in."),
    ("How many grams in a tablespoon?",
     "It depends on the ingredient: roughly 8 g of flour, 12.5 g of sugar, 18 g of table salt, 13.5 g of oil and 21 g of honey per level "
     "US tablespoon (14.8 ml)."),
]


def blocks(ctx):
    pick = ("harina", "fuerza", "maicena", "azucar", "moreno", "glas", "mantequilla", "aceite", "leche", "miel", "cacao", "avena")
    rows = "".join(f"<tr><td>{i[2]}</td><td class=\"num\">{i[3]:g} g</td><td class=\"num\">{i[3] / 16:.1f} g</td></tr>" for i in ING if i[0] in pick)
    return [
        ("How the conversion works", f"""
<p>A cup measures volume, and every ingredient packs a different weight into the same volume: a cup of all-purpose flour weighs
<b>125 g</b>, a cup of sugar <b>200 g</b> and a cup of honey <b>339 g</b>. There is no single «cups to grams» factor. This converter
uses the cup weight USDA FoodData Central publishes for each food (US cup of 236.6 ml, spooned and leveled) and scales it through
millilitres to tablespoons, teaspoons, fluid ounces or metric cups.</p>
<p>Example: a chocolate chip cookie recipe calls for 2¼ cups of flour, 1 cup of butter, ¾ cup of packed brown sugar and 2 cups of
chips. That is <b>281 g of flour</b> (2.25 × 125), 227 g of butter, 165 g of brown sugar and 336 g of chocolate chips. Write the gram
amounts on the recipe once and it will come out the same every time.</p>
<table class="tbl"><thead><tr><th>Ingredient</th><th>1 cup</th><th>1 tbsp</th></tr></thead><tbody>{rows}</tbody></table>"""),
        ("Why bakers weigh", """
<p>Measuring dry ingredients by volume has a large error: flour settles in the bag, powdered sugar clumps and cocoa changes a lot
once sifted. A few extra grams of flour are the difference between a moist cake and a dry one. If you have a kitchen scale, weigh;
if not, spoon the flour into the cup without pressing and level it with a knife. Liquids are the exception: water and milk weigh
almost exactly as many grams as their millilitres.</p>"""),
    ]


TOOL = {
    "slug": "cups-to-grams",
    "lang": "en",
    "twin": "tazas-a-gramos",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "scale",
    "order": 60,
    "name": "Cups to grams",
    "k": "cup flour sugar butter tablespoon teaspoon conversion baking weight",
    "title": "Cups to Grams Converter for Baking (USDA weights)",
    "desc": "Convert cups, tablespoons and teaspoons to grams and back for flour, sugar, butter, oil, cocoa and 30 more ingredients, using USDA weights.",
    "h1": "Cups to grams converter",
    "crumb": "Cups to grams",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": data("en"),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("USDA FoodData Central (SR Legacy portion weights)", FDC), ("NIST · Cooking unit conversions", NIST)],
    "credits": [("USDA FoodData Central · SR Legacy (April 2018)", "Public domain (CC0)", FDC_DL)],
    "related": ["recipe-scaler-pan-size", "bakers-percentage-calculator", "oven-temperature-conversion", "sourdough-starter-calculator"],
    "tests": [
        ({}, {"n.g": 125}),
        ({"ing": "mantequilla", "cant": "0.5"}, {"n.g": 113.5}),
        ({"ing": "chocolate", "cant": "2"}, {"n.g": 336}),
        ({"dir": "g", "ing": "azucar", "cant": "50"}, {"n.cups": 0.25}),
    ],
}
