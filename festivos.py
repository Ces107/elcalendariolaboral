"""Holiday pages, Spanish only, called by pages.write_pages after escolar (it reads the school breaks):

    /festivos/                        every 2027 holiday by month, with where it applies, and the national ones explained
    /festivos/reyes/                  6 Jan: the Año Nuevo-Reyes bridge and the return to school in each comunidad
    /festivos/san-jose/               19 Mar: the 5 comunidades, San José or Santiago, how it chains with Semana Santa
    /festivos/15-de-agosto/           Asunción on a Sunday: Monday 16, 11 Oct (Extremadura) or no extra day
    /festivos/12-de-octubre/          Tuesday: the Monday 11 bridge and what changes in each comunidad
    /festivos/puente-de-diciembre/    6 and 8 Dec: the year's best bridge
    /semana-santa/                    Jueves Santo, Viernes Santo and Lunes de Pascua per comunidad, with the school break

Only holidays with something of their own to say get a page; Año Nuevo, 1 de mayo, Todos los Santos and Navidad are
the same everywhere and fall where they fall, so they are short sections of /festivos/. Viernes Santo, Jueves Santo
and Lunes de Pascua share /semana-santa/ instead of three overlapping pages.

Rule (as guia.py): every date, count, name and bridge comes from data/2027.json, data/locales-2027.json and the school
files; the only outside facts are the legal texts, checked on boe.es on 07-11-2026: Estatuto de los Trabajadores
art. 37.2, Real Decreto 2001/1983 art. 45 (the list of national holidays and what a comunidad may change), the BOE
resolution of 2027 (BOE-A-2026-21254) and Ley 18/1987 (12 de octubre). Easter is computed, then checked against the
data. No Event markup: a day off is not an event (seo/RESEARCH-2026-11.md).
"""
import datetime as dt

import build as B
from build import E
import guia
from guia import D, idx, join, few, dl, notes, lead, upd, having, stats, webpage_ld, ET_URL, RD_URL

# First publication of these pages: the visible "Actualizado", dateModified and sitemap lastmod. Bump only with real
# content changes.
UPDATED = "2026-11-07"
LEY_FN = "https://www.boe.es/buscar/doc.php?id=BOE-A-1987-22831"
OG = "og/espana.png"
P = None  # pages module

PAGES = {  # date -> the page that explains it (hub table links)
    "2027-01-06": "festivos/reyes/", "2027-03-19": "festivos/san-jose/", "2027-03-25": "semana-santa/",
    "2027-03-26": "semana-santa/", "2027-03-29": "semana-santa/", "2027-08-16": "festivos/15-de-agosto/",
    "2027-10-11": "festivos/15-de-agosto/", "2027-10-12": "festivos/12-de-octubre/",
    "2027-12-06": "festivos/puente-de-diciembre/", "2027-12-08": "festivos/puente-de-diciembre/",
}
LINKS = [("festivos/reyes/", "Reyes"), ("festivos/san-jose/", "San José"), ("semana-santa/", "Semana Santa"),
         ("festivos/15-de-agosto/", "15 de agosto"), ("festivos/12-de-octubre/", "12 de octubre"),
         ("festivos/puente-de-diciembre/", "Puente de diciembre")]


# ---------------------------------------------------------------- data helpers

def easter(y):
    """Gregorian Easter Sunday (anonymous algorithm)."""
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    return dt.date(y, (h + l_ - 7 * m + 114) // 31, (h + l_ - 7 * m + 114) % 31 + 1)


def regs():
    return {r["slug"]: r for r in P.DATA["regions"]}


def rl(slug):
    """Link to the comunidad page."""
    return f'<a href="{B.BASE}{slug}/">{E(regs()[slug]["name"])}</a>'


def slugs_having(date):
    return [k for k, s in stats().items() if date in s["dates"]]


def wd(iso):
    return B.T["_wd"][D(iso).weekday()]


def days_word(n):
    return f'{n} día' + ("" if n == 1 else "s")


def ladder(hols, iso, kmax=4):
    """The longest run of days off that holds `iso` for 0..kmax vacation days. A row only when it gets longer.
    [{k, s, e, len, take}] with s, e and take as indexes of B.DAYS."""
    hd = {h["date"] for h in hols}
    work = [d.weekday() < 5 and d.isoformat() not in hd for d in B.DAYS]
    i = idx(iso)
    best = {}
    for a in range(max(0, i - 18), i + 1):
        for b in range(i, min(len(B.DAYS) - 1, i + 18) + 1):
            c = sum(work[a:b + 1])
            if c <= kmax and (c not in best or b - a > best[c][1] - best[c][0]):
                best[c] = (a, b)
    rows, prev = [], 0
    for k in range(kmax + 1):
        if k in best and best[k][1] - best[k][0] + 1 > prev:
            a, b = best[k]
            rows.append({"k": k, "s": a, "e": b, "len": b - a + 1, "take": [j for j in range(a, b + 1) if work[j]]})
            prev = b - a + 1
    return rows


def sig(rows):
    return tuple((r["k"], r["s"], r["e"]) for r in rows)


def ladder_groups(iso, only=None, kmax=4):
    """Comunidades with the same ladder together: [(rows, [slug])], biggest group first."""
    g = {}
    for k, s in stats().items():
        if only is not None and k not in only:
            continue
        rows = ladder(s["hols"], iso, kmax)
        g.setdefault(sig(rows), (rows, []))[1].append(k)
    return sorted(g.values(), key=lambda v: -len(v[1]))


def ladder_html(rows):
    tr = []
    for r in rows:
        k = "Sin pedir vacaciones" if not r["k"] else f'Pidiendo {days_word(r["k"])}'
        tr.append(f'<tr><th scope="row">{k}</th><td data-l="Días libres seguidos"><b>{days_word(r["len"])}</b></td>'
                  f'<td data-l="Del … al …">{span(r)}</td>'
                  f'<td data-l="Días que pides">{E(B.dlist(r["take"])) if r["take"] else "ninguno"}</td></tr>')
    return (f'<table class="tbl hub esc"><thead><tr><th scope="col">Vacaciones</th><th scope="col">Días libres seguidos</th>'
            f'<th scope="col">Del … al …</th><th scope="col">Días que pides</th></tr></thead><tbody>{"".join(tr)}</tbody></table>')


def span(r):
    return B.dshort(B.DAYS[r["s"]]) if r["s"] == r["e"] else B.drange(r["s"], r["e"])


def span_iso(item):
    """(province, first day, last day) of a school break -> 'del sáb 20 mar al dom 4 abr'"""
    return f'del {B.dshort(item[1])} al {B.dshort(item[2])}'


def brief(rows, upto=2):
    """'4 días sin pedir nada (sáb 9 – mar 12 oct); 6 días pidiendo vie 8, lun 11 oct (…)'. A lone day is left out."""
    out = []
    for r in rows:
        if r["k"] > upto:
            break
        if r["len"] < 2:
            continue
        how = "sin pedir nada" if not r["k"] else f'pidiendo {E(B.dlist(r["take"]))}'
        out.append(f'{r["len"]} días {how} ({span(r)})')
    return "; ".join(out)


def who(ks):
    """'Todas las comunidades', 'Todas salvo X e Y' or the list, linked."""
    if len(ks) == len(stats()):
        return "Todas las comunidades"
    if len(ks) > 12:
        return "Todas salvo " + join(rl(k) for k in regs() if k not in ks)
    return join(rl(k) for k in ks)


def groups_html(groups):
    return "".join(f'<h3>{who(ks)}</h3>{ladder_html(rows)}' for rows, ks in groups)


def local_changes(cities, iso, kmax=2):
    """City pages whose 2 local days change the run around `iso` (up to kmax vacation days): grouped as
    [(local dates, rows, [city])]."""
    g = {}
    for x in cities:
        base = B.region_holidays(P.DATA, x["r"]["slug"], x["zone"])
        r0, r1 = ladder(base, iso, kmax), ladder(x["hols"], iso, kmax)
        if sig(r0) == sig(r1):
            continue
        last = r1[-1]
        locs = [h for h in x["holidays"] if last["s"] <= idx(h["date"]) <= last["e"]]
        if not locs:
            continue
        dates = tuple(sorted({h["date"] for h in locs}))
        nm = " / ".join(h["name"] for h in locs if not h["name"].startswith(("Fiesta local", "Festa local")))
        g.setdefault((dates, sig(r1)), (dates, r1, []))[2].append((x, nm))
    return sorted(g.values(), key=lambda v: (v[0][0], -len(v[2])))


def local_html(changes, iso):
    items = []
    for dates, rows, xs in changes:
        by = {}
        for x, nm in xs:  # cities that give the day the same name together: "Vigo y Sanxenxo (San Roque)"
            by.setdefault(nm, []).append(f'<a href="{B.BASE}{x["path"]}">{E(x["title_name"])}</a>')
        cs = "; ".join(join(v) + (f' <span class="m">· {E(n)}</span>' if n else "") for n, v in by.items())
        items.append(f'<b>Festivo local el {join(dl(d) for d in dates)}:</b> {cs}. Queda así: {brief(rows)}.')
    return notes(items)


def school(kind):
    """{slug: [(province or None, first day without class, last day)]} for Infantil y Primaria, from escolar.py."""
    import escolar as S
    if not S.DATA:
        return {}
    out = {}
    for r, e, cs in S.courses():
        items = [(n, c.get(kind)) for n, a, c, p in S.provinces(e)] if S.provinces_mode(e) else [(None, cs[0].get(kind))]
        out[r["slug"]] = [(n, g["s"], g["e"]) for n, g in items if g]
    return out


def work_without_school(slug, s, e, lo=None):
    """Weekdays inside [s, e] (from `lo` on) that are not labour holidays of the comunidad: days to cover if you work."""
    hd = stats()[slug]["dates"]
    d, n = max(s, lo) if lo else s, 0
    while d <= e:
        n += d.weekday() < 5 and d.isoformat() not in hd
        d += dt.timedelta(1)
    return n


def legal(txt):
    return B.section("ley", "Origen y base legal", f'<div class="guide">{txt}</div>')


def rd(art="artículo 45"):
    return f'<a href="{RD_URL}" rel="noopener">{art} del Real Decreto 2001/1983</a>'


def et():
    return f'<a href="{ET_URL}" rel="noopener">artículo 37.2 del Estatuto de los Trabajadores</a>'


def boe():
    s = P.DATA["source"]
    return f'<a href="{s["url"]}" rel="noopener">resolución del BOE para 2027</a> ({s["id"]})'


def more_links(skip):
    return ('<p class="more-l">' + " · ".join(f'<a href="{B.BASE}{p}">{n} 2027</a>' for p, n in LINKS if p != skip)
            + (f' · <a href="{B.BASE}festivos/">Todos los festivos 2027</a>' if skip != "festivos/" else "")
            + f' · <a href="{B.BASE}puentes/">Puentes 2027</a></p>')


def write_page(write, path, title, desc, h1, crumb, lead_html, body, qas):
    crumbs = [("España", ""), ("Festivos 2027", "festivos/")] + ([(crumb, path)] if path != "festivos/" else [])
    hero = f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{lead_html}{upd(UPDATED)}</div>'
    main = f'{hero}<div class="wrap body narrow">{body}{P.faq_html(qas)}</div>'
    lds = [P.crumbs_ld(crumbs), webpage_ld(title, path, UPDATED), P.faq_ld(qas)]
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}{OG}", P.ld(*lds), langs=["es"])
    write(path, B.page(head, "pg", "fest" if path == "festivos/" else "", main, P.DATA, js=False), UPDATED, ["es"])


