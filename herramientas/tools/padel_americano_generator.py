"""Padel americano / mexicano generator (English twin of americano-padel): same compute, English texts."""
from herramientas.tools import _deporte as D
from herramientas.tools.americano_padel import JS, CSS

INPUTS = [
    {"id": "modo", "type": "seg", "label": "Format", "value": "am", "options": [("am", "Americano"), ("mx", "Mexicano")]},
    {"id": "jug", "type": "text", "label": "Players", "value": "Emma, Liam, Olivia, Noah, Ava, Jack, Mia, Leo", "w": "xl",
     "placeholder": "Emma, Liam, Olivia… or 12"},
    {"id": "pistas", "type": "number", "label": "Courts", "value": "2", "w": "s"},
    {"id": "rondas", "type": "number", "label": "Rounds", "value": "7", "w": "s"},
    {"id": "pts", "type": "seg", "label": "Points", "value": "24",
     "options": [("16", "16"), ("21", "21"), ("24", "24"), ("32", "32"), ("0", "Free")]},
    {"id": "sorteo", "type": "number", "label": "Variant", "value": "", "more": True, "w": "s"},
    {"id": "sc", "type": "text", "label": "Scores", "value": "", "more": True},
]

BLOCKS = [
    ("How the americano rotation works", """
<p>Type the players' names, the number of courts and how many rounds you have time for. The generator gives everyone a
new partner every round and spreads the opponents as evenly as it can. With 8 players, 2 courts and 7 rounds it finds the
perfect schedule: each player partners each of the other seven exactly once and faces every one of them twice. With
more players than court places (10 players on 2 courts, say) the extra players sit out in turn, and nobody sits out a second
time until everyone has sat out once.</p>
<p>In an americano <b>every match is played to a fixed number of points</b>, usually 16, 21, 24 or 32. Every point counts,
so a 15-9 win on a 24-point match gives each winner 15 and each loser 9. There is no winning team at the end: the player
with the most points wins. That is why you only need to type one side of each score: the other side fills in (in grey),
and the ranking updates with points, matches played, wins and points per match.</p>"""),
    ("Americano or mexicano", """
<p>An <b>americano</b> is fixed from the start, so you can print every round before the first serve and pin it up at the
club. A <b>mexicano</b> only fixes round one, taken in the order you list the names (put them roughly strongest to
weakest). Each later round is built from the live ranking: the top four play on court 1, fifth to eighth on court 2 and so
on, with 1st and 4th against 2nd and 3rd unless that pairing has already happened. Matches get closer as the session goes
on, which is the whole point of the format.</p>
<p>A worked example with the sample names, to 24 points. Mexicano round one puts Emma and Noah against Liam and Olivia on
court 1, and Ava and Leo against Jack and Mia on court 2. If Emma and Noah win 15-9 and Ava and Leo win 13-11, the table
reads Emma and Noah 15, Ava and Leo 13, Jack and Mia 11, Liam and Olivia 9. Round two sends the top four to court 1 (Emma
and Leo against Noah and Ava) and the bottom four to court 2 (Jack and Olivia against Mia and Liam).</p>"""),
    ("A scoreboard you can share and print", """
<p>The scores are stored in the page link itself: there is no account and no server. Press "Copy link" and drop it in
the group chat, and anyone who opens it sees the same draw, the scores so far and the ranking. Send it again after the
last round. "Print or PDF" gives you a sheet with every round and empty score boxes for pen-and-paper clubs. Under "More
options", "Variant" reshuffles the draw while keeping the same number of rounds, handy when two friends would rather not
be paired.</p>"""),
]

FAQ = [
    ("How many rounds does an 8-player americano need?",
     "Seven, so that every player partners each of the other seven once. With 12 players on 3 courts you need 11, and with 16 on 4 courts "
     "15. Short on court time? Play fewer rounds; the generator still avoids repeated partners."),
    ("How many points per match?",
     "24 points (about 15 minutes) and 32 points (about 20) are the most common. 16 or 21 suit big groups or short bookings. Choose "
     "\"Free\" if you count games or play against the clock, and type both scores."),
    ("What if the numbers don't fit the courts?",
     "Each round four players use each court and the rest sit out. Rests rotate, so by the end the gap between the most and least rested "
     "player is at most one round. Use the \"Avg\" column to compare players on points per match."),
    ("How are ties broken?",
     "First on total points, then on matches won, then on the order the names were entered. Many clubs settle a tie for first with a "
     "single golden point instead."),
    ("Do I lose the scores if I close the page?",
     "Not if you keep or share the link: the scores live inside it. Changing the player list rebuilds the draw and old scores stop "
     "matching, so lock the list before the first round."),
    ("Can I fix an old score in a mexicano?",
     "Yes, but the later rounds are rebuilt from the corrected ranking, so pairings of rounds already played may change. Correct only "
     "the round in progress."),
]

TOOL = {
    "slug": "padel-americano-generator",
    "lang": "en",
    "twin": "americano-padel",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "ball-tennis",
    "order": 10,
    "name": "Padel americano",
    "k": "americano mexicano padel tournament rotation partners courts scoreboard ranking",
    "title": "Padel Americano Generator: Rotations and Live Scores",
    "desc": "Free padel americano and mexicano generator: fair partner and court rotation for 4 to 24 players, live scores, ranking and a printable sheet.",
    "h1": "Padel americano generator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Social golfer problem · CSPLib prob010", "https://www.csplib.org/Problems/prob010/"),
                ("Whist tournament (every player partners every other once) · Wolfram MathWorld", "https://mathworld.wolfram.com/WhistTournament.html")],
    "credits": [D.MULBERRY_EN],
    "related": ["round-robin-generator", "tournament-bracket-generator"],
    "tests": [
        ({}, {"n.players": 8, "n.rounds": 7, "n.rep": 0}),
        ({"modo": "mx", "sc": "15-9,13"}, {"n.rounds": 2, "n.c1": ["Emma", "Leo", "Noah", "Ava"], "n.leader": "Emma"}),
        ({"jug": "16", "pistas": "4", "rondas": "15"}, {"n.rep": 0, "n.courts": 4}),
        ({"jug": "6", "pistas": "3", "rondas": "5", "pts": "0", "sc": "6-3"}, {"n.courts": 1, "n.top": 6}),
        ({"rondas": "0"}, {"err": "Enter how many rounds (1 to 40)."}),
    ],
}
