"""Coordinates of every municipality from Wikidata (CC0) -> data/tools/coords.json.

Wikidata Query Service: items with an INE municipality code (P772) and coordinates (P625). Only 5-digit codes present in
data/municipios.json are kept. Several items or points for one code (old and new item, a point per village) are
reduced to the point nearest the median of that code's points. Outliers are dropped: a point farther than
MAX_KM from its province's median point (Canarias, Baleares and Ceuta/Melilla are separate provinces, so the median is
local). Then `python -E -P data/tools/build_municipios.py --pop` adds lat/lon to data/municipios.json.

    python -E -P data/tools/fetch_coords.py
"""
import json
import math
import re
import statistics
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = "https://query.wikidata.org/sparql"
QUERY = "SELECT ?ine ?coord WHERE { ?m wdt:P772 ?ine; wdt:P625 ?coord. }"
UA = "elcalendariolaboral.es-data-build/1.0 (https://elcalendariolaboral.es/contacto/)"
MAX_KM = {"default": 220, "illes-balears": 250, "las-palmas": 250, "santa-cruz-de-tenerife": 250}


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


def main():
    req = urllib.request.Request(ENDPOINT + "?" + urllib.parse.urlencode({"query": QUERY, "format": "json"}),
                                 headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    rows = json.load(urllib.request.urlopen(req, timeout=180))["results"]["bindings"]
    munis = json.loads((ROOT / "data" / "municipios.json").read_text("utf-8"))["municipios"]
    known = {m["ine"]: m for m in munis}
    pts = defaultdict(list)
    for r in rows:
        ine = r["ine"]["value"].strip()
        m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", r["coord"]["value"])
        if ine in known and m:
            pts[ine].append((float(m.group(2)), float(m.group(1))))  # (lat, lon)
    one = {}
    for ine, ps in pts.items():
        med = (statistics.median(p[0] for p in ps), statistics.median(p[1] for p in ps))
        one[ine] = min(ps, key=lambda p: km(p, med))
    by_prov = defaultdict(list)
    for ine, p in one.items():
        by_prov[known[ine]["province_slug"]].append(p)
    pmed = {k: (statistics.median(p[0] for p in v), statistics.median(p[1] for p in v)) for k, v in by_prov.items()}
    out, dropped = {}, []
    for ine, p in sorted(one.items()):
        ps = known[ine]["province_slug"]
        if km(p, pmed[ps]) > MAX_KM.get(ps, MAX_KM["default"]):
            dropped.append((ine, known[ine]["name"], round(km(p, pmed[ps]))))
            continue
        out[ine] = [round(p[0], 5), round(p[1], 5)]
    res = {"source": {"title": "Wikidata (CC0): INE municipality code (P772) and coordinate location (P625)",
                      "url": "https://query.wikidata.org/", "license": "CC0 1.0"},
           "count": len(out), "coords": out}
    (ROOT / "data" / "tools" / "coords.json").write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")) + "\n",
                                                         "utf-8", newline="\n")
    print(f"{len(rows)} rows, {len(one)} of {len(munis)} municipalities with a point, {len(out)} kept "
          f"({100 * len(out) / len(munis):.1f} %), dropped {dropped}")
    print("missing:", [(m["ine"], m["name"]) for m in munis if m["ine"] not in out][:40])


if __name__ == "__main__":
    main()
