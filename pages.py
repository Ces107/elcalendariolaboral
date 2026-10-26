"""Pages built from data, called by build.py: home, the 19 regions, city pages and the /festivos-locales/ hub.

Each page type has a data function (what the page says, plain dicts) and an HTML function (how it looks), so a
redesign can restyle the HTML without touching the data logic. Shared components (head, header, app body, footer)
stay in build.py.

    Data used
    data/2027.json          home, regions, cities (BOE holidays, islands, Arán)
    data/locales-2027.json  cities: only status "boletin" or "ayuntamiento" get a page; "unpublished" only appear in the hub
"""
import datetime as dt
import html
import json
import re

import build as B
from build import E, t

SCHEMA = "https://schema.org"
PUBLISHED = ("boletin", "ayuntamiento")
# Canary cities: the island whose insular holiday applies (geography, not data that changes)
CITY_ZONE = {"las-palmas-de-gran-canaria": "gran-canaria", "telde": "gran-canaria",
             "santa-cruz-de-tenerife": "tenerife", "san-cristobal-de-la-laguna": "tenerife"}
# name variants people search for, placed once in the FAQ (plan §3.2)
VARIANT = {"cataluna": "Catalunya", "pais-vasco": "Euskadi", "comunitat-valenciana": "Comunitat Valenciana, GVA",
           "baleares": "Illes Balears"}

_written = []
_fix = None


# ---------------------------------------------------------------- small helpers

def load_locales():
    return json.loads((B.ROOT / "data" / "locales-2027.json").read_text("utf-8"))


def D(iso):
    return dt.date.fromisoformat(iso)


def dm(iso):
    d = D(iso)
    return f'{d.day} {t("mon3")[d.month - 1]}'


def dlong(iso):
    d = D(iso)
    return f'{t("wd")[d.weekday()]} {d.day} de {t("months")[d.month - 1]}'


def tm(iso, txt):
    return f'<time datetime="{iso}">{txt}</time>'


def strip(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s))


def ld(*objs):
    return "".join(f'<script type="application/ld+json">{json.dumps({"@context": SCHEMA, **o}, ensure_ascii=False)}</script>'
                   for o in objs if o)


def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "name": n, "item": B.URL + p} for k, (n, p) in enumerate(items)]}


def faq_ld(qas):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in qas]}


def list_ld(name, hols):
    return {"@type": "ItemList", "name": name, "numberOfItems": len(hols), "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "name": f'{h["name"]} · {dlong(h["date"])} de 2027'} for k, h in enumerate(hols)]}


def dataset_ld(name, desc, path, place, based_on, downloads):
    return {"@type": "Dataset", "name": name, "description": desc, "url": B.URL + path, "inLanguage": "es-ES",
            "dateModified": DATA["updated"], "temporalCoverage": "2027-01-01/2027-12-31",
            "spatialCoverage": {"@type": "Place", "name": f"{place}, España"}, "isBasedOn": based_on,
            "creator": {"@type": "Organization", "name": t("site_name")},
            "distribution": [{"@type": "DataDownload", "encodingFormat": f, "contentUrl": f"{B.SITE}{B.ASSETS}{u}"} for f, u in downloads]}


def faq_html(qas):
    items = "".join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>' for q, a in qas)
    return f'<section class="faq" aria-labelledby="h-faq"><h2 id="h-faq">Preguntas frecuentes</h2>{items}</section>'


def write(path, page, lastmod):
    d = B.OUT / path
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(_fix(page), "utf-8", newline="\n")
    _written.append((path, lastmod))


def shell(title, desc, path, crumbs, body, lds=(), og="espana", current=None):
    """A static page (hubs): same header and footer as the app, content in .pg."""
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}og/{og}.png", ld(crumbs_ld(crumbs), *lds))
    return head + f"""<body class="pg">
{B.top_html(app=False)}
<main class="wrap pg-in">
{B.crumbs_html(crumbs)}
{body}
</main>
{B.footer_html(DATA, current)}
{B.THEME_JS}
</body>
</html>
"""


