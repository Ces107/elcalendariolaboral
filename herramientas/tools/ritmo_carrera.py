"""Ritmo de carrera: time <-> pace (min/km, min/mi) <-> speed (km/h, mph), splits table and the same pace over the usual
race distances. EN twin: running-pace-calculator."""
from herramientas.tools import _deporte as D

MI = 1.609344

JS = r"""
function (v, H, C) {
  var EN = %EN%, MI = 1.609344;
  %FMT%
  %TIME%
  var T = EN ? {
    dist: 'Enter the distance.', time: 'Enter the time as h:mm:ss (or mm:ss).', pace: 'Enter the pace as m:ss.', speed: 'Enter the speed.',
    slow: 'That is slower than walking: check the time and the distance.', pace_l: 'Pace', time_l: 'Finish time', at: 'at', split: 'Split', cum: 'Time',
    races: 'Same pace over', dist_l: 'Distance', tt: 'Time', R: [['5K', 5], ['10K', 10], ['Half marathon', 21.0975], ['Marathon', 42.195]],
    perkm: 'per km', permi: 'per mile', kmh: 'Speed', mph: 'Speed'
  } : {
    dist: 'Indica la distancia.', time: 'Escribe el tiempo como h:mm:ss (o mm:ss).', pace: 'Escribe el ritmo como m:ss.', speed: 'Indica la velocidad.',
    slow: 'Eso es más lento que andar: revisa el tiempo y la distancia.', pace_l: 'Ritmo', time_l: 'Tiempo final', at: 'a', split: 'Parcial', cum: 'Paso',
    races: 'A ese ritmo', dist_l: 'Distancia', tt: 'Tiempo', R: [['5 km', 5], ['10 km', 10], ['Media maratón', 21.0975], ['Maratón', 42.195]],
    perkm: 'por km', permi: 'por milla', kmh: 'Velocidad', mph: 'Velocidad'
  };
  var km = v.dist === 'otra' ? (v.du === 'mi' ? v.km * MI : v.km) : +v.dist;
  if (!(km > 0) || km > 1000) return { err: T.dist };
  var pace;   /* seconds per km */
  if (v.modo === 'tiempo') {
    var t = tp(v.tiempo);
    if (!(t > 0)) return { err: T.time };
    pace = t / km;
  } else if (v.modo === 'ritmo') {
    var p = tp(v.ritmo);
    if (!(p > 0)) return { err: T.pace };
    pace = v.ru === 'mi' ? p / MI : p;
  } else {
    if (!(v.vel > 0)) return { err: T.speed };
    pace = 3600 / (v.vu === 'mph' ? v.vel * MI : v.vel);
  }
  if (pace > 1800) return { err: T.slow };
  var total = pace * km, kmh = 3600 / pace;
  /* splits: every 1 km / 5 km / 1 mile; 'auto' = 1 km up to 10 km, else 5 km */
  var step = v.parc === 'auto' ? (km <= 10.5 ? 1 : 5) : v.parc === 'mi' ? MI : +v.parc, rows = '', n = 0;
  if (step > 0) {
    for (var d = step; d < km - 1e-6 && n < 60; d += step, n++) rows += '<tr><td>' + (v.parc === 'mi' ? fv(r(d / MI, 0), 0) + ' mi' : fv(r(d, 2)) + ' km') + '</td><td class="num">' + ft(pace * d) + '</td></tr>';
    rows += '<tr class="tot"><td>' + fv(r(km, 3), 3) + ' km</td><td class="num">' + ft(total) + '</td></tr>';
  }
  var races = T.R.map(function (x) { return '<tr><td>' + x[0] + '</td><td class="num">' + ft(pace * x[1]) + '</td></tr>'; }).join('');
  /* English pages lead with the mile pace, Spanish ones with the km pace */
  var big = v.modo === 'tiempo' ? (EN ? ft(pace * MI) + ' /mi' : ft(pace) + ' min/km') : ft(total);
  var sub = v.modo === 'tiempo' ? (EN ? ft(pace) + ' /km · ' + fx(kmh / MI, 2) + ' mph' : ft(pace * MI) + ' /mi · ' + fx(kmh, 1) + ' km/h') :
    fv(r(km, 3), 3) + ' km ' + T.at + ' ' + (EN ? ft(pace * MI) + ' /mi' : ft(pace) + ' /km');
  return {
    label: v.modo === 'tiempo' ? T.pace_l : T.time_l, big: big, sub: sub,
    rows: [[T.pace_l + ' ' + T.perkm, ft(pace) + ' min/km'], [T.pace_l + ' ' + T.permi, ft(pace * MI) + ' min/mi'],
           [T.kmh, fx(kmh, 2) + ' km/h'], [T.mph, fx(kmh / MI, 2) + ' mph'], [T.tt + ' · ' + fv(r(km, 3), 3) + ' km', ft(total), 'tot']],
    html: (rows ? '<h3 class="rc-h">' + T.split + '</h3><table class="tbl rc-t"><thead><tr><th>' + T.dist_l + '</th><th class="num">' + T.cum + '</th></tr></thead><tbody>' + rows + '</tbody></table>' : '') +
      '<h3 class="rc-h">' + T.races + ' ' + ft(pace) + ' /km</h3><table class="tbl rc-t"><tbody>' + races + '</tbody></table>',
    print: true,
    n: { pace: r(pace, 3), time: r(total, 2), kmh: r(kmh, 3), splits: n + 1 }
  };
}
"""

