"""Running pace calculator (English twin of ritmo-carrera): same compute, English texts, mile defaults for pace input."""
from herramientas.tools import _deporte as D
from herramientas.tools.ritmo_carrera import JS, CSS

MI = 1.609344

INPUTS = [
    {"id": "modo", "type": "seg", "label": "Find", "value": "tiempo",
     "options": [("tiempo", "Pace"), ("ritmo", "Finish time"), ("vel", "From speed")]},
    {"id": "dist", "type": "select", "label": "Distance", "value": "10",
     "options": [("5", "5K"), ("10", "10K"), ("21.0975", "Half marathon"), ("42.195", "Marathon"), ("otra", "Other")]},
    {"id": "km", "type": "number", "label": "Distance", "value": "10", "step": "0.001", "w": "s", "show": ("dist", ["otra"])},
    {"id": "du", "type": "seg", "label": "Unit", "value": "mi", "options": [("km", "km"), ("mi", "miles")], "show": ("dist", ["otra"])},
    {"id": "tiempo", "type": "text", "label": "Time", "value": "50:00", "placeholder": "h:mm:ss", "w": "s", "show": ("modo", ["tiempo"])},
    {"id": "ritmo", "type": "text", "label": "Pace", "value": "8:00", "placeholder": "m:ss", "w": "s", "show": ("modo", ["ritmo"])},
    {"id": "ru", "type": "seg", "label": "Per", "value": "mi", "options": [("km", "km"), ("mi", "mile")], "show": ("modo", ["ritmo"])},
    {"id": "vel", "type": "number", "label": "Speed", "value": "7.5", "unit": "mph", "step": "0.1", "w": "s", "show": ("modo", ["vel"])},
    {"id": "vu", "type": "seg", "label": "Unit", "value": "mph", "options": [("kmh", "km/h"), ("mph", "mph")], "show": ("modo", ["vel"])},
    {"id": "parc", "type": "select", "label": "Splits", "value": "auto", "more": True,
     "options": [("auto", "Automatic"), ("1", "Every km"), ("5", "Every 5 km"), ("mi", "Every mile"), ("0", "No splits")]},
]


def blocks(ctx):
    return [
        ("How pace is worked out", """
<p>Pace is the time one kilometre or one mile takes you: <b>pace = time ÷ distance</b>. Run a 10K in 50 minutes and your
pace is 50 ÷ 10 = <b>5:00 per km</b>, which is <b>8:03 per mile</b> (multiply by 1.609) and 12 km/h, or 7.46 mph, on a
treadmill. Type times as h:mm:ss (1:45:00) or mm:ss (50:00); a bare number counts as minutes.</p>
<p>It works the other way round too. Choose "Finish time", enter the pace you plan to hold and you get the finishing time
plus a split for every kilometre or mile, ready to copy onto a pace band. "From speed" turns a treadmill reading in mph or
km/h into a road pace.</p>"""),
        ("Worked examples", f"""
<p>A sub-4-hour marathon needs {D.t(4 * 3600 / 42.195 * MI)} per mile ({D.t(4 * 3600 / 42.195)} per km) on average, and a
sub-3:30 needs {D.t(3.5 * 3600 / 42.195 * MI)} per mile. A 2-hour half marathon is run at exactly the same pace as a 4-hour
marathon, since it is half the distance. Eight-minute miles take you round a 5K in {D.t(480 / MI * 5)}, a 10K in
{D.t(480 / MI * 10)}, a half in {D.t(480 / MI * 21.0975)} and a full marathon in {D.t(480 / MI * 42.195)}, although few runners
can hold their 10K pace for 26.2 miles: for a realistic marathon estimate use the race time predictor.</p>
<p>Treadmill shortcuts: 6 mph is a 10:00 mile, 7.5 mph an 8:00 mile and 10 mph a 6:00 mile. The "Same pace over" table
lists what your pace gives over the four classic road distances.</p>"""),
        ("Official distances and rounding", """
<p>The half marathon is 21.0975 km (13.1 miles) and the marathon 42.195 km (26.2 miles), the distances World Athletics
sets for certified road races; an international mile is exactly 1,609.344 metres. Your GPS watch will usually read long,
because nobody runs the measured racing line perfectly: allow 0.2 to 0.4 km extra over a marathon and aim a few seconds per
mile faster than the theoretical pace. Paces are rounded to the second and speeds to two decimals.</p>"""),
    ]


FAQ = [
    ("What pace do I need for a sub-25 5K?",
     f"Exactly 25:00 is {D.t(1500 / 5 * MI)} per mile or 5:00 per km, so run a second or two faster: about 8:02 per mile."),
    ("What is a 4-hour marathon pace?",
     f"{D.t(4 * 3600 / 42.195 * MI)} per mile, or {D.t(4 * 3600 / 42.195)} per km. Because GPS distance runs long, many runners aim for 9:00 per mile."),
    ("How do I convert mph to minutes per mile?",
     "Divide 60 by the speed: 60 ÷ 7.5 mph = 8 minutes per mile. Choose \"From speed\" for decimals and the matching km pace."),
    ("How do I convert pace per mile to pace per km?",
     "Divide by 1.609: an 8:00 mile is 4:58 per km. Choose \"Finish time\", type the pace and keep \"Per\" on mile."),
    ("What are splits?",
     "Your elapsed time at set points of the race, such as every mile. Checking them tells you whether you are ahead of or behind your target."),
]

TOOL = {
    "slug": "running-pace-calculator",
    "lang": "en",
    "twin": "ritmo-carrera",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "run",
    "order": 40,
    "name": "Pace calculator",
    "k": "running pace per mile per km mph splits marathon half 10k 5k finish time",
    "title": "Running Pace Calculator: Per Mile, Per Km and Splits",
    "desc": "Work out your running pace per mile or per km from time and distance, or your finish time at a given pace, with splits and a 5K-to-marathon table.",
    "h1": "Running pace calculator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("World Athletics · Competition and Technical Rules (road distances)", "https://worldathletics.org/about-iaaf/documents/book-of-rules"),
                ("NIST · international mile = 1,609.344 m", "https://www.nist.gov/pml/us-surveyfoot/revised-unit-conversion-factors")],
    "related": ["race-time-predictor", "heart-rate-zone-calculator", "swim-pace-calculator"],
    "tests": [
        ({}, {"n.pace": 300, "n.kmh": 12}),
        ({"modo": "ritmo", "dist": "42.195"}, {"n.time": 12585, "big": "3:29:45"}),
        ({"modo": "vel"}, {"n.pace": 298.258}),
        ({"dist": "otra", "km": "", "du": "mi"}, {"err": "Enter the distance."}),
    ],
}
