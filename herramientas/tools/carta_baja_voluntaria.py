"""Carta de baja voluntaria: resignation letter generator with the notice period and the last working day."""

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
CC = "https://www.boe.es/buscar/act.php?id=BOE-A-1889-4763"
LGSS = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11724"

JS = r"""
function (v, H, C) {
  var MON = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var WD = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
  function ld(d) { return d.getUTCDate() + ' de ' + MON[d.getUTCMonth()] + ' de ' + d.getUTCFullYear(); }
  function addMonths(d, n) { /* same day n months later (CC art. 5: de fecha a fecha), or the last day of that month */
    var y = d.getUTCFullYear(), m = d.getUTCMonth() + n, ty = y + Math.floor(m / 12), tm = ((m % 12) + 12) % 12;
    return new Date(Date.UTC(ty, tm, Math.min(d.getUTCDate(), H.monthDays(ty, tm + 1))));
  }
  function f(s, ph) { s = String(s || '').trim(); return s ? H.esc(s) : '<span class="cb-ph">[' + ph + ']</span>'; }
  var e = v.entrega;
  if (!e) return { err: 'Elige el día en que entregas la carta.' };
  var pre = v.pre, fin, txt;
  if (pre === 'd') {
    if (!(v.dias >= 0 && v.dias <= 365 && Math.floor(v.dias) === v.dias)) return { err: 'Días de preaviso: un número entero de 0 a 365.' };
    fin = H.add(e, v.dias); txt = v.dias + ' ' + H.plural(v.dias, 'día', 'días');
  } else if (pre === '1m' || pre === '2m' || pre === '3m') {
    var n = +pre.charAt(0); fin = addMonths(e, n); txt = n === 1 ? 'un mes' : n === 2 ? 'dos meses' : 'tres meses';
  } else if (pre === 'p') { fin = e; txt = ''; }
  else { fin = H.add(e, 15); txt = '15 días'; }
  var dur = H.diff(e, fin), who = f(v.nombre, 'nombre y apellidos'), org = f(v.empresa, 'empresa');
  var body = pre === 'p'
    ? '<p>Por medio de la presente les comunico mi decisión de desistir del contrato de trabajo durante el periodo de prueba, de acuerdo con el ' +
      'artículo 14 del Estatuto de los Trabajadores, con efectos del día ' + ld(fin) + ', que será mi último día de trabajo.</p>'
    : '<p>Por medio de la presente les comunico mi decisión de causar baja voluntaria en la empresa, de acuerdo con el artículo 49.1.d) del ' +
      'Estatuto de los Trabajadores.</p><p>Con el preaviso de ' + txt + ' que establece ' + (v.conv ? 'mi convenio colectivo' : 'la costumbre') +
      ', contado desde el día siguiente a la entrega de esta carta, mi último día de trabajo será el ' + ld(fin) +
      ', fecha en la que se extinguirá la relación laboral.</p>';
  var letter = '<div class="cb-l" id="cb-t">' +
    '<p class="cb-r">' + f(v.ciudad, 'ciudad') + ', a ' + ld(e) + '</p>' +
    '<p>A la atención de la dirección de ' + org + '</p>' +
    '<p><b>Asunto: comunicación de baja voluntaria</b></p>' +
    '<p>Yo, ' + who + ', con DNI/NIE ' + f(v.dni, 'DNI o NIE') + ', que presto servicios en ' + org + ' como ' + f(v.puesto, 'puesto') + ':</p>' + body +
    '<p>Les ruego que preparen la liquidación con los salarios pendientes, la parte proporcional de las pagas extraordinarias y las vacaciones ' +
    'devengadas y no disfrutadas, y que me entreguen el certificado de empresa.</p>' +
    '<p>Atentamente,</p><p class="cb-s">Firma: ' + who + '</p>' +
    '<p class="cb-s">Recibí (firma y sello de la empresa) · fecha: ____ / ____ / ________</p></div>' +
    '<div class="tools hact"><button type="button" class="btn" onclick="var t=document.getElementById(\'cb-t\');if(navigator.clipboard){navigator.clipboard.writeText(t.innerText);this.textContent=\'Carta copiada\'}">Copiar carta</button></div>';
  return {
    label: 'Último día de trabajo', big: ld(fin),
    sub: WD[H.wd(fin)] + (dur ? ' · ' + dur + ' ' + H.plural(dur, 'día', 'días') + ' naturales desde la entrega' : ' · sin preaviso'),
    html: letter, print: true,
    note: 'Entrega dos copias y quédate una firmada por la empresa, o envíala por burofax.',
    n: { fin: H.iso(fin), dur: dur }
  };
}
"""

