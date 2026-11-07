"""Albacete province 2026 local holidays: Resolución de 19-11-2025 de la Delegación Provincial de la Consejería de Economía,
Empresas y Empleo en Albacete, "calendario de fiestas laborales locales para el año 2026" (BOP Albacete núm. 138,
26-11-2025, anuncio 25.039), plus two later changes by the same Delegación:
  - BOP núm. 33 (18-03-2026, anuncio 4.743): Villalgordo del Júcar, 22/07/2026 replaces 22/06/2026;
  - BOP núm. 89 (03-08-2026, anuncio 20.391): Casas de Lázaro, 09/10/2026 replaces 10/10/2026.
The BOP search (bop.dipualba.es, "fiestas", "fiestas laborales locales", "designación", 2025-09 .. 2026-11) shows no others.

Download (outside the repo) the whole bulletins:
    https://bop.dipualba.es/servicesajax/descararchivobopcompleto/?a=22627  (núm. 138)  -> bop_138.pdf
    https://bop.dipualba.es/servicesajax/descararchivobopcompleto/?a=22675  (2026 núm. 33)
    https://bop.dipualba.es/servicesajax/descararchivobopcompleto/?a=22731  (2026 núm. 89)
Run:
    python -E -P data/tools/loc2026_bop-albacete-2026.py bop_138.pdf bop_2026-33.pdf bop_2026-89.pdf

Annex read with PyMuPDF find_tables() (Población | Días festivos, e.g. "8 mayo y 29 septiembre"), dates only, on the pages
from the resolution's title to its signature. The two changes are single-day substitutions; the parser checks the
"en sustitución del día" sentence in each bulletin and applies it. Rows that are not INE municipalities (pedanías such as
Aguas Nuevas or El Salobral) are listed as unmatched.
"""
import datetime
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "02"
DL = "https://bop.dipualba.es/servicesajax/descararchivobopcompleto/?a="
SOURCE = {
    "title": "Resolución de la Delegación Provincial de la Consejería de Economía, Empresas y Empleo en Albacete acordando "
             "el calendario de fiestas laborales locales para el año 2026 en la provincia de Albacete (BOP Albacete núm. "
             "138, de 26-11-2025), modificada por los anuncios del BOP núm. 33 (18-03-2026, Villalgordo del Júcar) y "
             "núm. 89 (03-08-2026, Casas de Lázaro)",
    "url": DL + "22627",
    "published": "2025-11-26",
    "modifications": [DL + "22675", DL + "22731"],
}
MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
ALIAS = {"Chinchilla": "02029"}  # printed short name of Chinchilla de Monte-Aragón
CHANGES = [  # (bulletin label, municipality, new dd/mm/yyyy, old dd/mm/yyyy) -- verified against the bulletin text
    ("BOP Albacete núm. 33 (18-03-2026)", "Villalgordo del Júcar", "22/07/2026", "22/06/2026"),
    ("BOP Albacete núm. 89 (03-08-2026)", "Casas de Lázaro", "09/10/2026", "10/10/2026"),
]


def dates(txt):
    """'8 mayo y 29 septiembre' / '7 y 8 septiembre' / '15 mayo 14 septiembre' -> ISO list"""
    out, pending = [], []
    for num, mes in re.findall(r"(\d{1,2})(?:\s+(?:de\s+)?(" + "|".join(MES) + r"))?", txt.lower()):
        pending.append(int(num))
        if mes:
            out += [f"2026-{MES[mes]:02d}-{d:02d}" for d in pending]
            pending = []
    assert not pending and out, txt
    return sorted(set(out))


def annex_rows(pdf):
    doc = pymupdf.open(pdf)
    inside = False
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text()
        if "calendario de fiestas laborales locales para el año 2026" in re.sub(r"\s+", " ", text):
            inside = True
        if not inside:
            continue
        for t in page.find_tables().tables:
            for r in t.extract():
                if len(r) == 2 and r[0] and r[1] and r[0] != "Población":
                    yield r[0].replace("\n", " ").strip(), r[1].replace("\n", " ").strip()
        if re.search(r"Albacete, \d+ de \w+ de 2025\.\W*El Delegado Provincial", text):
            break  # signature: end of the resolution


def iso(dmy):
    d, m, y = dmy.split("/")
    return f"{y}-{m}-{d}"


def main(base, *mods):
    mt = Matcher()
    out, unmatched = {}, []
    for name, txt in annex_rows(base):
        ine = ALIAS.get(name) or mt.match(name, province=PROV)
        if not ine:
            unmatched.append(f"{name}: {txt}")
            continue
        assert ine not in out, (name, ine)
        out[ine] = {"holidays": [{"date": d, "name": ""} for d in dates(txt)]}
    assert len(mods) == len(CHANGES)
    for pdf, (label, name, new, old) in zip(mods, CHANGES):
        text = re.sub(r"\s+", " ", " ".join(p.get_text() for p in pymupdf.open(pdf)))
        assert re.search(rf"el día {new} en sustitución del día {old}.{{0,120}}municipio de {name}", text), (pdf, name)
        ine = mt.match(name, province=PROV)
        ds = [h["date"] for h in out[ine]["holidays"]]
        assert iso(old) in ds, (name, ds)
        ds = sorted(set(ds) - {iso(old)} | {iso(new)})
        out[ine] = {"holidays": [{"date": d, "name": ""} for d in ds],
                    "note": f"Changed by {label}: {new} replaces {old}."}
    for ine, v in out.items():
        notes = [v["note"]] if v.get("note") else []
        if len(v["holidays"]) != 2:
            notes.append(f"The bulletin gives {len(v['holidays'])} date(s).")
        suns = [h["date"] for h in v["holidays"] if datetime.date.fromisoformat(h["date"]).weekday() == 6]
        if suns:
            notes.append("Published date(s) falling on a Sunday, kept as published: " + ", ".join(suns) + ".")
        if notes:
            v["note"] = " ".join(notes)
    write_part("bop-albacete-2026", SOURCE, out, region="castilla-la-mancha", unmatched=unmatched)
    missing = [m["name"] for m in mt.munis if m["province_code"] == PROV and m["ine"] not in out]
    print("province municipalities not written:", len(missing), missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
