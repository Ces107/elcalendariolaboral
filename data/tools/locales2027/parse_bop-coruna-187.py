"""BOP A Coruña nº 187 (30-09-2026), anuncio 2026/6291: festas locais 2027, all municipalities.

Table per page: [CONCELLO | date | festa]; second row of each concello has an empty first cell.
Read with PyMuPDF find_tables().
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import galicia_util  # noqa: E402

SID = "bop-coruna-187"
CPRO = "15"
META = {
    "title": "Resolución do Departamento Territorial da Consellería de Emprego, Comercio e Emigración da Coruña sobre as festividades de carácter local na Provincia da Coruña (BOP A Coruña nº 187, 30/09/2026, anuncio 2026/6291)",
    "url": "https://bop.dacoruna.gal/bopportal/descargarPdf?page=1&fecha=20260930&numRegistro=2026/0000006291.pdf",
    "published": "2026-09-30",
    "region": "galicia",
}
DATE = re.compile(r"^(\d{1,2}) de (\w+)$")


def parse(pdf):
    import pymupdf
    doc = pymupdf.open(pdf)
    out, cur = [], None
    for page in doc:
        for t in page.find_tables().tables:
            for r in t.extract():
                if len(r) != 3:
                    continue
                name, date, fest = [(c or "").replace("\n", " ").strip() for c in r]
                m = DATE.match(re.sub(r"\s+", " ", date))
                if not m:
                    continue
                if name:
                    cur = {"name": name, "holidays": []}
                    out.append(cur)
                cur["holidays"].append({"date": common.iso(int(m.group(1)), m.group(2)), "name": fest or None})
    return out


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    parsed = parse(os.path.join(W, "dl", SID, "bop.pdf"))
    rows = []
    for p in parsed:
        code, how = ine.match(CPRO, p["name"])
        rows.append({"name": p["name"], "cpro": CPRO, "ine": code, "match": how,
                     "holidays": p["holidays"], "status": "boletin"})
    galicia_util.add_notes(rows)
    for c, n in common.coverage(ine, rows, [CPRO]):
        print("MISSING from bulletin:", c, n)
    common.save_parsed(W, SID, META, rows, SPOT)


SPOT = ("2026-11-07, spotcheck_galicia.py (independent read of the plain page text, lines after the "
        "concello name), 8 random rows + capital, all OK: Cabana de Bergantiños (02-09, 06-24); Oroso "
        "(02-09, 09-16); Boiro (07-16, 08-31); Ames (05-06, 06-24); Tordoia (02-09, 06-24); Lousame "
        "(03-18, 10-01); Muros (06-29, 07-16); As Somozas (07-23, 07-26); A Coruña (02-09, 06-24). "
        "93/93 concellos; all 30 existing Galician entries have identical dates.")

if __name__ == "__main__":
    main()
