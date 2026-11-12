"""Días lectivos que quedan: school days left in the 2026-2027 course for a comunidad (or province, where the calendar
is provincial) and stage, from the same school-calendar data as /calendario-escolar/ (data/escolar-2026-27.json) plus
the 2026 and 2027 labour holidays of the comunidad. Weekends, the official breaks, the non-teaching days of the order
and the holidays on weekdays are not school days. Local holidays and days chosen by each school are not in the data:
the visitor can subtract them by hand ("Otros días sin clase")."""
import datetime as dt
import json
import re
from pathlib import Path

from herramientas.tools._estudios import CAT

ROOT = Path(__file__).resolve().parents[2]
ESC = json.loads((ROOT / "data" / "escolar-2026-27.json").read_text("utf-8"))
LIMITED = re.compile(r"(?i)patr[oó]n|patronal|\bsolo\b")  # same rule as escolar.py: days for some schools only
STAGES = [("primaria", "Infantil y Primaria"), ("eso", "ESO"), ("bach", "Bachillerato"), ("bach2", "2.º Bachillerato"), ("fp", "FP")]


def _entities():
    """[(key, label, region, entity dicts merged in order)]: one per comunidad; per province where the comunidad
    publishes the calendar by province (Andalucía) or adds days per province (Aragón)."""
    out = []
    for r in ESC["regions"]:
        provs = r.get("provinces") or []
        if provs and not r.get("stages") and not r.get("breaks"):
            for p in provs:
                out.append((f'{r["slug"]}:{p["name"]}', f'{r["name"]} · {p["name"]}', r, [p]))
            continue
        out.append((r["slug"], r["name"], r, [r]))
        reg = {n["date"] for n in r.get("non_teaching_days", [])}
        for p in provs:
            if any(n["date"] not in reg for n in p.get("non_teaching_days", [])) and not p.get("stages"):
                out.append((f'{r["slug"]}:{p["name"]}', f'{r["name"]} · {p["name"]}', r, [r, p]))
    return out


ENT = _entities()


def _stage_rows(rows):
    """{primaria|eso|bach|bach2|fp: [start, end]} from the stage rows of the order (only rows with both dates)."""
    got = {}
    full = [x for x in rows if x.get("start") and x.get("end")]
    for x in full:
        ids, txt = x["stages"], x.get("text", "").lower()
        if "primaria" in ids and "primaria" not in got:
            got["primaria"] = [x["start"], x["end"]]
        if "eso" in ids and "eso" not in got:
            got["eso"] = [x["start"], x["end"]]
        if "fp" in ids and "fp" not in got:
            got["fp"] = [x["start"], x["end"]]
        if "bachillerato_2" in ids or ("bachillerato" in ids and re.match(r"\s*(segundo curso|2\.?º)", txt)):
            got.setdefault("bach2", [x["start"], x["end"]])
        elif "bachillerato" in ids and "bach" not in got:
            got["bach"] = [x["start"], x["end"]]
    return got


def data(ctx):
    hol = ctx.hol((2026, 2027))
    lo, hi = ESC["range"]
    out = {}
    for key, label, r, parts in ENT:
        st, off, brk = {}, {}, []
        for p in parts:
            st.update(_stage_rows(p.get("stages") or []))
            for b in p.get("breaks", []):
                if not (b.get("start") and b.get("end")):
                    continue
                name = {"navidad": "Navidad", "semana_santa": "Semana Santa"}.get(b["type"]) or b.get("name") or "Vacaciones"
                brk.append([b["start"], b["end"], name])
                d, e = dt.date.fromisoformat(b["start"]), dt.date.fromisoformat(b["end"])
                while d <= e:
                    off.setdefault(d.isoformat(), name)
                    d += dt.timedelta(1)
            for n in p.get("non_teaching_days", []):
                if n.get("date") and not LIMITED.search(n["name"]):
                    off.setdefault(n["date"], n["name"])
        for iso, name, _k in hol["reg"].get(r["slug"], hol["nat"]):
            off.setdefault(iso, name)
        days = sorted(d for d in off if lo <= d <= hi and dt.date.fromisoformat(d).weekday() < 5)
        src = parts[-1].get("source") or r.get("source") or {}
        t = src.get("title", "")
        t = "Resolución de la Delegación Territorial" if re.match(r"Resolución del? Delegad", t) else re.split(r", | – | \(| por la que", t, maxsplit=1)[0][:80]
        out[key] = {"n": label, "s": st, "o": days, "b": sorted(brk), "st": "verified" if parts[0] is not r else r["status"],  # Andalucía: partial = no regional calendar, provinces read
                    "src": [t, src.get("url", "")]}
    return {"e": out}


