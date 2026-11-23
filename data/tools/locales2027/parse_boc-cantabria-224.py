"""Cantabria: BOC núm. 224 (20-11-2026), CVE-2026-9104. Resolución de la Dirección General de Trabajo, Economía Social
y Empleo Autónomo por la que se dispone la publicación del calendario de fiestas nacionales, autonómicas y locales en el
ámbito de la Comunidad Autónoma de Cantabria para el año 2027 (signed 16-11-2026).

Input:  <W>/dl/boc-cantabria-224/BOC-2026-9104.pdf
  (https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=443286 ; found in the BOC summary of 20-11-2026)
Run:    python -I parse_boc-cantabria-224.py <W>

Table AYUNTAMIENTO | FESTIVIDAD | DÍA | MES, one ruled row per ayuntamiento, as in 2026
(data/tools/loc2026_boc-cantabria-2026.py). Festivity names wrap over several lines, so each name line is given to the
date printed on the same or the nearest line above it (word coordinates inside the row's cells). "-" = no name printed.
All-caps names are re-cased with cyl_util.nice(), spelling kept (e.g. "San Jose" stays without accent).
No weekday is printed in the local table; Sundays are noted. Month misprints (SEPTEIMBRE, SSEPTIEMBRE) are read as
SEPTIEMBRE and noted.
"""
import datetime
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))
import common  # noqa: E402
from cyl_util import nice  # noqa: E402  (all-caps festivity names -> 'Ntra. Sra. del Carmen')
from muni_match import Matcher  # noqa: E402

SID = "boc-cantabria-224"
CPRO = "39"
META = {
    "title": "Resolución por la que se dispone la publicación del calendario de fiestas nacionales, autonómicas y "
             "locales en el ámbito de la Comunidad Autónoma de Cantabria para el año 2027 (BOC núm. 224, 20-11-2026, "
             "CVE-2026-9104)",
    "url": "https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=443286",
    "published": "2026-11-20",
    "region": "cantabria",
}
MONTHS = {m: i for i, m in enumerate(
    "ENERO FEBRERO MARZO ABRIL MAYO JUNIO JULIO AGOSTO SEPTIEMBRE OCTUBRE NOVIEMBRE DICIEMBRE".split(), 1)}
MISPRINT = {"SEPTEIMBRE": "SEPTIEMBRE", "SSEPTIEMBRE": "SEPTIEMBRE"}
MANUAL = {  # bulletin spelling -> INE code (as in the 2026 parser)
    "HDAD. CAMPOO DE SUSO": "39032",
    "ARENAS IGUÑA": "39004",
    "TRESVISO, LA VILLA DE": "39088",
}
SPOTCHECK = ("Re-read against the PDF independently of the parser: Santander (17 May Virgen del Mar, 30 Aug Santos "
             "Mártires), Torrelavega (16 Aug, 16 Sep), Castro Urdiales (24 Jun, 30 Nov), Laredo (27 Aug, 17 Sep), "
             "Ampuero (8 Sep, name wrapped over two lines; 21 Sep), Camargo (24 Jun, 16 Jul), Reinosa (20 Jan, 21 Sep), "
             "Santoña (5 Feb, 8 Sep) - all match.")


def cell_lines(page, rect):
    import pymupdf
    d = page.get_text("dict", clip=pymupdf.Rect(rect))
    out = []
    for b in d["blocks"]:
        for ln in b.get("lines", []):
            txt = "".join(s["text"] for s in ln["spans"]).strip()
            if txt:
                out.append((ln["bbox"][1], txt))
    return sorted(out)


def rows(pdf):
    import pymupdf
    for page in pymupdf.open(pdf):
        for t in page.find_tables().tables:
            head = [(c or "").strip() for c in t.extract()[0]]
            if head != ["AYUNTAMIENTO", "FESTIVIDAD", "DÍA", "MES"]:
                continue
            for row in t.rows[1:]:
                cells = [cell_lines(page, c) if c else [] for c in row.cells]
                if not any(cells):
                    continue
                assert len(cells) == 4, cells
                yield cells


def main():
    W = common.workdir_from_argv()
    mt = Matcher()
    out, seen = [], set()
    for name_c, fest_c, day_c, mon_c in rows(os.path.join(W, "dl", SID, "BOC-2026-9104.pdf")):
        name = " ".join(x[1] for x in name_c)
        assert len(day_c) == len(mon_c), (name, day_c, mon_c)
        notes, hs = [], []
        for (y, day), (_, mon) in zip(day_c, mon_c):
            if mon in MISPRINT:
                notes.append(f"The bulletin prints the month as \"{mon}\".")
                mon = MISPRINT[mon]
            date = datetime.date(2027, MONTHS[mon], int(day))
            # name lines from this date's line down to the next date's line
            nxt = [yy for yy, _ in day_c if yy > y + 1]
            lim = min(nxt) - 1 if nxt else 1e9
            fest = " ".join(t for yy, t in fest_c if y - 1 <= yy < lim).strip()
            hs.append({"date": date.isoformat(), "name": None if fest in ("", "-") else nice(fest)})
            if date.weekday() == 6:
                notes.append(f"{date.isoformat()} falls on a Sunday; kept as published.")
        top = min(y for y, _ in day_c)
        assert all(yy >= top - 1 for yy, _ in fest_c), (name, fest_c)
        hs.sort(key=lambda h: h["date"])
        if len(hs) != 2:
            notes.append(f"The resolution gives {len(hs)} date(s).")
        code = MANUAL.get(name) or mt.match(name, province=CPRO)
        print(f"{name:<28} {code} " + " | ".join(f"{h['date']} {h['name']}" for h in hs) + (
            f"  NOTE {' '.join(notes)}" if notes else ""))
        if not code:
            print("NO INE:", name)
            continue
        assert code not in seen, (name, code)
        seen.add(code)
        r = {"name": name, "cpro": CPRO, "ine": code, "match": "manual" if name in MANUAL else "muni_match",
             "status": "boletin", "holidays": hs}
        if notes:
            r["note"] = " ".join(notes)
        out.append(r)
    ine = common.INE(W)
    print("not in the table:", [n for _, n in common.coverage(ine, out, [CPRO])])
    common.save_parsed(W, SID, META, out, SPOTCHECK)


if __name__ == "__main__":
    main()
