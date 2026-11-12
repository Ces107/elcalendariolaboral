"""Intereses de demora: legal, tax (LGT art. 26), commercial (Ley 3/2004) and procedural interest between two dates,
split by the rate of each year or half-year."""

LGT = "https://www.boe.es/buscar/act.php?id=BOE-A-2003-23186"
L32004 = "https://www.boe.es/buscar/act.php?id=BOE-A-2004-21830"
LEC = "https://www.boe.es/buscar/act.php?id=BOE-A-2000-323"
TESORO = "https://www.boe.es/boe/dias/2026/07/01/pdfs/BOE-A-2026-14327.pdf"
BDE = "https://clientebancario.bde.es/pcb/es/"
# yearly rates (%), from the LPGE of each year (2024-2026: LPGE 2023 extended)
LEGAL = {2020: 3.0, 2021: 3.0, 2022: 3.0, 2023: 3.25, 2024: 3.25, 2025: 3.25, 2026: 3.25, 2027: 3.25}
TRIB = {2020: 3.75, 2021: 3.75, 2022: 3.75, 2023: 4.0625, 2024: 4.0625, 2025: 4.0625, 2026: 4.0625, 2027: 4.0625}
# Ley 3/2004: ECB main refinancing rate on the last operation of the previous half-year + 8 points (Tesoro resolutions)
COM = {"2020-1": 8.0, "2020-2": 8.0, "2021-1": 8.0, "2021-2": 8.0, "2022-1": 8.0, "2022-2": 8.0, "2023-1": 10.5, "2023-2": 12.0,
       "2024-1": 12.5, "2024-2": 12.25, "2025-1": 11.15, "2025-2": 10.15, "2026-1": 10.15, "2026-2": 10.4, "2027-1": 10.4}
LAST = {"legal": 2026, "trib": 2026, "proc": 2026, "com": "2026-2"}

BLOCKS = [
    ("Qué interés aplicar", f"""
<p>En 2026 el <b>interés legal del dinero</b> es del <b>3,25 %</b> y el <b>interés de demora tributario</b>, del <b>4,0625 %</b>:
los mismos desde 2023, porque los Presupuestos de 2023 siguen prorrogados. El legal se usa en deudas civiles sin interés pactado
(una fianza no devuelta, una deuda entre particulares); el tributario, en las deudas con Hacienda y en las devoluciones que
Hacienda paga tarde (<a href="{LGT}#a26" rel="noopener">artículo 26 de la Ley General Tributaria</a>: el legal más un 25 %).</p>
<p>Entre empresas, o entre una empresa y la Administración, se aplica el <b>interés de demora comercial</b> de la
<a href="{L32004}#a7" rel="noopener">Ley 3/2004 contra la morosidad</a>: el tipo del Banco Central Europeo más 8 puntos, publicado
cada semestre. Es del <b>10,40 % en el segundo semestre de 2026</b> (<a href="{TESORO}" rel="noopener">resolución del Tesoro de
30 de junio de 2026</a>) y fue del 10,15 % en el primero. Y si hay sentencia, desde la fecha de la sentencia corre el
<b>interés procesal</b>, el legal más dos puntos: 5,25 % (<a href="{LEC}#a576" rel="noopener">artículo 576 de la LEC</a>).</p>"""),
    ("Cómo se calcula", """
<p>Interés = importe × tipo × días / 365 (366 en los años bisiestos). Si el periodo cruza un cambio de tipo (un año nuevo o, en
el comercial, un semestre), cada tramo se calcula con su tipo y se suman. Los días se cuentan desde el día siguiente al
vencimiento hasta el día del pago, ambos incluidos, que es lo mismo que restar las dos fechas.</p>
<p>Ejemplo: una factura de 5.000 € entre empresas que vencía el 1 de junio de 2026 y se paga el 1 de septiembre. Son 30 días de
junio al 10,15 % (41,71 €) y 62 días de julio y agosto al 10,40 % (88,33 €): <b>130,04 €</b> de intereses. La misma deuda entre
particulares, al interés legal del 3,25 %: 40,96 €. Por cada factura cobrada tarde, la Ley 3/2004 permite reclamar además 40 €
de costes de cobro.</p>"""),
]

FAQ = [
    ("¿Cuál es el interés legal del dinero en 2026?",
     "El 3,25 %, el mismo que en 2023, 2024 y 2025, porque los Presupuestos Generales de 2023 siguen prorrogados."),
    ("¿Cuánto es el interés de demora de Hacienda en 2026?",
     "El 4,0625 % anual. Se aplica a las deudas tributarias pagadas fuera de plazo y a las devoluciones que Hacienda paga con retraso."),
    ("¿Qué interés de demora se aplica entre empresas?",
     "El de la Ley 3/2004: el tipo del BCE más 8 puntos. Del 1 de julio al 31 de diciembre de 2026 es del 10,40 %."),
    ("¿Se pueden pactar otros intereses?",
     "Sí. Si el contrato fija un interés de demora, se aplica ese, con los límites de la ley de consumo o de la usura cuando es abusivo. "
     "Entre empresas, un pacto que excluya los intereses de demora es nulo."),
    ("¿Desde cuándo se cuentan los intereses?",
     "Desde el día siguiente al vencimiento del plazo de pago. Entre particulares sin plazo, desde que se reclama la deuda."),
]

