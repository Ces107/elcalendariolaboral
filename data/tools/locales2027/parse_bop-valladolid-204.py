"""BOP Valladolid 2026/204 (23-X-2026), BOPVA-A-2026-03085: Resolución de 16-X-2026 de la Oficina
Territorial de Trabajo de Valladolid que amplía la determinación de fiestas locales 2027 (councils
whose days arrived after BOP 2026/129).

Annex Ayuntamiento | 1ª Fiesta | 2ª Fiesta, one cell per text line (name, date, date).
'No comunicada' = the council sent no second day (kept as a single-date row).
Usage: python -I parse_bop-valladolid-204.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-valladolid-204"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Valladolid. Resolución de 16 de octubre de 2026 para la determinación de las fiestas locales, a efectos laborales, en los municipios de la provincia de Valladolid (ampliación 2027) (BOP Valladolid núm. 2026/204, 23-X-2026, BOPVA-A-2026-03085)",
    "url": "https://bop.sede.diputaciondevalladolid.es/boletines/2026/octubre/23/BOPVA-A-2026-03085.pdf",
    "published": "2026-10-23",
    "region": "castilla-y-leon",
}
SPOT = ("2026-11-27: all 21 rows re-read against the PDF text of page 31: CERVILLEGO DE LA CRUZ 3 May + 30 Aug; "
        "OLMEDO 29 Sep + 11 Oct; SAELICES DE MAYORGA 16 Jul + 'No comunicada'; VALLADOLID 13 May + 8 Sep "
        "(same as the city's own page); VILLABRÁGIMA 3 + 4 May; VILLAVERDE DE MEDINA 10 + 11 May: all match.")
DATE = re.compile(r"^(\d{1,2}) de ([a-záéíóú]+)$")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    doc = pymupdf.open(os.path.join(W, "dl", SID, "a.pdf"))
    text = doc[1].get_text()
    doc.close()
    body = text.split("2ª Fiesta", 1)[1].split("ID DOCUMENTO", 1)[0]
    cells = [c.strip() for c in body.splitlines() if c.strip()]
    assert len(cells) % 3 == 0, len(cells)
    recs = []
    for i in range(0, len(cells), 3):
        name, a, b = cells[i:i + 3]
        hs, note = [], "Late list (ampliación) to BOP Valladolid 2026/129; the annex gives dates only."
        for c in (a, b):
            m = DATE.match(c)
            if m:
                hs.append({"date": common.iso(int(m.group(1)), m.group(2)), "name": None})
            elif c == "No comunicada":
                note += " The other day is printed as 'No comunicada'."
            else:
                raise SystemExit(f"BAD CELL {name}: {c!r}")
        recs.append({"muni": name, "locality": None, "holidays": hs, "note": note})
    assert len(recs) == 21, len(recs)
    rows = cu.build_rows(ine, "47", recs)
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
