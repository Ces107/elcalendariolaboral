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
SKIP = {".git", ".well-known", "data", "seo", "icons", "og", "ics", "csv", "privacidad", "__pycache__"}
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

print(f"{len(fails)} fallos" if fails else f"OK: 19 comunidades, 12 festivos cada una, días de la semana correctos; {len(pages)} páginas en el sitemap")
for f in fails:
    print(" -", f)
sys.exit(1 if fails else 0)
