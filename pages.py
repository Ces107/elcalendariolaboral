"""Pages built from data, called by build.py: home, the 19 regions, city pages and the /festivos-locales/ hub.

Each page type has a data part (what it says) and an HTML part; shared components (head, header, tables, footer)
are in build.py. The FAQ and the explanatory sentences exist only in Spanish: the ca/gl/eu pages leave them out
instead of mixing languages.

    data/2027.json          home, regions, cities (BOE holidays, islands, Arán)
    data/locales-2027.json  cities: only status "boletin" or "ayuntamiento" get a page; "unpublished" only appear in the hub
"""
import datetime as dt
import html
import json
import re

import sys

import build as B
import guia
from build import E, t, tn

SCHEMA = "https://schema.org"
PUBLISHED = ("boletin", "ayuntamiento")
ISLAND_CITIES = {  # Canarias: each city page adds its island's holiday (test_data.py checks every Canarias city is here)
    "gran-canaria": ["las-palmas-de-gran-canaria", "telde", "santa-lucia-de-tirajana", "san-bartolome-de-tirajana", "arucas",
                     "ingenio", "aguimes", "galdar", "mogan"],
    "tenerife": ["santa-cruz-de-tenerife", "san-cristobal-de-la-laguna", "arona", "adeje", "granadilla-de-abona", "la-orotava",
                 "los-realejos", "puerto-de-la-cruz", "tacoronte", "candelaria", "icod-de-los-vinos", "san-miguel-de-abona", "guimar"],
    "lanzarote": ["arrecife", "teguise", "tias"],
    "fuerteventura": ["puerto-del-rosario", "la-oliva"],
    "la-palma": ["los-llanos-de-aridane", "santa-cruz-de-la-palma"],
    "la-gomera": ["san-sebastian-de-la-gomera"],
    "el-hierro": ["valverde"],
}
CITY_ZONE = {c: island for island, cs in ISLAND_CITIES.items() for c in cs}
VARIANT = {"cataluna": "Catalunya", "pais-vasco": "Euskadi", "comunitat-valenciana": "Comunitat Valenciana, GVA",
           "baleares": "Illes Balears"}
ES = B.LANG == "es"

_written = []
_fix = None


def load_locales():
    """locales-2027.json, with the bulletin data of locales-2027-all.json laid over it (muni.overlay_locales)."""
    import muni
    return muni.overlay_locales(json.loads((B.ROOT / "data" / "locales-2027.json").read_text("utf-8")))


def D(iso):
    return dt.date.fromisoformat(iso)


def tm(iso, txt):
    return f'<time datetime="{iso}">{txt}</time>'


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def first_sentences(s, limit):
    """Drop trailing sentences until the text fits (meta descriptions)."""
    while len(s) > limit and ". " in s.rstrip(". "):
        s = s.rstrip(". ").rsplit(". ", 1)[0] + "."
    return s


def ld(*objs):
    return "".join(f'<script type="application/ld+json">{json.dumps({"@context": SCHEMA, **o}, ensure_ascii=False, separators=(",", ":"))}</script>'
                   for o in objs if o)


def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "name": n, "item": B.URL + p} for k, (n, p) in enumerate(items)]}


def faq_ld(qas):
    if not qas:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qas]}


def webpage_ld(name, path, date):
    """WebPage with the visible 'Actualizado' date (never the build date)."""
    return {"@type": "WebPage", "name": name, "url": B.URL + path, "inLanguage": B.IN_LANG[B.LANG], "dateModified": date,
            "isPartOf": {"@type": "WebSite", "@id": f"{B.SITE}{B.ASSETS}#web", "name": t("site_name"), "url": f"{B.SITE}{B.ASSETS}"},
            "publisher": {"@type": "Organization", "@id": f"{B.SITE}{B.ASSETS}#org", "name": t("site_name")}}


