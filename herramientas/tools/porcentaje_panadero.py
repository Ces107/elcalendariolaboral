"""Porcentaje panadero: a bread formula from baker's percentages (flour = 100 %), by flour weight, total dough weight
or number of pieces; real hydration with a sourdough levain inside. English twin: bakers_percentage_calculator.py."""
from herramientas.tools._cocina import CAT, js

KA = "https://www.kingarthurbaking.com/pro/reference/bakers-percentage"
KAY = "https://www.kingarthurbaking.com/pro/reference/yeast"

BODY = r"""
  var F, mode = v.modo, loss = ok(v.merma) ? v.merma : 0;
  var p = { w: v.hid, s: v.sal, y: ok(v.lev) ? v.lev : 0, l: ok(v.mm) ? v.mm : 0, a: ok(v.azu) ? v.azu : 0, g: ok(v.gra) ? v.gra : 0 };
  var lh = ok(v.mmh) ? v.mmh : 100;
  if (!ok(p.w) || p.w < 0 || p.w > 150) return { err: T.e_hid };
  if (!ok(p.s) || p.s < 0 || p.s > 10) return { err: T.e_sal };
  if (p.y < 0 || p.y > 10 || p.l < 0 || p.l > 300 || p.a < 0 || p.a > 100 || p.g < 0 || p.g > 100) return { err: T.e_pct };
  if (lh < 20 || lh > 300) return { err: T.e_mmh };
  if (loss < 0 || loss >= 50) return { err: T.e_merma };
  var sum = 100 + p.w + p.s + p.y + p.a + p.g;
  var dough;
  if (mode === 'h') {
    if (!ok(v.harina) || v.harina <= 0 || v.harina > 1e6) return { err: T.e_harina };
    F = v.harina; dough = F * sum / 100;
  } else {
    if (mode === 'm') { if (!ok(v.masa) || v.masa <= 0 || v.masa > 2e6) return { err: T.e_masa }; dough = v.masa; }
    else {
      if (!ok(v.piezas) || v.piezas < 1 || v.piezas > 1000 || Math.round(v.piezas) !== v.piezas) return { err: T.e_piezas };
      if (!ok(v.peso) || v.peso <= 0 || v.peso > 1e5) return { err: T.e_peso };
      dough = v.piezas * v.peso;
    }
    dough = dough / (1 - loss / 100);
    F = dough * 100 / sum;
  }
  var L = F * p.l / 100, Lf = L / (1 + lh / 100), Lw = L - Lf;
  var W = F * p.w / 100, addF = F - Lf, addW = W - Lw;
  if (addW < -0.05) return { err: T.e_agua };
  if (addF < -0.05) return { err: T.e_mmflour };
  var yt = T.yt[v.levt] || T.yt.f, yk = { f: 1, s: 0.4, i: 1 / 3 }[v.levt] || 1;
  var rows = [[(p.l ? T.add + T.flour.toLowerCase() : T.flour) + ' · 100 %', gr(addF) + ' g']];
  rows.push([(p.l ? T.add + T.water.toLowerCase() : T.water) + ' · ' + nz(p.w, 1) + ' %', gr(Math.max(0, addW)) + ' g']);
  rows.push([T.salt + ' · ' + nz(p.s, 2) + ' %', gr(F * p.s / 100) + ' g']);
  if (p.y) rows.push([yt + ' · ' + nz(p.y, 2) + ' %', gr(F * p.y / 100) + ' g']);
  if (p.l) rows.push([T.lev + ' · ' + nz(p.l, 1) + ' %', gr(L) + ' g']);
  if (p.a) rows.push([T.sugar + ' · ' + nz(p.a, 1) + ' %', gr(F * p.a / 100) + ' g']);
  if (p.g) rows.push([T.fat + ' · ' + nz(p.g, 1) + ' %', gr(F * p.g / 100) + ' g']);
  rows.push([T.total + ' · ' + nz(sum, 1) + ' %', gr(dough) + ' g', 'tot']);
  if (p.l) {
    rows.splice(1, 0, [T.inlev, gr(Lf) + ' g ' + T.of_flour + ' + ' + gr(Lw) + ' g ' + T.of_water, 'sub']);
  }
  var note = [];
  if (p.y) {
    var fresh = p.y / yk, eq = [];
    ['f', 's', 'i'].forEach(function (k) { if (k !== (T.yt[v.levt] ? v.levt : 'f')) eq.push(T.yt[k].toLowerCase() + ' ' + nz(fresh * { f: 1, s: 0.4, i: 1 / 3 }[k], 2) + ' %'); });
    note.push(T.yeq + ' ' + eq.join(' · ') + '.');
  }
  if (mode === 'p') note.push(T.pieces.replace('{n}', v.piezas).replace('{w}', gr(v.peso)) + (loss ? ' ' + T.loss.replace('{l}', nz(loss, 1)) : ''));
  else if (mode === 'm' && loss) note.push(T.loss.replace('{l}', nz(loss, 1)));
  return {
    label: T.big_l, big: gr(F) + ' g',
    sub: T.sub.replace('{w}', nz(p.w, 1)).replace('{d}', gr(dough)),
    rows: rows, note: note.join(' '), print: true,
    n: { flour: H.r2(F), addFlour: H.r2(addF), water: H.r2(Math.max(0, addW)), salt: H.r2(F * p.s / 100), yeast: H.r2(F * p.y / 100), levain: H.r2(L), dough: H.r2(dough) }
  };
"""
JS = js(BODY)

