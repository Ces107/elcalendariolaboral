"""Días de asuntos propios (moscosos), días por antigüedad (canosos) and vacation days of AGE staff in a given year."""

RES = "https://www.boe.es/buscar/act.php?id=BOE-A-2026-8287"
EBEP = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11719"
CAL27 = "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-21254"

# National holidays that no comunidad can replace (RD 2001/1983 art. 45.1 a-c; marked * in the BOE yearly list). Viernes Santo
# is never a Saturday, so the fixed dates are enough.
FIXED = ["01-01", "05-01", "08-15", "10-12", "11-01", "12-06", "12-08", "12-25"]

JS = r"""
function (v, H, C) {
  var FIX = C.d.fix, DN = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
  function addY(d, n) { var y = d.getUTCFullYear() + n, m = d.getUTCMonth(); return new Date(Date.UTC(y, m, Math.min(d.getUTCDate(), H.monthDays(y, m + 1)))); }
  function fd(d) { return ('0' + d.getUTCDate()).slice(-2) + '/' + ('0' + (d.getUTCMonth() + 1)).slice(-2) + '/' + d.getUTCFullYear(); }
  var s = v.inicio, Y = +v.ano;
  if (!s) return { err: 'Elige la fecha de inicio de tus servicios.' };
  var last = new Date(Date.UTC(Y, 11, 30)); /* completed by 30 Dec: usable from the next day, still in the year */
  if (s > last) return { err: 'La fecha de inicio es posterior a ese año.' };
  var yrs = 0;
  while (addY(s, yrs + 1) <= last) yrs++;
  var t = Math.floor(yrs / 3), tri = t >= 6 ? 2 + Math.max(0, t - 7) : 0;
  var since = function (years) { var d = H.add(addY(s, years), 1); return d.getUTCFullYear() === Y ? ' desde ' + fd(d) : ''; };
  var d24 = new Date(Date.UTC(Y, 11, 24)), dec = H.wd(d24) >= 5 ? 2 : 0;
  var sat = FIX.filter(function (md) { return H.wd(H.parse(Y + '-' + md)) === 5; }), fes = sat.length ? 1 : 0;
  var vac = yrs >= 30 ? 26 : yrs >= 25 ? 25 : yrs >= 20 ? 24 : yrs >= 15 ? 23 : 22, vy = [0, 15, 20, 25, 30][vac - 22];
  var ap = 6 + tri + dec + fes;
  var rows = [
    ['Asuntos particulares', '6'],
    ['Por trienios · ' + t + ' ' + H.plural(t, 'trienio', 'trienios'), (tri ? '+' + tri + (t >= 6 ? since(3 * (t >= 8 ? t : 6)) : '') : '0')],
    ['24 y 31 de diciembre', dec ? '+2 · caen en ' + DN[H.wd(d24)] : '0'],
    ['Festivo nacional en sábado', fes ? '+1 · ' + sat.map(function (md) { return md.split('-').reverse().join('/'); }).join(', ') : '0'],
    ['Total días de permiso', String(ap), 'tot'],
    ['Vacaciones · ' + yrs + ' años', vac + ' días hábiles' + (vac > 22 ? since(vy) : ''), 'sub']
  ];
  return {
    label: 'Días de asuntos propios en ' + Y, big: ap,
    sub: '+ ' + vac + ' días hábiles de vacaciones · ' + (ap + vac) + ' en total',
    rows: rows,
    note: 'Reglas de la Administración General del Estado. Comunidades y ayuntamientos pueden tener las suyas.',
    n: { ap: ap, tri: tri, dec: dec, fes: fes, vac: vac, t: t, yrs: yrs }
  };
}
"""

BLOCKS = [
    ("Cuántos días te corresponden", f"""
<p>En la Administración General del Estado cada empleado público tiene <b>6 días de asuntos particulares</b> al año (los
«moscosos»), <b>2 más al cumplir el sexto trienio</b> y <b>uno más por cada trienio a partir del octavo</b> (los «canosos»). Cada año
se suman <b>2 días</b> si el 24 y el 31 de diciembre caen en sábado o domingo, y <b>1 día</b> si alguna fiesta nacional que las
comunidades no pueden cambiar cae en sábado. Las vacaciones son de <b>22 días hábiles</b>, que suben a 23, 24, 25 y 26 con 15, 20,
25 y 30 años de servicio. Todo ello está en la <a href="{RES}" rel="noopener">Resolución de 14 de abril de 2026</a> de la Secretaría
de Estado de Función Pública (apartados 9.1, 9.7 y 9.8), que sustituyó a la de 2019.</p>
<p>Los días por antigüedad se pueden usar desde el día siguiente a cumplir el trienio o los años, así que cuentan en el año en que
los cumples. La calculadora usa la fecha desde la que la administración te reconoce servicios, la misma de tus trienios.</p>"""),
    ("Ejemplo", """
<p>Un funcionario que empezó el 15 de enero de 2002 cumple 25 años de servicio el 15 de enero de 2027, y con ellos su octavo
trienio. En 2027 tiene 6 días de asuntos particulares, 3 por trienios (2 del sexto y 1 del octavo) y 1 más porque el 1 de mayo de
2027 cae en sábado: <b>10 días</b>. El 24 de diciembre de 2027 es viernes, así que no suma nada por Navidad. De vacaciones tiene
<b>25 días hábiles</b> desde el 16 de enero.</p>
<p>En 2028 el 24 y el 31 de diciembre caen en domingo y el 1 de enero en sábado: cualquier empleado del Estado suma 3 días más.</p>"""),
    ("Otras administraciones", f"""
<p>El <a href="{EBEP}#a48" rel="noopener">artículo 48.k) del Estatuto Básico del Empleado Público</a> garantiza los 6 días a todos los
empleados públicos. Las disposiciones adicionales <a href="{EBEP}#dadecimotercera" rel="noopener">decimotercera</a> y
<a href="{EBEP}#dadecimocuaa" rel="noopener">decimocuarta</a> permiten a cada administración dar <i>hasta</i> 2 días más en el sexto
trienio y uno por trienio desde el octavo, y <i>hasta</i> 4 días más de vacaciones por antigüedad. El Estado los da completos; muchas
comunidades autónomas, ayuntamientos y universidades también, pero algunas los regulan de otra forma en su propio acuerdo o
calendario, que es el que manda.</p>
<p>Las fiestas nacionales que ninguna comunidad puede sustituir son el 1 de enero, el Viernes Santo, el 1 de mayo, el 15 de agosto,
el 12 de octubre, el 1 de noviembre y el 6, 8 y 25 de diciembre (marcadas con asterisco en la
<a href="{CAL27}" rel="noopener">relación de fiestas que publica el BOE</a>).</p>"""),
]