# ---------------------------------------------------------------- /festivos/

def where(h):
    if h["regions"] == "all":
        return "Toda España"
    miss = [k for k in regs() if k not in h["regions"]]
    if len(h["regions"]) > 9:
        return f'Todas salvo {join(rl(k) for k in miss)}'
    return join(rl(k) for k in h["regions"])


def page_hub(write, cities):
    S = stats()
    hs = P.DATA["holidays"]
    nat = [h for h in hs if h["regions"] == "all"]
    own = [h for h in hs if h["regions"] != "all"]
    counts = sorted({s["n"] for k, s in S.items() if k != "canarias"})
    months = {}
    for h in hs:
        months.setdefault(D(h["date"]).month, []).append(h)
    blocks = []
    for m, xs in sorted(months.items()):
        mn = B.T["_months"][m - 1]
        rows = []
        for h in xs:
            nm = E(h["name"])
            if h["date"] in PAGES:
                nm = f'<a href="{B.BASE}{PAGES[h["date"]]}">{nm}</a>'
            we = " · fin de semana" if D(h["date"]).weekday() >= 5 else ""
            rows.append(f'<tr><th scope="row">{nm}</th><td data-l="Fecha"><time datetime="{h["date"]}">{dl(h["date"])}</time>'
                        f'<span class="m">{we}</span></td><td data-l="Dónde">{where(h)}</td></tr>')
        blocks.append(f'<h3 id="{mn}">{mn.capitalize()}</h3><table class="tbl hub esc"><thead><tr><th scope="col">Festivo</th>'
                      f'<th scope="col">Fecha</th><th scope="col">Dónde</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')
    isl = P.DATA["zones"]["canarias"]["options"]
    aran = next(o for o in P.DATA["zones"]["cataluna"]["options"] if "remove" in o)
    zones = (f'<p class="m">Además, cada isla de Canarias tiene su fiesta: '
             + "; ".join(f'{E(o["name"])}, {B.dm(o["add"]["date"])} ({E(o["add"]["name"])})' for o in isl if "add" in o)
             + f'. En Arán, el {B.dm(aran["remove"])} se cambia por el {B.dm(aran["add"]["date"])} ({E(aran["add"]["name"])}).</p>')
    cal = B.section("calendario", "Todos los festivos de 2027, mes a mes", "".join(blocks) + zones)

    # the national list of RD 2001/1983 art. 45.1, with what happens in 2027
    m16, m11 = slugs_having("2027-08-16"), slugs_having("2027-10-11")
    jt, sj = slugs_having("2027-03-25"), slugs_having("2027-03-19")
    nobody_santiago = not slugs_having("2027-07-25") and not slugs_having("2027-07-26")
    rows = [
        ("Año Nuevo", "2027-01-01", "b", f'{dl("2027-01-01").capitalize()}, en toda España.'),
        ("Epifanía del Señor (Reyes)", "2027-01-06", "d",
         f'{dl("2027-01-06").capitalize()}. Se puede cambiar, pero {"ninguna comunidad lo ha hecho" if len(slugs_having("2027-01-06")) == 19 else "no en todas"}.'),
        ("San José o Santiago Apóstol", "2027-03-19", "d",
         f'San José, {dl("2027-03-19")}, en {len(sj)} comunidades.'
         + (" El 25 de julio cae en domingo y ninguna lo ha elegido." if nobody_santiago else "")),
        ("Jueves Santo", "2027-03-25", "d", f'{dl("2027-03-25").capitalize()}, en {len(jt)} comunidades.'),
        ("Viernes Santo", "2027-03-26", "c", f'{dl("2027-03-26").capitalize()}, en toda España.'),
        ("Fiesta del Trabajo", "2027-05-01", "b", "Sábado 1 de mayo. No se traslada."),
        ("Asunción de la Virgen", "2027-08-15", "c",
         f'Domingo 15 de agosto: el lunes 16 en {len(m16)} comunidades'
         + (f', el 11 de octubre en {join(regs()[k]["name"] for k in m11)}' if m11 else "") + "."),
        ("Fiesta Nacional de España", "2027-10-12", "a", f'{dl("2027-10-12").capitalize()}, en toda España.'),
        ("Todos los Santos", "2027-11-01", "c", f'{dl("2027-11-01").capitalize()}, en toda España.'),
        ("Día de la Constitución", "2027-12-06", "a", f'{dl("2027-12-06").capitalize()}, en toda España.'),
        ("Inmaculada Concepción", "2027-12-08", "c", f'{dl("2027-12-08").capitalize()}, en toda España.'),
        ("Navidad", "2027-12-25", "b", "Sábado 25 de diciembre. No se traslada."),
    ]
    kind = {"a": "Cívica, no se cambia", "b": "Del Estatuto, no se cambia", "c": "Religiosa, no se cambia",
            "d": "Religiosa, la comunidad puede cambiarla"}
    tr = "".join(f'<tr><th scope="row">{E(n)}</th><td data-l="Tipo (art. 45.1)">{x}) {kind[x]}</td><td data-l="En 2027">{w}</td></tr>'
                 for n, d, x, w in rows)
    law = B.section("nacionales", "Las 12 fiestas nacionales y cuáles puede cambiar cada comunidad",
                    f'<p>El {rd()} enumera las fiestas nacionales en cuatro grupos. Las de los grupos a), b) y c) valen en '
                    f'toda España; las del grupo d) son las que cada comunidad puede sustituir por una fiesta propia. Si una '
                    f'cae en domingo, su descanso pasa al lunes, y ese lunes también lo puede cambiar la comunidad '
                    f'({et()}).</p>'
                    f'<table class="tbl hub esc"><thead><tr><th scope="col">Fiesta</th><th scope="col">Tipo (art. 45.1)</th>'
                    f'<th scope="col">En 2027</th></tr></thead><tbody>{tr}</tbody></table>'
                    f'<p class="m">Grupos del artículo 45.1: a) de carácter cívico; b) las que fija el Estatuto de los '
                    f'Trabajadores; c) y d) las del Acuerdo con la Santa Sede de 1979. Por eso el Jueves Santo y Reyes faltan '
                    f'en algunas comunidades y el Viernes Santo nunca.</p>')

    # the four national holidays without a page of their own
    natd = [h for h in S["madrid"]["hols"] if h["kind"] == "n"]
    run = lambda iso: (lambda r: {"s": r[0], "e": r[1]} if r and r[1] > r[0] else None)(guia.run_with(natd, iso))  # noqa: E731
    ny, tl = run("2027-01-01"), run("2027-11-01")
    may = [h for h in own if D(h["date"]).month == 5]
    sat = [h for h in nat if D(h["date"]).weekday() == 5]
    sun = [d for d in ("2027-07-25", "2027-08-15") if D(d).weekday() == 6]
    folded = B.section("otros", "Año Nuevo, 1 de mayo, Todos los Santos y Navidad", notes([
        f'<span id="ano-nuevo"></span><b>Año Nuevo, {dl("2027-01-01")}:</b> fin de semana largo en toda España, '
        f'{B.drange(ny["s"], ny["e"])}. Pidiendo el 4 y el 5 se une con Reyes: '
        f'<a href="{B.BASE}festivos/reyes/">puente de Año Nuevo y Reyes</a>.' if ny else "",
        f'<span id="1-de-mayo"></span><b>Fiesta del Trabajo, {dl("2027-05-01")}:</b> no hay puente de mayo nacional. Los '
        f'festivos que sí caen en mayo son de comunidad: '
        + "; ".join(f'{E(h["name"])} ({B.dm(h["date"])}, {wd(h["date"])}) en {join(rl(k) for k in h["regions"])}' for h in may) + ".",
        f'<span id="todos-los-santos"></span><b>Todos los Santos, {dl("2027-11-01")}:</b> fin de semana largo en toda España, '
        f'{B.drange(tl["s"], tl["e"])}, sin pedir nada.' if tl else "",
        f'<span id="navidad"></span><b>Navidad, {dl("2027-12-25")}:</b> el 24 y el 31 de diciembre son viernes y no son '
        f'festivos laborales en ninguna comunidad. El 1 de enero de 2028 también cae en sábado.',
        f'<b>En sábado:</b> {join(E(h["name"]) for h in sat)}. La ley solo pasa al lunes los festivos que caen en domingo, así que '
        f'estos no se recuperan; si trabajas los sábados, ese día lo libras.' if sat else "",
        f'<b>En domingo:</b> el 15 de agosto (Asunción) y el 25 de julio (Santiago). El primero se pasa al lunes en '
        f'{len(m16)} comunidades: <a href="{B.BASE}festivos/15-de-agosto/">qué pasa con el 15 de agosto</a>.' if sun else "",
    ]))
    wds = {}
    for h in nat:
        wds.setdefault(D(h["date"]).weekday(), []).append(h)
    week = notes([f'<b>En {B.T["_wd"][w]}:</b> ' + join(f'{E(h["name"])} ({B.dm(h["date"])})' for h in xs) for w, xs in sorted(wds.items())])
    week_sec = B.section("semana", f'Los {len(nat)} festivos de toda España, por día de la semana', week
                         + f'<p class="m">Los que caen en lunes o viernes dan un fin de semana largo; los de martes, jueves '
                           f'o miércoles, un puente si pides días: <a href="{B.BASE}puentes/">puentes 2027</a>.</p>')
    body = cal + B.ad("hub") + law + folded + week_sec + more_links("festivos/")
    lead_html = lead(f'En 2027 hay <b>{len(nat)} festivos en toda España</b> y {len(own)} fiestas que solo tienen algunas '
                     f'comunidades. Cada comunidad llega a {"/".join(map(str, counts))} (Canarias, a {S["canarias"]["n"]} más la '
                     f'fiesta de cada isla) y cada municipio suma 2 locales.')
    qas = [("¿Cuáles son los festivos nacionales de 2027?",
            f'{len(nat)} en toda España: ' + "; ".join(f'{E(h["name"])} ({B.dm(h["date"])})' for h in nat) + "."),
           ("¿Qué festivos de 2027 caen en fin de semana?",
            f'En sábado, {join(E(h["name"]) + " (" + B.dm(h["date"]) + ")" for h in sat)}: no se trasladan. En domingo, la '
            f'Asunción (15 de agosto): {len(m16)} comunidades la pasan al lunes 16.'),
           ("¿Cuántos festivos tiene cada comunidad en 2027?",
            f'{"/".join(map(str, counts))} festivos laborales, más 2 locales en cada municipio. Canarias tiene '
            f'{S["canarias"]["n"]} más la fiesta de cada isla.')]
    title = "Festivos 2027 en España: nacionales y por comunidad"
    desc = (f'Los festivos de 2027 mes a mes: {len(nat)} en toda España, los de cada comunidad y qué fiestas puede cambiar '
            f'cada una según la ley.')
    write_page(write, "festivos/", title, desc, "Festivos 2027", "", lead_html, body, qas)


