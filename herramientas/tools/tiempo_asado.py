"""Tiempo de asado: roasting time by weight (USDA FSIS timetables for turkey, chicken, lamb, pork, beef and ham;
traditional Segovian recipes for cochinillo), safe internal temperature, rest, and what time to put it in the oven.
English twin: roasting_time_calculator.py."""
from herramientas.tools._cocina import CAT, js

FS_CHART = "https://www.foodsafety.gov/food-safety-charts/meat-poultry-charts"
FS_TEMP = "https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures"
FSIS_TURKEY = "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/poultry/lets-talk-turkey-roasting"
COCHI = "https://www.hola.com/cocina/recetas/20200522168524/cochinillo-asado-candido/"

# t: 'tab' = rows [lb from, lb to, hours from, hours to]; 'lb' = rows [lb from, lb to, min/lb from, min/lb to];
# 'kg' = same per kg. oven/inside in °C and °F; rest = minutes used for the start time.
MEATS = [
    {"id": "pavo", "t": "tab", "rows": [[8, 12, 2.75, 3], [12, 14, 3, 3.75], [14, 18, 3.75, 4.25], [18, 20, 4.25, 4.5], [20, 24, 4.5, 5]],
     "oc": 163, "of": 325, "ic": 74, "if": 165, "rest": 20, "thaw": 1},
    {"id": "pavor", "t": "tab", "rows": [[8, 12, 3, 3.5], [12, 14, 3.5, 4], [14, 18, 4, 4.25], [18, 20, 4.25, 4.75], [20, 24, 4.75, 5.25]],
     "oc": 163, "of": 325, "ic": 74, "if": 165, "rest": 20, "thaw": 1, "stuff": 1},
    {"id": "pollo", "t": "tab", "rows": [[3, 4, 1.25, 1.5], [5, 7, 2, 2.25]], "oc": 177, "of": 350, "ic": 74, "if": 165, "rest": 10},
    {"id": "cordero", "t": "lb", "rows": [[5, 7, 20, 25], [7, 9, 15, 20]], "oc": 163, "of": 325, "ic": 63, "if": 145, "rest": 15},
    {"id": "corderod", "t": "lb", "rows": [[4, 7, 25, 30]], "oc": 163, "of": 325, "ic": 63, "if": 145, "rest": 15},
    {"id": "lomo", "t": "lb", "rows": [[2, 5, 20, 30]], "oc": 163, "of": 325, "ic": 63, "if": 145, "rest": 15},
    {"id": "rib", "t": "lb", "rows": [[4, 6, 23, 25]], "oc": 163, "of": 325, "ic": 63, "if": 145, "rest": 15},
    {"id": "redondo", "t": "lb", "rows": [[2.5, 4, 30, 35]], "oc": 163, "of": 325, "ic": 63, "if": 145, "rest": 15},
    {"id": "jamon", "t": "lb", "rows": [[10, 14, 15, 18]], "oc": 163, "of": 325, "ic": 60, "if": 140, "rest": 10, "cooked": 1},
    {"id": "cochinillo", "t": "kg", "rows": [[3.5, 5.5, 25, 30]], "oc": 180, "of": 356, "ic": 63, "if": 145, "rest": 10, "trad": 1},
]

