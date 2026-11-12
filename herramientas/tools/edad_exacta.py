"""Edad exacta: age in years, months and days on any date, total months/weeks/days lived, next birthday, weekday of
birth, next round-thousand-days milestone. The English twin (age_calculator.py) reuses make_js() with its strings."""
import datetime as dt
import json

from herramientas.tools import _astro as A

L_ES = {
    "lang": "es", "wd": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "mon": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "e_b": "Escribe la fecha de nacimiento.", "e_t": "Elige la fecha en la que calcular la edad.", "e_o": "La fecha de nacimiento es posterior.",
    "e_r": "Fecha fuera de rango (años 1000 a 9999).",
    "age": "Edad", "d1": "día", "dn": "días", "w1": "semana", "wn": "semanas", "m1": "mes", "mn": "meses", "y1": "año", "yn": "años", "and": " y ",
    "r_m": "En meses", "r_w": "En semanas", "r_d": "Días vividos", "r_born": "Naciste un", "r_next": "Próximo cumpleaños",
    "r_mile": "Cumplirás", "r_18": "Mayoría de edad (18)", "today": "hoy", "in": "dentro de ", "turns": "cumple ",
    "bday": "¡Feliz cumpleaños!", "leap": "Nacido un 29 de febrero: en los años no bisiestos el cumpleaños se cuenta el 28 de febrero.",
}


def make_js(L):
    return r"""
function (v, H, C) {
  var L = """ + json.dumps(L, ensure_ascii=False) + r""";
""" + A.DATE_JS + r"""
  function ok(d) { return d.getUTCFullYear() >= 1000 && d.getUTCFullYear() <= 9999; }
  if (!v.nac) return { err: L.e_b };
  if (!v.hoy) return { err: L.e_t };
  if (!ok(v.nac) || !ok(v.hoy)) return { err: L.e_r };
  if (v.nac > v.hoy) return { err: L.e_o };
  var q = ymd(v.nac, v.hoy), days = H.diff(v.nac, v.hoy), parts = [];
  if (q[0] || (!q[1] && !q[2])) parts.push(pl(q[0], L.y1, L.yn));
  if (q[1]) parts.push(pl(q[1], L.m1, L.mn));
  if (q[2]) parts.push(pl(q[2], L.d1, L.dn));
  var s = parts.length > 1 ? parts.slice(0, -1).join(', ') + L.and + parts[parts.length - 1] : parts[0];
  var nb = addMonths(v.nac, (q[0] + 1) * 12), toB = H.diff(v.hoy, nb), isB = q[1] === 0 && q[2] === 0 && q[0] > 0;
  var mile = (Math.floor(days / 1000) + 1) * 1000, md = H.add(v.nac, mile);
  var rows = [[L.r_m, nf(q[3])], [L.r_w, nf(Math.floor(days / 7)) + (days % 7 ? L.and + pl(days % 7, L.d1, L.dn) : '')], [L.r_d, nf(days), 'tot'],
    [L.r_born, L.wd[H.wd(v.nac)]],
    [L.r_next, fdate(nb, true) + ' · ' + L.turns + (q[0] + 1) + ' · ' + L['in'] + pl(toB, L.d1, L.dn)],
    [L.r_mile + ' ' + nf(mile) + ' ' + L.dn, fdate(md, true)]];
  if (q[0] < 18) rows.push([L.r_18, fdate(addMonths(v.nac, 216), true)]);
  var leap = v.nac.getUTCMonth() === 1 && v.nac.getUTCDate() === 29;
  return { label: L.age, big: pl(q[0], L.y1, L.yn), sub: (isB ? L.bday + ' · ' : '') + s, rows: rows, note: leap ? L.leap : '',
    n: { y: q[0], m: q[1], d: q[2], months: q[3], days: days, next: H.iso(nb), toNext: toB, wd: H.wd(v.nac) } };
}
"""


MES = L_ES["mon"]


