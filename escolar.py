"""School calendar pages, Spanish only (no ca/gl/eu strings yet), called by pages.write_pages:

    /calendario-escolar/                  hub: 19 comunidades, first and last class day, Navidad, Semana Santa
    /calendario-escolar/<comunidad>/      Sep-Jun month grid with the days without class, key dates, stages
    /vacaciones-escolares/navidad/        Christmas break per comunidad (Andalucía per province)
    /vacaciones-escolares/semana-santa/   Easter break, same table
    /vacaciones-escolares/carnaval/       February days without class (carnaval, Entroido, semana blanca), only where the file has them

Data: data/escolar-2026-27.json, plus data/escolar-2027-28.json where a comunidad has it (Cataluña). Only dates in
those files are shown; a missing one shows "–". A "sin clase" range is the official break widened with the days
next to it that have no class either: weekends, the file's non-teaching days and the 2027 labour holidays of
data/2027.json (Madrid: 23 dic - 6 ene in the order, plus 7-8 ene and the weekend, gives 23 dic - 10 ene).
"""
import datetime as dt
import json
import re
import unicodedata

import build as B
from build import E

ONLY = ["es"]
DAY = dt.timedelta(1)
STAGE = {"infantil": "Infantil", "primaria": "Primaria", "eso": "ESO", "bachillerato": "Bachillerato", "fp": "FP",
         "fp_basica": "FP Básica", "epa": "Adultos", "eoi": "Idiomas (EOI)", "infantil_0_3": "Infantil 0-3",
         "bachillerato_2": "2.º Bachillerato", "fp_especializacion": "FP especialización", "fp_virtual": "FP a distancia",
         "educacion_especial": "Ed. Especial", "musica": "Música", "danza": "Danza", "artes_plasticas": "Artes Plásticas",
         "artisticas_superiores": "Artísticas Superiores", "deportivas": "Deportivas"}
BREAK = {"navidad": "Vacaciones de Navidad", "semana_santa": "Semana Santa"}
LIMITED = re.compile(r"(?i)patr[oó]n|patronal|\bsolo\b")  # non-teaching days for some stages only: listed, not tinted
DATA = None
LAB = None  # data/2027.json


def load(name):
    p = B.ROOT / "data" / name
    return json.loads(p.read_text("utf-8")) if p.exists() else None


