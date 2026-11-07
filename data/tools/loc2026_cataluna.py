"""Cataluña 2026 local holidays from the Generalitat open data (dataset b4eh-r8up, Departament d'Empresa i Treball),
which is the machine-readable version of Ordre EMT/208/2025 (DOGC 9565, 17-12-2025) incl. its later amendments.

Download (outside the repo):
    curl -o cat2026.json "https://analisi.transparenciacatalunya.cat/resource/b4eh-r8up.json?$limit=50000&any_calendari=2026"
Run:
    python -E -P data/tools/loc2026_cataluna.py cat2026.json

pedania "000" = the municipality itself; other codes are núcleos/agregats with their own two days (kept in "nucleos").
Municipalities that only appear by núcleo get no municipal dates, just the núcleos and a note.
The bulletin gives no holiday names, so name is "".
"""
import collections
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

SOURCE = {
    "title": "Ordre EMT/208/2025, d'11 de desembre, per la qual s'estableix el calendari de festes locals a Catalunya per a "
             "l'any 2026 (DOGC núm. 9565, de 17-12-2025), i modificacions; dades obertes del Departament d'Empresa i "
             "Treball (conjunt b4eh-r8up)",
    "url": "https://analisi.transparenciacatalunya.cat/Treball/Calendari-de-festes-locals-a-Catalunya/b4eh-r8up",
    "published": "2025-12-17",
    "bulletin_url": "https://dogc.gencat.cat/ca/document-del-dogc/?documentId=1032232",
}


def nucli_name(s):
    """'Casetes de la Gornal, les' -> 'Les Casetes de la Gornal'"""
    if ", " in s:
        body, art = s.rsplit(", ", 1)
        if art.lower() in ("el", "la", "els", "les", "l'", "es", "sa", "ses"):
            art = art[0].upper() + art[1:]
            return f"{art}{body}" if art.endswith("'") else f"{art} {body}"
    return s


def main(path):
    rows = json.loads(Path(path).read_text("utf-8"))
    mt = Matcher()
    by = collections.defaultdict(lambda: collections.defaultdict(lambda: {"name": None, "dates": set()}))
    for r in rows:
        assert r["any_calendari"] == "2026" and r["festiu"] == "Festiu local", r
        ine = r["codi_municipi_ine"]
        assert ine in mt.by_ine and mt.by_ine[ine]["region"] == "cataluna", ine
        n = by[ine][r["pedania"]]
        n["name"] = r["ajuntament_o_nucli_municipal"]
        n["dates"].add(r["data"][:10])
    out = {}
    for ine, peds in by.items():
        main_ = peds.get("000")
        rec = {"holidays": [{"date": d, "name": ""} for d in sorted(main_["dates"])] if main_ else []}
        nuc = [{"name": nucli_name(p["name"]), "holidays": [{"date": d, "name": ""} for d in sorted(p["dates"])]}
               for code, p in sorted(peds.items()) if code != "000"]
        if nuc:
            rec["nucleos"] = nuc
        notes = []
        if not main_:
            notes.append("The order sets the two days per núcleo (agregat), not for the whole municipality; see nucleos.")
        elif len(main_["dates"]) != 2:
            notes.append(f"The order lists {len(main_['dates'])} local holiday(s) for the municipality.")
        if nuc and main_:
            notes.append("Some núcleos (agregats) have their own days; see nucleos.")
        if notes:
            rec["note"] = " ".join(notes)
        out[ine] = rec
    missing = sorted(m["ine"] for m in mt.munis if m["region"] == "cataluna" and m["ine"] not in out)
    write_part("dogc-2026", SOURCE, out, region="cataluna",
               unmatched=[f"{c} {mt.by_ine[c]['name']}: not in the 2026 data (proposta no formulada)" for c in missing])


if __name__ == "__main__":
    main(sys.argv[1])
