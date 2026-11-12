"""Calendario de siembra del huerto: what to sow in seedbed, sow direct or transplant each month, by climate zone of Spain.

Base calendar = interior templado (Madrid, Zaragoza, Toledo...), the usual one of municipal school-garden calendars. The other
zones move it with the rule the calendars themselves give: frost-tender summer crops one month earlier on the warm coast and
one month later in cold inland areas and the Atlantic north; cool-season crops one month earlier in spring on the warm coast,
whose autumn window also stays open a month longer (the reverse in cold areas), with a few explicit exceptions (broad beans, peas and garlic in hard-frost areas,
lettuce all year in the mild Atlantic summer)."""
AEMET = "https://www.aemet.es/es/serviciosclimaticos/datosclimatologicos/valoresclimatologicos"
MADRID = "https://diario.madrid.es/huertosescolares/"
FAO = "https://www.fao.org/4/a0218s/a0218s00.htm"

ZONES = [("templada", "Interior templado"), ("calida", "Litoral mediterráneo y sur"), ("fria", "Interior frío y montaña"),
         ("atlantica", "Norte atlántico")]
ZONE_TXT = {"templada": "Madrid, Zaragoza, Toledo, Lleida, Badajoz, Córdoba alta…", "calida": "Valencia, Murcia, Alicante, Málaga, Sevilla, Baleares…",
            "fria": "Burgos, León, Soria, Teruel, Ávila, Pirineo…", "atlantica": "Galicia, Asturias, Cantabria, País Vasco"}


def r(a, b):
    return list(range(a, b + 1)) if a <= b else list(range(a, 13)) + list(range(1, b + 1))


# name, kind (w = frost-tender summer crop, c = cool-season crop), semillero, siembra directa, trasplante/plantación (base zone)
CROPS = [
    ("Tomate", "w", r(2, 4), [], r(4, 6)),
    ("Pimiento", "w", r(1, 3), [], r(5, 6)),
    ("Berenjena", "w", r(2, 3), [], r(5, 6)),
    ("Calabacín", "w", r(3, 4), r(4, 6), r(4, 5)),
    ("Pepino", "w", r(3, 4), r(5, 6), r(5, 6)),
    ("Melón", "w", r(3, 4), [5], [5]),
    ("Sandía", "w", r(3, 4), [5], [5]),
    ("Calabaza", "w", r(3, 4), r(4, 6), [5]),
    ("Judía verde", "w", [], r(4, 7), []),
    ("Maíz dulce", "w", [], r(4, 6), []),
    ("Albahaca", "w", r(3, 4), [], r(5, 6)),
    ("Lechuga", "c", r(1, 3) + r(7, 9), r(3, 4) + r(8, 9), r(3, 5) + r(8, 10)),
    ("Espinaca", "c", [], r(2, 4) + r(9, 11), []),
    ("Acelga", "c", r(2, 3) + r(7, 8), r(3, 5) + r(8, 9), r(4, 5) + r(9, 10)),
    ("Zanahoria", "c", [], r(3, 7), []),
    ("Rábano", "c", [], r(2, 5) + r(9, 10), []),
    ("Remolacha", "c", [], r(3, 6), []),
    ("Cebolla", "c", r(1, 2) + r(9, 11), [], r(1, 4)),
    ("Puerro", "c", r(2, 4), [], r(5, 7)),
    ("Col y repollo", "c", r(3, 4) + r(6, 7), [], r(5, 6) + r(8, 9)),
    ("Brócoli", "c", r(6, 7), [], r(8, 9)),
    ("Coliflor", "c", r(5, 7), [], r(7, 9)),
    ("Guisante", "c", [], r(2, 3) + r(10, 11), []),
    ("Haba", "c", [], [2] + r(10, 11), []),
    ("Ajo", "c", [], r(10, 12) + [1], []),
    ("Patata", "c", [], r(3, 4), []),
    ("Fresa", "c", [], [], [3] + r(9, 10)),
    ("Perejil", "c", [], r(3, 5) + [9], []),
]

