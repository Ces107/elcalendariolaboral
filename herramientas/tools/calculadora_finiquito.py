"""Calculadora de finiquito: last month's pay, unused holidays, accrued extra pays, notice and severance by cause."""
ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"

FAQ = [
    ("¿Qué diferencia hay entre finiquito e indemnización?",
     "El finiquito es lo que la empresa te debe siempre que termina la relación: el salario de los días trabajados del último mes, "
     "las vacaciones no disfrutadas y la parte de pagas extra generada. La indemnización solo existe en algunos casos (despido, fin de "
     "contrato temporal) y se suma al finiquito."),
    ("¿Cuánto me corresponde de indemnización por despido improcedente?",
     "33 días de salario por año trabajado, con un máximo de 24 mensualidades. Si empezaste antes del 12 de febrero de 2012, ese "
     "tramo cuenta a 45 días por año, con el tope de 720 días de salario (o el importe de ese primer tramo si ya lo supera, hasta 42 "
     "mensualidades)."),
    ("Si me voy yo, ¿cobro finiquito?",
     "Sí, el finiquito siempre se cobra, aunque sea una baja voluntaria; lo que no hay es indemnización. Si no avisas con la antelación "
     "de tu convenio (a menudo 15 días), la empresa puede descontarte los días de preaviso que falten."),
    ("¿El finiquito paga IRPF?",
     "El salario, las vacaciones y las pagas extra sí, como una nómina. La indemnización por despido está exenta hasta la cuantía "
     "obligatoria del Estatuto, con un máximo de 180.000 euros (artículo 7.e de la Ley del IRPF)."),
    ("¿Tengo que firmar el finiquito si no estoy de acuerdo?",
     "Puedes firmarlo como «no conforme» o «recibí, no conforme»: así cobras lo que te dan y conservas el derecho a reclamar. Para "
     "impugnar un despido hay 20 días hábiles."),
]


def blocks(ctx):
    return [
        ("Qué incluye el finiquito", f"""
<p>El finiquito suma lo que la empresa te debe el día que terminas: <b>el salario de los días trabajados del último mes</b>,
<b>las vacaciones generadas y no disfrutadas</b> (es el único caso en que se pagan en dinero, <a href="{ET}#a38" rel="noopener">artículo
38 del Estatuto</a>) y, si cobras las pagas extra aparte, <b>la parte de cada paga generada hasta la fecha de baja</b>. Si la causa
da derecho a indemnización, se añade.</p>
<p>La calculadora usa el salario bruto anual con las pagas extra incluidas. El salario diario para las vacaciones y la
indemnización es el anual entre 365. La paga de verano se genera del 1 de julio al 30 de junio y la de Navidad del 1 de enero al 31
de diciembre, que es lo más habitual; tu convenio puede fijar otros periodos o importes.</p>"""),
        ("Indemnización según la causa", f"""
<table class="tbl"><thead><tr><th scope="col">Causa</th><th scope="col">Días por año</th><th scope="col">Tope</th></tr></thead><tbody>
<tr><td>Despido improcedente (<a href="{ET}#a56" rel="noopener">art. 56</a>)</td><td>33 (45 antes del 12-02-2012)</td><td>24 mensualidades (720 días con tramo anterior)</td></tr>
<tr><td>Despido objetivo o colectivo (<a href="{ET}#a53" rel="noopener">art. 53</a>)</td><td>20</td><td>12 mensualidades</td></tr>
<tr><td>Fin de contrato temporal (<a href="{ET}#a49" rel="noopener">art. 49.1.c</a>)</td><td>12</td><td>sin tope</td></tr>
<tr><td>Baja voluntaria, despido disciplinario procedente, periodo de prueba</td><td>0</td><td>–</td></tr>
</tbody></table>
<p>Los periodos de menos de un año se prorratean por meses, y los tribunales cuentan como mes entero el mes empezado; así lo hace
la calculadora. El tramo anterior al 12 de febrero de 2012 sale de la <a href="{ET}#dtundecima" rel="noopener">disposición transitoria
undécima</a> del Estatuto. El fin de contrato de interinidad o formativo no tiene indemnización.</p>"""),
        ("Ejemplo con números", """
<p>Salario de 28.000 euros brutos al año en 14 pagas (2.000 euros cada una), alta el 1 de marzo de 2020, despido improcedente el
15 de noviembre de 2026 y 20 días de vacaciones ya disfrutados ese año:</p>
<ul>
<li>Salario de noviembre: 15 días, 2.000 × 15 ÷ 30 = 1.000,00 €.</li>
<li>Vacaciones: 30 × 319 ÷ 365 = 26,22 días generados, menos 20 disfrutados = 6,22 días × 76,71 € = 477,09 €.</li>
<li>Paga de verano: 138 días desde el 1 de julio, 2.000 × 138 ÷ 365 = 756,16 €. Paga de Navidad: 2.000 × 319 ÷ 365 = 1.747,95 €.</li>
<li>Indemnización: 6 años y 9 meses (81 meses empezados) = 6,75 años × 33 días = 222,75 días × 76,71 € = 17.087,67 €.</li>
<li><b>Total bruto: 21.068,87 €</b>, de los que 17.087,67 € (la indemnización) no tributan.</li>
</ul>"""),
    ]


