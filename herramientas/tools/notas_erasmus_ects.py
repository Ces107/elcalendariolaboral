"""Conversión de notas Erasmus: a grade from one national scale to another by linear interpolation in two pieces
(fail range and pass range, pass mark to pass mark and top to top), the same idea as the "modified Bavarian formula"
German universities use. Scale presets fill min / pass / max; any custom scale works (inverted ones too: 1 best).
Optional: the old ECTS A-E letter from the student's position in the class (ECTS Users' Guide 2009 percentiles)."""
from herramientas.tools._estudios import CAT

SCALES = [  # key, label, worst, pass mark, best
    ("es", "España (0-10)", 0, 5, 10), ("it", "Italia (18-30)", 0, 18, 30), ("fr", "Francia (0-20)", 0, 10, 20),
    ("be", "Bélgica (0-20)", 0, 10, 20), ("pt", "Portugal (0-20)", 0, 10, 20), ("de", "Alemania (1-5, 1 mejor)", 5, 4, 1),
    ("at", "Austria (1-5, 1 mejor)", 5, 4, 1), ("cz", "Chequia (1-4, 1 mejor)", 4, 3, 1), ("nl", "Países Bajos (1-10)", 1, 5.5, 10),
    ("pl", "Polonia (2-5)", 2, 3, 5), ("ch", "Suiza (1-6)", 1, 4, 6), ("gr", "Grecia (0-10)", 0, 5, 10),
    ("ro", "Rumanía (1-10)", 1, 5, 10), ("hu", "Hungría (1-5)", 1, 2, 5), ("fi", "Finlandia (0-5)", 0, 1, 5),
    ("dk", "Dinamarca (-3 a 12)", -3, 2, 12), ("uk", "Reino Unido (%)", 0, 40, 100), ("ie", "Irlanda (%)", 0, 40, 100),
]


def _opts(p):
    return [(k, lab, {f"{p}min": str(lo), f"{p}ap": str(ap), f"{p}max": str(hi)}) for k, lab, lo, ap, hi in SCALES] + [("otra", "Otra escala")]


def _lab(k):
    return next(lab for kk, lab, *_ in SCALES if kk == k)


JS = r"""
function (v, H, C) {
  function sc(p) { return { lo: v[p + 'min'], ap: v[p + 'ap'], hi: v[p + 'max'] }; }
  var A = sc('d'), B = sc('a');
  function bad(s) { return isNaN(s.lo) || isNaN(s.ap) || isNaN(s.hi) || !((s.lo < s.ap && s.ap < s.hi) || (s.lo > s.ap && s.ap > s.hi)); }
  if (bad(A) || bad(B)) return { err: 'Cada escala necesita peor nota, aprobado y mejor nota en orden.' };
  var x = v.nota;
  if (isNaN(x)) return { err: 'Escribe la nota.' };
  if ((x - A.lo) * (x - A.hi) > 1e-12) { var lo = Math.min(A.lo, A.hi), hi = Math.max(A.lo, A.hi); return { err: 'La nota tiene que estar entre ' + H.num(lo, lo % 1 ? 1 : 0) + ' y ' + H.num(hi, hi % 1 ? 1 : 0) + '.' }; }
  function toU(s, y) { var t = (y - s.ap) / (s.hi - s.ap); return t >= 0 ? 0.5 + 0.5 * t : 0.5 * (y - s.lo) / (s.ap - s.lo); }  /* 0 worst, 0.5 pass, 1 best */
  function fromU(s, u) { return u >= 0.5 ? s.ap + (u - 0.5) * 2 * (s.hi - s.ap) : s.lo + u * 2 * (s.ap - s.lo); }
  var u = toU(A, x), y = fromU(B, u), es = 10 * u;
  var sp = Math.abs(A.hi - A.ap), stepd = sp >= 10 ? 0 : 1, rows = [];
  rows.push(['En España (0-10)', H.num(Math.round(es * 100) / 100, 2)]);
  var q = es >= 9 ? 'Sobresaliente' : es >= 7 ? 'Notable' : es >= 5 ? 'Aprobado' : 'Suspenso';
  rows.push(['Calificación', q]);
  if (v.pct > 0 && v.pct <= 100) {
    var L = v.pct <= 10 ? 'A' : v.pct <= 35 ? 'B' : v.pct <= 65 ? 'C' : v.pct <= 90 ? 'D' : 'E';
    rows.push(['Letra ECTS (top ' + H.num(v.pct, 0) + ' %)', L]);
  }
  var tb = '';
  for (var k = 0; k <= 5; k++) {
    var g = A.ap + (A.hi - A.ap) * k / 5;
    g = stepd ? Math.round(g * 10) / 10 : Math.round(g);
    tb += '<tr><td class="num">' + H.num(g, g % 1 ? 1 : 0) + '</td><td class="num">' + H.num(fromU(B, toU(A, g)), 2) + '</td></tr>';
  }
  var html = '<table class="tbl er-t"><thead><tr><th scope="col">Origen</th><th scope="col">Destino</th></tr></thead><tbody>' + tb + '</tbody></table>';
  return { label: 'Nota equivalente', big: H.num(Math.round(y * 100) / 100, 2),
    sub: 'de ' + H.num(x, x % 1 ? 2 : 0) + ' en ' + H.esc(v.de === 'otra' ? 'otra escala' : (C.d.lab[v.de] || '')) + ' a ' + H.esc(v.a === 'otra' ? 'otra escala' : (C.d.lab[v.a] || '')),
    rows: rows, html: html,
    note: 'Estimación lineal (aprobado con aprobado, máximo con máximo). La conversión que vale es la tabla de tu universidad.',
    n: { y: y, es: es, letra: rows.length > 2 ? rows[2][1] : null } };
}
"""