BODY = r"""
  var M = D.m.filter(function (x) { return x.id === v.carne; })[0] || D.m[0];
  var kg = ok(v.peso) ? v.peso * (v.pu === 'lb' ? 0.453592 : 1) : NaN;
  if (!ok(kg) || kg <= 0) return { err: T.e_peso };
  if (kg > 40) return { err: T.e_big };
  var lb = kg / 0.453592, rows = M.rows, lo, hi, est, out = 0;
  var w = M.t === 'kg' ? kg : lb, first = rows[0], last = rows[rows.length - 1];
  if (M.t === 'tab') {
    var at = function (r, x) { return r[2] + (x - r[0]) / (r[1] - r[0]) * (r[3] - r[2]); };
    var row = rows.filter(function (r) { return w >= r[0] && w <= r[1]; })[0];
    if (row) { lo = row[2]; hi = row[3]; est = at(row, w); }
    else if (w < first[0]) { lo = hi = est = first[2]; out = -1; }
    else if (w > last[1]) { est = at(last, w); lo = est - (last[3] - last[2]) / 2; hi = est + (last[3] - last[2]) / 2; out = 1; }
    else {
      for (var i = 0; i < rows.length - 1; i++) if (w > rows[i][1] && w < rows[i + 1][0]) {
        var a = rows[i], b = rows[i + 1], f = (w - a[1]) / (b[0] - a[1]);
        lo = a[3]; hi = b[2]; est = a[3] + f * (b[2] - a[3]);
      }
    }
    lo *= 60; hi *= 60; est *= 60;
  } else {
    var r = rows.filter(function (x) { return w >= x[0] && w <= x[1]; })[0];
    if (!r) { r = w < first[0] ? first : last; out = w < first[0] ? -1 : 1; }
    lo = w * r[2]; hi = w * r[3]; est = (lo + hi) / 2;
  }
  var deg = EN && v.pu === 'lb' ? 'f' : 'c', oven = deg === 'f' ? M.of + ' °F' : M.oc + ' °C', ins = deg === 'f' ? M.if + ' °F' : M.ic + ' °C';
  var alt = deg === 'f' ? ' (' + M.oc + ' °C)' : ' (' + M.of + ' °F)';
  var res = [[T.oven, oven + alt], [T.range, hm(lo) + ' – ' + hm(hi)], [T.inside, ins + ' · ' + (M.cooked ? T.reheat : T.where[M.id === 'pavo' || M.id === 'pavor' || M.id === 'pollo' ? 'p' : 'm'])]];
  if (M.stuff) res.push([T.stuffing, (deg === 'f' ? '165 °F' : '74 °C') + ' ' + T.center]);
  res.push([T.rest, M.rest + ' min' + (M.ic === 63 ? ' · ' + T.min3 : '')]);
  if (M.thaw) res.push([T.thaw, nz(Math.ceil(lb / 4 * 2) / 2, 1) + ' ' + T.days, 'sub']);
  var start = '';
  if (/^\d\d:\d\d$/.test(v.hora || '')) {
    var p = v.hora.split(':'), t = +p[0] * 60 + +p[1] - est - M.rest;
    var clock = function (m) { m = ((Math.round(m) % 1440) + 1440) % 1440; return (m < 600 ? '0' : '') + Math.floor(m / 60) + ':' + (m % 60 < 10 ? '0' : '') + (m % 60); };
    var show = function (s) {
      if (!EN) return s;
      var h = +s.slice(0, 2), ap = h < 12 ? ' am' : ' pm';
      return ((h % 12) || 12) + s.slice(2) + ap;
    };
    start = clock(t);
    res.push([T.start.replace('{h}', show(v.hora)), show(start), 'tot']);
    res.push([T.check, show(clock(+p[0] * 60 + +p[1] - est - M.rest + lo - 30)), 'sub']);
  }
  var notes = [];
  if (out) notes.push(out > 0 ? T.large : (M.t === 'tab' ? T.small : T.small_r.replace('{a}', first[0] + (M.t === 'kg' ? ' kg' : ' lb'))));
  if (M.trad) notes.push(T.trad);
  notes.push(T.therm);
  var wtxt = deg === 'f' ? nz(lb, 1) + ' lb' : nz(kg, 2) + ' kg';
  return {
    label: T.names[M.id] + ' · ' + wtxt, big: '≈ ' + hm(est), sub: T.sub.replace('{o}', oven), rows: res,
    note: notes.join(' '), print: true,
    n: { est: Math.round(est), lo: Math.round(lo), hi: Math.round(hi), start: start }
  };
"""
JS = js(BODY)

NAMES_ES = {"pavo": "Pavo sin relleno", "pavor": "Pavo relleno", "pollo": "Pollo entero", "cordero": "Pierna de cordero con hueso",
            "corderod": "Pierna de cordero deshuesada", "lomo": "Lomo de cerdo", "rib": "Costillar de vaca (rosbif con hueso)",
            "redondo": "Redondo o tapa de vaca", "jamon": "Jamón cocido entero (glaseado)", "cochinillo": "Cochinillo entero"}
NAMES_EN = {"pavo": "Turkey, unstuffed", "pavor": "Turkey, stuffed", "pollo": "Whole chicken", "cordero": "Leg of lamb, bone-in",
            "corderod": "Leg of lamb, boneless rolled", "lomo": "Pork loin roast", "rib": "Prime rib (standing rib roast)",
            "redondo": "Beef round or rump roast", "jamon": "Fully cooked ham, bone-in", "cochinillo": "Suckling pig (cochinillo)"}