def list_ld(name, hols):
    return {"@type": "ItemList", "name": name, "numberOfItems": len(hols), "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "name": f'{h["name"]} · {B.dlong(h["date"])} 2027'} for k, h in enumerate(hols)]}


def dataset_ld(name, desc, path, place, based_on, downloads):
    return {"@type": "Dataset", "name": name, "description": desc, "url": B.URL + path, "inLanguage": B.IN_LANG[B.LANG],
            "dateModified": DATA["updated"], "temporalCoverage": "2027-01-01/2027-12-31",
            "spatialCoverage": {"@type": "Place", "name": f'{place}, {t("spain")}'}, "isBasedOn": based_on,
            "creator": {"@type": "Organization", "name": t("site_name")},
            "distribution": [{"@type": "DataDownload", "encodingFormat": f, "contentUrl": f"{B.SITE}{B.ASSETS}{u}"} for f, u in downloads]}


def faq_html(qas):
    if not qas:
        return ""
    items = "".join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>' for q, a in qas)
    return B.section("faq", t("h_faq"), f'<div class="faq">{items}</div>')


THIN_ADS = 250  # visible words of 2+ letters in <main>, month grids left out: below it a page carries no ads (seo/ads.md)
_RX_GRID = re.compile(r"<caption>Enero</caption>.*?<caption>Diciembre</caption>.*?(?:</table>|</div>)", re.S)
_RX_AD = re.compile(r'<aside class="ad ad-[a-z]+".*?</aside>', re.S)
thin_no_ads = []  # paths whose ads the guard removed (printed by the build, listed in seo/ADSENSE-READINESS-*.md)


def main_words(page):
    """Same count as seo/audit_site.py: words of 2+ letters in <main>, without scripts and the 12-month grid."""
    m = re.search(r"<main\b.*?</main>", page, re.S)
    t = _RX_GRID.sub(" ", m.group(0) if m else "")
    t = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", t, flags=re.S)
    return len(re.findall(r"[^\W\d_]{2,}", html.unescape(re.sub(r"<[^>]+>", " ", t))))


def no_thin_ads(path, page):
    """Policy guard: a page with the AdSense loader but less than THIN_ADS words loses the loader and its units."""
    if B.ADSENSE not in page or main_words(page) >= THIN_ADS:
        return page
    thin_no_ads.append(path)
    return _RX_AD.sub("", page.replace(B.AD_HINTS + B.ADSENSE, "").replace(B.ADSENSE, ""))


def write(path, page, lastmod, langs=None):
    """langs: the languages this page exists in, when not all of them (the sitemap lists only those)."""
    d = B.OUT / path
    d.mkdir(parents=True, exist_ok=True)
    page = no_thin_ads(path, page)
    noindex = 'name="robots" content="noindex' in page
    if not noindex and not re.search(r'"@type": ?"WebPage"', page):  # every indexable page states its content date
        m = re.search(r"<title>(.*?)</title>", page)
        page = page.replace("</head>", ld(webpage_ld(html.unescape(m.group(1)), path, lastmod)) + "\n</head>", 1)
    (d / "index.html").write_text(_fix(page), "utf-8", newline="\n")
    if noindex:
        return  # reachable, but not in the sitemap
    _written.append((path, lastmod, langs) if langs else (path, lastmod))


def prov_links(region, province=None):
    """Links to the province pages of munipages.py (all municipalities with their status), Spanish, when MUNI_ON."""
    import muni
    if not (ES and muni.MUNI_ON):
        return ""
    ps = [p for p in muni.catalogue()["provs"] if p["region"] == region and p["path"] and (province is None or p["name"] == province)]
    if not ps:
        return ""
    lab = "Todos los municipios" if province is None else "Los demás municipios"
    return (f'<p class="more-l">{lab}: ' + " · ".join(f'<a href="{B.BASE}{p["path"]}">{E(p["label"])} ({len(p["munis"])})</a>' for p in ps)
            + "</p>")


def quick_access(r):
    """Right under the answer on a comunidad page: the search box and the province pages (every municipality)."""
    import muni
    ps = [p for p in muni.catalogue()["provs"] if p["region"] == r["slug"] and p["path"]] if muni.MUNI_ON else []
    if not ps:
        return ""
    links = " · ".join(f'<a href="{B.ASSETS}{p["path"]}">{E(p["label"])} <span class="m">({len(p["munis"])})</span></a>' for p in ps)
    n = sum(len(p["munis"]) for p in ps)
    lab = f"Los {n} municipios" if ES else t("municipio")
    caps = {p.get("capital_ine") for p in ps}
    ex = [x["name"] for x in sorted((x for p in ps for x in p["munis"] if x["ine"] not in caps),
                                    key=lambda x: -(x["m"].get("pop") or 0))[:2]]
    ph = f'Ej.: {", ".join(ex)}' if ES and len(ex) == 2 else None
    return (f'<div class="qa">{B.search_box("q-reg", big=True, region=r["slug"], ph=ph)}'
            f'<p class="qa-l"><b>{lab}:</b> {links}</p></div>')


def muni_directory(r):
    """Comunidad page, Spanish: every province with its published / pending count and its biggest municipalities
    (2027 dates, or 'pendiente'), each linking to its page; the province page lists all of them."""
    import muni
    import munipages as MP
    if not (ES and muni.MUNI_ON):
        return ""
    ps = [p for p in muni.catalogue()["provs"] if p["region"] == r["slug"] and p["path"] and p["munis"]]
    if not ps:
        return ""
    k = 24 if len(ps) == 1 else 12 if len(ps) <= 3 else 6  # Castilla y León: 9 provinces x 6, not a 100-row wall
    out = []
    for p in sorted(ps, key=lambda p: muni.fold(p["name"])):
        ok = sum(1 for x in p["munis"] if x["ok"])
        pen = len(p["munis"]) - ok
        cnt = " · ".join(s for s in (f"{ok} publicado{'s' if ok != 1 else ''}" if ok else "", f"{pen} pendiente{'s' if pen != 1 else ''}" if pen else "") if s)
        li = "".join(f'<li>{MP.link(x)} <span class="m{"" if x["ok"] else " pe"}">{MP.dates_of(x)}</span></li>'
                     for x in MP.by_pop(p["munis"])[:k])
        out.append(f'<h3 class="h3"><a href="{B.BASE}{p["path"]}">{E(p["label"])}</a> <span class="m">{cnt}</span></h3>'
                   f'<ul class="links">{li}</ul>'
                   f'<p class="more-l"><a href="{B.BASE}{p["path"]}">Los {len(p["munis"])} municipios →</a></p>')
    return "".join(out)


def school_link(r):
    """Spanish only: the school calendar pages have no ca/gl/eu version."""
    return f' · <a href="{B.BASE}calendario-escolar/{r["slug"]}/">Calendario escolar 2026-27 en {E(r["name"])}</a>' if ES else ""


def workdays_link(r):
    """The comunidad's row of /dias-laborables-2027/ (utilidades.py), in the languages that page exists in."""
    import utilidades
    if B.LANG not in utilidades.ONLY_DL:
        return ""
    return f' · <a href="{B.BASE}{utilidades.PATH_DL}#{r["slug"]}">{E(utilidades.L("dl_link"))}</a>'


def city_list(cities):
    """Links to city pages with their 2 local holidays."""
    li = "".join(f'<li><a href="{B.BASE}{x["path"]}">{E(x["title_name"])}</a> <span class="m">{B.dmon(x["holidays"][0]["date"])} · '
                 f'{B.dmon(x["holidays"][1]["date"])}</span></li>' for x in cities)
    return f'<ul class="links">{li}</ul>' if li else ""


# ---------------------------------------------------------------- cities: data

def city_name(c, regions):
    same = c["name"] == c["province"] or c["name"] == regions[c["region"]]["name"]
    return f'{c["name"]} capital' if c.get("capital") and same and ES else c["name"]


def source_label(c):
    if c["status"] == "ayuntamiento":
        return f'Pleno del Ayuntamiento de {c["name"]}'
    m = re.search(r"\(([^()]*\b(?:BO[A-Z]*|DO[A-Z]*)\b[^()]*)\)\s*$", c["source"]["title"])
    return m.group(1) if m else "Boletín oficial"


def city_ctx(c, regions):
    r = regions[c["region"]]
    zone = CITY_ZONE.get(c["slug"]) or ("general" if c["region"] == "cataluna" else None)
    name = city_name(c, regions)
    hols = B.page_holidays(DATA, r, {"zone": zone, "holidays": c["holidays"]})
    import muni
    m = muni.catalogue()["by_path"].get(f'{r["slug"]}/{c["slug"]}/')
    ref26 = muni.wide_and_partial(m["ref26"])[0] if m and m.get("ref26") else []  # 2026 locals: next-holiday card only
    return {"c": c, "r": r, "slug": c["slug"], "zone": zone, "ref26": ref26, "title_name": name, "holidays": c["holidays"],
            "path": f'{r["slug"]}/{c["slug"]}/', "hols": hols, "n": len(hols), "boe": len(hols) - 2,
            "pts": B.puentes(hols), "lab": B.workdays(hols), "src_label": source_label(c),
            "pending_bulletin": c["status"] == "ayuntamiento",
            "in": f"en {name}" if ES else f"· {name}",
            "h1": f'{t("h1")} de {name}' if ES else f'{t("h1")}: {name}'}


def published_cities(loc, regions):
    return [city_ctx(c, regions) for c in loc["cities"] if c["status"] in PUBLISHED and c["holidays"]]


# ---------------------------------------------------------------- cities: html

def city_page(x, siblings, mine, pend):
    c, r, name = x["c"], x["r"], x["title_name"]
    h1, h2 = x["holidays"]
    if ES:
        sn = c["name"]  # "Valencia", not "Valencia capital": the dates make it the city
        d1, d2 = B.dmon(h1["date"]), B.dmon(h2["date"])
        title = B.pick(60, f"Calendario laboral {sn} 2027: festivos {d1} y {d2} | Puentes",
                       f"Calendario laboral {sn} 2027: festivos {d1} y {d2}", f"Calendario laboral {sn} 2027: {d1} y {d2}",
                       f"Festivos {sn} 2027: {d1} y {d2}", f"Calendario laboral {sn} 2027")
        nm = lambda h: "" if h["name"].startswith("Fiesta local") else f' ({h["name"]})'  # noqa: E731
        tail = f'Con los {x["boe"]} de {r["name"]}: {x["n"]} festivos, {len(x["pts"])} puentes y {x["lab"]} días laborables.'
        desc = B.pick(155,
                      f'Festivos locales de {sn} en 2027: {B.dlong(h1["date"])}{nm(h1)} y {B.dlong(h2["date"])}{nm(h2)}. {tail}',
                      f'Festivos locales de {sn} en 2027: {B.dlong(h1["date"])} y {B.dlong(h2["date"])}. {tail}',
                      f'Festivos locales de {sn} en 2027: {d1} y {d2}. {tail}',
                      f'Festivos locales de {sn} en 2027: {d1} y {d2}. {x["n"]} festivos, {len(x["pts"])} puentes y {x["lab"]} días laborables.')
    else:
        suffix = t("title_region").split(":", 1)[1].strip()
        title = B.pick(60, f'{t("h1")} · {name}: {suffix}', f'{t("h1")} · {name}', name)
        per_boe = B.I18N["ui"]["per_boe"][B.LANG]
        desc = B.pick(155, f'{name}: {tn("n_hol", x["n"])}, {tn("n_pts", len(x["pts"]))}. {t("locals")}: {B.dm(h1["date"])}, {B.dm(h2["date"])}. {per_boe}',
                      f'{name}: {tn("n_hol", x["n"])}, {tn("n_pts", len(x["pts"]))}. {t("locals")}: {B.dm(h1["date"])}, {B.dm(h2["date"])}.')
    crumbs = [(t("spain"), ""), (r["name"], f'{r["slug"]}/'), (name, x["path"])]
    src = c["source"]
    status = f' · {t("pending")}' if x["pending_bulletin"] and ES else ""
    srcline = (f'<p class="src">{t("locals")}: <a href="{E(src["url"])}" rel="noopener" title="{E(src["title"])}">{E(x["src_label"])}</a>{status}'
               f' · <a href="{DATA["source"]["url"]}" rel="noopener">{t("data_source")}</a></p>')
    qas = []
    if ES:
        how = ("Los aprobó el pleno del ayuntamiento; falta su publicación en el boletín oficial." if x["pending_bulletin"]
               else f'Publicados en el {E(x["src_label"])}.')
        qas = [
            (f"¿Cuáles son los festivos locales de {name} en 2027?",
             f'{B.dlong(h1["date"]).capitalize()}, {E(h1["name"])}, y {B.dlong(h2["date"])}, {E(h2["name"])}. {how} '
             f'<a href="{E(src["url"])}" rel="noopener">Fuente</a>.'),
            (f"¿Cuántos días laborables tiene {name} en 2027?",
             f'{x["lab"]} días de lunes a viernes, una vez descontados los festivos que caen entre semana.'),
            (f'¿El {B.dmon(h1["date"])} es festivo en toda la provincia de {c["province"]}?',
             f'No. Los festivos locales solo valen en el municipio de {E(c["name"])}.'),
        ]
    rnames = B.R(r)
    near = B.section("locales", E(B.fill(t("h_loc"), rnames)),
                     city_list(siblings) + f'<p class="more-l"><a href="{B.BASE}{r["slug"]}/">{E(B.fill(t("h1_region"), rnames))}</a> · '
                     f'<a href="{B.BASE}festivos-locales/">{t("nav_locals")} 2027</a>{school_link(r)}</p>' + prov_links(r["slug"], c["province"]))
    key = f'{r["slug"]}-{c["slug"]}'
    upd_date = guia.lastmod(src["checked"], DATA["updated"], B.CONTENT_UPDATED if ES else None)
    lds = [crumbs_ld(crumbs), webpage_ld(title, x["path"], upd_date) if ES else None, list_ld(B.fill(t("h_hol"), {**rnames, "region": name, "region_in": x["in"]}), x["hols"]),
           dataset_ld(B.fill(t("h_hol"), {**rnames, "region": name, "region_in": x["in"]}), desc,
                      x["path"], c["name"], [DATA["source"]["url"], src["url"]], [("text/calendar", f"ics/{key}.ics"), ("text/csv", f"csv/{key}.csv")]),
           faq_ld(qas)]
    ctx = {**x, "crumbs": B.crumbs_html(crumbs)}
    # Spanish: indexable, no hreflang. ca/gl/eu: the same template translated, kept for users but noindex (seo/AUDIT-2026-11.md)
    # c["new"]: published after the AdSense review request (muni.overlay_locales): no ads until the site is approved
    head = B.head_html(title, desc, x["path"], f"{B.SITE}{B.ASSETS}og/{key}.png", ld(*lds), alts=False, index=ES,
                       ads=not c.get("new"))
    lead = guia.city_lead(x) + guia.upd(upd_date) if ES else ""
    notes = guia.city_notes(x, ALL_CITIES) if ES else ""
    main = B.app_main(DATA, r, ctx, srcline, notes + near + faq_html(qas), mine, pend, lead)
    return B.page(head, "app", "app", main, DATA, B.app_attrs(r, ctx))


def hub_locales(loc, regions, cities):
    by = {x["slug"] + "@" + x["r"]["slug"]: x for x in cities}
    n_pub = len(cities)
    n_pen = sum(1 for c in loc["cities"] if c["status"] not in PUBLISHED or not c["holidays"])
    blocks = []
    for r in DATA["regions"]:
        rows, pend = [], []
        for c in [c for c in loc["cities"] if c["region"] == r["slug"]]:
            x = by.get(c["slug"] + "@" + r["slug"])
            if x:
                h1, h2 = x["holidays"]
                src = c["source"]
                kind = "Fuente" if ES else x["src_label"]
                rows.append(f'<tr><th scope="row"><a href="{B.BASE}{x["path"]}">{E(x["title_name"])}</a></th>'
                            f'<td>{tm(h1["date"], B.dm(h1["date"]))}<br>{tm(h2["date"], B.dm(h2["date"]))}</td>'
                            f'<td><a href="{E(src["url"])}" rel="noopener" title="{E(src["title"])}">{E(kind)}</a></td></tr>')
            else:
                pend.append(c["name"])
        pend_html = f'<p class="m pend">Pendientes de publicar: {E(", ".join(pend))}.</p>' if pend and ES else ""
        if not rows and pend_html:
            blocks.append(f'<section class="sec" id="{r["slug"]}" aria-labelledby="h-{r["slug"]}"><div class="sec-h"><h2 id="h-{r["slug"]}">'
                          f'<a href="{B.BASE}{r["slug"]}/">{E(r["name"])}</a></h2></div>{pend_html}</section>')
        if rows:
            blocks.append(f'<section class="sec" id="{r["slug"]}" aria-labelledby="h-{r["slug"]}"><div class="sec-h"><h2 id="h-{r["slug"]}">'
                          f'<a href="{B.BASE}{r["slug"]}/">{E(r["name"])}</a></h2></div><table class="tbl hub">'
                          f'<thead><tr><th scope="col">{t("col_city")}</th><th scope="col">{t("nav_locals")}</th><th scope="col">{t("col_src")}</th></tr></thead>'
                          f'<tbody>{"".join(rows)}</tbody></table>{pend_html}</section>')
    qas = []
    if ES:
        qas = [("¿Quién fija los festivos locales?",
                "Cada ayuntamiento propone 2 días al año y la autoridad laboral de la comunidad los publica en el boletín oficial."),
               ("¿Por qué no sale mi ciudad?",
                "Porque aún no hay publicación oficial. Solo damos fechas de un boletín o de un acuerdo del pleno publicado por el ayuntamiento.")]
        import muni
        cat = muni.catalogue()
        m_ok, m_all = sum(1 for x in cat["munis"] if x["ok"]), len(cat["munis"])
        title = "Festivos locales 2027 por ciudad y provincia (oficiales)"
        desc = (f"Los 2 festivos locales de 2027 de {m_ok} municipios, con su fuente oficial, por ciudad y por provincia. "
                f"Los demás, en cuanto se publiquen.") if m_ok else (
                f"Los 2 festivos locales de 2027 de {n_pub} ciudades, con su fuente oficial: boletín o acuerdo del pleno. "
                f"Las demás, en cuanto se publiquen.")
        ctx = (f'<p class="ctx">{m_ok} de {m_all} municipios publicados' if m_ok else f'<p class="ctx">{n_pub} ciudades publicadas · {n_pen} pendientes') +             f' · <time datetime="{loc["updated"]}">actualizado {B.dmy(loc["updated"])}</time></p>'
    else:
        title = f'{t("nav_locals")} 2027 · El Calendario Laboral'
        names = ", ".join(x["title_name"] for x in cities)
        desc = B.pick(155, f'{t("nav_locals")} 2027: {names}', f'{t("nav_locals")} 2027: {names[:120].rsplit(", ", 1)[0]}…')
        ctx = f'<p class="ctx">{t("col_city")}: {n_pub}</p>' if B.LANG != "eu" else ""
    h1 = f'{t("nav_locals")} 2027'
    crumbs = [(t("spain"), ""), (h1, "festivos-locales/")]
    lead = ""
    if ES:
        import muni
        cat = muni.catalogue()
        m_ok, m_all = sum(1 for x in cat["munis"] if x["ok"]), len(cat["munis"])
        a_ok, a_pen = (m_ok, m_all - m_ok) if m_all else (n_pub, n_pen)
        lead = guia.lead(f'{a_ok} municipios ya tienen sus <b>2 festivos locales de 2027</b> publicados oficialmente; '
                         f'{a_pen} siguen pendientes y no les ponemos fecha hasta que salga en el boletín o en el acuerdo del pleno.')
        provs = [p for p in cat["provs"] if p["path"] and p["munis"]]
        if provs:  # every province page: the way to the other 8,000 municipalities
            li = "".join(f'<li><a href="{B.BASE}{p["path"]}">{E(p["label"])}</a> <span class="m">{sum(1 for x in p["munis"] if x["ok"])}'
                         f' de {len(p["munis"])}</span></li>' for p in sorted(provs, key=lambda p: muni.fold(p["name"])))
            blocks.insert(0, B.section("provincias", "Por provincia: todos los municipios", f'<ul class="links">{li}</ul>'))
    main = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{lead}{ctx}</div>'
            f'<div class="wrap body narrow">{guia.hub_notes(cities) if ES else ""}{"".join(blocks)}{faq_html(qas)}</div>')  # no ad(): this page has ads=False
    head = B.head_html(title, desc, "festivos-locales/", f"{B.SITE}{B.ASSETS}og/espana.png", ld(crumbs_ld(crumbs), faq_ld(qas)), ads=False)
    return B.page(head, "pg", "locals", main, DATA, js=False)