def D(iso):
    return dt.date.fromisoformat(iso)


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def join(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " y " + names[-1]


def days(a, b):
    """Every date from a to b, both included."""
    return [a + DAY * i for i in range((b - a).days + 1)]


def src_label(src):
    """'Orden 2034/2026', 'Resolución de 13 de mayo de 2026', 'Ayuntamiento de Jaén'."""
    t = src["title"]
    if t.startswith("Resolución de la Delegación") or t.startswith("Resolución del Delegado"):
        return "Delegación Territorial"
    return re.split(r", | – | \(| por la que", t, maxsplit=1)[0][:70]


def src_html(src, updated=None):
    up = f' · <time datetime="{updated}">actualizado {B.dmy(updated)}</time>' if updated else ""
    return (f'<p class="src">Fuente: <a href="{E(src["url"])}" rel="noopener" title="{E(src["title"])}">{E(src_label(src))}</a>{up}</p>')


# ---------------------------------------------------------------- data

def labour(slug, lo, hi):
    """2027 labour holidays of a comunidad that fall on a weekday inside [lo, hi]."""
    if not LAB or lo.year > 2027 or hi.year < 2027:
        return {}
    return {h["date"]: h["name"] for h in B.region_holidays(LAB, slug) if lo <= D(h["date"]) <= hi and D(h["date"]).weekday() < 5}


def stage_label(row, rows):
    ids = row["stages"]
    lab = join([STAGE.get(i, i) for i in ids])
    if not any(r is not row and set(r["stages"]) & set(ids) for r in rows):
        return lab
    txt = row.get("text", "").lower()  # the same stage twice: the official text says which course or cycle
    if ids == ["infantil"] and "primer ciclo" in txt:
        return "Infantil 0-3"
    if ids == ["bachillerato"] and re.search(r"primer curso|1º", txt):
        return "1.º Bachillerato"
    if ids == ["bachillerato"] and re.search(r"segundo curso|2º", txt):
        return "2.º Bachillerato"
    if "segundos cursos" in txt:
        return lab + ", 2.º curso"
    return lab


def main_stage(e):
    """The Infantil/Primaria row: its label, first and last class day (None when the order gives no date)."""
    rows = e.get("stages") or []
    for row in rows:
        if "primaria" in row["stages"]:
            return ("Infantil y Primaria" if "infantil" in row["stages"] else "Primaria"), row["start"], row["end"]
    return None, None, None


class Course:
    """One entity (comunidad or province) in one school year: what the page shows of it."""

    def __init__(self, e, slug, course):
        self.e, self.slug, self.course = e, slug, course
        self.y0 = int(course[:4])
        self.lo, self.hi = dt.date(self.y0, 9, 1), dt.date(self.y0 + 1, 6, 30)
        self.label, self.start, self.end = main_stage(e)
        self.breaks = [b for b in e.get("breaks", []) if b.get("start") and b.get("end")]
        ntd = [n for n in e.get("non_teaching_days", []) if n.get("date")]
        self.ntd = [n for n in ntd if not LIMITED.search(n["name"])]
        self.limited = [n for n in ntd if LIMITED.search(n["name"])]
        self.labour = labour(slug, self.lo, self.hi)
        self.in_break = {d.isoformat(): self.bname(b) for b in self.breaks for d in days(D(b["start"]), D(b["end"]))}
        self.off = set(self.in_break) | {n["date"] for n in self.ntd} | set(self.labour)

    @staticmethod
    def bname(b):
        return BREAK.get(b["type"]) or b.get("name") or "No lectivo"

    def widen(self, b):
        s, e = D(b["start"]), D(b["end"])
        free = lambda d: d.weekday() >= 5 or d.isoformat() in self.off  # noqa: E731
        while free(s - DAY):
            s -= DAY
        while free(e + DAY):
            e += DAY
        return s, e

    def ranges(self):
        """Breaks as days without class, by date. An 'otro' break inside an earlier range is left out (Melilla)."""
        out = []
        for b in sorted(self.breaks, key=lambda b: b["start"]):
            s, e = self.widen(b)
            if any(o["s"] <= s and e <= o["e"] for o in out):
                continue
            out.append({"type": b["type"], "name": self.bname(b), "s": s, "e": e, "n": (e - s).days + 1})
        return out

    def get(self, kind):
        return next((r for r in self.ranges() if r["type"] == kind), None)


def rng(r, short=False):
    f = B.dmon if short else B.dshort
    return f'<time datetime="{r["s"].isoformat()}">{f(r["s"])}</time> – <time datetime="{r["e"].isoformat()}">{f(r["e"])}</time>'


def one(iso, short=False):
    return f'<time datetime="{iso}">{(B.dmon if short else B.dshort)(iso)}</time>' if iso else '<span class="m">–</span>'


# ---------------------------------------------------------------- html blocks

def grid(c):
    """Same month cards as the region pages: days without class tinted 'v', days outside the course left blank."""
    hmap, marks = grid_marks(c)
    items = {}
    for iso, cls, day, name in marks:
        items.setdefault(iso[:7], []).append(f'<li class="{cls}"><b>{day}</b> {E(name)}</li>')
    months = [(c.y0, m) for m in range(9, 13)] + [(c.y0 + 1, m) for m in range(1, 7)]
    cards = "".join(B.month_html(m, hmap, [], year=y, idp=None,
                                 items="".join(items.get(f"{y}-{m:02d}", [])), show_year=True) for y, m in months)
    legend = f'<ul class="legend" aria-label="{B.t("legend")}"><li>{B.sw("v")}No lectivo</li></ul>'
    return legend + f'<div class="year">{cards}</div>'


def grid_marks(c):
    """Day tints {iso: {kind, name}} and the lines under each month [(iso, cls, day text, name)], by date (page and PDF)."""
    hmap = {}
    main_out = c.start and c.end
    for d in days(c.lo, c.hi):
        iso = d.isoformat()
        if iso in c.in_break:
            hmap[iso] = {"kind": "v", "name": c.in_break[iso]}
        elif main_out and (iso < c.start or iso > c.end):
            hmap[iso] = {"kind": "o", "name": ""}
    marks = []  # (iso, html) under each month
    for n in c.ntd:
        if n["date"] not in c.in_break:
            hmap[n["date"]] = {"kind": "v", "name": n["name"]}
            marks.append((n["date"], "k-v", str(D(n["date"]).day), n["name"]))
    seen = {n["date"] for n in c.ntd}
    for iso, name in c.labour.items():
        if iso not in c.in_break and iso not in seen:
            hmap[iso] = {"kind": "v", "name": name}
            marks.append((iso, "k-v", str(D(iso).day), name))
    for n in c.limited:
        marks.append((n["date"], "k-p", str(D(n["date"]).day), n["name"]))
    for b in c.breaks:  # one line per month the break touches
        s, e = D(b["start"]), D(b["end"])
        d = s
        while d <= e:
            last = min(e, dt.date(d.year + (d.month == 12), d.month % 12 + 1, 1) - DAY)
            marks.append((d.isoformat(), "k-v", f"{d.day}–{last.day}" if last != d else str(d.day), c.bname(b)))
            d = last + DAY
    if c.start:
        marks.append((c.start, "k-c", str(D(c.start).day), "Primer día de clase"))
    if c.end:
        marks.append((c.end, "k-c", str(D(c.end).day), "Último día de clase"))
    return hmap, sorted(marks)


def key_table(c):
    """First and last class day, breaks and single days without class, by date."""
    rows = []
    if c.start:
        rows.append((c.start, "Primer día de clase", one(c.start)))
    rs = c.ranges()
    for r in rs:
        rows.append((r["s"].isoformat(), r["name"], f'{rng(r)} <span class="m">· {r["n"]} días</span>'))
    inside = lambda iso: any(r["s"] <= D(iso) <= r["e"] for r in rs)  # noqa: E731  (already in a range above)
    for n in c.ntd + c.limited:
        if not inside(n["date"]):
            rows.append((n["date"], n["name"], one(n["date"])))
    for iso, name in c.labour.items():
        if not inside(iso) and iso not in {n["date"] for n in c.ntd}:
            rows.append((iso, name, one(iso)))
    if c.end:
        rows.append((c.end, "Último día de clase", one(c.end)))
    body = "".join(f'<tr><th scope="row">{E(lab)}</th><td>{val}</td></tr>' for _, lab, val in sorted(rows, key=lambda x: x[0]))
    return f'<table class="tbl hub">{body}</table>'


def stage_table(rows):
    tr = "".join(f'<tr><th scope="row">{E(stage_label(r, rows))}</th><td data-l="Primer día">{one(r["start"])}</td>'
                 f'<td data-l="Último día">{one(r["end"])}</td></tr>' for r in rows if r["start"] or r["end"])
    if not tr:
        return ""
    return (f'<table class="tbl hub esc"><thead><tr><th scope="col">Etapa</th><th scope="col">Primer día de clase</th>'
            f'<th scope="col">Último día de clase</th></tr></thead><tbody>{tr}</tbody></table>')


def ctx_line(c):
    if c.start and c.end:
        return f'<p class="ctx">{E(c.label)}: del {B.dlong(c.start)} al {B.dlong(c.end)}</p>'
    return ""


def pdf_tools(slug):
    f = f"calendario-escolar-2026-2027-{slug}.pdf"
    return f'<div class="tools"><a class="btn" href="{B.ASSETS}pdf/{slug}/{f}" download="{f}" type="application/pdf">PDF</a></div>'


def course_sections(c, sfx="", tools=""):
    """Grid, key dates and stages of one course, as page sections (sfx keeps ids unique on one page)."""
    yrs = f"{c.y0}-{c.y0 + 1}"
    out = B.section(f"calendario{sfx}", f"Calendario escolar {yrs}", grid(c), tools, cls="cal")
    out += B.section(f"fechas{sfx}", f"Días sin clase {yrs}", key_table(c))
    st = stage_table(c.e.get("stages") or [])
    if st:
        out += B.section(f"etapas{sfx}", f"Por etapa {yrs}", st)
    return out


# ---------------------------------------------------------------- per comunidad

def provinces_mode(r):
    return bool(r.get("provinces")) and not r.get("stages") and not r.get("breaks")


def provinces(r):
    """(display name, anchor, Course) per province. A calendar of the capital only says so in its name."""
    out = []
    for p in r.get("provinces", []):
        name = p["name"] + (" capital" if p.get("source", {}).get("title", "").startswith("Ayuntamiento") else "")
        out.append((name, slugify(p["name"]), Course(p, r["slug"], DATA["course"]), p))
    return out


def extra_province_days(r):
    """Aragón: the days each province adds to the regional calendar. Empty when the provinces repeat it (C.-La Mancha)."""
    reg = {n["date"] for n in r.get("non_teaching_days", [])} | {(b["start"], b["end"]) for b in r.get("breaks", [])}
    out = []
    for p in r.get("provinces", []):
        add = [n for n in p.get("non_teaching_days", []) if n["date"] not in reg]
        add += [b for b in p.get("breaks", []) if (b["start"], b["end"]) not in reg]
        if add:
            out.append((p, add))
    return out


def region_school_page(r, e, next_e):
    names = B.R(r)
    slug, name = r["slug"], r["name"]
    path = f"calendario-escolar/{slug}/"
    h1 = f'Calendario escolar 2026-2027 {names["region_of"]}'
    crumbs = [(B.t("spain"), ""), ("Calendario escolar", "calendario-escolar/"), (name, path)]
    upd = e["source"].get("checked") or DATA["updated"]
    if provinces_mode(e):
        provs = provinces(e)
        chips = "".join(f'<li><a href="#{a}">{E(n)}</a></li>' for n, a, _, _ in provs)
        body = B.section("provincias", "Provincias", f'<ul class="chips">{chips}</ul>', pdf_tools(slug))
        for n, a, c, p in provs:
            st = stage_table(p.get("stages") or [])
            # 8 provinces on one page: the key dates open, the month grid and the stages collapsed
            inner = (ctx_line(c) + src_html(p["source"]) + key_table(c)
                     + f'<div class="faq"><details><summary>Calendario escolar 2026-2027 de {E(n)}</summary>{grid(c)}</details>'
                     + (f'<details><summary>Por etapa</summary>{st}</details>' if st else "") + '</div>')
            body += B.section(a, E(n), inner, cls="cal")
        c0 = provs[0][2]
        starts = {c.start for _, _, c, _ in provs}
        ctx = (f'<p class="ctx">{E(c0.label)}: desde el {B.dlong(c0.start)} · fin y vacaciones según provincia</p>'
               if len(starts) == 1 and c0.start else '<p class="ctx">Fechas según provincia</p>')
        main_c = None
    else:
        main_c = Course(e, slug, DATA["course"])
        ctx = ctx_line(main_c)
        body = course_sections(main_c, tools=pdf_tools(slug))
        extra = extra_province_days(e)
        if extra:
            rows = "".join(f'<tr><th scope="row">{E(p["name"])}</th><td>'
                           + ", ".join(one(x["date"]) if "date" in x else rng({"s": D(x["start"]), "e": D(x["end"])}) for x in add)
                           + f' <a class="m" href="{E(p["source"]["url"])}" rel="noopener" title="{E(p["source"]["title"])}">Fuente</a></td></tr>'
                           for p, add in extra)
            body += B.section("provincias", "Días sin clase por provincia", f'<table class="tbl hub">{rows}</table>')
    if next_e:
        nc = Course(next_e, slug, NEXT["course"])
        body += f'<div id="curso-{NEXT["course"]}">' + course_sections(nc, "-2") + src_html(next_e["source"]) + '</div>'
    body += (f'<p class="more-l"><a href="{B.BASE}{slug}/">{E(B.fill(B.t("h1_region"), names))}</a> · '
             f'<a href="{B.BASE}calendario-escolar/">Calendario escolar 2026-2027 por comunidad</a> · '
             f'<a href="{B.BASE}vacaciones-escolares/navidad/">Vacaciones de Navidad 2026-2027</a> · '
             f'<a href="{B.BASE}vacaciones-escolares/semana-santa/">Vacaciones de Semana Santa 2027</a></p>')
    title, desc = region_titles(r, names, main_c)
    lds = [crumbs_ld(crumbs), {"@type": "Dataset", "name": h1, "description": desc, "url": B.URL + path, "inLanguage": "es-ES",
                               "dateModified": upd, "temporalCoverage": "2026-09-01/2027-06-30",
                               "spatialCoverage": {"@type": "Place", "name": f'{r["official"]}, España'},
                               "isBasedOn": e["source"]["url"], "creator": {"@type": "Organization", "name": B.t("site_name")}}]
    src = (f'<p class="src"><time datetime="{DATA["updated"]}">Actualizado {B.dmy(DATA["updated"])}</time></p>'
           if provinces_mode(e) else src_html(e["source"], DATA["updated"]))
    main = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{ctx}{src}</div>'
            f'<div class="wrap body">{body}</div>')
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}og/escolar-{slug}.png", ld(*lds), langs=ONLY)
    return path, B.page(head, "pg sch", "", main, PDATA, js=False), upd


