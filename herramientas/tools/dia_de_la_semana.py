"""Día de la semana de cualquier fecha (años 1000-9999): weekday, ISO week, day of the year, the same date in the next
years, and for dates before the Gregorian reform (15 Oct 1582) the weekday if the date is read as Julian. The English
twin (day_of_the_week.py) reuses make_js() with its strings."""
import json

from herramientas.tools import _astro as A

L_ES = {
    "lang": "es", "wd": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "mon": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "e_d": "Elige una fecha.", "e_r": "Fecha fuera de rango (años 1000 a 9999).", "was": " fue", "is": " es", "will": " será",
    "r_wk": "Semana ISO", "r_doy": "Día del año", "r_left": "Quedan del año", "r_leap": "Año bisiesto", "yes": "sí", "no": "no",
    "r_jul": "Si es fecha juliana", "jul_note": "Antes del 15 de octubre de 1582 se usaba el calendario juliano: si la fecha viene de un documento de esa época, el día de la semana es el de la fila «Si es fecha juliana».",
    "next": "La misma fecha en los próximos años", "year": "Año", "day": "Día", "of": " de ", "d1": "día", "dn": "días",
}


def make_js(L):
    return r"""
function (v, H, C) {
  var L = """ + json.dumps(L, ensure_ascii=False) + r""";
""" + A.DATE_JS + r"""
  if (!v.fecha) return { err: L.e_d };
  var d = v.fecha, y = d.getUTCFullYear(), m = d.getUTCMonth() + 1, dd = d.getUTCDate();
  if (y < 1000 || y > 9999) return { err: L.e_r };
  var w = H.wd(d), wk = isoWeek(d), dy = doy(d), left = H.yearDays(y) - dy;
  var now = new Date(), t0 = Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()), verb = d.getTime() < t0 ? L.was : d.getTime() > t0 ? L.will : L.is;
  var rows = [[L.r_wk, wk[1] + L.of + wk[0]], [L.r_doy, nf(dy)], [L.r_left, pl(left, L.d1, L.dn)], [L.r_leap, H.leap(y) ? L.yes : L.no]];
  var jw = null, note = '';
  if (d < new Date(Date.UTC(1582, 9, 15))) { /* Julian date -> Julian Day Number -> weekday (JDN mod 7 = 0 is Monday) */
    var a = Math.floor((14 - m) / 12), yy = y + 4800 - a, mm = m + 12 * a - 3;
    var jdn = dd + Math.floor((153 * mm + 2) / 5) + 365 * yy + Math.floor(yy / 4) - 32083;
    jw = jdn % 7; rows.push([L.r_jul, L.wd[jw], 'tot']); note = L.jul_note;
  }
  var tb = '<h2 class="cq-h">' + L.next + '</h2><table class="tbl dw"><thead><tr><th>' + L.year + '</th><th>' + L.day + '</th></tr></thead><tbody>';
  for (var k = 1, n = 0; n < 10 && y + k <= 9999 && k < 60; k++) {
    var x = addMonths(d, 12 * k);
    if (x.getUTCDate() !== dd) continue; /* 29 Feb only in leap years */
    tb += '<tr><td>' + (y + k) + '</td><td>' + L.wd[H.wd(x)] + '</td></tr>'; n++;
  }
  tb += '</tbody></table>';
  return { label: fdate(d, false) + verb, big: L.wd[w], rows: rows, html: tb, note: note,
    n: { wd: w, week: wk[1], wyear: wk[0], doy: dy, jul: jw } };
}
"""


