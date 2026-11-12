"""Azúcar para mermelada: sugar for a fruit weight and ratio, expected yield at a target sugar content (60 % = legal
«confitura» in the EU), water to cook off, jars, fruit per kg. Fruit sugars from USDA FoodData Central. English twin:
jam_sugar_calculator.py."""
from herramientas.tools._cocina import CAT, js

RD863 = "https://www.boe.es/eli/es/rd/2003/07/04/863"
RD1026 = "https://www.boe.es/eli/es/rd/2025/11/12/1026"
NCHFP = "https://nchfp.uga.edu/how/make-jam-jelly/jams-jellies-general-information/general-information-on-canning-jams-jellies-and-marmalades/"
NCHFP_T = "https://nchfp.uga.edu/how/make-jam-jelly/jams-jellies-general-information/testing-jelly-without-added-pectin/"
FDC_DL = "https://fdc.nal.usda.gov/download-datasets"

# id, Spanish, English, total sugars g/100 g (FDC SR Legacy nutrient 2000), FDC id
FRUIT = [
    ("fresa", "Fresa", "Strawberry", 4.89, 167762), ("frambuesa", "Frambuesa", "Raspberry", 4.42, 167755),
    ("mora", "Mora", "Blackberry", 4.88, 173946), ("arandano", "Arándano", "Blueberry", 9.96, 171711),
    ("melocoton", "Melocotón", "Peach", 8.39, 169928), ("albaricoque", "Albaricoque", "Apricot", 9.24, 171697),
    ("ciruela", "Ciruela", "Plum", 9.92, 169949), ("cereza", "Cereza", "Sweet cherry", 12.82, 171719),
    ("guinda", "Guinda (cereza ácida)", "Sour cherry", 8.49, 173954), ("naranja", "Naranja", "Orange", 9.35, 169097),
    ("higo", "Higo", "Fig", 16.26, 173021), ("manzana", "Manzana", "Apple", 10.39, 171688), ("pera", "Pera", "Pear", 9.75, 169118),
    ("mango", "Mango", "Mango", 13.66, 169910), ("tomate", "Tomate", "Tomato", 2.63, 170457), ("calabaza", "Calabaza", "Pumpkin", 2.76, 168448),
]

BODY = r"""
  var Fr = D.fr.filter(function (x) { return x[0] === v.fruta; })[0] || D.fr[0];
  var F = v.peso, p = v.azp, t = ok(v.punto) ? v.punto : 60, jar = ok(v.tarro) ? v.tarro : 250;
  if (!ok(F) || F <= 0 || F > 1e5) return { err: T.e_peso };
  if (!ok(p) || p < 0 || p > 200) return { err: T.e_azp };
  if (t < 30 || t > 75) return { err: T.e_punto };
  if (jar <= 0 || jar > 5000) return { err: T.e_tarro };
  var S = F * p / 100, fs = F * Fr[1] / 100, Y = (S + fs) / (t / 100), E = F + S - Y, already = E < 0;
  if (already) Y = F + S;
  var real = (S + fs) / Y * 100, perKg = F / Y * 1000, vol = Y / 1.3, jars = Math.ceil(vol / jar - 0.05);
  var rows = [[T.sugar, gr(S) + ' g', 'tot'], [T.fsug, gr(fs) + ' g ' + T.fsug_s.replace('{p}', nz(Fr[1], 2)), 'sub'],
              [T.yield, '≈ ' + gr(Y) + ' g'], [T.evap, already ? '0 g' : '≈ ' + gr(E) + ' g · ' + nf(E / (F + S) * 100, 0) + ' %'],
              [T.jars.replace('{j}', nf(jar, 0)), jars + ' (' + nf(vol, 0) + ' ml)'],
              [T.perkg, nf(perKg, 0) + ' g', perKg >= 450 && real >= 59.95 ? '' : 'sub']];
  var notes = [];
  if (already) notes.push(T.n_already.replace('{p}', nz(real, 1)));
  notes.push(real < 59.95 ? T.n_low : (perKg >= 500 ? T.n_extra : perKg >= 450 ? T.n_conf : T.n_fruit));
  return {
    label: T.lab.replace('{f}', gr(F)).replace('{n}', T.names[Fr[0]].toLowerCase()), big: gr(S) + ' g',
    sub: T.sub.replace('{p}', nz(p, 1)).replace('{t}', nz(t, 1)), rows: rows, note: notes.join(' '), print: true,
    n: { sugar: H.r2(S), yield: H.r2(Y), evap: H.r2(Math.max(0, E)), jars: jars, perKg: H.r2(perKg) }
  };
"""
JS = js(BODY)

