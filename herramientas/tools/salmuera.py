"""Salmuera: grams of salt for a brine of a given strength (olives, fermented pickles, meat brining) or for an
equilibrium ferment (sauerkraut, kimchi: salt on vegetables + water). English twin: brine_calculator.py."""
from herramientas.tools._cocina import CAT, js

UC = "https://escholarship.org/uc/item/55d9628m"
NCH_DILL = "https://nchfp.uga.edu/how/ferment/recipes/dill-pickles"
NCH_KRAUT = "https://nchfp.uga.edu/how/ferment/recipes/sauerkraut"
AESAN = "https://aesan.gob.es/actualidad/actualidad-noticias/conservas_caseras"
FDC = ("USDA FoodData Central · SR Legacy 173468 «Salt, table» (1 tbsp = 18 g, 1 cup = 292 g)", "Dominio público (CC0)",
       "https://fdc.nal.usda.gov/download-datasets")

BODY = r"""
  var WU = { l: 1000, gal: 3785.41, qt: 946.353 }, VU = { g: 1, kg: 1000, lb: 453.592 };
  var p = v.pct, base = v.base === 'a' ? 'a' : 't', ferm = v.modo === 'e';
  if (!ok(p) || p <= 0) return { err: T.e_pct };
  if ((base === 't' && p > 26) || (base === 'a' && p > 35.9)) return { err: T.e_sat };
  var wr = ferm ? v.aguae : v.agua, w = ok(wr) ? wr * (WU[v.wu] || 1000) : NaN, veg = 0;
  if (ferm) {
    veg = ok(v.verd) ? v.verd * (VU[v.vu] || 1) : NaN;
    if (!ok(veg) || veg <= 0) return { err: T.e_verd };
    if (!ok(w)) w = 0;
    if (w < 0) return { err: T.e_agua };
  } else if (!ok(w) || w <= 0) return { err: T.e_agua };
  var mass = w + veg, salt = base === 't' && !ferm ? mass * p / (100 - p) : mass * p / 100;
  var tot = salt / (mass + salt) * 100, perL = w ? salt / w * 1000 : 0;
  var rows = [];
  if (veg) rows.push([T.veg, gr(veg) + ' g']);
  if (w) rows.push([T.water, (EN && v.wu && v.wu !== 'l' ? nz(wr, 2) + ' ' + v.wu + ' = ' : '') + nz(w / 1000, 2) + ' L']);
  rows.push([T.salt, gr(salt) + ' g' + (EN ? ' = ' + nz(salt / 28.3495, 2) + ' oz' : ''), 'tot']);
  rows.push([T.tbsp, '≈ ' + nz(salt / 18, 1) + (EN ? ' (' + nz(salt / 292, 2) + ' cup)' : ''), 'sub']);
  if (!ferm) rows.push([T.perL, gr(perL) + ' g/L']);
  rows.push([T.ofTot, nz(tot, 2) + ' %']);
  return {
    label: ferm ? T.l_e : T.l_s, big: gr(salt) + ' g',
    sub: ferm ? T.sub_e.replace('{p}', nz(p, 2)) : (base === 't' ? T.sub_t : T.sub_a).replace('{p}', nz(p, 2)),
    rows: rows, note: T.note, print: true,
    n: { salt: H.r2(salt), perL: H.r2(perL), tot: H.r2(tot) }
  };
"""
JS = js(BODY)

T_ES = {
    "e_pct": "Escribe el porcentaje de sal.", "e_sat": "Por encima del 26 % del peso total (unos 360 g por litro) la sal ya no se disuelve.",
    "e_agua": "Escribe cuánta agua vas a usar.", "e_verd": "Escribe el peso de la verdura.",
    "veg": "Verdura", "water": "Agua", "salt": "Sal", "tbsp": "Cucharadas de sal fina", "perL": "Por litro de agua", "ofTot": "Sobre el peso total",
    "l_s": "Sal para la salmuera", "l_e": "Sal para el fermentado",
    "sub_t": "Salmuera al {p} % del peso total", "sub_a": "{p} % sobre el peso del agua", "sub_e": "{p} % de la verdura más el agua",
    "note": "Pesa la sal: una cucharada de sal gruesa pesa bastante menos que una de sal fina. Usa sal sin yodo ni antiaglomerantes.",
}
T_EN = {
    "e_pct": "Enter the salt percentage.", "e_sat": "Above 26 % of the total weight (about 360 g per litre) salt stops dissolving.",
    "e_agua": "Enter how much water you will use.", "e_verd": "Enter the weight of the vegetables.",
    "veg": "Vegetables", "water": "Water", "salt": "Salt", "tbsp": "Tbsp of fine table salt", "perL": "Per litre of water", "ofTot": "Of total weight",
    "l_s": "Salt for the brine", "l_e": "Salt for the ferment",
    "sub_t": "{p} % brine by total weight", "sub_a": "{p} % of the water weight", "sub_e": "{p} % of vegetables plus water",
    "note": "Weigh the salt: a spoon of kosher or flaky salt holds far less than a spoon of table salt. Use canning or pickling salt, without iodine or anti-caking agents.",
}