JS = r"""
function (v, H, C) {
  var CUT = H.parse('2012-02-12');
  function addM(d, k) { var y = d.getUTCFullYear(), m = d.getUTCMonth() + k, t = new Date(Date.UTC(y, m, 1)); return new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), Math.min(d.getUTCDate(), H.monthDays(t.getUTCFullYear(), t.getUTCMonth() + 1)))); }
  /* months from a to b (both included), a started month counts as a whole month */
  function months(a, b) {
    var end = H.add(b, 1), n = (end.getUTCFullYear() - a.getUTCFullYear()) * 12 + end.getUTCMonth() - a.getUTCMonth() + 1;
    while (n > 0 && addM(a, n) > end) n--;
    return addM(a, n) < end ? n + 1 : n;
  }
  var sal = v.sal, a = v.alta, b = v.baja;
  if (!(sal > 0)) return { err: 'Escribe el salario bruto anual.' };
  if (!a || !b) return { err: 'Escribe la fecha de alta y la de baja.' };
  if (b < a) return { err: 'La baja es anterior al alta.' };
  var p14 = v.pag === '14', mon = sal / (p14 ? 14 : 12), day = sal / 365, y = b.getUTCFullYear(), rows = [], tot = 0;
  function row(l, x, c) { rows.push([l, H.eur(x), c]); tot += x; }
  /* salary of the last month */
  var last = b.getUTCDate() === H.monthDays(y, b.getUTCMonth() + 1), from1 = new Date(Date.UTC(y, b.getUTCMonth(), 1));
  var dm = last ? 30 : Math.min(30, H.diff(a > from1 ? a : from1, b) + 1);
  if (!v.cob) row('Salario del mes · ' + dm + ' días', mon * dm / 30);
  /* holidays */
  var jan = new Date(Date.UTC(y, 0, 1)), vs = a > jan ? a : jan, gen = (isNaN(v.vtot) ? 30 : v.vtot) * (H.diff(vs, b) + 1) / H.yearDays(y);
  var vleft = gen - (isNaN(v.vac) ? 0 : v.vac);
  row((vleft >= 0 ? 'Vacaciones no disfrutadas · ' : 'Vacaciones disfrutadas de más · ') + H.num(Math.abs(vleft), 2) + ' días', vleft * day);
  /* extra pays */
  if (p14) {
    var jul = new Date(Date.UTC(b.getUTCMonth() >= 6 ? y : y - 1, 6, 1)), s1 = a > jul ? a : jul, s2 = vs;
    row('Paga de verano · ' + (H.diff(s1, b) + 1) + ' días', mon * (H.diff(s1, b) + 1) / 365);
    row('Paga de Navidad · ' + (H.diff(s2, b) + 1) + ' días', mon * (H.diff(s2, b) + 1) / 365);
  }
  /* notice */
  var pre = isNaN(v.pre) ? 0 : v.pre;
  if (pre > 0 && v.causa === 'vol') row('Preaviso no cumplido · ' + pre + ' días', -pre * day);
  if (pre > 0 && (v.causa === 'obj' || v.causa === 'fin')) row('Preaviso no dado · ' + pre + ' días', pre * day);
  /* severance */
  var M = months(a, b), ind = 0, indDays = 0, txt = '';
  if (v.causa === 'imp') {
    if (a < CUT) {
      var mPre = Math.min(M, months(a, H.add(CUT, -1))), dPre = 45 * mPre / 12, dPost = 33 * (M - mPre) / 12;
      if (dPre > 720) { indDays = dPre; ind = Math.min(dPre * day, 42 * sal / 12); }
      else { indDays = Math.min(dPre + dPost, 720); ind = indDays * day; }
      txt = '45 días/año hasta 2012 + 33 después';
    } else { indDays = 33 * M / 12; ind = Math.min(indDays * day, 24 * sal / 12); txt = '33 días/año'; }
  } else if (v.causa === 'obj') { indDays = 20 * M / 12; ind = Math.min(indDays * day, 12 * sal / 12); txt = '20 días/año'; }
  else if (v.causa === 'fin') { indDays = 12 * M / 12; ind = indDays * day; txt = '12 días/año'; }
  var fin = tot;
  if (ind > 0) row('Indemnización · ' + txt + ' · ' + M + ' meses', ind);
  rows.push(['Total bruto', H.eur(tot), 'tot']);
  return {
    label: 'Finiquito' + (ind > 0 ? ' e indemnización' : ''), big: H.eur(tot),
    sub: ind > 0 ? 'Finiquito ' + H.eur(fin) + ' + indemnización ' + H.eur(ind) + ' (exenta de IRPF hasta el mínimo legal)' : 'Sin indemnización por esta causa',
    rows: rows, note: 'Importes brutos: la empresa resta el IRPF y la Seguridad Social del salario, las vacaciones y las pagas. Tu convenio puede mejorar estas cifras.',
    n: { total: H.r2(tot), ind: H.r2(ind), months: M, indDays: H.r2(indDays), fin: H.r2(fin) }
  };
}
"""

