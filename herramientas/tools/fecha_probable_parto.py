"""Fecha probable de parto: Naegele's rule (last period + 280 days, adjusted for cycle length) or conception + 266 days,
weeks of pregnancy on a date, trimester and the usual check-up windows of the Spanish prenatal programme.
Informative only: the dating that counts is the first-trimester ultrasound."""
import datetime as dt

MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

JS = r"""
function (v, H, C) {
  var WD = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
  var MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function f(d, wd) { return (wd ? WD[H.wd(d)] + ', ' : '') + d.getUTCDate() + ' de ' + MES[d.getUTCMonth()] + ' de ' + d.getUTCFullYear(); }
  function s(d) { return d.getUTCDate() + ' ' + MES[d.getUTCMonth()].slice(0, 3); }
  if (!v.fur) return { err: v.modo === 'con' ? 'Escribe la fecha de concepción.' : 'Escribe el primer día de la última regla.' };
  var cyc = v.modo === 'con' ? 28 : v.ciclo;
  if (!(cyc >= 21 && cyc <= 45) || Math.floor(cyc) !== cyc) return { err: 'Ciclo: de 21 a 45 días.' };
  /* "day 0" of the pregnancy count = equivalent last period of a 28-day cycle */
  var lmp = v.modo === 'con' ? H.add(v.fur, -14) : H.add(v.fur, cyc - 28), fpp = H.add(lmp, 280);
  var y = v.fur.getUTCFullYear();
  if (y < 1900 || y > 2100) return { err: 'Fecha entre 1900 y 2100.' };
  var rows = [], ga = null, sub = '';
  if (v.hoy) {
    ga = H.diff(lmp, v.hoy);
    if (ga < 0) sub = 'La fecha de cálculo es anterior al inicio del embarazo.';
    else if (ga > 44 * 7) sub = 'Fecha de cálculo posterior a la semana 44.';
    else {
      var w = Math.floor(ga / 7), dd = ga % 7, tri = ga < 98 ? 'primer' : ga < 196 ? 'segundo' : 'tercer';
      sub = 'Semana ' + (w + 1) + ' de embarazo (' + w + ' + ' + dd + ') · ' + tri + ' trimestre · faltan ' + Math.max(0, H.diff(v.hoy, fpp)) + ' días';
      rows.push(['Semanas cumplidas', w + ' semanas y ' + dd + (dd === 1 ? ' día' : ' días'), 'tot']);
    }
  }
  function win(a, b) { return s(H.add(lmp, a * 7)) + ' – ' + s(H.add(lmp, b * 7 + 6)); }
  rows.push(['Concepción aproximada', s(H.add(lmp, 14))], ['Ecografía del 1.er trimestre (11-13)', win(11, 13)],
    ['Fin del 1.er trimestre (13 + 6)', s(H.add(lmp, 97))], ['Ecografía morfológica (18-22)', win(18, 22)],
    ['Cribado de diabetes (24-28)', win(24, 28)], ['Ecografía del 3.er trimestre (32-36)', win(32, 36)],
    ['A término (37 + 0)', s(H.add(lmp, 259))], ['Semana 41 + 0', s(H.add(lmp, 287)), 'z']);
  return { label: 'Fecha probable de parto', big: f(fpp, false), sub: sub || WD[H.wd(fpp)], rows: rows,
    note: 'Orientativo. La fecha que cuenta es la que fija la ecografía del primer trimestre; el calendario de pruebas lo marca tu matrona o tu ginecólogo.',
    n: { fpp: H.iso(fpp), ga: ga, lmp: H.iso(lmp) } };
}
"""


def blocks(ctx):
    f = dt.date(2026, 10, 1)
    p = f + dt.timedelta(280)
    p35 = f + dt.timedelta(287)
    return [
        ("Cómo se calcula la fecha de parto", f"""
<p>Con la regla de Naegele: el primer día de la última regla más 280 días, que son 40 semanas. Si la última regla empezó el 1 de
octubre de 2026, la fecha probable de parto es el <b>{p.day} de {MES[p.month - 1]} de {p.year}</b>. La regla supone un ciclo de 28
días con ovulación el día 14; si tus ciclos son más largos o más cortos, cambia «Ciclo» en «Más opciones» y la fecha se mueve lo
mismo: con ciclos de 35 días, al {p35.day} de {MES[p35.month - 1]}. Si conoces la fecha de concepción, elige «Concepción»: se suman
266 días (38 semanas).</p>
<p>Las semanas de embarazo se cuentan desde la última regla, no desde la concepción: el día de la fecha de parto estás de 40 semanas,
aunque el bebé tenga 38. Por eso «6 + 0» significa seis semanas cumplidas, el primer día de la séptima. El primer trimestre llega hasta
la semana 13 + 6, el segundo hasta la 27 + 6 y el tercero, hasta el parto.</p>"""),
        ("Qué precisión tiene", """
<p>Es una estimación: solo un 4-5 % de los bebés nace el día exacto de la fecha probable, y la mayoría lo hace entre las semanas 38
y 41. Un embarazo es «a término» desde la semana 37 + 0 hasta la 41 + 6. Cuando la regla es irregular o no se recuerda la fecha, la
datación buena es la de la ecografía del primer trimestre, que mide la longitud del embrión (CRL) entre las semanas 11 y 14; si las
dos fechas difieren más de unos días, se usa la de la ecografía.</p>
<p>Las ventanas que muestra la calculadora son las habituales en el seguimiento del embarazo en España: la ecografía y el cribado del
primer trimestre entre las semanas 11 y 13, la ecografía morfológica hacia la 20, el cribado de diabetes gestacional (test de
O'Sullivan) entre la 24 y la 28 y la ecografía del tercer trimestre entre la 32 y la 36. Cada comunidad y cada hospital ajusta su
calendario, así que tómalas como orientación y sigue el que te den en tu centro de salud.</p>"""),
    ]


