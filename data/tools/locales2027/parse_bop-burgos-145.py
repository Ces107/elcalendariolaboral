"""BOP Burgos 145 (4-VIII-2026), C.V.E. BOPBUR-2026-03251: Resolución de la Oficina Territorial de
Trabajo de Burgos (21-VII-2026), calendario de fiestas locales 2027 (annex pages 4-14).

One printed line per day: ENTIDAD LOCAL | DD/MM/YYYY | FESTIVIDAD (fonts decoded glyph by
glyph). Entities not in the INE municipality list are entidades locales menores whose parent
the bulletin does not give: kept apart in 'unassigned_localities'. 'FIESTA LOCAL' = no name.
Usage: python -I parse_bop-burgos-145.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-burgos-145"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Burgos. Resolución sobre calendario de fiestas locales, retribuidas y no recuperables, para el año 2027 (BOP Burgos núm. 145, 4-VIII-2026, C.V.E. BOPBUR-2026-03251)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/532/765/Publicacion%20Fiestas%20Locales%20-%20bopbur-2026-145.pdf?blobheader=application%2Fpdf%3Bcharset%3DUTF-8&blobnocache=true",
    "published": "2026-08-04",
    "region": "castilla-y-leon",
}
SPLIT = 280
# 'CARDEÑAJIMENO 17 /05/2027'; on a few lines the slash glyph decodes as a space ('15 05 2027')
ROW = re.compile(r"^(\d{1,2})\s*[/ ]\s*(\d{1,2})\s*[/ ]\s*(\d{4})\s*(.*)$")


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    for printed, official in MANUAL.items():
        ine.add_manual("09", printed, next(c for c, n in ine.by_code.items() if c[:2] == "09" and n == official))
    doc = pymupdf.open(os.path.join(W, "dl", SID, "jcyl.pdf"))
    order, ents, nodate, wrong, pending = [], {}, [], {}, None
    for pn in range(3, 14):
        for y, ss in cu.lines(cu.spans(doc, pn, decode=True)):
            t = cu.text_of(ss)
            if (not t or t.startswith(("boletín oficial", "burgos", "núm. 145", "diputación de burgos",
                                       "bopbur.", "ENTIDAD LOCAL", "– ")) or t in ("e", "A n E x O")):
                continue
            name = cu.clean(" ".join(s[4] for s in ss if s[0] < SPLIT))
            rest = cu.clean(" ".join(s[4] for s in ss if s[0] >= SPLIT))
            if not name:
                raise SystemExit(f"NO NAME p{pn + 1}: {t!r}")
            if not rest:  # long name wrapped onto the next line, which carries the date
                pending = name if not pending else pending + " " + name
                continue
            if pending:
                name = cu.clean(pending + " " + name)
                pending = None
            m = ROW.match(rest)
            if not m:
                raise SystemExit(f"BAD ROW p{pn + 1}: {t!r}")
            if int(m.group(3)) != common.YEAR:  # printed with another year: not a 2027 date, left out
                wrong.setdefault(name, []).append(f"{m.group(1)}/{m.group(2)}/{m.group(3)}")
                continue
            fest = cu.clean(m.group(4))
            h = {"date": common.iso(int(m.group(1)), int(m.group(2))),
                 "name": None if fest.upper() in ("FIESTA LOCAL", "") else cu.nice(fest)}
            name = re.sub(r"\s*\)", ")", re.sub(r"\(\s*", " (", name)).replace("  ", " ").strip()
            if name not in ents:
                order.append(name)
                ents[name] = []
            ents[name].append(h)
    doc.close()
    recs, unassigned = [], []
    for n in order:
        m = re.match(r"^(.*?)\s*\(([^)]+)\)\s*$", n)
        if m and m.group(2).strip().upper() not in ("EL", "LA", "LOS", "LAS"):
            # 'CITORES DEL PÁRAMO (SASAMÓN)': entidad local menor (municipality)
            recs.append({"muni": m.group(2).strip(), "locality": cu.nice(m.group(1).strip()), "holidays": ents[n]})
            continue
        code, _ = ine.match("09", cu.bulletin_name(n), fuzzy=False)
        note = "The annex gives one line per day; 'FIESTA LOCAL' means no festivity name."
        if n in wrong:
            note += (f" The bulletin also prints {', '.join(wrong[n])} (not a 2027 date): that day is left "
                     "out until a correction is published.")
        if code:
            recs.append({"muni": n, "locality": None, "holidays": ents[n], "note": note})
        else:
            unassigned.append({"name": n, "holidays": ents[n]})
    for n, ds in wrong.items():  # entity whose only days carry the wrong year
        if n not in ents:
            print("ONLY WRONG-YEAR DAYS:", n, ds)
    print("wrong year:", wrong)
    # one municipality printed under two spellings (Cillaperlata/Cillaperalta, Iglesias/Iglesas): one head
    merged, seen = [], {}
    for r in recs:
        code = ine.match("09", cu.bulletin_name(r["muni"]), fuzzy=False)[0] if not r["locality"] else None
        if code and code in seen:
            seen[code]["holidays"] += r["holidays"]
            seen[code]["note"] += f" One day is printed under the spelling '{r['muni']}'."
            continue
        if code:
            seen[code] = r
        merged.append(r)
    recs = merged
    rows = cu.build_rows(ine, "09", recs)
    miss = common.coverage(ine, rows, ["09"])
    nodate = sorted(set(nodate) - set(order))
    print("lines without a date:", nodate)
    print("unassigned (not INE municipalities):", [u["name"] for u in unassigned])
    print("not in bulletin:", len(miss))
    common.save_parsed(W, SID, META, rows, SPOT, extra={"not_listed": [c for c, _ in miss],
                                                        "unassigned_localities": unassigned,
                                                        "printed_without_date": nodate,
                                                        "wrong_year": wrong})


# bulletin spellings checked by eye against the INE list
MANUAL = {"CILLAPERALTA": "Cillaperlata",  # its 2nd day is printed with this misspelling
          "IGLESAS": "Iglesias",  # idem
          "ARCOS DE LA LLANA": "Arcos", "ARENILLAS DE RÍO PISUERGA": "Arenillas de Riopisuerga",
          "PERAL DEL ARLANZA": "Peral de Arlanza",
          "VILLARCAYO DE MERINDAD DE CASTILLA LA VIEJA": "Villarcayo de Merindad de Castilla la Vieja"}

SPOT = ("2026-11-07: annex decoded glyph by glyph, one line per day. Re-read against the decoded page "
        "text: ABAJAS 15/05 San Isidro + 14/09 La Cruz; ARANDA DE DUERO 13/09 + 14/09 'FIESTA LOCAL'; "
        "ARCOS DE LA LLANA 04/06 Curpillos + 29/06; BELORADO 26/08 San Vítores; BURGOS city (see row); "
        "CARAZO 23/08 + 29/12: all match.")

if __name__ == "__main__":
    main()
