"""Animal gestation calculator (English twin of gestacion-animal): same species data and compute, English strings."""
from herramientas.tools.gestacion_animal import DONKEY, MSD_EN, NMSU, SPECIES, make_js, species_options

L_EN = {
    "lang": "en",
    "mon": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    "wd": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "de": " ", "label": "Due date", "between": "Normal window: ", "and": " to ",
    "avg": "Average gestation", "range": "Usual range", "days": " days", "from": "Mating",
    "prep": "Get the birthing area ready", "today": "Today", "dayn": "day ", "left": "", "togo": " to go", "past": "past the due date",
    "late": "past the usual range: call your vet", "err": "Enter the mating date.",
    "note": "Averages from veterinary references: every animal, breed and litter varies. Not a substitute for a vet check.",
    "ics": "due-date.ics", "sum": "Due date", "win": "Birth window",
}


def blocks(ctx):
    rows = "".join(f"<tr><td>{en}</td><td class=\"num\">{a} days</td><td class=\"num\">{lo}–{hi} days</td><td class=\"num\">{a / 7:.1f} weeks</td></tr>"
                   for k, a, lo, hi, _, _, en, _ in SPECIES)
    return [
        ("How long each animal is pregnant", f"""
<p>The due date is the mating (or insemination) date plus the average gestation of the species. A dog whelps about <b>63
days</b> after ovulation, a cat at around 65 days, a rabbit after a month (31 days), a sow at 114 days (the old «three months, three
weeks and three days» rule), a ewe at about 147, a goat at 150, a cow at <b>283</b> and a mare at around 340 days, roughly eleven
months. Donkeys take the longest of the farm animals: a year on average, and a healthy jenny can go past fourteen months.</p>
<table class="tbl"><thead><tr><th>Species</th><th>Average</th><th>Usual range</th><th>Weeks</th></tr></thead><tbody>{rows}</tbody></table>
<p>The window matters as much as the average. In dogs, counted from the mating rather than from ovulation, birth can come anywhere
from day 58 to day 72, because sperm can wait several days in the tract until she ovulates. With more than one mating, count the
start of the window from the first and the end from the last.</p>"""),
        ("Worked example", """
<p>A cow inseminated on <b>1 December 2026</b> is due on <b>10 September 2027</b>, 283 days later, with the normal window running
from 6 to 19 September. A bitch mated on the same day would whelp around 2 February 2027, usually between 28 January and 11
February, so the whelping box should be ready by 21 January, a week before the window opens. Press «Download .ics» to put the due date
and the window in Google Calendar, Outlook or your phone.</p>"""),
        ("Where the numbers come from", f"""
<p>The averages are those of the <a href="{MSD_EN}" rel="noopener">MSD Veterinary Manual</a> table of approximate gestation
periods, with the cow and mare figures used by <a href="{NMSU}" rel="noopener">New Mexico State University's Guide B-130</a> (283
and 340 days). The ranges are the usual spread in the veterinary literature; the donkey's (11 to 14.5 months) is the one given by
<a href="{DONKEY}" rel="noopener">The Donkey Sanctuary</a>. Breed shifts the date by days (large beef breeds and some bulls lengthen
it), small litters run a little longer than big ones, and mares bred in spring tend to foal a few days earlier than those bred in
summer.</p>
<p>Treat the date as a planning aid, not a diagnosis. If labour starts far too early, goes past the range or the female shows signs
of distress, call your vet.</p>"""),
    ]


FAQ = [
    ("How long is a dog pregnant?",
     "About 63 days, nine weeks, from ovulation. Counted from the mating, whelping can fall anywhere from day 58 to day 72. Small breeds "
     "and big litters tend to whelp a little earlier."),
    ("How many months is a cow pregnant?",
     "Just over nine months: 283 days on average, much like a human. Depending on breed, 279 to 292 days."),
    ("How long is a horse pregnant?",
     "About 11 months (340 days on average), with normal foalings from 320 to 370 days. A donkey takes longer, around a year."),
    ("How long is a pig pregnant?",
     "114 days on average, the «three months, three weeks, three days» rule. 111 to 117 days is normal."),
    ("How long is a rabbit pregnant?",
     "About 31 days after mating, between 28 and 35. If a doe reaches day 32 without kindling, it is worth calling the vet."),
    ("How do I know she is really pregnant?",
     "The date is just arithmetic. A vet confirms pregnancy by ultrasound or a blood test: in dogs from 3 to 4 weeks, in cattle from "
     "about 30 days after insemination."),
]

TOOL = {
    "slug": "animal-gestation-calculator",
    "lang": "en",
    "twin": "gestacion-animal",
    "cat": "animals",
    "cat_name": "Animals and farm",
    "icon": "pig",
    "order": 20,
    "name": "Animal gestation calculator",
    "k": "dog cat rabbit cow horse donkey sheep goat pig due date pregnancy whelping calving foaling lambing",
    "title": "Animal Gestation Calculator: Due Date by Species",
    "desc": "Due date for a dog, cat, rabbit, cow, horse, donkey, sheep, goat or pig from the mating date, with the normal birth window and a calendar file.",
    "h1": "Animal gestation calculator",
    "crumb": "Animal gestation",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "especie", "type": "select", "label": "Species", "value": "perra", "options": species_options("en")},
        {"id": "fecha", "type": "date", "label": "Mating", "value": "2026-11-12", "today": True, "min": "2000-01-01", "max": "2035-12-31"},
    ],
    "js": make_js(L_EN),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("MSD Veterinary Manual · approximate gestation periods", MSD_EN),
                ("New Mexico State University · Guide B-130", NMSU),
                ("The Donkey Sanctuary · mares and foals", DONKEY)],
    "related": ["egg-incubation-calculator", "dog-cat-age-calculator"],
    "tests": [
        ({"especie": "vaca", "fecha": "2026-12-01"}, {"n.due": "2027-09-10", "n.lo": "2027-09-06"}),
        ({"especie": "yegua", "fecha": "2027-04-15"}, {"n.due": "2028-03-20", "n.days": 340}),
        ({"especie": "coneja", "fecha": "2027-02-01"}, {"n.due": "2027-03-04"}),
        ({"especie": "gata", "fecha": ""}, {"err": "Enter the mating date."}),
    ],
}
