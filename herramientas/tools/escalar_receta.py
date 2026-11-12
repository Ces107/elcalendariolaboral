"""Escalar receta: scale a recipe by servings or by pan size (round, square, rectangular: by area), and rescale a pasted
ingredient list. English twin: recipe_scaler_pan_size.py."""
from herramientas.tools._cocina import CAT, js

BODY = r"""
  function area(s, a, b) {
    if (!ok(a) || a <= 0) return NaN;
    if (s === 'r') return Math.PI * a * a / 4;
    if (s === 'c') return a * a;
    return ok(b) && b > 0 ? a * b : NaN;
  }
  var k, info;
  if (v.modo === 'm') {
    var A1 = area(v.f1, v.a1, v.lado1), A2 = area(v.f2, v.a2, v.lado2);
    if (!ok(A1)) return { err: T.e_m1 };
    if (!ok(A2)) return { err: T.e_m2 };
    k = A2 / A1;
    info = T.area.replace('{a}', nf(A1, 0)).replace('{b}', nf(A2, 0));
  } else {
    if (!ok(v.r1) || v.r1 <= 0) return { err: T.e_r1 };
    if (!ok(v.r2) || v.r2 <= 0) return { err: T.e_r2 };
    k = v.r2 / v.r1;
    info = T.serv.replace('{a}', nz(v.r1, 1)).replace('{b}', nz(v.r2, 1));
  }
  if (k > 1000 || k < 0.001) return { err: T.e_k };
  var FR = { '½': 0.5, '¼': 0.25, '¾': 0.75, '⅓': 1 / 3, '⅔': 2 / 3, '⅛': 0.125 };
  function qty(s) {
    var m = s.match(/^(\d+)\s*\/\s*(\d+)\s*(.*)$/), x;
    if (m) return +m[2] ? [+m[1] / +m[2], m[3]] : null;
    m = s.match(/^(\d+(?:[.,]\d+)?)(?:\s+(\d+)\s*\/\s*(\d+))?\s*([½¼¾⅓⅔⅛])?\s*(.*)$/);
    if (m) {
      x = parseFloat(m[1].replace(',', '.'));
      if (m[2] !== undefined) { if (!+m[3]) return null; x += +m[2] / +m[3]; }
      if (m[4]) x += FR[m[4]];
      return [x, m[5]];
    }
    m = s.match(/^([½¼¾⅓⅔⅛])\s*(.*)$/);
    return m ? [FR[m[1]], m[2]] : null;
  }
  function nice(x) { return x >= 100 ? nf(Math.round(x)) : x >= 10 ? nz(x, 1) : nz(x, 2); }
  var rows = [], items = [], parts = String(v.ing || '').split(/;|\n|,\s+/).map(function (p) { return p.trim(); }).filter(Boolean);
  parts.slice(0, 40).forEach(function (p) {
    var q = qty(p);
    if (!q || !(q[0] > 0)) { rows.push([H.esc(p), '—', 'z']); items.push(null); return; }
    var y = q[0] * k, egg = /\b(huevos?|yemas?|claras?|eggs?|yolks?|whites?)\b/i.test(q[1]);
    rows.push([H.esc(p), nice(y) + ' ' + H.esc(q[1]) + (egg && Math.abs(y - Math.round(y)) > 0.05 ? ' (≈ ' + Math.max(1, Math.round(y)) + ')' : '')]);
    items.push(H.r2(y));
  });
  var notes = [T.note];
  if (v.modo === 'm') notes.unshift(T.note_m);
  return {
    label: T.lab, big: '× ' + nz(k, 2), sub: info + ' · ' + T.pct.replace('{p}', nf(k * 100, 0)),
    rows: rows, note: notes.join(' '), print: rows.length > 0,
    n: { k: H.r2(k), items: items }
  };
"""
JS = js(BODY)

