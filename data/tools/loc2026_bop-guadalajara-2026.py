"""Guadalajara province 2026 local holidays: Anuncio de 20-11-2025 de la Delegación Provincial de la Consejería de Economía,
Empresas y Empleo de Guadalajara (BOP Guadalajara núm. 225, 24-11-2025), plus two modifications:
  - Anuncio de 9-2-2026 (BOP núm. 28, 11-02-2026): PEÑALÉN "donde dice 15 de agosto y 21 de octubre, debe decir
    15 de septiembre y 21 de octubre";
  - Anuncio de 14-5-2026 (BOP núm. 92, 18-05-2026): ALCOROCHES "donde dice 22 y 23 de agosto, debe decir 22 y 24".
The BOP search (boletin.dguadalajara.es, all years) shows no other 2026 modification.

Download (outside the repo) from https://boletin.dguadalajara.es/boletin/pdf/ :
    pdf2025_3507.pdf (base), pdf2026_360.pdf, pdf2026_1277.pdf
Run:
    python -E -P data/tools/loc2026_bop-guadalajara-2026.py pdf2025_3507.pdf

The base list is a two-column table printed as alternating lines (NAME / "15 MAYO Y 24 SEPTIEMBRE") in page text order;
dates only, no festivity names. The two modifications are one-line text changes, applied from MODS below (checked by eye).
Rows that are not INE municipalities (pedanías / entidades de ámbito territorial inferior) are listed as unmatched.
"""
import datetime
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "19"
PDF = "https://boletin.dguadalajara.es/boletin/pdf/"
SOURCE = {
    "title": "Anuncio de 20 de noviembre de 2025, de la Delegación Provincial de la Consejería de Economía, Empresas y "
             "Empleo de Guadalajara, por el que se da publicidad a la relación de fiestas de carácter local retribuidas y "
             "no recuperables para el año 2026 (BOP Guadalajara núm. 225, de 24-11-2025), modificado por los anuncios de "
             "9-2-2026 (BOP núm. 28, de 11-02-2026) y 14-5-2026 (BOP núm. 92, de 18-05-2026)",
    "url": PDF + "pdf2025_3507.pdf",
    "published": "2025-11-24",
    "modifications": [PDF + "pdf2026_360.pdf", PDF + "pdf2026_1277.pdf"],
}
MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
DATE_LINE = re.compile(r"^\d{1,2}\b.*\b(" + "|".join(MES) + r")\b", re.I)
MODS = {  # printed name: (dates, note)
    "PEÑALÉN": (["2026-09-15", "2026-10-21"],
              "Modified by anuncio of 9-2-2026 (BOP Guadalajara núm. 28, 11-02-2026) to 15 September and 21 October. "
              "That anuncio says it replaces '15 de agosto y 21 de octubre', but the 24-11-2025 list printed '7 y 15 "
              "agosto' for Peñalén; the modification's final dates are used."),
    "ALCOROCHES": (["2026-08-22", "2026-08-24"],
              "Modified by anuncio of 14-5-2026 (BOP Guadalajara núm. 92, 18-05-2026): 22 and 23 August replaced by "
              "22 and 24 August."),
}


def dates(txt):
    """'15 MAYO Y 24 SEPTIEMBRE' / '15 Y 19 JUNIO' / '29 AGOSTO, 14 SEPTIEMBRE Y 14 NOVIEMBRE' -> ISO list"""
    out, pending = [], []
    for num, mes in re.findall(r"(\d{1,2})(?:\s+(?:de\s+)?(" + "|".join(MES) + r"))?", txt.lower()):
        pending.append(int(num))
        if mes:
            out += [f"2026-{MES[mes]:02d}-{d:02d}" for d in pending]
            pending = []
    assert not pending and out, txt
    return sorted(set(out))


def entries(pdf):
    lines = []
    for page in pymupdf.open(pdf):
        lines += [ln.strip() for ln in page.get_text().splitlines() if ln.strip()]
    start = lines.index("Fiestas") + 1
    name = None
    for ln in lines[start:]:
        if ln.startswith(("BOP", "BOLETÍN OFICIAL", "B.O.P. DE", "Sede electrónica", "Cod. Veri")) or ln.isdigit():
            continue
        if DATE_LINE.match(ln):
            assert name, ln
            yield name, ln
            name = None
        else:
            assert name is None, (name, ln)
            name = ln


def main(pdf):
    mt = Matcher()
    out, unmatched = {}, []
    for name, txt in entries(pdf):
        ine = mt.match(name, province=PROV)
        if not ine:
            unmatched.append(f"{name}: {txt}")
            continue
        assert ine not in out, (name, ine)
        out[ine] = {"holidays": [{"date": d, "name": ""} for d in dates(txt)]}
    for name, (ds, note) in MODS.items():
        ine = mt.match(name, province=PROV)
        assert ine in out, name
        out[ine] = {"holidays": [{"date": d, "name": ""} for d in ds], "note": note}
    for ine, v in out.items():
        notes = [v["note"]] if v.get("note") else []
        n = len(v["holidays"])
        if n == 1:
            notes.append("The bulletin gives only one date.")
        elif n > 2:
            notes.append(f"The bulletin lists {n} dates; kept as published.")
        suns = [h["date"] for h in v["holidays"] if datetime.date.fromisoformat(h["date"]).weekday() == 6]
        if suns:
            notes.append("Published date(s) falling on a Sunday, kept as published: " + ", ".join(suns) + ".")
        if notes:
            v["note"] = " ".join(notes)
    write_part("bop-guadalajara-2026", SOURCE, out, region="castilla-la-mancha", unmatched=unmatched)
    missing = [m["name"] for m in mt.munis if m["province_code"] == PROV and m["ine"] not in out]
    print("province municipalities not written:", len(missing), missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
