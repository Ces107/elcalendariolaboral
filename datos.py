"""Open data: /datos/ (page) and /datos/festivos-locales-2027.csv (one row per municipality with official 2027 local holidays).

Every row comes from the same catalogue as the municipality pages (muni.catalogue(): official bulletins or council agreements
only, never press). Spanish only. Called from build.main() after pages.write_pages, like analisis.py:

    pages_written += datos.write(sys.modules[__name__], data, fix)      # [(path, lastmod, ["es"])]

The CSV is UTF-8 with BOM (Excel opens the accents), one header row, ';' is not used: standard commas with quotes.
"""
import csv
import io
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PATH = "datos/"
CSV_NAME = "festivos-locales-2027.csv"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/deed.es"

B = None
DATA = None


def _loc_text(localities):
    """'La Xara: 2027-09-03 Fiestas patronales, 2027-09-21 San Mateo | Jesús Pobre: …' from the data's `localities`."""
    out = []
    for l in localities or []:
        hs = ", ".join(f'{h["date"]} {h.get("name") or ""}'.strip() for h in (l.get("holidays") or []))
        out.append(f'{l.get("name", "")}: {hs}'.strip(": "))
    return " | ".join(out)


def _rows(cat, regions):
    import muni
    raw = (muni.load("locales-2027-all.json") or {}).get("municipios", {})
    out = []
    for x in cat["munis"]:
        if not x.get("ok") or not (x.get("hol27") or x.get("note")):
            continue
        wide, part = muni.wide_and_partial(x["hol27"] or [])
        wide = sorted(wide, key=lambda h: h["date"])
        src = x.get("src27") or {}
        extra_p = [f'{h["date"]} {h.get("name") or ""}'.strip() for h in sorted(part, key=lambda h: h["date"])]
        loc_t = _loc_text((raw.get(x["ine"]) or {}).get("localities"))
        extra = " | ".join(t for t in ((("; ".join(extra_p)) if extra_p else ""), loc_t) if t)
        nota = ""
        if extra and len(wide) < 2:
            nota = "El documento oficial no da dos fechas para todo el municipio: hay días solo para parte del municipio (columna anterior)."
        elif extra:
            nota = "Además hay días solo para parte del municipio (columna anterior)."
        elif len(wide) < 2:
            nota = "El documento oficial no da dos fechas para todo el municipio; ver la página del municipio."
        row = {
            "ine": x["ine"], "municipio": x["name"], "provincia": x["prov"]["name"], "comunidad": regions.get(x["region"], x["region"]),
            "estado": {"boletin": "boletín oficial", "ayuntamiento": "acuerdo del ayuntamiento"}.get(x["status"], x["status"]),
        }
        for k in range(3):
            h = wide[k] if k < len(wide) else None
            row[f"fecha_{k + 1}"] = h["date"] if h else ""
            row[f"nombre_{k + 1}"] = (h.get("name") or "") if h else ""
        row.update({"solo_parte_del_municipio": extra, "nota": nota, "fuente": src.get("title", ""), "fuente_url": src.get("url", ""),
                    "pagina": f"{B.SITE}{B.ASSETS}{x['path']}"})
        out.append(row)
    out.sort(key=lambda r: (r["comunidad"], r["provincia"], r["municipio"]))
    return out


FIELDS = ["ine", "municipio", "provincia", "comunidad", "estado", "fecha_1", "nombre_1", "fecha_2", "nombre_2", "fecha_3", "nombre_3",
          "solo_parte_del_municipio", "nota", "fuente", "fuente_url", "pagina"]