BLOCKS = [
    ("Cómo convertir una nota de Erasmus", """
<p>Elige la escala de la universidad de destino y la tuya, escribe la nota y verás su <b>equivalente</b>, la nota en la
escala española de 0 a 10 y una tabla con varias notas de la escala de origen ya convertidas. La conversión es lineal en dos
tramos: el aprobado de una escala se corresponde con el aprobado de la otra, la nota máxima con la máxima y lo que queda en
medio se reparte en proporción. Funciona también con escalas invertidas, como la alemana o la austriaca, donde el 1 es la
mejor nota y el 4 el aprobado, y con cualquier escala que no esté en la lista: elige «Otra escala» y escribe su peor nota,
su aprobado y su máxima en «Más opciones».</p>
<p>Es el mismo principio que la <i>fórmula bávara modificada</i> con la que las universidades alemanas convierten notas
extranjeras: nota = 1 + 3 × (máxima − obtenida) / (máxima − aprobado). Para notas aprobadas da el mismo resultado que esta
herramienta con destino Alemania.</p>"""),
    ("Ejemplos", """
<p>Un 27 sobre 30 en Italia, donde se aprueba con 18: está a 9 de los 12 puntos que hay entre el aprobado y el máximo, es
decir, al 75 % del tramo aprobado. En España eso es 5 + 0,75 × 5 = <b>8,75</b>, un notable. Un 2,3 alemán está a
(4 − 2,3) / (4 − 1) = 57 % del tramo entre el 4 y el 1, que en España da 7,83. Un 14 sobre 20 en Francia (aprobado en 10)
equivale a un 7. Y al revés: un 8 español en Italia sería 18 + 0,6 × 12 = 25,2.</p>
<p>Las notas suspensas se convierten en su propio tramo: un 15 italiano, por debajo del 18, queda en 15 / 18 × 5 = 4,17.</p>"""),
    ("La tabla ECTS y lo que hace tu universidad", """
<p>El sistema europeo ECTS no tiene una escala común de notas. La guía de usuarios ECTS de 2009 proponía letras de la A a la
E según la posición del alumno en su promoción (A el 10 % mejor, B el 25 % siguiente, C el 30 %, D el 25 % y E el 10 %
último); si conoces tu posición, escríbela en «Más opciones» para ver tu letra. La guía de 2015 sustituyó esas letras por
<b>tablas de distribución de notas</b>: cada universidad publica qué porcentaje de aprobados saca cada nota en cada área, y la
universidad de origen convierte comparando las dos tablas. Por eso dos universidades pueden convertir un mismo 27 italiano en
un 8,5 o en un 9.</p>
<p>Lo que entra en tu expediente es la conversión que aplique tu universidad según su normativa de movilidad y el
<i>Learning Agreement</i>. Para un título completo hecho fuera, el Ministerio de Ciencia, Innovación y Universidades emite
la declaración de equivalencia de nota media con sus propias tablas por país. Usa esta herramienta para estimar antes de
elegir destino o para revisar que la conversión que te han hecho es razonable.</p>"""),
]

