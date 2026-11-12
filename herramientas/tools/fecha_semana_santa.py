"""Fecha de Semana Santa de cualquier año (1583-4099): Easter by the anonymous Gregorian algorithm and every movable
feast that depends on it, plus Orthodox Easter. The English twin (easter_date.py) reuses make_js() with its strings."""
import datetime as dt
import json

from herramientas.tools import _astro as A

L_ES = {
    "lang": "es", "err": "Año entre 1583 y 4099.",
    "wd": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "mon": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "label": "Domingo de Resurrección", "week": "Semana Santa: del ", "to": " al ",
    "feasts": [[-47, "Martes de Carnaval"], [-46, "Miércoles de Ceniza"], [-7, "Domingo de Ramos"], [-3, "Jueves Santo"], [-2, "Viernes Santo"],
               [0, "Domingo de Resurrección", "tot"], [1, "Lunes de Pascua"], [39, "Ascensión (jueves)"], [49, "Pentecostés"], [60, "Corpus Christi (jueves)"]],
    "orth": "Pascua ortodoxa", "same": " (el mismo día)",
    "th": ["Año", "Jueves Santo", "Viernes Santo", "Pascua", "Lunes de Pascua"],
    "next": "Próximos años", "early": "la más temprana posible", "late": "la más tardía posible",
}


def make_js(L):
    return r"""
function (v, H, C) {
""" + A.EASTER_JS + r"""
  var L = """ + json.dumps(L, ensure_ascii=False) + r""";
  var y = v.ano;
  if (!(y >= 1583 && y <= 4099) || Math.floor(y) !== y) return { err: L.err };
  function f(d, wd) {
    var s = d.getUTCDate() + (L.lang === 'es' ? ' de ' + L.mon[d.getUTCMonth()] : ' ' + L.mon[d.getUTCMonth()]);
    return (wd ? L.wd[H.wd(d)] + ' ' : '') + s;
  }
  function sh(d) { return d.getUTCDate() + ' ' + L.mon[d.getUTCMonth()].slice(0, 3); }
  var e = easter(y), o = easterOrth(y), rows = L.feasts.map(function (x) { return [x[1], f(H.add(e, x[0]), true), x[2] || '']; });
  var same = H.iso(o) === H.iso(e);
  rows.push([L.orth, f(o, true) + (same ? L.same : ''), 'z']);
  var md = (e.getUTCMonth() + 1) * 100 + e.getUTCDate(), edge = md === 322 ? ' · ' + L.early : md === 425 ? ' · ' + L.late : '';
  var tb = '<h2 class="cq-h">' + L.next + '</h2><table class="tbl ss"><thead><tr>' + L.th.map(function (t) { return '<th>' + t + '</th>'; }).join('') + '</tr></thead><tbody>';
  for (var k = 1; k <= 10 && y + k <= 4099; k++) {
    var ek = easter(y + k);
    tb += '<tr><td>' + (y + k) + '</td><td>' + sh(H.add(ek, -3)) + '</td><td>' + sh(H.add(ek, -2)) + '</td><td>' + sh(ek) + '</td><td>' + sh(H.add(ek, 1)) + '</td></tr>';
  }
  tb += '</tbody></table>';
  return {
    label: L.label + ' ' + y, big: f(e, false),
    sub: L.week + f(H.add(e, -7), false) + L.to + f(e, false) + edge,
    rows: rows, html: tb,
    n: { easter: H.iso(e), goodfri: H.iso(H.add(e, -2)), orth: H.iso(o), ash: H.iso(H.add(e, -46)) }
  };
}
"""


MES = L_ES["mon"]


