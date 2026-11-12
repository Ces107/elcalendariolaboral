"""Stair calculator (English twin of escalera-huella-contrahuella): same compute, inches or cm, IRC or UK Part K limits."""
from herramientas.tools import _bricolaje as F
from herramientas.tools.escalera_huella_contrahuella import JS, CODES, NAMES_EN, stair

IRC = "https://codes.iccsafe.org/content/IRC2021P2/chapter-3-building-planning"
ADK = "https://www.gov.uk/government/publications/protection-from-falling-collision-and-impact-approved-document-k"


def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    H = 108 * 2.54
    n1, c1, t1, run1 = stair(H, 19.685, 25.4)
    n2, c2, t2, run2 = stair(260, 22, 22)
    return [
        ("How many steps and what size", f"""
<p>Divide the total rise by a comfortable riser of about 7 in (17.5 cm) and round to get the number of risers. Then set the
tread with Blondel's rule, <b>2 × riser + tread ≈ 25 in (63 cm)</b>, the length of an average stride. For a 9 ft (108 in)
floor-to-floor rise that gives {n1} risers of {n(c1 / 2.54, 2)} in and treads of {n(t1 / 2.54, 2)} in. The top floor acts as
the last step, so there are {n1 - 1} treads and the stair runs {n(run1 / 30.48, 2)} ft horizontally.</p>
<p>In metric, a 2.6 m rise in a UK house gives {n2} risers of {n(c2, 1)} cm and goings of {n(t2, 1)} cm, a run of
{n(run2 / 100, 2)} m. If the space is tight, enter the tread you can fit or a number of steps under More options and the
calculator checks whether the result still meets the code you selected.</p>"""),
        ("What the codes require", """
<p>The <b>International Residential Code</b> (IRC R311.7), used across most of the US, limits risers to 7¾ in and requires
treads of at least 10 in, measured nosing to nosing; one flight may rise at most 151 in between floors or landings. Risers in
a flight may not differ by more than ⅜ in. Many cities adopt local amendments, so check with your building department.</p>
<p>In England, <b>Approved Document K</b> sets for a private stair (inside a dwelling) a rise of 150 to 220 mm, a going of at
least 220 mm, 2R + G between 550 and 700 mm and a pitch of no more than 42°. Spain's CTE, the other option, asks for 13 to
18.5 cm risers and 28 cm treads in general-use stairs.</p>"""),
        ("Measuring correctly", """
<p>Measure the rise from finished floor to finished floor. If flooring is still to be laid at the bottom or top, add or subtract
its thickness: a small error is shared by all steps in theory, but in practice it lands on the first or last step, the classic
trip hazard. The stringer length shown is the diagonal from the bottom to the top tread, a starting point for cutting stock;
add the extra the stringer needs at each end.</p>"""),
    ]


FAQ = [
    ("What is the ideal rise and run for stairs?",
     "A rise of about 7 in (17.5 cm) and a run of 11 in (28 cm). That satisfies Blondel's rule and every common code."),
    ("How many steps for a 9 foot ceiling?",
     "With a 9 ft ceiling and a typical floor structure the rise is about 108 to 110 in: 15 or 16 risers of roughly 7 in."),
    ("What is the maximum riser height under the IRC?",
     "7¾ in (196 mm), with treads of at least 10 in (254 mm). A flight can rise at most 151 in before a landing is required."),
    ("What is the 2R + G rule?",
     "Twice the rise plus the going should fall between 550 and 700 mm in UK regulations, and close to 630 mm for a comfortable stair."),
    ("How much floor space does a staircase take?",
     "The number of treads times the tread depth: 15 treads of 10.5 in take about 13 ft, plus a landing at the bottom."),
]

TOOL = {
    "slug": "stair-calculator",
    "lang": "en",
    "twin": "escalera-huella-contrahuella",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "stairs",
    "order": 50,
    "name": "Stair calculator",
    "k": "stairs rise run riser tread stringer steps irc building code uk part k",
    "title": "Stair Calculator: Rise, Run, Risers and Treads",
    "desc": "Work out the number of steps, riser height, tread depth and stringer length for a staircase, checked against the IRC or UK Part K.",
    "h1": "Stair calculator",
    "updated": "2026-11-12",
    "data": {"codes": CODES, "names": NAMES_EN},
    "inputs": [
        {"id": "u", "type": "seg", "label": "Units", "value": "us", "options": [("us", "in"), ("m", "cm")]},
        {"id": "alto", "type": "number", "label": "Total rise", "value": "108", "step": "0.1"},
        {"id": "uso", "type": "seg", "label": "Code", "value": "irc", "options": [("irc", "IRC (US)"), ("uk", "UK Part K"), ("gen", "Spain CTE")]},
        {"id": "largo", "type": "number", "label": "Space for run", "value": "", "more": True},
        {"id": "huella", "type": "number", "label": "Tread", "value": "", "step": "0.1", "w": "s", "more": True},
        {"id": "np", "type": "number", "label": "Risers", "value": "", "w": "s", "more": True},
    ],
    "js": F.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("International Residential Code 2021, section R311.7 Stairways (ICC)", IRC),
                ("Approved Document K: protection from falling, collision and impact (GOV.UK)", ADK)],
    "related": ["concrete-calculator", "flooring-calculator", "tile-calculator", "wallpaper-calculator"],
    "tests": [
        ({}, {"n.n": 16, "n.ok": True}),
        ({"u": "m", "alto": "260", "uso": "uk"}, {"n.n": 15, "n.ok": True}),
        ({"alto": "160"}, {"n.land": True}),
        ({"huella": "9"}, {"n.ok": False}),
        ({"alto": "0"}, {"err": "Enter the total rise (floor to floor)."}),
    ],
}
