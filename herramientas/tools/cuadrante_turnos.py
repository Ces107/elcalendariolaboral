"""Cuadrante de turnos 2027: a repeating shift sequence over 2027, with the place's holidays, counts, .ics and print."""
import datetime as dt

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
RD1561 = "https://www.boe.es/buscar/act.php?id=BOE-A-1995-21781"
HOURS = {"M": 8, "T": 8, "N": 8, "X": 8, "D": 12, "G": 24, "L": 0}
PRESETS = [  # value, label, sequence
    ("5x2", "5x2 · lunes a viernes", "XXXXXLL"),
    ("6x3", "6x3", "XXXXXXLLL"),
    ("4x4", "4x4", "XXXXLLLL"),
    ("4x2", "4x2", "XXXXLL"),
    ("mtn", "Mañana-tarde-noche 2-2-2-4", "MMTTNNLLLL"),
    ("mtn7", "Mañana-tarde-noche semanal", "MMMMMLLTTTTTLLNNNNNLL"),
    ("mt7", "Mañana-tarde semanal", "MMMMMLLTTTTTLL"),
    ("12h", "12 h día-noche 2-2-4", "DDNNLLLL"),
    ("24x72", "24x72 · guardias", "GLLL"),
    ("24x48", "24x48", "GLL"),
]
START = dt.date(2027, 1, 4)


def count(seq, start=START):
    c = {}
    for i in range(365):
        d = dt.date(2027, 1, 1) + dt.timedelta(i)
        k = seq[(d - start).days % len(seq)]
        c[k] = c.get(k, 0) + 1
    return c


def blocks(ctx):
    c63, c44, cm, c24 = count("XXXXXXLLL"), count("XXXXLLLL"), count("MMTTNNLLLL"), count("GLLL")
    n = ctx.num
    return [
        ("Cómo funciona", f"""
<p>Elige el patrón de tu turno y el día en que empieza un ciclo: el cuadrante repite la secuencia todo 2027 y marca encima los
festivos de tu comunidad y, si lo eliges, los de tu municipio. Cada letra es un día: <b>M</b> mañana, <b>T</b> tarde, <b>N</b> noche,
<b>D</b> turno de día de 12 horas, <b>G</b> guardia de 24 horas, <b>X</b> trabajo (sin tipo) y <b>L</b> libre. Si tu turno no está en
la lista, escribe la secuencia a mano en «Secuencia», por ejemplo <code>MMTTNNLLLL</code>.</p>
<p>El ciclo se repite también hacia atrás: si tu ciclo empieza el 15 de marzo, enero y febrero salen con el turno que te habría
tocado. El enlace de «Copiar enlace» guarda el patrón, la fecha y el municipio, así que puedes mandárselo a tu equipo o abrirlo en el
móvil. Con «Descargar .ics» añades los turnos a Google Calendar, Outlook o el calendario del iPhone.</p>"""),
        ("Ejemplos en 2027", f"""
<p>Con el ciclo empezando el lunes 4 de enero de 2027:</p>
<ul>
<li><b>6x3</b> (seis días de trabajo y tres libres): {c63["X"]} días de trabajo y {c63["L"]} libres. Con turnos de 8 horas, son
{n(c63["X"] * 8)} horas, más que las 40 semanales de promedio del Estatuto: en la práctica el convenio compensa el exceso con más días libres o vacaciones.</li>
<li><b>4x4</b>: {c44["X"]} días de trabajo y {c44["L"]} libres; con turnos de 12 horas, {n(c44["X"] * 12)} horas.</li>
<li><b>Mañana-tarde-noche 2-2-2-4</b> (dos mañanas, dos tardes, dos noches y cuatro libres): {cm["M"]} mañanas, {cm["T"]} tardes,
{cm["N"]} noches y {cm["L"]} días libres.</li>
<li><b>24x72</b> (guardia de 24 horas y tres días libres, habitual en bomberos y algunos servicios sanitarios): {c24["G"]} guardias,
{n(c24["G"] * 24)} horas de presencia.</li>
</ul>"""),
        ("Lo que dice la ley", f"""
<p>El <a href="{ET}#a36" rel="noopener">artículo 36 del Estatuto de los Trabajadores</a> define el trabajo a turnos como el que se
organiza en equipos que ocupan sucesivamente los mismos puestos según un ritmo continuo o discontinuo, y fija que nadie esté en el
turno de noche más de dos semanas seguidas, salvo que lo elija. El trabajo nocturno es el de 22:00 a 6:00 y su jornada no puede
pasar de 8 horas diarias de promedio en un periodo de 15 días.</p>
<p>Según el <a href="{ET}#a34" rel="noopener">artículo 34</a>, la jornada máxima es de 40 horas semanales de promedio en cómputo
anual, entre el final de una jornada y el inicio de la siguiente debe haber al menos 12 horas y el trabajo efectivo no puede pasar
de 9 horas diarias salvo que el convenio lo reparta de otro modo. El <a href="{ET}#a37" rel="noopener">artículo 37</a> da un
descanso semanal de día y medio seguido, que se puede acumular en periodos de hasta 14 días, y 14 festivos al año. Los turnos de 12
y 24 horas existen por las excepciones del <a href="{RD1561}" rel="noopener">Real Decreto 1561/1995</a> de jornadas especiales y
por los convenios de cada sector.</p>"""),
    ]


