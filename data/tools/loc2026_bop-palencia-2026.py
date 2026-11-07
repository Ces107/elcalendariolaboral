"""Palencia province 2026 local holidays: Acuerdo de 12-9-2025 de la Oficina Territorial de Trabajo de Palencia de
determinación de las fiestas locales 2026, a efectos laborales (BOP Palencia núm. 112, 17-9-2025, anuncio 2535), copy
hosted by the Junta de Castilla y León (Trabajo y Prevención, 'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/358/890/04%20BOP%20FIESTAS%20LOCALES%20PALENCIA%2026,0.pdf
Run:
    python -E -P data/tools/loc2026_bop-palencia-2026.py <downloaded.pdf>

Annex table "MUNICIPIO | 1ª FIESTA | 2ª FIESTA", dates only; municipality names in capitals, its localities
(entidades locales menores) indented in mixed case below it with their own days. "No comunicado" = not communicated.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "34"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
MES = {m: i for i, m in enumerate(MESES, 1)}
SOURCE = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Palencia. Acuerdo de 12 de septiembre de 2025 de "
             "determinación de las fiestas locales 2026, a efectos laborales, en los municipios de la provincia de "
             "Palencia (BOP Palencia núm. 112, de 17-9-2025)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/358/890/04%20BOP%20FIESTAS%20LOCALES%20PALENCIA"
           "%2026,0.pdf",
    "published": "2025-09-17",
}
ALIAS = {"BUSTILLO DEL PÁRAMO": "34039", "LOMAS DE CAMPOS": "34096"}
CELL = re.compile(r"^(\d{1,2}\s+(?:de\s+)?(" + "|".join(MESES) + r")|No comunicad[oa])$", re.I)


def rows(page):
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip() and 90 <= s["bbox"][0] < 520:
                    spans.append(((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0], s["text"]))
    spans.sort()
    out = []
    for y, x, t in spans:
        if out and abs(out[-1][0] - y) < 3:
            out[-1][1].append((x, t))
        else:
            out.append([y, [(x, t)]])
    return [(y, sorted(c)) for y, c in out]


def iso(cell):
    m = CELL.match(cell.strip())
    assert m, cell
    if not m.group(2):
        return None
    return f"2026-{MES[m.group(2).lower()]:02d}-{int(cell.split()[0]):02d}"


def blocks(pdf):
    started, cur = False, None
    for page in pymupdf.open(pdf):
        for y, cells in rows(page):
            raw = "".join(t for x, t in cells if x < 260)
            name = re.sub(r"\s+", " ", raw).strip()
            f1 = " ".join(t.strip() for x, t in cells if 260 <= x < 400).strip()
            f2 = " ".join(t.strip() for x, t in cells if x >= 400).strip()
            if name == "MUNICIPIO":
                started = True
                continue
            if not started:
                continue
            if re.fullmatch(r"\d{3,5}", f2) and not name:  # anuncio number after the last row
                if cur:
                    yield cur
                return
            if not (f1 or f2):
                if name.isupper() and not name.startswith("BOP"):
                    if cur:
                        yield cur
                    cur = [name, None, []]  # municipality row without days of its own
                continue
            ds = [iso(c) for c in (f1, f2) if c]
            if raw[:1].isspace():
                cur[2].append((name, ds))
            else:
                if cur:
                    yield cur
                cur = [name, ds, []]
    if cur:
        yield cur


def hol(ds):
    return [{"date": d, "name": ""} for d in sorted({d for d in ds if d})]


def main(pdf):
    mt = Matcher()
    by_ine, unmatched, nocom = {}, [], []
    for name, own, locs in blocks(pdf):
        ine = ALIAS.get(name) or mt.match(name, province=PROV)
        if not ine:
            unmatched.append(f"{name}: {own} {locs}")
            continue
        assert ine not in by_ine, name
        loc_ok = [(n, ds) for n, ds in locs if any(ds)]
        if not (own and any(own)) and not loc_ok:
            nocom.append(name)
            continue
        rec = {"holidays": hol(own or [])}
        notes = []
        if loc_ok:
            rec["nucleos"] = [{"name": n, "holidays": hol(ds)} for n, ds in loc_ok]
            notes.append("The list also gives days for localities of the municipality; see nucleos." if rec["holidays"]
                         else "The list gives days only for localities of the municipality, not for the whole "
                              "municipality; see nucleos.")
        if own and len(rec["holidays"]) != 2:
            notes.append(f"The list gives {len(rec['holidays'])} day(s) for the municipality"
                         + (" (the other is 'No comunicado')." if None in own else "."))
        if notes:
            rec["note"] = " ".join(notes)
        by_ine[ine] = rec
    missing = [f"{m['ine']} {m['name']}: " + ("no comunicado" if m["ine"] in {ALIAS.get(n) or mt.match(n, province=PROV) for n in nocom}
                                              else "not listed")
               for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("no comunicado:", len(nocom), "missing total:", len(missing))
    write_part("bop-palencia-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(sys.argv[1])
