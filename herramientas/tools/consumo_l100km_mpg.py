"""Convertir consumo: l/100 km <-> km/l <-> mpg (US and UK gallons). Spanish page; the English twin is
mpg-to-l100km (same compute)."""
from herramientas.tools import _coche as K

NIST = "https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9"
UKWM = "https://www.legislation.gov.uk/ukpga/1985/72/schedule/1"

US = 100 * K.GAL_US / K.MILE_KM    # 235.2146
UK = 100 * K.GAL_UK / K.MILE_KM    # 282.4809

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var US = 100 * 3.785411784 / 1.609344, UK = 100 * 4.54609 / 1.609344, x = v.val, u = v.u, l;
  if (isNaN(x) || x <= 0) return { err: EN ? 'Enter a fuel economy figure above zero.' : 'Escribe un consumo mayor que cero.' };
  l = u === 'l100' ? x : u === 'kml' ? 100 / x : u === 'mpgus' ? US / x : UK / x;
  var o = { l100: l, kml: 100 / l, mpgus: US / l, mpguk: UK / l };
  var lab = EN ? { l100: 'L/100 km', kml: 'km/L', mpgus: 'mpg (US)', mpguk: 'mpg (UK)' } : { l100: 'l/100 km', kml: 'km/l', mpgus: 'mpg (EE. UU.)', mpguk: 'mpg (R. Unido)' };
  var main = u !== 'l100' ? 'l100' : EN ? 'mpgus' : 'kml';
  var rows = ['l100', 'kml', 'mpgus', 'mpguk'].filter(function (k) { return k !== u; }).map(function (k) { return [lab[k], fv(o[k], 2), k === main ? 'tot' : '']; });
  var LU = EN ? ' L' : ' l';
  rows.push([EN ? 'Fuel for 100 miles' : 'Litros en 100 millas', fv(l * 1.609344, 2) + LU + ' · ' + fv(l * 1.609344 / 3.785411784, 2) + (EN ? ' US gal' : ' gal EE. UU.'), 'z']);
  return {
    label: lab[main], big: fv(o[main], 2),
    sub: fv(x, 2) + ' ' + lab[u] + ' = ' + fv(o[main], 2) + ' ' + lab[main],
    rows: rows, n: { l100: r(l, 4), kml: r(o.kml, 4), mpgus: r(o.mpgus, 4), mpguk: r(o.mpguk, 4) }
  };
}
"""


def table(en):
    th = ("L/100 km", "km/L", "mpg (US)", "mpg (UK)") if en else ("l/100 km", "km/l", "mpg EE. UU.", "mpg R. Unido")
    rows = "".join(
        f"<tr><td class=num>{K.n(x, 0 if x % 1 == 0 else 1, en)}</td><td class=num>{K.n(100 / x, 1, en)}</td>"
        f"<td class=num>{K.n(US / x, 1, en)}</td><td class=num>{K.n(UK / x, 1, en)}</td></tr>"
        for x in (3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 8, 9, 10, 12, 15))
    return (f'<table class="tbl"><thead><tr>{"".join(f"<th>{h}</th>" for h in th)}</tr></thead>'
            f"<tbody>{rows}</tbody></table>")


def blocks(ctx):
    return [
        ("Las fórmulas", f"""
<p>En España y en casi toda Europa el consumo se da en <b>litros cada 100 km</b>: cuanto más bajo, mejor. En Estados Unidos y
en el Reino Unido se da al revés, en <b>millas por galón</b> (mpg): cuanto más alto, mejor. Y en Latinoamérica es habitual
hablar de <b>kilómetros por litro</b>. Las conversiones exactas son:</p>
<ul>
<li>km/l = 100 ÷ (l/100 km)</li>
<li>mpg de EE. UU. = 235,215 ÷ (l/100 km)</li>
<li>mpg del Reino Unido = 282,481 ÷ (l/100 km)</li></ul>
<p>Las constantes salen de las definiciones legales: la milla internacional mide 1,609344 km, el galón estadounidense
3,785411784 litros y el galón imperial británico 4,54609 litros. Como el galón británico es un 20 % mayor, la misma eficiencia
da más mpg en el Reino Unido: 40 mpg británicas son solo 33,3 mpg estadounidenses.</p>
<p>Ejemplo: un coche estadounidense anunciado con 30 mpg gasta 235,215 ÷ 30 = <b>7,84 l/100 km</b>. Un coche europeo de 5 l/100 km
hace 20 km por litro, 47 mpg en EE. UU. y 56,5 mpg en el Reino Unido.</p>"""),
        ("Tabla de equivalencias", f"""
