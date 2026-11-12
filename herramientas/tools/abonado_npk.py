"""Abonado NPK: kg of a compound fertiliser (N-P2O5-K2O label) to meet a nutrient target per hectare, with the
complement in straight fertilisers (urea, superphosphate, potassium chloride). Oxide/element factors are the standard
P2O5 = 2,2914 P and K2O = 1,2046 K."""
GUIA = "https://www.mapa.gob.es/es/agricultura/publicaciones/publicaciones-fertilizantes"
RD = "https://www.boe.es/buscar/act.php?id=BOE-A-2022-23052"

PRESETS = [("15-15-15", 15, 15, 15), ("8-15-15", 8, 15, 15), ("9-18-27", 9, 18, 27), ("20-10-10", 20, 10, 10),
           ("12-24-8", 12, 24, 8), ("18-46-0", 18, 46, 0), ("46-0-0", 46, 0, 0), ("27-0-0", 27, 0, 0), ("0-18-0", 0, 18, 0),
           ("0-0-60", 0, 0, 60), ("0-0-50", 0, 0, 50)]
NAMES = {"18-46-0": "fosfato diamónico", "46-0-0": "urea", "27-0-0": "nitrato amónico cálcico", "0-18-0": "superfosfato simple",
         "0-0-60": "cloruro potásico", "0-0-50": "sulfato potásico"}

JS = r"""
function (v, H, C) {
  var t = [v.n, v.p, v.k].map(function (x) { return isNaN(x) ? 0 : x; }), f = [v.fn, v.fp, v.fk].map(function (x) { return isNaN(x) ? 0 : x; });
  if (t.some(function (x) { return x < 0; }) || f.some(function (x) { return x < 0; })) return { err: 'Sin valores negativos.' };
  if (f[0] + f[1] + f[2] > 100) return { err: 'La riqueza N + P₂O₅ + K₂O no puede pasar de 100 %.' };
  if (v.elem) { t[1] *= 2.2914; t[2] *= 1.2046; }
  if (!(t[0] + t[1] + t[2] > 0)) return { err: 'Escribe cuántos kg de N, P₂O₅ o K₂O necesitas por hectárea.' };
  var r = [];
  for (var i = 0; i < 3; i++) if (f[i] > 0 && t[i] > 0) r.push(t[i] / (f[i] / 100));
  if (!r.length) return { err: 'Este abono no lleva ninguno de los nutrientes que pides.' };
  var dose = v.modo === 'max' ? Math.max.apply(null, r) : Math.min.apply(null, r);
  var got = f.map(function (x) { return dose * x / 100; }), ha = v.ha > 0 ? v.ha : 1, sac = v.saco > 0 ? v.saco : 25;
  var nm = ['N', 'P₂O₅', 'K₂O'], rows = [];
  for (i = 0; i < 3; i++) {
    var d = got[i] - t[i];
    rows.push([nm[i] + ' <small>objetivo ' + H.num(t[i], 0) + '</small>', H.num(got[i], 1) + ' kg/ha' + (Math.abs(d) < 0.05 ? '' : ' · ' + (d > 0 ? '+' : '−') + H.num(Math.abs(d), 1))]);
  }
  rows.push(['Abono ' + H.esc(v.fn + '-' + v.fp + '-' + v.fk), H.num(dose * ha, 0) + ' kg · ' + Math.ceil(dose * ha / sac - 1e-9) + ' sacos de ' + H.num(sac, 0) + ' kg' + (v.ha > 0 ? '' : ' por ha'), 'tot']);
  var simple = [['Urea 46 %', 46], ['Superfosfato 18 %', 18], ['Cloruro potásico 60 %', 60]], comp = [];
  for (i = 0; i < 3; i++) {
    var miss = t[i] - got[i];
    if (miss > 0.05) { var kg = miss / (simple[i][1] / 100); comp.push(kg); rows.push([simple[i][0] + ' <small>completar</small>', H.num(kg, 0) + ' kg/ha · ' + H.num(kg * ha, 0) + ' kg', 'sub']); }
    else comp.push(0);
  }
  return { label: 'Abono por hectárea', big: H.num(dose, 0) + ' kg/ha',
    sub: (ha !== 1 || v.ha > 0 ? H.num(dose * ha, 0) + ' kg en ' + H.num(ha, ha % 1 ? 2 : 0) + ' ha · ' : '') + H.num(dose / 10, 1) + ' g/m²',
    rows: rows, note: 'Las necesidades dependen del cultivo, la cosecha esperada y el análisis de suelo. Reparte el nitrógeno en varias aplicaciones.',
    n: { dose: H.r2(dose), n: H.r2(got[0]), p: H.r2(got[1]), k: H.r2(got[2]), urea: H.r2(comp[0]), sp: H.r2(comp[1]), kcl: H.r2(comp[2]) } };
}
"""