# ---------------------------------------------------------------- /festivos/reyes/

def page_reyes(write, cities):
    iso = "2027-01-06"
    have = slugs_having(iso)
    groups = ladder_groups(iso)
    rows0 = groups[0][0]
    one = next((r for r in rows0 if r["s"] == 0), None)  # the first row that reaches 1 January
    sch = school("navidad")
    jan1 = dt.date(2027, 1, 1)
    tr, ret = [], {}
    for k, items in sch.items():
        for n, s, e in items:
            back = e + dt.timedelta(1)
            w = work_without_school(k, s, e, jan1)
            label = rl(k) + (f' · {E(n)}' if n else "")
            tr.append((back, f'<tr{" class=sub" if n else ""}><th scope="row">{label}</th><td data-l="Último día sin clase">'
                             f'{B.dlong(e)}</td><td data-l="Vuelta a clase"><b>{B.dlong(back)}</b></td>'
                             f'<td data-l="Laborables de enero sin cole" class="num">{w}</td></tr>'))
            if n is None:  # comunidades with one calendar (the FAQ); Andalucía goes by province
                ret.setdefault(back, set()).add(k)
    by_prov = [k for k, items in sch.items() if any(n for n, _, _ in items)]
    tr.sort(key=lambda x: x[0])
    first_back, last_back = min(ret), max(ret)
    back_tbl = (f'<table class="tbl hub esc"><thead><tr><th scope="col">Comunidad</th><th scope="col">Último día sin clase</th>'
                f'<th scope="col">Vuelta a clase</th><th scope="col" class="num">Laborables de enero sin cole</th></tr></thead>'
                f'<tbody>{"".join(x[1] for x in tr)}</tbody></table>')
    loc = local_changes(cities, iso)
    title = "Reyes 2027: miércoles 6 de enero, festivo y puente"
    desc = (f'El 6 de enero de 2027 es miércoles y festivo en las {len(have)} comunidades. Cómo unirlo con Año Nuevo y cuándo '
            f'vuelven los niños al colegio en cada comunidad.')
    lead_html = lead(f'El Día de Reyes (Epifanía del Señor) cae en <b>{dl(iso)}</b> de 2027 y es festivo en '
                     f'{"las 19 comunidades" if len(have) == 19 else f"{len(have)} comunidades"}. '
                     + (f'Pidiendo {E(B.dlist(one["take"]))} enlazas con Año Nuevo: <b>{one["len"]} días libres</b>, '
                        f'{B.drange(one["s"], one["e"])}.' if one else ""))
    best = rows0[-1]
    body = (B.section("donde", "Dónde es festivo", notes([
        f'<b>En {"todas las comunidades" if len(have) == 19 else join(rl(k) for k in have)}.</b> Reyes es una de las '
        f'fiestas nacionales que cada comunidad puede cambiar por una propia; para 2027 '
        + ("ninguna lo ha hecho: el BOE la marca en las 19 como fiesta nacional no sustituida." if len(have) == 19
           else "algunas lo han hecho."),
        f'<b>Cae en {wd(iso)}:</b> a mitad de semana, así que solo da días seguidos si pides vacaciones antes o después.'
        if D(iso).weekday() in (1, 2, 3) else "",
        f'<b>Año Nuevo, el {dl("2027-01-01")},</b> deja un fin de semana largo justo antes: entre los dos festivos quedan '
        f'el lunes 4 y el martes 5 de enero.',
    ]))
        + B.section("puente", "Puente de Año Nuevo y Reyes 2027",
                    groups_html(groups)
                    + f'<p>La mejor relación está en pedir {days_word(one["k"])}: {one["len"]} días libres. Con {best["k"]} días '
                      f'({E(B.dlist(best["take"]))}) llegas a {best["len"]}, hasta el {B.dlong(B.DAYS[best["e"]])}.</p>'
                    + (f'<h3>Ciudades donde un festivo local lo cambia</h3>{local_html(loc, iso)}' if loc else ""))
        + B.ad("hub")
        + B.section("cole", "Vuelta al cole después de Reyes",
                    f'<p>Las vacaciones escolares de Navidad terminan entre el {B.dlong(min(e for v in sch.values() for _, _, e in v))} '
                    f'y el {B.dlong(max(e for v in sch.values() for _, _, e in v))}, según la comunidad. La última columna cuenta los '
                    f'días de enero de lunes a viernes sin clase que no son festivos laborales: los que tienes que cubrir si '
                    f'trabajas.</p>' + back_tbl
                    + f'<p class="m">Infantil y Primaria, según el calendario escolar oficial de cada comunidad'
                      + (f' ({join(regs()[k]["name"] for k in by_prov)}, por provincia)' if by_prov else "")
                      + f'. <a href="{B.BASE}vacaciones-escolares/navidad/">Vacaciones de Navidad 2026-2027</a></p>')
        + legal(f'<p>La Epifanía del Señor figura en el grupo d) del {rd()}, el de las fiestas que se fijan en cumplimiento del '
                f'Acuerdo con la Santa Sede de 1979 y que una comunidad puede sustituir por otra propia de su tradición. '
                f'Año Nuevo, en cambio, está en el grupo b): es una de las cuatro que el {et()} obliga a respetar como '
                f'fiesta nacional.</p><p>Las dos figuran en la {boe()}: Año Nuevo como fiesta nacional no sustituible y Reyes '
                f'como fiesta nacional que ninguna comunidad ha sustituido.</p>')
        + more_links("festivos/reyes/"))
    qas = [("¿Es festivo el 6 de enero de 2027?",
            f'Sí, en {"toda España" if len(have) == 19 else join(regs()[k]["name"] for k in have)}. Cae en miércoles.'),
           ("¿Qué puente hay en Reyes 2027?",
            f'Pidiendo {E(B.dlist(one["take"]))} tienes {one["len"]} días libres, {B.drange(one["s"], one["e"])}, uniendo Año '
            f'Nuevo y Reyes. Con {best["k"]} días, {best["len"]}.' if one else "Depende de los días que pidas."),
           ("¿Cuándo vuelven los niños al colegio después de Reyes en 2027?",
            f'Entre el {B.dlong(first_back)} y el {B.dlong(last_back)}, según la comunidad: el '
            f'{B.dlong(first_back)} en {few((regs()[k]["name"] for k in sorted(ret[first_back])), 5)}; el {B.dlong(last_back)} en '
            f'{few((regs()[k]["name"] for k in sorted(ret[last_back])), 5)}.'
            + (f' En {join(regs()[k]["name"] for k in by_prov)}, según la provincia.' if by_prov else ""))]
    write_page(write, "festivos/reyes/", title, desc, "Reyes 2027", "Reyes", lead_html, body, qas)


