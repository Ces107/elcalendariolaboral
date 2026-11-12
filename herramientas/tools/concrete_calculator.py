"""Concrete calculator (English twin of hormigon-mortero): same compute, feet/inches/yd3 with premix bags, or metric."""
import math

from herramientas.tools import _bricolaje as F
from herramientas.tools.hormigon_mortero import JS, DATA, mix

QUIKRETE = "https://www.quikrete.com/PDFs/DATA_SHEET-Concrete%20Mix%201101.pdf"
CTE_SEAE = "https://www.codigotecnico.org/pdf/Documentos/SE/DBSE-AE.pdf"


def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    ft3 = 10 * 10 * 4 / 12
    yd3 = ft3 / 27
    w = ft3 * 1.05
    cem, sand, grav, water = mix(w * 0.0283168, "1:2:4", "hor", 0)
    hole = math.pi * (10 * 0.0254) ** 2 / 4 * (24 * 0.0254) / 0.0283168
    return [
        ("How much concrete do I need", f"""
<p>Multiply length × width × thickness, in the same unit, then add a little spare. A 10 × 10 ft patio slab 4 in thick is
10 × 10 × 0.333 = {n(ft3, 1)} cubic feet, or {n(yd3, 2)} cubic yards. With 5% spare that is {n(w, 1)} ft³: about
<b>{math.ceil(w / 0.6)} bags of 80 lb premix</b> (each yields about 0.60 ft³), {math.ceil(w / 0.45)} bags of 60 lb or
{math.ceil(w / 0.3)} bags of 40 lb. Above roughly one cubic yard, ordering ready-mix from a plant is usually cheaper and much
less work than mixing 50+ bags by hand.</p>
<p>If you mix from scratch, the same slab at a 1:2:4 mix (one part cement, two sand, four gravel by volume) takes about
{n(cem * 2.20462, 0)} lb of Portland cement, {math.ceil(cem * 2.20462 / 94)} bags of 94 lb, plus {n(sand / 0.0283168, 1)} ft³
of sand and {n(grav / 0.0283168, 1)} ft³ of gravel.</p>"""),
        ("How the mix quantities are worked out", """
<p>Loose sand fills the gaps in the gravel and cement fills the gaps in the sand, so a cubic yard of mixed concrete needs far
more than a cubic yard of dry ingredients. The calculator uses the classic volume-batching rule: 1.54 volumes of dry material per
volume of wet concrete, and 1.33 for mortar. That dry volume is split by the ratio, so in 1:2:4 cement is 1/7, sand 2/7 and gravel
4/7. Volumes become weights with loose bulk densities of 1,440 kg/m³ (90 lb/ft³) for cement and 1,600 kg/m³ (100 lb/ft³) for
sand and gravel, values inside the ranges published in building codes for bulk materials.</p>
<p>Water is shown as a guide: a water-to-cement ratio of 0.5 for concrete and 0.7 for mortar. Wet sand already carries water, so
add it gradually until the mix is plastic and holds its shape. Extra water makes concrete easier to place but weaker and more
prone to cracking.</p>"""),
        ("Post holes, mortar and structural work", f"""
<p>For fence posts choose «Holes»: a 10 in diameter hole 24 in deep holds {n(hole, 2)} ft³, so one 80 lb bag per post plus a
little. Mortar (1:3 to 1:6 cement to sand) is for laying brick and block, rendering and bedding pavers; it has no gravel.</p>
<p>Site-mixed concrete is fine for patios, shed bases, paths and posts. Footings, foundations, retaining walls and anything
structural must follow the strength set by your local building code or engineer, typically delivered as ready-mix with a
specified strength.</p>"""),
    ]


FAQ = [
    ("How many 80 lb bags of concrete make a cubic yard?",
     "About 45. A cubic yard is 27 ft³ and each 80 lb bag yields roughly 0.60 ft³; with a little spare, buy 47 or 48."),
    ("How many bags of concrete for a fence post?",
     "Usually one to two 80 lb bags per post: a 10 in hole 24 in deep holds 1.1 ft³, a 12 in hole 36 in deep holds 2.4 ft³."),
    ("How thick should a concrete slab be?",
     "4 in for patios, paths and shed bases; 5 to 6 in for driveways that carry cars, on a compacted gravel base."),
    ("What is a 1:2:4 concrete mix?",
     "One part cement, two parts sand and four parts gravel by volume: a general-purpose mix for slabs and bases. 1:2:3 is richer and stronger; 1:3:6 is for blinding and fill."),
    ("How much water per bag of cement?",
     "About 5.6 US gallons per 94 lb bag of Portland cement at a 0.5 water-cement ratio, less if the sand is wet."),
]

