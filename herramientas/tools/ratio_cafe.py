"""Ratio de café: grams of coffee and water for filter (V60, Chemex), French press, moka, cold brew and espresso
from a brew ratio. English twin: coffee_ratio_calculator.py."""
from herramientas.tools._cocina import CAT, js

SCA = "https://sca.coffee/research/coffee-standards"

BODY = r"""
  var r = v.rat, esp = ok(r) && r <= 4, cold = v.met === 'cold';
  if (!ok(r) || r < 1 || r > 30) return { err: T.e_rat };
  var W, Cg;
  if (v.base === 'cafe') {
    if (!ok(v.cafe) || v.cafe <= 0 || v.cafe > 5000) return { err: T.e_cafe };
    Cg = v.cafe; W = Cg * r;
  } else if (v.base === 'tazas') {
    if (!ok(v.tazas) || v.tazas <= 0 || v.tazas > 200) return { err: T.e_tazas };
    if (!ok(v.ml) || v.ml <= 0 || v.ml > 2000) return { err: T.e_ml };
    W = v.tazas * v.ml; Cg = W / r;
  } else {
    if (!ok(v.agua) || v.agua <= 0 || v.agua > 1e5) return { err: T.e_agua };
    W = v.agua; Cg = W / r;
  }
  var rows, sub, note;
  if (esp) {
    rows = [[T.dose, nz(Cg, 1) + ' g', 'tot'], [T.yield, nz(W, 1) + ' g'], [T.ratio, '1:' + nz(r, 2), 'sub']];
    sub = T.sub_esp.replace('{w}', nz(W, 1)); note = T.note_esp + (v.base !== 'cafe' ? ' ' + T.esp_hint : '');
  } else {
    var drink = Math.max(0, W - 2 * Cg);
    rows = [[T.coffee, gr(Cg) + ' g', 'tot'], [T.water, nf(W, 0) + ' ml (g)'], [T.drink, '≈ ' + nf(drink, 0) + ' ml'],
            [T.gl, nz(1000 / r, 1) + ' g/L', 'sub'], [T.ratio, '1:' + nz(r, 2), 'sub']];
    sub = T.sub.replace('{w}', nf(W, 0)); note = cold ? T.note_cold : T.note;
  }
  return { label: T.names[v.met] || T.lab, big: gr(Cg) + ' g', sub: sub, rows: rows, note: note,
           n: { coffee: H.r2(Cg), water: H.r2(W) } };
"""
JS = js(BODY)

NAMES_ES = {"filtro": "Filtro · V60 · Chemex", "sca": "Golden Cup (SCA)", "prensa": "Prensa francesa", "moka": "Cafetera italiana",
            "cold": "Cold brew (concentrado)", "esp": "Espresso", "rist": "Ristretto", "lungo": "Lungo", "x": "Tu proporción"}
NAMES_EN = {"filtro": "Pour-over · V60 · Chemex", "sca": "SCA Golden Cup", "prensa": "French press", "moka": "Moka pot",
            "cold": "Cold brew concentrate", "esp": "Espresso", "rist": "Ristretto", "lungo": "Lungo", "x": "Your ratio"}

T_ES = {"e_rat": "Proporción entre 1:1 y 1:30.", "e_cafe": "Escribe los gramos de café.", "e_tazas": "Escribe el número de tazas.",
        "e_ml": "Escribe los ml de cada taza.", "e_agua": "Escribe el agua en ml.", "names": NAMES_ES, "lab": "Café",
        "coffee": "Café molido", "water": "Agua", "drink": "Café en la taza", "gl": "Concentración", "ratio": "Proporción",
        "dose": "Dosis de café", "yield": "Bebida en la taza (peso)", "sub": "para {w} ml de agua", "sub_esp": "para {w} g de bebida",
        "note": "El poso retiene unos 2 g de agua por gramo de café, por eso sale algo menos de lo que echas.",
        "note_cold": "Concentrado: deja en la nevera 12-24 h, filtra y sirve mezclado con la misma cantidad de agua o leche.",
        "note_esp": "En espresso la proporción se mide en peso de bebida, no en agua: pesa la taza.",
        "esp_hint": "Lo normal es partir de la dosis: elige «Café» y escribe, por ejemplo, 18 g."}
