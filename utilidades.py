"""Utility pages, called by pages.write_pages for every language; each page exists in the languages of its ONLY list:

    /semana/                ISO 8601 week of today (util.js; the HTML carries the build date as a fallback) and the
                            week tables of 2026 and 2027

Shared parts (head, header, footer, sections, FAQ, JSON-LD) are the ones of build.py and pages.py. util.js holds the
browser code; its pure functions are exported for node (test_utilidades.py runs them).
"""
import datetime as dt
import json

import build as B
from build import E

TODAY = dt.date.today()  # static fallback only: util.js writes the visitor's date
UPDATED = "2026-10-27"
YEARS = (2026, 2027)

# ---------------------------------------------------------------- strings

S = {
    "es": {
        "util": "Utilidades",
        "wk_link": "¿En qué semana estamos?",
        "wk_title": "¿En qué semana estamos? Número de semana de hoy",
        "wk_desc": "El número de semana de hoy según la ISO 8601, con su lunes y su domingo, y el calendario de semanas de 2026 y 2027 con las fechas de cada una.",
        "wk_h1": "¿En qué semana estamos?", "wk_crumb": "Número de semana",
        "wk_intro": "Semanas de lunes a domingo, numeradas según la ISO 8601, la norma que se usa en España.",
        "week": "Semana", "weeks_of": "Semanas de {y}", "col_week": "Semana", "col_mon_sun": "Lunes – domingo",
        "n_weeks": "{n} semanas",
        "left": {"one": "queda {n} día de {y}", "other": "quedan {n} días de {y}"},
        "wk_faq": [
            ("¿Cómo se numeran las semanas del año?",
             "Según la norma ISO 8601, la que se usa en España y en Europa: cada semana va de lunes a domingo y la semana 1 es la que "
             "contiene el primer jueves del año, es decir, la del 4 de enero."),
            ("¿Cuántas semanas tiene {y1}? ¿Y {y2}?",
             "{y1} tiene {n1} semanas y {y2} tiene {n2}. La semana 1 de {y2} empieza el {w1}."),
            ("¿En qué semana cae el 1 de enero de {y2}?",
             "En la semana {jw} de {jy}, que va del {jmon} al {jsun}."),
            ("¿Cómo saco el número de semana en Excel?",
             "Con =ISO.NUM.DE.SEMANA(A1) (en inglés, =ISOWEEKNUM(A1)). NUM.DE.SEMANA, sin «ISO», empieza la semana en domingo y "
             "puede dar otro número."),
        ],
    },
}
S["es"].update({
    "dh_link": "Calculadora de días hábiles",
    "dh_title": "Calculadora de días hábiles y laborables entre fechas",
    "dh_desc": "Calcula los días hábiles o laborables entre dos fechas, o qué día vence un plazo de días hábiles, con los festivos de tu comunidad y tu municipio.",
    "dh_h1": "Calculadora de días hábiles", "dh_crumb": "Días hábiles",
    "dh_intro": "Cuenta los días hábiles entre dos fechas o calcula cuándo vence un plazo, con los festivos de tu comunidad y tu municipio.",
    "nat_only": "Solo festivos nacionales", "all_region": "Toda la comunidad", "isla": "isla", "zona": "zona",
    "workweek": "Días hábiles", "mon_fri": "Lunes a viernes", "mon_sat": "Lunes a sábado",
    "mode_a": "Entre dos fechas", "mode_b": "Sumar días hábiles",
    "from": "Desde", "to": "Hasta", "start": "Fecha inicial", "n_work": "Días hábiles",
    "res_a": {"one": "día hábil", "other": "días hábiles"},
    "nat_days": {"one": "{n} día natural", "other": "{n} días naturales"},
    "n_hol_in": {"one": "{n} festivo", "other": "{n} festivos"},
    "after": {"one": "{n} día hábil después del {d}", "other": "{n} días hábiles después del {d}"},
    "no_loc": "sin festivos locales de 2026", "out": "Fuera de 2026-2027",
    "h_hols_in": "Festivos en esas fechas", "none_in": "Ningún festivo entre esas fechas.",
    "caveat": "Orientativo. Para plazos legales, consulta el calendario oficial de días inhábiles.",
    "dh_faq": [
        ("¿Qué días son inhábiles en un plazo administrativo?",
         "Según la Ley 39/2015 (artículo 30), los sábados, los domingos y los festivos nacionales, autonómicos y locales. Si un día "
         "es hábil donde vives e inhábil en la sede del organismo, o al revés, se considera inhábil."),
        ("¿Y los días laborables?",
         "Normalmente, de lunes a viernes menos los festivos. Si trabajas los sábados, elige «Lunes a sábado»."),
        ("¿Desde qué día se cuenta un plazo?",
         "Desde el día siguiente a la notificación o la publicación. Por eso, al sumar días hábiles, la cuenta empieza el día "
         "siguiente a la fecha inicial. Si el último día es inhábil, el plazo pasa al siguiente día hábil."),
        ("Entre dos fechas, ¿cuentan el primer y el último día?",
         "Sí: los dos cuentan si son hábiles."),
        ("¿Sirve para plazos judiciales?",
         "No del todo: en los judiciales también son inhábiles todo agosto y del 24 de diciembre al 6 de enero (artículo 183 de la "
         "Ley Orgánica del Poder Judicial), salvo actuaciones urgentes. Esta calculadora no los descuenta."),
    ],
})
S["es"].update({
    "dl_link": "Días laborables 2027",
    "dl_title": "Días laborables 2027 por comunidad y mes (y horas)",
    "dl_desc": "Días laborables de 2027 en cada comunidad autónoma, mes a mes, con el total del año y las horas de trabajo con jornada de 8 horas. Según el BOE.",
    "dl_h1": "Días laborables 2027", "dl_crumb": "Días laborables 2027",
    "dl_intro": "De lunes a viernes, menos los festivos nacionales y autonómicos del BOE. Sin los 2 locales de cada municipio.",
    "dl_h2": "Días laborables por comunidad", "col_total": "Total", "col_hours": "Horas (8 h)", "no_island": "sin fiesta insular",
    "dl_faq": [
        ("¿Cuántos días laborables tiene 2027?",
         "2027 tiene {wd} días de lunes a viernes. Quitando los festivos nacionales y autonómicos que caen entre semana, quedan "
         "entre {lo} y {hi}, según la comunidad, sin contar los 2 festivos locales."),
        ("¿Cuántas horas laborables tiene 2027?",
         "Con jornadas de 8 horas, entre {hlo} y {hhi} horas. Si restas 22 días laborables de vacaciones, quedan entre {vlo} y {vhi}."),
        ("¿Se cuentan los festivos locales?",
         'No, porque cambian en cada municipio. Resta los 2 de tu ciudad si caen entre semana: están en '
         '<a href="{loc}">festivos locales 2027</a>.'),
        ("¿Qué meses de 2027 tienen más días laborables?",
         "{mmax}: {nmax} en la mayoría de comunidades. Con menos días, {mmin}: {nmin}."),
    ],
})
S["es"].update({
    "ch_link": "Cambio de hora 2027",
    "ch_title": "Cambio de hora 2027: cuándo cambia la hora en España",
    "ch_desc": "Cuándo cambia la hora: el próximo cambio, si se adelanta o se atrasa el reloj, Canarias y las fechas de 2026, 2027 y 2028.",
    "ch_h1": "Cambio de hora 2027", "ch_crumb": "Cambio de hora",
    "ch_intro": "Último domingo de marzo y último domingo de octubre, como en toda la Unión Europea.",
    "next_change": "Próximo cambio", "last_change": "Último cambio",
    "su": "a las 2:00 serán las 3:00 (en Canarias, a la 1:00 serán las 2:00)",
    "wi": "a las 3:00 serán las 2:00 (en Canarias, a las 2:00 será la 1:00)",
    "su_s": "2:00 → 3:00", "wi_s": "3:00 → 2:00",
    "ch_h2": "Cambios de hora {a}-{b}", "col_year": "Año", "col_su": "Horario de verano", "col_wi": "Horario de invierno",
    "ch_src": "Real Decreto 236/2002",
    "ch_faq": [
        ("¿Cuándo cambia la hora en 2027?",
         "El {su27} (a las 2:00 serán las 3:00) y el {wi27} (a las 3:00 serán las 2:00). En Canarias, una hora antes en su reloj."),
        ("¿Se adelanta o se atrasa el reloj?",
         "En marzo se adelanta una hora, dormimos una hora menos y empieza el horario de verano. En octubre se atrasa una hora, "
         "dormimos una más y vuelve el horario de invierno."),
        ("¿Por qué cambia la hora en esas fechas?",
         "La Directiva 2000/84/CE fija el cambio el último domingo de marzo y el último de octubre, a la 1:00 UTC, en toda la Unión "
         'Europea. En España lo aplica el <a href="https://www.boe.es/eli/es/rd/2002/03/01/236" rel="noopener">Real Decreto 236/2002</a>.'),
        ("¿Se va a eliminar el cambio de hora?",
         "La Comisión Europea propuso suprimirlo en 2018 y España volvió a pedirlo en 2025, pero no se ha aprobado. Mientras no cambie "
         "la directiva, la hora cambia dos veces al año."),
    ],
})
BOE_RD = '<a href="https://www.boe.es/eli/es/rd/2002/03/01/236" rel="noopener">{}</a>'
S["ca"] = {
    "util": "Utilitats",
    "wk_link": "En quina setmana som?",
    "wk_title": "En quina setmana som? Número de setmana d'avui",
    "wk_desc": "El número de setmana d'avui segons la ISO 8601, amb el seu dilluns i el seu diumenge, i les setmanes del 2026 i el 2027 amb les dates de cadascuna.",
    "wk_h1": "En quina setmana som?", "wk_crumb": "Número de setmana",
    "wk_intro": "Setmanes de dilluns a diumenge, numerades segons la ISO 8601, la norma que s'utilitza a Espanya.",
    "week": "Setmana", "weeks_of": "Setmanes del {y}", "col_week": "Setmana", "col_mon_sun": "Dilluns – diumenge",
    "n_weeks": "{n} setmanes",
    "left": {"one": "queda {n} dia del {y}", "other": "queden {n} dies del {y}"},
    "wk_faq": [
        ("Com es numeren les setmanes de l'any?",
         "Segons la norma ISO 8601, la que s'utilitza a Espanya i a Europa: cada setmana va de dilluns a diumenge i la setmana 1 és la "
         "que conté el primer dijous de l'any, és a dir, la del 4 de gener."),
        ("Quantes setmanes té el {y1}? I el {y2}?",
         "El {y1} té {n1} setmanes i el {y2} en té {n2}. La setmana 1 del {y2} comença el {w1}."),
        ("En quina setmana cau l'1 de gener del {y2}?",
         "En la setmana {jw} del {jy}, que va del {jmon} al {jsun}."),
        ("Com obtinc el número de setmana a l'Excel?",
         "Amb =ISOWEEKNUM(A1) (a l'Excel en castellà, =ISO.NUM.DE.SEMANA(A1)). WEEKNUM, sense «ISO», comença la setmana en diumenge "
         "i pot donar un altre número."),
    ],
    "dh_link": "Calculadora de dies hàbils",
    "dh_title": "Calculadora de dies hàbils i feiners entre dates",
    "dh_desc": "Calcula els dies hàbils o feiners entre dues dates, o quin dia venç un termini de dies hàbils, amb els festius de la teva comunitat i el teu municipi.",
    "dh_h1": "Calculadora de dies hàbils", "dh_crumb": "Dies hàbils",
    "dh_intro": "Compta els dies hàbils entre dues dates o calcula quan venç un termini, amb els festius de la teva comunitat i el teu municipi.",
    "nat_only": "Només festius estatals", "all_region": "Tota la comunitat", "isla": "illa", "zona": "zona",
    "workweek": "Dies hàbils", "mon_fri": "De dilluns a divendres", "mon_sat": "De dilluns a dissabte",
    "mode_a": "Entre dues dates", "mode_b": "Sumar dies hàbils",
    "from": "Des de", "to": "Fins a", "start": "Data inicial", "n_work": "Dies hàbils",
    "res_a": {"one": "dia hàbil", "other": "dies hàbils"},
    "nat_days": {"one": "{n} dia natural", "other": "{n} dies naturals"},
    "n_hol_in": {"one": "{n} festiu", "other": "{n} festius"},
    "after": {"one": "{n} dia hàbil després del {d}", "other": "{n} dies hàbils després del {d}"},
    "no_loc": "sense festius locals del 2026", "out": "Fora del 2026-2027",
    "h_hols_in": "Festius en aquestes dates", "none_in": "Cap festiu entre aquestes dates.",
    "caveat": "Orientatiu. Per a terminis legals, consulta el calendari oficial de dies inhàbils.",
    "dh_faq": [
        ("Quins dies són inhàbils en un termini administratiu?",
         "Segons la Llei 39/2015 (article 30), els dissabtes, els diumenges i els festius estatals, autonòmics i locals. Si un dia és "
         "hàbil on vius i inhàbil a la seu de l'organisme, o al revés, es considera inhàbil."),
        ("I els dies feiners?",
         "Normalment, de dilluns a divendres menys els festius. Si treballes els dissabtes, tria «De dilluns a dissabte»."),
        ("Des de quin dia es compta un termini?",
         "Des de l'endemà de la notificació o la publicació. Per això, en sumar dies hàbils, el compte comença l'endemà de la data "
         "inicial. Si l'últim dia és inhàbil, el termini passa al dia hàbil següent."),
        ("Entre dues dates, compten el primer i l'últim dia?",
         "Sí: tots dos compten si són hàbils."),
        ("Serveix per a terminis judicials?",
         "No del tot: en els judicials també són inhàbils tot l'agost i del 24 de desembre al 6 de gener (article 183 de la Llei "
         "orgànica del poder judicial), excepte les actuacions urgents. Aquesta calculadora no els descompta."),
    ],
    "dl_link": "Dies feiners 2027",
    "dl_title": "Dies feiners 2027 per comunitat i mes (i hores)",
    "dl_desc": "Dies feiners del 2027 a cada comunitat autònoma, mes a mes, amb el total de l'any i les hores de feina amb jornada de 8 hores. Segons el BOE.",
    "dl_h1": "Dies feiners 2027", "dl_crumb": "Dies feiners 2027",
    "dl_intro": "De dilluns a divendres, menys els festius estatals i autonòmics del BOE. Sense els 2 locals de cada municipi.",
    "dl_h2": "Dies feiners per comunitat", "col_total": "Total", "col_hours": "Hores (8 h)", "no_island": "sense festa insular",
    "dl_faq": [
        ("Quants dies feiners té el 2027?",
         "El 2027 té {wd} dies de dilluns a divendres. Si es treuen els festius estatals i autonòmics que cauen entre setmana, en "
         "queden entre {lo} i {hi}, segons la comunitat, sense comptar els 2 festius locals."),
        ("Quantes hores de feina té el 2027?",
         "Amb jornades de 8 hores, entre {hlo} i {hhi} hores. Si restes 22 dies feiners de vacances, en queden entre {vlo} i {vhi}."),
        ("Es compten els festius locals?",
         'No, perquè canvien a cada municipi. Resta els 2 de la teva ciutat si cauen entre setmana: són a '
         '<a href="{loc}">festius locals 2027</a>.'),
        ("Quins mesos del 2027 tenen més dies feiners?",
         "{mmax}: {nmax} a la majoria de comunitats. Amb menys dies, {mmin}: {nmin}."),
    ],
    "ch_link": "Canvi d'hora 2027",
    "ch_title": "Canvi d'hora 2027: quan canvia l'hora a Espanya",
    "ch_desc": "Quan canvia l'hora: el proper canvi, si s'avança o s'endarrereix el rellotge, les Canàries i les dates del 2026, el 2027 i el 2028.",
    "ch_h1": "Canvi d'hora 2027", "ch_crumb": "Canvi d'hora",
    "ch_intro": "Últim diumenge de març i últim diumenge d'octubre, com a tota la Unió Europea.",
    "next_change": "Proper canvi", "last_change": "Últim canvi",
    "su": "a les 2.00 seran les 3.00 (a les Canàries, a la 1.00 seran les 2.00)",
    "wi": "a les 3.00 seran les 2.00 (a les Canàries, a les 2.00 serà la 1.00)",
    "su_s": "2.00 → 3.00", "wi_s": "3.00 → 2.00",
    "ch_h2": "Canvis d'hora {a}-{b}", "col_year": "Any", "col_su": "Horari d'estiu", "col_wi": "Horari d'hivern",
    "ch_src": "Reial decret 236/2002",
    "ch_faq": [
        ("Quan canvia l'hora el 2027?",
         "El {su27} (a les 2.00 seran les 3.00) i el {wi27} (a les 3.00 seran les 2.00). A les Canàries, una hora abans en el seu rellotge."),
        ("S'avança o s'endarrereix el rellotge?",
         "Al març s'avança una hora, dormim una hora menys i comença l'horari d'estiu. A l'octubre s'endarrereix una hora, dormim una "
         "hora més i torna l'horari d'hivern."),
        ("Per què canvia l'hora en aquestes dates?",
         "La Directiva 2000/84/CE fixa el canvi l'últim diumenge de març i l'últim d'octubre, a la 1.00 UTC, a tota la Unió Europea. "
         "A Espanya l'aplica el " + BOE_RD.format("Reial decret 236/2002") + "."),
        ("Se suprimirà el canvi d'hora?",
         "La Comissió Europea va proposar suprimir-lo el 2018 i Espanya ho va tornar a demanar el 2025, però no s'ha aprovat. Mentre "
         "no canviï la directiva, l'hora canvia dues vegades l'any."),
    ],
}
S["gl"] = {
    "util": "Utilidades",
    "wk_link": "En que semana estamos?",
    "wk_title": "En que semana estamos? Número de semana de hoxe",
    "wk_desc": "O número de semana de hoxe segundo a ISO 8601, co seu luns e o seu domingo, e as semanas de 2026 e 2027 coas datas de cada unha.",
    "wk_h1": "En que semana estamos?", "wk_crumb": "Número de semana",
    "wk_intro": "Semanas de luns a domingo, numeradas segundo a ISO 8601, a norma que se usa en España.",
    "week": "Semana", "weeks_of": "Semanas de {y}", "col_week": "Semana", "col_mon_sun": "Luns – domingo",
    "n_weeks": "{n} semanas",
    "left": {"one": "queda {n} día de {y}", "other": "quedan {n} días de {y}"},
    "wk_faq": [
        ("Como se numeran as semanas do ano?",
         "Segundo a norma ISO 8601, a que se usa en España e en Europa: cada semana vai de luns a domingo e a semana 1 é a que contén "
         "o primeiro xoves do ano, é dicir, a do 4 de xaneiro."),
        ("Cantas semanas ten {y1}? E {y2}?",
         "{y1} ten {n1} semanas e {y2} ten {n2}. A semana 1 de {y2} comeza o {w1}."),
        ("En que semana cae o 1 de xaneiro de {y2}?",
         "Na semana {jw} de {jy}, que vai do {jmon} ao {jsun}."),
        ("Como saco o número de semana en Excel?",
         "Con =ISOWEEKNUM(A1) (no Excel en castelán, =ISO.NUM.DE.SEMANA(A1)). WEEKNUM, sen «ISO», comeza a semana en domingo e pode "
         "dar outro número."),
    ],
    "dh_link": "Calculadora de días hábiles",
    "dh_title": "Calculadora de días hábiles e laborables entre datas",
    "dh_desc": "Calcula os días hábiles ou laborables entre dúas datas, ou que día vence un prazo de días hábiles, cos festivos da túa comunidade e o teu concello.",
    "dh_h1": "Calculadora de días hábiles", "dh_crumb": "Días hábiles",
    "dh_intro": "Conta os días hábiles entre dúas datas ou calcula cando vence un prazo, cos festivos da túa comunidade e o teu concello.",
    "nat_only": "Só festivos estatais", "all_region": "Toda a comunidade", "isla": "illa", "zona": "zona",
    "workweek": "Días hábiles", "mon_fri": "Luns a venres", "mon_sat": "Luns a sábado",
    "mode_a": "Entre dúas datas", "mode_b": "Sumar días hábiles",
    "from": "Desde", "to": "Ata", "start": "Data inicial", "n_work": "Días hábiles",
    "res_a": {"one": "día hábil", "other": "días hábiles"},
    "nat_days": {"one": "{n} día natural", "other": "{n} días naturais"},
    "n_hol_in": {"one": "{n} festivo", "other": "{n} festivos"},
    "after": {"one": "{n} día hábil despois do {d}", "other": "{n} días hábiles despois do {d}"},
    "no_loc": "sen festivos locais de 2026", "out": "Fóra de 2026-2027",
    "h_hols_in": "Festivos nesas datas", "none_in": "Ningún festivo entre esas datas.",
    "caveat": "Orientativo. Para prazos legais, consulta o calendario oficial de días inhábiles.",
    "dh_faq": [
        ("Que días son inhábiles nun prazo administrativo?",
         "Segundo a Lei 39/2015 (artigo 30), os sábados, os domingos e os festivos estatais, autonómicos e locais. Se un día é hábil "
         "onde vives e inhábil na sede do organismo, ou ao revés, considérase inhábil."),
        ("E os días laborables?",
         "Normalmente, de luns a venres menos os festivos. Se traballas os sábados, escolle «Luns a sábado»."),
        ("Desde que día se conta un prazo?",
         "Desde o día seguinte á notificación ou á publicación. Por iso, ao sumar días hábiles, a conta comeza o día seguinte á data "
         "inicial. Se o último día é inhábil, o prazo pasa ao seguinte día hábil."),
        ("Entre dúas datas, contan o primeiro e o último día?",
         "Si: os dous contan se son hábiles."),
        ("Serve para prazos xudiciais?",
         "Non de todo: nos xudiciais tamén son inhábiles todo agosto e do 24 de decembro ao 6 de xaneiro (artigo 183 da Lei orgánica "
         "do poder xudicial), agás as actuacións urxentes. Esta calculadora non os desconta."),
    ],
    "dl_link": "Días laborables 2027",
    "dl_title": "Días laborables 2027 por comunidade e mes (e horas)",
    "dl_desc": "Días laborables de 2027 en cada comunidade autónoma, mes a mes, co total do ano e as horas de traballo con xornada de 8 horas. Segundo o BOE.",
    "dl_h1": "Días laborables 2027", "dl_crumb": "Días laborables 2027",
    "dl_intro": "De luns a venres, menos os festivos estatais e autonómicos do BOE. Sen os 2 locais de cada concello.",
    "dl_h2": "Días laborables por comunidade", "col_total": "Total", "col_hours": "Horas (8 h)", "no_island": "sen festa insular",
    "dl_faq": [
        ("Cantos días laborables ten 2027?",
         "2027 ten {wd} días de luns a venres. Quitando os festivos estatais e autonómicos que caen entre semana, quedan entre {lo} e "
         "{hi}, segundo a comunidade, sen contar os 2 festivos locais."),
        ("Cantas horas laborables ten 2027?",
         "Con xornadas de 8 horas, entre {hlo} e {hhi} horas. Se restas 22 días laborables de vacacións, quedan entre {vlo} e {vhi}."),
        ("Cóntanse os festivos locais?",
         'Non, porque cambian en cada concello. Resta os 2 da túa cidade se caen entre semana: están en '
         '<a href="{loc}">festivos locais 2027</a>.'),
        ("Que meses de 2027 teñen máis días laborables?",
         "{mmax}: {nmax} na maioría das comunidades. Con menos días, {mmin}: {nmin}."),
    ],
    "ch_link": "Cambio de hora 2027",
    "ch_title": "Cambio de hora 2027: cando cambia a hora en España",
    "ch_desc": "Cando cambia a hora: o próximo cambio, se se adianta ou se atrasa o reloxo, Canarias e as datas de 2026, 2027 e 2028.",
    "ch_h1": "Cambio de hora 2027", "ch_crumb": "Cambio de hora",
    "ch_intro": "Último domingo de marzo e último domingo de outubro, como en toda a Unión Europea.",
    "next_change": "Próximo cambio", "last_change": "Último cambio",
    "su": "ás 2:00 serán as 3:00 (en Canarias, á 1:00 serán as 2:00)",
    "wi": "ás 3:00 serán as 2:00 (en Canarias, ás 2:00 será a 1:00)",
    "su_s": "2:00 → 3:00", "wi_s": "3:00 → 2:00",
    "ch_h2": "Cambios de hora {a}-{b}", "col_year": "Ano", "col_su": "Horario de verán", "col_wi": "Horario de inverno",
    "ch_src": "Real decreto 236/2002",
    "ch_faq": [
        ("Cando cambia a hora en 2027?",
         "O {su27} (ás 2:00 serán as 3:00) e o {wi27} (ás 3:00 serán as 2:00). En Canarias, unha hora antes no seu reloxo."),
        ("Adiántase ou atrásase o reloxo?",
         "En marzo adiántase unha hora, durmimos unha hora menos e empeza o horario de verán. En outubro atrásase unha hora, durmimos "
         "unha máis e volve o horario de inverno."),
        ("Por que cambia a hora nesas datas?",
         "A Directiva 2000/84/CE fixa o cambio o último domingo de marzo e o último de outubro, á 1:00 UTC, en toda a Unión Europea. "
         "En España aplícao o " + BOE_RD.format("Real decreto 236/2002") + "."),
        ("Vaise eliminar o cambio de hora?",
         "A Comisión Europea propuxo suprimilo en 2018 e España volveuno pedir en 2025, pero non se aprobou. Mentres non cambie a "
         "directiva, a hora cambia dúas veces ao ano."),
    ],
}
S["eu"] = {
    "util": "Tresnak",
    "wk_link": "Zenbagarren astean gaude?",
    "wk_title": "Zenbagarren astean gaude? Gaurko aste zenbakia",
    "wk_desc": "Gaurko aste zenbakia ISO 8601 arauaren arabera, astelehenetik igandera, eta 2026ko eta 2027ko asteak, aste bakoitzaren datekin.",
    "wk_h1": "Zenbagarren astean gaude?", "wk_crumb": "Aste zenbakia",
    "wk_intro": "Astelehenetik igandera doazen asteak, ISO 8601 arauaren arabera zenbakituta. Espainian arau hori erabiltzen da.",
    "week": "Astea", "weeks_of": "{y}ko asteak", "col_week": "Astea", "col_mon_sun": "Astelehena – igandea",
    "n_weeks": "{n} aste",
    "left": {"one": "{y}an egun {n} geratzen da", "other": "{y}an {n} egun geratzen dira"},
    "wk_faq": [
        ("Nola zenbakitzen dira urteko asteak?",
         "ISO 8601 arauaren arabera, Espainian eta Europan erabiltzen denaren arabera: aste bakoitza astelehenetik igandera doa, eta "
         "1. astea urteko lehen osteguna duena da, hau da, urtarrilaren 4a duena."),
        ("Zenbat aste ditu {y1}k? Eta {y2}k?",
         "{y1}k {n1} aste ditu, eta {y2}k {n2}. {y2}ko 1. astearen lehen eguna: {w1}."),
        ("Zein astetan dago {y2}ko urtarrilaren 1a?",
         "{jy}ko {jw}. astean. Aste horren lehen eguna: {jmon}. Azkena: {jsun}."),
        ("Nola lortu aste zenbakia Excelen?",
         "=ISOWEEKNUM(A1) formularekin (Excel gaztelaniaz badago, =ISO.NUM.DE.SEMANA(A1)). WEEKNUM funtzioak, «ISO» gabe, igandean "
         "hasten du astea eta beste zenbaki bat eman dezake."),
    ],
    "dh_link": "Egun baliodunen kalkulagailua",
    "dh_title": "Egun baliodunen eta lanegunen kalkulagailua",
    "dh_desc": "Kalkulatu bi dataren arteko egun baliodunak edo lanegunak, edo epe bat zein egunetan amaitzen den, zure erkidegoko eta udalerriko jaiegunekin.",
    "dh_h1": "Egun baliodunen kalkulagailua", "dh_crumb": "Egun baliodunak",
    "dh_intro": "Zenbatu bi dataren arteko egun baliodunak edo kalkulatu epe bat noiz amaitzen den, zure erkidegoko eta udalerriko jaiegunekin.",
    "nat_only": "Estatuko jaiegunak soilik", "all_region": "Erkidego osoa", "isla": "uhartea", "zona": "eremua",
    "workweek": "Egun baliodunak", "mon_fri": "Astelehenetik ostiralera", "mon_sat": "Astelehenetik larunbatera",
    "mode_a": "Bi dataren artean", "mode_b": "Egun baliodunak gehitu",
    "from": "Noiztik", "to": "Noiz arte", "start": "Hasiera data", "n_work": "Egun baliodunak",
    "res_a": {"one": "egun baliodun", "other": "egun baliodun"},
    "nat_days": {"one": "egun natural {n}", "other": "{n} egun natural"},
    "n_hol_in": {"one": "jaiegun {n}", "other": "{n} jaiegun"},
    "after": {"one": "egun baliodun {n} · hasiera: {d}", "other": "{n} egun baliodun · hasiera: {d}"},
    "no_loc": "2026ko tokiko jaiegunak gabe", "out": "2026-2027 tartetik kanpo",
    "h_hols_in": "Data horietako jaiegunak", "none_in": "Ez dago jaiegunik data horien artean.",
    "caveat": "Orientagarria da. Lege-epeetarako, begiratu egun baliogabeen egutegi ofiziala.",
    "dh_faq": [
        ("Zein egun dira baliogabeak administrazio-epe batean?",
         "39/2015 Legearen arabera (30. artikulua), larunbatak, igandeak eta estatuko, erkidegoko eta tokiko jaiegunak. Egun bat "
         "baliodun bada bizi zaren lekuan eta baliogabe erakundearen egoitzan, edo alderantziz, baliogabetzat hartzen da."),
        ("Eta lanegunak?",
         "Normalean, astelehenetik ostiralera, jaiegunak kenduta. Larunbatetan lan egiten baduzu, aukeratu «Astelehenetik larunbatera»."),
        ("Noiztik zenbatzen da epe bat?",
         "Jakinarazpenaren edo argitalpenaren hurrengo egunetik. Horregatik, egun baliodunak gehitzean, kontaketa hasiera dataren "
         "hurrengo egunean hasten da. Azken eguna baliogabea bada, epea hurrengo egun baliodunera pasatzen da."),
        ("Bi dataren artean, lehen eguna eta azkena zenbatzen dira?",
         "Bai: biak zenbatzen dira baliodunak badira."),
        ("Epe judizialetarako balio du?",
         "Ez guztiz: epe judizialetan abuztu osoa eta abenduaren 24tik urtarrilaren 6ra bitarteko egunak ere baliogabeak dira "
         "(Botere Judizialaren Lege Organikoaren 183. artikulua), presazko jarduketak izan ezik. Kalkulagailu honek ez ditu kentzen."),
    ],
    "dl_link": "2027ko lanegunak",
    "dl_title": "2027ko lanegunak erkidegoka eta hilabeteka (eta orduak)",
    "dl_desc": "2027ko lanegunak autonomia-erkidego bakoitzean, hilabetez hilabete, urteko guztizkoarekin eta lanorduekin, 8 orduko lanaldiarekin. BOEren arabera.",
    "dl_h1": "2027ko lanegunak", "dl_crumb": "2027ko lanegunak",
    "dl_intro": "Astelehenetik ostiralera, BOEko estatuko eta erkidegoko jaiegunak kenduta. Udalerri bakoitzeko 2 tokiko jaiegunak kontatu gabe.",
    "dl_h2": "Lanegunak erkidegoka", "col_total": "Guztira", "col_hours": "Orduak (8 h)", "no_island": "uharteko jaia gabe",
    "dl_faq": [
        ("Zenbat lanegun ditu 2027k?",
         "2027k {wd} egun ditu astelehenetik ostiralera. Astegunetan erortzen diren estatuko eta erkidegoko jaiegunak kenduta, {lo} "
         "eta {hi} artean geratzen dira, erkidegoaren arabera, 2 tokiko jaiegunak kontatu gabe."),
        ("Zenbat lanordu ditu 2027k?",
         "8 orduko lanaldiekin, {hlo} eta {hhi} ordu artean. 22 laneguneko oporrak kenduz gero, {vlo} eta {vhi} artean geratzen dira."),
        ("Tokiko jaiegunak kontatzen dira?",
         'Ez, udalerri bakoitzean aldatzen direlako. Kendu zure herriko 2ak astegunetan erortzen badira: '
         '<a href="{loc}">2027ko tokiko jaiegunak</a>.'),
        ("2027ko zein hilabetek dute lanegun gehien?",
         "{mmax}: {nmax} erkidego gehienetan. Egun gutxiagorekin, {mmin}: {nmin}."),
    ],
    "ch_link": "Ordu aldaketa 2027",
    "ch_title": "Ordu aldaketa 2027: noiz aldatzen den ordua Espainian",
    "ch_desc": "Noiz aldatzen den ordua: hurrengo aldaketa, erlojua aurreratu edo atzeratu egiten den, Kanariak eta 2026, 2027 eta 2028ko datak.",
    "ch_h1": "Ordu aldaketa 2027", "ch_crumb": "Ordu aldaketa",
    "ch_intro": "Martxoko azken igandean eta urriko azken igandean, Europar Batasun osoan bezala.",
    "next_change": "Hurrengo aldaketa", "last_change": "Azken aldaketa",
    "su": "2:00etan 3:00 izango dira (Kanarietan, 1:00etan 2:00 izango dira)",
    "wi": "3:00etan 2:00 izango dira (Kanarietan, 2:00etan 1:00 izango da)",
    "su_s": "2:00 → 3:00", "wi_s": "3:00 → 2:00",
    "ch_h2": "Ordu aldaketak {a}-{b}", "col_year": "Urtea", "col_su": "Udako ordutegia", "col_wi": "Neguko ordutegia",
    "ch_src": "236/2002 Errege Dekretua",
    "ch_faq": [
        ("Noiz aldatzen da ordua 2027an?",
         "Data hauetan: {su27} (2:00etan 3:00 izango dira) eta {wi27} (3:00etan 2:00 izango dira). Kanarietan, ordubete lehenago "
         "haien erlojuan."),
        ("Erlojua aurreratu edo atzeratu egiten da?",
         "Martxoan ordubete aurreratzen da, ordubete gutxiago lo egiten dugu eta udako ordutegia hasten da. Urrian ordubete atzeratzen "
         "da, ordubete gehiago lo egiten dugu eta neguko ordutegia itzultzen da."),
        ("Zergatik aldatzen da ordua data horietan?",
         "2000/84/EE Zuzentarauak martxoko azken igandean eta urriko azken igandean finkatzen du aldaketa, 1:00etan UTC, Europar "
         "Batasun osoan. Espainian " + BOE_RD.format("236/2002 Errege Dekretuak") + " aplikatzen du."),
        ("Ordu aldaketa kenduko da?",
         "Europako Batzordeak 2018an proposatu zuen kentzea, eta Espainiak berriro eskatu zuen 2025ean, baina ez da onartu. "
         "Zuzentaraua aldatzen ez den bitartean, ordua bi aldiz aldatzen da urtean."),
    ],
}
ONLY_WK = [x for x in ("es", "ca", "gl", "eu") if x in S]
PATH_WK = "semana/"
ONLY_DH = [x for x in ("es", "ca", "gl", "eu") if "dh_link" in S.get(x, {})]
PATH_DH = "dias-habiles/"
ONLY_DL = [x for x in ("es", "ca", "gl", "eu") if "dl_link" in S.get(x, {})]
PATH_DL = "dias-laborables-2027/"
ONLY_CH = [x for x in ("es", "ca", "gl", "eu") if "ch_link" in S.get(x, {})]
PATH_CH = "cambio-de-hora/"


