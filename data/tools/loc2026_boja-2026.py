"""Andalucía 2026 local holidays: BOJA núm. 197 (14-X-2025), Resolución de 6 de octubre de 2025 de la DG de
Trabajo, Seguridad y Salud Laboral (annex: one list per province, "MUNICIPIO  dd DE MES  dd DE MES"),
plus the three later resolutions that modify that annex:
  BOJA 247 (24-XII-2025)  Resolución 18-XII-2025: Coín corrected, 19 late municipalities added
  BOJA 33  (18-II-2026)   Resolución 12-II-2026: Loja
  BOJA 79  (27-IV-2026)   Resolución 20-IV-2026: 6 municipalities moved off 18-V (regional election day)
  BOJA 32  (17-II-2026)   Corrección de errores: Guarromán
(found by scanning the section-3 index of every BOJA issue 2025/198-250 and 2026/1-215 on 2026-11-07)

Run:  python -E -P data/tools/loc2026_boja-2026.py <main.pdf> <boja247.pdf> <boja33.pdf> <boja79.pdf> <boja32.pdf>
  main     https://www.juntadeandalucia.es/eboja/2025/197/BOJA25-197-00016-13517-01_00327114.pdf
  boja247  https://www.juntadeandalucia.es/eboja/2025/247/BOJA25-247-00002-17289-01_00330886.pdf
  boja33   https://www.juntadeandalucia.es/eboja/2026/33/BOJA26-033-00001-2142-01_00333367.pdf
  boja79   https://www.juntadeandalucia.es/eboja/2026/79/BOJA26-079-00002-5437-01_00336674.pdf
  boja32   https://www.juntadeandalucia.es/eboja/2026/32/BOJA26-032-00001-2090-01_00333315.pdf

The main annex is read with PyMuPDF word coordinates (words grouped per printed line), not pdftotext.
The amendments are short; their content is written below as data and every entry is asserted to be present
in the amendment PDF text, so the script fails loudly if a wrong file is passed.
"""
import datetime
import difflib
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

import pymupdf  # noqa: E402

SID = "boja-2026"
SOURCE = {
    "title": "Resolución de 6 de octubre de 2025, de la Dirección General de Trabajo, Seguridad y Salud Laboral, "
             "por la que se publica la relación de fiestas locales de los municipios de la Comunidad Autónoma de "
             "Andalucía para el año 2026 (BOJA núm. 197, 14-X-2025); modificada por Resoluciones de 18-XII-2025 "
             "(BOJA núm. 247, 24-XII-2025), 12-II-2026 (BOJA núm. 33, 18-II-2026) y 20-IV-2026 (BOJA núm. 79, "
             "27-IV-2026), y corrección de errores (BOJA núm. 32, 17-II-2026)",
    "url": "https://www.juntadeandalucia.es/eboja/2025/197/BOJA25-197-00016-13517-01_00327114.pdf",
    "published": "2025-10-14",
}
PROV = {"ALMERIA": "04", "CADIZ": "11", "CORDOBA": "14", "GRANADA": "18", "HUELVA": "21",
        "JAEN": "23", "MALAGA": "29", "SEVILLA": "41"}
MONTHS = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO", "SEPTIEMBRE",
          "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
DATE = re.compile(r"(\d{1,2})\s*DE\s*([A-Z]+)")

# bulletin spellings the generic matcher cannot resolve (checked by hand against data/municipios.json)
MANUAL = {("11", "ZAHARA DE LA SIERRA"): "11042", ("18", "DOMINGO PÉREZ"): "18915",
          ("18", "HUÉTOR SANTILLÁN"): "18099", ("18", "PINAR, EL"): "18910", ("18", "PÍÑAR"): "18159",
          ("18", "POLOPOS – LA MAMOLA"): "18162", ("18", "POLOPOS - LA MAMOLA"): "18162",
          ("18", "POLOPOS-LA MAMOLA"): "18162", ("21", "CORTELAZOR LA REAL"): "21026",
          ("23", "BEJÍJAR"): "23014",  # printed with J; INE "Begíjar", no other Jaén municipality is close
          ("23", "HORNOS DE SEGURA"): "23043", ("41", "ALANÍS DE LA SIERRA"): "41002"}

