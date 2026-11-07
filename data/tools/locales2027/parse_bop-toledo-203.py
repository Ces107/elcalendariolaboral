"""BOP Toledo nº 203 (22-10-2026), inserción 4840: fiestas locales 2027, all municipalities.

Table read with PyMuPDF find_tables() (3 columns: AYUNTAMIENTO | date | date).
UPPERCASE rows are municipalities; mixed-case rows are pedanías / entidades
locales with their own days, attached to the preceding municipality as a note.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-toledo-203"
META = {
    "title": "Delegación Provincial de Toledo, Consejería de Economía, Empresas y Empleo. Normas laborales. Fiestas locales 2027 (BOP Toledo núm. 203, 22-X-2026, inserción 4840)",
    "url": "https://bop.diputoledo.es/webEbop/DocGet?id=26104825%3B0&insert_number=4840&insert_year=2026",
    "published": "2026-10-22",
    "region": "castilla-la-mancha",
}
CPRO = "45"


SMALL = {"de", "del", "la", "las", "los", "el", "y", "con", "en", "a"}


def nice(upper):
    words = upper.title().split(" ")
    return " ".join(w.lower() if i and w.lower() in SMALL else w for i, w in enumerate(words))


def parse_date(cell):
    m = re.fullmatch(r"\s*(\d{1,2})\s+(?:de\s+)?([a-záéíóú]+)\s*", cell, re.I)
    if not m:
        raise ValueError(cell)
    return common.iso(int(m.group(1)), m.group(2))


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    doc = pymupdf.open(os.path.join(W, "dl", SID, "toledo.pdf"))
    raw = []
    for page in doc:
        for t in page.find_tables().tables:
            for r in t.extract():
                if r[0] == "AYUNTAMIENTO":
                    continue
                raw.append([c.replace("\n", " ").strip() for c in r])
    rows = []
    for name, d1, d2 in raw:
        dates = [parse_date(d1), parse_date(d2)]
        is_muni = name == name.upper()
        if is_muni:
            code, how = ine.match(CPRO, name)
            rows.append({"name": nice(name), "printed": name, "cpro": CPRO, "ine": code, "match": how,
                         "holidays": [{"date": d, "name": None} for d in dates],
                         "status": "boletin", "note": "", "_sub": []})
        else:
            rows[-1]["_sub"].append((name, dates))
    for r in rows:
        subs = r.pop("_sub")
        notes = ["The BOP annex gives dates only, without festivity names."]
        if subs:
            parts = []
            for n, ds in subs:
                parts.append(f"{n}: " + " and ".join(common_date_es(d) for d in ds))
            notes.append("The bulletin lists separate days for local entities of this municipality — "
                         + "; ".join(parts) + ".")
        r["note"] = " ".join(notes)
    miss = common.coverage(ine, rows, [CPRO])
    spot = SPOT
    common.save_parsed(W, SID, META, rows, spot, extra={"missing_from_list": [f"{c} {n}" for c, n in miss]})
    print("missing:", miss)


MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
       "septiembre", "octubre", "noviembre", "diciembre"]


def common_date_es(d):
    return f"{int(d[8:])} {MES[int(d[5:7]) - 1]}"


SPOT = ("2026-11-07: re-read with page.get_text() (plain line order, independent of find_tables) for "
        "Ajofrín (30 mar, 4 may), Lagartera (9 ago, 4 oct), Polán (28, 29 jun), Torrijos (19 may, 1 sep), "
        "Yuncos (13, 14 sep), Toledo (19, 29 mar); all match the parsed rows. Pedanías (mixed case in the "
        "PDF) kept as notes of the preceding municipality.")

if __name__ == "__main__":
    main()
