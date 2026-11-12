"""Round robin schedule generator (English twin of liguilla-round-robin): same compute, English texts."""
from herramientas.tools import _deporte as D
from herramientas.tools.liguilla_round_robin import JS, CSS

INPUTS = [
    {"id": "equipos", "type": "text", "label": "Teams", "value": "Reds, Blues, Greens, Yellows, Whites, Blacks", "w": "xl",
     "placeholder": "Reds, Blues, Greens… or 10"},
    {"id": "vueltas", "type": "seg", "label": "Legs", "value": "1", "options": [("1", "Single"), ("2", "Home and away")]},
    {"id": "inicio", "type": "date", "label": "First round", "value": ""},
    {"id": "cada", "type": "number", "label": "Every", "value": "7", "unit": "days", "w": "s"},
    {"id": "sorteo", "type": "number", "label": "Draw no.", "value": "", "more": True, "w": "s"},
]

BLOCKS = [
    ("How many rounds and matches", """
<p>In a round robin every team plays every other team once. With <b>n</b> teams that is <b>n × (n − 1) / 2 matches</b>,
spread over <b>n − 1 rounds</b> when n is even, or <b>n rounds</b> when n is odd, because one team has a bye each round.
Six teams play 15 matches in 5 rounds; seven teams play 21 matches in 7 rounds and each sits out once. A double round
robin (home and away) doubles everything: 30 matches over 10 rounds for six teams, with the second half repeating the
first in the same order and the venues swapped.</p>
<p>Type the names separated by commas, or just the number of teams, and the fixture list appears. Add the date of the
first round to date every round (weekly by default) and download an .ics file that drops each round into your phone's
calendar with the matches in the description. "Print or PDF" gives a sheet with a blank box after each match for the
score.</p>"""),
    ("A six-team example", """
<p>With Reds, Blues, Greens, Yellows, Whites and Blacks, round one is Reds v Blacks, Blues v Whites and Yellows v Greens
(the first-named team is at home). In round two Reds stay put while everyone else rotates one place: Whites v Reds,
Blacks v Yellows and Greens v Blues. Five rounds later every pair has met exactly once. Start on Saturday 9 January 2027
with a round every seven days and the last round falls on 6 February.</p>"""),
    ("The circle method behind it", """
<p>The schedule uses the circle method that leagues and chess federations have relied on for over a century: write the
teams in two rows, keep the first one fixed and rotate everybody else one position each round, like the hands of a clock.
With an odd number of teams a "bye" slot joins the rotation, so each team rests exactly once. Printed Berger tables,
named after the Austrian chess organiser Johann Berger, are the same pattern.</p>
<p>Home and away are balanced too. Every team gets half its matches at home (give or take one) and the number of times a
team has two home or two away games in a row is the theoretical minimum, n − 2 across the whole competition. For a
different running order, type a number in "Draw no." under "More options": the teams are shuffled before the rotation, and
the same number always gives the same schedule.</p>"""),
]

FAQ = [
    ("How many games in a round robin of 8 teams?",
     "28 matches over 7 rounds, four matches per round. Home and away doubles it to 56 matches over 14 rounds."),
    ("What happens with an odd number of teams?",
     "One team has a bye each round and every team gets exactly one bye per leg. Five teams play 10 matches over 5 rounds, two matches a round."),
    ("How is the second leg ordered?",
     "Same pairings in the same order as the first leg, with home and away swapped, which is how most leagues do it."),
    ("Can I use it for tennis, pickleball, five-a-side or board games?",
     "Yes. Enter players, doubles pairs or teams. If you have fewer courts or tables than matches, play each round in several slots."),
    ("Can I change the order of the fixtures?",
     "Enter a number in \"Draw no.\" and the teams are shuffled before the schedule is built. Keep the number and the schedule stays the same."),
]

TOOL = {
    "slug": "round-robin-generator",
    "lang": "en",
    "twin": "liguilla-round-robin",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "calendar-week",
    "order": 20,
    "name": "Round robin generator",
    "k": "round robin schedule league fixtures home away berger circle method tournament",
    "title": "Round Robin Generator: League Schedule Maker",
    "desc": "Make a round robin schedule for any league: rounds, byes, home and away, dates per round and an .ics calendar. Free and printable.",
    "h1": "Round robin schedule generator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Round-robin tournament · circle method and Berger tables (Wikipedia)", "https://en.wikipedia.org/wiki/Round-robin_tournament#Scheduling_algorithm")],
    "credits": [("Circle method / Berger tables (Johann Berger)", "public domain (method)", "https://en.wikipedia.org/wiki/Round-robin_tournament#Berger_tables"),
                D.MULBERRY_EN],
    "related": ["padel-americano-generator", "tournament-bracket-generator"],
    "tests": [
        ({}, {"n.rounds": 5, "n.matches": 15, "n.breaks": 4, "n.first": ["Reds", "Blacks"]}),
        ({"equipos": "5"}, {"n.rounds": 5, "n.matches": 10, "n.bye": "Team 1"}),
        ({"vueltas": "2", "inicio": "2027-01-09", "cada": "14"}, {"n.rounds": 10, "n.last": "2027-05-15"}),
        ({"equipos": "2"}, {"err": "Enter 3 to 40 team or player names separated by commas, or just how many there are."}),
    ],
}
