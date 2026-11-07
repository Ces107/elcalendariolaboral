"""Asturias 2026 local holidays: BOPA núm. 114 (16-VI-2025), Resolución de 3 de junio de 2025, cód. 2025-04744.

Usage: python -E -P data/tools/loc2026_bopa-2026.py <path/to/2025-04744.pdf> [--dry]

Ruled table CONCEJO | fecha | festividad, one row per date; the concejo cell spans its date rows.
Read with PyMuPDF find_tables() (pdftotext -layout misaligns names and dates in this PDF).
"""
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SID = "bopa-2026"
SOURCE = {
    "title": "Resolución de 3 de junio de 2025, de la Consejería de Ciencia, Industria y Empleo, por la que se aprueba "
             "el calendario de fiestas locales para el año 2026 en la Comunidad Autónoma del Principado de Asturias "
             "(BOPA núm. 114, 16-VI-2025, cód. 2025-04744)",
    "url": "https://miprincipado.asturias.es/bopa/2025/06/16/2025-04744.pdf",
    "published": "2025-06-16",
}
MONTHS = {m: i for i, m in enumerate(
    "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre".split(), 1)}
DATE = re.compile(r"(\d{1,2})\s+de\s+([a-záéíóú]+)", re.I)
MANUAL = {}  # bulletin spelling -> INE, verified by eye


def clean(s):
    s = (s or "").replace("\xad\n", "").replace("\xad ", "").replace("\xad", "")
    return " ".join(s.split())


def parse(pdf):
    import pymupdf
    doc = pymupdf.open(pdf)
    munis = []
    for page in doc:
        for t in page.find_tables().tables:
            for r in t.extract():
                name, date, fest = ([clean(c) for c in r] + ["", "", ""])[:3]
                if name.upper() in ("CONCEJO", "AYUNTAMIENTO"):
                    continue
                if name:
                    munis.append({"name": name, "raw": []})
                if date:
                    munis[-1]["raw"].append((date, fest))
    return munis


def main():
    pdf = sys.argv[1]
    dry = "--dry" in sys.argv
    mt = Matcher()
    out, unmatched = {}, []
    munis = []
    for m in parse(pdf):
        # a concejo name wrapped over its two rows comes out as two cells ("MUROS DE" / "NALÓN")
        if munis and not mt.match(munis[-1]["name"], province="33") \
                and mt.match(munis[-1]["name"] + " " + m["name"], province="33"):
            munis[-1]["name"] += " " + m["name"]
            munis[-1]["raw"] += m["raw"]
        else:
            munis.append(m)
    for m in munis:
        hol, bad = [], []
        for d, f in m["raw"]:
            found = DATE.findall(d)
            if len(found) != 1 or found[0][1].lower() not in MONTHS:
                bad.append(f"{d}: {f}")
                continue
            iso = dt.date(2026, MONTHS[found[0][1].lower()], int(found[0][0])).isoformat()
            hol.append({"date": iso, "name": f})
        hol.sort(key=lambda h: h["date"])
        notes = []
        if bad:
            notes.append("Unparsed cells: " + " | ".join(bad))
        if len(hol) > 2:
            notes.append(f"The resolution lists {len(hol)} dates; some apply only to part of the concejo "
                         "(parish/village named in the festivity).")
        if len(hol) < 2:
            notes.append(f"The resolution lists {len(hol)} date(s) for this concejo.")
        for h in hol:
            d = dt.date.fromisoformat(h["date"])
            if d.weekday() == 6:
                notes.append(f"{d.day}/{d.month} falls on a Sunday as published.")
        if any(not h["name"] for h in hol):
            notes.append("Some dates are given without a festivity name.")
        code = MANUAL.get(m["name"]) or mt.match(m["name"], province="33")
        print(f"{m['name']:<28} {code}  " + " | ".join(f"{h['date']} {h['name']}" for h in hol)
              + ("   NOTE: " + " ".join(notes) if notes else ""))
        if not code:
            unmatched.append(m["name"])
            continue
        assert code not in out, (code, m["name"])
        out[code] = {"holidays": hol}
        if notes:
            out[code]["note"] = " ".join(notes)
    missing = [x["name"] for x in mt.munis if x["province_code"] == "33" and x["ine"] not in out]
    print("unmatched:", unmatched, "| missing from part:", missing)
    if not dry:
        write_part(SID, SOURCE, out, region="asturias", unmatched=unmatched)


if __name__ == "__main__":
    main()
