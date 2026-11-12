"""When is Easter? (English twin of fecha-semana-santa): same compute, English feast names, UK/Ireland bank-holiday notes."""
import datetime as dt

from herramientas.tools import _astro as A
from herramientas.tools.fecha_semana_santa import make_js

L_EN = {
    "lang": "en", "err": "Year between 1583 and 4099.",
    "wd": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "mon": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "label": "Easter Sunday", "week": "Holy Week: ", "to": " to ",
    "feasts": [[-47, "Shrove Tuesday (Pancake Day)"], [-46, "Ash Wednesday"], [-21, "Mothering Sunday (UK)"], [-7, "Palm Sunday"],
               [-3, "Maundy Thursday"], [-2, "Good Friday"], [-1, "Holy Saturday"], [0, "Easter Sunday", "tot"], [1, "Easter Monday"],
               [39, "Ascension Day"], [49, "Pentecost (Whit Sunday)"], [56, "Trinity Sunday"], [60, "Corpus Christi"]],
    "orth": "Orthodox Easter", "same": " (same day)",
    "th": ["Year", "Maundy Thu", "Good Friday", "Easter", "Easter Mon"],
    "next": "Next years", "early": "the earliest possible", "late": "the latest possible",
}
MON = L_EN["mon"]


def blocks(ctx):
    rows = ""
    for y in range(2027, 2037):
        e, o = A.easter(y), A.easter_orthodox(y)
        f = lambda d: f"{d.day} {MON[d.month - 1][:3]}"  # noqa: E731
        rows += f"<tr><td>{y}</td><td>{f(e - dt.timedelta(2))}</td><td>{f(e)}</td><td>{f(e + dt.timedelta(1))}</td><td>{f(o)}</td></tr>"
    e = A.easter(2027)
    return [
        ("Easter dates 2027-2036", f"""
<p>Easter Sunday 2027 is on <b>{e.day} March</b>, one of the earliest of the decade, so Good Friday is 26 March and Easter Monday
29 March. In 2028 it moves to 16 April. Enter any year from 1583 to 4099 to get every date that hangs on Easter, from Shrove Tuesday
to Corpus Christi.</p>
<table class="tbl"><thead><tr><th>Year</th><th>Good Friday</th><th>Easter Sunday</th><th>Easter Monday</th><th>Orthodox Easter</th></tr></thead><tbody>{rows}</tbody></table>
<p>In England, Wales and Northern Ireland both Good Friday and Easter Monday are bank holidays; in Scotland only Good Friday is. In
Ireland, Easter Monday is a public holiday and Good Friday is not. Mothering Sunday in the UK is also tied to Easter: the fourth
Sunday of Lent, three weeks before Easter Sunday.</p>"""),
        ("The rule behind the date", """
<p>Since the Council of Nicaea in 325, Easter is the first Sunday after the first full moon on or after 21 March. That keeps it
between 22 March and 25 April. The full moon is not the astronomical one but an «ecclesiastical» moon from tables, which almost
always matches the sky but can be a day or two off, and 21 March is fixed even when the real equinox falls on the 20th.</p>
<p>The Gregorian reform of 1582 rewrote those tables, so the calculation is valid from 1583. Most Orthodox churches still use the
Julian calendar for Easter: some years both dates coincide (2028, 2031, 2034) and in others they are up to five weeks apart.</p>"""),
        ("How the date is calculated", """
<p>This uses the anonymous Gregorian algorithm, sent to Nature in 1876 and later printed by Jean Meeus. For 2027: the year modulo
19 is a = 13 (its place in the 19-year lunar cycle), the century b = 20 and the year within it c = 27. These give d = 5, e = 0,
f = 1 and g = 6, then the moon's age h = (19·13 + 20 − 5 − 6 + 15) mod 30 = 1. With i = 6 and k = 3, the weekday term is
l = (32 + 0 + 12 − 1 − 3) mod 7 = 5 and m = 0, so n = h + l − 7m + 114 = 120. The month is 120 ÷ 31 = 3 (March) and the day is the
remainder plus one, 27 + 1 = 28: Easter 2027 is 28 March.</p>
<p>The other movable feasts count from that Sunday: Ash Wednesday 46 days before, Palm Sunday 7 before, Ascension 39 after (a
Thursday, moved to the following Sunday in some countries), Pentecost 49 after and Corpus Christi 60 after.</p>"""),
    ]


FAQ = [
    ("When is Easter 2027?",
     "Sunday 28 March 2027. Good Friday is 26 March and Easter Monday 29 March. Orthodox Easter is later, on 2 May."),
    ("What are the earliest and latest possible Easter dates?",
     "22 March and 25 April. The next latest Easter is in 2038 (25 April); the next earliest is not until 2285 (22 March)."),
    ("Why does Easter move every year?",
     "Because it follows the moon: it is the Sunday after the first full moon of spring, and the 29.5-day lunar cycle does not fit evenly "
     "into the solar year."),
    ("When is Pancake Day?",
     "Shrove Tuesday is 47 days before Easter Sunday: 9 February in 2027 and 29 February in 2028."),
    ("Why is Orthodox Easter on a different date?",
     "The Orthodox churches compute Easter with the Julian calendar, now 13 days behind the Gregorian one, and with older moon tables. "
     "Both dates coincide in some years, such as 2028."),
]

TOOL = {
    "slug": "easter-date",
    "lang": "en",
    "twin": "fecha-semana-santa",
    "cat": "dates",
    "icon": "egg",
    "order": 30,
    "name": "Easter date",
    "k": "easter sunday good friday ash wednesday pancake day pentecost orthodox",
    "title": "When Is Easter? Easter Sunday Date for Any Year",
    "desc": "Find the date of Easter Sunday for any year from 1583 to 4099, with Good Friday, Easter Monday, Ash Wednesday, Pancake Day, Pentecost and Orthodox Easter.",
    "h1": "When is Easter?",
    "updated": "2026-11-12",
    "inputs": [{"id": "ano", "type": "number", "label": "Year", "value": 2027, "w": "s", "maxlength": 4}],
    "js": make_js(L_EN),
    "css": ".ss{max-width:560px;margin-top:8px}.ss td,.ss th{text-align:left}",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("US Naval Observatory · The Date of Easter", "https://aa.usno.navy.mil/faq/easter"),
                ("GOV.UK · UK bank holidays", "https://www.gov.uk/bank-holidays")],
    "credits": [("Anonymous Gregorian algorithm (Nature, 1876; Jean Meeus, Astronomical Algorithms, ch. 8)", "public domain",
                 "https://en.wikipedia.org/wiki/Date_of_Easter#Anonymous_Gregorian_algorithm")],
    "related": ["moon-phases-2027", "days-between-dates", "day-of-the-week", "countdown"],
    "tests": [
        ({"ano": "2027"}, {"n.easter": "2027-03-28", "n.goodfri": "2027-03-26", "n.orth": "2027-05-02", "n.ash": "2027-02-10"}),
        ({"ano": "2026"}, {"n.easter": "2026-04-05", "n.orth": "2026-04-12"}),
        ({"ano": "2038"}, {"n.easter": "2038-04-25"}),
        ({"ano": "1583"}, {"err": None}),
        ({"ano": "2027.5"}, {"err": "Year between 1583 and 4099."}),
    ],
}
