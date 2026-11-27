"""Albacete province: BOP Albacete núm. 137 (25-11-2026), anuncio 32.620. Resolución de la Delegación Provincial de la
Consejería de Economía, Empresas y Empleo en Albacete acordando el calendario de fiestas laborales locales para el año
2027 en la provincia de Albacete (signed 13-11-2026).

Input:  <W>/dl/bop-albacete/bop_137.pdf
  (https://bop.dipualba.es/servicesajax/descararchivobopcompleto/?a=22780 , the whole bulletin)
Run:    python -I parse_bop-albacete-137.py <W>

Annex "Población | Días festivos" ("7 mayo y 29 septiembre", "6 y 8 septiembre", "21 y 24 de mayo"), read as text
lines between the "Relación de fiestas laborales locales para el año 2027" heading and the "En Albacete a" signature.
Rows that are not INE municipalities (pedanías such as Aguas Nuevas, El Salobral, Bormate, La Felipa) are printed
as unmatched and left out, as in the 2026 parser (data/tools/loc2026_bop-albacete-2026.py).
"""
import datetime
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common  # noqa: E402

SID = "bop-albacete-137"
CPRO = "02"
META = {
    "title": "Resolución de la Delegación Provincial de la Consejería de Economía, Empresas y Empleo en Albacete "
             "acordando el calendario de fiestas laborales locales para el año 2027 en la provincia de Albacete (BOP "
             "Albacete núm. 137, 25-11-2026, anuncio 32.620)",
    "url": "https://bop.dipualba.es/servicesajax/descararchivobopcompleto/?a=22780",
    "published": "2026-11-25",
    "region": "castilla-la-mancha",
}
SPOTCHECK = ("Re-read against the pdftotext -layout output independently of the parser: 96 annex rows = 87 municipalities "
             "(all 87 of the province) + 9 pedanías. Albacete (24 Jun, 8 Sep), Almansa (6 May, 30 Aug), Caudete (5 Apr, "
             "8 Sep), Hellín (3 May, 24 Oct), Higueruela ('21 y 24 de mayo'), Minaya (12 Feb, 7 Sep), Montealegre del "
             "Castillo (printed '26 abril y 19 marzo'), La Roda (15 May, 6 Aug), Villarrobledo (12 Feb, 18 Aug), "
             "Villavaliente ('22 enero y el 14 mayo') - all match.")
MONTH_RE = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
SKIP = re.compile(r"^(Número 137|Página \d+|Miércoles, 25 de noviembre de 2026|Población|Días festivos)\b")


def lines(pdf):
    import pymupdf
    t = "\n".join(p.get_text() for p in pymupdf.open(pdf))
    i = t.index("Relación de fiestas laborales locales para el año 2027")
    j = t.index("En Albacete a 13 de noviembre de 2026", i)
    body = [ln.strip() for ln in t[i:j].splitlines()[1:]]
    return [ln for ln in body if ln and not SKIP.match(ln)]


def dates_of(txt):
    toks = re.findall(r"\d{1,2}|" + MONTH_RE, txt, flags=re.I)
    out, pend = [], []
    for tok in toks:
        if tok.isdigit():
            pend.append(int(tok))
        else:
            out += [datetime.date(2027, common.month_num(tok), d) for d in pend]
            pend = []
    assert not pend and out, txt
    left = re.sub(r"\d{1,2}|" + MONTH_RE + r"|\bde\b|\bel\b|\by\b|[,\s]", "", txt, flags=re.I)
    assert left == "", (txt, left)
    return sorted(out)


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    ls = lines(os.path.join(W, "dl", "bop-albacete", "bop_137.pdf"))
    # PyMuPDF gives name and dates either on one line or on two consecutive lines
    pairs, k = [], 0
    while k < len(ls):
        m = re.match(r"^(\D+?)\s{2,}(\d.*)$", ls[k])
        if m:
            pairs.append((m.group(1).strip(), m.group(2)))
            k += 1
        else:
            assert re.match(r"^\d", ls[k + 1]), (ls[k], ls[k + 1])
            pairs.append((ls[k], ls[k + 1]))
            k += 2
    rows, by_code = [], {}
    for name, dtxt in pairs:
        ds = dates_of(dtxt)
        hs = [{"date": d.isoformat(), "name": None} for d in ds]
        code, how = ine.match(CPRO, name)
        if not code:
            print("NOT A MUNICIPALITY (left out):", name, [h["date"] for h in hs], how)
            continue
        assert code not in by_code, (name, code)
        notes = [f"{d.isoformat()} falls on a Sunday; kept as published." for d in ds if d.weekday() == 6]
        r = {"name": name, "cpro": CPRO, "ine": code, "match": how, "status": "boletin", "holidays": hs}
        if notes:
            r["note"] = " ".join(notes)
        rows.append(r)
        by_code[code] = r
    print("annex rows:", len(pairs), "municipalities:", len(rows))
    print("not in the annex:", [n for _, n in common.coverage(ine, rows, [CPRO])])
    common.save_parsed(W, SID, META, rows, SPOTCHECK)


if __name__ == "__main__":
    main()
