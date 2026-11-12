"""Hormigón y mortero: cement, sand, gravel and water for a slab, post holes or a given volume, by volumetric mix
(1:2:4, 1:3 ...). English twin: concrete_calculator.py (same JS, plus US premix bags)."""
import math

from herramientas.tools import _bricolaje as F

CTE_SEAE = "https://www.codigotecnico.org/pdf/Documentos/SE/DBSE-AE.pdf"
COD_EST = "https://www.boe.es/buscar/act.php?id=BOE-A-2021-13681"

DRY = {"hor": 1.54, "mor": 1.33}     # dry volume of loose materials per m3 of wet mix (bulking + voids)
DEN = {"c": 1440, "s": 1600, "g": 1600}  # kg/m3, loose: cement (volume batching convention), sand, gravel (CTE DB SE-AE C.6)
WC = {"hor": 0.5, "mor": 0.7}         # water / cement by weight (indicative: depends on the moisture of the sand)

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var us = EN && v.u === 'us';
  var T = EN ? { dims: 'Enter length, width and thickness.', hole: 'Enter diameter, depth and number of holes.', vol: 'Enter the volume.',
      v: 'Volume', vw: 'With spare', c: 'Cement', s: 'Sand', g: 'Gravel', w: 'Water', bags: ' bags', bag1: ' bag', pre: 'Premix bags',
      lc: 'Concrete', lm: 'Mortar', t: ' t' }
    : { dims: 'Escribe largo, ancho y espesor.', hole: 'Escribe diámetro, profundidad y número de hoyos.', vol: 'Escribe el volumen.',
      v: 'Volumen', vw: 'Con margen', c: 'Cemento', s: 'Arena', g: 'Grava', w: 'Agua', bags: ' sacos', bag1: ' saco', pre: '',
      lc: 'Hormigón', lm: 'Mortero', t: ' t' };
  var D = C.d, FT3 = 0.0283168;
  var vol;
  if (v.forma === 'losa') {
    if (!(v.l > 0 && v.a > 0 && v.e > 0)) return { err: T.dims };
    vol = us ? v.l * v.a * v.e / 12 * FT3 : v.l * v.a * v.e / 100;
  } else if (v.forma === 'hoyo') {
    var nh = Math.floor(v.nh);
    if (!(v.d > 0 && v.p > 0 && nh > 0)) return { err: T.hole };
    var dm = us ? v.d * 0.0254 : v.d / 100, pm = us ? v.p * 0.0254 : v.p / 100;
    vol = Math.PI * dm * dm / 4 * pm * nh;
  } else {
    if (!(v.vol > 0)) return { err: T.vol };
    vol = us ? v.vol * 0.764555 : v.vol;
  }
  var mg = v.merma > 0 ? v.merma : 0, V = vol * (1 + mg / 100);
  var kind = v.obj === 'mor' ? 'mor' : 'hor';
  var mix = (kind === 'mor' ? v.mm : v.mh).split(':').map(Number), sum = mix.reduce(function (a, b) { return a + b; }, 0);
  var dry = V * D.dry[kind];
  var cem = dry * mix[0] / sum * D.den.c, sand = dry * mix[1] / sum, grav = mix.length > 2 ? dry * mix[2] / sum : 0;
  var water = cem * D.wc[kind];
  var bagL = us ? (+v.sacus || 94) + ' lb' : (+v.saco || 25) + ' kg', bag = us ? (+v.sacus || 94) * 0.453592 : (+v.saco || 25);
  var nb = Math.ceil(cem / bag - 1e-9);
  function vv(m3) { return us ? fx(m3 / FT3, 1) + ' ft³ · ' + fx(m3 / 0.764555, 2) + ' yd³' : fx(m3, 3) + ' m³'; }
  function mass(m3, den) { var kg = m3 * den; return us ? fx(kg * 2.20462 / 2000, 2) + ' tons (' + fx(kg * 2.20462, 0) + ' lb)' : fx(kg / 1000, 2) + T.t + ' (' + fx(kg, 0) + ' kg)'; }
  var rows = [[T.v, vv(vol)]];
  if (mg) rows.push([T.vw, vv(V), 'sub']);
  rows.push([T.c, (us ? fx(cem * 2.20462, 0) + ' lb' : fx(cem, 0) + ' kg') + ' · ' + nb + (nb === 1 ? T.bag1 : T.bags) + ' ' + bagL, 'tot']);
  rows.push([T.s, vv(sand) + ' · ' + mass(sand, D.den.s)]);
  if (grav) rows.push([T.g, vv(grav) + ' · ' + mass(grav, D.den.g)]);
  rows.push([T.w, us ? fx(water * 0.264172, 0) + ' gal' : fx(water, 0) + ' L']);
  var pre = null;
  if (us && kind === 'hor') {
    var y = { '80': 0.6, '60': 0.45, '40': 0.3 }, ft3 = V / FT3;
    pre = ['80', '60', '40'].map(function (k) { return Math.ceil(ft3 / y[k] - 1e-9) + ' × ' + k + ' lb'; }).join(' · ');
    rows.push([T.pre, pre]);
  }
  return {
    label: kind === 'mor' ? T.lm : T.lc, big: us ? fx(V / 0.764555, 2) + ' yd³' : fx(V, 2) + ' m³',
    sub: mix.join(':') + ' · ' + nb + (nb === 1 ? T.bag1 : T.bags) + ' ' + bagL,
    rows: rows,
    n: { vol: r(V, 4), cem: r(cem, 1), bags: nb, sand: r(sand, 4), grav: r(grav, 4), water: r(water, 1) }
  };
}
"""

DATA = {"dry": DRY, "den": DEN, "wc": WC}


def mix(vol, ratio, kind, waste=5):
    """Python twin: cement kg, sand m3, gravel m3, water L for vol m3 (waste %)."""
    V = vol * (1 + waste / 100)
    parts = [float(x) for x in ratio.split(":")]
    s = sum(parts)
    dry = V * DRY[kind]
    cem = dry * parts[0] / s * DEN["c"]
    return cem, dry * parts[1] / s, (dry * parts[2] / s if len(parts) > 2 else 0), cem * WC[kind]


def blocks(ctx):
    n = F.n
    cem, sand, grav, w = mix(0.6, "1:2:4", "hor")
    rows = "".join(f"<tr><td>{r}</td><td>{use}</td><td class=num>{n(mix(1, r, k, 0)[0], 0)} kg</td>"
                   f"<td class=num>{n(mix(1, r, k, 0)[1], 2)} m³</td><td class=num>{n(mix(1, r, k, 0)[2], 2) + ' m³' if k == 'hor' else '—'}</td></tr>"
                   for r, use, k in [("1:2:3", "hormigón de uso general, pequeñas losas", "hor"), ("1:2:4", "soleras, aceras, bases", "hor"),
                                     ("1:3:6", "hormigón de limpieza y rellenos", "hor"), ("1:3", "enfoscados y morteros impermeables", "mor"),
                                     ("1:4", "solados y fábrica de ladrillo", "mor"), ("1:6", "tabiques y rellenos", "mor")])
    return [
        ("Cuánto cemento, arena y grava por metro cúbico", f"""