T_ES = {
    "e_hid": "Hidratación: de 0 a 150 %.", "e_sal": "Sal: de 0 a 10 %.", "e_pct": "Revisa los porcentajes.",
    "e_mmh": "Hidratación de la masa madre: de 20 a 300 %.", "e_merma": "Merma: de 0 a 49 %.",
    "e_harina": "Escribe los gramos de harina.", "e_masa": "Escribe el peso total de masa.", "e_piezas": "Piezas: un número entero.",
    "e_peso": "Escribe el peso de cada pieza.",
    "e_agua": "La masa madre ya aporta más agua de la que pide esa hidratación: sube la hidratación o baja la masa madre.",
    "e_mmflour": "La masa madre aporta más harina que el total: baja su porcentaje.",
    "yt": {"f": "Levadura fresca", "s": "Levadura seca", "i": "Levadura instantánea"},
    "flour": "Harina", "water": "Agua", "salt": "Sal", "lev": "Masa madre", "sugar": "Azúcar", "fat": "Grasa", "total": "Masa total",
    "inlev": "Dentro de la masa madre", "of_flour": "harina", "of_water": "agua", "add": "Añadir ",
    "yeq": "Equivale a:", "pieces": "{n} piezas de {w} g.", "loss": "Incluye un {l} % de merma.",
    "big_l": "Harina total", "sub": "Hidratación {w} % · masa {d} g",
}
T_EN = {
    "e_hid": "Hydration: 0 to 150 %.", "e_sal": "Salt: 0 to 10 %.", "e_pct": "Check the percentages.",
    "e_mmh": "Starter hydration: 20 to 300 %.", "e_merma": "Loss: 0 to 49 %.",
    "e_harina": "Enter the flour weight in grams.", "e_masa": "Enter the total dough weight.", "e_piezas": "Pieces: a whole number.",
    "e_peso": "Enter the weight of each piece.",
    "e_agua": "The starter already brings more water than this hydration allows: raise the hydration or use less starter.",
    "e_mmflour": "The starter holds more flour than the whole formula: lower its percentage.",
    "yt": {"f": "Fresh yeast", "s": "Active dry yeast", "i": "Instant yeast"},
    "flour": "Flour", "water": "Water", "salt": "Salt", "lev": "Sourdough starter", "sugar": "Sugar", "fat": "Fat", "total": "Total dough",
    "inlev": "Inside the starter", "of_flour": "flour", "of_water": "water", "add": "Add ",
    "yeq": "Same as:", "pieces": "{n} pieces of {w} g.", "loss": "Includes {l} % for scaling and bench loss.",
    "big_l": "Total flour", "sub": "Hydration {w} % · dough {d} g",
}


