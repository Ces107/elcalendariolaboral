"""Ritmo de natación: pace per 100 m (or yd), a main set (reps x distance at a pace with rest -> send-off and total) and
critical swim speed from a 400 and a 200 test (Wakayoshi et al. 1992). EN twin: swim-pace-calculator."""
from herramientas.tools import _deporte as D

WAKAYOSHI = "https://pubmed.ncbi.nlm.nih.gov/1555562/"
NIST = "https://www.nist.gov/pml/us-surveyfoot/revised-unit-conversion-factors"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  %TIME%
  var u = v.u === 'yd' ? 'yd' : 'm', Y = 0.9144;
  var T = EN ? {
    dist: 'Enter the distance.', time: 'Enter the time as mm:ss.', pace: 'Enter the pace per 100 as m:ss.', reps: 'Enter 1 to 100 repeats.', rest: 'Rest must be 0 to 600 seconds.',
    css: 'Enter both test times as mm:ss.', css2: 'Your 400 must take more than twice your 200.', slow: 'Slower than 10:00 per 100: check the numbers.',
    pace_l: 'Pace', per: '/100 ' + u, speed: 'Speed', same: 'At this pace', set: 'Main set', swim: 'Swim time per repeat', send: 'Send-off (leave every)',
    total: 'Total set time', dtot: 'Set distance', cssl: 'Critical swim speed (CSS)', t400: '400 test', t200: '200 test', R: 'Distance', tt: 'Time'
  } : {
    dist: 'Indica la distancia.', time: 'Escribe el tiempo como mm:ss.', pace: 'Escribe el ritmo por 100 como m:ss.', reps: 'Indica de 1 a 100 repeticiones.', rest: 'El descanso debe estar entre 0 y 600 segundos.',
    css: 'Escribe los dos tiempos del test como mm:ss.', css2: 'Tu 400 tiene que durar más del doble que tu 200.', slow: 'Más lento de 10:00 por 100: revisa los datos.',
    pace_l: 'Ritmo', per: '/100 ' + u, speed: 'Velocidad', same: 'A este ritmo', set: 'Serie', swim: 'Tiempo nadando por repetición', send: 'Salida cada',
    total: 'Tiempo total de la serie', dtot: 'Metros de la serie', cssl: 'Velocidad crítica de nado (CSS)', t400: 'Test de 400', t200: 'Test de 200', R: 'Distancia', tt: 'Tiempo'
  };
  function table(p) {
    var ds = u === 'yd' ? [50, 100, 200, 500, 1000, 1650] : [50, 100, 200, 400, 800, 1500, 1900, 3800];
    return '<h3 class="rn-h">' + T.same + ' (' + ft(p) + ' ' + T.per + ')</h3><table class="tbl rn-t"><tbody>' + ds.map(function (d) {
      return '<tr><td>' + fv(d, 0) + ' ' + u + '</td><td class="num">' + ft(p * d / 100) + '</td></tr>';
    }).join('') + '</tbody></table>';
  }
  function kmh(p) { return 100 * (u === 'yd' ? Y : 1) / p * 3.6; }
  if (v.modo === 'css') {
    var a = tp(v.t400), b = tp(v.t200);
    if (!(a > 0 && b > 0)) return { err: T.css };
    if (a <= 2 * b) return { err: T.css2 };
    var css = (a - b) / 2;
    if (css > 600) return { err: T.slow };
    return {
      label: T.cssl, big: ft(css, true) + ' ' + T.per, sub: fx(kmh(css), 2) + ' km/h · (' + ft(a) + ' − ' + ft(b) + ') ÷ 2',
      rows: [[T.t400, ft(a) + ' · ' + ft(a / 4) + ' ' + T.per], [T.t200, ft(b) + ' · ' + ft(b / 2) + ' ' + T.per], [T.cssl, ft(css, true) + ' ' + T.per, 'tot']],
      html: table(css), n: { css: r(css, 2) }
    };
  }
  if (v.modo === 'serie') {
    var p = tp(v.ritmo), n = v.reps, d = v.drep, rest = isNaN(v.desc) ? 0 : v.desc;
    if (!(n >= 1 && n <= 100) || n % 1) return { err: T.reps };
    if (!(d > 0)) return { err: T.dist };
    if (!(p > 0)) return { err: T.pace };
    if (p > 600) return { err: T.slow };
    if (!(rest >= 0 && rest <= 600)) return { err: T.rest };
    var sw = p * d / 100, tot = sw * n + rest * (n - 1);
    return {
      label: T.set + ' · ' + n + ' × ' + fv(d, 0) + ' ' + u, big: ft(tot), sub: fv(n * d, 0) + ' ' + u + ' · ' + ft(p) + ' ' + T.per + ' · ' + T.send + ' ' + ft(sw + rest),
      rows: [[T.swim, ft(sw, true)], [T.send, ft(sw + rest)], [T.dtot, fv(n * d, 0) + ' ' + u], [T.total, ft(tot), 'tot']],
      n: { swim: r(sw, 2), send: r(sw + rest, 2), total: r(tot, 2) }
    };
  }
  var t = tp(v.tiempo), dist = v.dist;
  if (!(dist > 0)) return { err: T.dist };
  if (!(t > 0)) return { err: T.time };
  var pc = t / dist * 100;
  if (pc > 600) return { err: T.slow };
  return {
    label: T.pace_l, big: ft(pc, true) + ' ' + T.per, sub: fx(kmh(pc), 2) + ' km/h · ' + fv(dist, 0) + ' ' + u + ' ' + (EN ? 'in' : 'en') + ' ' + ft(t),
    html: table(pc), n: { pace: r(pc, 3), kmh: r(kmh(pc), 3) }
  };
}
"""

CSS = ".rn-h{font-size:1rem;margin:1rem 0 .3rem}.rn-t{max-width:20rem}"


def inputs(lang):
    es = lang == "es"
    return [
        {"id": "modo", "type": "seg", "label": "Calcular" if es else "Find", "value": "ritmo",
         "options": [("ritmo", "Ritmo" if es else "Pace"), ("serie", "Serie" if es else "Set"), ("css", "CSS")]},
        {"id": "u", "type": "seg", "label": "Piscina" if es else "Pool", "value": "m" if es else "yd", "options": [("m", "m"), ("yd", "yd")]},
        {"id": "dist", "type": "number", "label": "Distancia" if es else "Distance", "value": "1500" if es else "1650", "w": "s", "show": ("modo", ["ritmo"])},
        {"id": "tiempo", "type": "text", "label": "Tiempo" if es else "Time", "value": "30:00", "placeholder": "mm:ss", "w": "s", "show": ("modo", ["ritmo"])},
        {"id": "reps", "type": "number", "label": "Repeticiones" if es else "Repeats", "value": "10", "w": "s", "show": ("modo", ["serie"])},
        {"id": "drep", "type": "number", "label": "Distancia" if es else "Distance", "value": "100", "w": "s", "show": ("modo", ["serie"])},
        {"id": "ritmo", "type": "text", "label": "Ritmo /100" if es else "Pace /100", "value": "1:50", "placeholder": "m:ss", "w": "s", "show": ("modo", ["serie"])},
        {"id": "desc", "type": "number", "label": "Descanso" if es else "Rest", "value": "15", "unit": "s", "w": "s", "show": ("modo", ["serie"])},
        {"id": "t400", "type": "text", "label": "400", "value": "7:20", "placeholder": "mm:ss", "w": "s", "show": ("modo", ["css"])},
        {"id": "t200", "type": "text", "label": "200", "value": "3:30", "placeholder": "mm:ss", "w": "s", "show": ("modo", ["css"])},
    ]


def blocks(ctx):
    css = (440 - 210) / 2
    return [
        ("El ritmo por 100 metros", f"""