def L(key):
    return S[B.LANG][key]


def ln(key, n, **kw):
    v = L(key)
    return (v["one"] if n == 1 else v["other"]).format(n=n, **kw)


AND = {"es": "y", "ca": "i", "gl": "e", "eu": "eta"}


def join(xs):
    return xs[0] if len(xs) == 1 else f'{", ".join(xs[:-1])} {AND[B.LANG]} {xs[-1]}'


def langs_arg(only):
    """write() and head_html() take None for 'every language'."""
    return None if set(only) >= set(B.LANGS) else only


# ---------------------------------------------------------------- dates

def ds(d, year=None):
    """dshort, with the year when the date is outside `year` (or always when year is None)."""
    s = B.dshort(d)
    if year is not None and d.year == year:
        return s
    return f"{d.year} {s}" if B.LANG == "eu" else f"{s} {d.year}"


def rng(a, b, year=None):
    if a.month == b.month and a.year == b.year and B.LANG != "eu":
        return f'{B.T["_wd3"][a.weekday()]} {a.day} – {ds(b, year)}'
    return f"{ds(a, year)} – {ds(b, year)}"


def dlong_y(d):
    """lunes 4 de enero de 2027 · dilluns 4 de gener de 2027 · luns 4 de xaneiro de 2027 · 2027ko urtarrilaren 4a, astelehena"""
    return f"{d.year}ko {B.dlong(d)}" if B.LANG == "eu" else f"{B.dlong(d)} de {d.year}"


