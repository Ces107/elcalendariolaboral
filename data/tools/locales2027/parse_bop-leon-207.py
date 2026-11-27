"""BOP León 207 (30-X-2026), CVE BOP-LE-2026-207028: Resolución complementaria de la Oficina
Territorial de Trabajo de León (29-X-2026) to the Resolución de 20-VII-2026 (BOP 144), fiestas
locales 2027 (whole-bulletin pages 60-65).

PRIMERO: 'Anexo complementario' with municipalities that BOP 144 did not list.
SEGUNDO: three corrections of BOP 144 (Robles de la Valcueva, Matallana de Torío: 16 -> 17 Aug;
Brazuelo: 17 -> 23 Aug; Candanedo de Boñar, Vegaquemada: adds 26 Jul Santa Ana). The corrected
municipalities are re-emitted whole from the BOP 144 row in data/locales-2027-all.json.

The fonts here have a ToUnicode map (no glyph decoding). Lines are read by text, not indent
(indents drift on pages 63-65): 'UPPER NAME: days' = municipality, 'Mixed name: days' = locality,
'Para todo el municipio: days' = whole-municipality day, anything else = continuation.
Usage: python -I parse_bop-leon-207.py <workdir>
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-leon-207"
META = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de León. Resolución complementaria de la de 20 de julio de 2026, por la que se fijan las Fiestas Locales de los distintos Municipios de la provincia de León para el año 2027 (BOP León núm. 207, 30-X-2026, CVE BOP-LE-2026-207028)",
    "url": "https://bop.dipuleon.es/export/sites/bop/.galleries/Documentos-BOPs-en-PDF/bop-30_10_2026-4632db0a-d39d-11f1-affd-dd38f9a6a5be-1793339192595.pdf",
    "published": "2026-10-30",
    "region": "castilla-y-leon",
}
PARA_TODO = re.compile(r"^Para\s+todo\s+(?:el|del)\s+municipio\s*:\s*", re.I)
HEAD = re.compile(r"^([A-ZÁÉÍÓÚÑÜ][A-ZÁÉÍÓÚÑÜ .'()-]+?)\s*:\s*(.*)$")
LOC = re.compile(r"^([A-ZÁÉÍÓÚÑ][^:\d]*?)\s*:\s*(.*)$")
SKIP = re.compile(r"^(Página \d|CVE del|Verificable|Boletín núm|Delegación Territorial|Oficina Territorial|"
                  r"C/ Fraga|COPIA AUTENTICA|Fecha Firma|Firmado:|Acceda a la|Viernes 30|\d$)")
SPOT = ("2026-11-27: annex re-read against pdftotext of pages 62-65, independently of the parser: "
        "ASTORGA 23 Jul + 23 Aug; CEA 17 Jul + 15 May for the whole municipality (Sahelices del Rio 17 Aug); "
        "PUEBLA DE LILLO 5 Aug + 14 May (Solle 13 Aug, moved from the 16th); SANTIAGO MILLAS 26 Jul + 9 Feb; "
        "VILLABLINO 17 Aug + 4 Dec (13 localities); VILLAMOL 3 Aug + 15 May, Villapeceñil prints a rule "
        "('tercer lunes después de la Pascua...') instead of a date; ZOTES DEL PÁRAMO 15 May + 3 May. "
        "Corrections in SEGUNDO checked on page 60-61. All match.")


def days(text):
    # 'Solle: 13 de agosto, por traslado del 16 de agosto, San Roque' -> drop the moved-from date
    text = re.sub(r",?\s*por traslado del (?:domingo |lunes )?\d{1,2} de [a-záéíóú]+", "", text)
    return [{"date": d, "name": n} for d, n in cu.parse_free(text)]


def corrections(base):
    m = base["municipios"]
    out = []

    def row(code, holidays, locs, note):
        v = m[code]
        assert v["source"] == "bop-leon-144", (code, v["source"])
        r = {"name": v["name"], "cpro": "24", "ine": code, "match": "base", "holidays": holidays,
             "status": "boletin", "note": note}
        if locs is not None:
            r["localities"] = locs
            r["note"] = (note + " " + cu.sub_note([(l["name"], l["holidays"]) for l in locs])).strip()
        return r

    # Brazuelo (24023): 17 Aug -> 23 Aug
    v = m["24023"]
    hs = [dict(h) for h in v["holidays"]]
    assert [h["date"] for h in hs] == ["2027-07-23", "2027-08-17"], hs
    hs[1] = {"date": "2027-08-23", "name": None}
    out.append(row("24023", hs, None, "BOP León 207 (30-X-2026) corrects BOP 144: 23 Aug instead of 17 Aug."))
    # Matallana de Torío (24098): locality Robles de la Valcueva 16 -> 17 Aug
    v = m["24098"]
    locs = json.loads(json.dumps(v["localities"]))
    hit = [l for l in locs if l["name"] == "Robles de la Valcueva"]
    assert len(hit) == 1 and hit[0]["holidays"][0]["date"] == "2027-08-16", hit
    hit[0]["holidays"][0]["date"] = "2027-08-17"
    out.append(row("24098", v["holidays"], locs,
                   "One day is set for the whole municipality ('Para todo el Municipio'); the other listed day "
                   "is that of the main town. BOP León 207 (30-X-2026) moves Robles de la Valcueva from 16 to 17 Aug."))
    # Vegaquemada (24199): Candanedo de Boñar adds 26 Jul Santa Ana
    v = m["24199"]
    locs = json.loads(json.dumps(v["localities"]))
    hit = [l for l in locs if l["name"].startswith("Candanedo de Bo")]
    assert len(hit) == 1 and len(hit[0]["holidays"]) == 1, hit
    hit[0]["holidays"].append({"date": "2027-07-26", "name": "Santa Ana"})
    out.append(row("24199", v["holidays"], locs,
                   "BOP León 207 (30-X-2026) adds 26 Jul (Santa Ana) for Candanedo de Boñar."))
    return out


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    doc = pymupdf.open(os.path.join(W, "dl", SID, "bop.pdf"))
    ents, cur, started, done = [], None, False, False
    for pn in range(59, 65):
        for y, ss in cu.lines(cu.spans(doc, pn)):
            ss = [s for s in ss if s[0] < 430 or not re.match(r"(Página|CVE|Verificable)", s[4].strip())]
            t = cu.text_of(ss).replace("•", " ").strip()  # page-edge bullet marks
            t = " ".join(t.split())
            if not t:
                continue
            if "CALENDARIO DE FIESTAS LOCALES PARA EL AÑO 2027" in t:
                started = True
                continue
            if not started or done or SKIP.match(t):
                continue
            if PARA_TODO.match(t):
                cur = {"kind": "all", "text": PARA_TODO.sub("", t)}
                ents[-1]["parts"].append(cur)
                continue
            m = HEAD.match(t)
            if m and m.group(1).strip().upper() == m.group(1).strip():
                ents.append({"name": m.group(1).strip(), "parts": []})
                cur = {"kind": "head", "text": m.group(2)}
                ents[-1]["parts"].append(cur)
                continue
            m = LOC.match(t)
            if m:
                cur = {"kind": "loc", "name": m.group(1).strip(), "text": m.group(2)}
                ents[-1]["parts"].append(cur)
                continue
            cur["text"] += " " + t
    doc.close()

    recs = []
    for e in ents:
        hol, notes, locs = [], [], []
        for p in e["parts"]:
            hs = days(p["text"])
            if p["kind"] == "loc":
                if not hs:
                    locs.append({"muni": e["name"], "locality": p["name"], "holidays": [],
                                 "note": f"The bulletin gives '{cu.clean(p['text'])}' instead of a date."})
                else:
                    locs.append({"muni": e["name"], "locality": p["name"], "holidays": hs})
                continue
            hol += hs
            if p["kind"] == "all" and hs:
                notes.append("One day is set for the whole municipality ('Para todo el municipio'); the other "
                             "listed day is that of the main town.")
        notes.insert(0, "Complementary list to BOP León 144.")
        recs.append({"muni": e["name"], "locality": None, "holidays": hol, "note": " ".join(notes)})
        recs += locs
    rows = cu.build_rows(ine, "24", recs)
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "locales-2027-all.json"),
              encoding="utf-8") as f:
        base = json.load(f)
    rows += corrections(base)
    for r in rows:
        print(r["ine"], r["name"], [h["date"] for h in r["holidays"]], len(r.get("localities", [])))
    common.save_parsed(W, SID, META, rows, SPOT)


if __name__ == "__main__":
    main()