def blocks(ctx):
    y0 = 2028
    e = A.easter(y0)
    rows = ""
    for y in range(2027, 2037):
        x = A.easter(y)
        f = lambda d: f"{d.day} {MES[d.month - 1][:3]}"  # noqa: E731
        rows += f"<tr><td>{y}</td><td>{f(x - dt.timedelta(3))}</td><td>{f(x - dt.timedelta(2))}</td><td>{f(x)}</td><td>{f(x + dt.timedelta(1))}</td></tr>"
    return [
        ("Semana Santa de los próximos años", f"""
<p>En {y0} el Domingo de Resurrección es el <b>{e.day} de {MES[e.month - 1]}</b>, así que la Semana Santa va del Domingo de Ramos,
{(e - dt.timedelta(7)).day} de {MES[(e - dt.timedelta(7)).month - 1]}, al {e.day} de {MES[e.month - 1]}; el Jueves Santo es el
{(e - dt.timedelta(3)).day} y el Viernes Santo, el {(e - dt.timedelta(2)).day}. Escribe cualquier año entre 1583 y 4099 para ver
también el Carnaval, la Ascensión, Pentecostés y el Corpus, que se cuentan desde la Pascua.</p>
<table class="tbl"><thead><tr><th>Año</th><th>Jueves Santo</th><th>Viernes Santo</th><th>Pascua</th><th>Lunes de Pascua</th></tr></thead><tbody>{rows}</tbody></table>
<p>El Viernes Santo es festivo nacional todos los años. El Jueves Santo y el Lunes de Pascua dependen de cada comunidad y cambian de un
año a otro: los de 2027 están en <a href="/semana-santa/">Semana Santa 2027</a>.</p>"""),
        ("La regla de la Pascua", """
<p>Desde el Concilio de Nicea (año 325), la Pascua es el domingo siguiente a la primera luna llena que cae el 21 de marzo o
después. Por eso no puede ser antes del 22 de marzo ni después del 25 de abril. La luna que se usa no es la astronómica, sino una luna
«eclesiástica» de tablas, que casi siempre coincide con la real pero puede separarse un día o dos; y el 21 de marzo es una fecha fija,
aunque el equinoccio real caiga el 20.</p>
<p>La reforma gregoriana de 1582 cambió esas tablas, de modo que la fórmula sirve desde 1583. Las iglesias ortodoxas siguen calculando
la Pascua con el calendario juliano: unos años coincide con la católica (2028, 2031, 2034) y otros se separa hasta cinco semanas.</p>"""),
        ("El cálculo paso a paso", """
<p>Se usa el algoritmo gregoriano anónimo, publicado en la revista Nature en 1876 y recogido por Jean Meeus. Para 2027: el resto de
dividir el año entre 19 es a = 13 (la posición en el ciclo lunar de 19 años); el siglo es b = 20 y los años del siglo, c = 27. De ahí
salen d = 5, e = 0, f = 1 y g = 6, y la edad de la luna h = (19·13 + 20 − 5 − 6 + 15) mod 30 = 1. Con i = 6, k = 3, el día de
la semana l = (32 + 0 + 12 − 1 − 3) mod 7 = 5 y m = 0, el número n = h + l − 7m + 114 = 120: el mes es n ÷ 31 = 3 (marzo) y el día,
el resto más uno, 27 + 1 = 28. La Pascua de 2027 es el 28 de marzo.</p>
<p>Las demás fiestas móviles se cuentan desde ese domingo: Miércoles de Ceniza 46 días antes, Domingo de Ramos 7 antes, Ascensión 39
después (en España se celebra el domingo siguiente), Pentecostés 49 y Corpus Christi 60 (jueves), aunque en muchas diócesis la misa
del Corpus pasa al domingo.</p>"""),
    ]


FAQ = [
    ("¿Cuál es la Semana Santa más temprana y la más tardía?",
     "La Pascua puede caer entre el 22 de marzo y el 25 de abril. La próxima en la fecha más tardía es la de 2038 (25 de abril) y la "
     "próxima en la más temprana, la de 2285 (22 de marzo)."),
    ("¿Por qué cambia de fecha cada año?",
     "Porque depende de la luna: es el domingo siguiente a la primera luna llena de primavera, y el ciclo lunar de 29,5 días no encaja con "
     "el año solar."),
    ("¿Cuándo es la Semana Santa de 2028?",
     "Del 9 al 16 de abril de 2028: Jueves Santo el 13, Viernes Santo el 14 y Domingo de Resurrección el 16 de abril."),
    ("¿Cuándo es el Carnaval?",
     "El martes de Carnaval cae 47 días antes del Domingo de Resurrección, el día antes del Miércoles de Ceniza. En 2027 es el 9 de febrero "
     "y en 2028, el 29 de febrero."),
    ("¿La Pascua ortodoxa es el mismo día?",
     "A veces. En 2027 la ortodoxa es el 2 de mayo, cinco semanas después de la católica; en 2028 las dos caen el 16 de abril."),
]

TOOL = {
    "slug": "fecha-semana-santa",
    "lang": "es",
    "twin": "easter-date",
    "cat": "fechas",
    "icon": "egg",
    "order": 30,
    "name": "Fecha de Semana Santa",
    "k": "pascua domingo de resurrección jueves viernes santo carnaval ceniza corpus pentecostés",
    "title": "Fecha de Semana Santa de cualquier año: calcular Pascua",
    "desc": "Calcula cuándo es Semana Santa en cualquier año: Jueves y Viernes Santo, Domingo de Resurrección, Lunes de Pascua, Carnaval, Ascensión y Corpus.",
    "h1": "¿Cuándo es Semana Santa?",
    "updated": "2026-11-12",
    "inputs": [{"id": "ano", "type": "number", "label": "Año", "value": 2028, "w": "s", "maxlength": 4}],
    "js": make_js(L_ES),
    "css": ".ss{max-width:560px;margin-top:8px}.ss td,.ss th{text-align:left}",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Calendario laboral 2027 (BOE): Viernes Santo y festivos autonómicos", "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-21254"),
                ("US Naval Observatory · fecha de la Pascua", "https://aa.usno.navy.mil/faq/easter")],
    "credits": [("Algoritmo gregoriano anónimo (Nature, 1876; Jean Meeus, «Astronomical Algorithms», cap. 8)", "dominio público",
                 "https://en.wikipedia.org/wiki/Date_of_Easter#Anonymous_Gregorian_algorithm")],
    "related": ["calendario-lunar-2027", "dias-entre-fechas", "dia-de-la-semana", "cuenta-atras"],
    "tests": [
        ({"ano": "2027"}, {"n.easter": "2027-03-28", "n.goodfri": "2027-03-26", "n.orth": "2027-05-02", "n.ash": "2027-02-10"}),
        ({"ano": "2028"}, {"n.easter": "2028-04-16", "n.orth": "2028-04-16"}),
        ({"ano": "2038"}, {"n.easter": "2038-04-25"}),
        ({"ano": "2285"}, {"n.easter": "2285-03-22"}),
        ({"ano": "2025"}, {"n.easter": "2025-04-20", "n.orth": "2025-04-20"}),
        ({"ano": "1500"}, {"err": "Año entre 1583 y 4099."}),
    ],
}
