"""Hiking time calculator (English twin of tiempo-ruta-montana): Naismith first, imperial units by default."""
from herramientas.tools import _deporte as D
from herramientas.tools.tiempo_ruta_montana import JS, MIDE_URL, MIDE_PDF, NAISMITH_URL, _fh

INPUTS = [
    {"id": "met", "type": "seg", "label": "Method", "value": "nai", "options": [("nai", "Naismith"), ("mide", "MIDE")]},
    {"id": "u", "type": "seg", "label": "Units", "value": "imp", "options": [("imp", "mi · ft"), ("met", "km · m")]},
    {"id": "dist", "type": "number", "label": "Distance", "value": "8", "step": "0.1", "w": "s"},
    {"id": "sube", "type": "number", "label": "Ascent", "value": "2500", "w": "s"},
    {"id": "baja", "type": "number", "label": "Descent", "value": "2500", "w": "s"},
    {"id": "lang", "type": "select", "label": "Descent", "value": "no", "show": ("met", ["nai"]),
     "options": [("no", "No correction"), ("suave", "Gentle (5-12°) · −10 min/1,000 ft"), ("fuerte", "Steep (>12°) · +10 min/1,000 ft")]},
    {"id": "piso", "type": "select", "label": "Trail", "value": "4", "show": ("met", ["mide"]),
     "options": [("5", "Road or track · 5 km/h"), ("4", "Good path · 4 km/h"), ("3", "Rough path, scree · 3 km/h")]},
    {"id": "salida", "type": "time", "label": "Start", "value": "", "w": "s"},
    {"id": "paradas", "type": "number", "label": "Breaks", "value": "", "unit": "min", "w": "s", "more": True},
]

MI, FT = 1.609344, 0.3048


def blocks(ctx):
    km, up = 8 * MI, 2500 * FT
    nai = km / 5 + up / 600
    steep = nai + up / 300 * 10 / 60
    th, tv = km / 4, up / 400 + up / 600
    mide = max(th, tv) + min(th, tv) / 2
    return [
        ("Naismith's rule", f"""
<p>In 1892 the Scottish climber William W. Naismith set out the rule hillwalkers still learn: <b>allow one hour for every
3 miles (5 km) of distance, plus one hour for every 2,000 feet (600 m) of ascent</b>. The calculator works in metric
internally (5 km/h and 600 m per hour), which differs from the feet version by under 2%. An 8-mile loop with 2,500 ft of
climbing comes out at <b>{_fh(nai)}</b> of walking.</p>
<p>Naismith ignores descent, and long, steep descents are where most people slow down. Eric Langmuir, author of the
British mountain-leader handbook, added two corrections: on gentle descents (5 to 12 degrees) take off 10 minutes for every
300 m (about 1,000 ft) of descent; on steep ones (over 12 degrees) add 10 minutes per 300 m. Choose the steep option for
the same loop and the estimate grows to {_fh(steep)}.</p>"""),
        ("The MIDE method used in Spain", f"""
<p>Spanish trail boards and guidebooks use <b>MIDE</b>, the excursion information method of the Spanish mountain sports
federation. It is more conservative. Horizontal time runs at 5 km/h on roads and tracks, 4 km/h on good paths and 3 km/h on
rough ground; vertical time at <b>400 m per hour up and 600 m per hour down</b>. You take <b>the longer of the two and add
half of the shorter</b>. On a good path the same 8-mile, 2,500 ft loop gives {_fh(mide)}, which suits an average walker with
a daypack better than the original Naismith figure. MIDE also grades effort from 1 (up to an hour) to 5 (over ten hours).</p>"""),
        ("From walking time to a plan for the day", """
<p>Both rules give moving time only. Add the breaks you expect (lunch, photos, water) under "More options" and type a start
time to see when you should be back, then check that leaves a margin before sunset, especially in winter. Children, heavy
packs, snow, heat or poor visibility all slow you down well beyond any formula, so treat the result as a minimum.</p>"""),
    ]


FAQ = [
    ("How long does it take to hike 1,000 feet of elevation?",
     "Naismith allows 30 minutes per 1,000 ft of ascent on top of the distance time. MIDE allows about 45 minutes per 1,000 ft (400 m per hour)."),
    ("What is an average hiking speed?",
     "Around 3 mph (5 km/h) on easy flat ground and 2 to 2.5 mph on mountain paths, slowing further with every 1,000 ft of climbing."),
    ("Does Naismith's rule include breaks?",
     "No, it is moving time. Add breaks separately with \"Breaks\" under \"More options\"; a common allowance is 10 minutes per hour."),
    ("Which method should I use?",
     "Naismith suits fit hillwalkers on good paths. MIDE is more realistic for mixed groups and counts the descent."),
    ("What is total ascent?",
     "The sum of every climb on the route (elevation gain), not just the height difference between the start and the summit."),
]

TOOL = {
    "slug": "hiking-time-calculator",
    "lang": "en",
    "twin": "tiempo-ruta-montana",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "mountain",
    "order": 70,
    "name": "Hiking time calculator",
    "k": "naismith rule hiking time elevation gain ascent descent langmuir walking time trail",
    "title": "Hiking Time Calculator: Naismith's Rule with Elevation",
    "desc": "Estimate how long a hike takes from distance and elevation gain with Naismith's rule, Langmuir's descent corrections or MIDE, plus your return time.",
    "h1": "Hiking time calculator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": D.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Naismith's rule and Langmuir corrections (Wikipedia)", NAISMITH_URL),
                ("MIDE · Método de Información de Excursiones (FEDME, Montaña Segura)", MIDE_URL),
                ("MIDE manual: time criteria (Spanish)", MIDE_PDF)],
    "credits": [("Naismith's rule (W. W. Naismith, 1892) and Eric Langmuir's corrections", "public domain (method)", NAISMITH_URL),
                ("MIDE time criteria (FEDME, FAM, Prames)", "published method (reimplemented)", MIDE_URL)],
    "related": ["camino-de-santiago-planner", "running-pace-calculator"],
    "tests": [
        ({}, {"n.hours": 3.845, "big": "3 h 51 min"}),
        ({"lang": "fuerte"}, {"n.hours": 4.2683}),
        ({"u": "met", "dist": "12", "sube": "800", "baja": "800", "met": "mide"}, {"n.hours": 4.8333}),
        ({"salida": "09:15", "paradas": "60"}, {"n.arr": "14:06"}),
        ({"sube": ""}, {"err": "Enter the total ascent (0 if none)."}),
    ],
}