# explicit exceptions: (zone, crop) -> (semillero, directa, trasplante)
OVERRIDE = {
    ("fria", "Haba"): ([], r(2, 3), []),
    ("fria", "Guisante"): ([], r(3, 4), []),
    ("fria", "Ajo"): ([], [11] + r(2, 3), []),
    ("atlantica", "Lechuga"): (r(2, 8), r(3, 8), r(3, 9)),
    ("calida", "Patata"): ([], r(1, 3) + r(8, 9), []),
}


def shift(ms, kind, zone):
    if zone == "templada":
        return sorted(ms)
    out = set()
    for m in ms:
        if kind == "w":
            d = -1 if zone == "calida" else 1
        else:
            spring = m <= 6
            if zone == "calida" and not spring:  # mild winter: the autumn window stays open one month longer
                out.add(m)
            d = {"calida": -1 if spring else 1, "fria": 1 if spring else -1, "atlantica": 0}[zone]
        out.add((m - 1 + d) % 12 + 1)
    return sorted(out)


def table():
    out = {}
    for z, _ in ZONES:
        rows = []
        for name, kind, s, d, t in CROPS:
            if (z, name) in OVERRIDE:
                s2, d2, t2 = OVERRIDE[(z, name)]
            else:
                s2, d2, t2 = shift(s, kind, z), shift(d, kind, z), shift(t, kind, z)
            rows.append([name, s2, d2, t2])
        out[z] = rows
    return out


MON = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

JS = r"""
function (v, H, C) {
  var Z = C.d.T[v.zona] || C.d.T.templada, m = +String(v.mes).slice(5, 7), M = C.d.M;
  if (!(m >= 1 && m <= 12)) return { err: 'Elige un mes.' };
  function list(k) { return Z.filter(function (c) { return c[k].indexOf(m) >= 0; }).map(function (c) { return c[0]; }); }
  var s = list(1), d = list(2), t = list(3);
  var rows = [['Semillero', s.length ? s.join(', ') : '—'], ['Siembra directa', d.length ? d.join(', ') : '—'], ['Trasplante o plantación', t.length ? t.join(', ') : '—']];
  var head = '<tr><th>Cultivo</th>' + M.map(function (x, i) { return '<th' + (i + 1 === m ? ' class="hs-m"' : '') + '>' + x.charAt(0).toUpperCase() + '</th>'; }).join('') + '</tr>';
  var body = Z.map(function (c) {
    return '<tr><td>' + c[0] + '</td>' + M.map(function (x, i) {
      var k = i + 1, a = (c[1].indexOf(k) >= 0 ? 'S' : '') + (c[2].indexOf(k) >= 0 ? 'D' : '') + (c[3].indexOf(k) >= 0 ? 'T' : '');
      return '<td class="hs-c' + (a ? ' hs-' + a.charAt(a.length - 1) : '') + (k === m ? ' hs-m' : '') + '">' + a + '</td>';
    }).join('') + '</tr>';
  }).join('');
  var html = '<details class="hs-y"><summary>Todo el año</summary><div class="tblw"><table class="tbl hs-t"><thead>' + head + '</thead><tbody>' + body +
    '</tbody></table></div><p class="hnote">S semillero · D siembra directa · T trasplante o plantación</p></details>';
  return { label: 'Qué sembrar en ' + M[m - 1], big: s.concat(d, t).filter(function (x, i, a) { return a.indexOf(x) === i; }).length + ' cultivos', sub: C.d.ZN[v.zona] || '', rows: rows, html: html, print: true,
    note: 'Fechas medias de la zona. Los cultivos de verano no se trasplantan hasta que pasa la última helada de tu pueblo.',
    n: { s: s.join(','), d: d.join(','), t: t.join(',') } };
}
"""

