"""Coste de un viaje en coche: fuel from distance, consumption and price per litre, plus tolls and parking, per person."""

GEO = "https://geoportalgasolineras.es/"
WOB = "https://energy.ec.europa.eu/data-and-analysis/weekly-oil-bulletin_en"

BLOCKS = [
    ("Cuánto cuesta el viaje", """
<p>El gasto en combustible es <b>kilómetros × consumo ÷ 100 × precio del litro</b>. A eso se suman los peajes y el
aparcamiento, y el total se divide entre los que viajan. La calculadora hace exactamente eso y te da también los litros que
vas a gastar y el coste por kilómetro, útil para comparar con el tren, el autobús o un coche compartido.</p>
<p>Ejemplo: de Madrid a Valencia por la A-3 hay unos 355 km. Con un coche de gasolina que gasta 6,5 l/100 km y la gasolina a
1,55 €/l, la ida son 355 × 6,5 ÷ 100 = 23,08 litros, es decir, <b>35,77 €</b>. Ida y vuelta, 71,53 €. Si vais cuatro, cada
uno pone 17,88 € por los dos trayectos, sin peajes porque la A-3 es autovía libre. Si dejáis el coche dos días en un
aparcamiento a 18 € al día, súmalos en «Parking» y el reparto sube a 26,88 € por cabeza.</p>"""),
    ("El consumo real, no el del catálogo", """
<p>El dato de la ficha del coche es el del ciclo de homologación WLTP, medido en laboratorio. En carretera casi siempre se
gasta algo más: el aire acondicionado, el maletero lleno, la baca o un portabicicletas y, sobre todo, la velocidad. La
resistencia del aire crece con el cuadrado de la velocidad, así que ir a 130 km/h en lugar de a 110 se nota en el
depósito mucho más de lo que se nota en el tiempo de llegada. Lo más fiable es usar la media del ordenador de a bordo en
viajes parecidos, o el método del depósito lleno: llena, pon el cuentakilómetros parcial a cero, conduce, vuelve a llenar
y divide los litros repostados entre los kilómetros, por cien.</p>
<p>Si tu coche es eléctrico, el cálculo cambia de unidades (kWh/100 km y €/kWh) y depende de dónde cargues: usa la
calculadora de coste del coche eléctrico.</p>"""),
    ("Dónde mirar el precio del combustible", f"""
<p>El Ministerio para la Transición Ecológica publica el precio de cada gasolinera de España, actualizado varias veces al
día, en el <a href="{GEO}" rel="noopener">Geoportal de Gasolineras</a>; puedes buscar por provincia o por ruta. Entre
estaciones de la misma ciudad la diferencia supera a menudo los 10 céntimos por litro: en un depósito de 50 litros son 5 €.
Las gasolineras de autopista y las de las zonas turísticas suelen ser las más caras; repostar antes de salir o en un
polígono cercano a la ruta compensa.</p>
<p>Para un viaje por Europa, la Comisión Europea publica cada semana los precios medios por país en el
<a href="{WOB}" rel="noopener">Weekly Oil Bulletin</a>. Si cruzas a Francia, Portugal o Italia, compáralos antes de decidir
dónde llenar el depósito.</p>"""),
]

FAQ = [
    ("¿Cómo se calcula la gasolina de un viaje?",
     "Multiplica los kilómetros por el consumo en litros cada 100 km, divide entre 100 y multiplica por el precio del litro. "
     "300 km a 7 l/100 km y 1,60 €/l son 21 litros y 33,60 €."),
    ("¿Cuánto gasta un coche cada 100 km?",
     "Un utilitario de gasolina moderno, entre 5 y 7 litros en carretera; un diésel, entre 4 y 6; un SUV grande puede pasar de "
     "8. Mira la media de tu ordenador de a bordo: es tu dato real."),
    ("¿Cómo repartir la gasolina entre los pasajeros?",
     "Si todos hacéis el viaje completo, a partes iguales: es lo que muestra esta calculadora. Si alguien se baja antes, usa el "
     "reparto por tramos, que cobra a cada uno solo los kilómetros que viajó."),
    ("¿Los peajes se reparten también?",
     "Normalmente sí, igual que el combustible. Escribe el importe de los peajes de un trayecto; con «Ida y vuelta» se cuentan "
     "dos veces."),
    ("¿Sale más barato el coche que el tren?",
     "Depende de cuántos vayáis. Para una persona sola el tren suele ganar; a partir de tres o cuatro, el coche casi siempre "
     "sale más barato por persona, aunque cuentes el aparcamiento."),
]

