"""País Vasco 2026 local holidays: Open Data Euskadi dataset "Calendario laboral de Euskadi para el 2026"
(Gobierno Vasco, Departamento de Economía, Trabajo y Empleo), CSV distribution.

Usage: python -E -P data/tools/loc2026_euskadi-2026.py <path/to/calendario_laboral_2026.csv> [--dry]

The dataset compiles the three territorial resolutions of the Basque Government's labour delegates
(BOB 138 of 21-07-2025 + BOB 148 of 06-08-2025 for Bizkaia, BOG for Gipuzkoa, BOTHA for Álava).
Each territory has one territory-wide local day (row whose municipality is the territory itself:
31 July San Ignacio in Bizkaia and Gipuzkoa, 28 April San Prudencio in Álava) plus one row per
municipality. A few municipalities have one row per district/concejo ("Ayala - Llanteno",
"Pasaia - Trintxerpe"): their own day differs by part, so only the territory day is kept in
"holidays" and the per-part days go into the note.
municipalitycode is the 3-digit INE/EUSTAT municipality code ("59.0" -> 01059); the name is matched
as a cross-check.
"""
import csv
import datetime as dt
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SID = "euskadi-2026"
SOURCE = {
    "title": "Calendario laboral de Euskadi para el 2026 (Open Data Euskadi, Gobierno Vasco): fiestas de la CAE, "
             "de los Territorios Históricos y de cada municipio, según los boletines oficiales",
    "url": "https://opendata.euskadi.eus/contenidos/ds_eventos/calendario_laboral_2026/opendata/calendario_laboral_2026.csv",
    "published": "2025-11-19",
}
TERR = {"Álava - Araba": "01", "Gipuzkoa": "20", "Bizkaia": "48"}
TNAME = {"01": "Álava", "20": "Gipuzkoa", "48": "Bizkaia"}
WD = {5: "Saturday", 6: "Sunday"}


def clean_name(s):
    s = (s or "").strip()
    return "" if s.lower() == "fiesta local" else s


def main():
    path = sys.argv[1]
    dry = "--dry" in sys.argv
    mt = Matcher()
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    terr_day = {}
    munis = defaultdict(list)  # ine -> [(part or None, date, name, es, eu)]
    unmatched = []
    for r in rows:
        terr = r["territory"].strip()
        es, eu = r["municipalityEs"].strip(), r["MunicipalityEu"].strip()
        d = dt.datetime.strptime(r["date"].strip(), "%d/%m/%Y").date()
        assert d.year == 2026, r
        name = clean_name(r["descripcionEs"])
        if terr not in TERR:
            assert terr == "Todos/denak", r
            continue
        prov = TERR[terr]
        if es == terr:
            terr_day[prov] = {"date": d.isoformat(), "name": name}
            continue
        code = r["municipalitycode"].strip()
        base_es, part = (es.split(" - ", 1) + [None])[:2]
        base_es, part = base_es.strip(), part.strip() if part else None
        ine = f"{prov}{int(float(code)):03d}" if code else None
        by_name = mt.match(base_es, province=prov) or mt.match(eu.split(" - ")[0].strip(), province=prov)
        if ine not in mt.by_ine:
            ine = None
        if ine and by_name and ine != by_name:
            print(f"CODE/NAME MISMATCH {es}: code {ine} vs name {by_name}")
            ine = None
        ine = ine or by_name
        if not ine:
            unmatched.append(f"{es} ({TNAME[prov]})")
            continue
        munis[ine].append((part, d.isoformat(), name, es, eu))

    out = {}
    for ine, items in sorted(munis.items()):
        prov = ine[:2]
        td = terr_day[prov]
        notes = []
        whole = [x for x in items if x[0] is None]
        parts = [x for x in items if x[0] is not None]
        if len(parts) == 1 and not whole:
            # one row only, labelled "Municipality - Locality" (Leaburu - Txarama, Iruña de Oca -
            # Nanclares de la Oca): it is the municipality's only row, so it is its own day
            notes.append(f"Dataset label: '{parts[0][3]}'.")
            whole, parts = [(None,) + parts[0][1:]], []
        hol = [dict(td)]
        if whole and not parts and len(whole) == 1:
            _, d, n, _, _ = whole[0]
            if d == td["date"]:
                notes.append("The municipal day equals the territory day.")
            else:
                hol.append({"date": d, "name": n})
        else:
            for _, d, n, _, _ in whole:
                if d != td["date"]:
                    hol.append({"date": d, "name": n})
            pl = "; ".join(f"{p}: {dt.date.fromisoformat(d).day}/{dt.date.fromisoformat(d).month}"
                           + (f" {n}" if n else "") for p, d, n, _, _ in sorted(parts, key=lambda x: x[1]))
            notes.append(f"The second local day differs by part of the municipality ({pl}); only the "
                         f"territory-wide day is listed for the whole municipality.")
        hol.sort(key=lambda h: h["date"])
        notes.insert(0, f"{dt.date.fromisoformat(td['date']).day}/{dt.date.fromisoformat(td['date']).month} "
                        f"({td['name']}) is the territory-wide local day of {TNAME[prov]}.")
        if ine == "48020":
            notes.append("28/8 per the modifying resolution of 4-8-2025 (BOB 148, 06-08-2025); the original "
                         "resolution (BOB 138) had 21/8.")
        for h in hol:
            d = dt.date.fromisoformat(h["date"])
            if d.weekday() in WD:
                notes.append(f"{d.day}/{d.month} falls on a {WD[d.weekday()]}; recorded as published.")
        out[ine] = {"holidays": hol, "note": " ".join(notes)}
        print(f"{ine} {mt.by_ine[ine]['name']:<32} " + " | ".join(f"{h['date']} {h['name']}" for h in hol)
              + ("   PARTS" if parts else ""))
    allc = {x["ine"]: x["name"] for x in mt.munis if x["province_code"] in TERR.values()}
    print("territory days:", terr_day)
    print("unmatched:", unmatched)
    print("missing from part:", [f"{k} {v}" for k, v in allc.items() if k not in out], f"({len(out)}/{len(allc)})")
    if not dry:
        write_part(SID, SOURCE, out, region="pais-vasco", unmatched=unmatched)


if __name__ == "__main__":
    main()