T_ES = {
    "e_peso": "Escribe el peso de la fruta limpia.", "e_azp": "Azúcar: de 0 a 200 % del peso de la fruta.", "e_punto": "Punto final: de 30 a 75 %.",
    "e_tarro": "Escribe la capacidad del tarro.", "names": {f[0]: f[1] for f in FRUIT},
    "sugar": "Azúcar", "fsug": "Azúcar de la propia fruta", "fsug_s": "({p} %)", "yield": "Mermelada que sale",
    "evap": "Agua que hay que evaporar", "jars": "Tarros de {j} ml", "perkg": "Fruta por kg de mermelada",
    "lab": "{f} g de {n}", "sub": "{p} % de azúcar · punto final {t} % de azúcar",
    "n_already": "Sin reducir ya tiene un {p} % de azúcar: basta con cocer hasta que espese.",
    "n_low": "Por debajo del 60 % de azúcar no es «confitura» legal: guárdala en la nevera una vez abierta.",
    "n_extra": "Con este contenido de fruta se podría llamar «confitura extra» (500 g/kg).",
    "n_conf": "Cumple los mínimos de «confitura» (450 g de fruta por kg y 60 % de materia seca).",
    "n_fruit": "Menos de 450 g de fruta por kg: más azúcar que fruta en el bote.",
}
T_EN = {
    "e_peso": "Enter the weight of prepared fruit.", "e_azp": "Sugar: 0 to 200 % of the fruit weight.", "e_punto": "Final sugar: 30 to 75 %.",
    "e_tarro": "Enter the jar size.", "names": {f[0]: f[2] for f in FRUIT},
    "sugar": "Sugar", "fsug": "Sugar already in the fruit", "fsug_s": "({p} %)", "yield": "Jam you get",
    "evap": "Water to cook off", "jars": "{j} ml jars", "perkg": "Fruit per kg of jam",
    "lab": "{f} g {n}", "sub": "{p} % sugar · cooked to {t} % sugar",
    "n_already": "Before any reduction it is already {p} % sugar: just cook until it sets.",
    "n_low": "Below 60 % sugar it keeps less well: refrigerate after opening (EU rules call 60 % «jam»).",
    "n_extra": "That much fruit would qualify as «extra jam» under EU rules (500 g/kg).",
    "n_conf": "Meets the EU «jam» minimums (450 g fruit per kg, 60 % soluble solids).",
    "n_fruit": "Under 450 g of fruit per kg: more sugar than fruit in the jar.",
}


def data(lang):
    return {"en": lang == "en", "t": T_EN if lang == "en" else T_ES, "fr": [[f[0], f[3], f[4]] for f in FRUIT]}


def inputs(lang):
    es = lang == "es"
    presets = [("100", "1:1 tradicional (100 %)" if es else "1:1 classic (100 %)", {"azp": "100", "punto": "60"}),
               ("75", "Clásica (75 %)" if es else "Standard (75 %)", {"azp": "75", "punto": "60"}),
               ("50", "Menos dulce (50 %)" if es else "Less sweet (50 %)", {"azp": "50", "punto": "55"}),
               ("30", "Baja en azúcar (30 %)" if es else "Low sugar (30 %)", {"azp": "30", "punto": "45"}),
               ("x", "Otra" if es else "Other")]
    names = [(f[0], f[1] if es else f[2]) for f in FRUIT]
    return [
        {"id": "fruta", "type": "select", "label": "Fruta" if es else "Fruit", "value": "fresa", "options": names},
        {"id": "peso", "type": "number", "label": "Fruta limpia" if es else "Prepared fruit", "value": 1000, "unit": "g", "w": "s"},
        {"id": "prop", "type": "select", "label": "Azúcar" if es else "Sugar", "value": "75", "options": presets, "custom": "x"},
        {"id": "azp", "type": "number", "label": "Azúcar" if es else "Sugar", "value": 75, "unit": "%", "w": "s"},
        {"id": "punto", "type": "number", "label": "Punto final" if es else "Final sugar", "value": 60, "unit": "%", "w": "s", "more": True},
        {"id": "tarro", "type": "number", "label": "Tarro" if es else "Jar", "value": 250, "unit": "ml", "w": "s", "more": True},
    ]


TESTS = [
    ({}, {"n.sugar": 750, "n.yield": 1331.5, "n.evap": 418.5}),
    ({"fruta": "melocoton", "prop": "100", "azp": "100"}, {"n.yield": 1806.5, "n.evap": 193.5}),
    ({"fruta": "higo", "azp": "50"}, {"n.yield": 1104.33, "n.perKg": 905.52}),
    ({"azp": "200", "punto": "60"}, {"n.evap": 0}),
    ({"peso": ""}, {"err": T_ES["e_peso"]}),
]

