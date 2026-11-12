"""Días entre fechas: calendar days between two dates (and in weeks, months, years, weekdays, weekends), or a date plus
or minus N days. The English twin (days_between_dates.py) reuses make_js() with its strings."""
import datetime as dt
import json

from herramientas.tools import _astro as A

L_ES = {
    "lang": "es", "wd": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "mon": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "e_a": "Elige la fecha de inicio.", "e_b": "Elige la fecha final.", "e_n": "Días: un número entero de 0 a 3.000.000.",
    "e_r": "Fecha fuera de rango (años 1000 a 9999).",
    "days": "Días entre las fechas", "past": "La fecha final es anterior: el resultado va hacia atrás.",
    "d1": "día", "dn": "días", "w1": "semana", "wn": "semanas", "m1": "mes", "mn": "meses", "y1": "año", "yn": "años", "and": " y ",
    "r_w": "En semanas", "r_m": "En meses", "r_y": "En años, meses y días", "r_wd": "De lunes a viernes", "r_we": "Sábados y domingos",
    "r_h": "En horas", "r_res": "Fecha resultante", "res": "Fecha resultante", "after": " después de ", "before": " antes de ",
    "r_wk": "Semana ISO", "r_doy": "Día del año", "of": " de ",
    "note": "Sin festivos: para días hábiles usa la calculadora de días hábiles.",
}


def make_js(L):
    return r"""
function (v, H, C) {
  var L = """ + json.dumps(L, ensure_ascii=False) + r""";
""" + A.DATE_JS + r"""
  function ok(d) { return d && d.getUTCFullYear() >= 1000 && d.getUTCFullYear() <= 9999; }
  if (!v.a) return { err: L.e_a };
  if (!ok(v.a)) return { err: L.e_r };
  if (v.modo === 'sumar') {
    var n = v.n;
    if (!(n >= 0 && n <= 3e6) || Math.floor(n) !== n) return { err: L.e_n };
    var s = v.op === 'menos' ? -1 : 1, r = H.add(v.a, s * n);
    if (!ok(r)) return { err: L.e_r };
    var w = isoWeek(r);
    return { label: L.res, big: fdate(r, true), sub: pl(n, L.d1, L.dn) + (s > 0 ? L.after : L.before) + fdate(v.a, false),
      rows: [[L.r_wk, w[1] + L.of + w[0]], [L.r_doy, nf(doy(r)) + ' / ' + H.yearDays(r.getUTCFullYear())]],
      n: { date: H.iso(r), wd: H.wd(r), week: w[1] } };
  }
  if (!v.b) return { err: L.e_b };
  if (!ok(v.b)) return { err: L.e_r };
  var a = v.a, b = v.b, neg = b < a;
  if (neg) { var t = a; a = b; b = t; }
  var days = H.diff(a, b) + (v.ambos ? 1 : 0), end = v.ambos ? H.add(b, 1) : b;
  /* weekdays / weekend days in the counted span: (a, b], or [a, b] with both ends */
  var first = v.ambos ? a : H.add(a, 1), full = Math.floor(days / 7), we = full * 2, k;
  for (k = 0; k < days % 7; k++) if (H.wd(H.add(first, full * 7 + k)) >= 5) we++;
  var q = ymd(a, end), parts = [];
  if (q[0]) parts.push(pl(q[0], L.y1, L.yn));
  if (q[1]) parts.push(pl(q[1], L.m1, L.mn));
  if (q[2] || !parts.length) parts.push(pl(q[2], L.d1, L.dn));
  var ymdS = parts.length > 1 ? parts.slice(0, -1).join(', ') + L.and + parts[parts.length - 1] : parts[0];
  var wk = Math.floor(days / 7), wr = days % 7;
  return {
    label: L.days, big: nf(days) + ' ' + (days === 1 ? L.d1 : L.dn),
    sub: fdate(v.a, true) + ' → ' + fdate(v.b, true),
    rows: [[L.r_w, pl(wk, L.w1, L.wn) + (wr ? L.and + pl(wr, L.d1, L.dn) : '')],
      [L.r_m, q[3] ? pl(q[3], L.m1, L.mn) + (q[2] ? L.and + pl(q[2], L.d1, L.dn) : '') : pl(q[2], L.d1, L.dn)],
      [L.r_y, ymdS], [L.r_wd, nf(days - we)], [L.r_we, nf(we)], [L.r_h, nf(days * 24)]],
    note: (neg ? L.past + ' ' : '') + L.note,
    n: { days: neg ? -days : days, y: q[0], m: q[1], d: q[2], months: q[3], we: we, wd: days - we }
  };
}
"""


def inputs(L, lab):
    return [
        {"id": "modo", "type": "seg", "label": lab[0], "value": "entre", "options": [("entre", lab[1]), ("sumar", lab[2])]},
        {"id": "a", "type": "date", "label": lab[3], "value": "2026-11-12", "today": True, "min": "1000-01-01", "max": "9999-12-31"},
        {"id": "b", "type": "date", "label": lab[4], "value": "2027-12-31", "min": "1000-01-01", "max": "9999-12-31", "show": ("modo", ["entre"])},
        {"id": "ambos", "type": "check", "label": lab[5], "value": False, "show": ("modo", ["entre"])},
        {"id": "op", "type": "seg", "label": lab[6], "value": "mas", "options": [("mas", "+"), ("menos", "−")], "show": ("modo", ["sumar"])},
        {"id": "n", "type": "number", "label": lab[7], "value": 90, "unit": lab[8], "w": "s", "show": ("modo", ["sumar"])},
    ]


