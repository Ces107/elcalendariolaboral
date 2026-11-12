"""Race time predictor (English twin of prediccion-maraton): Riegel's formula, English texts."""
from herramientas.tools import _deporte as D
from herramientas.tools.prediccion_maraton import JS, CSS, RIEGEL_URL, _pred

MI = 1.609344

INPUTS = [
    {"id": "dist", "type": "select", "label": "Recent race", "value": "10",
     "options": [("5", "5K"), ("10", "10K"), ("16.09344", "10 miles"), ("21.0975", "Half marathon"), ("42.195", "Marathon"), ("otra", "Other")]},
    {"id": "km", "type": "number", "label": "Distance", "value": "15", "unit": "km", "step": "0.001", "w": "s", "show": ("dist", ["otra"])},
    {"id": "tiempo", "type": "text", "label": "Your time", "value": "50:00", "placeholder": "h:mm:ss", "w": "s"},
    {"id": "exp", "type": "number", "label": "Exponent", "value": "1.06", "step": "0.01", "w": "s", "more": True},
]


def blocks(ctx):
    m10 = _pred(3000, 10, 42.195)
    h10 = _pred(3000, 10, 21.0975)
    m_h = _pred(6300, 21.0975, 42.195)
    m_h8 = _pred(6300, 21.0975, 42.195, 1.08)
    return [
        ("Riegel's formula", f"""
<p>In 1977 the American engineer and runner Peter Riegel published a simple rule for predicting a race time from another
race: <b>T2 = T1 × (D2 ÷ D1)<sup>1.06</sup></b>. The 1.06 exponent captures the fact that doubling the distance more than
doubles the time, because your pace drops. Riegel fitted it to the world records of the day and set out the full analysis in
<i>American Scientist</i> in 1981. Most race predictors and many training-plan pace tables still use it.</p>
<p>A 50:00 10K predicts {D.t(h10)} for the half marathon and <b>{D.t(m10)}</b> for the marathon, which is
{D.t(m10 / 42.195 * MI)} per mile. A 1:45:00 half predicts a {D.t(m_h)} marathon. Enter your most recent all-out race and the
table gives the prediction for every classic distance from the mile to the marathon, with the pace for each.</p>"""),
        ("How far to trust it", f"""
<p>Predictions are best between similar distances and when you have trained for the target. For a marathon, a recent half
is the best guide because the jump is only twofold. From a 5K (8.4 times shorter) the formula is usually too kind,
especially if your long runs stop short of 18 to 20 miles, since endurance and glycogen, not speed, decide the last 10K. If
you run low weekly mileage, raise the exponent to 1.07 or 1.08 under "More options": at 1.08 the same 1:45 half predicts
{D.t(m_h8)} instead of {D.t(m_h)}.</p>
<p>Riegel himself noted that the relationship holds for efforts from roughly 3.5 minutes to about 4 hours. Shorter races
lean on different energy systems, and beyond four hours fuelling, heat and muscle damage take over. Treat the result as a
starting pace for training and adjust it to how the last few weeks have gone.</p>"""),
        ("Turning the prediction into a plan", """
<p>A practical approach: take the predicted time, add 2 to 4% if it is your first marathon, and spread that pace evenly
(or run the second half slightly faster than the first). The running pace calculator turns the target into mile or
kilometre splits for a pace band or your watch.</p>"""),
    ]


FAQ = [
    ("What marathon time does a 45-minute 10K predict?",
     f"About {D.t(_pred(2700, 10, 42.195))} with Riegel's formula. That is optimistic without proper long runs: first-time marathoners often need 5 to 15 minutes more."),
    ("What about a 2-hour half marathon?",
     f"It predicts a {D.t(_pred(7200, 21.0975, 42.195))} marathon, at {D.t(_pred(7200, 21.0975, 42.195) / 42.195 * MI)} per mile."),
    ("Why is the exponent 1.06?",
     "It is the value Riegel fitted to running world records: doubling the distance multiplies the time by 2^1.06, about 2.085."),
    ("Does it work for cycling or swimming?",
     "Riegel published different exponents for other sports, but this calculator uses the running one. You can change it under \"More options\"."),
    ("Which race predicts a marathon best?",
     "An all-out half marathon in the last 4 to 8 weeks. A 10K is fine too; a 5K tends to give over-optimistic marathon times."),
]

TOOL = {
    "slug": "race-time-predictor",
    "lang": "en",
    "twin": "prediccion-maraton",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "stopwatch",
    "order": 50,
    "name": "Race time predictor",
    "k": "riegel marathon time predictor half 10k 5k race equivalent finish time",
    "title": "Race Time Predictor: Marathon Time from 5K, 10K, Half",
    "desc": "Predict your marathon, half marathon, 10K or 5K time from a recent race with Riegel's formula, with the pace per mile and per km for each.",
    "h1": "Race time predictor",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Riegel, P. S. (1981). Athletic Records and Human Endurance. American Scientist 69(3): 285-290", RIEGEL_URL)],
    "credits": [("Riegel's formula (Peter S. Riegel, Runner's World 1977; American Scientist 1981)", "published formula (reimplemented)", RIEGEL_URL)],
    "related": ["running-pace-calculator", "heart-rate-zone-calculator"],
    "tests": [
        ({}, {"n.marathon": 13800.6}),
        ({"dist": "16.09344", "tiempo": "1:20:00"}, {"n.marathon": 13334.3}),
        ({"tiempo": ""}, {"err": "Enter your time as h:mm:ss (or mm:ss)."}),
        ({"dist": "otra", "km": "0"}, {"err": "Enter the race distance."}),
    ],
}
