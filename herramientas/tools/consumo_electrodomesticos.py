"""Consumo de electrodomésticos: kWh and money per hour, day, month and year from the power (W), hours of use, days per
week and the price of the kWh, with optional standby. English twin: appliance_energy_cost.py (same JS, any currency)."""
from herramientas.tools import _bricolaje as F

LABEL_EU = "https://eur-lex.europa.eu/eli/reg/2017/1369/oj?locale=es"
LABEL_EU_EN = "https://eur-lex.europa.eu/eli/reg/2017/1369/oj?locale=en"
IDAE = "https://www.idae.es/sites/default/files/documentos/Guia-de-la-energia-idae/Guia_Energia_2007.pdf"
DOE = "https://www.energy.gov/energysaver/articles/estimating-appliance-and-home-electronic-energy-use"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var cur = EN ? (v.cur || '$') : '€';
  function money(x, d) { var s = fx(x, d || 2); return EN ? (s.charAt(0) === '−' ? '−' + cur + s.slice(1) : cur + s) : s + ' €'; }
  var T = EN ? { w: 'Enter the power in watts.', h: 'Hours per day between 0 and 24.', p: 'Enter the price per kWh.', label: 'Cost per year',
      hr: 'Per hour of use', d: 'Per day', m: 'Per month', y: 'Per year', sb: 'Standby', u: ' units' }
    : { w: 'Escribe la potencia en vatios.', h: 'Horas al día entre 0 y 24.', p: 'Escribe el precio del kWh.', label: 'Coste al año',
      hr: 'Por hora de uso', d: 'Al día', m: 'Al mes', y: 'Al año', sb: 'En espera', u: ' unidades' };
  if (!(v.w > 0)) return { err: T.w };
  if (!(v.h >= 0 && v.h <= 24)) return { err: T.h };
  if (!(v.precio > 0)) return { err: T.p };
  var days = v.dias >= 0 && v.dias <= 7 ? v.dias : 7, n = v.uds > 0 ? Math.floor(v.uds) : 1, sb = v.espera > 0 ? v.espera : 0;
  var on = v.w * v.h / 1000 * days / 7, off = sb * (24 - v.h) / 1000;
  var kd = (on + off) * n, ky = kd * 365, km = ky / 12;
  function kwh(x) { return fx(x, x < 10 ? 2 : x < 100 ? 1 : 0) + ' kWh'; }
  var rows = [[T.hr, money(v.w / 1000 * v.precio * n, v.w / 1000 * v.precio * n < 1 ? 3 : 2) + ' · ' + kwh(v.w / 1000 * n)], [T.d, money(kd * v.precio) + ' · ' + kwh(kd)],
    [T.m, money(km * v.precio) + ' · ' + kwh(km)], [T.y, money(ky * v.precio) + ' · ' + kwh(ky), 'tot']];
  if (sb) rows.push([T.sb, money(off * n * 365 * v.precio) + ' · ' + kwh(off * n * 365), 'sub']);
  return {
    label: T.label, big: money(ky * v.precio), sub: kwh(ky) + (n > 1 ? ' · ' + n + T.u : ''),
    rows: rows,
    n: { kwhDay: r(kd, 4), kwhYear: r(ky, 2), year: r(ky * v.precio, 2), hour: r(v.w / 1000 * v.precio * n, 4) }
  };
}
"""

PRESETS = [
    ("otro", "Otro aparato"),
    ("nevera", "Frigorífico", {"w": "35", "h": "24"}), ("lavadora", "Lavadora (ciclo 40 °C)", {"w": "900", "h": "1", "dias": "4"}),
    ("lavavaj", "Lavavajillas (eco)", {"w": "1000", "h": "1", "dias": "5"}), ("secadora", "Secadora", {"w": "1200", "h": "1,5", "dias": "3"}),
    ("horno", "Horno", {"w": "1500", "h": "1", "dias": "3"}), ("placa", "Placa de inducción", {"w": "1500", "h": "1"}),
    ("micro", "Microondas", {"w": "1200", "h": "0,25"}), ("aire", "Aire acondicionado", {"w": "900", "h": "6"}),
    ("radiador", "Radiador eléctrico", {"w": "1500", "h": "4"}), ("termo", "Termo eléctrico", {"w": "1500", "h": "2"}),
    ("tv", "Televisor", {"w": "90", "h": "4"}), ("pc", "Ordenador de sobremesa", {"w": "150", "h": "6"}),
    ("portatil", "Portátil", {"w": "45", "h": "6"}), ("router", "Router wifi", {"w": "10", "h": "24"}),
    ("led", "Bombilla LED", {"w": "9", "h": "5"}), ("secador", "Secador de pelo", {"w": "1800", "h": "0,2"}),
]


def blocks(ctx):
    n, e = F.n, ctx.eur
    p = 0.15
    tv = 90 * 4 / 1000 * 365
    nev = 35 * 24 / 1000 * 365
    rad = 1500 * 4 / 1000
    return [
        ("Cuánto consume un electrodoméstico", f"""
