"""BOPPO nº 192 (06-10-2026), anuncio 2026071521: calendario laboral da provincia de Pontevedra 2027.

Section "Segundo" is a 3-column table [CONCELLO | date | festa] (second row of a concello has an
empty first cell; some festa cells are empty). Read with PyMuPDF find_tables(); the page-1 table of
general (regional) holidays has 2 columns and is skipped.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import galicia_util  # noqa: E402

SID = "boppo-192"
CPRO = "36"
META = {
    "title": "Calendario laboral da provincia de Pontevedra para o ano 2027, Departamento Territorial da Consellería de Emprego, Comercio e Emigración (BOPPO nº 192, 06/10/2026, anuncio 2026071521)",
    "url": "https://boppo.depo.gal/web/boppo/detalle/-/boppo/2026/10/06/2026071521",
    "published": "2026-10-06",
    "region": "galicia",
}
DATE = re.compile(r"^(\d{1,2}) de (\w+)( e)?$")


def parse(pdf):
    import pymupdf
    doc = pymupdf.open(pdf)
    out, cur = [], None
    for page in doc:
        for t in page.find_tables().tables:
            if t.col_count != 3:
                continue
            for r in t.extract():
                name, date, fest = [(c or "").replace("\n", " ").strip() for c in r]
                m = DATE.match(re.sub(r"\s+", " ", date))
                if not m:
                    print("UNPARSED ROW:", r)
                    continue
                if name:
                    cur = {"name": name, "holidays": [], "and": False}
                    out.append(cur)
                if m.group(3):
                    cur["and"] = True  # "24 de xuño e / 25 de xuño Festas patronais San Paio"
                cur["holidays"].append({"date": common.iso(int(m.group(1)), m.group(2)), "name": fest or None})
    for o in out:
        if o.pop("and"):
            named = [h["name"] for h in o["holidays"] if h["name"]]
            if len(named) == 1:
                for h in o["holidays"]:
                    h["name"] = named[0]
                o["note"] = ("The bulletin prints the two dates joined by 'e' with one denomination "
                             f"('{named[0]}'), applied to both days.")
    return out


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    parsed = parse(os.path.join(W, "dl", SID, "bop.pdf"))
    rows = []
    for p in parsed:
        code, how = ine.match(CPRO, p["name"])
        row = {"name": p["name"], "cpro": CPRO, "ine": code, "match": how,
               "holidays": p["holidays"], "status": "boletin"}
        if p.get("note"):
            row["note"] = p["note"]
        rows.append(row)
    galicia_util.add_notes(rows)
    for c, n in common.coverage(ine, rows, [CPRO]):
        print("MISSING from bulletin:", c, n)
    common.save_parsed(W, SID, META, rows, SPOT)


SPOT = ("2026-11-07, spotcheck_galicia.py (independent read of the plain page text), 8 random rows + "
        "capital, all OK: A Estrada (06-24, 06-25); Salceda de Caselas (02-09, 07-19); Soutomaior (03-29, "
        "08-06); Pontevedra (02-10, 03-29); Tui (02-09, 04-05); Vilanova de Arousa (01-15, 09-16); Meis "
        "(02-09, 03-29); Mos (06-14, 08-09). 61/61 concellos.")

if __name__ == "__main__":
    main()
