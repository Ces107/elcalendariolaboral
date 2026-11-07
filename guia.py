"""Explanations in our own words, all computed from data/2027.json and data/locales-2027.json (Spanish only).

Blocks for existing pages: lead() and upd() under the H1, home_notes(), region_notes(), city_notes() below the tool.
Pages: /puentes/, /como-se-fijan-los-festivos/, /sobre/, /contacto/, /aviso-legal/.

Rule: every date, count and name comes from the data files; the only outside facts are the legal framework (Estatuto de
los Trabajadores art. 37.2 and Real Decreto 2001/1983 arts. 45-47, checked on boe.es 06-11-2026) and the name of each
comunidad's official bulletin. Nothing here invents a date: what is not published is "pendiente de publicación oficial".
"""
import datetime as dt
import re

import build as B
from build import E

ET_URL = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430#a37"
RD_URL = "https://www.boe.es/buscar/act.php?id=BOE-A-1983-20906"
# Where each comunidad publishes its own decree of holidays (and, in most, the local ones)
BULL = {"andalucia": "BOJA", "aragon": "BOA", "asturias": "BOPA", "baleares": "BOIB", "canarias": "BOC", "cantabria": "BOC",
        "castilla-la-mancha": "DOCM", "castilla-y-leon": "BOCYL", "cataluna": "DOGC", "extremadura": "DOE", "galicia": "DOG",
        "madrid": "BOCM", "murcia": "BORM", "navarra": "BON", "pais-vasco": "BOPV", "la-rioja": "BOR",
        "comunitat-valenciana": "DOGV", "ceuta": "BOCCE", "melilla": "BOME"}
UPD = {"es": ("Actualizado", "Fuente"), "ca": ("Actualitzat", "Font"), "gl": ("Actualizado", "Fonte"), "eu": ("Eguneratua", "Iturria")}
EASTER = ("2027-03-25", "2027-03-26", "2027-03-29")

P = None  # pages module (set by init)


def init(pages_mod):
    global P, _S
    P, _S = pages_mod, None


def D(iso):
    return dt.date.fromisoformat(iso)


def idx(iso):
    return (D(iso) - B.DAYS[0]).days


