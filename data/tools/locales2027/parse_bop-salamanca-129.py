"""BOP Salamanca 129 (8-VII-2026): fiestas locales 2027, Oficina Territorial de Trabajo.

Annex 'ENTIDAD LOCAL | FECHA' without rules: name at x~105, dates at x>=330 on the same
printed line. Read by span coordinates. Usage: python -I parse_bop-salamanca-129.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-salamanca-129"
META = {
    "title": "Acuerdo de 1 de julio de 2026, de la Oficina Territorial de Trabajo de Salamanca, para la determinación de las fiestas locales, a efectos laborales, en los municipios de esta provincia para el año 2027 (BOP Salamanca núm. 129, 8-VII-2026)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/686/528/BOP-SA-20260708-001.pdf?blobheader=application%2Fpdf%3Bcharset%3DUTF-8&blobnocache=true",
    "published": "2026-07-08",
    "region": "castilla-y-leon",
}
SPLIT = 330
# villages printed as if they were municipalities (not in the INE list): Barceíno is a
# pedanía of Barceo, Escuernavacas a village of Moronta
LOCALITY_OF = {"BARCEINO": "BARCEO", "ESCUERNAVACAS": "MORONTA"}


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    by_name = {n: c for c, n in ine.by_code.items() if c[:2] == "37"}
    for printed, official in [("CRISTÓBAL DE LA SIERRA", "Cristóbal"), ("MASUECO DE LA RIBERA", "Masueco"),
                              ("BÓVEDA DE RIO ALMAR", "Bóveda del Río Almar"),
                              ("CASTILLEJO MARTIN VIEJO", "Castillejo de Martín Viejo"),
                              ("PALACIOS RUBIOS", "Palaciosrubios"),
                              ("VENTOSA DE RÍO ALMAR", "Ventosa del Río Almar")]:
        ine.add_manual("37", printed, by_name[official])
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    recs, started = [], False
    for pn in range(1, len(doc)):
        for y, ss in cu.lines(cu.spans(doc, pn)):
            t = cu.text_of(ss)
            if t.startswith("ENTIDAD LOCAL"):
                started = True
                continue
            if not started or t.startswith(("CVE:", "https://sede", "N.º 129", "Pág.")):
                continue
            if not t:
                continue
            # date spans start anywhere from x~345 to ~385 (right-aligned column): split on the first digit
            m = re.match(r"^(\D+?)\s+(\d.*)$", t)
            if not m or ss[0][0] > SPLIT:
                raise SystemExit(f"BROKEN LINE p{pn + 1}: {t!r}")
            L, R = m.group(1), m.group(2)
            hs = cu.hol([(d, None) for d, _ in cu.parse_free(R)])
            if not hs:
                raise SystemExit(f"NO DATES p{pn + 1}: {t!r}")
            if L in LOCALITY_OF:
                recs.append({"muni": LOCALITY_OF[L], "locality": cu.nice(L), "holidays": hs})
            else:
                recs.append({"muni": L, "locality": None, "holidays": hs,
                             "note": "The annex gives dates only, without festivity names."})
    doc.close()
    rows = cu.build_rows(ine, "37", recs)
    miss = common.coverage(ine, rows, ["37"])
    print("not in bulletin:", len(miss), [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOT, extra={"not_listed": [c for c, _ in miss]})


SPOT = ("2026-11-07: annex read by span coordinates (name x<330, dates x>=330 on the same line). "
        "Re-read against the PDF text: ABUSEJO 23 Jan + 3 May; BÉJAR 7 + 8 Sep; SALAMANCA 12 Jun + 8 Sep; "
        "VILLARES DE LA REINA 31 May + 31 Dec; ZARAPICOS printed '27 de julio y 20 de mayo' (out of order); "
        "ZORITA DE LA FRONTERA 28 + 29 Sep: all match.")

if __name__ == "__main__":
    main()
