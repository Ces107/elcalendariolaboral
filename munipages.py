"""Province and municipality pages (Spanish only), from muni.catalogue(). Called by pages.write_pages when MUNI_ON.

Every sentence is computed from the place's own dates: what each local day does (puente, fin de semana largo,
sábado), how many municipalities of the province share it, the province's most repeated day, municipalities with the
same two days, working days against the province median, the best puente. Pending municipalities say so, show the
2026 days only as a labelled reference and compute puentes and working days without locals. No ads (seo/ads.md).
Size: shared header/footer/css/js, a compact 12-month grid (no ids, no data-*), no inlined planner data.
"""
import datetime as dt
from collections import Counter, defaultdict

import build as B
from build import E
import guia
from muni import OFFICIAL, catalogue, fold, load, short_src, wide_and_partial  # noqa: F401

P = None  # pages module
REG = {}
UPDATED = None  # date of locales-2027-all.json


def D(iso):
    return dt.date.fromisoformat(iso)


def hname(h):
    return h.get("name") or "Fiesta local"


def join(xs):
    xs = list(xs)
    return "" if not xs else xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


def link(x):
    return f'<a href="{B.BASE}{x["path"]}">{E(x["name"])}</a>'


def wide_of(x):
    return wide_and_partial(x["hol27"] or [])[0]


def facts(x):
    """Holidays, puentes and working days of one municipality (official locals only when published)."""
    if "f" in x:
        return x["f"]
    base = B.region_holidays(P.DATA, x["region"], x["zone"])
    wide, part = wide_and_partial(x["hol27"] or [])
    bd = {b["date"] for b in base}
    loc = [{"date": h["date"], "name": hname(h), "code": 0, "kind": "l"} for h in wide]
    hols = sorted(base + [h for h in loc if h["date"] not in bd], key=lambda h: h["date"]) if x["ok"] else base
    x["f"] = {"base": base, "wide": wide, "part": part, "hols": hols, "breaks": B.all_breaks(hols), "pts": B.puentes(hols),
              "lab": B.workdays(hols), "blab": B.workdays(base), "bpts": B.puentes(base)}
    return x["f"]


def effect(h, f):
    """What one local day does for someone who works Monday to Friday."""
    d = D(h["date"])
    i = (d - B.DAYS[0]).days
    same = [b["name"] for b in f["base"] if b["date"] == h["date"]]
    if same:
        return f'coincide con {E(same[0])}, que ya es festivo en la comunidad'
    if d.weekday() >= 5:
        return f'cae en {B.T["_wd"][d.weekday()]} y no suma un día libre entre semana'
    it = next((b for b in f["breaks"] if b["s"] <= i <= b["e"]), None)
    if it and it["cost"]:
        return f'puente de {it["len"]} días ({B.drange(it["s"], it["e"])}) pidiendo {B.dlist(it["take"])}'
    if it:
        return f'fin de semana largo de {it["len"]} días ({B.drange(it["s"], it["e"])}) sin pedir vacaciones'
    return f'cae en {B.T["_wd"][d.weekday()]}, sin puente de 1 o 2 días'


