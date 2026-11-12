"""Heart rate zone calculator (English twin of zonas-frecuencia-cardiaca): same compute, English texts."""
from herramientas.tools import _deporte as D
from herramientas.tools.zonas_frecuencia_cardiaca import JS, CSS, KARVONEN, TANAKA, GULATI

INPUTS = [
    {"id": "edad", "type": "number", "label": "Age", "value": "35", "unit": "years", "w": "s"},
    {"id": "fcrep", "type": "number", "label": "Resting HR", "value": "60", "unit": "bpm", "w": "s", "show": ("met", ["kv"])},
    {"id": "met", "type": "seg", "label": "Method", "value": "kv", "options": [("kv", "Karvonen"), ("pm", "% of max")]},
    {"id": "fcmax", "type": "number", "label": "Measured max HR", "value": "", "unit": "bpm", "w": "s", "more": True},
    {"id": "form", "type": "select", "label": "Max HR formula", "value": "tanaka", "more": True,
     "options": [("tanaka", "Tanaka: 208 − 0.7 × age"), ("fox", "Classic: 220 − age"), ("gulati", "Gulati (women): 206 − 0.88 × age")]},
]


def blocks(ctx):
    mx = 208 - 0.7 * 35
    k = lambda p: round(60 + (mx - 60) * p / 100)  # noqa: E731
    m = lambda p: round(mx * p / 100)  # noqa: E731
    return [
        ("How your zones are worked out", f"""
<p>Heart rate zones come from two numbers: your <b>maximum heart rate</b> and, for the Karvonen method, your <b>resting
heart rate</b>. Karvonen works on the heart-rate <i>reserve</i>, max minus resting: <b>target HR = resting + (max −
resting) × intensity</b>. Two people with the same max but different fitness get different zones, which is why it is more
accurate than taking a straight percentage of max.</p>
<p>Example: at 35 the Tanaka formula estimates a max of 208 − 0.7 × 35 = {D.n(mx, 1, True)} bpm. With a resting rate of 60 bpm
the reserve is {D.n(mx - 60, 1, True)}, so zone 2 (60-70%) runs from <b>{k(60)} to {k(70)} bpm</b>. With the plain
percentage-of-max method the same zone would be {m(60)}-{m(70)} bpm, noticeably lower. That gap is why it pays to measure
your resting pulse (lying down, just after waking, over a full minute, on several mornings) and use Karvonen.</p>"""),
        ("Which max heart rate formula", """
<p>The familiar <b>220 − age</b> spread through fitness books in the 1970s without a proper study behind it; it tends to
overestimate max heart rate in young people and underestimate it in older ones. <b>Tanaka</b> and colleagues re-examined it
in 2001 using 351 studies covering about 19,000 people and proposed 208 − 0.7 × age, now the usual default. For women,
<b>Gulati</b>'s 2010 study of more than 5,400 women found 206 − 0.88 × age. All of them are averages, and an individual's real
maximum can sit 10 bpm either side. If you have measured yours in a lab test or an all-out effort with a chest strap, enter it
as "Measured max HR" and it replaces the formula.</p>"""),
        ("What each zone is for", """
<p><b>Zone 1</b> (50-60%) is for warming up and recovery. <b>Zone 2</b> (60-70%) is the aerobic base where you can still
talk in full sentences, and where most plans put the bulk of weekly volume. <b>Zone 3</b> (70-80%) is a steady, comfortably
hard effort close to marathon pace. <b>Zone 4</b> (80-90%) sits around threshold, with heavy breathing: 3 to 10 minute
intervals or 10K pace. <b>Zone 5</b> (90-100%) can only be held for a few minutes. If you take blood-pressure or heart
medication (beta blockers lower heart rate) or have a heart condition, ask your doctor for your zones: these formulas do not
apply.</p>"""),
    ]


FAQ = [
    ("What is my max heart rate for my age?",
     "With Tanaka's formula, 208 − 0.7 × age: 187 bpm at 30, 180 at 40, 173 at 50 and 166 at 60. It is an average with about ±10 bpm of spread."),
    ("What heart rate is zone 2?",
     "60-70% of your heart-rate reserve (or of max). For a 35-year-old with a resting rate of 60, that is about 134-146 bpm with Karvonen."),
    ("Karvonen or percentage of max?",
     "Karvonen if you know your resting heart rate, because it accounts for fitness. Percentage of max is simpler but gives lower zones."),
    ("How do I measure resting heart rate?",
     "In the morning before getting up, count your pulse for a full minute (or read your watch) on several days and take the average."),
    ("Why does my watch show different zones?",
     "Each brand uses its own formula and percentages. What matters is sticking to one system with a realistic maximum."),
]

TOOL = {
    "slug": "heart-rate-zone-calculator",
    "lang": "en",
    "twin": "zonas-frecuencia-cardiaca",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "heart-rate-monitor",
    "order": 60,
    "name": "Heart rate zones",
    "k": "heart rate zones karvonen max hr reserve zone 2 training bpm tanaka calculator",
    "title": "Heart Rate Zone Calculator (Karvonen Method)",
    "desc": "Find your five heart rate training zones with the Karvonen method or % of max HR. Max heart rate from age (Tanaka, 220 − age, Gulati) or measured.",
    "h1": "Heart rate zone calculator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Karvonen MJ, Kentala E, Mustala O (1957). The effects of training on heart rate. Ann Med Exp Biol Fenn 35: 307-315", KARVONEN),
                ("Tanaka H, Monahan KD, Seals DR (2001). Age-predicted maximal heart rate revisited. J Am Coll Cardiol 37: 153-156", TANAKA),
                ("Gulati M et al. (2010). Heart rate response to exercise stress testing in asymptomatic women. Circulation 122: 130-137", GULATI)],
    "credits": [("Karvonen method (1957)", "published formula (reimplemented)", KARVONEN),
                ("Tanaka formula (2001)", "published formula (reimplemented)", TANAKA)],
    "related": ["running-pace-calculator", "race-time-predictor", "swim-pace-calculator"],
    "tests": [
        ({}, {"n.max": 183.5, "n.z2": [134, 146]}),
        ({"form": "gulati", "edad": "50", "met": "pm"}, {"n.max": 162}),
        ({"fcmax": "250"}, {"err": "Max heart rate should be between 100 and 230 bpm."}),
        ({"fcrep": "110", "edad": "90"}, {"err": "Resting heart rate must be well below your max."}),
    ],
}
