"""Tiempo de una ruta de montaña: MIDE (FEDME/FAM, horizontal 5/4/3 km/h, 400 m/h up, 600 m/h down, larger time plus
half the smaller) or Naismith (5 km/h + 1 h per 600 m up, Langmuir descent corrections); start time -> arrival, MIDE
effort grade. EN twin: hiking-time-calculator."""
from herramientas.tools import _deporte as D

MIDE_URL = "https://www.montanasegura.com/mide/"
MIDE_PDF = "https://www.adm-suances.es/sites/default/files/manualmide.pdf"
NAISMITH_URL = "https://en.wikipedia.org/wiki/Naismith%27s_rule"

JS = r"""
function (v, H, C) {
  var EN = %EN%, FT = 0.3048, MI = 1.609344;
  %FMT%
  var T = EN ? {
    dist: 'Enter the distance.', up: 'Enter the total ascent (0 if none).', down: 'Descent cannot be negative.', far: 'That is more than a week of walking: split the route into stages.',
    lab: 'Walking time', eff: 'MIDE effort', grade: ['', 'up to 1 h', '1 to 3 h', '3 to 6 h', '6 to 10 h', 'over 10 h'], hor: 'Horizontal', ver: 'Climb and descent',
    rule: 'MIDE: the longer time plus half the shorter', nai: 'Naismith', lang: 'Langmuir descent', stops: 'Stops', total: 'Total with stops', arr: 'Arrival', start: 'Start',
    h: 'h', min: 'min', note: 'Walking time without stops, for an average fit walker with a light pack.'
  } : {
    dist: 'Indica la distancia.', up: 'Indica el desnivel de subida (0 si no hay).', down: 'La bajada no puede ser negativa.', far: 'Eso es más de una semana andando: divide la ruta en etapas.',
    lab: 'Tiempo de marcha', eff: 'Esfuerzo MIDE', grade: ['', 'hasta 1 h', 'de 1 a 3 h', 'de 3 a 6 h', 'de 6 a 10 h', 'más de 10 h'], hor: 'Horizontal', ver: 'Subida y bajada',
    rule: 'MIDE: el mayor más la mitad del menor', nai: 'Naismith', lang: 'Corrección de bajada', stops: 'Paradas', total: 'Total con paradas', arr: 'Llegada', start: 'Salida',
    h: 'h', min: 'min', note: 'Tiempo de marcha sin paradas, para un excursionista medio con mochila ligera.'
  };
  function fh(x) { var m = Math.round(x * 60), h = Math.floor(m / 60); m -= h * 60; return (h ? h + ' ' + T.h + ' ' : '') + (m || !h ? m + ' ' + T.min : '').trim(); }
  var imp = v.u === 'imp', km = imp ? v.dist * MI : v.dist, up = (isNaN(v.sube) ? NaN : v.sube) * (imp ? FT : 1), dn = isNaN(v.baja) ? 0 : v.baja * (imp ? FT : 1);
  if (!(km > 0)) return { err: T.dist };
  if (!(up >= 0)) return { err: T.up };
  if (dn < 0) return { err: T.down };
  var th, tv, t, rows = [];
  /* imperial inputs: show the miles and feet typed, then the metric figure the rule uses */
  var dk = imp ? fv(r(v.dist, 2)) + ' mi = ' + fv(r(km, 2)) + ' km' : fv(r(km, 2)) + ' km';
  function mt(x, raw) { return imp ? fv(raw, 0) + ' ft = ' + Math.round(x) + ' m' : Math.round(x) + ' m'; }
  if (v.met === 'mide') {
    var vh = +v.piso || 4;
    th = km / vh; tv = up / 400 + dn / 600;
    t = Math.max(th, tv) + Math.min(th, tv) / 2;
    rows.push([T.hor + ' · ' + dk + ' ÷ ' + vh + ' km/h', fh(th)], [T.ver + ' · ' + Math.round(up) + ' m ÷ 400 + ' + Math.round(dn) + ' m ÷ 600', fh(tv)], [T.rule, fh(t), 'tot']);
  } else {
    th = km / 5; tv = up / 600;
    var corr = v.lang === 'suave' ? -dn / 300 * 10 / 60 : v.lang === 'fuerte' ? dn / 300 * 10 / 60 : 0;
    t = th + tv + corr;
    rows.push([T.hor + ' · ' + dk + ' ÷ 5 km/h', fh(th)], ['+ ' + mt(up, v.sube) + ' ÷ 600 m/h', fh(tv)]);
    if (corr) rows.push([T.lang + ' · ' + mt(dn, v.baja), (corr < 0 ? '−' : '+') + fh(Math.abs(corr))]);
    rows.push([T.nai, fh(t), 'tot']);
  }
  if (t > 24 * 7) return { err: T.far };
  var stop = v.paradas > 0 ? v.paradas / 60 : 0, tt = t + stop;
  if (stop) rows.push([T.stops, fh(stop)], [T.total, fh(tt), 'tot']);
  var g = t <= 1 ? 1 : t <= 3 ? 2 : t <= 6 ? 3 : t <= 10 ? 4 : 5, arr = '';
  var m0 = /^(\d{1,2}):(\d\d)$/.exec(String(v.salida || '').trim());
  if (m0) {
    var mins = (+m0[1] * 60 + +m0[2] + Math.round(tt * 60)), day = Math.floor(mins / 1440); mins %= 1440;
    arr = (mins / 60 | 0) + ':' + ('0' + mins % 60).slice(-2) + (day ? ' (+' + day + ')' : '');
    rows.push([T.start + ' ' + m0[1] + ':' + m0[2] + ' → ' + T.arr, arr, 'tot']);
  }
  return {
    label: T.lab, big: fh(t), sub: T.eff + ' ' + g + ' · ' + T.grade[g] + (arr ? ' · ' + T.arr + ' ' + arr : ''), rows: rows, note: T.note,
    n: { hours: r(t, 4), effort: g, arr: arr || null }
  };
}
"""

