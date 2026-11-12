"""Nota de acceso y de admisión a la universidad (PAU, antes EBAU/EvAU), RD 534/2024 (BOE-A-2024-11858):
CFA = mean of the access exercises (art. 14, 3 decimals, >= 4), CAU = 0,6 x Bachillerato + 0,4 x CFA (art. 15, >= 5);
FP Técnico Superior: CAU = grade of the title (art. 23.2). Admission (art. 22.3): CAU + the two best weighted subjects.
The RD leaves the subjects and weights to each university: the weights (0, 0,1 or 0,2) and the >= 5 rule are typed by
the visitor as their university publishes them; no per-university table is embedded."""
from herramientas.tools._estudios import CAT

POND = [("0", "0"), ("0.1", "0,1"), ("0.2", "0,2")]

JS = r"""
function (v, H, C) {
  function r3(x) { return Math.round(x * 1000 + 1e-7) / 1000; }
  function ok(x) { return x >= 0 && x <= 10; }
  var fp = v.via === 'fp', rows = [], cau, cfa = null;
  if (fp) {
    if (!ok(v.nfp)) return { err: 'Escribe la nota del ciclo de FP (de 0 a 10).' };
    cau = r3(v.nfp);
    if (cau < 5) return { err: 'Con menos de un 5 en el ciclo no hay acceso.' };
    rows.push(['Nota del título de FP', H.num(cau, 3)]);
  } else {
    if (!ok(v.nmb)) return { err: 'Escribe la media de Bachillerato (de 0 a 10).' };
    var ex = [['Lengua', v.len], ['Historia o Filosofía', v.his], ['Lengua extranjera', v.ext], ['Materia de modalidad', v.mod]];
    if (!isNaN(v.coo)) ex.push(['Lengua cooficial', v.coo]);
    for (var i = 0; i < ex.length; i++) if (!ok(ex[i][1])) return { err: 'Falta la nota de ' + ex[i][0] + ' (de 0 a 10).' };
    cfa = r3(ex.reduce(function (s, x) { return s + x[1]; }, 0) / ex.length);
    rows.push(['Fase de acceso (media de ' + ex.length + ')', H.num(cfa, 3)]);
    if (cfa < 4) return { label: 'Sin acceso', big: H.num(cfa, 3), sub: 'La media de la fase de acceso tiene que llegar a 4.', rows: rows, n: { cfa: cfa, cau: null } };
    cau = r3(0.6 * v.nmb + 0.4 * cfa);
    rows.push(['60 % Bachillerato + 40 % fase', H.num(0.6 * v.nmb, 3) + ' + ' + H.num(0.4 * cfa, 3)]);
    if (cau < 5) return { label: 'Sin acceso', big: H.num(cau, 3), sub: 'La nota de acceso tiene que ser 5 o más.', rows: rows, n: { cfa: cfa, cau: cau } };
  }
  rows.push(['Nota de acceso', H.num(cau, 3), 'sub']);
  var cand = [];
  if (!fp && v.mod >= 5) cand.push(['Modalidad (fase de acceso)', v.mod, +v.pmod]);
  for (var k = 1; k <= 4; k++) {
    var g = v['m' + k], p = +v['p' + k];
    if (isNaN(g)) continue;
    if (!ok(g)) return { err: 'La materia ' + k + ' tiene que estar entre 0 y 10.' };
    cand.push(['Materia ' + k, g, p]);
  }
  var pts = cand.filter(function (c) { return c[1] >= 5 && c[2] > 0; }).map(function (c) { return [c[0], c[1], c[2], c[1] * c[2]]; })
    .sort(function (a, b) { return b[3] - a[3]; }).slice(0, 2);
  var add = 0;
  pts.forEach(function (c) { add += c[3]; rows.push([c[0] + ': ' + H.num(c[1], 2) + ' × ' + H.num(c[2], 1), '+' + H.num(c[3], 3)]); });
  var adm = r3(Math.min(14, cau + add));
  rows.push(['Nota de admisión', H.num(adm, 3), 'tot']);
  var skip = cand.filter(function (c) { return c[1] < 5 && c[2] > 0; }).length;
  return { label: 'Nota de admisión', big: H.num(adm, 3), sub: 'sobre 14 · acceso ' + H.num(cau, 3) + ' sobre 10', rows: rows,
    note: (skip ? 'Las materias con menos de un 5 no ponderan. ' : '') + (pts.length ? '' : 'Elige la ponderación de cada materia para tu grado (0,1 o 0,2) para sumar puntos. ') +
      'Las ponderaciones las publica cada universidad para cada grado.',
    n: { cfa: cfa, cau: cau, adm: adm } };
}
"""

