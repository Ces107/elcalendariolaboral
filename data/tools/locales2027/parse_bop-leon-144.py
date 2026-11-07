"""BOP León 144 (31-VII-2026), CVE BOP-LE-2026-144033: Resolución de 20 de julio de 2026 de la
Oficina Territorial de Trabajo, fiestas locales 2027 (annex pages 3-17).

The annex fonts have no ToUnicode map: text is decoded glyph by glyph (glyphdecode via
cyl_util.spans(decode=True)). Layout, by x of the first span of each printed line:
  x<100  'MUNICIPIO: days' | 'Para todo el Municipio: days' | 'Resto de las localidades...: days'
         | continuation of the previous text
  x>=100 'Locality[:] days' | continuation (lowercase start, no date right after a short name)
Municipality days = its own line + 'Para todo el Municipio'; localities go to 'localities'.
Usage: python -I parse_bop-leon-144.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-leon-144"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de León. Resolución de 20 de julio de 2026, por la que se fijan las Fiestas Locales de los distintos Municipios de la Provincia de León para el año 2027 (BOP León núm. 144, 31-VII-2026, CVE BOP-LE-2026-144033)",
    "url": "https://bop.dipuleon.es/export/sites/bop/.galleries/Documentos-Anuncios-en-PDF/firmado-1785473203697-final-5ba4d1de.pdf",
    "published": "2026-07-31",
    "region": "castilla-y-leon",
}
PARA_TODO = re.compile(r"^Para\s+todo\s+(?:el|del)\s+municipio\s*:?\s*", re.I)
RESTO = re.compile(r"^Resto de las localidades del municipio\s*:\s*", re.I)
# pages 10-11 print 'PONFERRADA 8 de septiembre...' without the colon
MUNI = re.compile(r"^([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ .'()-]+?)\s*(?::|(?=\s+(?:Para todo|\d)))\s*(.*)$")
DAYSTART = r"\d{1,2}(?:\s*y\s*\d{1,2})?\s+de\s+[a-záéíóú]+"
LOC = re.compile(r"^([A-ZÁÉÍÓÚÑ][^:\d()]*?)(?:\s*:\s*|\s+)(" + DAYSTART + r".*)$")  # 'Dueñas:15 de mayo' has no space
MOVED = re.compile(r"(\d{1,2}) de ([a-záéíóú]+)([^()]*?)\(\s*se traslada al (?:día )?(\d{1,2}) de ([a-záéíóú]+)\s*\)", re.I)


def is_loc(t):
    m = LOC.match(t)
    if not m:
        return None
    pre = m.group(1).strip()
    if re.search(r"(?:\s|^)(?:y|e|de|del|la|el)$", pre) or pre.endswith(","):
        return None
    return m


def days(text):
    """-> [{'date','name'}] from free text; '(se traslada al X)' replaces its date."""
    text = MOVED.sub(lambda m: f"{m.group(4)} de {m.group(5)}{m.group(3)}(traslado del {m.group(1)} de {m.group(2)})", text)
    return [{"date": d, "name": n} for d, n in cu.parse_free(text)]


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    by_name = {n: c for c, n in ine.by_code.items() if c[:2] == "24"}
    for printed, official in [("CARRIZO DE LA RIBERA", "Carrizo"), ("La VECILLA DE CURUEÑO", "Vecilla, La"),
                              ("MATANZA DE LOS OTEROS", "Matanza")]:
        ine.add_manual("24", printed, by_name[official])
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    ents, cur, started = [], None, False
    for pn in range(2, len(doc)):
        for y, ss in cu.lines(cu.spans(doc, pn, decode=True)):
            ss = [s for s in ss if s[0] < 560]  # right-margin CVE / page strip
            if not ss:
                continue
            t, x = cu.text_of(ss), ss[0][0]
            if "CALENDARIO DE FIESTAS LOCALES PARA EL AÑO 2027" in t:
                started = True
                continue
            if not started or t.startswith("Boletín núm. 144") or set(t) <= {"�", " "}:
                continue
            if x < 100:
                if PARA_TODO.match(t):
                    cur = {"kind": "all", "text": PARA_TODO.sub("", t)}
                    ents[-1]["parts"].append(cur)
                    continue
                if RESTO.match(t):
                    cur = {"kind": "loc", "name": "Resto de las localidades", "text": RESTO.sub("", t)}
                    ents[-1]["parts"].append(cur)
                    continue
                m = MUNI.match(t)
                if m and m.group(1).strip().upper() == m.group(1).strip():
                    rest = m.group(2)
                    ents.append({"name": m.group(1).strip(), "parts": []})
                    if PARA_TODO.match(rest):
                        cur = {"kind": "all", "text": PARA_TODO.sub("", rest)}
                    else:
                        cur = {"kind": "head", "text": rest}
                    ents[-1]["parts"].append(cur)
                    continue
                cur["text"] += " " + t  # continuation at municipality indent
                continue
            m = is_loc(t)
            if m:
                cur = {"kind": "loc", "name": m.group(1).strip(), "text": m.group(2)}
                ents[-1]["parts"].append(cur)
            else:
                cur["text"] += " " + t
    doc.close()

    recs = []
    for e in ents:
        hol, notes = [], []
        locs = []
        for p in e["parts"]:
            hs = days(p["text"])
            if p["kind"] == "loc":
                locs.append({"muni": e["name"], "locality": p["name"], "holidays": hs})
                continue
            if not hs and p["text"].strip():
                notes.append(f"The bulletin gives '{cu.clean(p['text'])}' instead of a date; that day is left out.")
            hol += hs
            if p["kind"] == "all" and any(q["kind"] == "head" for q in e["parts"]) and hs:
                notes.append("One day is set for the whole municipality ('Para todo el Municipio'); the other "
                             "listed day is that of the main town.")
        recs.append({"muni": e["name"], "locality": None, "holidays": hol, "note": " ".join(notes)})
        recs += locs
    rows = cu.build_rows(ine, "24", recs)
    miss = common.coverage(ine, rows, ["24"])
    print("not in bulletin:", len(miss), [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOT, extra={"not_listed": [c for c, _ in miss]})


SPOT = ("2026-11-07: annex decoded glyph by glyph and read by line indent. Re-read against the decoded "
        "page text: LEÓN 24 Jun San Juan + 5 Oct San Froilán; ACEBEDO 7 Dec + 26 Jul for the whole municipality "
        "(La Uña 9 Jul, Liegos 25 Jun); BAÑEZA (LA) 9 Feb Carnaval + 17 Aug San Roque (moved from the 16th); "
        "SOTO Y AMÍO 8 Dec 'Se traslada al 9 de diciembre' -> 9 Dec; Quintana de Rueda (Valdepiélago) 15 May "
        "'se traslada al 14 de mayo' -> 14 May; SANTA MARÍA DEL MONTE DE CEA prints a rule ('primer lunes...') "
        "instead of a date: left out. All match.")

if __name__ == "__main__":
    main()