# ---------------------------------------------------------------- home and regions

def region_facts(r):
    hols = B.region_holidays(DATA, r["slug"])
    return {"hols": hols, "n": len(hols), "nat": [h for h in hols if h["kind"] == "n"], "own": [h for h in hols if h["kind"] == "r"],
            "pts": B.puentes(hols), "can": r["slug"] == "canarias"}


def region_titles(r, f):
    names = B.R(r)
    if ES:
        nm, n, p = r["name"], f["n"] + (1 if f["can"] else 0), len(f["pts"])
        lab = B.workdays(f["hols"], 1 if f["can"] else 0)
        title = B.pick(60, f"Calendario laboral {nm} 2027: {n} festivos y {p} puentes",
                       f"Calendario laboral {nm} 2027: {n} festivos y puentes", f"Calendario laboral {nm} 2027: {n} festivos",
                       t("title_region", region=nm), t("title_region2", region=nm))
        own = ", ".join(f'{h["name"]} ({B.dmon(h["date"])})' for h in f["own"])
        isl = " y la fiesta de cada isla" if f["can"] else ""
        desc = B.pick(155,
                      f'{nm} tiene {f["n"]} festivos en 2027{isl}: {len(f["nat"])} nacionales y {len(f["own"])} propios, '
                      f'{own}. {p} puentes y {lab} días laborables.',
                      f'{nm} tiene {f["n"]} festivos en 2027{isl}: {len(f["nat"])} nacionales y {len(f["own"])} propios, '
                      f'{", ".join(B.dmon(h["date"]) for h in f["own"])}. {p} puentes y {lab} días laborables.',
                      f'Festivos 2027 en {nm}: {f["n"]}{isl}, {p} puentes y {lab} días laborables, más los 2 locales de tu municipio.')
        return title, desc
    cands = []
    if names["seo"]:
        seo = {k: (f'{v} ({names["seo"]})' if k in ("region", "region_in") else v) for k, v in names.items()}
        cands += [B.fill(t("title_region"), seo), B.fill(t("title_region2"), seo)]
    cands += [B.fill(t("title_region"), names), B.fill(t("title_region2"), names)]
    title = B.pick(60, *cands)
    desc = first_sentences(B.fill(t("desc_region"), names, n=f["n"] + (1 if f["can"] else 0), p=len(f["pts"])), 155)
    return title, desc


