"""Carga ganadera: UGM of a herd with the PAC conversion table (RD 1048/2022, anexo V) and UGM per hectare against the
ranges of the extensive grazing eco-scheme (art. 30.2.b: wet pastures 0,4-2, Mediterranean pastures 0,2-1,2)."""
RD = "https://www.boe.es/buscar/act.php?id=BOE-A-2022-23048"
UE = "https://eur-lex.europa.eu/eli/reg_impl/2014/808/oj"

# input id, label, UGM per head (RD 1048/2022 anexo V)
HERD = [
    ("vleche", "Vacas de leche", 1.0),
    ("vcarne", "Otras vacas", 0.8),
    ("novillas", "Novillas ≥ 2 años", 0.8),
    ("toros", "Machos ≥ 2 años", 1.0),
    ("bov12", "Bovinos 1-2 años", 0.7),
    ("bov01", "Terneros < 1 año", 0.4),
    ("ovi", "Ovejas y cabras", 0.1),
    ("equ", "Équidos", 0.8),
    ("cerdas", "Cerdas de cría", 0.5),
    ("cerdos", "Otros cerdos", 0.3),
    ("lechones", "Lechones > 20 kg", 0.027),
]

JS = r"""
function (v, H, C) {
  var K = C.d.K, ugm = 0, rows = [], n = 0;
  for (var i = 0; i < K.length; i++) {
    var c = v[K[i][0]];
    if (isNaN(c) || !c) continue;
    if (c < 0) return { err: 'El número de animales no puede ser negativo.' };
    var u = c * K[i][2]; ugm += u; n += c;
    rows.push([K[i][1] + ' <small>' + H.num(c, 0) + ' × ' + H.num(K[i][2], K[i][2] < 0.1 ? 3 : 1) + '</small>', H.num(u, 2) + ' UGM']);
  }
  if (!n) return { err: 'Escribe cuántos animales tienes.' };
  var ha = v.ha;
  if (!(ha > 0)) return { err: 'Escribe la superficie de pastos en hectáreas.' };
  var wet = v.pasto === 'h', lo = v.red ? (wet ? 0.2 : 0.1) : (wet ? 0.4 : 0.2), hi = wet ? 2 : 1.2, c = ugm / ha;
  var st = c < lo ? 'baja' : c > hi ? 'alta' : 'ok';
  rows.push(['Total', H.num(ugm, 2) + ' UGM', 'tot']);
  rows.push(['Rango del ecorrégimen', H.num(lo, 1) + '–' + H.num(hi, 1) + ' UGM/ha', 'sub']);
  rows.push(['Hectáreas para no pasar de ' + H.num(hi, 1), H.num(ugm / hi, 2) + ' ha']);
  rows.push(['Hectáreas máximas para llegar a ' + H.num(lo, 1), H.num(ugm / lo, 2) + ' ha']);
  var msg = st === 'ok' ? 'Dentro del rango del pastoreo extensivo.' : st === 'baja'
    ? 'Por debajo del mínimo: faltan ' + H.num(lo * ha - ugm, 2) + ' UGM o sobran ' + H.num(ha - ugm / lo, 2) + ' ha.'
    : 'Por encima del máximo: sobran ' + H.num(ugm - hi * ha, 2) + ' UGM o faltan ' + H.num(ugm / hi - ha, 2) + ' ha.';
  return { label: 'Carga ganadera', big: H.num(c, 2) + ' UGM/ha', sub: H.num(ugm, 2) + ' UGM en ' + H.num(ha, ha % 1 ? 2 : 0) + ' ha · ' + msg,
    rows: rows, note: 'Tabla del anexo V del RD 1048/2022 (PAC 2023-2027). La administración calcula la carga con los animales de SITRAN durante el periodo de pastoreo.',
    n: { ugm: H.r2(ugm), c: H.r2(c), st: st } };
}
"""


def blocks(ctx):
    rows = "".join(f"<tr><td>{lab}</td><td class=\"num\">{str(u).replace('.', ',')}</td></tr>" for _, lab, u in HERD)
    return [
        ("Cómo se calcula la carga ganadera", f"""
<p>La carga ganadera es el número de <b>unidades de ganado mayor (UGM) por hectárea</b> de pasto. Cada animal se convierte a UGM
con un coeficiente: una vaca de leche o un toro de más de dos años es 1 UGM, las demás vacas y novillas 0,8, un bovino de uno a dos
años 0,7, un ternero 0,4, un caballo o un burro 0,8 y una oveja o una cabra 0,1. Se suman las UGM del rebaño y se dividen entre las
hectáreas de pastos que se aprovechan a diente.</p>
<table class="tbl"><thead><tr><th>Animal</th><th>UGM por cabeza</th></tr></thead><tbody>{rows}</tbody></table>
<p>Para cobrar el <b>ecorrégimen de pastoreo extensivo</b> de la PAC, la carga tiene que quedar entre <b>0,4 y 2 UGM/ha en pastos
húmedos</b> y entre <b>0,2 y 1,2 UGM/ha en pastos mediterráneos</b>, con al menos 120 días de pastoreo al año. La comunidad
autónoma puede bajar el mínimo a 0,2 y 0,1 UGM/ha en parques naturales, por sequía u otras causas justificadas (marca «Mínimo
reducido» en «Más opciones»).</p>"""),
        ("Ejemplo", """
<p>Una explotación de vacuno de carne con <b>40 vacas, 1 toro, 8 novillas y 30 terneros</b> sobre <b>60 ha</b> de dehesa:
40 × 0,8 + 1 × 1 + 8 × 0,8 + 30 × 0,4 = 32 + 1 + 6,4 + 12 = <b>51,4 UGM</b>. Entre 60 ha salen <b>0,86 UGM/ha</b>, dentro del rango de
pastos mediterráneos (0,2-1,2). Con 300 ovejas más, el rebaño pasaría a 81,4 UGM y 1,36 UGM/ha: por encima del máximo, harían falta
al menos 67,83 ha.</p>"""),
        ("Norma y otras tablas", f"""
<p>Los coeficientes y los rangos son los del <a href="{RD}" rel="noopener">Real Decreto 1048/2022</a> sobre pagos directos de la
PAC: la tabla de conversión a UGM está en el anexo V y los intervalos de carga del pastoreo extensivo en el artículo 30.2.b. La
administración no usa los animales que declares, sino la media de los censos de SITRAN en las fechas de control del periodo de
pastoreo, así que conviene calcular con el rebaño medio del año y no con el máximo.</p>
<p>Otras normas usan otra tabla. El <a href="{UE}" rel="noopener">Reglamento de Ejecución (UE) 808/2014</a>, que siguen muchas
ayudas agroambientales de desarrollo rural, cuenta 1 UGM los bovinos de más de dos años y los équidos de más de seis meses, 0,6 los
bovinos de seis meses a dos años, 0,4 los menores de seis meses y 0,15 las ovejas y cabras. Las ordenanzas de pastos de muchos
ayuntamientos y la normativa de nitratos tienen sus propias equivalencias: revisa la de tu convocatoria.</p>"""),
    ]


