"""SMI 2026 a jornada parcial: Real Decreto 126/2026 prorated by weekly hours, in 14 or 12 payments, per day and per hour."""

RD = "https://www.boe.es/buscar/act.php?id=BOE-A-2026-3815"
ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"

MONTH, DAY, YEAR, EVENT, HOGAR = 1221, 40.70, 17094, 57.82, 9.55

JS = r"""
function (v, H, C) {
  var S = C.d;
  var h = v.horas, full = isNaN(v.full) ? 40 : v.full;
  if (!(full > 0 && full <= 40)) return { err: 'Jornada completa: de 1 a 40 horas semanales.' };
  if (!(h > 0)) return { err: 'Escribe las horas semanales de tu contrato.' };
  if (h > full) return { err: 'Las horas de tu contrato no pueden pasar de la jornada completa (' + H.num(full, 1).replace(',0', '') + ' h).' };
  var f = h / full, year = H.r2(S.year * f), m14 = H.r2(S.month * f), m12 = H.r2(year / 12), day = H.r2(S.day * f);
  var hour = H.r2(S.year / (full * 52.1429));
  var big = v.pagas === '12' ? m12 : m14;
  return {
    label: 'SMI 2026 · ' + H.num(h, 2).replace(/,00$/, '') + ' h/semana', big: H.eur(big),
    sub: 'al mes en ' + (v.pagas === '12' ? '12 pagas (extras prorrateadas)' : '14 pagas') + ' · ' + H.num(f * 100, 1).replace(',0', '') + ' % de jornada',
    rows: [
      ['Al mes · 14 pagas', H.eur(m14)],
      ['Al mes · 12 pagas', H.eur(m12)],
      ['Al año', H.eur(year), 'tot'],
      ['Al día', H.eur(day)],
      ['Por hora de contrato', H.eur(hour), 'sub'],
      ['Eventual ≤ 120 días · por jornada', H.eur(H.r2(S.event * f)), 'sub'],
      ['Empleada de hogar por horas', H.eur(S.hogar) + ' /h', 'sub']
    ],
    note: 'Importes brutos mínimos: tu convenio puede fijar más. El SMI se compara en cómputo anual con todo lo que cobras.',
    n: { m14: m14, m12: m12, year: year, day: day, hour: hour }
  };
}
"""

BLOCKS = [
    ("Cuánto es el SMI a media jornada", f"""
<p>El salario mínimo interprofesional de 2026 es de <b>1.221 € al mes en 14 pagas</b>, <b>17.094 € al año</b> o <b>40,70 € al
día</b> por la jornada completa, según el <a href="{RD}" rel="noopener">Real Decreto 126/2026</a>, con efectos desde el 1 de enero
de 2026. Si trabajas menos horas, el mínimo se cobra <i>a prorrata</i> (artículo 1 del real decreto): a media jornada de 20 horas
semanales son <b>610,50 € al mes en 14 pagas</b>, 712,25 € si las pagas extra se prorratean en 12 mensualidades, y 8.547 € al
año.</p>
<p>La calculadora divide tus horas por las de la jornada completa (40 a la semana, el máximo del
<a href="{ET}#a34" rel="noopener">artículo 34 del Estatuto de los Trabajadores</a>, o la que fije tu convenio en «Más opciones») y
aplica ese porcentaje a cada cuantía oficial.</p>"""),
    ("Ejemplos", f"""
<ul>
<li><b>30 horas</b> de 40: 75 % · 915,75 € al mes en 14 pagas · 1.068,38 € en 12 · 12.820,50 € al año.</li>
<li><b>25 horas</b> de 40: 62,5 % · 763,13 € al mes en 14 pagas · 10.683,75 € al año.</li>
<li><b>30 horas</b> en un convenio de 38 horas: 78,9 % · 963,95 € al mes en 14 pagas. Cuanto más corta es la jornada completa del
convenio, más vale cada hora.</li>
</ul>
<p>El precio por hora sale de repartir los 17.094 € anuales entre las horas de contrato de un año, 40 × 52,14 semanas: unos
8,20 € por hora con vacaciones y festivos pagados. No es una cuantía oficial; las únicas por hora que fija el real decreto son las de
empleadas de hogar por horas, <b>9,55 €</b>, que ya incluyen pagas extra y vacaciones.</p>"""),
    ("Cómo se aplica", f"""
<p>El SMI se compara en cómputo anual con todo lo que cobras en dinero, incluidos los complementos (artículo 3): si tu sueldo base es
menor pero los pluses te llevan por encima de 17.094 € (o su parte proporcional), la empresa cumple. El salario en especie no
cuenta para llegar al mínimo.</p>
<p>Con un contrato temporal de menos de 120 días en la misma empresa, el mínimo es de <b>57,82 € por jornada</b>, porque
incluye la parte de domingos, festivos y pagas extra (artículo 4).</p>"""),
]

