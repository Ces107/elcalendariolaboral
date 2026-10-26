#!/usr/bin/env python3
"""Comprueba data/2027.json contra el BOE-A-2026-21254.  Uso: python test_data.py"""
import datetime as dt
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

data = build.load()
slugs = [r["slug"] for r in data["regions"]]
WD = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 19 comunidades en el orden del BOE
check(slugs == ["andalucia", "aragon", "asturias", "baleares", "canarias", "cantabria", "castilla-la-mancha",
                "castilla-y-leon", "cataluna", "extremadura", "galicia", "madrid", "murcia", "navarra", "pais-vasco",
                "la-rioja", "comunitat-valenciana", "ceuta", "melilla"], "orden de comunidades")

for h in data["holidays"]:
    check(h["regions"] == "all" or all(s in slugs for s in h["regions"]), f"slug desconocido en {h}")
    check(dt.date.fromisoformat(h["date"]).year == 2027, f"año {h}")

# 12 festivos por comunidad. Canarias: 11 del BOE (el 30 de mayo cae en domingo) + 1 insular por isla.
for s in slugs:
    hols = build.region_holidays(data, s)
    dates = [h["date"] for h in hols]
    check(len(set(dates)) == len(dates), f"{s}: fechas repetidas")
    if s == "canarias":
        check(len(hols) == 11, f"canarias BOE: {len(hols)} != 11")
        for o in data["zones"]["canarias"]["options"]:
            n = len(build.region_holidays(data, s, o["slug"]))
            check(n == 12, f"canarias/{o['slug']}: {n} != 12")
    else:
        check(len(hols) == 12, f"{s}: {len(hols)} != 12")
    check(not any(h["date"] == "2027-08-15" for h in hols), f"{s}: 15 ago no es festivo en 2027")
check(len(build.region_holidays(data, "cataluna", "aran")) == 12, "Arán != 12")
check("2027-03-29" not in [h["date"] for h in build.region_holidays(data, "cataluna", "aran")], "Arán conserva el 29 mar")

# 9 comunes a las 19
check(sum(h["regions"] == "all" for h in data["holidays"]) == 9, "9 nacionales comunes")
# Jueves Santo en todas salvo Cataluña y C. Valenciana
js = next(h for h in data["holidays"] if h["date"] == "2027-03-25")
check(set(js["regions"]) == set(slugs) - {"cataluna", "comunitat-valenciana"}, "Jueves Santo")

# días de la semana
WEEKDAYS = {"2027-01-01": "vie", "2027-01-06": "mié", "2027-03-25": "jue", "2027-03-26": "vie", "2027-03-29": "lun",
            "2027-05-01": "sáb", "2027-08-15": "dom", "2027-08-16": "lun", "2027-09-11": "sáb", "2027-10-09": "sáb",
            "2027-10-12": "mar", "2027-11-01": "lun", "2027-12-06": "lun", "2027-12-08": "mié", "2027-12-25": "sáb",
            "2027-06-17": "jue", "2027-05-30": "dom"}
for d, w in WEEKDAYS.items():
    check(WD[dt.date.fromisoformat(d).weekday()] == w, f"{d} no es {w}")

# puentes: casos calculados a mano (Madrid). Un puente cuesta al menos un laborable;
# los fines de semana largos van aparte y no se repiten si caen dentro de un puente.
mad = build.region_holidays(data, "madrid")
span = lambda it: (build.DAYS[it["s"]].isoformat(), build.DAYS[it["e"]].isoformat(), it["cost"])
p = {span(i) for i in build.puentes(mad)}
lw = {span(i) for i in build.long_weekends(mad)}
for exp in [("2027-12-04", "2027-12-08", 1), ("2027-10-09", "2027-10-12", 1), ("2027-01-01", "2027-01-06", 2)]:
    check(exp in p, f"madrid puente {exp} no encontrado")
check(all(c > 0 for _, _, c in p), "puente sin coste")
for exp in [("2027-03-25", "2027-03-28", 0), ("2027-08-14", "2027-08-16", 0)]:
    check(exp in lw, f"madrid fin de semana largo {exp} no encontrado")
for gone in [("2027-01-01", "2027-01-03", 0), ("2027-12-04", "2027-12-06", 0)]:
    check(gone not in lw, f"madrid {gone} esta dentro de un puente y no debe salir")

