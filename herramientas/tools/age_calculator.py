"""Age calculator (English twin of edad-exacta): same compute, English strings."""
from herramientas.tools.edad_exacta import make_js

L_EN = {
    "lang": "en", "wd": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "mon": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "e_b": "Enter the date of birth.", "e_t": "Pick the date to calculate the age on.", "e_o": "The date of birth is later.",
    "e_r": "Date out of range (years 1000 to 9999).",
    "age": "Age", "d1": "day", "dn": "days", "w1": "week", "wn": "weeks", "m1": "month", "mn": "months", "y1": "year", "yn": "years", "and": " and ",
    "r_m": "In months", "r_w": "In weeks", "r_d": "Days lived", "r_born": "Born on a", "r_next": "Next birthday",
    "r_mile": "You reach", "r_18": "Turns 18 on", "today": "today", "in": "in ", "turns": "turns ",
    "bday": "Happy birthday!", "leap": "Born on 29 February: in common years the birthday is counted on 28 February.",
}


def blocks(ctx):
    return [
        ("How your exact age is worked out", """
<p>Someone born on 15 May 1990 is <b>36 years, 5 months and 28 days</b> old on 12 November 2026: 36 whole years up to 15 May
2026, five whole months to 15 October, then 28 more days. That is 13,330 days lived, or 1,904 weeks and 2 days, and the day of
birth was a Tuesday. The calculator counts whole years first, then whole months, then the days left over, the way people state
an age out loud.</p>
<p>The age is worked out for today by default, but «On date» takes any other date: how old someone was on a past event, how old
they will be on a trip or an exam, or a parent's age when a child was born. It also shows the next birthday, how many days are
left and which weekday it falls on, plus the date of your next thousand-day milestone, a fun one to celebrate: 10,000 days arrives
at about 27 years and 4 months.</p>"""),
        ("Leap-day birthdays and legal age", """
<p>People born on 29 February only get their exact birthday in leap years. In other years this calculator adds the year on
28 February, the last day of the month, which is how many legal systems count terms in years when the final month has no matching
day. Others celebrate on 1 March; the age in days is the same either way.</p>
<p>For legal age, most countries count a birthday from the start of the day, not the hour of birth: someone born on 15 May 2009
turns 18 at midnight on 15 May 2027. If the person is under 18, the result also shows the date they come of age. Rules for school
years, pensions or insurance often use a cut-off date instead, so check the date your form asks for.</p>"""),
    ]


FAQ = [
    ("How many days old am I?",
     "Enter your date of birth: «Days lived» counts every day from then to today, not counting the day you were born."),
    ("When will I be 10,000 days old?",
     "At 27 years, 4 months and 15 to 18 days, depending on your birth date. The «You reach» row gives the exact date of your next "
     "thousand-day mark."),
    ("How old was I on a specific date?",
     "Replace «On date» with that date. The result gives your age then in years, months and days."),
    ("How is age counted for someone born on 29 February?",
     "In common years this calculator counts the birthday on 28 February. Some people and some rules use 1 March instead."),
    ("Why does the number of weeks not match years times 52?",
     "A year is 52 weeks and one or two days, so the extra days add up: 36 years is about 1,878 weeks, not 1,872."),
]

TOOL = {
    "slug": "age-calculator",
    "lang": "en",
    "twin": "edad-exacta",
    "cat": "dates",
    "icon": "cake",
    "order": 20,
    "name": "Age calculator",
    "k": "exact age how old am i days old birthday date of birth",
    "title": "Age Calculator: Exact Age in Years, Months and Days",
    "desc": "Work out your exact age in years, months and days from your date of birth, plus days lived, your next birthday and the weekday you were born.",
    "h1": "Age calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "nac", "type": "date", "label": "Date of birth", "value": "1990-05-15", "min": "1000-01-01", "max": "9999-12-31"},
        {"id": "hoy", "type": "date", "label": "On date", "value": "2026-11-12", "today": True, "min": "1000-01-01", "max": "9999-12-31"},
    ],
    "js": make_js(L_EN),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ISO 8601 date and time format", "https://www.iso.org/iso-8601-date-and-time-format.html")],
    "related": ["days-between-dates", "day-of-the-week", "countdown"],
    "tests": [
        ({"nac": "1990-05-15", "hoy": "2026-11-12"}, {"n.y": 36, "n.m": 5, "n.d": 28, "n.days": 13330, "n.months": 437}),
        ({"nac": "2000-02-29", "hoy": "2028-02-29"}, {"n.y": 28, "n.m": 0, "n.d": 0}),
        ({"nac": "2009-05-15", "hoy": "2027-05-14"}, {"n.y": 17, "n.next": "2027-05-15", "n.toNext": 1}),
        ({"nac": "", "hoy": "2026-11-12"}, {"err": "Enter the date of birth."}),
    ],
}
