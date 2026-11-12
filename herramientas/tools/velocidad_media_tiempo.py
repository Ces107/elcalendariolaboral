"""Velocidad media, tiempo y distancia: solve any one from the other two, with a speed-limit check for average-speed
(section) cameras. Spanish page; the English twin is average-speed-calculator (same compute, km or miles)."""
from herramientas.tools import _coche as K

RGC = "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23514"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  %TIME%
  var mi = v.u === 'mi', du = mi ? 'mi' : 'km', su = mi ? 'mph' : 'km/h', k = mi ? 1.609344 : 1;
  var d = v.dist, s = v.vel, t = tp(v.t), c = v.calc;
  var E = EN ? { d: 'Enter the distance.', t: 'Enter the time as h:mm, for example 2:45.', s: 'Enter the speed.', neg: 'Use numbers above zero.' }
             : { d: 'Escribe la distancia.', t: 'Escribe el tiempo como h:mm, por ejemplo 2:45.', s: 'Escribe la velocidad.', neg: 'Usa números mayores que cero.' };
  if (c !== 'dist') { if (isNaN(d)) return { err: E.d }; if (d <= 0) return { err: E.neg }; }
  if (c !== 'tiempo') { if (isNaN(t)) return { err: E.t }; if (t <= 0) return { err: E.neg }; }
  if (c !== 'vel') { if (isNaN(s)) return { err: E.s }; if (s <= 0) return { err: E.neg }; }
  if (c === 'vel') s = d / (t / 3600); else if (c === 'tiempo') t = d / s * 3600; else d = s * t / 3600;
  var rows = [], lim = v.lim, out = { speed: r(s, 4), sec: r(t, 2), dist: r(d, 4) };
  rows.push([EN ? 'Distance' : 'Distancia', fv(d, 2) + ' ' + du]);
  rows.push([EN ? 'Time' : 'Tiempo', ft(t)]);
  rows.push([EN ? 'Average speed' : 'Velocidad media', fv(s, 1) + ' ' + su, c === 'vel' ? 'tot' : '']);
  rows.push([mi ? 'km/h' : 'mph', fv(mi ? s * k : s / 1.609344, 1), 'z']);
  rows.push(['m/s', fv(s * k / 3.6, 2), 'z']);
  var ps = Math.round(3600 / s), pace = ps >= 3600 ? ft(ps) : Math.floor(ps / 60) + ':' + (ps % 60 < 10 ? '0' : '') + ps % 60;
  rows.push([EN ? 'Pace per ' + du : 'Ritmo por km', pace + ' min', 'z']);
  if (!isNaN(lim) && lim > 0) {
    var tmin = d / lim * 3600;
    out.min = r(tmin, 2);
    rows.push([EN ? 'Minimum time at ' + fv(lim, 0) + ' ' + su : 'Tiempo mínimo a ' + fv(lim, 0) + ' ' + su, ft(tmin), s > lim + 1e-9 ? 'tot' : '']);
    rows.push([s > lim + 1e-9 ? (EN ? 'Over the limit by' : 'Por encima del límite') : (EN ? 'Under the limit by' : 'Por debajo del límite'), fv(Math.abs(s - lim), 1) + ' ' + su, 'z']);
  }
  var big = c === 'vel' ? fv(s, 1) + ' ' + su : c === 'tiempo' ? ft(t) : fv(d, 2) + ' ' + du;
  var label = c === 'vel' ? (EN ? 'Average speed' : 'Velocidad media') : c === 'tiempo' ? (EN ? 'Time' : 'Tiempo') : (EN ? 'Distance' : 'Distancia');
  return {
    label: label, big: big,
    sub: fv(d, 2) + ' ' + du + ' · ' + ft(t) + ' · ' + fv(s, 1) + ' ' + su,
    rows: rows, n: out
  };
}
"""


def blocks(ctx):
    return [
        ("Velocidad, tiempo y distancia", """
<p>Las tres cantidades se relacionan con una sola fórmula: <b>velocidad media = distancia ÷ tiempo</b>. Despejando,
tiempo = distancia ÷ velocidad y distancia = velocidad × tiempo. Elige qué quieres calcular, escribe las otras dos y la
calculadora da el resultado en km/h, mph y m/s, además del ritmo en minutos por kilómetro.</p>
<p>Ejemplo: de Madrid a Valencia hay unos 350 km. Si tardas 3 h 30 min puerta a puerta, tu media es 350 ÷ 3,5 =
<b>100 km/h</b>, aunque en la autovía hayas ido casi todo el rato a 120: las paradas, la salida de la ciudad y las
retenciones bajan la media. Al revés, para saber cuánto tardarás en 120 km a una media de 90 km/h: 120 ÷ 90 = 1,333 h, es decir,
<b>1 h 20 min</b>. El tiempo se escribe como horas y minutos («3:30», «3h30», «90min»); un número suelto se toma como horas.</p>"""),
        ("La trampa de las medias: ida a 60 y vuelta a 90", """