BLOCKS = [
    ("Cómo se calcula la nota de la PAU", """
<p>La nota que sirve para entrar en la universidad tiene dos pisos. El primero es la <b>nota de acceso</b>, de 0 a 10: el
60 % de la media de Bachillerato más el 40 % de la media de los ejercicios de la fase de acceso de la PAU (Lengua
Castellana y Literatura II, Historia de España o Historia de la Filosofía, Lengua Extranjera II, la materia específica
obligatoria de tu modalidad y, en las comunidades con lengua cooficial, esa lengua). Lo fija el Real Decreto 534/2024 en
sus artículos 14 y 15: cada ejercicio se califica de 0 a 10, la media de la fase debe llegar a 4 y la nota de acceso, a 5.
Aprobada, vale para siempre.</p>
<p>El segundo es la <b>nota de admisión</b>, hasta 14, que es la que ordena a los candidatos cuando hay más solicitudes que
plazas. Se suman a la nota de acceso las notas de las dos materias que más te favorezcan multiplicadas por su
<b>ponderación</b> para ese grado (art. 22.3). Pueden ser materias de la fase de admisión (hasta tres más una segunda
lengua extranjera) o la materia de modalidad de la fase de acceso, y solo ponderan si tienen un 5 o más.</p>"""),
    ("Un ejemplo completo", """
<p>Una alumna de Ciencias con un 8,2 de media de Bachillerato saca en la fase de acceso 7 en Lengua, 6,5 en Historia,
8,5 en Inglés y 7,8 en Matemáticas II. La media de la fase es 29,8 / 4 = 7,450 y su nota de acceso,
0,6 × 8,2 + 0,4 × 7,45 = 4,920 + 2,980 = <b>7,900</b>.</p>
<p>Quiere estudiar un grado de ingeniería que pondera 0,2 Matemáticas II, Física y Química. En la fase de admisión saca un 8
en Física y un 6 en Química. Las dos mejores ponderadas son Física (8 × 0,2 = 1,6) y Matemáticas II (7,8 × 0,2 = 1,56), así
que su nota de admisión es 7,9 + 1,6 + 1,56 = <b>11,060</b>. Química no suma: solo cuentan las dos mejores. Para un grado
donde Física pondere solo 0,1, la misma alumna tendría otra nota de admisión: por eso la nota de admisión depende del grado.</p>"""),
    ("Las ponderaciones y la vía de FP", """
<p>El real decreto no dice qué materias ponderan ni cuánto: cada universidad (o la comisión de su comunidad) publica al
principio de cada curso su tabla de ponderaciones por grado (art. 22.4), y en la práctica los valores son 0,1 o 0,2. Por eso
aquí no hay tablas metidas: busca la de tu universidad, elige 0,1 o 0,2 en cada materia y la herramienta escoge las dos
mejores. Las notas de la fase de admisión valen el curso siguiente y los dos posteriores (art. 22.5).</p>
<p>Con un título de <b>Técnico Superior de FP</b> no hace falta la fase de acceso: la nota de acceso es la nota media del
título (art. 23.2), y se puede subir hasta 14 con las materias de la fase de admisión, igual que desde Bachillerato. Elige
«FP» arriba y escribe la nota del ciclo.</p>"""),
]

FAQ = [
    ("¿Cuál es la fórmula de la nota de acceso?",
     "Nota de acceso = 0,6 × media de Bachillerato + 0,4 × media de la fase de acceso, con tres decimales. Hace falta al menos un 4 de media en la fase y un 5 en el resultado."),
    ("¿Cómo llego a un 14?",
     "Con un 10 de acceso y dos materias de la fase de admisión con un 10 que ponderen 0,2 para ese grado: 10 + 2 + 2 = 14."),
    ("¿La materia de modalidad cuenta dos veces?",
     "Puede: hace media en la fase de acceso y, si sacas un 5 o más y tu grado la pondera, también puede ser una de las dos materias de la nota de admisión, sin volver a examinarte."),
    ("¿Cuenta la lengua extranjera de la fase de acceso para ponderar?",
     "No: para la nota de admisión solo cuenta una segunda lengua extranjera examinada en la fase de admisión."),
    ("¿Cuánto tiempo valen las notas?",
     "La nota de acceso no caduca. Las notas de las materias de la fase de admisión valen para el curso siguiente a la prueba y los dos siguientes."),
    ("¿Entra Religión en la media de Bachillerato?",
     "No: el artículo 15 del RD 534/2024 excluye la materia de Religión de la nota media de Bachillerato que se usa para la nota de acceso."),
]

