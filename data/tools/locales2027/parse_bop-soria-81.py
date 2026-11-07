"""BOP Soria 81 (15-VII-2026): fiestas laborales 2027, Oficina Territorial de Trabajo.

One-column annex: 'MUNICIPIO: 2 de febrero y 24 de junio'; indented mixed-case lines are
localities of the municipality above ('	 Ontalvilla de Almazán: 11 y 12 de junio').
Usage: python -I parse_bop-soria-81.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-soria-81"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Soria. Fiestas laborales año 2027 (BOP Soria núm. 81, 15-VII-2026, BOPSO-81-15072026)",
    "url": "https://bop.dipsoria.es/index.php/mod.documentos/mem.descargar/fichero.documentos_1390_b8116e16%232E%23pdf",
    "published": "2026-07-15",
    "region": "castilla-y-leon",
}
NOISE = re.compile(r"^(Núm\. 81|Pág\. \d+|BOPSO-81|Boletín Oficial de la Provincia de Soria|Miércoles, 15 de julio|=====)")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    ine.add_manual("42", "El BURGO DE OSMA", "42043")  # INE: Burgo de Osma-Ciudad de Osma
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    text = "\n".join(p.get_text() for p in doc)
    doc.close()
    body = text.split("\nANEXO\n", 1)[1].split("Soria, 7 de julio de 2026")[0]
    raw = [ln.replace("\t", " ").strip() for ln in body.splitlines()]
    raw = [ln for ln in raw if ln and not NOISE.match(ln)]
    # a few rows break between the name and ': dates' (or before the dates)
    lines = []
    for ln in raw:
        if lines and (ln.startswith(":") or (re.match(r"^\d", ln) and ":" not in lines[-1])):
            lines[-1] = lines[-1] + ": " + ln.lstrip(": ")
        else:
            lines.append(ln)
    recs, muni = [], None
    for ln in lines:
        m = re.match(r"^(.+?)\s*:\s*(.+)$", ln)
        if not m:
            raise SystemExit(f"UNPARSED {ln!r}")
        name, dates = m.group(1).strip(), m.group(2)
        hs = cu.hol([(d, None) for d, _ in cu.parse_free(dates)])
        if not hs:
            raise SystemExit(f"NO DATES {ln!r}")
        if name == "VERGUIZAS":  # printed in capitals right after VIZMANOS: a village of Vizmanos
            recs.append({"muni": "VIZMANOS", "locality": "Verguizas", "holidays": hs})
        elif name.isupper():
            muni = name
            recs.append({"muni": name, "locality": None, "holidays": hs, "note": ""})
        else:
            recs.append({"muni": muni, "locality": name, "holidays": hs})
    rows = cu.build_rows(ine, "42", recs)
    for r in rows:
        r["note"] = ("The resolution gives dates only, without festivity names. " + r["note"]).strip()
    miss = common.coverage(ine, rows, ["42"])
    print("not in bulletin:", len(miss), [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOT, extra={"not_listed": [c for c, _ in miss]})


SPOT = ("2026-11-07: one-column annex read line by line (PyMuPDF text). Re-read against the PDF text: "
        "ABEJAR 2 Feb + 24 Jun; ALMAZÁN 17 May + 6 Sep (7 localities); ARÉVALO DE LA SIERRA only 27 Aug; "
        "CASTILLEJO DE ROBLEDO 30 Apr + 10 Sep (name and dates on two lines); SORIA 24 Jun + 2 Oct; "
        "Matute de Almazán (locality of Matamala) 24 + 27 Sep: all match.")

if __name__ == "__main__":
    main()
