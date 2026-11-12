"""Calculadora de paro: duration (LGSS art. 269 table) and amount of the contributory unemployment benefit, with the
2026 minimum and maximum (IPREM 600 €/month: the 2023 budget is still extended)."""
LGSS = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11724"
SEPE = "https://www.sepe.es/HomeSepe/es/prestaciones-desempleo/prestacion-contributiva/prestacion-contributiva-mas-de-un-anyo.html"
SEPE_EN = "https://www.sepe.es/HomeSepe/en/prestaciones-desempleo/prestacion-contributiva/prestacion-contributiva-mas-de-un-anyo.html"
IPREM = 600.0  # €/month, 2026 (Ley 31/2022 de PGE 2023, prorrogada): verify when a new budget is approved
TABLE = [(360, 120), (540, 180), (720, 240), (900, 300), (1080, 360), (1260, 420), (1440, 480), (1620, 540), (1800, 600),
         (1980, 660), (2160, 720)]


def blocks(ctx):
    rows = "".join(f'<tr><td>{a:,}{" o más" if k == len(TABLE) - 1 else f" a {TABLE[k + 1][0] - 1:,}"}</td><td>{d} días ({d // 30} meses)</td></tr>'
                   .replace(",", ".") for k, (a, d) in enumerate(TABLE))
    i = IPREM * 7 / 6
    e = ctx.eur
    return [
        ("Cómo se calcula", f"""
<p>La cuantía sale de tu <b>base reguladora</b>: la media de tus bases de cotización por desempleo de los últimos 180 días
trabajados, sin horas extra (en la nómina, la base de contingencias profesionales). Cobras el <b>70 %</b> durante los primeros 180
días y el <b>60 %</b> a partir del día 181, según el <a href="{SEPE}" rel="noopener">SEPE</a> y el artículo 270 de la
<a href="{LGSS}" rel="noopener">Ley General de la Seguridad Social</a>. Si no conoces tu base, usa tu salario bruto mensual con las
pagas extra prorrateadas: suele coincidir.</p>
<p>El resultado se ajusta a un mínimo y un máximo que dependen de los hijos a cargo y se calculan sobre el IPREM con una sexta
parte más ({e(i)} al mes con un IPREM de {e(IPREM)}):</p>
<table class="tbl"><thead><tr><th scope="col">Hijos a cargo</th><th scope="col" class="num">Mínimo</th><th scope="col" class="num">Máximo</th></tr></thead><tbody>
<tr><td>Ninguno</td><td class="num">{e(i * .8)} (80 %)</td><td class="num">{e(i * 1.75)} (175 %)</td></tr>
<tr><td>Uno</td><td class="num">{e(i * 1.07)} (107 %)</td><td class="num">{e(i * 2)} (200 %)</td></tr>
<tr><td>Dos o más</td><td class="num">{e(i * 1.07)} (107 %)</td><td class="num">{e(i * 2.25)} (225 %)</td></tr></tbody></table>
<p>Con jornada parcial, los topes se reducen en la misma proporción que tu jornada. Sobre el importe bruto, el SEPE descuenta tu
parte de la cotización a la Seguridad Social y, si corresponde, la retención de IRPF.</p>"""),
        ("Cuánto tiempo se cobra", f"""
<p>La duración depende de los días cotizados en los últimos seis años que no hayas usado ya para otra prestación
(<a href="{LGSS}#a269" rel="noopener">artículo 269 de la Ley General de la Seguridad Social</a>). Hace falta un mínimo de 360 días:</p>
<table class="tbl"><thead><tr><th scope="col">Días cotizados</th><th scope="col">Duración del paro</th></tr></thead><tbody>{rows}</tbody></table>"""),
        ("Ejemplo", f"""
<p>Base de cotización de 2.000 euros al mes, 1.800 días cotizados (casi cinco años) y sin hijos: corresponden 600 días de paro (20
meses). El 70 % de 2.000 son 1.400 euros, pero el máximo sin hijos es {e(i * 1.75)}, así que los seis primeros meses cobras
{e(i * 1.75)}. Desde el día 181, el 60 % son 1.200 euros al mes durante 14 meses. En total, {e(i * 1.75 * 6 + 1200 * 14)} brutos.</p>
<p>Cifras según la normativa vigente a 12 de noviembre de 2026: el IPREM sigue en {e(IPREM)} al mes porque se mantienen
prorrogados los Presupuestos de 2023. Si se aprueban unos nuevos, los topes cambiarán; la cifra oficial está en la página de
cuantías del SEPE.</p>"""),
    ]


FAQ = [
    ("¿Cuánto se cobra de paro en 2026?",
     "El 70 % de tu base reguladora los primeros 180 días y el 60 % después, con un mínimo de 560 euros al mes (749 con hijos) y un "
     "máximo de 1.225 euros sin hijos, 1.400 con uno y 1.575 con dos o más."),
    ("¿Cuántos días tengo que haber trabajado para cobrar el paro?",
     "Al menos 360 días cotizados en los últimos seis años. Con menos, puede corresponderte el subsidio por desempleo, que tiene "
     "otros requisitos."),
    ("¿El paro baja al 50 % a partir del séptimo mes?",
     "No en la prestación contributiva: el SEPE aplica el 60 % desde el día 181 hasta el final. Las cifras de 570, 540 y 480 euros "
     "son del subsidio, no de la prestación."),
    ("¿Si me voy voluntariamente cobro el paro?",
     "No: la baja voluntaria no es situación legal de desempleo. Sí lo es el despido, el fin de un contrato temporal o no superar el "
     "periodo de prueba a iniciativa de la empresa."),
    ("¿Se puede cobrar el paro trabajando a tiempo parcial?",
     "Sí, la prestación se puede compatibilizar con un trabajo a tiempo parcial: se descuenta en proporción a la jornada que trabajes."),
]

