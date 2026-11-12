"""Sopa de letras: a printable word search from the visitor's word list, Spanish alphabet (Ñ kept, accents dropped),
three levels of directions, drawn with a seeded generator so the same list, size, level and sheet number always give
the same puzzle (a shared link reproduces it), with a solutions page after a page break."""
from herramientas.tools._estudios import CAT, MULBERRY, RNG, js

BODY = r"""
  var MARKS = new RegExp('[' + String.fromCharCode(0x300) + '-' + String.fromCharCode(0x36f) + ']', 'g');
  var ABC = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ';
  function norm(w) { return w.toUpperCase().replace(/Ñ/g, '#').normalize('NFD').replace(MARKS, '').replace(/#/g, 'Ñ').replace(/[^A-ZÑ]/g, ''); }
  var N = v.tam, words = [], shown = [], seenW = {};
  if (!(N >= 6 && N <= 20) || N % 1) return { err: 'Tamaño entre 6 y 20.' };
  String(v.palabras || '').split(/[,;\n]+/).forEach(function (w) {
    var s = w.trim().replace(/\s+/g, ' '), k = norm(s);
    if (k.length >= 2 && !seenW[k]) { seenW[k] = 1; words.push(k); shown.push(s); }
  });
  if (!words.length) return { err: 'Escribe palabras separadas por comas.' };
  if (words.length > 40) return { err: 'Como mucho 40 palabras.' };
  var D = [[0, 1], [1, 0]];
  if (v.nivel !== 'facil') D = D.concat([[1, 1], [-1, 1]]);
  if (v.nivel === 'dificil') D = D.concat([[0, -1], [-1, 0], [-1, -1], [1, -1]]);
  var ficha = v.ficha >= 1 ? Math.floor(v.ficha) : 1;
  var R = seeded('sl|' + words.join(',') + '|' + N + '|' + v.nivel + '|' + ficha);
  var g = [], i, j;
  for (i = 0; i < N; i++) { g.push([]); for (j = 0; j < N; j++) g[i].push(''); }
  var idx = words.map(function (w, k) { return k; }).sort(function (a, b) { return words[b].length - words[a].length || a - b; });
  var cells = {}, miss = [], placed = 0;
  idx.forEach(function (k) {
    var w = words[k], L = w.length, done = false;
    for (var t = 0; t < 400 && !done; t++) {
      var d = D[R.int(D.length)], r = R.int(N), c = R.int(N), er = r + d[0] * (L - 1), ec = c + d[1] * (L - 1);
      if (er < 0 || er >= N || ec < 0 || ec >= N) continue;
      var fit = true;
      for (var q = 0; q < L && fit; q++) { var x = g[r + d[0] * q][c + d[1] * q]; if (x && x !== w[q]) fit = false; }
      if (!fit) continue;
      for (q = 0; q < L; q++) { g[r + d[0] * q][c + d[1] * q] = w[q]; cells[(r + d[0] * q) + ',' + (c + d[1] * q)] = 1; }
      done = true; placed++;
    }
    if (!done) miss.push(shown[k]);
  });
  for (i = 0; i < N; i++) for (j = 0; j < N; j++) if (!g[i][j]) g[i][j] = ABC[R.int(ABC.length)];
  function grid(sol) {
    return '<table class="sl-g" style="--n:' + N + '"><tbody>' + g.map(function (row, a) {
      return '<tr>' + row.map(function (ch, b) { return '<td' + (sol && cells[a + ',' + b] ? ' class="on"' : '') + '>' + ch + '</td>'; }).join('') + '</tr>';
    }).join('') + '</tbody></table>';
  }
  var list = '<ul class="sl-w">' + shown.filter(function (s) { return miss.indexOf(s) < 0; }).map(function (s) { return '<li>' + H.esc(s) + '</li>'; }).join('') + '</ul>';
  var title = H.esc(String(v.tit || '').trim() || 'Sopa de letras');
  var foot = '<p class="sl-f">elcalendariolaboral.es/utilidades/sopa-de-letras · ficha ' + ficha + '</p>';
  var html = '<div class="sl-sheet"><p class="sl-t">' + title + '</p>' + grid(false) + list + foot + '</div>' +
    '<div class="sl-sheet sl-sol"><p class="sl-t">Soluciones · ' + title + '</p>' + grid(true) + foot + '</div><p class="sl-np">' + NEWSEED + '</p>';
  return { label: 'Ficha nº ' + ficha, big: placed + ' ' + H.plural(placed, 'palabra', 'palabras'), sub: N + ' × ' + N + ' · ' + ({ facil: 'fácil', normal: 'normal', dificil: 'difícil' }[v.nivel] || ''),
    html: html, print: true,
    note: miss.length ? 'No caben: ' + miss.map(H.esc).join(', ') + '. Sube el tamaño o quita palabras.' : '',
    n: { placed: placed, miss: miss.length, row0: g[0].join(''), words: words.join(',') } };
"""

