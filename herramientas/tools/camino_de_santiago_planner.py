"""Camino de Santiago stage planner (English twin of etapas-camino-santiago): same data and compute, English texts."""
from herramientas.tools import _deporte as D
from herramientas.tools.etapas_camino_santiago import JS, CSS, DATA, GRONZE, inputs, total

MI = 1.609344


def blocks(ctx):
    fr = total("fr")
    sarria = total("fr", "Sarria")
    tui = total("pt", "Tui")
    porto = total("pt", "Porto")
    irun = total("no", "Irún")
    ovi = total("pr", "Oviedo")
    n = lambda x: D.n(x, 0, True)  # noqa: E731
    return [
        ("How the planner splits your days", f"""
<p>Pick a route and a starting town, type how far you want to walk each day and the date you set off. The planner starts
from the classic stages of each Camino and, day by day, picks the stopping point that best fits your daily distance while
keeping your running total on track: strong walkers get two short stages merged, gentler walkers get long stages cut into
equal parts, with the approximate kilometre where you should look for a bed. "Rest every" adds a day off after a set number
of walking days, in whichever town you have reached. Print the plan or download it as an .ics file for your phone's
calendar.</p>
<p>A worked example: the full Camino Francés from Saint-Jean-Pied-de-Port is about {n(fr)} km ({n(fr / MI)} miles) over
33 classic stages. At 22 km (14 miles) a day the plan follows those stages almost exactly, 33 walking days, or 37 with a rest
day every week. At 15 km a day it takes 51 days, with many stages split in two; at 30 km, 26 days. From Sarria it is
{n(sarria)} km, the most popular minimum for the Compostela, usually walked in five days.</p>"""),
        ("The four routes and their distances", f"""
<p>The <b>Camino Francés</b> is the busiest route and has the most services. The central <b>Portuguese Way</b> comes up
from Lisbon through Coimbra and Porto: {n(porto)} km from Porto and {n(tui)} km from Tui, just over the border in Galicia and
the classic start for the last 100 km. The <b>Camino del Norte</b> follows the Bay of Biscay coast from Irún ({n(irun)} km) and
joins the Francés at Arzúa; it is hillier and has fewer albergues. The <b>Primitivo</b>, the oldest route, leaves Oviedo,
crosses the Asturian mountains and meets the Francés at Melide: about {n(ovi)} km with big daily climbs. The Primitivo plan
takes the Hospitales stage (the bad-weather alternative via Pola de Allande adds 4.5 km) and the Norte uses the official
variants.</p>"""),
        ("The Compostela and the 100 km minimum", """
<p>To receive the Compostela certificate at the Pilgrim Office you must walk (or ride a horse) at least the <b>last 100
km</b> into Santiago, or cycle the last 200 km, and collect at least two dated stamps a day in your credential over that final
stretch. The planner warns you when your chosen start falls short. Stage distances are approximate and come from the
Gronze guide; expect a kilometre or two of difference depending on where you sleep and on any diversions.</p>"""),
    ]


FAQ = [
    ("How many days does the Camino Francés take?",
     "30 to 35 walking days at 22 to 25 km (14 to 15 miles) a day from Saint-Jean-Pied-de-Port, plus any rest days. From Sarria, about five days."),
    ("How far do pilgrims walk each day?",
     "Most walk 20 to 25 km (12 to 15 miles). If you are not used to it, keep the first days to 15 to 18 km: blisters and tendinitis come from pushing early."),
    ("Where do I start to earn the Compostela?",
     "Anywhere 100 km or more from Santiago on foot: Sarria on the Francés, Tui on the Portuguese Way or Vilalba on the Norte. On the Primitivo, Lugo is right on the limit; O Cádavo gives you a margin."),
    ("How often should I take a rest day?",
     "Many pilgrims rest one day a week, often in a city worth seeing: Pamplona, Burgos or León on the Francés."),
    ("Are the distances exact?",
     "They are the stage distances published by the Gronze guide. Real distances shift a little with your choice of lodging and with diversions; allow about 5%."),
    ("What if a stage is longer than I want to walk?",
     "The planner cuts it into equal parts and gives the approximate kilometre. Look for lodging near that point in a Camino guide or app."),
]

TOOL = {
    "slug": "camino-de-santiago-planner",
    "lang": "en",
    "twin": "etapas-camino-santiago",
    "cat": D.CAT_EN[0], "cat_name": D.CAT_EN[1],
    "icon": "walk",
    "order": 80,
    "name": "Camino stage planner",
    "k": "camino de santiago stages planner french way portuguese way norte primitivo km per day compostela pilgrim",
    "title": "Camino de Santiago Stage Planner: Plan Your Own Stages",
    "desc": "Plan your Camino de Santiago stages (Francés, Portuguese, Norte or Primitivo) by km per day, with rest days, dates and an .ics calendar.",
    "h1": "Camino de Santiago stage planner",
    "updated": "2026-11-12",
    "inputs": inputs("en"),
    "js": D.make(JS, True),
    "data": DATA,
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Gronze · stages of the Francés, Portuguese, Norte and Primitivo routes (Nov 2026)", GRONZE),
                ("Pilgrim's Office · Compostela requirements", "https://oficinadelperegrino.com/en/pilgrimage/the-compostela/")],
    "credits": [("Stage distances: Gronze.com (reference data, cited)", "factual data with citation", GRONZE)],
    "related": ["hiking-time-calculator", "running-pace-calculator"],
    "tests": [
        ({"inicio": "2027-05-01"}, {"n.km": 763.7, "n.walk": 33}),
        ({"inicio": "2027-05-01", "ruta": "no", "dno": "Irún", "kmd": "25"}, {"n.km": 820.9}),
        ({"inicio": "2027-05-01", "ruta": "pt", "dpt": "Porto", "desc": "5"}, {"n.km": 241.4}),
        ({"inicio": "2027-05-01", "kmd": "60"}, {"err": "Enter how many km a day you plan to walk (5 to 50)."}),
    ],
}