# amendments: (pdf index in argv, province, bulletin name, [dates], evidence strings that must be in the PDF)
AMEND = [
    # BOJA 247: Coín corrected; late inclusions
    (1, "29", "COÍN", ["4 DE MAYO", "1 DE JUNIO"], ["COÍN 4 DE MAYO 1 DE JUNIO"]),
    (1, "04", "CÓBDAR", ["19 DE ENERO", "10 DE AGOSTO"], ["CÓBDAR 19 DE ENERO 10 DE AGOSTO"]),
    (1, "04", "GARRUCHA", ["16 DE JULIO", "17 DE AGOSTO"], ["GARRUCHA 16 DE JULIO 17 DE AGOSTO"]),
    (1, "04", "ORIA", ["11 DE MAYO", "24 DE AGOSTO"], ["ORIA 11 DE MAYO 24 DE AGOSTO"]),
    (1, "18", "ALPUJARRA DE LA SIERRA", ["2 DE ENERO", "29 DE SEPTIEMBRE"],
     ["ALPUJARRA DE LA SIERRA 2 DE ENERO 29 DE SEPTIEMBRE"]),
    (1, "18", "CÁDIAR", ["2 DE OCTUBRE", "5 DE OCTUBRE"], ["CÁDIAR 2 DE OCTUBRE 5 DE OCTUBRE"]),
    (1, "18", "CASTRIL", ["5 DE OCTUBRE", "8 DE OCTUBRE"], ["CASTRIL 5 DE OCTUBRE 8 DE OCTUBRE"]),
    (1, "18", "COGOLLOS DE GUADIX", ["27 DE ABRIL", "28 DE AGOSTO"], ["COGOLLOS DE GUADIX 27 DE ABRIL 28 DE AGOSTO"]),
    (1, "18", "MOCLÍN", ["16 DE ENERO", "5 DE OCTUBRE"], ["MOCLÍN 16 DE ENERO 5 DE OCTUBRE"]),
    (1, "18", "PUEBLA DE DON FADRIQUE", ["25 DE MAYO", "28 DE DICIEMBRE"],
     ["PUEBLA DE DON FADRIQUE 25 DE MAYO 28 DE DICIEMBRE"]),
    (1, "18", "VILLANUEVA DE LAS TORRES", ["3 DE FEBRERO", "3 DE AGOSTO"],
     ["VILLANUEVA DE LAS TORRES 3 DE FEBRERO 3 DE AGOSTO"]),
    (1, "23", "BAÑOS DE LA ENCINA", ["11 DE MAYO", "30 DE OCTUBRE"], ["BAÑOS DE LA ENCINA 11 DE MAYO 30 DE OCTUBRE"]),
    (1, "23", "CAMBIL", ["23 DE FEBRERO", "22 DE MAYO"], ["CAMBIL 23 DE FEBRERO 22 DE MAYO"]),
    (1, "23", "CAROLINA, LA", ["15 DE MAYO", "24 DE NOVIEMBRE"], ["CAROLINA, LA 15 DE MAYO 24 DE NOVIEMBRE"]),
    (1, "23", "PORCUNA", ["21 DE MARZO", "4 DE SEPTIEMBRE"], ["PORCUNA 21 DE MARZO 4 DE SEPTIEMBRE"]),
    (1, "23", "RUS", ["3 DE FEBRERO", "23 DE SEPTIEMBRE"], ["RUS 3 DE FEBRERO 23 DE SEPTIEMBRE"]),
    # Málaga block: names and dates sit on the same printed line (checked by word y-coordinates: PUJERRA y=136,
    # 13 DE JUNIO/3 DE NOVIEMBRE y=136; SAYALONGA y=151, 20 DE JULIO/7 DE OCTUBRE y=151)
    (1, "29", "PUJERRA", ["13 DE JUNIO", "3 DE NOVIEMBRE"], ["PUJERRA 13 DE JUNIO 3 DE NOVIEMBRE"]),
    (1, "29", "SAYALONGA", ["20 DE JULIO", "7 DE OCTUBRE"], ["SAYALONGA 20 DE JULIO 7 DE OCTUBRE"]),
    # BOJA 33
    (2, "18", "LOJA", ["25 DE ABRIL", "4 DE SEPTIEMBRE"], ["Loja 25 de abril 4 de septiembre"]),
    # BOJA 79
    (3, "21", "ESCACENA DEL CAMPO", ["1 DE JUNIO", "17 DE AGOSTO"], ["Escacena del Campo 1 de junio 17 de agosto"]),
    (3, "29", "ALMOGÍA", ["6 DE ABRIL", "11 DE MAYO"], ["Almogía 6 de abril 11 de mayo"]),
    (3, "29", "GUARO", ["25 DE MAYO", "31 DE AGOSTO"], ["Guaro 25 de mayo 31 de agosto"]),
    (3, "41", "CAMPANA, LA", ["11 DE MAYO", "10 DE SEPTIEMBRE"], ["Campana, La 11 de mayo 10 de septiembre"]),
    (3, "41", "MOLARES, LOS", ["15 DE MAYO", "29 DE JULIO"], ["Molares, Los 15 de mayo 29 de julio"]),
    (3, "41", "VILLAVERDE DEL RÍO", ["1 DE JUNIO", "8 DE SEPTIEMBRE"], ["Villaverde del Río 1 de junio 8 de septiembre"]),
]
AMEND.append((4, "23", "GUARROMÁN", ["12 DE JUNIO", "24 DE JULIO"],
              ["GUARROMÁN 12 DE JUNIO 24 DE JUNIO", "Debe decir: «GUARROMÁN 12 DE JUNIO 24 DE JULIO"]))
