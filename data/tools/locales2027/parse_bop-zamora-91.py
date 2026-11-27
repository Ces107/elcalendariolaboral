"""BOP Zamora 91 (7-VIII-2026), R-202601943: corrección de errores del anexo of the 2027 calendar
published in BOP Zamora 88 (31-VII-2026).

The correction prints 'donde dice / debe decir' blocks plus two towns to add (Toro, Fuentelapeña).
This parser re-reads BOP 88 (parse_bop-zamora-88.read_recs, so dl/bop-zamora-88/bop.pdf is needed),
applies every block below and emits only the municipalities the correction touches; merge ranks
this later bulletin above BOP 88 for those rows. Name-only fixes (ABEZANES -> Abezames, already
matched by hand in BOP 88; Llanes -> Ilanes, a locality of Galende, same days) change no date and
are left out.
Usage: python -I parse_bop-zamora-91.py <workdir>
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

SID = "bop-zamora-91"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Zamora. Corrección de errores del anexo del calendario de fiestas de la provincia de Zamora para el año 2027 publicado en el BOP n.º 88 (BOP Zamora núm. 91, 7-VIII-2026, R-202601943)",
    "url": "https://www.diputaciondezamora.es/opencms/export/sites/dipu-zamora/servicios/BOP/.Archivos/documentos/BOP/anuncios/2026/91/202601943.pdf",
    "published": "2026-08-07",
    "region": "castilla-y-leon",
}


def h(d, m, name):
    return {"date": common.iso(d, m), "name": name}


# (municipality as printed in BOP 88, locality or None) -> corrected days ("debe decir")
FIX = {
    ("CUBO DE BENAVENTE", None): [h(7, "junio", "Corazón de Jesús")],
    ("FERRERAS DE ARRIBA", None): [h(3, "febrero", "San Blas")],
    ("MUELAS DEL PAN", "Ricobayo de Alba"): [h(17, "agosto", "Ntra. Sra. de la Asunción"), h(11, "octubre", "Ofertorio")],
    ("RABANALES", "Ufones"): [h(9, "diciembre", "Santa Eulalia"), h(10, "diciembre", "Santa Eulalia")],
    ("ROBLEDA-CERVANTES", "Robleda"): [h(27, "julio", "Santa Ana"), h(15, "septiembre", "La Patrona")],
    ("VEGA DE TERA", "Milla de Tera"): [h(28, "enero", "San Tirso")],
    ("VILLADEPERA", None): [h(15, "mayo", "San Isidro"), h(1, "octubre", "Ofertorio Virgen del Rosario")],
    ("VILLANUEVA DE AZOAGUE", "Castropepe"): [h(22, "julio", "Santa María Magdalena")],
}
ADD = {
    "TORO": [h(17, "mayo", "Cristo de las Batallas"), h(8, "septiembre", "Virgen del Canto")],
    "FUENTELAPEÑA": [h(25, "mayo", "2.º día de Quintos"), h(17, "agosto", "San Roque")],
}
NOTE = "Days as corrected by BOP Zamora 91 (corrección de errores of the BOP 88 annex)."

SPOT = ("2026-11-27: every 'debe decir' block and both added towns re-read against the PDF text of R-202601943 "
        "(2 pages): Cubo de Benavente and Ferreras de Arriba lose 16 Aug; Ricobayo 16 -> 17 Aug; Ufones "
        "10-11 -> 9-10 Dec; Robleda + 15 Sep; Milla de Tera loses 16 Aug; Villadepera 17 Aug -> 1 Oct; "
        "Castropepe loses 26 May; Toro 17 May + 8 Sep; Fuentelapeña 25 May + 17 Aug.")


def main():
    W = common.workdir_from_argv()
    sp = importlib.util.spec_from_file_location("z88", os.path.join(HERE, "parse_bop-zamora-88.py"))
    z88 = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(z88)
    ine, recs = z88.read_recs(W)
    touched, done = set(), set()
    for r in recs:
        k = (r["muni"], r["locality"])
        if k in FIX:
            r["holidays"] = FIX[k]
            if r["locality"] is None:
                r["note"] = NOTE
            touched.add(r["muni"])
            done.add(k)
    assert done == set(FIX), set(FIX) - done
    out = [r for r in recs if r["muni"] in touched]
    for r in out:
        if r["locality"] is None and r["muni"] not in {k[0] for k in FIX if k[1] is None}:
            r["note"] = (r.get("note", "") + " The days of one of its localities were corrected by "
                         "BOP Zamora 91 (corrección de errores of the BOP 88 annex).").strip()
    for n, hs in ADD.items():
        out.append({"muni": n, "locality": None, "holidays": hs, "note": NOTE + " Added by the correction."})
    rows = cu.build_rows(ine, "49", out)
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
