"""Horas extra: value of the ordinary hour from the yearly pay and hours, the overtime premium of the collective agreement, the total."""

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
ORDEN = "https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296"

JS = r"""
function (v, H, C) {
  var s = v.sueldo, w = v.semana, rec = isNaN(v.rec) ? 0 : v.rec, n = isNaN(v.horas) ? 0 : v.horas;
  if (!(s > 0)) return { err: 'Escribe tu sueldo bruto.' };
  if (!(w > 0 && w <= 40)) return { err: 'Horas semanales: de 1 a 40.' };
  if (rec < 0 || rec > 300) return { err: 'Recargo: de 0 a 300 %.' };
  if (n < 0 || n > 500) return { err: 'Horas extra: de 0 a 500.' };
  var A = v.por === 'm14' ? s * 14 : v.por === 'm12' ? s * 12 : s;
  /* hours a year: weeks of the year minus 30 natural days of holidays (ET art. 38), minus 14 public holidays (art. 37.2) */
  var auto = w * (365 - 30) / 7 - 14 * w / 5, yh = v.anual > 0 ? v.anual : auto;
  var ord = A / yh, ex = ord * (1 + rec / 100), tot = H.r2(ex * n);
  var cap = 80;
  return {
    label: n + ' ' + H.plural(n, 'hora extra', 'horas extra'), big: H.eur(tot),
    sub: H.eur(H.r2(ex)) + ' cada una · hora ordinaria ' + H.eur(H.r2(ord)),
    rows: [
      ['Sueldo al año', H.eur(H.r2(A))],
      ['Horas al año', H.num(yh, 0) + ' h' + (v.anual > 0 ? '' : ' (estimadas)')],
      ['Hora ordinaria', H.eur(H.r2(ord))],
      ['Recargo ' + H.num(rec, rec % 1 ? 1 : 0) + ' %', H.eur(H.r2(ex - ord))],
      ['Hora extra', H.eur(H.r2(ex)), 'tot'],
      ['Cotización adicional tuya 4,70 %', '−' + H.eur(H.r2(tot * 0.047)), 'sub'],
      ['Máximo al año', H.num(cap, 0) + ' h', 'sub']
    ],
    html: n > cap ? '<p class="herr">Más de ' + H.num(cap, 0) + ' horas extra al año solo si se compensan con descanso en cuatro meses.</p>' : '',
    note: 'Bruto. El recargo lo fija tu convenio; sin convenio, la hora extra vale al menos como la ordinaria.',
    n: { ord: H.r2(ord), ex: H.r2(ex), tot: tot, yh: H.r2(yh), cap: cap }
  };
}
"""

BLOCKS = [
    ("Cuánto vale una hora extra", f"""
<p>Una hora extra vale, como mínimo, lo mismo que una hora ordinaria: el <a href="{ET}#a35" rel="noopener">artículo 35 del Estatuto
de los Trabajadores</a> deja que el convenio o el contrato fije su precio, que «en ningún caso podrá ser inferior al valor de la hora
ordinaria», o que se compense con descanso. Si no hay nada pactado, se compensa con descanso en los cuatro meses siguientes. Muchos
convenios pagan un recargo del 25 % al 75 %; escríbelo en «Recargo».</p>
<p>La hora ordinaria sale de dividir todo lo que cobras en un año, con las pagas extra, entre las horas que trabajas en un año. Si
tu convenio dice su jornada anual (suele estar entre 1.700 y 1.830 horas), ponla en «Más opciones». Si no, la calculadora la estima
con tus horas semanales: las semanas del año menos 30 días naturales de vacaciones y 14 festivos. Con 40 horas son unas 1.802 horas.</p>"""),
    ("Ejemplo", """
<p>Sueldo de 1.500 € brutos al mes en 14 pagas, 40 horas semanales y un convenio que paga las horas extra con un 75 % de recargo:</p>
<ul>
<li>Sueldo al año: 1.500 × 14 = 21.000 €.</li>
<li>Hora ordinaria: 21.000 / 1.802 h = 11,65 €.</li>
<li>Hora extra: 11,65 × 1,75 = <b>20,39 €</b>.</li>
<li>Cinco horas extra en el mes: <b>101,95 €</b> brutos.</li>
</ul>
<p>Si el convenio no fijara recargo, esas 5 horas valdrían 58,26 €, o 5 horas de descanso retribuido.</p>"""),
    ("Límites y cotización", f"""
<ul>
<li><b>80 horas al año</b> como máximo, sin contar las compensadas con descanso en cuatro meses ni las hechas para reparar siniestros
o daños urgentes. Si tu jornada anual es menor que la general, el tope baja en la misma proporción.</li>
<li><b>Voluntarias</b>, salvo que el convenio o tu contrato las pacten.</li>
<li>Con <b>contrato a tiempo parcial</b> no se pueden hacer horas extra, salvo las de fuerza mayor (artículo 12.4.c); las horas de
más son horas complementarias, con otras reglas.</li>
<li>Se cotizan aparte (<a href="{ORDEN}#a5" rel="noopener">artículo 5 de la Orden PJC/297/2026</a>): un 28,30 %, del que 4,70 % es
tuyo y 23,60 % de la empresa. Las de fuerza mayor, un 14 % (2 % tuyo). Y tributan en el IRPF como el resto del sueldo.</li>
<li>Deben quedar en el <b>registro de jornada</b> y la empresa te da cada mes el resumen de las que has hecho (artículo 35.5).</li>
</ul>"""),
]