# ---------------------------------------------------------------- cities: data

def city_name(c, regions):
    """'Madrid capital' when a capital shares its name with its province or comunidad (plan §3.3)."""
    same = c["name"] == c["province"] or c["name"] == regions[c["region"]]["name"]
    return f'{c["name"]} capital' if c.get("capital") and same else c["name"]


def source_label(c):
    """Short visible label for the local-holiday source; the full title goes in the link title."""
    if c["status"] == "ayuntamiento":
        return f'Pleno del Ayuntamiento de {c["name"]}'
    m = re.search(r"\(([^()]*\b(?:BO[A-Z]*|DO[A-Z]*)\b[^()]*)\)\s*$", c["source"]["title"])
    return m.group(1) if m else "Boletín oficial"


def city_ctx(c, regions):
    """Everything a city page needs, as data."""
    r = regions[c["region"]]
    zone = CITY_ZONE.get(c["slug"]) or ("general" if c["region"] == "cataluna" else None)
    name = city_name(c, regions)
    hols = B.page_holidays(DATA, r, {"zone": zone, "holidays": c["holidays"]})
    return {"c": c, "r": r, "slug": c["slug"], "zone": zone, "title_name": name, "holidays": c["holidays"],
            "path": f'{r["slug"]}/{c["slug"]}/', "hols": hols, "n": len(hols), "boe": len(hols) - 2,
            "pts": B.puentes(hols), "lab": B.workdays(hols), "src_label": source_label(c),
            "pending_bulletin": c["status"] == "ayuntamiento"}


def published_cities(loc, regions):
    return [city_ctx(c, regions) for c in loc["cities"] if c["status"] in PUBLISHED and c["holidays"]]


# ---------------------------------------------------------------- cities: html