FAQ = [
    ("¿Cuál es el SMI de 2026?",
     "1.221 € brutos al mes en 14 pagas, o 1.424,50 € en 12 pagas, por jornada completa: 17.094 € al año. Se aplica desde el 1 de enero de 2026."),
    ("¿Cuánto es el SMI de 2026 a media jornada?",
     "610,50 € al mes en 14 pagas o 712,25 € en 12, si la jornada completa es de 40 horas y trabajas 20."),
    ("¿Cuánto es el SMI por hora en 2026?",
     "El real decreto no fija un precio por hora general. Repartiendo 17.094 € entre 40 horas por 52,14 semanas salen unos 8,20 € por hora de contrato. Para empleadas de hogar por horas sí hay cuantía: 9,55 €."),
    ("¿El SMI es bruto o neto?",
     "Bruto. De él se restan las cotizaciones del trabajador a la Seguridad Social y, si corresponde, la retención de IRPF."),
    ("¿Pueden pagarme menos del SMI si trabajo a tiempo parcial?",
     "Menos que el SMI completo sí, pero nunca menos que su parte proporcional a tus horas."),
]

TOOL = {
    "slug": "smi-jornada-parcial",
    "lang": "es",
    "cat": "trabajo",
    "icon": "cash",
    "order": 66,
    "name": "SMI a jornada parcial",
    "k": "salario mínimo 2026 1221 media jornada por horas 12 pagas 14 pagas",
    "title": "SMI 2026 a jornada parcial: por horas, mes y año",
    "desc": "Calcula el salario mínimo 2026 para tu jornada: 1.221 € en 14 pagas a tiempo completo, a media jornada, por horas, en 12 o 14 pagas y al año.",
    "h1": "SMI 2026 a jornada parcial",
    "updated": "2026-11-12",
    "data": {"month": MONTH, "day": DAY, "year": YEAR, "event": EVENT, "hogar": HOGAR},
    "inputs": [
        {"id": "horas", "type": "number", "label": "Horas semanales", "value": 20, "unit": "h", "step": "0.5", "w": "s"},
        {"id": "pagas", "type": "seg", "label": "Pagas", "value": "14", "options": [("14", "14"), ("12", "12")]},
        {"id": "full", "type": "number", "label": "Jornada completa", "value": 40, "unit": "h", "step": "0.5", "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Real Decreto 126/2026, salario mínimo interprofesional para 2026 (BOE-A-2026-3815)", RD),
                ("Estatuto de los Trabajadores, arts. 27 y 34 (BOE)", ET)],
    "related": ["horas-extra", "coste-empleada-hogar", "calculadora-finiquito"],
    "tests": [
        ({"horas": "20"}, {"n.m14": 610.5, "n.m12": 712.25, "n.year": 8547, "n.day": 20.35}),
        ({"horas": "40", "pagas": "12"}, {"n.m12": 1424.5, "n.year": 17094, "n.hour": 8.2}),
        ({"horas": "30", "full": "38"}, {"n.m14": 963.95}),
        ({"horas": "45"}, {"err": "Las horas de tu contrato no pueden pasar de la jornada completa (40 h)."}),
        ({"horas": ""}, {"err": "Escribe las horas semanales de tu contrato."}),
    ],
}
