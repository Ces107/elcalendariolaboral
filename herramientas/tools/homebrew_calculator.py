"""Homebrew calculator (English twin of cerveza-casera): ABV, IBU (Tinseth) and SRM (Morey), metric or US units."""
from herramientas.tools._cocina import CAT
from herramientas.tools.cerveza_casera import BJCP, CREDITS_EN, CSS, HOPS, JS, MOREY, T_EN, TINSETH, inputs

FAQ = [
    ("How do I calculate ABV from my hydrometer readings?",
     "Subtract final gravity from original gravity and multiply by 131.25. OG 1.050 and FG 1.010: 0.040 × 131.25 = 5.25 % ABV. "
     "Above about 1.070 the high-gravity formula is more accurate and usually reads a few tenths higher."),
    ("What is a good IBU for my style?",
     "Light lagers sit around 8-18 IBU, pale ales 30-45, American IPAs 40-70 and imperial stouts 50-90. The BJCP style guidelines "
     "list the range for every style, along with original gravity and color."),
    ("Why does my software give different IBUs?",
     "There are several models (Tinseth, Rager, Garetz) and each program tweaks things like pellet versus whole hops or whirlpool "
     "time. Tinseth is the most common for homebrew; treat the number as an estimate rather than a lab measurement."),
    ("Can I enter gravity as 1050 or 50?",
     "Yes. 1.050, 1050 and 50 (gravity points) all mean the same here. If your refractometer reads Brix or Plato, pick Plato under "
     "«More options»; Brix and Plato are close enough for wort. After fermentation a refractometer needs an alcohol correction, so use "
     "a hydrometer for FG."),
    ("What is the difference between SRM, Lovibond and EBC?",
     "SRM and EBC both describe beer color, EBC ≈ SRM × 1.97. Lovibond (°L) is how US maltsters rate grain; European malt is sold in "
     "EBC. Pick the unit your malt bag uses under «More options»."),
]


def blocks(ctx):
    return [
        ("ABV from gravity readings", """
<p>A hydrometer tells you how much sugar is dissolved in the wort before fermentation (original gravity, OG) and after it (final
gravity, FG). The drop is sugar the yeast turned into alcohol and CO₂. The everyday formula is <b>ABV = (OG − FG) × 131.25</b>:
a beer from 1.050 down to 1.010 is <b>5.25 %</b>. The high-gravity version, <b>76.08 × (OG − FG) ÷ (1.775 − OG) × FG ÷ 0.794</b>,
gives 5.34 % for the same beer and pulls away on big beers: a barleywine-ish 1.080 to 1.015 is 8.53 % with the simple formula and
9.10 % with the other. Apparent attenuation (80 % in the first example) shows how much of the sugar was eaten; most ale strains
land between 70 and 80 %.</p>"""),
        ("IBU with the Tinseth formula", """
<p>Glenn Tinseth fitted his model to measured beers: hop utilization is a gravity factor, <b>1.65 × 0.000125^(OG − 1)</b>, times
a time factor, <b>(1 − e^(−0.04 × minutes)) ÷ 4.15</b>. IBU is that utilization times the milligrams of alpha acid per litre.
In a 5 US gallon batch at 1.060, 1 oz of a 12 % hop for 60 minutes plus 1 oz of a 6 % hop for 5 minutes comes to about
<b>42 IBU</b>, a classic American pale ale. The same hops in a 1.080 wort give noticeably less, because sugar-heavy wort isomerises
alpha acids less efficiently. Use the volume at the end of the boil; flameout, whirlpool and dry hops count as zero here.</p>"""),
        ("Color with the Morey equation", """
<p>Each grain has a color in degrees Lovibond (or EBC). Malt color units are pounds × °L ÷ gallons, and Dan Morey's fit to real
beers turns them into SRM: <b>SRM = 1.4922 × MCU^0.6859</b>. Ten pounds of 2 °L pale malt plus one pound of 60 °L crystal in
5 gallons gives an MCU of 16 and about <b>10 SRM</b>, a light amber. EBC malt colors are converted with °L = (EBC + 1.2) ÷ 2.65.
The swatch is only a guide: screens and glass thickness change how a beer looks.</p>"""),
    ]


TOOL = {
    "slug": "homebrew-calculator",
    "lang": "en",
    "twin": "cerveza-casera",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "beer",
    "order": 40,
    "name": "Homebrew calculator",
    "k": "abv og fg ibu tinseth srm ebc morey beer gravity hops color",
    "title": "Homebrew Calculator: ABV, IBU (Tinseth) and SRM",
    "desc": "Free homebrew calculator: alcohol by volume from OG and FG, bitterness in IBU with Tinseth, beer color in SRM and EBC with Morey. Metric or US units.",
    "h1": "Homebrew calculator",
    "crumb": "Homebrew calculator",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "css": CSS,
    "data": {"en": True, "t": T_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Glenn Tinseth · Hop utilization", TINSETH), ("BeerSmith · Hop utilization models compared", HOPS),
                ("BeerSmith · SRM, Lovibond and EBC (Morey equation)", MOREY), ("BJCP · 2021 Style Guidelines", BJCP)],
    "credits": CREDITS_EN,
    "related": ["coffee-ratio-calculator", "jam-sugar-calculator", "brine-calculator", "party-food-calculator"],
    "tests": [
        ({}, {"n.abv": 5.25, "n.att": 80}),
        ({"calc": "ibu", "og": "1060", "vol": "5", "vu": "gal", "hu": "oz", "h1g": "1", "h1a": "12", "h1t": "60", "h2g": "1", "h2a": "6", "h2t": "5"},
         {"n.ibu": 41.67}),
        ({"calc": "srm", "vol": "5", "vu": "gal", "gu": "lb", "cu": "l", "m1k": "10", "m1c": "2", "m2k": "1", "m2c": "60"}, {"n.mcu": 16, "n.srm": 9.99}),
        ({"og": "12.5", "esc": "p", "fg": "2.5"}, {"n.abv": 5.35}),
    ],
}
