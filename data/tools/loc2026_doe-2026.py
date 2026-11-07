"""Extremadura 2026 local holidays: DOE núm. 204 (23-X-2025), Resolución de 15 de octubre de 2025 de la Dirección
General de Trabajo, calendario laboral oficial de fiestas locales 2026 (annex: "MUNICIPIO.-" then
"d de mes y d de mes."), plus every later resolution of the same DG that modifies that annex.

Run:  python -E -P data/tools/loc2026_doe-2026.py <main.pdf> [<amendment-issue.pdf> ...]
  main  https://doe.juntaex.es/pdfs/doe/2025/2040o/25063799.pdf
  amendments: the DOE issue PDFs listed in AMEND_DOCS below (whole issues are fine: the resolution page is located
  by its DOE registration number and its text is parsed for "Municipio: d de mes y d de mes.").

Entries of the annex that are not municipalities (entidades locales menores, which the DOE lists alongside the
municipalities) are reported in "unmatched" with the suffix "[ELM]" when checked by hand.
"""
import datetime
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

import pymupdf  # noqa: E402

SID = "doe-2026"
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
          "octubre", "noviembre", "diciembre"]
DATE = re.compile(r"(\d{1,2})\s+de\s+([a-záéíóú]+)", re.I)
PROV = {"badajoz": "06", "caceres": "10"}

# bulletin spellings the generic matcher cannot resolve (checked by hand against data/municipios.json)
MANUAL = {("06", "ARROYO SAN SERVÁN"): "06012", ("10", "GARVÍN DE LA JARA"): "10083",
          ("10", "MAJADAS .DE TIETAR"): "10114"}  # last one printed with a stray dot; INE "Majadas" (de Tiétar)
# annex entries that are entidades locales menores / pedanías, not municipalities: none of them is an INE
# municipality name in its province (checked by hand); they are skipped, not mapped to their parent municipality
ELM = {("06", n) for n in (
    "ALMORCHÓN", "BARBAÑO", "BAZANA (LA)", "BROVALES", "CORTEGANA", "ENTRERRÍOS", "ENTRÍN ALTO", "GARGÁLIGAS",
    "GUADAJIRA", "GUADALPERALES (LOS)", "HELECHAL", "HERNÁN CORTÉS", "NAVA (LA)", "OBANDO", "PALAZUELO", "PALLARES",
    "PUEBLA DE ALCOLLARÍN", "PUERTO HURRACO", "RETAMAR", "RUECAS", "SAN BENITO DE LA CONTIENDA",
    "SAN FRANCISCO DE OLIVENZA", "SAN JORGE DE ALOR", "SAN RAFAEL DE OLIVENZA", "SANTA MARÍA",
    "SANTO DOMINGO DE GUZMÁN", "TORREFRESNEDA", "TORVISCAL (EL)", "VALDEHORNILLOS", "VALDIVIA", "VALUENGO",
    "VEGAS ALTAS", "VILLARREAL", "VIVARES", "YELBES", "ZURBARÁN")} | {("10", n) for n in (
    "ALONSO DE OJEDA", "AZABAL", "BARQUILLA DE PINARES", "BATÁN (EL)", "BRONCO (EL)", "CASAR DE MIAJADAS",
    "MOHEDA DE GATA (LA)", "NAVATRASIERRA", "PIZARRO", "PRADOCHANO", "RETAMOSA DE CABAÑAS", "ROTURA DE CABAÑAS",
    "SAN GIL", "SANTA MARÍA DE LAS LOMAS", "SOLANA DE CABAÑAS", "TREVEJO", "VALDEÍÑIGOS", "VALDENCÍN",
    "VALDESALOR", "VALRÍO")}


