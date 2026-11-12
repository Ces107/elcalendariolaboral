"""Cantidades para una fiesta: food and drink by guest (paella rice, jamón, bread, tapas, beer, wine, cava, soft
drinks, water, ice) by type of party and hours. Portions anchored on AESAN serving sizes; party rules of thumb stated as
such. English twin: party_food_calculator.py."""
from herramientas.tools._cocina import CAT, js

AESAN = "https://www.aesan.gob.es/dam/jcr:d703fdbe-840d-4a49-ae2d-2f2e48e3f8bd/alimentacion_sana_todos.pdf.pdf"

# food: id, grams (or pieces) per adult for [comida, picoteo, coctel], unit 'g' | 'u', check input id or '', scales with hours
FOOD_ES = [["arroz", [100, 0, 0], "g", "paella", 0], ["jamon", [40, 60, 80], "g", "jamon", 0], ["pan", [60, 40, 60], "g", "", 0],
           ["bocados", [4, 3, 5], "u", "", 1]]
FOOD_EN = [["turkey", [453.6, 0, 0], "g", "turkey", 0], ["main", [225, 0, 0], "g", "plato", 0], ["sides", [150, 0, 0], "g", "", 0],
           ["rolls", [1.5, 0, 1], "u", "", 0], ["bocados", [4, 3, 5], "u", "", 1]]

BODY = r"""
  var a = v.adultos, k = ok(v.ninos) ? v.ninos : 0, h = v.horas, m = ok(v.margen) ? v.margen : 10, ti = { comida: 0, picoteo: 1, coctel: 2 }[v.tipo] || 0;
  if (!ok(a) || a < 0 || a > 5000 || Math.round(a) !== a) return { err: T.e_ad };
  if (k < 0 || k > 5000 || Math.round(k) !== k) return { err: T.e_ni };
  if (a + k === 0) return { err: T.e_ad };
  if (!ok(h) || h < 1 || h > 24) return { err: T.e_h };
  if (m < 0 || m > 100) return { err: T.e_m };
  function cl(x) { return Math.ceil(x - 1e-9); }
  var M = 1 + m / 100, rows = [], n = {}, people = a + k / 2;
  function kg(g) { return g >= 1000 ? nz(g / 1000, 1) + ' kg' : nf(cl(g / 10) * 10, 0) + ' g'; }
  function us(g) { return g >= 453.6 ? ' · ' + nz(g / 453.592, 1) + ' lb' : ' · ' + nz(g / 28.3495, 0) + ' oz'; }
  D.food.forEach(function (f) {
    if (f[3] && !v[f[3]]) return;
    var per = f[1][ti]; if (!per) return;
    var q = per * people * M;
    if (f[4]) q = ti === 0 ? q : q * Math.max(2, h);
    n[f[0]] = H.r2(q);
    var txt = f[2] === 'u' ? nf(cl(q), 0) + ' ' + T.u : kg(q) + (EN ? us(q) : '');
    if (f[0] === 'jamon') txt += ' · ' + T.ham.replace('{n}', nz(cl(q / 3500 * 2) / 2, 1));
    rows.push([T.f[f[0]], txt]);
  });
  var drinks = a * (2 + (h - 1)) * M, kids = k * (1 + h) * M;
  var beer = drinks * 0.4, wine = drinks * 0.25, soft = drinks * 0.35 + kids;
  if (v.sinalc) { soft += beer + wine; beer = 0; wine = 0; }
  if (beer) rows.push([T.beer, nf(cl(beer), 0) + ' ' + T.beer_u]);
  if (wine) rows.push([T.wine, nf(cl(wine / 5), 0) + ' ' + T.bottles + ' (' + nf(cl(wine), 0) + ' ' + T.glasses + ')']);
  if (v.cava && !v.sinalc && a) rows.push([T.cava, nf(cl(a * M / 6), 0) + ' ' + T.bottles]);
  rows.push([T.soft, nz(cl(soft * 0.33), 0) + ' L']);
  var water = (a + k) * (0.2 * h + 0.3) * M;
  rows.push([T.water, nz(cl(water), 0) + ' L'], [T.ice, nz(cl((a + k) * 0.5 * M), 0) + ' kg']);
  n.beer = cl(beer); n.wineBottles = cl(wine / 5); n.cava = v.cava && !v.sinalc ? cl(a * M / 6) : 0;
  n.soft = cl(soft * 0.33); n.water = cl(water); n.ice = cl((a + k) * 0.5 * M);
  return {
    label: T.lab.replace('{a}', a).replace('{k}', k ? ' + ' + k + ' ' + T.kids : ''), big: nf(cl(drinks + kids), 0) + ' ' + T.drinks,
    sub: T.types[ti] + ' · ' + h + ' h · ' + T.marg.replace('{m}', nz(m, 0)), rows: rows, note: T.note, print: true, n: n
  };
"""
JS = js(BODY)