def inputs(lang):
    es = lang == "es"
    presets = [
        ("ac", "Aceitunas: conservar (10 %)" if es else "Olives: storage brine (10 %)", {"modo": "s", "pct": "10"}),
        ("ai", "Aceitunas: 1.ª semana (6 %)" if es else "Olives: first week (6 %)", {"modo": "s", "pct": "6"}),
        ("pe", "Pepinillos fermentados (7 %)" if es else "Fermented dill pickles (7 %)", {"modo": "s", "pct": "7"}),
        ("ch", "Chucrut o kimchi (2 %)" if es else "Sauerkraut or kimchi (2 %)", {"modo": "e", "pct": "2"}),
        ("lf", "Verduras fermentadas (3 %)" if es else "Lacto-fermented veg (3 %)", {"modo": "e", "pct": "3"}),
        ("ca", "Pavo, pollo o cerdo (6 %)" if es else "Turkey, chicken or pork (6 %)", {"modo": "s", "pct": "6"}),
        ("x", "Otro" if es else "Other"),
    ]
    out = [
        {"id": "uso", "type": "select", "label": "Para" if es else "For", "value": "ac", "options": presets, "custom": "x", "w": "l"},
        {"id": "modo", "type": "seg", "label": "Sal sobre" if es else "Salt on", "value": "s",
         "options": [("s", "Agua" if es else "Water"), ("e", "Verdura + agua" if es else "Veg + water")]},
        {"id": "verd", "type": "number", "label": "Verdura" if es else "Vegetables", "value": 1000, "unit": "" if not es else "g", "show": ("modo", ["e"])},
        {"id": "agua", "type": "number", "label": "Agua" if es else "Water", "value": 1, "unit": "" if not es else "L", "step": "0.1",
         "show": ("modo", ["s"])},
        {"id": "aguae", "type": "number", "label": "Agua" if es else "Water", "value": 0, "unit": "" if not es else "L", "step": "0.1",
         "show": ("modo", ["e"])},
        {"id": "pct", "type": "number", "label": "Sal" if es else "Salt", "value": 10, "unit": "%", "w": "s", "step": "0.1"},
        {"id": "base", "type": "select", "label": "Porcentaje" if es else "Percentage", "value": "t", "more": True,
         "options": [("t", "Sobre el total (sal + agua)" if es else "Of total weight (salt + water)"),
                     ("a", "Sobre el agua (g por litro)" if es else "Of the water (g per litre)")]},
    ]
    if not es:
        out.insert(3, {"id": "vu", "type": "select", "label": "Unit", "value": "g", "w": "s", "show": ("modo", ["e"]),
                       "options": [("g", "g"), ("kg", "kg"), ("lb", "lb")]})
        out.insert(6, {"id": "wu", "type": "select", "label": "Unit", "value": "l", "w": "s",
                       "options": [("l", "litres"), ("gal", "US gallons"), ("qt", "US quarts")]})
    return out


TESTS = [
    ({}, {"n.salt": 111.11, "n.perL": 111.11, "n.tot": 10}),
    ({"base": "a"}, {"n.salt": 100, "n.tot": 9.09}),
    ({"modo": "e", "pct": "2", "verd": "1000"}, {"n.salt": 20}),
    ({"modo": "e", "pct": "3", "verd": "800", "aguae": "0,6"}, {"n.salt": 42}),
    ({"pct": "30"}, {"err": T_ES["e_sat"]}),
    ({"agua": ""}, {"err": T_ES["e_agua"]}),
]

FAQ = [
    ("¿Cuánta sal por litro de agua para las aceitunas?",
     "Para conservarlas, una salmuera fuerte del 10 % del peso total: 111 g de sal por cada litro de agua. Mucha gente usa «100 g "
     "por litro», que es un 9,1 % real. La guía de la Universidad de California da 1 libra de sal por galón de agua (unos 120 g por "
     "litro, un 10,7 %) para la salmuera de conservación, y la mitad para la primera semana."),
    ("¿Qué es la prueba del huevo?",
     "El método tradicional: se echa sal hasta que un huevo fresco flota y asoma un trozo del tamaño de una moneda. Funciona de forma "
     "aproximada (la flotación depende del huevo y de su edad), por eso es mejor pesar la sal: con una báscula de cocina sabes "
     "exactamente qué concentración tienes."),
    ("¿El porcentaje es sobre el agua o sobre el total?",
     "Las dos formas se usan. «Sobre el total» (sal dividida entre sal más agua) es lo que miden los salinómetros y lo que usan las "
     "guías técnicas; «sobre el agua» equivale a gramos por litro. La diferencia crece con la sal: al 10 % sobre el total son 111 g "
     "por litro; 100 g por litro son un 9,1 %. Puedes elegir en «Más opciones»."),
    ("¿Cuánta sal lleva el chucrut?",
     "Entre el 2 y el 2,5 % del peso de la col: 20 a 25 g por kilo. Las recetas del National Center for Home Food Preservation de "
     "EE. UU. (3 cucharadas de sal por cada 5 libras de col) dan algo menos del 2,5 %. Por debajo del 2 % la col se ablanda y "
     "aparecen más mohos."),
    ("¿Puedo usar sal yodada o sal gruesa?",
     "Mejor sal sin yodo y sin antiaglomerantes, que no enturbian la salmuera. La sal gruesa sirve igual si la pesas: por volumen, una "
     "cucharada de sal gruesa lleva mucha menos sal que una de sal fina."),
    ("¿Las aceitunas en salmuera pueden dar botulismo?",
     "El riesgo de botulismo está en las conservas caseras poco ácidas (pH por encima de 4,5) cerradas sin la técnica adecuada. Las "
     "aceitunas fermentadas en salmuera fuerte y bien cubiertas son un método tradicional seguro; lo que no debes hacer es embotarlas "
     "al baño maría sin fermentar ni guardar ajos, guindillas o hierbas en aceite a temperatura ambiente."),
]