<p>En natación el ritmo se mide en <b>tiempo por cada 100 metros</b>: ritmo = tiempo ÷ distancia × 100. Si nadas 1.500 m
en 30 minutos, vas a <b>2:00 /100 m</b>, unos 3 km/h. Con ese ritmo, la tabla te dice cuánto tardarías en 400 m (8:00), en
los 1.900 m de un medio Ironman (38:00) o en los 3.800 m de un Ironman (1:16:00), sin contar el desgaste ni la diferencia
entre piscina y aguas abiertas. Si entrenas en una piscina en yardas, cambia «Piscina» a yd y el ritmo se da por 100 yardas
(1 yarda = 0,9144 m).</p>"""),
        ("Calcular una serie", """
<p>En «Serie» escribes las repeticiones, la distancia de cada una, el ritmo al que quieres nadarlas y el descanso. Sale
el tiempo de cada repetición, la <b>salida</b> (cada cuánto se sale en el reloj de ritmo de la piscina: tiempo nadando más
descanso) y el tiempo total. Ejemplo: 10 × 100 m a 1:50 con 15 segundos de descanso es salir cada 2:05, y la serie completa
dura 20:35 (el último descanso no cuenta), con 1.000 metros nadados.</p>"""),
        ("Velocidad crítica de nado (CSS)", f"""