<p>Si vas a un pueblo a 60 km/h y vuelves a 90 km/h, la media del viaje no es 75 km/h sino <b>72 km/h</b>. Con 90 km de
distancia, la ida dura 1 h 30 min y la vuelta 1 h: 180 km en 2 h 30 min. Al ir más despacio pasas más tiempo a esa velocidad,
así que pesa más en la media. Para medias de varios tramos, suma todas las distancias y todos los tiempos y divide: nunca
promedies las velocidades. Por la misma razón, recuperar tiempo perdido al principio de un viaje exige ir mucho más deprisa de
lo que parece.</p>"""),
        ("Radares de tramo y límites", f"""
<p>Un radar de tramo no mide la velocidad en un punto: anota la hora a la que pasas por el inicio y por el final y calcula tu
velocidad media. Si el tramo mide 5,2 km y el límite es 100 km/h, el tiempo mínimo para no superar la media es
5,2 ÷ 100 × 3.600 = <b>187 segundos, 3 min 7 s</b>; si lo recorres en 2 min 50 s, tu media es de 110 km/h. Escribe el límite
en «Más opciones» y la calculadora te dice ese tiempo mínimo y si estás por encima o por debajo.</p>
<p>Los límites genéricos los fija el <a href="{RGC}" rel="noopener">Reglamento General de Circulación</a> (art. 48 y 50): para
turismos y motos, 120 km/h en autopistas y autovías, 90 km/h en carreteras convencionales y, en ciudad, 50, 30 o 20 km/h según
el tipo de calle. La DGT recomienda parar a descansar cada dos horas o cada 200 km.</p>"""),
    ]


FAQ = [
    ("¿Cómo se calcula la velocidad media?",
     "Dividiendo la distancia total entre el tiempo total. 240 km en 2 h 40 min (2,667 h) son 90 km/h."),
    ("¿Cuánto se tarda en recorrer 100 km a 120 km/h?",
     "50 minutos: 100 ÷ 120 = 0,833 h. A 100 km/h serían 60 minutos, solo 10 más."),
    ("¿Cómo paso de km/h a m/s?",
     "Divide entre 3,6. 90 km/h son 25 m/s, y 120 km/h, 33,3 m/s: más de 33 metros cada segundo."),
    ("¿Cómo funciona un radar de tramo?",
     "Calcula tu velocidad media entre dos puntos con la hora de paso por cada uno. Si la media supera el límite del tramo, hay "
     "denuncia aunque en algún momento fueras más despacio."),
    ("¿Cuánto tiempo ahorro yendo más rápido?",
     "Menos de lo que parece: en 300 km, pasar de 110 a 120 km/h ahorra unos 14 minutos y aumenta el consumo de forma apreciable."),
]

INPUTS_ES = [
    {"id": "calc", "type": "seg", "label": "Calcular", "value": "vel", "options": [("vel", "Velocidad"), ("tiempo", "Tiempo"), ("dist", "Distancia")]},
    {"id": "dist", "type": "number", "label": "Distancia", "value": "350", "unit": "km", "step": "0.01", "w": "s", "show": ("calc", ["vel", "tiempo"])},
    {"id": "t", "type": "text", "label": "Tiempo", "value": "3:30", "placeholder": "h:mm", "w": "s", "show": ("calc", ["vel", "dist"])},
    {"id": "vel", "type": "number", "label": "Velocidad", "value": "90", "unit": "km/h", "step": "0.1", "w": "s", "show": ("calc", ["tiempo", "dist"])},
    {"id": "lim", "type": "number", "label": "Límite", "value": "", "unit": "km/h", "w": "s", "more": True},
]

TOOL = {
    "slug": "velocidad-media-tiempo",
    "lang": "es",
    "twin": "average-speed-calculator",
    "cat": "vehiculos",
    "icon": "gauge",
    "order": 50,
    "name": "Velocidad media",
    "k": "calcular velocidad media tiempo distancia km/h cuánto tardo radar de tramo m/s",
    "title": "Calcular velocidad media, tiempo o distancia (km/h)",
    "desc": "Calcula la velocidad media de un viaje, cuánto tardarás o qué distancia recorres, y el tiempo mínimo para no superar la media de un radar de tramo.",
    "h1": "Calcular velocidad media, tiempo y distancia",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": K.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Reglamento General de Circulación, arts. 48 y 50 · límites de velocidad (BOE)", RGC)],
    "credits": [],
    "related": ["coste-viaje-coche", "horas-conduccion-tacografo", "consumo-l100km-mpg", "cambio-neumaticos-tamano"],
    "tests": [
        ({}, {"n.speed": 100}),
        ({"calc": "tiempo", "dist": "120", "vel": "90"}, {"n.sec": 4800}),
        ({"calc": "dist", "vel": "120", "t": "2h15"}, {"n.dist": 270}),
        ({"dist": "5,2", "t": "0:02:50", "lim": "100"}, {"n.speed": 110.1176, "n.min": 187.2}),
        ({"t": "90min", "dist": "120"}, {"n.speed": 80}),
        ({"t": "tres horas"}, {"err": "Escribe el tiempo como h:mm, por ejemplo 2:45."}),
    ],
}
