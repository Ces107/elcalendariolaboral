"""Party food and drink calculator (English twin of cantidades-fiesta): same compute, English menu (turkey, mains,
sides, rolls, appetizers) and US units next to metric."""
from herramientas.tools._cocina import CAT
from herramientas.tools.cantidades_fiesta import FOOD_EN, JS, T_EN, inputs

DGA = "https://www.dietaryguidelines.gov/"
FSIS_T = "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/poultry/lets-talk-turkey-roasting"

FAQ = [
    ("How much food per person for a party?",
     "For a sit-down dinner, plan about 8 oz (225 g) of boneless meat or fish per adult, or 1 lb (450 g) of whole bone-in turkey, plus "
     "about 5 oz (150 g) of each side dish and one or two rolls. Children count as half an adult. If it is drinks and nibbles instead, "
     "allow 3 appetizer pieces per person per hour, 5 if the food replaces dinner."),
    ("How many drinks per guest?",
     "A common planning rule is two drinks per adult in the first hour and one per hour after that. For 20 adults over 4 hours that is "
     "100 drinks, 110 with a 10 % margin: about 44 beers, 6 bottles of wine and 13 litres of soft drinks."),
    ("How many glasses in a bottle of wine or champagne?",
     "A standard 750 ml bottle pours five 5-oz (150 ml) glasses of wine, or about six 4-oz (125 ml) flutes of sparkling wine for a toast."),
    ("How much ice do I need for a party?",
     "About 1 lb (0.5 kg) per guest for drinks. If you also chill bottles in a tub or cooler, buy twice that."),
    ("How big a turkey for Thanksgiving?",
     "Plan 1 lb of whole turkey per person, more if you want leftovers. A 14 lb turkey feeds about 12 to 14. Remember thawing takes a "
     "day in the fridge for every 4 to 5 lb."),
]


def blocks(ctx):
    return [
        ("How the amounts are worked out", """
<p>Enter the number of adults and children, the kind of party and how long it lasts. Food is per person (a child counts as half an
adult) and drinks are per hour: <b>two drinks per adult in the first hour, then one per hour</b>, split 40 % beer, 25 % wine and 35 %
alcohol-free. Everything carries a 10 % margin you can change under «More options».</p>
<p>Example: Thanksgiving dinner for 12 adults and 4 kids over 5 hours, with turkey. People = 12 + 4 ÷ 2 = 14. Turkey: 1 lb × 14 ×
1.1 = <b>15.4 lb (7 kg)</b>. Each side dish: 150 g × 14 × 1.1 = 2.3 kg, about 5 lb. Drinks: 12 × (2 + 4) × 1.1 = 79 drinks for the
adults (32 beers, 4 bottles of wine) plus soft drinks for the kids, 23 litres of water and 9 kg of ice.</p>"""),
        ("Where the portions come from", """
<p>The turkey figure follows the USDA's long-standing advice of about one pound of whole turkey per person; boneless mains at
8 oz raw per adult and sides at roughly 5 oz are common catering rules of thumb rather than nutrition targets (the Dietary
Guidelines for Americans count a single protein serving as far less). The drink split and the appetizer counts are planning rules
too: if your crowd eats or drinks more, raise the margin.</p>
<p>Always have plenty of water and alcohol-free choices, and if guests are driving, tick «No alcohol» to see how much soft drink you
need when nobody drinks.</p>"""),
    ]


TOOL = {
    "slug": "party-food-calculator",
    "lang": "en",
    "twin": "cantidades-fiesta",
    "cat": CAT["en"][0], "cat_name": CAT["en"][1],
    "icon": "glass-champagne",
    "order": 110,
    "name": "Party food calculator",
    "k": "how much food per person guests drinks beer wine champagne ice thanksgiving turkey appetizers",
    "title": "Party Food and Drink Calculator per Guest",
    "desc": "How much food and drink to buy for a party: turkey or mains, sides, rolls, appetizers, beer, wine, champagne, soft drinks, water and ice per guest.",
    "h1": "Party food and drink calculator",
    "crumb": "Party food calculator",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": JS,
    "data": {"en": True, "t": T_EN, "food": FOOD_EN},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("USDA FSIS · Let's Talk Turkey", FSIS_T), ("Dietary Guidelines for Americans", DGA)],
    "related": ["roasting-time-calculator", "recipe-scaler-pan-size", "coffee-ratio-calculator", "homebrew-calculator"],
    "tests": [
        ({"adultos": "12", "ninos": "4", "horas": "5", "turkey": True, "plato": False}, {"n.turkey": 6985.44, "n.sides": 2310, "n.beer": 32, "n.water": 23, "n.ice": 9}),
        ({}, {"n.main": 4950, "n.rolls": 33}),
        ({"tipo": "coctel", "horas": "3", "adultos": "30"}, {"n.bocados": 495}),
    ],
}
