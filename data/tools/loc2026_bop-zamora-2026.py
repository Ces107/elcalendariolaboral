"""Zamora province 2026 local holidays: Calendario de fiestas locales para el año 2026, Oficina Territorial de Trabajo
de Zamora, resolución de 17-9-2025 (BOP Zamora núm. 106, 19-9-2025, R-202502347), copy hosted by the Junta de Castilla
y León (Trabajo y Prevención, 'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/778/74/09%20BOP%20FIESTAS%20LOCALES%20ZAMORA%2026,0.pdf
Run:
    python -E -P data/tools/loc2026_bop-zamora-2026.py <downloaded.pdf> [later corrections.pdf ...]

Annex table "localidad | día y mes | denominación", one date per printed row; the municipality name is on its first
row and rows starting with "-" are its localities (pedanías / entidades locales menores) with their own days.
Text is set in small caps, so names come out in mixed case; holiday names are re-cased.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "49"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
MES = {m: i for i, m in enumerate(MESES, 1)}
SOURCE = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Zamora. Calendario de fiestas locales para el "
             "año 2026 (resolución de 17-9-2025, BOP Zamora núm. 106, de 19-9-2025, R-202502347)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/778/74/09%20BOP%20FIESTAS%20LOCALES%20ZAMORA%2026,0.pdf",
    "published": "2025-09-19",
}
ALIAS = {"almeida": "49008", "bretó de la ribera": "49025", "cañizo de campos": "49035",
         "ferreruela de tábara": "49068", "granucillo de vidriales": "49092", "roales del pan": "49178"}
SMALL = {"de", "del", "la", "las", "los", "el", "y", "e", "en", "a"}


def recase(s):
    words = s.strip().lower().split()
    return " ".join(w if (i and w in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def rows(page):
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for s in ln["spans"]:
                if s["text"].strip() and 90 <= s["bbox"][0] < 540:
                    spans.append(((s["bbox"][1] + s["bbox"][3]) / 2, s["bbox"][0], s["text"]))
    spans.sort()
    out = []
    for y, x, t in spans:
        if out and abs(out[-1][0] - y) < 3:
            out[-1][1].append((x, t))
        else:
            out.append([y, [(x, t)]])
    return [(y, sorted(c)) for y, c in out]


def dates(txt):
    out, pending = [], []
    for num, mes in re.findall(r"(\d{1,2})(?:\s+(?:de\s+)?(" + "|".join(MESES) + r"))?", txt.lower()):
        pending.append(int(num))
        if mes:
            out += [f"2026-{MES[mes]:02d}-{d:02d}" for d in pending]
            pending = []
    assert not pending and out, txt
    return out


def blocks(pdf):
    """yield (municipality name, [(date, name)], [(locality, [(date, name)])])"""
    started, cur = False, None
    for page in pymupdf.open(pdf):
        for y, cells in rows(page):
            loc = " ".join(t.strip() for x, t in cells if x < 240).strip()
            day = " ".join(t.strip() for x, t in cells if 240 <= x < 370).strip()
            den = " ".join(t.strip() for x, t in cells if x >= 370).strip()
            if loc.lower() == "localidad":
                started = True
                continue
            if not started:
                continue
            if loc and not day and not loc.startswith("-") and not re.match(r"(BOLETÍN|n\.º|www\.|R-20\d\d)", loc, re.I):
                # municipality row without days of its own (only its localities follow), e.g. robleda-cerVanteS
                if cur:
                    yield cur
                cur = (re.sub(r"\s+", " ", loc), [], [])
                continue
            if not re.match(r"\d{1,2}\b", day):
                continue
            pairs = [(d, recase(den)) for d in dates(day)]
            if loc and not loc.startswith("-"):
                if cur:
                    yield cur
                cur = (re.sub(r"\s+", " ", loc), [], [])
            if loc.startswith("-"):
                cur[2].append((re.sub(r"\s+", " ", loc[1:]).strip(), []))
            (cur[2][-1][1] if cur[2] else cur[1]).extend(pairs)
    if cur:
        yield cur


def hol(pairs):
    seen = {}
    for d, n in pairs:
        seen.setdefault(d, n)
    return [{"date": d, "name": seen[d]} for d in sorted(seen)]


def main(*pdfs):
    mt = Matcher()
    by_ine, unmatched = {}, []
    for pdf in pdfs:
        for name, own, locs in blocks(pdf):
            ine = ALIAS.get(name.lower()) or mt.match(name, province=PROV)
            if not ine:
                unmatched.append(f"{name}: {own} {locs}")
                continue
            rec = {"holidays": hol(own)}
            notes = []
            if locs:
                rec["nucleos"] = [{"name": recase(n), "holidays": hol(p)} for n, p in locs]
                notes.append("The list also gives days for localities of the municipality; see nucleos." if own else
                             "The list gives days only per locality of the municipality, not for the whole "
                             "municipality; see nucleos.")
            if own and len(rec["holidays"]) != 2:
                notes.append(f"The list gives {len(rec['holidays'])} day(s) for the municipality itself.")
            if notes:
                rec["note"] = " ".join(notes)
            by_ine[ine] = rec
    missing = [f"{m['ine']} {m['name']}: not listed" for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("not listed:", len(missing))
    write_part("bop-zamora-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
