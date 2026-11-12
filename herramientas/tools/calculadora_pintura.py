"""Calculadora de pintura: litres for a room (walls minus doors and windows, optional ceiling) or a given area, by coats,
coverage on the tin and surface type, plus the cheapest set of tins. English twin: paint_calculator.py (same JS)."""
from herramientas.tools import _bricolaje as F

ECOLABEL = "https://eur-lex.europa.eu/eli/dec/2014/312/oj?locale=es"
ECOLABEL_EN = "https://eur-lex.europa.eu/eli/dec/2014/312/oj?locale=en"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  %PACKS%
  var us = EN && v.u === 'us';
  var A2 = us ? 'sq ft' : 'm²', VOL = us ? 'gal' : 'L';
  var T = EN ? { dims: 'Enter length, width and height.', area: 'Enter the area to paint.', cov: 'Enter the coverage per coat.',
      neg: 'Doors and windows take up the whole wall.', walls: 'Walls', ceil: 'Ceiling', holes: 'Doors and windows', net: 'Area to paint',
      f: 'Surface allowance', per: 'Paint per coat', mg: 'Spare', tot: 'Total', buy: 'Buy', coats: ' coats', coat: ' coat', label: 'Paint needed' }
    : { dims: 'Escribe largo, ancho y alto.', area: 'Escribe los m² que vas a pintar.', cov: 'Escribe el rendimiento por capa.',
      neg: 'Las puertas y ventanas ocupan toda la pared.', walls: 'Paredes', ceil: 'Techo', holes: 'Puertas y ventanas', net: 'Superficie a pintar',
      f: 'Ajuste por superficie', per: 'Pintura por capa', mg: 'Margen', tot: 'Total', buy: 'Comprar', coats: ' capas', coat: ' capa', label: 'Pintura necesaria' };
  var area, walls = 0, ceil = 0, holes = 0;
  if (v.modo === 'hab') {
    if (!(v.l > 0 && v.a > 0 && v.h > 0)) return { err: T.dims };
    walls = 2 * (v.l + v.a) * v.h;
    ceil = v.techo ? v.l * v.a : 0;
    var nd = v.puertas > 0 ? Math.floor(v.puertas) : 0, nw = v.ventanas > 0 ? Math.floor(v.ventanas) : 0;
    holes = nd * (us ? 20 : 1.6) + nw * (us ? 15 : 1.5);
    if (holes >= walls) return { err: T.neg };
    area = walls - holes + ceil;
  } else {
    if (!(v.m2 > 0)) return { err: T.area };
    area = v.m2;
  }
  var cov = us ? v.covus : v.rend;
  if (!(cov > 0)) return { err: T.cov };
  var coats = Math.max(1, Math.floor(+v.capas || 1)), f = +v.sup || 1, mg = v.margen > 0 ? v.margen : 0;
  var per = area * f / cov, total = per * coats * (1 + mg / 100);
  var sizes = us ? [5, 1, 0.25] : EN ? [10, 5, 2.5, 1] : [15, 4, 0.75];
  var p = packs(r(total, 3), sizes);
  function tin(s) { return us ? (s === 0.25 ? '1 qt' : s + ' gal') : fv(s) + ' L'; }
  var buy = p.list.map(function (x) { return x[1] + ' × ' + tin(x[0]); }).join(' + ');
  var rows = [];
  if (v.modo === 'hab') {
    rows.push([T.walls, fv(walls, 1) + ' ' + A2]);
    if (holes) rows.push([T.holes, '−' + fv(holes, 1) + ' ' + A2, 'sub']);
    if (ceil) rows.push([T.ceil, fv(ceil, 1) + ' ' + A2]);
  }
  rows.push([T.net, fv(area, 1) + ' ' + A2]);
  if (f !== 1) rows.push([T.f, '+' + fv((f - 1) * 100, 0) + (EN ? '%' : ' %'), 'sub']);
  rows.push([T.per, fx(per, 2) + ' ' + VOL]);
  if (mg) rows.push([T.mg, '+' + fv(mg, 1) + (EN ? '%' : ' %'), 'sub']);
  rows.push([T.tot, fx(total, 2) + ' ' + VOL, 'tot']);
  rows.push([T.buy, buy + ' = ' + fv(p.total, 2) + ' ' + VOL]);
  return {
    label: T.label, big: fx(total, 1) + ' ' + VOL,
    sub: fv(area, 1) + ' ' + A2 + ' × ' + coats + (coats > 1 ? T.coats : T.coat) + ' ÷ ' + fv(cov, 1) + ' ' + A2 + '/' + VOL,
    rows: rows,
    n: { area: r(area, 3), litres: r(total, 3), buy: r(p.total, 3) }
  };
}
"""


def example():
    walls = 2 * (4 + 3) * 2.5
    area = walls - 1.6 - 1.5
    tot = area * 2 / 10 * 1.1
    area_t = area + 12
    tot_t = area_t * 2 / 10 * 1.1
    return walls, area, tot, area_t, tot_t


def blocks(ctx):
    n = F.n
    walls, area, tot, area_t, tot_t = example()
    buy_t = " + ".join(f"{c} × {n(s, 2).rstrip('0').rstrip(',')} L" for s, c in F.packs(round(tot_t, 3), [15, 4, 0.75]))
    return [
        ("Cuántos litros de pintura necesitas", f"""
