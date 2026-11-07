"""BOP Lugo nº 221 (26-09-2026): calendario laboral 2027 da provincia de Lugo, all concellos.

Table: Concello | Data 1 | Denominación Data 1 | Data 2 | Denominación Data 2 (dates dd/mm/2027).
PyMuPDF find_tables() splits some long names into extra columns and wraps a few names onto a
continuation row (first cell empty); cells are assigned by column index, never by text order
(pdftotext -layout shifted Lugo/Mondoñedo by one row before 2026-10-26).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import galicia_util  # noqa: E402

SID = "bop-lugo-221"
CPRO = "27"
META = {
    "title": "Resolución sobre o calendario laboral do ano 2027 para a Provincia de Lugo, Dirección Territorial da Consellería de Emprego, Comercio e Emigración (BOP Lugo nº 221, 26/09/2026)",
    "url": "https://www.deputacionlugo.gal/sites/deputacionlugo.org/files/inline-files/26-09-2026.pdf",
    "published": "2026-09-26",
    "region": "galicia",
}
DATE = re.compile(r"^(\d{2})/(\d{2})/2027$")


def parse(pdf):
    import pymupdf
    doc = pymupdf.open(pdf)
    out, cur = [], None
    for page in doc:
        for t in page.find_tables().tables:
            rows = t.extract()
            if not rows or (rows[0][0] or "").strip() != "Concello":
                continue  # other notices in the same issue
            for r in rows:
                cells = [(c or "").replace("\n", " ").strip() for c in r]
                if not cells or cells[0] == "Concello":
                    continue
                dates = [i for i, c in enumerate(cells) if DATE.match(c)]
                if cells[0] and len(dates) == 2:
                    i1, i2 = dates
                    n1 = [j for j in range(i1 + 1, i2) if cells[j]]
                    n2 = [j for j in range(i2 + 1, len(cells)) if cells[j]]
                    cur = {"name": cells[0], "holidays": [], "cols": []}
                    for di, ns in ((i1, n1), (i2, n2)):
                        m = DATE.match(cells[di])
                        cur["holidays"].append({
                            "date": f"2027-{m.group(2)}-{m.group(1)}",
                            "name": " ".join(cells[j] for j in ns) or None})
                        cur["cols"].append((di, len(cells)))
                    out.append(cur)
                elif not cells[0] and not dates and cur and any(cells):
                    # wrapped name: attach to the holiday whose name column is closest on the left
                    for j, c in enumerate(cells):
                        if not c:
                            continue
                        k = 1 if j > cur["cols"][1][0] else 0
                        h = cur["holidays"][k]
                        h["name"] = f"{h['name']} {c}".strip() if h["name"] else c
                elif any(cells):
                    print("UNPARSED ROW:", cells)
    for o in out:
        o.pop("cols")
    return out


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    # verified by eye: bulletin spelling vs INE name
    ine.add_manual(CPRO, "Guntín de Pallares", "27023")  # INE "Guntín"
    ine.add_manual(CPRO, "Folgoso do Caurel", "27017")  # INE "Folgoso do Courel"
    ine.add_manual(CPRO, "Pobra de Brollón", "27047")  # INE "Pobra do Brollón, A"
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


SPOT = ("2026-11-07, spotcheck_galicia.py (independent read by word coordinates: dd/mm/2027 tokens on "
        "the concello's printed line), 8 random rows + capital, all OK: Guntín de Pallares (02-09, 07-05); "
        "Ribas de Sil (03-29, 08-16); Xove (02-09, 08-30); Pobra de Brollón (02-09, 08-27); Palas de Rei "
        "(01-28, 09-14); Castro de Rei (02-09, 08-09); Cospeito (02-09, 09-08); Folgoso do Caurel "
        "(08-19, 12-07); Lugo (02-09, 10-05). Mondoñedo keeps San Lucas 18-10 (no row shift). 67/67 concellos.")

if __name__ == "__main__":
    main()
