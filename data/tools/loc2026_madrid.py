"""Comunidad de Madrid 2026 local holidays: Resolución de 2-12-2025 de la DG de Trabajo (BOCM 296, 12-12-2025) and its
two partial modifications (Resoluciones de 15-12-2025, BOCM 309 of 29-12-2025, and 22-12-2025, BOCM 6 of 8-1-2026).

Download (outside the repo) the three PDFs from bocm.es:
    BOCM-20251212-34.PDF  BOCM-20251229-19.PDF  BOCM-20260108-18.PDF
Run (base first, then modifications in order; later ones override):
    python -E -P data/tools/loc2026_madrid.py BOCM-20251212-34.PDF BOCM-20251229-19.PDF BOCM-20260108-18.PDF
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
SOURCE = {
    "title": "Resolución de 2 de diciembre de 2025, de la Dirección General de Trabajo, por la que se declaran las fiestas "
             "laborales de ámbito local en la Comunidad de Madrid para el año 2026 (BOCM núm. 296, de 12-12-2025), "
             "modificada por las Resoluciones de 15-12-2025 (BOCM núm. 309, de 29-12-2025) y de 22-12-2025 (BOCM núm. 6, "
             "de 8-1-2026)",
    "url": "https://www.bocm.es/boletin/CM_Orden_BOCM/2025/12/12/BOCM-20251212-34.PDF",
    "published": "2025-12-12",
    "modifications": ["https://www.bocm.es/boletin/CM_Orden_BOCM/2025/12/29/BOCM-20251229-19.PDF",
                      "https://www.bocm.es/boletin/CM_Orden_BOCM/2026/01/08/BOCM-20260108-18.PDF"],
}
# Entries that are núcleos of a municipality, not municipalities: núcleo -> INE of the municipality
NUCLEOS = {"Mataelpino": "28023", "Cerceda": "28023",  # El Boalo (Boalo, Cerceda y Mataelpino)
           "El Espartal": "28168"}  # El Vellón
# Bulletin spellings that differ from INE
ALIAS = {"Berzosa de Lozoya": "28020", "Braojos de la Sierra": "28024", "Buitrago de Lozoya": "28027",
         "Valdetorres del Jarama": "28164"}
# Valdeolmos-Alalpardo: "15 de mayo y 10 de agosto (Valdeolmos) y 24 de agosto (Alalpardo)"
SPLIT = {"28162": {"common": ["2026-05-15"], "Valdeolmos": ["2026-05-15", "2026-08-10"],
                   "Alalpardo": ["2026-05-15", "2026-08-24"]}}


def dates(txt):
    """'11 y 14 de septiembre' / '3 de febrero y 15 de mayo' / '14 diciembre' -> ['2026-09-11', ...]"""
    out, pending = [], []
    for num, mes in re.findall(r"(\d{1,2})(?:\s+(?:de\s+)?(" + "|".join(MES) + r"))?", txt):
        pending.append(int(num))
        if mes:
            out += [f"2026-{MES[mes]:02d}-{d:02d}" for d in pending]
            pending = []
    assert not pending, txt
    return sorted(set(out))


def entries(pdf):
    text = " ".join(p.get_text() for p in pymupdf.open(pdf))
    text = re.sub(r"\s+", " ", text)
    for chunk in text.split("— ")[1:]:
        chunk = chunk.split(". ")[0].rstrip(".")
        m = re.match(r"([^:\d]+?):? (\d.*|no comunicado.*)$", chunk)
        assert m, chunk
        yield m.group(1).strip(), m.group(2).strip()


def main(*pdfs):
    mt = Matcher()
    by_ine, unmatched, nucleos = {}, [], {}
    names = {}
    for pdf in pdfs:
        for name, rest in entries(pdf):
            if name in NUCLEOS:
                nucleos.setdefault(NUCLEOS[name], {})[name] = rest
                continue
            ine = ALIAS.get(name) or mt.match(name, province="28")
            if not ine:
                unmatched.append(f"{name}: {rest}")
                continue
            names[ine] = name
            if "no comunicado" in rest:
                by_ine.pop(ine, None)
                continue
            if ine in SPLIT:
                assert "(Valdeolmos)" in rest and "(Alalpardo)" in rest, rest
                sp = SPLIT[ine]
                by_ine[ine] = {"holidays": [{"date": d, "name": ""} for d in sp["common"]],
                               "nucleos": [{"name": n, "holidays": [{"date": d, "name": ""} for d in sp[n]]}
                                           for n in ("Valdeolmos", "Alalpardo")],
                               "note": "15 May for the whole municipality; the second day differs: 10 August in "
                                       "Valdeolmos, 24 August in Alalpardo."}
                continue
            by_ine[ine] = {"holidays": [{"date": d, "name": ""} for d in dates(rest)]}
    for ine, ns in nucleos.items():
        rec = by_ine.setdefault(ine, {"holidays": []})
        rec["nucleos"] = [{"name": n, "holidays": [{"date": d, "name": ""} for d in dates(r)]} for n, r in ns.items()]
        rec["note"] = "The resolution also lists núcleos of the municipality with their own days; see nucleos."
    missing = [f"{m['ine']} {m['name']}: no communicated / not listed" for m in mt.munis
               if m["region"] == "madrid" and m["ine"] not in by_ine]
    write_part("bocm-2026", SOURCE, by_ine, region="madrid", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