INPUTS_ES = [
    {"id": "met", "type": "seg", "label": "Método", "value": "mide", "options": [("mide", "MIDE"), ("nai", "Naismith")]},
    {"id": "dist", "type": "number", "label": "Distancia", "value": "12", "unit": "km", "step": "0.1", "w": "s"},
    {"id": "sube", "type": "number", "label": "Desnivel +", "value": "800", "unit": "m", "w": "s"},
    {"id": "baja", "type": "number", "label": "Desnivel −", "value": "800", "unit": "m", "w": "s"},
    {"id": "piso", "type": "select", "label": "Camino", "value": "4", "show": ("met", ["mide"]),
     "options": [("5", "Pista o carretera · 5 km/h"), ("4", "Senda buena · 4 km/h"), ("3", "Mala senda, pedrera · 3 km/h")]},
    {"id": "lang", "type": "select", "label": "Bajada", "value": "no", "show": ("met", ["nai"]),
     "options": [("no", "Sin corregir"), ("suave", "Suave (5-12°) · −10 min/300 m"), ("fuerte", "Empinada (>12°) · +10 min/300 m")]},
    {"id": "salida", "type": "time", "label": "Salida", "value": "", "w": "s"},
    {"id": "paradas", "type": "number", "label": "Paradas", "value": "", "unit": "min", "w": "s", "more": True},
    {"id": "u", "type": "seg", "label": "Unidades", "value": "met", "more": True, "options": [("met", "km · m"), ("imp", "millas · pies")]},
]


def _mide(km, up, dn, vh):
    th, tv = km / vh, up / 400 + dn / 600
    return max(th, tv) + min(th, tv) / 2, th, tv


def _fh(x):
    m = round(x * 60)
    h, m = divmod(m, 60)
    return (f"{h} h " if h else "") + (f"{m} min" if m or not h else "").strip()