# ---------------------------------------------------------------- /festivos/san-jose/

def page_san_jose(write, cities):
    iso = "2027-03-19"
    have = slugs_having(iso)
    lack = [k for k in regs() if k not in have]
    groups = ladder_groups(iso, have)
    # the first row of each ladder that reaches Viernes Santo: San José and Semana Santa in one run
    vs = idx("2027-03-26")
    chains = [(next(r for r in rows if r["s"] <= vs <= r["e"]), ks) for rows, ks in groups
              if any(r["s"] <= vs <= r["e"] for r in rows)]
    sch = school("semana_santa")
    santiago = slugs_having("2027-07-25") + slugs_having("2027-07-26")
    loc = [c for c in local_changes(cities, iso, 1) if iso in c[0]]
    trs = []
    for k in have:
        s = stats()[k]
        run = guia.run_with(s["hols"], iso)
        items = sch.get(k, [])
        if items:
            n, a, b = items[0]
            cole = f'{B.dshort(a)} – {B.dshort(b)}' + (" · empieza el mismo 19" if a == D(iso) else "")
        else:
            cole = "–"
        trs.append(f'<tr><th scope="row">{rl(k)}</th><td data-l="Sin pedir nada">{B.drange(*run)}</td>'
                   f'<td data-l="Vacaciones escolares de Semana Santa">{cole}</td></tr>')
    title = "San José 2027: viernes 19 de marzo, ¿dónde es festivo?"
    desc = (f'El 19 de marzo de 2027 es viernes y festivo en {join(regs()[k]["name"] for k in have)}. Cómo unirlo con '
            f'Semana Santa y por qué no es festivo en el resto.')
    lead_html = lead(f'San José cae en <b>{dl(iso)}</b> de 2027. Es festivo en <b>{join(rl(k) for k in have)}</b>; en las '
                     f'otras {len(lack)} comunidades es laborable. Donde es festivo, da un fin de semana largo de 3 días sin pedir '
                     f'nada, y una semana después llega Semana Santa.')
    body = (B.section("donde", "Dónde es festivo y dónde no",
                      f'<table class="tbl hub esc"><thead><tr><th scope="col">Comunidad</th><th scope="col">Sin pedir nada</th>'
                      f'<th scope="col">Vacaciones escolares de Semana Santa</th></tr></thead><tbody>{"".join(trs)}</tbody></table>'
                      f'<p><b>Laborable en:</b> {join(rl(k) for k in lack)}.</p>'
                      + (f'<h3>Donde es festivo local</h3>{local_html(loc, iso)}' if loc else ""))
        + B.section("san-jose-o-santiago", "San José o Santiago", notes([
            f'<b>La ley deja elegir:</b> el {rd()} pone San José (19 de marzo) o Santiago Apóstol (25 de julio) como una sola '
            f'fiesta nacional, y cada comunidad elige cuál; si no elige, toca San José. Además, como fiesta del grupo d), la '
            f'puede cambiar por una propia.',
            f'<b>En 2027 el 25 de julio cae en {wd("2027-07-25")}</b>'
            + (" y ninguna comunidad tiene Santiago como festivo." if not santiago else f'; lo tienen {join(rl(k) for k in santiago)}.'),
            f'<b>{len(have)} comunidades mantienen San José</b> y las otras {len(lack)} lo han sustituido por fiestas propias.',
        ]))
        + B.ad("hub")
        + B.section("puente", "San José y Semana Santa: cuántos días seguidos",
                    f'<p>Viernes Santo cae justo una semana después, el {dl("2027-03-26")}. Pidiendo los días de entre medias, '
                    f'San José y Semana Santa quedan en una sola tirada:</p>'
                    + notes([f'<b>{join(rl(k) for k in ks)}:</b> {r["len"]} días libres pidiendo {days_word(r["k"])} '
                             f'({E(B.dlist(r["take"]))}), {B.drange(r["s"], r["e"])}.' for r, ks in chains])
                    + groups_html(groups))
        + legal(f'<p>San José está en el grupo d) del {rd()}: las fiestas fijadas en cumplimiento del Acuerdo con la Santa Sede '
                f'de 1979 que una comunidad puede sustituir. El mismo artículo da a cada comunidad la opción entre San José y '
                f'Santiago. En la {boe()} figura como fiesta nacional no sustituida en las {len(have)} comunidades que la '
                f'mantienen.</p>')
        + more_links("festivos/san-jose/"))
    qas = [("¿Es festivo el 19 de marzo de 2027?",
            f'Solo en {join(regs()[k]["name"] for k in have)}. En el resto es laborable, salvo donde sea festivo local.'),
           ("¿Se puede unir San José con Semana Santa en 2027?",
            "Sí, donde San José es festivo: " + "; ".join(
                f'en {join(regs()[k]["name"] for k in ks)}, {r["len"]} días seguidos pidiendo {days_word(r["k"])}' for r, ks in chains)
            + "."),
           ("¿Por qué San José no es festivo en mi comunidad?",
            "Porque es una fiesta nacional que cada comunidad puede cambiar por una propia, y la tuya lo ha hecho para 2027.")]
    write_page(write, "festivos/san-jose/", title, desc, "San José 2027", "San José", lead_html, body, qas)


