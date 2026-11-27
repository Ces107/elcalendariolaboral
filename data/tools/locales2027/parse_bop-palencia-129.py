"""BOP Palencia 129 (28-X-2026), page 3: ampliación de publicación de las fiestas locales 2027
(Oficina Territorial de Trabajo de Palencia, 26-X-2026), for councils whose days arrived after
BOP Palencia 83 (13-VII-2026), "con idénticos efectos jurídicos".

Annex MUNICIPIO | 1ª FIESTA | 2ª FIESTA without rules: name x<265 (municipality x~106,
locality x>=115), 1st date 265-400, 2nd date >=400; the left-margin signature strip (x<100) skipped.
Usage: python -I parse_bop-palencia-129.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-palencia-129"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Palencia. Ampliación de publicación de las fiestas locales a efectos laborales para el año 2027 en la provincia de Palencia (BOP Palencia núm. 129, 28-X-2026, anuncio 2809)",
    "url": "https://www.diputaciondepalencia.es/system/files/bop/2026/20261028-bop-129-Ordinario.pdf",
    "published": "2026-10-28",
    "region": "castilla-y-leon",
}
C1, C2 = 265, 400
SPOT = ("2026-11-27: all 15 municipalities and 4 localities re-read against the PDF text of page 3: "
        "BRAÑOSERA 13 Oct + 4 Dec; BUSTILLO DE LA VEGA 15 May + 29 Jun (Lagunilla 14+15 Sep); PÁRAMO DE "
        "BOEDO 3 Feb + 8 May; RENEDO DE LA VEGA 15 May + 11 Nov (Moslares, Santillán, Albalá); VALDERRÁBANO "
        "22 + 24 Nov; VILLASARRACINO 15 May + 8 Sep: all match.")


def cell(ws):
    t = " ".join(w[4] for w in ws).strip()
    m = re.fullmatch(r"(\d{1,2})\s+([a-záéíóú]+)", t)
    if not m:
        raise SystemExit(f"BAD CELL {t!r}")
    return common.iso(int(m.group(1)), m.group(2))


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    ine.add_manual("34", "LOMAS DE CAMPOS", "34096")  # INE name: Lomas
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    lines = {}
    for w in doc[2].get_text("words"):
        if w[0] < 100:
            continue
        lines.setdefault(round(w[3]), []).append(w)
    doc.close()
    recs, started, muni = [], False, None
    for k in sorted(lines):
        ws = sorted(lines[k], key=lambda w: w[0])
        t = " ".join(w[4] for w in ws)
        if t.startswith("MUNICIPIO"):
            started = True
            continue
        if not started:
            continue
        if t.strip() == "2809":
            break
        name = " ".join(w[4] for w in ws if w[0] < C1)
        hs = [{"date": cell([w for w in ws if C1 <= w[0] < C2]), "name": None},
              {"date": cell([w for w in ws if w[0] >= C2]), "name": None}]
        if ws[0][0] > 112:
            recs.append({"muni": muni, "locality": name, "holidays": hs})
        else:
            muni = name
            recs.append({"muni": name, "locality": None, "holidays": hs,
                         "note": "Late list (ampliación) to BOP Palencia 83; the annex gives dates only."})
    heads = [r for r in recs if not r["locality"]]
    assert len(heads) == 15 and len(recs) == 19, (len(heads), len(recs))
    rows = cu.build_rows(ine, "34", recs)
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
