"""Single-municipality official sources found in the 2026-11-07 sweep:

  bocce-6666       Ceuta: BOCCE nº 6.666 (03-11-2026), item 731, Resolución de 28-10-2026 de la
                   Delegación del Gobierno (Pleno de 29-09-2026)      <W>/dl/ceuta/b23314.pdf
  bome-bx-2026-43  Melilla: BOME Extraordinario 43 (30-09-2026), art. 108 (BOME-AX-2026-108),
                   Acuerdo del Consejo de Gobierno de 24-09-2026     <W>/dl/melilla/BOME-AX-2026-108.pdf
  madrid-councils  Aranjuez: council news of 29-10-2026 on the pleno ordinario of October
                   (status 'ayuntamiento', per-row source)           <W>/dl/madrid-councils/aranjuez-news.html

Each date is re-read from the downloaded text by a pattern; the script fails if the text changed.
Run:  python -I parse_sweep-2026-11-07.py <W>
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def pdf_text(path):
    import pymupdf
    return re.sub(r"\s+", " ", " ".join(p.get_text() for p in pymupdf.open(path)))


def html_text(path):
    t = open(path, "rb").read().decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style).*?</\1>", "", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def need(text, pattern):
    m = re.search(pattern, text)
    if not m:
        sys.exit(f"pattern not found: {pattern}")
    return m


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)

    # Ceuta
    t = pdf_text(os.path.join(W, "dl", "ceuta", "b23314.pdf"))
    need(t, r"731\.- ?Resolución de 28 de octubre de 2026, de la Delegación del Gobierno en Ceuta")
    m = need(t, r"-(\d{1,2}) de (marzo): (Fiesta de Culminación de Ramadán Eid ?al-Fitr) -(\d{1,2}) de (septiembre): (Dia de Ceuta)")
    code, how = ine.match("51", "Ceuta")
    common.save_parsed(W, "bocce-6666", {
        "title": "Resolución de 28 de octubre de 2026, de la Delegación del Gobierno en Ceuta, por la que se publica "
                 "la relación de fiestas locales de la Ciudad Autónoma de Ceuta para el año 2027 (BOCCE nº 6.666, "
                 "03-11-2026, núm. 731, pág. 3754)",
        "url": "https://www.ceuta.es/ceuta/component/jdownloads/finish/1983/23314?Itemid=0",
        "published": "2026-11-03", "region": "ceuta"},
        [{"name": "Ceuta", "cpro": "51", "ine": code, "match": how, "status": "boletin",
          "holidays": [{"date": common.iso(m.group(1), m.group(2)), "name": "Eid al-Fitr (Fiesta de Culminación de Ramadán)"},
                       {"date": common.iso(m.group(4), m.group(5)), "name": "Día de Ceuta"}],
          "note": "Local days agreed by the Pleno of the Ciudad Autónoma on 29-09-2026."}],
        "2026-11-07: resolution text read in the BOCCE PDF (p. 3754): '-10 de marzo: Fiesta de Culminación de "
        "Ramadán Eid al-Fitr -2 de septiembre: Dia de Ceuta'. Single row; checked by eye.")

    # Melilla
    t = pdf_text(os.path.join(W, "dl", "melilla", "BOME-AX-2026-108.pdf"))
    m = need(t, r"Las fiestas por las que se efectúa la opción y que tienen la consideración de locales son los días "
                r"(\d{1,2}) de (septiembre) \((Día de Ntra\. Sra\. Virgen de la Victoria)\) y (\d{1,2}) de (septiembre) \((Día de Melilla)\)")
    code, how = ine.match("52", "Melilla")
    common.save_parsed(W, "bome-bx-2026-43", {
        "title": "Acuerdo del Consejo de Gobierno, de fecha 24 de septiembre de 2026, relativo aprobación del Calendario "
                 "Laboral para el año 2027 (BOME Extraordinario nº 43, 30-09-2026, BOME-AX-2026-108)",
        "url": "https://bomemelilla.es/bome/descargar/BOME-AX-2026-108.pdf",
        "published": "2026-09-30", "region": "melilla"},
        [{"name": "Melilla", "cpro": "52", "ine": code, "match": how, "status": "boletin",
          "holidays": [{"date": common.iso(m.group(1), m.group(2)), "name": "Día de Nuestra Señora Virgen de la Victoria"},
                       {"date": common.iso(m.group(4), m.group(5)), "name": "Día de Melilla"}],
          "note": "The Consejo de Gobierno acts for the Pleno; the agreement lists 8 and 17 September as the two local days."}],
        "2026-11-07: full agreement read in the BOME PDF: 'Las fiestas ... que tienen la consideración de locales son "
        "los días 8 de septiembre (Día de Ntra. Sra. Virgen de la Victoria) y 17 de septiembre (Día de Melilla)'.")

    # Comunidad de Madrid: councils' own publications
    t = html_text(os.path.join(W, "dl", "madrid-councils", "aranjuez-news.html"))
    need(t, r"El Pleno Municipal ha aprobado por unanimidad , en sesión ordinaria correspondiente a octubre, "
            r"la declaración de las Fiestas Locales para el año 2027")
    m = need(t, r"el viernes (\d{1,2}) de (mayo) 2027, correspondiente a nuestro Patrón (San Fernando) , y, por otro, "
                r"el lunes (\d{1,2}) de (septiembre) , correspondiente a las (Fiestas del Motín)")
    code, how = ine.match("28", "Aranjuez")
    common.save_parsed(W, "madrid-councils", {
        "title": "Comunidad de Madrid: acuerdos municipales publicados por los ayuntamientos (pendientes del BOCM)",
        "url": "https://www.aranjuez.es/aprobados-los-dias-festivos-locales-2027/",
        "published": "2026-10-29", "region": "madrid"},
        [{"name": "Aranjuez", "cpro": "28", "ine": code, "match": how, "status": "ayuntamiento",
          "source_title": "Ayuntamiento de Aranjuez, noticia 29-10-2026 'Aprobados los días festivos locales 2027' "
                          "(Pleno ordinario de octubre, aprobado por unanimidad)",
          "source_url": "https://www.aranjuez.es/aprobados-los-dias-festivos-locales-2027/",
          "published": "2026-10-29",
          "holidays": [{"date": common.iso(m.group(1), m.group(2)), "name": m.group(3)},
                       {"date": common.iso(m.group(4), m.group(5)), "name": m.group(6)}],
          "note": "Council agreement; to be sent to the Dirección General de Trabajo for the BOCM resolution."}],
        "2026-11-07: council news text read: 'el viernes 28 de mayo 2027 ... San Fernando, y ... el lunes 6 de "
        "septiembre ... Fiestas del Motín'; weekdays match 2027.")


if __name__ == "__main__":
    main()
