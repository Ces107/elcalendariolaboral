"""Councils' own 2027 agreements found in the 2026-11-17 sweep (status 'ayuntamiento': the regional/provincial
bulletin for their territory is not out yet). One parsed file, one source per row.

Inputs in <W>/dl/councils-2026-11-17/ (downloaded from the URLs below). Each date is re-read from the downloaded
text by a pattern and its printed weekday is checked; the script fails if the text changed.
Run:  python -E -P parse_sweep-2026-11-17.py <W>
"""
import datetime as dt
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

SID = "councils-2026-11-17"
DL = "councils-2026-11-17"
WD = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def pdf_text(path):
    import pymupdf
    return re.sub(r"\s+", " ", " ".join(p.get_text() for p in pymupdf.open(path)))


def html_text(path):
    raw = open(path, "rb").read()
    try:
        t = raw.decode("utf-8")
    except UnicodeDecodeError:  # some council pages are served as windows-1252
        t = raw.decode("cp1252", "replace")
    t = re.sub(r"(?is)<(script|style).*?</\1>", "", t)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def need(text, pattern):
    m = re.search(pattern, text)
    if not m:
        sys.exit(f"pattern not found: {pattern}")
    return m


CA_WD = {"dilluns": "lunes", "dimarts": "martes", "dimecres": "miércoles", "dijous": "jueves", "divendres": "viernes",
         "dissabte": "sábado", "diumenge": "domingo"}


def day(d, month, weekday=None):
    iso = common.iso(int(d), month.lower())
    if weekday:
        w = CA_WD.get(weekday.lower(), weekday.lower())
        real = WD[dt.date.fromisoformat(iso).weekday()]
        assert common.strip_accents(real) == common.strip_accents(w), (iso, weekday, real)
    return iso


