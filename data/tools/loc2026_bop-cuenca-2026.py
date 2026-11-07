"""Cuenca province 2026 local holidays: Resolución de 10/11/2025 de la Delegación Provincial de la Consejería de Economía,
Empresas y Empleo en Cuenca (BOP Cuenca núm. 132, 14-11-2025, anuncio núm. 3291), plus two corrections:
  - BOP núm. 147 (22-12-2025, anuncio 3784): La Hinojosa 20/02 -> 20/01/2026;
  - BOP núm. 29 (09-03-2026, anuncio 552): Osa de la Vega 15/09 -> 14/09/2026.
The BOP search (dipucuenca.es/boletin1, "festivos locales" / "fiestas locales", 2025-08 .. 2026-11) shows no others.

Download (outside the repo) the whole signed bulletins from https://www.dipucuenca.es/documents/34525/<id>:
    c1ffc400-67b2-fa04-7279-5ed530b91ca0 (núm. 132)  03027178-f812-0650-6367-0cf0c26a2958 (núm. 147)
    a6c3e954-d0a5-27f3-b7cf-22c980fdb104 (2026 núm. 29)
Run (base first, then corrections in order):
    python -E -P data/tools/loc2026_bop-cuenca-2026.py bop_132.pdf bop_147.pdf bop_2026-29.pdf

Annex read with PyMuPDF find_tables() (Población | Pedanía | Festivo 1 | Festivo 2, dd/mm/yyyy), dates only.
A Población row with empty dates is followed by Pedanía rows (possibly across a page break):
  - the pedanía named like the municipality gives the municipality's own days, the rest go to "nucleos";
  - if no pedanía has the municipality's name and all share the same days, those are the municipality's days;
  - otherwise "holidays" is left empty (no municipality-wide days published) and every núcleo goes to "nucleos".
Rows marked "(EATIM)" are entidades locales menores, not INE municipalities: listed in unmatched.
"""
import datetime
import re
import sys
import unicodedata
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "16"
DOC = "https://www.dipucuenca.es/documents/34525/"
SOURCE = {
    "title": "Resolución de 10/11/2025 de la Delegación Provincial de la Consejería de Economía, Empresas y Empleo en "
             "Cuenca por la que se determinan los festivos locales para los municipios de la provincia de Cuenca durante "
             "el año 2026 (BOP Cuenca núm. 132, de 14-11-2025, anuncio 3291), con las correcciones de errores del BOP "
             "núm. 147 (22-12-2025, anuncio 3784) y núm. 29 (09-03-2026, anuncio 552)",
    "url": DOC + "c1ffc400-67b2-fa04-7279-5ed530b91ca0",
    "published": "2025-11-14",
    "modifications": [DOC + "03027178-f812-0650-6367-0cf0c26a2958", DOC + "a6c3e954-d0a5-27f3-b7cf-22c980fdb104"],
}
ANUNCIOS = ["3291", "3784", "552"]
ALIAS = {"Chillaron de Cuenca": "Chillarón de Cuenca", "Fuentenava de Jabaga": "Fuentenava de Jábaga",
         "Paracuellos de la Vega": "Paracuellos"}  # INE 16150 is "Paracuellos"
CORR_NOTE = {"3784": "Corrected by BOP Cuenca núm. 147 (22-12-2025): 20 February replaced by 20 January.",
             "552": "Corrected by BOP Cuenca núm. 29 (09-03-2026): 15 September replaced by 14 September."}


def a(s):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())


def anuncio_tables(pdf, num):
    """Rows of the 3/4-column holiday tables on the pages of anuncio NÚM. <num>."""
    doc = pymupdf.open(pdf)
    inside = False
    for i in range(len(doc)):
        page = doc[i]
        nums = re.findall(r"NÚM\. (\d+)\s*\n", page.get_text())
        if num in nums:
            inside = True
        if not inside:
            continue
        # every page of the annex repeats the "Población" header, so foreign tables are skipped by the header test
        for t in page.find_tables().tables:
            rows = t.extract()
            if not rows or rows[0][0] != "Población":
                continue
            for r in rows[1:]:
                yield [(c or "").replace("\n", " ").strip() for c in r]
        if nums and nums[-1] != num:
            break  # another anuncio starts on this page: ours ended here


