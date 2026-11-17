"""Cuenca province: BOP Cuenca núm. 130 (13-11-2026), anuncio núm. 2719. Resolución de 12/11/2026 de la Delegación
Provincial de la Consejería de Economía, Empresas y Empleo en Cuenca, festivos locales 2027.

Input:  <W>/dl/bop-cuenca-130/bop_130.pdf  (the whole signed bulletin)
  (https://www.dipucuenca.es/documents/34525/677c6742-e5d3-5de4-d58b-818c94f036b4 ; found with the BOP search at
   https://www.dipucuenca.es/boletin1, text "fiestas locales", 2026-09-01..2026-11-17)
Run:    python -E -P parse_bop-cuenca-130.py <W>

Same table as 2026 (Población | Pedanía | Festivo 1 | Festivo 2, dd/mm/yyyy), read with PyMuPDF find_tables(); the
rules of data/tools/loc2026_bop-cuenca-2026.py apply: a Población row with empty dates is followed by Pedanía rows,
  - the pedanía named like the municipality gives the municipality's days, the others go to "localities";
  - if none has the municipality's name and all share the same days, those are the municipality's days;
  - otherwise "holidays" is empty and every núcleo goes to "localities".
"(EATIM)" rows are entidades locales menores, not INE municipalities: reported, left out.
"""
import datetime
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))
import common  # noqa: E402
from muni_match import Matcher  # noqa: E402

SID = "bop-cuenca-130"
CPRO = "16"
NUM = "2719"
META = {
    "title": "Resolución de 12/11/2026 de la Delegación Provincial de la Consejería de Economía, Empresas y Empleo en "
             "Cuenca por la que se determinan los festivos locales para los municipios de la provincia de Cuenca durante "
             "el año 2027 y se ordena su publicación (BOP Cuenca núm. 130, 13-11-2026, anuncio núm. 2719)",
    "url": "https://www.dipucuenca.es/documents/34525/677c6742-e5d3-5de4-d58b-818c94f036b4",
    "published": "2026-11-13",
    "region": "castilla-la-mancha",
}
ALIAS = {"Chillaron de Cuenca": "Chillarón de Cuenca", "Fuentenava de Jabaga": "Fuentenava de Jábaga",
         "Paracuellos de la Vega": "Paracuellos"}  # as in the 2026 parser (INE 16150 is "Paracuellos")
SPOTCHECK = ("Re-read against the PDF by eye, independently of the parser: Cuenca, Tarancón, San Clemente, "
             "Motilla del Palancar, Las Pedroñeras, Alcalá de la Vega (+ El Cubillo), Altarejos (+ Poveda de la "
             "Obispalía), Abia de la Obispalía - all match.")


def a(s):
    return re.sub(r"[^a-z]", "", unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower())


def table_rows(pdf):
    import pymupdf
    doc = pymupdf.open(pdf)
    inside = False
    for page in doc:
        nums = re.findall(r"NÚM\. (\d+)\s*\n", page.get_text())
        if NUM in nums:
            inside = True
        if not inside:
            continue
        for t in page.find_tables().tables:
            rows = t.extract()
            if not rows or (rows[0][0] or "").upper().replace("Ó", "O") != "POBLACION":
                continue
            for r in rows[1:]:
                yield [(c or "").replace("\n", " ").strip() for c in r]
        if nums and nums[-1] != NUM:
            break


def iso(cell):
    m = re.fullmatch(r"(\d\d)/(\d\d)/(\d{4})", cell or "")
    assert m, cell
    return f"2027-{m.group(2)}-{m.group(1)}" if m.group(3) == "2027" else None


def hol(ds):
    return [{"date": d, "name": None} for d in sorted(set(d for d in ds if d))]


def main():
    W = common.workdir_from_argv()
    mt = Matcher()
    groups = []
    for r in table_rows(os.path.join(W, "dl", SID, "bop_130.pdf")):
        pob, ped, d1, d2 = r
        if pob:
            groups.append([pob, (d1, d2) if (d1 or d2) else None, []])
        else:
            assert ped and groups, r
            groups[-1][2].append((ped, d1, d2))
    rows, seen = [], set()
    for pob, own, peds in groups:
        name = ALIAS.get(pob, pob)
        if "(EATIM)" in name.upper():
            print(f"EATIM (left out): {pob} {own}")
            continue
        code = mt.match(name, province=CPRO)
        if not code:
            print("NO INE:", pob, own, peds)
            continue
        notes, locs = [], []
        if own:
            hs = hol(iso(c) for c in own)
            bad = [c for c in own if c and not iso(c)]
            if bad:
                notes.append(f"The bulletin prints {', '.join(bad)} (not 2027); left out.")
        else:
            same = [p for p in peds if a(p[0]) == a(name)]
            others = [p for p in peds if a(p[0]) != a(name)]
            if same:
                hs = hol([iso(same[0][1]), iso(same[0][2])])
            elif len({(p[1], p[2]) for p in peds}) == 1:
                hs = hol([iso(peds[0][1]), iso(peds[0][2])])
                notes.append("The bulletin lists the days per núcleo (" + ", ".join(p[0] for p in peds)
                             + "); all share the same two days, used here for the municipality.")
                others = []
            else:
                hs = []
                notes.append("The bulletin gives no municipality-wide days, only separate days for each núcleo "
                             "(see localities).")
            locs = [{"name": p[0], "holidays": hol([iso(p[1]), iso(p[2])])} for p in others]
            if others and same:
                notes.append("The bulletin lists separate days for: " + "; ".join(
                    f"{p[0]} {', '.join(h['date'] for h in hol([iso(p[1]), iso(p[2])]))}" for p in others) + ".")
        suns = [h["date"] for h in hs if datetime.date.fromisoformat(h["date"]).weekday() == 6]
        if suns:
            notes.append("Published date(s) falling on a Sunday, kept as published: " + ", ".join(suns) + ".")
        if len(hs) == 1:
            notes.append("Only one 2027 date is published for the municipality.")
        if not hs and not locs:
            print(f"LEFT OUT {pob}: no 2027 date ({' '.join(notes)})")
            continue
        assert code not in seen, (pob, code)
        seen.add(code)
        row = {"name": pob, "cpro": CPRO, "ine": code, "match": "muni_match", "status": "boletin", "holidays": hs}
        if locs:
            row["localities"] = locs
        if notes:
            row["note"] = " ".join(notes)
        rows.append(row)
    ine = common.INE(W)
    print("not in the annex:", [n for _, n in common.coverage(ine, rows, [CPRO])])
    common.save_parsed(W, SID, META, rows, SPOTCHECK)


if __name__ == "__main__":
    main()
