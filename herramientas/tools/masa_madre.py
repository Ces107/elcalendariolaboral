"""Masa madre: feeding amounts (1:1:1, 1:5:5...), swapping commercial yeast for a levain without changing the dough's
hydration, and fresh / active dry / instant yeast equivalents. English twin: sourdough_starter_calculator.py."""
from herramientas.tools._cocina import CAT, js

KAY = "https://www.kingarthurbaking.com/pro/reference/yeast"
KAS = "https://www.kingarthurbaking.com/recipes/sourdough-starter-recipe"

BODY = r"""
  var mh = ok(v.mh) ? v.mh : 100, YK = { f: 1, s: 0.4, i: 1 / 3 };
  if (mh < 20 || mh > 300) return { err: T.e_mh };
  var mf = 1 / (1 + mh / 100);
  if (v.modo === 'r') {
    var a = v.pm, b = v.ph, c = v.pa;
    if (!ok(a) || !ok(b) || !ok(c) || a <= 0 || b < 0 || c < 0 || a + b + c > 1000) return { err: T.e_parts };
    if (!ok(v.obj) || v.obj <= 0 || v.obj > 1e5) return { err: T.e_obj };
    var k = v.obj / (a + b + c), S = a * k, Fl = b * k, W = c * k;
    var tf = S * mf + Fl, tw = S - S * mf + W, hyd = tf ? tw / tf * 100 : 0;
    return {
      label: T.r_l.replace('{r}', nz(a, 2) + ':' + nz(b, 2) + ':' + nz(c, 2)), big: gr(v.obj) + ' g',
      sub: T.r_sub.replace('{h}', nz(hyd, 1)),
      rows: [[T.starter, gr(S) + ' g'], [T.flour, gr(Fl) + ' g'], [T.water, gr(W) + ' g'], [T.total, gr(v.obj) + ' g', 'tot']],
      note: T.r_note.replace('{x}', nz(a / (a + b + c) * 100, 0)),
      n: { starter: H.r2(S), flour: H.r2(Fl), water: H.r2(W), hyd: H.r2(hyd) }
    };
  }
  if (v.modo === 'c') {
    if (!ok(v.harina) || v.harina <= 0 || v.harina > 1e6) return { err: T.e_harina };
    if (!ok(v.agua) || v.agua < 0) return { err: T.e_agua };
    if (!ok(v.mmp) || v.mmp <= 0 || v.mmp > 100) return { err: T.e_mmp };
    var L = v.harina * v.mmp / 100, Lf = L * mf, Lw = L - Lf;
    if (Lw > v.agua + 0.05) return { err: T.e_wet };
    var rows = [[T.starter + ' · ' + nz(v.mmp, 1) + ' %', gr(L) + ' g'], [T.add_f, gr(v.harina - Lf) + ' g'], [T.add_w, gr(v.agua - Lw) + ' g']];
    if (ok(v.levg) && v.levg > 0) rows.push([T.yeast_out.replace('{g}', gr(v.levg)), '0 g', 'z']);
    rows.push([T.hyd, nz(v.agua / v.harina * 100, 1) + ' %', 'sub']);
    return {
      label: T.c_l, big: gr(L) + ' g', sub: T.c_sub.replace('{f}', gr(Lf)).replace('{w}', gr(Lw)),
      rows: rows, note: T.c_note,
      n: { levain: H.r2(L), addFlour: H.r2(v.harina - Lf), addWater: H.r2(v.agua - Lw) }
    };
  }
  if (!ok(v.cant) || v.cant <= 0 || v.cant > 1e5) return { err: T.e_cant };
  var from = YK[v.desde] ? v.desde : 'f', fresh = v.cant / YK[from], out = {};
  var yrows = ['f', 's', 'i'].map(function (t) { out[t] = fresh * YK[t]; return [T.yt[t], gr(out[t]) + ' g', t === from ? 'sub' : '']; });
  return {
    label: T.y_l.replace('{g}', gr(v.cant)).replace('{t}', T.yt[from].toLowerCase()), big: gr(out[from === 'f' ? 'i' : 'f']) + ' g',
    sub: T.yt[from === 'f' ? 'i' : 'f'], rows: yrows, note: T.y_note,
    n: { f: H.r2(out.f), s: H.r2(out.s), i: H.r2(out.i) }
  };
"""
JS = js(BODY)