def region_page(r, cities, pending):
    f = region_facts(r)
    slug, name = r["slug"], r["name"]
    title, desc = region_titles(r, f)
    qas = []
    if ES:
        n_txt = f'{f["n"]}' + (" (más la fiesta de tu isla)" if f["can"] else "")
        own = ", ".join(f'{E(h["name"])} ({B.dmon(h["date"])})' for h in f["own"])
        var = f' ({VARIANT[slug]})' if slug in VARIANT else ""
        dates = {h["date"] for h in f["hols"]}
        if "2027-03-29" in dates:
            q2 = (f"¿Es festivo el Lunes de Pascua en {name}?", "Sí, el lunes 29 de marzo de 2027.")
        else:
            q2 = (f"¿Es festivo el Jueves Santo en {name}?",
                  "Sí, el jueves 25 de marzo de 2027." if "2027-03-25" in dates else "No. El 25 de marzo de 2027 es laborable; el Viernes Santo (26 de marzo) sí es festivo.")
        if "2027-08-16" in dates:
            a3 = f"Cae en domingo y {name} lo pasa al lunes 16 de agosto."
        elif "2027-10-11" in dates:
            a3 = f"Cae en domingo y {name} lo pasa al lunes 11 de octubre."
        else:
            a3 = f"Cae en domingo y {name} no lo traslada, así que no hay festivo extra."
        qas = [(f"¿Cuántos festivos tiene {name} en 2027?",
                f'{n_txt} según el BOE: {len(f["nat"])} comunes a toda España y {len(f["own"])} propios de {E(name)}{E(var)}: {own}. '
                f'Además, cada municipio tiene 2 festivos locales.'),
               q2, (f"¿Qué pasa con el 15 de agosto de 2027 en {name}?", a3),
               (f"¿Dónde veo los festivos de mi municipio en {name}?",
                f'Cada ayuntamiento fija 2. Aquí están los de las ciudades ya publicadas: <a href="{B.BASE}festivos-locales/#{slug}">festivos locales 2027</a>.')]
    names = B.R(r)
    pend = f'<p class="m">Pendientes de publicar: {E(", ".join(pending))}.</p>' if pending and ES else ""
    dirx = muni_directory(r)
    more_l = f'<p class="more-l"><a href="{B.BASE}festivos-locales/">{t("nav_locals")} 2027</a>{school_link(r)}{workdays_link(r)}</p>'
    if dirx:  # every municipality reachable from here: no separate city list / pending line / province line
        locs = B.section("locales", E(B.fill(t("h_loc"), names)), dirx + more_l)
    else:
        locs = B.section("locales", E(B.fill(t("h_loc"), names)), city_list(cities) + pend + more_l + prov_links(slug))
    crumbs = [(t("spain"), ""), (name, f"{slug}/")]
    hname = B.fill(t("h_hol"), names)
    upd_date = guia.lastmod(DATA["updated"], B.CONTENT_UPDATED if ES else None)
    lds = [crumbs_ld(crumbs), webpage_ld(title, f"{slug}/", upd_date), list_ld(hname, f["hols"]),
           dataset_ld(hname, desc, f"{slug}/", r["official"], DATA["source"]["url"],
                      [("text/calendar", f"ics/{slug}.ics"), ("text/csv", f"csv/{slug}.csv")]),
           faq_ld(qas)]
    head = B.head_html(title, desc, f"{slug}/", f"{B.SITE}{B.ASSETS}og/{slug}.png", ld(*lds))
    lead = (guia.region_lead(r) if ES else "") + quick_access(r) + guia.upd(upd_date)
    notes = guia.region_notes(r, ALL_CITIES) if ES else ""
    main = (B.app_main(DATA, r, None, "", notes + faq_html(qas), cities, pending, lead, top=locs) if dirx
            else B.app_main(DATA, r, None, "", notes + locs + faq_html(qas), cities, pending, lead))
    return B.page(head, "app", "app", main, DATA, B.app_attrs(r))


