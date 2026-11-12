"""Gravel, soil and mulch calculator (English twin of calculadora-cesped-grava): same compute, yd3, tons and US bags."""
import math

from herramientas.tools import _bricolaje as F
from herramientas.tools.calculadora_cesped_grava import JS, CTE_SEAE

MATS = [("grava", "Gravel", 1600), ("gravilla", "Pea gravel", 1500), ("arena", "Sand", 1600), ("canto", "River rock", 1600),
        ("zahorra", "Crushed stone base", 1900), ("tierra", "Topsoil", 1300), ("sustrato", "Compost or garden soil", 600),
        ("corteza", "Bark mulch", 300)]


def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    ft3 = 20 * 10 * 3 / 12 * 1.05
    yd3 = ft3 / 27
    lb = ft3 * 0.0283168 * 1600 * 2.20462
    mulch = 20 * 10 * 3 / 12 * 1.05
    return [
        ("How much gravel do I need", f"""
<p>Multiply length × width × depth in feet to get cubic feet, divide by 27 for cubic yards, then multiply by the weight of the
material. A 20 × 10 ft path with 3 in of gravel is 50 ft³; with 5% spare, {n(ft3, 1)} ft³ or <b>{n(yd3, 2)} cubic yards</b>,
about {n(lb / 2000, 2)} tons. In 50 lb bags that is {math.ceil(lb / 50)} bags, so for anything beyond a small bed, bulk delivery by the
yard or ton is far cheaper.</p>
<p>Typical depths: 2 to 3 in of pea gravel or decorative stone over landscape fabric, 3 to 4 in for paths you walk on, 4 to
6 in of compacted crushed stone as a base for a patio or a shed, 2 to 3 in of mulch on flower beds and 4 to 6 in of topsoil for
a new lawn. For the same 20 × 10 ft bed, 3 in of bark mulch is {n(mulch, 1)} ft³, about {math.ceil(mulch / 2)} bags of 2 ft³.</p>"""),
        ("Weights and densities", """
<p>Aggregates are sold by weight or by the yard, so the loose bulk density matters. Gravel and sand run at about 100 lb per
cubic foot (1,600 kg/m³), roughly 1.35 short tons per cubic yard; building codes give ranges of 1,400 to 1,900 kg/m³ for sand
and 1,500 to 2,000 kg/m³ for sand and gravel. Topsoil is lighter when dry, around 80 lb/ft³, and much heavier wet. Mulch and
compost are light and sold by volume, which is why the calculator switches to bags of 2 ft³ (or 50 L) for them. If your
supplier quotes another weight per yard, type it in.</p>
<p>Crushed stone base compacts: plate-compacting removes 15 to 20% of the loose volume, so add that under «Spare» for a
compacted base.</p>"""),
        ("Lawn: seed or sod", """
<p>Seeding rates depend on the grass: about 3 to 4 lb per 1,000 sq ft for Kentucky bluegrass, 6 to 8 lb for tall fescue and
perennial ryegrass mixes. The calculator uses 7 lb per 1,000 sq ft (about 35 g/m²), a common figure for a sun-and-shade mix;
change it under More options to the rate on your seed bag. Sod is sold by the square foot or by the pallet (around 450 to
500 sq ft); order 5% extra for edges and lay it the day it arrives on prepared, watered soil.</p>"""),
    ]


FAQ = [
    ("How many tons of gravel are in a cubic yard?",
     "About 1.35 short tons (2,700 lb) of loose gravel, between 1.25 and 1.7 depending on stone size and moisture."),
    ("How many bags of gravel make a yard?",
     "About 54 bags of 50 lb, or 54 bags of 0.5 ft³. A cubic yard is 27 ft³."),
    ("How deep should gravel be for a driveway?",
     "4 to 6 in of compacted crushed stone base plus 2 to 3 in of surface gravel, for 6 to 9 in in total."),
    ("How much mulch do I need?",
     "A 2 to 3 in layer: 100 sq ft at 3 in is 25 ft³, about 0.93 cubic yards or 13 bags of 2 ft³."),
    ("How much topsoil for a new lawn?",
     "4 to 6 in. For 1,000 sq ft at 4 in, about 12.3 cubic yards."),
]

