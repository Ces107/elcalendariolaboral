"""Tazas a gramos: cups, spoons, yogurt pots and ml to grams (and back) by ingredient, with the cup weights of USDA
FoodData Central (SR Legacy, public domain). English twin: cups_to_grams.py."""
from herramientas.tools._cocina import CAT, js

FDC = "https://fdc.nal.usda.gov/"
FDC_DL = "https://fdc.nal.usda.gov/download-datasets"
NIST = "https://www.nist.gov/pml/owm/metric-si/unit-conversion"

# id, Spanish, English, grams per US cup (236.6 ml), FDC id (SR Legacy, food_portion)
ING = [
    ("harina", "Harina de trigo común", "All-purpose flour", 125, 168894),
    ("fuerza", "Harina de fuerza (panificable)", "Bread flour", 137, 168896),
    ("integral", "Harina integral", "Whole wheat flour", 120, 168893),
    ("centeno", "Harina de centeno", "Rye flour (medium)", 102, 168886),
    ("maicena", "Maicena (almidón de maíz)", "Cornstarch", 128, 169698),
    ("arrozh", "Harina de arroz", "Rice flour", 158, 169714),
    ("semola", "Sémola de trigo", "Semolina", 167, 169715),
    ("maiz", "Harina de maíz (polenta)", "Cornmeal", 122, 169697),
    ("almendra", "Almendra molida", "Ground almonds", 95, 170567),
    ("azucar", "Azúcar blanco", "Granulated sugar", 200, 169655),
    ("moreno", "Azúcar moreno (apretado)", "Brown sugar (packed)", 220, 168833),
    ("glas", "Azúcar glas (sin tamizar)", "Powdered sugar (unsifted)", 120, 169656),
    ("miel", "Miel", "Honey", 339, 169640),
    ("arce", "Sirope de arce", "Maple syrup", 315, 169661),
    ("mantequilla", "Mantequilla", "Butter", 227, 173430),
    ("aceite", "Aceite de oliva", "Olive oil", 216, 171413),
    ("girasol", "Aceite de girasol", "Sunflower or canola oil", 218, 171025),
    ("leche", "Leche entera", "Whole milk", 244, 171265),
    ("nata", "Nata para montar", "Heavy cream", 238, 170859),
    ("yogur", "Yogur natural", "Plain yogurt", 245, 171284),
    ("agua", "Agua", "Water", 237, 174158),
    ("huevo", "Huevo batido", "Beaten egg", 243, 171287),
    ("cacao", "Cacao en polvo sin azúcar", "Unsweetened cocoa powder", 86, 169593),
    ("sal", "Sal fina", "Table salt", 292, 173468),
    ("polvo", "Levadura química (polvo de hornear)", "Baking powder", 220.8, 172803),
    ("bicarb", "Bicarbonato sódico", "Baking soda", 220.8, 175040),
    ("levseca", "Levadura seca de panadería", "Active dry yeast", 192, 175043),
    ("avena", "Copos de avena", "Rolled oats", 81, 173904),
    ("arrozr", "Arroz redondo (crudo)", "Short-grain rice (raw)", 200, 168931),
    ("arrozl", "Arroz largo (crudo)", "Long-grain rice (raw)", 185, 168877),
    ("lenteja", "Lentejas (crudas)", "Lentils (dry)", 192, 172420),
    ("garbanzo", "Garbanzos (crudos)", "Chickpeas (dry)", 200, 173756),
    ("chocolate", "Pepitas de chocolate", "Chocolate chips", 168, 167976),
    ("pasas", "Pasas", "Raisins", 145, 168165),
    ("nueces", "Nueces picadas", "Chopped walnuts", 117, 170187),
    ("parmesano", "Parmesano rallado", "Grated parmesan", 100, 171247),
]
UNITS_ML = {"taza": 236.588, "tazam": 250, "cda": 14.787, "cdta": 4.929, "vyog": 125, "vaso": 200, "ml": 1, "floz": 29.5735}

BODY = r"""
  var I = D.ing.filter(function (x) { return x[0] === v.ing; })[0] || D.ing[0], dens = I[1] / 236.588, U = D.u;
  var q = v.cant;
  if (!ok(q) || q <= 0) return { err: T.e_cant };
  if (q > 1e5) return { err: T.e_big };
  var g, ml;
  if (v.dir === 'g') { g = q; ml = g / dens; }
  else { ml = q * (U[v.uni] || 1); g = ml * dens; }
  var list = EN ? ['taza', 'cda', 'cdta', 'ml', 'tazam', 'floz'] : ['taza', 'tazam', 'cda', 'cdta', 'vyog', 'vaso', 'ml'];
  var rows = list.filter(function (k) { return v.dir === 'g' || k !== v.uni; }).map(function (k) {
    var x = ml / U[k];
    return [T.un[k], (k === 'ml' ? nf(x, 0) : nz(x, x < 1 ? 2 : 1)) + ' ' + T.us[k]];
  });
  var head = v.dir === 'g' ? nz(q, 1) + ' g' : nz(q, 2) + ' ' + (q === 1 ? T.un[v.uni].toLowerCase() : T.us[v.uni]);
  return {
    label: head + ' · ' + T.names[I[0]], big: v.dir === 'g' ? nz(ml / U.taza, 2) + ' ' + T.us.taza : gr(g) + ' g',
    sub: v.dir === 'g' ? T.sub_g.replace('{ml}', nf(ml, 0)) : T.sub.replace('{c}', nf(I[1], I[1] % 1 ? 1 : 0)),
    rows: (v.dir === 'g' ? [] : [[T.grams, gr(g) + ' g', 'tot'], [T.oz, nz(g / 28.3495, 2) + ' oz', 'sub']]).concat(rows),
    note: T.note.replace('{id}', I[2]),
    n: { g: H.r2(g), ml: H.r2(ml), cups: H.r2(ml / U.taza) }
  };
"""
JS = js(BODY)