TOOL = {
    "slug": "concrete-calculator",
    "lang": "en",
    "twin": "hormigon-mortero",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "bucket",
    "order": 30,
    "name": "Concrete calculator",
    "k": "concrete bags slab cubic yards post holes mortar cement sand gravel mix 80 lb",
    "title": "Concrete Calculator: Bags, Cubic Yards and Mix",
    "desc": "Work out the concrete for a slab or post holes in cubic yards or m³, how many 80, 60 or 40 lb bags, or the cement, sand and gravel.",
    "h1": "Concrete calculator",
    "updated": "2026-11-12",
    "data": DATA,
    "inputs": [
        {"id": "u", "type": "seg", "label": "Units", "value": "us", "options": [("us", "ft · in"), ("m", "m · cm")]},
        {"id": "obj", "type": "seg", "label": "Material", "value": "hor", "options": [("hor", "Concrete"), ("mor", "Mortar")]},
        {"id": "forma", "type": "seg", "label": "Shape", "value": "losa", "options": [("losa", "Slab"), ("hoyo", "Holes"), ("vol", "Volume")]},
        {"id": "l", "type": "number", "label": "Length", "value": "10", "step": "0.01", "show": ("forma", ["losa"])},
        {"id": "a", "type": "number", "label": "Width", "value": "10", "step": "0.01", "show": ("forma", ["losa"])},
        {"id": "e", "type": "number", "label": "Thickness", "value": "4", "step": "0.5", "show": ("forma", ["losa"])},
        {"id": "d", "type": "number", "label": "Diameter", "value": "10", "show": ("forma", ["hoyo"])},
        {"id": "p", "type": "number", "label": "Depth", "value": "24", "show": ("forma", ["hoyo"])},
        {"id": "nh", "type": "number", "label": "Holes", "value": "4", "w": "s", "show": ("forma", ["hoyo"])},
        {"id": "vol", "type": "number", "label": "Volume", "value": "1", "unit": "yd³ or m³", "step": "0.01", "show": ("forma", ["vol"])},
        {"id": "mh", "type": "select", "label": "Mix", "value": "1:2:4", "show": ("obj", ["hor"]),
         "options": [("1:2:3", "1:2:3 · strong"), ("1:2:4", "1:2:4 · slabs"), ("1:3:6", "1:3:6 · fill")]},
        {"id": "mm", "type": "select", "label": "Mix", "value": "1:4", "show": ("obj", ["mor"]),
         "options": [("1:3", "1:3 · render"), ("1:4", "1:4 · brick"), ("1:5", "1:5 · block"), ("1:6", "1:6 · fill")]},
        {"id": "sacus", "type": "seg", "label": "Cement bag", "value": "94", "options": [("94", "94 lb"), ("47", "47 lb")], "more": True, "show": ("u", ["us"])},
        {"id": "saco", "type": "seg", "label": "Cement bag", "value": "25", "options": [("25", "25 kg"), ("50", "50 kg")], "more": True, "show": ("u", ["m"])},
        {"id": "merma", "type": "number", "label": "Spare", "value": "5", "unit": "%", "w": "s", "more": True},
    ],
    "js": F.make(JS, True),
    "intro": "Feet and inches (slab thickness, hole size in inches), or metres and centimetres.",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Quikrete Concrete Mix No. 1101 data sheet (bag yields)", QUIKRETE),
                ("Spanish Building Code CTE, DB SE-AE, table C.6 (bulk densities of materials)", CTE_SEAE)],
    "related": ["gravel-calculator", "tile-calculator", "stair-calculator", "paint-calculator"],
    "tests": [
        ({}, {"n.vol": 0.9911, "n.cem": 314.0, "n.bags": 8}),
        ({"forma": "vol", "vol": "1", "merma": "0"}, {"n.vol": 0.7646}),
        ({"u": "m", "l": "3", "a": "2", "e": "10"}, {"n.vol": 0.63, "n.cem": 199.6, "n.bags": 8}),
        ({"forma": "hoyo", "d": "10", "p": "24", "nh": "1", "merma": "0"}, {"n.vol": 0.0309}),
        ({"l": "-2"}, {"err": "Enter length, width and thickness."}),
    ],
}