def blocks_es(ctx):
    return [
        ("Cómo se calcula", """
<p>Elige para qué es la salmuera, cuánta agua vas a usar y el porcentaje. La sal se calcula sobre el peso total, como en las guías
técnicas: <b>sal = agua × % ÷ (100 − %)</b>. Para un litro al 10 % son <b>111 g de sal</b>, que en la salmuera final son
exactamente el 10 % del peso (111 de 1.111 g). Si tu receta dice «100 g de sal por litro», cambia el porcentaje a «sobre el agua»
en «Más opciones»: es lo mismo que un 9,1 % real.</p>
<p>Para chucrut, kimchi y verduras fermentadas se usa la salmuera de equilibrio: la sal se calcula sobre el peso de la verdura más
el del agua. Para 1 kg de col sin agua al 2 % son 20 g de sal; para 800 g de zanahoria cubierta con 600 ml de agua al 3 %,
42 g.</p>"""),
        ("Aceitunas: las salmueras de referencia", """
<p>La guía <i>Olives: Safe Methods for Home Pickling</i> de la Universidad de California (publicación 8267) usa tres fuerzas para
curar aceitunas en salmuera:</p>
<ul>
<li><b>Media</b>: 8 onzas de sal por galón de agua, un <b>5,7 %</b>, durante la primera semana, para que no se arruguen.</li>
<li><b>Fuerte</b>: 1 libra por galón, un <b>10,7 %</b>, para el curado de varios meses y para guardarlas hasta un año.</li>
<li>Al estilo siciliano, verdes: 10 onzas por galón (un 7 %) con unas 2 tazas de vinagre por galón.</li>
</ul>
<p>La guía insiste en no rebajar estas concentraciones durante la fermentación y en mantener las aceitunas siempre cubiertas.
Para las aceitunas aliñadas de casa (endulzadas en agua y luego aliñadas con tomillo, hinojo, ajo o piel de naranja) una salmuera
del 6 al 10 % es lo habitual; cuanto más floja, más corta su vida y más importante la nevera.</p>"""),
        ("Seguridad: lo que dicen las autoridades", """
<p>La Agencia Española de Seguridad Alimentaria (AESAN) recuerda que los alimentos más asociados al botulismo son las
<b>conservas caseras de alimentos poco ácidos</b> (pH por encima de 4,5), como guindillas en aceite, espárragos o judías verdes, y recomienda tirar
cualquier conserva abombada, con pérdidas o con olor raro (la toxina no cambia el sabor). Para fermentados, el National Center for
Home Food Preservation de EE. UU. aconseja fermentar entre 21 y 24 °C, retirar la espuma o el moho de la superficie varias veces
por semana y desechar lo que quede blando, viscoso o huela mal. Guarda los fermentados terminados en la nevera.</p>
<p>Para salmueras de carne (pavo, pollo o cerdo, entre el 5 y el 7 %), el Departamento de Agricultura de EE. UU. (USDA) pide
tener carne y salmuera a 4 °C o menos todo el tiempo, en la nevera o en una nevera portátil con hielo, nunca a temperatura
ambiente ni más de dos días, con la pieza totalmente sumergida, y tirar la salmuera al terminar.</p>"""),
    ]


TOOL = {
    "slug": "salmuera",
    "lang": "es",
    "twin": "brine-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "salt",
    "order": 30,
    "name": "Salmuera",
    "k": "aceitunas aliñar encurtidos sal por litro chucrut kimchi pepinillos fermentar",
    "title": "Calculadora de salmuera para aceitunas y encurtidos",
    "desc": "Cuánta sal por litro de agua para aliñar aceitunas, pepinillos, chucrut o una salmuera para pavo: gramos exactos al 2, 6 o 10 %.",
    "h1": "Calculadora de salmuera",
    "crumb": "Salmuera",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("Universidad de California · Olives: Safe Methods for Home Pickling (ANR 8267)", UC),
                ("NCHFP · Dill pickles", NCH_DILL), ("NCHFP · Sauerkraut", NCH_KRAUT), ("AESAN · Conservas caseras", AESAN),
                ("USDA FSIS · Salmuera de aves", "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/poultry/happy-thanksgiving")],
    "credits": [FDC],
    "related": ["azucar-mermelada", "tazas-a-gramos", "tiempo-asado", "escalar-receta"],
    "tests": TESTS,
}
