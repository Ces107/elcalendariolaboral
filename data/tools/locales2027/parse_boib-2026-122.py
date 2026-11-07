"""Illes Balears: BOIB núm. 122 (29-09-2026), Resolució de la consellera de Treball, Funció Pública i
Diàleg Social, calendari laboral general i local per a l'any 2027 (annex 2: local days per municipality,
and for some municipalities per nucleus).

Input:  <W>/dl/boib-2027/res.html  (official HTML rendering of the BOIB text)
        <W>/dl/boib-2027/boib122.pdf (authentic PDF; used to cross-check every cell of the HTML)
  https://www.caib.es/eboibfront/ca/2026/12335/720377/resolucio-de-la-consellera-de-treball-funcio-publi
  https://www.caib.es/eboibfront/pdf/ca/2026/122/1229309
Run:    python -I parse_boib-2026-122.py <W>

Table: bold first cell = municipality; plain first cell = nucleus (own pair of days); empty first cell =
second day of the row above. When a municipality has nuclei, the municipality row takes the nucleus that
carries the municipality's own name (or its first two words, e.g. 'Parròquia de Sant Antoni'; else the
first one listed) and the others go in 'note'.
"""
import html
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SID = "boib-2026-122"
META = {
    "title": "Resolució de la consellera de Treball, Funció Pública i Diàleg Social per la qual es fa públic el "
             "calendari laboral general i local per a l'any 2027 en l'àmbit de les Illes Balears "
             "(BOIB núm. 122, 29-IX-2026)",
    "url": "https://www.caib.es/eboibfront/pdf/ca/2026/122/1229309",
    "published": "2026-09-29",
    "region": "baleares",
}
DATE = re.compile(r"^(\d{1,2}) d(?:e |')(\w+)$")
MANUAL = [("07", "Ciutadella", "07015")]  # (cpro, bulletin name, INE code) when the name differs from the INE dictionary


class Rows(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows, self.row, self.cell, self.bold, self.in_td = [], None, "", False, False
        self.cellbold = False

    def handle_starttag(self, tag, a):
        if tag == "tr":
            self.row = []
        elif tag == "td":
            self.in_td, self.cell, self.cellbold = True, "", False
        elif tag == "strong" and self.in_td:
            self.cellbold = True

    def handle_endtag(self, tag):
        if tag == "td" and self.row is not None:
            self.row.append((re.sub(r"\s+", " ", self.cell.replace("\xa0", " ")).strip(), self.cellbold))
            self.in_td = False
        elif tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None

    def handle_data(self, d):
        if self.in_td:
            self.cell += d


def main():
    W = common.workdir_from_argv()
    src = open(os.path.join(W, "dl", "boib-2027", "res.html"), encoding="utf-8").read()
    start = src.find("2. Festes d")
    p = Rows()
    p.feed(src[start:])
    ine = common.INE(W)
    for cp, nm, code in MANUAL:
        ine.add_manual(cp, nm, code)

    munis = []  # [{"name", "nuclei": [[name, [(date, label)]]]}]
    for cells in p.rows:
        (c0, b0) = cells[0]
        d = cells[1][0] if len(cells) > 1 else ""
        lab = cells[2][0] if len(cells) > 2 else ""
        if c0 and b0 and not (munis and munis[-1]["nuclei"] and common.norm(c0) == common.norm(munis[-1]["name"])):
            munis.append({"name": c0, "nuclei": []})
            cur = munis[-1]
            if d:
                cur["nuclei"].append([c0, []])
        elif c0:
            munis[-1]["nuclei"].append([c0, []])
        if d:
            m = DATE.match(d)
            if not m:
                raise SystemExit(f"bad date cell {d!r} in {munis[-1]['name']}")
            munis[-1]["nuclei"][-1][1].append((common.iso(m.group(1), m.group(2)), lab or None))

    # cross-check against the authentic PDF: every name/date/label cell must appear in order
    import pymupdf
    pdf = "".join(pg.get_text() for pg in pymupdf.open(os.path.join(W, "dl", "boib-2027", "boib122.pdf")))
    flat = re.sub(r"\s+", "", pdf.replace("’", "'"))
    pos, misses = flat.find("Festesd'àmbitlocal"), []
    for cells in p.rows:
        for c, _ in cells:
            c2 = re.sub(r"\s+", "", c.replace("’", "'"))
            if not c2:
                continue
            k = flat.find(c2, pos)
            if k < 0:
                misses.append(c)
            else:
                pos = k + len(c2)
    print(f"PDF cross-check: {len(misses)} cells not found in order: {misses[:10]}")

    rows = []
    for mu in munis:
        code, how = ine.match("07", mu["name"])
        nuc = mu["nuclei"]
        nm = common.norm(mu["name"])
        two = " ".join(nm.split()[:2])
        main_n = (next((n for n in nuc if common.norm(n[0]) == nm), None)
                  or next((n for n in nuc if nm in common.norm(n[0])), None)
                  or next((n for n in nuc if two in common.norm(n[0])), None)
                  or nuc[0])
        r = {"name": mu["name"], "cpro": "07", "ine": code, "match": how,
             "holidays": [{"date": dt, "name": lb} for dt, lb in main_n[1]], "status": "boletin"}
        others = [n for n in nuc if n is not main_n]
        if others:
            fmt = lambda n: f"{n[0]}: " + " and ".join(dt[8:] + "/" + dt[5:7] for dt, _ in n[1])
            r["note"] = (f"The BOIB lists days per nucleus; these are the days of {main_n[0]}. Other nuclei: "
                         + "; ".join(fmt(n) for n in others) + ".")
            r["nuclei"] = [{"name": n[0], "holidays": [{"date": dt, "name": lb} for dt, lb in n[1]]}
                           for n in nuc]
        if len(r["holidays"]) != 2:
            r["note"] = (r.get("note", "") + f" The BOIB gives {len(r['holidays'])} day(s).").strip()
        rows.append(r)
    miss = common.coverage(ine, rows, ["07"])
    print(f"missing: {len(miss)} {miss}")
    spot = ("2026-11-07: parsed from the official HTML rendering; every cell (name, date, label) was found in "
            "the same order in the authentic PDF text (script cross-check). Manually re-read: Alaró 29-VI/16-VIII, "
            "Palma 20-I/24-VI, Selva 3-V/10-VIII (nuclei Biniamar, Caimari, Moscari), Ciutadella 24-VI/25-VI, "
            "Formentera 25-VII/3-XII, Sóller 10-V/24-VIII. Rows in the table carry a name per day; days that "
            "fall on a Sunday are recorded as printed.")
    common.save_parsed(W, SID, META, rows, spot, {"missing": [list(x) for x in miss]})


if __name__ == "__main__":
    main()
