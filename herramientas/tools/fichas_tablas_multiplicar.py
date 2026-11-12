"""Fichas de tablas de multiplicar: printable A4 worksheets (products, missing factor, divisions or a mix) drawn with a
seeded generator, so the same settings and sheet number always give the same sheet (a shared link reproduces it),
with a solutions page after a page break."""
from herramientas.tools._estudios import CAT, MULBERRY, RNG, js

BODY = r"""
  var T = [], bad = false;
  String(v.tablas || '').split(/[,;\s]+/).filter(Boolean).forEach(function (p) {
    var m = /^(\d{1,2})(?:-(\d{1,2}))?$/.exec(p);
    if (!m) { bad = true; return; }
    var a = +m[1], b = m[2] ? +m[2] : a;
    if (a > b) { var x = a; a = b; b = x; }
    for (var k = a; k <= b; k++) if (T.indexOf(k) < 0) T.push(k);
  });
  if (bad || !T.length) return { err: 'Escribe las tablas así: 2-9 o 3, 6, 7.' };
  if (T.some(function (t) { return t < 1 || t > 20; })) return { err: 'Tablas del 1 al 20.' };
  T.sort(function (a, b) { return a - b; });
  var n = v.n, hasta = v.hasta >= 1 ? Math.floor(v.hasta) : 10, ficha = v.ficha >= 1 ? Math.floor(v.ficha) : 1;
  if (!(n >= 1 && n <= 120) || n % 1) return { err: 'Entre 1 y 120 operaciones.' };
  if (hasta > 20) return { err: '«Hasta ×» como mucho 20.' };
  var R = seeded('tm|' + T.join(',') + '|' + v.tipo + '|' + n + '|' + hasta + '|' + ficha);
  var kinds = v.tipo === 'mix' ? ['mult', 'hueco', 'div'] : [v.tipo];
  var pool = T.length * hasta * kinds.length * (v.tipo === 'div' ? 1 : 2), seen = {}, ops = [], okAll = true;
  for (var i = 0; i < n; i++) {
    var op = null, last = null;
    for (var tries = 0; tries < 60 && !op; tries++) {
      var t = T[R.int(T.length)], m = 1 + R.int(hasta), kind = kinds[R.int(kinds.length)], sw = R.int(2) === 1, p = t * m, q, a;
      if (kind === 'mult') { q = sw ? m + ' × ' + t + ' =' : t + ' × ' + m + ' ='; a = p; }
      else if (kind === 'hueco') { q = sw ? '□ × ' + t + ' = ' + p : t + ' × □ = ' + p; a = m; }
      else { q = p + ' : ' + t + ' ='; a = m; }
      var key = q;
      last = { q: q, a: a, k: kind, t: t, m: m };
      if (seen[key] && (Object.keys(seen).length < pool || tries < 3)) continue;
      if (ops.length && ops[ops.length - 1].q === q && tries < 59) continue;
      seen[key] = 1; op = { q: q, a: a, k: kind, t: t, m: m };
    }
    if (!op) op = last;
    if (op.k === 'mult' ? op.a !== op.t * op.m : op.a !== op.m) okAll = false;
    ops.push(op);
  }
  function cell(o, sol) {
    var parts = o.q.split('□'), ans = sol ? '<b>' + o.a + '</b>' : '';
    if (parts.length > 1) return '<li>' + parts[0] + '<span class="tm-b">' + ans + '</span>' + parts[1] + '</li>';
    return '<li>' + o.q + ' <span class="tm-b">' + ans + '</span></li>';
  }
  var name = T.length === 1 ? 'Tabla del ' + T[0] : T.length > 2 && T[T.length - 1] - T[0] === T.length - 1 ? 'Tablas del ' + T[0] + ' al ' + T[T.length - 1] : 'Tablas del ' + T.join(', ').replace(/, (\d+)$/, ' y $1');
  var head = '<div class="tm-h"><span>Nombre: <i></i></span><span>Fecha: <i></i></span></div>';
  var foot = '<p class="tm-f">elcalendariolaboral.es/utilidades/fichas-tablas-multiplicar · ficha ' + ficha + '</p>';
  var html = '<div class="tm-sheet"><p class="tm-t">' + name + '</p>' + head + '<ol class="tm-g">' + ops.map(function (o) { return cell(o, false); }).join('') + '</ol>' + foot + '</div>' +
    '<div class="tm-sheet tm-sol"><p class="tm-t">Soluciones · ' + name + '</p><ol class="tm-g">' + ops.map(function (o) { return cell(o, true); }).join('') + '</ol>' + foot + '</div>' +
    '<p class="tm-np">' + NEWSEED + '</p>';
  return { label: 'Ficha nº ' + ficha, big: n + ' ' + H.plural(n, 'operación', 'operaciones'), sub: name + ' · con hoja de soluciones', html: html, print: true,
    n: { count: ops.length, first: ops[0].q, ok: okAll, tablas: T.length } };
"""

