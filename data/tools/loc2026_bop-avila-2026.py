"""Ávila province 2026 local holidays: Anuncio de la Oficina Territorial de Trabajo de Ávila de 16-9-2025 (BOP Ávila
núm. 186, 26-9-2025, anuncio 1884/25; copy hosted by the Junta de Castilla y León, Trabajo y Prevención, 'Calendario
laboral 2026') plus the two complementary lists: anuncio 2399/25 (BOP núm. 231, 1-12-2025) and anuncio 0213/26 (BOP
núm. 23, 4-2-2026).

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/77/36/01%20BOP%20FIESTAS%20LOCALES%20AVILA%2026,0.pdf
    https://www.diputacionavila.es/bops/2025/01-12-2025/01-12-2025_239925.pdf
    https://www.diputacionavila.es/bops/2026/04-02-2026/04-02-2026_021326.pdf
Run (base first, then the complementary lists in order; later ones override):
    python -E -P data/tools/loc2026_bop-avila-2026.py base.pdf compl1.pdf compl2.pdf

Table "Localidad | Fiestas" with ruled rows; a cell can wrap over several lines, so rows are cut at the horizontal
rules. Fiestas cell: "03 febrero y 21 septiembre. SAN BLAS y NTRA. SRA. DE LAS AGUAS" (names in date order, joined by a
lowercase "y"). "MUNICIPIO - LOCALIDAD (ANEJO)" rows are núcleos of the municipality.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "05"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
MES = {m: i for i, m in enumerate(MESES, 1)}
SOURCE = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Ávila: calendario de fiestas de carácter local "
             "año 2026 (BOP Ávila núm. 186, de 26-9-2025, anuncio 1884/25), con las relaciones complementarias de BOP "
             "núm. 231, de 1-12-2025 (anuncio 2399/25) y BOP núm. 23, de 4-2-2026 (anuncio 0213/26)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/77/36/01%20BOP%20FIESTAS%20LOCALES%20AVILA%2026,0.pdf",
    "published": "2025-09-26",
    "modifications": ["https://www.diputacionavila.es/bops/2025/01-12-2025/01-12-2025_239925.pdf",
                      "https://www.diputacionavila.es/bops/2026/04-02-2026/04-02-2026_021326.pdf"],
}
ALIAS = {"NAVALMORAL DE LA SIERRA": "05158"}
COL = 255  # x of the rule between the two columns


def hrules(page):
    ys = []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "l" and abs(it[1].y - it[2].y) < 0.5 and min(it[1].x, it[2].x) < 120 and max(it[1].x, it[2].x) > 240:
                ys.append(it[1].y)
            elif it[0] == "re" and it[1].height < 2 and it[1].x0 < 120 and it[1].x1 > 240:
                ys.append(it[1].y0)
    out = []
    for y in sorted(ys):
        if not out or y - out[-1] > 2:
            out.append(y)
    return out


def entries(pdf):
    for page in pymupdf.open(pdf):
        ys = hrules(page)
        spans = []
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                for s in ln["spans"]:
                    if s["text"].strip():
                        spans.append(((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0], s["text"]))
        for top, bot in zip(ys, ys[1:]):
            band = sorted((y, x, t) for y, x, t in spans if top < y < bot and 100 < x < 505)
            name = re.sub(r"\s+", " ", " ".join(t.strip() for y, x, t in band if x < COL)).strip()
            fiestas = re.sub(r"\s+", " ", " ".join(t.strip() for y, x, t in band if x >= COL)).strip()
            name = re.sub(r"\(\s+", "(", name)  # "OSO ( EL)"
            if name and name != "Localidad":
                yield name, fiestas


def parse(fiestas):
    """-> [(date, name)] in printed order"""
    m = re.match(r"^((?:\d{1,2}\s+(?:de\s+)?(?:" + "|".join(MESES) + r")\s*(?:y\s+)?)+)\.?\s*(.*)$", fiestas, re.I)
    assert m, fiestas
    ds = [f"2026-{MES[mes.lower()]:02d}-{int(d):02d}"
          for d, mes in re.findall(r"(\d{1,2})\s+(?:de\s+)?(" + "|".join(MESES) + ")", m.group(1), re.I)]
    names = [n.strip(" .") for n in re.split(r"\s+y\s+", m.group(2).strip(" ."))] if m.group(2).strip(" .") else []
    if len(names) != len(ds):
        names = [""] * len(ds)
    return list(zip(ds, names))


def hol(pairs):
    seen = {}
    for d, n in pairs:
        seen.setdefault(d, n)
    return [{"date": d, "name": seen[d]} for d in sorted(seen)]


def main(*pdfs):
    mt = Matcher()
    own, nuc, unmatched, names = {}, {}, [], {}
    for k, pdf in enumerate(pdfs):
        for name, fiestas in entries(pdf):
            if not fiestas:
                unmatched.append(f"{name}: (no dates printed)")
                continue
            pairs = parse(fiestas)
            ine = ALIAS.get(name) or mt.match(name, province=PROV)
            if ine:
                if k and ine in own:
                    print("complementary list repeats/overrides", name, own[ine], "->", pairs)
                    if [d for d, _ in own[ine]] == [d for d, _ in pairs]:
                        continue  # same days repeated: keep the names printed in the base list
                own[ine] = pairs
                names[ine] = name
                continue
            m = re.match(r"^(.+?)\s+-\s*(.+?)\s*(?:\((?:anejo)\))?$", name, re.I)
            parent = m and mt.match(m.group(1), province=PROV)
            if parent:
                nuc.setdefault(parent, {})[m.group(2).strip()] = pairs
            else:
                unmatched.append(f"{name}: {fiestas}")
    by_ine = {}
    for ine in sorted(set(own) | set(nuc)):
        rec = {"holidays": hol(own.get(ine, []))}
        notes = []
        if ine in nuc:
            rec["nucleos"] = [{"name": n, "holidays": hol(p)} for n, p in nuc[ine].items()]
            notes.append("The list also gives days for localities (anejos) of the municipality; see nucleos." if ine in own
                         else "The list gives days only per locality of the municipality, not for the whole "
                              "municipality; see nucleos.")
        if ine in own and len(rec["holidays"]) != 2:
            notes.append(f"The list gives {len(rec['holidays'])} day(s) for the municipality.")
        if notes:
            rec["note"] = " ".join(notes)
        by_ine[ine] = rec
    missing = [f"{m['ine']} {m['name']}: not listed" for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("not listed:", len(missing))
    write_part("bop-avila-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