<p>Valores frecuentes, redondeados a un decimal:</p>{table(False)}
<p>Fíjate en que la escala no es lineal: pasar de 10 a 8 l/100 km ahorra 2 litros cada 100 km, lo mismo que pasar de 23,5 a
29,4 mpg; en cambio, pasar de 40 a 50 mpg solo ahorra 1,2 litros. Para comparar cuánto vas a gastar, l/100 km es la medida
más intuitiva, porque es directamente proporcional al combustible y al dinero.</p>"""),
        ("Para qué sirve", """
<p>Para entender la ficha de un coche importado de Estados Unidos o del Reino Unido, comparar pruebas de revistas extranjeras,
leer el ordenador de a bordo de un coche configurado en millas o calcular el combustible de un viaje por EE. UU. con un
coche de alquiler. Si luego quieres saber cuánto te costará el viaje, pasa el consumo en l/100 km a la calculadora de coste del
viaje en coche.</p>"""),
    ]


FAQ = [
    ("¿Cuántos l/100 km son 40 mpg?",
     "Depende del galón: 40 mpg estadounidenses son 5,88 l/100 km y 40 mpg británicas, 7,06 l/100 km."),
    ("¿Cómo paso de km/l a l/100 km?",
     "Divide 100 entre los km/l. Un coche que hace 16 km por litro gasta 100 ÷ 16 = 6,25 l/100 km."),
    ("¿Por qué el mpg británico es más alto que el estadounidense?",
     "Porque el galón imperial (4,546 l) es mayor que el de EE. UU. (3,785 l). Con el mismo consumo, en un galón más grande se "
     "recorren más millas."),
    ("¿Qué es un buen consumo?",
     "En un turismo actual, por debajo de 6 l/100 km en carretera es bueno; un híbrido puede bajar de 5. En mpg de EE. UU., más "
     "de 40 se considera muy eficiente."),
    ("¿Sirve para coches eléctricos?",
     "No: los eléctricos se miden en kWh/100 km o en millas por kWh. Para su coste usa la calculadora del coche eléctrico."),
]

INPUTS_ES = [
    {"id": "val", "type": "number", "label": "Consumo", "value": "6,5", "step": "0.01", "w": "s"},
    {"id": "u", "type": "seg", "label": "Unidad", "value": "l100", "options": [
        ("l100", "l/100 km"), ("kml", "km/l"), ("mpgus", "mpg EE. UU."), ("mpguk", "mpg R. Unido")]},
]

TOOL = {
    "slug": "consumo-l100km-mpg",
    "lang": "es",
    "twin": "mpg-to-l100km",
    "cat": "vehiculos",
    "icon": "gas-station",
    "order": 45,
    "name": "Convertir consumo",
    "k": "litros 100 km km por litro mpg millas por galón convertir consumo gasolina",
    "title": "Convertir l/100 km a km/l y mpg (EE. UU. y Reino Unido)",
    "desc": "Convierte el consumo de un coche entre litros cada 100 km, kilómetros por litro y millas por galón de EE. UU. o del Reino Unido, con tabla.",
    "h1": "Convertir l/100 km, km/l y mpg",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": K.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("NIST SP 811, apéndice B.9 · factores de conversión (galón, milla)", NIST),
                ("Weights and Measures Act 1985, anexo 1 · galón imperial = 4,54609 l (legislation.gov.uk)", UKWM)],
    "credits": [],
    "related": ["coste-viaje-coche", "reparto-gasolina-viaje", "velocidad-media-tiempo", "cambio-neumaticos-tamano"],
    "tests": [
        ({}, {"n.kml": 15.3846, "n.mpgus": 36.1869, "n.mpguk": 43.4586}),
        ({"val": "30", "u": "mpgus"}, {"n.l100": 7.8405}),
        ({"val": "16", "u": "kml"}, {"n.l100": 6.25}),
        ({"val": "40", "u": "mpguk"}, {"n.l100": 7.0620, "n.mpgus": 33.307}),
        ({"val": "0"}, {"err": "Escribe un consumo mayor que cero."}),
    ],
}
