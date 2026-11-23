"""Valencia province: BOP València núm. 224 (20-11-2026), anunci 2026/14547. Resolució de 10 de novembre de 2026 de la
Direcció Territorial de Vivenda, Ocupació, Joventut i Igualtat de València, calendari de festes locals 2027.

The resolution first appeared in BOP núm. 223 (19-11-2026, anunci 2026/14151) without its annex; anunci 2026/14547
("correcció d'errors") republishes it in full with the annex, so that is the source used here.

Input:  <W>/dl/bop-valencia-224/bopv_2026_14547_VA.pdf
  (https://bop.dival.es/bop/downloads?anuncioNumReg=2026/14547&lang=va ; found with the BOP València portal search
   https://bop.dival.es/bop/xhtml/portal.xhtml, "fiestas locales", 02-11..23-11-2026. The lang=es PDF has the same
   annex text, checked line by line, and is the URL given as source.)
Run:    python -I parse_bop-valencia-224.py <W>

Prose annex (Spanish, some Valencian) parsed by cv_util, as Alicante/Castellón. Pre-processing: Valencian month names
in dates ("30 de març") read as the same month; "X, EATIM dependiente de Y:" rewritten to cv_util's Eatim form, and the
EATIM days go to the parent municipality's localities. Paragraphs where the printed text is inconsistent are in FIX,
each with a note saying what the bulletin prints; no date is guessed.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(1, os.path.dirname(HERE))
import common  # noqa: E402
import cv_util  # noqa: E402
from muni_match import Matcher  # noqa: E402

SID = "bop-valencia-224"
CPRO = "46"
PDF = "bopv_2026_14547_VA.pdf"
META = {
    "title": "Resolució de 10 de novembre de 2026, de la Direcció Territorial de Vivenda, Ocupació, Joventut i Igualtat "
             "de València, per la qual s'aprova el calendari de festes locals, retribuïdes i no recuperables, en "
             "l'àmbit de la província de València per a l'any 2027 (BOP València núm. 224, 20-11-2026, anunci "
             "2026/14547, correcció d'errors que publica l'annex omès a l'anunci 2026/14151 del BOP núm. 223)",
    "url": "https://bop.dival.es/bop/downloads?anuncioNumReg=2026/14547&lang=es",
    "published": "2026-11-20",
    "region": "comunitat-valenciana",
}
DROP = [r"^CSV:", r"^URL de validaci", r"^N[úu]m\. 224$", r"^P[àa]g\.$", r"^20-11-2026$", r"^\d{1,2}$",
        r"^Verificable a ", r"^ANEXO/ANNEX", r"^RELACI[ÓO] DE FESTES LOCALS"]
CA_MONTHS = {"gener": "enero", "febrer": "febrero", "març": "marzo", "abril": "abril", "maig": "mayo",
             "juny": "junio", "juliol": "julio", "agost": "agosto", "setembre": "septiembre", "octubre": "octubre",
             "novembre": "noviembre", "desembre": "diciembre"}
CA_RE = re.compile(r"(\d)\s*(?:de\s+|d['’]\s*)(" + "|".join(CA_MONTHS) + r")(?![a-zà-ú])", re.I)
EATIM_IN = re.compile(r"^(.+?),\s*EATIM dependiente de (.+?)\s*:\s*(.*)$")
# bulletin paragraph -> what to keep, with the reason (checked by eye against the PDF)
FIX = {
    "PALMERA": dict(dates=["2027-06-25"], names=[None], note="The bulletin prints \"25de junio, La Puríssima Concepció; "
                    "25 de junio, Mare de Déu del Carmen\": the same day twice with two festivities, so the second day "
                    "is not clear; only 25 June is listed here."),
    "SIMAT DE LA VALLDIGNA": dict(dates=["2027-04-05", "2027-07-26"], names=["Sant Vicent", "Santa Anna"],
                                  note="The bulletin prints \"26 de Julio, 26 de Julio, Santa Anna\" (the date "
                                       "repeated); read as one day, 26 July."),
}
# cv_util drops a leading "festividad/festivitat (de|del)", which here leaves a bare adjective: put the printed words back
NAME_BACK = {"Fallera": "Festividad fallera", "Local": "Festividad local", "Crist": "Festivitat del Crist"}
# EATIM names as printed (capitals, article after a comma) -> display name
LOC_NAMES = {"BARRACA D’AIGÜES VIVES, LA": "La Barraca d'Aigües Vives", "MARENY DE BARRAQUETES": "Mareny de Barraquetes",
             "PERELLÓ, EL": "El Perelló"}
SPOTCHECK = ("Re-read against the PDF text (pages 3-14) independently of the parser: València (22 Jan San Vicente "
             "Mártir, 5 Apr San Vicente Ferrer), Torrent, Gandia, Sagunt/Sagunto, Paterna, Alzira (+ La Barraca "
             "d'Aigües Vives), Sueca (+ Mareny de Barraquetes 30 Mar, El Perelló 7 Dec), Xàtiva (5 Apr, 5 Aug), "
             "Burjassot, Ontinyent, Vilamarxant (\"30de agosto\") - all match. 266 of 266 municipalities.")


def main():
    W = common.workdir_from_argv()
    import pymupdf
    doc = pymupdf.open(os.path.join(W, "dl", SID, PDF))
    text = "".join(p.get_text() for p in doc)
    text = text[text.index("RELACIÓN DE FIESTAS LOCALES"):].split("\n", 1)[1]
    text = CA_RE.sub(lambda m: f"{m.group(1)} de {CA_MONTHS[m.group(2).lower()]}", text)
    lines = []
    for s in cv_util.clean_lines(text, DROP):
        m = EATIM_IN.match(s)
        lines.append(f"Eatim de {m.group(1)}, dependiente de {m.group(2)} : {m.group(3)}" if m else s)
    paras = cv_util.paragraphs(lines)
    ents = cv_util.parse_annex(paras)
    ine, mt = common.INE(W), Matcher()
    rows, by_code, report = [], {}, []
    for e in ents:
        if e["kind"] == "eatim":
            continue
        code, how = cv_util.match(ine, mt, CPRO, e["name"])
        fix = FIX.get(e["name"])
        dates, names = e["dates"], [NAME_BACK.get(n, n) for n in e["names"]]
        notes = []
        if fix:
            keep = fix["dates"]
            names = fix.get("names") or [names[dates.index(d)] if d in dates else None for d in keep]
            dates = keep
            notes.append(fix["note"])
        elif e["issues"]:
            for iss in e["issues"]:
                if "printed" in iss and "year" not in iss:
                    notes.append(f"The bulletin prints a weekday that does not match the date ({iss}); "
                                 "dates kept as published.")
                elif "year printed" in iss:
                    notes.append(f"The bulletin prints the {iss.split(chr(39))[1]} year on one date of this 2027 "
                                 "list; read as 2027.")
                else:
                    notes.append(iss)
        if len(dates) != 2:
            report.append(f"COUNT {len(dates)} {e['name']}: {e['body'][:160]}")
        if not dates:
            report.append(f"SKIP {e['name']}: {e['body'][:80]}")
            continue
        row = {"name": e["name"], "cpro": CPRO, "ine": code, "match": how, "status": "boletin",
               "holidays": [{"date": d, "name": n} for d, n in zip(dates, names)]}
        if notes:
            row["note"] = " ".join(notes)
        if e["issues"]:
            report.append(f"ISSUE {e['name']}: {e['issues']} -> {dates}")
        assert code not in by_code or not code, (e["name"], code)
        rows.append(row)
        by_code[code] = row
    for e in ents:
        if e["kind"] != "eatim":
            continue
        code, _ = cv_util.match(ine, mt, CPRO, e["parent"])
        parent = by_code.get(code)
        assert parent, e
        lname = LOC_NAMES[e["name"]]
        parent.setdefault("localities", []).append(
            {"name": lname, "holidays": [{"date": d, "name": n} for d, n in zip(e["dates"], e["names"])]})
        add = f"The entidad local menor {lname} has its own days: {', '.join(e['dates'])} (see localities)."
        parent["note"] = f"{parent['note']} {add}" if parent.get("note") else add
    for r in report:
        print(r)
    miss = common.coverage(ine, rows, [CPRO])
    print("paragraphs:", len(ents), "rows:", len(rows))
    print("not in the annex:", [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOTCHECK)


if __name__ == "__main__":
    main()