def city_page(x, siblings):
    c, r, name = x["c"], x["r"], x["title_name"]
    h1, h2 = x["holidays"]
    title = B.pick(60, f"Calendario laboral 2027 {name}: festivos y puentes", f"Calendario laboral 2027 {name}: festivos locales",
                   f"Festivos 2027 {name}: calendario laboral", f"Calendario laboral 2027 {name}")
    desc = B.pick(155,
                  f'Festivos 2027 en {name}: los {x["boe"]} de {r["name"]} y los 2 locales ({dlong(h1["date"])} y {dlong(h2["date"])}), con puentes, días laborables y descarga a tu calendario.',
                  f'Festivos 2027 en {name}: los {x["boe"]} de {r["name"]} y los 2 locales ({dm(h1["date"])} y {dm(h2["date"])}), con puentes, días laborables y descarga a tu calendario.',
                  f'Festivos 2027 en {name}: los {x["boe"]} de {r["name"]} y los 2 locales ({dm(h1["date"])} y {dm(h2["date"])}), con puentes y descarga a tu calendario.',
                  f'Festivos 2027 en {name}: {x["boe"]} del BOE y 2 locales ({dm(h1["date"])} y {dm(h2["date"])}).')
    crumbs = [(t("crumb_home"), ""), (r["name"], f'{r["slug"]}/'), (name, x["path"])]
    src = c["source"]
    status = '<span class="sep" aria-hidden="true"> · </span>aprobado por el pleno, pendiente del boletín' if x["pending_bulletin"] else ""
    src_html = B.src_html(DATA, extra="").replace(
        '<p class="src">',
        f'<p class="src">Locales: <a href="{E(src["url"])}" rel="noopener" title="{E(src["title"])}">{E(x["src_label"])}</a>{status}'
        f'<span class="sep" aria-hidden="true"> · </span>Festivos: ', 1)
    ans = (f'Festivos locales de {E(c["name"])} en 2027: {tm(h1["date"], dlong(h1["date"]))} ({E(h1["name"])}) y '
           f'{tm(h2["date"], dlong(h2["date"]))} ({E(h2["name"])}). En total, {x["n"]} festivos.')
    how = ("Los aprobó el pleno del ayuntamiento; falta su publicación en el boletín oficial." if x["pending_bulletin"]
           else f'Publicados en el {E(x["src_label"])}.')
    qas = [
        (f"¿Cuáles son los festivos locales de {name} en 2027?",
         f'{dlong(h1["date"]).capitalize()}, {E(h1["name"])}, y {dlong(h2["date"])}, {E(h2["name"])}. {how} '
         f'<a href="{E(src["url"])}" rel="noopener">Fuente</a>.'),
        (f"¿Cuántos días laborables tiene {name} en 2027?",
         f'{x["lab"]} días de lunes a viernes, una vez descontados los festivos que caen entre semana.'),
        (f'¿El {dm(h1["date"])} es festivo en toda la provincia de {c["province"]}?',
         f'No. Los festivos locales solo valen en el municipio de {E(c["name"])}.'),
    ]
    sib = "".join(f'<li><a href="{B.BASE}{s["path"]}">{E(s["title_name"])}</a><span>{dm(s["holidays"][0]["date"])} · {dm(s["holidays"][1]["date"])}</span></li>'
                  for s in siblings)
    more = (f'<section class="more wrap" id="more"><div class="more-in">'
            f'<section aria-labelledby="h-near"><h2 id="h-near">Otras ciudades de {E(r["name"])}</h2><ul class="links">{sib}'
            f'<li><a href="{B.BASE}{r["slug"]}/">Calendario laboral 2027 {E(r["name"])}</a></li>'
            f'<li><a href="{B.BASE}festivos-locales/">Festivos locales de todas las ciudades</a></li></ul></section>'
            f'{faq_html(qas)}</div></section>')
    key = f'{r["slug"]}-{c["slug"]}'
    lds = [crumbs_ld(crumbs), list_ld(f"Festivos 2027 en {name}", x["hols"]),
           dataset_ld(f"Festivos laborales 2027 en {name}", f'Los {x["n"]} festivos laborales de 2027 en {c["name"]}: {x["boe"]} del BOE y 2 locales.',
                      x["path"], c["name"], [DATA["source"]["url"], src["url"]], [("text/calendar", f"ics/{key}.ics"), ("text/csv", f"csv/{key}.csv")]),
           faq_ld(qas)]
    ctx = {**x, "crumbs": B.crumbs_html(crumbs), "ans": ans, "src": src_html}
    return B.head_html(title, desc, x["path"], f"{B.SITE}{B.ASSETS}og/{key}.png", ld(*lds)) + B.app_body(DATA, r, ctx, more)


def hub_locales(loc, regions, cities):
    by = {x["slug"] + "@" + x["r"]["slug"]: x for x in cities}
    n_pub = len(cities)
    n_pen = sum(1 for c in loc["cities"] if c["status"] not in PUBLISHED or not c["holidays"])
    blocks = []
    for r in DATA["regions"]:
        rows = []
        for c in [c for c in loc["cities"] if c["region"] == r["slug"]]:
            x = by.get(c["slug"] + "@" + r["slug"])
            if x:
                h1, h2 = x["holidays"]
                src = c["source"]
                kind = "Pleno" if x["pending_bulletin"] else "Boletín"
                rows.append(f'<tr><th scope="row"><a href="{B.BASE}{x["path"]}">{E(x["title_name"])}</a></th>'
                            f'<td>{tm(h1["date"], dm(h1["date"]))} · {tm(h2["date"], dm(h2["date"]))}</td>'
                            f'<td><a href="{E(src["url"])}" rel="noopener" title="{E(src["title"])}">{kind}</a></td></tr>')
            else:
                rows.append(f'<tr class="pend"><th scope="row">{E(c["name"])}</th><td>pendiente de publicar</td><td></td></tr>')
        if rows:
            blocks.append(f'<section class="sec" id="{r["slug"]}" aria-labelledby="h-{r["slug"]}"><h2 id="h-{r["slug"]}">'
                          f'<a href="{B.BASE}{r["slug"]}/">{E(r["name"])}</a></h2><table class="tbl">'
                          f'<thead><tr><th scope="col">Ciudad</th><th scope="col">Festivos locales</th><th scope="col">Fuente</th></tr></thead>'
                          f'<tbody>{"".join(rows)}</tbody></table></section>')
    qas = [("¿Quién fija los festivos locales?",
            "Cada ayuntamiento propone 2 días al año y la autoridad laboral de la comunidad los publica en el boletín oficial."),
           ("¿Por qué no sale mi ciudad?",
            "Porque aún no hay publicación oficial. Solo damos fechas de un boletín o de un acuerdo del pleno publicado por el ayuntamiento.")]
    title = "Festivos locales 2027 por ciudad: fechas oficiales"
    desc = (f"Los 2 festivos locales de 2027 de {n_pub} ciudades, con su fuente oficial: boletín o acuerdo del pleno. "
            f"Las demás, en cuanto se publiquen.")
    body = (f'<h1>Festivos locales 2027</h1><p class="ans">{n_pub} ciudades con sus 2 festivos locales de 2027 aprobados; {n_pen} pendientes de publicar.</p>'
            f'<p class="src">Fuentes: boletines oficiales y plenos municipales<span class="sep" aria-hidden="true"> · </span>'
            f'<time datetime="{loc["updated"]}">{t("updated", d=B.dmy(loc["updated"]))}</time></p>'
            + "".join(blocks) + faq_html(qas))
    crumbs = [(t("crumb_home"), ""), ("Festivos locales 2027", "festivos-locales/")]
    return shell(title, desc, "festivos-locales/", crumbs, body, [faq_ld(qas)], current="festivos-locales/")


