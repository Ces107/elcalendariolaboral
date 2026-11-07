"""Castilla y León 2026 local holidays from the Junta de Castilla y León open-data calendar ("Fiestas locales: Calendario
de Fiestas de Carácter Local", datosabiertos.jcyl.es, 2026 distribution), used ONLY as a gap filler for municipalities
that the nine provincial bulletin lists (parts bop-<province>-2026) do not give.

Download (outside the repo):
    https://datosabiertos.jcyl.es/web/jcyl/risp/es/empleo/fiestas-locales/1284952783683-3.csv
Run AFTER the nine loc2026_bop-*-2026.py parsers (it skips every municipality they already wrote):
    python -E -P data/tools/loc2026_jcyl-2026.py <downloaded.csv>

CSV (latin-1, ';'): Provincia;Municipio;Fecha fiesta;Nombre fiesta;INE. The file mixes in entidades locales menores
under their municipality's code, carries some wrong codes and some previous-year or blank dates, so a row is used only
if its printed name matches the INE code it carries, and a municipality only if all its dates are 2026.
"""
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import PARTS, Matcher, write_part  # noqa: E402

PROVS = {"05": "avila", "09": "burgos", "24": "leon", "34": "palencia", "37": "salamanca", "40": "segovia",
         "42": "soria", "47": "valladolid", "49": "zamora"}
SOURCE = {
    "title": "Junta de Castilla y León, datos abiertos: Fiestas locales: Calendario de Fiestas de Carácter Local, año "
             "2026 (only municipalities missing from the provincial bulletin lists)",
    "url": "https://datosabiertos.jcyl.es/web/jcyl/risp/es/empleo/fiestas-locales/1284952783683-3.csv",
    "published": "2026-09-02",  # dataset page "fechaOrdenacion" (last update); the CSV itself carries no date
    "accessed": "2026-11-07",
}
# Rows whose name matches their code but which repeat another municipality's bulletin entry (wrong name in the CSV):
# "REDECILLA DEL CAMPO" carries exactly the days and names of Redecilla del Camino (09307) in BOP Burgos.
EXCLUDE = {"09308"}
NOTE = ("Not in the 2026 provincial bulletin list of the Oficina Territorial de Trabajo; taken from the Junta de "
        "Castilla y León open-data calendar of local holidays.")


def main(path):
    mt = Matcher()
    covered = set()
    for slug in PROVS.values():
        p = PARTS / f"bop-{slug}-2026.json"
        assert p.exists(), f"run loc2026_bop-{slug}-2026.py first"
        covered |= set(json.loads(p.read_text("utf-8"))["municipios"])
    rows = {}
    with open(path, encoding="latin-1", newline="") as f:
        for r in list(csv.reader(f, delimiter=";"))[1:]:
            if len(r) != 5:
                continue
            prov, name, fecha, fname, ine = (c.strip() for c in r)
            ine = ine.zfill(5)
            if ine[:2] not in PROVS or ine in covered or ine in EXCLUDE or mt.match(name, province=ine[:2]) != ine:
                continue
            rows.setdefault(ine, []).append((fecha, fname, name))
    by_ine, skipped = {}, []
    for ine, rs in sorted(rows.items()):
        ds = {}
        for fecha, fname, name in rs:
            if len(fecha) == 10 and fecha[2] == "/" and fecha[6:] == "2026":
                ds.setdefault(f"2026-{fecha[3:5]}-{fecha[:2]}", fname.title() if fname != "FIESTA LOCAL" else "Fiesta local")
            else:
                ds = None
                break
        if not ds:
            if all(r[0] == "NO COMUNICADA" for r in rs):
                continue
            skipped.append(f"{ine} {rs[0][2]}: {[r[0] for r in rs]} (not all 2026)")
            continue
        rec = {"holidays": [{"date": d, "name": n} for d, n in sorted(ds.items())], "note": NOTE}
        if len(ds) != 2:
            rec["note"] += f" The calendar gives {len(ds)} day(s)."
        by_ine[ine] = rec
    for ine, v in by_ine.items():
        print(ine, mt.by_ine[ine]["name"], [h["date"] for h in v["holidays"]])
    write_part("jcyl-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=skipped)


if __name__ == "__main__":
    main(sys.argv[1])
