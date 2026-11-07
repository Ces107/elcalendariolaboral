"""BOP Palencia 83 (13-VII-2026), pages 3-8: acuerdo de fiestas locales 2027.

Annex MUNICIPIO | 1ª FIESTA | 2ª FIESTA without rules. Words on the same printed line:
name x<265 (municipality x~120, locality x~140), 1st date 265-370, 2nd date >=370.
'no comunicado' = the council sent no date (left out; listed in 'not_communicated').
Usage: python -I parse_bop-palencia-83.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-palencia-83"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Palencia. Acuerdo de determinación de las fiestas locales, a efectos laborales, en los municipios de la provincia (año 2027) (BOP Palencia núm. 83, 13-VII-2026)",
    "url": "https://www.diputaciondepalencia.es/system/files/bop/2026/20260713-bop-83-Ordinario.pdf",
    "published": "2026-07-13",
    "region": "castilla-y-leon",
}
C1, C2 = 265, 370


def cell(ws):
    t = " ".join(w[4] for w in ws).strip()
    if not t or t == "no comunicado":
        return None, t
    m = re.fullmatch(r"(\d{1,2})\s+([a-záéíóú]+)", t)
    if not m:
        raise SystemExit(f"BAD CELL {t!r}")
    return common.iso(int(m.group(1)), m.group(2)), t


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    recs, nocom, started, done, muni = [], [], False, False, None
    for pn in range(2, 8):
        lines = {}
        for w in doc[pn].get_text("words"):
            if w[0] < 100:  # the rotated 'Firmado electrónicamente...' strip in the left margin
                continue
            lines.setdefault(round(w[3]), []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            t = " ".join(w[4] for w in ws)
            if t.startswith("MUNICIPIO") and "FIESTA" in t:
                started = True
                continue
            if not started or done:
                continue
            if t.strip() == "1814":  # the announcement number closes the annex
                done = True
                continue
            if ws[0][0] > C1 or t.startswith(("BOP de Palencia", "Lunes, 13 de julio", "Firmado", "http://csv",
                                             "Código de Verificación")) or re.fullmatch(r"\d+", t):
                continue
            name = " ".join(w[4] for w in ws if w[0] < C1)
            d1, t1 = cell([w for w in ws if C1 <= w[0] < C2])
            d2, t2 = cell([w for w in ws if w[0] >= C2])
            is_loc = ws[0][0] > 130
            hs = [{"date": d, "name": None} for d in (d1, d2) if d]
            if not is_loc:
                muni = name
            if not hs:
                nocom.append(name if not is_loc else f"{muni} / {name}")
                continue
            note = "The annex gives dates only, without festivity names."
            if len(hs) == 1:
                note += " The other day is printed as 'no comunicado' (not communicated by the council)."
            if is_loc:
                recs.append({"muni": muni, "locality": name, "holidays": hs})
            else:
                recs.append({"muni": name, "locality": None, "holidays": hs, "note": note})
    doc.close()
    rows = cu.build_rows(ine, "34", recs)
    miss = common.coverage(ine, rows, ["34"])
    print("no comunicado:", len(nocom), nocom)
    print("not in bulletin:", len(miss), [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOT,
                       extra={"not_listed": [c for c, _ in miss], "not_communicated": nocom})


SPOT = ("2026-11-07: annex read by word coordinates (three columns on the same printed line). "
        "Re-read against the PDF text: ABARCA DE CAMPOS 20 Jan + 14 Aug; AMUSCO 28 + 29 Jun (Valdespina "
        "24 Jun + 3 Aug); CASTRILLO DE ONIELO 'no comunicado' + 22 May; CEVICO DE LA TORRE '07 mayo' + 11 Nov; "
        "VILLATURDE 19 Mar + 14 Aug with 3 localities; VILLOVIECO 3 May + 9 Jul: all match.")

if __name__ == "__main__":
    main()