T_EN = {"e_rat": "Ratio between 1:1 and 1:30.", "e_cafe": "Enter the coffee in grams.", "e_tazas": "Enter the number of cups.",
        "e_ml": "Enter the size of each cup in ml.", "e_agua": "Enter the water in ml.", "names": NAMES_EN, "lab": "Coffee",
        "coffee": "Ground coffee", "water": "Water", "drink": "Coffee in the cup", "gl": "Strength", "ratio": "Ratio",
        "dose": "Coffee dose", "yield": "Beverage weight (yield)", "sub": "for {w} ml of water", "sub_esp": "for {w} g of espresso",
        "note": "Spent grounds hold about 2 g of water per gram of coffee, so you get a little less than you pour.",
        "note_cold": "Concentrate: steep 12-24 h in the fridge, strain, then dilute 1:1 with water or milk.",
        "note_esp": "Espresso ratios are by beverage weight, not water: put the cup on a scale.",
        "esp_hint": "Espresso usually starts from the dose: choose «Coffee» and enter, say, 18 g."}


def inputs(lang):
    es = lang == "es"
    n = NAMES_ES if es else NAMES_EN
    mets = [("filtro", 16), ("sca", 18.2), ("prensa", 15), ("moka", 10), ("cold", 8), ("esp", 2), ("rist", 1.5), ("lungo", 3)]
    opts = [(k, f"{n[k]} (1:{str(r).replace('.', ',') if es else r})", {"rat": str(r).replace(".", ",") if es else str(r)}) for k, r in mets] + [("x", n["x"])]
    return [
        {"id": "met", "type": "select", "label": "Método" if es else "Method", "value": "filtro", "options": opts, "custom": "x", "w": "l"},
        {"id": "base", "type": "seg", "label": "Parto de" if es else "I know", "value": "agua",
         "options": [("agua", "Agua" if es else "Water"), ("cafe", "Café" if es else "Coffee"), ("tazas", "Tazas" if es else "Cups")]},
        {"id": "agua", "type": "number", "label": "Agua" if es else "Water", "value": 500, "unit": "ml", "w": "s", "show": ("base", ["agua"])},
        {"id": "cafe", "type": "number", "label": "Café" if es else "Coffee", "value": 30, "unit": "g", "w": "s", "step": "0.1", "show": ("base", ["cafe"])},
        {"id": "tazas", "type": "number", "label": "Tazas" if es else "Cups", "value": 2, "w": "s", "show": ("base", ["tazas"])},
        {"id": "ml", "type": "number", "label": "Cada taza" if es else "Each cup", "value": 250, "unit": "ml", "w": "s", "show": ("base", ["tazas"])},
        {"id": "rat", "type": "number", "label": "Proporción 1:" if es else "Ratio 1:", "value": 16, "w": "s", "step": "0.1"},
    ]


TESTS = [
    ({}, {"n.coffee": 31.25, "n.water": 500}),
    ({"base": "cafe", "cafe": "30", "met": "prensa", "rat": "15"}, {"n.water": 450}),
    ({"base": "tazas", "met": "sca", "rat": "18,2"}, {"n.coffee": 27.47}),
    ({"met": "esp", "rat": "2", "base": "cafe", "cafe": "18"}, {"n.water": 36}),
    ({"rat": "0"}, {"err": T_ES["e_rat"]}),
]

