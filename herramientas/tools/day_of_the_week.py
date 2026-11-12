"""Day of the week for any date (English twin of dia-de-la-semana): same compute, English strings; Julian note keyed to
the British switch of 1752 in the text."""
from herramientas.tools.dia_de_la_semana import make_js

L_EN = {
    "lang": "en", "wd": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "mon": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "e_d": "Pick a date.", "e_r": "Date out of range (years 1000 to 9999).", "was": " was a", "is": " is a", "will": " will be a",
    "r_wk": "ISO week", "r_doy": "Day of the year", "r_left": "Days left in the year", "r_leap": "Leap year", "yes": "yes", "no": "no",
    "r_jul": "If it is a Julian date", "jul_note": "Before 15 October 1582 (1752 in Britain and its colonies) dates were written in the Julian calendar: for a date taken from a document of that time, use the «If it is a Julian date» row.",
    "next": "The same date in the next years", "year": "Year", "day": "Day", "of": " · ", "d1": "day", "dn": "days",
}


def blocks(ctx):
    return [
        ("Examples", """
<p>20 July 1969, the day Apollo 11 landed on the Moon, was a <b>Sunday</b>; 4 July 1776 was a Thursday; and Christmas Day 2027
falls on a Saturday, with Christmas Eve on the Friday. Enter any date from the year 1000 to 9999 to see which weekday it was or will
be, its ISO 8601 week number (weeks start on Monday, week 1 holds the year's first Thursday) and its day of the year.</p>
<p>Below the answer you get the same date over the next ten years, so you can see at a glance which weekday a birthday, an
anniversary or a recurring event falls on. A date moves forward one weekday each common year and two when the span crosses
29 February.</p>"""),
        ("Working it out by hand", """
<p>Zeller's congruence turns a date into a weekday with one sum. For 20 July 1969: day q = 20, month m = 7, the last two digits of
the year K = 69 and the century J = 19 (January and February count as months 13 and 14 of the previous year). Add q = 20, the whole
part of 13·(m + 1)/5 = 20, K = 69, the whole part of K/4 = 17, of J/4 = 4, and 5·J = 95: the total is 225. 225 divided by 7 leaves
1, and in Zeller's numbering 0 is Saturday and 1 is Sunday. The calculator does the same with exact date arithmetic, which agrees
over the whole range.</p>"""),
        ("Old dates and the Julian calendar", """
<p>Catholic Europe moved to the Gregorian calendar in 1582, dropping ten days: Thursday 4 October was followed by Friday 15 October.
Britain and its American colonies waited until 1752, when Wednesday 2 September was followed by Thursday 14 September; Russia
switched in 1918. Dates written before the switch, such as George Washington's birth on 11 February 1731 (Julian), are «Old
Style». For dates before 15 October 1582 the calculator adds the weekday as if the date were Julian; for British dates between 1582
and 1752, convert to the Gregorian date first.</p>"""),
    ]


FAQ = [
    ("What day of the week is Christmas 2027?",
     "Saturday 25 December 2027. Christmas Eve is a Friday and New Year's Day 2028 is a Saturday as well."),
    ("Why does a date move one weekday each year?",
     "Because 365 days is 52 weeks plus one day. A leap year has 366 days, so dates after 29 February move two weekdays."),
    ("What is an ISO week number?",
     "The ISO 8601 week count: weeks run Monday to Sunday and week 1 is the one with the year's first Thursday. So Friday 1 January 2027 "
     "is in week 53 of 2026."),
    ("Does it work for historical dates?",
     "Yes, from the year 1000. For dates written in the Julian calendar before 15 October 1582, read the «If it is a Julian date» row."),
    ("Do calendars repeat?",
     "Yes. A common year reuses an earlier calendar after 6 or 11 years, and with leap years the full cycle is 28 years within a century. "
     "The 2027 calendar is the same as 2021 and 2010."),
]

TOOL = {
    "slug": "day-of-the-week",
    "lang": "en",
    "twin": "dia-de-la-semana",
    "cat": "dates",
    "icon": "calendar-question",
    "order": 40,
    "name": "Day of the week",
    "k": "what day was weekday calculator date iso week julian",
    "title": "What Day of the Week Was It? Day Finder for Any Date",
    "desc": "Find the day of the week for any date from 1000 to 9999, with the ISO week number, the day of the year and the same date in the coming years.",
    "h1": "What day of the week is it?",
    "updated": "2026-11-12",
    "inputs": [{"id": "fecha", "type": "date", "label": "Date", "value": "1969-07-20", "min": "1000-01-01", "max": "9999-12-31"}],
    "js": make_js(L_EN),
    "css": ".dw{max-width:300px;margin-top:8px}.dw td,.dw th{text-align:left}",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ISO 8601 date and time format", "https://www.iso.org/iso-8601-date-and-time-format.html"),
                ("Calendar (New Style) Act 1750", "https://www.legislation.gov.uk/apgb/Geo2/24/23")],
    "credits": [("Zeller's congruence (1882) and Julian Day Number", "public domain", "https://en.wikipedia.org/wiki/Zeller%27s_congruence")],
    "related": ["age-calculator", "days-between-dates", "easter-date"],
    "tests": [
        ({"fecha": "1969-07-20"}, {"n.wd": 6, "n.week": 29, "n.doy": 201}),
        ({"fecha": "1776-07-04"}, {"n.wd": 3}),
        ({"fecha": "2027-12-25"}, {"n.wd": 5, "n.week": 51}),
        ({"fecha": "1066-10-14"}, {"n.jul": 5}),
        ({"fecha": "0999-12-31"}, {"err": "Date out of range (years 1000 to 9999)."}),
    ],
}
