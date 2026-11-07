"""Soria province 2026 local holidays: Oficina Territorial de Trabajo de Soria, "Fiestas laborales año 2026" (BOP Soria
núm. 108, 22-9-2025, BOPSO-108-22092025), copy hosted by the Junta de Castilla y León (Trabajo y Prevención,
'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/898/228/07%20BOP%20FIESTAS%20LOCALES%20SORIA%2026,0.pdf
Run:
    python -E -P data/tools/loc2026_bop-soria-2026.py <downloaded.pdf>

Annex lines "ABEJAR: 2 de febrero y 24 de junio" (municipality in capitals, left) followed by indented lines
"Ontalvilla de Almazán: 12 y 13 de junio" for its localities (pedanías / entidades locales menores), dates only.
"""
import re
import sys
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "42"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]
MES = {m: i for i, m in enumerate(MESES, 1)}
SOURCE = {
    "title": "Junta de Castilla y León, Oficina Territorial de Trabajo de Soria. Fiestas laborales año 2026 (BOP Soria "
             "núm. 108, de 22-9-2025, BOPSO-108-22092025)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/898/228/07%20BOP%20FIESTAS%20LOCALES%20SORIA%2026,0.pdf",
    "published": "2025-09-22",
}
ALIAS = {"BURGO DE OSMA (EL)": "42043"}
# VILLACIERVITOS is printed in capitals but is a locality (of Villaciervos), not a municipality: left in unmatched


def dates(txt):
    out, pending = [], []
    for num, mes in re.findall(r"(\d{1,2})(?:\s+(?:de\s+)?(" + "|".join(MESES) + r"))?", txt.lower()):
        pending.append(int(num))
        if mes:
            out += [f"2026-{MES[mes]:02d}-{d:02d}" for d in pending]
            pending = []
    assert not pending and out, txt
    return sorted(set(out))


def lines(pdf):
    started = False
    out = []
    for page in pymupdf.open(pdf):
        ls = []
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                t = "".join(s["text"] for s in ln["spans"]).strip()
                if t and 60 < ln["bbox"][0] < 300:
                    ls.append((ln["bbox"][1], ln["bbox"][0], t))
        for y, x, t in sorted(ls):
            if t == "ANEXO":
                started = True
                continue
            if not started or re.match(r"(Núm\.|Boletín Oficial|BOPSO-|Pág\.|(Lunes|Martes|Miércoles|Jueves|Viernes), \d)",
                                       t) or "Boletín Oficial" in t:
                continue
            if re.match(r"^Soria, \d", t) or t.startswith("El Jefe") or t.startswith("La Jefa"):
                return out
            if ":" not in t and ";" in t:  # "RENIEBLAS; 5 de febrero y 10 de agosto"
                t = t.replace(";", ":", 1)
            if t.startswith(":") and out:  # "CASTILLEJO DE ROBLEDO" / ": 2 de mayo y 12 de septiembre"
                out[-1] = (out[-1][0], out[-1][1] + t)
                continue
            if ":" not in t and out and not t.isupper():  # wrapped line
                out[-1] = (out[-1][0], out[-1][1] + " " + t)
                continue
            out.append((x, t))
    return out


def main(pdf):
    mt = Matcher()
    by_ine, unmatched, cur = {}, [], None
    for x, t in lines(pdf):
        name, _, rest = t.partition(":")
        name = re.sub(r"\s+", " ", name).strip()
        # municipalities are in capitals; a mixed-case name is a locality even when printed unindented (Valdespina)
        if x < 95 and name.isupper():
            ine = ALIAS.get(name) or mt.match(name, province=PROV)
            if not ine:
                unmatched.append(t)
                cur = None
                continue
            assert ine not in by_ine, name
            ds = dates(rest)
            by_ine[ine] = {"holidays": [{"date": d, "name": ""} for d in ds]}
            if len(ds) != 2:
                by_ine[ine]["note"] = f"The list gives {len(ds)} day(s) for the municipality."
            cur = ine
        else:
            if not cur:
                unmatched.append(f"(locality of an unmatched municipality) {t}")
                continue
            rec = by_ine[cur]
            rec.setdefault("nucleos", []).append({"name": name, "holidays": [{"date": d, "name": ""} for d in dates(rest)]})
            note = "The list also gives days for localities of the municipality; see nucleos."
            rec["note"] = (rec.get("note", "").replace(note, "") + " " + note).strip()
    missing = [f"{m['ine']} {m['name']}: not listed" for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("not listed:", len(missing))
    write_part("bop-soria-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(sys.argv[1])