T_ES = {
    "e_ad": "Escribe cuántos adultos vienen.", "e_ni": "Niños: un número entero.", "e_h": "Duración: de 1 a 24 horas.", "e_m": "Margen: de 0 a 100 %.",
    "f": {"arroz": "Arroz para paella (crudo)", "jamon": "Jamón loncheado", "pan": "Pan", "bocados": "Tapas y canapés"},
    "u": "piezas", "ham": "≈ {n} jamones de 7-8 kg", "beer": "Cerveza", "beer_u": "botellines o latas de 33 cl", "wine": "Vino",
    "bottles": "botellas", "glasses": "copas", "cava": "Cava para el brindis", "soft": "Refrescos y bebidas sin alcohol",
    "water": "Agua", "ice": "Hielo", "kids": "niños", "drinks": "bebidas", "lab": "{a} adultos{k}",
    "types": ["Comida o cena", "Picoteo o vermú", "Cóctel o cena de picoteo"], "marg": "margen {m} %",
    "note": "Estimación con margen: sobra mejor que falta. Ten siempre agua y bebidas sin alcohol de sobra.",
}
T_EN = {
    "e_ad": "Enter how many adults are coming.", "e_ni": "Children: a whole number.", "e_h": "Length: 1 to 24 hours.", "e_m": "Margin: 0 to 100 %.",
    "f": {"turkey": "Whole turkey (bone-in)", "main": "Main: boneless meat or fish", "sides": "Each side dish", "rolls": "Bread rolls",
          "bocados": "Appetizers and canapés"},
    "u": "pieces", "ham": "", "beer": "Beer", "beer_u": "bottles or cans (12 oz)", "wine": "Wine", "bottles": "bottles", "glasses": "glasses",
    "cava": "Sparkling wine for a toast", "soft": "Soft drinks and alcohol-free", "water": "Water", "ice": "Ice", "kids": "kids",
    "drinks": "drinks", "lab": "{a} adults{k}", "types": ["Sit-down meal", "Drinks and nibbles", "Cocktail party (as dinner)"],
    "marg": "{m} % margin", "note": "Estimates with a margin: running out is worse than leftovers. Always have plenty of water and alcohol-free drinks.",
}


def inputs(lang):
    es = lang == "es"
    out = [
        {"id": "adultos", "type": "number", "label": "Adultos" if es else "Adults", "value": 20, "w": "s"},
        {"id": "ninos", "type": "number", "label": "Niños" if es else "Kids", "value": 0, "w": "s"},
        {"id": "tipo", "type": "seg", "label": "Tipo" if es else "Party", "value": "comida",
         "options": [("comida", "Comida" if es else "Meal"), ("picoteo", "Picoteo" if es else "Nibbles"), ("coctel", "Cóctel" if es else "Cocktail")]},
        {"id": "horas", "type": "number", "label": "Duración" if es else "Length", "value": 4, "unit": "h", "w": "s"},
    ]
    if es:
        out += [{"id": "paella", "type": "check", "label": "Paella", "value": True, "show": ("tipo", ["comida"])},
                {"id": "jamon", "type": "check", "label": "Jamón", "value": True}]
    else:
        out += [{"id": "turkey", "type": "check", "label": "Turkey", "value": False, "show": ("tipo", ["comida"])},
                {"id": "plato", "type": "check", "label": "Other main", "value": True, "show": ("tipo", ["comida"])}]
    out += [{"id": "cava", "type": "check", "label": "Brindis" if es else "Toast", "value": False},
            {"id": "sinalc", "type": "check", "label": "Sin alcohol" if es else "No alcohol", "value": False, "more": True},
            {"id": "margen", "type": "number", "label": "Margen" if es else "Margin", "value": 10, "unit": "%", "w": "s", "more": True}]
    return out


TESTS = [
    ({}, {"n.arroz": 2200, "n.jamon": 880, "n.pan": 1320, "n.beer": 44, "n.wineBottles": 6, "n.water": 25, "n.ice": 11}),
    ({"tipo": "picoteo", "horas": "3", "adultos": "10"}, {"n.jamon": 660, "n.bocados": 99, "n.beer": 18}),
    ({"adultos": "10", "ninos": "4", "cava": True}, {"n.arroz": 1320, "n.cava": 2}),
    ({"sinalc": True}, {"n.beer": 0, "n.soft": 37}),
    ({"adultos": "0"}, {"err": T_ES["e_ad"]}),
]

