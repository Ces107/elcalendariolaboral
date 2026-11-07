"""León province 2026 local holidays: Resolución de 15-9-2025 de la Oficina Territorial de Trabajo de León
(BOP León núm. 177, 17-9-2025, CVE BOP-LE-2025-177019), copy hosted by the Junta de Castilla y León (Trabajo y
Prevención, 'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/868/589/03%20BOP%20FIESTAS%20LOCALES%20LEON%2026,0.pdf
Run:
    python -E -P data/tools/loc2026_bop-leon-2026.py <downloaded.pdf>

Annex layout: one bold line per municipality ("Astorga: 24 de julio, Festividad de ... y 24 de agosto, Santa Marta"),
followed by indented lines for its localities (pedanías / entidades locales menores) with their own days, and
optionally "Para todo el municipio: <date>" = a day for every locality. Lines starting at the left margin continue the
previous line. Municipality days = its own line + "para todo el municipio"; each locality = its line + the common day.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "24"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
MES = {m: i for i, m in enumerate(MESES, 1)}
DATE = re.compile(r"(\d{1,2}(?:\s*(?:,|y|e)\s*\d{1,2})*)\s+(?:de\s+)?(" + "|".join(MESES) + r")\b", re.I)
SOURCE = {
    "title": "Resolución de 15 de septiembre de 2025, de la Oficina Territorial de Trabajo de León, por la que se fijan "
             "las fiestas locales de los distintos municipios de la provincia de León para el año 2026 (BOP León núm. "
             "177, de 17-9-2025, CVE BOP-LE-2025-177019)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/868/589/03%20BOP%20FIESTAS%20LOCALES%20LEON%2026,0.pdf",
    "published": "2025-09-17",
}
ALIAS = {"Carrizo de la Ribera": "24039", "Vecilla de Curueño (La)": "24193", "Villagatón-Brañuelas": "24210"}
# Non-bold lines that are municipalities, recognisable by "<Name>: Para todo el municipio: ..." in alphabetical position
MUNI_LINE = re.compile(r"^[^:]+:\s*para todo el municipio", re.I)
TODO = re.compile(r"^para todo el municipio\s*:?\s*", re.I)


def lines(pdf):
    """[(is_bold_start, x0, text)] of the annex, continuation lines already joined."""
    out = []
    started = False
    for page in pymupdf.open(pdf):
        prev_y = None
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                spans = [s for s in ln["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).strip()
                x0, y0 = ln["bbox"][0], ln["bbox"][1]
                if text.startswith("CALENDARIO DE FIESTAS LOCALES PARA EL AÑO 2026"):
                    started = True
                    continue
                if not started or x0 > 400 or re.match(r"(Verificable|CVE|Página \d|Boletín núm)", text):
                    continue
                bold = "Bold" in spans[0]["font"]
                gap = y0 - prev_y if prev_y is not None else 99
                prev_y = y0
                # continuation of the previous line: left margin, or the tighter line spacing (11 pt vs 13.5 pt)
                if not bold and (x0 < 90 or gap < 12.3):
                    prev = out[-1]
                    sep = "" if prev[2].endswith("-") else " "
                    out[-1] = (prev[0], prev[1], (prev[2].rstrip("-") if sep == "" else prev[2]) + sep + text)
                    continue
                out.append((bold, x0, text))
    return out


def dated(txt):
    """'24 de julio, Festividad de X y 24 de agosto, Santa Marta' -> [(date, name)]; parentheses ignored for dates."""
    clean = re.sub(r"\([^)]*\)", "", txt)
    clean = re.sub(r",?\s*por traslado del (?:día )?\d{1,2} de \w+", "", clean)
    ms = list(DATE.finditer(clean))
    out = []
    for i, m in enumerate(ms):
        tail = clean[m.end():ms[i + 1].start() if i + 1 < len(ms) else len(clean)]
        tail = re.sub(r"[.,]?\s*(?:que\s+)?se traslada al.*$", "", tail, flags=re.I | re.S)
        name = re.sub(r"(^|\s+)(y|e)$", "", tail.strip(" ,.;")).strip(" ,.;")
        ds = [f"2026-{MES[m.group(2).lower()]:02d}-{int(d):02d}" for d in re.findall(r"\d{1,2}", m.group(1))]
        before = clean[ms[i - 1].end() if i else 0:m.start()]
        if i and re.search(r"se traslada al\s+(?:\w+\s+)?$", before, re.I):
            # "4 de junio, El Corpus. Se traslada al 8 de junio": the day moves; keep the new date with the old name
            _, old_name = out.pop()
            out += [(d, old_name) for d in ds]
            continue
        out += [(d, name) for d in ds]
    return out


def hol(pairs):
    seen = {}
    for d, n in pairs:
        seen.setdefault(d, n)
    return [{"date": d, "name": seen[d]} for d in sorted(seen)]


def blocks(pdf):
    cur = None
    for bold, x0, text in lines(pdf):
        if bold or MUNI_LINE.match(text):
            if cur:
                yield cur
            name, _, rest = text.partition(":")
            cur = {"name": name.strip(), "own": rest.strip(), "todo": [], "locs": []}
            if TODO.match(cur["own"]):
                cur["todo"].append(TODO.sub("", cur["own"]))
                cur["own"] = ""
        else:
            assert cur, text
            if TODO.match(text):
                cur["todo"].append(TODO.sub("", text))
            else:
                n, sep, rest = text.partition(":")
                assert sep, text
                cur["locs"].append((n.strip(), rest.strip()))
    if cur:
        yield cur


def main(pdf):
    mt = Matcher()
    by_ine, unmatched, raw = {}, [], {}
    for b in blocks(pdf):
        ine = ALIAS.get(b["name"]) or mt.match(b["name"], province=PROV)
        if not ine:
            unmatched.append(f"{b['name']}: {b['own']} | todo={b['todo']} | {b['locs']}")
            continue
        assert ine not in by_ine, b
        todo = [p for t in b["todo"] for p in dated(t)]
        own = dated(b["own"])
        rec = {"holidays": hol(own + todo)}
        notes = []
        if b["locs"]:
            rec["nucleos"] = [{"name": n, "holidays": hol(dated(r) + todo)} for n, r in b["locs"]]
            notes.append("The resolution also gives days for localities of the municipality (pedanías / entidades "
                         "locales menores); see nucleos.")
            if todo:
                notes.append("'Para todo el municipio' days are included for every locality.")
        if len(rec["holidays"]) != 2:
            notes.append(f"The resolution gives {len(rec['holidays'])} day(s) for {b['name']} itself.")
        if notes:
            rec["note"] = " ".join(notes)
        by_ine[ine] = rec
        raw[ine] = b
    if "--debug" in sys.argv:
        for ine, b in raw.items():
            print(ine, b["name"], "|", b["own"], "|", b["todo"], "|", by_ine[ine]["holidays"])
    missing = [f"{m['ine']} {m['name']}: not listed" for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("not listed:", len(missing))
    write_part("bop-leon-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(sys.argv[1])
