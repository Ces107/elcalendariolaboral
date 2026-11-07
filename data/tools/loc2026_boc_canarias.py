"""Canarias 2026 local holidays: Orden de 6 de agosto de 2025, por la que se determinan las fiestas locales propias de
cada municipio de la Comunidad Autónoma de Canarias para el año 2026 (BOC núm. 165, de 21-08-2025, anuncio 3029).

Download (outside the repo): https://www.gobiernodecanarias.org/boc/2025/165/3029.html
Run: python -E -P data/tools/loc2026_boc_canarias.py 3029.html

Only the two municipal days; the insular holiday is not a local holiday and is not recorded here.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
SOURCE = {
    "title": "Orden de 6 de agosto de 2025, por la que se determinan las fiestas locales propias de cada municipio de la "
             "Comunidad Autónoma de Canarias para el año 2026 (BOC núm. 165, de 21-08-2025)",
    "url": "https://www.gobiernodecanarias.org/boc/2025/165/3029.html",
    "published": "2025-08-21",
}


def lines(path):
    t = Path(path).read_text("utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = re.sub(r"<(tr|p|br|h\d|li|div)[^>]*>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    return [re.sub(r"\s+", " ", ln).strip() for ln in t.splitlines() if ln.strip()]


def main(path):
    mt = Matcher()
    ls = lines(path)
    start = next(i for i, ln in enumerate(ls) if ln.startswith("RELACIÓN DE FIESTAS LOCALES"))
    out, unmatched, cur, name = {}, [], None, None

    def flush():
        if name is None:
            return
        ine = ({"SAN BARTOLOMÉ DE LANZAROTE": "35018", "SANTA LUCÍA": "35022", "SANTA MARÍA DE GUÍA": "35023",
                "VALSEQUILLO": "35031"}.get(name)
               or mt.match(name.title(), region="canarias") or mt.match(name, region="canarias"))
        if not ine:
            unmatched.append(f"{name}: {cur}")
            return
        rec = {"holidays": sorted(cur, key=lambda h: h["date"])}
        if len(cur) != 2:
            rec["note"] = f"The order lists {len(cur)} date(s) for this municipality."
        out[ine] = rec

    for ln in ls[start + 1:]:
        if ln.startswith("©"):
            break  # end of the annex
        m = re.match(r"^(\d{1,2}) (?:de )?(\w+):\s*(.*?)\.?$", ln)
        if m and m.group(2).lower() in MES:
            cur.append({"date": f"2026-{MES[m.group(2).lower()]:02d}-{int(m.group(1)):02d}", "name": m.group(3).strip()})
        elif re.match(r"^[A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ .,'-]+\.$", ln):
            flush()
            name, cur = ln.rstrip("."), []
        else:
            unmatched.append(f"unparsed line: {ln}")
    flush()
    write_part("boc-canarias-2026", SOURCE, out, region="canarias", unmatched=unmatched)


if __name__ == "__main__":
    main(sys.argv[1])