def ascii_low(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def iso(day, month):
    return datetime.date(2026, MONTHS.index(ascii_low(month)) + 1, int(day)).isoformat()


def clean_lines(doc, first=0, last=None):
    out = []
    for p in list(doc)[first:last]:
        for ln in p.get_text().splitlines():
            s = ln.replace("­", "-").strip()
            if not s or re.fullmatch(r"N[ÚU]MERO \d+", s) or re.fullmatch(r"\d{4,6}", s) or s == "• • •" \
                    or re.fullmatch(r"(Lunes|Martes|Miércoles|Jueves|Viernes) \d+ de \w+ de 20\d\d", s):
                continue
            out.append(s)
    return out


def parse_main(path):
    doc = pymupdf.open(path)
    lines = clean_lines(doc)
    i = next(k for k, s in enumerate(lines) if s.startswith("CALENDARIO OFICIAL DE FIESTAS LOCALES"))
    entries, prov, cur = [], None, None
    for s in lines[i + 1:]:
        m = re.match(r"La provincia de (\w+)", s)
        if m:
            prov = PROV[ascii_low(m.group(1))]
            continue
        if s.endswith(".-") or re.fullmatch(r"[^a-z]+\.-.*", s):
            name, _, rest = s.partition(".-")
            cur = {"prov": prov, "name": name.strip(), "text": rest.strip()}
            entries.append(cur)
        elif cur is not None:
            cur["text"] = (cur["text"] + " " + s).strip()
    for e in entries:
        e["dates"] = [iso(d, m) for d, m in DATE.findall(e["text"])]
        e["leftover"] = DATE.sub("", e["text"]).replace(" y ", " ").strip(" .,y")
    return entries


def parse_amendments(path):
    """Yield (label, date_published, prov, name, dates, raw) for each amendment resolution found in the PDF."""
    doc = pymupdf.open(path)
    for pno, page in enumerate(doc):
        t = page.get_text()
        if "se modifica el anexo de la Resolución de 15 de octubre de 2025" not in re.sub(r"\s+", " ", t):
            continue
        if "Mérida," not in t and pno + 1 < len(doc):
            t += "\n" + doc[pno + 1].get_text()
        head = re.search(r"N[ÚU]MERO (\d+)\s*\n\s*\w+ (\d+) de (\w+) de (20\d\d)", t)
        res = re.search(r"RESOLUCI[ÓO]N de (\d+ de \w+ de 20\d\d)", t)
        if not head or not res:
            continue
        pub = datetime.date(int(head.group(4)), MONTHS.index(ascii_low(head.group(3))) + 1,
                            int(head.group(2))).isoformat()
        label = f"Resolución de {res.group(1)} (DOE núm. {head.group(1)}, {pub})"
        body = t[t.find("ACUERDA"):t.find("Segundo.")]
        prov = None
        for ln in [x.strip() for x in body.splitlines()]:
            m = re.match(r"Provincia de (\w+)", ln)
            if m:
                prov = PROV[ascii_low(m.group(1))]
                continue
            m = re.match(r"([^:]+):\s*(.+)$", ln)
            if m and prov and DATE.search(m.group(2)):
                ds = [iso(d, mo) for d, mo in DATE.findall(m.group(2))]
                yield label, pub, prov, m.group(1).strip(), ds, ln


def main():
    main_pdf, *amend = sys.argv[1:]
    mt = Matcher()
    entries = parse_main(main_pdf)
    out, unmatched, names = {}, [], {}

    def lookup(prov, name):
        return MANUAL.get((prov, name)) or mt.match(name, province=prov)

    def record(ine, ds, notes):
        ds = sorted(set(ds))
        sundays = [d for d in ds if datetime.date.fromisoformat(d).weekday() == 6]
        notes = list(notes)
        if len(ds) != 2:
            notes.append(f"The DOE lists {len(ds)} date(s) for this municipality.")
        if sundays:
            notes.append(f"Bulletin date(s) {', '.join(sundays)} fall on a Sunday.")
        rec = {"holidays": [{"date": d, "name": ""} for d in ds]}
        if notes:
            rec["note"] = " ".join(notes)
        return rec

    for e in entries:
        if e["leftover"]:
            print("LEFTOVER TEXT", e)
        ine = lookup(e["prov"], e["name"])
        if ine is None:
            tag = " [ELM]" if (e["prov"], e["name"]) in ELM else ""
            print("UNMATCHED", e["prov"], e["name"], e["dates"], tag)
            unmatched.append(f"{e['name']} ({e['prov']}){tag}")
            continue
        if ine in out:
            print("DUPLICATE", ine, e["name"], names[ine])
        if len(e["dates"]) != 2:
            print("NOT TWO DATES", e["name"], e["text"])
        out[ine] = record(ine, e["dates"], [])
        names[ine] = e["name"]
    amend_labels = []
    for path in amend:
        found = list(parse_amendments(path))
        assert found, f"no amendment found in {path}"
        for label, pub, prov, name, ds, raw in sorted(found, key=lambda x: x[1]):
            ine = lookup(prov, name)
            assert ine, (label, name)
            old = [h["date"] for h in out[ine]["holidays"]] if ine in out else None
            print(f"AMEND {label}: {name} {old} -> {ds}   [{raw}]")
            out[ine] = record(ine, ds, [f"Updated by the {label} amendment." if old else
                                        f"Added by the {label} amendment."])
            amend_labels.append(label)
    for ine, v in out.items():
        if "Sunday" in v.get("note", ""):
            print("SUNDAY", ine, names.get(ine), v["holidays"])
    total = {p: sum(1 for m in mt.munis if m["ine"][:2] == p) for p in PROV.values()}
    for p in PROV.values():
        print(f"province {p}: {sum(1 for k in out if k[:2] == p)} / {total[p]}")
    missing = sorted(m["ine"] + " " + m["name"] for m in mt.munis if m["ine"][:2] in PROV.values() and m["ine"] not in out)
    print(f"not in the bulletin ({len(missing)}):", "; ".join(missing))
    source = {
        "title": "Resolución de 15 de octubre de 2025, de la Dirección General de Trabajo, por la que se hace público "
                 "el calendario laboral oficial de fiestas locales para la Comunidad Autónoma de Extremadura durante "
                 "el año 2026 (DOE núm. 204, 23-X-2025)"
                 + ("; anexo modificado por " + "; ".join(sorted(set(amend_labels), key=lambda s: s[-11:]))
                    if amend_labels else ""),
        "url": "https://doe.juntaex.es/pdfs/doe/2025/2040o/25063799.pdf",
        "published": "2025-10-23",
    }
    write_part(SID, source, out, region="extremadura", unmatched=unmatched)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