UN_ES = {"taza": "Taza (EE. UU.)", "tazam": "Taza métrica", "cda": "Cucharada", "cdta": "Cucharadita", "vyog": "Vaso de yogur",
         "vaso": "Vaso de agua", "ml": "Mililitros", "floz": "Onza líquida"}
US_ES = {"taza": "tazas", "tazam": "tazas de 250 ml", "cda": "cucharadas", "cdta": "cucharaditas", "vyog": "vasos de yogur",
         "vaso": "vasos", "ml": "ml", "floz": "fl oz"}
UN_EN = {"taza": "US cup", "tazam": "Metric cup (AU, CA, NZ)", "cda": "Tablespoon", "cdta": "Teaspoon", "vyog": "Yogurt pot",
         "vaso": "Glass (200 ml)", "ml": "Millilitres", "floz": "US fluid ounce"}
US_EN = {"taza": "cups", "tazam": "metric cups", "cda": "tbsp", "cdta": "tsp", "vyog": "pots", "vaso": "glasses", "ml": "ml", "floz": "fl oz"}

T_ES = {"e_cant": "Escribe una cantidad.", "e_big": "Cantidad demasiado grande.", "un": UN_ES, "us": US_ES,
        "names": {i[0]: i[1] for i in ING}, "grams": "Gramos", "oz": "Onzas",
        "sub": "1 taza = {c} g", "sub_g": "{ml} ml",
        "note": "Peso de USDA FoodData Central (id {id}), taza llena a ras sin apretar. Por volumen siempre hay margen: pesa si puedes."}
T_EN = {"e_cant": "Enter an amount.", "e_big": "Amount too large.", "un": UN_EN, "us": US_EN,
        "names": {i[0]: i[2] for i in ING}, "grams": "Grams", "oz": "Ounces",
        "sub": "1 cup = {c} g", "sub_g": "{ml} ml",
        "note": "Weight from USDA FoodData Central (FDC {id}), cup spooned and leveled, not packed unless stated. Volume is never exact: weigh when you can."}


def data(lang):
    return {"en": lang == "en", "t": T_EN if lang == "en" else T_ES, "u": UNITS_ML, "ing": [[i[0], i[3], i[4]] for i in ING]}


def inputs(lang):
    es = lang == "es"
    names = sorted(((i[0], i[1] if es else i[2]) for i in ING), key=lambda x: x[1]) if not es else [(i[0], i[1]) for i in ING]
    units = ([("taza", "Taza (EE. UU.)"), ("tazam", "Taza métrica (250 ml)"), ("cda", "Cucharada (15 ml)"), ("cdta", "Cucharadita (5 ml)"),
              ("vyog", "Vaso de yogur (125 ml)"), ("vaso", "Vaso de agua (200 ml)"), ("ml", "Mililitros")] if es else
             [("taza", "US cups"), ("cda", "Tablespoons"), ("cdta", "Teaspoons"), ("floz", "Fluid ounces"), ("ml", "Millilitres"),
              ("tazam", "Metric cups (250 ml)")])
    return [
        {"id": "dir", "type": "seg", "label": "Pasar" if es else "Convert", "value": "v",
         "options": [("v", "A gramos" if es else "To grams"), ("g", "Desde gramos" if es else "From grams")]},
        {"id": "ing", "type": "select", "label": "Ingrediente" if es else "Ingredient", "value": "harina", "options": names, "w": "l"},
        {"id": "cant", "type": "number", "label": "Cantidad" if es else "Amount", "value": 1, "w": "s", "step": "0.25"},
        {"id": "uni", "type": "select", "label": "Medida" if es else "Unit", "value": "taza", "options": units, "show": ("dir", ["v"])},
    ]


TESTS = [
    ({}, {"n.g": 125}),
    ({"ing": "azucar", "cant": "2", "uni": "cda"}, {"n.g": 25}),
    ({"cant": "1", "uni": "vyog"}, {"n.g": 66.04}),
    ({"dir": "g", "ing": "mantequilla", "cant": "100"}, {"n.cups": 0.44}),
    ({"cant": ""}, {"err": T_ES["e_cant"]}),
]