def prov_stats(p):
    if "st" in p:
        return p["st"]
    ok = [x for x in p["munis"] if x["ok"]]
    by_date = defaultdict(list)
    for x in ok:
        for h in wide_of(x):
            by_date[h["date"]].append(x)
    dates = Counter({d: len(xs) for d, xs in by_date.items()})
    labs = sorted(facts(x)["lab"] for x in ok)
    srcs = Counter((x["src27"] or {}).get("title", "") for x in ok)
    p["st"] = {"ok": ok, "dates": dates, "by_date": by_date, "med": labs[len(labs) // 2] if labs else None,
               "labs": labs, "srcs": [s for s, _ in srcs.most_common() if s],
               "urls": {(x["src27"] or {}).get("title", ""): (x["src27"] or {}).get("url", "") for x in ok}}
    return p["st"]


def mini_year(hols):
    """12 small month tables, ~3 KB: no ids, no data-*, blank cells before day 1 (weekends styled by column in CSS),
    optional end tags left out (valid HTML)."""
    hm = {}
    for h in hols:
        hm.setdefault(h["date"], h)
    out = []
    for m in range(1, 13):
        first = dt.date(B.YEAR, m, 1)
        nd = ((dt.date(B.YEAR + (m == 12), m % 12 + 1, 1)) - first).days
        col = first.weekday()
        rows = "<tr>" + "<td>" * col
        for d in range(1, nd + 1):
            h = hm.get(f"{B.YEAR}-{m:02d}-{d:02d}")
            rows += f'<td class={h["kind"]}>{d}' if h else f"<td>{d}"
            col += 1
            if col == 7 and d < nd:
                rows += "<tr>"
                col = 0
        out.append(f'<table class=mc><caption>{B.T["_months"][m - 1].capitalize()}</caption>'
                   f'<tr><th>L<th>M<th>X<th>J<th>V<th>S<th>D{rows}</table>')
    return '<div class="mcs">' + "".join(out) + "</div>"


def pts_rows(breaks):
    """Puentes table, compact markup (same columns as build.pts_row)."""
    out = []
    for it in breaks:
        nm = " · ".join(it["names"])
        vac = (f'<b>{it["cost"]}</b> <span class="m">{E(B.dlist(it["take"]))}</span>' if it["cost"]
               else f'<b>0</b> <span class="m">{B.t("no_vac")}</span>')
        out.append(f'<tr{" class=lw" if not it["cost"] else ""}><td><b>{B.drange(it["s"], it["e"])}</b><br><span class="m">{E(nm)}</span>'
                   f'<td class=num>{it["len"]}<td>{vac}')
    return "".join(out)


def hl_rows(hols):
    """The holiday list, compact (same look as build.hol_item)."""
    out = []
    for h in hols:
        d = D(h["date"])
        out.append(f'<li class=k-{h["kind"]}><span class=d><time datetime={h["date"]}>{B.dm(d)}</time> <i>{B.T["_wd"][d.weekday()]}</i>'
                   f'</span><span class=h>{E(h["name"])}</span><span class=s>{B.scope_txt(h["kind"])}</span>')
    return '<ol class="hl hm">' + "".join(out) + "</ol>"


def legend(kinds):
    return '<ul class="legend">' + "".join(f'<li>{B.sw(k)}{B.scope_txt(k)}</li>' for k in kinds) + "</ul>"


def region_ics(x):
    k = x["region"] + (f'-{x["zone"]}' if x["zone"] and x["zone"] != "general" else "")
    return f"{B.ASSETS}ics/{k}.ics"


def nearest(munis, k=6):
    """x["near"] = [(municipality, km)] for the k nearest by great-circle distance (coordinates: Wikidata, CC0)."""
    import numpy as np
    xs = [x for x in munis if x["m"].get("lat") is not None]
    lat = np.radians([x["m"]["lat"] for x in xs])
    lon = np.radians([x["m"]["lon"] for x in xs])
    for i, x in enumerate(xs):
        h = np.sin((lat - lat[i]) / 2) ** 2 + np.cos(lat[i]) * np.cos(lat) * np.sin((lon - lon[i]) / 2) ** 2
        d = 2 * 6371 * np.arcsin(np.sqrt(h))
        d[i] = np.inf
        idx = np.argpartition(d, k)[:k]
        x["near"] = [(xs[j], max(1, int(round(d[j])))) for j in sorted(idx, key=lambda j: d[j])]


def by_pop(xs):
    """Biggest first (INE official population), then name."""
    return sorted(xs, key=lambda y: (-(y["m"].get("pop") or 0), fold(y["name"])))


def dates_of(x):
    if not x["ok"]:
        return "pendiente"
    return " · ".join(B.dmon(h["date"]) for h in wide_of(x)) or "por localidad"


# ---------------------------------------------------------------- municipality

def notes_official(x, f, p, st, rname):
    items = []
    wide = f["wide"]
    for h in wide:
        items.append(f'<b>{B.dlong(h["date"]).capitalize()}:</b> {effect(h, f)}.')
    for h in wide:
        sh = [y for y in st["by_date"].get(h["date"], []) if y is not x]
        if sh:
            ex = by_pop(sh)[:3]
            items.append(f'<b>El {B.dm(h["date"])} en {E(p["name"])}:</b> también es fiesta local en {len(sh)} '
                         f'municipio{"s" if len(sh) != 1 else ""} más, como {join(link(y) for y in ex)}.')
        else:
            items.append(f'<b>El {B.dm(h["date"])} en {E(p["name"])}:</b> ningún otro municipio con fecha publicada lo tiene.')
    mine = sorted(h["date"] for h in wide)
    twins = [y for y in st["ok"] if y is not x and len(mine) == 2 and sorted(h["date"] for h in wide_of(y)) == mine]
    if twins:
        tw = by_pop(twins)
        items.append(f'<b>Los mismos días que</b> {join(link(y) for y in tw[:5])}' + (f' y {len(tw) - 5} más' if len(tw) > 5 else "") + ".")
    top = st["dates"].most_common(1)
    if top and top[0][0] not in mine and top[0][1] > 1:
        items.append(f'<b>El día más repetido en {E(p["name"])}</b> es el {B.dlong(top[0][0])} ({top[0][1]} municipios); '
                     f'aquí es laborable.')
    diff = f["lab"] - (st["med"] or f["lab"])
    items.append(f'<b>{f["lab"]} días laborables</b> de lunes a viernes: '
                 + (f'{abs(diff)} {"más" if diff > 0 else "menos"} que la mediana de {E(p["name"])} ({st["med"]})' if diff
                    else f'igual que la mediana de {E(p["name"])}') + f'. Sin los locales, {f["blab"]}.')
    b = guia.best(f["breaks"])
    if b:
        same = any((b["s"], b["e"]) == (y["s"], y["e"]) for y in f["bpts"])
        items.append(f'<b>Mejor puente{" (el de toda la comunidad)" if same else ""}:</b> {guia.brk(b)}.')
    return items


def notes_pending(x, f, p, st, rname):
    items = []
    if x["ref26"] or x.get("nuc26"):
        w26 = wide_and_partial(x["ref26"])[0]
        ds = [B.dlong(h["date"]) + " de 2026" + (f' ({E(h["name"])})' if h.get("name") else "") for h in w26]
        s = x["src26"] or {}
        sl = (f'<a href="{E(s["url"])}" rel="noopener">{E(short_src(s.get("title")))}</a>' if s.get("url")
              else E(short_src(s.get("title"))))
        ref = "<b>Referencia 2026 (no es el calendario oficial de 2027):</b>"
        if ds:
            items.append(f'{ref} en 2026 fueron el {join(ds)} ({sl}).')
        nuc = x.get("nuc26") or []
        if nuc:
            li = "".join(f'<li><b>{E(n["name"])}</b> <span class="m">' + ", ".join(
                B.dmon(h["date"]) + " 2026" + (f' ({E(h["name"])})' if h.get("name") else "") for h in n.get("holidays") or [])
                + "</span></li>" for n in nuc)
            items.append(("" if ds else f"{ref} ") + f'<details class="more"><summary>En 2026 cada núcleo tuvo su propia fiesta '
                         f'({len(nuc)})</summary><ul class="links">{li}</ul></details>')
        if s.get("published"):
            items.append(f'<b>Cuándo salen:</b> las de 2026 se publicaron el {B.dmy(s["published"])}. Esta página cambia en '
                         f'cuanto se publiquen las de 2027.')
    if st["ok"]:
        top = st["dates"].most_common(1)[0]
        items.append(f'<b>En {E(p["name"])}</b> ya tienen fecha {len(st["ok"])} de {len(p["munis"])} municipios'
                     + (f'; el día más repetido es el {B.dlong(top[0])} ({top[1]}).' if top[1] > 1 else
                        f' ({join(link(y) for y in by_pop(st["ok"])[:3])}).'))
    b = guia.best(f["breaks"])
    if b:
        items.append(f'<b>Mejor puente de {E(rname)}:</b> {guia.brk(b)}.')
    items.append('<b>Puentes y días laborables</b> de esta página: solo con los festivos de la comunidad, sin los locales.')
    return items


def muni_page(x, cat, write):
    m, p, r = x["m"], x["prov"], REG[x["region"]]
    f = facts(x)
    name, ok, rname = x["name"], x["ok"], r["name"]
    nm_t = f'{name} ({p["name"]})' if cat["dup_names"][name] > 1 else name
    st = prov_stats(p)
    wide, part = f["wide"], f["part"]
    kinds = ["n", "r"] + (["i"] if x["region"] == "canarias" and x["zone"] else []) + ["l"]
    crumbs = [("España", ""), (rname, f'{r["slug"]}/')] + ([(p["label"], p["path"])] if p["path"] else []) + [(name, x["path"])]
    isl = ""
    if x["region"] == "canarias" and x["zone"]:
        o = next(o for o in P.DATA["zones"]["canarias"]["options"] if o["slug"] == x["zone"])
        isl = f', con la fiesta de {E(o["name"])} el {B.dm(o["add"]["date"])}'
    elif x["zone"] == "aran":
        isl = ", con la Fiesta de Arán el 17 de junio en lugar del Lunes de Pascua"
    upd_date = UPDATED or P.DATA["updated"]
    if ok and wide:
        ds = [f'<b>{B.dlong(h["date"])}</b>' + (f' ({E(h["name"])})' if h.get("name") else "") for h in wide]
        lead = (f'{"Los festivos locales" if len(wide) > 1 else "El festivo local"} de {E(name)} en 2027 '
                f'{"son el" if len(wide) > 1 else "es el"} {join(ds)}. Con los {len(f["base"])} de {E(rname)}{isl}, '
                f'{len(f["hols"])} festivos y {f["lab"]} días laborables.')
        items = notes_official(x, f, p, st, rname)
    elif ok:
        lead = (f'El boletín no fija para 2027 un festivo local común a todo {E(name)}: cada localidad tiene los suyos. '
                f'Con los {len(f["base"])} de {E(rname)}{isl}, {f["blab"]} días laborables antes de los locales.')
        items = [f'<b>Puentes y días laborables</b> de esta página: con los festivos de {E(rname)}; los de cada localidad, abajo.']
    else:
        lead = (f'Las fiestas locales de 2027 de {E(name)} aún no se han publicado en el boletín oficial. Con los '
                f'{len(f["base"])} festivos de {E(rname)}{isl}, {f["blab"]} días laborables antes de restar los locales.')
        items = notes_pending(x, f, p, st, rname)
    if part:
        items.append("<b>Solo en una parte del municipio:</b> " + "; ".join(f'{B.dm(h["date"])}, {E(hname(h))}' for h in part) + ".")
    locs = x.get("localities") or []
    loc_html = ""
    if locs:
        li = "".join(f'<li><b>{E(lo["name"])}</b> <span class="m">' + ", ".join(
            B.dmon(h["date"]) + (f' ({E(h["name"])})' if h.get("name") else "") for h in lo["holidays"]) + "</span></li>" for lo in locs)
        loc_html = f'<h3 class="h3">Solo en cada localidad</h3><ul class="links">{li}</ul>'

    src = x["src27"] or {}
    if ok and src:
        stt = " · acuerdo del ayuntamiento, pendiente del boletín" if x["status"] == "ayuntamiento" else ", según el boletín"
        s_html = (f'Locales: <a href="{E(src.get("url") or "")}" rel="noopener" title="{E(src.get("title", ""))}">'
                  f'{E(short_src(src.get("title"), "Ayuntamiento de " + name))}</a>{stt}')
    else:
        s_html = 'Locales 2027: pendientes de publicación oficial'
    srcline = (f'<p class="src">{s_html} · Comunidad: <a href="{P.DATA["source"]["url"]}" rel="noopener">{P.DATA["source"]["id"]}</a>'
               f' · Actualizado: <time datetime="{upd_date}">{B.dmy(upd_date)}</time></p>')
    where = E(p["name"]) + (f', {E(rname)}' if p["name"] != rname else "")
    offn = f' · nombre oficial: {E(x["official_name"])}' if x["official_name"] != name else ""

    stats = B.stats_html([(None, B.tn("n_hol", len(f["hols"])) + ("" if ok else " sin locales")), (None, B.tn("n_lab", f["lab"])),
                          (None, B.tn("n_pts", len(f["pts"])))])
    ics = region_ics(x)
    gc = [(f'{B.dmon(h["date"])} · {hname(h)}', B.gcal_event(h["date"], hname(h), name)) for h in wide] if ok else []
    gc.append((f'Festivos de {rname} (suscripción)', "https://calendar.google.com/calendar/r?cid=" + B.quote(f"webcal://{B.HOST}{ics}", safe="")))
    acts = B.actions_html(ics, f'festivos-2027-{m["slug"]}.ics', f"Calendario laboral {name} 2027", gc)
    acts = acts.replace('data-x="dl"', f'data-ics="{E(name)}" data-key="{m["ine"]}"', 1)
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}'
            + B.hero_grid(f'<h1>Calendario laboral {E(name)} 2027</h1><p class="lead">{lead}</p>',
                          B.next_card(f["hols"], prev=B.prev26(x["region"], x["zone"], wide_and_partial(x["ref26"] or [])[0])) + stats + acts, f'<p class="ctx">{where}{offn}</p>{srcline}') + '</div>')

    pts = pts_rows(f["breaks"]) or f'<tr><td colspan="3">{B.t("no_bridges")}</td></tr>'
    close = x.get("near") or []  # 6 nearest by distance (Wikidata coordinates), any province
    seen = {id(y) for y, _ in close}
    big = [y for y in by_pop(p["munis"]) if y is not x and id(y) not in seen][:4 if close else 8]
    near_html = "".join(f'<li>{link(y)} <span class="m">{d} km · {dates_of(y)}</span></li>' for y, d in close)
    big_html = "".join(f'<li>{link(y)} <span class="m">{dates_of(y)}</span></li>' for y in big)
    up = ('<p class="more-l">' + (f'<a href="{B.BASE}{p["path"]}">{E(p["label"])}: los {len(p["munis"])} municipios</a> · ' if p["path"] else "")
          + f'<a href="{B.BASE}{r["slug"]}/">Calendario laboral 2027 de {E(rname)}</a></p>')
    body = (B.section("festivos", f'Festivos 2027 en {E(name)}', hl_rows(f["hols"]) + loc_html)
            + B.section("claves", f'Qué cambian los festivos de {E(name)}' if ok and wide else f'{E(name)} en 2027', guia.notes(items))
            + B.section("calendario", "Calendario 2027", legend(kinds) + mini_year(f["hols"]), cls="cal")
            + B.section("puentes", f'Puentes 2027 en {E(name)}', f'<table class="tbl ptm"><thead><tr><th scope="col">Puente<th scope="col" class="num">Días libres'
                        f'<th scope="col">Vacaciones</thead><tbody>{pts}</tbody></table>')
            + (B.section("cerca", f'Cerca de {E(name)}', f'<ul class="links">{near_html}</ul>') if close else "")
            + B.section("mas", f'Más municipios de {E(p["name"])}', f'<ul class="links">{big_html}</ul>{up}'))
    main = f'{hero}<div class="wrap body">{body}</div>'

    if ok and wide:
        d_ = [B.dmon(h["date"]) for h in wide[:3]]
        title = B.pick(60, f"Calendario laboral {nm_t} 2027: festivos {join(d_)}", f"Festivos {nm_t} 2027: {join(d_)}",
                       f"Calendario laboral {nm_t} 2027", f"Festivos {nm_t} 2027")
        nmx = lambda h: f' ({h["name"]})' if h.get("name") else ""  # noqa: E731
        tail = f'Con los {len(f["base"])} de {rname}: {len(f["hols"])} festivos, {len(f["pts"])} puentes y {f["lab"]} días laborables.'
        desc = B.pick(155, f'Festivos locales de {name} ({p["name"]}) en 2027: {join(B.dlong(h["date"]) + nmx(h) for h in wide)}. {tail}',
                      f'Festivos locales de {name} ({p["name"]}) en 2027: {join(B.dlong(h["date"]) for h in wide)}. {tail}',
                      f'Festivos locales de {name} en 2027: {join(d_)}. {tail}',
                      f'Festivos locales de {name} en 2027: {join(d_)}. {len(f["hols"])} festivos y {f["lab"]} días laborables.')
    else:
        title = B.pick(60, f"Calendario laboral {nm_t} 2027", f"Festivos {nm_t} 2027")
        desc = B.pick(155, f'Calendario laboral 2027 de {name} ({p["name"]}): festivos de {rname}, puentes y días laborables. '
                           f'Locales {"por localidad" if ok else "pendientes de publicación"}.',
                      f'Calendario laboral 2027 de {name}: festivos de {rname} y puentes.')
    head = B.head_html(title, desc, x["path"], f'{B.SITE}{B.ASSETS}og/{x["region"]}.png',
                       P.ld(P.crumbs_ld(crumbs), P.webpage_ld(title, x["path"], upd_date)), langs=["es"], index=ok, ads=False)
    write(x["path"], B.page(head, "pg mu", "", main, P.DATA, js=False, lean=True), upd_date, ["es"])