T_ES = {
    "e_peso": "Escribe el peso de la pieza.", "e_big": "Más de 40 kg: revisa el peso.", "names": NAMES_ES,
    "oven": "Horno", "range": "Tiempo según la tabla", "inside": "Temperatura interior", "reheat": "jamón ya cocido, solo calentar",
    "where": {"p": "en el muslo, el ala y la parte más gruesa de la pechuga", "m": "en el centro de la pieza, sin tocar el hueso"},
    "stuffing": "Relleno", "center": "en el centro", "rest": "Reposo antes de trinchar", "min3": "mínimo 3 min (USDA)",
    "thaw": "Descongelar en la nevera", "days": "días", "start": "Al horno para comer a las {h}", "check": "Empieza a medir la temperatura",
    "small": "Pieza más pequeña que la tabla: el tiempo mostrado es el mínimo de la tabla, mide antes.",
    "small_r": "La tabla empieza en {a}; para piezas menores se aplican los mismos minutos por libra.",
    "large": "Pieza más grande que la tabla: estimación extrapolada, mide la temperatura.",
    "trad": "Cochinillo: tiempo de las recetas tradicionales segovianas, no de una tabla oficial.",
    "therm": "El tiempo orienta; la temperatura interior manda.", "sub": "Horno convencional a {o}",
}
T_EN = {
    "e_peso": "Enter the weight.", "e_big": "Over 40 kg (88 lb): check the weight.", "names": NAMES_EN,
    "oven": "Oven", "range": "Time from the chart", "inside": "Safe internal temperature", "reheat": "fully cooked, reheat only",
    "where": {"p": "in the thigh, wing and thickest part of the breast", "m": "in the center, not touching bone"},
    "stuffing": "Stuffing", "center": "in the center", "rest": "Rest before carving", "min3": "at least 3 min (USDA)",
    "thaw": "Thaw in the fridge", "days": "days", "start": "Into the oven to eat at {h}", "check": "Start checking the temperature",
    "small": "Smaller than the chart covers: the time shown is the chart's minimum, so check early.",
    "small_r": "The chart starts at {a}; smaller roasts use the same minutes per pound.",
    "large": "Larger than the chart covers: extrapolated estimate, rely on the thermometer.",
    "trad": "Suckling pig: time from traditional Segovian recipes, not an official chart.",
    "therm": "Time is a guide; internal temperature decides.", "sub": "Conventional oven at {o}",
}


def inputs(lang):
    es = lang == "es"
    names = NAMES_ES if es else NAMES_EN
    order = (["pavo", "pavor", "pollo", "cordero", "corderod", "lomo", "cochinillo", "rib", "redondo", "jamon"] if es else
             ["pavo", "pavor", "pollo", "rib", "redondo", "jamon", "lomo", "cordero", "corderod", "cochinillo"])
    out = [
        {"id": "carne", "type": "select", "label": "Pieza" if es else "Roast", "value": "pavo" if not es else "cordero",
         "options": [(k, names[k]) for k in order], "w": "l"},
        {"id": "peso", "type": "number", "label": "Peso" if es else "Weight", "value": 2 if es else 14, "unit": "kg" if es else "", "step": "0.1", "w": "s"},
        {"id": "hora", "type": "time", "label": "Comer a las" if es else "Eat at", "value": "14:30" if es else "16:00"},
    ]
    if not es:
        out.insert(2, {"id": "pu", "type": "select", "label": "Unit", "value": "lb", "w": "s", "options": [("lb", "lb"), ("kg", "kg")]})
    return out


TESTS = [
    ({}, {"n.lo": 88, "n.hi": 110, "n.est": 99}),
    ({"carne": "pavo", "peso": "6"}, {"n.lo": 180, "n.hi": 225, "n.est": 208}),
    ({"carne": "cochinillo", "peso": "4", "hora": "14:30"}, {"n.est": 110, "n.start": "12:30"}),
    ({"carne": "pollo", "peso": "1,6"}, {"n.est": 83}),
    ({"peso": "0"}, {"err": T_ES["e_peso"]}),
]

FAQ = [
    ("¿Cuánto tiempo se asa un pavo por kilo?",
     "A 163 °C, un pavo sin relleno de 5,5-6,3 kg necesita unas 3 h a 3 h 45 min, y uno de 9-11 kg entre 4 h 30 y 5 h, según la tabla "
     "del Departamento de Agricultura de EE. UU. Relleno tarda hasta media hora más. El tiempo por kilo baja cuanto más grande es "
     "el pavo, por eso la calculadora usa la tabla y no una regla fija."),
    ("¿A qué temperatura interior está hecho el pollo o el pavo?",
     "A 74 °C medidos en la parte más gruesa del muslo, el ala y la pechuga, sin tocar el hueso. Si está relleno, el centro del relleno "
     "también tiene que llegar a 74 °C."),
    ("¿Y el cordero, el cerdo o el rosbif?",
     "Para piezas enteras (no picadas), el USDA fija 63 °C en el centro y un reposo de al menos 3 minutos. Es el mínimo seguro: muchas "
     "recetas de cordero lechal o cochinillo lo pasan con creces por textura."),
    ("¿Cuánto tarda en descongelarse un pavo?",
     "En la nevera, un día por cada 2 kg (4 o 5 libras). Un pavo de 6 kg necesita unos 3 días y medio. No lo descongeles a temperatura "
     "ambiente."),
    ("¿Y si mi horno tiene ventilador?",
     "Las tablas son para horno convencional (arriba y abajo). Con aire, muchos fabricantes recomiendan bajar unos 10-20 °C o vigilar "
     "antes, porque cocina más deprisa. En cualquier caso, mide con termómetro."),
    ("¿Cuánto tiempo necesita un cochinillo?",
     "Las recetas segovianas clásicas asan un cochinillo de 4 a 4,5 kg a unos 180 °C durante 1 h 45 a 2 h, empezando con la piel hacia "
     "abajo y dándole la vuelta a mitad, con un poco de agua en la fuente. La calculadora usa 25-30 minutos por kilo."),
]