INPUTS = [
    {"id": "via", "type": "seg", "label": "Vía", "value": "bach", "options": [("bach", "Bachillerato"), ("fp", "FP superior")]},
    {"id": "nmb", "type": "number", "label": "Media Bachillerato", "value": 8.2, "w": "s", "step": "0.01", "show": ("via", ["bach"])},
    {"id": "nfp", "type": "number", "label": "Nota del ciclo", "value": "", "w": "s", "step": "0.01", "show": ("via", ["fp"])},
    {"id": "len", "type": "number", "label": "Lengua", "value": 7, "w": "s", "step": "0.01", "show": ("via", ["bach"])},
    {"id": "his", "type": "number", "label": "Historia o Filosofía", "value": 6.5, "w": "s", "step": "0.01", "show": ("via", ["bach"])},
    {"id": "ext", "type": "number", "label": "Lengua extranjera", "value": 8.5, "w": "s", "step": "0.01", "show": ("via", ["bach"])},
    {"id": "mod", "type": "number", "label": "Materia de modalidad", "value": 7.8, "w": "s", "step": "0.01", "show": ("via", ["bach"])},
    {"id": "pmod", "type": "select", "label": "Ponderación", "value": "0.2", "options": POND, "w": "s", "show": ("via", ["bach"])},
    {"id": "coo", "type": "number", "label": "Lengua cooficial", "value": "", "w": "s", "step": "0.01", "show": ("via", ["bach"])},
]
for k, (g, p) in enumerate([(8, "0.2"), (6, "0.2"), ("", "0.1"), ("", "0.1")], 1):
    INPUTS += [{"id": f"m{k}", "type": "number", "label": f"Materia {k}", "value": g, "w": "s", "step": "0.01"},
               {"id": f"p{k}", "type": "select", "label": "Ponderación", "value": p, "options": POND, "w": "s"}]

TOOL = {
    "slug": "nota-acceso-universidad",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "school",
    "order": 30,
    "name": "Nota de la PAU",
    "k": "selectividad ebau evau pau nota de admision ponderaciones 14 nota de corte",
    "title": "Calcular nota de la PAU y nota de admisión (sobre 14)",
    "desc": "Calcula tu nota de acceso y de admisión a la universidad con la fórmula oficial de la PAU (RD 534/2024): 60 % Bachillerato, 40 % fase y ponderaciones.",
    "h1": "Calcular la nota de la PAU",
    "crumb": "Nota PAU",
    "updated": "2026-11-12",
    "inputs": INPUTS,
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("BOE · Real Decreto 534/2024, arts. 14, 15, 22 y 23 (acceso y admisión)", "https://www.boe.es/buscar/act.php?id=BOE-A-2024-11858"),
                ("Universidad de Alcalá · Qué debo saber de la PAU 2026 (ponderaciones 0,1 / 0,2, mínimo 5)", "https://uah.es/export/sites/uah/es/admision-y-ayudas/.galleries/Descargas-Acceso/Que_debo_saber_de_la_PAU.pdf")],
    "credits": [],
    "related": ["nota-media-ponderada", "nota-necesaria-examen", "dias-lectivos-restantes"],
    "tests": [
        ({}, {"n.cfa": 7.45, "n.cau": 7.9, "n.adm": 11.06}),
        ({"nmb": "5,60", "len": "4.20", "his": "3.80", "ext": "6", "mod": "5.5", "m1": "", "m2": "", "pmod": "0"}, {"n.cfa": 4.875, "n.cau": 5.31, "n.adm": 5.31}),
        ({"nmb": "5", "len": "4.20", "his": "3.80", "ext": "6", "mod": "5.5"}, {"n.cau": 4.95, "label": "Sin acceso"}),
        ({"nmb": "10", "len": "10", "his": "10", "ext": "10", "mod": "10", "m1": "10", "m2": "10"}, {"n.adm": 14}),
        ({"via": "fp", "nfp": "8", "m1": "9", "p1": "0.2", "m2": "4", "p2": "0.2"}, {"n.cau": 8, "n.adm": 9.8}),
        ({"coo": "3", "m1": "", "m2": ""}, {"n.cfa": 6.56, "n.adm": 9.104}),
    ],
}
