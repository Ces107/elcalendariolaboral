"""Horario escolar imprimible: a weekly timetable (Monday to Friday) from the start time, session length, number of
sessions and one or two breaks, with the subjects of each day typed as a comma-separated list. Each subject gets a
pastel colour (same subject, same colour), and the sheet prints on one A4 landscape page."""
from herramientas.tools._estudios import CAT

DAYS = [("lu", "Lunes", "Matemáticas, Lengua, Inglés, Geografía, Biología, Ed. Física"),
        ("ma", "Martes", "Lengua, Matemáticas, Física y Química, Inglés, Tecnología, Música"),
        ("mi", "Miércoles", "Inglés, Geografía, Matemáticas, Lengua, Plástica, Tutoría"),
        ("ju", "Jueves", "Biología, Lengua, Matemáticas, Ed. Física, Inglés, Física y Química"),
        ("vi", "Viernes", "Matemáticas, Tecnología, Lengua, Geografía, Música, Plástica")]

JS = r"""
function (v, H, C) {
  var PAL = ['#fde2e4', '#dfe7fd', '#fff1c1', '#e2f0d9', '#e8dff5', '#d7f0f7', '#fce1c8', '#f6d6e8', '#dde8b9', '#cfe3f0', '#f2e6d8', '#e0e0e0'];
  var DN = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'], ids = ['lu', 'ma', 'mi', 'ju', 'vi'];
  var m = /^(\d{1,2}):(\d\d)/.exec(v.ini || '');
  if (!m) return { err: 'Escribe la hora de entrada.' };
  var t0 = +m[1] * 60 + +m[2], dur = v.dur, ses = v.ses;
  if (!(dur >= 10 && dur <= 180)) return { err: 'La sesión tiene que durar entre 10 y 180 minutos.' };
  if (!(ses >= 1 && ses <= 12) || ses % 1) return { err: 'Entre 1 y 12 sesiones.' };
  function hm(x) { x = ((x % 1440) + 1440) % 1440; return (x / 60 | 0) + ':' + ('0' + x % 60).slice(-2); }
  var days = ids.map(function (id) { return String(v[id] || '').split(/[,;\n]/).map(function (s) { return s.trim().replace(/^-$/, ''); }); });
  var col = {}, order = [], hours = {}, over = 0;
  days.forEach(function (d) {
    if (d.filter(Boolean).length > ses && d.length > ses) over = 1;
    d.slice(0, ses).forEach(function (s) {
      if (!s) return;
      var k = s.toLowerCase();
      if (!(k in col)) { col[k] = PAL[order.length % PAL.length]; order.push(s); hours[s] = 0; }
      hours[order.filter(function (o) { return o.toLowerCase() === k; })[0]] += 1;
    });
  });
  var breaks = {};
  if (v.rec >= 1 && v.rec < ses && v.drec > 0) breaks[v.rec] = v.drec;
  if (v.rec2 >= 1 && v.rec2 < ses && v.drec2 > 0) breaks[v.rec2] = (breaks[v.rec2] || 0) + v.drec2;
  var t = t0, body = '';
  for (var s = 1; s <= ses; s++) {
    body += '<tr><th scope="row" class="hs-h">' + hm(t) + '<br>' + hm(t + dur) + '</th>';
    for (var d = 0; d < 5; d++) {
      var name = days[d][s - 1] || '';
      body += '<td' + (name ? ' style="background:' + col[name.toLowerCase()] + '"' : '') + '>' + H.esc(name) + '</td>';
    }
    body += '</tr>';
    t += dur;
    if (breaks[s]) { body += '<tr class="hs-r"><th scope="row" class="hs-h">' + hm(t) + '</th><td colspan="5">Recreo · ' + breaks[s] + ' min</td></tr>'; t += breaks[s]; }
  }
  var title = String(v.tit || '').trim();
  var html = '<div class="hs-sheet">' + (title ? '<p class="hs-t">' + H.esc(title) + '</p>' : '') +
    '<table class="hs"><thead><tr><th scope="col"></th>' + DN.map(function (x) { return '<th scope="col">' + x + '</th>'; }).join('') + '</tr></thead><tbody>' + body + '</tbody></table></div>';
  var rows = order.map(function (o) { return [H.esc(o), hours[o] + ' ' + H.plural(hours[o], 'sesión', 'sesiones') + ' · ' + H.num(hours[o] * dur / 60, 1).replace(',0', '') + ' h']; });
  var tot = order.reduce(function (a, o) { return a + hours[o]; }, 0);
  rows.push(['Total semanal', tot + ' sesiones · ' + H.num(tot * dur / 60, 1).replace(',0', '') + ' h', 'tot']);
  var h = {};
  order.forEach(function (o) { h[o] = hours[o] * dur / 60; });
  return { label: 'Horario', big: hm(t0) + ' – ' + hm(t), sub: ses + ' sesiones de ' + dur + ' min · ' + order.length + ' materias',
    html: html, rows: rows, print: true, note: over ? 'Algún día tiene más materias que sesiones: sobran las últimas.' : '',
    n: { end: hm(t), total: tot, h: h } };
}
"""

