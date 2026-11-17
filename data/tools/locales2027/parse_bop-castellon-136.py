"""Castellón province: BOP Castellón núm. 136 (10-11-2026), anuncio 04772-2026. Resolución de 29 de octubre de 2026 de
la Dirección Territorial de Vivienda, Empleo, Juventud e Igualdad de Castellón, calendario de fiestas locales 2027.

Input:  <W>/dl/bop-castellon-136/anuncio.pdf
  (https://bop.dipcas.es/PortalBOP/api/descargarAnuncio/es/4NShdAoeCp ; the bulletin page is
   https://bop.dipcas.es/PortalBOP/ -> Nº 136, Administración Autonómica)
Run:    python -E -P parse_bop-castellon-136.py <W>

Prose annex parsed by cv_util (same format as Alicante's, "5 de abril y 11 de octubre").
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))
import common  # noqa: E402
import cv_util  # noqa: E402
from muni_match import Matcher  # noqa: E402

SID = "bop-castellon-136"
CPRO = "12"
META = {
    "title": "Resolución de 29 de octubre de 2026 de la Dirección Territorial de Vivienda, Empleo, Juventud e Igualdad "
             "de Castellón, por la que se aprueba el calendario de fiestas locales, retribuidas y no recuperables, en el "
             "ámbito de la provincia de Castellón para el año 2027 (BOP Castellón núm. 136, 10-11-2026, anuncio "
             "04772-2026)",
    "url": "https://bop.dipcas.es/PortalBOP/api/descargarAnuncio/es/4NShdAoeCp",
    "published": "2026-11-10",
    "region": "comunitat-valenciana",
}
DROP = [r"^Número 136 - 10 de noviembre de 2026", r"^\d{1,2}$"]
SPOTCHECK = ("Re-read against the PDF (pages 3-8) by eye, independently of the parser: Castellón de la Plana (1 Mar, "
             "29 Jun), Vila-real (5 Apr, 17 May), Burriana (3 Feb, 8 Sep), La Vall d'Uixó (5 Apr, 11 Oct), Vinaròs "
             "(20 Jan, 24 Jun), Benicarló (18 Mar, 24 Aug), Onda (6 Aug, 25 Oct), Morella (7-8 Jan) - all match.")


def main():
    W = common.workdir_from_argv()
    import pymupdf
    doc = pymupdf.open(os.path.join(W, "dl", SID, "anuncio.pdf"))
    text = "".join(p.get_text() for p in doc)
    text = text[text.index("RELACIÓN DE FIESTAS LOCALES"):].split("\n", 1)[1]
    paras = cv_util.paragraphs(cv_util.clean_lines(text, DROP))
    ents = cv_util.parse_annex(paras)
    ine, mt = common.INE(W), Matcher()
    rows = []
    for e in ents:
        assert e["kind"] == "muni", e
        code, how = cv_util.match(ine, mt, CPRO, e["name"])
        row = {"name": e["name"], "cpro": CPRO, "ine": code, "match": how, "status": "boletin",
               "holidays": [{"date": d, "name": n} for d, n in zip(e["dates"], e["names"])]}
        if e["issues"]:
            print(f"ISSUE {e['name']}: {e['issues']} -> {e['dates']}")
            row["note"] = " ".join(f"The bulletin prints a weekday that does not match the date ({i}); date kept as "
                                   "published." for i in e["issues"])
        rows.append(row)
    miss = common.coverage(ine, rows, [CPRO])
    print("not in the annex:", [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOTCHECK)


if __name__ == "__main__":
    main()