def blocks(ctx):
    return [
        ("Cuántos kilos de abono echar", """
<p>Los números de un saco de abono son su riqueza en porcentaje: un <b>15-15-15</b> lleva 15 kg de nitrógeno (N), 15 kg de fósforo
expresado como P₂O₅ y 15 kg de potasio expresado como K₂O por cada 100 kg. Para saber cuánto echar, divide lo que necesita el
cultivo entre la riqueza: si quieres 60 kg de P₂O₅ por hectárea con un 15-15-15, son <b>60 ÷ 0,15 = 400 kg/ha</b>.</p>
<p>Un abono compuesto rara vez cuadra con los tres nutrientes a la vez. Con «Sin pasarme» la dosis se ajusta al nutriente que antes
llega al objetivo y la calculadora te dice cuánto completar con abonos simples: urea (46 % de N), superfosfato (18 % de P₂O₅) y
cloruro potásico (60 % de K₂O). Con «Cubrir todo» la dosis alcanza los tres y verás lo que sobra de cada uno, que normalmente es
dinero tirado y, en el caso del nitrógeno, nitratos que acaban en el acuífero.</p>"""),
        ("Ejemplo", """
<p>Un cereal de secano al que el técnico recomienda <b>120 kg de N, 60 de P₂O₅ y 60 de K₂O por hectárea</b>. Con un 15-15-15 en
sementera bastan <b>400 kg/ha</b> para el fósforo y el potasio, que aportan también 60 kg de N. Los 60 kg de N que faltan se dan en
cobertera con 130 kg/ha de urea (60 ÷ 0,46), mejor en una o dos veces a la salida del invierno. Para 12 ha, son 4.800 kg de
15-15-15 (192 sacos de 25 kg) y 1.565 kg de urea. Si se hubiera usado el 15-15-15 para cubrirlo todo, habrían hecho falta 800 kg/ha
y sobrarían 60 kg de P₂O₅ y 60 de K₂O por hectárea.</p>
<p>Si el análisis de suelo o la recomendación vienen en fósforo y potasio elementales (P y K), marca «Objetivo en P y K» en «Más
opciones»: la calculadora los pasa a óxidos multiplicando por 2,2914 y 1,2046.</p>"""),
        ("Normativa y método", f"""
<p>El <a href="{RD}" rel="noopener">Real Decreto 1051/2022</a> de nutrición sostenible de los suelos agrarios obliga, desde el 1 de
septiembre de 2026, a tener un <b>plan de abonado</b> en cada unidad de producción, con algunas excepciones como los pastos que no se
abonan y las parcelas de secano de hasta 10 hectáreas (artículo 4.2). El plan se basa en el balance entre lo que necesita el cultivo,
lo que aporta el suelo, el agua de riego y el estiércol, y lo que se pierde. Las dosis de cada cultivo, las extracciones por tonelada
de cosecha y la forma de repartir el nitrógeno están en la <a href="{GUIA}" rel="noopener">Guía práctica de la fertilización
racional de los cultivos en España</a> del Ministerio de Agricultura.</p>
<p>Esta calculadora solo resuelve la aritmética del saco: cuántos kilos de un abono concreto dan los nutrientes que ya sabes que
necesitas.</p>"""),
    ]