def region_titles(r, names, c):
    name, of = r["name"], names["region_of"]
    title = B.pick(60, f"Calendario escolar 2026-2027 {name}: inicio y vacaciones",
                   f"Calendario escolar 2026-2027 {name}: clases y vacaciones", f"Calendario escolar 2026-2027 {name}")
    cands = []
    if c and c.start and c.end:
        nav, ss = c.get("navidad"), c.get("semana_santa")
        cl = f"clases del {B.dmon(c.start)} al {B.dmon(c.end)}"
        if nav and ss:
            cands.append(f"Calendario escolar 2026-2027 {of}: {cl}, Navidad del {B.dmon(nav['s'])} al {B.dmon(nav['e'])} y "
                         f"Semana Santa del {B.dmon(ss['s'])} al {B.dmon(ss['e'])}. Días sin clase.")
            cands.append(f"Calendario escolar 2026-2027 {of}: {cl}, Navidad del {B.dmon(nav['s'])} al {B.dmon(nav['e'])} y "
                         f"Semana Santa del {B.dmon(ss['s'])} al {B.dmon(ss['e'])}.")
        if nav:
            cands.append(f"Calendario escolar 2026-2027 {of}: {cl} y Navidad del {B.dmon(nav['s'])} al {B.dmon(nav['e'])}.")
    cands.append(f"Calendario escolar 2026-2027 {of}: primer y último día de clase, Navidad, Semana Santa y días no lectivos, según la norma oficial.")
    cands.append(f"Calendario escolar 2026-2027 {of}: inicio y fin de clases, Navidad, Semana Santa y días no lectivos.")
    return title, B.pick(155, *cands)