def blocks_es(ctx):
    return [
        ("Cómo se calcula", """
<p>Elige la pieza y su peso; la calculadora usa las tablas de asado del Servicio de Inspección y Seguridad Alimentaria del USDA
(FSIS) para horno convencional. El pavo y el pollo tienen tablas por tramos de peso: un pavo de 6 kg (13,2 libras) cae en el tramo
de 12-14 libras, que pide <b>3 h a 3 h 45 min a 163 °C</b>; la calculadora interpola dentro del tramo y te da unas 3 h 28 min.
El cordero, el cerdo y la vaca se calculan por minutos por libra: una pierna de cordero con hueso de 2 kg (4,4 libras) a 20-25
min/libra son <b>1 h 28 a 1 h 50</b>.</p>
<p>Si escribes la hora de comer, te dice cuándo meterla en el horno contando el reposo, y a qué hora empezar a pinchar con el
termómetro. Para comer a las 14:30 un cochinillo de 4 kg (unos 110 minutos más 10 de reposo), al horno a las 12:30.</p>"""),
        ("Temperaturas seguras", """
<p>El tiempo es solo una guía: cada horno calienta distinto y la forma de la pieza cambia mucho la cocción. Lo que garantiza la
seguridad es la temperatura en el centro, medida con un termómetro de cocina:</p>
<ul>
<li><b>Pavo, pollo y otras aves</b>: 74 °C en el muslo, el ala y la parte más gruesa de la pechuga; el relleno, también 74 °C.</li>
<li><b>Cordero, cerdo, ternera y vaca en piezas enteras</b>: 63 °C y al menos 3 minutos de reposo.</li>
<li><b>Carne picada</b> (hamburguesas, albóndigas): 71 °C. No uses estas tablas para picada.</li>
<li><b>Jamón ya cocido</b> que solo se calienta: 60 °C.</li>
</ul>
<p>El USDA recomienda dejar reposar el pavo 20 minutos antes de sacar el relleno y trinchar. Para las piezas de cordero, cerdo y
vaca, un reposo de 10 a 15 minutos ayuda además a que los jugos no se pierdan al cortar.</p>"""),
        ("Ejemplos", """
<ul>
<li><b>Pavo relleno de 7 kg</b> (15,4 libras): tabla de 14-18 libras, 4 h a 4 h 15 min a 163 °C. Descongélalo en la nevera durante
4 días.</li>
<li><b>Pollo de 1,6 kg</b> (3,5 libras): tramo de 3-4 libras, 1 h 15 a 1 h 30 a 177 °C; unos 83 minutos.</li>
<li><b>Lomo de cerdo de 1,5 kg</b> (3,3 libras): 20-30 min/libra, 1 h 06 a 1 h 39 a 163 °C, hasta 63 °C dentro.</li>
</ul>"""),
    ]


TOOL = {
    "slug": "tiempo-asado",
    "lang": "es",
    "twin": "roasting-time-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "meat",
    "order": 50,
    "name": "Tiempo de asado",
    "k": "pavo cordero cochinillo pollo horno minutos por kilo temperatura interior navidad",
    "title": "Tiempo de asado al horno: pavo, cordero y cochinillo",
    "desc": "Cuánto tiempo asar un pavo, pierna de cordero, cochinillo o pollo según su peso, a qué temperatura y a qué hora meterlo en el horno.",
    "h1": "Calculadora de tiempo de asado",
    "crumb": "Tiempo de asado",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES, "m": MEATS},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("USDA FSIS · Let's Talk Turkey: tabla de asado", FSIS_TURKEY), ("FoodSafety.gov · Tablas de asado de carne y aves", FS_CHART),
                ("FoodSafety.gov · Temperaturas internas mínimas", FS_TEMP), ("Cochinillo asado estilo Cándido (receta)", COCHI)],
    "related": ["temperatura-horno", "cantidades-fiesta", "salmuera", "escalar-receta"],
    "tests": TESTS,
}