JS = r"""
function (v, H, C) {
  var D = C.d, x = v.importe, a = v.desde, b = v.hasta, t = v.tipo;
  if (!(x > 0)) return { err: 'Escribe el importe de la deuda.' };
  if (!a || !b) return { err: 'Elige las dos fechas.' };
  if (b <= a) return { err: 'La fecha de pago debe ser posterior al vencimiento.' };
  if (a.getUTCFullYear() < 2020 || b.getUTCFullYear() > 2027) return { err: 'Fechas entre 2020 y 2027.' };
  function rate(d) {
    var y = d.getUTCFullYear();
    if (t === 'com') return D.com[y + '-' + (d.getUTCMonth() < 6 ? 1 : 2)];
    return t === 'trib' ? D.trib[y] : D.legal[y] + (t === 'proc' ? 2 : 0);
  }
  function nextChange(d) {
    var y = d.getUTCFullYear();
    if (t === 'com' && d.getUTCMonth() < 6) return new Date(Date.UTC(y, 6, 1));
    return new Date(Date.UTC(y + 1, 0, 1));
  }
  var cur = a, total = 0, rows = [], prov = false, last = D.last[t];
  while (cur < b) {
    var end = nextChange(cur); if (end > b) end = b;
    var days = H.diff(cur, end), r = rate(cur), yd = H.yearDays(cur.getUTCFullYear()), i = x * r / 100 * days / yd;
    var key = t === 'com' ? cur.getUTCFullYear() + '-' + (cur.getUTCMonth() < 6 ? 1 : 2) : cur.getUTCFullYear();
    if (String(key) > String(last)) prov = true;
    total += i;
    rows.push([(t === 'com' ? (cur.getUTCMonth() < 6 ? '1.er' : '2.º') + ' sem. ' : '') + cur.getUTCFullYear() + ' · ' + days + ' d al ' + H.num(r, r * 100 % 100 ? (r * 10000 % 100 ? 4 : 2) : 2).replace(/0+$/, '').replace(/,$/, '') + ' %', H.eur(i)]);
    cur = end;
  }
  total = H.r2(total);
  rows.push(['Intereses', H.eur(total), 'tot'], ['Deuda + intereses', H.eur(x + total)]);
  return {
    label: 'Intereses', big: H.eur(total), sub: H.diff(a, b) + ' días · total ' + H.eur(x + total),
    rows: rows, note: prov ? 'Tipo aún no publicado para parte del periodo: se usa el último conocido.' : '',
    n: { total: total, days: H.diff(a, b) }
  };
}
"""

TOOL = {
    "slug": "intereses-demora",
    "lang": "es",
    "cat": "dinero",
    "icon": "calendar-dollar",
    "order": 50,
    "name": "Intereses de demora",
    "k": "interés legal del dinero 2026 3,25 demora tributario 4,0625 morosidad ley 3/2004 10,40 procesal deuda factura",
    "title": "Intereses de demora 2026: interés legal y comercial",
    "desc": "Calcula los intereses de una deuda entre dos fechas con el interés legal (3,25 %), el de demora de Hacienda (4,0625 %) o el comercial (10,40 %) de 2026.",
    "h1": "Calcular intereses de demora",
    "updated": "2026-11-12",
    "data": {"legal": LEGAL, "trib": TRIB, "com": COM, "last": LAST},
    "inputs": [
        {"id": "importe", "type": "money", "label": "Deuda", "value": 5000, "w": "l"},
        {"id": "desde", "type": "date", "label": "Vencimiento", "value": "2026-06-01", "min": "2020-01-01", "max": "2027-12-31"},
        {"id": "hasta", "type": "date", "label": "Pago", "value": "2026-09-01", "today": True, "min": "2020-01-01", "max": "2027-12-31"},
        {"id": "tipo", "type": "select", "label": "Interés", "value": "com",
         "options": [("com", "Comercial · Ley 3/2004"), ("legal", "Legal del dinero"), ("trib", "Demora tributaria"), ("proc", "Procesal (legal + 2)")]},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Resolución del Tesoro, interés de demora comercial 2.º semestre 2026 (BOE-A-2026-14327)", TESORO),
                ("Ley 3/2004 de lucha contra la morosidad, art. 7 (BOE)", L32004), ("Ley 58/2003 General Tributaria, art. 26 (BOE)", LGT),
                ("Ley 1/2000 de Enjuiciamiento Civil, art. 576 (BOE)", LEC)],
    "related": ["actualizar-alquiler", "factura-retencion-irpf", "dividir-gastos", "precio-sin-iva"],
    "tests": [
        ({"importe": "10000", "desde": "2026-01-01", "hasta": "2026-07-01", "tipo": "legal"}, {"n.total": 161.16, "n.days": 181}),
        ({"importe": "10000", "desde": "2026-01-01", "hasta": "2026-07-01", "tipo": "trib"}, {"n.total": 201.46}),
        ({"importe": "1000", "desde": "2026-06-01", "hasta": "2026-08-01", "tipo": "com"}, {"n.total": 17.18}),
        ({"importe": "1000", "desde": "2022-12-01", "hasta": "2023-02-01", "tipo": "legal"}, {"n.total": 5.31}),
        ({"importe": "5000", "desde": "2026-06-01", "hasta": "2026-09-01", "tipo": "com"}, {"n.total": 130.04}),
        ({"importe": "1000", "desde": "2026-06-01", "hasta": "2026-05-01"}, {"err": "La fecha de pago debe ser posterior al vencimiento."}),
    ],
}