T_ES = {
    "e_mh": "Hidratación de tu masa madre: de 20 a 300 %.", "e_parts": "Proporción: escribe las tres partes (la madre, mayor que 0).",
    "e_obj": "Escribe cuánta masa madre quieres.", "e_harina": "Escribe la harina de la receta.", "e_agua": "Escribe el agua de la receta.",
    "e_mmp": "Masa madre: de 1 a 100 % de la harina.", "e_wet": "Esa masa madre aporta más agua que toda la receta: baja el porcentaje o usa una madre más firme.",
    "e_cant": "Escribe los gramos de levadura.",
    "starter": "Masa madre", "flour": "Harina", "water": "Agua", "total": "Total", "hyd": "Hidratación de la masa",
    "add_f": "Harina a añadir", "add_w": "Agua a añadir", "yeast_out": "Levadura ({g} g)",
    "r_l": "Refresco {r}", "r_sub": "Hidratación resultante {h} %",
    "r_note": "La madre es el {x} % del refresco: cuanto menor, más tarda en llegar a su punto.",
    "c_l": "Masa madre para la receta", "c_sub": "Lleva {f} g de harina y {w} g de agua",
    "c_note": "Misma harina total, misma agua total y la misma sal. Cuenta con varias horas más de fermentación que con levadura.",
    "yt": {"f": "Levadura fresca", "s": "Seca activa", "i": "Seca instantánea"},
    "y_l": "{g} g de {t} equivalen a", "y_note": "Equivalencias por poder de fermentación: fresca × 0,4 = seca activa; fresca ÷ 3 = instantánea.",
}
T_EN = {
    "e_mh": "Starter hydration: 20 to 300 %.", "e_parts": "Ratio: enter all three parts (starter above 0).",
    "e_obj": "Enter how much starter you want.", "e_harina": "Enter the flour in the recipe.", "e_agua": "Enter the water in the recipe.",
    "e_mmp": "Starter: 1 to 100 % of the flour.", "e_wet": "That much starter holds more water than the whole recipe: lower the percentage or keep a stiffer starter.",
    "e_cant": "Enter the yeast in grams.",
    "starter": "Starter", "flour": "Flour", "water": "Water", "total": "Total", "hyd": "Dough hydration",
    "add_f": "Flour to add", "add_w": "Water to add", "yeast_out": "Yeast ({g} g)",
    "r_l": "Feed {r}", "r_sub": "Resulting hydration {h} %",
    "r_note": "Starter is {x} % of the feed: the lower it is, the longer it takes to peak.",
    "c_l": "Levain for this recipe", "c_sub": "It holds {f} g flour and {w} g water",
    "c_note": "Same total flour, same total water, same salt. Expect several more hours of fermentation than with yeast.",
    "yt": {"f": "Fresh yeast", "s": "Active dry", "i": "Instant"},
    "y_l": "{g} g {t} equals", "y_note": "Equivalents by leavening power: fresh × 0.4 = active dry; fresh ÷ 3 = instant.",
}