CSS = """
.tm-sheet{border:1px solid var(--line,#ccc);border-radius:6px;padding:1rem 1.1rem;margin:1rem 0;background:#fff;color:#111}
.tm-t{font-weight:700;font-size:1.2rem;margin:0 0 .6rem}
.tm-h{display:flex;gap:1.5rem;margin:0 0 1rem;font-size:.95rem}.tm-h span{flex:1;display:flex;gap:.4rem}.tm-h i{flex:1;border-bottom:1px solid #333}
.tm-g{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(9.5rem,1fr));gap:.9rem 1.2rem;
font-size:1.15rem;font-variant-numeric:tabular-nums}
.tm-g li{white-space:nowrap}.tm-b{display:inline-block;min-width:2.4em;border-bottom:1.5px solid #333;text-align:center;margin:0 .15em}
.tm-sol .tm-g{font-size:1rem}.tm-sol .tm-b b{color:#0a5}
.tm-f{margin:1rem 0 0;font-size:.7rem;color:#777}
@media print{.tm-np{display:none}.tm-sheet{border:0;padding:0;margin:0}.tm-g{grid-template-columns:repeat(4,1fr);gap:7mm 6mm;font-size:15pt}
.tm-sol{break-before:page;page-break-before:always}.tm-sol .tm-g{font-size:12pt;gap:4mm 6mm}.tm-t{font-size:16pt}}
"""

BLOCKS = [
    ("Fichas para practicar las tablas", """
<p>Elige qué tablas quieres repasar (<code>2-9</code>, <code>7</code> o <code>3, 6, 8</code>), el tipo de ejercicio y
cuántas operaciones, y la ficha aparece lista para imprimir en A4 con su <b>hoja de soluciones</b> en una página aparte.
Hay cuatro tipos: multiplicaciones normales (7 × 8 =), huecos para encontrar el factor que falta (7 × □ = 56), divisiones
exactas (56 : 7 =) y una mezcla de los tres. Los factores salen en los dos órdenes, 7 × 8 y 8 × 7, para que se aprenda que
el producto no cambia.</p>
<p>Cada ficha tiene un número. Con los mismos ajustes y el mismo número sale exactamente la misma ficha, así que el enlace
de «Copiar enlace» sirve para que toda la clase haga la misma o para repetirla otro día y comparar. Para una ficha nueva,
pulsa «Otra ficha» o cambia el número.</p>"""),
    ("Un ejemplo para 3.º de Primaria", """
<p>Una maestra quiere repasar las tablas del 6, 7 y 8, que son las que más cuestan, antes de empezar la división. Escribe
<code>6-8</code>, elige «Huecos» y 30 operaciones: le sale una ficha de 30 ejercicios del tipo 8 × □ = 48 o □ × 6 = 42.
La imprime para la clase y se guarda la hoja de soluciones para corregir. La semana siguiente usa «Mezcla» con la ficha
número 2 para combinar productos, huecos y divisiones de esas mismas tablas.</p>
<p>Un truco para corregir rápido: apunta el tiempo que tarda cada alumno y repite la misma ficha (mismo número) unas semanas
después. Si baja el tiempo y los errores, la tabla está aprendida; si se atasca siempre en la misma, prepara una ficha solo
de esa tabla en modo «Huecos».</p>"""),
    ("Por qué practicar así", """
<p>El currículo de Primaria (Real Decreto 157/2022) incluye en Matemáticas el cálculo mental y las estrategias de cálculo
con las cuatro operaciones, y las tablas de multiplicar son la base de las dos últimas. Practicarlas en orden ayuda al
principio, pero en orden aleatorio es como se comprueba que se saben de verdad: el alumno no puede contar de tres en tres
desde la fila anterior. Los huecos y las divisiones trabajan la misma tabla en sentido inverso, que es lo que se necesita
después para dividir y simplificar fracciones.</p>
<p>Las operaciones se eligen al azar sin repetirse mientras haya combinaciones distintas suficientes; si pides 60
operaciones de una sola tabla hasta × 10, solo hay unas 20 diferentes y algunas se repetirán.</p>"""),
]