# file, cpro, INE name, pattern (named groups d1 m1 w1 n1 d2 m2 w2 n2), source title/url/published, note
COUNCILS = [
    dict(file="zaragoza-pleno30092026.pdf", cpro="50", name="Zaragoza",
         pattern=r"fiestas de carácter local para el año 2027 a observar en este municipio, .{0,160}?de las fechas "
                 r"siguientes: - (?P<d1>\d{1,2}) de (?P<m1>enero), (?P<w1>viernes), festividad de (?P<n1>San Valero)\. - "
                 r"(?P<d2>\d{1,2}) de (?P<m2>marzo), (?P<w2>viernes), (?P<n2>Cincomarzada)\. UNANIMIDAD",
         title="Ayuntamiento de Zaragoza, acta del Pleno ordinario de 30 de septiembre de 2026, expediente 74.111/2026: "
               "propuesta a la Subdirección Provincial de Trabajo del Gobierno de Aragón de las fiestas locales de 2027 "
               "(aprobada por unanimidad)",
         url="https://www.zaragoza.es/cont/paginas/gestionmunicipal/tablon/pleno30092026.pdf",
         published="2026-09-30",
         note="Pleno agreement sent to the Subdirección Provincial de Trabajo; the BOA resolution with the 2027 local "
              "holidays of Aragón's municipalities was not yet published on 2026-11-17 (2026's: BOA 20-11-2025)."),
    dict(file="alcala-news.html", cpro="28", name="Alcalá de Henares",
         pattern=r"sesión ordinaria celebrada el pasado 20 de octubre de 2026\..{0,200}?las dos jornadas festivas locales "
                 r"fijadas para 2027 son: . (?P<w1>Viernes), (?P<d1>\d{1,2}) de (?P<m1>agosto): (?P<n1>Festividad de los "
                 r"Santos Niños), patronos de la ciudad\. . (?P<w2>Sábado), (?P<d2>\d{1,2}) de (?P<m2>octubre): "
                 r"(?P<n2>Conmemoración del bautismo de Miguel de Cervantes)",
         title="Ayuntamiento de Alcalá de Henares, noticia 16-11-2026 'El Pleno del Ayuntamiento de Alcalá de Henares "
               "aprobó los festivos locales para el año 2027' (Pleno ordinario de 20-10-2026, por unanimidad)",
         url="https://www.ayto-alcaladehenares.es/el-pleno-del-ayuntamiento-de-alcala-de-henares-aprobo-los-festivos-"
             "locales-para-el-ano-2027",
         published="2026-11-16",
         note="Pleno agreement (20-10-2026, unanimous); the BOCM resolution with the 2027 local holidays of the "
              "Comunidad de Madrid was not yet published on 2026-11-17 (2026's: BOCM 12-12-2025). 9 October 2027 is a "
              "Saturday."),
    dict(file="rivas-news.html", cpro="28", name="Rivas-Vaciamadrid",
         pattern=r"el Pleno del Ayuntamiento de Rivas ha aprobado los dos festivos locales del próximo año\. En 2027, "
                 r"será fiesta local los días (?P<w1>jueves) (?P<d1>\d{1,2}) y (?P<w2>viernes) (?P<d2>\d{1,2}) de "
                 r"(?P<m2>mayo), coincidiendo con la celebración de las (?P<n2>Fiestas de Rivas)",
         same_month=True,
         title="Ayuntamiento de Rivas-Vaciamadrid, noticia 03-11-2026 'Rivas cerró 2025 con superávit de 1,19 millones "
               "y remanente de tesorería de 5,77 millones' (Pleno extraordinario de 03-11-2026; apartado sobre los "
               "festivos locales de 2027)",
         url="https://www.rivasciudad.es/noticias/hacienda/2026/11/03/rivas-cerro-2025-con-superavit-de-119-millones-y-"
             "remanente-de-tesoreria-de-577-millones/862600287857/",
         published="2026-11-03",
         note="Pleno agreement reported on the council's own site (the sub-heading says 'Festivos locales 2026' but the "
              "text gives the 2027 days); the BOCM resolution was not yet published on 2026-11-17."),
    dict(file="ssreyes-acta-pleno-15102026.pdf", cpro="28", name="San Sebastián de los Reyes",
         pattern=r"Establecer para el año 2027, las dos fiestas locales del Ayuntamiento de San Sebastián de los Reyes que "
                 r"a continuación se relacionan: - El (?P<w1>miércoles) (?P<d1>\d{1,2}) de (?P<m1>enero) de 2027: "
                 r"Festividad de (?P<n1>San Sebastián Mártir)\. - El (?P<w2>sábado) (?P<d2>\d{1,2}) de (?P<m2>agosto) "
                 r"de 2027: Festividad del (?P<n2>Santísimo Cristo de los Remedios)",
         title="Ayuntamiento de San Sebastián de los Reyes, acta del Pleno ordinario de 15 de octubre de 2026 (portal de "
               "transparencia), acuerdo de fiestas locales 2027 (25 votos a favor, ninguno en contra)",
         url="https://transparencia.ssreyes.org/documents/1678104/4964822/Acta+PLE-15_10_2026-11.pdf/"
             "0a95fc68-8290-7e6e-1af5-eb8bb11ac7f8?t=1793263866195",
         published="2026-10-15",
         note="Pleno agreement of 15-10-2026, sent to the Dirección General de Trabajo for the BOCM resolution (not yet "
              "published on 2026-11-17). 28 August 2027 is a Saturday."),
    dict(file="guadalajara-news.html", cpro="19", name="Guadalajara",
         pattern=r"el Pleno aprobó la propuesta relativa a la determinación de las fiestas locales para el año 2027, de "
                 r"modo que los días (?P<d1>\d{1,2}) y (?P<d2>\d{1,2}) de (?P<m2>septiembre) de 2027 como fiestas locales "
                 r"de carácter retribuido y no recuperable en el término municipal de Guadalajara\. La primera de estas "
                 r"fechas coincide con la festividad de la (?P<n1>Virgen de la Antigua)",
         same_month_only=True, n2="Ferias y Fiestas",
         title="Ayuntamiento de Guadalajara, noticia 30-10-2026 'El Pleno municipal se inicia con un minuto de silencio "
               "por las víctimas de Urda y aprueba dos nuevos planes de emergencia' (Pleno ordinario de 30-10-2026)",
         url="https://www.guadalajara.es/el-pleno-municipal-se-inicia-con-un-minuto-de-silencio-por-las-victimas-de-"
             "urda-y-aprueba-dos-nuevos-planes-de-emergencia.html",
         published="2026-10-30",
         note="Pleno agreement; 17 September falls within the Ferias y Fiestas. The BOP Guadalajara list of 2027 was not "
              "yet published on 2026-11-17 (2026's: BOP 24-11-2025)."),
    dict(file="burgos-news.html", cpro="09", name="Burgos",
         pattern=r"La Junta de Gobierno Local ha aprobado formalmente la propuesta de los dos días de carácter festivo "
                 r"local para la ciudad de Burgos de cara al año 2027, seleccionando el (?P<w1>viernes) (?P<d1>\d{1,2}) de "
                 r"(?P<m1>junio) \(coincidiendo con la Festividad del (?P<n1>Curpillos)\) y el (?P<w2>martes) "
                 r"(?P<d2>\d{1,2}) de (?P<m2>junio) \(Festividad de (?P<n2>San Pedro y San Pablo)",
         title="Ayuntamiento de Burgos, noticia 11-11-2026 'Aprobación de los festivos locales de la ciudad de Burgos "
               "para el año 2027' (acuerdo de la Junta de Gobierno Local)",
         url="https://www.aytoburgos.es/-/aprobaci%C3%B3n-de-los-festivos-locales-de-la-ciudad-de-burgos-para-el-a%C3%B1o-2027.",
         published="2026-11-11",
         note="Junta de Gobierno Local agreement. The city's proposal reached the Oficina Territorial de Trabajo after its "
              "30-06-2026 deadline (the council's own diligencia says so), which is why Burgos city is missing from the "
              "BOP Burgos list of 04-08-2026; a later bulletin entry is still pending."),
    dict(file="torrelavega-news.html", cpro="39", name="Torrelavega",
         pattern=r"el Pleno ha aprobado, con el voto en contra de IU-Podemos, las fiestas locales para el año 2027, que "
                 r"serán el (?P<w1>lunes) (?P<d1>\d{1,2}) de (?P<m1>agosto), festividad de (?P<n1>San Roque), y el "
                 r"(?P<w2>miércoles) (?P<d2>\d{1,2}) de (?P<m2>septiembre), festividad de (?P<n2>San Cipriano)",
         skip_wd=("w2",),
         title="Ayuntamiento de Torrelavega, noticia 04-08-2026 'El Pleno insta al Gobierno de Cantabria a mantener las "
               "aulas de 2 años y aprueba el convenio para renovar la cubierta de La Habana Vieja' (Pleno de 04-08-2026)",
         url="https://torrelavega.es/noticia/el-pleno-insta-al-gobierno-de-cantabria-a-mantener-las-aulas-de-2-anos-y-"
             "aprueba-el-convenio-para-renovar-la-cubierta-de-la-habana-vieja/",
         published="2026-08-04",
         note="Pleno agreement. The council note prints 'miércoles 16 de septiembre' (San Cipriano); 16 September 2027 "
              "is a Thursday. The date is kept as printed (San Cipriano is 16 September; 15 September is already the "
              "regional holiday of La Bien Aparecida). The BOC Cantabria list was not yet published on 2026-11-17."),
    dict(file="burjassot-certificado.pdf", cpro="46", name="Burjassot",
         pattern=r"Señalar como festividades locales, con carácter retribuido y no recuperable para el año 2027, las que "
                 r"seguidamente se indica: 1\. Día (?P<d1>\d{1,2}) de (?P<m1>agosto), festividad de (?P<n1>Sant Roc)\. 2\. "
                 r"Día (?P<d2>\d{1,2}) de (?P<m2>septiembre), festividad de la (?P<n2>Virgen de la Cabeza)\.",
         title="Ajuntament de Burjassot, certificado de la Secretaría del acuerdo del Pleno de 31-03-2026 'Festividades "
               "locales año 2027' (expediente 2026/3471B, por unanimidad), portal de transparencia",
         url="http://transparencia.burjassot.org/wp-content/uploads/2026/04/Certificado-acuerdo-plenario-festividades-2027.pdf",
         published="2026-04-01",
         note="Pleno agreement sent to the Servicio Territorial de Trabajo; the Valencia province resolution of 2027 was "
              "not yet published on 2026-11-17 (Alicante's and Castellón's are out in their BOPs)."),
]

