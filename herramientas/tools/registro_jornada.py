"""Registro de jornada: printable monthly time sheet with weekends and the place's holidays pre-marked (art. 34.9 ET)."""
import datetime as dt

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
RDL8 = "https://www.boe.es/buscar/doc.php?id=BOE-A-2019-3481"
LISOS = "https://www.boe.es/buscar/act.php?id=BOE-A-2000-15060"
GUIA = "https://www.mites.gob.es/ficheros/ministerio/GuiaRegistroJornada.pdf"


def example(ctx):
    """Working days and hours of November 2026 in Madrid, 8:00-17:00 with 1 h break (8 h a day)."""
    off = {h[0] for h in ctx.hol((2026, 2027))["reg"]["madrid"]}
    days = [dt.date(2026, 11, d) for d in range(1, 31)]
    work = [d for d in days if d.weekday() < 5 and d.isoformat() not in off]
    hols = [d for d in days if d.weekday() < 5 and d.isoformat() in off]
    return len(work), len(hols)


def blocks(ctx):
    n, h = example(ctx)
    return [
        ("Qué es y quién tiene que llevarlo", f"""
<p>Desde el 12 de mayo de 2019 todas las empresas tienen que registrar cada día la hora de entrada y de salida de cada
trabajador, sea cual sea su contrato o su jornada. Lo dice el <a href="{ET}#a34" rel="noopener">artículo 34.9 del Estatuto de los
Trabajadores</a>, introducido por el <a href="{RDL8}" rel="noopener">Real Decreto-ley 8/2019</a>. La empresa debe conservar los
registros <b>cuatro años</b> y tenerlos a disposición de los trabajadores, de sus representantes y de la Inspección de Trabajo.</p>
<p>La ley no impone un formato: vale una aplicación, un sistema de fichaje o una hoja en papel firmada, siempre que sea fiable y no
se pueda alterar después. Esta hoja sirve para el papel: rellena los datos de la empresa y del trabajador, elige el mes y tu
municipio, e imprímela o guárdala en PDF. Los fines de semana y los festivos nacionales, autonómicos y locales ya salen marcados,
así que solo hay que anotar las horas reales de cada día y firmar.</p>"""),
        ("Ejemplo: noviembre de 2026 en Madrid", f"""
<p>Con un horario de 8:00 a 17:00 y una hora de pausa para comer, cada día cuenta 8 horas de trabajo efectivo. Noviembre de 2026
tiene en Madrid {n} días laborables ({h} festivo entre semana: el lunes 2, día siguiente a Todos los Santos), así que la hoja
suma <b>{n * 8} horas</b> en el mes. Si un día sales a las 18:30, anota la salida real: la hora y media de más es tiempo extra y
debe constar en el registro.</p>
<p>La pausa solo se descuenta si no es tiempo de trabajo efectivo. El Estatuto da derecho a un descanso de al menos 15 minutos
cuando la jornada continuada pasa de seis horas (<a href="{ET}#a34" rel="noopener">artículo 34.4</a>); si tu convenio lo considera
tiempo de trabajo, pon 0 minutos en «Pausa».</p>"""),
        ("Contratos a tiempo parcial, horas extra y sanciones", f"""
<p>En los contratos a tiempo parcial, la jornada se registra día a día y se suma cada mes, y la empresa tiene que entregar al
trabajador una copia del resumen mensual junto con la nómina (<a href="{ET}#a12" rel="noopener">artículo 12.4.c del Estatuto</a>).
Las horas extraordinarias se registran y se totalizan con la nómina, con un máximo de 80 al año (<a href="{ET}#a35" rel="noopener">artículo 35</a>).</p>
<p>No llevar el registro es una infracción grave según el <a href="{LISOS}" rel="noopener">artículo 7.5 de la Ley sobre Infracciones
y Sanciones en el Orden Social</a>. El Ministerio de Trabajo publicó una <a href="{GUIA}" rel="noopener">guía sobre el registro de
jornada</a> con los criterios de la Inspección.</p>
<p>El Gobierno prepara un real decreto que obligará a que el registro sea digital. Según la normativa vigente a 12 de noviembre de
2026 la hoja en papel firmada sigue siendo válida; si el real decreto ya se ha publicado en el BOE cuando leas esto, revisa sus
plazos de adaptación.</p>"""),
    ]


