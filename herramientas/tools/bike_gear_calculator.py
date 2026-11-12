"""Bike gear calculator (English twin of desarrollo-bicicleta): gear inches first, mph alongside km/h."""
import math

from herramientas.tools import _deporte as D
from herramientas.tools.desarrollo_bicicleta import JS, CSS, ETRTO, SHELDON, inputs, rollout


def blocks(ctx):
    c = rollout(25, 622)
    dia = c / math.pi / 25.4
    gi_hi, gi_lo = 50 / 11 * dia, 34 / 30 * dia
    hi, lo = 50 / 11 * c / 1000, 34 / 30 * c / 1000
    mph = lambda d: d * 90 * 0.06 / 1.609344  # noqa: E731
    n = lambda x, d=1: D.n(x, d, True)  # noqa: E731
    return [
        ("Gear inches, development and speed", f"""
<p>Three numbers describe a bike gear. <b>Gear inches</b> = wheel diameter in inches × chainring teeth ÷ cog teeth, a
measure that goes back to the high-wheel bicycles whose front wheel size set the gear. <b>Development</b> (or rollout) is
how far the bike travels per crank turn: gear ratio × wheel circumference. <b>Speed</b> is development × cadence. On a
700×25c wheel (about {c} mm round, {n(dia)} in across) a 50×11 top gear is <b>{n(gi_hi)} gear inches</b>, or {n(hi, 2)} m
per pedal stroke, and at 90 rpm that is {n(mph(hi))} mph. The compact low gear, 34×30, is {n(gi_lo)} inches, {n(lo, 2)} m and
{n(mph(lo))} mph at the same cadence.</p>
<p>The table gives every chainring and cog combination, shaded from easiest to hardest, in gear inches, metres, km/h, mph or
plain ratio. Use it to compare cassettes before you buy, spot big jumps between neighbouring gears or choose chainrings for a
hilly sportive.</p>"""),
        ("Getting the wheel size right", f"""
<p>Choose the wheel by its ETRTO size, moulded on the tyre sidewall: 25-622 means a 25 mm tyre on a rim with a 622 mm bead
seat diameter (700c). The circumference is estimated as π × (622 + 2 × 25) = {c} mm. For a precise figure, roll it out: mark the
tyre and the floor, push the bike one full turn with your weight on it and measure the distance, then type it as
"Circumference". A 29×2.35 mountain-bike tyre comes out at about {rollout(60, 622)} mm; with a 32-tooth ring and a 51-tooth cog
that is a tiny {n(32 / 51 * rollout(60, 622) / 25.4 / math.pi)} gear inches for steep climbs.</p>"""),
        ("Choosing a range", """
<p>For long climbs, a common rule is to be able to keep 70 to 80 rpm in your lowest gear: climbing at 6 mph that means about
25 to 30 gear inches, which is why compact chainsets with 32 or 34-tooth cogs have become standard on endurance road bikes.
On the flat most amateur riders cruise at 18 to 22 mph in gears of 80 to 95 inches. Steps of more than about 15% between
neighbouring cogs feel like a gap when you shift; tight cassettes such as 11-28 give smooth steps but less range.</p>"""),
    ]


FAQ = [
    ("How many gear inches is 50×11?",
     f"About {D.n(50 / 11 * rollout(25, 622) / math.pi / 25.4, 1, True)} gear inches on a 700×25c wheel; slightly more on wider 700c tyres."),
    ("What low gear do I need for climbing?",
     "Low enough to spin 70 to 80 rpm. For steady climbing at 5 to 6 mph that is roughly 22 to 30 gear inches, such as 34×32 or 34×34 on a road bike."),
    ("How do I work out speed from cadence?",
     "Speed (mph) = gear inches × cadence × π × 60 ÷ 63,360. With 90 gear inches at 90 rpm: about 24 mph."),
    ("What is the difference between gear inches and development?",
     "Gear inches use the wheel diameter; development (rollout) uses the circumference, so it equals gear inches × π, usually given in metres."),
    ("How do I measure my wheel circumference?",
     "Mark the tyre and the floor, roll the bike one full turn while sitting on it and measure the gap in millimetres."),
]

TOOL = {
    "slug": "bike-gear-calculator",
    "lang": "en",
    "twin": "desarrollo-bicicleta",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "bike",
    "order": 90,
    "name": "Bike gear calculator",
    "k": "gear inches calculator chainring cassette cog ratio cadence speed mph development rollout cycling",
    "title": "Bike Gear Calculator: Gear Inches, Ratio and Speed",
    "desc": "Bike gear calculator: gear inches, development and speed at your cadence for every chainring and cog. Road, gravel and MTB cassettes.",
    "h1": "Bike gear calculator",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ETRTO · tyre and rim designation (ISO 5775)", ETRTO),
                ("Sheldon Brown · Gear theory for bicyclists (reference)", SHELDON)],
    "credits": [("Approximate circumference π × (BSD + 2 × width), ETRTO / ISO 5775 sizes", "sizing standard (formula)", ETRTO)],
    "related": ["running-pace-calculator", "heart-rate-zone-calculator"],
    "tests": [
        ({}, {"n.max": 9.595, "n.top": 120.249}),
        ({"ver": "mph"}, {"n.top": 32.196}),
        ({"platos": "40", "pinones": "10,12,14,16,18,21,24,28,33,39,45,51"}, {"n.cells": 12, "n.min": 1.656}),
        ({"cad": "200"}, {"err": "Cadence should be between 30 and 150 rpm."}),
    ],
}
