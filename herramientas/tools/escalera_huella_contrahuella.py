"""Escalera: number of steps, riser and tread for a floor-to-floor height with Blondel's rule (2C + H = 63 cm), checked
against CTE DB-SUA 1 (uso general / uso restringido). English twin: stair_calculator.py (same JS, IRC and UK Part K)."""
import math

from herramientas.tools import _bricolaje as F

CTE_SUA = "https://www.codigotecnico.org/pdf/Documentos/SUA/DBSUA.pdf"

# limits in cm: cmin/cmax riser, hmin tread, b = 2C+H range, fl = max rise of one flight, pitch = max angle
CODES = {
    "gen": {"cmin": 13, "cmax": 18.5, "hmin": 28, "b": [54, 70], "fl": 320, "pitch": 0},
    "res": {"cmin": 0, "cmax": 20, "hmin": 22, "b": None, "fl": 0, "pitch": 0},
    "irc": {"cmin": 0, "cmax": 19.685, "hmin": 25.4, "b": None, "fl": 383.54, "pitch": 0},
    "uk": {"cmin": 15, "cmax": 22, "hmin": 22, "b": [55, 70], "fl": 0, "pitch": 42},
}

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var us = EN && v.u === 'us', k = us ? 2.54 : 1;
  var T = EN ? { h: 'Enter the total rise (floor to floor).', n: 'Too few steps for that rise.', label: 'Stairs', st: ' steps of ', rise: 'Total rise',
      c: 'Riser', t: 'Tread (going)', b: '2 × riser + tread', nr: 'Risers', nt: 'Treads', run: 'Total run', ang: 'Pitch', str: 'Stringer length',
      ok: 'Meets ', no: 'Does not meet ', room: 'Space available', land: 'Landing needed: one flight may rise at most ' }
    : { h: 'Escribe la altura a salvar (de suelo a suelo).', n: 'Demasiado pocos peldaños para esa altura.', label: 'Escalera', st: ' peldaños de ', rise: 'Altura a salvar',
      c: 'Contrahuella', t: 'Huella', b: '2C + H', nr: 'Contrahuellas', nt: 'Huellas', run: 'Longitud en planta', ang: 'Inclinación', str: 'Largo de la zanca',
      ok: 'Cumple ', no: 'No cumple ', room: 'Espacio disponible', land: 'Hace falta una meseta: un tramo salva como mucho ' };
  var D = C.d.codes[v.uso] || C.d.codes.gen, NAME = C.d.names[v.uso] || '';
  if (!(v.alto > 0)) return { err: T.h };
  var Ht = v.alto * k;
  var nmin = Math.ceil(Ht / D.cmax - 1e-9), n = v.np > 0 ? Math.floor(v.np) : Math.max(nmin, Math.round(Ht / 17.5));
  if (n < 2) return { err: T.n };
  var c = Ht / n;
  var t = v.huella > 0 ? v.huella * k : Math.max(D.hmin, 63 - 2 * c);
  var b = 2 * c + t, run = (n - 1) * t, ang = Math.atan(c / t) * 180 / Math.PI, str = Math.sqrt(run * run + Math.pow(Ht - c, 2));
  var fails = [];
  if (c > D.cmax + 1e-9) fails.push(T.c + ' > ' + L(D.cmax));
  if (D.cmin && c < D.cmin - 1e-9) fails.push(T.c + ' < ' + L(D.cmin));
  if (t < D.hmin - 1e-9) fails.push(T.t + ' < ' + L(D.hmin));
  if (D.b && (b < D.b[0] - 1e-9 || b > D.b[1] + 1e-9)) fails.push(T.b + ' ' + L(D.b[0]) + '–' + L(D.b[1]));
  if (D.pitch && ang > D.pitch + 1e-9) fails.push(T.ang + ' > ' + D.pitch + '°');
  var land = D.fl && Ht > D.fl + 1e-9;
  function L(cm) { return us ? fv(cm / 2.54, 2) + ' in' : fv(cm, 1) + ' cm'; }
  function Lm(cm) { return us ? fv(cm / 30.48, 2) + ' ft' : fx(cm / 100, 2) + ' m'; }
  var rows = [[T.rise, L(Ht)], [T.nr, String(n)], [T.c, L(c), 'tot'], [T.t, L(t), 'tot'], [T.b, L(b)], [T.nt, String(n - 1)],
    [T.run, Lm(run)], [T.ang, fv(ang, 1) + '°'], [T.str, Lm(str)]];
  if (v.largo > 0) rows.push([T.room, Lm(v.largo * k) + (v.largo * k + 1e-9 < run ? ' ✗' : ' ✓')]);
  var note = (fails.length ? T.no + NAME + ': ' + fails.join(' · ') + '.' : T.ok + NAME + '.') + (land ? ' ' + T.land + Lm(D.fl) + '.' : '');
  return {
    label: T.label, big: n + T.st + L(c), sub: T.t + ' ' + L(t) + ' · ' + T.b + ' = ' + L(b),
    rows: rows, note: note,
    n: { n: n, c: r(c, 3), t: r(t, 3), run: r(run, 2), ok: !fails.length, land: !!land }
  };
}
"""

NAMES_ES = {"gen": "CTE DB-SUA, escalera de uso general", "res": "CTE DB-SUA, escalera de uso restringido"}
NAMES_EN = {"irc": "IRC R311.7", "uk": "Approved Document K (private stair)", "gen": "Spain CTE, general use"}


def stair(Ht, cmax=18.5, hmin=28):
    n = max(math.ceil(Ht / cmax - 1e-9), round(Ht / 17.5))
    c = Ht / n
    t = max(hmin, 63 - 2 * c)
    return n, c, t, (n - 1) * t


def blocks(ctx):
    n = F.n
    n1, c1, t1, run1 = stair(280)
    n2, c2, t2, run2 = stair(265, 20, 22)
    return [
        ("Cuántos peldaños y de qué medida", f"""