FAQ = [
    ("¿Cuántos gramos tiene una taza de harina?",
     "Unos 125 g de harina de trigo común, según la base de datos de alimentos del Departamento de Agricultura de EE. UU., llenando la "
     "taza con cuchara y enrasando. Si hundes la taza en el paquete, puede pasar de 150 g. La harina de fuerza pesa algo más (137 g) "
     "y la integral algo menos (120 g)."),
    ("¿Cuántos gramos son una taza de azúcar?",
     "200 g de azúcar blanco. El azúcar moreno apretado pesa 220 g por taza y el azúcar glas sin tamizar, 120 g."),
    ("¿Cuánto mide una taza en las recetas americanas?",
     "La taza estadounidense son 236,6 ml (en etiquetas nutricionales se redondea a 240 ml). En Australia, Canadá y Nueva Zelanda se usa "
     "la taza métrica de 250 ml. La cucharada son 15 ml y la cucharadita 5 ml."),
    ("¿Cuántos gramos es un vaso de yogur de harina?",
     "El vaso de yogur de 125 ml, el del bizcocho de yogur de toda la vida, lleva unos 66 g de harina, 106 g de azúcar o 114 g de "
     "aceite de oliva. Elige «Vaso de yogur» en la medida."),
    ("¿Cuántos gramos tiene una cucharada?",
     "Depende del ingrediente: una cucharada rasa de azúcar son unos 12,5 g, de harina unos 8 g, de sal fina 18 g, de aceite 13,5 g y de "
     "miel 21 g. Las cucharas de casa no son exactas; las de medir sí."),
]


def blocks_es(ctx):
    rows = "".join(f"<tr><td>{i[1]}</td><td class=\"num\">{C(i[3])} g</td><td class=\"num\">{C(i[3] / 16, 1)} g</td></tr>"
                   for i in ING if i[0] in ("harina", "fuerza", "maicena", "azucar", "moreno", "glas", "mantequilla", "aceite", "leche", "miel", "cacao", "avena"))
    return [
        ("Cómo se convierte", f"""
<p>Una taza es una medida de volumen, y cada ingrediente pesa distinto en el mismo volumen: una taza de harina de trigo pesa
<b>125 g</b>, una de azúcar <b>200 g</b> y una de miel <b>339 g</b>. Por eso no hay una única equivalencia «taza = gramos». La
calculadora usa el peso de una taza que publica para cada alimento la base de datos FoodData Central del USDA (taza
estadounidense de 236,6 ml, llena sin apretar y enrasada) y lo reparte por mililitros para pasar a cucharadas, vasos o tazas
métricas.</p>
<p>Ejemplo: una receta americana de galletas pide 2¼ tazas de harina, 1 taza de mantequilla y ¾ de taza de azúcar moreno. Son
<b>281 g de harina</b> (2,25 × 125), 227 g de mantequilla y 165 g de azúcar moreno apretado (0,75 × 220).</p>
<table class="tbl"><thead><tr><th>Ingrediente</th><th>1 taza</th><th>1 cucharada</th></tr></thead><tbody>{rows}</tbody></table>"""),
        ("Por qué conviene pesar", """
<p>Medir por volumen tiene un margen de error grande con los ingredientes en polvo: la harina se compacta en el paquete, el
azúcar glas se apelmaza y el cacao cambia mucho si está tamizado. En repostería, unos gramos de más de harina se notan en un
bizcocho seco. Si tienes báscula, pesa; si no, llena la taza con una cuchara sin apretar y pasa un cuchillo por encima. Con los
líquidos el volumen sí es fiable: la leche y el agua pesan casi lo mismo en gramos que en mililitros.</p>"""),
    ]


def C(x, dec=0):
    s = f"{x:,.{dec}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return s


TOOL = {
    "slug": "tazas-a-gramos",
    "lang": "es",
    "twin": "cups-to-grams",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "scale",
    "order": 60,
    "name": "Tazas a gramos",
    "k": "taza harina azúcar mantequilla cucharada cucharadita vaso de yogur equivalencias medidas",
    "title": "Tazas a gramos: harina, azúcar, mantequilla y más",
    "desc": "Convierte tazas, cucharadas y vasos de yogur a gramos (y al revés) para harina, azúcar, mantequilla, aceite y otros 30 ingredientes, con datos del USDA.",
    "h1": "Conversor de tazas a gramos",
    "crumb": "Tazas a gramos",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": data("es"),
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("USDA FoodData Central (SR Legacy, pesos por porción)", FDC), ("NIST · Conversión de unidades de cocina", NIST)],
    "credits": [("USDA FoodData Central · SR Legacy (abril 2018)", "Dominio público (CC0)", FDC_DL)],
    "related": ["escalar-receta", "porcentaje-panadero", "temperatura-horno", "masa-madre"],
    "tests": TESTS,
}