# ---------------------------------------------------------------- hubs

def crumbs_ld(items):
    import pages
    return pages.crumbs_ld(items)


def ld(*objs):
    import pages
    return pages.ld(*objs)


def courses():
    """(region from 2027.json, school entry, [Course] = one, or one per province)."""
    by = {x["slug"]: x for x in DATA["regions"]}
    out = []
    for r in PDATA["regions"]:
        e = by.get(r["slug"])
        if not e:
            continue
        if provinces_mode(e):
            out.append((r, e, [c for _, _, c, _ in provinces(e)]))
        else:
            out.append((r, e, [Course(e, r["slug"], DATA["course"])]))
    return out


def same(vals, fmt):
    vals = list(vals)
    if all(v is None for v in vals):
        return '<span class="m">–</span>'
    return fmt(vals[0]) if len(set(map(str, vals))) == 1 and vals[0] is not None else '<span class="m">Según provincia</span>'


def hub_page():
    rows = []
    for r, e, cs in courses():
        href = f'{B.BASE}calendario-escolar/{r["slug"]}/'
        nav = same([c.get("navidad") and (c.get("navidad")["s"], c.get("navidad")["e"]) for c in cs],
                   lambda v: rng({"s": v[0], "e": v[1]}, True))
        ss = same([c.get("semana_santa") and (c.get("semana_santa")["s"], c.get("semana_santa")["e"]) for c in cs],
                  lambda v: rng({"s": v[0], "e": v[1]}, True))
        rows.append(f'<tr><th scope="row"><a href="{href}">{E(r["name"])}</a></th>'
                    f'<td data-l="Primer día" class="lk">{same([c.start for c in cs], lambda v: one(v, True))}</td>'
                    f'<td data-l="Último día" class="lk">{same([c.end for c in cs], lambda v: one(v, True))}</td>'
                    f'<td data-l="Navidad">{nav}</td><td data-l="Semana Santa">{ss}</td></tr>')
    h1 = "Calendario escolar 2026-2027"
    crumbs = [(B.t("spain"), ""), ("Calendario escolar", "calendario-escolar/")]
    table = (f'<table class="tbl hub esc"><thead><tr><th scope="col">Comunidad</th><th scope="col">Primer día de clase</th>'
             f'<th scope="col">Último día de clase</th><th scope="col">Navidad</th><th scope="col">Semana Santa</th></tr></thead>'
             f'<tbody>{"".join(rows)}</tbody></table>')
    more = (f'<p class="more-l">{break_links()}'
            + (f' · <a href="{B.BASE}calendario-escolar/cataluna/#curso-{NEXT["course"]}">Calendario escolar {NEXT["course"]} de Cataluña</a>'
               if NEXT and any(x["slug"] == "cataluna" for x in NEXT["regions"]) else "") + '</p>')
    ctx = (f'<p class="ctx">Infantil y Primaria · días sin clase con fines de semana · '
           f'<time datetime="{DATA["updated"]}">actualizado {B.dmy(DATA["updated"])}</time></p>')
    main = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{ctx}</div>'
            f'<div class="wrap body narrow"><section class="sec" id="comunidades">{table}{more}</section>{B.ad("hub")}</div>')
    title = "Calendario escolar 2026-2027 en España por comunidad"
    desc = ("Calendario escolar 2026-2027 de las 19 comunidades: primer y último día de clase y vacaciones de Navidad "
            "y Semana Santa, según cada norma oficial.")
    head = B.head_html(title, desc, "calendario-escolar/", f"{B.SITE}{B.ASSETS}og/escolar.png", ld(crumbs_ld(crumbs)), langs=ONLY)
    return B.page(head, "pg sch", "", main, PDATA, js=False)