T_ES = {
    "e_m1": "Escribe las medidas del molde de la receta.", "e_m2": "Escribe las medidas de tu molde.",
    "e_r1": "Escribe las raciones de la receta.", "e_r2": "Escribe cuántas raciones quieres.", "e_k": "Revisa los números: el cambio es demasiado grande.",
    "lab": "Multiplica cada ingrediente por", "area": "{a} cm² → {b} cm²", "serv": "{a} → {b} raciones", "pct": "{p} % de la receta",
    "note_m": "Mismo grosor de masa: si tu molde es más alto o más bajo, ajusta también el tiempo de horno.",
    "note": "Los huevos se redondean al final; la sal, la levadura y las especias, mejor ajustarlas a tu gusto.",
}
T_EN = {
    "e_m1": "Enter the recipe's pan size.", "e_m2": "Enter your pan size.",
    "e_r1": "Enter the recipe's servings.", "e_r2": "Enter how many servings you want.", "e_k": "Check the numbers: that change is too large.",
    "lab": "Multiply every ingredient by", "area": "{a} → {b} square units", "serv": "{a} → {b} servings", "pct": "{p} % of the recipe",
    "note_m": "Same batter depth assumed: in a deeper or shallower pan, adjust the baking time too.",
    "note": "Round eggs at the end; salt, leavening and spices are best adjusted to taste.",
}


def inputs(lang):
    es = lang == "es"
    shapes = [("r", "Redondo" if es else "Round"), ("c", "Cuadrado" if es else "Square"), ("x", "Rectangular" if es else "Rectangle")]
    u = "cm" if es else ""
    lab_a = {"es": "Diámetro o lado", "en": "Diameter or side"}[lang]
    m = ("modo", ["m"])
    return [
        {"id": "modo", "type": "seg", "label": "Escalar por" if es else "Scale by", "value": "r",
         "options": [("r", "Raciones" if es else "Servings"), ("m", "Molde" if es else "Pan size")]},
        {"id": "r1", "type": "number", "label": "Receta" if es else "Recipe", "value": 4, "w": "s", "step": "0.5", "show": ("modo", ["r"])},
        {"id": "r2", "type": "number", "label": "Quiero" if es else "I need", "value": 6, "w": "s", "step": "0.5", "show": ("modo", ["r"])},
        {"id": "f1", "type": "select", "label": "Molde receta" if es else "Recipe pan", "value": "r", "options": shapes, "show": m},
        {"id": "a1", "type": "number", "label": lab_a, "value": 20 if es else 8, "unit": u, "w": "s", "step": "0.5", "show": m},
        {"id": "lado1", "type": "number", "label": "Otro lado" if es else "Other side", "value": "", "unit": u, "w": "s", "step": "0.5", "show": m},
        {"id": "f2", "type": "select", "label": "Mi molde" if es else "My pan", "value": "r", "options": shapes, "show": m},
        {"id": "a2", "type": "number", "label": lab_a, "value": 24 if es else 9, "unit": u, "w": "s", "step": "0.5", "show": m},
        {"id": "lado2", "type": "number", "label": "Otro lado" if es else "Other side", "value": "", "unit": u, "w": "s", "step": "0.5", "show": m},
        {"id": "ing", "type": "text", "label": "Ingredientes" if es else "Ingredients", "value": "", "w": "xl", "maxlength": 1200,
         "placeholder": "200 g harina; 3 huevos; 1/2 cucharadita de sal" if es else "2 1/4 cups flour; 2 eggs; 1/2 tsp salt"},
    ]


TESTS = [
    ({}, {"n.k": 1.5}),
    ({"modo": "m"}, {"n.k": 1.44}),
    ({"modo": "m", "a1": "22", "f2": "c", "a2": "20"}, {"n.k": 1.05}),
    ({"modo": "m", "f1": "x", "a1": "30", "lado1": "20", "a2": "26"}, {"n.k": 0.88}),
    ({"ing": "200 g harina; 3 huevos; 1/2 cdta sal, 1,5 dl leche"}, {"n.items": [300, 4.5, 0.75, 2.25]}),
    ({"r1": "0"}, {"err": T_ES["e_r1"]}),
]

