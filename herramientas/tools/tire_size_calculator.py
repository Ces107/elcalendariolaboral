"""Tire size calculator (English twin of cambio-neumaticos-tamano): same compute, inches and revs per mile."""
from herramientas.tools import _coche as K
from herramientas.tools.cambio_neumaticos_tamano import JS, R39


def blocks(ctx):
    return [
        ("Reading a tire size", """
<p>A metric size such as <b>245/70R17</b> gives the section width in millimetres (245), the aspect ratio, which is the
sidewall height as a percentage of the width (70%), the radial construction (R) and the wheel diameter in inches (17). The
overall diameter is <b>rim × 25.4 + 2 × width × aspect ÷ 100</b> in millimetres: 17 × 25.4 = 431.8 mm of wheel plus two
171.5 mm sidewalls, 774.8 mm or 30.50 inches in total. The calculator does this for both sizes and compares diameter,
sidewall, width, circumference and revolutions per mile.</p>
<p>Example: a popular pickup upgrade from 245/70R17 to 265/70R17 adds 20 mm of width and grows the tire to 802.8 mm
(31.61 in), <b>3.61% taller</b>. Revolutions per mile drop from 661 to 638, so the odometer under-counts, and when the
speedometer reads 60 mph you are really doing 62.2 mph. Going from 205/55R16 to 225/45R17 for a bigger wheel, on the other
hand, changes the diameter by only 0.38%.</p>"""),
        ("Speedometer error and the 3% rule of thumb", f"""
<p>Speedometers are built to read high, never low. Under <a href="{R39}" rel="noopener">UN Regulation No. 39</a>, used for
type approval in Europe and many other markets, the indicated speed must lie between the true speed and the true speed plus
10% plus 4 km/h. US federal rules set no comparable accuracy band, but most manufacturers there also calibrate slightly high. Taller tires eat into that
margin, so after a big upsize the speedometer can show less than your real speed, which is no defence at a speed check.
Smaller tires do the opposite.</p>
<p>Tire shops commonly keep a replacement within about 3% of the original diameter, so that speedometer, ABS, traction
control and transmission shift points keep working as designed and the tire clears the suspension at full lock. That is a
guideline, not a legal limit: your vehicle's placard and owner's manual list the approved sizes, and the load index and speed
rating of the new tires should never be lower than those of the originals. Lifted trucks with oversized tires are usually
recalibrated with a programmer or a new speedometer gear.</p>"""),
    ]


FAQ = [
    ("What does 225/45R17 mean?",
     "225 mm section width, sidewall 45% of the width (101.25 mm), radial construction and a 17-inch wheel. Its overall diameter "
     "is 634.3 mm, or 24.97 inches."),
    ("How much does a bigger tire change my speedometer?",
     "By the same percentage as the diameter. A tire 3% taller means that at an indicated 60 mph you are doing about 61.8 mph."),
    ("Can I put wider tires on the same wheels?",
     "Often one size wider fits if the wheel width is within the range the tire maker lists for that size. Check clearance and "
     "your vehicle's approved sizes first."),
    ("What is a P-metric or LT tire size?",
     "P225/65R17 is a passenger tire and LT245/75R16 a light-truck tire; the numbers mean the same. The calculator ignores the "
     "prefix, but load ratings differ between them."),
    ("How do I convert a tire size to inches?",
     "Overall diameter in inches = rim + 2 × width × aspect ÷ 100 ÷ 25.4. For 265/70R17: 17 + 2 × 185.5 ÷ 25.4 = 31.61 inches."),
]

INPUTS = [
    {"id": "a1", "type": "number", "label": "Current width", "value": "245", "unit": "mm", "w": "s"},
    {"id": "p1", "type": "number", "label": "Current aspect", "value": "70", "unit": "%", "w": "s"},
    {"id": "r1", "type": "number", "label": "Current rim", "value": "17", "unit": "in", "w": "s"},
    {"id": "a2", "type": "number", "label": "New width", "value": "265", "unit": "mm", "w": "s"},
    {"id": "p2", "type": "number", "label": "New aspect", "value": "70", "unit": "%", "w": "s"},
    {"id": "r2", "type": "number", "label": "New rim", "value": "17", "unit": "in", "w": "s"},
    {"id": "vm", "type": "number", "label": "Speedometer", "value": "60", "unit": "mph", "w": "s", "more": True},
]

TOOL = {
    "slug": "tire-size-calculator",
    "lang": "en",
    "twin": "cambio-neumaticos-tamano",
    "cat": K.CAT_EN[0], "cat_name": K.CAT_EN[1],
    "icon": "wheel",
    "order": 30,
    "name": "Tire size calculator",
    "k": "tyre size comparison diameter speedometer error revs per mile plus size wheel upgrade",
    "title": "Tire Size Calculator: Compare Diameter and Speedometer",
    "desc": "Compare two tire sizes: overall diameter in mm and inches, sidewall, revs per mile and speedometer error, with a check against the 3% guideline.",
    "h1": "Tire size calculator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": K.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("UN Regulation No. 39 · speedometer approval (EUR-Lex)", R39)],
    "credits": [],
    "related": ["average-speed-calculator", "mpg-to-l100km"],
    "tests": [
        ({}, {"n.d1": 774.8, "n.d2": 802.8, "n.diff": 3.6138, "n.real": 62.17, "n.ok": False}),
        ({"a1": "205", "p1": "55", "r1": "16", "a2": "225", "p2": "45", "r2": "17"}, {"n.diff": 0.3798, "n.ok": True}),
        ({"a2": "245", "p2": "75", "r2": "16"}, {"n.d2": 773.9}),
        ({"p2": "10"}, {"err": "Aspect ratio in %, for example 55."}),
    ],
}
