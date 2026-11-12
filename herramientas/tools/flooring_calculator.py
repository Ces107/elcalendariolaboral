"""Flooring calculator (English twin of calculadora-tarima-suelo): same compute, sq ft boxes, 8 ft baseboard, 100 sq ft
underlayment rolls, or metric."""
import math

from herramientas.tools import _bricolaje as F
from herramientas.tools.calculadora_tarima_suelo import JS

NWFA = "https://nwfa.org/technical-guidelines/"


def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    area = 15 * 12
    pk = math.ceil(area * 1.1 / 20 - 1e-9)
    pk15 = math.ceil(area * 1.15 / 20 - 1e-9)
    sk = 2 * (15 + 12) - 2.7
    bars = math.ceil(sk * 1.1 / 8 - 1e-9)
    rolls = math.ceil(area * 1.05 / 100 - 1e-9)
    return [
        ("How much flooring do I need", f"""
<p>Multiply the room's length by its width, add a waste allowance and divide by the coverage of one box, rounding up. A
15 × 12 ft living room is {n(area)} sq ft; with 10% waste you need {n(area * 1.1)} sq ft, which in boxes of 20 sq ft is
<b>{pk} boxes</b>. Laid diagonally or in herringbone, with 15% waste, it is {pk15} boxes. For L-shaped rooms, split the floor
into rectangles and add them, or enter the overall size and leave out the missing corner under More options.</p>
<p>Baseboard follows the perimeter minus door openings: 2 × (15 + 12) − 2.7 = {n(sk, 1)} ft. With 10% for mitred corners that is
{bars} lengths of 8 ft. Underlayment covers the whole floor: with 100 sq ft rolls and 5% for overlaps and trimming, {rolls}
rolls.</p>"""),
        ("Choosing the waste allowance", """
<p>5% is enough for a plain rectangular room laid straight, when the offcut from the end of each row starts the next one. 10% is
the safe figure for most rooms, with closets, hallways or columns. Diagonal, herringbone and chevron layouts need 15% or more,
since every edge piece is cut at an angle and the offcut rarely fits anywhere else. Keep the spare boxes: matching the same
colour and lot years later for a repair is often impossible.</p>
<p>Lay planks parallel to the main source of light or the longest wall, and leave boxes open in the room for a day or two so
the boards acclimatise to its temperature and humidity before installation.</p>"""),
        ("Expansion gaps and baseboard", """
<p>Wood and laminate move with humidity, so floating floors need an expansion gap of roughly 1/4 to 1/2 in (6 to 12 mm)
around walls, pipes and door frames, hidden afterwards by the baseboard or quarter round. Industry guidance such as the NWFA
technical guidelines and every manufacturer's instructions require it, plus transition strips in doorways and on long runs.
That is why baseboard is nailed to the wall, never to the floor.</p>"""),
    ]


FAQ = [
    ("How many square feet are in a box of flooring?",
     "It varies by product: laminate boxes often hold 18 to 25 sq ft, engineered hardwood 20 to 35 sq ft, vinyl plank 20 to 30 sq ft. The label states it."),
    ("How much extra flooring should I buy?",
     "10% for a standard straight layout, 5% for a very simple room, 15% or more for diagonal or herringbone."),
    ("How much baseboard do I need?",
     "The room's perimeter minus door openings, plus 10% for cuts. A 12 × 10 ft room with one door needs about 45 ft: six 8 ft lengths."),
    ("Do I need underlayment under laminate?",
     "Yes for floating floors, unless the planks have it attached. Over concrete add a vapour barrier if the underlayment has none."),
    ("Can I install flooring over tile?",
     "A floating floor can go over flat, well-bonded tile. Check door clearances: the floor rises by about 3/8 to 5/8 in."),
]

TOOL = {
    "slug": "flooring-calculator",
    "lang": "en",
    "twin": "calculadora-tarima-suelo",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "layout-board",
    "order": 25,
    "name": "Flooring calculator",
    "k": "laminate hardwood vinyl plank flooring boxes square feet waste baseboard underlayment",
    "title": "Flooring Calculator: Square Feet, Boxes and Baseboard",
    "desc": "Work out how many boxes of laminate, hardwood or vinyl flooring to buy with waste, plus baseboard lengths and underlayment rolls.",
    "h1": "Flooring calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "u", "type": "seg", "label": "Units", "value": "us", "options": [("us", "ft · sq ft"), ("m", "m · m²")]},
        {"id": "l", "type": "number", "label": "Length", "value": "15", "step": "0.01"},
        {"id": "a", "type": "number", "label": "Width", "value": "12", "step": "0.01"},
        {"id": "pm2", "type": "number", "label": "Area per box", "value": "20", "step": "0.01", "w": "s"},
        {"id": "merma", "type": "seg", "label": "Waste", "value": "10", "options": [("5", "5%"), ("10", "10%"), ("15", "15%")]},
        {"id": "rod", "type": "check", "label": "Baseboard", "value": True},
        {"id": "puertas", "type": "number", "label": "Doors", "value": "1", "w": "s", "show": ("rod", ["1", "True", "true"])},
        {"id": "base", "type": "check", "label": "Underlayment", "value": True},
        {"id": "resta", "type": "number", "label": "Leave out", "value": "0", "step": "0.01", "more": True},
        {"id": "barra", "type": "number", "label": "Baseboard length", "value": "", "placeholder": "8 ft / 2.4 m", "step": "0.01", "w": "s", "more": True},
        {"id": "rollo", "type": "number", "label": "Roll area", "value": "", "placeholder": "100 sq ft / 15 m²", "w": "s", "more": True},
    ],
    "js": F.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("NWFA · Technical guidelines for wood flooring installation", NWFA)],
    "related": ["tile-calculator", "paint-calculator", "wallpaper-calculator", "stair-calculator"],
    "tests": [
        ({}, {"n.area": 180, "n.packs": 10, "n.skirting": 51.3, "n.bars": 8, "n.rolls": 2}),
        ({"merma": "15"}, {"n.packs": 11}),
        ({"u": "m", "l": "5", "a": "4", "pm2": "2.22"}, {"n.packs": 10, "n.skirting": 17.2, "n.bars": 8, "n.rolls": 2}),
        ({"l": "12", "a": "10"}, {"n.bars": 6}),
        ({"a": ""}, {"err": "Enter the length and width of the room."}),
    ],
}