BREAK_PAGES = {
    # kind: (path, h1, crumb, section id, title, description)
    "navidad": ("vacaciones-escolares/navidad/", "Vacaciones de Navidad 2026-2027", "Vacaciones de Navidad", "navidad",
                "Vacaciones de Navidad 2026-2027 por comunidad",
                "Vacaciones escolares de Navidad 2026-2027 en las 19 comunidades: primer y último día sin clase y días de "
                "vacaciones, según cada calendario escolar oficial."),
    "semana_santa": ("vacaciones-escolares/semana-santa/", "Vacaciones de Semana Santa 2027", "Semana Santa", "semana-santa",
                     "Vacaciones de Semana Santa 2027 por comunidad",
                     "Vacaciones escolares de Semana Santa 2027 en las 19 comunidades: primer y último día sin clase y días "
                     "de vacaciones, según cada calendario escolar oficial."),
}
CARNAVAL = ("vacaciones-escolares/carnaval/", "Carnaval y semana blanca 2027", "Carnaval y semana blanca", "carnaval",
            "Carnaval 2027 y semana blanca: días sin clase por comunidad",
            "Días sin clase de febrero de 2027 por comunidad: Carnaval, Entroido y semana blanca, con fines de semana "
            "incluidos, según cada calendario escolar oficial.")


