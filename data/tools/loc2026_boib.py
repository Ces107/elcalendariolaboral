"""Illes Balears 2026 local holidays: Resolución de la consejera de Trabajo, Función Pública y Diálogo Social de
25-9-2025 por la que se hace público el calendario laboral general y local para 2026 (BOIB núm. 129, 27-9-2025),
corrected by Resoluciones of 13-10-2025 (BOIB 139), 6-11-2025 (BOIB 150) and 27-1-2026 (BOIB 15, 31-1-2026).

Download (outside the repo) from https://www.caib.es/sites/calendarilaboral/es/aao_2026/ (the four PDFs, Spanish):
    main.pdf (archivopub id 529406), c1.pdf (531920), c2.pdf (536513), c3.pdf (546066)
Run: python -E -P data/tools/loc2026_boib.py main.pdf c1.pdf c2.pdf c3.pdf

Table: UPPERCASE first column = municipality; mixed-case = núcleo/parroquia of the municipality above it; empty first
column = second date of the entity above. The three corrections are short and applied from CORRECTIONS below; the
script asserts that each corrected text is present in its PDF.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
MES["juliol"] = 7
SOURCE = {
    "title": "Resolución de la consejera de Trabajo, Función Pública y Diálogo Social por la que se hace público el "
             "calendario laboral general y local para el año 2026 en el ámbito de las Illes Balears (BOIB núm. 129, de "
             "27-9-2025), con las correcciones de los BOIB núm. 139 (21-10-2025), 150 (13-11-2025) y 15 (31-1-2026)",
    "url": "https://www.caib.es/sites/calendarilaboral/es/aao_2026/",
    "published": "2025-09-27",
}
# (pdf index, text that must be in that pdf, entity, municipality-level?, new holidays)
CORRECTIONS = [
    (1, "25 de julio: San Jaime, Diada de Formentera", "FORMENTERA", None,
     [("2026-07-25", "San Jaime, Diada de Formentera"), ("2026-12-03", "San Francisco Javier")]),
    (2, "Parròquia de Sant Carles de Peralta", "SANTA EULÀRIA DES RIU", "Parròquia de Sant Carles de Peralta",
     [("2026-02-12", "festividad de Santa Eulària des Riu"), ("2026-11-04", "festividad de Sant Carles")]),
    (3, "8 de abril: romería del Cocó", "LLOSETA", None,
     [("2026-04-08", "romería del Cocó"), ("2026-09-08", "fiestas patronales")]),
    (3, "19 de octubre", "LLUCMAJOR", None, [("2026-09-29", "San Miguel"), ("2026-10-19", "")]),
]
DATE = re.compile(r"(\d{1,2}) (?:de |d')?(\w+)(?::\s*(.*))?$")


def table_rows(pdf):
    for p in pymupdf.open(pdf):
        for t in p.find_tables().tables:
            for r in t.extract():
                yield [(c or "").strip() for c in r[:2]]


def parse(pdf):
    """-> {MUNICIPALITY: {"holidays": [(date, name)], "nucleos": {name: [(date, name)]}}}"""
    out, muni, ent, prev_named, started = {}, None, None, False, False
    for name, val in table_rows(pdf):
        if name.startswith("2.1."):
            started = True
            continue
        if not started or re.match(r"^\d\.\d\.", name):
            continue
        lines = [x.strip() for x in val.split("\n") if x.strip()]
        name = name.replace("\n", " ")
        if name and name == name.upper() and re.search(r"[A-ZÀ-Ý]", name):
            muni, ent = name, None
            out[muni] = {"holidays": [], "nucleos": {}}
            target = out[muni]["holidays"]
            prev_named = True
        elif name:
            if ent is not None and len(out[muni]["nucleos"][ent]) == 1 and prev_named:
                # wrapped núcleo name ("Parròquies de Santa Eulària i" / "Puig d'en Valls")
                new = f"{ent} {name}"
                out[muni]["nucleos"][new] = out[muni]["nucleos"].pop(ent)
                ent = new
            else:
                ent = name.rstrip(":")
                out[muni]["nucleos"][ent] = []
            target = out[muni]["nucleos"][ent]
            prev_named = True
        else:
            prev_named = False
        for ln in lines:
            m = DATE.match(ln)
            if m and m.group(2).lower() in MES:
                target.append((f"2026-{MES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}", (m.group(3) or "").strip()))
    return out


def main(base, *corr):
    mt = Matcher()
    data = parse(base)
    texts = [None] + [re.sub(r"\s+", " ", " ".join(p.get_text() for p in pymupdf.open(c))) for c in corr]
    for idx, must, muni, ent, hs in CORRECTIONS:
        assert must in texts[idx], (idx, must)
        if ent:
            data[muni]["nucleos"][ent] = hs
        elif data[muni]["nucleos"] and not data[muni]["holidays"]:
            raise AssertionError(muni)
        else:
            data[muni]["holidays"] = hs
    out, unmatched = {}, []
    for muni, v in data.items():
        ine = mt.match(muni.title(), region="baleares") or mt.match(muni, region="baleares")
        if not ine:
            unmatched.append(muni)
            continue
        hs = {d: n for d, n in v["holidays"]}
        rec = {"holidays": [{"date": d, "name": n} for d, n in sorted(hs.items())]}
        nuc = [{"name": n, "holidays": [{"date": d, "name": x} for d, x in sorted(dict(h).items())]}
               for n, h in v["nucleos"].items() if h]
        notes = []
        if nuc:
            rec["nucleos"] = nuc
            notes.append("The resolution sets the days per núcleo/parroquia; see nucleos." if not hs else
                         "Some núcleos/parroquias have their own days; see nucleos.")
        if hs and len(hs) != 2:
            notes.append(f"The resolution lists {len(hs)} date(s) for the municipality.")
        if notes:
            rec["note"] = " ".join(notes)
        if hs or nuc:
            out[ine] = rec
    write_part("boib-2026", SOURCE, out, region="baleares", unmatched=unmatched)


if __name__ == "__main__":
    main(*sys.argv[1:])