# Cataluña: councils' own pages and agreements (the DOGC order is not out yet)
CAT = ("The DOGC Ordre with the 2027 local holidays of Catalonia was not yet published on 2026-11-17 (2026's: DOGC "
       "17-12-2025).")
COUNCILS += [
    dict(file="sabadell-calendari-2027.html", cpro="08", name="Sabadell",
         pattern=r"CALENDARI LABORAL 2027 (?P<n1>Aplec de la Salut): (?P<d1>\d{1,2}) de (?P<m1>maig) (?P<n2>Festa Major): "
                 r"(?P<d2>\d{1,2}) de (?P<m2>setembre)",
         title="Ajuntament de Sabadell, 'Calendari oficial de festes laborals 2027' (proposta aprovada pel Ple de "
               "22-06-2026, exp. ALC/2026/103)",
         url="https://web.sabadell.cat/blog-agenda/114796-agenda-1178671", published=None,
         note="Council page (undated); the Ple of 22-06-2026 approved the proposal of the two local days. " + CAT),
    dict(file="lleida-calendari-laboral.html", cpro="25", name="Lleida",
         pattern=r"Les festes locals pel calendari 2027 són: LLEIDA: (?P<d1>\d{1,2}) de (?P<m1>maig) \((?P<n1>Festa Major - "
                 r"Sant Anastasi)\) i (?P<d2>\d{1,2}) de (?P<m2>setembre) \((?P<n2>Festa Major - Sant Miquel)\)\. RAIMAT: 27 "
                 r"d'abril i 23 de juliol\. SUCS: 14 de maig i 13 d'agost\.",
         localities=[("Raimat", ["2027-04-27", "2027-07-23"]), ("Sucs", ["2027-05-14", "2027-08-13"])],
         title="Ajuntament de Lleida (La Paeria), 'Calendari laboral': festes locals 2027",
         url="https://www.paeria.cat/ca/ciutat/calendaris/calendari-laboral", published=None,
         note="Council page (modified 2026-08-31). Raimat and Sucs have their own days (see localities). " + CAT),
    dict(file="girona-calendari.html", cpro="17", name="Girona",
         pattern=r"Festes locals 2027 \(acord del Ple de 13/07/202\): (?P<w1>Dilluns) (?P<d1>\d{1,2}) de (?P<m1>juliol) "
                 r"(?P<w2>Divendres) (?P<d2>\d{1,2}) d'(?P<m2>octubre) \((?P<n2>Sant Narcís)\)",
         title="Ajuntament de Girona, seu electrònica, 'Calendari de dies inhàbils 2026 i 2027. Calendari laboral i festes "
               "locals' (acord del Ple de 13-07-2026)",
         url="https://seu.girona.cat/portal/girona_ca/ajuntament/calendari/", published="2026-07-13",
         note="Council page; the Ple agreement date is printed '13/07/202'. 26 July has no name on the page. " + CAT),
    dict(file="santcugat-avis.html", cpro="08", name="Sant Cugat del Vallès",
         pattern=r"Segons acord del ple ordinari de 19 de juny de 2026, les dues festes laborals d’àmbit local per a l’any "
                 r"2027 , retribuïdes i no recuperables, .{0,120}?són: Sant Cugat: (?P<w1>dimecres) (?P<d1>\d{1,2}) de "
                 r"(?P<m1>març) \((?P<n1>Sant Medir)\) i (?P<w2>dimarts) (?P<d2>\d{1,2}) de (?P<m2>juny) \((?P<n2>Sant "
                 r"Pere)\) Valldoreix: dimecres 3 de març i dijous 16 de setembre \(Sant Cebrià\)",
         localities=[("Valldoreix (EMD)", ["2027-03-03", "2027-09-16"])],
         title="Ajuntament de Sant Cugat del Vallès, avís 'Festes locals per als anys 2026 i 2027' (acord del Ple "
               "ordinari de 19-06-2026)",
         url="https://santcugat.cat/avis/festes-locals-2026", published="2026-06-19",
         note="Ple agreement of 19-06-2026. The EMD of Valldoreix has 3 March and 16 September (see localities). " + CAT),
    dict(file="cornella-festes-locals.html", cpro="08", name="Cornellà de Llobregat",
         pattern=r"Dies festius a Cornellà de Llobregat \(2027\):.{0,300}?(?P<d1>\d{1,2}) de (?P<m1>maig) \(FESTA LOCAL\), "
                 r"(?P<w1>dilluns)\. (?P<d2>\d{1,2}) de (?P<m2>maig) \(FESTA LOCAL\), (?P<w2>divendres)\.",
         title="Ajuntament de Cornellà de Llobregat, 'Festes locals i fires': dies festius 2027 (decret de festes locals "
               "2027; Ple de 22-07-2026)",
         url="https://www.cornella.cat/ca/viure-a-cornella/la-ciutat/festes-locals-i-fires", published=None,
         note="Council page (modified 2026-09-28) listing both days as 'festa local', without names. " + CAT),
    dict(file="santboi-acta-ple-28052026.pdf", cpro="08", name="Sant Boi de Llobregat",
         pattern=r"que fixi com a festes locals del municipi de Sant Boi de Llobregat, per a l'any 2027, les següents dates: "
                 r"- (?P<d1>\d{1,2}) de (?P<m1>maig) - (?P<d2>\d{1,2}) de (?P<m2>desembre)",
         title="Ajuntament de Sant Boi de Llobregat, acta del Ple ordinari de 28-05-2026 (sessió SPL260006), proposta "
               "de festes locals 2027 al Departament d'Empresa i Treball",
         url="https://media.seu-e.cat/acteca/820090004/2026/7d588788-7862-4bcc-9c9d-ab3a8e4c6e0d/6%20Sessi%f3%20del%20dia%"
             "2028.05.2026%20_SPL260006_.pdf", published="2026-05-28",
         note="Ple agreement of 28-05-2026 (dates without names; the council's calendar page shows the same days). " + CAT),
    dict(file="rubi-festes-locals.html", cpro="08", name="Rubí",
         pattern=r"Festius locals de 2027: (?P<w1>Dilluns) (?P<d1>\d{1,2}) de (?P<m1>juny) \((?P<n1>Festa Major de Sant "
                 r"Pere)\) (?P<w2>Dimarts) (?P<d2>\d{1,2}) de (?P<m2>juny) \((?P<n2>Festa Major de Sant Pere)\)",
         title="Ajuntament de Rubí, 'Festes locals' (dies festius locals aprovats pel Ple; Ple ordinari de 28-05-2026, "
               "exp. 1/2026/CFL)",
         url="https://www.rubi.cat/ca/rubi-ciutat/festes-locals", published="2026-05-28",
         note="Ple agreement of 28-05-2026. " + CAT),
    dict(file="manresa-cronica-ple-18062026.html", cpro="08", name="Manresa",
         pattern=r"s.han aprovat les festes locals de Manresa per al 2027, que seran el (?P<d1>\d{1,2}) de (?P<m1>febrer) .ja "
                 r"que la diada de (?P<n1>La Llum), 21 de febrer, cau en diumenge. i el (?P<w2>dilluns) (?P<d2>\d{1,2}) "
                 r"d.(?P<m2>agost), per la (?P<n2>Festa Major)\. També s.ha aprovat per unanimitat",
         title="Ajuntament de Manresa, 'Crònica del Ple ordinari de l'Ajuntament de Manresa del dia 18 de juny de 2026'",
         url="https://web.manresa.cat/web/noticies/14092-cronica-del-ple-ordinari-de-l-ajuntament-de-manresa-del-dia-18-de-"
             "juny-de-2026", published="2026-06-18",
         note="Ple agreement of 18-06-2026 (unanimous); La Llum (21 February) falls on a Sunday and is moved to Monday "
              "22 February. " + CAT),
    dict(file="vilanova-calendaris.html", cpro="08", name="Vilanova i la Geltrú",
         pattern=r"va acordar en la seva sessió ordinària de l'1 de juny de 2026 establir les dues festes locals de la ciutat "
                 r"per a l'any 2027, que seran: (?P<d1>\d{1,2}) de (?P<m1>febrer) de 2027, (?P<w1>dilluns) de Carnaval "
                 r"(?P<d2>\d{1,2}) d'(?P<m2>agost) de 2027, (?P<w2>dijous), festivitat de la (?P<n2>Mare de Déu de les Neus)",
         n1="Dilluns de Carnaval",
         title="Ajuntament de Vilanova i la Geltrú, 'Calendaris municipals': festes locals 2027 (acord del Ple ordinari "
               "d'1-06-2026)",
         url="https://www.vilanova.cat/calendaris_municipals", published="2026-06-01",
         note="Ple agreement of 01-06-2026. " + CAT),
    dict(file="granollers-acords-ple-21072026.html", cpro="08", name="Granollers",
         pattern=r"El Ple a ?prova com a festes locals de Granollers per a l'any 2027 els dies: (?P<w1>divendres) "
                 r"(?P<d1>\d{1,2}) de (?P<m1>maig) \((?P<n1>l'Ascensió)\) i (?P<w2>divendres) (?P<d2>\d{1,2}) d.(?P<m2>agost) "
                 r"\((?P<n2>Festa Major)\)\. Aprovat per unanimitat",
         title="Ajuntament de Granollers, sala de premsa, 'Resum dels acords del Ple de 21 de juliol de 2026'",
         url="https://www.granollers.cat/noticies/sala-de-premsa/resum-dels-acords-del-ple-de-21-de-juliol-de-2026",
         published="2026-07-22",
         note="Ple agreement of 21-07-2026 (unanimous); the Ascension holiday is taken on Friday 7 May. " + CAT),
    dict(file="prat-horaris-comercials.html", cpro="08", name="El Prat de Llobregat",
         pattern=r"Festivitats locals del Prat 2027 (?P<d1>\d{1,2}) de (?P<m1>maig) \((?P<w1>dilluns) (?P<n1>Segona Pasqua)\) "
                 r"(?P<d2>\d{1,2}) de (?P<m2>setembre) \((?P<w2>dilluns) de (?P<n2>Festa Major)\)",
         title="Ajuntament del Prat de Llobregat, 'Horaris comercials i normativa': festivitats locals 2027",
         url="https://www.elprat.cat/empresa-comerc-i-ocupacio/el-comerc-del-prat/horaris-comercials-i-normativa",
         published=None, note="Council page (undated, no agreement cited). " + CAT),
    dict(file="esplugues-dies-festius.html", cpro="08", name="Esplugues de Llobregat",
         pattern=r"El Ple de maig del 2026, ha aprovat que els festius locals per a l.any 2027 seran: (?P<w1>Dilluns) "
                 r"(?P<d1>\d{1,2}) de (?P<m1>maig) (?P<w2>Dimarts) (?P<d2>\d{1,2}) de (?P<m2>setembre)",
         title="Ajuntament d'Esplugues de Llobregat, 'Dies festius a Esplugues' (acord del Ple de maig de 2026)",
         url="https://www.esplugues.cat/ciutat/dies-festius-festes-laborals-i-locals-a-esplugues/", published=None,
         note="Ple agreement of May 2026 (dates without names). " + CAT),
    dict(file="badia-certificat-ple-25062026.pdf", cpro="08", name="Badia del Vallès",
         pattern=r"QUE ES DECLARIN EN AQUEST MUNICIPI ELS DIES (?P<d1>\d{1,2}) D.(?P<m1>ABRIL) I (?P<d2>\d{1,2}) DE "
                 r"(?P<m2>MAIG), COM A FESTES LOCALS DURANT L.ANY 2027",
         title="Ajuntament de Badia del Vallès, certificat de l'acord del Ple de 25-06-2026 (expedient 2614/2026), "
               "festes locals 2027",
         url="https://www.badiadelvalles.cat/ARXIUS/2026/CalendariLaboral/Certificat_d_acord.pdf", published="2026-06-26",
         note="Ple agreement of 25-06-2026 (unanimous; dates without names). " + CAT),
    dict(file="santadria-calendari.html", cpro="08", name="Sant Adrià de Besòs",
         pattern=r"2027 Divendres 1 de gener .{0,200}?(?P<w1>Dilluns) (?P<d1>\d{1,2}) de (?P<m1>maig) \((?P<n1>Pasqua "
                 r"Granada), festa local\) .{0,40}?(?P<w2>Dimecres) (?P<d2>\d{1,2}) de (?P<m2>setembre) \((?P<n2>Festa "
                 r"Major Sant Adrià), festa local\)",
         title="Ajuntament de Sant Adrià de Besòs, 'Calendari de dies inhàbils i festius a Sant Adrià' (2027)",
         url="https://www.sant-adria.cat/sant-adria-per-temes/oficina-datencio-ciutadana-oac/calendari-de-dies-inhabils-i-"
             "festius-a-sant-adria", published=None,
         note="Council page (undated, no agreement cited). " + CAT),
    dict(file="blanes-ple-25062026.html", cpro="17", name="Blanes",
         pattern=r"El punt catorzè va aprovar establir els dos dies festius locals per a l.any vinent: el dia de "
                 r"l.(?P<n1>Aplec del Vilar), que al 2027 serà el (?P<d1>\d{1,2}) de (?P<m1>març), i la Festivitat de "
                 r"(?P<n2>Santa Anna) del (?P<d2>\d{1,2}) de (?P<m2>juliol), que coincidirà amb un (?P<w2>dilluns)",
         title="Ajuntament de Blanes, notícia 26-06-2026 sobre el Ple municipal de 25-06-2026 (punt 14: festes locals 2027)",
         url="https://www.blanes.cat/docweb/2026-06-26-ple", published="2026-06-26",
         note="Ple agreement of 25-06-2026. " + CAT),
]