FAQ = [
    ("¿Cómo calculo de cuántas semanas estoy?",
     "Escribe el primer día de tu última regla: el resultado da las semanas cumplidas a fecha de hoy. Para otra fecha, cámbiala en «Más "
     "opciones»."),
    ("¿Cuánto dura un embarazo?",
     "Unos 280 días (40 semanas) desde la última regla, o 266 días (38 semanas) desde la concepción. Un parto entre las semanas 37 y 42 se "
     "considera a término."),
    ("¿Por qué la ecografía da otra fecha?",
     "Porque mide el tamaño del embrión y no depende de recordar la regla ni de la duración del ciclo. Si difiere, vale la de la ecografía "
     "del primer trimestre."),
    ("¿Y si mis ciclos son irregulares?",
     "La regla de Naegele es poco fiable con ciclos irregulares. Usa la fecha como aproximación y espera a la datación por ecografía."),
    ("¿Sirve para embarazos por FIV?",
     "Como aproximación: con la fecha de la punción o de la inseminación elige «Concepción». Tu clínica te dará la fecha exacta según el día "
     "del embrión transferido."),
]

TOOL = {
    "slug": "fecha-probable-parto",
    "lang": "es",
    "cat": "fechas",
    "icon": "baby-carriage",
    "order": 60,
    "name": "Fecha probable de parto",
    "k": "fpp semanas de embarazo calculadora embarazo naegele última regla trimestre",
    "title": "Calculadora de embarazo: fecha probable de parto y semanas",
    "desc": "Calcula la fecha probable de parto desde la última regla o la concepción, de cuántas semanas estás, el trimestre y las ecografías habituales.",
    "h1": "Fecha probable de parto",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "modo", "type": "seg", "label": "Desde", "value": "fur", "options": [("fur", "Última regla"), ("con", "Concepción")]},
        {"id": "fur", "type": "date", "label": "Fecha", "value": "2026-10-01", "min": "1900-01-01", "max": "2100-12-31"},
        {"id": "ciclo", "type": "number", "label": "Ciclo", "value": 28, "unit": "días", "w": "s", "more": True, "show": ("modo", ["fur"])},
        {"id": "hoy", "type": "date", "label": "A fecha de", "value": "2026-11-12", "today": True, "more": True, "min": "1900-01-01", "max": "2100-12-31"},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Ministerio de Sanidad · Guía de práctica clínica de atención en el embarazo y puerperio", "https://www.sanidad.gob.es/organizacion/sns/planCalidadSNS/0Guiaatembarazo.htm")],
    "credits": [("Regla de Naegele (1812)", "dominio público", "https://en.wikipedia.org/wiki/Naegele%27s_rule")],
    "related": ["cuenta-atras", "dias-entre-fechas", "edad-exacta", "permiso-nacimiento"],
    "tests": [
        ({"fur": "2026-10-01", "hoy": "2026-11-12"}, {"n.fpp": "2027-07-08", "n.ga": 42}),
        ({"fur": "2026-10-01", "ciclo": "35", "hoy": "2026-11-12"}, {"n.fpp": "2027-07-15", "n.ga": 35}),
        ({"modo": "con", "fur": "2026-10-15", "hoy": "2026-11-12"}, {"n.fpp": "2027-07-08"}),
        ({"fur": "2026-03-02", "hoy": "2026-11-12"}, {"n.fpp": "2026-12-07", "n.ga": 255}),
        ({"fur": "2026-10-01", "ciclo": "60"}, {"err": "Ciclo: de 21 a 45 días."}),
        ({"fur": ""}, {"err": "Escribe el primer día de la última regla."}),
    ],
}