def join(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


def few(xs, k=6):
    xs = list(xs)
    return join(xs) if len(xs) <= k else f'{", ".join(xs[:k])} y {len(xs) - k} más'


def dl(iso):
    """'lunes 1 de marzo'"""
    return B.dlong(iso)


def lastmod(*dates):
    return max(d for d in dates if d)


# ---------------------------------------------------------------- stats over the 19 comunidades

_S = None


def stats():
    global _S
    if _S is None:
        _S = {}
        for r in P.DATA["regions"]:
            hols = B.region_holidays(P.DATA, r["slug"])
            can = r["slug"] == "canarias"
            _S[r["slug"]] = {"r": r, "hols": hols, "dates": {h["date"] for h in hols}, "names": {h["name"] for h in hols},
                             "pts": B.puentes(hols), "breaks": B.all_breaks(hols), "lab": B.workdays(hols, 1 if can else 0),
                             "n": len(hols), "can": can}
    return _S


def having(date):
    return [s["r"]["name"] for s in stats().values() if date in s["dates"]]


def lacking(date):
    return [s["r"]["name"] for s in stats().values() if date not in s["dates"]]


def best(items):
    """Best puente: most days off per vacation day, then the longest."""
    c = [it for it in items if it["cost"]]
    return max(c, key=lambda it: (it["len"] / it["cost"], it["len"], -it["s"])) if c else None


def brk(it):
    s = f'{B.drange(it["s"], it["e"])}: {it["len"]} días libres'
    return s + (f' cogiendo {it["cost"]} ({B.dlist(it["take"])})' if it["cost"] else " sin coger vacaciones")


def run_with(hols, iso):
    """The run of days off (weekends + holidays) that holds `iso`, or None."""
    hd = {h["date"] for h in hols}
    off = lambda i: 0 <= i < len(B.DAYS) and (B.DAYS[i].weekday() >= 5 or B.DAYS[i].isoformat() in hd)  # noqa: E731
    i = idx(iso)
    if not off(i):
        return None
    a, b = i, i
    while off(a - 1):
        a -= 1
    while off(b + 1):
        b += 1
    return a, b


def notes(items):
    return '<ul class="notes">' + "".join(f"<li>{x}</li>" for x in items if x) + "</ul>"


# ---------------------------------------------------------------- under the H1

def upd(date, src=True):
    """'Actualizado: 6 nov 2026 · Fuente: BOE-A-2026-21254 (BOE núm. 254, de 13 de octubre de 2026)'"""
    lab, fl = UPD.get(B.LANG, UPD["es"])
    s = P.DATA["source"]
    out = f'{lab}: <time datetime="{date}">{B.dmy(date)}</time>'
    if src:
        out += f' · {fl}: <a href="{s["url"]}" rel="noopener">{s["id"]}</a> ({E(s["boe"])})'
    return f'<p class="upd">{out}</p>'


def lead(txt):
    return f'<p class="lead">{txt}</p>'


def region_lead(r):
    s = stats()[r["slug"]]
    nat = sum(1 for h in s["hols"] if h["kind"] == "n")
    own = s["n"] - nat
    extra = ", más la fiesta de cada isla y los 2 locales de cada municipio" if s["can"] else ", más los 2 locales de cada municipio"
    return lead(f'{E(r["name"])} tiene <b>{s["n"]} festivos</b> laborales en 2027: {nat} comunes a toda España y {own} que '
                f'elige la comunidad{extra}.')


def home_lead():
    S = stats()
    nat = sum(1 for h in S["madrid"]["hols"] if h["kind"] == "n")
    return lead(f'En 2027 hay <b>{nat} festivos comunes</b> a toda España. Cada comunidad llega a 12 con los suyos '
                f'(Canarias, a 11 más la fiesta de cada isla) y cada municipio suma 2 locales: 14 días en total.')


def city_lead(x):
    h1, h2 = x["holidays"]
    nm = lambda h: "" if h["name"].startswith("Fiesta local") else f' ({E(h["name"])})'  # noqa: E731
    return lead(f'Festivos locales de {E(x["title_name"])} en 2027: <b>{dl(h1["date"])}</b>{nm(h1)} y '
                f'<b>{dl(h2["date"])}</b>{nm(h2)}. Con los {x["boe"]} de {E(x["r"]["name"])}, {x["n"]} festivos en total.')


# ---------------------------------------------------------------- home

def home_notes():
    S = stats()
    nat = [h for h in S["madrid"]["hols"] if h["kind"] == "n"]
    jt, lp, sj = having("2027-03-25"), having("2027-03-29"), having("2027-03-19")
    m16, m11 = having("2027-08-16"), having("2027-10-11")
    rest = [s["r"]["name"] for s in S.values() if "2027-08-16" not in s["dates"] and "2027-10-11" not in s["dates"]]
    sat = [h for h in nat if D(h["date"]).weekday() == 5]
    b = best(B.all_breaks(nat))
    labs = sorted(s["lab"] for s in S.values())
    items = [
        f'<b><a href="{B.BASE}semana-santa/">Jueves Santo</a> (25 de marzo):</b> festivo en {len(jt)} comunidades; '
        f'laborable en {join(lacking("2027-03-25"))}.',
        f'<b><a href="{B.BASE}semana-santa/#lunes-de-pascua">Lunes de Pascua</a> (29 de marzo):</b> festivo en {join(lp)}.',
        f'<b><a href="{B.BASE}festivos/san-jose/">San José</a> (19 de marzo):</b> festivo en {join(sj)}.',
        f'<b><a href="{B.BASE}festivos/15-de-agosto/">El 15 de agosto</a> cae en domingo:</b> {join(m16)} lo pasan al lunes 16'
        + (f'; {join(m11)}, al lunes 11 de octubre' if m11 else "") + f'. En {few(rest, 5)} no hay día extra.',
        f'<b>{join(E(h["name"]) + " (" + B.dm(h["date"]) + ")" for h in sat)} caen en sábado</b> y no se pasan a otro día.' if sat else "",
        f'<b>El mejor puente nacional:</b> {brk(b)}.' if b else "",
        f'<b>Días laborables:</b> entre {labs[0]} y {labs[-1]} de lunes a viernes según la comunidad, antes de restar los 2 locales.',
    ]
    more = (f'<details class="more"><summary>Cómo se fijan los festivos</summary>'
            f'<p>El Estatuto de los Trabajadores permite hasta 14 festivos laborales al año, retribuidos y no recuperables, '
            f'y 2 de ellos son locales. El Gobierno publica en el BOE los nacionales; cada comunidad puede cambiar algunos '
            f'por fiestas propias, y cada ayuntamiento propone sus 2 locales.</p>'
            f'<p><a href="{B.BASE}como-se-fijan-los-festivos/">Cómo se fijan los festivos, paso a paso</a> · '
            f'<a href="{B.BASE}puentes/">Puentes 2027 de cada comunidad</a></p></details>'
            f'<p class="more-l"><a href="{B.BASE}festivos/">Festivos 2027 mes a mes</a> · '
            f'<a href="{B.BASE}festivos/reyes/">Reyes</a> · <a href="{B.BASE}semana-santa/">Semana Santa</a> · '
            f'<a href="{B.BASE}festivos/12-de-octubre/">12 de octubre</a> · '
            f'<a href="{B.BASE}festivos/puente-de-diciembre/">Puente de diciembre</a></p>')
    return B.section("claves", "Lo que cambia en 2027", notes(items) + more)


# ---------------------------------------------------------------- comunidad

def local_sources(slug, cities):
    """Distinct official sources of the local holidays already published in this comunidad."""
    out = []
    for x in cities:
        if x["r"]["slug"] != slug:
            continue
        lab = "acuerdo del pleno del ayuntamiento" if x["pending_bulletin"] else re.split(r",| núm| nº", x["src_label"])[0].strip()
        if lab == "Boletín oficial":
            lab = "boletín oficial del territorio"
        if lab not in out:
            out.append(lab)
    return out


def easter_txt(s, name):
    days = [h for h in EASTER if h in s["dates"]]
    rn = run_with(s["hols"], "2027-03-26")
    run = f'{B.drange(*rn)}, {rn[1] - rn[0] + 1} días seguidos sin coger vacaciones' if rn else ""
    nm = {"2027-03-25": "Jueves Santo", "2027-03-26": "Viernes Santo", "2027-03-29": "Lunes de Pascua"}
    txt = (f'<b><a href="{B.BASE}semana-santa/">Semana Santa</a>:</b> {join(nm[d] for d in days)} '
           f'{"son festivos" if len(days) > 1 else "es festivo"}: {run}.')
    if "2027-03-25" not in s["dates"]:
        txt += f' El Jueves Santo es laborable, como solo pasa en {join(lacking("2027-03-25"))}.'
    elif "2027-03-29" not in s["dates"]:
        txt += " El Lunes de Pascua es laborable."
    return txt


def region_notes(r, cities):
    S = stats()
    s = S[r["slug"]]
    name = r["name"]
    chosen = [h for h in s["hols"] if h["kind"] == "r"]

    def shared(h):
        o = [x["r"]["name"] for k, x in S.items() if k != r["slug"] and h["name"] in x["names"] and h["date"] in x["dates"]]
        if not o:
            return ""
        return f', también en {join(o)}' if len(o) <= 4 else f', también en otras {len(o)} comunidades'

    items = [f'<b>Los {len(chosen)} que elige {E(name)}:</b> '
             + "; ".join(f'{E(h["name"])}, {dl(h["date"])}{shared(h)}' for h in chosen) + "."]
    items.append(easter_txt(s, name))
    ago = f'<b><a href="{B.BASE}festivos/15-de-agosto/">15 de agosto</a>:</b>'
    if "2027-08-16" in s["dates"]:
        items.append(f"{ago} cae en domingo y se disfruta el lunes 16 de agosto.")
    elif "2027-10-11" in s["dates"]:
        items.append(f"{ago} cae en domingo y se sustituye por el lunes 11 de octubre, que hace puente largo con el 12.")
    else:
        items.append(f"{ago} cae en domingo y aquí no se traslada: no hay día extra.")
    sat = [h for h in s["hols"] if D(h["date"]).weekday() >= 5]
    if sat:
        items.append(f'<b>En fin de semana:</b> {join(E(h["name"]) + " (" + B.dlong(h["date"]) + ")" for h in sat)}. No se pasan a otro día.')
    b = best(s["breaks"])
    lw = sum(1 for it in s["breaks"] if not it["cost"])
    if b:
        items.append(f'<b>{len(s["pts"])} puentes:</b> el mejor, {brk(b)}. Además, {lw} fines de semana largos sin coger nada. '
                     f'<a href="{B.BASE}puentes/#{r["slug"]}">Comparar con otras comunidades</a>.')
    labs = sorted(x["lab"] for x in S.values())
    same = sum(1 for x in S.values() if x["lab"] == s["lab"]) - 1
    items.append(f'<b>{s["lab"]} días laborables</b> de lunes a viernes, antes de restar los 2 locales'
                 + (f', igual que otras {same} comunidades' if same else "") + f' (en España, de {labs[0]} a {labs[-1]}).')
    z = P.DATA["zones"].get(r["slug"])
    if z and r["slug"] == "canarias":
        isl = "; ".join(f'{E(o["name"])}, {E(o["add"]["name"])} ({B.dm(o["add"]["date"])})' for o in z["options"] if "add" in o)
        items.append(f'<b>Fiesta de cada isla:</b> {isl}. {E(z["note"])}')
    elif z:
        items.append(f'<b>Arán:</b> {E(z["note"])}')
    mine = [x for x in cities if x["r"]["slug"] == r["slug"]]
    if mine:
        items.append(f'<b>Festivos locales:</b> {len(mine)} municipios ya publicados, con fecha oficial '
                     f'({join(local_sources(r["slug"], cities))}). El resto, pendiente de publicación oficial.')
    else:
        items.append(f'<b>Festivos locales:</b> pendientes de publicación oficial para 2027. Los publica la autoridad laboral '
                     f'de la comunidad en el boletín oficial.')
    more = (f'<details class="more"><summary>Cómo se fijan los festivos en {E(name)}</summary>'
            f'<p>El Estatuto de los Trabajadores permite hasta 14 festivos laborales al año, 2 de ellos locales. El Gobierno '
            f'fija los nacionales y cada comunidad puede cambiar algunos por fiestas propias: {E(name)} aprueba su calendario '
            f'en su boletín oficial ({BULL[r["slug"]]}) y el BOE los recoge todos en la '
            f'<a href="{P.DATA["source"]["url"]}" rel="noopener">{P.DATA["source"]["id"]}</a>.</p>'
            f'<p>Los 2 festivos locales los propone el pleno de cada ayuntamiento y los publica la autoridad laboral en el '
            f'boletín oficial. Hasta entonces, aquí salen como pendientes y no adelantamos fechas.</p>'
            f'<p><a href="{B.BASE}como-se-fijan-los-festivos/">Cómo se fijan los festivos, paso a paso</a></p></details>')
    fest = [("festivos/reyes/", "Reyes")] + ([("festivos/san-jose/", "San José")] if "2027-03-19" in s["dates"] else []) + [
        ("semana-santa/", "Semana Santa"), ("festivos/12-de-octubre/", "12 de octubre"),
        ("festivos/puente-de-diciembre/", "puente de diciembre")]
    more += (f'<p class="more-l">En {E(name)}: ' + " · ".join(f'<a href="{B.BASE}{p}">{n} 2027</a>' for p, n in fest)
             + f' · <a href="{B.BASE}festivos/">todos los festivos 2027</a></p>')
    return B.section("claves", f'Lo propio de {E(name)} en 2027', notes(items) + more)


# ---------------------------------------------------------------- city

def city_notes(x, cities):
    c, r = x["c"], x["r"]
    name = x["title_name"]
    hols = x["hols"]
    base = B.region_holidays(P.DATA, r["slug"], x["zone"])
    breaks = B.all_breaks(hols)
    items = []
    for h in x["holidays"]:
        d = D(h["date"])
        nm = "" if h["name"].startswith("Fiesta local") else f' · {E(h["name"])}'
        i = idx(h["date"])
        it = next((b for b in breaks if b["s"] <= i <= b["e"]), None)
        others = [n for n in (it["names"] if it else []) if n != h["name"]]
        withs = f', junto a {join(E(n) for n in others)}' if others else ""
        if d.weekday() == 5:
            eff = "cae en sábado: si trabajas de lunes a viernes, no te da un día libre más"
        elif it and it["cost"]:
            eff = f'puente de {it["len"]} días cogiendo {it["cost"]} ({B.dlist(it["take"])}): {B.drange(it["s"], it["e"])}{withs}'
        elif it:
            eff = f'fin de semana largo de {it["len"]} días sin coger vacaciones: {B.drange(it["s"], it["e"])}{withs}'
        else:
            eff = f'cae en {B.T["_wd"][d.weekday()]}, a mitad de semana, sin puente'
        items.append(f'<b>{dl(h["date"]).capitalize()}{nm}:</b> {eff}.')
    blab = B.workdays(base, 0)
    bpts = B.puentes(base)
    items.append(f'<b>{E(name)} frente al resto de {E(r["name"])}:</b> {x["lab"]} días laborables de lunes a viernes, frente a '
                 f'{blab}; {len(x["pts"])} puentes, frente a {len(bpts)}.')
    b, rb = best(breaks), best(B.all_breaks(base))
    if b:
        same = rb and (b["s"], b["e"]) == (rb["s"], rb["e"])
        items.append(f'<b>Mejor puente{" (el mismo que en toda la comunidad)" if same else ""}:</b> {brk(b)}.')
    for h in x["holidays"]:
        sh = [y["title_name"] for y in cities if y is not x and y["r"]["slug"] == r["slug"]
              and any(z["date"] == h["date"] for z in y["holidays"])]
        if sh:
            items.append(f'<b>El {B.dm(h["date"])} también es festivo local en</b> {few(E(n) for n in sh)}.')
    src = c["source"]
    st = (" Aprobado por el pleno; falta su publicación en el boletín oficial." if x["pending_bulletin"] else "")
    items.append(f'<b>Fuente oficial:</b> <a href="{E(src["url"])}" rel="noopener">{E(x["src_label"])}</a>, comprobada el '
                 f'{B.dmy(src["checked"])}.{st}')
    return B.section("claves", f'Qué cambian los festivos locales de {E(name)}', notes(items))


# ---------------------------------------------------------------- /festivos-locales/

def hub_notes(cities):
    from collections import Counter
    days = [(x, h) for x in cities for h in x["holidays"]]
    by_date = Counter(h["date"] for _, h in days)
    top = by_date.most_common(4)

    def label(d):
        names = Counter(h["name"] for _, h in days if h["date"] == d and not h["name"].startswith("Fiesta local"))
        return f' ({E(next(iter(names)))})' if len(names) == 1 else ""  # only when every city names it the same

    wd = Counter(D(h["date"]).weekday() for _, h in days)
    long_ = wd[0] + wd[4]
    bridge = 0
    for x, h in days:
        i = idx(h["date"])
        it = next((b for b in B.all_breaks(x["hols"]) if b["s"] <= i <= b["e"]), None)
        bridge += bool(it and it["cost"])
    months = Counter(D(h["date"]).month for _, h in days)
    m, mn = months.most_common(1)[0]
    items = [
        "<b>Los días más repetidos:</b> " + "; ".join(f'{B.dm(d)}{label(d)}, en {n} municipios' for d, n in top) + ".",
        f'<b>En lunes o viernes:</b> {long_} de los {len(days)} días locales, que dan un fin de semana largo sin coger nada.',
        f'<b>Con puente:</b> {bridge} días locales caen en martes o jueves (o junto a otro festivo) y hacen puente cogiendo 1 o 2 días.',
        f'<b>En sábado:</b> {wd[5]} días locales; para quien trabaja de lunes a viernes no suman un día libre.',
        f'<b>El mes con más fiestas locales:</b> {B.T["_months"][m - 1]}, con {mn}.',
    ]
    return B.section("claves", "Lo que dicen los festivos locales de 2027", notes(items)
                     + f'<p class="m">Calculado con los {len(cities)} municipios publicados. '
                       f'<a href="{B.BASE}como-se-fijan-los-festivos/">Cómo se fijan los festivos locales</a></p>')


# ---------------------------------------------------------------- /puentes/

def page_puentes(write, cities):
    S = stats()
    nat = [h for h in S["madrid"]["hols"] if h["kind"] == "n"]
    nb = B.all_breaks(nat)
    nkeys = {(it["s"], it["e"], it["cost"]) for it in nb}
    b = best(nb)
    most = max(S.values(), key=lambda s: len(s["pts"]))
    least = min(S.values(), key=lambda s: len(s["pts"]))
    title = "Puentes 2027 en España y en cada comunidad"
    desc = (f'Puentes 2027: los nacionales y los de cada comunidad, cuántos días libres dan y qué días hay que pedir. '
            f'El mejor, {B.drange(b["s"], b["e"])}.')
    crumbs = [("España", ""), ("Puentes 2027", "puentes/")]
    upd_date = lastmod(P.DATA["updated"], B.CONTENT_UPDATED)
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>Puentes 2027</h1>'
            + lead(f'Con los festivos nacionales, el mejor puente de 2027 es <b>{brk(b)}</b>. Cada comunidad suma los suyos: '
                   f'de {len(least["pts"])} a {len(most["pts"])} puentes según dónde trabajes.')
            + upd(upd_date) + '</div>')
    nat_sec = B.section("nacionales", "Puentes nacionales 2027",
                        f'<table class="tbl pts">{B.pts_head()}<tbody>{"".join(B.pts_row(it) for it in nb)}</tbody></table>'
                        f'<p class="m">Valen en toda España. En cada comunidad cambian según sus festivos propios. En '
                        f'detalle: <a href="{B.BASE}festivos/reyes/">Año Nuevo y Reyes</a> · '
                        f'<a href="{B.BASE}semana-santa/">Semana Santa</a> · <a href="{B.BASE}festivos/12-de-octubre/">12 de '
                        f'octubre</a> · <a href="{B.BASE}festivos/puente-de-diciembre/">puente de diciembre</a>.</p>')
    regs = []
    for k, s in S.items():
        r = s["r"]
        own = [it for it in s["breaks"] if (it["s"], it["e"], it["cost"]) not in nkeys]
        rows = "".join(B.pts_row(it) for it in own) or f'<tr><td colspan="3">Los mismos que los nacionales.</td></tr>'
        rb = best(s["breaks"])
        regs.append(f'<details class="rg" id="{k}"><summary><span>{E(r["name"])}</span><span class="m">{len(s["pts"])} puentes'
                    f'{" · mejor: " + B.drange(rb["s"], rb["e"]) if rb else ""}</span></summary><div>'
                    f'<p class="m">Puentes y fines de semana largos que dan sus festivos propios:</p>'
                    f'<table class="tbl pts">{B.pts_head()}<tbody>{rows}</tbody></table>'
                    f'<p class="more-l"><a href="{B.BASE}{k}/#puentes">Calendario laboral 2027 de {E(r["name"])}: todos sus puentes</a></p>'
                    f'</div></details>')
    reg_sec = B.section("comunidades", "Puentes 2027 por comunidad", "".join(regs))
    how = B.section("como", "Cómo contamos los puentes", notes([
        "<b>Puente:</b> días libres seguidos alrededor de un festivo cogiendo 1 o 2 días de vacaciones (por ejemplo, el lunes "
        "entre un domingo y un martes festivo).",
        "<b>Fin de semana largo:</b> 3 o más días libres seguidos sin coger nada, porque el festivo cae en lunes o viernes.",
        "<b>Solo festivos laborales:</b> los del BOE y los de tu comunidad. Los 2 locales cambian el resultado: búscalos en la "
        f'página de tu ciudad (<a href="{B.BASE}festivos-locales/">festivos locales 2027</a>).',
        f'<b>Para elegir días:</b> el <a href="{B.BASE}vacaciones-2027/">planificador de vacaciones 2027</a> reparte tus días '
        "de vacaciones para sacar el máximo de días libres seguidos.",
    ]))
    qas = [("¿Cuántos puentes hay en 2027?",
            f'Con los festivos nacionales, {sum(1 for it in nb if it["cost"])} puentes y {sum(1 for it in nb if not it["cost"])} '
            f'fines de semana largos. Con los de cada comunidad, entre {len(least["pts"])} y {len(most["pts"])} puentes.'),
           ("¿Hay puente de mayo en 2027?",
            "No a nivel nacional: el 1 de mayo de 2027 cae en sábado. Solo puede haberlo donde un festivo local caiga cerca."),
           ("¿Cuál es el mejor puente de 2027?", f'{brk(b)[0].upper() + brk(b)[1:]}.'),
           ("¿Qué comunidad tiene más puentes en 2027?",
            f'{join(s["r"]["name"] for s in S.values() if len(s["pts"]) == len(most["pts"]))}, con {len(most["pts"])}.')]
    main = (f'{hero}<div class="wrap body narrow">{nat_sec}{reg_sec}{B.ad("hub")}{how}{P.faq_html(qas)}</div>')
    lds = [P.crumbs_ld(crumbs), webpage_ld(title, "puentes/", upd_date), P.faq_ld(qas)]
    head = B.head_html(title, desc, "puentes/", f"{B.SITE}{B.ASSETS}og/espana.png", P.ld(*lds), langs=["es"])
    write("puentes/", B.page(head, "pg", "", main, P.DATA, js=False), upd_date, ["es"])


