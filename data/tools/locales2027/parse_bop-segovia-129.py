"""BOP Segovia 129 (28-X-2026), RC-13938, page 6: second list of fiestas locales 2027 of the
Oficina Territorial de Trabajo de Segovia (acuerdo 23-X-2026), for councils whose proposals came
after BOP Segovia 80 (incl. most of the '*' towns printed there with their 2026 days).
Same five-column layout as BOP 80 (read by word coordinates).
Usage: python -I parse_bop-segovia-129.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-segovia-129"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Segovia. Fiestas locales 2027 (acuerdo de 23-X-2026) (BOP Segovia núm. 129, 28-X-2026, RC-13938)",
    "url": "https://www.dipsegovia.es/documents/39512/de568f33-0970-6e5a-59ce-739a904cc74c",
    "published": "2026-10-28",
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
# printed as municipalities but not in the INE list (localities); parent not printed -> kept out
UNASSIGNED = {"LA SALCEDA", "MATA DE QUINTANAR", "VALLE DE SAN PEDRO"}  # localities, parent not printed
DATE = re.compile(r"^\d{1,2}\.\d{1,2}\.\d{4}$")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    by_name = {n: c for c, n in ine.by_code.items() if c[:2] == "40"}
    for printed, official in MANUAL.items():
        ine.add_manual("40", printed, by_name[official])
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    ents, started, odd = [], False, []
    for pn in range(5, 6):
        lines = {}
        for w in doc[pn].get_text("words"):
            if w[0] >= 545:  # vertical signature footer in the right margin ("Documento firmado ... Página")
                continue
            lines.setdefault(round((w[1] + w[3]) / 2 / 2), []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            t = " ".join(w[4] for w in ws)
            if t.startswith("LOCALIDAD FECHA"):
                started = True
                continue
            if not started:
                continue
            if t.startswith(("* AL NO HABER", "RE-")):
                started = False
                continue
            if t.startswith(("Cód. Validación", "Verificación:", "Documento firmado", "Miércoles, 28 de octubre",
                             "www.dipsegovia", "Boletín Oficial", "BOPS", "Núm. 129", "Pág.")):
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
            recs.append({"muni": name, "locality": None, "holidays": hs, "note": "Second list (BOP Segovia 129) after BOP Segovia 80."})
    rows = cu.build_rows(ine, "40", recs)
    print("asterisk (2026 days shown):", len(star), star)
    common.save_parsed(W, SID, META, rows, SPOT,
                       extra={"unassigned_localities": unassigned})


SPOT = ("2026-11-27: annex re-read against pdftotext -layout of page 6, independently of the parser: "
        "ALCONADA DE MADERUELO 21.06 San Luis + 15.11 San Martín; ALDEONTE and Olmillo 20.09 + 25.10; "
        "CUÉLLAR 05.04 + 01.10 'Fiestas Locales'; RIAZA 10.05 + 08.09; VALVERDE DEL MAJANO 29.06 + 25.10: all match.")

if __name__ == "__main__":
    main()