# ---------------------------------------------------------------- generated site (run build.py first)
import json  # noqa: E402
import re  # noqa: E402

ROOT = Path(__file__).resolve().parent
SKIP = {".git", ".well-known", "data", "seo", "icons", "og", "ics", "csv", "privacidad", "__pycache__", "embed"}
pages = sorted(p for p in ROOT.rglob("index.html") if not SKIP & set(p.relative_to(ROOT).parts[:-1]))
sm = (ROOT / "sitemap.xml").read_text("utf-8")
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
site = locs[0].rstrip("/") if locs else ""
paths_in_sm = {u[len(site):] for u in locs}
for p in pages:
    rel = "/" + "/".join(p.relative_to(ROOT).parts[:-1]) + ("/" if len(p.relative_to(ROOT).parts) > 1 else "")
    check(rel in paths_in_sm, f"{rel} no está en sitemap.xml")
    h = p.read_text("utf-8")
    title = re.search(r"<title>([^<]*)</title>", h).group(1)
    desc = re.search(r'<meta name="description" content="([^"]*)"', h).group(1)
    import html as _h  # noqa: E402
    check(len(_h.unescape(title)) <= 60, f"{rel}: título de {len(_h.unescape(title))} > 60: {title}")
    check(len(_h.unescape(desc)) <= 155, f"{rel}: descripción de {len(_h.unescape(desc))} > 155")
    check(h.count("<h1") == 1, f"{rel}: debe tener un solo h1")
    check('"@type": "Event"' not in h, f"{rel}: sin marcado Event")
check(len(pages) == len(paths_in_sm), f"sitemap {len(paths_in_sm)} urls != {len(pages)} páginas")
_seen = {}
for p in pages:
    h = p.read_text("utf-8")
    for tag in (re.search(r"<title>([^<]*)</title>", h).group(1), re.search(r'<meta name="description" content="([^"]*)"', h).group(1)):
        check(tag not in _seen, f"{p.relative_to(ROOT)}: título o descripción repetidos con {_seen.get(tag)}")
        _seen.setdefault(tag, p.relative_to(ROOT))

# páginas de ciudad: solo las publicadas, con sus 2 fechas oficiales
loc = json.loads((ROOT / "data" / "locales-2027.json").read_text("utf-8"))
for c in loc["cities"]:
    f = ROOT / c["region"] / c["slug"] / "index.html"
    published = c["status"] in ("boletin", "ayuntamiento") and c["holidays"]
    check(f.exists() == bool(published), f"{c['region']}/{c['slug']}: página {'falta' if published else 'sobra'}")
    if published:
        h = f.read_text("utf-8")
        check(len(c["holidays"]) == 2, f"{c['slug']}: {len(c['holidays'])} festivos locales")
        locs_attr = json.loads(__import__("html").unescape(re.search(r'data-locals="([^"]*)"', h).group(1)))
        check([x["date"] for x in locs_attr] == [x["date"] for x in c["holidays"]], f"{c['slug']}: fechas locales distintas de los datos")
        hl = re.search(r'<ol class="hl" id="hlist">(.*?)</ol>', h, re.S).group(1)
        for x in c["holidays"]:
            check('<li class="k-l"' in hl and f'datetime="{x["date"]}"' in hl, f"{c['slug']}: {x['date']} no está en la lista")
        reg = {x["date"] for x in build.region_holidays(data, c["region"])}
        check(not reg & {x["date"] for x in c["holidays"]}, f"{c['slug']}: un local coincide con un festivo de la comunidad")
        check(c["source"]["url"] in h, f"{c['slug']}: falta la fuente")
        check(("pendiente del boletín" in h) == (c["status"] == "ayuntamiento"), f"{c['slug']}: estado del boletín")
        check((ROOT / "csv" / f"{c['region']}-{c['slug']}.csv").exists(), f"{c['slug']}: falta el csv")
for s in slugs:
    b = (ROOT / "csv" / f"{s}.csv").read_bytes()
    check(b.startswith(b"\xef\xbb\xbfFecha;"), f"csv/{s}.csv: BOM y ';'")

