"""Valladolid province 2026 local holidays: Resolución de 17-9-2025 de la Oficina Territorial de Trabajo de Valladolid
(BOP Valladolid núm. 2025/179, 19-9-2025), copy hosted by the Junta de Castilla y León (Trabajo y Prevención,
'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/635/169/08%20BOP%20FIESTAS%20LOCALES%20VALLADOLID%2026,0.pdf
Run:
    python -E -P data/tools/loc2026_bop-valladolid-2026.py <downloaded.pdf>

Annex = 3-column table (Ayuntamiento | 1ª Fiesta | 2ª Fiesta), dates only. Read by word coordinates per printed row.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "47"
MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
TYPO = {"deptiembre": "septiembre"}
SOURCE = {
    "title": "Resolución de 17 de septiembre de 2025, de la Oficina Territorial de Trabajo de Valladolid, para la "
             "determinación de las fiestas locales, a efectos laborales, en los municipios de la provincia de Valladolid "
             "(BOP Valladolid núm. 2025/179, de 19-9-2025)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/635/169/08%20BOP%20FIESTAS%20LOCALES%20VALLADOLID"
           "%2026,0.pdf",
    "published": "2025-09-19",
}
# Bulletin spellings the matcher misses (INE checked by hand in data/municipios.json)
ALIAS = {"BAHABÓN DE VALCORBA": "47012", "CASTREJON": "47037", "CASTROPONCE DE VALDERAUEY": "47046",
         "CORCOS DEL VALLE": "47055", "MURIEL DE ZAPARDIEL": "47100", "SAN LLORENTE DEL VALLE": "47143",
         "SAN SALVADOR DE HORNIJA": "47151", "VILLACO DE ESGUEVA": "47200", "VILLAFUERTE DE ESGUEVA": "47206"}
# Rows that are entidades locales menores, not municipalities (the bulletin does not name their municipality): skipped
ELM = {"ALDEALBAR", "FONCASTÍN", "GORDALIZA DE LA LOMA", "LA SANTA ESPINA", "SAN BERNARDO", "SANTIAGO DEL ARROYO",
       "TORRECILLA DEL VALLE"}
CELL = re.compile(r"(\d{1,2} de [a-z]+|No comunicada)", re.I)


def rows(page, xmin=60):
    """Spans grouped by printed line: [(y, [(x0, text), ...])] sorted top-down, left-right."""
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip() and s["bbox"][0] >= xmin:
                    spans.append(((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0], s["text"]))
    spans.sort()
    out = []
    for y, x, t in spans:
        if out and abs(out[-1][0] - y) < 3:
            out[-1][1].append((x, t))
        else:
            out.append([y, [(x, t)]])
    return [(y, sorted(c)) for y, c in out]


def one_date(txt):
    txt = txt.strip().lower()
    for a, b in TYPO.items():
        txt = txt.replace(a, b)
    m = re.fullmatch(r"(\d{1,2}) de (" + "|".join(MES) + ")", txt)
    assert m, txt
    return f"2026-{MES[m.group(2)]:02d}-{int(m.group(1)):02d}"


def entries(pdf):
    doc = pymupdf.open(pdf)
    started = False
    for page in doc:
        for y, cells in rows(page):
            cols = {"name": [], "f1": [], "f2": []}
            for x, t in cells:
                cols["name" if x < 260 else "f1" if x < 350 else "f2"].append(t.strip())
            name, f1, f2 = (" ".join(cols[k]).strip() for k in ("name", "f1", "f2"))
            if name == "Ayuntamiento" and f1 == "1ª Fiesta":
                started = True
                continue
            if not started or not (CELL.fullmatch(f1) and CELL.fullmatch(f2)):
                continue
            yield re.sub(r"\s+", " ", name), f1, f2
        if started and "VALLADOLID" in page.get_text() and "ZARATAN" in page.get_text():
            break


def main(pdf):
    mt = Matcher()
    by_ine, unmatched, nocom = {}, [], []
    for name, f1, f2 in entries(pdf):
        if name in ELM:
            unmatched.append(f"{name} (entidad local menor): {f1}; {f2}")
            continue
        if f1 == f2 == "No comunicada":
            nocom.append(name)
            continue
        ine = ALIAS.get(name) or mt.match(name, province=PROV)
        if not ine:
            unmatched.append(f"{name}: {f1}; {f2}")
            continue
        assert ine not in by_ine, (name, ine)
        ds = sorted({one_date(f1), one_date(f2)})
        by_ine[ine] = {"holidays": [{"date": d, "name": ""} for d in ds]}
    print("no comunicada:", len(nocom), nocom)
    write_part("bop-valladolid-2026", SOURCE, by_ine, region="castilla-y-leon",
               unmatched=unmatched + [f"{n}: no comunicada" for n in nocom])


if __name__ == "__main__":
    main(*sys.argv[1:])
