"""Presupuesto de viaje: total and per-person budget by days, travellers and categories, with a contingency margin,
optional currency conversion and the INE average daily spend as a yardstick."""

INE = "https://ine.es/dyngs/Prensa/ETR4T25.htm"
BCE = "https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html"

BLOCKS = [
    ("Cómo se calcula el presupuesto", """
<p>Un presupuesto de viaje fiable separa lo que depende de las <b>noches</b> (el alojamiento), lo que depende de los
<b>días y las personas</b> (comida, entradas, transporte en destino) y lo que se paga <b>una sola vez</b> (los billetes o la
gasolina de ida y vuelta, el seguro, el visado). La calculadora multiplica cada partida por lo suyo, suma un margen para
imprevistos y te da el total, lo que toca a cada persona y el gasto por persona y día, que es la cifra que mejor se compara
entre destinos.</p>
<p>Ejemplo: una pareja pasa 5 días y 4 noches en Lisboa. Hotel a 90 € la noche (la habitación, no por persona), comidas a
35 € por persona y día, 20 € diarios por persona entre entradas y metro, y 250 € de vuelos para los dos. Alojamiento 360 €,
comida 350 €, actividades 200 € y transporte 250 €: 1.160 €. Con un 10 % de imprevistos, <b>1.276 € en total</b>, 638 € por
persona y 127,60 € por persona y día.</p>"""),
    ("¿Es mucho o poco? La media de los viajeros en España", f"""
<p>El Instituto Nacional de Estadística mide cada trimestre lo que gastan los residentes en España cuando viajan, en la
<a href="{INE}" rel="noopener">Encuesta de Turismo de Residentes</a>. En 2025 el gasto medio fue de <b>66 € por persona y día</b>
en los viajes dentro de España y de <b>131 €</b> en los viajes al extranjero (81 € de media entre los dos). Esa media incluye
muchas noches en casa de familiares o en segunda residencia, que no cuestan alojamiento, así que un viaje con hotel suele quedar
por encima. La calculadora te muestra la comparación debajo del resultado.</p>
<p>Si tu cifra por persona y día sale muy por debajo, revisa si te has dejado algo: el transporte desde el aeropuerto, las
propinas, la tasa turística (en Cataluña, Baleares y algunas ciudades se cobra por persona y noche en el alojamiento), o las
comidas del día de llegada y del de vuelta.</p>"""),
    ("Viajes fuera de la zona euro", f"""
<p>Si vas a pagar en otra moneda, escribe en «Más opciones» cuántas unidades de esa moneda dan por 1 euro y verás el total
convertido. El Banco Central Europeo publica cada día laborable los <a href="{BCE}" rel="noopener">tipos de cambio de
referencia del euro</a>; tu banco o la casa de cambio aplicarán un tipo algo peor, más una comisión si pagas con tarjeta en
divisa. Un margen de imprevistos del 10 al 15 % suele cubrir esa diferencia y los gastos que no se planifican.</p>"""),
]

FAQ = [
    ("¿Cuánto dinero llevar para un viaje de una semana?",
     "Con la media del INE, unos 460 € por persona en España (7 días × 66 €) y unos 920 € al extranjero, sin contar los billetes si "
     "son caros. Con hotel y comidas fuera, calcula tu caso con la calculadora."),
    ("¿El alojamiento se pone por persona o por habitación?",
     "Por noche y en total: lo que pagáis entre todos por el hotel o el apartamento cada noche. La calculadora lo multiplica por "
     "las noches, no por las personas."),
    ("¿Cuántas noches tiene un viaje de 5 días?",
     "Cuatro, si llegas el primer día y te vas el último. Si cambian, escribe las noches en «Más opciones»."),
    ("¿Qué porcentaje dejar para imprevistos?",
     "Entre un 10 y un 15 %. Más si viajas con niños, en coche de alquiler o a un país con una moneda muy variable."),
    ("¿Qué entra en «Transporte»?",
     "Lo que se paga una vez para todo el grupo: vuelos, tren o autobús de ida y vuelta, o la gasolina y los peajes si vais en coche. "
     "El metro o los taxis del día a día, mejor en «Actividades»."),
]

