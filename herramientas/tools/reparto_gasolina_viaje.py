"""Reparto de gasolina por tramos: split the fuel (and tolls) of a car trip among people who ride different distances;
each stretch of road is shared equally by the people in the car on that stretch."""

GEO = "https://geoportalgasolineras.es/"

BLOCKS = [
    ("Cada uno paga los kilómetros que viaja", """
<p>Cuando no todos hacen el viaje entero, dividir la gasolina a partes iguales es injusto para el que se baja a mitad de
camino, y cobrar a cada uno «sus kilómetros × el precio por kilómetro» hace que el coche se pague varias veces. Lo justo es
repartir <b>por tramos</b>: el coste de cada tramo de carretera se divide entre las personas que van en el coche en ese tramo.
El conductor cuenta como uno más, salvo que elijas «No paga».</p>
<p>Ejemplo: cuatro amigos salen de Madrid hacia Valencia, 400 km contando el desvío hasta el apartamento. Uno se baja en
Cuenca, a 150 km. El coche gasta 6,5 l/100 km y el litro cuesta 1,55 €: 26 litros, 40,30 € en total, 0,10075 € por km. Los
primeros 150 km (15,11 €) se reparten entre cuatro: 3,78 € cada uno. Los 250 km restantes (25,19 €) entre tres: 8,40 €. El
que se baja en Cuenca paga <b>3,78 €</b> y los otros tres, <b>12,17 €</b> cada uno. La suma cuadra: 3,78 + 3 × 12,17 = 40,30 €
(con el redondeo de céntimos).</p>"""),
    ("Cómo meter los datos", f"""
<p>Escribe el recorrido total del coche (lo que marca el cuentakilómetros parcial del conductor) y, para cada pasajero, los
kilómetros que va dentro. El cálculo supone que todos salen del mismo origen y se van bajando por el camino; si alguien sube a
mitad de ruta y llega hasta el final, el resultado es el mismo por simetría. Si en tu viaje unos se bajan y otros suben a la
vez en tramos distintos, haz una cuenta por cada parte del viaje.</p>
<p>Los peajes se reparten igual que la gasolina, como si se pagaran a lo largo de toda la ruta. Si un peaje solo afecta a un
tramo concreto, déjalo fuera y repártelo aparte entre los que iban en ese tramo. Para el precio del litro, el Ministerio
publica el de cada gasolinera en el <a href="{GEO}" rel="noopener">Geoportal de Gasolineras</a>; usa el del repostaje real si
ya lo tienes.</p>"""),
]

FAQ = [
    ("¿El conductor paga gasolina?",
     "Entre amigos, lo normal es que sí: el coche lo usa él también. Si el conductor pone el coche y no quiere cobrar su parte a "
     "los demás, o al revés, los demás quieren invitarle, elige «No paga» en «Conductor»."),
    ("¿Cómo se calcula el precio por kilómetro?",
     "Litros por kilómetro por precio del litro: con 6,5 l/100 km y 1,55 €/l son 0,065 × 1,55 = 0,10 € por km, más los peajes "
     "repartidos por la distancia."),
    ("¿Y el desgaste del coche?",
     "Esta cuenta solo reparte combustible y peajes. Si queréis compensar neumáticos, aceite y desgaste, una referencia es el "
     "importe por kilómetro que Hacienda deja pagar sin impuestos por el uso del coche propio: 0,26 €/km."),
    ("¿Se puede cobrar a desconocidos por llevarles en el coche?",
     "Compartir gastos sí, ganar dinero no: las plataformas de coche compartido limitan el precio para que solo cubra los costes. "
     "Llevar pasajeros con beneficio es un transporte que exige autorización."),
]