TOOL = {
    "slug": "calculadora-finiquito",
    "lang": "es",
    "cat": "trabajo",
    "icon": "calculator",
    "order": 40,
    "footer": True,
    "name": "Calculadora de finiquito",
    "k": "indemnización despido improcedente objetivo baja voluntaria",
    "title": "Calculadora de finiquito e indemnización por despido",
    "desc": "Calcula tu finiquito: salario del mes, vacaciones no disfrutadas, pagas extra e indemnización por despido improcedente, objetivo o fin de contrato.",
    "h1": "Calculadora de finiquito",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "sal", "type": "money", "label": "Salario bruto anual", "value": 24000, "w": "l"},
        {"id": "pag", "type": "seg", "label": "Pagas", "value": "14", "options": [("14", "14"), ("12", "12 o prorrateadas")]},
        {"id": "alta", "type": "date", "label": "Alta", "value": "2022-03-01", "min": "1970-01-01", "max": "2030-12-31"},
        {"id": "baja", "type": "date", "label": "Baja", "value": "2026-11-30", "today": True, "min": "1970-01-01", "max": "2030-12-31"},
        {"id": "causa", "type": "select", "label": "Causa", "value": "imp",
         "options": [("imp", "Despido improcedente"), ("obj", "Despido objetivo"), ("fin", "Fin de contrato temporal"),
                     ("vol", "Baja voluntaria"), ("disc", "Despido procedente o prueba")]},
        {"id": "vac", "type": "number", "label": "Vacaciones disfrutadas", "value": 0, "unit": "días", "w": "s"},
        {"id": "pre", "type": "number", "label": "Preaviso que faltó", "value": 0, "unit": "días", "w": "s", "show": ("causa", ["vol", "obj", "fin"])},
        {"id": "vtot", "type": "number", "label": "Vacaciones al año", "value": 30, "unit": "días", "w": "s", "more": True},
        {"id": "cob", "type": "check", "label": "Ya cobré el mes", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, arts. 38, 49, 53, 56 y DT 11.ª", ET),
                ("Ley del IRPF, art. 7.e", "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764#a7")],
    "related": ["calculadora-paro", "calculadora-vacaciones", "registro-jornada"],
    "tests": [
        ({"sal": "28000", "alta": "2020-03-01", "baja": "2026-11-15", "vac": "20"},
         {"n.months": 81, "n.ind": 17087.67, "n.total": 21068.87}),
        ({"sal": "36.000", "alta": "2005-06-01", "baja": "2026-11-30"}, {"n.indDays": 720, "n.ind": 71013.70}),
        ({"sal": "30000", "pag": "12", "alta": "2023-12-01", "baja": "2026-11-30", "causa": "obj", "vac": "30"},
         {"n.months": 36, "n.ind": 4931.51, "n.fin": 2290.58}),  # 2,55 days of holidays taken in advance are deducted
        ({"sal": "20000", "alta": "2026-01-01", "baja": "2026-06-30", "causa": "vol", "pre": "15", "vac": "15", "cob": "1"},
         {"n.ind": 0, "n.months": 6}),
        ({"sal": "", "alta": "2026-01-01", "baja": "2026-06-30"}, {"err": "Escribe el salario bruto anual."}),
        ({"sal": "20000", "alta": "2026-07-01", "baja": "2026-06-30"}, {"err": "La baja es anterior al alta."}),
    ],
}