TOOL = {
    "slug": "gravel-calculator",
    "lang": "en",
    "twin": "calculadora-cesped-grava",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "shovel",
    "order": 35,
    "name": "Gravel and mulch calculator",
    "k": "gravel calculator cubic yards tons bags mulch topsoil sand crushed stone grass seed sod",
    "title": "Gravel Calculator: Cubic Yards, Tons and Bags",
    "desc": "Work out how many cubic yards, tons or bags of gravel, sand, topsoil or mulch you need for an area and depth, plus grass seed or sod.",
    "h1": "Gravel, soil and mulch calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "u", "type": "seg", "label": "Units", "value": "us", "options": [("us", "ft · in"), ("m", "m · cm")]},
        {"id": "uso", "type": "seg", "label": "Calculate", "value": "ari", "options": [("ari", "Gravel or soil"), ("ces", "Lawn")]},
        {"id": "l", "type": "number", "label": "Length", "value": "20", "step": "0.01"},
        {"id": "a", "type": "number", "label": "Width", "value": "10", "step": "0.01"},
        {"id": "mat", "type": "select", "label": "Material", "value": "grava", "custom": "otro", "show": ("uso", ["ari"]),
         "options": [(k, name, {"dens": str(d), "densus": str(round(d / 16.0185))}) for k, name, d in MATS] + [("otro", "Other")]},
        {"id": "e", "type": "number", "label": "Depth", "value": "3", "step": "0.5", "w": "s", "show": ("uso", ["ari"])},
        {"id": "densus", "type": "number", "label": "Density", "value": "100", "unit": "lb/ft³", "w": "s", "show": ("u", ["us"])},
        {"id": "dens", "type": "number", "label": "Density", "value": "1600", "unit": "kg/m³", "w": "s", "show": ("u", ["m"])},
        {"id": "ces", "type": "seg", "label": "Lawn", "value": "sem", "options": [("sem", "Seed"), ("tepe", "Sod")], "show": ("uso", ["ces"])},
        {"id": "dosus", "type": "number", "label": "Seed rate", "value": "7", "unit": "lb/1,000 sq ft", "w": "s", "more": True, "show": ("u", ["us"])},
        {"id": "dosis", "type": "number", "label": "Seed rate", "value": "35", "unit": "g/m²", "w": "s", "more": True, "show": ("u", ["m"])},
        {"id": "merma", "type": "number", "label": "Spare", "value": "5", "unit": "%", "w": "s", "more": True},
        {"id": "resta", "type": "number", "label": "Leave out", "value": "0", "step": "0.01", "more": True},
        {"id": "sacous", "type": "number", "label": "Bag", "value": "50", "unit": "lb", "w": "s", "more": True, "show": ("u", ["us"])},
        {"id": "bolus", "type": "number", "label": "Light bag", "value": "2", "unit": "ft³", "w": "s", "more": True, "show": ("u", ["us"])},
        {"id": "saco", "type": "number", "label": "Bag", "value": "25", "unit": "kg", "w": "s", "more": True, "show": ("u", ["m"])},
        {"id": "bol", "type": "number", "label": "Light bag", "value": "50", "unit": "L", "w": "s", "more": True, "show": ("u", ["m"])},
    ],
    "js": F.make(JS, True),
    "intro": "Length and width in feet (or metres), depth in inches (or centimetres).",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Spanish Building Code CTE, DB SE-AE, table C.6 (bulk densities of sand and gravel)", CTE_SEAE)],
    "related": ["concrete-calculator", "flooring-calculator", "tile-calculator", "paint-calculator"],
    "tests": [
        ({}, {"n.vol": 1.4866, "n.bags": 105}),
        ({"mat": "corteza", "densus": "19"}, {"n.bags": 27}),
        ({"u": "m", "l": "4", "a": "3", "e": "5"}, {"n.vol": 0.63, "n.kg": 1008, "n.bags": 41}),
        ({"uso": "ces", "l": "100", "a": "10"}, {"n.kg": 3.334}),
        ({"e": "0"}, {"err": "Enter the depth."}),
    ],
}
