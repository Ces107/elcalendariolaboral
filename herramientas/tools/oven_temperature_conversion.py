"""Oven temperature conversion (English twin of temperatura-horno): °F, °C, gas mark, fan and convection."""
from herramientas.tools._cocina import CAT
from herramientas.tools.temperatura_horno import JS, NIST, NIST_T, T_EN, gas_table, inputs

FAQ = [
    ("What is 350 °F in Celsius?",
     "176.7 °C, usually written as 180 °C in European recipes (or 160 °C fan). It is gas mark 4 in UK recipes."),
    ("How do I convert Celsius to Fahrenheit?",
     "Multiply by 9/5 and add 32. 200 °C × 9 ÷ 5 = 360; + 32 = 392 °F, which recipes round to 400 °F. Going the other way, subtract 32 "
     "and multiply by 5/9."),
    ("How much lower for a fan or convection oven?",
     "UK and European recipes reduce by 20 °C for a fan oven (180 °C conventional becomes 160 °C fan). US guidance for convection is "
     "25 °F lower (350 °F becomes 325 °F). If the recipe already says «fan», do not reduce it again."),
    ("What does gas mark 4 mean?",
     "Gas marks are the dial numbers of British gas cookers. Gas 4 is 350 °F (about 180 °C). Each mark adds 25 °F, from gas 1 at 275 °F "
     "to gas 9 at 475 °F; below 1 come ½ (250 °F) and ¼ (225 °F)."),
    ("What is a moderate or hot oven?",
     "Old recipe terms: slow or cool is about 300-325 °F (150-160 °C), moderate 350 °F (180 °C), moderately hot 375-400 °F, hot "
     "400-425 °F (200-220 °C) and very hot 450 °F (230 °C) and above."),
]


def blocks(ctx):
    return [
        ("How the conversion works", f"""
<p>Enter the recipe temperature and its scale. Fahrenheit to Celsius: <b>°C = (°F − 32) × 5 ÷ 9</b>; Celsius to Fahrenheit:
<b>°F = °C × 9 ÷ 5 + 32</b>. So 350 °F is 176.7 °C and 220 °C is 428 °F. Recipes never use exact figures: oven dials move in steps of
10 or 25 degrees and a 5-degree difference does not change a cake, which is why recipes round 177 °C to 180 °C and 392 °F to 400 °F.
The calculator shows the exact value and the dial value.</p>
<p>A British recipe that says «gas mark 6» means 400 °F, about 200 °C conventional or 180 °C fan. The full table:</p>
{gas_table("en")}"""),
        ("Fan, convection and conventional ovens", """
<p>A fan circulates hot air, so food browns and cooks faster and the temperature comes down. UK and European oven makers advise
<b>20 °C lower</b> than a conventional (top and bottom heat) setting; American convection guidance is <b>25 °F lower</b>, almost the
same thing (about 14 °C). A recipe that already says «180 °C fan» is adjusted: in an oven without a fan that is 200 °C. Choose
«Fan / convection» under «Recipe oven» and the calculator works it back to the conventional equivalent.</p>
<p>Ovens also drift from their dial, sometimes by 20 °F or more. An inexpensive oven thermometer tells you how far yours is off,
which matters more than any conversion table.</p>"""),
    ]


TOOL = {
    "slug": "oven-temperature-conversion",
    "lang": "en",
    "twin": "temperatura-horno",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "temperature",
    "order": 70,
    "name": "Oven temperature",
    "k": "fahrenheit celsius gas mark fan convection oven conversion chart",
    "title": "Oven Temperature Conversion: °F, °C, Gas Mark, Fan",
    "desc": "Convert oven temperatures between Fahrenheit, Celsius and gas mark, and adjust for fan or convection ovens. Full conversion chart included.",
    "h1": "Oven temperature conversion",
    "crumb": "Oven temperature",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("NIST · SI units: temperature", NIST_T), ("NIST · Unit conversion", NIST)],
    "related": ["roasting-time-calculator", "cups-to-grams", "bakers-percentage-calculator", "recipe-scaler-pan-size"],
    "tests": [
        ({}, {"n.c": 176.67, "n.gas": "4"}),
        ({"t": "200", "u": "c"}, {"n.f": 392, "n.fan": 180}),
        ({"t": "160", "u": "c", "modo": "v"}, {"n.c": 180, "n.gas": "4"}),
        ({"t": "", "u": "c"}, {"err": T_EN["e_t"]}),
    ],
}