FAQ = [
    ("¿Qué significa trabajar a turnos 6x3?",
     "Seis días de trabajo seguidos y tres libres, en un ciclo de nueve días que se repite sin mirar el día de la semana. Por eso unas "
     "semanas libras el fin de semana y otras no."),
    ("¿Cuántas horas al año se trabajan con un 4x4?",
     "Con turnos de 12 horas, unos 182 días de trabajo al año, cerca de 2.190 horas. El convenio suele reducirlas con días de libranza "
     "para no pasar de la jornada máxima anual."),
    ("¿Los festivos se trabajan si me toca turno?",
     "En los turnos rotativos, normalmente sí: se trabajan y se compensan con descanso o con un plus, según el convenio. Si tu empresa "
     "cierra los festivos, marca «Festivos libres» y el cuadrante los pone como libres."),
    ("¿Puedo hacer un cuadrante con mi propio turno?",
     "Sí. Escribe la secuencia en «Secuencia» con las letras M, T, N, D, G, X y L (hasta 60 días por ciclo) y elige el día en que empieza."),
    ("¿Cómo paso los turnos a Google Calendar?",
     "Pulsa «Descargar .ics» y, en Google Calendar, ve a Configuración, Importar y exportar, e importa el archivo. Cada día de trabajo "
     "aparece como un evento de todo el día con el nombre del turno."),
]

JS = r"""
function (v, H, C) {
  var NAMES = { M: 'Mañana', T: 'Tarde', N: 'Noche', D: 'Día 12 h', G: 'Guardia 24 h', X: 'Trabajo', L: 'Libre' };
  var HOURS = { M: 8, T: 8, N: 8, D: 12, G: 24, X: v.hx, L: 0 };
  var MON = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  var seq = String(v.seq).toUpperCase().replace(/[^A-Z]/g, '');
  if (!/^[MTNDGXL]{1,60}$/.test(seq)) return { err: 'Secuencia: solo M, T, N, D, G, X y L (máximo 60).' };
  if (!v.start) return { err: 'Elige el día en que empieza el ciclo.' };
  if (!(v.hx > 0 && v.hx <= 24)) return { err: 'Horas por turno: de 1 a 24.' };
  var hol = H.holidayMap(v.lugar), y0 = Date.UTC(2027, 0, 1), cnt = {}, hours = 0, worked = 0, holWorked = 0, ev = [], html = '';
  var mods = seq.length;
  for (var m = 0; m < 12; m++) {
    var first = new Date(Date.UTC(2027, m, 1)), nd = H.monthDays(2027, m + 1), lead = H.wd(first), cells = [];
    for (var k = 0; k < lead; k++) cells.push('<td class="o"></td>');
    for (var day = 1; day <= nd; day++) {
      var d = new Date(Date.UTC(2027, m, day)), i = ((H.diff(v.start, d) % mods) + mods) % mods, c = seq.charAt(i), h = hol[H.iso(d)];
      if (h && v.fl) c = 'L';
      cnt[c] = (cnt[c] || 0) + 1;
      if (c !== 'L') {
        worked++; hours += HOURS[c];
        if (h) holWorked++;
        ev.push('BEGIN:VEVENT\r\nUID:' + H.icsDate(d) + '-' + c + '@elcalendariolaboral.es\r\nDTSTAMP:20261112T000000Z\r\nDTSTART;VALUE=DATE:' + H.icsDate(d) +
          '\r\nDTEND;VALUE=DATE:' + H.icsDate(H.add(d, 1)) + '\r\nSUMMARY:' + H.icsEsc(NAMES[c] + (h ? ' · ' + h[1] : '')) + '\r\nTRANSP:TRANSPARENT\r\nEND:VEVENT');
      }
      cells.push('<td class="s-' + c + (h ? ' hol' : '') + '"' + (h ? ' title="' + H.esc(h[1]) + '"' : '') + '>' + day + (c !== 'L' ? '<b>' + c + '</b>' : '') + '</td>');
    }
    while (cells.length % 7) cells.push('<td class="o"></td>');
    var rows = '';
    for (var r = 0; r < cells.length; r += 7) rows += '<tr>' + cells.slice(r, r + 7).join('') + '</tr>';
    html += '<div class="cq-m"><table><caption>' + MON[m] + '</caption><thead><tr><th>L</th><th>M</th><th>X</th><th>J</th><th>V</th><th>S</th><th>D</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
  }
  var leg = Object.keys(NAMES).filter(function (c) { return cnt[c]; }).map(function (c) {
    return '<li><i class="s-' + c + '"></i>' + NAMES[c] + ' · <b>' + cnt[c] + '</b></li>';
  }).join('') + '<li><i class="hol" style="box-shadow:inset 0 0 0 2px #c8102e"></i>Festivo</li>';
  var ics = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//elcalendariolaboral.es//Cuadrante de turnos 2027//ES\r\nCALSCALE:GREGORIAN\r\nX-WR-CALNAME:Turnos 2027\r\n' +
    ev.join('\r\n') + (ev.length ? '\r\n' : '') + 'END:VCALENDAR\r\n';
  return {
    label: 'Días de trabajo en 2027', big: worked,
    sub: H.num(hours, 0) + ' h · ' + (cnt.L || 0) + ' libres · ' + holWorked + ' festivos trabajados · ' + H.esc(v.lugar_label),
    html: '<h2 class="cq-h">Cuadrante de turnos 2027 · ' + H.esc(seq) + '</h2><ul class="cq-leg">' + leg + '</ul><div class="cq-y">' + html + '</div>',
    print: true, ics: { name: 'turnos-2027.ics', text: ics },
    n: { worked: worked, hours: hours, cnt: cnt, holWorked: holWorked }
  };
}
"""