FAQ = [
    ("¿Cómo adapto una receta de un molde de 20 cm a uno de 24 cm?",
     "Multiplica los ingredientes por la relación entre las superficies: (24 ÷ 20)² = 1,44. Un molde de 24 cm tiene un 44 % más de "
     "superficie que uno de 20 cm, aunque el diámetro solo sea un 20 % mayor. Para 22 cm el factor es 1,21; para 26 cm, 1,69."),
    ("¿Y si paso de un molde redondo a uno cuadrado o rectangular?",
     "Compara superficies: la de un molde redondo es π × diámetro² ÷ 4 y la de uno rectangular, largo × ancho. Un redondo de 22 cm "
     "(380 cm²) equivale casi a un cuadrado de 20 cm (400 cm²). Elige la forma de cada molde y la calculadora hace la cuenta."),
    ("¿Cómo divido una receta con 3 huevos a la mitad?",
     "Salen 1,5 huevos. Bate dos huevos y usa tres cuartas partes, o usa un huevo y una yema. En general un huevo M pesa unos 50 g sin "
     "cáscara: pesa el batido y quédate con 75 g."),
    ("¿Hay que cambiar el tiempo de horno?",
     "Si mantienes la misma altura de masa, el tiempo cambia poco. Si la masa queda más alta (molde más pequeño para la misma "
     "cantidad), necesita más tiempo y a veces bajar 10 °C para que no se queme por fuera. Comprueba con un palillo."),
    ("¿Puedo pegar la lista de ingredientes?",
     "Sí: escribe cada ingrediente empezando por la cantidad y sepáralos con punto y coma («200 g harina; 3 huevos»). Acepta decimales "
     "con coma y fracciones como 1/2 o ½."),
]


def blocks_es(ctx):
    return [
        ("Cómo se calcula", """
<p>Por raciones, el factor es simplemente <b>raciones que quieres ÷ raciones de la receta</b>: de 4 a 6 personas, × 1,5. Por
molde, lo que cuenta es la superficie, no el diámetro. Un molde redondo de 20 cm tiene 314 cm² y uno de 24 cm, 452 cm²: el factor
es <b>1,44</b>, no 1,2. Por eso un bizcocho pensado para 20 cm queda bajo y seco si lo haces tal cual en un molde de 24 cm.</p>
<p>Pega la lista de ingredientes y la calculadora multiplica cada cantidad. Con un factor de 1,44, una receta de 200 g de harina,
150 g de azúcar, 3 huevos y 100 ml de aceite pasa a <b>288 g de harina, 216 g de azúcar, 4,32 huevos (4 huevos M) y 144 ml de
aceite</b>.</p>"""),
        ("Superficies de los moldes más comunes", """
<table class="tbl"><thead><tr><th>Molde</th><th>Superficie</th><th>Factor desde 20 cm</th></tr></thead><tbody>
<tr><td>Redondo 18 cm</td><td class="num">254 cm²</td><td class="num">0,81</td></tr>
<tr><td>Redondo 20 cm</td><td class="num">314 cm²</td><td class="num">1</td></tr>
<tr><td>Redondo 22 cm</td><td class="num">380 cm²</td><td class="num">1,21</td></tr>
<tr><td>Redondo 24 cm</td><td class="num">452 cm²</td><td class="num">1,44</td></tr>
<tr><td>Redondo 26 cm</td><td class="num">531 cm²</td><td class="num">1,69</td></tr>
<tr><td>Cuadrado 20 cm</td><td class="num">400 cm²</td><td class="num">1,27</td></tr>
<tr><td>Rectangular 30 × 20 cm</td><td class="num">600 cm²</td><td class="num">1,91</td></tr>
</tbody></table>
<p>Lo que no se escala igual: la sal, las especias y la levadura química suelen funcionar bien escaladas en recetas pequeñas, pero
si multiplicas por más de 2 conviene probar y ajustar. Y el tiempo de horno depende de la altura de la masa, no de la cantidad.</p>"""),
    ]


TOOL = {
    "slug": "escalar-receta",
    "lang": "es",
    "twin": "recipe-scaler-pan-size",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "tools-kitchen-2",
    "order": 80,
    "name": "Escalar receta",
    "k": "raciones personas molde redondo cuadrado diámetro adaptar receta bizcocho tarta",
    "title": "Adaptar receta a otro molde o raciones",
    "desc": "Calcula cuánto multiplicar una receta para más o menos raciones o para otro molde (redondo, cuadrado o rectangular) y reescala la lista de ingredientes.",
    "h1": "Adaptar una receta a otro molde o raciones",
    "crumb": "Escalar receta",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("NIST · Conversión de unidades", "https://www.nist.gov/pml/owm/metric-si/unit-conversion")],
    "related": ["tazas-a-gramos", "porcentaje-panadero", "temperatura-horno", "cantidades-fiesta"],
    "tests": TESTS,
}