def inputs(lang):
    es = lang == "es"
    return [
        {"id": "modo", "type": "seg", "label": "Calcular desde" if es else "Start from", "value": "h",
         "options": [("h", "Harina" if es else "Flour"), ("m", "Masa total" if es else "Dough weight"), ("p", "Piezas" if es else "Pieces")]},
        {"id": "harina", "type": "number", "label": "Harina" if es else "Flour", "value": 1000, "unit": "g", "show": ("modo", ["h"])},
        {"id": "masa", "type": "number", "label": "Masa total" if es else "Dough", "value": 1600, "unit": "g", "show": ("modo", ["m"])},
        {"id": "piezas", "type": "number", "label": "Piezas" if es else "Pieces", "value": 2, "w": "s", "show": ("modo", ["p"])},
        {"id": "peso", "type": "number", "label": "Peso pieza" if es else "Each", "value": 800, "unit": "g", "show": ("modo", ["p"])},
        {"id": "hid", "type": "number", "label": "Hidratación" if es else "Hydration", "value": 70, "unit": "%", "w": "s", "step": "0.5"},
        {"id": "sal", "type": "number", "label": "Sal" if es else "Salt", "value": 2, "unit": "%", "w": "s", "step": "0.1"},
        {"id": "levt", "type": "select", "label": "Tipo" if es else "Yeast type", "value": "f",
         "options": [("f", "Fresca" if es else "Fresh"), ("s", "Seca activa" if es else "Active dry"), ("i", "Instantánea" if es else "Instant")]},
        {"id": "lev", "type": "number", "label": "Levadura" if es else "Yeast", "value": 1.5, "unit": "%", "w": "s", "step": "0.1"},
        {"id": "mm", "type": "number", "label": "Masa madre" if es else "Starter", "value": 0, "unit": "%", "w": "s"},
        {"id": "mmh", "type": "number", "label": "Hidratación MM" if es else "Starter hydration", "value": 100, "unit": "%", "w": "s", "more": True},
        {"id": "azu", "type": "number", "label": "Azúcar" if es else "Sugar", "value": 0, "unit": "%", "w": "s", "more": True},
        {"id": "gra", "type": "number", "label": "Grasa" if es else "Fat", "value": 0, "unit": "%", "w": "s", "more": True},
        {"id": "merma", "type": "number", "label": "Merma" if es else "Loss", "value": 0, "unit": "%", "w": "s", "more": True},
    ]


TESTS = [
    ({}, {"n.flour": 1000, "n.water": 700, "n.salt": 20, "n.yeast": 15, "n.dough": 1735}),
    ({"modo": "m", "masa": "1735"}, {"n.flour": 1000, "n.water": 700}),
    ({"modo": "p", "piezas": "2", "peso": "800"}, {"n.dough": 1600, "n.flour": 922.19, "n.water": 645.53}),
    ({"mm": "20", "lev": "0"}, {"n.levain": 200, "n.addFlour": 900, "n.water": 600, "n.dough": 1720}),
    ({"hid": "40", "mm": "100"}, {"err": T_ES["e_agua"]}),
    ({"harina": ""}, {"err": T_ES["e_harina"]}),
]

