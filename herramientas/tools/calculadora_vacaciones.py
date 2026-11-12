"""Vacaciones que me corresponden: proportional holiday days by time worked in the year (art. 38 ET, ILO C132)."""
ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
OIT = "https://normlex.ilo.org/dyn/normlex/es/f?p=NORMLEXPUB:12100:0::NO::P12100_ILO_CODE:C132"

FAQ = [
    ("¿Cuántos días de vacaciones me corresponden por mes trabajado?",
     "Con los 30 días naturales del mínimo legal, 2,5 días naturales por mes trabajado (30 entre 12). En días laborables, unos 1,83 "
     "por mes (22 entre 12)."),
    ("¿Son 30 días naturales o 22 laborables?",
     "El Estatuto fija un mínimo de 30 días naturales. Muchos convenios lo expresan como 22 días laborables (de lunes a viernes), que "
     "viene a ser lo mismo para una jornada de lunes a viernes. Si tu convenio da más días, escríbelos en «Días al año»."),
    ("¿Si trabajo a tiempo parcial tengo menos vacaciones?",
     "No: tienes los mismos días que a jornada completa; lo que cambia es el sueldo de esos días. Solo si trabajas menos días por "
     "semana cambian los días laborables, y eso se ajusta con «Días por semana»."),
    ("¿Cuentan las bajas médicas para generar vacaciones?",
     "Sí. La incapacidad temporal no interrumpe el devengo, y si la baja coincide con tus vacaciones puedes disfrutarlas después, "
     "hasta 18 meses tras el final del año en que se generaron (artículo 38.3 del Estatuto)."),
    ("¿Qué pasa con las vacaciones que no disfruto si me voy de la empresa?",
     "Se pagan en el finiquito: es el único caso en que las vacaciones se pueden cambiar por dinero."),
    ("¿Se redondean los días?",
     "La ley no lo dice. Muchos convenios y empresas redondean al alza al día entero; la calculadora muestra el valor exacto y el "
     "redondeado."),
]


def blocks(ctx):
    return [
        ("Cómo se calcula", f"""
<p>Las vacaciones se generan día a día a lo largo del año natural. Si no trabajas el año entero (entras en julio, terminas un
contrato en septiembre…), te corresponde la parte proporcional: <b>días al año × días trabajados ÷ días del año</b>. La cuenta
incluye el primer y el último día de contrato, y los días de baja médica cuentan como trabajados.</p>
<p>El resultado sale en días naturales (los que cuentan si te vas un mes entero, con fines de semana incluidos) y en días
laborables, que es como lo cuentan muchas empresas cuando pides días sueltos. La equivalencia habitual es 30 naturales = 22
laborables con jornada de lunes a viernes; si trabajas 3 o 4 días por semana, cambia «Días por semana» en «Más opciones».</p>"""),
        ("Ejemplos", """
<ul>
<li><b>Alta el 1 de julio de 2026</b>, hasta final de año: 184 días trabajados de 365. 30 × 184 ÷ 365 = <b>15,12 días naturales</b>,
o 22 × 184 ÷ 365 = 11,09 días laborables (11 o 12 según se redondee).</li>
<li><b>Contrato del 15 de marzo al 30 de septiembre de 2027</b>: 200 días. 30 × 200 ÷ 365 = 16,44 días naturales; en laborables,
12,05.</li>
<li><b>Año completo trabajando 3 días por semana</b>: los mismos 30 días naturales, que son 13,2 de tus días laborables
(22 × 3 ÷ 5).</li>
</ul>"""),
        ("Lo que dice la ley", f"""
<p>El <a href="{ET}#a38" rel="noopener">artículo 38 del Estatuto de los Trabajadores</a> fija que las vacaciones anuales
retribuidas son las del convenio o el contrato y que <b>nunca pueden ser menos de 30 días naturales</b>, ni cambiarse por
dinero mientras sigas en la empresa. El calendario de vacaciones se fija en cada empresa y debes conocer tus fechas al menos dos
meses antes de empezarlas. El cálculo proporcional para quien no trabaja el año completo viene del
<a href="{OIT}" rel="noopener">Convenio 132 de la OIT</a> sobre vacaciones pagadas, que España ratificó, y lo aplican los
convenios colectivos.</p>"""),
    ]


