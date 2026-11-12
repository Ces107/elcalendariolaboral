"""Desarrollo de bicicleta: metres per crank turn for every chainring x cog, speed at a cadence, gear inches and ratio.
Wheel rollout from the ETRTO size (pi x (bead seat diameter + 2 x tyre width)) or measured. EN twin: bike-gear-calculator."""
import math

from herramientas.tools import _deporte as D

ETRTO = "https://www.etrto.org/"
SHELDON = "https://www.sheldonbrown.com/gears/"

# (ETRTO width, bead seat diameter, label)
WHEELS = [
    (23, 622, "700×23c"), (25, 622, "700×25c"), (28, 622, "700×28c"), (32, 622, "700×32c"), (40, 622, "700×40c (gravel)"),
    (45, 622, "700×45c"), (47, 584, "650b×47"), (55, 622, "29×2,2"), (60, 622, "29×2,35"), (57, 584, "27,5×2,25"),
    (54, 559, "26×2,1"), (47, 406, "20×1,75"),
]
CASSETTES = [
    ("11-28", "11,12,13,14,15,17,19,21,23,25,28"), ("11-30", "11,12,13,14,15,17,19,21,24,27,30"),
    ("11-32", "11,12,13,14,16,18,20,22,25,28,32"), ("11-34", "11,13,15,17,19,21,23,25,27,30,34"),
    ("10-33", "10,11,12,13,14,15,17,19,21,24,27,30,33"), ("10-51", "10,12,14,16,18,21,24,28,33,39,45,51"),
    ("10-52", "10,12,14,16,18,21,24,28,32,36,42,52"),
]
RINGS = [("53/39", "53,39"), ("52/36", "52,36"), ("50/34", "50,34"), ("48/35", "48,35"), ("46/30", "46,30"),
         ("40", "40"), ("36", "36"), ("32", "32")]


def rollout(w, bsd):
    return round(math.pi * (bsd + 2 * w))


JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var T = EN ? {
    rings: 'Enter the chainring teeth, e.g. 50, 34.', cogs: 'Enter the teeth of every cog, e.g. 11, 12, 13…', teeth: 'Teeth must be between 8 and 80.',
    circ: 'Wheel circumference should be between 1,000 and 2,500 mm.', cad: 'Cadence should be between 30 and 150 rpm.', many: 'Up to 3 chainrings and 14 cogs.',
    lab: 'Development', m: 'm', kmh: 'km/h', inch: 'in', ratio: '', range: 'at', rpm: 'rpm', cog: 'Cog', hi: 'Top gear', lo: 'Lowest gear',
    view: { m: 'metres per pedal turn', v: 'km/h at {c} rpm', mph: 'mph at {c} rpm', in: 'gear inches', r: 'gear ratio' }, wheel: 'wheel'
  } : {
    rings: 'Escribe los dientes de los platos, por ejemplo 50, 34.', cogs: 'Escribe los dientes de los piñones, por ejemplo 11, 12, 13… (todos los del casete).', teeth: 'Los dientes deben estar entre 8 y 80.',
    circ: 'La circunferencia de la rueda debe estar entre 1.000 y 2.500 mm.', cad: 'La cadencia debe estar entre 30 y 150 rpm.', many: 'Como mucho 3 platos y 14 piñones.',
    lab: 'Desarrollo', m: 'm', kmh: 'km/h', inch: 'pulg.', ratio: '', range: 'a', rpm: 'rpm', cog: 'Piñón', hi: 'Marcha más larga', lo: 'Marcha más corta',
    view: { m: 'metros por pedalada', v: 'km/h a {c} rpm', mph: 'mph a {c} rpm', in: 'pulgadas de desarrollo', r: 'relación' }, wheel: 'rueda'
  };
  function list(s) {
    var out = [], parts = String(s).split(/[,;\s\/]+/).filter(Boolean);
    for (var i = 0; i < parts.length; i++) if (!/^\d+$/.test(parts[i])) return null; else out.push(+parts[i]);
    return out;
  }
  var R = list(v.platos), G = list(v.pinones);
  if (!R || !R.length) return { err: T.rings };
  if (!G || !G.length) return { err: T.cogs };
  if (R.length > 3 || G.length > 14) return { err: T.many };
  if (R.concat(G).some(function (x) { return x < 8 || x > 80; })) return { err: T.teeth };
  if (!(v.circ >= 1000 && v.circ <= 2500)) return { err: T.circ };
  var cad = isNaN(v.cad) ? 90 : v.cad;
  if (!(cad >= 30 && cad <= 150)) return { err: T.cad };
  R.sort(function (a, b) { return b - a; }); G.sort(function (a, b) { return a - b; });
  var circ = v.circ / 1000, dia = v.circ / Math.PI / 25.4, w = v.ver || 'm';
  function val(rg, cg) { var q = rg / cg; return w === 'v' ? q * circ * cad * 0.06 : w === 'mph' ? q * circ * cad * 0.06 / 1.609344 : w === 'in' ? q * dia : w === 'r' ? q : q * circ; }
  function spd(d) { return fx(d * cad * 0.06, 1) + ' km/h' + (EN ? ' (' + fx(d * cad * 0.06 / 1.609344, 1) + ' mph)' : ''); }
  function show(x) { return fx(x, w === 'in' ? 1 : 2); }
  var all = [];
  R.forEach(function (rg) { G.forEach(function (cg) { all.push(val(rg, cg)); }); });
  var mx = Math.max.apply(null, all), mn = Math.min.apply(null, all);
  var head = '<tr><th>' + T.cog + '</th>' + R.map(function (rg) { return '<th class="num">' + rg + '</th>'; }).join('') + '</tr>', body = '';
  G.forEach(function (cg) {
    body += '<tr><th scope="row">' + cg + '</th>' + R.map(function (rg) {
      var x = val(rg, cg), t = mx > mn ? (x - mn) / (mx - mn) : 0;
      return '<td class="num" style="background:rgba(59,130,196,' + (0.08 + t * 0.42).toFixed(2) + ')">' + show(x) + '</td>';
    }).join('') + '</tr>';
  });
  var dmax = R[0] / G[0] * circ, dmin = R[R.length - 1] / G[G.length - 1] * circ;
  return {
    label: T.lab + ' · ' + R.join('/') + ' × ' + G[0] + '-' + G[G.length - 1], big: fx(dmin, 2) + ' – ' + fx(dmax, 2) + ' m',
    sub: fx(dmin * cad * 0.06, 1) + ' – ' + fx(dmax * cad * 0.06, 1) + ' km/h' + (EN ? ' (' + fx(dmin * cad * 0.06 / 1.609344, 1) + ' – ' + fx(dmax * cad * 0.06 / 1.609344, 1) + ' mph)' : '') + ' ' + T.range + ' ' + fv(cad, 0) + ' ' + T.rpm + ' · ' + fv(v.circ, 0) + ' mm ' + T.wheel,
    html: '<p class="bd-v">' + T.view[w].replace('{c}', fv(cad, 0)) + '</p><div class="bd-w"><table class="tbl bd-t"><thead>' + head + '</thead><tbody>' + body + '</tbody></table></div>',
    rows: [[T.hi + ' · ' + R[0] + '×' + G[0], fx(dmax, 2) + ' m · ' + spd(dmax)], [T.lo + ' · ' + R[R.length - 1] + '×' + G[G.length - 1], fx(dmin, 2) + ' m · ' + spd(dmin)]],
    print: true,
    n: { max: r(dmax, 3), min: r(dmin, 3), top: r(mx, 3), cells: all.length }
  };
}
"""

CSS = ".bd-v{margin:.8rem 0 .2rem;font-size:.9rem;color:var(--mut,#666)}.bd-w{overflow-x:auto}.bd-t td,.bd-t th{padding:.3rem .5rem}.bd-t{width:auto;min-width:12rem}"


def inputs(lang):
    es = lang == "es"
    views = [("m", "m"), ("v", "km/h"), ("in", "pulg."), ("r", "relación")] if es else [("in", "inches"), ("m", "m"), ("v", "km/h"), ("mph", "mph"), ("r", "ratio")]
    lab = (lambda s: s) if es else (lambda s: s.replace(",", "."))
    return [
        {"id": "platos", "type": "text", "label": "Platos" if es else "Chainrings", "value": "50, 34", "w": "s"},
        {"id": "cas", "type": "select", "label": "Casete" if es else "Cassette", "value": "11-30", "custom": "otro",
         "options": [(k, k, {"pinones": s}) for k, s in CASSETTES] + [("otro", "Otro" if es else "Other")]},
        {"id": "pinones", "type": "text", "label": "Piñones" if es else "Cogs", "value": "11,12,13,14,15,17,19,21,24,27,30", "w": "l"},
        {"id": "rueda", "type": "select", "label": "Rueda" if es else "Wheel", "value": "25-622", "custom": "otra",
         "options": [(f"{w}-{b}", f"{lab(l)} · {w}-{b}", {"circ": str(rollout(w, b))}) for w, b, l in WHEELS] + [("otra", "Medida a mano" if es else "Measured")]},
        {"id": "circ", "type": "number", "label": "Circunferencia" if es else "Circumference", "value": str(rollout(25, 622)), "unit": "mm", "w": "s"},
        {"id": "cad", "type": "number", "label": "Cadencia" if es else "Cadence", "value": "90", "unit": "rpm", "w": "s"},
        {"id": "ver", "type": "seg", "label": "Tabla" if es else "Show", "value": "m" if es else "in", "options": views},
    ]


def blocks(ctx):
    c = rollout(25, 622) / 1000
    hi, lo = 50 / 11 * c, 34 / 30 * c
    mtb = rollout(60, 622) / 1000
    m_lo = 32 / 51 * mtb
    n = D.n
    return [
        ("Qué es el desarrollo", f"""
