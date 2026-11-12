"""Permiso por nacimiento y cuidado de menor (ET art. 48.4 after RDL 9/2025): weeks, dates, deadlines and the subsidy."""

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
RDL = "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-15741"
LGSS = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11724"
EBEP = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11719"

JS = r"""
function (v, H, C) {
  var MON = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  function fd(d) { return d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear(); }
  function bday(d, n) { var y = d.getUTCFullYear() + n, m = d.getUTCMonth(); return new Date(Date.UTC(y, m, Math.min(d.getUTCDate(), H.monthDays(y, m + 1)))); }
  var p = v.parto;
  if (!p) return { err: 'Elige la fecha del parto (o la prevista).' };
  if (H.iso(p) < '2024-08-02') return { err: 'Para nacimientos antes del 2 de agosto de 2024 rigen las 16 semanas anteriores.' };
  var old = H.iso(p) < '2025-07-31', mono = v.mono;
  if (old && mono) return { err: 'Familias monoparentales con nacimientos antes del 31 de julio de 2025: consulta a la Seguridad Social.' };
  var kids = isNaN(v.hijos) ? 1 : v.hijos;
  if (kids < 1 || kids > 8 || Math.floor(kids) !== kids) return { err: 'Hijos: de 1 a 8.' };
  var ant = v.quien === 'm' ? (+v.ant || 0) : 0;
  var ob = 6, fl = old ? 10 : mono ? 22 : 11, c8 = mono ? 4 : 2;
  var extra = (kids - 1 + (v.disc ? 1 : 0)) * (mono ? 2 : 1);
  fl += extra;
  var total = ob + fl + c8, start = H.add(p, -7 * ant);
  var obEnd = H.add(p, 7 * ob - 1), contEnd = H.add(p, 7 * (ob + fl - ant) - 1), y1 = bday(p, 1), y8 = bday(p, 8);
  var rows = [
    ['Obligatorias · ' + ob + ' sem.', fd(p) + ' – ' + fd(obEnd)],
    ['Flexibles · ' + fl + ' sem.', 'hasta ' + fd(H.add(y1, -1))],
    ['Hasta los 8 años · ' + c8 + ' sem.', 'hasta ' + fd(H.add(y8, -1))]
  ];
  if (ant) rows.splice(0, 0, ['Antes del parto · ' + ant + ' sem.', 'desde ' + fd(start)]);
  var money = null;
  if (v.base > 0) {
    money = H.r2(v.base / 30 * total * 7);
    rows.push(['Prestación · ' + total * 7 + ' días', H.eur(money), 'tot']);
  }
  rows.push(['Total', total + ' semanas', money ? 'sub' : 'tot']);
  return {
    label: 'Fin si lo coges seguido', big: fd(contEnd),
    sub: H.wd(contEnd) === 6 ? 'domingo · vuelves el lunes ' + fd(H.add(contEnd, 1)) : 'vuelves el ' + fd(H.add(contEnd, 1)),
    rows: rows,
    note: 'Seguido = obligatorias + flexibles sin interrumpir. Las ' + c8 + ' semanas hasta los 8 años se cogen aparte. Avisa a la empresa con 15 días.' +
      (old ? ' Nacimientos del 2-8-2024 al 30-7-2025: 16 semanas + 2 hasta los 8 años (RDL 9/2025).' : ''),
    n: { total: total, fl: fl, obEnd: H.iso(obEnd), contEnd: H.iso(contEnd), y1: H.iso(y1), money: money }
  };
}
"""

BLOCKS = [
    ("Cuántas semanas son", f"""
<p>Desde el <a href="{RDL}" rel="noopener">Real Decreto-ley 9/2025</a> el permiso por nacimiento y cuidado de menor es de
<b>19 semanas para cada progenitor</b>, la madre biológica y el otro progenitor, y de <b>32 semanas</b> si la familia es
monoparental. Según el <a href="{ET}#a48" rel="noopener">artículo 48.4 del Estatuto de los Trabajadores</a> se reparten así:</p>
<ul>
<li><b>6 semanas obligatorias</b>, seguidas y a jornada completa, justo después del parto.</li>
<li><b>11 semanas flexibles</b> (22 si es monoparental), por semanas sueltas o seguidas, hasta que el bebé cumpla 12 meses. La
madre biológica puede adelantar hasta 4 de ellas antes de la fecha prevista del parto.</li>
<li><b>2 semanas</b> (4 si es monoparental) que se pueden coger hasta que el niño cumpla 8 años.</li>
</ul>
<p>Cada progenitor tiene su permiso y no se puede ceder al otro. Por parto múltiple se suma una semana a cada progenitor por cada
hijo a partir del segundo, y otra por discapacidad del bebé (<a href="{ET}#a48" rel="noopener">artículo 48.6</a>). Si el bebé
queda ingresado más de siete días, el permiso se amplía lo que dure el ingreso, hasta 13 semanas más.</p>"""),
    ("Ejemplo", """
<p>Un bebé nace el lunes 2 de marzo de 2026 en una familia con dos progenitores. Cada uno tiene 19 semanas:</p>
<ul>
<li>Obligatorias: del 2 de marzo al 12 de abril de 2026.</li>
<li>Si encadenan las 11 flexibles, el permiso acaba el domingo 28 de junio de 2026 y vuelven al trabajo el lunes 29.</li>
<li>Si prefieren guardar semanas, pueden usarlas sueltas hasta el 1 de marzo de 2027, el día antes del primer cumpleaños.</li>
<li>Las otras 2 semanas, hasta el 1 de marzo de 2034.</li>
</ul>
<p>Con una base de cotización de 1.800 € al mes, la prestación es de 1.800 / 30 = 60 € al día: 133 días × 60 € = 7.980 € por
progenitor, en bruto. Esta prestación está exenta del IRPF.</p>"""),
    ("La prestación", f"""
<p>La Seguridad Social paga el <b>100 % de la base reguladora</b>: la base de cotización por contingencias comunes del mes anterior
al parto dividida entre 30 (<a href="{LGSS}#a179" rel="noopener">artículo 179 de la Ley General de la Seguridad Social</a>). La
encuentras en tu nómina como «base de contingencias comunes». Para cobrarla hay que estar de alta y, según el
<a href="{LGSS}#a178" rel="noopener">artículo 178</a>, haber cotizado 90 días en los últimos siete años si tienes entre 21 y 26 años,
o 180 días si tienes 26 o más (también valen 180 o 360 días en toda la vida laboral). Por debajo de 21 años no se exige cotización.</p>
<p>Los funcionarios y el resto del personal público tienen el mismo permiso por el <a href="{EBEP}#a49" rel="noopener">artículo 49
del Estatuto Básico del Empleado Público</a>, con sueldo íntegro.</p>
<p>Para nacimientos entre el 2 de agosto de 2024 y el 30 de julio de 2025 el permiso fue de 16 semanas, más las 2 semanas hasta los
8 años que el Real Decreto-ley 9/2025 añadió con efectos retroactivos y que se pueden pedir desde el 1 de enero de 2026.</p>"""),
]