<p>Multiplica los metros cuadrados que vas a pintar por el número de capas y divide entre el rendimiento que indica el
envase. Para un dormitorio de 4 × 3 metros con 2,5 m de altura, una puerta y una ventana, salen {n(area, 1)} m² de pared:
a dos manos y con una pintura plástica de 10 m²/L hacen falta unos <b>{n(area * 2 / 10, 1)} litros</b>, {n(tot, 1)} con un
10 % de margen. Lo práctico es comprar dos botes de 4 litros.</p>
<p>La superficie de las paredes es el perímetro de la habitación por la altura: (4 + 3) × 2 × 2,5 = {n(walls, 0)} m². A eso
se le restan los huecos grandes. La calculadora descuenta 1,6 m² por puerta (una puerta normal mide unos 0,8 × 2 m) y 1,5 m²
por ventana; si tus ventanas son mucho mayores, usa el modo «Metros²» con la medida real. Los huecos pequeños, como
enchufes o rejillas, no se descuentan: el margen ya los cubre de sobra.</p>"""),
        ("Ejemplo con el techo", f"""
<p>Si en la misma habitación también pintas el techo, se suman 4 × 3 = 12 m² y quedan {n(area_t, 1)} m². Con dos capas,
10 m²/L y un 10 % de margen hacen falta {n(tot_t, 1)} litros. La combinación de envases que propone la calculadora es
<b>{buy_t}</b>: el litro suele salir más barato en los botes grandes, así que se busca la combinación más económica y no
solo la que deja menos sobrante. Si vas a pintar techo y paredes de colores distintos, calcula cada parte por separado.</p>"""),
        ("El rendimiento: lo que dice el bote y lo que pasa en la pared", """
<p>El rendimiento es la superficie que cubre un litro en <b>una</b> capa. En pintura plástica para interiores suele estar
entre 8 y 14 m²/L y viene en la ficha técnica o en la etiqueta. Como referencia, la etiqueta ecológica de la UE exige a las
pinturas blancas o claras de interior al menos 8 m²/L con un poder cubriente del 98 %, así que un bote que promete
12 m²/L es razonable, y uno que promete 20 suele hablar de condiciones ideales.</p>
<p>En la pared real se gasta más. Un yeso nuevo o una placa de yeso sin imprimar chupa pintura en la primera mano (en
«Más opciones», «Yeso nuevo» suma un 15 %), y el gotelé o las superficies rugosas tienen más superficie real que la que
mides con el metro (+30 %). Para tapar un color oscuro con uno claro suelen hacer falta tres capas, o una imprimación y dos
capas. Muchos fabricantes recomiendan diluir la primera mano con un poco de agua: eso no cambia los litros de pintura que
compras, solo cómo la aplicas.</p>"""),
        ("Consejos para no quedarte corto", """
