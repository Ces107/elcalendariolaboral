"""BOP Soria 113 (28-IX-2026), anuncio 1756: corrección de error material del Acuerdo de 7-VII-2026
of the Oficina Territorial de Trabajo de Soria (BOP Soria 81): BERLANGA DE DUERO 23 Aug (not 30 Aug)
and 24 Sep. The row is re-emitted with the corrected dates after checking the PDF text.
Usage: python -I parse_bop-soria-113.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-soria-113"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Soria. Corrección de error material del Acuerdo de 7 de julio de 2026 por el que se determinan las fiestas laborales de las localidades de la provincia de Soria (BOP Soria núm. 113, 28-IX-2026, anuncio 1756)",
    "url": "https://bop.dipsoria.es/index.php/mod.documentos/mem.descargar/fichero.documentos_1756_8b789a52%232E%23pdf",
    "published": "2026-09-28",
    "region": "castilla-y-leon",
}
SPOT = ("2026-11-27: one-row correction re-read in the PDF: 'Donde dice: BERLANGA DE DUERO: 30 de agosto y "
        "24 de septiembre. Debe decir: BERLANGA DE DUERO: 23 de agosto y 24 de septiembre'. Matches.")


def main():
    W = common.workdir_from_argv()
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    t = " ".join(" ".join(p.get_text().split()) for p in doc)
    doc.close()
    assert re.search(r"Debe decir:\s*\W?BERLANGA DE DUERO: 23 de agosto y 24 de septiembre", t), t[:800]
    rows = [{"name": "Berlanga de Duero", "cpro": "42", "ine": "42035", "match": "exact",
             "holidays": [{"date": "2027-08-23", "name": None}, {"date": "2027-09-24", "name": None}],
             "status": "boletin",
             "note": "BOP Soria 113 (28-IX-2026) corrects BOP Soria 81: 23 Aug instead of 30 Aug. "
                     "The resolution gives dates only, without festivity names."}]
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