CSS = """
.sl-sheet{border:1px solid var(--line,#ccc);border-radius:6px;padding:1rem;margin:1rem 0;background:#fff;color:#111}
.sl-t{font-weight:700;font-size:1.2rem;margin:0 0 .7rem;text-align:center}
.sl-g{border-collapse:collapse;margin:0 auto;font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:700}
.sl-g td{width:calc(min(100vw - 5.5rem,34rem) / var(--n));height:calc(min(100vw - 5.5rem,34rem) / var(--n));text-align:center;padding:0;
font-size:calc(min(100vw - 5.5rem,34rem) / var(--n) * .58);border:1px solid #ddd}
.sl-g td.on{background:#ffe27a}
.sl-w{list-style:none;padding:0;margin:1rem auto 0;max-width:34rem;columns:3 8rem;font-size:1rem}.sl-w li{padding:.1rem 0;text-transform:uppercase}
.sl-f{margin:1rem 0 0;font-size:.7rem;color:#777;text-align:center}
@media print{.sl-np{display:none}.sl-sheet{border:0;padding:0;margin:0}
.sl-g td{width:calc(180mm / var(--n));height:calc(180mm / var(--n));font-size:calc(180mm / var(--n) * .55);border-color:#bbb}
.sl-g td.on{-webkit-print-color-adjust:exact;print-color-adjust:exact}
.sl-w{max-width:none;columns:4;font-size:12pt}.sl-t{font-size:18pt}.sl-sol{break-before:page;page-break-before:always}}
"""

BLOCKS = [
    ("Cómo crear tu sopa de letras", """
<p>Escribe las palabras separadas por comas, elige el tamaño de la cuadrícula y la dificultad, y la sopa de letras aparece
lista para imprimir en A4, con la lista de palabras debajo y una <b>hoja de soluciones</b> en otra página con las palabras
resaltadas. En «Fácil» las palabras van solo de izquierda a derecha y de arriba abajo; en «Normal» también en diagonal; en
«Difícil», además, del revés. Las tildes se quitan (en las sopas de letras impresas no se suelen poner) pero la Ñ se
mantiene, y las letras de relleno se eligen entre las 27 del abecedario español.</p>
<p>Cada sopa tiene un número de ficha: con las mismas palabras, tamaño, dificultad y número sale siempre la misma, así que el
enlace de «Copiar enlace» sirve para compartirla con la clase o con la familia. Si quieres otra distribución con las mismas
palabras, pulsa «Otra ficha».</p>"""),
    ("Un ejemplo para Infantil y Primaria", """
<p>Para una unidad sobre animales de la granja en 1.º de Primaria: diez palabras (gato, perro, conejo, tortuga, loro,
caballo, oveja, vaca, cerdo, pato) en una cuadrícula de 12 × 12 en modo «Normal». La palabra más larga, CABALLO, tiene siete
letras y cabe de sobra. Para Infantil conviene bajar a 8 × 8 con cinco o seis palabras cortas en modo «Fácil», y para el
último ciclo de Primaria o la ESO, 15 × 15 o más en «Difícil» con vocabulario de la asignatura: los ríos de España, los
huesos del cuerpo o los verbos irregulares en inglés.</p>
<p>Una buena proporción es que las letras de las palabras ocupen menos de la mitad de las casillas: en una cuadrícula de
12 × 12 (144 casillas) caben con holgura entre 10 y 15 palabras de cinco o seis letras.</p>"""),
    ("Para qué sirve en clase", """
<p>Buscar palabras obliga a fijarse en el orden exacto de las letras, así que refuerza la ortografía y el vocabulario de un
tema sin que parezca un ejercicio. El currículo de Primaria (Real Decreto 157/2022) incluye en Lengua Castellana el
conocimiento del vocabulario y la ortografía, y una sopa de letras con las palabras de la unidad es un repaso rápido para el
final de la clase o para casa. Si una palabra no cabe, la herramienta lo avisa debajo en lugar de cortarla: sube el
tamaño o quita alguna.</p>"""),
]