def main():
    W = common.workdir_from_argv()
    ine = common.INE(W)
    rows, checks = [], []
    for c in COUNCILS:
        path = os.path.join(W, "dl", DL, c["file"])
        t = pdf_text(path) if path.endswith(".pdf") else html_text(path)
        g = need(t, c["pattern"]).groupdict()
        if c.get("same_month"):  # "jueves 13 y viernes 14 de mayo ... Fiestas de Rivas"
            g["m1"], g["n1"] = g["m2"], g["n2"]
        if c.get("same_month_only"):  # "los días 8 y 17 de septiembre"
            g["m1"], g["n2"] = g["m2"], c["n2"]
        for k in c.get("skip_wd", ()):  # printed weekday is wrong: explained in the note
            g[k] = None
        cap = lambda n: (n[0].upper() + n[1:]) if n else None  # noqa: E731
        hol = [{"date": day(g["d1"], g["m1"], g.get("w1")), "name": cap(g.get("n1") or c.get("n1"))},
               {"date": day(g["d2"], g["m2"], g.get("w2")), "name": cap(g.get("n2") or c.get("n2"))}]
        code, how = ine.match(c["cpro"], c["name"], fuzzy=False)
        assert code, c["name"]
        row = {"name": c["name"], "cpro": c["cpro"], "ine": code, "match": how, "status": "ayuntamiento",
               "source_title": c["title"], "source_url": c["url"], "published": c["published"],
               "holidays": hol, "note": c["note"]}
        if c.get("localities"):  # printed inside the matched text, so already checked by the pattern
            row["localities"] = [{"name": n, "holidays": [{"date": d, "name": None} for d in ds]}
                                 for n, ds in c["localities"]]
        rows.append(row)
        checks.append(f"{c['name']}: {hol[0]['date']} {hol[0]['name']}, {hol[1]['date']} {hol[1]['name']}")
    common.save_parsed(W, SID, {
        "title": "Acuerdos municipales de fiestas locales 2027 publicados por los propios ayuntamientos "
                 "(pendientes del boletín de su territorio)",
        "url": COUNCILS[0]["url"], "published": None, "region": None},  # each row has its own source and date
        rows, "2026-11-17: each agreement read in the council's own document; the pattern quotes the dates and the "
              "printed weekdays, which match 2027. " + "; ".join(checks))


if __name__ == "__main__":
    main()
