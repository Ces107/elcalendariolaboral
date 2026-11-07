"""Murcia: BORM 171 (27-07-2026), all 45 municipalities. Table on page 3:
nº | MUNICIPIO | weekday | day | month | weekday | day | month (no festivity names)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import pymupdf
import datetime as dt

W = common.workdir_from_argv()
ID = "borm-171"
META = {
    "title": "Resolución de la Dirección General de Trabajo por la que se publica el calendario de fiestas laborales para el año 2027 (BORM nº 171, 27/07/2026, NPE A-270726-3718)",
    "url": "https://www.borm.es/services/anuncio/844400/pdf",
    "published": "2026-07-27",
    "region": "murcia",
}
WEEKDAYS = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]

ine = common.INE(W)
ine.add_manual("30", "FUENTE ALAMO", "30021")  # INE: Fuente Álamo de Murcia
doc = pymupdf.open(os.path.join(W, "dl", ID, "borm.pdf"))
rows = []
for page in doc:
    for t in page.find_tables().tables:
        for r in t.extract():
            # the regional-days table on page 2 is also numbered: skip it (4 columns)
            if len(r) != 8 or not r[0] or not str(r[0]).strip().isdigit():
                continue
            name = " ".join(r[1].split())
            hol = []
            for wd, d, m in ((r[2], r[3], r[4]), (r[5], r[6], r[7])):
                date = common.iso(int(d), m.strip())
                got = WEEKDAYS[dt.date.fromisoformat(date).weekday()]
                assert common.strip_accents(wd.strip()).lower() == got, (name, wd, date)
                hol.append({"date": date, "name": None})
            code, how = ine.match("30", name)
            note = "The resolution gives dates only, without festivity names."
            if any(dt.date.fromisoformat(h["date"]).weekday() == 5 for h in hol):
                note += " One of the two days falls on a Saturday, as published."
            rows.append({"name": name, "cpro": "30", "ine": code, "match": how,
                         "holidays": hol, "status": "boletin", "note": note})

assert len(rows) == 45, len(rows)
miss = common.coverage(ine, rows, ["30"])
assert not miss, miss
SPOT = ("2026-11-07: table read with PyMuPDF find_tables(); every row's printed weekday was checked "
        "against the computed 2027 weekday (45/45 agree). Spot-checked against the page text: "
        "Águilas (9 Feb, 30 Apr), Fuente Álamo (20 Jul, Sat 28 Aug), Lorca (8 Sep, 23 Nov), "
        "Ricote (20 Jan, 22 Jan), Torre Pacheco (7 Oct, 27 Dec), Yecla (13 Sep, 7 Dec): all match.")
common.save_parsed(W, ID, META, rows, SPOT)
