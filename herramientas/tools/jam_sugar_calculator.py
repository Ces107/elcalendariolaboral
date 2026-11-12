"""Jam sugar calculator (English twin of azucar-mermelada): same compute and USDA fruit sugars, English strings."""
from herramientas.tools._cocina import CAT
from herramientas.tools.azucar_mermelada import FDC_DL, JS, NCHFP, NCHFP_T, T_EN, data, inputs

EU = "https://eur-lex.europa.eu/eli/dir/2024/1438/oj"

FAQ = [
    ("How much sugar per pound of fruit for jam?",
     "The old rule is 1:1, a pound of sugar per pound of fruit. Most modern recipes use 0.6 to 0.75 lb per lb, and very sweet fruit "
     "(figs, mango) or added pectin lets you go down to half. Below that you need pectin made for low-sugar jam and the fridge for "
     "storage."),
    ("How much jam will I get from my fruit?",
     "With 1 kg (2.2 lb) of strawberries and 750 g of sugar, about 1,330 g of jam cooked to 60 % sugar, or five 250 ml (half-pint) jars. "
     "Less sugar means less jam, because more water has to be cooked off before it sets."),
    ("How do I know when jam is set?",
     "The National Center for Home Food Preservation gives three tests: a temperature of 220 °F (8 °F above the boiling point of water) "
     "at sea level, the spoon test (two drops run together and «sheet» off a cool metal spoon), or a little jam on a plate in the freezer "
     "for a few minutes that gels."),
    ("How long do I process jam jars in a water bath?",
     "NCHFP: fill hot jars leaving ¼ inch headspace and process 5 minutes in a boiling-water canner if the jars were sterilized, 10 minutes "
     "if not, adding a minute per 1,000 ft of altitude to the 5-minute time. Reduced-sugar spreads are best refrigerated or frozen."),
    ("What makes a jam legally «jam» in Europe?",
     "Under the EU breakfast directive, as amended by Directive (EU) 2024/1438, jam needs at least 450 g of fruit per kilo of product "
     "(500 g for «extra jam») from 14 June 2026, and EU countries such as Spain keep a 60 % soluble-solids minimum, except for "
     "reduced-sugar products."),
]


def blocks(ctx):
    return [
        ("How the numbers are worked out", """
<p>Sugar is a percentage of the prepared fruit weight (pitted, peeled, stems off): 1 kg of strawberries at 75 % takes
<b>750 g of sugar</b>. To estimate the yield, the calculator adds the sugar you put in to the sugar already in the fruit (4.9 g per
100 g of strawberries in USDA FoodData Central) and finds the weight at which that sugar is 60 % of the jam: (750 + 49) ÷ 0.60 =
<b>1,332 g of jam</b>. Getting there means boiling off 1,750 − 1,332 = 418 g of water, almost a quarter of what is in the pot.</p>
<p>A 1:1 jam barely needs reducing and sets fast; with less sugar you cook longer, and below about 50 % you usually need pectin (or
pectin-rich fruit such as apple or quince) to set without cooking the fruit to paste. Lemon juice is not only for flavour: acidity
helps pectin gel. Fruit sugar values are averages; very ripe fruit is sweeter.</p>"""),
        ("Shelf life and sugar", """
<p>Sugar is part of what preserves jam: at around 60 % it ties up enough water to keep well once opened. Lower-sugar spreads are
fine, they just belong in the fridge after opening. The calculator also reports fruit per kilo of finished jam: 1 kg of fruit with
750 g of sugar cooked to 60 % gives 751 g of fruit per kg, comfortably above the 450 g European minimum for jam. Fill hot, sterilized
jars, process them as NCHFP describes, and keep opened jars refrigerated.</p>"""),
    ]


TOOL = {
    "slug": "jam-sugar-calculator",
    "lang": "en",
    "twin": "azucar-mermelada",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "cherry",
    "order": 100,
    "name": "Jam sugar",
    "k": "jam sugar ratio fruit yield jars preserves strawberry fig low sugar",
    "title": "Jam Sugar Calculator: Sugar, Yield and Jars",
    "desc": "Work out how much sugar your jam needs for the fruit you have, how much jam you will get, how much water to cook off and how many jars to prepare.",
    "h1": "Jam sugar calculator",
    "crumb": "Jam sugar",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": data("en"),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("NCHFP · Canning jams and jellies", NCHFP), ("NCHFP · Testing jelly without added pectin", NCHFP_T),
                ("EUR-Lex · Directive (EU) 2024/1438", EU)],
    "credits": [("USDA FoodData Central · SR Legacy, total sugars of fruit", "Public domain (CC0)", FDC_DL)],
    "related": ["brine-calculator", "recipe-scaler-pan-size", "cups-to-grams", "party-food-calculator"],
    "tests": [
        ({}, {"n.sugar": 750, "n.yield": 1331.5, "n.jars": 5}),
        ({"fruta": "mango", "azp": "50", "punto": "55"}, {"n.yield": 1157.45}),
        ({"azp": "300"}, {"err": T_EN["e_azp"]}),
    ],
}
