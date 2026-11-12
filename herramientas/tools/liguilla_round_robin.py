"""Liguilla todos contra todos (round robin): circle method (Berger tables) with balanced home/away (n-2 breaks, the
minimum), rest slot for odd numbers, one or two legs, dates per round + .ics, printable. EN twin: round-robin-generator."""
from herramientas.tools import _deporte as D

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  var T = EN ? {
    t: 'Team', np: 'Enter 3 to 40 team or player names separated by commas, or just how many there are.', many: 'Up to 40 names.',
    dup: 'Repeated name: ', rd: 'Round', rest: 'Bye', rounds: 'rounds', matches: 'matches', teams: 'teams', leg2: 'Second leg',
    one: 'single round robin', two: 'home and away', every: 'Enter the days between rounds (1 to 60).', cal: 'Round robin', home: 'home'
  } : {
    t: 'Equipo', np: 'Escribe de 3 a 40 nombres de equipos o jugadores separados por comas, o solo cuántos son.', many: 'Como mucho 40 nombres.',
    dup: 'Nombre repetido: ', rd: 'Jornada', rest: 'Descansa', rounds: 'jornadas', matches: 'partidos', teams: 'equipos', leg2: 'Segunda vuelta',
    one: 'a una vuelta', two: 'ida y vuelta', every: 'Indica cada cuántos días hay jornada (de 1 a 60).', cal: 'Liguilla', home: 'en casa'
  };
  var MON = EN ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] : ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  var WD = EN ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] : ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom'];
  %RND%
  var raw = String(v.equipos).split(/[,;\n]+/).map(function (s) { return s.trim().replace(/\s+/g, ' '); }).filter(Boolean), names;
  if (raw.length === 1 && /^\d+$/.test(raw[0])) { names = []; for (var q = 1; q <= +raw[0] && q <= 99; q++) names.push(T.t + ' ' + q); }
  else names = raw;
  var N = names.length;
  if (N < 3) return { err: T.np };
  if (N > 40) return { err: T.many };
  var low = names.map(function (s) { return s.toLowerCase(); });
  for (var i = 0; i < N; i++) if (low.indexOf(low[i]) !== i) return { err: T.dup + H.esc(names[i]) };
  var two = v.vueltas === '2', every = isNaN(v.cada) ? 7 : v.cada;
  if (v.inicio && !(every >= 1 && every <= 60 && every % 1 === 0)) return { err: T.every };
  var idx = []; for (i = 0; i < N; i++) idx.push(i);
  if (v.sorteo >= 0) idx = shuf(idx, rng(low.join('|') + '#' + v.sorteo));
  var n = N % 2 ? N + 1 : N, a = idx.slice();
  if (N % 2) a.push(-1);   /* -1 = bye */
  /* circle method: a[0] fixed, the rest rotate one place clockwise each round. Home side: the fixed team alternates,
     pair i (i > 0) is home for the left slot when i is odd: n - 2 breaks, the minimum for a single round robin */
  var rounds = [];
  for (var r = 0; r < n - 1; r++) {
    var ms = [], bye = null;
    for (i = 0; i < n / 2; i++) {
      var x = a[i], y = a[n - 1 - i], left = i === 0 ? r % 2 === 0 : i % 2 === 1, m = left ? [x, y] : [y, x];
      if (x < 0 || y < 0) bye = x < 0 ? y : x; else ms.push(m);
    }
    rounds.push({ m: ms, bye: bye });
    a = [a[0], a[n - 1]].concat(a.slice(1, n - 1));
  }
  if (two) for (r = 0; r < n - 1; r++) rounds.push({ m: rounds[r].m.map(function (m) { return [m[1], m[0]]; }), bye: rounds[r].bye, leg2: r === 0 });
  function nm(x) { return H.esc(names[x]); }
  function fd(d) { return WD[H.wd(d)] + ' ' + (EN ? MON[d.getUTCMonth()] + ' ' + d.getUTCDate() : d.getUTCDate() + ' ' + MON[d.getUTCMonth()]); }
  var h = '', ics = [], homeN = [], seq = [];
  for (i = 0; i < N; i++) { homeN.push(0); seq.push(''); }
  for (r = 0; r < rounds.length; r++) {
    var R = rounds[r], d = v.inicio ? H.add(v.inicio, r * every) : null, li = '';
    R.m.forEach(function (m) {
      homeN[m[0]]++; seq[m[0]] += 'H'; seq[m[1]] += 'A';
      li += '<tr><td>' + nm(m[0]) + '</td><td class="rr-v">–</td><td>' + nm(m[1]) + '</td><td class="rr-b"></td></tr>';
    });
    if (R.leg2) h += '<h3 class="rr-l">' + T.leg2 + '</h3>';
    h += '<div class="rr-j"><h4>' + T.rd + ' ' + (r + 1) + (d ? ' · <span>' + fd(d) + '</span>' : '') + '</h4><table class="tbl rr-t"><tbody>' + li + '</tbody></table>' +
      (R.bye !== null ? '<p class="rr-r">' + T.rest + ': ' + nm(R.bye) + '</p>' : '') + '</div>';
    if (d) ics.push('BEGIN:VEVENT\r\nUID:rr-' + r + '-' + H.icsDate(d) + '@elcalendariolaboral.es\r\nDTSTAMP:' + H.icsDate(d) + 'T000000Z\r\nDTSTART;VALUE=DATE:' + H.icsDate(d) +
      '\r\nDTEND;VALUE=DATE:' + H.icsDate(H.add(d, 1)) + '\r\nSUMMARY:' + H.icsEsc(T.rd + ' ' + (r + 1)) + '\r\nDESCRIPTION:' +
      H.icsEsc(R.m.map(function (m) { return names[m[0]] + ' - ' + names[m[1]]; }).join('\n') + (R.bye !== null ? '\n' + T.rest + ': ' + names[R.bye] : '')) + '\r\nEND:VEVENT');
  }
  var breaks = 0;
  seq.forEach(function (s) { for (var k = 1; k < s.length; k++) if (s[k] === s[k - 1]) breaks++; });
  var M = rounds.reduce(function (s, x) { return s + x.m.length; }, 0), last = v.inicio ? H.add(v.inicio, (rounds.length - 1) * every) : null;
  return {
    label: T.cal + ' · ' + (two ? T.two : T.one), big: rounds.length + ' ' + T.rounds,
    sub: N + ' ' + T.teams + ' · ' + M + ' ' + T.matches + (last ? ' · ' + fd(v.inicio) + ' → ' + fd(last) + ' ' + last.getUTCFullYear() : ''),
    html: h, print: true,
    ics: ics.length ? { name: (EN ? 'round-robin' : 'liguilla') + '.ics', text: 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//elcalendariolaboral.es//liguilla//ES\r\nCALSCALE:GREGORIAN\r\n' + ics.join('\r\n') + '\r\nEND:VCALENDAR\r\n' } : null,
    n: { rounds: rounds.length, matches: M, homeMin: Math.min.apply(null, homeN), homeMax: Math.max.apply(null, homeN), breaks: breaks,
         first: [names[rounds[0].m[0][0]], names[rounds[0].m[0][1]]], bye: rounds[0].bye === null ? null : names[rounds[0].bye], last: last ? H.iso(last) : null }
  };
}
"""

CSS = """
.rr-j{break-inside:avoid;margin:.2rem 0 .8rem}.rr-j h4{margin:.6rem 0 .3rem;font-size:.98rem}.rr-j h4 span{font-weight:400;color:var(--mut,#666)}
.rr-t td{padding:.3rem .45rem}.rr-t td:first-child{text-align:right;width:44%}.rr-v{width:1.2rem;text-align:center;color:var(--mut,#777)}
.rr-b{width:4.5rem}.rr-r{font-size:.9rem;color:var(--mut,#666);margin:.1rem 0}.rr-l{margin:1.2rem 0 .2rem;font-size:1.05rem}
@media print{.rr-b{border-bottom:1px solid #999}}
"""

INPUTS_ES = [
    {"id": "equipos", "type": "text", "label": "Equipos", "value": "Rojos, Azules, Verdes, Amarillos, Blancos, Negros", "w": "xl",
     "placeholder": "Rojos, Azules, Verdes… o 10"},
    {"id": "vueltas", "type": "seg", "label": "Vueltas", "value": "1", "options": [("1", "Una"), ("2", "Ida y vuelta")]},
    {"id": "inicio", "type": "date", "label": "Primera jornada", "value": ""},
    {"id": "cada", "type": "number", "label": "Cada", "value": "7", "unit": "días", "w": "s"},
    {"id": "sorteo", "type": "number", "label": "Sorteo nº", "value": "", "more": True, "w": "s"},
]


def blocks(ctx):
    return [
        ("Cuántas jornadas y partidos tiene una liguilla", """
<p>En una liguilla todos contra todos cada equipo juega una vez contra cada uno de los demás. Con <b>n</b> equipos hay
<b>n × (n − 1) / 2 partidos</b> repartidos en <b>n − 1 jornadas</b> si el número es par, o en <b>n jornadas</b> si es impar,
porque cada jornada descansa un equipo. Seis equipos juegan 15 partidos en 5 jornadas; siete equipos, 21 partidos en 7
jornadas con un descanso cada uno. A ida y vuelta se duplica todo: los seis equipos jugarían 30 partidos en 10 jornadas, y
en la segunda vuelta se repiten los cruces en el mismo orden con el campo cambiado.</p>
<p>Escribe los nombres separados por comas (o solo el número de equipos) y el calendario sale al momento. Si indicas la
fecha de la primera jornada, cada jornada lleva su fecha (por defecto, una por semana) y puedes descargar un .ics para
añadirlas al calendario del móvil, con los partidos en la descripción. «Imprimir o PDF» deja una hoja con huecos para
apuntar los resultados.</p>"""),
        ("Un ejemplo: liguilla de seis equipos", """
<p>Con Rojos, Azules, Verdes, Amarillos, Blancos y Negros, la primera jornada es Rojos–Negros, Azules–Blancos y
Amarillos–Verdes (el primero de cada partido juega en casa). En la segunda, Rojos sigue en su sitio y los demás giran una
posición: Blancos–Rojos, Negros–Amarillos y Verdes–Azules. Así, en cinco jornadas, todos se han cruzado con todos sin que se repita ningún partido.
Si la liguilla empieza el sábado 9 de enero de 2027 y se juega cada siete días, la última jornada cae el 6 de febrero.</p>"""),
        ("El método del círculo (tablas de Berger)", """
<p>El calendario sigue el método clásico que usan las federaciones para las ligas: se colocan los equipos en dos filas, el
primero se queda fijo y el resto gira una posición en cada jornada, como las agujas de un reloj. Con número impar se añade
un hueco de «descanso» que también gira, de modo que cada equipo descansa exactamente una jornada. Las tablas impresas que
usan los torneos de ajedrez son el mismo esquema, publicado por Johann Berger a finales del siglo XIX.</p>
<p>Además, el reparto de quién juega en casa está equilibrado: cada equipo juega en casa la mitad de los partidos (o uno
más o menos) y el número de veces que alguien repite casa o fuera en dos jornadas seguidas es el mínimo posible, n − 2 en
toda la liguilla. Si queréis otro orden de cruces, cambia el número de «Sorteo» en «Más opciones»: los equipos se barajan
antes de aplicar el método.</p>"""),
    ]


FAQ = [
    ("¿Cuántos partidos tiene una liguilla de 8 equipos?",
     "28 partidos en 7 jornadas, a 4 partidos por jornada. A ida y vuelta, 56 partidos en 14 jornadas."),
    ("¿Qué pasa si el número de equipos es impar?",
     "Cada jornada descansa un equipo, y todos descansan una vez por vuelta. Con 5 equipos hay 5 jornadas de 2 partidos y 10 partidos en total."),
    ("¿Cómo se hace la segunda vuelta?",
     "Con los mismos cruces y en el mismo orden que la primera, pero cambiando quién juega en casa. Es el formato habitual de las ligas."),
    ("¿Sirve para tenis, pádel, fútbol sala o juegos de mesa?",
     "Sí: escribe parejas, jugadores o equipos. Para tenis o pádel con pistas limitadas, cada jornada puede jugarse en varios turnos."),
    ("¿Se puede cambiar el orden de los partidos?",
     "Sí: escribe un número en «Sorteo nº» y los equipos se barajan antes de hacer el calendario. El mismo número da siempre el mismo calendario."),
]

TOOL = {
    "slug": "liguilla-round-robin",
    "lang": "es",
    "twin": "round-robin-generator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "calendar-week",
    "order": 20,
    "name": "Calendario de liguilla",
    "k": "liga todos contra todos round robin jornadas ida vuelta torneo calendario fútbol tenis",
    "title": "Calendario de liguilla todos contra todos (ida y vuelta)",
    "desc": "Genera el calendario de una liga todos contra todos: jornadas, descansos, ida y vuelta, fechas y .ics. Para fútbol, pádel, tenis o juegos.",
    "h1": "Calendario de liguilla todos contra todos",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Round-robin tournament · método del círculo y tablas de Berger (Wikipedia)", "https://en.wikipedia.org/wiki/Round-robin_tournament#Scheduling_algorithm")],
    "credits": [("Método del círculo / tablas de Berger (Johann Berger)", "dominio público (método)", "https://en.wikipedia.org/wiki/Round-robin_tournament#Berger_tables"),
                D.MULBERRY],
    "related": ["americano-padel", "cuadro-torneo"],
    "tests": [
        ({}, {"n.rounds": 5, "n.matches": 15, "n.homeMin": 2, "n.homeMax": 3, "n.breaks": 4, "n.first": ["Rojos", "Negros"]}),
        ({"equipos": "7"}, {"n.rounds": 7, "n.matches": 21, "n.bye": "Equipo 1"}),
        ({"vueltas": "2", "inicio": "2027-01-09"}, {"n.rounds": 10, "n.matches": 30, "n.last": "2027-03-13"}),
        ({"inicio": "2027-01-09"}, {"n.last": "2027-02-06"}),
        ({"equipos": "Ana, Luis"}, {"err": "Escribe de 3 a 40 nombres de equipos o jugadores separados por comas, o solo cuántos son."}),
        ({"equipos": "A, B, a"}, {"err": "Nombre repetido: a"}),
    ],
}
