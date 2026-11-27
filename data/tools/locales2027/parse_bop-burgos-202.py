"""BOP Burgos 202 (23-X-2026), C.V.E. BOPBUR-2026-04503: Resolución complementaria de la Oficina
Territorial de Trabajo de Burgos (13-X-2026), fiestas locales 2027 for the councils whose proposal
arrived after BOP Burgos 145 (4-VIII-2026).

The annex (page 5 of the bulletin) is a scanned image: its 16 lines (8 entities x 2 days) are
transcribed below from a 300 dpi render of the PDF and re-read twice. 'FIESTA LOCAL' = no name.
Usage: python -I parse_bop-burgos-202.py <workdir>
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

SID = "bop-burgos-202"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Burgos. Resolución complementaria sobre calendario de fiestas locales, retribuidas y no recuperables, para el año 2027 (BOP Burgos núm. 202, 23-X-2026, C.V.E. BOPBUR-2026-04503)",
    "url": "https://bopbur.diputaciondeburgos.es/sites/default/files/private/publicado/bopbur-2026-202/bopbur-2026-202-anuncio-202604503.pdf",
    "published": "2026-10-23",
    "region": "castilla-y-leon",
}

# ENTIDAD LOCAL | FECHA | FESTIVIDAD, as printed
ANNEX = [
    ("ALFOZ DE QUINTANADUEÑAS", "04/06/2027", "FIESTA LOCAL"),
    ("ALFOZ DE QUINTANADUEÑAS", "04/10/2027", "FIESTA LOCAL"),
    ("BURGOS", "04/06/2027", "CURPILLOS"),
    ("BURGOS", "29/06/2027", "SAN PEDRO Y SAN PABLO"),
    ("HONTORIA DEL PINAR", "13/08/2027", "FIESTA LOCAL"),
    ("HONTORIA DEL PINAR", "17/08/2027", "FIESTA LOCAL"),
    ("HUERMECES", "24/06/2027", "SAN JUAN"),
    ("HUERMECES", "10/08/2027", "SAN LORENZO"),
    ("MERINDAD DE MONTIJA", "29/03/2027", "LUNES DE PASCUA"),
    ("MERINDAD DE MONTIJA", "29/06/2027", "SAN PEDRO"),
    ("MERINDAD DE VALDIVIELSO", "15/05/2027", "SAN ISIDRO"),
    ("MERINDAD DE VALDIVIELSO", "24/06/2027", "SAN JUAN"),
    ("PALACIOS DE RIOPISUERGA", "25/01/2027", "FIESTA LOCAL"),
    ("PALACIOS DE RIOPISUERGA", "03/06/2027", "FIESTA LOCAL"),
    ("VILLAQUIRAN DE LOS INFANTES", "08/09/2027", "NATIVIDAD DE NTRA SRA"),
    ("VILLAQUIRAN DE LOS INFANTES", "09/09/2027", "FIESTA LOCAL"),
]

SPOT = ("2026-11-27: the annex is an image; all 16 lines transcribed from a 300 dpi render and "
        "re-read line by line (name, date, festivity). Counts: 16 lines = 8 entities x 2 days. "
        "Burgos city 04/06 Curpillos + 29/06 matches its Junta de Gobierno entry of 2026-11-17.")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    ents, order = {}, []
    for name, d, fest in ANNEX:
        dd, mm, yy = d.split("/")
        assert yy == str(common.YEAR)
        if name not in ents:
            ents[name] = []
            order.append(name)
        ents[name].append({"date": common.iso(int(dd), int(mm)),
                           "name": None if fest == "FIESTA LOCAL" else cu.nice(fest)})
    assert len(order) == 8 and all(len(v) == 2 for v in ents.values())
    note = ("Complementary list (proposals received after BOP Burgos 145); the annex gives one line "
            "per day; 'FIESTA LOCAL' means no festivity name.")
    recs = [{"muni": n, "locality": None, "holidays": ents[n], "note": note} for n in order]
    rows = cu.build_rows(ine, "09", recs)
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