<p>Para una solera de 3 × 2 m y 10 cm de espesor hacen falta 0,6 m³ de hormigón, 0,63 m³ con un 5 % de margen. Con la
dosificación 1:2:4 (una parte de cemento, dos de arena y cuatro de grava, medidas en volumen) son <b>{n(cem, 0)} kg de
cemento</b>, es decir, {math.ceil(cem / 25)} sacos de 25 kg, {n(sand, 2)} m³ de arena ({n(sand * 1.6, 2)} t),
{n(grav, 2)} m³ de grava ({n(grav * 1.6, 2)} t) y unos {n(w, 0)} litros de agua.</p>
<table class="tbl"><thead><tr><th>Mezcla</th><th>Uso</th><th>Cemento</th><th>Arena</th><th>Grava</th></tr></thead><tbody>{rows}</tbody></table>
<p class="hnote">Cantidades para 1 m³ de hormigón o mortero ya amasado, sin margen.</p>"""),
        ("Cómo se calcula", """
<p>Al mezclar, la arena rellena los huecos de la grava y el cemento los de la arena, así que el volumen final es bastante
menor que la suma de los materiales sueltos. Por eso se parte del <b>volumen seco</b>: 1,54 m³ de materiales por cada m³ de
hormigón y 1,33 m³ por cada m³ de mortero, un método clásico de dosificación por volumen. Ese volumen se reparte según la
proporción: en 1:2:4 el cemento es 1/7, la arena 2/7 y la grava 4/7.</p>
<p>Los volúmenes se pasan a peso con la densidad aparente de cada material suelto: 1.440 kg/m³ para el cemento medido a
granel y 1.600 kg/m³ para la arena y la grava, dentro de los intervalos que da el Código Técnico (DB SE-AE, tabla C.6:
arena de 14 a 19 kN/m³, arena y grava de 15 a 20 kN/m³). El agua es orientativa, una relación agua/cemento de 0,5 en
hormigón y de 0,7 en mortero: si la arena está mojada hará falta menos. Echa el agua poco a poco hasta que la masa tenga
consistencia plástica, sin charcos, porque el exceso de agua resta resistencia.</p>"""),
        ("Para qué sirve y para qué no", """
