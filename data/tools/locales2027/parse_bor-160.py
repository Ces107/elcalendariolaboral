"""La Rioja: BOR 160 (21-08-2026), 'Calendario laboral de fiestas locales 2027' (III.3259).
Running text, one paragraph per municipality: 'Name: D de mes (fiesta) y D de mes (fiesta);
Aldea: ...'. Municipalities not listed get 'las dos fiestas tradicionales' (no dates) and are
left out. PDF from the Gobierno de La Rioja 'calendario festivos laborales 2027' page (the BOR
HTML page is behind a bot check)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common
import pymupdf

W = common.workdir_from_argv()
ID = "bor-160"
META = {
    "title": "Calendario laboral de fiestas locales 2027, Dirección General de Trabajo y Salud Laboral (BOR nº 160, 21/08/2026, III.3259)",
    "url": "https://ias1.larioja.org/boletin/Bor_Boletin_visor_Servlet?referencia=41863576-1-PDF-579228",
    "published": "2026-08-21",
    "region": "la-rioja",
}
MONTH = r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
TOKEN = re.compile(r"(\d{1,2})(?:\s+y\s+(\d{1,2}))?(?:\s+de)?\s+" + MONTH + r"\s*(\([^)]*\))?")
GENERIC = re.compile(r"^(Fiestas|Festivos) [Ll]ocales$")
NOISE = re.compile(r"^(BOLETÍN OFICIAL DE LA RIOJA|Núm\.160|Viernes, 21 de agosto|Página 14\d\d\d|Este documento se ha almacenado)")
START = re.compile(r"^[A-ZÁÉÍÓÚÑ][^:;()]{1,60}\s?:\s*\d")

doc = pymupdf.open(os.path.join(W, "dl", ID, "bor.pdf"))
text = "\n".join(p.get_text() for p in doc).replace("￿", " ").replace("\xa0", " ")
body = text.split("para cada localidad.")[1].split("Restantes municipios de La Rioja")[0]
entries = []
for ln in body.splitlines():
    ln = " ".join(ln.split())
    if not ln or NOISE.match(ln):
        continue
    if START.match(ln) and not (entries and entries[-1].endswith(";")):  # 'Aldea:' after ';' continues
        entries.append(ln)
    else:
        entries[-1] += " " + ln


def parse_dates(spec):
    out = []
    toks = list(TOKEN.finditer(spec))
    for i, t in enumerate(toks):
        name = t.group(4)[1:-1].strip() if t.group(4) else None
        days = [t.group(1)] + ([t.group(2)] if t.group(2) else [])
        for d in days:
            out.append({"date": common.iso(int(d), t.group(3)), "name": name})
    # a trailing generic name ('Fiestas Locales') covers every date of the entry
    last = out[-1]["name"] if out else None
    if last and GENERIC.match(last):
        for h in out:
            h["name"] = h["name"] or last
    return out


ine = common.INE(W)
ine.add_manual("26", "Pradillo de Cameros", "26118")  # INE: Pradillo
rows = []
for e in entries:
    segs = [s.strip() for s in e.split(";") if s.strip()]
    name, spec = segs[0].split(":", 1)
    code, how = ine.match("26", name.strip())
    row = {"name": name.strip(), "cpro": "26", "ine": code, "match": how,
           "holidays": parse_dates(spec), "status": "boletin"}
    if len(segs) > 1:
        row["localities"] = []
        for s in segs[1:]:
            ln, ls = s.split(":", 1)
            row["localities"].append({"name": ln.strip(), "holidays": parse_dates(ls)})
        row["note"] = "The resolution gives separate days for some villages of the municipality (see localities)."
    if any(h["name"] is None for h in row["holidays"]):
        row["note"] = (row.get("note", "") + " The resolution names only some of the days.").strip()
    rows.append(row)

for r in rows:
    if len(r["holidays"]) != 2:
        print("ODD COUNT:", r["name"], r["holidays"])
miss = common.coverage(ine, rows, ["26"])
print(f"listed {len(rows)}; not in the resolution ('dos fiestas tradicionales', no dates): {len(miss)}")
SPOT = ("2026-11-07: running text parsed with a date-token regex. Spot-checked against the PDF: Ábalos "
        "(3 Aug San Esteban, 8 Sep Virgen de la Rosa), Ajamil de Cameros (8 Jul, 17 Aug; Larriba 7 Sep, "
        "Torremuña 5 Aug as localities), Haro ('25 junio y 8 septiembre'), San Román de Cameros (20 Jan, "
        "15 May, printed without 'y'), Logroño (11 Jun San Bernabé, 21 Sep San Mateo), Zarzosa (5 Jun, 2 Aug): all match. "
        "Municipalities not named in the resolution keep 'las dos fiestas tradicionales' with no dates and are not included.")
common.save_parsed(W, ID, META, rows, SPOT)