<p>El desarrollo es la distancia que avanza la bici con una vuelta completa de los pedales: <b>desarrollo = (dientes
del plato ÷ dientes del piñón) × circunferencia de la rueda</b>. Con un 50 delante, un 11 detrás y una rueda de 700×25c
(unos {rollout(25, 622)} mm de circunferencia), cada pedalada te lleva {n(50 / 11, 2)} × {n(c, 3)} = <b>{n(hi, 2)} m</b>. Con la
marcha más corta de un compacto, 34×30, son {n(lo, 2)} m. Multiplicando por la cadencia sale la velocidad: a 90 pedaladas por
minuto, {n(hi * 90 * 0.06, 1)} km/h con el 50×11 y {n(lo * 90 * 0.06, 1)} km/h con el 34×30.</p>
<p>La tabla muestra el desarrollo de cada combinación de plato y piñón, coloreada de más corta a más larga, y puede
cambiarse a velocidad a tu cadencia, pulgadas de desarrollo (la medida anglosajona: diámetro de la rueda en pulgadas por
la relación) o relación de transmisión. Sirve para comparar casetes antes de comprar, ver si un cambio te deja huecos
grandes entre marchas o elegir los platos para una ruta con puertos.</p>"""),
        ("La circunferencia de la rueda", f"""
<p>La rueda se elige por su medida ETRTO, la que viene grabada en el flanco del neumático: 25-622 significa 25 mm de ancho
sobre una llanta de 622 mm de diámetro de asiento (la 700c de carretera). La circunferencia se estima como π × (622 + 2 × 25)
= {rollout(25, 622)} mm. Para más precisión, mídela: marca el neumático y el suelo, empuja la bici una vuelta con tu peso
encima y mide la distancia; escríbela en «Circunferencia». Un neumático de MTB 29×2,35 da unos {rollout(60, 622)} mm, y con un
plato de 32 y un piñón de 51 el desarrollo baja a {n(m_lo, 2)} m, ideal para rampas muy duras.</p>"""),
        ("Cómo elegir desarrollos", """
