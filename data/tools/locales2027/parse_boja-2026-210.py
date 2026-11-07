"""Andalucía: BOJA núm. 210 (29-10-2026), Resolución de 23 de octubre de 2026 de la DG de Trabajo,
Seguridad y Salud Laboral, relación de fiestas locales 2027 (annex: one 3-column table per province).

Input:  <W>/dl/boja-2026-210/boja.pdf
  (https://www.juntadeandalucia.es/eboja/2026/210/BOJA26-210-00021-14189-01_00345419.pdf)
Run:    python -I parse_boja-2026-210.py <W>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SID = "boja-2026-210"
META = {
    "title": "Resolución de 23 de octubre de 2026, de la Dirección General de Trabajo, Seguridad y Salud "
             "Laboral, por la que se publica la relación de fiestas locales de los municipios de la Comunidad "
             "Autónoma de Andalucía para el año 2027 (BOJA núm. 210, 29-X-2026)",
    "url": "https://www.juntadeandalucia.es/eboja/2026/210/BOJA26-210-00021-14189-01_00345419.pdf",
    "published": "2026-10-29",
    "region": "andalucia",
}
PROV = {"ALMERIA": "04", "CADIZ": "11", "CORDOBA": "14", "GRANADA": "18", "HUELVA": "21",
        "JAEN": "23", "MALAGA": "29", "SEVILLA": "41"}
# bulletin spellings that differ from the INE name (checked by hand against the INE dictionary)
MANUAL = [("11", "ZAHARA DE LA SIERRA", "11042"), ("18", "DOMINGO PÉREZ", "18915"),
          ("18", "PINAR, EL", "18910"), ("18", "PÍÑAR", "18159"), ("18", "POLOPOS – LA MAMOLA", "18162"),
          ("21", "CORTELAZOR LA REAL", "21026"), ("23", "HORNOS DE SEGURA", "23043"),
          ("41", "ALANÍS DE LA SIERRA", "41002"), ("18", "HUÉTOR SANTILLÁN", "18099")]
DATE = re.compile(r"^\s*(\d{1,2})\s*DE\s*([A-ZÁÉÍÓÚ]+)\s*$", re.I)


def main():
    W = common.workdir_from_argv()
    import pymupdf
    doc = pymupdf.open(os.path.join(W, "dl", SID, "boja.pdf"))
    ine = common.INE(W)
    for cp, nm, code in MANUAL:
        ine.add_manual(cp, nm, code)
    rows, problems = [], []
    cpro = None
    for page in doc:
        # province headers are printed letter-spaced ("A L M E R Í A")
        heads = []
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                txt = "".join(s["text"] for s in ln["spans"])
                key = common.strip_accents(txt.replace(" ", "")).upper()
                if key in PROV and re.search(r"\w \w", txt):
                    heads.append((ln["bbox"][1], PROV[key]))
        events = [(y, "H", c) for y, c in heads]
        for t in page.find_tables().tables:
            events.append((t.bbox[1], "T", t))
        for y, kind, obj in sorted(events, key=lambda e: e[0]):
            if kind == "H":
                cpro = obj
                continue
            for cells in obj.extract():
                cells = [(c or "").replace("\n", " ").strip() for c in cells]
                if not any(cells):
                    continue
                name, dates = cells[0], [c for c in cells[1:] if c]
                hol = []
                for c in dates:
                    m = DATE.match(c)
                    if not m:
                        problems.append((name, c))
                        continue
                    hol.append({"date": common.iso(m.group(1), m.group(2)), "name": None})
                code, how = ine.match(cpro, name)
                r = {"name": name, "cpro": cpro, "ine": code, "match": how, "holidays": hol,
                     "status": "boletin"}
                if len(hol) != 2:
                    r["note"] = f"The BOJA annex gives {len(hol)} date(s) for this municipality."
                rows.append(r)
    seen = {}
    for r in rows:
        if r["ine"] in seen:
            print("DUPLICATE INE:", r["ine"], seen[r["ine"]], r["name"])
        seen[r["ine"]] = r["name"]
    for p in problems:
        print("UNPARSED CELL:", p)
    miss = common.coverage(ine, rows, PROV.values())
    print(f"missing from annex: {len(miss)}")
    for c, n in miss:
        print("  MISSING", c, n)
    spot = ("2026-11-07: table rows (find_tables) re-read against the raw page text, all equal: Íllar 4-III/26-VII "
            "(p.3), Vícar 21-VI/20-IX (p.4), Carcabuey 29-III/8-IX (p.6), Córdoba 8-IX/25-X (p.6), Montillana "
            "3-V/8-X (p.10), Cala 8-IX/10-IX (p.12), Lepe 10-V ('10 DEMAYO' in print)/17-VIII (p.12), Jaén "
            "11-VI/18-X (p.14), Torredelcampo 10-VI/26-VII (p.15), Marbella 11-VI/19-X (p.18). Province of each "
            "table taken from the letter-spaced province heading above it. The annex gives dates only, no "
            "festivity names, and lists the municipalities whose plenary agreement had reached the labour "
            "authority by 23-10-2026 (766 of 785; the 19 missing are listed in 'missing').")
    common.save_parsed(W, SID, META, rows, spot, {"missing": [list(x) for x in miss]})


if __name__ == "__main__":
    main()