FAQ = [
    ("¿Cómo se convierte una nota italiana a la escala española?",
     "De forma lineal entre el aprobado (18 → 5) y el máximo (30 → 10): nota española = 5 + 5 × (nota − 18) / 12. Un 24 equivale a 7,5 y un 30 e lode, a 10 (la lode suele contarse como matrícula de honor)."),
    ("¿Y una nota alemana?",
     "En Alemania el 1,0 es la mejor nota y el 4,0 el aprobado: nota española = 5 + 5 × (4 − nota) / 3. Un 1,7 equivale a 8,83 y un 3,0 a 6,67."),
    ("¿Esta conversión es la oficial?",
     "No: cada universidad aplica su propia tabla, a menudo basada en la distribución de notas de cada centro. Esta conversión lineal es una estimación razonable y transparente para comparar."),
    ("¿Qué es la letra ECTS?",
     "Una escala A-E por percentiles que proponía la guía ECTS de 2009: A para el 10 % mejor de la promoción, B el 25 % siguiente, C el 30 %, D el 25 % y E el 10 % último. Hoy se usan tablas de distribución."),
    ("¿Puedo usar una escala que no aparece?",
     "Sí: elige «Otra escala» y escribe en «Más opciones» la peor nota, el aprobado y la mejor nota, tanto de origen como de destino."),
]

INPUTS = [
    {"id": "nota", "type": "number", "label": "Nota", "value": 27, "w": "s", "step": "0.01"},
    {"id": "de", "type": "select", "label": "Escala de la nota", "value": "it", "options": _opts("d"), "custom": "otra"},
    {"id": "a", "type": "select", "label": "Convertir a", "value": "es", "options": _opts("a"), "custom": "otra"},
    {"id": "dmin", "type": "number", "label": "Origen: peor", "value": 0, "more": True, "w": "s"},
    {"id": "dap", "type": "number", "label": "Origen: aprobado", "value": 18, "more": True, "w": "s"},
    {"id": "dmax", "type": "number", "label": "Origen: mejor", "value": 30, "more": True, "w": "s"},
    {"id": "amin", "type": "number", "label": "Destino: peor", "value": 0, "more": True, "w": "s"},
    {"id": "aap", "type": "number", "label": "Destino: aprobado", "value": 5, "more": True, "w": "s"},
    {"id": "amax", "type": "number", "label": "Destino: mejor", "value": 10, "more": True, "w": "s"},
    {"id": "pct", "type": "number", "label": "Tu posición (top)", "value": "", "unit": "%", "more": True, "w": "s"},
]

TOOL = {
    "slug": "notas-erasmus-ects",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "world",
    "order": 40,
    "name": "Conversor notas Erasmus",
    "k": "equivalencia notas erasmus italia alemania francia portugal ects convertir calificaciones extranjero",
    "title": "Convertir notas Erasmus: equivalencia entre países",
    "desc": "Convierte notas de Erasmus entre la escala española y la de Italia, Alemania, Francia, Portugal y otros países, con tabla y letra ECTS.",
    "h1": "Conversor de notas Erasmus",
    "crumb": "Notas Erasmus",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": JS,
    "data": {"lab": {k: lab for k, lab, *_ in SCALES}},
    "css": ".er-t{max-width:20rem}",
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Comisión Europea · ECTS Users' Guide 2015 (tablas de distribución de notas)", "https://op.europa.eu/en/publication-detail/-/publication/da7467e6-8450-11e5-b8b7-01aa75ed71a1"),
                ("BOE · Real Decreto 1125/2003, art. 5 (escala española de 0 a 10)", "https://www.boe.es/buscar/act.php?id=BOE-A-2003-17643")],
    "credits": [],
    "related": ["nota-media-ponderada", "nota-necesaria-examen", "nota-acceso-universidad"],
    "tests": [
        ({}, {"n.y": 8.75}),
        ({"nota": "2,3", "de": "de", "dmin": "5", "dap": "4", "dmax": "1"}, {"n.y": 7.833333}),
        ({"nota": "8", "de": "es", "dmin": "0", "dap": "5", "dmax": "10", "a": "it", "amin": "0", "aap": "18", "amax": "30"}, {"n.y": 25.2}),
        ({"nota": "15"}, {"n.y": 4.166667}),
        ({"nota": "27", "pct": "30"}, {"n.letra": "B"}),
        ({"nota": "31"}, {"err": "La nota tiene que estar entre 0 y 30."}),
    ],
}
