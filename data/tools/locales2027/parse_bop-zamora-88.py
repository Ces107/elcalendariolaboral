"""BOP Zamora 88 (31-VII-2026), R-202601897: corrección de errores con publicación íntegra del
calendario de fiestas locales 2027 (replaces the list in BOP 87 of 27-VII-2026).

Annex 'Localidad | Día y mes | Denominación' without rules: words grouped by printed line,
name x<260 ('- NAME' = locality of the municipality above), date 260-365, name >=365.
Usage: python -I parse_bop-zamora-88.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-zamora-88"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Zamora. Calendario de fiestas locales para el año 2027 — corrección de errores con publicación íntegra (BOP Zamora núm. 88, 31-VII-2026, R-202601897)",
    "url": "https://www.diputaciondezamora.es/opencms/export/sites/dipu-zamora/servicios/BOP/.Archivos/documentos/BOP/anuncios/2026/88/202601897.pdf",
    "published": "2026-07-31",
    "region": "castilla-y-leon",
}
C1, C2 = 260, 365
SKIP = ("BOLETÍN OFICIAL", "N.º 88", "Pág.", "www.diputaciondezamora", "R-202601897", "Cód. Validación",
        "Verificación:", "Documento firmado", "Localidad Día")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    by_name = {n: c for c, n in ine.by_code.items() if c[:2] == "49"}
    for printed, official in [("ABEZANES", "Abezames"), ("BRETÓ DE LA RIBERA", "Bretó"),
                              ("FERRERUELA DE TÁBARA", "Ferreruela"), ("ALMEIDA", "Almeida de Sayago"),
                              ("CAÑIZO DE CAMPOS", "Cañizo"), ("GRANUCILLO DE VIDRIALES", "Granucillo"),
                              ("ROALES DEL PAN", "Roales")]:
        ine.add_manual("49", printed, by_name[official])
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    ents, started, odd = [], False, []
    for pn in range(len(doc)):
        lines = {}
        for w in doc[pn].get_text("words"):
            if w[0] >= 540:  # rotated validation strip in the right margin
                continue
            lines.setdefault(round((w[1] + w[3]) / 2 / 2), []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            t = " ".join(w[4] for w in ws)
            if t.startswith("Localidad Día y mes"):
                started = True
                continue
            if not started or t.startswith(SKIP):
                continue
            if t.startswith("Zamora, 22 de julio de 2026"):
                started = False
                continue
            name = " ".join(w[4] for w in ws if w[0] < C1)
            date = " ".join(w[4] for w in ws if C1 <= w[0] < C2)
            den = " ".join(w[4] for w in ws if w[0] >= C2)
            if name:
                if not date:
                    odd.append((pn + 1, t))
                ents.append({"name": name, "raw": []})
            if date:
                ents[-1]["raw"].append([date, den])
            elif den and not name:  # wrapped festivity name
                ents[-1]["raw"][-1][1] += " " + den
    doc.close()
    for o in odd:
        print("NAME WITHOUT DATE", o)
    recs, muni = [], None
    for e in ents:
        hs = []
        note = ""
        for date, den in e["raw"]:
            if date.endswith(" mayor"):  # Riego del Camino: printed '15 de mayor'
                date = date[:-1]
                note = "The bulletin prints '15 de mayor' (read as 15 May)."
            pairs = cu.parse_free(date)
            if not pairs:
                raise SystemExit(f"BAD DATE {e['name']}: {date!r}")
            hs += [{"date": d, "name": cu.clean(den) or None} for d, _ in pairs]
        if e["name"].startswith("-"):
            recs.append({"muni": muni, "locality": cu.nice(e["name"].lstrip("- ").strip()), "holidays": hs,
                         **({"note": note} if note else {})})
        elif not hs:  # municipality printed without days, only its localities follow (Robleda-Cervantes)
            muni = e["name"]
        else:
            muni = e["name"]
            recs.append({"muni": muni, "locality": None, "holidays": hs, "note": note})
    rows = cu.build_rows(ine, "49", recs)
    miss = common.coverage(ine, rows, ["49"])
    print("not in bulletin:", len(miss), [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOT, extra={"not_listed": [c for c, _ in miss]})


SPOT = ("2026-11-07: annex read by word coordinates. This is the full re-publication (corrección de errores) "
        "that replaces BOP 87. Re-read against the PDF text: ABEZANES 24 Jun San Juan + 29 Sep San Miguel; "
        "ALCAÑICES 5 Jul La Salud + 17 Aug San Roque (localities Alcorcillo, Santa Ana '27 y 28 de julio', "
        "Vivinera); ARQUILLINOS 30 Jan + 7 Aug San Tirso de Verano; AYOÓ DE VIDRIALES/Congosta de Vidriales "
        "printed '2 de julio Corpus Christi'; BERMILLO DE SAYAGO 7 May + 6 Aug 'Fiesta Local': all match.")

if __name__ == "__main__":
    main()