FAQ = [
    ("¿Cuántas UGM es una oveja?",
     "0,1 UGM en la PAC española (RD 1048/2022): diez ovejas o cabras equivalen a una vaca de leche. En la tabla de desarrollo rural de "
     "la UE (Reglamento 808/2014) cuentan 0,15."),
    ("¿Cuál es la carga ganadera máxima del ecorrégimen de pastoreo?",
     "2 UGM por hectárea en pastos húmedos y 1,2 UGM/ha en pastos mediterráneos. Los mínimos son 0,4 y 0,2 UGM/ha."),
    ("¿Cuántas UGM es un caballo?",
     "0,8 UGM en la tabla de la PAC, sea caballo, yegua, burro o mulo. En el Reglamento (UE) 808/2014, 1 UGM si tiene más de seis meses."),
    ("¿Cuántas vacas puedo tener por hectárea?",
     "Depende del pasto. Para el ecorrégimen, en pastos mediterráneos hasta 1,2 UGM/ha: 1,5 vacas de carne (0,8 UGM) por hectárea. Lo que "
     "aguanta tu pasto sin degradarse puede ser bastante menos: depende de la lluvia y de la producción de hierba de cada año."),
    ("¿Con qué animales calcula la carga la administración?",
     "Con los que figuran en SITRAN para tu explotación en las fechas de control del periodo de pastoreo, no con los que declares. Si "
     "solo vas a pastorear con parte del rebaño, se indica en la solicitud única."),
]

TOOL = {
    "slug": "carga-ganadera",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "fence",
    "order": 50,
    "name": "Carga ganadera",
    "k": "ugm unidades ganado mayor hectarea pac ecorregimen pastoreo extensivo vacas ovejas",
    "title": "Calculadora de carga ganadera: UGM por hectárea (PAC)",
    "desc": "Calcula las UGM de tu rebaño con la tabla de la PAC (RD 1048/2022) y la carga por hectárea frente al ecorrégimen de pastoreo extensivo.",
    "h1": "Calculadora de carga ganadera",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ha", "type": "number", "label": "Pastos", "value": 50, "unit": "ha", "step": "0.01", "w": "s"},
        {"id": "pasto", "type": "seg", "label": "Tipo", "value": "m", "options": [("m", "Mediterráneo"), ("h", "Húmedo")]},
    ] + [{"id": i, "type": "number", "label": lab, "value": 300 if i == "ovi" else "", "unit": "cab.", "w": "s",
          **({"more": True} if i in ("cerdas", "cerdos", "lechones") else {})} for i, lab, _ in HERD]
      + [{"id": "red", "type": "check", "label": "Mínimo reducido", "value": False, "more": True}],
    "js": JS,
    "data": {"K": [[i, lab, u] for i, lab, u in HERD]},
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Real Decreto 1048/2022, art. 30 y anexo V (BOE-A-2022-23048)", RD),
                ("Reglamento de Ejecución (UE) 808/2014, anexo II", UE)],
    "related": ["medidas-agrarias", "gestacion-animal", "abonado-npk"],
    "tests": [
        ({}, {"n.ugm": 30, "n.c": 0.6, "n.st": "ok"}),
        ({"ovi": "", "vcarne": "40", "toros": "1", "novillas": "8", "bov01": "30", "ha": "60"}, {"n.ugm": 51.4, "n.c": 0.86, "n.st": "ok"}),
        ({"ovi": "", "vleche": "100", "ha": "40", "pasto": "h"}, {"n.c": 2.5, "n.st": "alta"}),
        ({"ovi": "50", "ha": "40"}, {"n.c": 0.13, "n.st": "baja"}),
        ({"ovi": "50", "ha": "40", "red": True}, {"n.st": "ok"}),
        ({"ha": "0"}, {"err": "Escribe la superficie de pastos en hectáreas."}),
        ({"ovi": ""}, {"err": "Escribe cuántos animales tienes."}),
    ],
}