def weeks(year):
    """[(week, monday, sunday)] of an ISO year."""
    d, out = dt.date.fromisocalendar(year, 1, 1), []
    while d.isocalendar()[0] == year:
        out.append((d.isocalendar()[1], d, d + dt.timedelta(6)))
        d += dt.timedelta(7)
    return out


# ---------------------------------------------------------------- shared html

def js_cfg(cfg):
    js = json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<script id="u-data" type="application/json">{js}</script>\n'
            f'<script src="{B.ASSETS}util.js?v={B.short_hash(B.ROOT / "util.js")}"></script>')


def base_cfg():
    return {"wd3": B.T["_wd3"], "mon3": B.T["_mon3"], "wd": B.T["_wd"], "months": B.T["_months"], "eu": B.LANG == "eu"}


def faq(qas):
    import pages
    return pages.faq_html(qas), pages.faq_ld(qas)


def ld(*objs):
    import pages
    return pages.ld(*objs)


def crumbs(name, path):
    import pages
    items = [(B.t("spain"), ""), (name, path)]
    return B.crumbs_html(items), pages.crumbs_ld(items)


def app_ld(name, path, desc):
    return {"@type": "WebApplication", "name": name, "url": B.URL + path, "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Web", "inLanguage": B.IN_LANG[B.LANG], "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "description": desc}


def card(big_id, big, label, sub, label_first=False, pre=""):
    """The big-number card of the vacation optimizer (.vres), without its share buttons; `pre`: a small label on top."""
    n = f'<b class="vh-n" id="{big_id}">{big}</b>'
    t = f'<span class="vh-t" id="{big_id}-t">{label}</span>'
    pre = f'<p class="flabel">{pre}</p>' if pre else ""
    return (f'<div class="vres"><div class="vres-t">{pre}<p class="vhd">{t + n if label_first else n + t}</p>'
            f'<p class="vh-s">{sub}</p></div></div>')


# ---------------------------------------------------------------- 1 /semana/

def week_page(data, write):
    y, w, _ = TODAY.isocalendar()
    mon = TODAY - dt.timedelta(TODAY.weekday())
    left = (dt.date(TODAY.year, 12, 31) - TODAY).days
    sub = (f'<span id="wr">{rng(mon, mon + dt.timedelta(6))}</span> · '
           f'<span id="wl">{ln("left", left, y=TODAY.year)}</span>')
    h1 = L("wk_h1")
    ch, cld = crumbs(L("wk_crumb"), PATH_WK)
    hero = (f'<div class="hero wrap">{ch}<h1>{E(h1)}</h1><p class="ctx">{E(L("wk_intro"))}</p>'
            f'{card("wn", w, L("week"), sub, label_first=True)}</div>')
    secs = []
    for year in YEARS:
        ws = weeks(year)
        rows = "".join(f'<tr data-w="{year}-{n}"{" class=on" if (year, n) == (y, w) else ""}><th scope="row">{n}</th>'
                       f'<td>{rng(a, b, year)}</td></tr>' for n, a, b in ws)
        tbl = (f'<table class="tbl vrank wk"><thead><tr><th scope="col">{L("col_week")}</th><th scope="col">{L("col_mon_sun")}</th></tr></thead>'
               f'<tbody>{rows}</tbody></table>')
        secs.append(B.section(f"s{year}", L("weeks_of").format(y=year), tbl, f'<p class="m">{L("n_weeks").format(n=len(ws))}</p>'))
    y1, y2 = YEARS
    jy, jw, _ = dt.date(y2, 1, 1).isocalendar()
    jmon = dt.date.fromisocalendar(jy, jw, 1)
    fmt = {"y1": y1, "y2": y2, "n1": len(weeks(y1)), "n2": len(weeks(y2)), "w1": dlong_y(dt.date.fromisocalendar(y2, 1, 1)),
           "jw": jw, "jy": jy, "jmon": dlong_y(jmon), "jsun": dlong_y(jmon + dt.timedelta(6))}
    qas = [(q.format(**fmt), a.format(**fmt)) for q, a in L("wk_faq")]
    fh, fld = faq(qas)
    main = (f'{hero}<div class="wrap body narrow">{secs[0]}{B.ad("hub")}{secs[1]}{fh}</div>'
            + js_cfg({**base_cfg(), "page": "week", "left": L("left")}))
    head = B.head_html(L("wk_title"), L("wk_desc"), PATH_WK, f"{B.SITE}{B.ASSETS}og/espana.png", ld(cld, fld),
                       langs=langs_arg(ONLY_WK))
    write(PATH_WK, B.page(head, "pg", "", main, data, js=False), UPDATED, langs_arg(ONLY_WK))


# ---------------------------------------------------------------- 2 /dias-habiles/

LO, HI, LOC_FROM = dt.date(2026, 1, 1), dt.date(2027, 12, 31), "2027-01-01"  # data years; city locals only for 2027


def load_year(year):
    """data/<year>.json with names in this language (missing translations stay Spanish)."""
    d = B.localize(json.loads((B.ROOT / "data" / f"{year}.json").read_text("utf-8")))
    tr = NAMES_2026.get(B.LANG, {}) if year == 2026 else {}
    for h in d["holidays"]:
        h["name"] = tr.get(h["name"], h["name"])
    for z in d["zones"].values():
        for o in z["options"]:
            if "add" in o:
                o["add"]["name"] = tr.get(o["add"]["name"], o["add"]["name"])
    return d


NAMES_2026 = {  # 2026-only holiday names in ca/gl/eu (2027 names come from data/i18n.json, same wording)
    "ca": {"Asunción de la Virgen": "L'Assumpció", "Día de Canarias": "Dia de Canàries", "Día de Ceuta": "Dia de Ceuta",
           "Día de la Rioja": "Dia de La Rioja", "Día siguiente a Todos los Santos": "L'endemà de Tots Sants",
           "Fiesta Sacrificio-Aid al Adha": "Festa del Sacrifici-Aid al Adha", "Fiesta Sacrificio-Eidul Adha": "Festa del Sacrifici-Eidul Adha",
           "Fiesta de la Comunidad de Madrid": "Festa de la Comunitat de Madrid",
           "Lunes siguiente al Día de la Constitución Española": "Dilluns següent al Dia de la Constitució",
           "Lunes siguiente al Día de les Illes Balears": "Dilluns següent al Dia de les Illes Balears",
           "San Esteban": "Sant Esteve", "San Juan": "Sant Joan",
           "Santiago Apóstol/Día Nacional de Galicia": "Sant Jaume / Dia Nacional de Galiza"},
    "gl": {"Asunción de la Virgen": "Asunción da Virxe", "Día de Canarias": "Día de Canarias", "Día de Ceuta": "Día de Ceuta",
           "Día de la Rioja": "Día da Rioxa", "Día siguiente a Todos los Santos": "Día seguinte a Todos os Santos",
           "Fiesta Sacrificio-Aid al Adha": "Festa do Sacrificio-Aid al Adha", "Fiesta Sacrificio-Eidul Adha": "Festa do Sacrificio-Eidul Adha",
           "Fiesta de la Comunidad de Madrid": "Festa da Comunidade de Madrid",
           "Lunes siguiente al Día de la Constitución Española": "Luns seguinte ao Día da Constitución Española",
           "Lunes siguiente al Día de les Illes Balears": "Luns seguinte ao Día das Illes Balears",
           "San Esteban": "Santo Estevo", "San Juan": "San Xoán",
           "Santiago Apóstol/Día Nacional de Galicia": "Santiago Apóstolo / Día Nacional de Galiza"},
    "eu": {"Asunción de la Virgen": "Ama Birjinaren Jasokundea", "Día de Canarias": "Kanarietako Eguna", "Día de Ceuta": "Ceutako Eguna",
           "Día de la Rioja": "Errioxaren Eguna", "Día siguiente a Todos los Santos": "Santu Guztien Egunaren hurrengo eguna",
           "Fiesta Sacrificio-Aid al Adha": "Sakrifizioaren Jaia - Aid al Adha", "Fiesta Sacrificio-Eidul Adha": "Eidul Adha - Sakrifizioaren Jaia",
           "Fiesta de la Comunidad de Madrid": "Madrilgo Erkidegoaren Jaia",
           "Lunes siguiente al Día de la Constitución Española": "Konstituzio Egunaren hurrengo astelehena",
           "Lunes siguiente al Día de les Illes Balears": "Illes Balears-en Egunaren hurrengo astelehena",
           "San Esteban": "San Esteban eguna", "San Juan": "San Joan eguna",
           "Santiago Apóstol/Día Nacional de Galicia": "Santiago Apostolua / Galizako Eguna Nazionala"},
}


def is_off(d, off, sat=False):
    """Sunday, Saturday unless it is a working day, or a holiday. Same as isOff() in util.js."""
    return d.weekday() == 6 or (d.weekday() == 5 and not sat) or d.isoformat() in off


def count_workdays(a, b, off, sat=False):
    """Working days from a to b, both included (swapped when a > b). Same as countWorkdays() in util.js."""
    if a > b:
        a, b = b, a
    return sum(1 for k in range((b - a).days + 1) if not is_off(a + dt.timedelta(k), off, sat))


def add_workdays(a, n, off, sat=False):
    """The n-th working day after a (the count starts the next day, Ley 39/2015 art. 30); n = 0 gives a.
    Same as addWorkdays() in util.js."""
    d = a
    while n > 0:
        d += dt.timedelta(1)
        if not is_off(d, off, sat):
            n -= 1
    return d


def dh_data(datas, cities):
    """Holidays for util.js: national, per comunidad, zones (islands, Arán) and cities (2027 locals), both years."""
    nat, reg, zon, cit = [], {}, {}, {}
    for d in datas:
        nat += [[h["date"], h["name"], "n"] for h in d["holidays"] if h["regions"] == "all"]
        for r in d["regions"]:
            reg.setdefault(r["slug"], []).extend([h["date"], h["name"], h["kind"]] for h in B.region_holidays(d, r["slug"]))
            for o in d["zones"].get(r["slug"], {}).get("options", []):
                if "add" not in o:
                    continue
                zs = zon.setdefault(r["slug"], {})
                z = zs.setdefault(o["slug"], [o["slug"], o["name"], [], []])
                z[2].append([o["add"]["date"], o["add"]["name"], "i" if r["slug"] == "canarias" else "r"])
                if "remove" in o:
                    z[3].append(o["remove"])
    for x in sorted(cities, key=lambda x: x["title_name"]):
        cit.setdefault(x["r"]["slug"], []).append([x["slug"], x["title_name"], x["zone"] or "", [[h["date"], h["name"]] for h in x["holidays"]]])
    return {"nat": sorted(nat), "reg": {k: sorted(v) for k, v in reg.items()}, "zon": {k: list(v.values()) for k, v in zon.items()}, "cit": cit}


def dmy_long(d):
    """2 de noviembre de 2026 · 2 de novembre de 2026 · 2026ko azaroaren 2a (holiday list when the range spans years)."""
    return f"{d.year}ko {B.dm(d)}" if B.LANG == "eu" else f"{B.dm(d)} de {d.year}"


def hl_item(iso, name, kind, multi):
    """One holiday of the range: the markup of build.hol_item(). Same as hlItem() in util.js."""
    d = dt.date.fromisoformat(iso)
    we = " we" if d.weekday() >= 5 else ""
    return (f'<li class="k-{kind}"><span class="d"><time datetime="{iso}">{dmy_long(d) if multi else B.dm(d)}</time> '
            f'<span class="m{we}">{B.T["_wd"][d.weekday()]}</span></span><span class="h">{E(name)}</span>'
            f'<span class="s">{B.sw(kind)}{B.t(B.KINDS[kind])}</span></li>')


def date_field(id_, label, value):
    return (f'<div class="field"><label for="{id_}">{label}</label><input type="date" class="din" id="{id_}" value="{value}" '
            f'min="{LO}" max="{HI}" required></div>')


def dh_page(data, write, cities):
    datas = [load_year(2026), data]
    cfg = dh_data(datas, cities)
    a, b = TODAY, dt.date(TODAY.year, 12, 31)
    off = {x[0]: x for x in cfg["nat"]}
    n = count_workdays(a, b, off)
    inr = [x for x in cfg["nat"] if a.isoformat() <= x[0] <= b.isoformat()]
    k = sum(1 for x in inr if not (dt.date.fromisoformat(x[0]).weekday() >= 5))
    regs = "".join(f'<option value="{r["slug"]}">{E(r["name"])}</option>' for r in data["regions"])
    pick1 = (f'<div class="pickers">'
             f'<div class="field"><label for="dreg">{B.t("region_label")}</label><select id="dreg"><option value="">{L("nat_only")}</option>{regs}</select></div>'
             f'<div class="field" id="dmun-f" hidden><label for="dmun">{B.t("municipio")}</label><select id="dmun"></select></div>'
             f'<div class="field"><label for="dsat">{L("workweek")}</label><select id="dsat"><option value="0">{L("mon_fri")}</option>'
             f'<option value="1">{L("mon_sat")}</option></select></div></div>')
    modes = (f'<div class="tools dmode" role="group"><button type="button" class="btn on" data-mode="a" aria-pressed="true">{L("mode_a")}</button>'
             f'<button type="button" class="btn" data-mode="b" aria-pressed="false">{L("mode_b")}</button></div>')
    pick2 = (f'<div class="pickers" id="dpa">{date_field("da", L("from"), a)}{date_field("db", L("to"), b)}</div>'
             f'<div class="pickers" id="dpb" hidden>{date_field("dc", L("start"), a)}'
             f'<div class="field"><label for="dn">{L("n_work")}</label><span class="stepper"><button type="button" id="dnm" aria-label="{B.t("one_less")}">−</button>'
             f'<input id="dn" type="number" inputmode="numeric" min="0" max="999" value="10"><button type="button" id="dnp" aria-label="{B.t("one_more")}">+</button></span></div></div>')
    sub = (f'<span id="dsub">{rng(a, b)} · {ln("nat_days", (b - a).days + 1)} · {ln("n_hol_in", k)}</span>'
           f'<br><span class="m">{L("caveat")}</span>')
    res = card("dres", n, ln("res_a", n), sub)
    h1 = L("dh_h1")
    ch, cld = crumbs(L("dh_crumb"), PATH_DH)
    hero = f'<div class="hero wrap">{ch}<h1>{E(h1)}</h1><p class="ctx">{E(L("dh_intro"))}</p>{pick1}{modes}{pick2}{res}</div>'
    multi = a.year != b.year
    items = "".join(hl_item(*x, multi) for x in inr)
    hol_sec = B.section("festivos", L("h_hols_in"), f'<ol class="hl" id="dhl">{items}</ol><p class="m" id="dnone"{" hidden" if items else ""}>{L("none_in")}</p>')
    qas = L("dh_faq")
    fh, fld = faq(qas)
    keys = ["res_a", "nat_days", "n_hol_in", "after", "no_loc", "out", "all_region", "isla", "zona"]
    js = {**base_cfg(), **cfg, "page": "dh", "min": str(LO), "max": str(HI), "loc": LOC_FROM, "mof": B.T["_mof"],
          "k": {x: B.t(B.KINDS[x]) for x in B.KINDS}, "s": {x: L(x) for x in keys}}
    main = f'{hero}<div class="wrap body narrow">{hol_sec}{B.ad("hub")}{fh}</div>' + js_cfg(js)
    head = B.head_html(L("dh_title"), L("dh_desc"), PATH_DH, f"{B.SITE}{B.ASSETS}og/espana.png",
                       ld(cld, app_ld(h1, PATH_DH, L("dh_desc")), fld), langs=langs_arg(ONLY_DH))
    write(PATH_DH, B.page(head, "pg vac", "", main, data, js=False), UPDATED, langs_arg(ONLY_DH))


# ---------------------------------------------------------------- 3 /dias-laborables-2027/

def per_month(hols, year=B.YEAR):
    """Working days (Monday to Friday, not a holiday) in each month of `year`."""
    hd = {h["date"] for h in hols}
    out = [0] * 12
    d = dt.date(year, 1, 1)
    while d.year == year:
        if d.weekday() < 5 and d.isoformat() not in hd:
            out[d.month - 1] += 1
        d += dt.timedelta(1)
    return out


def dl_rows(data):
    """[(slug, label, zone label or None, months)]: each comunidad, then its islands / Arán as sub-rows."""
    out = []
    for r in data["regions"]:
        out.append((r["slug"], r["name"], None, per_month(B.region_holidays(data, r["slug"]))))
        for o in data["zones"].get(r["slug"], {}).get("options", []):
            if "add" in o:
                out.append((r["slug"], r["name"], o["name"], per_month(B.region_holidays(data, r["slug"], o["slug"]))))
    return out


def dl_page(data, write):
    rows = dl_rows(data)
    head_m = "".join(f'<th scope="col" class="num">{m.capitalize()}</th>' for m in B.T["_mon3"])
    trs = []
    for slug, name, zone, ms in rows:
        tot = sum(ms)
        if zone:
            th = f'<th scope="row">{E(zone)}</th>'
        else:
            note = f' <span class="m">{L("no_island")}</span>' if slug == "canarias" else ""
            th = f'<th scope="row"><a href="{B.BASE}{slug}/">{E(name)}</a>{note}</th>'
        cells = "".join(f'<td class="num">{n}</td>' for n in ms)
        trs.append(f'<tr{" class=sub" if zone else f" id={slug}"}>{th}{cells}<td class="num"><b>{tot}</b></td><td class="num">{tot * 8}</td></tr>')
    tbl = (f'<div class="tscroll"><table class="tbl hub dl"><thead><tr><th scope="col">{B.t("region_label")}</th>{head_m}'
           f'<th scope="col" class="num">{L("col_total")}</th><th scope="col" class="num">{L("col_hours")}</th></tr></thead>'
           f'<tbody>{"".join(trs)}</tbody></table></div>')
    mains = [sum(ms) for slug, _, zone, ms in rows if not zone and slug != "canarias"] + \
            [sum(ms) for slug, _, zone, ms in rows if zone and slug == "canarias"]  # Canarias: with the island's day
    lo, hi = min(mains), max(mains)
    regs = [ms for _, _, zone, ms in rows if not zone]
    mode = [max(sorted({ms[k] for ms in regs}), key=[ms[k] for ms in regs].count) for k in range(12)]  # usual value per month
    nmax, nmin = max(mode), min(mode)
    kmax, kmin = [k for k in range(12) if mode[k] == nmax], [k for k in range(12) if mode[k] == nmin]
    wd = sum(1 for d in B.DAYS if d.weekday() < 5)
    fmt = {"wd": wd, "lo": lo, "hi": hi, "hlo": f"{lo * 8:,}".replace(",", "."), "hhi": f"{hi * 8:,}".replace(",", "."),
           "vlo": f"{(lo - 22) * 8:,}".replace(",", "."), "vhi": f"{(hi - 22) * 8:,}".replace(",", "."),
           "loc": f"{B.BASE}festivos-locales/", "mmax": join([B.T["_months"][k] for k in kmax]).capitalize(), "nmax": nmax,
           "mmin": join([B.T["_months"][k] for k in kmin]), "nmin": nmin}
    qas = [(q.format(**fmt), a.format(**fmt)) for q, a in L("dl_faq")]
    fh, fld = faq(qas)
    h1 = L("dl_h1")
    ch, cld = crumbs(L("dl_crumb"), PATH_DL)
    src = data["source"]
    hero = (f'<div class="hero wrap">{ch}<h1>{E(h1)}</h1><p class="ctx">{E(L("dl_intro"))} '
            f'<a href="{src["url"]}" rel="noopener">{src["id"]}</a></p></div>')
    sec = B.section("comunidades", L("dl_h2"), tbl)
    main = f'{hero}<div class="wrap body">{sec}{B.ad("hub")}<div class="narrow">{fh}</div></div>'
    head = B.head_html(L("dl_title"), L("dl_desc"), PATH_DL, f"{B.SITE}{B.ASSETS}og/espana.png", ld(cld, fld),
                       langs=langs_arg(ONLY_DL))
    write(PATH_DL, B.page(head, "pg", "", main, data, js=False), data["updated"], langs_arg(ONLY_DL))


# ---------------------------------------------------------------- 4 /cambio-de-hora/

CH_YEARS = (2026, 2027, 2028)


def last_sunday(year, month):
    """Last Sunday of the month: summer time starts the last Sunday of March and ends the last Sunday of October
    (Directive 2000/84/EC, Real Decreto 236/2002)."""
    d = dt.date(year + month // 12, month % 12 + 1, 1) - dt.timedelta(1)
    return d - dt.timedelta((d.weekday() + 1) % 7)


def changes():
    """[(date, 'su' | 'wi')] in order."""
    return [(last_sunday(y, m), k) for y in CH_YEARS for m, k in ((3, "su"), (10, "wi"))]


def month_year(d):
    return f'{d.year}ko {B.T["_months"][d.month - 1]}' if B.LANG == "eu" else f'{B.T["_months"][d.month - 1]} {d.year}'


def ch_page(data, write):
    cs = changes()
    nxt = next(((d, k) for d, k in cs if d >= TODAY), cs[-1])
    prev = [(d, k) for d, k in cs if d < TODAY]
    sub = (f'<span id="cwd">{B.T["_wd"][nxt[0].weekday()]}</span> · <span id="cdo">{L(nxt[1])}</span><br>'
           f'{L("last_change")}: <span id="cla">{ds(prev[-1][0]) + " · " + L(prev[-1][1] + "_s") if prev else "–"}</span>')
    big = card("cnx", nxt[0].day, month_year(nxt[0]), sub, pre=L("next_change"))
    h1 = L("ch_h1")
    ch, cld = crumbs(L("ch_crumb"), PATH_CH)
    hero = f'<div class="hero wrap">{ch}<h1>{E(h1)}</h1><p class="ctx">{E(L("ch_intro"))}</p>{big}</div>'
    by = {}
    for d, k in cs:
        by.setdefault(d.year, {})[k] = d
    rows = "".join(f'<tr{" class=on" if nxt[0].year == y else ""}><th scope="row">{y}</th>'
                   f'<td><time datetime="{by[y]["su"]}">{ds(by[y]["su"], y)}</time> <span class="m">{L("su_s")}</span></td>'
                   f'<td><time datetime="{by[y]["wi"]}">{ds(by[y]["wi"], y)}</time> <span class="m">{L("wi_s")}</span></td></tr>' for y in CH_YEARS)
    tbl = (f'<table class="tbl vrank"><thead><tr><th scope="col">{L("col_year")}</th><th scope="col">{L("col_su")}</th>'
           f'<th scope="col">{L("col_wi")}</th></tr></thead><tbody>{rows}</tbody></table>'
           f'<p class="src"><a href="https://www.boe.es/eli/es/rd/2002/03/01/236" rel="noopener">{L("ch_src")}</a></p>')
    sec = B.section("fechas", L("ch_h2").format(a=CH_YEARS[0], b=CH_YEARS[-1]), tbl)
    fmt = {"su27": dlong_y(by[2027]["su"]), "wi27": dlong_y(by[2027]["wi"])}
    qas = [(q.format(**fmt), a.format(**fmt)) for q, a in L("ch_faq")]
    fh, fld = faq(qas)
    js = {**base_cfg(), "page": "ch", "cs": [[d.isoformat(), k] for d, k in cs], "s": {k: L(k) for k in ("su", "wi", "su_s", "wi_s")}}
    main = f'{hero}<div class="wrap body narrow">{sec}{B.ad("hub")}{fh}</div>' + js_cfg(js)
    head = B.head_html(L("ch_title"), L("ch_desc"), PATH_CH, f"{B.SITE}{B.ASSETS}og/espana.png", ld(cld, fld),
                       langs=langs_arg(ONLY_CH))
    write(PATH_CH, B.page(head, "pg", "", main, data, js=False), UPDATED, langs_arg(ONLY_CH))


# ---------------------------------------------------------------- footer and entry point

def footer_links():
    """The 'Utilidades' block of the footer: the pages in this language, or the Spanish ones marked hreflang=es."""
    s = S.get(B.LANG, S["es"])
    items = [(PATH_DL, ONLY_DL, "dl_link"), (PATH_DH, ONLY_DH, "dh_link"), (PATH_WK, ONLY_WK, "wk_link"), (PATH_CH, ONLY_CH, "ch_link")]
    li = []
    for path, only, key in items:
        if B.LANG in only:
            li.append(f'<li><a href="{B.BASE}{path}">{E(s[key])}</a></li>')
        else:
            li.append(f'<li><a href="{B.ASSETS}{path}" hreflang="es" lang="es">{E(S["es"][key])}</a></li>')
    return f'<h2>{E(s["util"])}</h2><ul>{"".join(li)}</ul>'


def home_links():
    """One line of links on the home, below the comunidad chips: the utility pages of this language."""
    items = [(PATH_DL, ONLY_DL, "dl_link"), (PATH_DH, ONLY_DH, "dh_link"), (PATH_WK, ONLY_WK, "wk_link"), (PATH_CH, ONLY_CH, "ch_link")]
    li = [f'<a href="{B.BASE}{p}">{E(L(k))}</a>' for p, only, k in items if B.LANG in only]
    return f'<p class="more-l">{" · ".join(li)}</p>' if li else ""


def write_pages(data, write, cities):
    if B.LANG in ONLY_WK:
        week_page(data, write)
    if B.LANG in ONLY_DH:
        dh_page(data, write, cities)
    if B.LANG in ONLY_DL:
        dl_page(data, write)
    if B.LANG in ONLY_CH:
        ch_page(data, write)