# calendario escolar (solo castellano): una página por comunidad, fechas iguales al JSON, todas en el sitemap
esc = json.loads((ROOT / "data" / "escolar-2026-27.json").read_text("utf-8"))
nav_html = (ROOT / "vacaciones-escolares" / "navidad" / "index.html").read_text("utf-8")
ss_html = (ROOT / "vacaciones-escolares" / "semana-santa" / "index.html").read_text("utf-8")
car_html = (ROOT / "vacaciones-escolares" / "carnaval" / "index.html").read_text("utf-8")
for path in ["calendario-escolar/", "vacaciones-escolares/navidad/", "vacaciones-escolares/semana-santa/", "vacaciones-escolares/carnaval/"] + [f"calendario-escolar/{r['slug']}/" for r in esc["regions"]]:
    check(f"/{path}" in paths_in_sm, f"/{path} no está en sitemap.xml")
    check(not (ROOT / "ca" / path).exists(), f"/ca/{path} no debe existir (solo castellano)")
    f = ROOT / path / "index.html"
    check(f.exists(), f"falta /{path}")
    if f.exists():
        check('hreflang="ca"' not in f.read_text("utf-8").split("</head>")[0], f"/{path}: sin hreflang a idiomas que no tiene")
check(len(esc["regions"]) == 19, "escolar: 19 comunidades")


def nav_row(href, page=None):
    m = re.search(r'<a href="' + re.escape(href) + r'">.*?</tr>', nav_html if page is None else page, re.S)
    return m.group(0) if m else ""


def og_of(h):
    m = re.search(r'<meta property="og:image" content="[^"]*/og/([^"]+)"', h)
    return m.group(1) if m else ""


for r in esc["regions"]:
    f = ROOT / "calendario-escolar" / r["slug"] / "index.html"
    if not f.exists():
        continue
    h = f.read_text("utf-8")
    check(r["source"]["url"].replace("&", "&amp;") in h, f"escolar {r['slug']}: falta la fuente")
    units = [(p, f"/calendario-escolar/{r['slug']}/#" + __import__("escolar").slugify(p["name"])) for p in r.get("provinces", [])] \
        if r.get("provinces") and not r["stages"] and not r["breaks"] else [(r, f"/calendario-escolar/{r['slug']}/")]
    for u, href in units:
        prim = next((x for x in u["stages"] if "primaria" in x["stages"]), None)
        for k in ("start", "end"):
            if prim and prim[k]:
                check(f'datetime="{prim[k]}"' in h, f"escolar {r['slug']}/{u['name']}: falta {k} {prim[k]}")
        for n in u.get("non_teaching_days", []):
            check(f'data-d="{n["date"]}"' in h, f"escolar {r['slug']}: {n['date']} no está en la rejilla")
        for kind, page in (("navidad", nav_html), ("semana_santa", ss_html)):
            nb = next((b for b in u["breaks"] if b["type"] == kind), None)
            row = nav_row(href, page)
            check(bool(row), f"{kind}: falta la fila de {u['name']}")
            if not (nb and row):
                continue
            ds = re.findall(r'datetime="([\d-]+)"', row)
            n = int(re.search(r'class="num">(\d+)<', row).group(1))
            s, e = dt.date.fromisoformat(ds[0]), dt.date.fromisoformat(ds[1])
            check(s <= dt.date.fromisoformat(nb["start"]) and dt.date.fromisoformat(nb["end"]) <= e,
                  f"{kind} {u['name']}: {ds} no cubre {nb['start']}..{nb['end']}")
            check(n == (e - s).days + 1, f"{kind} {u['name']}: {n} días != {ds}")
            check((s - dt.timedelta(1)).weekday() < 5 and (e + dt.timedelta(1)).weekday() < 5, f"{kind} {u['name']}: el rango no acaba en día de clase")
            check(f'datetime="{nb["start"]}"' in h or s.isoformat() in h, f"escolar {r['slug']}: {kind} no está en la página")
        # carnaval: every February day without class of the file (break 'otro' or single day) sits inside a listed range
        feb = [n["date"] for n in u.get("non_teaching_days", []) if n["date"][:7] == "2027-02" and not re.search(r"(?i)patr[oó]n|solo", n["name"])]
        feb += [b["start"] for b in u["breaks"] if b["type"] == "otro" and b["start"][:7] == "2027-02"]
        if feb:
            crow = "".join(m.group(0) for m in re.finditer(r'<a href="' + re.escape(href) + r'">.*?</tr>', car_html, re.S))
            spans = re.findall(r'datetime="([\d-]+)">[^<]*</time></td><td data-l="Hasta"><time datetime="([\d-]+)"', crow)
            for x in feb:
                check(any(a <= x <= b for a, b in spans), f"carnaval {u['name']}: {x} no está en la tabla")
    check(og_of(h) == f"escolar-{r['slug']}.png" and (ROOT / "og" / og_of(h)).exists(), f"escolar {r['slug']}: og:image")