JS = r"""
function (v, H, C) {
  var y = +v.anio, a = new Date(Date.UTC(y, 0, 1)), b = new Date(Date.UTC(y, 11, 31));
  var from = v.alta && v.alta > a ? v.alta : a, to = v.baja && v.baja < b ? v.baja : b;
  if (v.alta && v.baja && v.baja < v.alta) return { err: 'La baja es anterior al alta.' };
  if (to < from) return { err: 'Las fechas no caen en ' + y + '.' };
  var n = H.diff(from, to) + 1, Y = H.yearDays(y), ds = isNaN(v.dsem) ? 5 : v.dsem;
  if (!(ds >= 1 && ds <= 6)) return { err: 'Días por semana: de 1 a 6.' };
  var N, W;
  if (v.base === 'n') { N = 30; W = 22 * ds / 5; }
  else if (v.base === 'cn') { if (!(v.dias > 0 && v.dias <= 60)) return { err: 'Días al año: de 1 a 60.' }; N = v.dias; W = v.dias * 22 / 30 * ds / 5; }
  else { if (!(v.dias > 0 && v.dias <= 60)) return { err: 'Días al año: de 1 a 60.' }; W = v.dias; N = v.dias * 30 / 22; }
  var nat = N * n / Y, lab = W * n / Y, used = isNaN(v.usados) ? 0 : v.usados;
  var unitLab = v.base === 'cl', mine = unitLab ? lab : nat, left = mine - used;
  function up(x) { return Math.ceil(H.r2(x)); }
  return {
    label: 'Vacaciones en ' + y, big: H.num(nat, 2) + ' días naturales',
    sub: H.num(lab, 2) + ' días laborables · ' + n + ' de ' + Y + ' días trabajados',
    rows: [
      ['Días naturales', H.num(nat, 2) + ' · redondeado ' + up(nat)],
      ['Días laborables', H.num(lab, 2) + ' · redondeado ' + up(lab)],
      ['Ya disfrutados', H.num(used, 2) + (unitLab ? ' laborables' : ' naturales'), 'sub'],
      ['Te quedan', H.num(left, 2) + (unitLab ? ' laborables' : ' naturales'), 'tot']
    ],
    note: 'Del ' + H.iso(from).split('-').reverse().join('/') + ' al ' + H.iso(to).split('-').reverse().join('/') + '. Tu convenio puede dar más días o redondear distinto.',
    n: { nat: H.r2(nat), lab: H.r2(lab), days: n, left: H.r2(left) }
  };
}
"""

TOOL = {
    "slug": "calculadora-vacaciones",
    "lang": "es",
    "cat": "trabajo",
    "icon": "beach",
    "order": 30,
    "footer": True,
    "name": "Vacaciones que me corresponden",
    "k": "proporcionales días naturales laborables contrato",
    "title": "Calculadora de vacaciones: días que me corresponden",
    "desc": "Calcula los días de vacaciones proporcionales al tiempo trabajado en 2026 o 2027, en días naturales y laborables, según tu fecha de alta o de baja.",
    "h1": "Vacaciones que me corresponden",
    "crumb": "Calculadora de vacaciones",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "anio", "type": "seg", "label": "Año", "value": "2026", "options": [("2026", "2026"), ("2027", "2027")]},
        {"id": "alta", "type": "date", "label": "Alta", "value": "", "min": "2000-01-01", "max": "2027-12-31"},
        {"id": "baja", "type": "date", "label": "Baja", "value": "", "min": "2026-01-01", "max": "2030-12-31"},
        {"id": "base", "type": "select", "label": "Días al año", "value": "n",
         "options": [("n", "30 naturales (mínimo legal)"), ("cn", "Otro, en naturales"), ("cl", "Otro, en laborables")]},
        {"id": "dias", "type": "number", "label": "Días", "value": 23, "w": "s", "show": ("base", ["cn", "cl"])},
        {"id": "usados", "type": "number", "label": "Disfrutados", "value": 0, "unit": "días", "w": "s", "step": "0.5"},
        {"id": "dsem", "type": "number", "label": "Días por semana", "value": 5, "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, art. 38", ET + "#a38"), ("Convenio 132 de la OIT", OIT)],
    "related": ["calculadora-finiquito", "cuadrante-turnos", "vacaciones-2027/", "dias-laborables-2027/"],
    "tests": [
        ({"anio": "2026", "alta": "2026-07-01"}, {"n.days": 184, "n.nat": 15.12, "n.lab": 11.09}),
        ({"anio": "2027"}, {"n.nat": 30, "n.lab": 22, "n.days": 365}),
        ({"anio": "2027", "alta": "2027-03-15", "baja": "2027-09-30"}, {"n.days": 200, "n.nat": 16.44, "n.lab": 12.05}),
        ({"anio": "2027", "dsem": "3"}, {"n.lab": 13.2}),
        ({"anio": "2027", "base": "cl", "dias": "25", "usados": "5"}, {"n.lab": 25, "n.left": 20}),
        ({"anio": "2027", "alta": "2027-05-01", "baja": "2027-04-01"}, {"err": "La baja es anterior al alta."}),
    ],
}