def webpage_ld(name, path, date):
    return {"@type": "WebPage", "name": name, "url": B.URL + path, "inLanguage": "es-ES", "dateModified": date,
            "isPartOf": {"@type": "WebSite", "name": "El Calendario Laboral", "url": B.URL},
            "publisher": {"@type": "Organization", "name": "El Calendario Laboral", "url": B.URL}}


# ---------------------------------------------------------------- /como-se-fijan-los-festivos/

def page_como(write, cities, loc):
    S = stats()
    src = P.DATA["source"]
    hs = P.DATA["holidays"]
    c1 = [h for h in hs if h["code"] == 1]
    c2 = {}
    for h in hs:
        if h["code"] == 2:
            c2.setdefault((h["date"], h["name"]), h)
    c3 = sorted({h["name"] for h in hs if h["code"] == 3})
    m16, m11 = having("2027-08-16"), having("2027-10-11")
    n_pub = len(cities)
    n_pen = sum(1 for c in loc["cities"] if c["status"] not in P.PUBLISHED or not c["holidays"])
    title = "Cómo se fijan los festivos laborales en España"
    desc = ("Quién decide los festivos: hasta 14 al año, los nacionales del BOE, los que cambia cada comunidad y los 2 "
            "locales de cada ayuntamiento. Ejemplo: 2027.")
    crumbs = [("España", ""), ("Cómo se fijan los festivos", "como-se-fijan-los-festivos/")]
    upd_date = lastmod(P.DATA["updated"], B.CONTENT_UPDATED)
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>Cómo se fijan los festivos</h1>'
            + lead("Hasta <b>14 al año</b>: el Gobierno publica los nacionales en el BOE, cada comunidad cambia algunos por "
                   "fiestas propias y cada ayuntamiento añade 2 locales.")
            + upd(upd_date) + '</div>')

    def li(xs):
        return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"

    rows = []
    for k, s in S.items():
        labs = local_sources(k, cities)
        rows.append(f'<tr><th scope="row"><a href="{B.BASE}{k}/">{E(s["r"]["name"])}</a></th><td>{BULL[k]}</td>'
                    f'<td>{E(join(labs)) if labs else "pendiente de publicación oficial"}</td></tr>')
    body = (
        f'<h2>1. Un máximo de 14 al año</h2>'
        f'<p>El <a href="{ET_URL}" rel="noopener">artículo 37.2 del Estatuto de los Trabajadores</a> fija que las fiestas '
        f'laborales son retribuidas y no recuperables, que no pueden pasar de 14 al año y que 2 de ellas son locales. '
        f'Las de Navidad, Año Nuevo, 1 de mayo y 12 de octubre tienen que ser nacionales siempre.</p>'
        f'<h2>2. Las nacionales que no cambian</h2>'
        f'<p>En 2027 son {len(c1)} y valen en toda España:</p>'
        + li(f'{E(h["name"])}: {dl(h["date"])}' for h in c1)
        + f'<h2>3. Las que cada comunidad puede cambiar</h2>'
        f'<p>El <a href="{RD_URL}" rel="noopener">Real Decreto 2001/1983</a> (artículos 45 a 47, los que siguen en vigor) deja '
        f'que cada comunidad sustituya algunas fiestas nacionales por fiestas propias de su tradición. En 2027:</p>'
        + li(f'{E(n)} ({B.dm(d)}): festivo en {len(having(d))} de 19 comunidades' for (d, n) in sorted(c2))
        + f'<p>A cambio, las comunidades ponen {len(c3)} fiestas propias distintas, del Día de Andalucía a la Fiesta Nacional '
        f'de Cataluña. Cada una aprueba su lista en su boletín oficial, y el BOE las recoge todas en una resolución '
        f'de la Dirección General de Trabajo: para 2027, la <a href="{src["url"]}" rel="noopener">{src["id"]}</a> '
        f'({E(src["boe"])}).</p>'
        f'<h2>4. Si un festivo cae en domingo</h2>'
        f'<p>La comunidad puede pasarlo al lunes o poner otra fiesta. En 2027 el 15 de agosto es domingo: {join(m16)} lo '
        f'pasan al lunes 16' + (f', {join(m11)} lo cambia por el lunes 11 de octubre' if m11 else "")
        + f' y las demás no añaden ningún día. El 1 de mayo y el 25 de diciembre caen en sábado y no se trasladan.</p>'
        f'<h2>5. Los 2 festivos locales</h2>'
        f'<p>Los propone el pleno de cada ayuntamiento y los aprueba y publica la autoridad laboral en el boletín oficial '
        f'(el de la comunidad o el de la provincia). Solo valen en ese municipio. Llevamos {n_pub} municipios con fecha '
        f'oficial para 2027 y {n_pen} pendientes: solo publicamos una fecha cuando sale en un boletín o en un acuerdo del '
        f'pleno publicado por el ayuntamiento.</p>'
        f'<table class="tbl hub"><caption class="vh">Dónde se publican los festivos de 2027</caption><thead><tr>'
        f'<th scope="col">Comunidad</th><th scope="col">Boletín de la comunidad</th><th scope="col">Festivos locales 2027 publicados en</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
        + B.ad("hub") +
        f'<h2>6. Si trabajas un festivo</h2>'
        f'<p>El <a href="{RD_URL}" rel="noopener">artículo 47 del Real Decreto 2001/1983</a> dice que, si por razones técnicas '
        f'u organizativas no puedes librar un festivo, la empresa te paga esas horas con un recargo mínimo del 75 %, salvo '
        f'que te dé descanso a cambio. Tu convenio puede mejorarlo.</p>'
        f'<h2>7. Festivos laborales y calendario escolar no son lo mismo</h2>'
        f'<p>Los días sin clase los fija cada consejería de educación y no coinciden siempre con los festivos laborales. '
        f'Están en el <a href="{B.BASE}calendario-escolar/">calendario escolar 2026-2027</a>.</p>'
        f'<p class="more-l"><a href="{B.BASE}">Calendario laboral 2027</a> · <a href="{B.BASE}festivos/">Festivos 2027 '
        f'mes a mes</a> · <a href="{B.BASE}puentes/">Puentes 2027</a> · '
        f'<a href="{B.BASE}festivos-locales/">Festivos locales 2027</a></p>')
    qas = [("¿Cuántos festivos hay al año como máximo?", "14 festivos laborales, de los que 2 son locales (artículo 37.2 del Estatuto de los Trabajadores)."),
           ("¿Quién fija los festivos locales?", "El pleno de cada ayuntamiento propone 2 días y la autoridad laboral de la comunidad los publica en el boletín oficial."),
           ("¿Dónde se publica el calendario laboral 2027?",
            f'En el BOE del 13 de octubre de 2026: <a href="{src["url"]}" rel="noopener">{src["id"]}</a>.')]
    main = f'{hero}<div class="wrap body"><div class="guide">{body}</div>{P.faq_html(qas)}</div>'
    lds = [P.crumbs_ld(crumbs), webpage_ld(title, "como-se-fijan-los-festivos/", upd_date), P.faq_ld(qas)]
    head = B.head_html(title, desc, "como-se-fijan-los-festivos/", f"{B.SITE}{B.ASSETS}og/espana.png", P.ld(*lds), langs=["es"])
    write("como-se-fijan-los-festivos/", B.page(head, "pg", "", main, P.DATA, js=False), upd_date, ["es"])


