"""Countdown (English twin of cuenta-atras): same compute and live ticker, English presets (Christmas, New Year,
Easter, Halloween, Valentine's Day, US Thanksgiving) or any date and time with a name."""
from herramientas.tools.cuenta_atras import inputs, make_js

L_EN = {
    "lang": "en", "wd": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "mon": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "ev": {"christmas": [12, 25, "Christmas"], "newyear": [1, 1, "New Year"], "easter": ["E", 0, "Easter"], "halloween": [10, 31, "Halloween"],
           "valentine": [2, 14, "Valentine's Day"], "thanksgiving": ["T", 0, "Thanksgiving"]},
    "e_d": "Pick the date.", "e_r": "Date out of range (years 1000 to 9999).", "e_t": "Invalid time.",
    "left": "Time left", "until": " until ", "today": "It's today!", "past": "Already passed", "ago": "", "mine": "My date",
    "d1": "day", "dn": "days", "w1": "week", "wn": "weeks", "and": " and ", "u": ["d", "h", "m", "s"],
    "r_date": "Date", "r_w": "In weeks", "r_h": "In hours", "r_m": "In minutes", "at": " at ",
    "note": "Uses your device's clock and time zone.",
}
OPTS_EN = [("christmas", "Christmas"), ("newyear", "New Year"), ("easter", "Easter"), ("halloween", "Halloween"),
           ("valentine", "Valentine's Day"), ("thanksgiving", "Thanksgiving (US)"), ("fecha", "Other date")]


def blocks(ctx):
    return [
        ("How it works", """
<p>Pick an event from the list (Christmas, New Year, Easter, Halloween, Valentine's Day or US Thanksgiving) and the countdown starts
straight away in days, hours, minutes and seconds. For anything else, a wedding, a trip, a due date, exams or the last day at work,
choose «Other date», set the day, an optional time and a name. «Copy link» stores all of it in the address, so whoever opens it sees
the same countdown, with your title, on their own phone.</p>
<p>The listed events roll over by themselves: after 31 October the Halloween countdown jumps to next year, Easter is recalculated
each year from the church rule, and Thanksgiving is always the fourth Thursday of November (26 November in 2026, 25 November in
2027). From 12 November 2026 there are 43 days to Christmas and 50 to New Year's Day.</p>"""),
        ("Days left versus exact time", """
<p>«Days left» is a calendar count from today to the target day, not counting today. The hours, minutes and seconds run to midnight at
the start of that day, or to the time you set, using your device's clock and time zone: a New Year countdown hits zero in London at
the same moment as in Lisbon, an hour after Paris and five hours before New York. If your phone's clock is set by the network,
the countdown is accurate to the second.</p>
<p>Under «More options», «Count from» works out how many days were or will be left from another date, for instance how far the
wedding was on the day you booked the venue.</p>"""),
    ]


FAQ = [
    ("How many days until Christmas?",
     "From 12 November 2026, 43 days. The countdown above updates itself from today's date and runs to midnight on 25 December."),
    ("Can I make a countdown for my wedding or holiday?",
     "Yes. Choose «Other date», enter the day, the time and a name such as «Our wedding», then copy the link and share it."),
    ("Is my countdown saved?",
     "Nothing is stored on a server: everything is in the link. Bookmark it or add it to your phone's home screen to come back."),
    ("When is Thanksgiving 2027?",
     "Thursday 25 November 2027, the fourth Thursday of November. In 2026 it is on 26 November."),
    ("Why does it differ from another countdown?",
     "Countdowns can aim at different times (midnight, dinner, the ceremony) or use another time zone. This one uses your device's."),
]

TOOL = {
    "slug": "countdown",
    "lang": "en",
    "twin": "cuenta-atras",
    "cat": "dates",
    "icon": "hourglass",
    "order": 50,
    "name": "Countdown",
    "k": "countdown timer days until christmas new year wedding holiday",
    "title": "Countdown Timer: How Many Days Until Any Date",
    "desc": "A live countdown in days, hours, minutes and seconds to Christmas, New Year, Easter, Halloween or your own date, with a link to share it.",
    "h1": "Countdown to any date",
    "updated": "2026-11-12",
    "inputs": inputs(L_EN, ["Until", "Date", "Time", "Name", "Count from"], OPTS_EN, "2027-07-31", "Our wedding"),
    "js": make_js(L_EN),
    "css": ".t-countdown .hbig-n{font-variant-numeric:tabular-nums}",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("NIST · official US time", "https://www.time.gov/"),
                ("US Office of Personnel Management · federal holidays", "https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/")],
    "related": ["days-between-dates", "easter-date", "age-calculator"],
    "tests": [
        ({"ev": "christmas", "desde": "2026-11-12"}, {"n.days": 43, "n.date": "2026-12-25"}),
        ({"ev": "thanksgiving", "desde": "2026-11-12"}, {"n.date": "2026-11-26", "n.days": 14}),
        ({"ev": "thanksgiving", "desde": "2026-11-27"}, {"n.date": "2027-11-25"}),
        ({"ev": "easter", "desde": "2026-11-12"}, {"n.date": "2027-03-28"}),
        ({"ev": "fecha", "d": "2027-07-31", "h": "25:00", "desde": "2026-11-12"}, {"err": "Invalid time."}),
    ],
}