FAQ = [
    ("¿Cuánto azúcar por kilo de fruta para mermelada?",
     "La receta tradicional es 1:1, un kilo de azúcar por kilo de fruta. Hoy lo más habitual son 600-750 g por kilo, y con fruta muy "
     "dulce (higos, mango) o pectina se puede bajar a 500 g. Por debajo de eso hace falta pectina y guardarla en la nevera."),
    ("¿Cuánta mermelada sale de un kilo de fruta?",
     "Con 750 g de azúcar y fresas, unos 1.330 g de mermelada cocida al 60 % de azúcar: unos cinco tarros de 250 ml. Cuanto menos "
     "azúcar, menos rendimiento, porque hay que evaporar más agua para que espese."),
    ("¿Qué diferencia hay entre mermelada y confitura?",
     "En la normativa española, «confitura» es fruta con azúcar con al menos un 60 % de materia seca soluble y, desde el 14 de junio de "
     "2026, al menos 450 g de fruta por kilo (500 g en la «confitura extra»). «Mermelada» se reserva para la de cítricos. En casa se "
     "llama mermelada a todo."),
    ("¿Cómo sé que la mermelada está en su punto?",
     "Pon una gota en un plato frío y empújala con el dedo: si se arruga, está. Con termómetro, el punto de gelificación con un 60-65 % "
     "de azúcar está unos 4 °C por encima del punto de ebullición del agua, unos 104 °C a nivel del mar."),
    ("¿Hace falta esterilizar los botes?",
     "Para guardar la mermelada fuera de la nevera, sí: botes limpios y calientes, llenar en caliente y tratar al baño maría. El "
     "National Center for Home Food Preservation da 5 minutos de baño hirviendo para tarros esterilizados (10 si no lo están), con "
     "6 mm de espacio libre, y un minuto más por cada 300 m de altitud. Las mermeladas bajas en azúcar, siempre en la nevera una vez "
     "abiertas."),
]


def blocks_es(ctx):
    return [
        ("Cómo se calcula", """
<p>El azúcar se calcula como porcentaje del peso de la fruta ya limpia (sin huesos, pieles ni tallos): con 1 kg de fresas al 75 %
son <b>750 g de azúcar</b>. Para saber cuánta mermelada sale, la calculadora suma el azúcar que pones y el que ya trae la fruta
(4,9 g por cada 100 g de fresa, según la base de datos del USDA) y busca el peso con el que ese azúcar es el 60 % del total:
(750 + 49) ÷ 0,60 = <b>1.332 g de mermelada</b>. Para llegar ahí hay que evaporar 1.750 − 1.332 = 418 g de agua, casi una cuarta
parte de lo que hay en la olla.</p>
<p>Con la receta tradicional 1:1 se evapora muy poco y la mermelada espesa enseguida; con menos azúcar hay que cocer más tiempo, y
por debajo del 50 % casi siempre hace falta pectina (o fruta rica en pectina, como la manzana o el membrillo) para que cuaje sin
reducirla demasiado. El limón no es solo sabor: la acidez ayuda a que la pectina gelifique.</p>"""),
        ("Lo que dice la normativa", """
<p>La norma de calidad de las confituras (Real Decreto 863/2003, modificado por el Real Decreto 1026/2025 que traspone la
Directiva (UE) 2024/1438) fija desde el 14 de junio de 2026 que una <b>confitura</b> lleva al menos <b>450 g de fruta por cada
1.000 g</b> de producto y la <b>confitura extra</b>, 500 g, con una materia seca soluble mínima del 60 %. Los productos «con
contenido reducido de azúcares» o con edulcorantes quedan fuera de ese 60 %. Esto es para lo que se vende, pero es una buena
referencia casera: al 60 % de azúcar la mermelada se conserva bien una vez abierta; por debajo, mejor en la nevera.</p>
<p>La calculadora te dice cuánta fruta lleva cada kilo de tu mermelada. Con 1 kg de fresa y 750 g de azúcar cocida al 60 % salen
751 g de fruta por kilo, muy por encima del mínimo.</p>"""),
    ]


TOOL = {
    "slug": "azucar-mermelada",
    "lang": "es",
    "twin": "jam-sugar-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "cherry",
    "order": 100,
    "name": "Azúcar para mermelada",
    "k": "mermelada confitura azúcar por kilo fruta rendimiento tarros fresa higo tomate",
    "title": "Cuánto azúcar para mermelada: calculadora por kilo",
    "desc": "Calcula el azúcar para tu mermelada según el peso de la fruta, cuánta mermelada sale, el agua que hay que evaporar y cuántos tarros necesitas.",
    "h1": "Calculadora de azúcar para mermelada",
    "crumb": "Azúcar para mermelada",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": data("es"),
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("BOE · Real Decreto 863/2003 (confituras)", RD863), ("BOE · Real Decreto 1026/2025", RD1026), ("NCHFP · Canning jams and jellies", NCHFP),
                ("NCHFP · Testing jelly (punto)", NCHFP_T)],
    "credits": [("USDA FoodData Central · SR Legacy, azúcares totales de la fruta", "Dominio público (CC0)", FDC_DL)],
    "related": ["salmuera", "escalar-receta", "tazas-a-gramos", "cantidades-fiesta"],
    "tests": TESTS,
}