def inputs(lang):
    es = lang == "es"
    ratios = [("111", "1:1:1", {"pm": "1", "ph": "1", "pa": "1"}), ("122", "1:2:2", {"pm": "1", "ph": "2", "pa": "2"}),
              ("133", "1:3:3", {"pm": "1", "ph": "3", "pa": "3"}), ("155", "1:5:5", {"pm": "1", "ph": "5", "pa": "5"}),
              ("11010", "1:10:10", {"pm": "1", "ph": "10", "pa": "10"}), ("125", "1:5:4 (" + ("firme" if es else "stiff") + ")", {"pm": "1", "ph": "5", "pa": "4"}),
              ("x", "Otra" if es else "Other")]
    show_r, show_c, show_y = ("modo", ["r"]), ("modo", ["c"]), ("modo", ["y"])
    return [
        {"id": "modo", "type": "seg", "label": "Calcular" if es else "Calculate", "value": "r",
         "options": [("r", "Refresco" if es else "Feeding"), ("c", "Sin levadura" if es else "Swap yeast"), ("y", "Levaduras" if es else "Yeast types")]},
        {"id": "obj", "type": "number", "label": "Quiero" if es else "I need", "value": 200, "unit": "g", "show": show_r},
        {"id": "prop", "type": "select", "label": "Proporción" if es else "Ratio", "value": "111", "options": ratios, "custom": "x", "show": show_r},
        {"id": "pm", "type": "number", "label": "Madre" if es else "Starter", "value": 1, "w": "s", "step": "0.5", "show": show_r},
        {"id": "ph", "type": "number", "label": "Harina" if es else "Flour", "value": 1, "w": "s", "step": "0.5", "show": show_r},
        {"id": "pa", "type": "number", "label": "Agua" if es else "Water", "value": 1, "w": "s", "step": "0.5", "show": show_r},
        {"id": "harina", "type": "number", "label": "Harina" if es else "Flour", "value": 500, "unit": "g", "show": show_c},
        {"id": "agua", "type": "number", "label": "Agua" if es else "Water", "value": 350, "unit": "g", "show": show_c},
        {"id": "levg", "type": "number", "label": "Levadura" if es else "Yeast", "value": 7, "unit": "g", "w": "s", "show": show_c},
        {"id": "mmp", "type": "number", "label": "Masa madre" if es else "Starter", "value": 20, "unit": "%", "w": "s", "show": show_c},
        {"id": "cant", "type": "number", "label": "Cantidad" if es else "Amount", "value": 25, "unit": "g", "step": "0.5", "show": show_y},
        {"id": "desde", "type": "select", "label": "Tengo" if es else "I have", "value": "f", "show": show_y,
         "options": [("f", "Fresca" if es else "Fresh"), ("s", "Seca activa" if es else "Active dry"), ("i", "Instantánea" if es else "Instant")]},
        {"id": "mh", "type": "number", "label": "Hidratación madre" if es else "Starter hydration", "value": 100, "unit": "%", "w": "s", "more": True},
    ]


TESTS = [
    ({}, {"n.starter": 66.67, "n.flour": 66.67, "n.water": 66.67, "n.hyd": 100}),
    ({"prop": "155", "pm": "1", "ph": "5", "pa": "5", "obj": "220"}, {"n.starter": 20, "n.flour": 100, "n.water": 100}),
    ({"pm": "1", "ph": "2", "pa": "2", "obj": "250", "mh": "50"}, {"n.starter": 50, "n.hyd": 87.5}),
    ({"modo": "c"}, {"n.levain": 100, "n.addFlour": 450, "n.addWater": 300}),
    ({"modo": "c", "agua": "50", "mmp": "100"}, {"err": T_ES["e_wet"]}),
    ({"modo": "y", "cant": "25"}, {"n.s": 10, "n.i": 8.33}),
]

FAQ = [
    ("¿Qué significa refrescar 1:1:1 o 1:5:5?",
     "Son partes en peso de masa madre, harina y agua. 1:1:1 son, por ejemplo, 50 g de madre, 50 g de harina y 50 g de agua. "
     "1:5:5 es 20 g de madre con 100 g de harina y 100 g de agua: la madre queda más diluida y tarda más en llegar a su punto, "
     "útil si la vas a dejar toda la noche."),
    ("¿Cuánta masa madre pongo en lugar de levadura?",
     "Lo más común es entre el 15 y el 25 % del peso de la harina, en masa madre activa (en su punto). Más masa madre acelera la "
     "fermentación y da más acidez; menos la alarga. La calculadora resta la harina y el agua que lleva dentro para que la masa no "
     "cambie de textura."),
    ("¿A cuánto equivale un cubito de levadura fresca en seca?",
     "Un cubito de 25 g de levadura fresca equivale a unos 10 g de levadura seca activa o a unos 8 g de levadura seca instantánea, "
     "que es la de los sobres de supermercado que se mezcla directamente con la harina."),
    ("¿Por qué mi masa madre no sube después del refresco?",
     "Las causas habituales son el frío (por debajo de 20 °C todo va muy lento), un refresco demasiado diluido para el tiempo que le "
     "das, o una madre aún joven. Prueba un refresco 1:1:1 en un sitio templado y espera a que duplique antes de usarla."),
    ("¿Qué es la hidratación de la masa madre?",
     "El agua dividida entre la harina, por 100. Una madre líquida al 100 % lleva el mismo peso de agua que de harina; una firme al "
     "50-60 % lleva la mitad o algo más. Cámbiala en «Más opciones» si la tuya no es al 100 %."),
]


