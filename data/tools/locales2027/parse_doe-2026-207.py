"""Extremadura: DOE núm. 207 (27-10-2026), Resolución de 15 de octubre de 2026 de la Dirección General
de Trabajo, calendario laboral oficial de fiestas locales 2027 (annex by province: 'NAME.' at x~103,
'D de mes y D de mes.' at x>=300 on the same printed line). Dates only, no festivity names.

Input:  <W>/dl/doe/doe-26062650.pdf  (https://doe.juntaex.es/pdfs/doe/2026/2070o/26062650.pdf)
Run:    python -I parse_doe-2026-207.py <W>

Entidades locales menores (Barbaño, La Bazana, ...) are not INE municipalities: they are kept out of
'rows' and listed in 'sub_municipal' with their dates.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SID = "doe-2026-207"
META = {
    "title": "Resolución de 15 de octubre de 2026, de la Dirección General de Trabajo, por la que se hace público "
             "el calendario laboral oficial de fiestas locales para la Comunidad Autónoma de Extremadura durante "
             "el año 2027 (DOE núm. 207, 27-X-2026, 2026062650)",
    "url": "https://doe.juntaex.es/pdfs/doe/2026/2070o/26062650.pdf",
    "published": "2026-10-27",
    "region": "extremadura",
}
PROV = {"BADAJOZ": "06", "CACERES": "10"}
DATE = re.compile(r"(\d{1,2})\s*de\s*([a-záéíóú]+)", re.I)
# bulletin spellings that differ from the INE dictionary, checked by hand
MANUAL = [("10", "GARVÍN DE LA JARA", "10083"),   # INE: Garvín
          ("10", "MAJADAS DE TIETAR", "10114")]   # INE: Majadas


def lines_of(page):
    lines = {}
    for w in page.get_text("words"):
        lines.setdefault(round((w[1] + w[3]) / 2 / 3), []).append(w)
    for k in sorted(lines):
        ws = sorted(lines[k], key=lambda w: w[0])
        yield (" ".join(w[4] for w in ws if w[0] < 300).strip(),
               " ".join(w[4] for w in ws if w[0] >= 300).strip())


def main():
    W = common.workdir_from_argv()
    import pymupdf
    doc = pymupdf.open(os.path.join(W, "dl", "doe", "doe-26062650.pdf"))
    ine = common.INE(W)
    for cp, nm, code in MANUAL:
        ine.add_manual(cp, nm, code)
    entries, cpro, started, pend = [], None, False, ""
    for page in doc:
        for name, dates in lines_of(page):
            if name.startswith(("NÚMERO", "Martes 27 de octubre")) or re.fullmatch(r"\d{5}", dates or name):
                continue
            m = re.match(r"LA PROVINCIA DE (\w+)", common.strip_accents(name).upper())
            if m and m.group(1) in PROV:
                cpro, started = PROV[m.group(1)], True
                continue
            if not started or name.startswith(("ANEXO", "Calendario oficial")):
                continue
            if name and not dates:          # long name wrapped over two lines
                pend = (pend + " " + name).strip()
                continue
            name = (pend + " " + name).strip()
            pend = ""
            found = DATE.findall(dates)
            entries.append((cpro, name.rstrip(". "), dates, found))
    rows, sub, problems = [], [], []
    for cpro, name, dates, found in entries:
        hol = [{"date": common.iso(int(d), mth), "name": None} for d, mth in found]
        if not hol:
            problems.append((name, dates))
            continue
        code, how = ine.match(cpro, name)
        if not code:
            sub.append({"name": name, "cpro": cpro, "holidays": hol, "match": how})
            continue
        r = {"name": name, "cpro": cpro, "ine": code, "match": how, "holidays": hol, "status": "boletin",
             "note": "The DOE annex gives dates only, without festivity names."}
        if len(hol) != 2:
            r["note"] = f"The DOE annex gives {len(hol)} date(s) for this municipality, without festivity names."
        import datetime as dt
        wk = [h["date"] for h in hol if dt.date.fromisoformat(h["date"]).weekday() >= 5]
        if wk:
            r["note"] += " Falls on a weekend, as published: " + ", ".join(wk) + "."
        rows.append(r)
    seen = {}
    for r in rows:
        if r["ine"] in seen:
            print("DUPLICATE INE:", r["ine"], seen[r["ine"]], r["name"])
        seen[r["ine"]] = r["name"]
    for p in problems:
        print("NO DATES:", p)
    for s in sub:
        print("NOT AN INE MUNICIPALITY:", s["cpro"], s["name"], [h["date"] for h in s["holidays"]], s["match"])
    miss = common.coverage(ine, rows, PROV.values())
    print(f"missing from annex: {len(miss)}")
    for c, n in miss:
        print("  MISSING", c, n)
    spot = SPOT
    common.save_parsed(W, SID, META, rows, spot, {"missing": [list(x) for x in miss], "sub_municipal": sub})


SPOT = ("2026-11-07: annex read by word coordinates (name x<300, dates x>=300 on the same printed line). "
        "All 388 INE municipalities of Badajoz and Cáceres present. Re-read in the raw page text, all equal: "
        "Sancti-Spíritus 14-IX/7-X, Pedroso de Acim 18-X/7-XII, Majadas de Tiétar 20-I/7-IX, Higuera de "
        "Vargas 12-II/3-IX, Arroyomolinos de la Vera 25-I/16-VIII, Piedras Albas 9-V (Sunday)/13-VIII, "
        "Badajoz 9-II/24-VI, Mérida 13-V/10-XII, Cáceres 23-IV/28-V, Plasencia 10-VI/11-VI. 56 entidades "
        "locales menores/pedanías listed in the annex are kept in 'sub_municipal'.")

if __name__ == "__main__":
    main()