JS = r"""
function (v, H, C) {
  var d = v.dias, p = v.pers, ni = isNaN(v.noches) ? Math.max(0, d - 1) : v.noches;
  function z(x) { return isNaN(x) ? 0 : x; }
  var al = z(v.aloj), co = z(v.comida), ac = z(v.act), tr = z(v.transp), ot = z(v.otros), im = isNaN(v.imprev) ? 0 : v.imprev;
  if (isNaN(d) || d < 1 || d % 1) return { err: 'Días: un número entero desde 1.' };
  if (isNaN(p) || p < 1 || p % 1) return { err: 'Personas: un número entero desde 1.' };
  if (ni < 0 || ni % 1 || ni > d) return { err: 'Noches: un número entero entre 0 y los días.' };
  if (al < 0 || co < 0 || ac < 0 || tr < 0 || ot < 0 || im < 0) return { err: 'Sin números negativos.' };
  var A = al * ni, Co = co * p * d, Ac = ac * p * d, sub = A + Co + Ac + tr + ot, I = sub * im / 100, tot = sub + I, pp = tot / p, ppd = pp / d;
  var rows = [];
  if (A) rows.push(['Alojamiento · ' + ni + ' ' + H.plural(ni, 'noche', 'noches'), H.eur(H.r2(A))]);
  if (Co) rows.push(['Comida', H.eur(H.r2(Co))]);
  if (Ac) rows.push(['Actividades', H.eur(H.r2(Ac))]);
  if (tr) rows.push(['Transporte', H.eur(H.r2(tr))]);
  if (ot) rows.push(['Otros', H.eur(H.r2(ot))]);
  if (I) rows.push(['Imprevistos ' + H.num(im, im % 1 ? 1 : 0) + ' %', H.eur(H.r2(I))]);
  rows.push(['Total', H.eur(H.r2(tot)), 'tot']);
  if (p > 1) rows.push(['Por persona', H.eur(H.r2(pp)), 'tot']);
  rows.push(['Por persona y día', H.eur(H.r2(ppd)), 'z']);
  if (!isNaN(v.cambio) && v.cambio > 0) rows.push(['En moneda local × ' + H.num(v.cambio, 4).replace(/,?0+$/, ''), H.num(tot * v.cambio, 2), 'z']);
  if (!tot) return { err: 'Escribe al menos una partida del viaje.' };
  return {
    label: 'Presupuesto', big: H.eur(H.r2(tot)),
    sub: d + ' ' + H.plural(d, 'día', 'días') + ' · ' + p + ' ' + H.plural(p, 'persona', 'personas') + ' · ' + H.eur(H.r2(ppd)) + ' por persona y día',
    rows: rows,
    note: 'Media en 2025 (INE): 66 € por persona y día en viajes por España, 131 € en el extranjero.',
    print: true,
    n: { total: H.r2(tot), pp: H.r2(pp), ppd: H.r2(ppd), noches: ni }
  };
}
"""

TOOL = {
    "slug": "presupuesto-viaje",
    "lang": "es",
    "cat": "ocio",
    "icon": "luggage",
    "order": 50,
    "name": "Presupuesto de viaje",
    "k": "cuánto cuesta viajar gasto vacaciones por persona por día dinero llevar hotel comida",
    "title": "Calculadora de presupuesto de viaje por persona y día",
    "desc": "Calcula el presupuesto de tu viaje por días y personas: alojamiento, comida, actividades, transporte e imprevistos, con el gasto por persona y día.",
    "h1": "Calculadora de presupuesto de viaje",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "dias", "type": "number", "label": "Días", "value": "5", "w": "s"},
        {"id": "pers", "type": "number", "label": "Personas", "value": "2", "w": "s"},
        {"id": "aloj", "type": "money", "label": "Alojamiento", "value": "90", "unit": "€/noche", "w": "s"},
        {"id": "comida", "type": "money", "label": "Comida", "value": "35", "unit": "€/pers./día", "w": "s"},
        {"id": "act", "type": "money", "label": "Actividades", "value": "20", "unit": "€/pers./día", "w": "s"},
        {"id": "transp", "type": "money", "label": "Transporte", "value": "250", "unit": "€ total", "w": "s"},
        {"id": "imprev", "type": "number", "label": "Imprevistos", "value": "10", "unit": "%", "w": "s"},
        {"id": "noches", "type": "number", "label": "Noches", "value": "", "placeholder": "días − 1", "w": "s", "more": True},
        {"id": "otros", "type": "money", "label": "Otros", "value": "0", "unit": "€ total", "w": "s", "more": True},
        {"id": "cambio", "type": "number", "label": "Cambio", "value": "", "unit": "por 1 €", "step": "0.0001", "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("INE · Encuesta de Turismo de Residentes, 4.º trimestre y año 2025 (26-03-2026)", INE),
                ("Banco Central Europeo · tipos de cambio de referencia del euro", BCE)],
    "credits": [],
    "related": ["dividir-gastos", "coste-viaje-coche", "reparto-gasolina-viaje", "cuenta-atras"],
    "tests": [
        ({}, {"n.total": 1276, "n.pp": 638, "n.ppd": 127.6, "n.noches": 4}),
        ({"noches": "5", "imprev": "0", "pers": "1"}, {"n.total": 975}),
        ({"dias": "1", "aloj": "0", "transp": "0", "pers": "3", "imprev": "0"}, {"n.total": 165, "n.noches": 0}),
        ({"dias": "0"}, {"err": "Días: un número entero desde 1."}),
        ({"noches": "9"}, {"err": "Noches: un número entero entre 0 y los días."}),
    ],
}
