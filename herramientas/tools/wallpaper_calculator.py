"""Wallpaper calculator (English twin of papel-pintado): same compute, US double rolls in feet/inches or Euro rolls."""
from herramientas.tools import _bricolaje as F
from herramientas.tools.papel_pintado import JS, EN233, rolls


def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    P = 44 * 0.3048 - 0.8
    s, per, r, cut = rolls(P, 8 * 0.3048, 20.5 * 0.0254, 33 * 0.3048, trim=4 * 0.0254)
    s2, per2, r2, cut2 = rolls(P, 9 * 0.3048, 20.5 * 0.0254, 33 * 0.3048, 21 * 0.0254, True, 4 * 0.0254)
    se, pe, re_, ce = rolls(13.2, 2.5, 0.53, 10.05)
    return [
        ("How many rolls of wallpaper do I need", f"""
<p>Wallpaper is worked out in <b>drops</b> (full-height strips), not square feet. A 12 × 10 ft room with one door has about
{n(P / 0.3048, 1)} ft of wall to cover. A US double roll is 20.5 in wide and 33 ft long; with 8 ft walls and 4 in left for
trimming, each drop is {n(cut / 0.3048, 2)} ft, so {per} drops come out of each roll. You need {s} drops, which means
<b>{r} double rolls</b>.</p>
<p>Dividing by area gives the wrong answer: those walls are about 330 sq ft and a double roll holds 56 sq ft, which suggests six
rolls. But the last 8 ft of each roll is too short for another full drop. Offcuts do get used above doors and above and below
windows, which is why windows are not subtracted. For a Euro roll (0.53 × 10.05 m) in a 4 × 3 m room with 2.5 m walls you
need {se} drops at {pe} per roll: {re_} rolls.</p>"""),
        ("Pattern repeat and match", f"""
<p>With a pattern, each drop must start at the same point of the design as the one next to it, and that costs paper. The
<b>repeat</b> is printed on the label. With a <b>straight</b> match the motif lines up at the same height across drops, so
each drop is rounded up to a whole number of repeats. With an <b>offset</b> (drop or half-drop) match the motif steps down
half a repeat on every other drop, which wastes on average another half repeat per drop.</p>
<p>In the same room with 9 ft walls, a 21 in repeat with an offset match means cutting drops of {n(cut2 / 0.3048, 2)} ft: only {per2} per roll,
and {r2} double rolls in total. Plain papers and random-match designs are calculated with a repeat of 0.</p>"""),
        ("Roll sizes and batch numbers", """
<p>In Europe the standard roll is set by EN 233: 5.326 m² with a nominal width of 500 to 530 mm, which is the familiar
0.53 × 10.05 m roll. In the US, wallpaper is priced per single roll but sold in double rolls of about 56 sq ft (20.5 in × 33 ft),
and wide 27 in papers also exist. Check the label: some brands use slightly different lengths, so enter your own size with
«Other».</p>
<p>Make sure every roll carries the same <b>batch or lot number</b>, since the shade can change between print runs. A spare roll
costs little compared with not finding the same batch months later for a repair.</p>"""),
    ]


FAQ = [
    ("How many square feet does a roll of wallpaper cover?",
     "A US double roll holds about 56 sq ft, but after trimming and matching expect 45 to 50 sq ft of wall. A Euro roll is 5.3 m², usually covering about 4 m²."),
    ("How many rolls for an accent wall?",
     "For a 12 ft wide, 8 ft high wall with a US double roll: 8 drops, 3 per roll, so 3 double rolls without a large repeat."),
    ("Do I subtract windows and doors?",
     "Subtract doors and floor-to-ceiling openings. Leave windows in: the offcuts are used above and below them."),
    ("What is a half-drop match?",
     "A pattern that steps down half a repeat from one drop to the next. It wastes more paper than a straight match, on average half a repeat per drop."),
    ("How much extra length do I allow per drop?",
     "About 2 in at the top and 2 in at the bottom, 4 in per drop, to trim against uneven ceilings and baseboards."),
]

