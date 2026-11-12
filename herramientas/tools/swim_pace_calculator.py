"""Swim pace calculator (English twin of ritmo-natacion): yards by default, English texts."""
from herramientas.tools import _deporte as D
from herramientas.tools.ritmo_natacion import JS, CSS, WAKAYOSHI, NIST, inputs


def blocks(ctx):
    css = (440 - 210) / 2
    return [
        ("Pace per 100", """
<p>Swimmers measure pace as <b>time per 100</b>, yards or metres depending on the pool: pace = time ÷ distance × 100. The
classic 1,650-yard "mile" in 30 minutes is <b>1:49 per 100 yd</b>; 1,500 m in 30 minutes is 2:00 per 100 m. Pick your pool
length with the "Pool" switch (yd or m). The table under the result shows what that pace means over the usual distances:
500 and 1,000 yd, the mile, or in metres the 1,900 m of a half Ironman and the 3,800 m of a full one, before allowing for
fatigue or open-water conditions.</p>"""),
        ("Working out a set", """
<p>Choose "Set" and enter the number of repeats, the distance of each one, the pace you want to hold and the rest. You get
the swim time of each repeat, the <b>send-off</b> (how often you leave on the pace clock: swim time plus rest) and the time
for the whole set. Example: 10 × 100 at 1:50 per 100 with 15 seconds' rest means leaving every 2:05, and the set takes 20:35
in total, since the rest after the last repeat does not count.</p>"""),
        ("Critical swim speed (CSS)", f"""
<p><b>Critical swim speed</b> is the pace you could hold for a long time without fatigue running away, the swimming
equivalent of threshold pace. You estimate it from two all-out swims on the same day, a 400 and a 200 with a good recovery
between them: <b>CSS = (400 time − 200 time) ÷ 2</b>, per 100. A 7:20 400 and a 3:30 200 give (440 − 210) ÷ 2 = {css:g} seconds,
or <b>{D.t(css)} per 100</b>. The method comes from Wakayoshi and colleagues' 1992 study of competitive swimmers, which linked
this speed to the lactate threshold. Retest every 6 to 8 weeks: a falling CSS means you have improved. Many endurance sets
are swum at CSS or a few seconds slower.</p>"""),
    ]


FAQ = [
    ("What is a good swim pace per 100?",
     "Adult fitness swimmers usually hold 1:45 to 2:15 per 100 yd over longer swims. Under 1:30 per 100 yd is strong club level; elite distance swimmers go under 1:05."),
    ("How long does it take to swim a mile?",
     "At 2:00 per 100 yd, a 1,650-yard pool mile takes 33 minutes; at 1:45, about 29 minutes. Enter your time to get your exact pace."),
    ("What does \"leave on 2:05\" mean?",
     "Each repeat starts when the pace clock has moved on 2:05 from the start of the previous one; whatever time you are not swimming is your rest."),
    ("How do I do a CSS test?",
     "Warm up well, swim an all-out 400, recover with 5 to 10 minutes of easy swimming, then swim an all-out 200. Enter both times under \"CSS\"."),
    ("Does it work for metre pools?",
     "Yes. Switch \"Pool\" to m and every distance and pace changes to metres. Speed is shown in km/h either way."),
]

TOOL = {
    "slug": "swim-pace-calculator",
    "lang": "en",
    "twin": "ritmo-natacion",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "swimming",
    "order": 100,
    "name": "Swim pace calculator",
    "k": "swim pace per 100 yards meters pool send-off interval set css critical swim speed triathlon",
    "title": "Swim Pace Calculator: Per 100 Yards or Meters, CSS",
    "desc": "Work out your swim pace per 100 yd or m, the send-off and total time of a set with rest, and your critical swim speed (CSS) from a 400 and 200.",
    "h1": "Swim pace calculator",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Wakayoshi K et al. (1992). Determination and validity of critical velocity as an index of swimming performance. Eur J Appl Physiol 64: 153-157", WAKAYOSHI),
                ("NIST · international yard = 0.9144 m", NIST)],
    "credits": [("Critical swim speed (Wakayoshi et al., 1992)", "published formula (reimplemented)", WAKAYOSHI)],
    "related": ["running-pace-calculator", "heart-rate-zone-calculator", "bike-gear-calculator"],
    "tests": [
        ({}, {"n.pace": 109.091}),
        ({"modo": "serie", "reps": "8", "drep": "50", "ritmo": "1:40", "desc": "10"}, {"n.swim": 50, "n.send": 60, "n.total": 470}),
        ({"modo": "css", "t400": "6:40", "t200": "3:12"}, {"n.css": 104}),
        ({"modo": "serie", "reps": "0"}, {"err": "Enter 1 to 100 repeats."}),
    ],
}