# ---------------------------------------------------------------- home and regions

def region_facts(r):
    hols = B.region_holidays(DATA, r["slug"])
    return {"hols": hols, "n": len(hols), "nat": [h for h in hols if h["kind"] == "n"], "own": [h for h in hols if h["kind"] == "r"],
            "pts": B.puentes(hols), "can": r["slug"] == "canarias"}


def region_page(r, cities, pending):
    f = region_facts(r)
    slug, name = r["slug"], r["name"]
    title = B.pick(60, t("title_region", name=name), t("title_region2", name=name))
    n_txt = f'{f["n"]}' + (" (más la fiesta de tu isla)" if f["can"] else "")
    desc = B.pick(155, t("desc_region", name=name, n=f["n"], p=len(f["pts"])),
                  f'Festivos 2027 en {name}: los {f["n"]} del BOE con su día, {len(f["pts"])} puentes y planificador. Añade tus 2 locales.')
    own = ", ".join(f'{E(h["name"])} ({dm(h["date"])})' for h in f["own"])
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
    rows = "".join(f'<li><a href="{B.BASE}{x["path"]}">{E(x["title_name"])}</a><span>{dm(x["holidays"][0]["date"])} · {dm(x["holidays"][1]["date"])}</span></li>'
                   for x in cities)
    pend = (f'<p class="mut">Pendientes de publicar: {E(", ".join(pending))}.</p>' if pending else "")
    more = (f'<section class="more wrap" id="more"><div class="more-in">'
            f'<section aria-labelledby="h-loc"><h2 id="h-loc">Festivos locales 2027 en {E(name)}</h2>'
            f'{"<ul class=links>" + rows + "</ul>" if rows else ""}{pend}'
            f'<ul class="links"><li><a href="{B.BASE}festivos-locales/">Festivos locales de todas las ciudades</a></li></ul></section>'
            f'{faq_html(qas)}</div></section>')
    crumbs = [(t("crumb_home"), ""), (name, f"{slug}/")]
    lds = [crumbs_ld(crumbs), list_ld(t("ld_list", place=r["official"]), f["hols"]),
           dataset_ld(f'Festivos laborales 2027 en {r["official"]}', f'Los {f["n"]} festivos laborales de 2027 en {r["official"]} según el {DATA["source"]["id"]}, con día de la semana.',
                      f"{slug}/", r["official"], DATA["source"]["url"], [("text/calendar", f"ics/{slug}.ics"), ("text/csv", f"csv/{slug}.csv")]),
           faq_ld(qas)]
    return B.head_html(title, desc, f"{slug}/", f"{B.SITE}{B.ASSETS}og/{slug}.png", ld(*lds)) + B.app_body(DATA, r, None, more)