FAQ = [
    ("¿Es obligatorio firmar el registro de jornada?",
     "La ley no exige la firma, pero el registro tiene que ser fiable. En papel, la firma diaria o mensual del trabajador es la forma "
     "habitual de demostrar que las horas son las reales."),
    ("¿Cuánto tiempo hay que guardar el registro?",
     "Cuatro años, a disposición de los trabajadores, de sus representantes y de la Inspección de Trabajo (artículo 34.9 del Estatuto)."),
    ("¿Tengo derecho a una copia de mis horas?",
     "Sí: el registro debe estar a tu disposición. Si trabajas a tiempo parcial, la empresa tiene que darte cada mes el resumen de "
     "tus horas junto con la nómina."),
    ("¿Vale una hoja de Excel o de papel?",
     "Sí, si se rellena cada día con las horas reales y no se puede modificar después sin dejar rastro. Por eso en papel se firma y en "
     "Excel conviene guardar copias en PDF."),
    ("¿Qué pasa con los festivos y las vacaciones?",
     "No se trabajan, así que no tienen horas. En esta hoja los festivos de tu municipio ya salen marcados; las vacaciones y las bajas "
     "puedes anotarlas en la columna de firma o de observaciones."),
]

JS = r"""
function (v, H, C) {
  var WD = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
  var MON = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function mins(s) { var m = /^(\d{1,2}):(\d\d)$/.exec(s || ''); return m ? +m[1] * 60 + +m[2] : NaN; }
  function hm(x) { return Math.floor(x / 60) + ':' + ('0' + Math.round(x % 60)).slice(-2); }
  if (!/^\d{4}-\d\d$/.test(v.mes)) return { err: 'Elige el mes.' };
  var y = +v.mes.slice(0, 4), m = +v.mes.slice(5, 7), e = mins(v.ent), s = mins(v.sal), p = isNaN(v.pau) ? 0 : v.pau;
  var fill = v.fill;
  if (fill && (isNaN(e) || isNaN(s))) return { err: 'Escribe la hora de entrada y la de salida.' };
  if (p < 0 || p > 600) return { err: 'Pausa: de 0 a 600 minutos.' };
  var per = fill ? (s >= e ? s - e : s + 1440 - e) - p : 0;
  if (fill && per <= 0) return { err: 'La pausa es más larga que la jornada.' };
  var hol = H.holidayMap(v.lugar), nd = H.monthDays(y, m), rows = '', work = 0, holn = 0;
  for (var d = 1; d <= nd; d++) {
    var dt = new Date(Date.UTC(y, m - 1, d)), w = H.wd(dt), h = hol[H.iso(dt)];
    var day = '<td class="c">' + d + '</td><td>' + WD[w] + '</td>';
    if (h || w === 6 || (w === 5 && !v.sat)) {
      if (h && (w < 5 || (w === 5 && v.sat))) holn++;
      rows += '<tr class="' + (h ? 'fh' : 'off') + '">' + day + '<td colspan="4">' + (h ? 'Festivo · ' + H.esc(h[1]) : WD[w].charAt(0).toUpperCase() + WD[w].slice(1)) + '</td><td></td></tr>';
    } else {
      work++;
      rows += '<tr>' + day + (fill ? '<td class="c">' + H.esc(v.ent) + '</td><td class="c">' + H.esc(v.sal) + '</td><td class="c">' + (p ? p + ' min' : '') +
        '</td><td class="c">' + hm(per) + '</td>' : '<td></td><td></td><td></td><td></td>') + '<td></td></tr>';
    }
  }
  var total = work * per, place = v.lugar_label, f = function (k, val) { return '<p><b>' + k + ':</b> ' + (val ? H.esc(val) : '') + '</p>'; };
  var locNote = (v.lugar_m && y === 2026) ? '<p class="rj-n">Sin festivos locales de 2026 en los datos: márcalos a mano.</p>' : '';
  var html = '<div class="rj" id="sheet"><h2 class="cq-h">Registro de jornada · ' + MON[m - 1] + ' de ' + y + '</h2>' +
    '<div class="rj-h">' + f('Empresa', v.emp) + f('CIF', v.cif) + f('Centro de trabajo', v.cen) + f('Trabajador/a', v.tra) + f('DNI/NIE', v.dni) + f('Calendario', place) + '</div>' +
    '<table class="rj-t"><thead><tr><th>Día</th><th></th><th>Entrada</th><th>Salida</th><th>Pausa</th><th>Horas</th><th>Firma</th></tr></thead><tbody>' + rows +
    '</tbody><tfoot><tr><td colspan="5">Total del mes · ' + work + ' días laborables</td><td class="c">' + (fill ? hm(total) : '') + '</td><td></td></tr></tfoot></table>' +
    '<div class="rj-s"><p>Firma de la empresa</p><p>Firma del trabajador/a</p></div>' +
    '<p class="rj-n">Registro diario de jornada (artículo 34.9 del Estatuto de los Trabajadores). La empresa lo conserva cuatro años.</p>' + locNote + '</div>';
  return {
    label: 'Horas del mes', big: fill ? hm(total) + ' h' : work + ' días',
    sub: work + ' días laborables · ' + holn + (holn === 1 ? ' festivo' : ' festivos') + ' entre semana · ' + H.esc(place),
    html: html, print: true, n: { work: work, hol: holn, minutes: total }
  };
}
"""

