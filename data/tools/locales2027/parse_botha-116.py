"""Álava: BOTHA 116 (09-10-2026). 28 April (San Prudencio) is the territory-wide local day
for every municipality; the annex gives each municipality's own day (Ayala: one day per
concejo/locality). Read by word coordinates: name x~157, locality x~198, date x 266-330,
festivity x>=335."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import pymupdf

W = common.workdir_from_argv()
ID = "botha-116"
META = {
    "title": "Resolución de 5 de octubre de 2026 del delegado territorial de Álava del Departamento de Economía, Trabajo y Empleo, que aprueba la determinación de las fiestas locales de Álava para el año 2027 (BOTHA nº 116, 09/10/2026, anuncio 2026-02851)",
    "url": "https://www.araba.eus/botha/Boletines/2026/116/2026_116_02851_C.pdf",
    "published": "2026-10-09",
    "region": "pais-vasco",
}
TERRITORY = {"date": "2027-04-28", "name": "San Prudencio"}

ine = common.INE(W)
ine.add_manual("01", "Salvatierra", "01051")  # INE: Agurain/Salvatierra
ine.add_manual("01", "Cripán", "01019")  # INE: Kripan
doc = pymupdf.open(os.path.join(W, "dl", ID, "botha.pdf"))

entries = []  # (level, name, date_text, fest)
for page in list(doc)[1:]:
    lines = {}
    for w in page.get_text("words"):
        lines.setdefault(round((w[1] + w[3]) / 2 / 3), []).append(w)
    started = False
    for k in sorted(lines):
        ws = sorted(lines[k], key=lambda w: w[0])
        text = " ".join(w[4] for w in ws)
        if "DÍAS DE FIESTA DE CARÁCTER LOCAL" in text:
            started = True
            continue
        if not started:
            continue
        if text.startswith("Vitoria-Gasteiz, 5 de octubre"):
            break
        if text.startswith(("www.araba.eus", "D.L.:")):  # page footer
            continue
        name = " ".join(w[4] for w in ws if w[0] < 260)
        date = " ".join(w[4] for w in ws if 260 <= w[0] < 335)
        fest = " ".join(w[4] for w in ws if w[0] >= 335)
        level = 1 if ws[0][0] > 190 else 0
        entries.append((level, name, date, fest))

# A municipality split by locality (Ayala) prints its name without a date, vertically
# centred in its block of indented localities: the whole contiguous block belongs to it.
munis = []
i = 0
while i < len(entries):
    level, name, date, fest = entries[i]
    if level == 0 and date:
        munis.append({"name": name, "date": date, "fest": fest, "localities": []})
        i += 1
        continue
    j = i
    block = []
    while j < len(entries) and (entries[j][0] == 1 or not entries[j][2]):
        block.append(entries[j])
        j += 1
    heads = [e for e in block if e[0] == 0]
    assert len(heads) == 1, block
    munis.append({"name": heads[0][1], "date": "", "fest": "",
                  "localities": [{"name": e[1], "date": e[2], "fest": e[3]} for e in block if e[0] == 1]})
    i = j


def hol(date, fest):
    # the festivity column does not start at the same x on every row: parse date+festivity as one string
    m = re.fullmatch(r"(\d{1,2})\s*de\s+(\w+)\s*(.*)", f"{date} {fest}".strip())
    if not m:
        return None
    return {"date": common.iso(int(m.group(1)), m.group(2)),
            "name": m.group(3).strip("() ") or None}


rows = []
for m in munis:
    code, how = ine.match("01", m["name"])
    row = {"name": m["name"], "cpro": "01", "ine": code, "match": how,
           "holidays": [dict(TERRITORY)], "status": "boletin",
           "note": "28 April (San Prudencio) is the territory-wide local day of Álava; the other day is the municipality's own."}
    if m["localities"]:
        row["localities"] = []
        for loc in m["localities"]:
            h = hol(loc["date"], loc["fest"])
            row["localities"].append({"name": loc["name"], "holidays": [h]})
        row["note"] = ("28 April (San Prudencio) is the territory-wide local day of Álava; the second day "
                       "differs by concejo/locality (see localities).")
    elif m["date"]:
        h = hol(m["date"], m["fest"])
        if h:
            row["holidays"].append(h)
        else:
            row["note"] = (f"28 April (San Prudencio) is the territory-wide local day of Álava. The resolution prints "
                           f"the municipality's own day as '{m['date']} {m['fest']}' without the day of the month; "
                           f"it is left out until a correction is published.")
    rows.append(row)

miss = common.coverage(ine, rows, ["01"])
print("missing:", miss)
SPOT = ("2026-11-07: annex read by word coordinates (name / locality / date / festivity columns). "
        "Spot-checked against the PDF: Alegría-Dulantzi (3 Feb San Blas), Ayala/Retes de Llanteno (22 Jul), "
        "Labastida (printed 'noviembre (2º día de Acción de Gracias)' with no day number), Vitoria-Gasteiz "
        "(5 Aug Virgen Blanca), Yécora (printed '20de agosto'), Zuia (29 Sep San Miguel): all match.")
common.save_parsed(W, ID, META, rows, SPOT)
