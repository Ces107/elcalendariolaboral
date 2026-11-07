"""Every municipality (8,132, INE) and province: the catalogue for search, and (MUNI_ON) a lean page for each.

    data/municipios.json        INE catalogue: ine, name, name_es, aliases, slug, province(_slug/_code), region, capital, island
    data/provincias.json        52 provinces: code, name, slug, aliases, region, capital_ine, municipios
    data/locales-2027.json      202 cities, the source of the existing rich city pages (pages.py): kept as they are
    data/locales-2027-all.json  official 2027 locals of every municipality in a published bulletin (optional)
    data/locales-2026.json      official 2026 locals, shown only as a labelled reference while 2027 is pending (optional)

URLs: a municipality is /<region>/<slug>/ (the 155 existing city pages keep theirs; a slug taken twice in a region
gets -<province_slug>). A province is /<region>/provincia-de-<slug>/; in the 7 single-province comunidades the same
list is /<region>/municipios/ ("provincia de Madrid" is not how anyone says it). Ceuta and Melilla have no province
page: province, city and comunidad are the same place.

Indexing: a municipality with official 2027 locals is index,follow and in the sitemap; a pending one is noindex,follow
and out of the sitemap, and flips on the next build once its bulletin is in the data. No ads on these new page types
(head_html(ads=False)) until AdSense has reviewed the site (seo/ads.md).
"""
import json
import os
import re
import unicodedata
from collections import Counter, defaultdict

import build as B

MUNI_ON = os.environ.get("CL_MUNI", "0") == "1"
OFFICIAL = ("boletin", "ayuntamiento")
NO_PROV_PAGE = {"ceuta", "melilla"}
# Val d'Aran (Conselh Generau d'Aran): its 9 municipalities take the Aran zone of data/2027.json (Fiesta de Arán)
ARAN = {"25025", "25031", "25045", "25057", "25059", "25063", "25121", "25243", "25247"}


def load(name):
    p = B.ROOT / "data" / name
    return json.loads(p.read_text("utf-8")) if p.exists() else None


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def names_of(m):
    out = {m["name"], m["name_es"], m["ine_name"], *m.get("aliases", [])}
    for n in list(out):
        out.update(x.strip() for x in n.split("/"))
        if ", " in n:  # INE "Coruña, A"
            a, b = n.rsplit(", ", 1)
            out.add(f"{b} {a}")
    return {fold(x) for x in out if x}


_CAT = None


def catalogue():
    """All municipalities and provinces with their page path, status and data. Same result in every language build."""
    global _CAT
    if _CAT is not None:
        return _CAT
    mj, pj = load("municipios.json"), load("provincias.json")
    loc = load("locales-2027.json")
    all27, loc26 = load("locales-2027-all.json"), load("locales-2026.json")
    cat = {"munis": [], "provs": [], "by_ine": {}, "conflicts": [], "unmatched": [], "has27": bool(all27), "has26": bool(loc26),
           "src27": (all27 or {}).get("sources", {}), "src26": (loc26 or {}).get("sources", {})}
    _CAT = cat
    if not mj or not pj:
        return cat
    regions_prov = Counter(p["region"] for p in pj["provincias"])
    for p in pj["provincias"]:
        uni = regions_prov[p["region"]] == 1
        path = "" if p["region"] in NO_PROV_PAGE else (f'{p["region"]}/municipios/' if uni else f'{p["region"]}/provincia-de-{p["slug"]}/')
        cat["provs"].append({**p, "uni": uni, "path": path,
                             "label": f'Municipios de {p["name"]}' if uni else f'Provincia de {p["name"]}', "munis": []})
    provs = {p["slug"]: p for p in cat["provs"]}

    rich = {(c["region"], c["slug"]): c for c in loc["cities"] if c["status"] in OFFICIAL and c["holidays"]}
    existing = {(c["region"], c["slug"]): c for c in loc["cities"]}
    taken = Counter((m["region"], m["slug"]) for m in mj["municipios"])
    by_prov_name = defaultdict(dict)
    for m in mj["municipios"]:
        for n in names_of(m):
            by_prov_name[fold(m["province"])].setdefault(n, m["ine"])

    # 2027 official locals of every bulletin, by INE code ("province|name" keys matched by name inside the province)
    o27 = {}
    for k, v in ((all27 or {}).get("municipios") or {}).items():
        ine = k if re.fullmatch(r"\d{5}", k) else None
        if not ine and "|" in k:
            pr, nm = k.split("|", 1)
            ine = by_prov_name.get(fold(pr), {}).get(fold(nm))
        if not ine:
            cat["unmatched"].append(k)
            continue
        o27[ine] = v

    for m in mj["municipios"]:
        key = (m["region"], m["slug"])
        p = provs[m["province_slug"]]
        if key in rich:
            path, kind = f'{m["region"]}/{m["slug"]}/', "city"
        else:
            slug = m["slug"] if taken[key] == 1 or key in existing else f'{m["slug"]}-{m["province_slug"]}'
            path, kind = f'{m["region"]}/{slug}/', "page"
        zone = m.get("island") or (("aran" if m["ine"] in ARAN else "general") if m["region"] == "cataluna" else None)
        x = {"m": m, "ine": m["ine"], "name": m["name_es"], "official_name": m["name"], "path": path, "kind": kind, "prov": p,
             "region": m["region"], "zone": zone, "status": None, "hol27": None, "src27": None, "note": None, "ref26": None, "src26": None}
        e = o27.get(m["ine"])
        if e and e.get("status") in OFFICIAL and e.get("holidays"):
            x.update(status=e["status"], hol27=sorted(e["holidays"], key=lambda h: h["date"]), note=e.get("note"),
                     src27=cat["src27"].get(e.get("source")) or ({"title": e["source"], "url": ""} if e.get("source") else None))
        if kind == "city":
            c = rich[key]
            x.update(status=c["status"], hol27=c["holidays"], src27={"title": c["source"]["title"], "url": c["source"]["url"]})
            if e and e.get("holidays"):
                a = sorted(h["date"] for h in c["holidays"])
                b = sorted(h["date"] for h in e["holidays"])
                if a != b:
                    cat["conflicts"].append({"ine": m["ine"], "name": m["name_es"], "locales-2027": a, "locales-2027-all": b,
                                             "source_all": e.get("source")})
        r26 = ((loc26 or {}).get("municipios") or {}).get(m["ine"])
        if r26 and r26.get("holidays"):
            x.update(ref26=sorted(r26["holidays"], key=lambda h: h["date"]), src26=cat["src26"].get(r26.get("source")))
        x["ok"] = bool(x["hol27"])
        cat["munis"].append(x)
        cat["by_ine"][m["ine"]] = x
        p["munis"].append(x)
    return cat


def index_rows():
    """(munis, provs) for buscar.build_index: every municipality with a page (all of them when MUNI_ON; otherwise only the
    existing city pages), provinces with a path only when their page is written."""
    cat = catalogue()
    munis = [{"name": x["name"], "province_slug": x["prov"]["slug"], "path": x["path"], "ok": x["ok"],
              "aliases": sorted({x["official_name"], *x["m"].get("aliases", [])} - {x["name"]})}
             for x in cat["munis"] if MUNI_ON or x["kind"] == "city"]
    provs = [{"name": p["name"], "slug": p["slug"], "region": p["region"], "aliases": p.get("aliases", []),
              "path": p["path"] if MUNI_ON else "", "label": p["label"]} for p in cat["provs"]]
    return munis, provs