def blocks(ctx):
    t, th, tv = _mide(12, 800, 800, 4)
    nai = 12 / 5 + 800 / 600
    t2, _, _ = _mide(8, 1100, 0, 4)
    return [
        ("Cómo calcula el tiempo el MIDE", f"""
<p>El <b>MIDE</b> (Método de Información de Excursiones), que recomiendan la FEDME y las federaciones autonómicas y que
aparece en los paneles de inicio de muchos senderos, calcula el horario en tres pasos. Primero, el tiempo por distancia
horizontal: 5 km/h por pistas y carreteras, 4 km/h por sendas buenas y prados, 3 km/h por malas sendas, pedreras o cauces.
Segundo, el tiempo por desnivel: <b>400 m por hora de subida y 600 m por hora de bajada</b>. Tercero, se toma <b>el mayor de
los dos y se le suma la mitad del menor</b>.</p>
<p>Ejemplo: una ruta circular de 12 km por senda con 800 m de subida y 800 de bajada. Horizontal: 12 ÷ 4 = {_fh(th)}.
Desnivel: 800 ÷ 400 + 800 ÷ 600 = {_fh(tv)}. Horario MIDE: {_fh(tv)} + la mitad de {_fh(th)} = <b>{_fh(t)}</b> de marcha efectiva,
esfuerzo 3 (de 3 a 6 horas). Una subida a cumbre de 8 km con 1.100 m de desnivel solo de ida sale en {_fh(t2)}.</p>"""),
        ("La regla de Naismith", f"""
<p>En 1892 el montañero escocés William W. Naismith propuso una regla que aún se enseña en las escuelas de montaña
británicas: <b>una hora por cada 5 km (3 millas) y una hora más por cada 600 m (2.000 pies) de subida</b>. Para la misma ruta
de 12 km y 800 m da {_fh(nai)}, casi una hora menos que el MIDE, porque Naismith pensaba en montañeros en forma y no cuenta la
bajada. Eric Langmuir añadió después dos correcciones: restar 10 minutos por cada 300 m de bajada suave (de 5 a 12 grados)
y sumar 10 minutos por cada 300 m de bajada empinada (más de 12 grados), que es donde de verdad se frena el paso.</p>"""),
        ("Del tiempo de marcha al horario del día", """
<p>Las dos fórmulas dan tiempo de marcha efectiva, sin paradas. Para planificar el día, suma las paradas que pienses
hacer (comer, fotos, fuentes) en «Más opciones» y escribe la hora de salida para ver a qué hora llegarás. Comprueba que esa
hora queda con margen antes de que anochezca, sobre todo en invierno, y recuerda que con niños, mochila pesada, nieve o
calor el ritmo baja bastante. El grado de esfuerzo MIDE va de 1 (hasta 1 hora de marcha) a 5 (más de 10 horas) y es el mismo
que verás en los paneles y topoguías.</p>"""),
    ]


FAQ = [
    ("¿Cuánto se tarda en subir 1.000 metros de desnivel?",
     "Unas 2 h 30 min solo por el desnivel, según el MIDE (400 m/h). Si además hay distancia horizontal, se suma la mitad del tiempo menor."),
    ("¿A qué velocidad se anda por la montaña?",
     "En llano, 4 a 5 km/h por buenas sendas y pistas. En subida, unos 400 m de desnivel por hora; en bajada, unos 600."),
    ("¿El MIDE incluye las paradas?",
     "No: calcula horas de marcha efectiva. Añade las paradas aparte, con «Paradas» en «Más opciones»."),
    ("¿Qué método es más fiable?",
     "El MIDE se ajusta mejor a un excursionista medio y cuenta la bajada. Naismith suele quedarse corto salvo para gente en buena forma."),
    ("¿Qué es el desnivel acumulado?",
     "La suma de todos los metros que subes (desnivel +) o bajas (desnivel −) en la ruta, no solo la diferencia entre la salida y la cumbre."),
]

TOOL = {
    "slug": "tiempo-ruta-montana",
    "lang": "es",
    "twin": "hiking-time-calculator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "mountain",
    "order": 70,
    "name": "Tiempo de ruta",
    "k": "mide naismith senderismo excursión desnivel horario montaña tiempo ruta calcular",
    "title": "Calcular el tiempo de una ruta de montaña (MIDE y Naismith)",
    "desc": "Calcula cuánto se tarda en una ruta de senderismo por distancia y desnivel con el método MIDE o la regla de Naismith, con hora de llegada.",
    "h1": "Tiempo de una ruta de montaña",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": D.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("MIDE · Método de Información de Excursiones (FEDME, FAM, Montaña Segura)", MIDE_URL),
                ("Manual MIDE: criterios para el cálculo de horarios", MIDE_PDF),
                ("Naismith's rule y correcciones de Langmuir (Wikipedia)", NAISMITH_URL)],
    "credits": [("Criterios de horario MIDE (FEDME, FAM, Prames)", "método publicado (reimplementado)", MIDE_URL),
                ("Regla de Naismith (W. W. Naismith, 1892) y correcciones de Eric Langmuir", "dominio público (método)", NAISMITH_URL)],
    "related": ["etapas-camino-santiago", "amanecer-atardecer", "ritmo-carrera"],
    "tests": [
        ({}, {"n.hours": 4.8333, "n.effort": 3}),
        ({"met": "nai"}, {"n.hours": 3.7333}),
        ({"met": "nai", "lang": "fuerte"}, {"n.hours": 4.1778}),
        ({"dist": "8", "sube": "1100", "baja": "0", "salida": "08:30", "paradas": "45"}, {"n.hours": 3.75, "n.arr": "13:00"}),
        ({"dist": "0"}, {"err": "Indica la distancia."}),
        ({"u": "imp", "dist": "5", "sube": "1000", "baja": "1000", "piso": "5"}, {"n.effort": 2}),
    ],
}
