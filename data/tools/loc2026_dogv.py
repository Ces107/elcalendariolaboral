"""Comunitat Valenciana 2026 local holidays: Resolución de 12-11-2025 (DOGV 10238, 14-11-2025, CVE DOGV-C-2025-46326)
and its modifications (DOGV-C-2026-1043, 15-01-2026; DOGV-C-2026-6733, 03-03-2026).

Download (outside the repo), Spanish versions from dogv.gva.es:
    https://dogv.gva.es/datos/2025/11/14/pdf/2025_46326_es.pdf
    https://dogv.gva.es/datos/2026/01/15/pdf/2026_1043_es.pdf
    https://dogv.gva.es/datos/2026/03/03/pdf/2026_6733_es.pdf
Run: python -E -P data/tools/loc2026_dogv.py 2025_46326_es.pdf 2026_1043_es.pdf 2026_6733_es.pdf

Annex lines are "NAME: date, holiday name; date, holiday name." Entidades locales menores (EATIM) appear either as
"Eatim de X, dependiente de Y: ..." under their municipality or as "X, Eatim dependiente de Y: ..." in alphabetical
order; both go to the parent municipality's "nucleos".
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
PROV = {"ALICANTE": "03", "CASTELLÓN": "12", "CASTELLON": "12", "VALENCIA": "46"}
SOURCE = {
    "title": "Resolución de 12 de noviembre de 2025, por la que se aprueba el calendario de fiestas locales, retribuidas y "
             "no recuperables, en el ámbito de la Comunitat Valenciana para el año 2026 (DOGV núm. 10238, de 14-11-2025), "
             "modificada por las Resoluciones de 13-1-2026 (DOGV núm. 10281, de 15-1-2026) y de 27-2-2026 (DOGV núm. "
             "10314, de 3-3-2026)",
    "url": "https://dogv.gva.es/datos/2025/11/14/pdf/2025_46326_es.pdf",
    "published": "2025-11-14",
    "modifications": ["https://dogv.gva.es/datos/2026/01/15/pdf/2026_1043_es.pdf",
                      "https://dogv.gva.es/datos/2026/03/03/pdf/2026_6733_es.pdf"],
}
DATE = re.compile(r"(\d{1,2})(?:\s*(?:y|i|,)\s*(\d{1,2}))?\s+(?:de\s+)?(" + "|".join(MES) + r")\b", re.I)
HEAD = re.compile(r"^(Núm\. \d+ / [\d.]+|\d+ / \d+|CVE: DOGV.*|https://dogv\.gva\.es/)$")
UPPER_ENTRY = re.compile(r"^[«\"]?([A-ZÀ-ÝÑÇ][A-ZÀ-ÝÑÇ'´’`·.,()/\- ]+?):\s*(.*)$")
EATIM_UNDER = re.compile(r"^Eatim de (.+?),? dependiente de [^:]+?\s*:\s*(.*)$")
EATIM_ALPHA = re.compile(r"^(.+?), Eatim dependiente de ([^:]+?)\s*:\s*(.*)$")
# Bulletin spellings the matcher cannot resolve (province, bulletin name) -> INE
ALIAS = {("03", "RAFÓL DE ALMÚNIA"): "03110", ("12", "LA POBLA DE TORNESA"): "12094",
         ("03", "HONDÓN de los FRAILES"): "03078"}


def holidays(txt):
    """'16 de abril, Festividad de Santa Faz; 23 de junio, Fogueres' -> [(date, name), ...]"""
    ms = list(DATE.finditer(txt))
    out = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(txt)
        name = txt[m.end():end].strip(" ,;.:").strip()
        name = re.sub(r"[,;]?\s*\b(y|e)$", "", name).strip(" ,;.").replace("  ", " ")
        mes = MES[m.group(3).lower()]
        days = [int(m.group(1))] + ([int(m.group(2))] if m.group(2) else [])
        for j, d in enumerate(days):
            k = f"2026-{mes:02d}-{d:02d}"
            out[k] = out.get(k) or (name if j == len(days) - 1 else "")
    return sorted(out.items())


def entries(pdf):
    """Yield dicts {prov, name, rest, nucleos:[[name, rest]], parent?} from the annex."""
    lines = [ln.strip() for p in pymupdf.open(pdf) for ln in p.get_text().splitlines()]
    lines = [ln for ln in lines if ln and not HEAD.match(ln)]
    prov, cur = None, None
    for ln in lines:
        m = re.search(r"FIESTAS LOCALES EN LA PROVINCIA DE (\w+)", ln, re.I)
        if m:
            if cur:
                yield cur
            cur, prov = None, PROV[m.group(1).upper()]
            continue
        if prov is None:
            continue
        me, ma, mu = EATIM_UNDER.match(ln), EATIM_ALPHA.match(ln), UPPER_ENTRY.match(ln)
        if cur and me:
            cur["nucleos"].append([me.group(1).strip(), me.group(2)])
        elif ma:
            if cur:
                yield cur
            cur = {"prov": prov, "name": ma.group(1).strip(), "rest": ma.group(3), "nucleos": [],
                   "parent": ma.group(2).strip()}
        elif (mu and mu.group(1) == mu.group(1).upper()) or ln.startswith("HONDÓN de los FRAILES:"):
            if cur:
                yield cur
            name, rest = (mu.group(1), mu.group(2)) if mu and mu.group(1) == mu.group(1).upper() else ln.split(":", 1)
            cur = {"prov": prov, "name": name.strip(), "rest": rest, "nucleos": []}
        elif cur:
            if cur["nucleos"]:
                cur["nucleos"][-1][1] += " " + ln
            else:
                cur["rest"] += " " + ln
    if cur:
        yield cur


def clean_name(n):
    n = n.replace("´", "'").replace("’", "'").replace("`", "'")
    return re.sub(r"^(L|EL|LA|ELS|LES)\s*'\s*", r"\1'", n)


def front(n):
    """'PERELLÓ, EL' -> 'EL PERELLÓ'"""
    m = re.match(r"^(.*), (EL|LA|L'|L’|LOS|LAS|ELS|LES)$", n)
    return f"{m.group(2)} {m.group(1)}" if m else n


def main(base, *mods):
    mt = Matcher()
    out, unmatched, eatims = {}, [], []

    def find(prov, name):
        return (ALIAS.get((prov, name)) or mt.match(clean_name(name), province=prov)
                or mt.match(clean_name(name).title(), province=prov))

    def put(prov, name, rest, src, nucleos=()):
        rest = re.sub(r"[»\"]?;?\s*$", "", rest.strip())
        ine = find(prov, name)
        if not ine:
            unmatched.append(f"{prov} {name}: {rest} ({src})")
            return
        hs = holidays(rest.replace(": ", "; "))
        rec = {"holidays": [{"date": d, "name": n} for d, n in hs]}
        old = out.get(ine, {})
        nuc = list(old.get("nucleos", [])) + [{"name": n, "holidays": [{"date": d, "name": x} for d, x in holidays(r)]}
                                              for n, r in nucleos]
        notes = []
        if nuc:
            rec["nucleos"] = nuc
            notes.append("Entidades locales menores (EATIM) of the municipality have their own days; see nucleos.")
        if not hs and not nuc:
            unmatched.append(f"{ine} {name}: no dates in the resolution ({rest[:60]})")
            out.pop(ine, None)
            return
        if len(hs) != 2:
            notes.append(f"The resolution lists {len(hs)} date(s): «{rest[:200]}»")
        if notes:
            rec["note"] = " ".join(notes)
        out[ine] = rec

    for e in entries(base):
        if e.get("parent"):
            eatims.append(e)
        else:
            put(e["prov"], e["name"], e["rest"], "base", e["nucleos"])
    for e in eatims:
        ine = find(e["prov"], e["parent"]) or find(e["prov"], e["parent"].upper())
        if not ine or ine not in out:
            unmatched.append(f"EATIM {e['name']} of {e['parent']}: parent not found")
            continue
        rec = out[ine]
        rec.setdefault("nucleos", []).append({"name": front(e["name"]).title().replace("D'", "d'").replace("D’", "d’").replace(" De ", " de "),
                                              "holidays": [{"date": d, "name": x} for d, x in holidays(e["rest"])]})
        if "EATIM" not in rec.get("note", ""):
            rec["note"] = (rec.get("note", "") + " Entidades locales menores (EATIM) of the municipality have their own "
                           "days; see nucleos.").strip()
    for pdf in mods:
        text = " ".join(ln.strip() for p in pymupdf.open(pdf) for ln in p.get_text().splitlines()
                        if not HEAD.match(ln.strip()))
        text = re.sub(r"\s+", " ", text)
        prov = None
        for m in re.finditer(r"provincia de (Alicante|Castellón|Valencia)|Debe decir:? «([^:»]+): ([^»]+)»", text):
            if m.group(1):
                prov = PROV[m.group(1).upper()]
            else:
                ine = find(prov, m.group(2).strip())
                keep = out.get(ine, {}).get("nucleos")
                put(prov, m.group(2).strip(), m.group(3), Path(pdf).name)
                if keep and ine in out:
                    out[ine]["nucleos"] = keep
    missing = [f"{m['ine']} {m['name']}" for m in mt.munis if m["region"] == "comunitat-valenciana" and m["ine"] not in out]
    write_part("dogv-2026", SOURCE, out, region="comunitat-valenciana",
               unmatched=unmatched + [f"not listed: {x}" for x in missing])


if __name__ == "__main__":
    main(*sys.argv[1:])