def home_page():
    regs = {r["slug"]: region_facts(r) for r in DATA["regions"]}
    nat = regs["madrid"]["nat"]
    qas = []
    if ES:
        counts = sorted({(f["n"]) for s, f in regs.items() if s != "canarias"})
        weekend = [h for h in nat if D(h["date"]).weekday() >= 5]
        labs = [B.workdays(f["hols"], 1 if f["can"] else 0) for f in regs.values()]
        moved16 = [DATA["regions"][k]["name"] for k, (s, f) in enumerate(regs.items()) if any(h["date"] == "2027-08-16" for h in f["hols"])]
        moved11 = [DATA["regions"][k]["name"] for k, (s, f) in enumerate(regs.items()) if any(h["date"] == "2027-10-11" for h in f["hols"])]
        src = DATA["source"]
        qas = [("¿Cuántos festivos hay en 2027?",
                f'{len(nat)} comunes a toda España y {"/".join(map(str, counts))} en cada comunidad (en Canarias, {regs["canarias"]["n"]} más la fiesta de cada isla). '
                f'Además, cada municipio tiene 2 festivos locales.'),
               ("¿Cuándo se publicó el calendario laboral 2027?",
                f'En el BOE del 13 de octubre de 2026: <a href="{src["url"]}" rel="noopener">{src["id"]}</a>.'),
               ("¿Qué festivos caen en fin de semana en 2027?",
                " y ".join(f'{E(h["name"])} ({B.dlong(h["date"])})' for h in weekend) + ". "
                f'El 15 de agosto es domingo: lo pasan al lunes 16 {", ".join(moved16)}' + (f'; {", ".join(moved11)} al 11 de octubre.' if moved11 else ".")),
               ("¿Cuántos días laborables tiene 2027?",
                f"261 de lunes a viernes. Restando los festivos quedan entre {min(labs)} y {max(labs)}, según la comunidad, sin contar los 2 locales."),
               ("¿Cuándo es Semana Santa 2027?", "Del domingo 21 al domingo 28 de marzo. Jueves Santo es el 25 y Viernes Santo el 26.")]
    if ES:
        nlabs = sorted(B.workdays(f["hols"], 1 if f["can"] else 0) for f in regs.values())
        title = "Calendario laboral 2027: festivos y puentes de España"
        desc = B.pick(155, f'Calendario laboral 2027 según el BOE: {len(nat)} festivos nacionales, los de cada comunidad y los '
                           f'2 locales de tu municipio. Puentes y de {nlabs[0]} a {nlabs[-1]} días laborables.',
                      t("desc_home"))
    else:
        title, desc = B.pick(60, t("title_home"), t("h1")), first_sentences(t("desc_home"), 155)
    sp = {"region": t("spain"), "region_in": t("in_spain"), "region_of": t("spain")}
    chips = "".join(f'<li><a href="{B.BASE}{r["slug"]}/">{E(r["name"])}</a></li>' for r in DATA["regions"])
    n_regions = B.I18N["ui"]["n_regions"][B.LANG] if B.I18N else "19 comunidades"
    upd_date = guia.lastmod(DATA["updated"], B.CONTENT_UPDATED if ES else None)
    upd = guia.upd(upd_date, src=False)
    labs = sorted(B.workdays(f["hols"], 1 if f["can"] else 0) for f in regs.values())
    lab_rng = tn("n_lab", labs[-1]).replace(str(labs[-1]), f"{labs[0]}–{labs[-1]}", 1)
    stats = B.stats_html([(None, tn("n_nat", len(nat))), (None, lab_rng), (None, tn("n_pts", len(B.puentes(nat))))])
    hero = ('<div class="hero wrap">'
            + B.hero_grid(f'<h1>{E(t("h1"))}</h1>{guia.home_lead() if ES else ""}{B.search_box("q-home", big=True)}'
                          f'<div class="pickers">{B.region_select(None)}{B.home_city_select()}</div>',
                          B.next_card(nat, prev=B.prev26()) + stats,
                          f'<p class="ctx">{E(n_regions)} · <a href="{DATA["source"]["url"]}" rel="noopener">{t("data_source")}</a></p>{upd}')
            + '</div>')
    cal_sec = B.section("calendario", t("h_cal"), B.legend_html(["n"]) + B.year_html(nat), B.tools_html(), "cal")
    school = (f'<p class="more-l"><a href="{B.BASE}calendario-escolar/">Calendario escolar 2026-2027</a> · '
              f'<a href="{B.BASE}vacaciones-escolares/navidad/">Vacaciones de Navidad 2026-2027</a> · '
              f'<a href="{B.BASE}vacaciones-escolares/semana-santa/">Vacaciones de Semana Santa 2027</a></p>') if ES else ""
    import utilidades
    reg_sec = B.section("comunidades", t("pick_region"), f'<ul class="chips">{chips}</ul>{school}{utilidades.home_links()}')
    hol_sec = B.section("festivos", E(B.fill(t("h_hol"), sp)), f'<ol class="hl">{"".join(B.hol_item(h) for h in nat)}</ol>')
    prow = "".join(B.pts_row(it) for it in B.all_breaks(nat))
    vac = f'<p class="more-l"><a href="{B.BASE}vacaciones-2027/">Maximiza tus vacaciones 2027 →</a></p>' if ES else ""
    pts_sec = B.section("puentes", E(B.fill(t("h_pts"), sp)), f'<table class="tbl pts">{B.pts_head()}<tbody>{prow}</tbody></table>{vac}')
    notes = guia.home_notes() if ES else ""
    main = f'{hero}<div class="wrap body">{cal_sec}{B.ad("cal")}{reg_sec}{hol_sec}{pts_sec}{notes}{faq_html(qas)}</div>{B.POP}'
    org = f"{B.SITE}{B.ASSETS}#org"
    # No SearchAction: Google retired the sitelinks search box (Nov 2024) and /buscar/ is a noindex fallback.
    lds = [{"@type": "WebSite", "@id": f"{B.SITE}{B.ASSETS}#web", "name": t("site_name"), "alternateName": B.HOST, "url": B.URL,
            "inLanguage": B.IN_LANG[B.LANG], "publisher": {"@id": org}},
           {"@type": "Organization", "@id": org, "name": t("site_name"), "url": f"{B.SITE}{B.ASSETS}",
            "logo": f"{B.SITE}{B.ASSETS}icons/icon-512.png", "email": B.EMAIL, "publishingPrinciples": f"{B.SITE}{B.ASSETS}sobre/"},
           webpage_ld(title, "", upd_date), faq_ld(qas)]
    head = B.head_html(title, desc, "", f"{B.SITE}{B.ASSETS}og/espana.png", ld(*lds))
    return B.page(head, "home", "", main, DATA)


