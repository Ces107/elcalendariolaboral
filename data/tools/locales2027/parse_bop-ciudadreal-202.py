"""BOP Ciudad Real nº 202 (20-10-2026), anuncio 3389: fiestas locales 2027, all municipalities.

Annex table read with PyMuPDF find_tables() (MUNICIPIO | dd/mmm | dd/mmm); dates only, no names.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-ciudadreal-202"
META = {
    "title": "Delegación Provincial de Economía, Empresas y Empleo de Ciudad Real. Fiestas Locales para el año 2027 (BOP Ciudad Real núm. 202, 20-X-2026, anuncio 3389)",
    "url": "https://se1.dipucr.es:4443/SIGEM_BuscadorDocsWeb/getDocument.do?entidad=005&doc=7828286",
    "published": "2026-10-20",
    "region": "castilla-la-mancha",
}
CPRO = "13"
SMALL = {"de", "del", "la", "las", "los", "el", "y", "con", "en", "a"}
# names printed without accents in the annex -> INE code checked by eye
MANUAL = {"ALCOBA DE LOS MONTES": "13006"}  # INE name: Alcoba


def nice(upper):
    words = upper.title().split(" ")
    return " ".join(w.lower() if i and w.lower() in SMALL else w for i, w in enumerate(words))


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    for n, c in MANUAL.items():
        ine.add_manual(CPRO, n, c)
    doc = pymupdf.open(os.path.join(W, "dl", SID, "cr.pdf"))
    rows = []
    for page in doc:
        for t in page.find_tables().tables:
            for r in t.extract():
                if len(r) != 3 or not all(r):
                    continue
                name = re.sub(r"\s+", " ", r[0]).strip()
                dates = []
                for c in r[1:]:
                    m = re.fullmatch(r"(\d\d)/([a-z]{3})", c.strip())
                    dates.append(common.iso(int(m.group(1)), m.group(2)))
                code, how = ine.match(CPRO, name)
                rows.append({"name": nice(name), "printed": name, "cpro": CPRO, "ine": code, "match": how,
                             "holidays": [{"date": d, "name": None} for d in dates], "status": "boletin",
                             "note": "The BOP annex gives dates only, without festivity names."})
    miss = common.coverage(ine, rows, [CPRO])
    common.save_parsed(W, SID, META, rows, SPOT, extra={"missing_from_list": [f"{c} {n}" for c, n in miss]})
    print("missing:", miss)


SPOT = ("2026-11-07: re-read with page.get_text() (plain line order, independent of find_tables) for "
        "Abenójar (15 may, 24 jun), Almagro (5, 24 ago), Campo de Criptana (29 mar, 24 ago), "
        "Puertollano (printed 08/sep then 13/may), Tomelloso (25, 31 ago), Viso del Marqués (23 jul, 30 nov); "
        "all match. The resolution grants councils 15 days from publication to request corrections.")

if __name__ == "__main__":
    main()