# ---------------------------------------------------------------- trust pages

def doc_page(write, path, title, desc, h1, body, date):
    crumbs = [("España", ""), (h1, path)]
    main = f'<div class="wrap doc guide">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{upd(date, src=False)}{body}</div>'
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}og/espana.png",
                       P.ld(P.crumbs_ld(crumbs), webpage_ld(title, path, date)), langs=["es"], ads=False)
    write(path, B.page(head, "pg", "", main, P.DATA, js=False), date, ["es"])


def trust_pages(write, cities, loc):
    src = P.DATA["source"]
    mail = f'<a href="mailto:{B.EMAIL}">{B.EMAIL}</a>'
    date = B.CONTENT_UPDATED
    n_pub = len(cities)
    doc_page(write, "sobre/", "Quién hace El Calendario Laboral y de dónde salen los datos",
             "El Calendario Laboral es una web independiente: festivos 2027 sacados del BOE y de los boletines oficiales, "
             "con la fuente al lado de cada fecha.",
             "Quién hace esta web",
             f'<p>El Calendario Laboral es una web independiente que hace {B.OWNER} desde Valencia. No es una web oficial ni '
             f'depende de ninguna administración.</p>'
             f'<h2>De dónde salen los datos</h2><ul>'
             f'<li><b>Festivos nacionales y de cada comunidad:</b> la resolución del BOE '
             f'<a href="{src["url"]}" rel="noopener">{src["id"]}</a> ({E(src["boe"])}).</li>'
             f'<li><b>Festivos locales:</b> el boletín oficial de la provincia o de la comunidad, o el acuerdo del pleno '
             f'publicado por el ayuntamiento. Hoy hay {n_pub} municipios con fecha oficial; cada uno enlaza su fuente.</li>'
             f'<li><b>Calendario escolar:</b> la orden o resolución de cada consejería de educación, enlazada en cada página.</li>'
             f'</ul><h2>Cómo trabajamos</h2><ul>'
             f'<li>Cada fecha se copia del documento oficial y se enlaza. Si un dato no está publicado, ponemos «pendiente de '
             f'publicación oficial» y no adelantamos fechas de prensa ni del año anterior.</li>'
             f'<li>Los puentes, días laborables y planes de vacaciones se calculan con esas fechas; la regla está en '
             f'<a href="{B.BASE}puentes/">puentes 2027</a>.</li>'
             f'<li>De noviembre a enero, cuando salen los festivos locales, revisamos los boletines con frecuencia. Cada página '
             f'muestra la fecha de su última actualización.</li></ul>'
             f'<h2>Errores y avisos</h2><p>Si ves una fecha mal o tu municipio ya publicó sus festivos, escribe a {mail} con el '
             f'enlace al boletín o al acuerdo del pleno. Lo comprobamos con la fuente y lo corregimos.</p>'
             f'<h2>Cómo se paga</h2><p>Con anuncios de Google AdSense y con un enlace patrocinado a una agenda en papel. No '
             f'cambian ningún dato. No hay cuentas ni registro: lo que eliges se guarda solo en tu navegador '
             f'(<a href="{B.BASE}privacidad/">privacidad</a>).</p>', date)
    doc_page(write, "contacto/", "Contacto · El Calendario Laboral",
             "Escribe a El Calendario Laboral para corregir una fecha o avisar de los festivos locales de tu municipio.",
             "Contacto",
             f'<p>Correo: {mail}</p>'
             f'<h2>Para corregir un dato</h2><p>Indica la página y el enlace al documento oficial (BOE, boletín de tu comunidad '
             f'o de tu provincia, o acuerdo del pleno). Sin fuente oficial no podemos cambiar una fecha.</p>'
             f'<h2>Para el widget o los datos</h2><p>El <a href="{B.ASSETS}widget/">widget</a> y los archivos CSV e ICS se '
             f'pueden usar en tu web enlazando a esta página.</p>'
             f'<p>Respondemos por correo; no hay formulario ni guardamos tus datos.</p>', date)
    doc_page(write, "aviso-legal/", "Aviso legal · El Calendario Laboral",
             "Aviso legal de elcalendariolaboral.es: titular, contacto, condiciones de uso y responsabilidad sobre los datos.",
             "Aviso legal",
             f'<h2>Titular</h2><p>Esta web, {B.HOST}, es de {B.OWNER}. Contacto: {mail}.</p>'
             f'<h2>Objeto</h2><p>Informar de los festivos laborales, el calendario escolar y los puentes de España, con '
             f'herramientas gratuitas para planificar las vacaciones.</p>'
             f'<h2>Responsabilidad</h2><p>Los datos se toman de fuentes oficiales y se enlazan. Aun así, la información es '
             f'orientativa: el texto que vale es el publicado en el boletín oficial. No respondemos de decisiones tomadas '
             f'solo con esta web.</p>'
             f'<h2>Propiedad intelectual</h2><p>Las fechas oficiales son información pública. El diseño, los textos y las '
             f'herramientas de esta web son de su titular; puedes enlazarlos y usar el widget, citando la fuente.</p>'
             f'<h2>Enlaces y publicidad</h2><p>La web enlaza a boletines oficiales y a otros sitios que no controlamos. '
             f'Muestra anuncios de Google AdSense; los datos que usa Google se explican en la '
             f'<a href="{B.BASE}privacidad/">política de privacidad</a>.</p>'
             f'<h2>Ley aplicable</h2><p>Esta web se rige por la ley española, incluida la Ley 34/2002 de servicios de la '
             f'sociedad de la información.</p>', date)


def write_pages(write, cities, loc):
    page_puentes(write, cities)
    page_como(write, cities, loc)
    trust_pages(write, cities, loc)