<p>Estas mezclas hechas en obra sirven para soleras de casetas y trasteros, aceras, bases de barbacoa, recibir postes y
reparaciones. Para elementos estructurales (zapatas, muros de carga, forjados, vigas o pilares) el Código Estructural exige
un hormigón con resistencia y durabilidad definidas en el proyecto, como HM-20 o HA-25, que normalmente se pide a una planta
de hormigón preparado y se controla en obra. Una dosificación por volumen no garantiza esa resistencia.</p>
<p>Para recibir postes de valla, usa el modo «Hoyos»: un hoyo de 30 cm de diámetro y 60 cm de profundidad lleva 42 litros
de hormigón, algo menos si descuentas el poste.</p>"""),
    ]


FAQ = [
    ("¿Cuántos sacos de cemento lleva un metro cúbico de hormigón?",
     "Con dosificación 1:2:4, unos 317 kg: 13 sacos de 25 kg. Con 1:2:3, unos 370 kg (15 sacos). Para mortero 1:4, unos 383 kg."),
    ("¿Cuánta arena y grava hace falta para un m³ de hormigón?",
     "Con 1:2:4, unos 0,44 m³ de arena y 0,88 m³ de grava, aproximadamente 0,7 y 1,4 toneladas."),
    ("¿Qué diferencia hay entre hormigón y mortero?",
     "El mortero es cemento, arena y agua; el hormigón añade grava. El mortero se usa para pegar ladrillos, enfoscar y solar; "
     "el hormigón para soleras, cimientos y piezas que deben aguantar peso."),
    ("¿Qué espesor necesita una solera?",
     "Unos 10 cm para pisar o para una caseta ligera, 12 a 15 cm si van a pasar coches, siempre sobre una base de grava compactada."),
    ("¿Cuánta agua se le echa a un saco de cemento?",
     "En hormigón, unos 12 litros por saco de 25 kg (relación 0,5). Depende de lo húmeda que esté la arena: ajusta hasta una masa plástica."),
]

TOOL = {
    "slug": "hormigon-mortero",
    "lang": "es",
    "twin": "concrete-calculator",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "bucket",
    "order": 30,
    "name": "Hormigón y mortero",
    "k": "dosificación cemento arena grava sacos m3 solera losa postes agua 1:2:4 1:3",
    "title": "Calcular hormigón y mortero: cemento, arena y grava",
    "desc": "Calcula los sacos de cemento, la arena, la grava y el agua para una solera, hoyos de postes o un volumen, según la dosificación.",
    "h1": "Calculadora de hormigón y mortero",
    "updated": "2026-11-12",
    "data": DATA,
    "inputs": [
        {"id": "obj", "type": "seg", "label": "Material", "value": "hor", "options": [("hor", "Hormigón"), ("mor", "Mortero")]},
        {"id": "forma", "type": "seg", "label": "Medir", "value": "losa", "options": [("losa", "Losa"), ("hoyo", "Hoyos"), ("vol", "m³")]},
        {"id": "l", "type": "number", "label": "Largo", "value": "3", "unit": "m", "step": "0.01", "show": ("forma", ["losa"])},
        {"id": "a", "type": "number", "label": "Ancho", "value": "2", "unit": "m", "step": "0.01", "show": ("forma", ["losa"])},
        {"id": "e", "type": "number", "label": "Espesor", "value": "10", "unit": "cm", "step": "0.5", "show": ("forma", ["losa"])},
        {"id": "d", "type": "number", "label": "Diámetro", "value": "30", "unit": "cm", "show": ("forma", ["hoyo"])},
        {"id": "p", "type": "number", "label": "Profundidad", "value": "60", "unit": "cm", "show": ("forma", ["hoyo"])},
        {"id": "nh", "type": "number", "label": "Hoyos", "value": "4", "w": "s", "show": ("forma", ["hoyo"])},
        {"id": "vol", "type": "number", "label": "Volumen", "value": "1", "unit": "m³", "step": "0.01", "show": ("forma", ["vol"])},
        {"id": "mh", "type": "select", "label": "Mezcla", "value": "1:2:4", "show": ("obj", ["hor"]),
         "options": [("1:2:3", "1:2:3 · general"), ("1:2:4", "1:2:4 · soleras"), ("1:3:6", "1:3:6 · limpieza")]},
        {"id": "mm", "type": "select", "label": "Mezcla", "value": "1:4", "show": ("obj", ["mor"]),
         "options": [("1:3", "1:3 · enfoscado"), ("1:4", "1:4 · ladrillo"), ("1:5", "1:5 · tabique"), ("1:6", "1:6 · relleno")]},
        {"id": "saco", "type": "seg", "label": "Saco", "value": "25", "options": [("25", "25 kg"), ("35", "35 kg")], "more": True},
        {"id": "merma", "type": "number", "label": "Margen", "value": "5", "unit": "%", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("CTE · DB SE-AE, anejo C, tabla C.6 (peso específico de materiales a granel)", CTE_SEAE),
                ("Real Decreto 470/2021, Código Estructural (BOE)", COD_EST)],
    "related": ["calculadora-cesped-grava", "calculadora-azulejos", "escalera-huella-contrahuella", "calculadora-pintura"],
    "tests": [
        ({}, {"n.vol": 0.63, "n.cem": 199.6, "n.bags": 8, "n.sand": 0.2772, "n.grav": 0.5544, "n.water": 99.8}),
        ({"forma": "vol", "vol": "1", "merma": "0", "mh": "1:2:3"}, {"n.cem": 369.6, "n.bags": 15}),
        ({"obj": "mor", "forma": "vol", "vol": "1", "merma": "0"}, {"n.cem": 383.0, "n.grav": 0, "n.water": 268.1}),
        ({"forma": "hoyo", "nh": "1", "merma": "0"}, {"n.vol": 0.0424}),
        ({"e": ""}, {"err": "Escribe largo, ancho y espesor."}),
        ({"forma": "hoyo", "nh": "0"}, {"err": "Escribe diámetro, profundidad y número de hoyos."}),
    ],
}
