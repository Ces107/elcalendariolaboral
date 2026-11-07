"""Cantabria 2026 local holidays: BOC núm. 238 (11-12-2025), CVE-2025-10276, Resolución de la Dirección General
de Trabajo, Economía Social y Empleo Autónomo (calendario de fiestas nacionales, autonómicas y locales 2026).

Usage: python -E -P data/tools/loc2026_boc-cantabria-2026.py <path/to/BOC-2025-10276.pdf> [--dry]

Table AYUNTAMIENTO | FESTIVIDAD | DÍA | MES; each ayuntamiento is one ruled row whose cells hold its two
lines separated by newlines. Read with PyMuPDF find_tables() and paired line by line inside the same
row (pdftotext -layout prints the names and the dates out of step in this PDF).
"""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SID = "boc-cantabria-2026"
SOURCE = {
    "title": "Resolución por la que se dispone la publicación del calendario de fiestas nacionales, autonómicas y "
             "locales en el ámbito de la Comunidad Autónoma de Cantabria para el año 2026 (BOC núm. 238, "
             "11-12-2025, CVE-2025-10276)",
    "url": "https://boc.cantabria.es/boces/verAnuncioAction.do?idAnuBlob=428192",
    "published": "2025-12-11",
}
MONTHS = {m: i for i, m in enumerate(
    "ENERO FEBRERO MARZO ABRIL MAYO JUNIO JULIO AGOSTO SEPTIEMBRE OCTUBRE NOVIEMBRE DICIEMBRE".split(), 1)}
# bulletin spelling -> INE code, verified by eye
MANUAL = {
    "HDAD. CAMPOO DE SUSO": "39032",  # Hermandad de Campoo de Suso
    "ARENAS IGUÑA": "39004",          # Arenas de Iguña
    "TRESVISO, LA VILLA DE": "39088",  # Tresviso
}
WD = {5: "Saturday", 6: "Sunday"}


def lines(c):
    return [x.strip() for x in (c or "").split("\n") if x.strip()]


def parse(pdf):
    import pymupdf
    out = []
    for page in pymupdf.open(pdf):
        for t in page.find_tables().tables:
            rows = t.extract()
            if not rows or "AYUNTAMIENTO" not in [(c or "").strip() for c in rows[0]]:
                continue
            for r in rows[1:]:
                cells = [c for c in r if c and c.strip()]
                if not cells:
                    continue
                if len(cells) != 4:
                    print("ODD ROW:", r)
                    continue
                name = " ".join(cells[0].split())
                fest, days, months = lines(cells[1]), lines(cells[2]), lines(cells[3])
                out.append({"name": name, "fest": fest, "days": days, "months": months})
    return out


def main():
    pdf = sys.argv[1]
    dry = "--dry" in sys.argv
    mt = Matcher()
    out, unmatched = {}, []
    for m in parse(pdf):
        notes = []
        fest, days, months = m["fest"], m["days"], m["months"]
        if not (len(fest) == len(days) == len(months)):
            # a long festivity wrapped onto two lines: only safe when dates are complete
            notes.append(f"Check: {len(fest)} name lines for {len(days)} dates.")
            if len(fest) > len(days):
                fest = fest[:len(days) - 1] + [" ".join(fest[len(days) - 1:])] if len(days) == 1 else fest
        hol = []
        for i, (d, mo) in enumerate(zip(days, months)):
            iso = dt.date(2026, MONTHS[mo.upper()], int(d)).isoformat()
            n = fest[i] if i < len(fest) else ""
            hol.append({"date": iso, "name": "" if n in ("-", "") else n})
        hol.sort(key=lambda h: h["date"])
        if len(hol) != 2:
            notes.append(f"The resolution gives {len(hol)} date(s) for this ayuntamiento.")
        if len({h['date'] for h in hol}) != len(hol):
            notes.append("Repeated date in the bulletin.")
            seen = {}
            for h in hol:
                seen.setdefault(h["date"], h)
            hol = list(seen.values())
        for h in hol:
            d = dt.date.fromisoformat(h["date"])
            if d.weekday() in WD:
                notes.append(f"{d.day}/{d.month} falls on a {WD[d.weekday()]}; recorded as published.")
        code = MANUAL.get(m["name"]) or mt.match(m["name"], province="39")
        print(f"{m['name']:<30} {code}  " + " | ".join(f"{h['date']} {h['name']}" for h in hol)
              + (f"   NOTE: {' '.join(notes)}" if notes else ""))
        if not code:
            unmatched.append(m["name"])
            continue
        assert code not in out, (code, m["name"])
        out[code] = {"holidays": hol}
        if notes:
            out[code]["note"] = " ".join(notes)
    allc = {x["ine"]: x["name"] for x in mt.munis if x["province_code"] == "39"}
    print("unmatched:", unmatched)
    print("missing from part:", [v for k, v in allc.items() if k not in out], f"({len(out)}/{len(allc)})")
    if not dry:
        write_part(SID, SOURCE, out, region="cantabria", unmatched=unmatched)


if __name__ == "__main__":
    main()