def break_links(skip=None):
    """The school-break pages, for the 'more' lines."""
    pages = [(p[0], p[1]) for k, p in BREAK_PAGES.items() if k != skip] + ([(CARNAVAL[0], CARNAVAL[1])] if skip != "carnaval" else [])
    return " · ".join(f'<a href="{B.BASE}{p}">{E(h)}</a>' for p, h in pages)


def navidad_page(kind="navidad"):
    rows = []

    def row(label_html, c, src, cls=""):
        nav = c.get(kind)
        link = f'<a href="{E(src["url"])}" rel="noopener" title="{E(src["title"])}">Fuente</a>'
        if not nav:
            return (f'<tr{cls}><th scope="row">{label_html}</th><td colspan="3"><span class="m">–</span></td>'
                    f'<td data-l="&nbsp;" class="lk">{link}</td></tr>')
        return (f'<tr{cls}><th scope="row">{label_html}</th>'
                f'<td data-l="Desde">{one(nav["s"].isoformat())}</td><td data-l="Hasta">{one(nav["e"].isoformat())}</td>'
                f'<td data-l="Días" class="num">{nav["n"]}</td><td data-l="&nbsp;" class="lk">{link}</td></tr>')

    for r, e, cs in courses():
        href = f'{B.BASE}calendario-escolar/{r["slug"]}/'
        if provinces_mode(e):
            rows.append(f'<tr><th scope="row"><a href="{href}">{E(r["name"])}</a></th>'
                        f'<td colspan="4"><span class="m">Según provincia</span></td></tr>')
            for n, a, c, p in provinces(e):
                rows.append(row(f'<a href="{href}#{a}">{E(n)}</a>', c, p["source"], ' class="sub"'))
        else:
            rows.append(row(f'<a href="{href}">{E(r["name"])}</a>', cs[0], e["source"]))
    path, h1, crumb, sid, title, desc = BREAK_PAGES[kind]
    return break_html(kind, path, h1, crumb, sid, title, desc, "".join(rows))


def break_html(kind, path, h1, crumb, sid, title, desc, rows):
    crumbs = [(B.t("spain"), ""), ("Calendario escolar", "calendario-escolar/"), (crumb, path)]
    table = (f'<table class="tbl hub esc"><thead><tr><th scope="col">Comunidad</th><th scope="col">Primer día sin clase</th>'
             f'<th scope="col">Último día sin clase</th><th scope="col" class="num">Días</th><th scope="col">Fuente</th></tr></thead>'
             f'<tbody>{rows}</tbody></table>')
    ctx = (f'<p class="ctx">Días sin clase, fines de semana incluidos · '
           f'<time datetime="{DATA["updated"]}">actualizado {B.dmy(DATA["updated"])}</time></p>')
    more = (f'<p class="more-l"><a href="{B.BASE}calendario-escolar/">Calendario escolar 2026-2027 por comunidad</a> · '
            f'{break_links(kind)}</p>')
    main = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{ctx}</div>'
            f'<div class="wrap body narrow"><section class="sec" id="{sid}">{table}{more}</section></div>')
    og = f"{B.SITE}{B.ASSETS}og/{OG[kind]}.png"
    head = B.head_html(title, desc, path, og, ld(crumbs_ld(crumbs)), langs=ONLY)
    return path, B.page(head, "pg sch", "", main, PDATA, js=False)