<p>Compra toda la pintura del mismo lote si es un color mezclado en tienda: dos mezclas distintas pueden verse diferentes
en la misma pared. Guarda un poco para retoques y apunta la referencia del color. Un margen del 10 % cubre el rodillo, la
bandeja y los retoques; si pintas con pistola, sube el margen al 20 o 30 %, porque una parte se pierde en el aire.</p>"""),
    ]


FAQ = [
    ("¿Cuántos m² pinta un bote de 15 litros?",
     "Con un rendimiento de 10 m²/L, 150 m² a una capa o 75 m² a dos capas, que es más o menos un piso de 70 m² de paredes "
     "interiores de una o dos habitaciones grandes. Con 12 m²/L, 90 m² a dos manos."),
    ("¿Cuántas capas de pintura hacen falta?",
     "Dos en casi todos los casos. Una sola mano basta si repintas el mismo color sobre una pared en buen estado; tres, o "
     "imprimación más dos, si cambias de un color oscuro a uno claro o pintas yeso nuevo."),
    ("¿Se descuentan las puertas y ventanas?",
     "Sí, las grandes. La calculadora resta 1,6 m² por puerta y 1,5 m² por ventana. Los enchufes, interruptores y rejillas no "
     "se descuentan."),
    ("¿Cuánta pintura necesita el techo?",
     "Su superficie es el largo por el ancho de la habitación. Pintar el techo cuesta más y salpica, por eso conviene una "
     "pintura específica de techos, más espesa, y contar con el mismo número de capas que en las paredes."),
    ("¿Qué rendimiento pongo si no lo sé?",
     "10 m²/L es una cifra prudente para pintura plástica de interior. Las pinturas baratas suelen rendir menos y las de "
     "gama alta, entre 12 y 14 m²/L."),
]

TOOL = {
    "slug": "calculadora-pintura",
    "lang": "es",
    "twin": "paint-calculator",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "paint",
    "order": 10,
    "name": "Calculadora de pintura",
    "k": "litros pintura habitación paredes techo m2 rendimiento capas botes",
    "title": "Calculadora de pintura: cuántos litros necesito",
    "desc": "Calcula los litros de pintura para paredes y techo según los m², las capas y el rendimiento del bote, y qué envases comprar.",
    "h1": "Calculadora de pintura",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "modo", "type": "seg", "label": "Medir", "value": "hab", "options": [("hab", "Habitación"), ("m2", "Metros²")]},
        {"id": "l", "type": "number", "label": "Largo", "value": "4", "unit": "m", "step": "0.01", "show": ("modo", ["hab"])},
        {"id": "a", "type": "number", "label": "Ancho", "value": "3", "unit": "m", "step": "0.01", "show": ("modo", ["hab"])},
        {"id": "h", "type": "number", "label": "Alto", "value": "2,5", "unit": "m", "step": "0.01", "show": ("modo", ["hab"])},
        {"id": "puertas", "type": "number", "label": "Puertas", "value": "1", "w": "s", "show": ("modo", ["hab"])},
        {"id": "ventanas", "type": "number", "label": "Ventanas", "value": "1", "w": "s", "show": ("modo", ["hab"])},
        {"id": "techo", "type": "check", "label": "Techo", "value": False, "show": ("modo", ["hab"])},
        {"id": "m2", "type": "number", "label": "Superficie", "value": "30", "unit": "m²", "step": "0.1", "show": ("modo", ["m2"])},
        {"id": "capas", "type": "seg", "label": "Capas", "value": "2", "options": [("1", "1"), ("2", "2"), ("3", "3")]},
        {"id": "rend", "type": "number", "label": "Rendimiento", "value": "10", "unit": "m²/L", "step": "0.1"},
        {"id": "sup", "type": "select", "label": "Pared", "value": "1", "more": True,
         "options": [("1", "Lisa o ya pintada"), ("1.15", "Yeso nuevo (+15 %)"), ("1.3", "Rugosa o gotelé (+30 %)")]},
        {"id": "margen", "type": "number", "label": "Margen", "value": "10", "unit": "%", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Decisión (UE) 2014/312 · etiqueta ecológica de pinturas, criterio de rendimiento (EUR-Lex)", ECOLABEL)],
    "related": ["papel-pintado", "calculadora-azulejos", "calculadora-tarima-suelo", "hormigon-mortero"],
    "tests": [
        ({}, {"n.area": 31.9, "n.litres": 7.018, "n.buy": 8}),
        ({"techo": True}, {"n.area": 43.9, "n.litres": 9.658, "n.buy": 10.25}),
        ({"modo": "m2", "m2": "50", "capas": "1", "rend": "12", "margen": "0"}, {"n.litres": 4.167, "n.buy": 4.75}),
        ({"sup": "1.3", "margen": "0"}, {"n.litres": 8.294}),
        ({"l": ""}, {"err": "Escribe largo, ancho y alto."}),
        ({"l": "1", "a": "1", "h": "1", "puertas": "3"}, {"err": "Las puertas y ventanas ocupan toda la pared."}),
    ],
}
