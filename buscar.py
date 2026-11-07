"""Municipality search: the static index /buscar.json and the /buscar/ fallback page (Spanish, noindex).

The index is fetched by app.js on the first focus of a search box (never inlined in the pages) and versioned with
?v=<hash> (the service worker caches it like css/js). Compact rows, the URL is rebuilt in app.js:

    {"r": [[name, path, aliases]],                 comunidades (path below the site root)
     "p": [[name, region_idx, path, aliases]],     provincias (path "" while the province has no page)
     "m": [[name, prov_idx, path, ok, pop, aliases?]]}  municipios with a page; ok 1 = official 2027 local holidays,
                                                     pop = INE population (ranking tie-breaker)

aliases: "|"-joined other names (bilingual halves, exonyms: Castellón|Castelló). app.js folds accents and case.
"""
import hashlib
import json

import build as B
from build import E

PATH = "buscar/"
VARIANT = {"cataluna": "Catalunya", "pais-vasco": "Euskadi|Euskal Herria", "comunitat-valenciana": "Comunitat Valenciana|País Valencià",
           "baleares": "Illes Balears|Islas Baleares", "navarra": "Nafarroa", "asturias": "Principado de Asturias",
           "madrid": "Comunidad de Madrid", "murcia": "Región de Murcia"}


def load_json(name):
    p = B.ROOT / "data" / name
    return json.loads(p.read_text("utf-8")) if p.exists() else None


def build_index(data, munis, provs):
    """munis: [{name, province_slug, path, aliases, ok}] (municipios with a page); provs: [{name, slug, region, path, aliases}]."""
    regs = data["regions"]
    ri = {r["slug"]: k for k, r in enumerate(regs)}
    r_rows = [[r["name"], f'{r["slug"]}/', "|".join(x for x in [r["official"] if r["official"] != r["name"] else "",
                                                                     VARIANT.get(r["slug"], "")] if x)] for r in regs]
    pi = {p["slug"]: k for k, p in enumerate(provs)}
    p_rows = [[p["name"], ri[p["region"]], p.get("path") or "", "|".join(p.get("aliases") or [])] for p in provs]
    m_rows = sorted(([m["name"], pi[m["province_slug"]], m["path"], 1 if m["ok"] else 0, m.get("pop") or 0,
                      "|".join(a for a in m.get("aliases") or [] if a != m["name"])] for m in munis), key=lambda x: (x[0], x[1]))
    for row in m_rows:  # no aliases: 5 columns
        if not row[5]:
            del row[5]
    return {"r": r_rows, "p": p_rows, "m": m_rows}


def index_bytes(idx):
    return json.dumps(idx, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def index_hash(b):
    return hashlib.sha256(b).hexdigest()[:10]


def page(data, provs, write, upd):
    """/buscar/: the search box, then every comunidad and provincia as plain links (works without JS)."""
    regs = data["regions"]
    blocks = []
    for r in regs:
        ps = [p for p in provs if p["region"] == r["slug"] and p.get("path")]
        sub = "".join(f'<li><a href="{B.BASE}{p["path"]}">{E(p["label"])}</a></li>' for p in ps)
        blocks.append(f'<li><a href="{B.BASE}{r["slug"]}/"><b>{E(r["name"])}</b></a>{f"<ul>{sub}</ul>" if sub else ""}</li>')
    crumbs = [("España", ""), ("Buscar", PATH)]
    main = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(B.t("search"))}</h1>'
            f'{B.search_box("q-page", big=True)}</div>'
            f'<div class="wrap body narrow">' + B.section("lista", "Comunidades y provincias", f'<ul class="tree">{"".join(blocks)}</ul>')
            + '</div>')
    head = B.head_html("Buscar municipio · El Calendario Laboral", "Busca el calendario laboral 2027 de tu municipio.", PATH,
                       f"{B.SITE}{B.ASSETS}og/espana.png", index=False, ads=False)
    write(PATH, B.page(head, "pg", "", main, data, js=False), upd)