# ---------------------------------------------------------------- entry points

DATA = None
ALL_CITIES = []


def write_pages(data, fix):
    """Write every page of this language. Returns [(path, lastmod)] for the sitemap (privacy is left out)."""
    global DATA, _fix, ALL_CITIES
    DATA, _fix = data, fix
    guia.init(sys.modules[__name__])
    _written.clear()
    regions = {r["slug"]: r for r in data["regions"]}
    loc = load_locales()
    import muni
    by_path = muni.catalogue()["by_path"]
    pop = lambda c: (by_path.get(f'{c["region"]}/{c["slug"]}/') or {"m": {}})["m"].get("pop") or 0  # noqa: E731
    loc = {**loc, "cities": sorted(loc["cities"], key=lambda c: -pop(c))}  # published and pending lists: biggest first
    cities = published_cities(loc, regions)
    ALL_CITIES = cities
    upd = guia.lastmod(data["updated"], B.CONTENT_UPDATED)
    write("", home_page(), upd)
    for r in data["regions"]:
        mine = [x for x in cities if x["r"]["slug"] == r["slug"]]
        pend = [c["name"] for c in loc["cities"] if c["region"] == r["slug"] and (c["status"] not in PUBLISHED or not c["holidays"])]
        write(f'{r["slug"]}/', region_page(r, mine, pend), upd)
    for x in cities:
        sib = [s for s in cities if s["r"]["slug"] == x["r"]["slug"] and s is not x][:10]
        mine = [s for s in cities if s["r"]["slug"] == x["r"]["slug"]]
        pend = [c["name"] for c in loc["cities"] if c["region"] == x["r"]["slug"] and (c["status"] not in PUBLISHED or not c["holidays"])]
        write(x["path"], city_page(x, sib, mine, pend), guia.lastmod(x["c"]["source"]["checked"], upd), ["es"])
    write("festivos-locales/", hub_locales(loc, regions, cities), loc["updated"])
    import utilidades
    utilidades.write_pages(data, write, cities)
    if ES:
        guia.write_pages(write, cities, loc)
        import escolar
        escolar.write_pages(data, write)
        import festivos  # after escolar: it reads the school breaks
        festivos.write_pages(write, cities, sys.modules[__name__])
        import widget
        widget.write_pages(data, write, cities)
        import vacaciones
        vacaciones.write_pages(data, write, cities)
        import pdfhub
        pdfhub.write_page(data, write, cities)
        import buscar
        import muni
        buscar.page(data, muni.index_rows()[1], write, upd)
        if muni.MUNI_ON:
            import munipages
            munipages.write_pages(sys.modules[__name__], write)
    return list(_written)