# ---------------------------------------------------------------- /festivos/15-de-agosto/

def page_agosto(write, cities):
    iso = "2027-08-15"
    m16, m11 = slugs_having("2027-08-16"), slugs_having("2027-10-11")
    none = [k for k in regs() if k not in m16 and k not in m11]
    S = stats()
    aug = [d for d in B.DAYS if d.month == 8 and d.weekday() < 5]
    trs = []
    for k in regs():
        s = S[k]
        if k in m16:
            what, run = "Se pasa al <b>lunes 16 de agosto</b>", guia.run_with(s["hols"], "2027-08-16")
        elif k in m11:
            what, run = "Se cambia por el <b>lunes 11 de octubre</b>", guia.run_with(s["hols"], "2027-10-11")
        else:
            what, run = "Sin día extra", None
        lab = sum(1 for d in aug if d.isoformat() not in s["dates"])
        trs.append(f'<tr><th scope="row">{rl(k)}</th><td data-l="Qué pasa">{what}</td>'
                   f'<td data-l="Fin de semana largo">{B.drange(*run) + f" · {run[1] - run[0] + 1} días" if run else "–"}</td>'
                   f'<td data-l="Laborables en agosto" class="num">{lab}</td></tr>')
    other = [h for h in P.DATA["holidays"] if D(h["date"]).month == 8 and h["date"] != "2027-08-16"]
    isl = [o for o in P.DATA["zones"]["canarias"]["options"] if "add" in o and D(o["add"]["date"]).month == 8]
    loc = local_changes(cities, iso, 1)
    title = "15 de agosto de 2027: cae en domingo, ¿se pasa al lunes?"
    desc = (f'El 15 de agosto de 2027 es domingo. {len(m16)} comunidades pasan el festivo al lunes 16, '
            + (f'{regs()[m11[0]]["name"]} al 11 de octubre ' if len(m11) == 1 else "")
            + f'y {len(none)} no tienen día extra.')
    lead_html = lead(f'La Asunción (15 de agosto) cae en <b>domingo</b> en 2027. <b>{join(rl(k) for k in m16)}</b> pasan el '
                     f'festivo al lunes 16'
                     + (f'; {join(rl(k) for k in m11)} lo cambia por el lunes 11 de octubre' if m11 else "")
                     + f'. En las otras {len(none)} comunidades no hay día extra.')
    body = (B.section("ley", "Qué pasa cuando un festivo cae en domingo", notes([
        f'<b>La regla:</b> el {et()} dice que el descanso de un festivo que coincide con domingo pasa al lunes siguiente.',
        f'<b>La excepción:</b> el mismo artículo y el {rd()} permiten a cada comunidad no hacerlo y usar ese lunes para una '
        f'fiesta propia. Por eso la {boe()} no incluye el 15 de agosto: recoge el «lunes siguiente a la Asunción» en '
        f'{len(m16)} comunidades' + (f' y la «sustitución del 15 de agosto» en {join(regs()[k]["name"] for k in m11)}' if m11 else "") + ".",
        f'<b>Ninguna comunidad pierde festivos:</b> las {len(none)} que no lo trasladan tienen igualmente '
        f'{"/".join(map(str, sorted({S[k]["n"] for k in none if k != "canarias"})))} festivos; usan ese día en otra fecha del año.',
    ]))
        + B.section("comunidades", "El 15 de agosto en cada comunidad",
                    f'<table class="tbl hub esc"><thead><tr><th scope="col">Comunidad</th><th scope="col">Qué pasa</th>'
                    f'<th scope="col">Fin de semana largo</th><th scope="col" class="num">Laborables en agosto</th></tr></thead>'
                    f'<tbody>{"".join(trs)}</tbody></table>'
                    f'<p class="m">Laborables en agosto: días de lunes a viernes que no son festivo laboral de la comunidad '
                    f'(sin contar los 2 locales). Agosto de 2027 tiene {len(aug)} días de lunes a viernes.</p>')
        + B.ad("hub")
        + B.section("mas", "Otros festivos de agosto de 2027", notes(
            [f'<b>{dl(h["date"]).capitalize()}:</b> {E(h["name"])}, en {join(rl(k) for k in h["regions"])}.' for h in other]
            + [f'<b>{dl(o["add"]["date"]).capitalize()}:</b> {E(o["add"]["name"])}, fiesta insular de {E(o["name"])}.' for o in isl]))
        + (B.section("locales", "Donde un festivo local cambia el 15 de agosto",
                     f'<p>En comunidades que no trasladan la Asunción, algunos municipios tienen el lunes 16 (o un día '
                     f'cercano) como festivo local:</p>{local_html(loc, iso)}') if loc else "")
        + legal(f'<p>La Asunción de la Virgen está en el grupo c) del {rd()}, el de las fiestas del Acuerdo con la Santa Sede '
                f'de 1979 que las comunidades no pueden sustituir. Lo que sí pueden cambiar es el lunes al que se traslada '
                f'cuando cae en domingo, como pasa en 2027.</p>')
        + more_links("festivos/15-de-agosto/"))
    qas = [("¿Es festivo el lunes 16 de agosto de 2027?",
            f'Sí en {join(regs()[k]["name"] for k in m16)}. En el resto es laborable, salvo donde sea festivo local.'),
           ("¿Por qué el 15 de agosto de 2027 no se pasa al lunes en mi comunidad?",
            "Porque la ley permite a cada comunidad usar ese lunes para una fiesta propia en otra fecha. "
            + (f'{join(regs()[k]["name"] for k in m11)} lo pone el 11 de octubre; ' if m11 else "")
            + f'en {few((regs()[k]["name"] for k in none), 4)} simplemente no hay día extra.'),
           ("¿Hay puente en agosto de 2027?",
            f'Solo un fin de semana largo, del sábado 14 al lunes 16, donde el 16 es festivo. No hay puente nacional.')]
    write_page(write, "festivos/15-de-agosto/", title, desc, "15 de agosto de 2027", "15 de agosto", lead_html, body, qas)