<p>Divide la altura total entre una contrahuella cómoda, de unos 17,5 cm, y redondea: ese es el número de peldaños. Luego
saca la huella con la regla de Blondel, <b>2C + H = 63 cm</b>, el paso medio de una persona. Para salvar 280 cm de suelo a
suelo salen {n1} contrahuellas de {n(c1, 1)} cm y huellas de {n(t1, 1)} cm. Como el último peldaño es el propio suelo de
arriba, hay {n1 - 1} huellas y la escalera ocupa {n(run1 / 100, 2)} m en planta.</p>
<p>Dentro de una vivienda (uso restringido) se permiten peldaños más altos y huellas más cortas. Para 265 cm salen {n2}
contrahuellas de {n(c2, 1)} cm y huellas de {n(t2, 1)} cm: {n(run2 / 100, 2)} m de recorrido. Si no tienes ese espacio,
escribe en «Más opciones» la huella que te cabe o el número de peldaños y la calculadora te dice si cumple.</p>"""),
        ("Lo que exige el Código Técnico", """
<p>El Documento Básico SUA 1 del Código Técnico de la Edificación fija las medidas. En escaleras de <b>uso general</b>
(portales, zonas comunes, locales): huella de 28 cm como mínimo en tramos rectos, contrahuella entre 13 y 18,5 cm (17,5 cm
como máximo en zonas de uso público o si no hay ascensor alternativo) y la relación 54 cm ≤ 2C + H ≤ 70 cm. Cada tramo
tendrá al menos 3 peldaños y salvará como mucho 3,20 m (2,25 m en zonas de uso público sin ascensor); si la altura es mayor,
hace falta una meseta de 1 m de largo como mínimo.</p>
<p>En escaleras de <b>uso restringido</b>, las de dentro de una vivienda o las que usan como mucho 10 personas habituales,
la contrahuella será de 20 cm como máximo y la huella de 22 cm como mínimo, con un ancho de tramo de 0,80 m. Todos los
peldaños entre dos plantas deben tener la misma contrahuella, y en tramos rectos, la misma huella.</p>"""),
        ("Cómo medir", """
