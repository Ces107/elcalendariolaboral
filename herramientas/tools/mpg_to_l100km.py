"""MPG to L/100 km converter (English twin of consumo-l100km-mpg): same compute, US and UK gallons, km/L."""
from herramientas.tools import _coche as K
from herramientas.tools.consumo_l100km_mpg import JS, NIST, UKWM, table


def blocks(ctx):
    return [
        ("The conversion formulas", """
<p>Miles per gallon and litres per 100 km measure the same thing upside down. MPG tells you how far one gallon takes you,
so higher is better; L/100 km tells you how much fuel you burn over a fixed distance, so lower is better. Because one is the
reciprocal of the other, you convert by dividing a constant by the figure you have:</p>
<ul>
<li>L/100 km = 235.215 ÷ US mpg</li>
<li>L/100 km = 282.481 ÷ UK (imperial) mpg</li>
<li>km/L = 100 ÷ L/100 km</li></ul>
<p>The constants come straight from the legal definitions: the international mile is exactly 1.609344 km, the US gallon
3.785411784 litres and the imperial gallon 4.54609 litres. A US car rated at 30 mpg therefore burns 235.215 ÷ 30 =
<b>7.84 L/100 km</b>; a European hatchback quoted at 5 L/100 km returns 47 US mpg, 56.5 UK mpg or 20 km per litre.</p>"""),
        ("US versus UK mpg", f"""
<p>The imperial gallon is about 20% bigger than the US gallon, so the same car shows a higher mpg figure in Britain. A car
that does 40 mpg on a UK forecourt does only 33.3 mpg by American measure, and both equal 7.06 L/100 km. When you compare
reviews, owner forums or window stickers from different countries, check which gallon is meant before you decide one car is
more frugal than another. Canada and Australia moved to L/100 km decades ago, but older manuals and many drivers there still
quote imperial mpg.</p>
<p>Common values, rounded to one decimal:</p>{table(True)}"""),
        ("Why L/100 km is easier to compare", """
<p>MPG is not linear in fuel used. Going from 20 to 25 mpg (US) saves 2.35 litres every 100 km, while going from 40 to
50 mpg saves only 1.18 litres, although on paper it is twice the gain. This is the well-known "mpg illusion":
replacing the thirstiest vehicle in a household usually saves far more fuel than upgrading an already efficient one. If you
want to estimate the cost of a road trip, convert to L/100 km (or gallons per 100 miles), multiply by the distance and then
by the price per litre or gallon.</p>"""),
    ]


FAQ = [
    ("How many L/100 km is 30 mpg?",
     "30 US mpg is 7.84 L/100 km; 30 UK mpg is 9.42 L/100 km."),
    ("How do I convert km/L to mpg?",
     "Multiply km/L by 2.352 for US mpg or by 2.825 for UK mpg. 15 km/L is about 35.3 US mpg or 42.4 UK mpg."),
    ("Is the UK gallon bigger than the US gallon?",
     "Yes. The imperial gallon is 4.54609 litres and the US gallon 3.785411784 litres, so the UK gallon holds about 20% more."),
    ("What is good fuel economy?",
     "For a modern petrol car, under 6 L/100 km (about 40 US mpg or 47 UK mpg) on the highway is good; hybrids often beat "
     "5 L/100 km."),
    ("Does this work for electric cars?",
     "No. EVs are rated in kWh/100 km, miles per kWh or, in the US, MPGe, which counts 33.7 kWh as the energy of one gallon of "
     "gasoline."),
]

INPUTS = [
    {"id": "val", "type": "number", "label": "Economy", "value": "30", "step": "0.01", "w": "s"},
    {"id": "u", "type": "seg", "label": "Unit", "value": "mpgus", "options": [
        ("mpgus", "mpg (US)"), ("mpguk", "mpg (UK)"), ("l100", "L/100 km"), ("kml", "km/L")]},
]

TOOL = {
    "slug": "mpg-to-l100km",
    "lang": "en",
    "twin": "consumo-l100km-mpg",
    "cat": K.CAT_EN[0], "cat_name": K.CAT_EN[1],
    "icon": "gas-station",
    "order": 10,
    "name": "MPG converter",
    "k": "mpg to l/100km litres per 100 km km per litre us uk imperial gallon fuel economy",
    "title": "MPG to L/100 km Converter (US and UK Gallons)",
    "desc": "Convert fuel economy between US mpg, UK imperial mpg, litres per 100 km and km per litre, with the exact formulas and a quick table.",
    "h1": "MPG to L/100 km converter",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": K.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("NIST SP 811, Appendix B.9 · conversion factors (gallon, mile)", NIST),
                ("Weights and Measures Act 1985, Schedule 1 · imperial gallon = 4.54609 L (legislation.gov.uk)", UKWM)],
    "credits": [],
    "related": ["average-speed-calculator", "tire-size-calculator"],
    "tests": [
        ({}, {"n.l100": 7.8405, "n.mpguk": 36.0285}),
        ({"val": "30", "u": "mpguk"}, {"n.l100": 9.416}),
        ({"val": "15", "u": "kml"}, {"n.mpgus": 35.2822, "n.mpguk": 42.3721}),
        ({"val": "5", "u": "l100"}, {"n.kml": 20, "n.mpgus": 47.0429}),
        ({"val": ""}, {"err": "Enter a fuel economy figure above zero."}),
    ],
}
