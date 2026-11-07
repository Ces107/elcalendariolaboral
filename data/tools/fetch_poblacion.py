"""Official population of every municipality (INE, "Cifras oficiales de población de los municipios españoles:
Revisión del Padrón Municipal", latest year) -> data/tools/poblacion.json.

Source: INE API (servicios.ine.es/wstempus), operation 22, the 52 tables "<provincia>: Población por municipios y sexo"
(total, both sexes, last period). Then `python -E -P data/tools/build_municipios.py --pop` adds `pop` to
data/municipios.json (or a full rebuild from the xlsx picks it up too).

    python -E -P data/tools/fetch_poblacion.py
"""
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
API = "https://servicios.ine.es/wstempus/js/ES"


def get(url):
    for k in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (elcalendariolaboral.es data build)"})
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception as e:  # noqa: BLE001  (network hiccup: retry)
            print("retry", url, e)
            time.sleep(3 * (k + 1))
    raise SystemExit(f"failed: {url}")


def main():
    tables = [t for t in get(f"{API}/TABLAS_OPERACION/22") if "Población por municipios y sexo" in t["Nombre"]]
    assert len(tables) == 52, len(tables)
    pop, years = {}, set()
    for t in tables:
        for s in get(f"{API}/DATOS_TABLA/{t['Id']}?nult=1&tip=AM"):
            md = {m["T3_Variable"]: m for m in s["MetaData"]}
            mu = md.get("Municipios")
            if not mu or md["Sexo"]["Codigo"] != "0" or len(mu.get("Codigo") or "") != 5 or not s["Data"]:
                continue
            pop[mu["Codigo"]] = int(s["Data"][0]["Valor"])
            years.add(s["Data"][0]["Anyo"])
        time.sleep(0.3)
    assert len(years) == 1, years
    out = {"source": {"title": "INE, Cifras oficiales de población de los municipios españoles: Revisión del Padrón Municipal",
                      "url": "https://www.ine.es/dynt3/inebase/es/index.htm?padre=517", "date": f"{years.pop()}-01-01"},
           "count": len(pop), "pop": dict(sorted(pop.items()))}
    (ROOT / "data" / "tools" / "poblacion.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n",
                                                            "utf-8", newline="\n")
    print(len(pop), "municipios,", out["source"]["date"])


if __name__ == "__main__":
    main()