CSS = (".hs-t{font-size:.82rem}.hs-t th,.hs-t td{text-align:center;padding:.25rem .3rem}.hs-t td:first-child{text-align:left;white-space:nowrap}"
       ".hs-S{background:color-mix(in srgb,#d9a400 22%,transparent)}.hs-D{background:color-mix(in srgb,#3c9a3c 24%,transparent)}"
       ".hs-T{background:color-mix(in srgb,#2f74c0 22%,transparent)}.hs-t .hs-m{outline:2px solid currentColor;outline-offset:-2px}"
       ".hs-y summary{cursor:pointer;font-weight:600;margin:.8rem 0 .4rem}.tblw{overflow-x:auto}")


def data(ctx):
    return {"T": table(), "M": MON, "ZN": ZONE_TXT}


def blocks(ctx):
    T = table()
    oct_c = [c[0] for c in T["calida"] if 10 in c[2] or 10 in c[3]]
    mar_t = [c[0] for c in T["templada"] if 3 in c[1]]
    return [
        ("Qué se siembra cada mes en el huerto", f"""
<p>En el huerto hay dos temporadas. Los <b>cultivos de verano</b> (tomate, pimiento, berenjena, calabacín, pepino, melón, sandía,
judía, maíz) no aguantan las heladas: se siembran en semillero protegido a finales de invierno y se trasplantan cuando ya no hiela,
en abril o mayo en el interior. Los <b>cultivos de invierno</b> (ajo, haba, guisante, cebolla, coles, espinaca, lechuga) prefieren el
fresco: se siembran a finales de verano y en otoño, y algunos otra vez a finales de invierno.</p>
<p>Elige tu zona y el mes, y verás qué toca en semillero, qué se siembra directamente en la tierra y qué se trasplanta o se planta.
En «Todo el año» tienes el calendario completo de 28 cultivos para imprimir. Por ejemplo, en marzo, en el interior templado, se
siembran en semillero {", ".join(mar_t[:-1]).lower()} y {mar_t[-1].lower()}.</p>"""),
        ("Las cuatro zonas", f"""
<ul>
<li><b>Interior templado</b> ({ZONE_TXT["templada"]}): inviernos con heladas, veranos calurosos. Es el calendario de referencia; los
tomates se trasplantan a partir de mediados de abril o en mayo, cuando pasa la última helada.</li>
<li><b>Litoral mediterráneo y sur</b> ({ZONE_TXT["calida"]}): casi sin heladas. Los cultivos de verano se adelantan un mes y los de
invierno se siembran durante todo el otoño y el invierno; en octubre se siembran o plantan {", ".join(oct_c[:-1]).lower()} y
{oct_c[-1].lower()}. En pleno verano el calor para la lechuga y la espinaca.</li>
<li><b>Interior frío y montaña</b> ({ZONE_TXT["fria"]}): heladas hasta mayo. Todo lo de verano se retrasa un mes, y las habas, los
guisantes y buena parte de los ajos se siembran a finales de invierno, no en otoño.</li>
<li><b>Norte atlántico</b> ({ZONE_TXT["atlantica"]}): inviernos suaves y veranos frescos y húmedos. Los cultivos de verano van un mes
más tarde que en el interior, pero la lechuga se puede sembrar de febrero a agosto.</li>
</ul>
<p>Canarias, con temperaturas suaves todo el año, se parece al litoral mediterráneo pero sin parón por frío: casi todo se puede
sembrar en cualquier mes salvo en las zonas altas.</p>"""),
        ("Cómo está hecho el calendario", f"""
<p>La base es el calendario de huerto del interior templado que usan, con pocas diferencias, los huertos escolares y urbanos
municipales, como el programa de <a href="{MADRID}" rel="noopener">huertos escolares del Ayuntamiento de Madrid</a>. Las otras zonas
lo desplazan con la regla que dan esos mismos calendarios: un mes antes o después según el riesgo de helada y el calor del verano,
que puedes comprobar en los <a href="{AEMET}" rel="noopener">valores climatológicos normales de AEMET</a> de tu estación más cercana
(días de helada y temperatura media de cada mes). La FAO explica cómo preparar el suelo, los semilleros y las rotaciones en
<a href="{FAO}" rel="noopener">«Crear y manejar un huerto escolar»</a>.</p>
<p>Las fechas son medias. Mira la variedad (hay lechugas de verano, cebollas de día corto y de día largo, habas tempranas) y la
experiencia de los hortelanos de tu pueblo: un valle abrigado y una umbría a cien metros pueden ir con un mes de diferencia.</p>"""),
    ]


