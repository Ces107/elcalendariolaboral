"""Edad de perro o gato en años humanos: the veterinary rule (15 the first year, 24 at two, then 4-7 a year by size)
and, for dogs, the epigenetic formula of Wang et al. 2020 (16 ln(age) + 31). English twin: dog_cat_age_calculator.py."""
import json

AKC = "https://www.akc.org/expert-advice/health/how-to-calculate-dog-years-to-human-years/"
WANG = "https://doi.org/10.1016/j.cels.2020.06.006"
AAFP = "https://catvets.com/life-stage"

# dog sizes: key, human years added per year after the second
SIZES = [("p", 4), ("m", 5), ("g", 6), ("x", 7)]

L_ES = {
    "label": "Edad humana", "years": " años", "y1": " año", "rule": "Regla veterinaria", "epi": "Reloj epigenético (Wang 2020)",
    "na": "solo desde 1 año", "stage": "Etapa", "senior": "Senior desde", "err": "Escribe la edad.", "neg": "La edad no puede ser negativa.",
    "max": "Edad máxima: 30 años.", "dog": "Perro", "cat": "Gato", "of": " de ",
    "st_dog": ["Cachorro", "Adulto", "Senior"], "st_cat": ["Gatito", "Adulto joven", "Adulto maduro", "Senior"],
    "note": "Es una equivalencia orientativa: la raza, el peso y la salud cambian mucho el envejecimiento real.",
    "mo": " meses", "sz": {"p": "pequeño", "m": "mediano", "g": "grande", "x": "gigante"},
}


def make_js(L):
    return r"""
function (v, H, C) {
  var L = """ + json.dumps(L, ensure_ascii=False) + r""", K = """ + json.dumps(dict(SIZES)) + r""";
  var y = isNaN(v.anos) ? 0 : v.anos, m = isNaN(v.meses) ? 0 : v.meses;
  if (isNaN(v.anos) && isNaN(v.meses)) return { err: L.err };
  if (y < 0 || m < 0) return { err: L.neg };
  var a = y + m / 12;
  if (a > 30) return { err: L.max };
  if (a <= 0) return { err: L.err };
  var dog = v.animal !== 'gato', k = K[v.tam] || 5, h;
  function lerp(pts, x) { for (var i = 1; i < pts.length; i++) if (x <= pts[i][0]) { var p = pts[i - 1], q = pts[i]; return p[1] + (q[1] - p[1]) * (x - p[0]) / (q[0] - p[0]); } return pts[pts.length - 1][1]; }
  if (dog) h = a <= 2 ? lerp([[0, 0], [1, 15], [2, 24]], a) : 24 + k * (a - 2);
  else h = a <= 2 ? lerp([[0, 0], [1 / 12, 1], [0.25, 4], [0.5, 10], [1, 15], [1.5, 21], [2, 24]], a) : 24 + 4 * (a - 2);
  var epi = dog && a >= 1 ? 16 * Math.log(a) + 31 : null, sen = dog ? (k >= 6 ? 6 : 7) : 10, st;
  if (dog) st = a < 1 ? L.st_dog[0] : a < sen ? L.st_dog[1] : L.st_dog[2];
  else st = a < 1 ? L.st_cat[0] : a < 7 ? L.st_cat[1] : a < 10 ? L.st_cat[2] : L.st_cat[3];
  var age = (y ? y + (y === 1 ? L.y1 : L.years) : '') + (m ? (y ? ' ' : '') + H.num(m, m % 1 ? 1 : 0) + L.mo : '');
  var rows = [[L.rule, H.num(h, 0) + L.years]];
  if (dog) rows.push([L.epi, epi === null ? L.na : H.num(epi, 0) + L.years]);
  rows.push([L.stage, st], [L.senior, sen + L.years, 'sub']);
  return { label: (dog ? L.dog + ' ' + L.sz[v.tam || 'm'] : L.cat) + L.of + age, big: '≈ ' + H.num(h, 0) + L.years, rows: rows, note: L.note,
    n: { h: H.r2(h), epi: epi === null ? null : H.r2(epi), a: a } };
}
"""


