"""Paint calculator (English twin of calculadora-pintura): same compute, feet/gallons or metres/litres."""
from herramientas.tools import _bricolaje as F
from herramientas.tools.calculadora_pintura import JS, ECOLABEL_EN



def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    walls = 2 * (12 + 10) * 8
    area = walls - 20 - 15
    gal = area * 2 / 350 * 1.1
    m_area = 2 * (4 + 3) * 2.5 - 1.6 - 1.5
    m_l = m_area * 2 / 10 * 1.1
    return [
        ("How much paint for a room", f"""
<p>Take the wall area, multiply by the number of coats and divide by the coverage printed on the can. A 12 × 10 ft bedroom
with 8 ft ceilings has {n(walls)} sq ft of wall; take away one door (about 20 sq ft) and one window (about 15 sq ft) and
{n(area)} sq ft are left. At 350 sq ft per gallon and two coats that is {n(area * 2 / 350, 2)} gallons, or
<b>{n(gal, 2)} gallons</b> with a 10% spare: buy two one-gallon cans.</p>
<p>In metric the same logic applies. A 4 × 3 m room with 2.5 m walls, a door and a window gives {n(m_area, 1)} m²; two coats of
a 10 m²/L emulsion need {n(m_l, 1)} litres including the spare, so a 5 L and a 2.5 L tin, or a single 10 L tub if you will
also do touch-ups later. Switch the units button at the top to change between feet and gallons and metres and litres.</p>"""),
        ("Coverage: the can versus the wall", """
<p>Coverage (also called spreading rate) is the area one gallon or one litre covers in a single coat. Typical interior latex
or emulsion paint states 350 to 400 sq ft per gallon, or 10 to 14 m² per litre. For context, the EU Ecolabel requires white
and light indoor paints to reach at least 8 m² per litre while hiding 98% of the surface beneath, so treat much higher claims
as ideal laboratory conditions.</p>
<p>Real walls take more. Fresh plaster and bare drywall soak up the first coat (the "New plaster" option adds 15%), and
textured finishes such as knockdown, popcorn or pebble-dash have more surface than a tape measure shows (+30%). Covering a dark
colour with a light one usually needs a primer plus two coats, or three coats of a one-coat paint, whatever the label says.</p>"""),
        ("What the calculator counts", """
<p>Walls are the room's perimeter times its height. Each door subtracts 20 sq ft (1.6 m²) and each window 15 sq ft (1.5 m²):
typical sizes, so use the "Area" mode with your own measurement for patio doors or picture windows. The ceiling is length times
width. Sockets, switches and vents are not subtracted; the spare covers them, plus what stays in the roller and the tray.</p>
<p>The can suggestion picks the cheapest mix, assuming paint gets cheaper per gallon or litre in bigger containers: 5-gallon
buckets, gallons and quarts in US mode; 10, 5, 2.5 and 1 litre tins in metric. Buy tinted paint from a single batch, because two
mixes of the same colour can look different side by side on one wall.</p>"""),
    ]


FAQ = [
    ("How many square feet does a gallon of paint cover?",
     "About 350 to 400 sq ft in one coat on a smooth, primed wall. On new drywall, bare plaster or texture expect 250 to 300 sq ft."),
    ("How many coats of paint do I need?",
     "Two for almost every job. One coat is enough only when you repaint the same colour on a sound wall; a big colour change or "
     "fresh plaster needs a primer first."),
    ("Do I subtract doors and windows?",
     "Yes, for the large openings. The calculator takes 20 sq ft (1.6 m²) per door and 15 sq ft (1.5 m²) per window. Small items "
     "such as outlets are left in."),
    ("How much paint for a ceiling?",
     "Its area is the room's length times its width. A 12 × 10 ft ceiling is 120 sq ft: about two-thirds of a gallon for two coats."),
    ("How much spare paint should I buy?",
     "Around 10% for brush and roller work, 20 to 30% if you spray, because part of the paint is lost as overspray."),
]

INPUTS = [
    {"id": "u", "type": "seg", "label": "Units", "value": "us", "options": [("us", "ft · gal"), ("m", "m · L")]},
    {"id": "modo", "type": "seg", "label": "Measure", "value": "hab", "options": [("hab", "Room"), ("m2", "Area")]},
    {"id": "l", "type": "number", "label": "Length", "value": "12", "step": "0.01", "show": ("modo", ["hab"])},
    {"id": "a", "type": "number", "label": "Width", "value": "10", "step": "0.01", "show": ("modo", ["hab"])},
    {"id": "h", "type": "number", "label": "Height", "value": "8", "step": "0.01", "show": ("modo", ["hab"])},
    {"id": "puertas", "type": "number", "label": "Doors", "value": "1", "w": "s", "show": ("modo", ["hab"])},
    {"id": "ventanas", "type": "number", "label": "Windows", "value": "1", "w": "s", "show": ("modo", ["hab"])},
    {"id": "techo", "type": "check", "label": "Ceiling", "value": False, "show": ("modo", ["hab"])},
    {"id": "m2", "type": "number", "label": "Area", "value": "300", "step": "0.1", "show": ("modo", ["m2"])},
    {"id": "capas", "type": "seg", "label": "Coats", "value": "2", "options": [("1", "1"), ("2", "2"), ("3", "3")]},
    {"id": "covus", "type": "number", "label": "Coverage", "value": "350", "unit": "sq ft/gal", "show": ("u", ["us"])},
    {"id": "rend", "type": "number", "label": "Coverage", "value": "10", "unit": "m²/L", "step": "0.1", "show": ("u", ["m"])},
    {"id": "sup", "type": "select", "label": "Surface", "value": "1", "more": True,
     "options": [("1", "Smooth or painted"), ("1.15", "New plaster (+15%)"), ("1.3", "Textured (+30%)")]},
    {"id": "margen", "type": "number", "label": "Spare", "value": "10", "unit": "%", "w": "s", "more": True},
]

TOOL = {
    "slug": "paint-calculator",
    "lang": "en",
    "twin": "calculadora-pintura",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "paint",
    "order": 10,
    "name": "Paint calculator",
    "k": "how much paint gallons litres room walls ceiling coats coverage",
    "title": "Paint Calculator: How Much Paint Do I Need?",
    "desc": "Work out how many gallons or litres of paint a room needs from its size, doors, windows, coats and the coverage on the can.",
    "h1": "Paint calculator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": F.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Commission Decision 2014/312/EU · EU Ecolabel for paints, spreading-rate criterion (EUR-Lex)", ECOLABEL_EN)],
    "related": ["wallpaper-calculator", "tile-calculator", "flooring-calculator", "concrete-calculator"],
    "tests": [
        ({}, {"n.area": 317, "n.litres": 1.993, "n.buy": 2}),
        ({"techo": True}, {"n.area": 437, "n.buy": 2.75}),
        ({"u": "m", "l": "4", "a": "3", "h": "2.5"}, {"n.area": 31.9, "n.litres": 7.018, "n.buy": 7.5}),
        ({"modo": "m2", "m2": "", "u": "m"}, {"err": "Enter the area to paint."}),
        ({"covus": "0"}, {"err": "Enter the coverage per coat."}),
    ],
}