TOOL = {
    "slug": "cuadrante-turnos",
    "lang": "es",
    "cat": "trabajo",
    "icon": "calendar-repeat",
    "order": 10,
    "footer": True,
    "name": "Cuadrante de turnos",
    "k": "6x3 4x4 24x72 rotativo mañana tarde noche calendario",
    "title": "Cuadrante de turnos 2027: calendario 6x3, 4x4, 24x72",
    "desc": "Crea gratis tu cuadrante de turnos 2027: 6x3, 4x4, mañana-tarde-noche, 24x72 o tu secuencia, con los festivos de tu municipio. Imprímelo o pásalo al móvil.",
    "h1": "Cuadrante de turnos 2027",
    "updated": "2026-11-12",
    "hol": (2027,),
    "inputs": [
        {"id": "pat", "type": "select", "label": "Turno", "value": "6x3", "custom": "x",
         "options": [(v, lab, {"seq": s}) for v, lab, s in PRESETS] + [("x", "Personalizado")]},
        {"id": "seq", "type": "text", "label": "Secuencia", "value": "XXXXXXLLL", "maxlength": 60, "w": "l"},
        {"id": "start", "type": "date", "label": "Empieza el ciclo", "value": "2027-01-04", "min": "2020-01-01", "max": "2030-12-31"},
        {"id": "lugar", "type": "place"},
        {"id": "fl", "type": "check", "label": "Festivos libres", "value": False, "more": True},
        {"id": "hx", "type": "number", "label": "Horas por turno X", "value": 8, "unit": "h", "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, arts. 34, 36 y 37", ET), ("Real Decreto 1561/1995", RD1561),
                ("Calendario laboral 2027 (BOE)", "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-21254")],
    "related": ["registro-jornada", "calculadora-vacaciones", "dias-laborables-2027/", "vacaciones-2027/"],
    "tests": [
        ({"seq": "XXXXXXLLL", "start": "2027-01-04", "hx": "8"}, {"n.worked": 242, "n.cnt.L": 123, "n.hours": 1936}),
        ({"seq": "MMTTNNLLLL", "start": "2027-01-04", "hx": "8"}, {"n.cnt.M": 74, "n.cnt.T": 72, "n.cnt.N": 72, "n.cnt.L": 147}),
        ({"seq": "GLLL", "start": "2027-01-04", "hx": "8"}, {"n.worked": 91, "n.hours": 2184}),
        ({"seq": "XXXXXLL", "start": "2027-01-04", "hx": "8", "fl": "1", "lugar": {"r": "madrid"}}, {"n.worked": 251, "n.holWorked": 0}),  # = build.workdays(madrid)
        ({"seq": "XXXXXLL", "start": "2026-12-28", "hx": "8"}, {"n.worked": 261}),
        ({"seq": "ABC", "start": "2027-01-04", "hx": "8"}, {"err": "Secuencia: solo M, T, N, D, G, X y L (máximo 60)."}),
    ],
}
