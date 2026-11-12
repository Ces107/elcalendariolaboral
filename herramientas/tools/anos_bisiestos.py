"""Años bisiestos: is a year a leap year (Gregorian rule, with the reason), next and previous one, weekday of its
29 February, and the list of leap years in a range."""

JS = r"""
function (v, H, C) {
  var WD = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
  var y = v.ano, a = v.desde, b = v.hasta;
  function int(x) { return x === Math.floor(x); }
  if (!(y >= 1583 && y <= 9999 && int(y))) return { err: 'Año: de 1583 a 9999.' };
  if (!(a >= 1583 && b <= 9999 && int(a) && int(b) && a <= b)) return { err: 'Rango: años de 1583 a 9999, «desde» antes que «hasta».' };
  if (b - a > 1000) return { err: 'Rango de 1.000 años como máximo.' };
  var lp = H.leap(y), why = y % 400 === 0 ? 'divisible entre 400' : y % 100 === 0 ? 'divisible entre 100 pero no entre 400' : y % 4 === 0 ? 'divisible entre 4 y no entre 100' : 'no divisible entre 4';
  var nx = y + 1, pv = y - 1;
  while (!H.leap(nx)) nx++;
  while (pv >= 1583 && !H.leap(pv)) pv--;
  var list = [];
  for (var k = a; k <= b; k++) if (H.leap(k)) list.push(k);
  var rows = [['Motivo', why], ['Días del año', H.yearDays(y)]];
  if (lp) rows.push(['29 de febrero de ' + y, WD[H.wd(new Date(Date.UTC(y, 1, 29)))]]);
  rows.push(['Próximo bisiesto', nx], ['Anterior', pv >= 1583 ? pv : '–']);
  return { label: 'Año ' + y, big: lp ? 'Sí, es bisiesto' : 'No es bisiesto', sub: lp ? '366 días: tiene 29 de febrero' : '365 días',
    rows: rows,
    html: '<h2 class="cq-h">Bisiestos de ' + a + ' a ' + b + ' · ' + list.length + '</h2><p class="bis">' + (list.length ? list.join(' · ') : '–') + '</p>',
    n: { leap: lp, next: nx, prev: pv, count: list.length } };
}
"""

BLOCKS = [
    ("La regla de los años bisiestos", """
<p>Un año es bisiesto si es divisible entre 4, salvo los que acaban en 00, que solo lo son si además son divisibles entre 400. Así,
2028 es bisiesto (2028 ÷ 4 = 507), 2100 no lo será (divisible entre 100 pero no entre 400) y 2000 sí lo fue (2000 ÷ 400 = 5). Entre
1900 y 2100 hay 49 años bisiestos: de 1904 a 2096, cada cuatro años, contando el 2000. Escribe un año para comprobarlo o cambia el
rango para obtener la lista completa, por ejemplo para una hoja de cálculo o un ejercicio de clase.</p>
<p>El próximo bisiesto es 2028, y su 29 de febrero cae en martes; el siguiente, 2032, en domingo. Los bisiestos tienen 366 días, así
que todas las fechas a partir del 29 de febrero se desplazan dos días de la semana respecto al año anterior en lugar de uno.</p>"""),
    ("Por qué existen", """
<p>La Tierra tarda unos 365,2422 días en completar el ciclo de las estaciones (el año trópico). El calendario juliano, de Julio César,
añadía un día cada cuatro años: 365,25 días de media, once minutos de más cada año. En el siglo XVI el desfase acumulado era de diez
días y el equinoccio de primavera caía el 11 de marzo. La reforma del papa Gregorio XIII en 1582 quitó esos diez días y suprimió tres
bisiestos cada 400 años (los años 00 no divisibles entre 400). El año gregoriano dura de media 365,2425 días, y el error que queda
es de un día cada unos 3.000 años.</p>
<p>La palabra viene del latín <i>bis sextus</i>: los romanos no añadían el 29 de febrero, sino que repetían el sexto día antes de las
calendas de marzo, el 24 de febrero. Por eso la regla solo vale desde 1583: antes se usaba el juliano, en el que todos los años
divisibles entre 4, incluidos 1500 o 1300, eran bisiestos. No hay que confundirlos con los segundos intercalares que se añaden de vez
en cuando a la hora atómica: esos no cambian el calendario.</p>"""),
]

FAQ = [
    ("¿Cuál es el próximo año bisiesto?",
     "2028. Después vienen 2032, 2036, 2040 y 2044. El año 2100 no será bisiesto."),
    ("¿2026 o 2027 son bisiestos?",
     "No: ninguno es divisible entre 4, así que febrero tiene 28 días y el año, 365."),
    ("¿Por qué el año 2000 fue bisiesto si acaba en 00?",
     "Porque es divisible entre 400. Los años 00 solo son bisiestos en ese caso: 1600 y 2000 sí; 1700, 1800, 1900 y 2100 no."),
    ("¿Cuántos años bisiestos hay en un siglo?",
     "24 o 25: 24 en un siglo como el XXI cuyo año 2100 no es bisiesto y 25 en los que incluyen un año divisible entre 400, como el que va "
     "de 1901 a 2000."),
    ("¿Cuándo celebran el cumpleaños los nacidos un 29 de febrero?",
     "En los años no bisiestos, muchos lo celebran el 28 de febrero y otros el 1 de marzo. La calculadora de edad exacta cuenta el año "
     "cumplido el 28 de febrero."),
]

TOOL = {
    "slug": "anos-bisiestos",
    "lang": "es",
    "cat": "fechas",
    "icon": "calendar-plus",
    "order": 80,
    "name": "Años bisiestos",
    "k": "bisiesto lista es bisiesto 29 de febrero próximo año bisiesto",
    "title": "Años bisiestos: lista y comprobador de cualquier año",
    "desc": "Comprueba si un año es bisiesto y por qué, cuál es el próximo y en qué día cae su 29 de febrero, y saca la lista de bisiestos de cualquier rango.",
    "h1": "Años bisiestos",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ano", "type": "number", "label": "Año", "value": 2028, "w": "s", "maxlength": 4},
        {"id": "desde", "type": "number", "label": "Lista desde", "value": 1900, "w": "s", "maxlength": 4},
        {"id": "hasta", "type": "number", "label": "Hasta", "value": 2100, "w": "s", "maxlength": 4},
    ],
    "js": JS,
    "css": ".bis{margin:6px 0 0;max-width:760px;line-height:1.8;font-variant-numeric:tabular-nums}",
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("RAE · Diccionario de la lengua española: bisiesto", "https://dle.rae.es/bisiesto"),
                ("ISO 8601 · calendario gregoriano", "https://www.iso.org/iso-8601-date-and-time-format.html")],
    "related": ["dia-de-la-semana", "edad-exacta", "dias-entre-fechas", "semana/"],
    "tests": [
        ({"ano": "2028"}, {"n.leap": True, "n.next": 2032, "n.prev": 2024, "n.count": 49}),
        ({"ano": "1900"}, {"n.leap": False, "n.next": 1904}),
        ({"ano": "2000"}, {"n.leap": True}),
        ({"ano": "2100", "desde": "2001", "hasta": "2100"}, {"n.leap": False, "n.count": 24}),
        ({"ano": "2027", "desde": "1901", "hasta": "2000"}, {"n.next": 2028, "n.count": 25}),
        ({"ano": "1500"}, {"err": "Año: de 1583 a 9999."}),
    ],
}
