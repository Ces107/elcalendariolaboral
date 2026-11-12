"""Predicción de tiempo en maratón (y 5k-media) con la fórmula de Riegel, T2 = T1 x (D2/D1)^k, k = 1,06 by default.
EN twin: race-time-predictor."""
from herramientas.tools import _deporte as D

RIEGEL_URL = "https://www.jstor.org/stable/27850427"

JS = r"""
function (v, H, C) {
  var EN = %EN%, MI = 1.609344;
  %FMT%
  %TIME%
  var T = EN ? {
    dist: 'Enter the race distance.', time: 'Enter your time as h:mm:ss (or mm:ss).', k: 'The exponent should be between 1.00 and 1.20.',
    short: 'Riegel only holds for races of about 3.5 minutes or more: use a longer race.', far: 'Predictions more than 8 times your race distance are optimistic: a half marathon predicts a marathon far better than a 5K.',
    lab: 'Predicted marathon', race: 'Race', tt: 'Time', pace: 'Pace', you: 'your race', fast: 'Faster than the world record: check the time.',
    R: [['1 mile', MI], ['5K', 5], ['10K', 10], ['15K', 15], ['10 miles', 10 * MI], ['Half marathon', 21.0975], ['30K', 30], ['Marathon', 42.195]]
  } : {
    dist: 'Indica la distancia de la carrera.', time: 'Escribe tu tiempo como h:mm:ss (o mm:ss).', k: 'El exponente debe estar entre 1,00 y 1,20.',
    short: 'Riegel solo vale para carreras de unos 3,5 minutos o más: usa una carrera más larga.', far: 'Predecir más de 8 veces tu distancia da tiempos optimistas: una media predice el maratón mucho mejor que un 5 km.',
    lab: 'Maratón previsto', race: 'Carrera', tt: 'Tiempo', pace: 'Ritmo', you: 'tu carrera', fast: 'Más rápido que el récord del mundo: revisa el tiempo.',
    R: [['1 milla', MI], ['5 km', 5], ['10 km', 10], ['15 km', 15], ['10 millas', 10 * MI], ['Media maratón', 21.0975], ['30 km', 30], ['Maratón', 42.195]]
  };
  var d1 = v.dist === 'otra' ? v.km : +v.dist, t1 = tp(v.tiempo), k = isNaN(v.exp) ? 1.06 : v.exp;
  if (!(d1 > 0) || d1 > 100) return { err: T.dist };
  if (!(t1 > 0)) return { err: T.time };
  if (!(k >= 1 && k <= 1.2)) return { err: T.k };
  if (t1 < 210) return { err: T.short };
  if (t1 / d1 < 135) return { err: T.fast };   /* 2:15 min/km beats every record from 1 mile up */
  function pred(d2) { return t1 * Math.pow(d2 / d1, k); }
  var rows = T.R.map(function (x) {
    var t = pred(x[1]), same = Math.abs(x[1] - d1) < 0.01;
    return '<tr' + (same ? ' class="tot"' : '') + '><td>' + x[0] + (same ? ' · ' + T.you : '') + '</td><td class="num">' + ft(same ? t1 : t) + '</td><td class="num">' + ft((same ? t1 : t) / x[1]) + ' /km</td></tr>';
  }).join('');
  var m = pred(42.195);
  return {
    label: T.lab, big: ft(m), sub: ft(m / 42.195) + ' /km · ' + ft(m / 42.195 * MI) + ' /mi',
    html: '<table class="tbl pm-t"><thead><tr><th>' + T.race + '</th><th class="num">' + T.tt + '</th><th class="num">' + T.pace + '</th></tr></thead><tbody>' + rows + '</tbody></table>',
    note: 42.195 / d1 > 8.01 ? T.far : '',
    n: { marathon: r(m, 1), half: r(pred(21.0975), 1), ten: r(pred(10), 1) }
  };
}
"""

CSS = ".pm-t{max-width:28rem}"

INPUTS_ES = [
    {"id": "dist", "type": "select", "label": "Carrera hecha", "value": "10",
     "options": [("5", "5 km"), ("10", "10 km"), ("21.0975", "Media maratón"), ("42.195", "Maratón"), ("otra", "Otra")]},
    {"id": "km", "type": "number", "label": "Distancia", "value": "15", "unit": "km", "step": "0.001", "w": "s", "show": ("dist", ["otra"])},
    {"id": "tiempo", "type": "text", "label": "Tu tiempo", "value": "50:00", "placeholder": "h:mm:ss", "w": "s"},
    {"id": "exp", "type": "number", "label": "Exponente", "value": "1.06", "step": "0.01", "w": "s", "more": True},
]


def _pred(t1, d1, d2, k=1.06):
    return t1 * (d2 / d1) ** k


