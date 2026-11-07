"""BOP Ourense nº 197 (14-10-2026), R. 2.320: calendario laboral 2027 da provincia de Ourense.

Single-column list: CONCELLO in capitals, then one line per day "D de mes, denominación."
(some days have no denominación: "14 de xuño."). Read line by line with PyMuPDF get_text().
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import galicia_util  # noqa: E402

SID = "bop-ourense-197"
CPRO = "32"
META = {
    "title": "Calendario laboral 2027 da provincia de Ourense, Departamento Territorial da Consellería de Emprego, Comercio e Emigración (BOP Ourense nº 197, 14/10/2026, R. 2.320)",
    "url": "https://bop.depourense.es/portalapi/api/edicto/descargar/pdf/352736/idioma/gl",
    "published": "2026-10-14",
    "region": "galicia",
}
DATE = re.compile(r"^(\d{1,2}) de (\w+)\s*[.,]\s*(.*?)\.?$")
SKIP = ("BOP|", "Boletín Oficial", "Deputación", "CSV:", "Verificar:", "N.º 197")


def parse(pdf):
    import pymupdf
    doc = pymupdf.open(pdf)
    out, cur, started = [], None, False
    for page in doc:
        for line in page.get_text().splitlines():
            line = line.strip()
            if not line or line.startswith(SKIP):
                continue
            if line.endswith("as seguintes festas locais:"):
                started = True
                continue
            if not started:
                continue
            if line.startswith("As empresas, en virtude"):
                return out
            m = DATE.match(line)
            if m:
                name = m.group(3).strip() or None
                if name:
                    name = name[0].upper() + name[1:]
                cur["holidays"].append({"date": common.iso(int(m.group(1)), m.group(2)), "name": name})
            elif line.isupper():
                cur = {"name": line, "holidays": []}
                out.append(cur)
            else:
                raise SystemExit(f"unexpected line: {line!r}")
    return out


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    # verified by eye: bulletin spelling vs INE name
    ine.add_manual(CPRO, "A RÚA DE VALDEORRAS", "32072")  # INE "Rúa, A"
    ine.add_manual(CPRO, "O CASTRO DE CALDELAS", "32023")  # INE "Castro Caldelas"
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


SPOT = ("2026-11-07, spotcheck_galicia.py (independent read of the plain page text), 8 random rows + "
        "capital, all OK: Vilardevós (02-10, 08-16); Toén (02-09, 11-11); Allariz (02-09, 05-28); Verín "
        "(02-10, 09-08); Vilamartín de Valdeorras (04-23, 07-22); Maside (02-09, 08-27); Leiro (05-03, "
        "06-29); A Veiga (02-09, 09-08); Ourense (02-09, 11-11). 92/92 concellos (single-column list).")

if __name__ == "__main__":
    main()
