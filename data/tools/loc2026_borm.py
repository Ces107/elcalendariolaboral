"""Región de Murcia 2026 local holidays: Resolución de la Dirección General de Trabajo por la que se publica el
calendario de fiestas laborales para el año 2026 (BORM núm. 163, 17-07-2025, anuncio 3546).

Download (outside the repo): https://www.borm.es/services/anuncio/ano/2025/numero/3546/pdf?id=837607
Run: python -E -P data/tools/loc2026_borm.py borm3546.pdf

The table has shaded alternate rows and pdftotext -layout shifts them; rows are rebuilt from word coordinates.
Each date is printed with its weekday; a weekday that does not match the date is reported in "note".
"""
import datetime as dt
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
SOURCE = {
    "title": "Resolución de la Dirección General de Trabajo por la que se publica el calendario de fiestas laborales "
             "para el año 2026 (BORM núm. 163, de 17-07-2025, anuncio 3546)",
    "url": "https://www.borm.es/services/anuncio/ano/2025/numero/3546/pdf?id=837607",
    "published": "2025-07-17",
}
ROW = re.compile(r"^(\d{1,2}) (.+?)\.? (" + "|".join(DIAS) + r") (\d{1,2}) (\w+) (" + "|".join(DIAS) + r") (\d{1,2}) (\w+)$",
                 re.I)


def rows(pdf):
    for page in pymupdf.open(pdf):
        lines = []
        for w in sorted(page.get_text("words"), key=lambda w: (w[3], w[0])):
            if lines and abs(lines[-1][0] - w[3]) < 3:
                lines[-1][1].append(w)
            else:
                lines.append([w[3], [w]])
        for _, ws in lines:
            yield " ".join(w[4] for w in sorted(ws, key=lambda w: w[0]))


def main(pdf):
    mt = Matcher()
    out, unmatched, n = {}, [], 0
    for ln in rows(pdf):
        m = ROW.match(ln)
        if not m:
            continue
        n += 1
        num, name = m.group(1), m.group(2).rstrip(".")
        hs, notes = [], []
        for wd, d, mes in (m.group(3, 4, 5), m.group(6, 7, 8)):
            day = dt.date(2026, MES[mes.lower()], int(d))
            hs.append({"date": day.isoformat(), "name": ""})
            if DIAS[day.weekday()] != wd.lower():
                notes.append(f"The bulletin prints {wd} {d} {mes}, but {day.isoformat()} is a {DIAS[day.weekday()]}.")
        ine = {"FUENTE ÁLAMO": "30021"}.get(name) or mt.match(name.title(), province="30") or mt.match(name, province="30")
        if not ine:
            unmatched.append(ln)
            continue
        rec = {"holidays": sorted(hs, key=lambda h: h["date"])}
        if notes:
            rec["note"] = " ".join(notes)
        out[ine] = rec
    assert n == 45, n
    write_part("borm-2026", SOURCE, out, region="murcia", unmatched=unmatched)


if __name__ == "__main__":
    main(sys.argv[1])
