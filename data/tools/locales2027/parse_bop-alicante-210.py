"""Alicante province: BOP Alicante núm. 210 (04-11-2026), edicto 8352/2026. Resolución de 29 de octubre de 2026 de la
Dirección Territorial de Vivienda, Empleo, Juventud e Igualdad de Alicante, calendario de fiestas locales 2027.

Input:  <W>/dl/bop-alicante-210/2026_008352.pdf
  (https://www.dip-alicante.es/bop2/pdftotal/2026/11/04_210/2026_008352.pdf)
Run:    python -E -P parse_bop-alicante-210.py <W>

Prose annex parsed by cv_util. The paragraphs where the printed text is inconsistent are handled in FIX below, each
with a note saying what the bulletin prints; no date is guessed. Muro de Alcoy is printed "SIN DETERMINAR" (left out).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))
import common  # noqa: E402
import cv_util  # noqa: E402
from muni_match import Matcher  # noqa: E402

SID = "bop-alicante-210"
CPRO = "03"
META = {
    "title": "Resolución de 29 de octubre de 2026 de la Dirección Territorial de Vivienda, Empleo, Juventud e Igualdad "
             "de Alicante, por la que se aprueba el calendario de fiestas locales, retribuidas y no recuperables, en el "
             "ámbito de la provincia de Alicante para el año 2027 (BOP Alicante núm. 210, 04-11-2026, edicto 8352)",
    "url": "https://www.dip-alicante.es/bop2/pdftotal/2026/11/04_210/2026_008352.pdf",
    "published": "2026-11-04",
    "region": "comunitat-valenciana",
}
DROP = [r"^Butllet", r"^edita excma", r"^Bolet[ií]n Oficial de la Provincia", r"^N[º°] 210 de", r"^P[áa]g\. \d+",
        r"^8352 / 2026"]
# bulletin paragraph -> what to keep, with the reason (checked by eye against the PDF)
FIX = {
    "AGOST": dict(dates=["2027-03-03"], names=["Día de la Vella"], note="The bulletin prints the second day without its day number "
                  "(\"de julio, lunes, Festividad de San Pedro Apóstol\"); only 3 March is listed here."),
    "TÀRBENA": dict(dates=["2027-08-09"], note="The bulletin prints \"9 de agosto, lunes; 9 de agosto, martes\": "
                    "the second day is not clear (9 August 2027 is a Monday); only 9 August is listed here."),
    "RÀFOL DE ALMÚNIA (EL)": dict(dates=["2027-08-12"], note="The bulletin prints the second day as \"viernes 143de "
                                  "agosto\" (a misprint); only 12 August is listed here."),
}
SPOTCHECK = ("Re-read against the PDF (pages 3-9) by eye, independently of the parser: Alicante (8 Apr, 24 Jun), "
             "Elche (5 Apr, 29 Dec), Benidorm (15-16 Nov), Torrevieja (5 Apr, 16 Jul), Orihuela (17 Jul, 8 Sep), "
             "Alcoy (24 Apr, 26 Apr), Elda (8-9 Sep), San Vicente del Raspeig (5-6 Apr), Dénia (7 Jul, 16 Aug + "
             "La Xara, Jesús Pobre) - all match.")


def main():
    W = common.workdir_from_argv()
    import pymupdf
    doc = pymupdf.open(os.path.join(W, "dl", SID, "2026_008352.pdf"))
    text = "".join(p.get_text() for p in doc)
    text = text[text.index("RELACIÓN DE FIESTAS LOCALES"):].split("\n", 1)[1]
    paras = cv_util.paragraphs(cv_util.clean_lines(text, DROP))
    ents = cv_util.parse_annex(paras)
    ine, mt = common.INE(W), Matcher()
    rows, by_code, report = [], {}, []
    for e in ents:
        if e["kind"] == "eatim":
            continue
        code, how = cv_util.match(ine, mt, CPRO, e["name"])
        fix = FIX.get(e["name"])
        dates, names = e["dates"], e["names"]
        notes = []
        if fix:
            keep = fix["dates"]
            names = fix.get("names") or [names[dates.index(d)] if d in dates else None for d in keep]
            dates = keep
            notes.append(fix["note"])
        elif e["issues"]:
            for iss in e["issues"]:
                if "printed" in iss and "year" not in iss:
                    notes.append(f"The bulletin prints a weekday that does not match the date ({iss}); "
                                 "dates kept as published.")
                elif "year printed" in iss:
                    notes.append(f"The bulletin prints the {iss.split(chr(39))[1]} year on one date of this 2027 "
                                 "list; read as 2027.")
                else:
                    notes.append(iss)
        if not dates:
            report.append(f"SKIP {e['name']}: {e['body'][:80]}")
            continue
        row = {"name": e["name"], "cpro": CPRO, "ine": code, "match": how, "status": "boletin",
               "holidays": [{"date": d, "name": n} for d, n in zip(dates, names)]}
        if notes:
            row["note"] = " ".join(notes)
        if e["issues"]:
            report.append(f"ISSUE {e['name']}: {e['issues']} -> {dates}")
        rows.append(row)
        by_code[code] = row
    for e in ents:
        if e["kind"] != "eatim":
            continue
        code, _ = cv_util.match(ine, mt, CPRO, e["parent"])
        parent = by_code.get(code)
        assert parent, e
        parent.setdefault("localities", []).append(
            {"name": e["name"], "holidays": [{"date": d, "name": n} for d, n in zip(e["dates"], e["names"])]})
        add = f"The entidad local menor {e['name']} has its own days: {', '.join(e['dates'])} (see localities)."
        parent["note"] = f"{parent['note']} {add}" if parent.get("note") else add
    for r in report:
        print(r)
    miss = common.coverage(ine, rows, [CPRO])
    print("not in the annex:", [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOTCHECK)


if __name__ == "__main__":
    main()
