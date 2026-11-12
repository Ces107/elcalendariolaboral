"""Nota media ponderada por créditos: the average of a university transcript as RD 1125/2003 art. 5.3 defines it
(sum of credits x grade over the credits obtained), with MH typed as "MH" and an option to count failed subjects."""
from herramientas.tools._estudios import CAT, NUMS, js

BODY = r"""
  var mhv = v.mh >= 0 && v.mh <= 10 ? v.mh : 10;
  var raw = String(v.notas || '').replace(/\bm\.?\s?h\.?(?=\s|;|$)/gi, ' MH ');
  var tok = raw.split(/[;\s|]+/).filter(Boolean), g = [], isMH = [];
  tok.forEach(function (t) { if (/^MH,?$/.test(t)) { g.push(mhv); isMH.push(true); } else nums(t).forEach(function (x) { g.push(x); isMH.push(false); }); });
  var cr = nums(v.creditos), plain = !cr.length;
  if (!g.length) return { err: 'Escribe las notas separadas por espacios: 7,5 6 8,2 MH' };
  for (var i = 0; i < g.length; i++) if (!(g[i] >= 0 && g[i] <= 10)) return { err: 'La nota ' + (i + 1) + ' no está entre 0 y 10.' };
  if (plain) cr = g.map(function () { return 1; });
  if (cr.length !== g.length) return { err: g.length + ' notas y ' + cr.length + ' créditos: tiene que haber uno por asignatura.' };
  for (i = 0; i < cr.length; i++) if (!(cr[i] > 0 && cr[i] <= 100)) return { err: 'Los créditos de la asignatura ' + (i + 1) + ' no son válidos.' };
  var sum = 0, cs = 0, fail = 0, nfail = 0, simple = 0, n = 0;
  for (i = 0; i < g.length; i++) {
    if (g[i] < 5 && !v.susp) { fail += cr[i]; nfail++; continue; }
    sum += g[i] * cr[i]; cs += cr[i]; simple += g[i]; n++;
  }
  if (!cs) return { err: 'No hay ninguna asignatura aprobada: marca «Contar suspensos» para ver la media.' };
  var m = sum / cs, m2 = Math.round(m * 100 + 1e-9) / 100;
  var q = m2 >= 9 ? 'Sobresaliente' : m2 >= 7 ? 'Notable' : m2 >= 5 ? 'Aprobado' : 'Suspenso';
  var rows = [[plain ? 'Asignaturas' : 'Créditos en la media', H.num(cs, cs % 1 ? 1 : 0)], ['Suma nota × créditos', H.num(sum, 2)]];
  if (!plain) rows.push(['Media sin ponderar', H.num(simple / n, 2)]);
  if (nfail) rows.push(['Suspensos fuera', nfail + ' · ' + H.num(fail, fail % 1 ? 1 : 0) + (plain ? '' : ' créditos')]);
  if (isMH.indexOf(true) >= 0) rows.push(['Matrícula de honor', 'cuenta como ' + H.num(mhv, mhv % 1 ? 1 : 0)]);
  rows.push(['Media', H.num(m, 3), 'tot']);
  return { label: plain ? 'Nota media' : 'Nota media ponderada', big: H.num(m2, 2), sub: q + ' · ' + n + ' ' + H.plural(n, 'asignatura', 'asignaturas'),
    rows: rows, note: plain ? 'Sin créditos: media aritmética simple.' : '',
    n: { media: m, creditos: cs, fuera: nfail } };
"""

BLOCKS = [
    ("Cómo se calcula la nota media del expediente", """
<p>La nota media de un expediente universitario no es la media de las notas: cada asignatura pesa tanto como sus
<b>créditos ECTS</b>. Se multiplica cada nota por sus créditos, se suman esos productos y el total se divide entre los
créditos superados. Así lo fija el artículo 5.3 del Real Decreto 1125/2003 para todas las titulaciones oficiales: «suma
de los créditos obtenidos por el alumno multiplicados cada uno de ellos por el valor de las calificaciones que
correspondan, y dividida por el número de créditos totales obtenidos». Una optativa de 3 créditos mueve la media la mitad
que una troncal de 6.</p>
<p>Escribe las notas en el primer campo y los créditos en el segundo, en el mismo orden y separados por espacios (la coma
es la de los decimales: <code>7,5 6 8,2</code>). Si dejas vacío el de créditos, la herramienta hace la media simple, que es
la que se usa en Bachillerato o en una asignatura con varios exámenes del mismo peso.</p>"""),
    ("Un ejemplo con cinco asignaturas", """
<p>Un primer cuatrimestre con Cálculo 7,5 (6 créditos), Física 6 (6), Programación 8,2 (4,5), Inglés 9 (6) y
Estadística 5 (9). Los productos son 45, 36, 36,9, 54 y 45, que suman 216,9; los créditos suman 31,5. La media ponderada es
216,9 / 31,5 = <b>6,89</b>, Aprobado alto. La media simple de esas cinco notas sería 7,14: la diferencia viene de que el
5 de Estadística pesa 9 créditos.</p>
<p>Si además hubiera un 4 en Química (6 créditos), por defecto no entra en la media, porque el real decreto habla de
créditos <i>obtenidos</i>. Algunas convocatorias (ciertas becas, rankings de movilidad) sí cuentan los suspensos: con
«Contar suspensos» la media baja a 240,9 / 37,5 = 6,42.</p>"""),
    ("Matrícula de honor, convalidaciones y escalas", """
<p>La matrícula de honor solo puede darse con un 9 o más y como mucho al 5 % del grupo (art. 5.6). El real decreto no le
asigna un número propio, así que cada universidad la computa a su manera: en la mayoría vale 10 en la media; escribe
<code>MH</code> en su lugar y, si tu universidad usa otro valor, cámbialo en «Más opciones».</p>
<p>Los créditos reconocidos por actividades formativas sin nota (prácticas extracurriculares, idiomas, voluntariado) no
cuentan en la media (art. 5.5): no los escribas. Las asignaturas convalidadas suelen llevar la nota de origen, que sí
cuenta. La escala cualitativa es la del artículo 5.4: suspenso por debajo de 5, aprobado de 5 a 6,9, notable de 7 a 8,9
y sobresaliente de 9 a 10.</p>"""),
]

