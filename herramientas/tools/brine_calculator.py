"""Brine calculator (English twin of salmuera): same compute, English strings, US units."""
from herramientas.tools._cocina import CAT
from herramientas.tools.salmuera import JS, NCH_DILL, NCH_KRAUT, T_EN, UC, inputs

FDC = ("USDA FoodData Central · SR Legacy 173468 «Salt, table» (1 tbsp = 18 g, 1 cup = 292 g)", "Public domain (CC0)",
       "https://fdc.nal.usda.gov/download-datasets")
FSIS = "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/poultry/happy-thanksgiving"

FAQ = [
    ("How much salt per gallon for a brine?",
     "It depends on the strength. A 5 % brine is about 7 oz (199 g) of salt per US gallon of water, 7 % about 10 oz, and a 10 % "
     "storage brine for olives about 15 oz (421 g). The University of California's olive guide rounds the strong brine to 1 lb per "
     "gallon (10.7 %)."),
    ("How much salt for sauerkraut?",
     "About 2 to 2.5 % of the cabbage weight: 2 to 2.5 lb of salt per 100 lb, or 20 to 25 g per kilo. The National Center for Home "
     "Food Preservation uses 3 tablespoons of canning salt per 5 lb of shredded cabbage."),
    ("Is the percentage of the water or of the whole brine?",
     "Both conventions exist. Salt ÷ (salt + water) is what a salinity meter reads and what technical guides use; salt ÷ water is "
     "the same as grams per litre. At 10 %, the first gives 111 g per litre and the second 100 g. Switch under «More options»."),
    ("Why weigh salt instead of using cups?",
     "Salt crystals vary wildly in size. A cup of fine table salt weighs about 292 g (USDA), while the same cup of flaky kosher salt "
     "can weigh roughly half that. A recipe written for one brand in cups can end up twice as salty with another."),
    ("What brine strength for a Thanksgiving turkey?",
     "Wet brines for poultry and pork usually run around 5 to 7 % (roughly ¾ to 1 cup of table salt per gallon). Whatever the recipe, "
     "USDA advice is to keep bird and brine at 40 °F (4 °C) or colder the whole time (fridge, or a cooler with ice), never at room "
     "temperature, for no longer than two days, fully submerged, and to discard the brine afterwards."),
    ("Can brined olives cause botulism?",
     "The botulism risk lies in low-acid foods sealed in jars without the right process. Olives fermented in a strong brine and kept "
     "covered are a traditional, well-documented method; what you should not do is water-bath can unfermented or lye-cured olives "
     "(UC says they need pressure canning) or keep garlic or herbs in oil at room temperature."),
]


def blocks(ctx):
    return [
        ("How the salt is worked out", """
<p>Pick what the brine is for, how much water you will use and the strength. Salt is calculated on the total weight, the way food
science guides and salinity meters do it: <b>salt = water × % ÷ (100 − %)</b>. One US gallon (3.79 L) at 10 % takes
<b>421 g (14.8 oz) of salt</b>, which is then exactly 10 % of the finished brine. If your recipe means «grams per litre», switch the
base under «More options».</p>
<p>For sauerkraut, kimchi and other lacto-fermented vegetables, use the equilibrium method: the salt is a percentage of the
vegetables plus any water. 5 lb (2,268 g) of cabbage at 2 % needs 45 g of salt; 800 g of carrots covered with 600 ml of water at
3 % needs 42 g.</p>"""),
        ("Olive brines from the University of California", """
<p>UC's <i>Olives: Safe Methods for Home Pickling</i> (ANR publication 8267) uses three strengths:</p>
<ul>
<li><b>Medium</b>: 8 oz pickling salt per gallon of water, <b>5.7 %</b>, for the first week so the fruit does not shrivel.</li>
<li><b>Strong</b>: 1 lb per gallon, <b>10.7 %</b>, for curing over several months and storing up to a year.</li>
<li>Sicilian-style green olives: 10 oz per gallon (about 7 %) with roughly 2 cups of vinegar per gallon.</li>
</ul>
<p>The guide is explicit that these concentrations should not be lowered during fermentation, and that olives must stay covered
with brine at all times. Spanish-style cracked green olives, debittered in water and then dressed with thyme, fennel and garlic, are
usually kept in a 6 to 10 % brine; the weaker it is, the shorter they keep and the more the fridge matters.</p>"""),
        ("Pickles, kraut and food safety", """
<p>The National Center for Home Food Preservation's fermented dill pickles use ½ cup of canning salt to 8 cups of water and ¼ cup
of vinegar for 4 lb of cucumbers, roughly a 7 % brine. Ferment at 70-75 °F (21-24 °C): it takes 3 to 4 weeks, 5 to 6 at
55-65 °F, and above 80 °F pickles turn soft. Skim any scum or mold several times a week, discard anything soft, slimy or bad-smelling,
and refrigerate the finished jars. Botulism is a low-acid problem: never store garlic, chilies or herbs in oil at room
temperature.</p>"""),
    ]


TOOL = {
    "slug": "brine-calculator",
    "lang": "en",
    "twin": "salmuera",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "salt",
    "order": 30,
    "name": "Brine calculator",
    "k": "salt per gallon olives pickles sauerkraut kimchi turkey brine percentage",
    "title": "Brine Calculator: Salt per Gallon or Litre",
    "desc": "Salt in grams and ounces for any brine strength: olives, fermented pickles, sauerkraut, kimchi or a turkey brine, in litres or US gallons.",
    "h1": "Brine calculator",
    "crumb": "Brine calculator",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("University of California · Olives: Safe Methods for Home Pickling (ANR 8267)", UC),
                ("NCHFP · Dill pickles", NCH_DILL), ("NCHFP · Sauerkraut", NCH_KRAUT), ("USDA FSIS · Thanksgiving food safety (brining)", FSIS)],
    "credits": [FDC],
    "related": ["jam-sugar-calculator", "cups-to-grams", "roasting-time-calculator", "recipe-scaler-pan-size"],
    "tests": [
        ({"agua": "1", "wu": "gal"}, {"n.salt": 420.6}),
        ({"modo": "e", "uso": "ch", "pct": "2", "verd": "5", "vu": "lb"}, {"n.salt": 45.36}),
        ({"agua": "1", "wu": "gal", "pct": "5"}, {"n.salt": 199.23}),
        ({"pct": "40"}, {"err": T_EN["e_sat"]}),
    ],
}