def feb_ranges(c):
    """Days without class that start on a February 2027 weekday (carnaval, semana blanca, single days), widened with the
    weekends and days off next to them. [(start, end, n, names)]"""
    out = []
    names = {**{n["date"]: n["name"] for n in c.ntd}, **c.labour, **c.in_break}
    for d in days(dt.date(2027, 2, 1), dt.date(2027, 2, 28)):
        if d.weekday() >= 5 or d.isoformat() not in c.off or any(s <= d <= e for s, e, _, _ in out):
            continue
        s, e = c.widen({"start": d.isoformat(), "end": d.isoformat()})
        nm = []
        for x in days(s, e):
            n = names.get(x.isoformat())
            if n and n not in nm:
                nm.append(n)
        out.append((s, e, (e - s).days + 1, nm))
    return out


def carnaval_page():
    rows, none, nodata = [], [], []

    def row(label, c, src, cls=""):
        link = f'<a href="{E(src["url"])}" rel="noopener" title="{E(src["title"])}">Fuente</a>'
        out = ""
        for s, e, n, nm in feb_ranges(c):
            why = f' <span class="m">· {E(", ".join(nm))}</span>' if nm else ""
            out += (f'<tr{cls}><th scope="row">{label}{why}</th>'
                    f'<td data-l="Desde">{one(s.isoformat())}</td><td data-l="Hasta">{one(e.isoformat())}</td>'
                    f'<td data-l="Días" class="num">{n}</td><td data-l="&nbsp;" class="lk">{link}</td></tr>')
        if not out and cls:  # a province without February days: listed, like the Navidad table
            out = (f'<tr{cls}><th scope="row">{label}</th><td colspan="3"><span class="m">–</span></td>'
                   f'<td data-l="&nbsp;" class="lk">{link}</td></tr>')
        return out

    for r, e, cs in courses():
        href = f'{B.BASE}calendario-escolar/{r["slug"]}/'
        if provinces_mode(e) and any(feb_ranges(c) for c in cs):
            sub = "".join(row(f'<a href="{href}#{a}">{E(n)}</a>', c, p["source"], ' class="sub"') for n, a, c, p in provinces(e))
            rows.append(f'<tr><th scope="row"><a href="{href}">{E(r["name"])}</a></th>'
                        f'<td colspan="4"><span class="m">Según provincia</span></td></tr>' + sub)
            continue
        if provinces_mode(e):
            got = ""
        else:
            got = row(f'<a href="{href}">{E(r["name"])}</a>', cs[0], e["source"])
        if got:
            rows.append(got)
        elif e.get("status") == "verified":
            none.append(f'<a href="{href}">{E(r["name"])}</a>')
        else:
            nodata.append(f'<a href="{href}">{E(r["name"])}</a>')
    path, h1, crumb, sid, title, desc = CARNAVAL
    path, html = break_html("carnaval", path, h1, crumb, sid, title, desc, "".join(rows))
    extra = ""
    if none:
        extra += f'<p class="m pend">Ningún día sin clase en febrero en el calendario autonómico: {", ".join(none)}.</p>'
    if nodata:
        extra += f'<p class="m pend">Sin datos: {", ".join(nodata)}.</p>'
    return path, html.replace('</tbody></table><p class="more-l">', '</tbody></table>' + extra + '<p class="more-l">', 1)


OG = {"navidad": "escolar-navidad", "semana_santa": "escolar-semana-santa", "carnaval": "escolar-carnaval"}


# ---------------------------------------------------------------- entry point

PDATA = None  # data/2027.json as the pages use it (header, footer, region names)
NEXT = None


def write_pages(data, write):
    global DATA, LAB, PDATA, NEXT
    DATA, LAB, PDATA, NEXT = load("escolar-2026-27.json"), data, data, load("escolar-2027-28.json")
    if not DATA:
        return
    write("calendario-escolar/", hub_page(), DATA["updated"], ONLY)
    by = {x["slug"]: x for x in DATA["regions"]}
    nxt = {x["slug"]: x for x in (NEXT or {}).get("regions", [])}
    for r in data["regions"]:
        if r["slug"] in by:
            path, html, upd = region_school_page(r, by[r["slug"]], nxt.get(r["slug"]))
            write(path, html, upd, ONLY)
    for page in (navidad_page, lambda: navidad_page("semana_santa"), carnaval_page):
        path, html = page()
        write(path, html, DATA["updated"], ONLY)


# ---------------------------------------------------------------- og images (Spanish build only, from pages.write_shared)

