"""Days between dates (English twin of dias-entre-fechas): same compute, English strings."""
import datetime as dt

from herramientas.tools.dias_entre_fechas import inputs, make_js

L_EN = {
    "lang": "en", "wd": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "mon": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "e_a": "Pick the start date.", "e_b": "Pick the end date.", "e_n": "Days: a whole number from 0 to 3,000,000.",
    "e_r": "Date out of range (years 1000 to 9999).",
    "days": "Days between the dates", "past": "The end date is earlier, so the count goes backwards.",
    "d1": "day", "dn": "days", "w1": "week", "wn": "weeks", "m1": "month", "mn": "months", "y1": "year", "yn": "years", "and": " and ",
    "r_w": "In weeks", "r_m": "In months", "r_y": "In years, months and days", "r_wd": "Weekdays (Mon-Fri)", "r_we": "Weekend days",
    "r_h": "In hours", "r_res": "Result", "res": "Resulting date", "after": " after ", "before": " before ",
    "r_wk": "ISO week", "r_doy": "Day of the year", "of": " · ",
    "note": "Public holidays are not removed.",
}


def blocks(ctx):
    a, b = dt.date(2026, 11, 12), dt.date(2027, 12, 25)
    d = (b - a).days
    w, r = divmod(d, 7)
    n100 = a + dt.timedelta(100)
    return [
        ("How the days are counted", f"""
<p>From 12 November 2026 to 25 December 2027 there are <b>{d} days</b>, or {w} weeks and {r} days. The count is a plain subtraction:
the start date is left out and the end date is in, the way most people count «how many days until». If you need both ends (the
nights of a trip, the days of a hospital stay, a rental period that includes the first and last day), tick «Count both days» and
one day is added.</p>
<p>Switch to «Add or subtract» to move forward or back from a date: 100 days after 12 November 2026 is {n100:%A} {n100.day}
{n100:%B} {n100.year}. Below the result you also get the ISO week number and the day of the year, handy for project plans,
warranty periods, notice periods and medication schedules.</p>"""),
        ("Months and years are not fixed lengths", """
<p>Days are exact, but months and years are not: a month is 28 to 31 days and a year 365 or 366. So the breakdown in years, months
and days counts whole calendar months first and then the days left over. From 31 January to 28 February 2027 is one whole month,
because February has no 31st and the month ends on its last day; the same rule is used for legal and contract terms in many
countries.</p>
<p>Weekdays are counted Monday to Friday over the same span, with no public holidays removed, since they differ by country, state
and even city. For business deadlines, subtract the holidays that apply to you from the weekday figure.</p>"""),
    ]


FAQ = [
    ("How many days until Christmas 2027?",
     "From 12 November 2026 there are 408 days to 25 December 2027. Leave today's date in «From» to count from whenever you open the page."),
    ("Does the count include the start date?",
     "No. Like most calculators and legal deadlines, it starts counting the day after. Tick «Count both days» to include it."),
    ("How many weekdays are there between two dates?",
     "The «Weekdays (Mon-Fri)» row gives Monday-to-Friday days in the span, without removing public holidays."),
    ("How do I find the date 90 days from today?",
     "Choose «Add or subtract», keep today's date, type 90 and press +. You get the weekday, the ISO week and the day of the year."),
    ("Why is one year sometimes 366 days?",
     "Because the span includes 29 February of a leap year. From 1 March 2027 to 1 March 2028 there are 366 days."),
]

TOOL = {
    "slug": "days-between-dates",
    "lang": "en",
    "twin": "dias-entre-fechas",
    "cat": "dates",
    "icon": "calendar-due",
    "order": 10,
    "name": "Days between dates",
    "k": "day counter how many days until date calculator add days subtract",
    "title": "Days Between Dates Calculator: Count, Add or Subtract",
    "desc": "Count the days between two dates, in weeks, months and years, with weekdays and weekends, or add and subtract days from any date. Free, no sign-up.",
    "h1": "Days between dates",
    "updated": "2026-11-12",
    "inputs": inputs(L_EN, ["Mode", "Between dates", "Add or subtract", "From", "To", "Count both days", "Operation", "Days", "days"]),
    "js": make_js(L_EN),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ISO 8601 date and time format", "https://www.iso.org/iso-8601-date-and-time-format.html")],
    "related": ["age-calculator", "countdown", "day-of-the-week"],
    "tests": [
        ({"a": "2026-11-12", "b": "2027-12-25"}, {"n.days": 408, "n.y": 1, "n.m": 1, "n.d": 13}),
        ({"a": "2027-03-01", "b": "2028-03-01"}, {"n.days": 366, "n.y": 1}),
        ({"a": "2027-01-04", "b": "2027-01-11"}, {"n.days": 7, "n.we": 2, "n.wd": 5}),
        ({"modo": "sumar", "a": "2026-11-12", "n": "100"}, {"n.date": "2027-02-20"}),
        ({"a": "", "b": "2027-01-01"}, {"err": "Pick the start date."}),
    ],
}
