"""BOP Ávila 129 (8-VII-2026), anuncio 1448/26: calendario de fiestas de carácter local 2027.

Ruled two-column table (LOCALIDAD | FIESTAS), cells vertically centred. Row bands
from the table's horizontal rules; text by span coordinates (column split x=245).
Usage: python -I parse_bop-avila-129.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-avila-129"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Ávila. Anuncio: calendario de fiestas de carácter local año 2027 (BOP Ávila núm. 129, 8-VII-2026, anuncio 1448/26)",
    "url": "https://www.diputacionavila.es/bops/2026/08-07-2026/08-07-2026_144826.pdf",
    "published": "2026-07-08",
    "region": "castilla-y-leon",
}
SPLIT = 245


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    ine.add_manual("05", "NAVALMORAL DE LA SIERRA", "05158")  # INE name: Navalmoral
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    # Row bands come from the table's horizontal rules (page drawings); every printed
    # line is assigned to the band containing its centre and split at x=SPLIT.
    recs = []
    for pn in range(1, len(doc)):
        page = doc[pn]
        ys = set()
        for dr in page.get_drawings():
            for it in dr["items"]:
                if it[0] == "l" and abs(it[1].y - it[2].y) < 1 and abs(it[2].x - it[1].x) > 200:
                    ys.add(round(it[1].y, 1))
                elif it[0] == "re" and it[1].height < 2 and it[1].width > 200:
                    ys.add(round(it[1].y0, 1))
        ys = sorted(ys)
        bands = [(a, b) for a, b in zip(ys, ys[1:]) if b - a > 5]
        for a, b in bands:
            L, R = [], []
            for y, ss in cu.lines(cu.spans(doc, pn)):
                yc = (ss[0][1] + ss[0][3]) / 2
                if a < yc < b:
                    L += [s for s in ss if s[0] < SPLIT]
                    R += [s for s in ss if s[0] >= SPLIT]
            L, R = cu.text_of(L), cu.text_of(R)
            if not L or L.upper() == "LOCALIDAD":
                continue
            recs.append((pn, cu.clean(L), cu.clean(R)))
    out = []
    for pn, left, right in recs:
        m = re.match(r"^(.*?\d{1,2} de [a-záéíóú]+(?: y \d{1,2} de [a-záéíóú]+)?)\s*\.?\s*(.*)$", right)
        if not m:
            print("UNPARSED", pn, left, "|", right)
            continue
        dates = [d for d, _ in cu.parse_free(m.group(1))]
        names_txt = cu.clean(m.group(2))
        names = [cu.clean(x) for x in names_txt.split(" y ")] if names_txt else []
        note = ""
        if names and len(names) == len(dates):
            hs = [{"date": d, "name": cu.nice(n)} for d, n in zip(dates, names)]
        else:
            hs = [{"date": d, "name": None} for d in dates]
            if names_txt:
                note = f"Festivity names as printed: {names_txt}."
        name = re.sub(r"\s+", " ", left)
        loc = None
        if "(ANEJO)" in name.upper() or " - " in name:
            muni, loc = [x.strip() for x in re.sub(r"\(ANEJO\)", "", name, flags=re.I).split(" - ", 1)]
        else:
            m2 = re.match(r"^(GRANDES Y SAN MARTÍN) \((.+)\)$", name)
            muni, loc = (m2.group(1), m2.group(2)) if m2 else (name, None)
        out.append({"muni": muni, "locality": cu.nice(loc) if loc else None, "holidays": hs, "note": note})
    rows = cu.build_rows(ine, "05", out)
    for r in rows:
        if len(r["holidays"]) != 2:
            print("COUNT", r["name"], r["holidays"], r["note"][:150])
    miss = common.coverage(ine, rows, ["05"])
    print("not in bulletin:", len(miss), [n for _, n in miss])
    spot = SPOT
    common.save_parsed(W, SID, META, rows, spot, extra={"not_listed": [c for c, _ in miss]})


SPOT = ("Re-read against the PDF page images/text (pages 2-8): ALDEASECA 2-VII y 29-IX; "
        "BRABOS 10-VIII y 6-VIII (printed in that order); NAVALUENGA, PIEDRAHÍTA, SOTILLO DE LA ADRADA "
        "and VITA (20-I y 2-VII) match the parser output.")

if __name__ == "__main__":
    main()
