"""Galicia 2026 local holidays: DOG núm. 210 (30-10-2025), Resolución do 21 de outubro de 2025 da Secretaría
Xeral de Emprego e Relacións Laborais (all concellos of the four provinces, annexes I-IV).

Usage: python -E -P data/tools/loc2026_dog-2026.py <path/to/AnuncioG0767-221025-0001_gl.pdf> [--dry]

The annexes are prose, one numbered paragraph per concello:
    "30. Coruña, A: 17 de febreiro, Martes de Entroido; 7 de outubro, festividade do Rosario."
so there is no column layout to misalign. Text is taken with PyMuPDF, page headers/margins dropped,
end-of-line hyphenation joined, then each annex is walked by its running number (1., 2., ...).
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

SID = "dog-2026"
SOURCE = {
    "title": "Resolución do 21 de outubro de 2025, da Secretaría Xeral de Emprego e Relacións Laborais, pola que se "
             "dá publicidade ás festas laborais de carácter local para o ano 2026, correspondentes aos concellos das "
             "catro provincias da Comunidade Autónoma de Galicia (DOG núm. 210, 30-10-2025)",
    "url": "https://www.xunta.gal/dog/Publicados/2025/20251030/AnuncioG0767-221025-0001_gl.html",
    "published": "2025-10-30",
}
MONTHS = {m: i for i, m in enumerate(
    "xaneiro febreiro marzo abril maio xuño xullo agosto setembro outubro novembro decembro".split(), 1)}
DATE = re.compile(r"^(\d{1,2}) de (" + "|".join(MONTHS) + r")\b,?\s*(.*)$")
ANNEXES = [("ANEXO I\n", "15", "A Coruña"), ("ANEXO II\n", "27", "Lugo"),
           ("ANEXO III\n", "32", "Ourense"), ("ANEXO IV\n", "36", "Pontevedra")]
# bulletin spelling -> INE code, verified by eye (filled after the first dry run)
MANUAL = {
    ("27", "Guntín de Pallares"): "27023",     # INE "Guntín"
    ("32", "Rúa de Valdeorras, A"): "32072",   # INE "Rúa, A"
}
WD = {5: "Saturday", 6: "Sunday"}
EXTRA_NOTES = {
    "15052": "Both the Galician and Spanish texts print 13 September (a Sunday) for 'Luns da Barca' (Monday); "
             "not corrected here, check for a later corrección de erros.",
}


def text_of(pdf):
    import pymupdf
    lines = []
    for page in pymupdf.open(pdf):
        for ln in page.get_text().splitlines():
            s = ln.strip()
            if not s or s.startswith(("ISSN", "DOG Núm.", "CVE-DOG", "https://www.xunta.gal", "Depósito legal")) \
                    or re.fullmatch(r"Páx\. \d+|Xoves, 30 de outubro de 2025|DOG Núm\. 210", s):
                continue
            lines.append(s)
    t = "\n".join(lines)
    t = re.sub(r"(\w)-\n(\w)", r"\1\2", t)       # end-of-line hyphenation
    t = re.sub(r"ANEXO (I{1,3}|IV)\n", lambda m: f"\0ANEXO {m.group(1)}\n", t)
    return t


def entries(block):
    """Walk '1. Name: ...' '2. Name: ...' by running number."""
    flat = " ".join(block.split())
    out, n, pos = [], 1, 0
    while True:
        m = re.compile(rf"(?:^|\s){n}\. ([^:]{{2,60}}): ").search(flat, pos)
        if not m:
            break
        nxt = re.compile(rf"\s{n + 1}\. [^:]{{2,60}}: ").search(flat, m.end())
        body = flat[m.end(): nxt.start() if nxt else len(flat)].strip()
        out.append((n, m.group(1).strip(), body))
        pos, n = m.end(), n + 1
    return out


def parse_body(body):
    body = body.strip().rstrip(".")
    hol, bad = [], []
    # "2 de febreiro, 29 de xuño" (dates without names) is split on the comma before a date too
    parts = re.split(r";\s*|,\s*(?=\d{1,2} de (?:" + "|".join(MONTHS) + r")\b)", body)
    for part in [p.strip() for p in parts if p.strip()]:
        m = DATE.match(part)
        if not m:
            bad.append(part)
            continue
        name = re.sub(r"^(luns|martes|mércores|xoves|venres|sábado|domingo),\s*", "", m.group(3).strip())
        hol.append({"date": dt.date(2026, MONTHS[m.group(2)], int(m.group(1))).isoformat(),
                    "name": name.rstrip(".")})
    return hol, bad


def main():
    pdf = sys.argv[1]
    dry = "--dry" in sys.argv
    mt = Matcher()
    t = text_of(pdf)
    chunks = {c.split("\n", 1)[0]: c for c in t.split("\0")[1:]}
    out, unmatched = {}, []
    for head, prov, pname in ANNEXES:
        block = chunks[head.strip()]
        block = block.split("Provincia:", 1)[1].split("\n", 1)[1]
        ents = entries(block)
        print(f"== {pname}: {len(ents)} entries")
        for n, name, body in ents:
            hol, bad = parse_body(body)
            seen = {}
            for h in hol:
                if h["date"] in seen:
                    bad.append(f"repeated date {h['date']}")
                seen.setdefault(h["date"], h)
            hol = sorted(seen.values(), key=lambda h: h["date"])
            notes = []
            if bad:
                notes.append("Bulletin text not parsed as a date: " + " | ".join(bad) + ".")
            if len(hol) != 2:
                notes.append(f"The resolution gives {len(hol)} date(s) for this concello.")
            for h in hol:
                d = dt.date.fromisoformat(h["date"])
                if d.weekday() in WD:
                    notes.append(f"{d.day}/{d.month} falls on a {WD[d.weekday()]}; recorded as published.")
            code = MANUAL.get((prov, name)) or mt.match(name, province=prov)
            if code in EXTRA_NOTES:
                notes.append(EXTRA_NOTES[code])
            flag = "" if len(hol) == 2 and not bad else "  <<<"
            print(f"{n:>3}. {name:<30} {code}  " + " | ".join(f"{h['date']} {h['name']}" for h in hol)
                  + (f"   NOTE: {' '.join(notes)}" if notes else "") + flag)
            if not code:
                unmatched.append(f"{name} ({pname})")
                continue
            assert code not in out, (code, name)
            out[code] = {"holidays": hol}
            if notes:
                out[code]["note"] = " ".join(notes)
    galicia = {x["ine"]: x["name"] for x in mt.munis if x["province_code"] in ("15", "27", "32", "36")}
    print("unmatched:", unmatched)
    print("missing from part:", [v for k, v in galicia.items() if k not in out], f"({len(out)}/{len(galicia)})")
    if not dry:
        write_part(SID, SOURCE, out, region="galicia", unmatched=unmatched)


if __name__ == "__main__":
    main()