def iso(cell):
    """'15/05/2026' -> '2026-05-15'; anything not in 2026 -> None"""
    m = re.fullmatch(r"(\d\d)/(\d\d)/(\d{4})", cell)
    assert m, cell
    return f"2026-{m.group(2)}-{m.group(1)}" if m.group(3) == "2026" else None


def hol(ds):
    return [{"date": d, "name": ""} for d in sorted(set(d for d in ds if d))]


def main(base, *corrections):
    mt = Matcher()
    groups = []  # [name, own_dates_cells or None, [(pedania, d1, d2)]]
    for r in anuncio_tables(base, ANUNCIOS[0]):
        pob, ped, d1, d2 = r
        if pob:
            groups.append([pob, (d1, d2) if (d1 or d2) else None, []])
        else:
            assert ped and groups, r
            groups[-1][2].append((ped, d1, d2))
    out, unmatched = {}, []
    for pob, own, peds in groups:
        name = ALIAS.get(pob, pob)
        if "(EATIM)" in name:
            unmatched.append(f"{pob} [entidad local menor]: {own[0]}, {own[1]}")
            continue
        ine = mt.match(name, province=PROV)
        if not ine:
            unmatched.append(f"{pob}: {own or peds}")
            continue
        notes, rec = [], {}
        if own:
            cells = list(own)
            rec["holidays"] = hol(iso(c) for c in cells)
        else:
            same = [p for p in peds if a(p[0]) == a(name)]
            others = [p for p in peds if a(p[0]) != a(name)]
            if same:
                cells = [same[0][1], same[0][2]]
                rec["holidays"] = hol(iso(c) for c in cells)
            elif len({(p[1], p[2]) for p in peds}) == 1:
                cells = [peds[0][1], peds[0][2]]
                rec["holidays"] = hol(iso(c) for c in cells)
                notes.append("The bulletin lists the days per núcleo (" + ", ".join(p[0] for p in peds)
                             + "); all núcleos share the same two days, used here for the municipality.")
                others = []
            else:
                cells = []
                rec["holidays"] = []
                notes.append("The bulletin gives no municipality-wide days, only separate days for each núcleo "
                             "(see nucleos).")
            if others:
                rec["nucleos"] = [{"name": p[0], "holidays": hol([iso(p[1]), iso(p[2])])} for p in others]
                if same:
                    notes.append("The bulletin lists separate days for núcleos: " + ", ".join(p[0] for p in others) + ".")
            bad = [p for p in peds for c in p[1:] if c and not iso(c)]
            for p in bad:
                notes.append(f"For {p[0]} the bulletin prints {p[1]} and {p[2]}; the date not in 2026 is left out "
                             "(no correction published).")
        assert ine not in out, (pob, ine)
        out[ine] = rec
        if notes:
            rec["note"] = " ".join(notes)
    for pdf, num in zip(corrections, ANUNCIOS[1:]):
        rows = list(anuncio_tables(pdf, num))
        assert len(rows) == 2, (num, rows)  # "Donde dice" row, then "Debe decir" row
        (old_name, *old), (new_name, *new) = rows
        assert old_name == new_name, rows
        ine = mt.match(new_name, province=PROV)
        assert [h["date"] for h in out[ine]["holidays"]] == sorted(iso(c) for c in old), (new_name, out[ine])
        out[ine]["holidays"] = hol(iso(c) for c in new)
        out[ine]["note"] = " ".join(filter(None, [out[ine].get("note"), CORR_NOTE[num]]))
    for ine, v in out.items():
        notes = [v["note"]] if v.get("note") else []
        if len(v["holidays"]) == 1:
            notes.append("Only one 2026 date is published for the municipality.")
        suns = [h["date"] for h in v["holidays"] if datetime.date.fromisoformat(h["date"]).weekday() == 6]
        if suns:
            notes.append("Published date(s) falling on a Sunday, kept as published: " + ", ".join(suns) + ".")
        if notes:
            v["note"] = " ".join(notes)
    write_part("bop-cuenca-2026", SOURCE, out, region="castilla-la-mancha", unmatched=unmatched)
    missing = [m["name"] for m in mt.munis if m["province_code"] == PROV and m["ine"] not in out]
    print("province municipalities not written:", len(missing), missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
