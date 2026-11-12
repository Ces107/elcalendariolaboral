"""Antigüedad en la empresa: years, months and days between the start date and a date; trienios, quinquenios, sexenios."""

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
CC = "https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763"

JS = r"""
function (v, H, C) {
  function addM(d, n) { var y = d.getUTCFullYear(), m = d.getUTCMonth() + n, ty = y + Math.floor(m / 12), tm = ((m % 12) + 12) % 12;
    return new Date(Date.UTC(ty, tm, Math.min(d.getUTCDate(), H.monthDays(ty, tm + 1)))); }
  function fd(d) { return ('0' + d.getUTCDate()).slice(-2) + '/' + ('0' + (d.getUTCMonth() + 1)).slice(-2) + '/' + d.getUTCFullYear(); }
  var a = v.alta, b = v.hasta;
  if (!a) return { err: 'Elige la fecha de alta.' };
  if (!b) return { err: 'Elige la fecha final.' };
  var end = v.incl ? H.add(b, 1) : b; /* counting the last day: the period runs to the end of that day */
  if (end <= a) return { err: 'La fecha final tiene que ser posterior a la de alta.' };
  var k = 0;
  while (addM(a, k + 1) <= end) k++;
  var y = Math.floor(k / 12), m = k % 12, d = H.diff(addM(a, k), end), days = H.diff(a, end);
  var ind = y + (m + (d > 0 ? 1 : 0)) / 12; /* art. 56 ET: periods under a year prorated by months (a started month counts) */
  function per(n) { var c = Math.floor(k / (12 * n)); return [c, addM(a, 12 * n * (c + 1))]; }
  var t3 = per(3), t5 = per(5), t6 = per(6);
  var s = y + ' ' + H.plural(y, 'año', 'años') + ', ' + m + ' ' + H.plural(m, 'mes', 'meses') + ' y ' + d + ' ' + H.plural(d, 'día', 'días');
  return {
    label: 'Antigüedad', big: s,
    sub: H.num(days, 0) + ' días naturales · desde el ' + fd(a),
    rows: [
      ['Trienios', t3[0] + ' · el siguiente, ' + fd(t3[1])],
      ['Quinquenios', t5[0] + ' · el siguiente, ' + fd(t5[1])],
      ['Sexenios', t6[0] + ' · el siguiente, ' + fd(t6[1])],
      ['Años para indemnización', H.num(H.r2(ind), 2), 'sub'],
      ['Meses completos', String(k), 'sub']
    ],
    n: { y: y, m: m, d: d, days: days, k: k, t3: t3[0], next3: H.iso(t3[1]), ind: H.r2(ind) }
  };
}
"""

BLOCKS = [
    ("Cómo se cuenta la antigüedad", f"""
<p>La antigüedad es el tiempo que llevas en la empresa desde tu fecha de alta, la que figura en la nómina como «antigüedad». La
calculadora la da en años, meses y días contando de fecha a fecha, como el <a href="{CC}#a5" rel="noopener">artículo 5 del
Código Civil</a> cuenta los plazos por meses y años, e incluye el último día trabajado si marcas «Contar el último día», que es lo
habitual en un finiquito.</p>
<p>Además cuenta los <b>trienios</b>, <b>quinquenios</b> y <b>sexenios</b> cumplidos y la fecha del siguiente. El
<a href="{ET}#a25" rel="noopener">artículo 25 del Estatuto de los Trabajadores</a> permite que el convenio pague un complemento por
antigüedad, pero no lo obliga: mira en tu convenio si existe, cada cuánto se cumple y cuánto vale. En los funcionarios el trienio está
fijado por ley.</p>"""),
    ("Ejemplo", """
<p>Alta el 1 de marzo de 2020 y último día el 28 de febrero de 2026, contándolo: son <b>6 años, 0 meses y 0 días</b>, 2.191 días
naturales. Tiene 2 trienios y el tercero se cumple el 1 de marzo de 2029. Con alta el 15 de septiembre de 2021 y cálculo a 12 de
noviembre de 2026 salen 5 años, 1 mes y 29 días: para la indemnización por despido cuentan 5 años y 2 meses, 5,17 años.</p>"""),
    ("Antigüedad e indemnización", f"""
<p>La indemnización por despido se calcula por años de servicio: 33 días de salario por año en el despido improcedente, con un tope
de 24 mensualidades, y 20 días por año en el objetivo, con un tope de 12 (<a href="{ET}#a53" rel="noopener">artículos 53</a> y
<a href="{ET}#a56" rel="noopener">56 del Estatuto</a>). Los periodos de menos de un año se prorratean por meses, y los tribunales
cuentan como mes entero el que está empezado: por eso «Años para indemnización» redondea los días sueltos a un mes más.</p>
<p>Tu antigüedad puede ser anterior a tu contrato actual. Cuenta desde el primer contrato si encadenaste contratos temporales sin
interrupciones largas, y la mantienes si la empresa cambia de dueño o te subroga otra contrata
(<a href="{ET}#a44" rel="noopener">artículo 44</a>). Si tu nómina pone una fecha distinta de la real, puedes reclamarla.</p>"""),
]

