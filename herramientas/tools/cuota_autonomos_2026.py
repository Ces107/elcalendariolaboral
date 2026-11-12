"""Cuota de autónomos 2026: RETA contribution by net-income bracket (Orden PJC/297/2026, tables of RDL 13/2022)."""

ORDEN = "https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296"
LGSS = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11724"
SS = "https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/CotizacionRecaudacionTrabajadores/10721/10957/583"
RATE = 31.5  # 28.30 contingencias comunes + 1.30 profesionales + 0.90 cese + 0.10 formación + 0.90 MEI
SOC_MIN = 1424.40
# (upper limit of monthly net income, base mínima, base máxima); None = no limit
TABLE = [
    (670, 653.59, 718.94), (900, 718.95, 900.00), (1166.69, 849.67, 1166.70),
    (1300, 950.98, 1300.00), (1500, 960.78, 1500.00), (1700, 960.78, 1700.00), (1850, 1143.79, 1850.00),
    (2030, 1209.15, 2030.00), (2330, 1274.51, 2330.00), (2760, 1356.21, 2760.00), (3190, 1437.91, 3190.00),
    (3620, 1519.61, 3620.00), (4050, 1601.31, 4050.00), (6000, 1732.03, 5101.20), (None, 1928.10, 5101.20),
]


def blocks(ctx):
    e = ctx.eur
    lo, rows = 0, ""
    for k, (hi, bmin, bmax) in enumerate(TABLE):
        name = f"Reducida {k + 1}" if k < 3 else f"General {k - 2}"
        rng = f"hasta {ctx.num(hi, 2 if hi % 1 else 0)} €" if lo == 0 else (f"más de {ctx.num(lo, 0)} €" if hi is None else f"{ctx.num(lo, 2 if lo % 1 else 0)} – {ctx.num(hi, 2 if hi % 1 else 0)} €")
        rows += f"<tr><td>{name}</td><td>{rng}</td><td class=num>{e(bmin)}</td><td class=num><b>{e(bmin * RATE / 100)}</b></td></tr>"
        lo = hi
    return [
        ("Cuánto paga un autónomo en 2026", f"""
<p>Desde 2023 la cuota depende de los <b>rendimientos netos</b>: lo que ganas al mes después de gastos. En 2026 va de
<b>{e(653.59 * RATE / 100)} al mes</b> (rendimientos de hasta 670 €) a <b>{e(1928.10 * RATE / 100)}</b> (más de 6.000 €) si
cotizas por la base mínima de tu tramo. Las tablas de 2026 son las mismas de 2025, prorrogadas por el Real Decreto-ley 3/2026
y fijadas en la <a href="{ORDEN}" rel="noopener">Orden PJC/297/2026</a>; lo único que sube es el mecanismo de equidad
intergeneracional (MEI), del 0,8 % al 0,9 %, de modo que el tipo total pasa al <b>31,5 %</b> de la base.</p>
<table class="tbl"><thead><tr><th>Tramo</th><th>Rendimiento neto al mes</th><th>Base mínima</th><th>Cuota mínima</th></tr></thead>
<tbody>{rows}</tbody></table>"""),
        ("Cómo se calcula el rendimiento neto", f"""
<p>Se parte del rendimiento neto del IRPF (ingresos menos gastos deducibles) <b>sin restar la propia cuota de autónomos</b>, y se
le quita un 7 % de gastos genéricos (un 3 % si eres autónomo societario o administrador), según el
<a href="{LGSS}#a308" rel="noopener">artículo 308 de la Ley General de la Seguridad Social</a>. El resultado se divide entre 12.</p>
<p>Ejemplo: facturas 30.000 € al año y tienes 6.000 € de gastos. Rendimiento: 24.000 €; menos el 7 %, 22.320 €; al mes,
1.860 €. Estás en el tramo 5 de la tabla general (1.850-2.030 €), con base mínima de 1.209,15 € y una cuota de
{e(1209.15 * RATE / 100)} al mes, {e(1209.15 * RATE / 100 * 12)} al año. Puedes elegir cualquier base entre la mínima y la máxima de
tu tramo: una base más alta da más pensión, más paro de autónomo y más baja por enfermedad.</p>
<p>La base se elige con una previsión de ingresos y se puede cambiar hasta seis veces al año. Cuando Hacienda conoce tus
rendimientos reales, la Seguridad Social regulariza: si cotizaste de menos, te reclama la diferencia; si cotizaste de más, te la
devuelve de oficio.</p>"""),
        ("Tarifa plana y autónomos societarios", f"""
<p>Los nuevos autónomos pagan una <b>cuota reducida de 80 € al mes</b> los primeros 12 meses, ampliables otros 12 si los
rendimientos no llegan al salario mínimo (artículo 38 ter de la LGSS). La calculadora la aplica si marcas «Tarifa plana».</p>
<p>Los <b>autónomos societarios</b> (socios que controlan su sociedad y administradores) no pueden cotizar por debajo de la base
mínima del grupo 7 del régimen general, que en 2026 es de 1.424,40 €: su cuota mínima es de {e(SOC_MIN * RATE / 100)} al mes
aunque sus rendimientos estén en un tramo inferior.</p>"""),
    ]