def home_page():
    regs = {r["slug"]: region_facts(r) for r in DATA["regions"]}
    nat = regs["madrid"]["nat"]
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
            " y ".join(f'{E(h["name"])} ({dlong(h["date"])})' for h in weekend) + ". "
            f'El 15 de agosto es domingo: lo pasan al lunes 16 {", ".join(moved16)}' + (f'; {", ".join(moved11)} al 11 de octubre.' if moved11 else ".")),
           ("¿Cuántos días laborables tiene 2027?",
            f"261 de lunes a viernes. Restando los festivos quedan entre {min(labs)} y {max(labs)}, según la comunidad, sin contar los 2 locales."),
           ("¿Cuándo es Semana Santa 2027?", "Del domingo 21 al domingo 28 de marzo. Jueves Santo es el 25 y Viernes Santo el 26.")]
    more = (f'<section class="more wrap" id="more"><div class="more-in">'
            f'<section aria-labelledby="h-hubs"><h2 id="h-hubs">Más calendarios</h2><ul class="links">'
            + "".join(f'<li><a href="{B.BASE}{p}">{E(n)}</a></li>' for p, n in B.HUBS if p in BUILT_HUBS)
            + f'</ul></section>{faq_html(qas)}</div></section>')
    title, desc = t("title_home"), t("desc_home")
    lds = [{"@type": "WebSite", "name": t("site_name"), "alternateName": B.HOST, "url": B.URL, "inLanguage": "es-ES"},
           {"@type": "Organization", "name": t("site_name"), "url": B.URL, "logo": f"{B.SITE}{B.ASSETS}icons/icon-512.png"},
           {"@type": "WebApplication", "name": t("ld_app"), "url": B.URL, "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Web, Android", "inLanguage": B.LANG, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
            "description": desc},
           faq_ld(qas)]
    return B.head_html(title, desc, "", f"{B.SITE}{B.ASSETS}og/espana.png", ld(*lds)) + B.app_body(DATA, None, None, more)


# ---------------------------------------------------------------- entry points

DATA = None
BUILT_HUBS = {"festivos-locales/"}  # hubs that exist so far; the footer and home only link these


def write_pages(data, fix):
    """Write every page of this language. Returns [(path, lastmod)] for the sitemap (privacy is left out)."""
    global DATA, _fix
    DATA, _fix = data, fix
    _written.clear()
    B.HUBS[:] = [h for h in B.HUBS if h[0] in BUILT_HUBS]
    regions = {r["slug"]: r for r in data["regions"]}
    loc = load_locales()
    cities = published_cities(loc, regions)
    write("", home_page(), data["updated"])
    for r in data["regions"]:
        mine = [x for x in cities if x["r"]["slug"] == r["slug"]]
        pend = [c["name"] for c in loc["cities"] if c["region"] == r["slug"] and (c["status"] not in PUBLISHED or not c["holidays"])]
        write(f'{r["slug"]}/', region_page(r, mine, pend), data["updated"])
    for x in cities:
        sib = [s for s in cities if s["r"]["slug"] == x["r"]["slug"] and s is not x][:10]
        write(x["path"], city_page(x, sib), x["c"]["source"]["checked"])
    write("festivos-locales/", hub_locales(loc, regions, cities), loc["updated"])
    return list(_written)


def csv_text(rows):
    """Spanish Excel: UTF-8 with BOM, ';' separator, CRLF."""
    out = ["Fecha;Día;Festivo;Ámbito"]
    for iso, name, scope in rows:
        d = D(iso)
        cells = [d.strftime("%d/%m/%Y"), t("wd")[d.weekday()], name, scope]
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
    """Files shared by every language: .csv for regions and cities, .ics and og images for cities."""
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
            B.og_image(B.ROOT / "og" / f"{key}.png", x["title_name"], t("og_sub", n=x["n"], p=len(x["pts"])), x["hols"])
