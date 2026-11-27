"""BOP Zamora 130 (6-XI-2026), R-202602561: calendario complementario de fiestas locales 2027
(Oficina Territorial de Trabajo de Zamora, 3-XI-2026), for the councils that communicated their
days after BOP 87/88.

Annex 'localidad | día y mes | denominación' after the regional list: words grouped by printed
line (the font prints small caps as mixed case: names re-cased from upper case), name x<240 (one date starts at x=242: '- muga de alBa 8 de mayo y 24 septiembre'), date
240-385, festivity >=385. '- NAME' = locality of the municipality above.
Usage: python -I parse_bop-zamora-130.py <workdir>
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-zamora-130"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Zamora. Calendario complementario de fiestas locales para el año 2027 (BOP Zamora núm. 130, 6-XI-2026, R-202602561)",
    "url": "https://www.diputaciondezamora.es/opencms/export/sites/dipu-zamora/servicios/BOP/.Archivos/documentos/BOP/anuncios/2026/130/202602561.pdf",
    "published": "2026-11-06",
    "region": "castilla-y-leon",
}
C1, C2 = 240, 385
SKIP = ("BOLETÍN OFICIAL", "n.º 130", "pág.", "www.diputaciondezamora", "r-202602561", "Cód. Validación",
        "Verificación:", "Documento firmado", "localidad día")
NOTE = "Complementary list (councils that communicated their days after BOP Zamora 87/88)."

SPOT = ("2026-11-27: annex read by word coordinates; re-read against the PDF text: ALFARAZ DE SAYAGO 15 May "
        "+ 7 Oct (Viñuela 15 May + 8 Sep); BENAVENTE 5 Apr La Veguilla + 26 May Toro Enmaromado; LOSACINO "
        "1-2 Oct (Muga de Alba 8 May + 24 Sep); PUEBLA DE SANABRIA 8-9 Sep (Castellanos, Robledo, Ungilde); "
        "SANTA EUFEMIA DEL BARCO '6 mayo' + 16 Sep; TÁBARA 29 Mar + 17 Aug; VILLANUEVA DE LAS PERAS 15 May "
        "only: all match. Count: 39 municipalities printed in the annex.")


def fmt(hs, skip=None):
    drop = {x["date"] for x in skip["holidays"]} if skip else set()
    return " + ".join(x["date"] for x in hs if x["date"] not in drop)


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    by_name = {n: c for c, n in ine.by_code.items() if c[:2] == "49"}
    ine.add_manual("49", "MADERAL (EL)", by_name["Maderal, El"])
    ine.add_manual("49", "FERRERUELA DE TÁBARA", by_name["Ferreruela"])  # INE name: Ferreruela
    doc = pymupdf.open(os.path.join(W, "dl", "zamora", "202602561.pdf"))
    ents, started = [], False
    for pn in range(1, len(doc)):
        lines = {}
        for w in doc[pn].get_text("words"):
            if w[0] >= 540:
                continue
            lines.setdefault(round((w[1] + w[3]) / 2 / 2), []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            t = " ".join(w[4] for w in ws)
            if t.startswith("localidad día"):
                started = True
                continue
            if not started or t.startswith(SKIP):
                continue
            name = " ".join(w[4] for w in ws if w[0] < C1)
            date = " ".join(w[4] for w in ws if C1 <= w[0] < C2)
            den = " ".join(w[4] for w in ws if w[0] >= C2)
            if name:
                ents.append({"name": name, "raw": []})
            if date:
                ents[-1]["raw"].append([date, den])
            elif den:
                raise SystemExit(f"FESTIVITY WITHOUT DATE p{pn + 1}: {t!r}")
    doc.close()
    recs, muni = [], None
    for e in ents:
        hs = []
        for date, den in e["raw"]:
            pairs = cu.parse_free(date)
            if not pairs:
                raise SystemExit(f"BAD DATE {e['name']}: {date!r}")
            hs += [{"date": d, "name": cu.nice(cu.clean(den).upper()) or None} for d, _ in pairs]
        if not hs:
            raise SystemExit(f"NO DAYS {e['name']}")
        if e["name"].startswith("-"):
            recs.append({"muni": muni, "locality": cu.nice(e["name"].lstrip("- ").strip().upper()), "holidays": hs})
        else:
            muni = e["name"].upper()
            recs.append({"muni": muni, "locality": None, "holidays": hs, "note": NOTE})
    heads = [r for r in recs if not r["locality"]]
    print("municipalities:", len(heads), "localities:", len(recs) - len(heads))
    # A municipality BOP 88 already lists (one day only) gets its other day here ("nuevas
    # festividades"): keep BOP 88's day and localities so the merged row is complete.
    sp = importlib.util.spec_from_file_location("z88", os.path.join(HERE, "parse_bop-zamora-88.py"))
    z88 = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(z88)
    _, recs88 = z88.read_recs(W)
    code_of = lambda n: ine.match("49", cu.bulletin_name(n), fuzzy=False)[0]  # noqa: E731
    codes88 = {code_of(r["muni"]) for r in recs88 if not r["locality"]}
    for h in heads:
        c = code_of(h["muni"])
        if c in codes88:
            old = [r for r in recs88 if code_of(r["muni"]) == c]
            head88 = next(r for r in old if not r["locality"])
            h["holidays"] = sorted(head88["holidays"] + [x for x in h["holidays"] if x["date"] not in
                                                          {y["date"] for y in head88["holidays"]}],
                                   key=lambda x: x["date"])
            h["note"] = (f"{fmt(head88['holidays'])} from BOP Zamora 88; {fmt(h['holidays'], head88)} added by "
                         "this complementary list (BOP Zamora 130).")
            recs += [dict(r, muni=h["muni"]) for r in old if r["locality"]]
            print("completed from BOP 88:", h["muni"], h["holidays"])
    rows = cu.build_rows(ine, "49", recs)
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