# ---------------------------------------------------------------- /festivos/12-de-octubre/

def page_octubre(write, cities):
    iso = "2027-10-12"
    S = stats()
    groups = ladder_groups(iso)
    main_rows = groups[0][0]
    k1 = next((r for r in main_rows if r["k"] == 1), None)
    octo = [h for h in P.DATA["holidays"] if D(h["date"]).month == 10 and h["regions"] != "all"]
    isl = [o for o in P.DATA["zones"]["canarias"]["options"] if "add" in o and D(o["add"]["date"]).month == 10]
    loc = local_changes(cities, iso, 2)
    title = "12 de octubre de 2027: martes festivo y puente de 4 días"
    desc = (f'La Fiesta Nacional cae en martes 12 de octubre de 2027, festivo en toda España. Puente pidiendo el lunes 11 y '
            f'qué cambia en cada comunidad.')
    lead_html = lead(f'La Fiesta Nacional de España cae en <b>{dl(iso)}</b> de 2027 y es festivo en toda España. '
                     + (f'Pidiendo el {B.dlong(B.DAYS[k1["take"][0]])} tienes un <b>puente de {k1["len"]} días</b>, '
                        f'{B.drange(k1["s"], k1["e"])}.' if k1 else "")
                     + (" En Extremadura ese lunes ya es festivo." if "2027-10-11" in S["extremadura"]["dates"] else ""))
    items = []
    for h in octo:
        ks = h["regions"]
        d = D(h["date"])
        g = [rows for rows, kk in groups if ks[0] in kk][0]
        eff = ("cae en sábado: no suma un día libre" if d.weekday() == 5 else
               f'con el 12, {brief(g, 2)}')
        items.append(f'<b>{join(rl(k) for k in ks)}, {dl(h["date"])} ({E(h["name"])}):</b> {eff}.')
    for o in isl:
        items.append(f'<b>{E(o["name"])}, {dl(o["add"]["date"])}:</b> fiesta insular ({E(o["add"]["name"])}), la semana anterior.')
    body = (B.section("puente", "El puente del 12 de octubre", groups_html(groups[:1]))
        + B.section("comunidades", "Lo que cambia en cada comunidad", notes(items)
                    + "".join(f'<h3>{join(rl(k) for k in ks)}</h3>{ladder_html(rows)}' for rows, ks in groups[1:]))
        + B.ad("hub")
        + (B.section("locales", "Ciudades donde un festivo local cambia el puente", local_html(loc, iso)) if loc else "")
        + legal(f'<p>El 12 de octubre es una de las cuatro fiestas que el {et()} obliga a respetar siempre como nacionales, '
                f'con Navidad, Año Nuevo y el 1 de mayo. El {rd()} la pone en el grupo a), el de las fiestas de carácter '
                f'cívico, junto al Día de la Constitución, y ninguna comunidad la puede cambiar.</p>'
                f'<p>La fecha la fija la <a href="{LEY_FN}" rel="noopener">Ley 18/1987, de 7 de octubre</a>, que establece el '
                f'día de la Fiesta Nacional de España en el 12 de octubre. En la {boe()} figura como fiesta nacional no '
                f'sustituible.</p>')
        + more_links("festivos/12-de-octubre/"))
    qas = [("¿Es festivo el 12 de octubre de 2027?", f'Sí, en toda España. Cae en {wd(iso)}.'),
           ("¿Hay puente el 12 de octubre de 2027?",
            (f'Sí: pidiendo el lunes 11 tienes {k1["len"]} días libres, {B.drange(k1["s"], k1["e"])}. ' if k1 else "")
            + ("En Extremadura no hace falta pedirlo: el 11 es festivo." if "2027-10-11" in S["extremadura"]["dates"] else "")),
           ("¿Es festivo el lunes 11 de octubre de 2027?",
            f'Solo en {join(regs()[k]["name"] for k in slugs_having("2027-10-11"))} y donde sea festivo local.'
            if slugs_having("2027-10-11") else "No es festivo de comunidad en ninguna; solo donde sea festivo local.")]
    write_page(write, "festivos/12-de-octubre/", title, desc, "12 de octubre de 2027", "12 de octubre", lead_html, body, qas)


# ---------------------------------------------------------------- /festivos/puente-de-diciembre/