def blocks(ctx):
    return [
        ("Cuántos años humanos tiene tu perro o tu gato", """
<p>La regla de «un año de perro son siete humanos» no se sostiene: los perros y los gatos maduran muy deprisa al principio y
luego envejecen más despacio. La equivalencia que usan los veterinarios es <b>15 años humanos el primer año</b> y <b>24 a los dos
años</b>; desde ahí, cada año suma unos <b>4 años en los gatos y en los perros pequeños</b> (menos de 10 kg), 5 en los medianos, 6
en los grandes y 7 en los gigantes, porque los perros grandes viven menos. Un perro mediano de 5 años tiene unos 39 años humanos;
un gato de 10, unos 56.</p>
<p>Para los perros, la calculadora añade el «reloj epigenético» de un estudio de la Universidad de California en San Diego (Wang y
otros, 2020), que compara los cambios de metilación del ADN de perros y personas: <b>edad humana = 16 × ln(edad del perro) + 31</b>.
Da cifras más altas en los primeros años (un perro de un año equivale a una persona de 31) y más bajas en la vejez.</p>"""),
        ("Ejemplos", """
<ul>
<li><b>Gato de 6 meses</b>: unos 10 años humanos, en plena «pubertad».</li>
<li><b>Gato de 14 años</b>: 24 + 4 × 12 = <b>72 años</b>, senior desde los 10 según las guías felinas.</li>
<li><b>Yorkshire de 10 años</b> (pequeño): 24 + 4 × 8 = 56 años; con la fórmula epigenética, 16 × ln(10) + 31 = 68.</li>
<li><b>Labrador de 8 años</b> (grande): 24 + 6 × 6 = 60 años; senior desde los 6.</li>
<li><b>Gran danés de 7 años</b> (gigante): 24 + 7 × 5 = 59 años.</li>
</ul>"""),
        ("Fuentes y límites", f"""
<p>La regla de 15, 9 y unos 5 años más por año es la que recoge el <a href="{AKC}" rel="noopener">American Kennel Club</a> a partir
de la Asociación Americana de Medicina Veterinaria (AVMA) para un perro mediano; el ajuste por tamaño (de 4 a 7 años por año) es la
versión simplificada de la tabla veterinaria por peso. La fórmula epigenética es la del artículo de
<a href="{WANG}" rel="noopener">Wang y otros en Cell Systems (2020)</a>, calibrada con 104 labradores, así que encaja peor en
razas muy pequeñas o muy grandes y sus autores no la recomiendan para cachorros. Las etapas del gato son las de las
<a href="{AAFP}" rel="noopener">guías felinas AAHA/AAFP de 2021</a>: gatito hasta el año, adulto joven de 1 a 6, adulto maduro de
7 a 10 y senior desde los 10.</p>
<p>Sirve para hacerse una idea, por ejemplo de cuándo pasar a revisiones de senior (dos al año) o a un pienso para mayores. La salud
real depende de la raza, el peso, la esterilización y la vida que lleve.</p>"""),
    ]


FAQ = [
    ("¿Un año de perro son siete años humanos?",
     "No. El primer año equivale a unos 15 años humanos y el segundo a otros 9. Después, de 4 a 7 años por año según el tamaño."),
    ("¿Cuántos años humanos tiene un gato de 15 años?",
     "Unos 76: 24 a los dos años y 4 más por cada año siguiente (24 + 4 × 13)."),
    ("¿A qué edad es senior un perro?",
     "Los pequeños y medianos hacia los 7 años; los grandes y gigantes antes, hacia los 5 o 6, porque envejecen más deprisa."),
    ("¿Qué es la fórmula del logaritmo para perros?",
     "La de un estudio de 2020 que comparó la metilación del ADN de labradores y personas: 16 × ln(edad) + 31. Se aplica desde el "
     "año de vida; un perro de 2 años sale con 42 años humanos y uno de 12, con 71."),
    ("¿Cuánto vive un gato?",
     "Un gato doméstico que vive en casa suele llegar a los 12-18 años; muchos pasan de los 20. Los que salen a la calle viven de media "
     "bastante menos."),
]

TOOL = {
    "slug": "edad-perro-gato",
    "lang": "es",
    "twin": "dog-cat-age-calculator",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "paw",
    "order": 40,
    "name": "Edad perro o gato",
    "k": "años humanos perro gato edad real calculadora mascota senior cachorro",
    "title": "Edad de perro o gato en años humanos: calculadora",
    "desc": "Calcula la edad de tu perro o gato en años humanos según su tamaño, con la regla veterinaria y la fórmula epigenética de 2020, y su etapa de vida.",
    "h1": "Edad de perro o gato en años humanos",
    "crumb": "Edad de perro o gato",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "animal", "type": "seg", "label": "Animal", "value": "perro", "options": [("perro", "Perro"), ("gato", "Gato")]},
        {"id": "anos", "type": "number", "label": "Años", "value": 5, "w": "s"},
        {"id": "meses", "type": "number", "label": "Meses", "value": "", "w": "s"},
        {"id": "tam", "type": "select", "label": "Tamaño", "value": "m", "show": ("animal", ["perro"]),
         "options": [("p", "Pequeño (< 10 kg)"), ("m", "Mediano (10-25 kg)"), ("g", "Grande (25-45 kg)"), ("x", "Gigante (> 45 kg)")]},
    ],
    "js": make_js(L_ES),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("American Kennel Club · How to calculate dog years to human years (AVMA)", AKC),
                ("Wang y otros, Cell Systems 2020 · reloj epigenético perro-humano", WANG),
                ("AAHA/AAFP · Feline Life Stage Guidelines 2021", AAFP)],
    "credits": [("Wang T. y otros (2020), fórmula 16·ln(edad)+31 (reimplementada)", "fórmula publicada", WANG)],
    "related": ["gestacion-animal", "edad-exacta", "incubacion-huevos"],
    "tests": [
        ({"animal": "perro", "anos": "5", "tam": "m"}, {"n.h": 39, "n.epi": 56.75}),
        ({"animal": "perro", "anos": "10", "tam": "p"}, {"n.h": 56, "n.epi": 67.84}),
        ({"animal": "perro", "anos": "7", "tam": "x"}, {"n.h": 59}),
        ({"animal": "gato", "anos": "14"}, {"n.h": 72, "n.epi": None}),
        ({"animal": "gato", "anos": "", "meses": "6"}, {"n.h": 10}),
        ({"animal": "perro", "anos": "-2"}, {"err": "La edad no puede ser negativa."}),
    ],
}
