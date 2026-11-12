"""Nota necesaria en el examen final: the grade the final exam needs for a target course grade, given the current
average and the weight of the final. need = (target - current x (1 - w)) / w, with an optional minimum on the final."""
from herramientas.tools._estudios import CAT

JS = r"""
function (v, H, C) {
  var mx = v.max > 0 ? v.max : 10, w = v.peso / 100, cur = v.actual, obj = v.obj;
  if (!(w > 0 && w <= 1)) return { err: 'El peso del final tiene que estar entre 1 y 100 %.' };
  if (!(cur >= 0 && cur <= mx) && w < 1) return { err: 'La nota actual tiene que estar entre 0 y ' + H.num(mx, 0) + '.' };
  if (!(obj >= 0 && obj <= mx)) return { err: 'La nota deseada tiene que estar entre 0 y ' + H.num(mx, 0) + '.' };
  if (w === 1) cur = 0;
  var need = (obj - cur * (1 - w)) / w, minf = v.minf >= 0 && v.minf <= mx ? v.minf : null, why = '';
  if (minf !== null && need < minf) { need = minf; why = 'Te lo exige el mínimo del final.'; }
  var big, sub, lab = 'Necesitas en el final';
  if (need > mx + 1e-9) { big = 'Imposible'; sub = 'Haría falta un ' + H.num(need, 2) + ' sobre ' + H.num(mx, 0) + '. Con un ' + H.num(mx, 0) + ' llegarías a ' + H.num(cur * (1 - w) + mx * w, 2) + '.'; }
  else if (need <= 0) { big = '0'; sub = 'Ya lo tienes: con un 0 en el final sacarías ' + H.num(cur * (1 - w), 2) + '.'; }
  else { big = H.num(Math.ceil(need * 100 - 1e-9) / 100, 2); sub = 'sobre ' + H.num(mx, 0) + ' · el final vale el ' + H.num(v.peso, v.peso % 1 ? 1 : 0) + ' %' + (why ? ' · ' + why : ''); }
  var rows = [], step = mx / 10;
  for (var k = 0; k <= 10; k++) {
    var f = step * k, tot = cur * (1 - w) + f * w, okm = minf === null || f >= minf;
    rows.push(['Si sacas ' + H.num(f, step % 1 ? 1 : 0), (okm ? H.num(tot, 2) : 'no aprueba (mínimo)'), okm && tot >= obj - 1e-9 ? 'tot' : 'z']);
  }
  return { label: lab, big: big, sub: sub, rows: rows,
    note: 'Nota final = actual × ' + H.num(1 - w, 2) + ' + final × ' + H.num(w, 2) + '.',
    n: { need: need } };
}
"""

BLOCKS = [
    ("Qué nota necesito en el examen final", """
<p>Escribe tu nota media hasta ahora (parciales, prácticas, trabajos), cuánto vale el examen final sobre la nota de la
asignatura y la nota que quieres sacar. La herramienta te da la <b>nota mínima que necesitas en el final</b> y una tabla con
la nota de la asignatura que resultaría con cada nota del examen, de 0 a 10, marcando las que llegan a tu objetivo.</p>
<p>La fórmula es la de cualquier media ponderada, despejada: si el final pesa <i>w</i>, la nota de la asignatura es
nota actual × (1 − <i>w</i>) + final × <i>w</i>; para llegar a un objetivo <i>N</i> hace falta un final de
(<i>N</i> − actual × (1 − <i>w</i>)) / <i>w</i>. Si sale más de 10, el objetivo ya no es alcanzable; si sale menos de 0,
lo tienes aunque no te presentes (salvo que la guía docente exija presentarse o una nota mínima).</p>"""),
    ("Ejemplos con números", """
<p>Llevas un 6 de media en la evaluación continua y el final vale el 40 %. Para aprobar con un 5 necesitas
(5 − 6 × 0,6) / 0,4 = (5 − 3,6) / 0,4 = <b>3,5</b>. Para un notable (7): (7 − 3,6) / 0,4 = 8,5. Para un sobresaliente (9)
haría falta un 13,5, imposible: con un 10 en el final llegarías a 7,6.</p>
<p>Muchas guías docentes añaden una condición: sacar al menos un 4 (o un 5) en el examen final para que haga media.
Escríbelo en «Mínimo en el final». En el ejemplo anterior, aunque para aprobar baste un 3,5, la herramienta te dirá que
necesitas un 4, y la tabla marcará como suspensas las filas por debajo de ese mínimo.</p>"""),
    ("Otras escalas y varios exámenes", """
<p>Si tu escala no es de 0 a 10 (de 0 a 20 en algunos másteres, de 0 a 100 en exámenes de idiomas), cámbiala en «Nota
máxima» y todo se recalcula en esa escala. Si te quedan dos exámenes del mismo peso, suma sus pesos y el resultado es la
media que necesitas entre los dos. Y si tu nota actual es una mezcla de partes con pesos distintos, calcúlala antes con la
<a href="/utilidades/nota-media-ponderada/">nota media ponderada</a> usando los porcentajes como créditos.</p>
<p>En la universidad la escala oficial es la de 0 a 10 con un decimal y el aprobado en 5 (Real Decreto 1125/2003, art. 5),
pero cómo se reparten los pesos y si hay nota mínima en el final lo decide la guía docente de cada asignatura: consúltala
antes de fiarte del cálculo.</p>"""),
]

