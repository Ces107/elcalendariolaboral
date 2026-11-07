"""Gipuzkoa: BOG 187 (01-10-2026), HTML edition. 31 July (San Ignacio de Loyola) for the
whole territory plus one day per municipality; a few municipalities split by locality
(Bidania-Goiatz, Ezkio-Itsaso, Pasaia). Table: NAME | date | festivity."""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common

W = common.workdir_from_argv()
ID = "bog-187"
META = {
    "title": "Resolución de 21 de septiembre de 2026 del delegado territorial de Trabajo y Seguridad Social de Gipuzkoa, por la que se aprueba el calendario de las fiestas locales de Gipuzkoa para el año 2027 (BOG nº 187, 01/10/2026, anuncio 6250)",
    "url": "https://egoitza.gipuzkoa.eus/gao-bog/castell/bog/2026/10/01/c2606250.htm",
    "published": "2026-10-01",
    "region": "pais-vasco",
}
TERRITORY = {"date": "2027-07-31", "name": "San Ignacio de Loyola"}
NOTE = ("31 July (San Ignacio de Loyola) is the local day for the whole of Gipuzkoa; in 2027 it "
        "falls on a Saturday. The other day is the municipality's own.")

raw = open(os.path.join(W, "dl", ID, "bog.htm"), encoding="cp1252", errors="replace").read()
t = re.sub(r"(?is)<(script|style).*?</\1>", "", raw)
t = re.sub(r"(?i)<br\s*/?>|</p>|</tr>|</div>|</li>", "\n", t)
t = re.sub(r"(?i)</td>", " | ", t)
t = html.unescape(re.sub(r"<[^>]+>", "", t))
lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
start = next(i for i, ln in enumerate(lines) if "Para cada municipio del Territorio" in ln) + 1
end = next(i for i, ln in enumerate(lines) if ln.startswith("San Sebastián, a 21 de septiembre de 2026"))
lines = lines[start:end]

ine = common.INE(W)
ine.add_manual("20", "MONDRAGON", "20055")  # INE: Arrasate/Mondragón
ine.add_manual("20", "LEABURU-TXARAMA", "20050")  # INE: Leaburu
ine.add_manual("20", "PLACENCIA DE LAS ARMAS", "20065")  # INE: Soraluze-Placencia de las Armas
DAY = re.compile(r"^\|\s*(\d{1,2}) (?:de )?(\w+)$")  # Errezil prints "11 noviembre"

munis = []
cur = None  # dict receiving the next date/festivity (municipality or locality)
expect = None
for ln in lines:
    if not ln.startswith("|"):
        if ln.isupper():
            munis.append({"name": ln, "holidays": [], "localities": []})
            cur = munis[-1]
        else:  # locality line inside a split municipality
            loc = {"name": ln, "holidays": []}
            munis[-1]["localities"].append(loc)
            cur = loc
        expect = "date"
        continue
    val = ln.lstrip("|").strip()
    m = DAY.match(ln)
    if expect == "date" and m:
        cur["holidays"].append({"date": common.iso(int(m.group(1)), m.group(2)), "name": None})
        expect = "fest"
    elif expect == "fest":
        if val:
            cur["holidays"][-1]["name"] = val
        expect = None

rows = []
for m in munis:
    code, how = ine.match("20", m["name"])
    row = {"name": m["name"].title(), "cpro": "20", "ine": code, "match": how,
           "holidays": [dict(TERRITORY)] + m["holidays"], "status": "boletin", "note": NOTE}
    if m["localities"]:
        row["localities"] = m["localities"]
        row["note"] = ("31 July (San Ignacio de Loyola) is the local day for the whole of Gipuzkoa (a Saturday "
                       "in 2027); the second day differs by locality (see localities).")
    rows.append(row)
    assert len(row["holidays"]) == (1 if m["localities"] else 2), row

for r in rows:
    if r["name"] == "Ezkio-Itsaso":
        r["note"] += (" The bulletin prints 22 June for Itsaso-Alegia with the name 'M.ª Magdalena' "
                      "(Mary Magdalene's day is 22 July); recorded as published.")
miss = common.coverage(ine, rows, ["20"])
print("missing:", miss)
SPOT = ("2026-11-07: HTML edition table read cell by cell. Spot-checked against the page: Abaltzisketa "
        "(24 Jun, no name), Altzo (8 Feb Lunes de carnaval), Mondragón (24 Jun S. Juan Bautista), "
        "Pasaia (Donibane 24 Jun, San Pedro 29 Jun, Antxo 7 Jul...), Ezkio-Itsaso (Itsaso-Alegia 22 Jun "
        "'M.ª Magdalena', as printed), Zumarraga (2 Jul Santa Isabel): all match.")
common.save_parsed(W, ID, META, rows, SPOT)
