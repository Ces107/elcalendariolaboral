"""Segovia province 2026 local holidays: Anuncio/Acuerdo de 16-9-2025 de la Oficina Territorial de Trabajo de Segovia,
"Fiestas locales de la provincia de Segovia para el año 2026" (BOP Segovia núm. 113, 19-9-2025), full issue hosted by
the Junta de Castilla y León (Trabajo y Prevención, 'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/125/489/06%20BOP%20FIESTAS%20LOCALES%20SEGOVIA%2026,0.pdf
Run:
    python -E -P data/tools/loc2026_bop-segovia-2026.py <downloaded.pdf>

Annex table "LOCALIDAD | FECHA | FESTIVIDAD | FECHA | FESTIVIDAD" with dd.mm.yyyy dates; rows starting with "–" are
localities (entidades locales menores) of the municipality above. A festividad that wraps continues on the next line.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "40"
SOURCE = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Segovia. Fiestas locales de la provincia de "
             "Segovia para el año 2026 (acuerdo de 16-9-2025, BOP Segovia núm. 113, de 19-9-2025)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/125/489/06%20BOP%20FIESTAS%20LOCALES%20SEGOVIA"
           "%2026,0.pdf",
    "published": "2025-09-19",
}
# Abbreviated names in the bulletin (INE checked by hand in data/municipios.json)
ALIAS = {"ALDEALENGUA DE STA. MARÍA": "40008", "FUENTE DE STA. CRUZ": "40082", "FUENTE EL OLMO DE FDÑA.": "40083",
         "FUENTESAÚCO DE FDÑA.": "40089", "MARTÍN MUÑOZ POSADAS": "40121", "MONTEJO VEGA SERREZUELA": "40130",
         "REAL SITIO DE S. ILDEFONSO": "40181", "RIAGUAS DE S. BARTOLOMÉ": "40168", "S. CRISTÓBAL DE CUÉLLAR": "40177",
         "S. CRISTÓBAL DE SEGOVIA": "40906", "SANTA Mª LA REAL DE NIEVA": "40185", "SANTIUSTE S. JUAN BAUTISTA": "40189"}
# PECHARROMÁN (also printed as a locality of Valtiendas) and TEJARES are not municipalities: left in unmatched
D = re.compile(r"(\d{2})\.(\d{2})\.(\d{4})")


SMALL = {"de", "del", "la", "las", "los", "el", "y", "e", "en", "a"}


def recase(s):
    """'CASTRILLO DE MURCIA' -> 'Castrillo de Murcia'"""
    words = s.strip().lower().split()
    return " ".join(w if (i and w in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def rows(page):
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip() and 60 <= s["bbox"][0] < 540:
                    spans.append(((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0], s["text"]))
    spans.sort()
    out = []
    for y, x, t in spans:
        if out and abs(out[-1][0] - y) < 3:
            out[-1][1].append((x, t))
        else:
            out.append([y, [(x, t)]])
    return [(y, sorted(c)) for y, c in out]


def cell(txt):
    """'24.06.2026    San Juan' -> ('2026-06-24', 'San Juan'); '' -> None"""
    txt = re.sub(r"\s+", " ", txt).strip()
    if not txt:
        return None
    m = D.match(txt)
    assert m, txt
    assert m.group(3) == "2026", txt
    return f"2026-{m.group(2)}-{m.group(1)}", txt[m.end():].strip()


def entries(pdf):
    started, last = False, None
    for page in pymupdf.open(pdf):
        if started and "LOCALIDAD" not in page.get_text():
            return  # the annex is over (the rest of the issue is other notices)
        for y, cells in rows(page):
            loc = " ".join(t.strip() for x, t in cells if x < 205).strip()
            c1 = " ".join(t.strip() for x, t in cells if 205 <= x < 355)
            c2 = " ".join(t.strip() for x, t in cells if 355 <= x < 540)
            if loc == "LOCALIDAD":
                started = True
                continue
            if not started or loc.startswith(("www.", "Núm.", "Boletín Oficial", "BOPS")) or "Documento firmado" in c2:
                continue
            if loc and D.match(c1.strip()):
                last = [re.sub(r"\s+", " ", loc), cell(c1), cell(c2)]
                yield last
            elif not loc and last and (c1.strip() or c2.strip()) and not D.search(c1 + c2):
                # wrapped festividad: append to the name of the column it sits in
                for i, extra in ((1, c1), (2, c2)):
                    if extra.strip() and last[i]:
                        last[i] = (last[i][0], (last[i][1] + " " + extra.strip()).strip())
            elif loc or D.search(c1 + c2):
                print("UNEXPECTED ROW (skipped):", repr(loc), repr(c1), repr(c2))


def main(pdf):
    mt = Matcher()
    by_ine, unmatched, cur = {}, [], None
    raw = list(entries(pdf))  # materialise first: wrapped names are patched into the yielded lists afterwards
    items = [(n, [p for p in (a, b) if p]) for n, a, b in raw]
    for name, pairs in items:
        hol = [{"date": d, "name": n} for d, n in sorted(dict(pairs).items())]
        if name.startswith(("–", "-")):
            assert cur, name
            rec = by_ine[cur]
            rec.setdefault("nucleos", []).append({"name": recase(name.lstrip("–- ").strip()), "holidays": hol})
            rec["note"] = "The list also gives days for localities of the municipality; see nucleos."
            continue
        ine = ALIAS.get(name) or mt.match(name, province=PROV)
        if not ine:
            unmatched.append(f"{name}: {pairs}")
            cur = None
            continue
        assert ine not in by_ine, name
        by_ine[ine] = {"holidays": hol}
        if len(hol) != 2:
            by_ine[ine]["note"] = f"The list gives {len(hol)} day(s) for the municipality."
        cur = ine
    missing = [f"{m['ine']} {m['name']}: not listed" for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("not listed:", len(missing))
    write_part("bop-segovia-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(sys.argv[1])