FAQ = [
    ("¿Dónde veo mi fecha de antigüedad?",
     "En la cabecera de tu nómina, en el campo «antigüedad». También en el informe de vida laboral, que da la fecha de alta de cada contrato."),
    ("¿Se cuenta el último día de trabajo?",
     "Sí: el último día también lo trabajas. Del 1 de marzo de 2020 al 28 de febrero de 2026, incluido, hay 6 años justos."),
    ("¿Cuántos trienios tengo con 10 años en la empresa?",
     "Tres trienios: a los 3, 6 y 9 años. El cuarto llega a los 12. Si tu convenio paga quinquenios, con 10 años tienes dos."),
    ("¿Es obligatorio pagar la antigüedad?",
     "No en general. Solo si lo dice tu convenio colectivo o tu contrato. Muchos convenios la han congelado o sustituido por otros pluses."),
    ("¿Los contratos temporales anteriores cuentan?",
     "Cuentan si forman con el actual una misma relación laboral, sin interrupciones significativas. Los periodos de prácticas y de prueba también cuentan."),
]

TOOL = {
    "slug": "antiguedad-empresa",
    "lang": "es",
    "cat": "trabajo",
    "icon": "hourglass",
    "order": 68,
    "name": "Antigüedad en la empresa",
    "k": "años trabajados trienios quinquenios sexenios fecha alta",
    "title": "Calcular antigüedad en la empresa: años, meses y días",
    "desc": "Calcula tu antigüedad en la empresa en años, meses y días desde la fecha de alta, con trienios, quinquenios y años de servicio para la indemnización.",
    "h1": "Calcular la antigüedad en la empresa",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "alta", "type": "date", "label": "Alta", "value": "2020-03-01", "min": "1950-01-01", "max": "2035-12-31"},
        {"id": "hasta", "type": "date", "label": "Hasta", "value": "2026-11-12", "today": True, "min": "1950-01-01", "max": "2040-12-31"},
        {"id": "incl", "type": "check", "label": "Contar el último día", "value": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, arts. 25, 44, 53 y 56 (BOE)", ET), ("Código Civil, art. 5 (BOE)", CC)],
    "related": ["calculadora-finiquito", "trienios-funcionarios", "carta-baja-voluntaria", "fecha-jubilacion"],
    "tests": [
        ({"alta": "2020-03-01", "hasta": "2026-02-28", "incl": "1"}, {"n.y": 6, "n.m": 0, "n.d": 0, "n.days": 2191, "n.t3": 2, "n.next3": "2029-03-01"}),
        ({"alta": "2021-09-15", "hasta": "2026-11-12", "incl": ""}, {"n.y": 5, "n.m": 1, "n.d": 28, "n.ind": 5.17}),
        ({"alta": "2019-01-31", "hasta": "2019-03-01", "incl": ""}, {"n.y": 0, "n.m": 1, "n.d": 1}),
        ({"alta": "2026-11-12", "hasta": "2026-11-12", "incl": "1"}, {"n.days": 1, "n.d": 1}),
        ({"alta": "2026-11-13", "hasta": "2026-11-12", "incl": "1"}, {"err": "La fecha final tiene que ser posterior a la de alta."}),
    ],
}