FAQ = [
    ("¿Qué es el porcentaje panadero?",
     "Una forma de escribir recetas de pan en la que la harina vale siempre 100 % y cada ingrediente se expresa como porcentaje "
     "del peso de la harina. Por eso los porcentajes suman más de 100: una masa con 70 % de agua, 2 % de sal y 1,5 % de levadura "
     "suma 173,5 %."),
    ("¿Cómo calculo la hidratación de mi masa?",
     "Divide los gramos de agua entre los gramos de harina y multiplica por 100. 650 g de agua con 1 kg de harina son un 65 % de "
     "hidratación. Si usas masa madre, suma también el agua y la harina que lleva dentro: esa es la hidratación real."),
    ("¿Cuánta sal lleva el pan?",
     "Lo habitual es entre el 1,8 y el 2,2 % del peso de la harina: 18 a 22 g por kilo. Por debajo del 1,5 % el pan queda soso; "
     "por encima del 2,5 % la sal frena la fermentación."),
    ("¿Qué hidratación usar para cada pan?",
     "Como orientación: pan de molde y bagels, 55-62 %; barra o pan de pueblo, 65-70 %; chapata y panes de miga muy abierta, "
     "75-85 %. Las harinas integrales y de fuerza absorben más agua que una harina floja, así que empieza por abajo y sube."),
    ("¿El porcentaje de levadura es de fresca o de seca?",
     "Depende de la receta: muchos libros profesionales lo dan en levadura fresca. Para pasar a seca activa multiplica por 0,4 y "
     "para instantánea por un tercio (1 % de fresca ≈ 0,33 % de instantánea). La calculadora lo hace al elegir el tipo."),
    ("¿Para qué sirve la merma?",
     "Al dividir y bolear se queda masa en el bol, la mesa y las manos. Con 2-3 % de merma salen las piezas con el peso exacto "
     "que buscas."),
]


def blocks_es(ctx):
    return [
        ("Cómo funciona", """
<p>Escribe la harina que vas a usar, o el peso de masa que quieres sacar, o cuántas piezas y de qué peso, y los porcentajes de tu
receta. La calculadora devuelve los gramos de cada ingrediente. Todo se refiere al <b>peso total de harina = 100 %</b>: agua 70 %
significa 700 g de agua por cada kilo de harina. Es el sistema que usan los panaderos porque una receta así se escala sin pensar:
para el doble de pan, el doble de harina, y los porcentajes no cambian.</p>
<p>Desde el peso de masa se calcula al revés: harina = masa ÷ (suma de porcentajes ÷ 100). Por eso para 1.600 g de masa al 70 %
de agua, 2 % de sal y 1,5 % de levadura fresca necesitas 1.600 ÷ 1,735 = <b>922 g de harina</b>, 646 g de agua, 18 g de sal y
14 g de levadura.</p>"""),
        ("Con masa madre: la hidratación real", """
<p>La masa madre también lleva harina y agua. Si la receta dice «20 % de masa madre al 100 %» sobre 1 kg de harina, son 200 g de
masa madre con 100 g de harina y 100 g de agua dentro. Para que la hidratación siga siendo del 70 %, añades solo 900 g de harina
y 600 g de agua. La calculadora hace esa resta y te enseña cuánto aporta la masa madre, así no acabas con una masa más blanda
de lo que querías. Si tu masa madre es más firme (por ejemplo al 60 %), cámbialo en «Más opciones».</p>"""),
        ("Ejemplos con números", """
<ul>
<li><b>Pan de pueblo de 1 kg de harina</b>: 70 % de agua (700 g), 2 % de sal (20 g), 1,5 % de levadura fresca (15 g). Masa total
1.735 g: dos hogazas de unos 865 g.</li>
<li><b>Seis bocadillos de 120 g</b>: 720 g de masa. Con 65 % de agua, 2 % de sal y 0,5 % de instantánea, 430 g de harina y
279 g de agua.</li>
<li><b>Brioche</b>: 100 % harina, 20 % azúcar, 40 % mantequilla («Grasa»), 2 % sal y la hidratación de huevos y leche
(alrededor del 55-60 %).</li>
</ul>"""),
    ]


TOOL = {
    "slug": "porcentaje-panadero",
    "lang": "es",
    "twin": "bakers-percentage-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "bread",
    "order": 10,
    "name": "Porcentaje panadero",
    "k": "pan hidratación harina agua sal levadura receta masa",
    "title": "Calculadora de porcentaje panadero e hidratación",
    "desc": "Calcula los gramos de harina, agua, sal y levadura de tu pan con el porcentaje panadero: por harina, por peso de masa o por piezas, con masa madre.",
    "h1": "Calculadora de porcentaje panadero",
    "crumb": "Porcentaje panadero",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("King Arthur Baking · Baker's percentage", KA), ("King Arthur Baking · Yeast (conversiones)", KAY)],
    "related": ["masa-madre", "escalar-receta", "tazas-a-gramos", "temperatura-horno"],
    "tests": TESTS,
}