FAQ = [
    ("¿Cómo saco otra ficha distinta?",
     "Pulsa «Otra ficha» debajo de la hoja o cambia el número de ficha. Con el mismo número y los mismos ajustes siempre sale la misma."),
    ("¿Dónde están las soluciones?",
     "En la segunda hoja, que al imprimir sale en una página aparte. Si no la quieres, elige imprimir solo la página 1 en el diálogo de impresión."),
    ("¿Puedo practicar hasta × 12?",
     "Sí: cambia «Hasta ×» a 12 (o hasta 20). Las tablas también pueden ir del 1 al 20."),
    ("¿Las divisiones tienen resto?",
     "No: todas son exactas, porque salen de invertir una multiplicación de la tabla (56 : 7 = 8)."),
    ("¿Puedo usarla en el ordenador sin imprimir?",
     "Sí, la ficha se ve en pantalla, pero está pensada para papel: escribir el resultado a mano ayuda a memorizar."),
]

TOOL = {
    "slug": "fichas-tablas-multiplicar",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "math-x-divide-y-2",
    "order": 60,
    "name": "Fichas de tablas",
    "k": "tablas de multiplicar fichas imprimir ejercicios primaria pdf divisiones huecos",
    "title": "Fichas de tablas de multiplicar para imprimir",
    "desc": "Genera fichas de tablas de multiplicar para imprimir: multiplicaciones, huecos y divisiones al azar, con hoja de soluciones. Gratis, en PDF.",
    "h1": "Fichas de tablas de multiplicar",
    "crumb": "Fichas de tablas",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "tablas", "type": "text", "label": "Tablas", "value": "2-9", "w": "s", "placeholder": "2-9"},
        {"id": "tipo", "type": "seg", "label": "Tipo", "value": "mult",
         "options": [("mult", "7 × 8"), ("hueco", "7 × □"), ("div", "56 : 7"), ("mix", "Mezcla")]},
        {"id": "n", "type": "number", "label": "Operaciones", "value": 40, "w": "s"},
        {"id": "hasta", "type": "number", "label": "Hasta ×", "value": 10, "w": "s"},
        {"id": "ficha", "type": "number", "label": "Ficha nº", "value": 1, "w": "s"},
    ],
    "js": js(BODY, RNG),
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("BOE · Real Decreto 157/2022, enseñanzas mínimas de Educación Primaria (Matemáticas: cálculo)", "https://www.boe.es/buscar/act.php?id=BOE-A-2022-3296")],
    "credits": [MULBERRY],
    "related": ["sopa-de-letras", "horario-escolar", "nota-necesaria-examen"],
    "tests": [
        ({}, {"n.count": 40, "n.ok": True, "n.tablas": 8, "n.first": "6 × 8 ="}),
        ({"ficha": "7"}, {"n.first": "5 × 9 ="}),
        ({"tablas": "3, 6, 7", "tipo": "mix", "n": "60"}, {"n.count": 60, "n.ok": True, "n.tablas": 3}),
        ({"tablas": "7", "tipo": "div", "n": "5", "hasta": "1"}, {"n.first": "7 : 7 ="}),
        ({"tablas": "abc"}, {"err": "Escribe las tablas así: 2-9 o 3, 6, 7."}),
        ({"n": "0"}, {"err": "Entre 1 y 120 operaciones."}),
    ],
}