FAQ = [
    ("¿Puedo poner palabras con tilde o con ñ?",
     "Sí. Las tildes se quitan al colocarlas en la cuadrícula (CAMIÓN se busca como CAMION) y la Ñ se respeta como una letra más."),
    ("¿Y palabras de dos palabras, como «oso polar»?",
     "Se colocan juntas, sin el espacio (OSOPOLAR); en la lista de abajo aparecen tal como las escribiste."),
    ("¿Cuántas palabras caben?",
     "Hasta 40. Depende del tamaño: en 12 × 12 caben cómodas unas 10-15 palabras medianas. Si alguna no cabe, se avisa."),
    ("¿Cómo imprimo sin las soluciones?",
     "En el diálogo de impresión elige solo la página 1; las soluciones van siempre en la página 2."),
    ("¿Se guardan mis palabras?",
     "No en ningún servidor: van dentro del enlace. Con «Copiar enlace» puedes guardarla o compartirla y se abrirá igual."),
]

TOOL = {
    "slug": "sopa-de-letras",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "abc",
    "order": 70,
    "name": "Sopa de letras",
    "k": "generador sopa de letras imprimir pdf palabras infantil primaria crear",
    "title": "Generador de sopa de letras para imprimir gratis",
    "desc": "Crea una sopa de letras con tus palabras: tamaño, dificultad y hoja de soluciones, lista para imprimir o guardar en PDF. Gratis y sin registro.",
    "h1": "Generador de sopa de letras",
    "crumb": "Sopa de letras",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "palabras", "type": "text", "label": "Palabras", "value": "gato, perro, conejo, tortuga, loro, caballo, oveja, vaca, cerdo, pato",
         "w": "xl", "placeholder": "gato, perro, conejo…"},
        {"id": "tam", "type": "number", "label": "Tamaño", "value": 12, "unit": "×", "w": "s"},
        {"id": "nivel", "type": "seg", "label": "Dificultad", "value": "normal",
         "options": [("facil", "Fácil"), ("normal", "Normal"), ("dificil", "Difícil")]},
        {"id": "ficha", "type": "number", "label": "Ficha nº", "value": 1, "w": "s"},
        {"id": "tit", "type": "text", "label": "Título", "value": "", "more": True, "maxlength": 50, "placeholder": "Animales de la granja"},
    ],
    "js": js(BODY, RNG),
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("BOE · Real Decreto 157/2022, enseñanzas mínimas de Educación Primaria (Lengua: vocabulario y ortografía)", "https://www.boe.es/buscar/act.php?id=BOE-A-2022-3296")],
    "credits": [MULBERRY],
    "related": ["fichas-tablas-multiplicar", "horario-escolar", "amigo-invisible"],
    "tests": [
        ({}, {"n.placed": 10, "n.miss": 0}),
        ({"palabras": "camión, niño, oso polar", "tam": "8"}, {"n.words": "CAMION,NIÑO,OSOPOLAR", "n.placed": 3}),
        ({"palabras": "murcielaguito", "tam": "8"}, {"n.miss": 1, "n.placed": 0}),
        ({"palabras": ", ,"}, {"err": "Escribe palabras separadas por comas."}),
        ({"tam": "30"}, {"err": "Tamaño entre 6 y 20."}),
    ],
}