def _options():
    return [(k, lab) for k, lab, _, _ in ENT]


JS = r"""
function (v, H, C) {
  var MON = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  function f(d) { return d.getUTCDate() + ' ' + MON[d.getUTCMonth()] + ' ' + d.getUTCFullYear(); }
  var e = C.d.e[v.zona];
  if (!e) return { err: 'Elige la comunidad.' };
  var key = v.etapa, s = e.s[key], note = '';
  if (!s && key === 'bach2' && e.s.bach) { s = e.s.bach; note = 'La norma no da aparte el último día de 2.º de Bachillerato: se usa el de Bachillerato. En 2.º las clases suelen acabar antes, por la PAU.'; }
  if (!s) return { err: 'No hay fechas oficiales de esta etapa en ' + H.esc(e.n) + '. Prueba otra etapa.' };
  var start = H.parse(s[0]), end = H.parse(s[1]);
  var from = v.desde || (H.today ? H.today() : start);
  var off = {}, i;
  for (i = 0; i < e.o.length; i++) off[e.o[i]] = 1;
  function lectivos(a, b) {
    var n = 0;
    for (var d = a; d <= b; d = H.add(d, 1)) if (H.wd(d) < 5 && !off[H.iso(d)]) n++;
    return n;
  }
  var extra = v.extra > 0 ? Math.floor(v.extra) : 0;
  var total = lectivos(start, end);
  if (from > end) return { label: 'Curso terminado', big: '0', sub: 'Las clases acabaron el ' + f(end), n: { left: 0, total: total } };
  var a = from < start ? start : from;
  var rest = lectivos(a, end), left = Math.max(0, rest - extra);
  var done = from < start || !total ? 0 : Math.max(0, Math.min(100, 100 * (1 - rest / total)));
  var rows = [['Último día de clase', f(end)], ['Días naturales', H.num(H.diff(from, end) + (from <= end ? 1 : 0), 0)]];
  var nb = null, inb = null;
  for (i = 0; i < e.b.length; i++) {
    var bs = H.parse(e.b[i][0]), be = H.parse(e.b[i][1]);
    if (bs <= from && from <= be) inb = e.b[i];
    else if (bs > from && bs <= end && !nb) nb = e.b[i];
  }
  if (inb) rows.unshift(['Ahora', 'Vacaciones de ' + H.esc(inb[2]) + ' hasta el ' + f(H.parse(inb[1]))]);
  if (nb) rows.push(['Próximas: ' + H.esc(nb[2]), f(H.parse(nb[0])) + ' · faltan ' + lectivos(a, H.add(H.parse(nb[0]), -1)) + ' días lectivos']);
  if (from < start) rows.push(['Primer día de clase', f(start)]);
  rows.push(['Días lectivos del curso', H.num(total, 0)]);
  rows.push(['Curso hecho', H.num(done, 0) + ' %']);
  if (extra) rows.push(['Restados a mano', '−' + extra]);
  var bar = '<div class="dl-bar" role="img" aria-label="' + H.num(done, 0) + ' % del curso hecho"><i style="width:' + H.r2(done) + '%"></i></div>';
  return {
    label: 'Días lectivos que quedan', big: H.num(left, 0),
    sub: H.esc(e.n) + ' · ' + (key === 'primaria' ? 'Infantil y Primaria' : key === 'bach2' ? '2.º Bachillerato' : key === 'bach' ? 'Bachillerato' : key.toUpperCase()) +
      ' · ' + H.plural(Math.round(left / 5), 'una semana', 'unas ' + Math.round(left / 5) + ' semanas'),
    rows: rows, html: bar,
    note: (note ? note + ' ' : '') + (e.st !== 'verified' ? 'Calendario verificado solo en parte: revisa la norma. ' : '') +
      'Sin festivos locales ni días de libre disposición del centro: réstalos en «Más opciones». Fuente: <a href="' + H.esc(e.src[1]) + '" rel="noopener">' + H.esc(e.src[0]) + '</a>',
    n: { left: left, total: total, next: nb ? nb[0] : null }
  };
}
"""

