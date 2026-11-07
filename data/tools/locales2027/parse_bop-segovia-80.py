"""BOP Segovia 80 (6-VII-2026), RC-9105, pages 8-13: fiestas locales 2027 (acuerdo 30-VI-2026).

Annex LOCALIDAD | FECHA | FESTIVIDAD | FECHA | FESTIVIDAD without rules; dates as DD.MM.YYYY.
Words on one printed line: name x<210 ('- NAME' = locality), date1 210-258, fest1 258-365,
date2 365-412, fest2 >=412. Rows marked '*' carry the 2026 days because the council sent
nothing: they are NOT 2027 dates and are left out (listed in 'asterisk_2026').
Usage: python -I parse_bop-segovia-80.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-segovia-80"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Segovia. Fiestas locales 2027 (acuerdo de 30-VI-2026) (BOP Segovia núm. 80, 6-VII-2026, RC-9105)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/629/351/BOP%20Fiestas%20locales.pdf?blobheader=application%2Fpdf%3Bcharset%3DUTF-8&blobnocache=true",
    "published": "2026-07-06",
    "region": "castilla-y-leon",
}
X = [210, 258, 365, 412]
# bulletin abbreviations -> INE names (checked by eye)
MANUAL = {"FUENTESAUCO DE FDÑA.": "Fuentesaúco de Fuentidueña", "MARTÍN MUÑOZ POSADAS": "Martín Muñoz de las Posadas",
          "MONTEJO VEGA SERREZUELA": "Montejo de la Vega de la Serrezuela",
          "ALDEALENGUA DE STA. MARIA": "Aldealengua de Santa María", "FUENTE DE STA. CRUZ": "Fuente de Santa Cruz",
          "FUENTE EL OLMO DE FDÑA.": "Fuente el Olmo de Fuentidueña", "HONRRUBIA DE LA CUESTA": "Honrubia de la Cuesta",
          "S. CRISTÓBAL DE CUÉLLAR": "San Cristóbal de Cuéllar", "S. CRISTÓBAL DE LA VEGA": "San Cristóbal de la Vega",
          "S. CRISTÓBAL DE SEGOVIA": "San Cristóbal de Segovia", "SANTA M.ª LA REAL DE NIEVA": "Santa María la Real de Nieva",
          "SANTIUSTE S. JUAN BAUTISTA": "Santiuste de San Juan Bautista"}
# printed as a municipality but not one in the INE list; parent not confirmed -> kept out
UNASSIGNED = {"TEJARES"}
DATE = re.compile(r"^\d{1,2}\.\d{1,2}\.\d{4}$")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    by_name = {n: c for c, n in ine.by_code.items() if c[:2] == "40"}
    for printed, official in MANUAL.items():
        ine.add_manual("40", printed, by_name[official])
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    ents, started, odd = [], False, []
    for pn in range(8, 13):
        lines = {}
        for w in doc[pn].get_text("words"):
            lines.setdefault(round((w[1] + w[3]) / 2 / 2), []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            t = " ".join(w[4] for w in ws)
            if t.startswith("LOCALIDAD FECHA"):
                started = True
                continue
            if not started:
                continue
            if t.startswith("* AL NO HABER"):
                started = False
                continue
            if t.startswith(("Cód. Validación", "Verificación:", "Documento firmado", "Lunes, 6 de julio",
                             "www.dipsegovia", "Boletín Oficial", "BOPS", "Núm. 80", "Pág.")):
                continue
            cols = [[], [], [], [], []]
            for w in ws:
                cols[sum(w[0] >= x for x in X)].append(w[4])
            name, d1, f1, d2, f2 = (" ".join(c) for c in cols)
            if name:
                ents.append({"name": name, "cells": [[d1, f1], [d2, f2]]})
                if not (d1 or d2):
                    odd.append((pn + 1, t))
            else:  # wrapped festivity text (or a stray second line)
                if d1 or d2:
                    odd.append((pn + 1, t))
                    if d1:
                        ents[-1]["cells"][0][0] += " " + d1
                    if d2:
                        ents[-1]["cells"][1][0] += " " + d2
                ents[-1]["cells"][0][1] += (" " + f1) if f1 else ""
                ents[-1]["cells"][1][1] += (" " + f2) if f2 else ""
    doc.close()
    for o in odd:
        print("ODD LINE", o)
    recs, star, muni, unassigned = [], [], None, []
    for e in ents:
        name = e["name"]
        if name.endswith("*"):
            star.append(name.rstrip("*").strip())
            if not name.startswith("-"):
                muni = name.rstrip("*").strip()
            continue
        hs = []
        for d, f in e["cells"]:
            d = d.strip()
            if not d:
                continue
            if not DATE.match(d):
                raise SystemExit(f"BAD DATE {name}: {d!r}")
            iso, year = cu.numeric_date(d)
            if not iso:
                raise SystemExit(f"NOT 2027 {name}: {d!r}")
            hs.append({"date": iso, "name": cu.clean(f) or None})
        if name in UNASSIGNED:
            unassigned.append({"name": name, "holidays": hs})
        elif name.startswith("-"):
            recs.append({"muni": muni, "locality": cu.nice(name.lstrip("- ").strip()), "holidays": hs})
        else:
            muni = name
            recs.append({"muni": name, "locality": None, "holidays": hs, "note": ""})
    rows = cu.build_rows(ine, "40", recs)
    miss = common.coverage(ine, rows, ["40"])
    print("asterisk (2026 days shown):", len(star), star)
    print("not in bulletin:", len(miss), [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOT,
                       extra={"not_listed": [c for c, _ in miss], "asterisk_2026": star,
                              "unassigned_localities": unassigned})


SPOT = ("2026-11-07: annex read by word coordinates (five columns on one printed line). Re-read against the "
        "PDF text: ABADES 04.06 Romería + 10.08 San Lorenzo; ALCONADA DE MADERUELO* printed with 2026 dates "
        "(left out per the footnote); ALDEONTE and its locality Olmillo 24.05 + 29.11; ALDEHUELA DEL CODONAL "
        "16.08 + 17.08 San Roque; ZARZUELA DEL PINAR 03.05 + 14.09: all match.")

if __name__ == "__main__":
    main()
