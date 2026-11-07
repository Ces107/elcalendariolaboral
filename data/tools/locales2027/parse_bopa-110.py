"""Asturias: BOPA 110 (10-06-2026), Resolución de 22 de mayo de 2026, all 78 concejos.
Ruled table: CONCEJO | fecha | festividad, one row per date (name cell only on the first)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import pymupdf

W = common.workdir_from_argv()
ID = "bopa-110"
META = {
    "title": "Resolución de 22 de mayo de 2026, de la Consejería de Ciencia, Industria y Empleo, por la que se aprueba el calendario de fiestas locales para el año 2027 en el ámbito del Principado de Asturias (BOPA núm. 110, 10-VI-2026, cód. 2026-04656)",
    "url": "https://miprincipado.asturias.es/bopa/2026/06/10/2026-04656.pdf",
    "published": "2026-06-10",
    "region": "asturias",
}
DATE = re.compile(r"(\d{1,2})\s+(?:de\s+)?([A-Za-záéíóú]+)")

ine = common.INE(W)
doc = pymupdf.open(os.path.join(W, "dl", ID, "bopa.pdf"))
munis = []
for page in doc:
    for t in page.find_tables().tables:
        for r in t.extract():
            name, date, fest = (r + [None, None, None])[:3]
            if name and name.strip():
                munis.append({"name": " ".join(name.split()), "raw": []})
            if date and date.strip():
                fest = (fest or "").replace("\xad\n", "").replace("\xad ", "").replace("\xad", "")
                munis[-1]["raw"].append((" ".join(date.split()), " ".join(fest.split())))

rows = []
for m in munis:
    hol, extra = [], []
    for d, f in m["raw"]:
        found = DATE.findall(d)
        if len(found) != 1:
            extra.append(f"{d}: {f}")
            continue
        hol.append({"date": common.iso(int(found[0][0]), found[0][1]), "name": f or None})
    code, how = ine.match("33", m["name"])
    row = {"name": m["name"], "cpro": "33", "ine": code, "match": how,
           "holidays": hol, "status": "boletin"}
    if extra:
        row["note"] = "Unparsed cells: " + " | ".join(extra)
    if len(hol) > 2:
        row["note"] = (f"The resolution lists {len(hol)} dates: some apply only to part of the "
                       "concejo (parishes/villages named in each festivity).")
    if any(not h["name"] for h in hol):
        row["note"] = (row.get("note", "") + " The resolution gives the dates without festivity names.").strip()
    rows.append(row)

miss = common.coverage(ine, rows, ["33"])
print("missing:", miss)
SPOT = ("2026-11-07: ruled table read with PyMuPDF find_tables() (concejo cell spans its two date rows). "
        "Spot-checked against the rendered page text: Allande (9 and 10 Sep, no names), Caravia "
        "('2 agosto' Santiago Apóstol, 6 Sep), Castropol (11 Oct, 7 Dec), Grado (23 Jul, 26 Jul), "
        "Gijón (9 Feb, 29 Jun), Oviedo (18 May, 21 Sep): all match.")
common.save_parsed(W, ID, META, rows, SPOT)
