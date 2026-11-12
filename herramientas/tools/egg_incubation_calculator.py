"""Egg incubation calculator (English twin of incubacion-huevos): same bird data and compute, English strings, °F shown."""
from herramientas.tools.incubacion_huevos import BIRDS, CSS, MSD, MSU, bird_options, make_js

L_EN = {
    "lang": "en",
    "mon": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "wd": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "label": "Hatch day", "start": "Set the eggs", "turn": "Last turning day", "lock": "Lockdown: no turning, more humidity",
    "c1": "First candling", "c2": "Second candling", "hatch": "Hatch", "temp": "Temperature", "wb": "wet bulb",
    "days": " days", "day": "Day", "date": "Date", "task": "Task", "t_turn": "Turn 3-5 times (odd number)",
    "t_lock": "Do not turn · raise humidity", "t_c": "Candle", "t_h": "Hatch", "today": "today",
    "err": "Enter the day you set the eggs.", "sub": "Turn until ",
    "note": "Forced-air incubator figures (Mississippi State University). Eggs from heavy breeds or stored over 7 days can take a day longer.",
    "ics": "incubation.ics", "x": "Day by day", "inc": "Incubation · ",
}


def f(c):
    return round(c * 9 / 5 + 32)


def blocks(ctx):
    rows = "".join(f"<tr><td>{en}</td><td class=\"num\">{d}</td><td class=\"num\">{t}</td><td class=\"num\">{f(c)} °F · {c} °C</td></tr>"
                   for k, d, t, c, wb, es, en in BIRDS)
    return [
        ("How many days until the eggs hatch", f"""
<p>Chicken eggs hatch <b>21 days</b> after you set them in the incubator. Ducks and turkeys take <b>28</b>, Muscovy ducks 35, geese
28 to 34 (30 is a fair average), coturnix quail <b>17</b> and guinea fowl 28. Day 0 is the day the eggs go in, and the first chicks
usually pip the evening before the hatch date.</p>
<table class="tbl"><thead><tr><th>Bird</th><th>Days</th><th>Last turn</th><th>Temperature</th></tr></thead><tbody>{rows}</tbody></table>
<p>The calculator gives the hatch date, the last turning day, both candling days and a printable day-by-day plan, and «Download
.ics» puts the milestones in your calendar so you do not miss lockdown.</p>"""),
        ("Turning, temperature and humidity", """
<p><b>Turn the eggs</b> from day one until two or three days before the hatch, so the embryo does not stick to the shell membrane.
An automatic turner should tilt them at least every two hours; by hand, turn an odd number of times a day (3, 5 or 7) so each egg
does not spend two nights in a row on the same side, and pencil an X on one side to check every egg really moved. After the last
turning day comes lockdown: keep the lid shut and raise the humidity so the membrane stays soft for the chick.</p>
<p>In a fan-forced incubator, run <b>100 °F (37.8 °C)</b> for most species and 99 °F (37.2 °C) for geese and turkeys. A still-air
incubator needs 2 to 3 °F more, measured at the top of the eggs; the «Still air» option adds about 2 °F (1 °C). Humidity is given as
a wet-bulb reading of about 85 to 87 °F, roughly 55 to 60 % relative humidity at 100 °F.</p>"""),
        ("Worked example and sources", f"""
<p>Set chicken eggs on <b>Monday 1 March 2027</b> and the first candling falls on day 7 (8 March), the last turn on day 18 (19 March)
and the hatch on day 21, <b>Monday 22 March</b>. The days, last turning days and temperatures come from the
<a href="{MSU}" rel="noopener">Mississippi State University Extension hatchery management guide</a> for forced-air machines, and
agree with the <a href="{MSD}" rel="noopener">MSD Veterinary Manual incubation periods</a>. The first candling is placed a third of
the way through (day 7 for chickens), when the veins show; the second on the last turning day, to take out clear eggs and early
deaths before lockdown.</p>"""),
    ]


FAQ = [
    ("How long does it take for a chicken egg to hatch?",
     "21 days at 100 °F (37.8 °C) in a fan-forced incubator. Unsteady temperature or eggs stored over a week can push it a day either way."),
    ("When do you stop turning chicken eggs?",
     "On day 18. From then until the hatch, do not turn the eggs or open the incubator, and raise the humidity."),
    ("How long do duck eggs take to hatch?",
     "28 days for most breeds (Pekin, Runner, Khaki Campbell) and 35 for Muscovy ducks. Stop turning on day 25 and day 31."),
    ("How long do quail eggs take to hatch?",
     "17 days for coturnix (Japanese) quail, with the last turn on day 15. Bobwhite quail take 23 to 24 days."),
    ("What if the power goes out during incubation?",
     "A few hours of cooling early on usually just lengthens incubation; cover the incubator with a blanket and keep it closed. "
     "Overheating is far more dangerous than a short chill."),
    ("When should I candle the eggs?",
     "For chickens, around day 7, when veins and the embryo show, and on day 18 before lockdown, to remove clear eggs and dead embryos."),
]

TOOL = {
    "slug": "egg-incubation-calculator",
    "lang": "en",
    "twin": "incubacion-huevos",
    "cat": "animals",
    "cat_name": "Animals and farm",
    "icon": "egg-cracked",
    "order": 30,
    "name": "Egg incubation calculator",
    "k": "incubator hatch date chicken duck quail goose turkey guinea lockdown candling turning 21 days",
    "title": "Egg Incubation Calculator: Hatch Date and Lockdown",
    "desc": "Hatch date, last turning day, candling days and a day-by-day plan for chicken (21 days), duck, quail, goose, turkey or guinea eggs. Print it or save it.",
    "h1": "Egg incubation calculator",
    "crumb": "Egg incubation",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ave", "type": "select", "label": "Bird", "value": "gallina", "options": bird_options("en")},
        {"id": "fecha", "type": "date", "label": "Set on", "value": "2026-11-12", "today": True, "min": "2000-01-01", "max": "2035-12-31"},
        {"id": "aire", "type": "check", "label": "Still air", "value": False, "more": True},
    ],
    "js": make_js(L_EN),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Mississippi State University Extension · Hatchery management guide", MSU),
                ("MSD Veterinary Manual · approximate incubation periods", MSD)],
    "related": ["animal-gestation-calculator", "dog-cat-age-calculator", "moon-phases-2027"],
    "tests": [
        ({"ave": "gallina", "fecha": "2027-03-01"}, {"n.hatch": "2027-03-22", "n.last": "2027-03-19"}),
        ({"ave": "pato", "fecha": "2027-05-10"}, {"n.hatch": "2027-06-07", "n.last": "2027-06-04"}),
        ({"ave": "pavo", "fecha": "2027-05-10", "aire": True}, {"n.temp": 38.2}),
        ({"ave": "oca", "fecha": ""}, {"err": "Enter the day you set the eggs."}),
    ],
}