def page_diciembre(write, cities):
    iso = "2027-12-06"
    S = stats()
    groups = ladder_groups(iso)
    rows = groups[0][0]
    k1 = next((r for r in rows if r["k"] == 1), None)
    nat = [h for h in S["madrid"]["hols"] if h["kind"] == "n"]
    nb = [it for it in B.all_breaks(nat) if it["cost"]]
    nb.sort(key=lambda it: (-it["len"] / it["cost"], -it["len"]))
    rank = "\n".join(f'<tr><th scope="row">{E(" · ".join(it["names"]))}</th><td data-l="Días libres">{it["len"]} días</td>'
                     f'<td data-l="Del … al …">{B.drange(it["s"], it["e"])}</td>'
                     f'<td data-l="Días que pides">{E(B.dlist(it["take"]))}</td></tr>' for it in nb)
    is_best = nb and nb[0]["s"] <= idx(iso) <= nb[0]["e"]
    loc = local_changes(cities, iso, 1)
    xmas = guia.run_with(nat, "2027-12-25")
    title = "Puente de diciembre 2027: Constitución e Inmaculada"
    desc = ('El 6 de diciembre de 2027 es lunes y el 8, miércoles. Pidiendo el martes 7 tienes 5 días libres: el mejor '
            'puente de 2027, y cómo alargarlo.' if is_best and k1 and k1["len"] == 5 else
            'El 6 y el 8 de diciembre de 2027: qué días caen, cuántos días libres dan y cómo alargar el puente.')
    lead_html = lead(f'El Día de la Constitución cae en <b>{dl(iso)}</b> y la Inmaculada en <b>{dl("2027-12-08")}</b>, '
                     f'festivos en toda España. '
                     + (f'Pidiendo el {B.dlong(B.DAYS[k1["take"][0]])} tienes <b>{k1["len"]} días libres</b>, '
                        f'{B.drange(k1["s"], k1["e"])}' if k1 else "")
                     + (": el mejor puente del año." if is_best else "."))
    body = (B.section("puente", "Cuántos días libres da", groups_html(groups)
                      + notes([
                          f'<b>Sin pedir nada</b> ya tienes {rows[0]["len"]} días, {B.drange(rows[0]["s"], rows[0]["e"])}.'
                          if not rows[0]["k"] and rows[0]["len"] >= 3 else "",
                          f'<b>El {B.dlong(B.DAYS[k1["take"][0]])} es la clave:</b> un solo día une los dos festivos con el '
                          f'fin de semana.' if k1 else "",
                          f'<b>Con {rows[-1]["k"]} días</b> ({E(B.dlist(rows[-1]["take"]))}) llegas al '
                          f'{B.dlong(B.DAYS[rows[-1]["e"]])}: {rows[-1]["len"]} días seguidos.' if rows[-1]["k"] > 1 else "",
                      ]))
        + B.section("comparado", "Comparado con los otros puentes de 2027",
                    f'<p>Puentes nacionales de 2027, de más a menos días libres por día de vacaciones:</p>'
                    f'<table class="tbl hub esc"><thead><tr><th scope="col">Festivos</th><th scope="col">Días libres</th>'
                    f'<th scope="col">Del … al …</th><th scope="col">Días que pides</th></tr></thead><tbody>{rank}</tbody></table>'
                    f'<p class="m">Cada comunidad suma los suyos: <a href="{B.BASE}puentes/">puentes 2027 por comunidad</a>.</p>')
        + B.ad("hub")
        + (B.section("locales", "Ciudades donde un festivo local cambia el puente", local_html(loc, iso)) if loc else "")
        + B.section("navidad", "Y después, Navidad", notes([
            f'<b>Navidad cae en sábado</b> (25 de diciembre) y no se traslada: '
            f'{"el fin de semana del " + B.drange(*xmas) + " no suma ningún día laborable libre" if xmas else "no da día libre extra"}.',
            '<b>El 24 y el 31 de diciembre son viernes</b> y laborables en todas las comunidades.',
            f'<a href="{B.BASE}festivos/#navidad">Navidad y Año Nuevo en la lista de festivos 2027</a>.',
        ]))
        + legal(f'<p>Las dos son fiestas nacionales que ninguna comunidad puede cambiar, pero por motivos distintos. El '
                f'{rd()} pone el Día de la Constitución en el grupo a), de carácter cívico, junto al 12 de octubre: recuerda '
                f'el referéndum del 6 de diciembre de 1978 en el que se aprobó la Constitución. La Inmaculada Concepción está en '
                f'el grupo c), el de las fiestas del Acuerdo con la Santa Sede de 1979 que no se pueden sustituir.</p>'
                f'<p>Las dos figuran en la {boe()} como fiestas nacionales no sustituibles en las 19 comunidades.</p>')
        + more_links("festivos/puente-de-diciembre/"))
    qas = [("¿Hay puente en diciembre de 2027?",
            f'Sí: pidiendo el martes 7 tienes {k1["len"]} días libres, {B.drange(k1["s"], k1["e"])}.' if k1 else "Sí."),
           ("¿Cuál es el mejor puente de 2027?",
            f'El de diciembre: {k1["len"]} días libres pidiendo uno solo.' if is_best and k1
            else f'{E(" · ".join(nb[0]["names"]))}: {nb[0]["len"]} días pidiendo {nb[0]["cost"]}.'),
           ("¿Es festivo el 7 de diciembre de 2027?",
            "No es festivo de comunidad en ninguna: es laborable, salvo donde sea festivo local.")]
    write_page(write, "festivos/puente-de-diciembre/", title, desc, "Puente de diciembre 2027", "Puente de diciembre",
               lead_html, body, qas)


# ---------------------------------------------------------------- /semana-santa/