TOOL = {
    "slug": "wallpaper-calculator",
    "lang": "en",
    "twin": "papel-pintado",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "wallpaper",
    "order": 40,
    "name": "Wallpaper calculator",
    "k": "how many rolls wallpaper double roll pattern repeat drop match accent wall",
    "title": "Wallpaper Calculator: How Many Rolls Do I Need?",
    "desc": "Work out how many rolls of wallpaper a room or accent wall needs, with the pattern repeat and match type, for US double rolls or Euro rolls.",
    "h1": "Wallpaper calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "u", "type": "seg", "label": "Units", "value": "us", "options": [("us", "ft · in"), ("m", "m · cm")]},
        {"id": "modo", "type": "seg", "label": "Measure", "value": "hab", "options": [("hab", "Room"), ("pared", "One wall")]},
        {"id": "l", "type": "number", "label": "Length", "value": "12", "step": "0.01", "show": ("modo", ["hab"])},
        {"id": "a", "type": "number", "label": "Width", "value": "10", "step": "0.01", "show": ("modo", ["hab"])},
        {"id": "pw", "type": "number", "label": "Wall width", "value": "12", "step": "0.01", "show": ("modo", ["pared"])},
        {"id": "h", "type": "number", "label": "Height", "value": "8", "step": "0.01"},
        {"id": "puertas", "type": "number", "label": "Doors", "value": "1", "w": "s", "show": ("modo", ["hab"])},
        {"id": "rollus", "type": "select", "label": "Roll", "value": "dbl", "custom": "otro", "show": ("u", ["us"]),
         "options": [("dbl", "Double roll 20.5 in × 33 ft", {"rwin": "20.5", "rlft": "33"}),
                     ("w27", "Wide 27 in × 27 ft", {"rwin": "27", "rlft": "27"}), ("otro", "Other")]},
        {"id": "rwin", "type": "number", "label": "Roll width", "value": "20.5", "unit": "in", "step": "0.1", "w": "s", "show": ("u", ["us"])},
        {"id": "rlft", "type": "number", "label": "Roll length", "value": "33", "unit": "ft", "step": "0.1", "w": "s", "show": ("u", ["us"])},
        {"id": "rollo", "type": "select", "label": "Roll", "value": "eu", "custom": "otro", "show": ("u", ["m"]),
         "options": [("eu", "Euro roll 0.53 × 10.05 m", {"rw": "53", "rl": "10.05"}), ("70", "0.70 × 10.05 m", {"rw": "70", "rl": "10.05"}),
                     ("106", "1.06 × 10.05 m", {"rw": "106", "rl": "10.05"}), ("otro", "Other")]},
        {"id": "rw", "type": "number", "label": "Roll width", "value": "53", "unit": "cm", "step": "0.1", "w": "s", "show": ("u", ["m"])},
        {"id": "rl", "type": "number", "label": "Roll length", "value": "10.05", "unit": "m", "step": "0.01", "w": "s", "show": ("u", ["m"])},
        {"id": "repin", "type": "number", "label": "Repeat", "value": "0", "unit": "in", "w": "s", "show": ("u", ["us"])},
        {"id": "rep", "type": "number", "label": "Repeat", "value": "0", "unit": "cm", "w": "s", "show": ("u", ["m"])},
        {"id": "casado", "type": "seg", "label": "Match", "value": "rec", "options": [("rec", "Straight"), ("des", "Offset")]},
        {"id": "trimin", "type": "number", "label": "Trim", "value": "4", "unit": "in", "w": "s", "more": True, "show": ("u", ["us"])},
        {"id": "sobra", "type": "number", "label": "Trim", "value": "10", "unit": "cm", "w": "s", "more": True, "show": ("u", ["m"])},
    ],
    "js": F.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("EN 233:2016 · Wallcoverings in roll form, specification (CEN)", EN233)],
    "related": ["paint-calculator", "tile-calculator", "flooring-calculator", "stair-calculator"],
    "tests": [
        ({}, {"n.strips": 25, "n.per": 3, "n.rolls": 9}),
        ({"modo": "pared", "pw": "12"}, {"n.strips": 8, "n.rolls": 3}),
        ({"repin": "21", "casado": "des"}, {"n.per": 3, "n.rolls": 9}),
        ({"h": "9", "repin": "21", "casado": "des"}, {"n.per": 2, "n.rolls": 13}),
        ({"u": "m", "l": "4", "a": "3", "h": "2.5"}, {"n.strips": 25, "n.rolls": 9}),
        ({"rlft": "6"}, {"err": "The roll is shorter than one drop."}),
    ],
}
