"""BOP Salamanca 206 (23-X-2026), CVE BOP-SA-20261023-001: Acuerdo complementario de 19-X-2026 de la
Oficina Territorial de Trabajo de Salamanca, fiestas locales 2027 for councils whose agreement arrived
after BOP Salamanca 129 (8-VII-2026).

The annex uses subset fonts without a usable ToUnicode map (text extraction gives control codes), so
its 32 rows were transcribed from a 200 dpi render. Cross-check: the day numbers and months of each row
are also read from the PDF as glyph codes; one glyph->character map must explain all 32 transcribed
rows at once (a bijection), so any misread digit or month would break it.
Usage: python -I parse_bop-salamanca-206.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-salamanca-206"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Salamanca. Acuerdo complementario de 19 de octubre de 2026 para la determinación de las fiestas locales del año 2027 (BOP Salamanca núm. 206, 23-X-2026, CVE BOP-SA-20261023-001)",
    "url": "https://sede.diputaciondesalamanca.gob.es/documentacion/bop/2026/20261023/BOP-SA-20261023-001.pdf",
    "published": "2026-10-23",
    "region": "castilla-y-leon",
}

ANNEX = [
    ("AHIGAL DE LOS ACEITEROS", "18 de junio y 13 de agosto"),
    ("ALDEA DEL OBISPO", "20 de enero y 26 de julio"),
    ("CESPEDOSA DE TORMES", "8 de septiembre y 9 de septiembre"),
    ("DOÑINOS DE SALAMANCA", "26 de abril y 9 de agosto"),
    ("GALLEGOS DE ARGAÑÁN", "26 de abril y 27 de abril"),
    ("LAGUNILLA", "14 de septiembre y 15 de septiembre"),
    ("LEDESMA", "27 de mayo y 31 de mayo"),
    ("MARTIAGO", "13 de septiembre y 14 de septiembre"),
    ("MONTERRUBIO DE ARMUÑA", "12 de junio y 8 de septiembre"),
    ("NAVALMORAL DE BÉJAR", "23 de agosto y 24 de agosto"),
    ("PEÑAPARDA", "18 de junio y 21 de junio"),
    ("PEÑARANDILLA", "31 de mayo y 5 de febrero"),
    ("PUEBLA DE SAN MEDEL", "2 de julio y 27 de agosto"),
    ("REDONDA (LA)", "3 de mayo y 13 de agosto"),
    ("RETORTILLO", "3 de febrero y 3 de junio"),
    ("RINCONADA DE LA SIERRA (LA)", "2 de febrero y 26 de julio"),
    ("ROBLIZA DE COJOS", "23 de enero y 6 de agosto"),
    ("ROLLÁN", "20 de enero y 10 de agosto"),
    ("SAGRADA (LA)", "15 de mayo y 29 de mayo"),
    ("SAHÚGO (EL)", "7 de agosto y 24 de septiembre"),
    ("SAN MARTÍN DEL CASTAÑAR", "11 de octubre y 11 de noviembre"),
    ("SAN MIGUEL DE VALERO", "30 de septiembre y 1 de octubre"),
    ("SAN MIGUEL DEL ROBLEDO", "7 de mayo y 29 de septiembre"),
    ("SAN PEDRO DE ROZADOS", "3 de febrero y 27 de mayo"),
    ("SANTIZ", "28 de septiembre y 29 de septiembre"),
    ("VALDELACASA", "16 de septiembre y 17 de septiembre"),
    ("VALDERRODRIGO", "1 de octubre y 4 de octubre"),
    ("VALVERDÓN", "15 de junio y 24 de junio"),
    ("VILLARMUERTO", "14 de agosto y 20 de agosto"),
    ("VILLORIA", "5 de abril y 8 de septiembre"),
    ("ZAMARRA", "20 de enero y 3 de mayo"),
    ("ZARZA DE PUMAREDA (LA)", "29 de marzo y 10 de agosto"),
]

SPOT = ("2026-11-27: 32 rows transcribed from a 200 dpi render (two crops) and re-read; every FECHA cell "
        "checked against the PDF's own glyph codes through one consistent glyph map (see docstring).")


GAP = "\x02"  # a second space glyph of the font


def glyph_dates(doc):
    """FECHA cell of each row, top to bottom, as (span at x~324, span at x~338). The first span holds the
    first day number plus an overlapping start of 'de'; the second 'de <month> y <day> de <month>' (its
    first letters may overlap the first span). One row repeats its spans (overprint): first one kept."""
    out = []
    for y, ss in cu.lines(cu.spans(doc, 1, decode=True)):
        if not 198 < y < 740:  # y~190 is the header row (FECHA)
            continue
        first = {}
        for s in ss:
            if s[0] >= 320 and s[4].replace(GAP, "").replace(" ", "") and round(s[0]) not in first:
                first[round(s[0])] = s[4].replace(GAP, " ")
        if first:
            xs = sorted(first)
            out.append((first[xs[0]], first[xs[-1]]))
    return out


def check_glyphs(cells):
    """One glyph->char map must explain every row: the first day number (prefix of the first span) and
    the whole second span (aligned from the end of '<d1> de <m1> y <d2> de <m2>'). The font's '7' decodes
    as a space and swallows the word space after it, so '7 ' in the transcription is compared as ' '
    (the 7s themselves rest on the render); every other glyph must map to exactly one character and back."""
    assert len(cells) == len(ANNEX), (len(cells), len(ANNEX))
    fwd, back = {}, {}

    def pair(g, c, name):
        if g == " ":
            if c != " ":
                raise SystemExit(f"GLYPH CONFLICT {name}: space glyph vs {c!r}")
            return
        if fwd.setdefault(g, c) != c or back.setdefault(c, g) != g:
            raise SystemExit(f"GLYPH CONFLICT {name}: {g!r} -> {fwd[g]!r} / {c!r}")

    for (a, b), (name, txt) in zip(cells, ANNEX):
        txt = txt.replace("7 ", " ")
        d1 = txt.split(" ")[0] + " "
        for g, c in zip(a[:len(d1)], d1):
            pair(g, c, name)
        if len(b) > len(txt):
            raise SystemExit(f"LENGTH MISMATCH {name}: {b!r} vs {txt!r}")
        for g, c in zip(reversed(b), reversed(txt)):
            pair(g, c, name)
    return len(fwd)


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    doc = pymupdf.open(os.path.join(W, "dl", SID, "a.pdf"))
    n = check_glyphs(glyph_dates(doc))
    doc.close()
    print("glyph map consistent over all rows,", n, "glyphs")
    recs = []
    for name, txt in ANNEX:
        pairs = cu.parse_free(txt)
        assert len(pairs) == 2, (name, pairs)
        recs.append({"muni": name, "locality": None, "holidays": cu.hol([(d, None) for d, _ in pairs]),
                     "note": "Complementary list to BOP Salamanca 129; the annex gives dates only."})
    rows = cu.build_rows(ine, "37", recs)
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