FAQ = [
    ("¿Qué significan los números 15-15-15 de un abono?",
     "Los kilos de nitrógeno (N), fósforo como P₂O₅ y potasio como K₂O que hay en 100 kg de producto. Un 9-18-27 lleva 9 kg de N, 18 de "
     "P₂O₅ y 27 de K₂O por cada 100 kg."),
    ("¿Cuánta urea hay que echar por hectárea?",
     "La que resulte de dividir el nitrógeno que falta entre 0,46. Para 60 kg de N, 130 kg de urea; para 100 kg de N, 217 kg."),
    ("¿Cómo paso de P a P₂O₅ y de K a K₂O?",
     "Multiplica el fósforo por 2,2914 y el potasio por 1,2046. Al revés, P₂O₅ × 0,4364 = P y K₂O × 0,8301 = K."),
    ("¿Cuántos gramos de abono por metro cuadrado son 400 kg por hectárea?",
     "40 g/m², porque una hectárea tiene 10.000 m². En un huerto pequeño, divide los kg/ha entre 10 para tener los gramos por m²."),
    ("¿Es obligatorio el plan de abonado?",
     "Desde el 1 de septiembre de 2026 lo exige el Real Decreto 1051/2022 en cada unidad de producción, salvo excepciones como los pastos "
     "que no se fertilizan y el secano de hasta 10 hectáreas. Las anotaciones van al cuaderno de explotación."),
]

TOOL = {
    "slug": "abonado-npk",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "flask",
    "order": 60,
    "name": "Calculadora de abonado NPK",
    "k": "abono fertilizante 15-15-15 urea superfosfato cloruro potasico kg por hectarea nitrogeno fosforo potasio",
    "title": "Calculadora de abonado NPK: kg de abono por hectárea",
    "desc": "Calcula los kg de abono 15-15-15, 8-15-15, urea u otro por hectárea para cubrir el N, P₂O₅ y K₂O que necesita tu cultivo, con sacos y complementos.",
    "h1": "Calculadora de abonado NPK",
    "crumb": "Abonado NPK",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "n", "type": "number", "label": "N", "value": 120, "unit": "kg/ha", "w": "s"},
        {"id": "p", "type": "number", "label": "P₂O₅", "value": 60, "unit": "kg/ha", "w": "s"},
        {"id": "k", "type": "number", "label": "K₂O", "value": 60, "unit": "kg/ha", "w": "s"},
        {"id": "abono", "type": "select", "label": "Abono", "value": "15-15-15", "custom": "otro",
         "options": [(c, c + (f" · {NAMES[c]}" if c in NAMES else ""), {"fn": n, "fp": p, "fk": k}) for c, n, p, k in PRESETS] + [("otro", "Otro")]},
        {"id": "fn", "type": "number", "label": "Riqueza N", "value": 15, "unit": "%", "w": "s"},
        {"id": "fp", "type": "number", "label": "Riqueza P₂O₅", "value": 15, "unit": "%", "w": "s"},
        {"id": "fk", "type": "number", "label": "Riqueza K₂O", "value": 15, "unit": "%", "w": "s"},
        {"id": "modo", "type": "seg", "label": "Dosis", "value": "min", "options": [("min", "Sin pasarme"), ("max", "Cubrir todo")]},
        {"id": "ha", "type": "number", "label": "Superficie", "value": "", "unit": "ha", "step": "0.01", "w": "s"},
        {"id": "saco", "type": "number", "label": "Saco", "value": 25, "unit": "kg", "w": "s", "more": True},
        {"id": "elem", "type": "check", "label": "Objetivo en P y K", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("MAPA · Guía práctica de la fertilización racional de los cultivos en España", GUIA),
                ("Real Decreto 1051/2022, nutrición sostenible en los suelos agrarios (BOE-A-2022-23052)", RD)],
    "related": ["marco-plantacion", "riego-goteo", "medidas-agrarias", "calendario-siembra"],
    "tests": [
        ({}, {"n.dose": 400, "n.n": 60, "n.urea": 130.43, "n.sp": 0, "n.kcl": 0}),
        ({"modo": "max"}, {"n.dose": 800, "n.p": 120}),
        ({"ha": "12"}, {"n.dose": 400}),
        ({"abono": "46-0-0", "fn": "46", "fp": "0", "fk": "0", "p": "0", "k": "0", "n": "100"}, {"n.dose": 217.39}),
        ({"elem": True, "n": "0", "p": "26.18", "k": "0"}, {"n.dose": 399.93}),
        ({"fn": "60", "fp": "30", "fk": "20"}, {"err": "La riqueza N + P₂O₅ + K₂O no puede pasar de 100 %."}),
        ({"n": "0", "p": "0", "k": "0"}, {"err": "Escribe cuántos kg de N, P₂O₅ o K₂O necesitas por hectárea."}),
    ],
}