def _csv(rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def write(b, data, fix):
    """Write datos/index.html and datos/festivos-locales-2027.csv. Returns [(path, lastmod, ['es'])] for the sitemap."""
    global B, DATA
    B, DATA = b, data
    if B.LANG != "es":
        return []
    import muni
    import pages as P
    from build import E
    cat = muni.catalogue()
    regions = {r["slug"]: r["name"] for r in data["regions"]}
    rows = _rows(cat, regions)
    all27 = muni.load("locales-2027-all.json") or {}
    upd = all27.get("updated") or "2026-11-17"
    total = len(cat["munis"])
    by_reg_ok = Counter(r["comunidad"] for r in rows)
    by_reg_all = Counter(regions.get(x["region"], x["region"]) for x in cat["munis"])
    n_boe = sum(1 for r in rows if r["estado"] == "boletín oficial")
    n_ayto = len(rows) - n_boe

    out = ROOT / PATH.rstrip("/")
    out.mkdir(exist_ok=True)
    (out / CSV_NAME).write_bytes(b"\xef\xbb\xbf" + _csv(rows).encode("utf-8"))

    trs = "".join(f'<tr><th scope="row">{E(c)}</th><td>{by_reg_ok[c]}</td><td>{by_reg_all[c]}</td></tr>'
                  for c in sorted(by_reg_all))
    cols = [("ine", "Código INE de 5 cifras del municipio"), ("municipio, provincia, comunidad", "Nombres en castellano"),
            ("estado", "«boletín oficial» o «acuerdo del ayuntamiento» (pendiente de boletín)"),
            ("fecha_1 … fecha_3, nombre_1 … nombre_3", "Festivos locales de todo el municipio (AAAA-MM-DD) y su nombre, si el documento lo da"),
            ("solo_parte_del_municipio", "Días que el documento limita a una parroquia, pedanía o localidad"),
            ("nota", "Aviso cuando el documento no da dos fechas para todo el municipio o añade días por localidad"),
            ("fuente, fuente_url", "Título y enlace del documento oficial"),
            ("pagina", "La página de este sitio con ese municipio")]
    cols_tr = "".join(f"<tr><th scope=\"row\"><code>{E(a)}</code></th><td>{E(b_)}</td></tr>" for a, b_ in cols)
    title = "Datos abiertos: festivos locales 2027 por municipio (CSV)"
    desc = f"Descarga gratis los festivos locales de 2027 de {len(rows)} municipios, con el boletín oficial de cada uno. Licencia CC BY 4.0."
    lead = (f'<p class="lead">Un archivo CSV con los festivos locales de 2027 de <b>{len(rows)} municipios</b> ({n_boe} con boletín oficial y '
            f'{n_ayto} con el acuerdo del pleno publicado por el ayuntamiento), de los {total} de España. Cada fila enlaza el documento '
            f'oficial de donde sale. Actualizado el {B.dmy(upd)}.</p>')
    dl = (f'<p><a class="btn p" href="{B.ASSETS}{PATH}{CSV_NAME}" download>Descargar el CSV ({len(rows)} filas)</a></p>')
    sections = [
        B.section("descarga", "Descarga", dl +
                  f'<p>UTF-8, una fila por municipio, separado por comas, con cabecera. Se abre directamente en Excel, LibreOffice, '
                  f'Google Sheets o cualquier lenguaje de programación.</p>'),
        B.section("columnas", "Columnas", f'<table class="tbl"><tbody>{cols_tr}</tbody></table>'),
        B.section("cobertura", "Cobertura por comunidad",
                  f'<p>Solo hay fila cuando existe una publicación oficial. Los demás municipios están pendientes de su boletín y '
                  f'no se rellenan con fechas de prensa ni del año anterior.</p>'
                  f'<div class="tw"><table class="tbl"><thead><tr><th>Comunidad</th><th>Con datos de 2027</th><th>Municipios</th></tr></thead>'
                  f'<tbody>{trs}</tbody></table></div>'),
        B.section("licencia", "Licencia y cómo citarlo",
                  f'<p>Los datos están bajo <a href="{LICENSE_URL}" rel="noopener license">Creative Commons Atribución 4.0</a>: puedes '
                  f'copiarlos, modificarlos y usarlos, también con fines comerciales, citando «elcalendariolaboral.es» con un enlace a esta '
                  f'página. Los textos oficiales de los que salen son de dominio público. Consulta la <a href="{B.BASE}sobre/">metodología</a> '
                  f'y los <a href="{B.BASE}analisis/">análisis</a> hechos con estos mismos datos.</p>'
                  f'<p>Si ves una fecha mal, escribe a {E(B.EMAIL)} con el enlace al boletín; lo corregimos en la siguiente actualización.</p>'),
    ]
    crumbs = [("España", ""), ("Datos abiertos", PATH)]
    lds = [P.crumbs_ld(crumbs), P.webpage_ld(title, PATH, upd),
           {"@type": "Dataset", "name": "Festivos locales 2027 por municipio (España)", "description": desc, "url": B.URL + PATH,
            "license": LICENSE_URL, "inLanguage": "es-ES", "dateModified": upd,
            "creator": {"@type": "Organization", "name": B.t("site_name"), "url": B.URL},
            "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                              "contentUrl": f"{B.SITE}{B.ASSETS}{PATH}{CSV_NAME}"}]}]
    head = B.head_html(title, desc, PATH, f"{B.SITE}{B.ASSETS}og/espana.png", P.ld(*lds), langs=["es"], ads=False)
    hero = f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E("Festivos locales 2027 por municipio: datos abiertos")}</h1>{lead}</div>'
    main = f'{hero}<div class="wrap body narrow">{"".join(sections)}</div>'
    page = B.page(head, "pg", "datos", main, DATA, js=False)
    (out / "index.html").write_text(fix(page), "utf-8", newline="\n")
    return [(PATH, upd, ["es"])]
