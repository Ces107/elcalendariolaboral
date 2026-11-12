"""Dog and cat age in human years (English twin of edad-perro-gato): same compute, English strings, pounds and kilos."""
from herramientas.tools.edad_perro_gato import AAFP, AKC, WANG, make_js

L_EN = {
    "label": "Human age", "years": " years", "y1": " year", "rule": "Vet rule of thumb", "epi": "Epigenetic clock (Wang 2020)",
    "na": "from age 1 only", "stage": "Life stage", "senior": "Senior from", "err": "Enter the age.", "neg": "Age cannot be negative.",
    "max": "Maximum age: 30 years.", "dog": "Dog", "cat": "Cat", "of": ", ",
    "st_dog": ["Puppy", "Adult", "Senior"], "st_cat": ["Kitten", "Young adult", "Mature adult", "Senior"],
    "note": "A rough equivalence: breed, weight and health change real ageing a lot.",
    "mo": " months", "sz": {"p": "small", "m": "medium", "g": "large", "x": "giant"},
}


def blocks(ctx):
    return [
        ("How old is my dog or cat in human years?", """
<p>The old «one dog year equals seven human years» rule does not hold up: dogs and cats grow up very fast and then age more
slowly. The rule vets use is <b>15 human years for the first year</b> and <b>24 by the second birthday</b>. After that, each year adds
about <b>4 human years for cats and small dogs</b> (under 22 lb), 5 for medium dogs, 6 for large and 7 for giant breeds, because big
dogs have shorter lives. A medium-sized dog of 5 is roughly 39 in human years; a 10-year-old cat, about 56.</p>
<p>For dogs the calculator also shows the «epigenetic clock» from a University of California San Diego study (Wang and colleagues,
2020), which matched DNA methylation changes in dogs and people: <b>human age = 16 × ln(dog age) + 31</b>. It runs older in the early
years (a one-year-old dog is like a 31-year-old person) and younger in old age.</p>"""),
        ("Examples", """
<ul>
<li><b>Kitten of 6 months</b>: about 10 in human years, a cat in its early teens.</li>
<li><b>Cat of 14</b>: 24 + 4 × 12 = <b>72</b>, and a senior since 10 by the feline life-stage guidelines.</li>
<li><b>Yorkshire terrier of 10</b> (small): 24 + 4 × 8 = 56; on the epigenetic formula, 16 × ln(10) + 31 = 68.</li>
<li><b>Labrador of 8</b> (large): 24 + 6 × 6 = 60, a senior since 6.</li>
<li><b>Great Dane of 7</b> (giant): 24 + 7 × 5 = 59.</li>
</ul>"""),
        ("Sources and limits", f"""
<p>The 15, 9 and then about 5 years rule is the one the <a href="{AKC}" rel="noopener">American Kennel Club</a> quotes from the
American Veterinary Medical Association for a medium-sized dog; the size adjustment (4 to 7 years per year) is a simplified reading
of the vets' chart by weight. The epigenetic formula is from <a href="{WANG}" rel="noopener">Wang et al., Cell Systems (2020)</a>,
built on 104 Labrador retrievers, so it fits very small or very large breeds less well and its authors do not apply it to puppies.
Cat life stages follow the <a href="{AAFP}" rel="noopener">2021 AAHA/AAFP Feline Life Stage Guidelines</a>: kitten up to 1, young
adult 1 to 6, mature adult 7 to 10 and senior from 10.</p>
<p>Use it to get a feel for when to move to twice-yearly senior check-ups or a senior diet; real health depends on breed, weight,
neutering and lifestyle.</p>"""),
    ]


FAQ = [
    ("Is one dog year really seven human years?",
     "No. The first year is worth about 15 human years and the second about 9 more. After that it is 4 to 7 years per year depending on size."),
    ("How old is a 15-year-old cat in human years?",
     "About 76: 24 at two, plus 4 for each year after that (24 + 4 × 13)."),
    ("When is a dog considered senior?",
     "Small and medium dogs at around 7; large and giant breeds earlier, at 5 or 6, because they age faster."),
    ("What is the logarithm formula for dog years?",
     "It comes from a 2020 study that compared DNA methylation in Labradors and people: 16 × ln(age) + 31. It applies from age one; a "
     "2-year-old dog comes out at 42 and a 12-year-old at 71."),
    ("How long do cats live?",
     "Indoor cats usually reach 12 to 18 and many pass 20. Cats that roam outdoors live noticeably shorter lives on average."),
]

TOOL = {
    "slug": "dog-cat-age-calculator",
    "lang": "en",
    "twin": "edad-perro-gato",
    "cat": "animals",
    "cat_name": "Animals and farm",
    "icon": "paw",
    "order": 40,
    "name": "Dog and cat age",
    "k": "dog years cat years human years pet age calculator senior puppy kitten",
    "title": "Dog and Cat Age Calculator: Pet Years to Human Years",
    "desc": "Convert your dog's or cat's age to human years by size, with the vets' rule of thumb and the 2020 epigenetic formula, plus its life stage.",
    "h1": "Dog and cat age in human years",
    "crumb": "Dog and cat age",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "animal", "type": "seg", "label": "Pet", "value": "perro", "options": [("perro", "Dog"), ("gato", "Cat")]},
        {"id": "anos", "type": "number", "label": "Years", "value": 5, "w": "s"},
        {"id": "meses", "type": "number", "label": "Months", "value": "", "w": "s"},
        {"id": "tam", "type": "select", "label": "Size", "value": "m", "show": ("animal", ["perro"]),
         "options": [("p", "Small (< 22 lb · 10 kg)"), ("m", "Medium (22-55 lb)"), ("g", "Large (55-100 lb)"), ("x", "Giant (> 100 lb · 45 kg)")]},
    ],
    "js": make_js(L_EN),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("American Kennel Club · How to calculate dog years to human years (AVMA)", AKC),
                ("Wang et al., Cell Systems 2020 · dog-to-human epigenetic clock", WANG),
                ("AAHA/AAFP · Feline Life Stage Guidelines 2021", AAFP)],
    "credits": [("Wang T. et al. (2020), formula 16·ln(age)+31 (reimplemented)", "published formula", WANG)],
    "related": ["animal-gestation-calculator", "egg-incubation-calculator", "age-calculator"],
    "tests": [
        ({"animal": "perro", "anos": "5", "tam": "m"}, {"n.h": 39, "n.epi": 56.75}),
        ({"animal": "perro", "anos": "8", "tam": "g"}, {"n.h": 60}),
        ({"animal": "gato", "anos": "1", "meses": "6"}, {"n.h": 21}),
        ({"animal": "gato", "anos": "40"}, {"err": "Maximum age: 30 years."}),
    ],
}