def blocks(ctx):
    a, b = dt.date(2026, 11, 12), dt.date(2027, 12, 31)
    d = (b - a).days
    n90 = a + dt.timedelta(90)
    wd = L_ES["wd"]
    mon = L_ES["mon"]
    return [
        ("Cómo se cuentan los días", f"""
<p>Del 12 de noviembre de 2026 al 31 de diciembre de 2027 hay <b>{d} días</b>: es la resta de las dos fechas, que no cuenta el día de
inicio y sí el final. Si quieres contar los dos (por ejemplo, los días de un viaje o de una estancia que incluye la llegada y la
salida), marca «Contar ambos días» y el resultado sube a {d + 1}. Debajo aparece lo mismo en semanas, en meses y en años, meses y
días, y cuántos de esos días caen de lunes a viernes o en fin de semana.</p>
<p>Para sumar o restar, cambia a «Sumar o restar»: 90 días después del 12 de noviembre de 2026 es el {wd[n90.weekday()]}
{n90.day} de {mon[n90.month - 1]} de {n90.year}. Sirve para fechas de caducidad, periodos de prueba, devoluciones o cualquier plazo
expresado en días naturales.</p>"""),
        ("Plazos legales en días naturales", """
<p>El artículo 5 del Código Civil fija la regla general: en los plazos señalados por días, a contar desde uno determinado, ese día
queda fuera del cómputo, que empieza al día siguiente. Es justo lo que hace la resta. Y si el plazo se fija en meses o años, se cuenta
«de fecha a fecha»; cuando el mes final no tiene ese día (un plazo de un mes desde el 31 de enero), vence el último día del mes. Esta
calculadora cuenta así los meses: del 31 de enero al 28 de febrero de 2027 hay un mes justo.</p>
<p>Ojo con los plazos administrativos y judiciales: la Ley 39/2015 de procedimiento administrativo cuenta en días hábiles, sin
sábados, domingos ni festivos, y en los juzgados agosto tampoco cuenta. Para esos plazos usa la
<a href="/dias-habiles/">calculadora de días hábiles</a>, que descuenta los festivos de tu comunidad y tu municipio.</p>"""),
    ]


FAQ = [
    ("¿Cuántos días faltan para el 31 de diciembre de 2027?",
     "Desde el 12 de noviembre de 2026, 414 días. Pon la fecha de hoy en «Desde» (sale por defecto) para verlo desde cualquier día."),
    ("¿Se cuenta el primer día?",
     "No, en la cuenta normal y en los plazos legales (art. 5 del Código Civil) el día de inicio queda fuera. Si necesitas contarlo, marca "
     "«Contar ambos días»."),
    ("¿Cuántos días tiene un año?",
     "365, o 366 en los bisiestos como 2028. Por eso «un año» desde una fecha no siempre son 365 días: del 1 de marzo de 2027 al 1 de marzo "
     "de 2028 hay 366."),
    ("¿Cómo calculo qué fecha será dentro de 100 días?",
     "Elige «Sumar o restar», deja la fecha de hoy, escribe 100 y pulsa +. El resultado muestra el día de la semana y la semana del año."),
    ("¿Tiene en cuenta los festivos?",
     "No: cuenta días naturales y separa los de lunes a viernes. Para quitar los festivos nacionales, autonómicos y locales, usa la "
     "calculadora de días hábiles."),
]

TOOL = {
    "slug": "dias-entre-fechas",
    "lang": "es",
    "twin": "days-between-dates",
    "cat": "fechas",
    "icon": "calendar-due",
    "order": 10,
    "name": "Días entre fechas",
    "k": "cuantos dias faltan contar dias naturales sumar restar dias a una fecha plazo",
    "title": "Días entre dos fechas: calcular y sumar o restar días",
    "desc": "Cuenta los días naturales entre dos fechas, en semanas, meses y años, o suma y resta días a una fecha. Con días de lunes a viernes y fines de semana.",
    "h1": "Días entre fechas",
    "updated": "2026-11-12",
    "inputs": inputs(L_ES, ["Calcular", "Entre fechas", "Sumar o restar", "Desde", "Hasta", "Contar ambos días", "Operación", "Días", "días"]),
    "js": make_js(L_ES),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Código Civil, art. 5 (cómputo de plazos)", "https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763#a5"),
                ("Ley 39/2015, art. 30 (días hábiles)", "https://www.boe.es/buscar/act.php?id=BOE-A-2015-10565#a30")],
    "related": ["dias-habiles/", "edad-exacta", "cuenta-atras", "dia-de-la-semana"],
    "tests": [
        ({"a": "2026-11-12", "b": "2027-12-31"}, {"n.days": 414, "n.y": 1, "n.m": 1, "n.d": 19}),
        ({"a": "2027-01-01", "b": "2027-12-31", "ambos": "1"}, {"n.days": 365, "n.y": 1, "n.m": 0, "n.d": 0, "n.we": 104}),
        ({"a": "2027-01-31", "b": "2027-02-28"}, {"n.days": 28, "n.months": 1, "n.d": 0}),
        ({"a": "2027-03-01", "b": "2027-02-01"}, {"n.days": -28}),
        ({"modo": "sumar", "a": "2026-11-12", "n": "90"}, {"n.date": "2027-02-10", "n.wd": 2}),
        ({"modo": "sumar", "a": "2027-03-01", "op": "menos", "n": "1"}, {"n.date": "2027-02-28"}),
        ({"modo": "sumar", "a": "2027-03-01", "n": "-5"}, {"err": "Días: un número entero de 0 a 3.000.000."}),
    ],
}