CSS = """
.dl-bar{height:10px;border-radius:5px;background:var(--line,#ddd);overflow:hidden;margin:.6rem 0}
.dl-bar i{display:block;height:100%;background:var(--acc,#2a6);border-radius:5px}
"""

BLOCKS = [
    ("Cuántos días de clase quedan", """
<p>Elige tu comunidad (en Andalucía, tu provincia, porque allí el calendario lo aprueba cada Delegación Territorial) y la
etapa, y verás los <b>días lectivos que quedan</b> desde hoy hasta el último día de clase del curso 2026-2027. Cuenta solo
los días de lunes a viernes que tienen clase: quita los fines de semana, las vacaciones de Navidad y Semana Santa, los días no
lectivos que fija la orden del calendario escolar y los festivos nacionales y autonómicos que caen entre semana. Debajo
aparecen las próximas vacaciones con los días de clase que faltan para llegar a ellas y el porcentaje del curso que ya ha
pasado.</p>
<p>Las fechas salen de los mismos datos que nuestras páginas de <a href="/calendario-escolar/">calendario escolar</a>, leídos
en el boletín oficial o en la web de cada consejería. Lo que no está en esos datos son los dos <b>festivos locales</b> de tu
municipio y los días que algunas comunidades dejan elegir al consejo escolar o al ayuntamiento; si ya los conoces, réstalos
en «Más opciones» y el resultado será exacto para tu centro.</p>"""),
    ("Un ejemplo", """
<p>Un alumno de Primaria de la Comunidad de Madrid que mira la cuenta el jueves 12 de noviembre de 2026. Las clases
acaban el viernes 18 de junio de 2027: entre una fecha y otra hay 31 semanas, 157 días de lunes a viernes, pero no
todos son lectivos. Navidad va del 23 de diciembre al 6 de enero, Semana Santa del 20 al 28 de marzo, y la orden de
calendario escolar añade días no lectivos sueltos como el 7 de diciembre, el 7 y el 8 de enero o el 12 y el 15 de febrero,
además del festivo del 8 de diciembre. Descontado todo eso quedan <b>133 días lectivos</b>, 27 de ellos antes de las
vacaciones de Navidad. El curso completo tiene 179, por encima del mínimo legal de 175.</p>
<p>Si su municipio tiene un festivo local en día de clase, basta con escribir 1 en «Otros días sin clase» y la cuenta
baja a 132.</p>"""),
    ("Cómo se calcula", """
<p>La Ley Orgánica de Educación obliga a que el curso tenga al menos <b>175 días lectivos</b> en las enseñanzas
obligatorias (disposición adicional quinta), y cada comunidad fija sus fechas en una orden o resolución anual. El cálculo
recorre día a día el intervalo entre la fecha que eliges (o el primer día de clase, si aún no ha empezado) y el último día
de clase de tu etapa, y descarta sábados, domingos y cualquier día marcado como no lectivo o festivo. El total del curso
se calcula igual desde el primer día, y sirve para ver si tu comunidad está cerca del mínimo legal: la mayoría queda entre
175 y 180.</p>
<p>Cuando la orden da fechas distintas por etapa (en muchas comunidades la ESO empieza uno o dos días después que Primaria,
y 2.º de Bachillerato termina en mayo para dejar sitio a la PAU), se usa la de la etapa elegida. Si una comunidad todavía no
ha publicado la fecha de una etapa, la herramienta lo dice en lugar de inventarla.</p>"""),
]