JS = r"""
function (v, H, C) {
  var km = v.km, c = v.cons, p = v.precio, pe = isNaN(v.peajes) ? 0 : v.peajes, pk = isNaN(v.parking) ? 0 : v.parking, n = isNaN(v.pers) ? 1 : v.pers;
  if (isNaN(km) || km <= 0) return { err: 'Escribe la distancia en km.' };
  if (isNaN(c) || c <= 0) return { err: 'Escribe el consumo en l/100 km.' };
  if (c > 60) return { err: 'Consumo en litros cada 100 km (por ejemplo 6,5).' };
  if (isNaN(p) || p <= 0) return { err: 'Escribe el precio del litro.' };
  if (pe < 0 || pk < 0) return { err: 'Sin números negativos.' };
  if (n < 1 || n % 1) return { err: 'Personas: un número entero desde 1.' };
  var k = v.tr === '1' ? 1 : 2, dist = km * k, lit = dist * c / 100, fuel = lit * p, tolls = pe * k, total = fuel + tolls + pk;
  var rows = [['Combustible · ' + H.num(lit, 1) + ' l', H.eur(H.r2(fuel))]];
  if (tolls) rows.push(['Peajes' + (k === 2 ? ' (2 trayectos)' : ''), H.eur(H.r2(tolls))]);
  if (pk) rows.push(['Parking', H.eur(H.r2(pk))]);
  rows.push(['Total', H.eur(H.r2(total)), 'tot']);
  if (n > 1) rows.push(['Por persona (' + n + ')', H.eur(H.r2(total / n)), 'tot']);
  rows.push(['Coste por km', H.num(total / dist, 3) + ' €', 'z']);
  return {
    label: n > 1 ? 'Por persona' : 'Coste del viaje', big: H.eur(H.r2(n > 1 ? total / n : total)),
    sub: H.num(dist, dist % 1 ? 1 : 0) + ' km' + (k === 2 ? ' ida y vuelta' : '') + ' · ' + H.num(lit, 1) + ' litros' + (n > 1 ? ' · total ' + H.eur(H.r2(total)) : ''),
    rows: rows, n: { lit: lit, fuel: H.r2(fuel), total: H.r2(total), pp: H.r2(total / n) }
  };
}
"""

TOOL = {
    "slug": "coste-viaje-coche",
    "lang": "es",
    "cat": "vehiculos",
    "icon": "route",
    "order": 30,
    "name": "Coste viaje en coche",
    "k": "gasolina diésel combustible cuánto cuesta viaje litros peajes por persona consumo",
    "title": "Calcular el coste de un viaje en coche: gasolina y peajes",
    "desc": "Calcula cuánto cuesta un viaje en coche: litros y euros de gasolina o diésel según tu consumo, peajes, parking y lo que paga cada persona.",
    "h1": "Coste de un viaje en coche",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "km", "type": "number", "label": "Distancia", "value": "355", "unit": "km", "w": "s"},
        {"id": "tr", "type": "seg", "label": "Trayecto", "value": "2", "options": [("1", "Solo ida"), ("2", "Ida y vuelta")]},
        {"id": "cons", "type": "number", "label": "Consumo", "value": "6,5", "unit": "l/100 km", "step": "0.1", "w": "s"},
        {"id": "precio", "type": "money", "label": "Precio", "value": "1,55", "unit": "€/l", "w": "s"},
        {"id": "pers", "type": "number", "label": "Personas", "value": "4", "w": "s"},
        {"id": "peajes", "type": "money", "label": "Peajes por trayecto", "value": "0", "w": "s"},
        {"id": "parking", "type": "money", "label": "Parking", "value": "0", "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("MITECO · Geoportal de Gasolineras (precios oficiales por estación)", GEO),
                ("Comisión Europea · Weekly Oil Bulletin", WOB)],
    "credits": [],
    "related": ["reparto-gasolina-viaje", "consumo-l100km-mpg", "coste-coche-electrico", "kilometraje-dietas"],
    "tests": [
        ({"tr": "1", "pers": "1"},{"n.total": 35.77, "n.lit": 23.075}),
        ({}, {"n.total": 71.53, "n.pp": 17.88}),
        ({"parking": "36"}, {"n.pp": 26.88}),
        ({"km": "100", "tr": "1", "peajes": "12,40", "pers": "2", "cons": "5", "precio": "1,6"}, {"n.total": 20.4, "n.pp": 10.2}),
        ({"km": ""}, {"err": "Escribe la distancia en km."}),
        ({"pers": "2,5"}, {"err": "Personas: un número entero desde 1."}),
    ],
}