FAQ = [
    ("¿Cuántas semanas de baja por paternidad hay en 2026?",
     "19 semanas, las mismas que la madre: 6 obligatorias tras el parto, 11 flexibles hasta los 12 meses del bebé y 2 hasta los 8 años."),
    ("¿Las 6 semanas obligatorias tienen que ser justo después del parto?",
     "Sí, para los dos progenitores: seis semanas seguidas a jornada completa desde el día del parto."),
    ("¿Puedo coger las semanas flexibles a media jornada?",
     "Sí, si lo acuerdas con la empresa. Una semana a media jornada consume media semana de permiso."),
    ("¿Se puede ceder el permiso al otro progenitor?",
     "No. Cada progenitor tiene el suyo y es intransferible. Solo si fallece uno de ellos, el otro puede usar lo que quedaba."),
    ("¿Cuánto se cobra durante el permiso?",
     "El 100 % de la base reguladora, que es la base de cotización por contingencias comunes del mes anterior dividida entre 30, por cada día del permiso. Está exenta de IRPF."),
    ("¿Con cuánta antelación hay que avisar a la empresa?",
     "Con 15 días como mínimo para las semanas flexibles y las de hasta los 8 años, o lo que diga tu convenio."),
]

TOOL = {
    "slug": "permiso-nacimiento",
    "lang": "es",
    "cat": "trabajo",
    "icon": "baby-carriage",
    "order": 63,
    "name": "Permiso por nacimiento",
    "k": "baja maternidad paternidad 19 semanas 16 semanas cuidado menor",
    "title": "Permiso por nacimiento 2026: 19 semanas, fechas y prestación",
    "desc": "Calcula las fechas de tu baja por maternidad o paternidad: 19 semanas (32 monoparental), 6 obligatorias, flexibles hasta los 12 meses y cuánto cobras.",
    "h1": "Calculadora del permiso por nacimiento",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "parto", "type": "date", "label": "Parto", "value": "2026-03-02", "today": True, "min": "2024-08-02", "max": "2028-12-31"},
        {"id": "quien", "type": "seg", "label": "Progenitor", "value": "m", "options": [("m", "Madre biológica"), ("o", "Otro progenitor")]},
        {"id": "mono", "type": "check", "label": "Monoparental", "value": False},
        {"id": "base", "type": "money", "label": "Base de cotización", "value": "", "placeholder": "1.800", "unit": "€/mes"},
        {"id": "hijos", "type": "number", "label": "Hijos en el parto", "value": 1, "w": "s", "more": True},
        {"id": "disc", "type": "check", "label": "Discapacidad", "value": False, "more": True},
        {"id": "ant", "type": "seg", "label": "Semanas antes del parto", "value": "0", "more": True, "show": ("quien", ["m"]),
         "options": [("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")]},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, art. 48.4-6 (BOE)", ET), ("Real Decreto-ley 9/2025 (BOE-A-2025-15741)", RDL),
                ("Ley General de la Seguridad Social, arts. 178-179 (BOE)", LGSS), ("Estatuto Básico del Empleado Público, art. 49 (BOE)", EBEP),
                ("Ley 35/2006 del IRPF, art. 7.h) (BOE)", "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764")],
    "related": ["calculadora-vacaciones", "dias-asuntos-propios", "calculadora-finiquito"],
    "tests": [
        ({"parto": "2026-03-02"}, {"n.total": 19, "n.obEnd": "2026-04-12", "n.contEnd": "2026-06-28", "n.y1": "2027-03-02"}),
        ({"parto": "2026-03-02", "mono": "1"}, {"n.total": 32, "n.contEnd": "2026-09-13"}),
        ({"parto": "2026-03-02", "hijos": "2", "base": "1800"}, {"n.total": 20, "n.fl": 12, "n.money": 8400}),
        ({"parto": "2026-03-02", "ant": "2"}, {"n.total": 19, "n.contEnd": "2026-06-14"}),
        ({"parto": "2026-03-02", "ant": "2", "quien": "o"}, {"n.contEnd": "2026-06-28"}),
        ({"parto": "2025-01-15"}, {"n.total": 18, "n.fl": 10}),
        ({"parto": "2024-05-01"}, {"err": "Para nacimientos antes del 2 de agosto de 2024 rigen las 16 semanas anteriores."}),
    ],
}
