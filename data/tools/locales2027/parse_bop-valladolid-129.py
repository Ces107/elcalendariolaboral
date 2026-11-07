"""BOP Valladolid 129 (09-VII-2026), BOPVA-A-2026-02051: Resolución de 6 de julio de 2026 de la
Oficina Territorial de Trabajo, fiestas locales 2027.

Annex Ayuntamiento | 1ª Fiesta | 2ª Fiesta without rules: words on the same printed line,
name 100-270, 1st date 270-365, 2nd >=365. 'No comunicada' = no date sent by the council.
Usage: python -I parse_bop-valladolid-129.py <workdir>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import cyl_util as cu  # noqa: E402

import pymupdf  # noqa: E402

SID = "bop-valladolid-129"
META = {
    "title": "Resolución de 6 de julio de 2026, de la Oficina Territorial de Trabajo de Valladolid, para la determinación de las fiestas locales, a efectos laborales, en los municipios de la provincia de Valladolid para el año 2027 (BOP Valladolid núm. 129, 09-VII-2026, BOPVA-A-2026-02051)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/569/674/Fiestas%20BOPVA-A-2026-02051.pdf?blobheader=application%2Fpdf%3Bcharset%3DUTF-8&blobnocache=true",
    "published": "2026-07-09",
    "region": "castilla-y-leon",
}
C1, C2 = 270, 365
# bulletin spelling -> INE name (same municipality)
MANUAL = {"BAHABÓN DE VALCORBA": "Bahabón", "CASTREJON": "Castrejón de Trabancos",
          "CASTROPONCE DE VALDERAUEY": "Castroponce", "CORCOS DEL VALLE": "Corcos",
          "MURIEL DE ZAPARDIEL": "Muriel", "SAN LLORENTE DEL VALLE": "San Llorente",
          "SAN SALVADOR DE HORNIJA": "San Salvador", "VILLACO DE ESGUEVA": "Villaco",
          "VILLAFUERTE DE ESGUEVA": "Villafuerte"}
# entidades locales menores printed as rows of their own (parents from public gazetteers:
# Foncastín and Torrecilla del Valle -> Rueda; La Santa Espina -> Castromonte;
# Villamarciel and Villavieja del Cerro -> Tordesillas)
LOCALITY_OF = {"FONCASTÍN": "RUEDA", "TORRECILLA DEL VALLE": "RUEDA", "LA SANTA ESPINA": "CASTROMONTE",
               "VILLAMARCIEL": "TORDESILLAS", "VILLAVIEJA DEL CERRO": "TORDESILLAS"}
# localities whose municipality could not be confirmed: kept out of the rows
UNASSIGNED = {"GORDALIZA DE LA LOMA", "SANTIAGO DEL ARROYO"}


def cell(ws):
    t = " ".join(w[4] for w in ws).strip()
    if not t or t.lower() == "no comunicada":
        return None
    m = re.fullmatch(r"(\d{1,2})\s+de\s+([a-záéíóú]+)", t)
    if not m:
        raise SystemExit(f"BAD CELL {t!r}")
    return common.iso(int(m.group(1)), m.group(2))


def cell_text(t):
    if t == "No comunicada":
        return None
    d, mo = re.fullmatch(r"(\d{1,2}) de ([a-záéíóú]+)", t).groups()
    return common.iso(int(d), mo)


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    doc = pymupdf.open(os.path.join(W, "dl", "bop-valladolid", "jcyl.pdf"))
    recs, nocom, started, pending, unassigned = [], [], False, None, []
    for pn in range(1, len(doc)):
        lines = {}
        for w in doc[pn].get_text("words"):
            if w[0] < 100:  # left-margin verification strip
                continue
            lines.setdefault(round(w[3]), []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            t = " ".join(w[4] for w in ws)
            if t.startswith("Ayuntamiento 1ª Fiesta"):
                started = True
                continue
            if not started or ws[0][0] > C1 or t.startswith(("Número 2026/129", "BOLETÍN OFICIAL", "D.L.:", "Verificación")):
                continue
            if t.startswith(("Jueves", "Pág")) or set(t.split()) <= {"DE", "LA", "BOLETÍN", "OFICIAL", "PROVINCIA", "VALLADOLID"}:  # header fragments
                continue
            # a few long names run past x=270: split the printed line on its text instead
            m = re.match(r"^(.*?)\s+((?:\d{1,2} de |No comunicada).*)$", t)
            if not m:  # long name wrapped: the first part sits on its own line above
                if re.search(r"\d", t):
                    raise SystemExit(f"BROKEN LINE p{pn + 1}: {t!r}")
                pending = t
                continue
            name = (pending + " " + m.group(1)) if pending else m.group(1)
            pending = None
            cells = re.findall(r"\d{1,2} de [a-záéíóú]+|No comunicada", m.group(2))
            if len(cells) != 2 or re.sub(r"\d{1,2} de [a-záéíóú]+|No comunicada|\s", "", m.group(2)):
                raise SystemExit(f"BAD CELLS p{pn + 1}: {t!r}")
            hs = [{"date": d, "name": None} for d in map(cell_text, cells) if d]
            if not hs:
                nocom.append(name)
                continue
            note = "The annex gives dates only, without festivity names."
            if len(hs) == 1:
                note += " The other day is printed as 'No comunicada' (not communicated by the council)."
            if name in UNASSIGNED:
                unassigned.append({"name": name, "holidays": hs})
            elif name in LOCALITY_OF:
                recs.append({"muni": LOCALITY_OF[name], "locality": cu.nice(name), "holidays": hs})
            else:
                recs.append({"muni": name, "locality": None, "holidays": hs, "note": note})
    doc.close()
    # a locality whose parent printed 'No comunicada' still needs a head row
    heads = {r["muni"] for r in recs if not r["locality"]}
    for r in [r for r in recs if r["locality"] and r["muni"] not in heads]:
        heads.add(r["muni"])
        recs.append({"muni": r["muni"], "locality": None, "holidays": [],
                     "note": "The municipality's own days are printed as 'No comunicada'."})
    for printed, official in MANUAL.items():
        ine.add_manual("47", printed, next(c for c, n in ine.by_code.items() if c[:2] == "47" and n == official))
    rows = cu.build_rows(ine, "47", recs)
    for r in rows:  # build_rows sets holidays [] -> keep only the explanatory note once
        r["note"] = r["note"].replace("The bulletin gives no municipality-wide days, only days for each locality. "
                                      "The municipality's own days are printed as 'No comunicada'.",
                                      "The municipality's own days are printed as 'No comunicada'; only its localities have days.")
    print("unassigned localities:", unassigned)
    miss = common.coverage(ine, rows, ["47"])
    print("no comunicada:", len(nocom), nocom)
    print("not in bulletin:", len(miss), [n for _, n in miss])
    common.save_parsed(W, SID, META, rows, SPOT,
                       extra={"not_listed": [c for c, _ in miss], "not_communicated": nocom,
                              "unassigned_localities": unassigned})


SPOT = ("2026-11-07: annex read by word coordinates (three columns on one printed line). Re-read against "
        "the PDF text: ADALIA 6 May + 28 Aug; ALDEALBAR 'No comunicada' twice (left out); MEDINA DEL CAMPO "
        "14 Jun + 2 Sep; VALLADOLID 'No comunicada' twice (city keeps its ayuntamiento entry); ARROYO DE LA "
        "ENCOMIENDA 6 May + 14 Jun; BARRUELO DEL VALLE 29 Mar + 2 Jun: all match.")

if __name__ == "__main__":
    main()
