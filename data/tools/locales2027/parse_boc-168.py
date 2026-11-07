"""Canarias: BOC 168 (21-08-2026), Orden de 7 de agosto de 2026, annex with all 88
municipalities. Single-column text: 'NAME.' then lines 'D de mes: festivity.'"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import pymupdf

W = common.workdir_from_argv()
ID = "boc-168"
META = {
    "title": "Orden de 7 de agosto de 2026, por la que se determinan las fiestas locales propias de cada municipio de la Comunidad Autónoma de Canarias para el año 2027 (BOC nº 168, 21-08-2026, anuncio 3035)",
    "url": "https://sede.gobiernodecanarias.org/boc/boc-a-2026-168-3035.pdf",
    "published": "2026-08-21",
    "region": "canarias",
}
HEADER = re.compile(r"^(https://sede|boc-a-2026|Boletín Oficial de Canarias|Viernes 21 de agosto|\d{5}$)")
DATE = re.compile(r"^(\d{1,2}) de ([a-záéíóú]+):?\s*(.*)$")

ine = common.INE(W)

doc = pymupdf.open(os.path.join(W, "dl", ID, "boc.pdf"))
lines = []
started = False
for page in doc:
    for ln in page.get_text().splitlines():
        ln = ln.strip()
        if "RELACIÓN DE FIESTAS LOCALES PARA EL AÑO 2027" in ln:
            started = True
            continue
        if started and ln and not HEADER.match(ln):
            lines.append(ln)

munis = []
for ln in lines:
    m = DATE.match(ln)
    if m:
        munis[-1][1].append({"date": common.iso(int(m.group(1)), m.group(2)),
                             "name": m.group(3).rstrip(".").strip() or None})
    elif ln.isupper() and ln.endswith("."):
        munis.append([ln.rstrip("."), []])
    else:  # continuation of the previous festivity name
        h = munis[-1][1][-1]
        h["name"] = (h["name"] + " " + ln.rstrip(".")).strip()

rows = []
for name, hol in munis:
    # province: try both Canarian provinces
    code, how = None, "none"
    for cpro in ("35", "38"):
        c, h = ine.match(cpro, name, fuzzy=False)
        if c:
            code, how = c, h
            break
    rows.append({"name": name.title(), "cpro": code[:2] if code else None, "ine": code,
                 "match": how, "holidays": hol, "status": "boletin"})

assert len(rows) == 88, len(rows)
miss = common.coverage(ine, rows, ["35", "38"])
assert not miss, miss
SPOT = ("2026-11-07: annex read line by line with PyMuPDF (one column, 'D de mes: name'). "
        "Spot-checked against the PDF pages: Adeje (20 Jan San Sebastián, 11 Oct Santa Úrsula), "
        "El Paso (21 Aug, 3 Sep), Garachico (24 Jun, 26 Jul — printed without colon), "
        "Tuineje (second name runs onto a second line, batallas del Cuchillete y Tamasite), "
        "Santa Cruz de Tenerife, Las Palmas de Gran Canaria: all match.")
common.save_parsed(W, ID, META, rows, SPOT)
