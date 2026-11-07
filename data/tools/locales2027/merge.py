"""Build data/locales-2027-all.json from <workdir>/parsed/*.json plus the official
entries already in data/locales-2027.json.

python -I merge.py <workdir> [--write]
Without --write it only prints the coverage table and the conflicts."""
import glob
import json
import os
import re
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

W = common.workdir_from_argv()
WRITE = "--write" in sys.argv
UPDATED = "2026-11-07"
OUT = os.path.join(common.REPO, "data", "locales-2027-all.json")
OLD = os.path.join(common.REPO, "data", "locales-2027.json")
PROV_CODE = {v[0]: k for k, v in common.PROVINCES.items()}
ROMAN = {r: i for i, r in enumerate("I II III IV V VI VII VIII IX X XI XII".split(), start=1)}

ine = common.INE(W)


def display_name(ine_name):
    """INE 'Coruña, A' -> 'A Coruña'; "Alfàs del Pi, l'" -> "L'Alfàs del Pi"; per '/' part."""
    out = []
    for part in ine_name.split("/"):
        m = re.match(r"^(.*),\s*(\S+)$", part)
        if m and common.norm(m.group(2)) in common.ARTICLES:
            art = m.group(2)
            art = art[0].upper() + art[1:]
            part = f"{art}{m.group(1)}" if art.endswith("'") else f"{art} {m.group(1)}"
        out.append(part)
    return "/".join(out)


def slug(s):
    s = common.strip_accents(s).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def pub_from_title(title):
    m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](20\d\d)", title)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m = re.search(r"(\d{1,2})-([IVX]+)-(20\d\d)", title)
    if m and m.group(2) in ROMAN:
        return f"{m.group(3)}-{ROMAN[m.group(2)]:02d}-{int(m.group(1)):02d}"
    return None


sources = {}
munis = {}
log = []


def put(key, entry, origin):
    old = munis.get(key)
    if old:
        rank = lambda e: (e["status"] == "boletin", sources[e["source"]].get("published") or "")
        a = [h["date"] for h in old["holidays"]]
        b = [h["date"] for h in entry["holidays"]]
        if a != b:
            log.append(f"CONFLICT {key} {old['name']}: {old['source']} {a} vs {entry['source']} {b}")
        if rank(entry) <= rank(old):
            log.append(f"keep {key} from {old['source']} over {entry['source']}")
            return
        log.append(f"replace {key}: {old['source']} -> {entry['source']} ({origin})")
    munis[key] = entry


# 1) parsed bulletins / council agreements
for path in sorted(glob.glob(os.path.join(W, "parsed", "*.json"))):
    p = json.load(open(path, encoding="utf-8"))
    sid = p["id"]
    sources[sid] = {"title": p["title"], "url": p["url"], "published": p.get("published")}
    for r in p["rows"]:
        src = sid
        if r.get("source_url"):  # one file holding several council sources
            src = f"{sid}:{slug(r['name'])}"
            sources[src] = {"title": r.get("source_title") or p["title"], "url": r["source_url"],
                            "published": r.get("published") or p.get("published")}
        cpro = r.get("cpro") or (r["ine"][:2] if r.get("ine") else None)
        prov, region = common.PROVINCES[cpro] if cpro else (r.get("province"), p.get("region"))
        if r.get("ine"):
            key, name = r["ine"], display_name(ine.by_code[r["ine"]])
        else:
            key, name = f"{prov}|{r['name']}", r["name"]
            log.append(f"no INE code: {key} ({sid})")
        e = {"name": name, "province": prov, "region": region,
             "holidays": [{"date": h["date"], "name": h.get("name")} for h in r["holidays"]],
             "status": r.get("status", "boletin"), "source": src}
        if r.get("note"):
            e["note"] = r["note"]
        locs = r.get("localities") or r.get("sub_municipal")  # DOE parser names it sub_municipal
        if locs:
            e["localities"] = locs
        put(key, e, sid)

# 2) official entries already on the site (data/locales-2027.json)
old = json.load(open(OLD, encoding="utf-8"))
for c in old["cities"]:
    cpro = PROV_CODE[c["province"]]
    code, how = ine.match(cpro, c["name"])
    key = code or f"{c['province']}|{c['name']}"
    if c["status"] not in ("boletin", "ayuntamiento"):
        if key not in munis:
            continue
        log.append(f"now official: {key} {c['name']} (was {c['status']}) via {munis[key]['source']}")
        continue
    if key in munis:
        e = munis[key]
        a = [h["date"] for h in c["holidays"]]
        b = [h["date"] for h in e["holidays"]]
        if a != b:
            log.append(f"DIFF vs site data {key} {c['name']}: site {a} ({c['status']}) / new {b} ({e['source']})")
        # carry curated festivity names onto bulletin rows that print dates only
        names = {h["date"]: h.get("name") for h in c["holidays"]}
        for h in e["holidays"]:
            if not h["name"] and names.get(h["date"]):
                h["name"] = names[h["date"]]
        continue
    s = c["source"]
    sid = "site:" + c["slug"]
    sources[sid] = {"title": s["title"], "url": s["url"], "published": pub_from_title(s["title"])}
    e = {"name": display_name(ine.by_code[code]) if code else c["name"], "province": c["province"],
         "region": c["region"], "holidays": [{"date": h["date"], "name": h.get("name")} for h in c["holidays"]],
         "status": c["status"], "source": sid}
    if c.get("note"):
        e["note"] = c["note"]
    put(key, e, "site")

# 3) coverage per region
regions = {}
for code in ine.by_code:
    regions.setdefault(common.PROVINCES[code[:2]][1], {"total": 0})["total"] += 1
for e in munis.values():
    r = regions.setdefault(e["region"], {"total": 0})
    r[e["status"]] = r.get(e["status"], 0) + 1
print(f"{'region':22} {'INE':>5} {'boletin':>8} {'ayto':>5}")
for reg in sorted(regions):
    v = regions[reg]
    print(f"{reg:22} {v['total']:5} {v.get('boletin', 0):8} {v.get('ayuntamiento', 0):5}")
print("total", len(munis), "of", len(ine.by_code))
for x in log:
    print(x)
used = {e["source"] for e in munis.values()}
sources = {k: v for k, v in sorted(sources.items()) if k in used}

doc = {
    "year": 2027,
    "updated": UPDATED,
    "about": ("Fiestas locales de 2027 por municipio (clave: código INE de 5 cifras). Solo publicadas "
              "oficialmente: boletín (BOP/autonómico) o acuerdo del ayuntamiento publicado por el propio "
              "ayuntamiento. 'name' es null cuando la publicación da solo la fecha. 'localities' recoge días "
              "que solo rigen en una parte del municipio. Los municipios sin publicación oficial no aparecen."),
    "status_values": {"boletin": "publicado en boletín oficial",
                      "ayuntamiento": "acuerdo publicado por el ayuntamiento, pendiente de boletín"},
    "sources": sources,
    "municipios": dict(sorted(munis.items())),
}
if WRITE:
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("wrote", OUT)