<p>Mide la altura a salvar de suelo terminado a suelo terminado: si todavía falta el pavimento de abajo o de arriba, suma o
resta su grosor, porque un centímetro de error se reparte entre todos los peldaños pero se nota entero en el primero o en el
último. La huella se mide en horizontal de borde a borde sin contar el vuelo del peldaño superior. La zanca es la viga
inclinada que sostiene los peldaños; su largo es la hipotenusa entre la longitud en planta y la altura hasta la última huella.</p>"""),
    ]


FAQ = [
    ("¿Cuál es la medida ideal de un peldaño?",
     "Una contrahuella de 17 a 18 cm con una huella de 27 a 29 cm. Cumple la regla de Blondel (2C + H ≈ 63 cm) y las medidas del CTE."),
    ("¿Cuántos peldaños tiene una escalera de 3 metros?",
     "Unos 17 peldaños con contrahuellas de 17,6 cm. Aunque sea de uso general cabe en un solo tramo, porque el CTE pide meseta "
     "a partir de 3,20 m de altura."),
    ("¿Qué es la regla de Blondel?",
     "Una fórmula del arquitecto François Blondel (siglo XVII): dos contrahuellas más una huella deben medir unos 63 cm, la longitud del paso de una persona."),
    ("¿Cuánto espacio ocupa una escalera?",
     "El número de huellas por la medida de la huella. Para 280 cm de altura con huellas de 28 cm, unos 4,2 m en planta, más el desembarco."),
    ("¿Puedo hacer una escalera más empinada en mi casa?",
     "Dentro de la vivienda el CTE admite contrahuellas de hasta 20 cm y huellas de 22 cm. Más empinada ya es una escalera de servicio o de altillo."),
]

TOOL = {
    "slug": "escalera-huella-contrahuella",
    "lang": "es",
    "twin": "stair-calculator",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "stairs",
    "order": 50,
    "name": "Calculadora de escaleras",
    "k": "peldaños huella contrahuella blondel cte db-sua escalera medidas zanca",
    "title": "Calcular escalera: huella y contrahuella (CTE)",
    "desc": "Calcula el número de peldaños, la huella y la contrahuella de una escalera con la regla de Blondel y comprueba si cumple el CTE DB-SUA.",
    "h1": "Calculadora de escaleras: huella y contrahuella",
    "updated": "2026-11-12",
    "data": {"codes": CODES, "names": NAMES_ES},
    "inputs": [
        {"id": "alto", "type": "number", "label": "Altura a salvar", "value": "280", "unit": "cm", "step": "0.1"},
        {"id": "uso", "type": "seg", "label": "Uso", "value": "gen", "options": [("gen", "General"), ("res", "Vivienda")]},
        {"id": "largo", "type": "number", "label": "Espacio en planta", "value": "", "unit": "cm", "more": True},
        {"id": "huella", "type": "number", "label": "Huella", "value": "", "unit": "cm", "step": "0.1", "w": "s", "more": True},
        {"id": "np", "type": "number", "label": "Peldaños", "value": "", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("CTE · Documento Básico SUA, sección SUA 1, apartado 4 (escaleras)", CTE_SUA)],
    "related": ["hormigon-mortero", "calculadora-tarima-suelo", "calculadora-azulejos", "papel-pintado"],
    "tests": [
        ({}, {"n.n": 16, "n.c": 17.5, "n.t": 28, "n.run": 420, "n.ok": True, "n.land": False}),
        ({"alto": "300", "uso": "res"}, {"n.n": 17, "n.c": 17.647, "n.t": 27.706, "n.ok": True}),
        ({"alto": "350"}, {"n.n": 20, "n.land": True}),
        ({"huella": "25"}, {"n.t": 25, "n.ok": False}),
        ({"np": "14"}, {"n.c": 20, "n.ok": False}),
        ({"alto": ""}, {"err": "Escribe la altura a salvar (de suelo a suelo)."}),
    ],
}
