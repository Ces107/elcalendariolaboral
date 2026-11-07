"""Ciudad Real province 2026 local holidays: Delegación Provincial de Economía, Empresas y Empleo de Ciudad Real,
"Fiestas locales para el año 2026" (BOP Ciudad Real núm. 199, 15-10-2025, anuncio 3563), plus three later resolutions:
  - BOP 214 (05-11-2025, anuncio 3798): Fontanarejo communicated out of time (30-abr, 07-nov);
  - BOP 216 (07-11-2025, anuncio 3852): Carrizosa corrected (6 April -> 5 June: 04-may, 05-jun);
  - BOP 217 (10-11-2025, anuncio 3873): Fontanarejo corrected (7 Nov -> 7 Dec: 30-abr, 07-dic).
The BOP search (bop.dipucr.es/buscador, 2025-09 .. 2026-11) shows no other 2026 notices.

Download (outside the repo), https://se1.dipucr.es:4443/SIGEM_BuscadorDocsWeb/getDocument.do?entidad=005&doc=<n>
for n = 7160514 (base), 7201737, 7208549, 7211839.
Run (base first, then the corrections in order; later rows override):
    python -E -P data/tools/loc2026_bop-ciudad-real-2026.py cr_7160514.pdf cr_7201737.pdf cr_7208549.pdf cr_7211839.pdf

Tables read with PyMuPDF find_tables(): annex rows are (nº | MUNICIPIO | dd/mmm | dd/mmm), correction rows
(MUNICIPIO | dd-mmm | dd-mmm). Dates only, no festivity names.
"""
import datetime
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "13"
DOC = "https://se1.dipucr.es:4443/SIGEM_BuscadorDocsWeb/getDocument.do?entidad=005&doc="
SOURCE = {
    "title": "Delegación Provincial de Economía, Empresas y Empleo de Ciudad Real. Fiestas locales para el año 2026 "
             "(BOP Ciudad Real núm. 199, de 15-10-2025, anuncio 3563), with the resolutions of BOP núm. 214 (05-11-2025, "
             "Fontanarejo), 216 (07-11-2025, Carrizosa) and 217 (10-11-2025, Fontanarejo)",
    "url": DOC + "7160514",
    "published": "2025-10-15",
    "modifications": [DOC + "7201737", DOC + "7208549", DOC + "7211839"],
}
MES = {m: i for i, m in enumerate(["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"], 1)}
CORRECTED = {"13032": "Corrected by BOP Ciudad Real núm. 216 (07-11-2025): 6 April replaced by 5 June."}
NOTE_FONTANAREJO = ("Not in the 15-10-2025 annex (blank row); communicated out of time in BOP núm. 214 (05-11-2025) as "
                    "30 April and 7 November, then corrected in BOP núm. 217 (10-11-2025) to 30 April and 7 December.")


def iso(cell):
    m = re.fullmatch(r"\s*(\d{1,2})[/-]([a-z]{3})\s*", cell.lower())
    assert m, cell
    return f"2026-{MES[m.group(2)]:02d}-{int(m.group(1)):02d}"


def rows(pdf):
    for page in pymupdf.open(pdf):
        for t in page.find_tables().tables:
            for r in t.extract():
                r = [(c or "").replace("\n", " ").strip() for c in r]
                if len(r) == 4 and r[0].isdigit():
                    r = r[1:]
                if len(r) == 3 and r[0] and r[0] == r[0].upper() and not r[0].startswith("S e d e"):
                    yield r


def main(*pdfs):
    mt = Matcher()
    out, unmatched, blank = {}, [], []
    for pdf in pdfs:
        for name, d1, d2 in rows(pdf):
            ine = mt.match(name, province=PROV)
            if not ine:
                unmatched.append(f"{name}: {d1}, {d2}")
                continue
            if not d1 and not d2:
                blank.append(name)
                continue
            out[ine] = {"holidays": [{"date": d, "name": ""} for d in sorted({iso(d1), iso(d2)})]}
    for ine, v in out.items():
        notes = []
        if ine in CORRECTED:
            notes.append(CORRECTED[ine])
        if ine == "13041":
            notes.append(NOTE_FONTANAREJO)
        suns = [h["date"] for h in v["holidays"] if datetime.date.fromisoformat(h["date"]).weekday() == 6]
        if suns:
            notes.append("Published date(s) falling on a Sunday: " + ", ".join(suns) + ".")
        if len(v["holidays"]) != 2:
            notes.append("The bulletin gives only one date.")
        if notes:
            v["note"] = " ".join(notes)
    write_part("bop-ciudad-real-2026", SOURCE, out, region="castilla-la-mancha", unmatched=unmatched)
    missing = [m["name"] for m in mt.munis if m["province_code"] == PROV and m["ine"] not in out]
    print("blank rows:", blank, "| province municipalities not written:", len(missing), missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