AMEND_LABEL = {1: "BOJA 247, 24-XII-2025", 2: "BOJA 33, 18-II-2026", 3: "BOJA 79, 27-IV-2026",
               4: "BOJA 32, 17-II-2026 (corrección de errores)"}


def ascii_up(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper()


def iso(day, month):
    m = ascii_up(month)
    if m not in MONTHS:
        close = difflib.get_close_matches(m, MONTHS, n=1, cutoff=0.75)
        if not close:
            raise ValueError(f"month? {month}")
        m = close[0]
    d = datetime.date(2026, MONTHS.index(m) + 1, int(day))
    return d.isoformat()


def lines_of(page):
    """Words grouped by printed line (vertical centre within 3 pt), each line sorted left to right."""
    words = sorted(page.get_text("words"), key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    out = []
    for w in words:
        yc = (w[1] + w[3]) / 2
        if out and abs(out[-1][0] - yc) <= 3:
            out[-1][1].append(w)
        else:
            out.append([yc, [w]])
    return [sorted(ws, key=lambda w: w[0]) for _, ws in out]


def parse_main(path):
    doc = pymupdf.open(path)
    rows, odd = [], []
    prov = None
    for pno, page in enumerate(doc):
        if pno == 0:
            continue  # preamble; the ANEXO starts on page 2
        for ws in lines_of(page):
            text = " ".join(w[4] for w in ws).strip()
            key = ascii_up(text.replace(" ", ""))
            if key in PROV:
                prov = PROV[key]
                continue
            if (prov is None or re.match(r"^(BOJA|Bolet|N.mero|Dep.sito|p.gina|ANEXO|FIESTAS LOCALES)", text)
                    or re.fullmatch(r"\d{8}", text) or "juntadeandalucia" in text):
                continue
            ws = [w for w in ws if not re.fullmatch(r"\d{8}", w[4])]  # page-margin document id
            # the name column ends where the first "<day> DE" starts
            idx = next((i for i in range(len(ws) - 1)
                        if re.fullmatch(r"\d{1,2}", ws[i][4]) and ws[i + 1][4].upper() == "DE"), None)
            if idx is None:
                odd.append((pno + 1, text))
                continue
            name = " ".join(w[4] for w in ws[:idx]).strip()
            right = ascii_up(" ".join(w[4] for w in ws[idx:]))
            dates = DATE.findall(right)
            leftover = DATE.sub("", right).strip()
            rows.append({"page": pno + 1, "prov": prov, "name": name, "raw": right,
                         "dates": [iso(d, m) for d, m in dates], "leftover": leftover})
    return rows, odd


def main():
    main_pdf, *amend_pdfs = sys.argv[1:]
    assert len(amend_pdfs) == 4, "pass main PDF + BOJA 247, 33, 79, 32 PDFs"
    amend_text = {}
    for i, p in enumerate(amend_pdfs, 1):
        # text rebuilt from printed lines (word coordinates), so a name and its dates are adjacent
        t = " ".join(" ".join(w[4] for w in ws) for pg in pymupdf.open(p) for ws in lines_of(pg))
        amend_text[i] = re.sub(r"\s+", " ", t.replace("“", "").replace("”", ""))
    rows, odd = parse_main(main_pdf)
    for o in odd:
        print("UNPARSED LINE:", o)
    mt = Matcher()
    out, unmatched, src_of = {}, [], {}

    def put(prov, name, dates, note=None, origin="main"):
        ine = MANUAL.get((prov, name)) or mt.match(name, province=prov)
        if ine is None:
            # "SURNAME, ART" forms and dash variants
            alt = re.sub(r"\s*[–-]\s*", "-", name)
            ine = mt.match(alt, province=prov)
        if ine is None:
            print("UNMATCHED", prov, name, mt.candidates(name, province=prov))
            unmatched.append(f"{name} ({prov})")
            return
        if ine in out and origin == "main":
            print("DUPLICATE", ine, name, src_of[ine])
        ds = sorted(set(dates))
        sundays = [d for d in ds if datetime.date.fromisoformat(d).weekday() == 6]
        notes = [note] if note else []
        if len(ds) != 2:
            print("NOT TWO DATES", prov, name, ds)
            notes.append(f"The BOJA lists {len(ds)} date(s) for this municipality.")
        if sundays:
            notes.append(f"Bulletin date(s) {', '.join(sundays)} fall on a Sunday.")
            print("SUNDAY", name, sundays)
        rec = {"holidays": [{"date": d, "name": ""} for d in ds]}
        if notes:
            rec["note"] = " ".join(notes)
        out[ine] = rec
        src_of[ine] = (origin, name)

    for r in rows:
        if r["leftover"]:
            print("LEFTOVER TEXT", r)
        put(r["prov"], r["name"], r["dates"])
    for i, prov, name, dates, ev in AMEND:
        for e in ev:
            assert e in amend_text[i], (i, e)
        ds = [iso(*DATE.match(ascii_up(x)).groups()) for x in dates]
        ine = MANUAL.get((prov, name)) or mt.match(name, province=prov)
        old = [h["date"] for h in out[ine]["holidays"]] if ine in out else None
        print(f"AMEND {AMEND_LABEL[i]}: {name} {old} -> {ds}")
        put(prov, name, ds, note=f"Updated by the {AMEND_LABEL[i]} amendment." if old else
            f"Added to the annex by the {AMEND_LABEL[i]} amendment.", origin=AMEND_LABEL[i])

    per = {}
    for ine in out:
        per[ine[:2]] = per.get(ine[:2], 0) + 1
    total = {p: sum(1 for m in mt.munis if m["ine"][:2] == p) for p in PROV.values()}
    for p in sorted(per):
        print(f"province {p}: {per[p]} / {total[p]}")
    missing = sorted(m["ine"] + " " + m["name"] for m in mt.munis if m["ine"][:2] in PROV.values() and m["ine"] not in out)
    print(f"not in the bulletin ({len(missing)}):", "; ".join(missing))
    write_part(SID, SOURCE, out, region="andalucia", unmatched=unmatched)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