FAQ = [
    ("¿Cuándo se plantan los tomates?",
     "Se siembran en semillero entre febrero y abril y se trasplantan cuando ya no hiela: en marzo-abril en la costa mediterránea, de "
     "mediados de abril a junio en el interior y en mayo-junio en zonas frías y en el norte."),
    ("¿Qué se siembra en octubre en el huerto?",
     "Ajos, habas, guisantes y espinacas, además de trasplantar lechugas, cebollas tempranas y coles en las zonas templadas. En la costa "
     "mediterránea, octubre es uno de los mejores meses del año para sembrar."),
    ("¿Cuándo se siembran los ajos?",
     "Entre octubre y enero en casi toda España (el refrán dice «ajo, por Todos los Santos»). En zonas de heladas muy fuertes, en "
     "noviembre o a finales de invierno, en febrero o marzo."),
    ("¿Qué diferencia hay entre semillero y siembra directa?",
     "En el semillero la semilla nace en bandejas o macetas protegidas y la planta se trasplanta después; se usa para tomates, "
     "pimientos, coles o cebollas. La siembra directa se hace en el sitio definitivo, como zanahorias, rábanos, judías o guisantes, que "
     "no toleran bien el trasplante."),
    ("¿Influye la luna en la siembra?",
     "Es una tradición muy extendida, pero los ensayos no han encontrado efectos claros. Si quieres seguirla, consulta el calendario "
     "lunar: lo decisivo es la temperatura del suelo y el riesgo de helada."),
]

TOOL = {
    "slug": "calendario-siembra",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "seeding",
    "order": 5,
    "name": "Calendario de siembra",
    "k": "huerto que sembrar este mes semillero trasplante tomate ajo lechuga hortalizas zona",
    "title": "Calendario de siembra del huerto: qué sembrar cada mes",
    "desc": "Qué sembrar en el huerto cada mes según tu zona de España: semillero, siembra directa y trasplante de 28 hortalizas, con el calendario anual imprimible.",
    "h1": "Calendario de siembra del huerto",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "zona", "type": "select", "label": "Zona", "value": "templada", "options": ZONES},
        {"id": "mes", "type": "month", "label": "Mes", "value": "2026-11", "today": True, "min": "2026-01", "max": "2030-12"},
    ],
    "js": JS,
    "css": CSS,
    "data": data,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("AEMET · valores climatológicos normales", AEMET), ("Ayuntamiento de Madrid · huertos escolares", MADRID),
                ("FAO · Crear y manejar un huerto escolar", FAO)],
    "related": ["calendario-lunar-2027", "riego-goteo", "abonado-npk", "marco-plantacion"],
    "tests": [
        ({"zona": "templada", "mes": "2026-10"}, {"n.d": "Espinaca,Rábano,Guisante,Haba,Ajo"}),
        ({"zona": "calida", "mes": "2027-03"}, {"n.t": "Tomate,Calabacín,Lechuga,Acelga,Cebolla"}),
        ({"zona": "fria", "mes": "2027-03"}, {"n.d": "Espinaca,Rábano,Guisante,Haba,Ajo"}),
        ({"zona": "templada", "mes": "2026-11"}, {"n.t": "", "n.s": "Cebolla"}),
        ({"zona": "atlantica", "mes": "2027-08"}, {"n.s": "Lechuga,Acelga"}),
        ({"mes": ""}, {"err": "Elige un mes."}),
    ],
}