def csv_text(rows):
    """Spanish Excel: UTF-8 with BOM, ';' separator, CRLF."""
    out = ["Fecha;Día;Festivo;Ámbito"]
    for iso, name, scope in rows:
        d = D(iso)
        cells = [d.strftime("%d/%m/%Y"), B.T["_wd"][d.weekday()], name, scope]
        out.append(";".join('"' + c.replace('"', '""') + '"' if any(x in c for x in ';"\n') else c for c in cells))
    return "﻿" + "\r\n".join(out) + "\r\n"


def region_csv_rows(r):
    rows = [(h["date"], h["name"], "Nacional" if h["kind"] == "n" else r["official"]) for h in B.region_holidays(DATA, r["slug"])]
    z = DATA["zones"].get(r["slug"])
    for o in (z or {}).get("options", []):
        if "add" in o:
            rows.append((o["add"]["date"], o["add"]["name"], f'Solo {o["name"]}'))
        if "remove" in o:
            rows = [(d, n, s + f' (salvo {o["name"]})' if d == o["remove"] else s) for d, n, s in rows]
    return sorted(rows)


def write_shared(data, img=True):
    """Files shared by every language (Spanish build only): .csv for regions and cities, .ics and og images for cities."""
    regions = {r["slug"]: r for r in data["regions"]}
    cities = published_cities(load_locales(), regions)
    (B.ROOT / "csv").mkdir(exist_ok=True)
    for r in data["regions"]:
        (B.ROOT / "csv" / f'{r["slug"]}.csv').write_bytes(csv_text(region_csv_rows(r)).encode("utf-8"))
    for x in cities:
        key = f'{x["r"]["slug"]}-{x["slug"]}'
        rows = [(h["date"], h["name"], "Nacional" if h["kind"] == "n" else ("Local" if h["kind"] == "l" else x["r"]["official"])) for h in x["hols"]]
        (B.ROOT / "csv" / f"{key}.csv").write_bytes(csv_text(rows).encode("utf-8"))
        (B.ROOT / "ics" / f"{key}.ics").write_bytes(B.ics_text(x["hols"], x["title_name"], key).encode("utf-8"))
        if img:
            B.og_image(B.ROOT / "og" / f"{key}.png", x["title_name"], f'{t("og_sub", n=x["n"], p=len(x["pts"]))} · {x["lab"]} laborables',
                       x["hols"], [(h["date"], "l") for h in x["holidays"]], "Festivos locales")
    if img and ES:
        import escolar
        escolar.og_images()
        import vacaciones
        vacaciones.og_images(data)