FAQ = [
    ("¿Cómo calculo cuánto necesito sacar en el final?",
     "Resta a tu objetivo lo que ya tienes ponderado (nota actual × peso de lo hecho) y divide entre el peso del final. Con un 6, "
     "un final del 40 % y objetivo 5: (5 − 3,6) / 0,4 = 3,5."),
    ("¿Y si el resultado es mayor que 10?",
     "Entonces el objetivo no se puede alcanzar con ese final. La herramienta te dice la nota máxima a la que llegarías con un 10."),
    ("¿Qué pasa si hay nota mínima en el examen?",
     "Escríbela en «Mínimo en el final»: si con menos ya llegabas al objetivo, el resultado sube hasta ese mínimo, porque por debajo "
     "la asignatura queda suspensa aunque la media dé más de 5."),
    ("¿Sirve si el examen vale el 100 %?",
     "Sí: pon 100 % y la nota que necesitas es directamente tu objetivo. La nota actual no se usa."),
    ("¿Puedo usarlo en Bachillerato o en la ESO?",
     "Sí, siempre que tu profesor calcule la nota como una media ponderada. Si redondea al entero o usa otros criterios (actitud, "
     "evaluación continua), el resultado es solo orientativo."),
]

TOOL = {
    "slug": "nota-necesaria-examen",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "target-arrow",
    "order": 20,
    "name": "Nota para el final",
    "k": "que nota necesito para aprobar examen final porcentaje calculadora",
    "title": "¿Qué nota necesito en el examen final para aprobar?",
    "desc": "Calcula qué nota necesitas en el examen final para aprobar o sacar un notable, según tu nota actual y lo que vale el final.",
    "h1": "Qué nota necesito en el examen final",
    "crumb": "Nota necesaria",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "actual", "type": "number", "label": "Nota actual", "value": 6, "w": "s", "step": "0.01"},
        {"id": "peso", "type": "number", "label": "Peso del final", "value": 40, "unit": "%", "w": "s"},
        {"id": "obj", "type": "number", "label": "Nota deseada", "value": 5, "w": "s", "step": "0.01"},
        {"id": "minf", "type": "number", "label": "Mínimo en el final", "value": "", "more": True, "w": "s", "step": "0.1"},
        {"id": "max", "type": "number", "label": "Nota máxima", "value": 10, "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("BOE · Real Decreto 1125/2003, art. 5 (escala de 0 a 10, aprobado en 5)", "https://www.boe.es/buscar/act.php?id=BOE-A-2003-17643")],
    "credits": [],
    "related": ["nota-media-ponderada", "nota-acceso-universidad", "notas-erasmus-ects"],
    "tests": [
        ({}, {"n.need": 3.5}),
        ({"obj": "7"}, {"n.need": 8.5}),
        ({"obj": "9"}, {"big": "Imposible"}),
        ({"minf": "4"}, {"n.need": 4}),
        ({"peso": "100", "actual": "", "obj": "5"}, {"n.need": 5}),
        ({"peso": "0"}, {"err": "El peso del final tiene que estar entre 1 y 100 %."}),
    ],
}