CSS = """
.cb-l{background:var(--bg,#fff);border:1px solid var(--line,#ddd);border-radius:8px;padding:18px 20px;margin:12px 0;line-height:1.55}
.cb-l p{margin:0 0 .8em}.cb-r{text-align:right}.cb-s{margin-top:1.6em!important}.cb-ph{color:#b45309}
@media print{.cb-l{border:0;padding:0;font-size:11.5pt}.cb-ph{color:inherit}}
"""

BLOCKS = [
    ("Cómo dejar el trabajo", f"""
<p>Para irte de una empresa basta con comunicarlo por escrito con el <b>preaviso</b> que marque tu convenio colectivo o, si no dice
nada, la costumbre, que suele ser de <b>15 días naturales</b>. El <a href="{ET}#a49" rel="noopener">artículo 49.1.d) del Estatuto de
los Trabajadores</a> no fija un plazo propio: lo deja al convenio. Muchos convenios piden 15 días a la mayoría de la plantilla y un
mes o dos a técnicos y mandos; búscalo en el capítulo de «ceses» o «extinción del contrato» del tuyo.</p>
<p>El plazo se cuenta desde el día siguiente a la entrega, como manda el <a href="{CC}#a5" rel="noopener">artículo 5 del Código
Civil</a>: los plazos por días excluyen el primero y los plazos por meses van de fecha a fecha. Si estás en <b>periodo de prueba</b>,
puedes irte sin preaviso (<a href="{ET}#a14" rel="noopener">artículo 14</a>).</p>"""),
    ("Ejemplo", """
<p>Entregas la carta el martes 1 de diciembre de 2026 y tu convenio pide 15 días. El día 1 no cuenta; el primer día del plazo es el
2 y el decimoquinto, el <b>miércoles 16 de diciembre</b>, que es tu último día. El finiquito se calcula hasta esa fecha. Si tu
convenio pidiera un mes, el último día sería el 1 de enero de 2027.</p>"""),
    ("Lo que conviene saber", f"""
<ul>
<li><b>Que quede constancia</b>: pide que firmen y sellen tu copia con la fecha. Si se niegan, envía la carta por burofax con
certificación de texto, o por correo electrónico con acuse si es como os comunicáis normalmente.</li>
<li><b>Si no cumples el preaviso</b>, la empresa puede descontarte del finiquito el salario de los días que falten, si el convenio lo
prevé. También puede dejarte marchar antes: entonces te paga hasta el día que acordéis.</li>
<li><b>Sin paro</b>: la baja voluntaria no es situación legal de desempleo (<a href="{LGSS}#a267" rel="noopener">artículo 267 de la
Ley General de la Seguridad Social</a>), así que no da derecho a la prestación. Sí lo da si después te despiden de otro empleo y
tienes cotización suficiente.</li>
<li><b>El finiquito</b> incluye el salario del mes hasta el último día, la parte de pagas extra y las vacaciones no disfrutadas. Si no
estás de acuerdo con la cantidad, firma «recibí, no conforme».</li>
<li><b>Con causa</b>: si te vas por impagos, retrasos continuados en el salario o cambios graves de condiciones, no es una baja
voluntaria sino una extinción del <a href="{ET}#a50" rel="noopener">artículo 50</a>, que se pide al juzgado y lleva indemnización.</li>
</ul>"""),
]

