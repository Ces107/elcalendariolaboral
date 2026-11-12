"""Roasting time calculator (English twin of tiempo-asado): same compute, pounds or kilos, °F first."""
from herramientas.tools._cocina import CAT
from herramientas.tools.tiempo_asado import FS_CHART, FS_TEMP, FSIS_TURKEY, JS, MEATS, T_EN, inputs

FAQ = [
    ("How long do I cook a turkey per pound?",
     "At 325 °F, an unstuffed 12-14 lb turkey takes 3 to 3¾ hours and a 20-24 lb bird 4½ to 5 hours, according to the USDA chart. "
     "That works out to roughly 13 to 15 minutes per pound, falling as birds get bigger, which is why this calculator follows the "
     "chart instead of one fixed rate. A stuffed bird needs up to half an hour more."),
    ("What temperature should turkey be when done?",
     "165 °F (74 °C) measured in the innermost part of the thigh and wing and the thickest part of the breast. If you stuff the bird, "
     "the center of the stuffing must also reach 165 °F."),
    ("How long does a turkey take to thaw?",
     "In the refrigerator, about 24 hours for every 4 to 5 pounds. A 14 lb turkey needs three to four days, so start the weekend before "
     "Thanksgiving. Never thaw it on the counter."),
    ("What about prime rib, ham and pork loin?",
     "Whole cuts of beef, pork, lamb and veal are safe at 145 °F (63 °C) with a 3-minute rest. A fully cooked ham only needs reheating "
     "to 140 °F (60 °C). Many cooks take prime rib out earlier for rare; 145 °F is the USDA's safe minimum, not a doneness target."),
    ("Does a convection oven change the time?",
     "The USDA charts assume a conventional oven. Convection cooks faster; manufacturers usually suggest lowering the temperature by "
     "about 25 °F or checking earlier. Either way, the thermometer is the real test."),
]


def blocks(ctx):
    return [
        ("How the time is worked out", """
<p>Pick the roast and its weight. The calculator follows the USDA Food Safety and Inspection Service timetables for a conventional
oven. Turkey and chicken use weight brackets: a 14 lb unstuffed turkey sits at the top of the 12-14 lb row, <b>3 to 3¾ hours at
325 °F</b>, so it estimates 3 h 45 min. Beef, pork and lamb use minutes per pound: a 5 lb standing rib roast at 23-25 min/lb takes
<b>1 h 55 to 2 h 05</b>.</p>
<p>Enter the time you want to eat and it tells you when the roast goes in, resting time included, and when to start checking with
a thermometer. For a 16 lb stuffed turkey (4 to 4¼ hours) and dinner at 4:00 pm, it goes in at about 11:33 am; start probing around
3:00 pm.</p>"""),
        ("Safe internal temperatures", """
<p>Time only gets you close: ovens vary and the shape of the roast matters as much as the weight. Safety comes from the temperature
in the center, read with a food thermometer:</p>
<ul>
<li><b>Turkey, chicken and all poultry</b>: 165 °F (74 °C) in the thigh, wing and thickest part of the breast; stuffing 165 °F too.</li>
<li><b>Beef, pork, lamb and veal steaks, chops and roasts</b>: 145 °F (63 °C) plus at least 3 minutes of rest.</li>
<li><b>Ground meat</b>: 160 °F (71 °C). These charts are not for meatloaf or burgers.</li>
<li><b>Fully cooked ham</b> being reheated: 140 °F (60 °C).</li>
</ul>
<p>The USDA suggests letting a turkey stand 20 minutes before removing the stuffing and carving. Ten to fifteen minutes' rest also
keeps beef, pork and lamb juicier when you slice.</p>"""),
        ("Thanksgiving turkey planner", """
<ul>
<li><b>12 lb unstuffed</b>: top of the 8-12 lb row, 2¾ to 3 hours at 325 °F (estimate 3 h). Thaw: 3 days in the fridge.</li>
<li><b>16 lb stuffed</b>: 4 to 4¼ hours (estimate 4 h 08). Thaw: 4 days.</li>
<li><b>22 lb unstuffed</b>: 4½ to 5 hours (estimate 4 h 45). Thaw: 5½ days, so it goes in the fridge on the Friday before.</li>
</ul>"""),
    ]


TOOL = {
    "slug": "roasting-time-calculator",
    "lang": "en",
    "twin": "tiempo-asado",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "meat",
    "order": 50,
    "name": "Roasting time",
    "k": "turkey cooking time per pound thanksgiving prime rib ham lamb thaw thermometer",
    "title": "Turkey and Roast Cooking Time Calculator (USDA)",
    "desc": "How long to roast a turkey, prime rib, ham, pork or lamb by weight, the safe internal temperature, thawing days and what time it goes in the oven.",
    "h1": "Roasting time calculator",
    "crumb": "Roasting time",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN, "m": MEATS},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("USDA FSIS · Let's Talk Turkey: roasting", FSIS_TURKEY), ("FoodSafety.gov · Meat and poultry roasting charts", FS_CHART),
                ("FoodSafety.gov · Safe minimum internal temperatures", FS_TEMP)],
    "related": ["oven-temperature-conversion", "party-food-calculator", "brine-calculator", "recipe-scaler-pan-size"],
    "tests": [
        ({}, {"n.lo": 180, "n.hi": 225, "n.est": 225}),
        ({"carne": "pavor", "peso": "16", "hora": "16:00"}, {"n.est": 248, "n.start": "11:33"}),
        ({"carne": "rib", "peso": "5"}, {"n.lo": 115, "n.hi": 125}),
        ({"carne": "pavo", "peso": "6", "pu": "kg"}, {"n.est": 208}),
    ],
}