def blocks(ctx):
    return [
        ("Ejemplos", """
<p>El 6 de diciembre de 1978, día del referéndum de la Constitución, fue <b>miércoles</b>; el 20 de julio de 1969, cuando el Apolo 11
se posó en la Luna, era domingo; y la Nochebuena de 2027 cae en viernes, así que la Navidad será en sábado. Escribe cualquier fecha
entre el año 1000 y el 9999 para saber qué día de la semana fue o será, en qué semana del año cae (según la norma ISO 8601, la que
se usa en Europa) y qué día del año es.</p>
<p>Debajo aparece la misma fecha en los diez años siguientes: útil para saber en qué día caerá tu cumpleaños, un aniversario o una
fiesta local que siempre es el mismo día del mes. Cada año normal la fecha avanza un día de la semana, y dos cuando pasa por un 29 de
febrero.</p>"""),
        ("Cómo se calcula a mano", """
<p>La congruencia de Zeller da el día de la semana con una suma. Para el 6 de diciembre de 1978: día q = 6, mes m = 12, los dos
últimos dígitos del año K = 78 y el siglo J = 19 (enero y febrero se cuentan como meses 13 y 14 del año anterior). Se suman q, la
parte entera de 13·(m + 1)/5 = 33, K = 78, la parte entera de K/4 = 19, la de J/4 = 4 y 5·J = 95: total 235. El resto de dividir
235 entre 7 es 4, y en la fórmula 0 es sábado, 1 domingo, 2 lunes, 3 martes y 4 miércoles. La calculadora hace lo mismo con la
aritmética de fechas del navegador, que da el mismo resultado en todo el rango.</p>"""),
        ("Fechas antiguas: el calendario juliano", """
<p>El calendario gregoriano empezó a usarse en España, Italia y Portugal en 1582: tras el jueves 4 de octubre vino directamente el
viernes 15 de octubre, y se saltaron diez días para corregir el desfase del calendario juliano. Las fechas anteriores que aparecen
en documentos, crónicas o partidas de bautismo están en juliano. Para ellas, la calculadora añade la fila «Si es fecha juliana»
con el día de la semana real de ese día. Otros países cambiaron más tarde: Reino Unido en 1752 y Rusia en 1918.</p>"""),
    ]


FAQ = [
    ("¿Qué día de la semana cae Navidad en 2027?",
     "En sábado: el 25 de diciembre de 2027 es sábado y la Nochebuena, viernes. Año Nuevo de 2028 será también sábado."),
    ("¿Por qué una fecha avanza un día de la semana cada año?",
     "Porque 365 días son 52 semanas y un día. En los años bisiestos, con 366 días, avanza dos a partir del 29 de febrero."),
    ("¿Qué es la semana ISO?",
     "La numeración de semanas de la norma ISO 8601: las semanas empiezan el lunes y la semana 1 es la que contiene el primer jueves del "
     "año. Por eso el 1 de enero de 2027, viernes, pertenece a la semana 53 de 2026."),
    ("¿Sirve para fechas de antes de 1582?",
     "Sí, desde el año 1000. Si la fecha procede de un documento de antes del 15 de octubre de 1582, mira la fila «Si es fecha juliana»."),
    ("¿Se repiten los calendarios?",
     "Sí: un año normal repite el calendario de otro cada 6 u 11 años, y el ciclo completo con bisiestos dura 28 años dentro del mismo "
     "siglo. El calendario de 2027 es igual que el de 2021 y el de 2010."),
]

TOOL = {
    "slug": "dia-de-la-semana",
    "lang": "es",
    "twin": "day-of-the-week",
    "cat": "fechas",
    "icon": "calendar-question",
    "order": 40,
    "name": "Día de la semana",
    "k": "que dia fue que dia cae fecha nacimiento semana iso juliano",
    "title": "¿Qué día de la semana fue o será? Calcula cualquier fecha",
    "desc": "Qué día de la semana fue o será cualquier fecha del año 1000 al 9999, con la semana ISO, el día del año y en qué día cae los próximos años.",
    "h1": "¿Qué día de la semana es?",
    "updated": "2026-11-12",
    "inputs": [{"id": "fecha", "type": "date", "label": "Fecha", "value": "1978-12-06", "min": "1000-01-01", "max": "9999-12-31"}],
    "js": make_js(L_ES),
    "css": ".dw{max-width:300px;margin-top:8px}.dw td,.dw th{text-align:left}",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ISO 8601 · semanas y fechas", "https://www.iso.org/iso-8601-date-and-time-format.html")],
    "credits": [("Congruencia de Zeller (1882) y número de día juliano", "dominio público", "https://en.wikipedia.org/wiki/Zeller%27s_congruence")],
    "related": ["semana/", "edad-exacta", "dias-entre-fechas", "anos-bisiestos"],
    "tests": [
        ({"fecha": "1978-12-06"}, {"n.wd": 2, "n.week": 49, "n.doy": 340, "n.jul": None}),
        ({"fecha": "2027-01-01"}, {"n.wd": 4, "n.week": 53, "n.wyear": 2026}),
        ({"fecha": "1969-07-20"}, {"n.wd": 6, "n.week": 29}),
        ({"fecha": "1582-10-04"}, {"n.jul": 3}),
        ({"fecha": "1582-10-15"}, {"n.wd": 4, "n.jul": None}),
        ({"fecha": ""}, {"err": "Elige una fecha."}),
    ],
}
