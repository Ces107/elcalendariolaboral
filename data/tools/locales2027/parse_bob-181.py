"""Bizkaia: BOB 181 (22-09-2026). 31 July (San Ignacio de Loyola) for the whole territory,
plus one day per municipality: 'Name' line then '– DD de mes (festivity)'."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import pymupdf

W = common.workdir_from_argv()
ID = "bob-181"
META = {
    "title": "Resolución de 12 de septiembre de 2026, de la delegada territorial de Trabajo y Seguridad Social de Bizkaia, por la que se establece el Calendario de Fiestas Locales del Territorio Histórico de Bizkaia para el año 2027 (BOB nº 181, 22/09/2026, BOB-2026a181-(III-145))",
    "url": "https://www.bizkaia.eus/lehendakaritza/Bao_bob/2026/09/22/III-145_cas.pdf",
    "published": "2026-09-22",
    "region": "pais-vasco",
}
TERRITORY = {"date": "2027-07-31", "name": "San Ignacio de Loyola"}
NOISE = re.compile(r"^(cve:|BOLETÍN OFICIAL DE BIZKAIA|BOB$|Martes, 22 de septiembre|Núm\. 181|Pág\. \d|•$|=====)")
DAY = re.compile(r"^–\s*(\d{1,2}) de (\w+)\s*-?\s*(.*)$")

ine = common.INE(W)
ine.add_manual("48", "Valle de Karrantza", "48022")
ine.add_manual("48", "Abanto y Ciérvana", "48002")  # INE: Abanto y Ciérvana-Abanto Zierbena
ine.add_manual("48", "Trucíos", "48087")  # INE: Trucios-Turtzioz
doc = pymupdf.open(os.path.join(W, "dl", ID, "bob.pdf"))
text = "\n".join(p.get_text() for p in doc)
body = text.split("Para cada Municipio del Territorio Histórico de Bizkaia:")[1].split("En Bilbao, a 12 de septiembre")[0]
body = re.sub(r"[\x00-\x08\x0b-\x1f•]", " ", body)  # bullet glyphs come out as control chars
lines = [ln.strip() for ln in body.splitlines() if ln.strip() and not NOISE.match(ln.strip())]

rows = []
for ln in lines:
    m = DAY.match(ln)
    if m:
        name = m.group(3).strip()
        name = name[1:-1] if name.startswith("(") and name.endswith(")") else name
        rows[-1]["holidays"].append({"date": common.iso(int(m.group(1)), m.group(2)), "name": name or None})
    else:
        code, how = ine.match("48", ln)
        rows.append({"name": ln, "cpro": "48", "ine": code, "match": how,
                     "holidays": [dict(TERRITORY)], "status": "boletin",
                     "note": "31 July (San Ignacio de Loyola) is the local day for the whole of Bizkaia; in 2027 it falls on a Saturday. The other day is the municipality's own."})

for r in rows:
    assert len(r["holidays"]) == 2, r
miss = common.coverage(ine, rows, ["48"])
print("missing:", miss)
SPOT = ("2026-11-07: list read line by line with PyMuPDF (one column). Spot-checked against the PDF: "
        "Ajangiz (06 May, Día de la Ascensión), Bilbao (27 Aug, Viernes de la Semana Grande), "
        "Mallabia (10 Feb, Miércoles de Ceniza), Valle de Trápaga-Trapagaran ('06 de agosto-Transfiguración "
        "del Señor (Día de San Salvador)'), Usansolo (30 Nov San Andrés), Ziérbena (15 Oct): all match.")
common.save_parsed(W, ID, META, rows, SPOT)