for path, img in (("calendario-escolar/", "escolar.png"), ("vacaciones-escolares/navidad/", "escolar-navidad.png"),
                  ("vacaciones-escolares/semana-santa/", "escolar-semana-santa.png"), ("vacaciones-escolares/carnaval/", "escolar-carnaval.png")):
    h = (ROOT / path / "index.html").read_text("utf-8")
    check(og_of(h) == img and (ROOT / "og" / img).exists(), f"/{path}: og:image {og_of(h)}")
    check('"@type": "BreadcrumbList"' in h, f"/{path}: falta BreadcrumbList")
cat = json.loads((ROOT / "data" / "escolar-2027-28.json").read_text("utf-8"))["regions"][0]
hc = (ROOT / "calendario-escolar" / "cataluna" / "index.html").read_text("utf-8")
check('id="curso-2027-2028"' in hc and f'datetime="{cat["stages"][0]["start"]}"' in hc, "cataluña: falta el curso 2027-2028")

# widget: la página en el sitemap; un embed por comunidad, isla y ciudad publicada, con el enlace de crédito visible
CREDIT = "Calendario laboral 2027 · elcalendariolaboral.es"
check("/widget/" in paths_in_sm, "/widget/ no está en sitemap.xml")
wp = ROOT / "widget" / "index.html"
check(wp.exists() and 'id="wprev"' in wp.read_text("utf-8") and CREDIT in _h.unescape(wp.read_text("utf-8")), "widget: falta la vista previa o el crédito en el código")
emb = ROOT / "widget" / "embed"
keys = slugs + [f"{c['region']}-{c['slug']}" for c in loc["cities"] if c["status"] in ("boletin", "ayuntamiento") and c["holidays"]] \
    + [f"{s}-{o['slug']}" for s, z in data["zones"].items() for o in z["options"] if "add" in o]
for k in keys:
    f = emb / k / "index.html"
    check(f.exists(), f"widget: falta /widget/embed/{k}/")
    if not f.exists():
        continue
    h = f.read_text("utf-8")
    cr = re.search(r'<p class="cr"><a href="([^"]+)" target="_blank" rel="noopener">([^<]+)</a></p>', h)
    check(bool(cr) and cr.group(2) == CREDIT and cr.group(1).startswith(site + "/"), f"widget {k}: enlace de crédito")
    check("<noscript" not in h and "nofollow" not in h, f"widget {k}: el crédito debe ser un enlace normal")
    check('<meta name="robots" content="noindex">' in h and f'<link rel="canonical" href="{cr.group(1) if cr else ""}">' in h, f"widget {k}: noindex y canonical")
    check(not re.search(r'(src|href)="(https?:)?//(?!' + re.escape(site.split("://")[-1]) + ')', h), f"widget {k}: petición externa")
    check("adsbygoogle" not in h and len(h.encode()) < 12000, f"widget {k}: sin anuncios y ligero ({len(h.encode())} B)")
    if k in slugs:
        exp = [x["date"] for x in build.region_holidays(data, k)]
        check(re.findall(r'data-d="([\d-]+)"', h) == exp, f"widget {k}: festivos distintos de los datos")
check(len(list(emb.iterdir())) == len(keys), f"widget: {len(list(emb.iterdir()))} embeds != {len(keys)}")
for p in pages:
    check("/widget/" in p.read_text("utf-8").split('<footer', 1)[-1], f"{p.relative_to(ROOT)}: falta «Widget para tu web» en el pie")

print(f"{len(fails)} fallos" if fails else f"OK: 19 comunidades, 12 festivos cada una, días de la semana correctos; {len(pages)} páginas en el sitemap")
for f in fails:
    print(" -", f)
sys.exit(1 if fails else 0)