FAQ = [
    ("¿Cuántos gramos de café por taza?",
     "Para café de filtro, unos 15-16 g por cada taza de 250 ml de agua (proporción 1:16). La referencia Golden Cup de la Specialty "
     "Coffee Association son 55 g por litro, unos 8,25 g por cada 150 ml, algo más suave. En prensa francesa se usa algo más de café, "
     "unos 17 g por cada 250 ml."),
    ("¿Qué significa una proporción 1:16?",
     "Un gramo de café por cada 16 gramos (o mililitros) de agua. 30 g de café con 480 ml de agua es 1:16. Cuanto más bajo el segundo "
     "número, más cargado sale el café."),
    ("¿Cuánto café lleva un espresso?",
     "Un espresso doble usa unos 16-20 g de café molido y se extrae hasta unos 32-40 g de bebida en la taza (proporción 1:2), en unos "
     "25-30 segundos. Un ristretto se corta antes (1:1,5) y un lungo se alarga (1:3)."),
    ("¿Cuánto café para la cafetera italiana?",
     "Se llena el filtro a ras sin apretar y el agua hasta la válvula: la proporción sale en torno a 1:10, más fuerte que un filtro. "
     "En una italiana de 3 tazas son unos 15-17 g de café con 150-170 ml de agua."),
    ("¿Cómo se hace el cold brew?",
     "Café molido grueso con agua fría en proporción 1:8 para un concentrado, 12 a 24 horas en la nevera, se filtra y se sirve con la "
     "misma cantidad de agua o leche. Para tomar sin diluir, usa 1:15 o 1:16."),
]


def blocks_es(ctx):
    return [
        ("Cómo se calcula", """
<p>Elige el método, cuánta agua vas a usar (o cuánto café tienes, o cuántas tazas quieres) y la proporción. El café es
<b>agua ÷ proporción</b>: para 500 ml de agua a 1:16 son <b>31 g de café</b>. Al revés, con 30 g de café a 1:15 en prensa francesa
necesitas 450 ml de agua. El agua se puede medir en mililitros o en gramos, porque un mililitro de agua pesa un gramo.</p>
<p>No todo el agua llega a la taza: el café molido retiene alrededor de 2 g de agua por cada gramo, así que de esos 500 ml
saldrán unos 440 ml de café. En espresso la proporción se mide sobre el peso de la bebida: 18 g de café a 1:2 son 36 g de
espresso en la taza.</p>"""),
        ("Proporciones de referencia", """
<table class="tbl"><thead><tr><th>Método</th><th>Proporción</th><th>Para 500 ml</th></tr></thead><tbody>
<tr><td>Filtro, V60, Chemex</td><td class="num">1:15 a 1:17</td><td class="num">29-33 g</td></tr>
<tr><td>Golden Cup (SCA)</td><td class="num">1:18,2 (55 g/L)</td><td class="num">27,5 g</td></tr>
<tr><td>Prensa francesa</td><td class="num">1:12 a 1:15</td><td class="num">33-42 g</td></tr>
<tr><td>Cafetera italiana</td><td class="num">≈ 1:10</td><td class="num">50 g</td></tr>
<tr><td>Cold brew concentrado</td><td class="num">1:8</td><td class="num">62,5 g</td></tr>
<tr><td>Espresso</td><td class="num">1:2 (en bebida)</td><td class="num">—</td></tr>
</tbody></table>
<p>Son puntos de partida. Si el café sale aguado o ácido, baja la proporción (más café) o muele más fino; si sale amargo y áspero,
súbela o muele más grueso. Cambia una sola cosa cada vez y apunta el resultado.</p>"""),
    ]


TOOL = {
    "slug": "ratio-cafe",
    "lang": "es",
    "twin": "coffee-ratio-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "coffee",
    "order": 90,
    "name": "Ratio de café",
    "k": "proporción café agua gramos v60 chemex prensa francesa espresso italiana cold brew",
    "title": "Proporción café y agua: gramos para V60, prensa y espresso",
    "desc": "Calcula cuántos gramos de café y de agua usar en filtro V60, Chemex, prensa francesa, cafetera italiana, cold brew o espresso según la proporción.",
    "h1": "Calculadora de proporción de café",
    "crumb": "Ratio de café",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("Specialty Coffee Association · Coffee standards", SCA)],
    "related": ["cerveza-casera", "tazas-a-gramos", "cantidades-fiesta", "temperatura-horno"],
    "tests": TESTS,
}