FAQ = [
    ("¿Cuánto arroz por persona para una paella?",
     "Unos 100 g de arroz crudo por adulto cuando la paella es el plato principal, y la mitad para los niños. Es algo más que la ración "
     "de 60-80 g que da la AESAN para un plato normal de arroz, porque en una celebración la paella suele ser plato único."),
    ("¿Cuánto jamón por persona?",
     "Como entrante de una comida, unos 40 g por persona; en un picoteo, 60 g, y si el jamón es casi la cena (cóctel), 80 g. Un jamón "
     "de 7-8 kg rinde unos 3,5 kg de jamón loncheado, así que da para unas 45 personas en un picoteo."),
    ("¿Cuántas cervezas y botellas de vino comprar?",
     "Una regla habitual es contar dos bebidas por adulto en la primera hora y una más por cada hora siguiente, y repartirlas entre "
     "cerveza, vino y bebidas sin alcohol. Para 20 adultos en una comida de 4 horas son 100 bebidas, 110 con un 10 % de "
     "margen: unas 44 cervezas, 6 botellas de vino y 13 litros de refrescos."),
    ("¿Cuántas copas salen de una botella?",
     "De una botella de 75 cl salen unas 5 copas de vino de 150 ml o 6 copas de cava de 125 ml para el brindis."),
    ("¿Cuánto hielo necesito?",
     "Calcula medio kilo por persona para enfriar bebidas y servir copas. Si tienes que enfriar las botellas en barreño, compra el doble."),
]


def blocks_es(ctx):
    return [
        ("Cómo se calcula", """
<p>Escribe cuántos adultos y niños vienen, qué tipo de celebración es y cuánto va a durar. La comida se calcula por persona (los
niños cuentan como medio adulto) y la bebida por horas: <b>dos bebidas por adulto la primera hora y una más por cada hora
siguiente</b>, repartidas en un 40 % de cerveza, un 25 % de vino y un 35 % de bebidas sin alcohol. Todo lleva un 10 % de margen
que puedes cambiar en «Más opciones».</p>
<p>Ejemplo: una comida de 20 adultos durante 4 horas con paella y jamón de entrante. Arroz: 100 g × 20 × 1,10 = <b>2,2 kg</b>.
Jamón: 40 g × 20 × 1,10 = 880 g loncheado. Bebida: 20 × (2 + 3) × 1,10 = 110 bebidas: 44 cervezas, 6 botellas de vino
(28 copas) y 13 litros de refrescos, más 25 litros de agua y 11 kg de hielo.</p>"""),
        ("De dónde salen las raciones", """
<p>La Agencia Española de Seguridad Alimentaria y Nutrición (AESAN), en su guía <i>Una alimentación sana para todos</i>, da como
ración de arroz o pasta 60-80 g en crudo, de pan 40-60 g, de carne 100-125 g y de pescado 125-150 g. En una fiesta se come algo
más que en un día normal y la paella suele ser plato único, por eso aquí se cuentan 100 g de arroz por adulto y 60 g de pan en
las comidas. El reparto de las bebidas y los bocados del picoteo (3 por persona y hora; 5 si el cóctel sustituye a la cena)
son reglas habituales de catering, no una norma: si tus invitados son de mucho comer, sube el margen.</p>
<p>La misma guía recomienda evitar el alcohol o tomarlo con moderación. Ten agua y bebidas sin alcohol de sobra, y si hay
conductores, marca «Sin alcohol» para ver cuánto refresco hace falta si nadie bebe.</p>"""),
    ]


TOOL = {
    "slug": "cantidades-fiesta",
    "lang": "es",
    "twin": "party-food-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "glass-champagne",
    "order": 110,
    "name": "Cantidades para fiesta",
    "k": "invitados comida bebida cerveza vino cava hielo paella jamón cumpleaños boda comunión barbacoa",
    "title": "Cuánta comida y bebida para una fiesta por persona",
    "desc": "Calcula cuánta comida y bebida comprar según los invitados: arroz para paella, jamón, pan, tapas, cerveza, vino, cava, refrescos, agua y hielo.",
    "h1": "Calculadora de comida y bebida para fiestas",
    "crumb": "Cantidades para fiesta",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES, "food": FOOD_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("AESAN · Una alimentación sana para todos (raciones)", AESAN)],
    "related": ["escalar-receta", "tiempo-asado", "ratio-cafe", "azucar-mermelada"],
    "tests": TESTS,
}