# ---------------------------------------------------------------- province

def prov_page(p, cat, write):
    r = REG[p["region"]]
    st = prov_stats(p)
    munis = sorted(p["munis"], key=lambda y: fold(y["name"]))
    n, n_ok = len(munis), len(st["ok"])
    pend = n - n_ok
    base = B.region_holidays(P.DATA, r["slug"])
    lab = B.workdays(base, 1 if r["slug"] == "canarias" else 0)
    place = ("la Comunidad de Madrid" if r["slug"] == "madrid" else p["name"]) if p["uni"] else f'la provincia de {p["name"]}'
    h1 = f'Festivos locales 2027 en {"los municipios de " + place if p["uni"] else place}'
    items = []
    if n_ok:
        top = st["dates"].most_common(5)
        items.append("<b>Los días más repetidos:</b> " + "; ".join(f'{B.dlong(d)}, en {c} municipio{"s" if c != 1 else ""}' for d, c in top) + ".")
        wd = Counter()
        mo = Counter()
        for d, c in st["dates"].items():
            wd[D(d).weekday()] += c
            mo[D(d).month] += c
        tot = sum(wd.values())
        items.append(f'<b>Día de la semana:</b> {wd[0] + wd[4]} de los {tot} días locales caen en lunes o viernes (fin de semana '
                     f'largo) y {wd[5] + wd[6]} en sábado o domingo, sin día libre extra.')
        m1 = mo.most_common(1)[0]
        items.append(f'<b>El mes con más fiestas locales:</b> {B.T["_months"][m1[0] - 1]}, con {m1[1]}.')
        cap = cat["by_ine"].get(p.get("capital_ine"))
        if cap and cap["ok"]:
            items.append(f'<b>La capital,</b> {link(cap)}: {join(B.dlong(h["date"]) for h in wide_of(cap))}.')
        items.append(f'<b>Días laborables</b> con los locales: de {st["labs"][0]} a {st["labs"][-1]} según el municipio '
                     f'(mediana {st["med"]}); {lab} con solo los festivos de {E(r["name"])}.')
    if pend:
        y26 = sorted({(x["src26"] or {}).get("published") for x in munis if not x["ok"] and x["src26"]} - {None})
        items.append(f'<b>Pendientes:</b> {pend} municipio{"s" if pend != 1 else ""} sin fecha oficial para 2027'
                     + (f'; las de 2026 se publicaron el {B.dmy(y26[0])}' if y26 else "")
                     + ". Sus páginas cambian cuando salga el boletín.")
    if st["srcs"]:
        items.append("<b>Fuente:</b> " + "; ".join(f'<a href="{E(st["urls"].get(s, ""))}" rel="noopener" title="{E(s)}">'
                                                  f'{E(short_src(s, s[:60]))}</a>' for s in st["srcs"][:4]) + ".")
    if n_ok:
        lead = (f'<b>{n_ok} de {n} municipios</b> de {E(place)} tienen publicados sus festivos locales de 2027'
                + (f'; {pend} siguen pendientes.' if pend else ".") + f' A ellos se suman los {len(base)} de {E(r["name"])}.')
    else:
        lead = (f'Los festivos locales de 2027 de los {n} municipios de {E(place)} aún no se han publicado en el boletín oficial. '
                f'Mientras, valen los {len(base)} festivos de {E(r["name"])}.')
    def ul(xs):  # biggest first (INE population); app.js re-sorts A-Z with the toggle (data-a = folded name)
        return ('<ul class="links" data-sortable>' + "".join(
            f'<li data-a="{E(fold(x["name"]))}">{link(x)} <span class="m">{dates_of(x)}</span></li>' for x in by_pop(xs)) + "</ul>")
    pub, pen = [x for x in munis if x["ok"]], [x for x in munis if not x["ok"]]
    rows = ((f'<h3 class="h3">Con festivos de 2027 publicados ({len(pub)})</h3>{ul(pub)}' if pub else "")
            + (f'<h3 class="h3">Pendientes de publicación ({len(pen)})</h3>{ul(pen)}' if pen else ""))
    az = ('<p class="srt" role="group" aria-label="Orden"><button type="button" class="btn sm on" data-sort="pop" aria-pressed="true">'
          'Por población</button><button type="button" class="btn sm" data-sort="az" aria-pressed="false">A–Z</button></p>')
    chips = "".join(f'<li class="k-{h["kind"]}">{B.sw(h["kind"])}{B.dmon(h["date"])} · {E(h["name"])}</li>' for h in base)
    crumbs = [("España", ""), (r["name"], f'{r["slug"]}/'), (p["label"], p["path"])]
    upd_date = UPDATED or P.DATA["updated"]
    stats = B.stats_html([(None, f"{n} municipios"), (None, f"{n_ok} publicados"), (None, f"{pend} pendientes")])
    meta = (f'<p class="upd">Actualizado: <time datetime="{upd_date}">{B.dmy(upd_date)}</time> · Comunidad: '
            f'<a href="{P.DATA["source"]["url"]}" rel="noopener">{P.DATA["source"]["id"]}</a></p>')
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}'
            + B.hero_grid(f'<h1>{E(h1)}</h1><p class="lead">{lead}</p>', stats + B.search_box("q-prov"), meta) + '</div>')
    body = (B.section("claves", "Lo que dicen las fechas", guia.notes(items))
            + B.section("comunidad", f'Los {len(base)} festivos de {E(r["name"])}', f'<ul class="dchips">{chips}</ul>'
                        f'<p class="more-l"><a href="{B.BASE}{r["slug"]}/">Calendario laboral 2027 de {E(r["name"])}</a></p>')
            + B.section("municipios", f'Los {n} municipios', f'{az}{rows}'))
    main = f'{hero}<div class="wrap body narrow">{body}</div>'
    pn = "Madrid" if p["uni"] and r["slug"] == "madrid" else p["name"]
    if n_ok:
        top2 = [B.dmon(d) for d, _ in st["dates"].most_common(2)]
        title = B.pick(60, f'Festivos locales 2027 {pn}: {n_ok} municipio{"s" if n_ok != 1 else ""} publicado{"s" if n_ok != 1 else ""}', f'Festivos locales 2027 en {pn}')
        desc = B.pick(155, f'Festivos locales 2027 de los {n} municipios de {pn}: {n_ok} ya publicado{"s" if n_ok != 1 else ""}, los días más repetidos '
                           f'({join(top2)}) y los {len(base)} festivos de {r["name"]}.',
                      f'Festivos locales 2027 de los {n} municipios de {pn}: {n_ok} publicado{"s" if n_ok != 1 else ""} y los {len(base)} de {r["name"]}.')
    else:
        title = B.pick(60, f'Festivos locales 2027 {pn}: los {n} municipios', f'Festivos locales 2027 en {pn}')
        desc = B.pick(155, f'Festivos locales 2027 de los {n} municipios de {pn}: pendientes del boletín oficial. Mientras, los '
                           f'{len(base)} festivos de {r["name"]}.', f'Festivos locales 2027 en {pn}: pendientes del boletín.')
    head = B.head_html(title, desc, p["path"], f'{B.SITE}{B.ASSETS}og/{r["slug"]}.png',
                       P.ld(P.crumbs_ld(crumbs), P.webpage_ld(title, p["path"], upd_date)), langs=["es"], ads=False)
    write(p["path"], B.page(head, "pg", "", main, P.DATA, js=False, lean=True), upd_date, ["es"])


def write_pages(pages_mod, write):
    """Province pages and a page for every municipality without a rich city page."""
    global P, UPDATED
    P = pages_mod
    REG.update({r["slug"]: r for r in P.DATA["regions"]})
    cat = catalogue()
    a27 = load("locales-2027-all.json") or {}
    UPDATED = a27.get("updated")
    cat["dup_names"] = Counter(x["name"] for x in cat["munis"])
    e27 = a27.get("municipios", {})
    for x in cat["munis"]:
        x["localities"] = (e27.get(x["ine"]) or {}).get("localities") if x["ok"] and x["kind"] == "page" else None
    nearest(cat["munis"])
    for p in cat["provs"]:
        if p["path"]:
            prov_page(p, cat, write)
    n = 0
    for x in cat["munis"]:
        if x["kind"] == "page":
            muni_page(x, cat, write)
            n += 1
    print(f"muni · {n} municipality pages ({sum(1 for x in cat['munis'] if x['kind'] == 'page' and x['ok'])} official), "
          f"{sum(1 for p in cat['provs'] if p['path'])} province pages · conflicts {len(cat['conflicts'])} · "
          f"unmatched {len(cat['unmatched'])}")
    return cat