JS = r"""
function (v, H, C) {
  var km = v.km, c = v.cons, p = v.precio, pe = isNaN(v.peajes) ? 0 : v.peajes;
  if (isNaN(km) || km <= 0) return { err: 'Escribe el recorrido total en km.' };
  if (isNaN(c) || c <= 0 || c > 60) return { err: 'Escribe el consumo en l/100 km (por ejemplo 6,5).' };
  if (isNaN(p) || p <= 0) return { err: 'Escribe el precio del litro.' };
  if (pe < 0) return { err: 'Sin números negativos.' };
  var ppl = [];
  ['p1', 'p2', 'p3', 'p4', 'p5', 'p6'].forEach(function (k, i) { if (!isNaN(v[k]) && v[k] !== 0) ppl.push({ name: 'Pasajero ' + (i + 1), d: v[k], pay: true, s: 0 }); });
  for (var i = 0; i < ppl.length; i++) {
    if (ppl[i].d < 0) return { err: 'Sin números negativos.' };
    if (ppl[i].d > km + 1e-9) return { err: ppl[i].name + ' no puede viajar más km que el coche.' };
  }
  var dp = v.cond !== 'no', drv = { name: 'Conductor', d: km, pay: dp, s: 0 }, all = [drv].concat(ppl);
  var lit = km * c / 100, total = lit * p + pe, ck = total / km, cuts = all.map(function (x) { return x.d; }).sort(function (a, b) { return a - b; });
  var prev = 0, alone = 0;
  cuts.forEach(function (d) {
    if (d <= prev) return;
    var on = all.filter(function (x) { return x.d >= d && x.pay; }), cost = ck * (d - prev);
    if (on.length) on.forEach(function (x) { x.s += cost / on.length; }); else alone += cost;
    prev = d;
  });
  drv.s += alone;
  var rows = all.map(function (x) {
    return [x.name + ' · ' + H.num(x.d, x.d % 1 ? 1 : 0) + ' km', H.eur(H.r2(x.s)), x === drv && !dp && !alone ? 'z' : ''];
  });
  rows.push(['Total', H.eur(H.r2(total)), 'tot']);
  return {
    label: 'Coste del viaje', big: H.eur(H.r2(total)),
    sub: H.num(lit, 1) + ' litros · ' + H.num(ck, 3) + ' €/km' + (pe ? ' con peajes' : ''),
    rows: rows,
    note: !dp && alone ? 'Los tramos en los que el conductor va solo los paga él.' : '',
    n: { total: H.r2(total), drv: H.r2(drv.s), p: ppl.map(function (x) { return H.r2(x.s); }) }
  };
}
"""

TOOL = {
    "slug": "reparto-gasolina-viaje",
    "lang": "es",
    "cat": "vehiculos",
    "icon": "users",
    "order": 35,
    "name": "Reparto de gasolina",
    "k": "dividir gasolina pasajeros tramos compartir coche cuánto paga cada uno bajarse a mitad peajes",
    "title": "Repartir la gasolina entre pasajeros por kilómetros",
    "desc": "Reparte la gasolina y los peajes de un viaje en coche entre pasajeros que hacen distinto recorrido: cada tramo se divide entre los que van en él.",
    "h1": "Repartir la gasolina entre pasajeros",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "km", "type": "number", "label": "Recorrido total", "value": "400", "unit": "km", "w": "s"},
        {"id": "cons", "type": "number", "label": "Consumo", "value": "6,5", "unit": "l/100 km", "step": "0.1", "w": "s"},
        {"id": "precio", "type": "money", "label": "Precio", "value": "1,55", "unit": "€/l", "w": "s"},
        {"id": "peajes", "type": "money", "label": "Peajes", "value": "0", "w": "s"},
        {"id": "cond", "type": "seg", "label": "Conductor", "value": "si", "options": [("si", "Paga"), ("no", "No paga")]},
        {"id": "p1", "type": "number", "label": "Pasajero 1", "value": "400", "unit": "km", "w": "s"},
        {"id": "p2", "type": "number", "label": "Pasajero 2", "value": "400", "unit": "km", "w": "s"},
        {"id": "p3", "type": "number", "label": "Pasajero 3", "value": "150", "unit": "km", "w": "s"},
        {"id": "p4", "type": "number", "label": "Pasajero 4", "value": "", "unit": "km", "w": "s"},
        {"id": "p5", "type": "number", "label": "Pasajero 5", "value": "", "unit": "km", "w": "s", "more": True},
        {"id": "p6", "type": "number", "label": "Pasajero 6", "value": "", "unit": "km", "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("MITECO · Geoportal de Gasolineras (precios oficiales por estación)", GEO)],
    "credits": [],
    "related": ["coste-viaje-coche", "dividir-gastos", "kilometraje-dietas", "consumo-l100km-mpg"],
    "tests": [
        ({}, {"n.total": 40.3, "n.drv": 12.17, "n.p.0": 12.17, "n.p.2": 3.78}),
        ({"cond": "no"}, {"n.drv": 0, "n.p.0": 17.63, "n.p.2": 5.04}),
        ({"p1": "100", "p2": "", "p3": "", "cond": "no"}, {"n.p.0": 10.08, "n.drv": 30.23}),
        ({"p1": "500"}, {"err": "Pasajero 1 no puede viajar más km que el coche."}),
        ({"km": "0"}, {"err": "Escribe el recorrido total en km."}),
    ],
}
