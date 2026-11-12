"""Tournament bracket generator (English twin of cuadro-torneo): same compute, English texts."""
from herramientas.tools import _deporte as D
from herramientas.tools.cuadro_torneo import JS, CSS

INPUTS = [
    {"id": "nombres", "type": "text", "label": "Players", "value": "Emma, Liam, Olivia, Noah, Ava, Jack, Mia, Leo, Grace, Sam", "w": "xl",
     "placeholder": "Emma, Liam, Olivia… or 16"},
    {"id": "orden", "type": "seg", "label": "Order", "value": "serie", "options": [("serie", "Seeded"), ("sorteo", "Random draw")]},
    {"id": "tercero", "type": "check", "label": "Third-place match", "value": False},
    {"id": "sorteo", "type": "number", "label": "Draw no.", "value": "", "more": True, "w": "s", "show": ("orden", ["sorteo"])},
    {"id": "g", "type": "text", "label": "Winners", "value": "", "more": True},
]

BLOCKS = [
    ("How a knockout bracket is built", """
<p>A single-elimination bracket needs a power-of-two number of slots: 4, 8, 16, 32 or 64. When fewer players enter, the
empty slots become <b>byes</b> and whoever is drawn against one goes straight through to round two. Ten players fill a
16-slot draw with 6 byes, so the first round has only 2 real matches and from the round of 16 on the draw is full. A
knockout always takes <b>players − 1 matches</b> (9 for 10 players), plus one if you play off for third place.</p>
<p>List the names in ranking order and keep "Seeded": the top two land in opposite halves and can only meet in the final,
seeds 3 and 4 go to opposite quarters, and the byes go to the highest seeds, exactly as in sanctioned events. "Random
draw" shuffles the names first; the draw number lets you reproduce the same bracket later.</p>"""),
    ("Where each seed goes", """
<p>Placement follows the classic rule: in every round, seed <i>s</i> faces the seed that adds up with it to the draw size
plus one. In a 16-player draw the first round reads 1 v 16, 8 v 9, 5 v 12, 4 v 13, 3 v 14, 6 v 11, 7 v 10 and 2 v 15 from top
to bottom. If every favourite wins, the quarter-finals are 1 v 8, 4 v 5, 3 v 6 and 2 v 7, and the semi-finals 1 v 4 and
2 v 3. With 10 entries the top six seeds get byes and the only first-round matches are 8 v 9 and 7 v 10.</p>"""),
    ("Recording results and sharing", """
<p>On the day, tap the winner of each match and the name moves into the next round; tap again to undo. Changing a result
clears the later matches that depended on it, so nobody advances by mistake. The results are saved inside the page link:
"Copy link" and send it to the group, and everyone sees the live bracket. "Print or PDF" gives you a clean sheet to pin on the
noticeboard or fill in by hand.</p>"""),
]

FAQ = [
    ("How many byes in a 12-player bracket?",
     "Four. The draw has 16 slots and 16 − 12 = 4, so the top four seeds go straight into the second round."),
    ("How many matches in a single-elimination tournament?",
     "One fewer than the number of players, because every match knocks out exactly one: 15 matches for 16 players, 31 for 32."),
    ("Why are seeds 1 and 2 in opposite halves?",
     "So the two favourites can only meet in the final. Tennis, padel, badminton and most federations place seeds this way."),
    ("Can I make a completely random bracket?",
     "Yes, choose \"Random draw\". Names are shuffled before they go into the slots, and the byes stay spread out so two byes never meet."),
    ("Do I need a third-place match?",
     "Only if you hand out prizes or medals to the top three. It is played between the two losing semi-finalists."),
]

TOOL = {
    "slug": "tournament-bracket-generator",
    "lang": "en",
    "twin": "cuadro-torneo",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "tournament",
    "order": 30,
    "name": "Bracket generator",
    "k": "tournament bracket single elimination knockout seeding byes printable draw",
    "title": "Tournament Bracket Generator with Byes (Printable)",
    "desc": "Make a single-elimination bracket for 3 to 64 players: proper seeding, byes, a third-place match and live results. Free and printable.",
    "h1": "Tournament bracket generator",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": D.make(JS, True),
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Single-elimination tournament · seeding and byes (Wikipedia)", "https://en.wikipedia.org/wiki/Single-elimination_tournament"),
                ("ITF · World Tennis Tour regulations (seeding)", "https://www.itftennis.com/en/about-us/governance/rules-and-regulations/")],
    "credits": [D.MULBERRY_EN],
    "related": ["round-robin-generator", "padel-americano-generator"],
    "tests": [
        ({}, {"n.size": 16, "n.byes": 6, "n.r1": [["Emma", "-"], ["Leo", "Grace"], ["Ava", "-"], ["Noah", "-"]]}),
        ({"nombres": "32"}, {"n.size": 32, "n.matches": 31}),
        ({"nombres": "3", "g": "022"}, {"n.champ": "Player 3", "n.size": 4, "n.byes": 1}),
        ({"nombres": "1"}, {"err": "Enter 3 to 64 names separated by commas, or just how many players."}),
    ],
}