def blocks(ctx):
    n = D.n
    m10 = _pred(3000, 10, 42.195)
    h10 = _pred(3000, 10, 21.0975)
    m_h = _pred(6300, 21.0975, 42.195)
    m_h7 = _pred(6300, 21.0975, 42.195, 1.08)
    return [
        ("La fórmula de Riegel", f"""
<p>Para estimar tu tiempo en una distancia a partir de otra carrera, Peter Riegel propuso en 1977 una fórmula muy
sencilla: <b>T2 = T1 × (D2 ÷ D1)<sup>1,06</sup></b>. El exponente 1,06 refleja que, al doblar la distancia, no tardas el doble
sino algo más, porque el ritmo cae. Riegel lo ajustó con los récords del mundo de su época y lo publicó con detalle en
<i>American Scientist</i> en 1981; sigue siendo la base de casi todas las calculadoras de predicción y de las tablas de ritmo
de muchos planes de entrenamiento.</p>
<p>Con 50:00 en un 10 km, la fórmula da {D.t(h10)} en la media maratón y <b>{D.t(m10)}</b> en el maratón, a
{D.t(m10 / 42.195)} min/km. Con 1:45:00 en una media, el maratón previsto es {D.t(m_h)}. Escribe tu marca más reciente y la
tabla te da la predicción de la milla al maratón, con el ritmo por kilómetro de cada una.</p>"""),
        ("Qué tan fiable es", f"""
<p>La predicción es buena entre distancias parecidas y cuando has entrenado para la distancia objetivo. Para el maratón,
la mejor referencia es una media maratón reciente: el salto es solo de 2 veces la distancia. Desde un 5 km (8,4 veces) la
fórmula suele quedarse corta, sobre todo si no has hecho tiradas largas de más de 30 km, porque la resistencia y el
agotamiento del glucógeno pesan más que la velocidad. Si eres un corredor popular con poco volumen semanal, sube el
exponente a 1,07 o 1,08 en «Más opciones»: con 1,08, la misma media de 1:45:00 predice {D.t(m_h7)} en lugar de {D.t(m_h)}.</p>
<p>Riegel advirtió que la relación solo se cumple para esfuerzos de entre unos 3,5 minutos y unas 4 horas. Por debajo, la
velocidad depende de otras vías energéticas; por encima, influyen la alimentación, el calor y el cansancio muscular. Usa el
resultado como ritmo de partida para tus entrenamientos y ajústalo con las sensaciones de las últimas semanas.</p>"""),
        ("Cómo usar la predicción", """
<p>Una forma práctica: toma el tiempo previsto, súmale un margen del 2 al 4 % si es tu primer maratón y reparte ese
ritmo de forma uniforme (o los segundos 21 km un poco más rápidos que los primeros). La calculadora de ritmo convierte
ese objetivo en parciales por kilómetro para la pulsera o el reloj.</p>"""),
    ]


FAQ = [
    ("¿Qué tiempo haré en maratón si corro 10 km en 45 minutos?",
     f"Con la fórmula de Riegel, unos {D.t(_pred(2700, 10, 42.195))}. Es una estimación optimista si no has hecho tiradas largas: cuenta con 5 a 15 minutos más en un primer maratón."),
    ("¿Y si corro la media maratón en 2 horas?",
     f"La predicción es {D.t(_pred(7200, 21.0975, 42.195))} en maratón, a {D.t(_pred(7200, 21.0975, 42.195) / 42.195)} min/km."),
    ("¿Por qué el exponente es 1,06?",
     "Es el valor con el que Riegel ajustó los récords del mundo de carrera a pie: al doblar la distancia el tiempo se multiplica por 2^1,06 ≈ 2,085."),
    ("¿Sirve para ciclismo o natación?",
     "Riegel publicó exponentes distintos para otros deportes, pero esta calculadora usa el de carrera a pie. Puedes cambiarlo en «Más opciones»."),
    ("¿Qué carrera es mejor para predecir el maratón?",
     "Una media maratón corrida a tope en las últimas 4 a 8 semanas. Un 10 km también sirve; un 5 km da predicciones demasiado optimistas."),
]

TOOL = {
    "slug": "prediccion-maraton",
    "lang": "es",
    "twin": "race-time-predictor",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "stopwatch",
    "order": 50,
    "name": "Predicción de maratón",
    "k": "riegel predicción tiempo maratón media 10k 5k estimar marca calculadora",
    "title": "Predicción de tiempo en maratón: fórmula de Riegel",
    "desc": "Calcula qué tiempo harás en maratón, media, 10 km o 5 km a partir de una carrera reciente con la fórmula de Riegel. Con ritmo por km.",
    "h1": "Predicción de tiempo en maratón",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Riegel, P. S. (1981). Athletic Records and Human Endurance. American Scientist 69(3): 285-290", RIEGEL_URL)],
    "credits": [("Fórmula de Riegel (Peter S. Riegel, Runner's World 1977; American Scientist 1981)", "fórmula publicada (reimplementada)", RIEGEL_URL)],
    "related": ["ritmo-carrera", "zonas-frecuencia-cardiaca"],
    "tests": [
        ({}, {"n.marathon": 13800.6, "n.half": 6619.2}),
        ({"dist": "21.0975", "tiempo": "1:45:00"}, {"n.marathon": 13135.1, "big": "3:38:55"}),
        ({"dist": "5", "tiempo": "25:00"}, {"n.ten": 3127.4}),
        ({"tiempo": "3:00"}, {"err": "Riegel solo vale para carreras de unos 3,5 minutos o más: usa una carrera más larga."}),
        ({"tiempo": "20:00"}, {"err": "Más rápido que el récord del mundo: revisa el tiempo."}),
        ({"exp": "1.5"}, {"err": "El exponente debe estar entre 1,00 y 1,20."}),
    ],
}