def blocks(ctx):
    b, t = dt.date(1990, 5, 15), dt.date(2026, 11, 12)
    days = (t - b).days
    return [
        ("Cómo se calcula la edad", f"""
<p>Una persona nacida el 15 de mayo de 1990 tiene, el 12 de noviembre de 2026, <b>36 años, 5 meses y 28 días</b>: 36 años completos
hasta el 15 de mayo de 2026, 5 meses hasta el 15 de octubre y 28 días más. En total lleva {ctx.num(days)} días vividos, unas
{ctx.num(days // 7)} semanas, y nació en martes. La calculadora cuenta primero los años enteros, luego los meses enteros y al final los
días sueltos, igual que se cuenta la edad de palabra.</p>
<p>Por defecto la edad se calcula a fecha de hoy, pero puedes poner cualquier otra en «En la fecha»: la edad que tenía alguien en una
fecha del pasado, la que tendrá el día de un viaje o un examen, o la de un familiar al nacer otro. También muestra cuándo es el próximo
cumpleaños, cuántos días faltan y en qué día de la semana cae.</p>"""),
        ("Edad legal y 29 de febrero", """
<p>El artículo 315 del Código Civil dice que la mayoría de edad empieza a los 18 años cumplidos y que, para computarla, se incluye
completo el día del nacimiento: quien nació el 15 de mayo de 2009 es mayor de edad desde el primer minuto del 15 de mayo de 2027,
sin esperar a la hora en que nació. Si la persona aún no tiene 18 años, el resultado incluye la fecha en que los cumplirá.</p>
<p>Los nacidos un 29 de febrero celebran su cumpleaños exacto solo en los años bisiestos. En el resto, esta calculadora cuenta el
año cumplido el 28 de febrero, el último día del mes, como hace el artículo 5 del Código Civil con los plazos de años cuando el mes
final no tiene ese día. Hay quien lo celebra el 1 de marzo; la edad en días es la misma en los dos casos.</p>"""),
    ]


FAQ = [
    ("¿Cuántos días he vivido?",
     "Escribe tu fecha de nacimiento: «Días vividos» cuenta los días desde ese día hasta hoy, sin contar el del nacimiento. A los 30 años "
     "son unos 10.957 días, según cuántos 29 de febrero hayan caído."),
    ("¿Cuándo cumpliré 10.000 días?",
     "A los 27 años, 4 meses y entre 15 y 18 días, según la fecha de nacimiento. La fila «Cumplirás» te da la fecha exacta del siguiente millar de días."),
    ("¿Qué edad tenía en una fecha concreta?",
     "Cambia «En la fecha» por esa fecha. Sirve para saber la edad en un viaje, al casarte o en el nacimiento de un hermano."),
    ("¿Cómo se cuenta la edad de los nacidos el 29 de febrero?",
     "En años no bisiestos, esta calculadora suma el año el 28 de febrero, el último día del mes. La ley no fija un día especial y hay "
     "quien lo celebra el 1 de marzo."),
    ("¿Desde qué día se es mayor de edad?",
     "Desde el día en que se cumplen 18 años, contado entero: el art. 315 del Código Civil incluye completo el día del nacimiento."),
]

INPUTS_ES = [
    {"id": "nac", "type": "date", "label": "Nacimiento", "value": "1990-05-15", "min": "1000-01-01", "max": "9999-12-31"},
    {"id": "hoy", "type": "date", "label": "En la fecha", "value": "2026-11-12", "today": True, "min": "1000-01-01", "max": "9999-12-31"},
]

TOOL = {
    "slug": "edad-exacta",
    "lang": "es",
    "twin": "age-calculator",
    "cat": "fechas",
    "icon": "cake",
    "order": 20,
    "name": "Edad exacta",
    "k": "calcular edad años meses días vividos cumpleaños fecha de nacimiento",
    "title": "Calcular edad exacta: años, meses y días vividos",
    "desc": "Calcula tu edad exacta en años, meses y días desde la fecha de nacimiento, los días vividos, cuánto falta para tu cumpleaños y en qué día naciste.",
    "h1": "Calcular la edad exacta",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": make_js(L_ES),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Código Civil, art. 315 (mayoría de edad)", "https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763#a315"),
                ("Código Civil, art. 5 (cómputo por años)", "https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763#a5")],
    "related": ["dias-entre-fechas", "dia-de-la-semana", "cuenta-atras", "antiguedad-empresa"],
    "tests": [
        ({"nac": "1990-05-15", "hoy": "2026-11-12"}, {"n.y": 36, "n.m": 5, "n.d": 28, "n.days": 13330, "n.wd": 1, "n.next": "2027-05-15", "n.toNext": 184}),
        ({"nac": "2000-02-29", "hoy": "2027-02-28"}, {"n.y": 27, "n.m": 0, "n.d": 0}),
        ({"nac": "2000-02-29", "hoy": "2027-02-27"}, {"n.y": 26, "n.m": 11, "n.d": 29}),
        ({"nac": "2026-11-12", "hoy": "2026-11-12"}, {"n.y": 0, "n.days": 0}),
        ({"nac": "2027-01-01", "hoy": "2026-11-12"}, {"err": "La fecha de nacimiento es posterior."}),
    ],
}