CSS = """
.hs-sheet{margin:1rem 0;overflow-x:auto}.hs-t{font-weight:700;font-size:1.15rem;margin:0 0 .5rem}
.hs{width:100%;border-collapse:collapse;table-layout:fixed;min-width:34rem}
.hs th,.hs td{border:1px solid #999;padding:.45rem .3rem;text-align:center;font-size:.9rem;line-height:1.2}
.hs td{color:#111;font-weight:600}.hs thead th{font-weight:700}
.hs .hs-h{width:4.2rem;font-size:.78rem;font-weight:400;white-space:nowrap}
.hs .hs-r td{font-size:.8rem;font-weight:400;letter-spacing:.04em;background:repeating-linear-gradient(45deg,transparent 0 6px,rgba(0,0,0,.05) 6px 12px)}
@media print{@page{size:A4 landscape;margin:12mm}.hs-sheet{overflow:visible;margin:0}.hs{min-width:0}
.hs th,.hs td{padding:3mm 1.5mm;font-size:11pt;border-color:#555}.hs .hs-h{font-size:9pt}.hs-t{font-size:16pt}
.hs td,.hs .hs-r td{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""

BLOCKS = [
    ("Cómo hacer tu horario", """
<p>Pon la hora de entrada, lo que dura cada sesión, cuántas hay al día y después de cuál va el recreo; luego escribe las
materias de cada día en orden, separadas por comas. El horario se dibuja al momento con las horas de inicio y fin de cada
clase calculadas, y cada materia con su color, el mismo todos los días, para que se vea de un vistazo. Pulsa «Imprimir o PDF»
y sale en una hoja A4 apaisada, sin nada más alrededor; también puedes guardarlo como PDF desde el mismo diálogo.</p>
<p>Si una hora está libre, deja el hueco entre dos comas o pon un guion: <code>Lengua, -, Inglés</code>. Si tu centro tiene
un segundo recreo, o una pausa para comer en jornada partida, añádelo en «Más opciones». Debajo del horario verás cuántas
sesiones y horas a la semana tiene cada materia, útil para comprobar que cuadra con lo que dice tu centro.</p>"""),
    ("Un ejemplo de 1.º de ESO", """
<p>Un instituto con entrada a las 8:30, seis sesiones de 55 minutos y recreo de 30 minutos después de la tercera. Las clases
quedan así: 8:30-9:25, 9:25-10:20 y 10:20-11:15; recreo hasta las 11:45; y 11:45-12:40, 12:40-13:35 y 13:35-14:30. Son 30
sesiones semanales, 27,5 horas de clase. Con las materias del ejemplo, Matemáticas y Lengua tienen cinco sesiones cada una
(4,6 horas), Inglés cuatro y el resto dos o tres, más una de tutoría.</p>
<p>El enlace que copias con «Copiar enlace» lleva todo el horario dentro: si lo mandas al grupo de la clase o a otro
profesor, lo abre tal cual y puede imprimirlo sin volver a escribir nada.</p>"""),
    ("Cuántas horas de clase hay en cada etapa", """