<p>La <b>CSS</b> (critical swim speed) es el ritmo que podrías mantener durante mucho tiempo sin que el cansancio se
dispare, el equivalente al umbral en carrera. Se estima con dos pruebas a tope el mismo día, un 400 y un 200 con buen
descanso entre ellas: <b>CSS = (tiempo del 400 − tiempo del 200) ÷ 2</b>, por cada 100 metros. Con 7:20 en el 400 y 3:30 en el
200, la CSS es (440 − 210) ÷ 2 = {css:g} segundos, <b>{D.t(css)} /100 m</b>. El método procede del estudio de Wakayoshi y
colaboradores (1992) con nadadores de competición, que relacionó esta velocidad con el umbral de lactato. Repite el test
cada 6 a 8 semanas: si tu CSS baja, has mejorado. Muchas series de fondo se nadan a ritmo CSS o unos segundos más lento.</p>"""),
    ]


FAQ = [
    ("¿Qué es un buen ritmo de natación por 100 metros?",
     "Para un nadador popular adulto, entre 2:00 y 2:30 /100 m en distancias largas es habitual. Por debajo de 1:40 ya es un nivel de club; los nadadores de élite van por debajo de 1:10 en 1.500."),
    ("¿Cuánto se tarda en nadar 1.500 metros?",
     "A 2:00 /100 m, 30 minutos; a 2:30, 37:30; a 1:45, 26:15. Escribe tu tiempo y la herramienta te da el ritmo exacto."),
    ("¿Qué significa «salida cada 2:05»?",
     "Que cada repetición empieza cuando el reloj de la piscina ha avanzado 2:05 desde la anterior: el tiempo que no nadas es tu descanso."),
    ("¿Cómo hago el test de CSS?",
     "Calienta bien, nada un 400 a tope, descansa 5-10 minutos nadando suave y nada un 200 a tope. Apunta los dos tiempos y escríbelos en «CSS»."),
    ("¿Sirve para piscinas en yardas?",
     "Sí: elige «yd» y todas las distancias y ritmos pasan a yardas. La velocidad se sigue dando en km/h."),
]

TOOL = {
    "slug": "ritmo-natacion",
    "lang": "es",
    "twin": "swim-pace-calculator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "swimming",
    "order": 100,
    "name": "Ritmo de natación",
    "k": "natación ritmo 100 metros piscina series salida css velocidad crítica triatlón",
    "title": "Calculadora de ritmo de natación por 100 m y series",
    "desc": "Calcula tu ritmo de natación por 100 m, el tiempo y la salida de una serie con descanso, y tu velocidad crítica (CSS) con un test de 400 y 200.",
    "h1": "Calculadora de ritmo de natación",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Wakayoshi K et al. (1992). Determination and validity of critical velocity as an index of swimming performance. Eur J Appl Physiol 64: 153-157", WAKAYOSHI),
                ("NIST · yarda internacional = 0,9144 m", NIST)],
    "credits": [("Velocidad crítica de nado (Wakayoshi et al., 1992)", "fórmula publicada (reimplementada)", WAKAYOSHI)],
    "related": ["ritmo-carrera", "zonas-frecuencia-cardiaca", "desarrollo-bicicleta"],
    "tests": [
        ({}, {"n.pace": 120, "n.kmh": 3}),
        ({"modo": "serie"}, {"n.swim": 110, "n.send": 125, "n.total": 1235}),
        ({"modo": "css"}, {"n.css": 115}),
        ({"modo": "css", "t400": "6:00", "t200": "3:10"}, {"err": "Tu 400 tiene que durar más del doble que tu 200."}),
        ({"u": "yd", "dist": "100", "tiempo": "1:30"}, {"n.pace": 90, "n.kmh": 3.6576}),
        ({"tiempo": ""}, {"err": "Escribe el tiempo como mm:ss."}),
    ],
}
