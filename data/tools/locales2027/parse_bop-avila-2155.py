"""BOP Ávila 210 (29-X-2026), anuncio 2155/26: segunda relación COMPLEMENTARIA del calendario de
fiestas de carácter local 2027 (Oficina Territorial de Trabajo de Ávila, 26-X-2026).

It covers late proposals and "variaciones de los festivos locales inicialmente determinados", so
its rows replace those of BOP Ávila 129 (merge ranks the later bulletin first).
Two-column list (Localidad | Fiestas): an upper-case line is a municipality, the following lines
are its days in free text (a long text wraps onto a second line).
Usage: python -I parse_bop-avila-2155.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-avila-2155"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Ávila. Anuncio: segunda relación complementaria del calendario de fiestas de carácter local año 2027 (BOP Ávila núm. 210, 29-X-2026, anuncio 2155/26)",
    "url": "https://www.diputacionavila.es/bops/2026/29-10-2026/29-10-2026_215526.pdf",
    "published": "2026-10-29",
    "region": "castilla-y-leon",
}

SPOT = ("2026-11-27: all 16 rows re-read against the PDF text: ADANERO 13+14 Sep; LA ADRADA 3 Feb San Blas "
        "+ 6 Aug El Salvador; EL BARCO DE ÁVILA 12 Aug + 3 Sep; EL HORNILLO 26 Apr + 27 Dec; LANGA 2 Feb + "
        "17 May; MARTIHERRERO 1+2 Jul; PRADOSEGAR 16+17 Aug; TORNADIZOS DE ÁVILA 29 Sep + 1 Oct: all match.")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    doc = pymupdf.open(os.path.join(W, "dl", SID, "a.pdf"))
    text = doc[1].get_text()
    doc.close()
    body = text.split("\nFiestas\n", 1)[1]
    recs, cur = [], None
    for ln in body.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if ln == ln.upper() and not re.search(r"\d", ln):
            cur = [ln, ""]
            recs.append(cur)
        else:
            cur[1] += " " + ln
    out = []
    for name, fest in recs:
        pairs = cu.parse_free(cu.clean(fest))
        assert len(pairs) == 2, (name, fest, pairs)
        out.append({"muni": name, "locality": None, "holidays": cu.hol(pairs),
                    "note": f"Second complementary list (late proposals and changes to BOP Ávila 129); printed: «{cu.clean(fest)}»."})
    assert len(out) == 16, len(out)
    rows = cu.build_rows(ine, "05", out)
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
