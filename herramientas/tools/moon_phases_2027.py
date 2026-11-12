"""Moon phases 2027 (English twin of calendario-lunar-2027): same compute, English strings, any time zone, traditional
full-moon names."""
import datetime as dt
import zoneinfo

from herramientas.tools import _astro as A
from herramientas.tools.calendario_lunar_2027 import make_js

NAMES = ["Wolf Moon", "Snow Moon", "Worm Moon", "Pink Moon", "Flower Moon", "Strawberry Moon", "Buck Moon", "Sturgeon Moon",
         "Corn Moon", "Hunter's Moon", "Beaver Moon", "Cold Moon"]
L_EN = {
    "ph": ["New moon", "First quarter", "Full moon", "Last quarter"],
    "ab": ["NM", "FQ", "FM", "LQ"],
    "mon": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "m3": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "wd": ["M", "T", "W", "T", "F", "S", "S"],
    "names": NAMES, "harvest": "Harvest Moon", "hunter": "Hunter's Moon", "bluename": "Blue Moon", "namecol": "Name",
    "big_l": "Full moons in ", "full": "full moons", "new": "new moons", "blue": "Blue moon (second full moon in a month)",
    "today": "Today", "ill": "lit", "month": "Month", "cal": "Moon calendar ",
    "stages": ["New moon", "Waxing crescent", "First quarter", "Waxing gibbous", "Full moon", "Waning gibbous", "Last quarter", "Waning crescent"],
    "err": "Year between 1900 and 2100.", "tzname": {"UTC": "UTC"},
    "note": "Clock time in the chosen zone, daylight saving included. Each square shows the moon at noon.",
    "ics": "moon-phases-", "lang": "EN",
}
TZS = [("local", "My time zone"), ("UTC", "UTC"), ("Europe/London", "London"), ("Europe/Dublin", "Dublin"), ("Europe/Paris", "Paris · Berlin · Madrid"),
       ("America/New_York", "New York · Toronto"), ("America/Chicago", "Chicago"), ("America/Denver", "Denver"), ("America/Phoenix", "Phoenix"),
       ("America/Los_Angeles", "Los Angeles · Vancouver"), ("America/Anchorage", "Anchorage"), ("Pacific/Honolulu", "Honolulu"),
       ("America/Mexico_City", "Mexico City"), ("America/Sao_Paulo", "São Paulo"), ("Africa/Johannesburg", "Johannesburg"),
       ("Asia/Kolkata", "India"), ("Asia/Singapore", "Singapore"), ("Asia/Tokyo", "Tokyo"), ("Australia/Perth", "Perth"),
       ("Australia/Sydney", "Sydney · Melbourne"), ("Pacific/Auckland", "Auckland")]


def blocks(ctx):
    ny, ldn = zoneinfo.ZoneInfo("America/New_York"), zoneinfo.ZoneInfo("Europe/London")
    fm = [t for q, t in A.phases(2027) if q == 2]
    r = lambda t, z: (t + dt.timedelta(seconds=30)).astimezone(z)  # noqa: E731
    rows = "".join(f"<tr><td>{NAMES[t.month - 1] if t.month not in (9, 10) else ('Harvest Moon' if t.month == 9 else NAMES[9])}</td>"
                   f"<td>{r(t, ldn):%a %d %b, %H:%M}</td><td>{r(t, ny):%a %d %b, %H:%M}</td></tr>" for t in fm)
    jun = next(t for t in fm if t.month == 6)
    jun_ny = r(jun, ny)
    return [
        ("Full moons in 2027", f"""
<p>2027 has <b>12 full moons</b>, one per month, starting with the Wolf Moon on 22 January and ending with the Cold Moon on
13 December. There is no blue moon this year: the last one was on 31 May 2026 and the next falls on 31 December 2028. The times
below are for London and New York; pick your own time zone above, or leave «My time zone» and the calendar follows your device.</p>
<table class="tbl"><thead><tr><th>Name</th><th>London</th><th>New York</th></tr></thead><tbody>{rows}</tbody></table>
<p>A phase is a single instant for the whole planet, so the date can change with the time zone: the June full moon happens at
{r(jun, dt.timezone.utc):%H:%M} UTC on 19 June, which is still {jun_ny:%d} June at {jun_ny:%H:%M} in New York.</p>"""),
        ("Where the moon names come from", """
<p>The monthly names (Wolf, Snow, Worm, Pink, Flower, Strawberry, Buck, Sturgeon, Corn, Hunter's, Beaver, Cold) are the ones
popularised by North American almanacs, drawn from Algonquian and colonial traditions. Two of them move with the equinox rather than
the calendar month: the Harvest Moon is the full moon closest to the September equinox, and the Hunter's Moon is the one after it.
In 2027 the Harvest Moon falls on 15 September, a week before the equinox, so October gets the Hunter's Moon. A Blue Moon here means
the second full moon in a calendar month, the most common modern use.</p>
<p>Other cultures name them differently, and supermoons (a full moon near perigee) are not marked, since the term has no agreed
threshold.</p>"""),
        ("How the phases are calculated", """
<p>New moon is the moment the Moon and the Sun share the same ecliptic longitude as seen from Earth; first quarter, full moon and
last quarter are 90, 180 and 270 degrees later. The calendar uses the series in chapter 49 of Jean Meeus' «Astronomical Algorithms»:
the mean phase plus more than 40 periodic terms for the eccentricity of both orbits, the Moon's inclination and the pull of the
planets, then the gap between dynamical time and clock time. Against the US Naval Observatory list for 2027, every one of the 49
phases agrees to within a minute.</p>
<p>Between phases, each day's moon is drawn by interpolating the phase angle at noon, so the lit percentage shown on hover is
approximate (one or two percent). From one new moon to the next takes 29.53 days on average, but single lunar months vary by several
hours because the Moon's orbit is elliptical.</p>"""),
    ]