FAQ = [
    ("¿Cuál es la cuota mínima de autónomos en 2026?",
     f"205,88 € al mes, la del tramo 1 de la tabla reducida (rendimientos de hasta 670 € al mes), con la base mínima de 653,59 € al 31,5 %."),
    ("¿Las cuotas de autónomos han subido en 2026?",
     "Las bases son las mismas de 2025. La cuota sube muy poco porque el MEI pasa del 0,8 % al 0,9 %: unos 0,65 € al mes en el tramo "
     "más bajo y 1,93 € en el más alto."),
    ("¿Qué gastos cuentan para el rendimiento neto?",
     "Los deducibles en el IRPF: material, alquiler del local, suministros afectos, gestoría, seguros, amortizaciones… pero no la propia "
     "cuota de autónomos, que se vuelve a sumar."),
    ("¿Qué pasa si gano más de lo que declaré al elegir la base?",
     "Al año siguiente, con los datos de Hacienda, la Seguridad Social calcula la base que te correspondía y te pide la diferencia, sin "
     "recargo si pagas en plazo."),
    ("¿Cuánto paga un autónomo que gana 1.000 € al mes?",
     "Con 1.000 € de rendimiento neto está en el tramo 3 de la tabla reducida: base mínima de 849,67 € y cuota de 267,65 € al mes."),
]

JS = r"""
function (v, H, C) {
  var T = C.d.t, R = C.d.rate / 100, ing = v.ingresos, gas = v.gastos;
  if (!(ing >= 0)) return { err: 'Escribe tus ingresos del año.' };
  if (!(gas >= 0)) gas = 0;
  var g = v.tipo === 'soc' ? 0.03 : 0.07, rn = ing - gas, comp = rn > 0 ? rn * (1 - g) : rn, mon = H.r2(comp / 12);
  var k = 0;
  while (T[k][0] !== null && mon > T[k][0] + 1e-9) k++;
  var bmin = T[k][1], bmax = T[k][2], note = '';
  if (v.tipo === 'soc' && bmin < C.d.soc) { bmin = C.d.soc; if (bmax < bmin) bmax = Math.max(bmin, 5101.2); note = 'Societario: base mínima de ' + H.eur(C.d.soc) + '.'; }
  var name = k < 3 ? 'reducida, tramo ' + (k + 1) : 'general, tramo ' + (k - 2);
  var cuota = H.r2(bmin * R), cmax = H.r2(bmax * R);
  if (v.tp) { cuota = 80; note = 'Tarifa plana: 80 € al mes durante 12 meses (art. 38 ter LGSS).'; }
  return {
    label: 'Cuota mínima al mes', big: H.eur(cuota),
    sub: 'Tabla ' + name + ' · ' + H.eur(cuota * 12) + ' al año',
    rows: [['Rendimiento neto', H.eur(rn)], ['Gastos genéricos ' + (g * 100) + ' %', '− ' + H.eur(rn > 0 ? rn * g : 0)], ['Rendimiento al mes', H.eur(mon)],
      ['Base mínima', H.eur(bmin)], ['Base máxima del tramo', H.eur(bmax)], ['Cuota con la base máxima', H.eur(cmax)], ['Tu cuota', H.eur(cuota), 'tot']],
    note: note,
    n: { tramo: k + 1, mon: mon, cuota: cuota }
  };
}
"""

TOOL = {
    "slug": "cuota-autonomos-2026",
    "lang": "es",
    "cat": "trabajo",
    "cat_name": None,
    "icon": "briefcase",
    "order": 60,
    "name": "Cuota de autónomos 2026",
    "k": "reta tramos rendimientos netos seguridad social tarifa plana societario base cotización",
    "title": "Cuota de autónomos 2026: calcula tu tramo y cuánto pagas",
    "desc": "Calcula la cuota de autónomos de 2026 según tus rendimientos netos: tramo, base mínima y máxima y cuota mensual con el 31,5 % (Orden PJC/297/2026).",
    "h1": "Cuota de autónomos 2026 por tramos",
    "updated": "2026-11-12",
    "data": {"t": TABLE, "rate": RATE, "soc": SOC_MIN},
    "inputs": [
        {"id": "ingresos", "type": "money", "label": "Ingresos al año", "value": 30000, "w": "l"},
        {"id": "gastos", "type": "money", "label": "Gastos al año", "value": 6000, "w": "l"},
        {"id": "tipo", "type": "seg", "label": "Autónomo", "value": "pf", "options": [("pf", "Persona física"), ("soc", "Societario")]},
        {"id": "tp", "type": "check", "label": "Tarifa plana", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Orden PJC/297/2026, de cotización 2026 (BOE)", ORDEN), ("Ley General de la Seguridad Social, arts. 38 ter y 308 (BOE)", LGSS),
                ("Seguridad Social · Cotización de autónomos", SS)],
    "related": ["factura-retencion-irpf", "precio-sin-iva", "kilometraje-dietas", "calculadora-finiquito"],
    "tests": [
        ({"ingresos": "30000", "gastos": "6000"}, {"n.tramo": 8, "n.mon": 1860, "n.cuota": 380.88}),
        ({"ingresos": "8000", "gastos": "0"}, {"n.tramo": 1, "n.cuota": 205.88}),
        ({"ingresos": "13000", "gastos": "100"}, {"n.tramo": 3, "n.cuota": 267.65}),
        ({"ingresos": "100000", "gastos": "10000"}, {"n.tramo": 15, "n.cuota": 607.35}),
        ({"ingresos": "12000", "gastos": "0", "tipo": "soc"}, {"n.cuota": 448.69}),
        ({"ingresos": "", "gastos": "0"}, {"err": "Escribe tus ingresos del año."}),
    ],
}
