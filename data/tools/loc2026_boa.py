"""Aragón 2026 local holidays: Resolución de 4-11-2025 del Director General de Trabajo (BOA núm. 225, 20-11-2025) and
the complementary Resolución de 10-3-2026 (BOA núm. 56, 23-3-2026), which adds and corrects municipalities.

Download (outside the repo):
    https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1421874360606   (main.pdf)
    https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1440857030505   (comp.pdf)
Run: python -E -P data/tools/loc2026_boa.py main.pdf comp.pdf

Annex prose: "- Municipio. 30 de abril y 14 de agosto. San X y San Y. • Núcleo. 2 de julio y 31 de agosto."
Holiday names are only assigned when the printed names split cleanly into one per date.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
PROV = {"Huesca": "22", "Teruel": "44", "Zaragoza": "50"}
SOURCE = {
    "title": "Resolución de 4 de noviembre de 2025, del Director General de Trabajo, por la que se determinan las fiestas "
             "laborales para el año 2026 en los municipios de las provincias de Huesca, Teruel y Zaragoza (BOA núm. 225, "
             "de 20-11-2025), y Resolución complementaria de 10 de marzo de 2026 (BOA núm. 56, de 23-3-2026)",
    "url": "https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1421874360606",
    "published": "2025-11-20",
    "modifications": ["https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1440857030505"],
}
DATES = re.compile(r"^((?:\d{1,2}(?: y \d{1,2})? (?:de )?(?:" + "|".join(MES) + r")(?:,| y | e )?\s*)+)", re.I)
ONE = re.compile(r"(\d{1,2})(?: y (\d{1,2}))? (?:de )?(" + "|".join(MES) + r")", re.I)
HEAD = re.compile(r"BOLETÍN OFICIAL DE ARAGÓN|^\d{1,2} de \w+ de 20\d\d$|^Número \d+$|^csv: BOA\d+$|^\d+$")
ALIAS = {("22", "Torla"): "22230", ("22", "Binaced – Valcarca"): "22060", ("22", "Veracruz"): "22246", ("22", "Santa Cilia de Jaca"): "22208",
         ("22", "Isabena"): "22129", ("22", "Villanueva de Sijena"): "22251", ("44", "Santa Eulalia del Campo"): "44209",
         ("50", "Campillo"): "50071", ("50", "Pleitas de Jalón"): "50212",
         ("50", "San Martin de la Virgen del Moncayo"): "50234", ("50", "Villalba del Perejil"): "50286",
         ("50", "Vistabella de Huerva"): "50295"}
# Entidades locales menores listed as if they were municipalities: name -> parent INE
ELM = {("50", "Sofuentes"): "50248", ("50", "Ontinar de Salz"): "50298"}


def text_of(pdf):
    ls = [ln.strip() for p in pymupdf.open(pdf) for ln in p.get_text().splitlines()]
    return re.sub(r"\s+", " ", " ".join(ln for ln in ls if ln and not HEAD.search(ln)))


def parse_entry(body):
    """'30 de abril y 14 de agosto. San X y San Y' -> holidays"""
    m = DATES.match(body)
    if not m:
        return None
    ds = [f"2026-{MES[mo.lower()]:02d}-{int(d):02d}" for d1, d2, mo in ONE.findall(m.group(1)) for d in (d1, d2) if d]
    names_txt = body[m.end():].strip(" .")
    parts = [p.strip(" .") for p in re.split(r"\s*/\s*", names_txt)] if "/" in names_txt else \
        [p.strip(" .") for p in re.split(r"\s+y\s+", names_txt)]
    names = parts if names_txt and len(parts) == len(ds) else [""] * len(ds)
    out = {}
    for d, n in zip(ds, names):
        out[d] = out.get(d) or n
    return [{"date": d, "name": n} for d, n in sorted(out.items())]


def entries(pdf):
    text = text_of(pdf)
    for sec in re.split(r"Relación de días festivos de carácter local de los distintos municipios de la provincia de ", text)[1:]:
        prov = PROV[sec.split()[0]]
        sec = sec.split(" para el año 2026.", 1)[1]
        for m in re.finditer(r"(?:^|\s)([-•])\s+(.+?)(?=\s[-•]\s|$)", sec):
            kind, chunk = m.groups()
            nm = re.match(r"^(.+?)\.?\s+(\d.*)$", chunk)
            if not nm:
                yield prov, kind, chunk, None
                continue
            yield prov, kind, nm.group(1).strip(), nm.group(2)


def main(base, *comps):
    mt = Matcher()
    out, unmatched = {}, []
    for pdf in (base, *comps):
        cur = None
        for prov, kind, name, body in entries(pdf):
            hs = parse_entry(body) if body else None
            if hs is None:
                unmatched.append(f"{prov} unparsed: {kind} {name} {body or ''}"[:200])
                continue
            if kind == "•":
                if cur is None:
                    unmatched.append(f"{prov} núcleo without municipality: {name}")
                    continue
                rec = out[cur]
                rec.setdefault("nucleos", [])
                rec["nucleos"] = [n for n in rec["nucleos"] if n["name"] != name] + [{"name": name, "holidays": hs}]
                rec["note"] = "Some núcleos (entidades/pueblos) of the municipality have their own days; see nucleos."
                continue
            if (prov, name) in ELM:
                rec = out.setdefault(ELM[(prov, name)], {"holidays": []})
                rec["nucleos"] = [n for n in rec.get("nucleos", []) if n["name"] != name] + [{"name": name, "holidays": hs}]
                rec["note"] = "Some núcleos (entidades locales menores) have their own days; see nucleos."
                cur = None
                continue
            base_name = re.sub(r"\s*\((?!(?:El|La|Los|Las)\))[^)]*\)\s*$", "", name)  # "Hoz y Costean (Hoz de Barbastro)"
            ine = (ALIAS.get((prov, name)) or ALIAS.get((prov, base_name)) or mt.match(name, province=prov)
                   or mt.match(base_name, province=prov)
                   or mt.match(re.sub(r"\s*[–-]\s*", " y ", base_name), province=prov)
                   or mt.match(re.sub(r"\s*[–-]\s*", "-", base_name), province=prov))
            if not ine:
                unmatched.append(f"{prov} {name}: {body}")
                cur = None
                continue
            rec = {"holidays": hs}
            notes = []
            prev = out.get(ine, {})
            if prev.get("nucleos") and pdf == base:  # an ELM listed before its municipality
                rec["nucleos"] = prev["nucleos"]
                notes.append(prev["note"])
            if len(hs) != 2:
                notes.append(f"The resolution lists {len(hs)} date(s) for the municipality.")
            if notes:
                rec["note"] = " ".join(notes)
            out[ine] = rec
            cur = ine
    write_part("boa-2026", SOURCE, out, region="aragon", unmatched=unmatched)


if __name__ == "__main__":
    main(*sys.argv[1:])
