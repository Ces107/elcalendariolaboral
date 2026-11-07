"""Toledo province 2026 local holidays: Resolución de la Delegación Provincial de Economía, Empresas y Empleo en Toledo
(BOP Toledo núm. 199, 17-10-2025, inserción 5039). No later corrections found in the BOP search (2025-09 .. 2026-11).

Download (outside the repo):
    https://bop.diputoledo.es/webEbop/DocGet?id=25103044%3B0&insert_number=5039&insert_year=2025  -> to5039.pdf
Run:
    python -E -P data/tools/loc2026_bop-toledo-2026.py to5039.pdf

Table read with PyMuPDF find_tables() (AYUNTAMIENTO | date | date), dates only, no festivity names.
UPPERCASE rows are municipalities; mixed-case rows are pedanías / entidades locales with their own days, attached to the
preceding municipality as "nucleos".
"""
import datetime
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "45"
SOURCE = {
    "title": "Resolución de la Delegación Provincial de la Consejería de Economía, Empresas y Empleo en Toledo por la que "
             "se declaran inhábiles a efectos laborales en los distintos municipios de la provincia para el año 2026 los "
             "días que se relacionan (BOP Toledo núm. 199, de 17-10-2025, inserción 5039)",
    "url": "https://bop.diputoledo.es/webEbop/DocGet?id=25103044%3B0&insert_number=5039&insert_year=2025",
    "published": "2025-10-17",
}
MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
ALIAS = {}  # printed name -> INE, checked by eye


def iso(cell):
    m = re.fullmatch(r"\s*(\d{1,2})\s+(?:de\s+)?([a-záéíóú]+)\s*", cell, re.I)
    assert m, cell
    return f"2026-{MES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}"


def rows(pdf):
    for page in pymupdf.open(pdf):
        for t in page.find_tables().tables:
            for r in t.extract():
                if len(r) != 3 or None in r or r[0] == "AYUNTAMIENTO":
                    continue
                yield [c.replace("\n", " ").strip() for c in r]


def sunday(d):
    return datetime.date.fromisoformat(d).weekday() == 6


def main(pdf):
    mt = Matcher()
    out, unmatched, last = {}, [], None
    for name, d1, d2 in rows(pdf):
        ds = sorted({iso(d1), iso(d2)})
        clean = name.lstrip("- ").strip()
        if clean != clean.upper():  # pedanía of the previous municipality
            assert last, name
            out[last].setdefault("nucleos", []).append({"name": clean, "holidays": [{"date": d, "name": ""} for d in ds]})
            continue
        ine = ALIAS.get(clean) or mt.match(clean, province=PROV)
        if not ine:
            unmatched.append(f"{clean}: {d1}, {d2}")
            last = None
            continue
        assert ine not in out, (clean, ine)
        out[ine] = {"holidays": [{"date": d, "name": ""} for d in ds]}
        last = ine
    for ine, v in out.items():
        notes = []
        if len(v["holidays"]) != 2:
            notes.append("The bulletin gives only one date.")
        suns = [h["date"] for h in v["holidays"] if sunday(h["date"])]
        if suns:
            notes.append("Published date(s) falling on a Sunday: " + ", ".join(suns) + ".")
        if v.get("nucleos"):
            notes.append("The bulletin lists separate days for local entities/pedanías: "
                         + ", ".join(n["name"] for n in v["nucleos"]) + ".")
        if notes:
            v["note"] = " ".join(notes)
    write_part("bop-toledo-2026", SOURCE, out, region="castilla-la-mancha", unmatched=unmatched)
    missing = [m["name"] for m in mt.munis if m["province_code"] == PROV and m["ine"] not in out]
    print("province municipalities not in the list:", len(missing), missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
