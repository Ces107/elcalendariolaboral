"""Ceuta and Melilla 2026 local holidays (one municipality each).

Ceuta: Resolución de 15-9-2025 de la Delegación del Gobierno en Ceuta (BOCCE núm. 6549, 19-9-2025, anuncio 580).
    https://www.ceuta.es/ceuta/component/jdownloads/finish/1960-septiembre/22923-bocce-6549-19-09-2025?Itemid=0
Melilla: Acuerdo del Consejo de Gobierno de 19-9-2025, calendario laboral 2026 (BOME núm. 6315, 3-10-2025, BOME-A-2025-1033).
    https://bomemelilla.es/bome/descargar/BOME-A-2025-1033.pdf
Run: python -E -P data/tools/loc2026_ceuta_melilla.py bocce6549.pdf BOME-A-2025-1033.pdf
The script checks that the quoted sentences are in the downloaded bulletins before writing the parts.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import write_part  # noqa: E402


def text(pdf):
    return re.sub(r"\s+", " ", " ".join(p.get_text() for p in pymupdf.open(pdf))).replace("r elación", "relación")


def main(bocce, bome):
    t = text(bocce)
    assert "-20 de marzo: Fiesta de Culminación de Ramadán Eid al-Fitr -13 de junio: San Antonio" in t
    write_part("bocce-2026", {
        "title": "Resolución de 15 de septiembre de 2025, de la Delegación del Gobierno en Ceuta, por la que se publica la "
                 "relación de fiestas locales de la Ciudad Autónoma de Ceuta para el año 2026 (BOCCE núm. 6549, de 19-9-2025)",
        "url": "https://www.ceuta.es/ceuta/component/jdownloads/finish/1960-septiembre/22923-bocce-6549-19-09-2025?Itemid=0",
        "published": "2025-09-19"},
        {"51001": {"holidays": [{"date": "2026-03-20", "name": "Fiesta de Culminación de Ramadán Eid al-Fitr"},
                                {"date": "2026-06-13", "name": "San Antonio"}]}}, region="ceuta")
    t = text(bome)
    assert ("tienen la consideración de locales son los días 8 de septiembre (Día de Ntra. Sra. Virgen de la Victoria) y "
            "el 17 de septiembre (día de Melilla)") in t
    write_part("bome-2026", {
        "title": "Acuerdo del Consejo de Gobierno de 19 de septiembre de 2025, relativo a calendario laboral para el año "
                 "2026 (BOME núm. 6315, de 3-10-2025, BOME-A-2025-1033)",
        "url": "https://bomemelilla.es/bome/descargar/BOME-A-2025-1033.pdf",
        "published": "2025-10-03"},
        {"52001": {"holidays": [{"date": "2026-09-08", "name": "Día de Ntra. Sra. Virgen de la Victoria"},
                                {"date": "2026-09-17", "name": "Día de Melilla"}]}}, region="melilla")


if __name__ == "__main__":
    main(*sys.argv[1:])
