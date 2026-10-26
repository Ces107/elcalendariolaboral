"""/calendario-laboral-2027-pdf/: every PDF of pdfs.py by comunidad (Spanish only, called by pages.write_pages).

File names live here (no reportlab import) so the hub, the page buttons, pdfs.py and the tests agree:
    pdf/<key>/calendario-laboral-2027-<key>[-vertical|-mensual].pdf, pdf/<slug>/calendario-escolar-2026-2027-<slug>.pdf
"""
import build as B
from build import E

PATH = "calendario-laboral-2027-pdf/"
ONLY = ["es"]
KINDS = [("", "Horizontal"), ("-vertical", "Vertical"), ("-mensual", "Mensual")]


def file_of(key, kind=""):
    return f"pdf/{key}/calendario-laboral-2027-{key}{kind}.pdf"


def school_file(slug):
    return f"pdf/{slug}/calendario-escolar-2026-2027-{slug}.pdf"


def entries(data, cities, school_slugs=()):
    """[(file, page path, label, holidays or None)]: every PDF the build writes."""
    out = []
    for r in data["regions"]:
        slug = r["slug"]
        keys = [(slug, r["name"], B.region_holidays(data, slug))]
        keys += [(f'{slug}-{o["slug"]}', f'{r["name"]} · {o["name"]}', B.region_holidays(data, slug, o["slug"]))
                 for o in data["zones"].get(slug, {}).get("options", []) if "add" in o]
        for key, label, hols in keys:
            out += [(file_of(key, k), f"{slug}/", f"{label} · {lab}", hols) for k, lab in KINDS]
    for x in cities:
        key = f'{x["r"]["slug"]}-{x["slug"]}'
        out += [(file_of(key, k), x["path"], f'{x["title_name"]} · {lab}', x["hols"]) for k, lab in KINDS[:2]]
    out += [(school_file(s), f"calendario-escolar/{s}/", f"Calendario escolar 2026-2027 · {s}", None) for s in school_slugs]
    return out


def links(key, kinds):
    return " · ".join(f'<a href="{B.ASSETS}{file_of(key, k)}" type="application/pdf">{lab}</a>' for k, lab in kinds)


def write_page(data, write, cities):
    import escolar
    import pages
    sch = {x["slug"] for x in (escolar.load("escolar-2026-27.json") or {}).get("regions", [])}
    n_files = len(entries(data, cities, sch))
    blocks = []
    for r in data["regions"]:
        slug = r["slug"]
        rows = [f'<tr><th scope="row"><a href="{B.BASE}{slug}/">{E(r["name"])}</a></th><td>{links(slug, KINDS)}</td></tr>']
        for o in data["zones"].get(slug, {}).get("options", []):
            if "add" in o:
                rows.append(f'<tr class="sub"><th scope="row">{E(o["name"])}</th><td>{links(f"{slug}-{o['slug']}", KINDS)}</td></tr>')
        for x in [x for x in cities if x["r"]["slug"] == slug]:
            rows.append(f'<tr class="sub"><th scope="row"><a href="{B.BASE}{x["path"]}">{E(x["title_name"])}</a></th>'
                        f'<td>{links(x["r"]["slug"] + "-" + x["slug"], KINDS[:2])}</td></tr>')
        if slug in sch:
            rows.append(f'<tr class="sub"><th scope="row"><a href="{B.BASE}calendario-escolar/{slug}/">Calendario escolar 2026-2027</a></th>'
                        f'<td><a href="{B.ASSETS}{school_file(slug)}" type="application/pdf">PDF</a></td></tr>')
        blocks.append(f'<section class="sec" id="{slug}" aria-labelledby="h-{slug}"><div class="sec-h"><h2 id="h-{slug}">'
                      f'<a href="{B.BASE}{slug}/">{E(r["name"])}</a></h2></div>'
                      f'<table class="tbl hub"><tbody>{"".join(rows)}</tbody></table></section>')
    h1 = "Calendario laboral 2027 PDF"
    title = B.pick(60, "Calendario laboral 2027 PDF para imprimir, por comunidad", "Calendario laboral 2027 PDF para imprimir")
    desc = B.pick(155, f"Calendario laboral 2027 en PDF para imprimir: A4 horizontal, vertical y mensual de las 19 comunidades "
                       f"y {len(cities)} ciudades con sus festivos locales. Según el BOE.",
                  f"Calendario laboral 2027 en PDF para imprimir: las 19 comunidades y {len(cities)} ciudades con festivos locales.")
    crumbs = [(B.t("spain"), ""), (h1, PATH)]
    chips = "".join(f'<li><a href="#{r["slug"]}">{E(r["name"])}</a></li>' for r in data["regions"])
    src = data["source"]
    ctx = f'<p class="ctx">{n_files} PDF · A4 · <a href="{src["url"]}" rel="noopener">{src["id"]}</a></p>'
    main = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{ctx}</div>'
            f'<div class="wrap body narrow">{B.section("comunidades", B.t("pick_region"), f"<ul class=chips>{chips}</ul>")}'
            f'{"".join(blocks[:3])}{B.ad("hub")}{"".join(blocks[3:])}</div>')
    docs = {"@type": "ItemList", "name": h1, "numberOfItems": len(data["regions"]), "itemListElement": [
        {"@type": "ListItem", "position": k + 1, "name": f'Calendario laboral 2027 {r["name"]} PDF',
         "url": f'{B.SITE}{B.ASSETS}{file_of(r["slug"])}'} for k, r in enumerate(data["regions"])]}
    head = B.head_html(title, desc, PATH, f"{B.SITE}{B.ASSETS}og/espana.png", pages.ld(pages.crumbs_ld(crumbs), docs), langs=ONLY)
    write(PATH, B.page(head, "pg", "", main, data, js=False), data["updated"], ONLY)