<p>El horario lo decide cada centro dentro de lo que fija su comunidad. Los reales decretos de enseñanzas mínimas (157/2022
para Primaria y 217/2022 para la ESO) recogen en su anexo IV las horas mínimas de cada área o materia, que según el
artículo 6.4 de la Ley Orgánica de Educación son el 50 % del horario en las comunidades con lengua cooficial y el 60 % en las
demás; el resto lo reparte cada comunidad. En la práctica, los colegios suelen tener 25 horas semanales repartidas en cinco
o seis sesiones al día, y los institutos unas 30 sesiones semanales de 50 a 60 minutos. Si eres docente, también te sirve
para tu horario personal: escribe el grupo junto a la materia (<code>Mates 2.ºB</code>) y las guardias o reuniones en los
huecos.</p>"""),
]

FAQ = [
    ("¿Cómo pongo una hora libre?",
     "Deja el hueco vacío entre dos comas o escribe un guion: «Lengua, -, Inglés». La celda sale en blanco."),
    ("¿Puedo añadir un segundo recreo o la comida?",
     "Sí, en «Más opciones»: «2.º recreo tras» indica después de qué sesión va y «2.º recreo» su duración en minutos."),
    ("¿Se puede imprimir en blanco y negro?",
     "Sí. Los colores salen muy suaves para que se lea bien en cualquier impresora; si tu navegador no imprime fondos, actívalo en «Más ajustes» del diálogo de impresión."),
    ("¿Se guarda mi horario?",
     "No se guarda en ningún servidor: va dentro del enlace. Pulsa «Copiar enlace» y guárdalo en favoritos o mándatelo para recuperarlo."),
    ("¿Sirve para horario de tarde o de academia?",
     "Sí: cualquier hora de entrada y duración de sesión entre 10 y 180 minutos, hasta 12 sesiones al día."),
]

INPUTS = [
    {"id": "tit", "type": "text", "label": "Título", "value": "1.º ESO A · 2026-2027", "w": "l", "maxlength": 60},
    {"id": "ini", "type": "time", "label": "Entrada", "value": "08:30"},
    {"id": "dur", "type": "number", "label": "Sesión", "value": 55, "unit": "min", "w": "s"},
    {"id": "ses", "type": "number", "label": "Sesiones", "value": 6, "w": "s"},
    {"id": "rec", "type": "number", "label": "Recreo tras", "value": 3, "unit": "ª", "w": "s"},
    {"id": "drec", "type": "number", "label": "Recreo", "value": 30, "unit": "min", "w": "s"},
] + [{"id": i, "type": "text", "label": lab, "value": val, "w": "xl"} for i, lab, val in DAYS] + [
    {"id": "rec2", "type": "number", "label": "2.º recreo tras", "value": "", "unit": "ª", "more": True, "w": "s"},
    {"id": "drec2", "type": "number", "label": "2.º recreo", "value": 15, "unit": "min", "more": True, "w": "s"},
]

TOOL = {
    "slug": "horario-escolar",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "table",
    "order": 50,
    "name": "Horario escolar",
    "k": "plantilla horario clases imprimir pdf colegio instituto semanal docente",
    "title": "Horario escolar para imprimir: crea el tuyo gratis",
    "desc": "Crea un horario escolar semanal con horas, recreo y colores por materia, e imprímelo en A4 o guárdalo en PDF. Gratis y sin registro.",
    "h1": "Generador de horario escolar",
    "crumb": "Horario escolar",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": JS,
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("BOE · Real Decreto 157/2022, enseñanzas mínimas de Educación Primaria", "https://www.boe.es/buscar/act.php?id=BOE-A-2022-3296"),
                ("BOE · Real Decreto 217/2022, enseñanzas mínimas de la ESO", "https://www.boe.es/buscar/act.php?id=BOE-A-2022-4975")],
    "credits": [],
    "related": ["dias-lectivos-restantes", "fichas-tablas-multiplicar", "sopa-de-letras"],
    "tests": [
        ({}, {"n.end": "14:30", "n.total": 30, "n.h.Matemáticas": 4.583333}),
        ({"rec2": "5", "drec2": "15"}, {"n.end": "14:45"}),
        ({"lu": "Lengua, -, Inglés", "ma": "", "mi": "", "ju": "", "vi": "", "ses": "3"}, {"n.total": 2}),
        ({"dur": "5"}, {"err": "La sesión tiene que durar entre 10 y 180 minutos."}),
        ({"ini": ""}, {"err": "Escribe la hora de entrada."}),
    ],
}