FAQ = [
    ("¿Cuántos moscosos tiene un funcionario?",
     "Seis días de asuntos particulares al año, más los que dé la antigüedad y los que se añaden cuando el 24 y el 31 de diciembre o un festivo nacional caen en fin de semana."),
    ("¿Qué son los canosos?",
     "Los días de asuntos particulares por antigüedad: 2 al cumplir el sexto trienio (18 años) y uno más por cada trienio desde el octavo (24 años)."),
    ("¿Cuántos días de vacaciones tiene un funcionario con 20 años de servicio?",
     "En la Administración del Estado, 24 días hábiles: 22 más 2 por haber cumplido 20 años. Con 25 años son 25 y con 30, 26."),
    ("¿Hasta cuándo puedo coger los días de asuntos propios?",
     "Hasta el 31 de diciembre, o hasta el 31 de enero del año siguiente si por necesidades del servicio no pudiste antes."),
    ("¿Los interinos tienen los mismos días?",
     "Sí. Los días de permiso son para todos los empleados públicos, y los de antigüedad dependen de los trienios, que los interinos también cumplen."),
    ("¿Se pueden juntar con las vacaciones?",
     "Sí, si el servicio lo permite: la resolución de 2026 deja acumularlos a los días de vacaciones que se cojan sueltos."),
]

TOOL = {
    "slug": "dias-asuntos-propios",
    "lang": "es",
    "cat": "trabajo",
    "icon": "calendar-plus",
    "order": 65,
    "name": "Días de asuntos propios",
    "k": "moscosos canosos funcionarios vacaciones antigüedad trienios AGE",
    "title": "Días de asuntos propios de funcionarios: moscosos y canosos",
    "desc": "Calcula tus días de asuntos propios de funcionario: 6 moscosos, canosos por trienios, días por 24 y 31 de diciembre y vacaciones por años de servicio.",
    "h1": "Días de asuntos propios y vacaciones de funcionarios",
    "updated": "2026-11-12",
    "data": {"fix": FIXED},
    "inputs": [
        {"id": "inicio", "type": "date", "label": "Inicio servicios", "value": "2002-01-15", "min": "1960-01-01", "max": "2028-12-31"},
        {"id": "ano", "type": "seg", "label": "Año", "value": "2027", "options": [("2026", "2026"), ("2027", "2027"), ("2028", "2028")]},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Resolución de 14 de abril de 2026, jornada y horarios de la AGE, apartados 9.1, 9.7 y 9.8 (BOE-A-2026-8287)", RES),
                ("Estatuto Básico del Empleado Público, art. 48 y DA 13ª y 14ª (BOE)", EBEP),
                ("Fiestas laborales 2027 (BOE-A-2026-21254)", CAL27)],
    "related": ["trienios-funcionarios", "calculadora-vacaciones", "permiso-nacimiento"],
    "tests": [
        ({"inicio": "2008-03-10", "ano": "2026"}, {"n.ap": 9, "n.tri": 2, "n.fes": 1, "n.dec": 0, "n.vac": 23}),
        ({"inicio": "2002-01-15", "ano": "2027"}, {"n.ap": 10, "n.tri": 3, "n.vac": 25, "n.yrs": 25}),
        ({"inicio": "2020-06-01", "ano": "2028"}, {"n.ap": 9, "n.dec": 2, "n.fes": 1, "n.tri": 0, "n.vac": 22}),
        ({"inicio": "1990-12-31", "ano": "2026"}, {"n.t": 11, "n.tri": 6, "n.vac": 26, "n.ap": 13}),
        ({"inicio": "2028-12-31", "ano": "2028"}, {"err": "La fecha de inicio es posterior a ese año."}),
    ],
}