<p>Multiplica la potencia en vatios por las horas de uso y divide entre 1.000: salen los kWh. Por el precio del kWh, el
coste. Una estufa o radiador de 1.500 W encendido 4 horas consume {n(rad, 0)} kWh al día; a 0,15 €/kWh son {e(rad * p)} al
día y unos {e(rad * p * 30)} al mes. Un televisor de 90 W cuatro horas al día gasta {n(tv, 0)} kWh al año, unos
{e(tv * p)}.</p>
<p>Los aparatos con termostato o compresor no consumen su potencia máxima todo el tiempo. Un frigorífico de 150 W solo
funciona a ratos y su media ronda los 30 a 40 W: la calculadora usa 35 W durante 24 horas, {n(nev, 0)} kWh al año, en línea
con lo que indica la etiqueta energética de un frigorífico combi actual. Para estos aparatos, lo más fiable es la etiqueta
energética europea: da el consumo en kWh al año (frigoríficos) o en kWh por 100 ciclos (lavadoras y lavavajillas, desde
2021). Divide ese último entre 100 y tendrás el consumo de un lavado.</p>"""),
        ("El precio del kWh", """
<p>El precio que hay que poner es el del <b>término de energía</b> de tu factura, en €/kWh. Si la factura lo da sin
impuestos, multiplícalo por 1,27 aproximadamente (impuesto eléctrico del 5,11 % e IVA del 21 %). Con discriminación horaria
el kWh cuesta bastante menos en valle (de 0:00 a 8:00 y fines de semana) que en punta (de 10:00 a 14:00 y de 18:00 a 22:00
los laborables), así que poner la lavadora o cargar el coche de noche baja el coste aunque los kWh sean los mismos. La
potencia contratada se paga aparte, consumas o no.</p>"""),
        ("El consumo en espera", """
<p>Muchos aparatos siguen gastando apagados con el mando: decodificadores, equipos de sonido, cafeteras con reloj o
cargadores enchufados. En «Más opciones» puedes añadir los vatios en espera para las horas que el aparato no se usa. Dos o
tres vatios parecen poco, pero 24 horas al día durante un año son entre 18 y 26 kWh por aparato. Una regleta con interruptor
lo elimina. Las normas europeas de diseño ecológico limitan el modo espera de los aparatos nuevos a menos de 1 W, así que
los que más gastan apagados suelen ser los antiguos.</p>"""),
    ]


FAQ = [
    ("¿Cuánto cuesta tener encendido un aparato una hora?",
     "Su potencia en kW por el precio del kWh. Un aparato de 2.000 W, a 0,15 €/kWh, cuesta 0,30 € por hora; uno de 100 W, 1,5 céntimos."),
    ("¿Cuánto consume un aire acondicionado al mes?",
     "Un split de 3.000 frigorías gasta en torno a 0,9 kW de media. Seis horas al día durante 30 días son unos 160 kWh, unos 24 € a 0,15 €/kWh."),
    ("¿Qué electrodoméstico gasta más?",
     "Los que calientan: termo, radiadores, horno, secadora y placa. Aunque se usen menos horas, su potencia es de 1.500 a 2.500 W."),
    ("¿Cómo sé la potencia de mi aparato?",
     "Viene en la placa de características (pegatina trasera o inferior) en vatios (W). Si da amperios, multiplica por 230 V."),
    ("¿Cuánto gasta un frigorífico al año?",
     "Entre 150 y 350 kWh un modelo actual, según tamaño y clase energética: de 22 a 52 € al año a 0,15 €/kWh. La etiqueta da la cifra exacta."),
]

TOOL = {
    "slug": "consumo-electrodomesticos",
    "lang": "es",
    "twin": "appliance-energy-cost",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "plug",
    "order": 65,
    "name": "Consumo de electrodomésticos",
    "k": "kwh vatios coste luz aparato hora día mes año frigorífico radiador aire acondicionado espera",
    "title": "Consumo de electrodomésticos: kWh y euros",
    "desc": "Calcula cuánto consume y cuánto cuesta un electrodoméstico por hora, día, mes y año según sus vatios, las horas de uso y el precio del kWh.",
    "h1": "Calculadora de consumo de electrodomésticos",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ap", "type": "select", "label": "Aparato", "value": "radiador", "options": PRESETS, "custom": "otro"},
        {"id": "w", "type": "number", "label": "Potencia", "value": "1500", "unit": "W"},
        {"id": "h", "type": "number", "label": "Horas al día", "value": "4", "unit": "h", "step": "0.05", "w": "s"},
        {"id": "dias", "type": "number", "label": "Días/semana", "value": "7", "w": "s"},
        {"id": "precio", "type": "number", "label": "Precio", "value": "0,15", "unit": "€/kWh", "step": "0.001", "w": "s"},
        {"id": "uds", "type": "number", "label": "Unidades", "value": "1", "w": "s", "more": True},
        {"id": "espera", "type": "number", "label": "En espera", "value": "0", "unit": "W", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Reglamento (UE) 2017/1369, etiquetado energético (EUR-Lex)", LABEL_EU),
                ("IDAE · Guía práctica de la energía: consumo eficiente y responsable", IDAE)],
    "related": ["potencia-contratada", "frigorias-aire-acondicionado", "placas-solares-estimacion", "seccion-cable"],
    "tests": [
        ({}, {"n.kwhDay": 6, "n.kwhYear": 2190, "n.year": 328.5, "n.hour": 0.225}),
        ({"w": "90", "h": "4"}, {"n.kwhYear": 131.4}),
        ({"w": "900", "h": "1", "dias": "4"}, {"n.kwhDay": 0.5143}),
        ({"w": "10", "h": "0", "espera": "2"}, {"n.kwhDay": 0.048}),
        ({"h": "25"}, {"err": "Horas al día entre 0 y 24."}),
        ({"precio": ""}, {"err": "Escribe el precio del kWh."}),
    ],
}
