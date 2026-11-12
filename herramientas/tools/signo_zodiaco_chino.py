"""Signo del zodiaco chino por fecha de nacimiento: animal, element and yin/yang of the lunar year, using the real
Chinese New Year date of each year 1901-2100 (computed at build time by _astro.cny, checked against the Hong Kong
Observatory tables), so people born in January or early February get the previous year's sign."""
import datetime as dt

from herramientas.tools import _astro as A

YEARS = range(1901, 2101)
CNY = {y: A.cny(y) for y in YEARS}
ANIM = ["Rata", "Buey", "Tigre", "Conejo", "Dragón", "Serpiente", "Caballo", "Cabra", "Mono", "Gallo", "Perro", "Cerdo"]
ELEM = ["Madera", "Fuego", "Tierra", "Metal", "Agua"]
MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def sign(y):
    return ANIM[(y - 4) % 12], ELEM[((y - 4) % 10) // 2], "yang" if (y - 4) % 2 == 0 else "yin"


JS = r"""
function (v, H, C) {
  var A = ['Rata', 'Buey', 'Tigre', 'Conejo', 'Dragón', 'Serpiente', 'Caballo', 'Cabra', 'Mono', 'Gallo', 'Perro', 'Cerdo'];
  var E = ['Madera', 'Fuego', 'Tierra', 'Metal', 'Agua'];
  var MES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  if (!v.fecha) return { err: 'Escribe la fecha de nacimiento.' };
  var d = v.fecha, y = d.getUTCFullYear();
  function ny(yy) { var s = C.d.cny[yy]; return s ? new Date(Date.UTC(yy, +s.slice(0, 2) - 1, +s.slice(2))) : null; }
  var first = ny(y);
  if (!first || y > 2100 || (y === 1901 && d < first)) return { err: 'Fecha entre el 19 de febrero de 1901 y 2100.' };
  var ly = d < first ? y - 1 : y, start = ny(ly), next = ny(ly + 1), a = (ly - 4) % 12, st = (ly - 4) % 10;
  var an = A[a], el = E[Math.floor(st / 2)], yy = st % 2 ? 'yin' : 'yang';
  function f(x) { return x.getUTCDate() + ' ' + MES[x.getUTCMonth()] + ' ' + x.getUTCFullYear(); }
  var trine = [a, (a + 4) % 12, (a + 8) % 12].sort(function (p, q) { return p - q; }).filter(function (i) { return i !== a; }).map(function (i) { return A[i]; });
  var years = [];
  for (var k = ly - 60; k <= ly + 36; k += 12) if (k >= 1901 && k <= 2100) years.push(k === ly ? '<b>' + k + '</b>' : k);
  var rows = [['Animal', an, 'tot'], ['Elemento', el], ['Polaridad', yy],
    ['Año lunar', f(start) + ' – ' + (next ? f(H.add(next, -1)) : '…')], ['Afines (trígono)', trine.join(' y ')],
    ['Opuesto', A[(a + 6) % 12]], ['Años del ' + an, years.join(' · ')]];
  return { label: 'Signo del zodiaco chino', big: an, sub: an + ' de ' + el + ' · ' + yy, rows: rows,
    note: ly < y ? 'Naciste antes del Año Nuevo chino de ' + y + ' (' + f(first) + '): tu signo es el del año lunar ' + ly + '.' : '',
    n: { animal: an, elem: el, yy: yy, ly: ly, start: H.iso(start) } };
}
"""


def blocks(ctx):
    s27, e27 = CNY[2027], CNY[2028] - dt.timedelta(1)
    rows = ""
    for y in range(2020, 2032):
        a, e, p = sign(y)
        c = CNY[y]
        rows += f"<tr><td>{y}</td><td>{a} de {e}</td><td>{c.day} {MES[c.month - 1][:3]}</td></tr>"
    c90 = CNY[1990]
    return [
        ("El año de la Cabra de Fuego", f"""
<p>El Año Nuevo chino de 2027 cae el <b>{s27.day} de {MES[s27.month - 1]}</b> y empieza el año de la <b>Cabra de Fuego</b>, que dura
hasta el {e27.day} de {MES[e27.month - 1]} de {e27.year}. Quien nazca en enero de 2027 o los primeros días de febrero, antes del día 6,
es todavía Caballo, el signo de 2026. Ese es el error más común de las tablas que van por años: el año chino no empieza el 1 de
enero, sino con una luna nueva que cae entre el 21 de enero y el 20 de febrero, casi siempre la segunda después del solsticio de
invierno.</p>
<table class="tbl"><thead><tr><th>Año</th><th>Signo</th><th>Empieza</th></tr></thead><tbody>{rows}</tbody></table>
<p>Por ejemplo, alguien nacido el 15 de enero de 1990 es Serpiente de Tierra, el signo de 1989, porque el año del Caballo de Metal
no empezó hasta el {c90.day} de {MES[c90.month - 1]} de 1990.</p>"""),
        ("Animales, elementos y yin-yang", """
<p>El ciclo combina 12 animales (Rata, Buey, Tigre, Conejo, Dragón, Serpiente, Caballo, Cabra, Mono, Gallo, Perro y Cerdo) con 10
«troncos celestes» que se agrupan de dos en dos en cinco elementos: Madera, Fuego, Tierra, Metal y Agua. Cada elemento dura dos
años seguidos, el primero yang y el segundo yin. Como 12 y 10 solo coinciden cada 60 años, la misma combinación, por ejemplo Caballo
de Metal, vuelve cada seis décadas: 1930, 1990 y 2050.</p>
<p>La tradición agrupa los animales en cuatro trígonos de afinidad (Rata, Dragón y Mono; Buey, Serpiente y Gallo; Tigre, Caballo
y Perro; Conejo, Cabra y Cerdo) y enfrenta a cada uno con el que está seis puestos más allá. En algunos países cambian los nombres:
la Cabra es también Oveja, el Buey es Búfalo en Vietnam, que además pone al Gato en lugar del Conejo, y el Cerdo es Jabalí en
Japón.</p>"""),
        ("De dónde salen las fechas", """
<p>Las fechas del Año Nuevo chino se calculan con las reglas del calendario chino actual, en hora de China (UTC+8): el mes 11 es la
lunación que contiene el solsticio de diciembre, cada mes empieza el día de la luna nueva, y cuando entre dos meses 11 hay 13 lunas
nuevas, el primer mes sin término solar principal es bisiesto. Con las fases lunares de Jean Meeus y la posición del Sol, el
resultado coincide con las tablas del Observatorio de Hong Kong en todos los años comprobados, incluidos los casos raros como 1985
(20 de febrero) y 2034 (19 de febrero, tras un mes bisiesto).</p>"""),
    ]


FAQ = [
    ("¿Qué animal es 2027 en el horóscopo chino?",
     "La Cabra de Fuego (yin), del 6 de febrero de 2027 al 25 de enero de 2028. El 26 de enero de 2028 empieza el año del Mono de Tierra."),
    ("Nací en enero, ¿qué signo chino soy?",
     "Casi siempre el del año anterior, porque el Año Nuevo chino cae entre el 21 de enero y el 20 de febrero. Escribe tu fecha completa "
     "y la calculadora lo comprueba."),
    ("¿Cuándo es el Año Nuevo chino 2026?",
     "El 17 de febrero de 2026 empezó el año del Caballo de Fuego, que termina el 5 de febrero de 2027."),
    ("¿Qué es el elemento de mi signo?",
     "Uno de los cinco elementos (Madera, Fuego, Tierra, Metal y Agua) que cambia cada dos años. Depende de la última cifra del año lunar: "
     "0-1 Metal, 2-3 Agua, 4-5 Madera, 6-7 Fuego y 8-9 Tierra."),
    ("¿Los signos chinos predicen el carácter?",
     "Es una tradición cultural, no una ciencia. La calculadora te da el signo y su combinación según el calendario chino; las "
     "interpretaciones son parte del folclore."),
]

TOOL = {
    "slug": "signo-zodiaco-chino",
    "lang": "es",
    "cat": "fechas",
    "icon": "yin-yang",
    "order": 70,
    "name": "Horóscopo chino",
    "k": "signo chino zodiaco chino animal año nuevo chino elemento",
    "title": "Horóscopo chino: qué signo soy según mi fecha de nacimiento",
    "desc": "Calcula tu signo del zodiaco chino con la fecha real del Año Nuevo chino de cada año: animal, elemento, yin o yang y signos afines.",
    "h1": "¿Qué signo del horóscopo chino soy?",
    "updated": "2026-11-12",
    "inputs": [{"id": "fecha", "type": "date", "label": "Nacimiento", "value": "1990-05-15", "min": "1901-02-19", "max": "2100-12-31"}],
    "data": {"cny": {str(y): f"{d.month:02d}{d.day:02d}" for y, d in CNY.items()}},
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Hong Kong Observatory · Gregorian-Lunar Calendar Conversion Table", "https://www.hko.gov.hk/en/gts/time/conversion.htm")],
    "credits": [("Jean Meeus, «Astronomical Algorithms» (fases lunares y posición del Sol, fórmulas reimplementadas)", "fórmula publicada",
                 "https://en.wikipedia.org/wiki/Jean_Meeus")],
    "related": ["calendario-lunar-2027", "edad-exacta", "dia-de-la-semana", "anos-bisiestos"],
    "tests": [
        ({"fecha": "1990-05-15"}, {"n.animal": "Caballo", "n.elem": "Metal", "n.yy": "yang", "n.start": "1990-01-27"}),
        ({"fecha": "1990-01-15"}, {"n.animal": "Serpiente", "n.elem": "Tierra", "n.ly": 1989}),
        ({"fecha": "2027-02-06"}, {"n.animal": "Cabra", "n.elem": "Fuego", "n.yy": "yin"}),
        ({"fecha": "2027-02-05"}, {"n.animal": "Caballo", "n.ly": 2026}),
        ({"fecha": "1985-02-19"}, {"n.animal": "Rata", "n.ly": 1984}),
        ({"fecha": "1900-06-01"}, {"err": "Fecha entre el 19 de febrero de 1901 y 2100."}),
    ],
}