FAQ = [
    ("¿Cuántos días lectivos tiene un curso escolar?",
     "Al menos 175 en Primaria y ESO, por la disposición adicional quinta de la Ley Orgánica de Educación. Las comunidades suelen "
     "quedar entre 175 y 180; la herramienta muestra el total de la tuya en «Días lectivos del curso»."),
    ("¿Cuenta el día de hoy?",
     "Sí: si hoy hay clase, entra en la cuenta. Si lo miras por la tarde y no quieres contarlo, pon 1 en «Otros días sin clase»."),
    ("¿Por qué no salen los festivos de mi pueblo?",
     "Porque cada municipio tiene dos festivos locales y aquí se cuentan solo los nacionales y autonómicos, que son iguales para "
     "toda la comunidad. Puedes consultarlos en el calendario laboral de tu municipio y restarlos a mano."),
    ("¿Qué pasa con 2.º de Bachillerato?",
     "En casi todas las comunidades las clases de 2.º acaban a mediados o finales de mayo por la PAU. Elige «2.º Bachillerato»: "
     "si la orden no da esa fecha aparte, se avisa y se usa la de Bachillerato."),
    ("¿Sirve para FP?",
     "Sí para la fecha general de Formación Profesional de la orden. Los ciclos con formación en empresa tienen periodos propios "
     "que dependen del centro y no están en estos datos."),
]

TOOL = {
    "slug": "dias-lectivos-restantes",
    "lang": "es",
    "cat": CAT[0], "cat_name": CAT[1],
    "icon": "calendar-time",
    "order": 80,
    "name": "Días lectivos que quedan",
    "k": "cuantos dias de clase quedan curso escolar 2026 2027 fin de curso vacaciones colegio instituto",
    "title": "¿Cuántos días de clase quedan? Curso 2026-2027",
    "desc": "Cuenta los días lectivos que quedan hasta el fin de curso 2026-2027 en tu comunidad y etapa, sin fines de semana, vacaciones ni festivos.",
    "h1": "Días lectivos que quedan",
    "crumb": "Días lectivos",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "zona", "type": "select", "label": "Comunidad", "value": "madrid", "options": _options(), "w": "l"},
        {"id": "etapa", "type": "select", "label": "Etapa", "value": "primaria", "options": STAGES},
        {"id": "desde", "type": "date", "label": "Desde", "value": "", "today": True},
        {"id": "extra", "type": "number", "label": "Otros días sin clase", "value": "", "more": True, "w": "s", "min": 0},
    ],
    "js": JS,
    "css": CSS,
    "data": data,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("BOE · Ley Orgánica 2/2006 de Educación, disposición adicional quinta (175 días lectivos)", "https://www.boe.es/buscar/act.php?id=BOE-A-2006-7899"),
                ("Órdenes de calendario escolar 2026-2027 de cada comunidad (enlazadas en el resultado)", "https://elcalendariolaboral.es/calendario-escolar/")],
    "credits": [],
    "related": ["horario-escolar", "cuenta-atras", "dias-entre-fechas"],
    "tests": [
        ({"zona": "madrid", "etapa": "primaria", "desde": "2026-11-12"}, {"n.left": 133, "n.total": 179}),
        ({"zona": "madrid", "etapa": "primaria", "desde": "2026-11-12", "extra": "1"}, {"n.left": 132}),
        ({"zona": "andalucia:Almería", "etapa": "primaria", "desde": "2026-09-01"}, {"n.left": 178, "n.total": 178}),
        ({"zona": "madrid", "etapa": "primaria", "desde": "2027-07-01"}, {"n.left": 0}),
        ({"zona": "pais-vasco", "etapa": "primaria", "desde": "2026-11-12"}, {"err": "No hay fechas oficiales de esta etapa en País Vasco / Euskadi. Prueba otra etapa."}),
    ],
}
