"""Aragón: BOA núm. 230 (27-11-2026), csv BOA20261127012. RESOLUCIÓN de 13 de noviembre de 2026, del Director General
de Trabajo, por la que se determinan las fiestas laborales, de carácter retribuido, no recuperables e inhábiles, para
el año 2027, en los municipios de las provincias de Huesca, Teruel y Zaragoza.

Input:  <W>/dl/boa/boa-20261127.pdf
  (https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1476882940808 ; found in the BOA open-data JSON of
   27-11-2026, BRSCGI?CMD=VERLST&BASE=BOLE&SEC=OPENDATABOAJSONAPP&OUTPUTMODE=JSON&PUBL=20261127, DOCN 007962837)
Run:    python -I parse_boa-230.py <W>

Annex in prose, one item per municipality: "- Name. 22 de enero y 11 de octubre. Festivity names." Items starting with
"•" are núcleos (villages) of the municipality printed before them; they go to that row's `localities`. When the
municipality item names a núcleo in brackets ("Isábena (La Puebla de Roda)"), its dates are those of that núcleo, as
printed; this is said in `note`. Festivity names are not paired with dates (the bulletin prints them as one phrase,
e.g. "Santas Nunilo y Alodia" for one day): `name` stays null. Single-date items are kept with one date and a note.
"- " items that match no municipality (La Sotonera's villages Aniés, Esquedas... printed with "-") are attached as
localities of the municipality before them when listed in VILLAGE_OF, else reported.
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SID = "boa-230"
META = {
    "title": "Resolución de 13 de noviembre de 2026, del Director General de Trabajo, por la que se determinan las "
             "fiestas laborales, de carácter retribuido, no recuperables e inhábiles, para el año 2027, en los "
             "municipios de las provincias de Huesca, Teruel y Zaragoza (BOA núm. 230, 27-11-2026)",
    "url": "https://www.boa.aragon.es/cgi-bin/EBOA/BRSCGI?CMD=VEROBJ&MLKOB=1476882940808",
    "published": "2026-11-27",
    "region": "aragon",
}
PROVS = [("Huesca", "22"), ("Teruel", "44"), ("Zaragoza", "50")]
MANUAL = {  # (cpro, bulletin name) -> INE code
    ("22", "Binaced-Valcarca"): "22060",  # INE "Binaced" (Valcarca is its village)
    ("22", "Santa Cilia de Jaca"): "22208",  # INE "Santa Cilia"
    ("44", "Santa Eulalia del Campo"): "44209",  # INE "Santa Eulalia"
    ("50", "Campillo"): "50071",  # INE "Campillo de Aragón"
    ("50", "Pleitas de Jalón"): "50212",  # INE "Pleitas"
    ("50", "Vistabella de Huerva"): "50295",  # INE "Vistabella"
}
VILLAGE_OF = {  # (cpro, bulletin name) -> parent INE code: villages printed as "- " items
    ("22", "Aniés"): "22904", ("22", "Esquedas"): "22904", ("22", "Lierta"): "22904",
    ("22", "Plasencia"): "22904", ("22", "Puibolea"): "22904", ("22", "Quinzano"): "22904",  # La Sotonera
    ("50", "Ontinar de Salz"): "50298",  # Zuera
    ("50", "Sofuentes"): "50248",  # Sos del Rey Católico
}
SPOTCHECK = ("Counts re-read from the pdftotext output independently of the parser: 548 '- ' items (540 municipalities "
             "+ 8 villages printed with '-') and 83 '•' villages = 631 items, all accounted for. Re-read against the "
             "text: Torralba de Ribota (18 Jan, 2 Aug), Villanova (29-30 Apr), Puertomingalvo (19 Mar, 14 Jun), Montanuy "
             "(29 Mar, 24 Jun), Berge (29 Apr, 14 Jul), Lechón (20 Jan, 10 Aug), Arcos de las Salinas (11, 13 Oct), "
             "Híjar (29 Mar, 21 Aug), Alcalá del Obispo (28 May, 27 Sep), Salillas de Jalón (21 May, 4 Oct), the "
             "capitals Huesca (22 Jan, 10 Aug), Teruel (30 Mar, 12 Jul), Zaragoza (29 Jan, 5 Mar), and the single-date "
             "rows Blecua-Torres (31 Aug) and Murero (17 Aug) - all match.")

HEADER = re.compile(r"^(BOLETÍN OFICIAL DE ARAGÓN|27 de noviembre de 2026|Número 230|csv: BOA20261127012|\d{1,2}|"
                    r"ANEXO\.?)$")
MONTH_RE = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"


def annex_text(pdf):
    import pymupdf
    lines = []
    for page in pymupdf.open(pdf):
        for ln in page.get_text().splitlines():
            ln = ln.strip()
            if not ln or HEADER.match(ln):
                continue
            ln = ln.replace("ANEXO.", "").strip()
            lines.append(ln)
    t = " ".join(lines)
    i = t.index("Relación de días festivos")
    return re.sub(r"\s+", " ", t[i:])


def sections(t):
    parts = re.split(r"Relación de días festivos de carácter local de los distintos municipios de la provincia de "
                     r"(Huesca|Teruel|Zaragoza) para el año 2027\.", t)
    assert parts[0].strip() == "", parts[0][:200]
    for k in range(1, len(parts), 2):
        yield parts[k], parts[k + 1]


def items(body):
    # an item starts with "- " or "• " followed by an upper-case letter (hyphens inside names have no spaces around)
    toks = re.split(r"(?:^|\s)([-•])\s+(?=[A-ZÁÉÍÓÚÑ])", " " + body)
    assert toks[0].strip() == "", toks[0][:100]
    for k in range(1, len(toks), 2):
        yield toks[k], toks[k + 1].strip()


def parse_item(txt):
    m = re.match(r"^(?P<name>[^\d]+?)\s*[.:]\s*(?P<rest>\d.*)$", txt)
    assert m, txt
    name, rest = m.group("name").strip(), m.group("rest")
    # date part: up to the first ". " followed by a letter, or the end
    dm = re.match(r"^(.*?)(?:\.\s+(?=[A-Za-zÁÉÍÓÚÑ])|\.?\s*$)", rest)
    dpart = dm.group(1)
    fest = rest[dm.end():].strip().rstrip(".") or None
    toks = re.findall(r"\d{1,2}|" + MONTH_RE, dpart, flags=re.I)
    dates, pend = [], []
    for tok in toks:
        if tok.isdigit():
            pend.append(int(tok))
        else:
            assert pend, (txt, toks)
            mon = common.month_num(tok)
            dates += [datetime.date(2027, mon, d) for d in pend]
            pend = []
    assert not pend and dates, (txt, toks)
    # nothing but separators may remain in the date part
    left = re.sub(r"\d{1,2}|" + MONTH_RE + r"|\bde\b|\bel\b|\by\b|[,/\s]", "", dpart, flags=re.I)
    assert left == "", (txt, left)
    return name, sorted(set(dates)), fest


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    for (cpro, bname), code in MANUAL.items():
        ine.add_manual(cpro, bname, code)
    t = annex_text(os.path.join(W, "dl", "boa", "boa-20261127.pdf"))
    rows, by_code, report = [], {}, []
    counts, deferred = {}, []
    for prov, body in sections(t):
        cpro = dict(PROVS)[prov]
        parent = None
        n_items = 0
        for kind, txt in items(body):
            n_items += 1
            name, dates, fest = parse_item(txt)
            hs = [{"date": d.isoformat(), "name": None} for d in dates]
            sundays = [d.isoformat() for d in dates if d.weekday() == 6]
            if kind == "-" and (cpro, name) not in VILLAGE_OF:
                code, how = ine.match(cpro, name)
                if not code:
                    report.append(f"NO INE ({prov}): {name} [{how}] {[h['date'] for h in hs]}")
                    parent = None
                    continue
                assert code not in by_code, (name, code, by_code.get(code, {}).get("name"))
                notes = []
                br = re.search(r"\(([^)]+)\)\s*$", name)
                if br and common.norm(br.group(1)) not in common.ARTICLES and \
                        common.norm(br.group(1)) not in {common.norm(x) for x in ("La", "El", "Los", "Las")}:
                    notes.append(f"The resolution prints the days of the núcleo {br.group(1)}.")
                if len(hs) != 2:
                    notes.append(f"The resolution gives {len(hs)} date(s).")
                if sundays:
                    notes.append(f"{', '.join(sundays)} falls on a Sunday; kept as published.")
                row = {"name": name, "cpro": cpro, "ine": code, "match": how, "status": "boletin", "holidays": hs}
                if fest:
                    row["festivities"] = fest
                if notes:
                    row["note"] = " ".join(notes)
                rows.append(row)
                by_code[code] = row
                parent = row
                counts[cpro] = counts.get(cpro, 0) + 1
            elif kind == "-":
                deferred.append((VILLAGE_OF[(cpro, name)], name, hs))
            else:
                assert parent, (prov, kind, name)
                deferred.append((parent["ine"], name, hs))
        print(f"{prov}: {n_items} items, {counts.get(cpro, 0)} municipalities")
    for code, lname, hs in deferred:
        p = by_code[code]
        p.setdefault("localities", []).append({"name": lname, "holidays": hs})
        add = f"The village {lname} has its own days: {', '.join(h['date'] for h in hs)} (see localities)."
        p["note"] = f"{p['note']} {add}" if p.get("note") else add
    print("villages attached:", len(deferred))
    for r in report:
        print(r)
    for r in rows:
        if str(r["match"]).startswith(("fuzzy", "ambig")):
            print("CHECK MATCH:", r["name"], r["match"], ine.by_code[r["ine"]])
    for prov, cpro in PROVS:
        print(f"not in the annex ({prov}):", [n for _, n in common.coverage(ine, rows, [cpro])])
    for r in rows:
        r.pop("festivities", None)
    common.save_parsed(W, SID, META, rows, SPOTCHECK)


if __name__ == "__main__":
    main()
