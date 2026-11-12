"""Zonas de frecuencia cardiaca: max HR measured or estimated (Tanaka 2001, Fox 220 - age, Gulati 2010), five zones by
Karvonen (heart-rate reserve) or % of max HR. EN twin: heart-rate-zone-calculator."""
from herramientas.tools import _deporte as D

KARVONEN = "https://pubmed.ncbi.nlm.nih.gov/13470504/"
TANAKA = "https://pubmed.ncbi.nlm.nih.gov/11153730/"
GULATI = "https://pubmed.ncbi.nlm.nih.gov/20585008/"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var T = EN ? {
    age: 'Enter your age (10 to 100).', max: 'Max heart rate should be between 100 and 230 bpm.', rest: 'Enter your resting heart rate (30 to 110 bpm) or switch to % of max.',
    rest2: 'Resting heart rate must be well below your max.', lab: 'Max heart rate', res: 'reserve', meas: 'measured',
    F: { tanaka: 'Tanaka', fox: '220 − age', gulati: 'Gulati (women)' }, zone: 'Zone', bpm: 'bpm', pct: '%',
    Z: ['Recovery', 'Endurance', 'Tempo', 'Threshold', 'Maximum'], U: ['warm-up, easy days', 'long easy runs, base', 'steady, marathon pace', 'hard intervals, 10K pace', 'short repeats, sprints'],
    kv: 'Karvonen (heart-rate reserve)', pm: '% of max heart rate'
  } : {
    age: 'Indica tu edad (de 10 a 100 años).', max: 'La FC máxima debe estar entre 100 y 230 ppm.', rest: 'Indica tu FC en reposo (de 30 a 110 ppm) o cambia a % de la máxima.',
    rest2: 'La FC en reposo tiene que ser bastante menor que la máxima.', lab: 'FC máxima', res: 'reserva', meas: 'medida',
    F: { tanaka: 'Tanaka', fox: '220 − edad', gulati: 'Gulati (mujeres)' }, zone: 'Zona', bpm: 'ppm', pct: '%',
    Z: ['Recuperación', 'Aeróbica', 'Tempo', 'Umbral', 'Máxima'], U: ['calentar, días suaves', 'rodajes largos, fondo', 'ritmo sostenido, maratón', 'series duras, ritmo 10 km', 'series cortas, sprints'],
    kv: 'Karvonen (FC de reserva)', pm: '% de la FC máxima'
  };
  var max, src;
  if (v.fcmax > 0) {
    if (v.fcmax < 100 || v.fcmax > 230) return { err: T.max };
    max = v.fcmax; src = T.meas;
  } else {
    if (!(v.edad >= 10 && v.edad <= 100)) return { err: T.age };
    max = v.form === 'fox' ? 220 - v.edad : v.form === 'gulati' ? 206 - 0.88 * v.edad : 208 - 0.7 * v.edad;
    src = T.F[v.form] || T.F.tanaka;
  }
  var kv = v.met === 'kv', rest = v.fcrep;
  if (kv) {
    if (!(rest >= 30 && rest <= 110)) return { err: T.rest };
    if (rest > max - 40) return { err: T.rest2 };
  } else rest = 0;
  var P = [50, 60, 70, 80, 90, 100], b = P.map(function (p) { return Math.round(rest + (max - rest) * p / 100); });
  var rows = '', zs = [];
  for (var i = 0; i < 5; i++) {
    zs.push([b[i], b[i + 1]]);
    rows += '<tr class="fc-z' + (i + 1) + '"><td><b>' + (i + 1) + '</b> ' + T.Z[i] + '<br><small>' + T.U[i] + '</small></td><td class="num">' + P[i] + '–' + P[i + 1] + ' %</td><td class="num"><b>' + b[i] + '–' + b[i + 1] + '</b> ' + T.bpm + '</td></tr>';
  }
  return {
    label: T.lab, big: Math.round(max) + ' ' + T.bpm,
    sub: src + (kv ? ' · ' + T.res + ' ' + Math.round(max - rest) + ' ' + T.bpm : '') + ' · ' + (kv ? T.kv : T.pm),
    html: '<table class="tbl fc-t"><thead><tr><th>' + T.zone + '</th><th class="num">' + T.pct + '</th><th class="num">' + T.bpm + '</th></tr></thead><tbody>' + rows + '</tbody></table>',
    print: true,
    n: { max: r(max, 1), z2: zs[1], z4: zs[3] }
  };
}
"""

CSS = """
.fc-t td{vertical-align:middle}.fc-t small{color:var(--mut,#666)}.fc-t tr td:first-child{border-left:5px solid transparent}
.fc-z1 td:first-child{border-left-color:#9aa5b1!important}.fc-z2 td:first-child{border-left-color:#3b82c4!important}
.fc-z3 td:first-child{border-left-color:#3fa34d!important}.fc-z4 td:first-child{border-left-color:#e3a21a!important}
.fc-z5 td:first-child{border-left-color:#d64545!important}
"""

INPUTS_ES = [
    {"id": "edad", "type": "number", "label": "Edad", "value": "35", "unit": "años", "w": "s"},
    {"id": "fcrep", "type": "number", "label": "FC en reposo", "value": "60", "unit": "ppm", "w": "s", "show": ("met", ["kv"])},
    {"id": "met", "type": "seg", "label": "Método", "value": "kv", "options": [("kv", "Karvonen"), ("pm", "% FC máx.")]},
    {"id": "fcmax", "type": "number", "label": "FC máx. medida", "value": "", "unit": "ppm", "w": "s", "more": True},
    {"id": "form", "type": "select", "label": "Fórmula FC máx.", "value": "tanaka", "more": True,
     "options": [("tanaka", "Tanaka: 208 − 0,7 × edad"), ("fox", "Clásica: 220 − edad"), ("gulati", "Gulati (mujeres): 206 − 0,88 × edad")]},
]


def blocks(ctx):
    mx = 208 - 0.7 * 35
    k = lambda p: round(60 + (mx - 60) * p / 100)  # noqa: E731
    m = lambda p: round(mx * p / 100)  # noqa: E731
    return [
        ("Cómo se calculan tus zonas", f"""
<p>Las zonas se calculan a partir de dos datos: tu <b>frecuencia cardiaca máxima</b> y, con el método de Karvonen, tu
<b>frecuencia en reposo</b>. Karvonen trabaja sobre la <i>reserva</i> (máxima − reposo): <b>FC objetivo = reposo +
(máxima − reposo) × %</b>. Así, dos personas con la misma máxima pero distinta forma física obtienen zonas distintas, lo que
lo hace más preciso que aplicar el porcentaje a la máxima sin más.</p>
<p>Ejemplo: a los 35 años la fórmula de Tanaka da una máxima de 208 − 0,7 × 35 = {D.n(mx, 1)} ppm. Con 60 ppm en reposo, la
reserva es {D.n(mx - 60, 1)} y la zona 2 (60-70 %) va de <b>{k(60)} a {k(70)} ppm</b>. Con el método del % de la máxima, la
misma zona quedaría en {m(60)}-{m(70)} ppm, bastante más baja: por eso conviene medir el pulso en reposo (nada más
despertar, tumbado, durante un minuto, varios días seguidos) y usar Karvonen.</p>"""),
        ("Qué fórmula de FC máxima usar", """
<p>La regla clásica de <b>220 − edad</b> se popularizó en los años 70 sin un estudio que la respaldara y sobreestima la
máxima en jóvenes y la subestima en mayores. <b>Tanaka</b> (2001) la revisó con 351 estudios y unas 19.000 personas y
propuso 208 − 0,7 × edad, hoy la más usada por defecto. Para mujeres, el estudio de <b>Gulati</b> (2010), con más de
5.400 mujeres, obtuvo 206 − 0,88 × edad. Todas son medias: la máxima real de una persona puede estar 10 ppm por encima o
por debajo. Si has medido la tuya en una prueba de esfuerzo o en una serie a tope con pulsómetro de pecho, escríbela en
«FC máx. medida» y se usará en lugar de la fórmula.</p>"""),
        ("Para qué sirve cada zona", """
<p>La <b>zona 1</b> (50-60 %) es para calentar y recuperar. La <b>zona 2</b> (60-70 %) es la base aeróbica: permite
hablar en frases completas y es donde la mayoría de los planes ponen el grueso del volumen semanal. La <b>zona 3</b>
(70-80 %) corresponde a un ritmo sostenido, cercano al de maratón. La <b>zona 4</b> (80-90 %) ronda el umbral, donde la
respiración ya es pesada: series de 3 a 10 minutos o ritmo de 10 km. La <b>zona 5</b> (90-100 %) solo se aguanta unos
minutos. Si tomas medicación para la tensión o el corazón (los betabloqueantes bajan la frecuencia) o tienes una
cardiopatía, pide a tu médico tus zonas: estas fórmulas no sirven en ese caso.</p>"""),
    ]


FAQ = [
    ("¿Cuál es mi frecuencia cardiaca máxima por edad?",
     "Con la fórmula de Tanaka, 208 − 0,7 × edad: 187 ppm a los 30 años, 180 a los 40, 173 a los 50 y 166 a los 60. Es una media con un margen de unos ±10 ppm."),
    ("¿Qué es la zona 2 y cuántas pulsaciones son?",
     "Es el 60-70 % de tu reserva (o de tu máxima). Para alguien de 35 años con 60 ppm en reposo son unas 134-146 ppm con Karvonen."),
    ("¿Karvonen o porcentaje de la máxima?",
     "Karvonen, si conoces tu pulso en reposo: tiene en cuenta tu forma física. El % de la máxima es más sencillo, pero da zonas más bajas."),
    ("¿Cómo mido la frecuencia en reposo?",
     "Por la mañana, antes de levantarte, cuenta el pulso un minuto entero (o usa el reloj) varios días y quédate con la media."),
    ("¿Por qué mi reloj me da otras zonas?",
     "Cada marca usa su propia fórmula y sus porcentajes. Lo importante es usar siempre el mismo sistema y una máxima realista."),
]

TOOL = {
    "slug": "zonas-frecuencia-cardiaca",
    "lang": "es",
    "twin": "heart-rate-zone-calculator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "heart-rate-monitor",
    "order": 60,
    "name": "Zonas de frecuencia cardiaca",
    "k": "zonas pulsaciones fc máxima karvonen reserva zona 2 entrenamiento pulsómetro tanaka",
    "title": "Zonas de frecuencia cardiaca: calculadora Karvonen",
    "desc": "Calcula tus 5 zonas de pulsaciones con el método de Karvonen o el % de la FC máxima. FC máxima por edad (Tanaka, 220 − edad, Gulati) o medida.",
    "h1": "Calculadora de zonas de frecuencia cardiaca",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Karvonen MJ, Kentala E, Mustala O (1957). The effects of training on heart rate. Ann Med Exp Biol Fenn 35: 307-315", KARVONEN),
                ("Tanaka H, Monahan KD, Seals DR (2001). Age-predicted maximal heart rate revisited. J Am Coll Cardiol 37: 153-156", TANAKA),
                ("Gulati M et al. (2010). Heart rate response to exercise stress testing in asymptomatic women. Circulation 122: 130-137", GULATI)],
    "credits": [("Método de Karvonen (1957)", "fórmula publicada (reimplementada)", KARVONEN),
                ("Fórmula de Tanaka (2001)", "fórmula publicada (reimplementada)", TANAKA)],
    "related": ["ritmo-carrera", "prediccion-maraton", "ritmo-natacion"],
    "tests": [
        ({}, {"n.max": 183.5, "n.z2": [134, 146], "n.z4": [159, 171]}),
        ({"met": "pm"}, {"n.z2": [110, 128]}),
        ({"fcmax": "190", "fcrep": "50"}, {"n.max": 190, "n.z2": [134, 148]}),
        ({"form": "fox", "edad": "40", "met": "pm"}, {"n.max": 180, "n.z4": [144, 162]}),
        ({"edad": ""}, {"err": "Indica tu edad (de 10 a 100 años)."}),
        ({"fcrep": "150"}, {"err": "Indica tu FC en reposo (de 30 a 110 ppm) o cambia a % de la máxima."}),
    ],
}