<p>Para subir puertos largos sin forzar las rodillas, la referencia habitual es poder mantener 70-80 rpm en la marcha
más corta: si subes a 10 km/h, necesitas un desarrollo de unos 2,1 a 2,4 m. En llano, la mayoría de ciclistas aficionados
va a 30-35 km/h en marchas de 6 a 7 m. Saltos de más del 15 % entre piñones consecutivos se notan como un «hueco» al cambiar;
los casetes de dientes muy juntos (11-28) dan saltos pequeños a cambio de menos rango.</p>"""),
    ]


FAQ = [
    ("¿Cuántos metros avanza un 50×11?",
     f"Con una rueda 700×25c, unos {D.n(50 / 11 * rollout(25, 622) / 1000, 2)} m por pedalada. Con 700×28c algo más, porque la rueda es mayor."),
    ("¿Qué desarrollo necesito para subir un puerto?",
     "Lo bastante corto para pedalear a 70-80 rpm. Para subir a 8-10 km/h eso son unos 1,7 a 2,4 m: un 34×30 (2,4 m) o un 34×34 (2,1 m) en carretera."),
    ("¿Cómo calculo la velocidad con la cadencia?",
     "Velocidad (km/h) = desarrollo (m) × cadencia (rpm) × 0,06. Con 7 m a 90 rpm: 7 × 90 × 0,06 = 37,8 km/h."),
    ("¿Qué son las pulgadas de desarrollo?",
     "La medida anglosajona clásica: diámetro de la rueda en pulgadas multiplicado por la relación plato ÷ piñón. Multiplicada por π da las pulgadas que avanzas por pedalada."),
    ("¿Cómo mido la circunferencia de mi rueda?",
     "Marca el neumático y el suelo, empuja la bici una vuelta completa sentado encima y mide la distancia en milímetros."),
]

TOOL = {
    "slug": "desarrollo-bicicleta",
    "lang": "es",
    "twin": "bike-gear-calculator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "bike",
    "order": 90,
    "name": "Desarrollo de bicicleta",
    "k": "desarrollo bicicleta platos piñones casete relación cadencia velocidad metros pedalada ciclismo",
    "title": "Calculadora de desarrollo de bicicleta: platos y piñones",
    "desc": "Calcula el desarrollo de tu bici: metros por pedalada y velocidad según la cadencia para cada plato y piñón. Carretera, gravel y MTB.",
    "h1": "Calculadora de desarrollo de bicicleta",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ETRTO · designación de neumáticos y llantas (ISO 5775)", ETRTO),
                ("Sheldon Brown · Gear theory for bicyclists (referencia)", SHELDON)],
    "credits": [("Circunferencia aproximada π × (BSD + 2 × ancho), medidas ETRTO / ISO 5775", "norma de medidas (fórmula)", ETRTO)],
    "related": ["ritmo-carrera", "zonas-frecuencia-cardiaca"],
    "tests": [
        ({}, {"n.max": 9.595, "n.min": 2.392, "n.cells": 22}),
        ({"ver": "v"}, {"n.top": 51.811}),
        ({"platos": "32", "pinones": "10,12,14,16,18,21,24,28,33,39,45,51", "circ": "2331"}, {"n.min": 1.463, "n.cells": 12}),
        ({"platos": "50, 34", "pinones": "11 a 30"}, {"err": "Escribe los dientes de los piñones, por ejemplo 11, 12, 13… (todos los del casete)."}),
        ({"circ": "500"}, {"err": "La circunferencia de la rueda debe estar entre 1.000 y 2.500 mm."}),
        ({"platos": "90"}, {"err": "Los dientes deben estar entre 8 y 80."}),
    ],
}