CSS = ".rc-h{font-size:1rem;margin:1rem 0 .3rem}.rc-t{max-width:22rem}"

INPUTS_ES = [
    {"id": "modo", "type": "seg", "label": "Calcular", "value": "tiempo",
     "options": [("tiempo", "Ritmo"), ("ritmo", "Tiempo"), ("vel", "Desde km/h")]},
    {"id": "dist", "type": "select", "label": "Distancia", "value": "10",
     "options": [("5", "5 km"), ("10", "10 km"), ("21.0975", "Media maratón"), ("42.195", "Maratón"), ("otra", "Otra")]},
    {"id": "km", "type": "number", "label": "Distancia", "value": "15", "step": "0.001", "w": "s", "show": ("dist", ["otra"])},
    {"id": "du", "type": "seg", "label": "Unidad", "value": "km", "options": [("km", "km"), ("mi", "millas")], "show": ("dist", ["otra"])},
    {"id": "tiempo", "type": "text", "label": "Tiempo", "value": "50:00", "placeholder": "h:mm:ss", "w": "s", "show": ("modo", ["tiempo"])},
    {"id": "ritmo", "type": "text", "label": "Ritmo", "value": "5:00", "placeholder": "m:ss", "w": "s", "show": ("modo", ["ritmo"])},
    {"id": "ru", "type": "seg", "label": "Por", "value": "km", "options": [("km", "km"), ("mi", "milla")], "show": ("modo", ["ritmo"])},
    {"id": "vel", "type": "number", "label": "Velocidad", "value": "12", "unit": "km/h", "step": "0.1", "w": "s", "show": ("modo", ["vel"])},
    {"id": "vu", "type": "seg", "label": "Unidad", "value": "kmh", "options": [("kmh", "km/h"), ("mph", "mph")], "show": ("modo", ["vel"]), "more": True},
    {"id": "parc", "type": "select", "label": "Parciales", "value": "auto", "more": True,
     "options": [("auto", "Automático"), ("1", "Cada km"), ("5", "Cada 5 km"), ("mi", "Cada milla"), ("0", "Sin parciales")]},
]