FAQ = [
    ("¿Cuentan los suspensos en la nota media?",
     "En la media oficial del expediente no: el RD 1125/2003 divide entre los créditos obtenidos, es decir, superados. Cuando "
     "apruebas la asignatura, entra con la nota del aprobado. Algunas becas y procesos de movilidad sí los cuentan: marca «Contar suspensos»."),
    ("¿Cuánto vale una matrícula de honor en la media?",
     "Normalmente 10, aunque el real decreto no le da un valor numérico propio y alguna universidad la computa con su nota real. "
     "Escribe MH y ajusta su valor en «Más opciones» si tu normativa dice otra cosa."),
    ("¿Cómo pongo las notas y los créditos?",
     "En el mismo orden, separados por espacios o punto y coma: notas «7,5 6 8,2» y créditos «6 6 4,5». La coma es decimal; "
     "si escribes con punto (7.5) también se entiende."),
    ("¿Sirve para la media de Bachillerato?",
     "Sí: deja vacío el campo de créditos y obtendrás la media aritmética. Para la PAU se usa la media de todas las materias de "
     "Bachillerato salvo Religión."),
    ("¿Por qué mi media en la secretaría es distinta?",
     "Suele deberse a reconocimientos sin nota, a asignaturas de otra titulación incluidas en el expediente o a otro valor de "
     "la matrícula de honor. El certificado académico oficial es el que vale."),
]

TOOL = {
    "slug": "nota-media-ponderada",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "calculator",
    "order": 10,
    "name": "Nota media ponderada",
    "k": "media expediente creditos ects universidad matricula de honor beca",
    "title": "Calcular nota media ponderada por créditos",
    "desc": "Calcula la nota media de tu expediente universitario ponderada por créditos ECTS, con matrícula de honor y la opción de contar suspensos.",
    "h1": "Nota media ponderada por créditos",
    "crumb": "Nota media",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "notas", "type": "text", "label": "Notas", "value": "7,5 6 8,2 9 5", "w": "xl", "placeholder": "7,5 6 8,2 MH"},
        {"id": "creditos", "type": "text", "label": "Créditos", "value": "6 6 4,5 6 9", "w": "xl", "placeholder": "6 6 4,5 6"},
        {"id": "susp", "type": "check", "label": "Contar suspensos", "value": False, "more": True},
        {"id": "mh", "type": "number", "label": "MH vale", "value": 10, "more": True, "w": "s", "step": "0.1"},
    ],
    "js": js(BODY, NUMS),
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("BOE · Real Decreto 1125/2003, art. 5 (sistema de calificaciones y media del expediente)", "https://www.boe.es/buscar/act.php?id=BOE-A-2003-17643")],
    "credits": [],
    "related": ["nota-necesaria-examen", "notas-erasmus-ects", "nota-acceso-universidad"],
    "tests": [
        ({}, {"n.media": 6.885714, "n.creditos": 31.5}),
        ({"notas": "7,5 6 8,2 9 5 4", "creditos": "6 6 4,5 6 9 6"}, {"n.media": 6.885714, "n.fuera": 1}),
        ({"notas": "7,5 6 8,2 9 5 4", "creditos": "6 6 4,5 6 9 6", "susp": "1"}, {"n.media": 6.424}),
        ({"notas": "MH 8", "creditos": "6; 6"}, {"n.media": 9}),
        ({"notas": "7.5, 6, 9", "creditos": ""}, {"n.media": 7.5}),
        ({"notas": "7 11", "creditos": "6 6"}, {"err": "La nota 2 no está entre 0 y 10."}),
    ],
}