FAQ = [
    ("How many full moons are there in 2027?",
     "Twelve: 22 January, 20 February, 22 March, 20 April, 20 May, 19 June, 18 July, 17 August, 15 September, 15 October, 14 November "
     "and 13 December (UTC dates)."),
    ("When is the next blue moon?",
     "On 31 December 2028, the second full moon of that month. The previous one was on 31 May 2026."),
    ("Is the waxing moon lit on the right or the left?",
     "In the northern hemisphere a waxing moon is lit on the right and a waning moon on the left. South of the equator it is the other "
     "way round, and near the equator the crescent looks more like a smile."),
    ("Why does my calendar show a different date for the full moon?",
     "Because the phase is one instant worldwide. A full moon at 00:44 UTC on 19 June 2027 is still the evening of 18 June in the "
     "Americas. Set the time zone above to match where you are."),
    ("What is the Harvest Moon in 2027?",
     "The full moon of 15 September 2027, the closest to the September equinox. The full moon of 15 October is the Hunter's Moon."),
]

TOOL = {
    "slug": "moon-phases-2027",
    "lang": "en",
    "twin": "calendario-lunar-2027",
    "cat": "sky",
    "cat_name": "Sun and moon",
    "icon": "moon",
    "order": 10,
    "name": "Moon phases 2027",
    "k": "lunar calendar full moon new moon names harvest blue moon",
    "title": "Moon Phases 2027: Full Moon Calendar with Times",
    "desc": "Every moon phase of 2027 with date and time in your time zone: full moons and their names, new moons, quarters, blue moons. Print or add to your calendar.",
    "h1": "Moon phases 2027",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ano", "type": "select", "label": "Year", "value": "2027", "options": [(str(y), str(y)) for y in range(2024, 2036)]},
        {"id": "zona", "type": "select", "label": "Time zone", "value": "local", "options": TZS},
    ],
    "js": make_js(L_EN),
    "css": A.MOON_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("US Naval Observatory · Phases of the Moon", "https://aa.usno.navy.mil/data/MoonPhases"),
                ("NASA · Moon phases", "https://science.nasa.gov/moon/moon-phases/")],
    "credits": [("Jean Meeus, Astronomical Algorithms, ch. 49 (formula reimplemented)", "published formula", "https://en.wikipedia.org/wiki/Jean_Meeus")],
    "related": ["easter-date", "day-of-the-week", "countdown"],
    "tests": [
        # US Naval Observatory 2027, UTC: first full moon 22 Jan 12:17, June 19 00:44
        ({"ano": "2027", "zona": "UTC"}, {"n.full": 12, "n.first": 122, "n.firsthm": "12:17", "n.blue": 0}),
        ({"ano": "2027", "zona": "America/New_York"}, {"n.firsthm": "07:17"}),
        ({"ano": "2028", "zona": "UTC"}, {"n.full": 13, "n.blue": 1}),
        ({"ano": "2099", "zona": "Pacific/Auckland"}, {"err": None}),
        ({"ano": "2101", "zona": "UTC"}, {"err": "Year between 1900 and 2100."}),
    ],
}