def blocks(ctx):
    n = D.n
    return [
        ("Cómo se calcula el ritmo", f"""
<p>El ritmo es el tiempo que tardas en recorrer un kilómetro: <b>ritmo = tiempo ÷ distancia</b>. Si corres 10 km en
50 minutos, tu ritmo es 50 ÷ 10 = <b>5:00 min/km</b>. La velocidad es la inversa, 60 ÷ 5 = <b>12 km/h</b>, y el ritmo por
milla se obtiene multiplicando por 1,609: 8:03 min/mi. Escribe el tiempo como h:mm:ss (1:45:00) o mm:ss (50:00); un número
suelto se toma como minutos.</p>
<p>La herramienta también funciona al revés: elige «Tiempo», escribe el ritmo que quieres llevar y te dice a qué hora
cruzarás la meta, con la tabla de parciales para cada kilómetro o cada 5 km. Es la forma más rápida de preparar una
pulsera de ritmos para el día de la carrera o de saber qué ritmo marcar en la cinta, que suele ir en km/h.</p>"""),
        ("Ejemplos con números reales", f"""
<p>Bajar de 4 horas en maratón exige {D.t(4 * 3600 / 42.195)} min/km de media ({n(42.195 * 3600 / (4 * 3600), 2)} km/h); bajar de
3:30, {D.t(3.5 * 3600 / 42.195)} min/km. La media maratón en 2 horas sale al mismo ritmo que el maratón en 4,
{D.t(7200 / 21.0975)} min/km, porque es justo la mitad de distancia. Un 5 km en 25 minutos va a 5:00 min/km, igual que los 10 km
en 50: a ese ritmo, la media maratón saldría en {D.t(300 * 21.0975)} y el maratón en {D.t(300 * 42.195)}, aunque en la práctica
casi nadie aguanta su ritmo de 10 km durante 42 (para estimar eso está la predicción de Riegel).</p>
<p>En la cinta: 10 km/h equivalen a 6:00 min/km, 12 km/h a 5:00 y 15 km/h a 4:00. La tabla «A ese ritmo» muestra el tiempo
que darían 5 km, 10 km, la media y el maratón con el ritmo calculado.</p>"""),
        ("Distancias oficiales y redondeo", """
<p>La media maratón mide 21,0975 km y el maratón 42,195 km, las distancias que fija World Athletics para las pruebas de
ruta homologadas; la milla internacional son 1.609,344 metros. En carrera, el GPS suele marcar algo más que la distancia
oficial porque no siempre se corre por la trazada más corta: cuenta con 200 a 400 metros de más en un maratón y elige un
ritmo objetivo unos segundos más rápido que el teórico. Los ritmos se redondean al segundo y las velocidades a la centésima.</p>"""),
    ]


FAQ = [
    ("¿Qué ritmo necesito para bajar de 50 minutos en 10 km?",
     "5:00 min/km exactos dan 50:00, así que necesitas ir algo más rápido, 4:59 o menos. Son 12 km/h en la cinta."),
    ("¿A qué ritmo hay que correr un maratón en 4 horas?",
     f"A {D.t(4 * 3600 / 42.195)} min/km de media, unos 10,55 km/h. Por los metros de más del GPS, conviene apuntar a 5:35-5:38."),
    ("¿Cómo paso de km/h a min/km?",
     "Divide 60 entre la velocidad: 60 ÷ 12 km/h = 5 minutos por km. Al revés, 60 ÷ 5:00 min/km = 12 km/h. Elige «Desde km/h» para hacerlo con decimales."),
    ("¿Cómo convierto el ritmo por milla en ritmo por kilómetro?",
     "Divide entre 1,609: 8:00 min/mi son 4:58 min/km. Elige «Tiempo», pon el ritmo y cambia «Por» a milla."),
    ("¿Qué es un parcial?",
     "El tiempo de paso en cada punto de la carrera, por ejemplo en cada kilómetro. Sirve para saber si vas por delante o por detrás de tu objetivo."),
]

TOOL = {
    "slug": "ritmo-carrera",
    "lang": "es",
    "twin": "running-pace-calculator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "run",
    "order": 40,
    "name": "Ritmo de carrera",
    "k": "ritmo min/km km/h correr running parciales maratón media 10k 5k calculadora pace",
    "title": "Calculadora de ritmo de carrera: min/km, km/h y parciales",
    "desc": "Calcula tu ritmo por km o por milla a partir del tiempo y la distancia, o el tiempo final a un ritmo dado. Con parciales y tabla de 5k a maratón.",
    "h1": "Calculadora de ritmo de carrera",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("World Athletics · Competition and Technical Rules (distancias de ruta)", "https://worldathletics.org/about-iaaf/documents/book-of-rules"),
                ("NIST · milla internacional = 1.609,344 m", "https://www.nist.gov/pml/us-surveyfoot/revised-unit-conversion-factors")],
    "related": ["prediccion-maraton", "zonas-frecuencia-cardiaca", "ritmo-natacion"],
    "tests": [
        ({}, {"n.pace": 300, "n.kmh": 12, "n.splits": 10}),
        ({"modo": "ritmo", "dist": "42.195", "ritmo": "5:00"}, {"n.time": 12658.5, "big": "3:30:59"}),
        ({"dist": "21.0975", "tiempo": "1:45:00"}, {"n.pace": 298.614, "big": "4:59 min/km"}),
        ({"modo": "vel", "vel": "10"}, {"n.pace": 360}),
        ({"modo": "ritmo", "ritmo": "8:00", "ru": "mi"}, {"n.pace": 298.258}),
        ({"tiempo": "abc"}, {"err": "Escribe el tiempo como h:mm:ss (o mm:ss)."}),
    ],
}