def og_school(path, label, sub, off, outside=frozenset()):
    """Same look as build.og_image: wordmark, 'Calendario escolar 2026-2027', a big label and the school year
    (Sep-Jun) as a grid of squares, the days without class tinted like the page ('v'), days outside the course blank."""
    from PIL import Image, ImageDraw
    F, INK, BG, MUT, LINE, WE, RED = B.font, B.INK, B.BG, B.MUT, B.LINE, B.WE, B.RED
    VAC, VACB = (185, 211, 242), (95, 147, 211)
    W, H, S = 1200, 630, 2
    im = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(im)
    X = 72 * S
    d.rectangle((X, 76 * S, X + 18 * S, 94 * S), fill=RED)
    d.text((X + 30 * S, 70 * S), "elcalendariolaboral", font=F(26 * S, "b"), fill=INK)
    w = d.textlength("elcalendariolaboral", font=F(26 * S, "b"))
    d.text((X + 30 * S + w, 70 * S), ".es", font=F(26 * S, "r"), fill=MUT)
    d.text((X, 150 * S), f"Calendario escolar {DATA['course']}", font=F(36 * S, "sb"), fill=MUT)
    size = 76 if len(label) <= 11 else (60 if len(label) <= 16 else (46 if len(label) <= 20 else 34))
    d.text((X, 200 * S), label, font=F(size * S, "b"), fill=INK)
    d.text((X, 330 * S), sub, font=F(30 * S, "sb"), fill=MUT)
    y0 = int(DATA["course"][:4])
    months = [(y0, m) for m in range(9, 13)] + [(y0 + 1, m) for m in range(1, 7)]
    x0, top, c, gx, gy = 700 * S, 58 * S, 17 * S, 30 * S, 22 * S
    for k, (y, m) in enumerate(months):
        col, row = k % 3, k // 3
        ox, oy = x0 + col * (7 * c + gx), top + row * (6 * c + gy + 24 * S)
        d.text((ox, oy - 4 * S), B.T["_months"][m - 1][:3].capitalize(), font=F(15 * S, "b"), fill=INK)
        first = dt.date(y, m, 1)
        nd = (dt.date(y + (m == 12), m % 12 + 1, 1) - first).days
        for dd in range(nd):
            day = first + DAY * dd
            idx = first.weekday() + dd
            cx, cy = ox + (idx % 7) * c, oy + 24 * S + (idx // 7) * c
            iso = day.isoformat()
            if iso in outside:
                continue
            v = iso in off
            fill_ = VAC if v else (WE if day.weekday() >= 5 else BG)
            d.rectangle((cx + S, cy + S, cx + c - S, cy + c - S), fill=fill_, outline=VACB if v else LINE)
    im = im.resize((W, H), Image.LANCZOS).quantize(colors=96, method=Image.Quantize.MEDIANCUT, kmeans=2)
    im.save(path, optimize=True)


def _span(r):
    return {x.isoformat() for x in days(r["s"], r["e"])}


def og_images():
    if not DATA:
        return
    out = B.ROOT / "og"
    allc = [(r, e, cs) for r, e, cs in courses()]
    union = {"navidad": set(), "semana_santa": set(), "carnaval": set()}
    for r, e, cs in allc:
        for c in cs:
            for k in ("navidad", "semana_santa"):
                g = c.get(k)
                if g:
                    union[k] |= _span(g)
            for s, e_, _, _ in feb_ranges(c):
                union["carnaval"] |= {x.isoformat() for x in days(s, e_)}
        c = cs[0]
        if provinces_mode(e):
            sub = f"{len(cs)} provincias · clases y vacaciones"
            off = set.intersection(*(set(c2.off) for c2 in cs))  # days without class in every province
            outside = frozenset()
        else:
            sub = f"Clases: {B.dmon(c.start)} – {B.dmon(c.end)}" if c.start and c.end else "Clases y vacaciones"
            off = c.off
            outside = frozenset(x.isoformat() for x in days(c.lo, c.hi) if c.start and c.end and (x.isoformat() < c.start or x.isoformat() > c.end))
        og_school(out / f"escolar-{r['slug']}.png", r["name"], sub, off, outside)
    og_school(out / "escolar.png", "Por comunidad", "19 comunidades · clases y vacaciones", union["navidad"] | union["semana_santa"])
    og_school(out / "escolar-navidad.png", "Navidad", "Vacaciones por comunidad", union["navidad"])
    og_school(out / "escolar-semana-santa.png", "Semana Santa", "Vacaciones 2027 por comunidad", union["semana_santa"])
    og_school(out / "escolar-carnaval.png", "Carnaval", "Días sin clase en febrero 2027", union["carnaval"])
