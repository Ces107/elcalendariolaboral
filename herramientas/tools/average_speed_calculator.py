"""Average speed calculator (English twin of velocidad-media-tiempo): same compute, miles or kilometres."""
from herramientas.tools import _coche as K
from herramientas.tools.velocidad_media_tiempo import JS

GOV = "https://www.gov.uk/speed-limits"
HWC = "https://www.gov.uk/guidance/the-highway-code/rules-for-drivers-and-motorcyclists-89-to-102"
NIST = "https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9"


def blocks(ctx):
    return [
        ("Speed, distance and time", """
<p>Average speed is total distance divided by total time. Rearranged, time = distance ÷ speed and distance = speed × time.
Pick what you want to find, fill in the other two and the calculator answers in mph or km/h, plus metres per second and the
pace per mile or kilometre.</p>
<p>Example: a 200-mile drive that takes 3 hours 20 minutes door to door averages 200 ÷ 3.333 = <b>60 mph</b>, even if you
spent most of it at 70 on the motorway; fuel stops, town traffic and roadworks pull the average down. The other way round, 120
miles at an average of 50 mph takes 2.4 hours, which is <b>2 hours 24 minutes</b>, not 2 hours 40. Type the time as h:mm
("3:20"), as "3h20" or as minutes ("90min"); a plain number is read as hours.</p>"""),
        ("Why you cannot average two speeds", """
<p>Drive 60 miles out at 40 mph and back at 60 mph and your average is not 50 mph but <b>48 mph</b>. The outward leg takes
1 h 30 min and the return 1 h, so 120 miles take 2 h 30 min. You spend longer at the slower speed, so it weighs more in the
average (it is the harmonic mean, not the arithmetic one). For any multi-leg trip, add up all the distances and all the times
and divide once. The same arithmetic explains why making up lost time later in a journey takes a much higher speed than
people expect.</p>"""),
        ("Average speed cameras and breaks", f"""
<p>Average speed cameras, common on UK motorway roadworks and some rural A-roads, time your car between two points and work
out exactly this average. Over a 3-mile section with a 50 mph limit, the minimum legal time is 3 ÷ 50 × 3,600 =
<b>216 seconds, 3 min 36 s</b>; covering it in 3 minutes means 60 mph. Enter the limit under "More options" to see the minimum
time and how far above or below the limit you are. National limits for cars on GOV.UK are
<a href="{GOV}" rel="noopener">30 mph in built-up areas, 60 on single carriageways and 70 on dual carriageways and
motorways</a>, unless signs say otherwise.</p>
<p>For long drives, the <a href="{HWC}" rel="noopener">Highway Code (rule 91)</a> recommends a break of at least 15 minutes
after every two hours of driving: at a 60 mph average that is roughly every 120 miles.</p>"""),
    ]


FAQ = [
    ("How do you calculate average speed?",
     "Divide the total distance by the total time. 150 miles in 2 h 30 min (2.5 h) is 60 mph."),
    ("How long does it take to drive 100 miles at 70 mph?",
     "About 1 hour 26 minutes: 100 ÷ 70 = 1.43 h. At 60 mph it would be 1 h 40 min, only 14 minutes more."),
    ("How do I convert mph to km/h?",
     "Multiply by 1.609344, because the international mile is exactly 1,609.344 metres. 70 mph is 112.7 km/h."),
    ("How do average speed cameras work?",
     "They read your number plate at two or more points and divide the distance between them by the time you took. If that "
     "average is above the limit, you can be fined even if you slowed down at the cameras."),
    ("Does driving faster save much time?",
     "Less than it seems. Over 200 miles, going 75 instead of 70 mph saves about 11 minutes and burns noticeably more fuel."),
]

INPUTS = [
    {"id": "calc", "type": "seg", "label": "Find", "value": "vel", "options": [("vel", "Speed"), ("tiempo", "Time"), ("dist", "Distance")]},
    {"id": "u", "type": "seg", "label": "Units", "value": "mi", "options": [("mi", "miles"), ("km", "km")]},
    {"id": "dist", "type": "number", "label": "Distance", "value": "200", "step": "0.01", "w": "s", "show": ("calc", ["vel", "tiempo"])},
    {"id": "t", "type": "text", "label": "Time", "value": "3:20", "placeholder": "h:mm", "w": "s", "show": ("calc", ["vel", "dist"])},
    {"id": "vel", "type": "number", "label": "Speed", "value": "50", "step": "0.1", "w": "s", "show": ("calc", ["tiempo", "dist"])},
    {"id": "lim", "type": "number", "label": "Speed limit", "value": "", "w": "s", "more": True},
]

TOOL = {
    "slug": "average-speed-calculator",
    "lang": "en",
    "twin": "velocidad-media-tiempo",
    "cat": K.CAT_EN[0], "cat_name": K.CAT_EN[1],
    "icon": "gauge",
    "order": 20,
    "name": "Average speed calculator",
    "k": "speed distance time mph km/h how long to drive average speed camera",
    "title": "Average Speed Calculator: Speed, Distance and Time",
    "desc": "Work out average speed, travel time or distance in mph or km/h, and the minimum time to stay under the limit through average speed cameras.",
    "h1": "Average speed calculator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": K.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("GOV.UK · Speed limits", GOV), ("GOV.UK · The Highway Code, rules 89 to 102", HWC),
                ("NIST SP 811, Appendix B.9 · mile = 1,609.344 m", NIST)],
    "credits": [],
    "related": ["mpg-to-l100km", "tire-size-calculator"],
    "tests": [
        ({}, {"n.speed": 60}),
        ({"calc": "tiempo", "dist": "120", "vel": "50"}, {"n.sec": 8640}),
        ({"calc": "dist", "vel": "70", "t": "1h30"}, {"n.dist": 105}),
        ({"dist": "3", "t": "0:03:00", "lim": "50"}, {"n.speed": 60, "n.min": 216}),
        ({"dist": ""}, {"err": "Enter the distance."}),
    ],
}