TOOL = {
    "slug": "registro-jornada",
    "lang": "es",
    "cat": "trabajo",
    "icon": "clock-check",
    "order": 20,
    "footer": True,
    "name": "Registro de jornada",
    "k": "hoja horas fichaje control horario plantilla pdf",
    "title": "Registro de jornada: plantilla mensual en PDF gratis",
    "desc": "Genera la hoja de registro de jornada del mes con los festivos de tu municipio ya marcados. Entrada, salida, pausa y firma. Imprímela o guárdala en PDF.",
    "h1": "Registro de jornada mensual",
    "crumb": "Registro de jornada",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "mes", "type": "month", "label": "Mes", "value": "2026-11", "today": True},
        {"id": "lugar", "type": "place"},
        {"id": "emp", "type": "text", "label": "Empresa", "value": "", "maxlength": 80, "w": "l"},
        {"id": "cif", "type": "text", "label": "CIF", "value": "", "maxlength": 12},
        {"id": "tra", "type": "text", "label": "Trabajador/a", "value": "", "maxlength": 80, "w": "l"},
        {"id": "ent", "type": "time", "label": "Entrada", "value": "08:00"},
        {"id": "sal", "type": "time", "label": "Salida", "value": "17:00"},
        {"id": "pau", "type": "number", "label": "Pausa", "value": 60, "unit": "min", "w": "s"},
        {"id": "fill", "type": "check", "label": "Rellenar horas", "value": True},
        {"id": "dni", "type": "text", "label": "DNI/NIE", "value": "", "maxlength": 12, "more": True},
        {"id": "cen", "type": "text", "label": "Centro de trabajo", "value": "", "maxlength": 80, "w": "l", "more": True},
        {"id": "sat", "type": "check", "label": "Trabaja los sábados", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, art. 34.9", ET + "#a34"), ("Real Decreto-ley 8/2019", RDL8),
                ("Guía del Ministerio de Trabajo", GUIA)],
    "related": ["cuadrante-turnos", "calculadora-vacaciones", "dias-habiles/", "dias-laborables-2027/"],
    "tests": [
        ({"mes": "2026-11", "lugar": {"r": "madrid"}}, {"n.work": 20, "n.hol": 1, "n.minutes": 9600, "err": None}),
        ({"mes": "2027-01", "lugar": {"r": "madrid"}, "ent": "09:00", "sal": "14:00", "pau": "0"}, {"n.work": 19, "n.minutes": 5700}),
        ({"mes": "2027-01", "ent": "22:00", "sal": "06:00", "pau": "30"}, {"n.minutes": 19 * 450}),
        ({"mes": "2027-05", "sat": "1"}, {"n.work": 25, "n.hol": 1}),
        ({"mes": "2027-01", "ent": "09:00", "sal": "10:00", "pau": "90"}, {"err": "La pausa es más larga que la jornada."}),
        ({"mes": "2027-02", "fill": False}, {"n.work": 20, "n.minutes": 0}),
    ],
}