FAQ = [
    ("¿Es obligatorio pagar las horas extra?",
     "Hay que pagarlas o compensarlas con descanso. Si no hay pacto, se compensan con descanso dentro de los cuatro meses siguientes."),
    ("¿Cuánto se paga la hora extra por ley?",
     "Al menos lo mismo que la hora ordinaria. La ley no obliga a un recargo; lo fija el convenio colectivo o el contrato."),
    ("¿Cuántas horas extra se pueden hacer al año?",
     "80 como máximo. No cuentan las compensadas con descanso en cuatro meses ni las de fuerza mayor."),
    ("¿Se cotiza por las horas extra?",
     "Sí, con una cotización adicional del 28,30 %: 4,70 % a cargo del trabajador y 23,60 % de la empresa. Las de fuerza mayor, 14 %."),
    ("¿Un trabajador a media jornada puede hacer horas extra?",
     "No, salvo por fuerza mayor. Lo que puede hacer son horas complementarias, si están pactadas por escrito."),
    ("¿Las horas extra cuentan para la pensión?",
     "No. La cotización adicional por horas extra no cuenta para la base reguladora de las prestaciones."),
]

TOOL = {
    "slug": "horas-extra",
    "lang": "es",
    "cat": "trabajo",
    "icon": "clock-plus",
    "order": 69,
    "name": "Horas extra",
    "k": "horas extraordinarias precio hora ordinaria recargo convenio 80 horas",
    "title": "Calcular horas extra: precio de la hora extraordinaria",
    "desc": "Calcula cuánto vale tu hora ordinaria y tu hora extra con el recargo de tu convenio, el total bruto de tus horas extra y el máximo de 80 horas al año.",
    "h1": "Calculadora de horas extra",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "sueldo", "type": "money", "label": "Sueldo bruto", "value": 1500},
        {"id": "por", "type": "seg", "label": "Por", "value": "m14", "options": [("m14", "Mes · 14"), ("m12", "Mes · 12"), ("a", "Año")]},
        {"id": "semana", "type": "number", "label": "Horas semanales", "value": 40, "unit": "h", "step": "0.5", "w": "s"},
        {"id": "rec", "type": "number", "label": "Recargo", "value": 0, "unit": "%", "w": "s"},
        {"id": "horas", "type": "number", "label": "Horas extra", "value": 5, "unit": "h", "step": "0.5", "w": "s"},
        {"id": "anual", "type": "number", "label": "Jornada anual", "value": "", "unit": "h", "w": "s", "more": True, "placeholder": "1.780"},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, arts. 12.4, 35, 37 y 38 (BOE)", ET),
                ("Orden PJC/297/2026, de cotización 2026, art. 5 (BOE-A-2026-7296)", ORDEN)],
    "related": ["smi-jornada-parcial", "registro-jornada", "horas-conduccion-tacografo"],
    "tests": [
        ({"sueldo": "24000", "por": "a", "semana": "40", "rec": "0", "horas": "10"}, {"n.ord": 13.32, "n.tot": 133.16, "n.yh": 1802.29}),
        ({"sueldo": "1500", "por": "m14", "semana": "40", "rec": "75", "horas": "5"}, {"n.ex": 20.39, "n.tot": 101.95}),
        ({"sueldo": "1500", "por": "m14", "semana": "40", "rec": "0", "horas": "5"}, {"n.tot": 58.26}),
        ({"sueldo": "30000", "por": "a", "anual": "1760", "horas": "1"}, {"n.ord": 17.05, "n.yh": 1760}),
        ({"sueldo": "", "por": "a"}, {"err": "Escribe tu sueldo bruto."}),
    ],
}