def blocks_es(ctx):
    return [
        ("Refresco: cuánta madre, harina y agua", """
<p>Elige cuánta masa madre necesitas y en qué proporción la refrescas; la calculadora reparte el peso. Para 200 g en 1:1:1 son
<b>67 g de madre, 67 g de harina y 67 g de agua</b>. Si mañana vas a amasar con 150 g de masa madre, prepara algo más (200 g) para
que te quede un poco de madre para el siguiente refresco.</p>
<p>La proporción decide el tiempo. Con harina de trigo y una cocina a 24-26 °C, una madre sana suele duplicar en unas 4-6 horas
con 1:1:1, y necesita bastante más con 1:5:5 o 1:10:10, que son las que se usan para dejarla toda la noche. Son tiempos
orientativos: cada madre, cada harina y cada cocina van a su ritmo, y la señal fiable es que haya duplicado su volumen y tenga
burbujas por toda la masa.</p>"""),
        ("Pasar una receta de levadura a masa madre", """
<p>En «Sin levadura» escribe la harina y el agua de tu receta y qué porcentaje de masa madre quieres (sobre la harina). Para
500 g de harina y 350 g de agua con un 20 % de masa madre al 100 %: usas <b>100 g de masa madre</b> y añades solo 450 g de harina
y 300 g de agua, porque la madre ya trae 50 g de cada. La hidratación sigue en el 70 % y la sal no cambia (unos 10 g, el 2 %).
Quitas toda la levadura.</p>
<p>Lo que sí cambia es el tiempo: una masa con masa madre fermenta en bloque bastante más despacio que con levadura comercial y
suele ganar con un reposo largo en nevera. Mira el volumen de la masa, no el reloj.</p>"""),
        ("Levadura fresca, seca e instantánea", """
<p>Las tres son la misma levadura de panadería (<i>Saccharomyces cerevisiae</i>) con distinta cantidad de agua. Para el mismo
efecto: <b>seca activa = fresca × 0,4</b> e <b>instantánea = fresca ÷ 3</b>. 25 g de fresca son 10 g de seca activa u 8,3 g de
instantánea. La seca activa se suele disolver antes en agua tibia; la instantánea se mezcla directamente con la harina. La masa
madre no tiene una equivalencia fija con la levadura, porque su fuerza depende de lo activa que esté: por eso se calcula como
porcentaje de la harina.</p>"""),
    ]


TOOL = {
    "slug": "masa-madre",
    "lang": "es",
    "twin": "sourdough-starter-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "baguette",
    "order": 20,
    "name": "Masa madre",
    "k": "refresco proporción levadura fresca seca instantánea equivalencia sourdough",
    "title": "Calculadora de masa madre: refresco y levadura",
    "desc": "Calcula el refresco de tu masa madre (1:1:1, 1:5:5…), cuánta usar en lugar de levadura y la equivalencia entre levadura fresca, seca e instantánea.",
    "h1": "Calculadora de masa madre",
    "crumb": "Masa madre",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("King Arthur Baking · Yeast (equivalencias)", KAY), ("King Arthur Baking · Sourdough starter", KAS)],
    "related": ["porcentaje-panadero", "escalar-receta", "temperatura-horno", "tazas-a-gramos"],
    "tests": TESTS,
}
