"""Salamanca province 2026 local holidays: Acuerdo de 16-9-2025 de la Oficina Territorial de Trabajo de Salamanca
(BOP Salamanca núm. 181, 19-9-2025, CVE BOP-SA-20250919-018), copy hosted by the Junta de Castilla y León (Trabajo y
Prevención, 'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/189/931/05%20BOP%20FIESTAS%20LOCALES%20SALAMANCA%2026,0.pdf
Run:
    python -E -P data/tools/loc2026_bop-salamanca-2026.py <downloaded.pdf>

Annex = 2-column table (ENTIDAD LOCAL | FECHA, e.g. "23 de enero y 4 de mayo"), dates only, read by printed row.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "37"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
MES = {m: i for i, m in enumerate(MESES, 1)}
SOURCE = {
    "title": "Acuerdo de 16 de septiembre de 2025, de la Oficina Territorial de Trabajo de Salamanca, para la "
             "determinación de las fiestas locales, a efectos laborales, en los municipios de esta provincia (BOP "
             "Salamanca núm. 181, de 19-9-2025, CVE BOP-SA-20250919-018)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/189/931/05%20BOP%20FIESTAS%20LOCALES%20SALAMANCA"
           "%2026,0.pdf",
    "published": "2025-09-19",
}
ALIAS = {"BÓVEDA DE RIO ALMAR": "37057", "CRISTÓBAL DE LA SIERRA": "37112", "MASUECO DE LA RIBERA": "37184",
         "VENTOSA DE RÍO ALMAR": "37348"}
# ESCUERNAVACAS is printed as its own row but is not a municipality (entidad local menor): left in unmatched


def rows(page):
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip():
                    spans.append(((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0], s["text"]))
    spans.sort()
    out = []
    for y, x, t in spans:
        if out and abs(out[-1][0] - y) < 3:
            out[-1][1].append((x, t))
        else:
            out.append([y, [(x, t)]])
    return [(y, sorted(c)) for y, c in out]


def dates(txt):
    """'23 de enero y 4 de mayo' / '8 y 9 de septiembre' / '6 julio y 7 de julio' -> sorted ISO dates"""
    out, pending = [], []
    for num, mes in re.findall(r"(\d{1,2})(?:\s+(?:de\s+)?(" + "|".join(MESES) + r"))?", txt.lower()):
        pending.append(int(num))
        if mes:
            out += [f"2026-{MES[mes]:02d}-{d:02d}" for d in pending]
            pending = []
    assert not pending and out, txt
    return sorted(set(out))


def entries(pdf):
    started = False
    for page in pymupdf.open(pdf):
        for y, cells in rows(page):
            name = " ".join(t.strip() for x, t in cells if 100 <= x < 300).strip()
            fecha = " ".join(t.strip() for x, t in cells if 300 <= x < 520).strip()
            if name == "ENTIDAD LOCAL":
                started = True
                continue
            if started and name and fecha and not name.startswith("BOLETÍN OFICIAL"):
                yield re.sub(r"\s+", " ", name), fecha


def main(pdf):
    mt = Matcher()
    by_ine, unmatched = {}, []
    for name, fecha in entries(pdf):
        ine = ALIAS.get(name) or mt.match(name, province=PROV)
        if not ine:
            unmatched.append(f"{name}: {fecha}")
            continue
        assert ine not in by_ine, (name, ine)
        ds = dates(fecha)
        rec = {"holidays": [{"date": d, "name": ""} for d in ds]}
        if len(ds) != 2:
            rec["note"] = f"The agreement gives {len(ds)} day(s): '{fecha}'."
        by_ine[ine] = rec
    missing = [f"{m['ine']} {m['name']}: not listed" for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("not listed:", len(missing))
    write_part("bop-salamanca-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(sys.argv[1])