JS = r"""
function (v, H, C) {
  var T = C.d.table, I = C.d.iprem * 7 / 6;
  var mult = v.u === 'a' ? 365 : v.u === 'm' ? 30 : 1, days = v.cot * mult;
  if (!(v.base > 0)) return { err: 'Escribe tu base de cotización mensual.' };
  if (!(days >= 0)) return { err: 'Escribe lo que has cotizado.' };
  if (days < 360) return { err: 'Con menos de 360 días cotizados en los últimos 6 años no hay prestación contributiva: mira el subsidio por desempleo.' };
  var par = isNaN(v.parc) ? 100 : v.parc;
  if (!(par > 0 && par <= 100)) return { err: 'Jornada: de 1 a 100 %.' };
  var dur = 0;
  T.forEach(function (r) { if (days >= r[0]) dur = r[1]; });
  var k = par / 100, h = v.hijos;
  var min = I * (h === '0' ? 0.8 : 1.07) * k, max = I * (h === '0' ? 1.75 : h === '1' ? 2 : 2.25) * k;
  function clamp(x) { return Math.min(Math.max(x, min), max); }
  var m1 = clamp(v.base * 0.7), m2 = clamp(v.base * 0.6), d1 = Math.min(dur, 180), d2 = Math.max(dur - 180, 0);
  var total = m1 * d1 / 30 + m2 * d2 / 30;
  var tope = v.base * 0.7 > max ? 'máximo' : v.base * 0.6 < min ? 'mínimo' : '';
  var rows = [['Duración', dur + ' días · ' + dur / 30 + ' meses'], ['Base reguladora diaria', H.eur(v.base / 30)],
    ['Primeros 180 días (70 %)', H.eur(m1) + ' al mes']];
  if (d2) rows.push(['Desde el día 181 (60 %)', H.eur(m2) + ' al mes']);
  rows.push(['Mínimo · máximo', H.eur(min) + ' · ' + H.eur(max), 'sub']);
  rows.push(['Total bruto', H.eur(total), 'tot']);
  return {
    label: 'Paro al mes', big: H.eur(m1), sub: dur / 30 + ' meses' + (d2 ? ' · después ' + H.eur(m2) + ' al mes' : '') + (tope ? ' · con el ' + tope + ' aplicado' : ''),
    rows: rows, note: 'Bruto: el SEPE descuenta tu cotización a la Seguridad Social y el IRPF si corresponde. IPREM 2026: ' + H.eur(C.d.iprem) + ' al mes.',
    n: { dur: dur, m1: H.r2(m1), m2: H.r2(m2), total: H.r2(total) }
  };
}
"""

TOOL = {
    "slug": "calculadora-paro",
    "lang": "es",
    "cat": "trabajo",
    "icon": "cash-banknote",
    "order": 50,
    "footer": True,
    "name": "Calculadora de paro",
    "k": "prestación desempleo sepe cuánto cobro duración",
    "title": "Calculadora de paro 2026: cuánto cobro y cuánto tiempo",
    "desc": "Calcula cuánto cobrarás de paro en 2026 y durante cuántos meses: 70 % y 60 % de tu base, con los mínimos y máximos según tus hijos a cargo.",
    "h1": "Calculadora de paro 2026",
    "crumb": "Calculadora de paro",
    "updated": "2026-11-12",
    "data": {"iprem": IPREM, "table": TABLE},
    "inputs": [
        {"id": "base", "type": "money", "label": "Base de cotización mensual", "value": 1800, "w": "l"},
        {"id": "cot", "type": "number", "label": "Cotizado (6 años)", "value": 3, "w": "s"},
        {"id": "u", "type": "seg", "label": "En", "value": "a", "options": [("a", "años"), ("m", "meses"), ("d", "días")]},
        {"id": "hijos", "type": "seg", "label": "Hijos a cargo", "value": "0", "options": [("0", "0"), ("1", "1"), ("2", "2 o más")]},
        {"id": "parc", "type": "number", "label": "Jornada", "value": 100, "unit": "%", "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("SEPE · prestación contributiva", SEPE), ("Ley General de la Seguridad Social, arts. 269 y 270", LGSS)],
    "related": ["calculadora-finiquito", "calculadora-vacaciones", "registro-jornada"],
    "tests": [
        ({"base": "2000", "cot": "1800", "u": "d"}, {"n.dur": 600, "n.m1": 1225, "n.m2": 1200, "n.total": 24150}),
        ({"base": "1000", "cot": "400", "u": "d", "hijos": "1"}, {"n.dur": 120, "n.m1": 749, "n.total": 2996}),
        ({"base": "3.000", "cot": "7", "u": "a", "hijos": "2"}, {"n.dur": 720, "n.m1": 1575, "n.m2": 1575, "n.total": 37800}),
        ({"base": "900", "cot": "24", "u": "m", "parc": "50"}, {"n.dur": 240, "n.m1": 612.5, "n.m2": 540, "n.total": 4755}),
        ({"base": "1500", "cot": "300", "u": "d"}, {"n.dur": None}),
    ],
}