def page_semana_santa(write, cities):
    S = stats()
    es = easter(B.YEAR)
    iso = lambda d: d.isoformat()  # noqa: E731
    ramos, jue, vie, lun = es - dt.timedelta(7), es - dt.timedelta(3), es - dt.timedelta(2), es + dt.timedelta(1)
    names = {iso(jue): "Jueves Santo", iso(vie): "Viernes Santo", iso(lun): "Lunes de Pascua"}
    for d, n in names.items():  # the computed Easter must match the BOE data
        assert any(h["date"] == d and h["name"] == n for h in P.DATA["holidays"]), (d, n)
    jt, lp = slugs_having(iso(jue)), slugs_having(iso(lun))
    no_jt = [k for k in regs() if k not in jt]
    sch = school("semana_santa")
    nxt = easter(B.YEAR + 1)
    day_rows = [
        (ramos, "Domingo de Ramos", "Domingo"),
        (jue, "Jueves Santo", f'Festivo en {len(jt)} comunidades; laborable en {join(rl(k) for k in no_jt)}'),
        (vie, "Viernes Santo", "Festivo en toda España"),
        (es, "Domingo de Resurrección", "Domingo"),
        (lun, "Lunes de Pascua", f'Festivo en {join(rl(k) for k in lp)}'),
    ]
    days_tbl = (f'<table class="tbl hub esc"><thead><tr><th scope="col">Día</th><th scope="col">Fecha</th>'
                f'<th scope="col">¿Festivo?</th></tr></thead><tbody>'
                + "".join(f'<tr><th scope="row">{n}</th><td data-l="Fecha">{dl(iso(d))}</td><td data-l="¿Festivo?">{w}</td></tr>'
                          for d, n, w in day_rows) + '</tbody></table>')
    trs, cover = [], {}
    for k in regs():
        s = S[k]
        fs = [n for d, n in names.items() if d in s["dates"]]
        run = guia.run_with(s["hols"], iso(vie))
        items = sch.get(k, [])
        if len(items) == 1:
            _, a, b = items[0]
            w = work_without_school(k, a, b)
            cole, wtxt = f'{B.dshort(a)} – {B.dshort(b)}', str(w)
            cover[k] = w
        elif items:
            ws = [work_without_school(k, a, b) for _, a, b in items]
            cole = f'Según provincia, del {B.dmon(min(a for _, a, _ in items))} al {B.dmon(max(b for _, _, b in items))}'
            wtxt = f'{min(ws)}–{max(ws)}' if min(ws) != max(ws) else str(ws[0])
        else:
            cole, wtxt = "–", "–"
        trs.append(f'<tr><th scope="row">{rl(k)}</th><td data-l="Festivos">{", ".join(fs)}</td>'
                   f'<td data-l="Días libres seguidos">{B.drange(*run)} · <b>{run[1] - run[0] + 1}</b></td>'
                   f'<td data-l="Sin clase (Infantil y Primaria)">{cole}</td><td data-l="Laborables sin cole" class="num">{wtxt}</td></tr>')
    reg_tbl = (f'<table class="tbl hub esc"><thead><tr><th scope="col">Comunidad</th><th scope="col">Festivos</th>'
               f'<th scope="col">Días libres seguidos</th><th scope="col">Sin clase (Infantil y Primaria)</th>'
               f'<th scope="col" class="num">Laborables sin cole</th></tr></thead><tbody>{"".join(trs)}</tbody></table>')
    runs = {k: guia.run_with(S[k]["hols"], iso(vie)) for k in regs()}
    longest = max(r[1] - r[0] + 1 for r in runs.values())
    five = [k for k, r in runs.items() if r[1] - r[0] + 1 == longest]
    most = max(cover.values()) if cover else 0
    least = min(cover.values()) if cover else 0
    groups = ladder_groups(iso(vie))
    aran = next(o for o in P.DATA["zones"]["cataluna"]["options"] if "remove" in o)
    loc = local_changes(cities, iso(vie), 1)
    title = "Semana Santa 2027: fechas, festivos y vacaciones"
    desc = (f'Semana Santa 2027 es del {ramos.day} al {es.day} de marzo. Viernes Santo es festivo en toda España, Jueves Santo '
            f'en {len(jt)} comunidades y Lunes de Pascua en {len(lp)}. Puentes y colegios.')
    lead_html = lead(f'Semana Santa 2027 va del <b>{dl(iso(ramos))} al {dl(iso(es))}</b>. Viernes Santo ({B.dm(iso(vie))}) '
                     f'es festivo en toda España, Jueves Santo ({B.dm(iso(jue))}) en {len(jt)} comunidades y Lunes de Pascua '
                     f'({B.dm(iso(lun))}) en {len(lp)}.')
    body = (B.section("dias", "Los días de Semana Santa 2027", days_tbl
                      + f'<p class="m">Pascua es el domingo siguiente a la primera luna llena de primavera (según el cálculo de la '
                        f'Iglesia), por eso cambia cada año. En {B.YEAR + 1} será el {B.dm(nxt)}: Semana Santa del {B.dm(nxt - dt.timedelta(7))} al '
                        f'{B.dm(nxt)}.</p>')
        + B.section("comunidades", "Semana Santa 2027 en cada comunidad", reg_tbl
                    + f'<p class="m">Días libres seguidos: con los festivos de la comunidad y el fin de semana, sin pedir '
                      f'vacaciones. Laborables sin cole: días de lunes a viernes sin clase que no son festivo laboral, los que '
                      f'tienes que cubrir si trabajas (sin contar los 2 locales). Fuente de las fechas escolares: el calendario '
                      f'escolar de cada comunidad, en <a href="{B.BASE}vacaciones-escolares/semana-santa/">vacaciones de Semana '
                      f'Santa 2027</a>.</p>')
        + B.section("claves", "Lo que cambia de una comunidad a otra", notes([
            f'<b>La Semana Santa más larga sin pedir días:</b> {longest} días en {join(rl(k) for k in five)}, que tienen '
            f'Jueves Santo y Lunes de Pascua.',
            f'<b>Jueves Santo laborable:</b> {join(rl(k) for k in no_jt)}. Allí el Lunes de Pascua es festivo, así que '
            f'también tienen {runs[no_jt[0]][1] - runs[no_jt[0]][0] + 1} días seguidos, del viernes al lunes.'
            if no_jt and all(k in lp for k in no_jt) else "",
            f'<b>Arán:</b> el Lunes de Pascua se cambia por el {dl(aran["add"]["date"])} ({E(aran["add"]["name"])}).',
            f'<b>Colegios:</b> quien trabaja tiene que cubrir de {least} a {most} días laborables sin clase. '
            + "; ".join(f'{n} en {join(rl(k) for k in ks)}' + (f', donde el colegio cierra {rs.pop()}' if len(rs) == 1 else "")
                        for n, ks, rs in ((n, [k for k in cover if cover[k] == n], {span_iso(sch[k][0]) for k in cover if cover[k] == n})
                                          for n in (most, least))) + "."
            if cover and most != least else "",
            f'<b>San José:</b> en {join(rl(k) for k in slugs_having("2027-03-19"))} el viernes 19 de marzo es festivo, una '
            f'semana antes: <a href="{B.BASE}festivos/san-jose/">cómo unir San José y Semana Santa</a>.',
        ]))
        + B.ad("hub")
        + B.section("puentes", "Cómo alargar Semana Santa", groups_html(groups))
        + (B.section("locales", "Ciudades con un festivo local en Semana Santa", local_html(loc, iso(vie))) if loc else "")
        + B.section("ley", "Por qué unos días son festivos en toda España y otros no", f'<div class="guide">'
                    f'<p id="viernes-santo"><b>Viernes Santo</b> está en el grupo c) del {rd()}: fiestas del Acuerdo con la '
                    f'Santa Sede de 1979 que ninguna comunidad puede cambiar. Es festivo en las 19.</p>'
                    f'<p id="jueves-santo"><b>Jueves Santo</b> está en el grupo d): la comunidad puede sustituirlo por una '
                    f'fiesta propia. Para 2027 lo han hecho {join(regs()[k]["name"] for k in no_jt)}.</p>'
                    f'<p id="lunes-de-pascua"><b>Lunes de Pascua</b> no es fiesta nacional: lo eligen como fiesta propia '
                    f'{join(regs()[k]["name"] for k in lp)}. La {boe()} lo marca como fiesta de comunidad autónoma.</p></div>')
        + more_links("semana-santa/"))
    qas = [("¿Cuándo es Semana Santa 2027?",
            f'Del domingo {ramos.day} al domingo {es.day} de marzo. Jueves Santo es el {jue.day}, Viernes Santo el {vie.day} y '
            f'Lunes de Pascua el {lun.day}.'),
           ("¿Es festivo el Jueves Santo de 2027?",
            f'Sí en {len(jt)} comunidades. Es laborable en {join(regs()[k]["name"] for k in no_jt)}.'),
           ("¿Dónde es festivo el Lunes de Pascua de 2027?", f'En {join(regs()[k]["name"] for k in lp)}.'),
           (f"¿Cuándo es Semana Santa {B.YEAR + 1}?",
            f'Del domingo {(nxt - dt.timedelta(7)).day} al domingo {nxt.day} de {B.T["_months"][nxt.month - 1]} de {B.YEAR + 1}. '
            f'Los festivos de {B.YEAR + 1} se publican en el BOE en otoño de {B.YEAR}.')]
    crumbs_path = "semana-santa/"
    write_page(write, crumbs_path, title, desc, "Semana Santa 2027", "Semana Santa", lead_html, body, qas)


def write_pages(write, cities, pages_mod):
    global P
    P = pages_mod
    page_hub(write, cities)
    page_reyes(write, cities)
    page_san_jose(write, cities)
    page_semana_santa(write, cities)
    page_agosto(write, cities)
    page_octubre(write, cities)
    page_diciembre(write, cities)