FAQ = [
    ("¿Cuántos días de preaviso hay que dar?",
     "Los que diga tu convenio colectivo. Si no dice nada, se aplica la costumbre, que suele ser de 15 días naturales. El Estatuto de los "
     "Trabajadores no fija un mínimo."),
    ("¿El preaviso son días naturales o laborables?",
     "Naturales, salvo que el convenio diga lo contrario. Cuentan sábados, domingos y festivos."),
    ("¿Qué pasa si no doy el preaviso?",
     "La empresa puede descontarte del finiquito los días de preaviso que falten, si el convenio lo permite. No pierdes el finiquito ni las vacaciones."),
    ("¿Puedo irme durante el periodo de prueba sin avisar?",
     "Sí. En el periodo de prueba cualquiera de las dos partes puede terminar el contrato sin preaviso ni indemnización."),
    ("¿Cobro el paro si me doy de baja voluntaria?",
     "No. La baja voluntaria no da derecho a la prestación por desempleo. Si luego trabajas en otra empresa y te despiden, sí."),
    ("¿Tengo que explicar por qué me voy?",
     "No. La carta solo tiene que decir que te vas y desde cuándo. No hace falta dar motivos."),
]

TOOL = {
    "slug": "carta-baja-voluntaria",
    "lang": "es",
    "cat": "trabajo",
    "icon": "file-text",
    "order": 62,
    "name": "Carta de baja voluntaria",
    "k": "dimisión preaviso 15 días renuncia modelo",
    "title": "Carta de baja voluntaria: modelo con fecha de preaviso",
    "desc": "Genera gratis tu carta de baja voluntaria con el preaviso de 15 días, un mes o el de tu convenio: calcula tu último día de trabajo e imprímela.",
    "h1": "Carta de baja voluntaria",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "nombre", "type": "text", "label": "Nombre", "value": "", "maxlength": 80, "w": "l"},
        {"id": "dni", "type": "text", "label": "DNI/NIE", "value": "", "maxlength": 12, "w": "s"},
        {"id": "empresa", "type": "text", "label": "Empresa", "value": "", "maxlength": 80, "w": "l"},
        {"id": "puesto", "type": "text", "label": "Puesto", "value": "", "maxlength": 60},
        {"id": "ciudad", "type": "text", "label": "Ciudad", "value": "", "maxlength": 40},
        {"id": "entrega", "type": "date", "label": "Entrega", "value": "2026-12-01", "today": True},
        {"id": "pre", "type": "select", "label": "Preaviso", "value": "15",
         "options": [("15", "15 días"), ("1m", "1 mes"), ("2m", "2 meses"), ("3m", "3 meses"), ("d", "Otros días"), ("p", "Periodo de prueba")]},
        {"id": "dias", "type": "number", "label": "Días", "value": 30, "unit": "días", "w": "s", "show": ("pre", ["d"])},
        {"id": "conv", "type": "check", "label": "Lo fija mi convenio", "value": True, "more": True},
    ],
    "js": JS,
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, arts. 14, 49 y 50 (BOE)", ET), ("Código Civil, art. 5 (BOE)", CC),
                ("Ley General de la Seguridad Social, art. 267 (BOE)", LGSS)],
    "related": ["calculadora-finiquito", "calculadora-vacaciones", "antiguedad-empresa"],
    "tests": [
        ({"entrega": "2026-12-01", "pre": "15"}, {"n.fin": "2026-12-16", "n.dur": 15}),
        ({"entrega": "2026-12-01", "pre": "1m"}, {"n.fin": "2027-01-01"}),
        ({"entrega": "2027-01-31", "pre": "1m"}, {"n.fin": "2027-02-28"}),
        ({"entrega": "2026-11-30", "pre": "3m"}, {"n.fin": "2027-02-28"}),
        ({"entrega": "2027-03-10", "pre": "p"}, {"n.fin": "2027-03-10", "n.dur": 0}),
        ({"entrega": "2027-03-10", "pre": "d", "dias": "7"}, {"n.fin": "2027-03-17"}),
        ({"entrega": "2027-03-10", "pre": "d", "dias": "-3"}, {"err": "Días de preaviso: un número entero de 0 a 365."}),
    ],
}
