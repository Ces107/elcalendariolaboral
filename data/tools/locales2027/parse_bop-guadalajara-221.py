"""Guadalajara province: BOP Guadalajara núm. 221 (18-11-2026). Anuncio de 12 de noviembre de 2026, de la Delegación
Provincial de la Consejería de Economía, Empresas y Empleo de Guadalajara, relación de fiestas de carácter local
retribuidas y no recuperables para el año 2027.

Input:  <W>/dl/bop-guadalajara-221/pdf2026_3030.pdf
  (https://boletin.dguadalajara.es/boletin/pdf/pdf2026_3030.pdf ; found in the BOP daily list of 18-11-2026,
   https://boletin.dguadalajara.es/boletin/index.php/buscar-k2-menu/date/2026/11/18)
Run:    python -I parse_bop-guadalajara-221.py <W>

Same layout as 2026 (data/tools/loc2026_bop-guadalajara-2026.py): a two-column list printed as alternating lines
(Municipio / "15 mayo y 24 septiembre"), dates only, no festivity names, no weekdays printed. Rows that are not INE
municipalities (pedanías / entidades de ámbito territorial inferior) are reported and left out.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))
import common  # noqa: E402
from muni_match import Matcher  # noqa: E402

SID = "bop-guadalajara-221"
CPRO = "19"
META = {
    "title": "Anuncio de 12 de noviembre de 2026, de la Delegación Provincial de la Consejería de Economía, Empresas y "
             "Empleo de Guadalajara, por el que se da publicidad a la relación de fiestas de carácter local retribuidas "
             "y no recuperables para el año 2027 (BOP Guadalajara núm. 221, 18-11-2026)",
    "url": "https://boletin.dguadalajara.es/boletin/pdf/pdf2026_3030.pdf",
    "published": "2026-11-18",
    "region": "castilla-la-mancha",
}
MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
DATE_LINE = re.compile(r"^\d{1,2}\b.*\b(" + "|".join(MES) + r")\b", re.I)
SKIP = ("BOP", "BOLETÍN OFICIAL", "B.O.P. DE", "Sede electrónica", "Cod. Veri")
SPOTCHECK = ("Re-read against the PDF text independently of the parser: Guadalajara (8 and 17 Sep), Azuqueca de "
             "Henares (14 May, 20 Sep), Sigüenza (22 Jan, 16 Aug), Alovera (25 Jan, 8 Sep), Albares (14 and 18 Jun), "
             "Villaseca de Henares (3 and 4 Feb) and 5 random rows (Mandayona, Berninches, Alcocer, Medranda, Selas) "
             "- all match. 283 of 288 municipalities (Pardos, Robledillo de Mohernando, Rueda de la Sierra, Torrubia, "
             "Traíd not listed); 34 pedanía rows left out, as in 2026.")


def dates(txt):
    """'15 mayo y 24 septiembre' / '14 y 18 junio' -> sorted ISO list"""
    out, pending = [], []
    for num, mes in re.findall(r"(\d{1,2})(?:\s+(?:de\s+)?(" + "|".join(MES) + r"))?", txt.lower()):
        pending.append(int(num))
        if mes:
            out += [datetime.date(2027, MES[mes], d).isoformat() for d in pending]
            pending = []
    assert not pending and out, txt
    return sorted(set(out))


def entries(pdf):
    import pymupdf
    lines = []
    for page in pymupdf.open(pdf):
        lines += [ln.strip() for ln in page.get_text().splitlines() if ln.strip()]
    start = lines.index("Fiestas") + 1
    name = None
    for ln in lines[start:]:
        if ln.startswith(SKIP) or ln.isdigit():
            continue
        if DATE_LINE.match(ln):
            assert name, ln
            yield name, ln
            name = None
        else:
            assert name is None, (name, ln)
            name = ln
    assert name is None, name


def main():
    W = common.workdir_from_argv()
    mt = Matcher()
    rows, seen, left = [], set(), []
    for name, txt in entries(os.path.join(W, "dl", SID, "pdf2026_3030.pdf")):
        code = mt.match(name, province=CPRO)
        if not code:
            left.append(f"{name}: {txt}")
            continue
        assert code not in seen, (name, code)
        seen.add(code)
        hs = [{"date": d, "name": None} for d in dates(txt)]
        notes = []
        if len(hs) == 1:
            notes.append("The bulletin gives only one date.")
        elif len(hs) > 2:
            notes.append(f"The bulletin lists {len(hs)} dates; kept as published.")
        suns = [h["date"] for h in hs if datetime.date.fromisoformat(h["date"]).weekday() == 6]
        if suns:
            notes.append("Published date(s) falling on a Sunday, kept as published: " + ", ".join(suns) + ".")
        row = {"name": name, "cpro": CPRO, "ine": code, "match": "muni_match", "status": "boletin", "holidays": hs}
        if notes:
            row["note"] = " ".join(notes)
        rows.append(row)
    print("not INE municipalities (left out):", len(left))
    for x in left:
        print("  ", x)
    ine = common.INE(W)
    print("not in the list:", [n for _, n in common.coverage(ine, rows, [CPRO])])
    common.save_parsed(W, SID, META, rows, SPOTCHECK)


if __name__ == "__main__":
    main()
