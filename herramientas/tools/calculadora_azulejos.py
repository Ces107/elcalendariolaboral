"""Calculadora de azulejos: tiles and boxes for a floor or wall, with joint width and waste, plus grout and tile adhesive.
English twin: tile_calculator.py (same JS, feet/inches or metres/centimetres, no adhesive line)."""
import math

from herramientas.tools import _bricolaje as F

CTE_SUA = "https://www.codigotecnico.org/pdf/Documentos/SUA/DBSUA.pdf"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var us = EN && v.u === 'us';
  var T = EN ? { dims: 'Enter the length and width of the area.', neg: 'The area to leave out is larger than the area.', tile: 'Enter the tile size.',
      area: 'Area', tile2: 'Tile + joint', raw: 'Tiles, no waste', w: 'Waste', pcs: 'Tiles to buy', boxes: 'Boxes', got: 'Area bought',
      grout: 'Grout', glue: 'Adhesive', label: 'Tiles', bx: ' boxes', bx1: ' box', pc: ' tiles' }
    : { dims: 'Escribe el largo y el ancho de la superficie.', neg: 'Lo que descuentas es mayor que la superficie.', tile: 'Escribe la medida de la pieza.',
      area: 'Superficie', tile2: 'Pieza + junta', raw: 'Piezas sin merma', w: 'Merma', pcs: 'Piezas a comprar', boxes: 'Cajas', got: 'm² comprados',
      grout: 'Material de rejuntado', glue: 'Cemento cola', label: 'Azulejos', bx: ' cajas', bx1: ' caja', pc: ' piezas' };
  var A2 = us ? 'sq ft' : 'm²';
  if (!(v.l > 0 && v.a > 0)) return { err: T.dims };
  var off = v.resta > 0 ? v.resta : 0, area = v.l * v.a - off;
  if (area <= 0) return { err: T.neg };
  var tl, tw, j, th;
  if (us) { tl = v.plin * 0.0254; tw = v.pain * 0.0254; j = (+v.jin || 0) * 0.0254; th = (+v.espin || 0) * 0.0254; }
  else { tl = v.pl / 100; tw = v.pa / 100; j = v.junta > 0 ? v.junta / 1000 : 0; th = v.esp > 0 ? v.esp / 1000 : 0; }
  if (!(tl > 0 && tw > 0)) return { err: T.tile };
  var aM = us ? area * 0.09290304 : area;
  var cell = (tl + j) * (tw + j), raw = aM / cell, m = +v.merma || 0;
  var pcs = Math.ceil(raw * (1 + m / 100) - 1e-9);
  var box = v.caja > 0 ? Math.floor(v.caja) : 0, boxes = box ? Math.ceil(pcs / box) : 0;
  var boughtM = (box ? boxes * box : pcs) * tl * tw, bought = us ? boughtM / 0.09290304 : boughtM;
  var A = tl * 1000, B = tw * 1000, grout = j > 0 && th > 0 ? (A + B) / (A * B) * th * 1000 * j * 1000 * 1.6 * aM : 0;
  function tsz() { return us ? fv(v.plin, 2) + ' × ' + fv(v.pain, 2) + ' in' : fv(v.pl, 1) + ' × ' + fv(v.pa, 1) + ' cm'; }
  var rows = [[T.area, fv(area, 2) + ' ' + A2], [T.tile2, tsz() + ' + ' + (us ? ({ '0.0625': '1/16', '0.125': '1/8', '0.1875': '3/16', '0.25': '1/4' }[v.jin] || v.jin) + ' in' : fv(j * 1000, 1) + ' mm')],
    [T.raw, fx(raw, 1)], [T.w, '+' + m + (EN ? '%' : ' %'), 'sub'], [T.pcs, String(pcs), 'tot']];
  if (box) rows.push([T.boxes, boxes + ' × ' + box + ' = ' + boxes * box + T.pc, 'tot']);
  rows.push([T.got, fv(bought, 2) + ' ' + A2]);
  if (grout) rows.push([T.grout, us ? fx(grout * 2.20462, 1) + ' lb' : fx(grout, 1) + ' kg']);
  var glue = 0;
  if (!EN && v.cola > 0) { glue = v.cola * aM; var nb = Math.ceil(glue / 25 - 1e-9); rows.push([T.glue, fx(glue, 0) + ' kg · ' + nb + (nb === 1 ? ' saco' : ' sacos') + ' de 25 kg']); }
  return {
    label: T.label, big: box ? boxes + (boxes === 1 ? T.bx1 : T.bx) : pcs + T.pc,
    sub: pcs + T.pc + ' · ' + fv(area, 2) + ' ' + A2 + ' + ' + m + (EN ? '%' : ' %'),
    rows: rows,
    n: { pcs: pcs, boxes: boxes, raw: r(raw, 3), grout: r(grout, 3), glue: r(glue, 2) }
  };
}
"""


def tiles(area, l_cm, w_cm, j_mm, waste, box):
    cell = (l_cm / 100 + j_mm / 1000) * (w_cm / 100 + j_mm / 1000)
    raw = area / cell
    pcs = math.ceil(raw * (1 + waste / 100) - 1e-9)
    return raw, pcs, math.ceil(pcs / box)


def grout(area, l_cm, w_cm, th_mm, j_mm):
    a, b = l_cm * 10, w_cm * 10
    return (a + b) / (a * b) * th_mm * j_mm * 1.6 * area


def blocks(ctx):
    n = F.n
    raw, pcs, bx = tiles(6, 60, 30, 2, 10, 8)
    raw2, pcs2, bx2 = tiles(14, 60, 60, 2, 10, 4)
    g = grout(6, 60, 30, 9, 2)
    return [
        ("Cuántos azulejos necesito", f"""
<p>Divide la superficie entre lo que ocupa cada pieza <b>con su junta</b>, suma la merma y redondea a cajas completas. Para el
suelo de un baño de 3 × 2 m (6 m²) con porcelánico de 30 × 60 cm y juntas de 2 mm caben {n(raw, 1)} piezas; con un 10 % de
merma hay que comprar <b>{pcs} piezas</b>, que en cajas de 8 son <b>{bx} cajas</b> (7,2 m²).</p>
<p>Las juntas cuentan más de lo que parece en formatos pequeños: un azulejo de 20 × 20 cm con junta de 3 mm ocupa un 3 % más
de superficie que la pieza sola, así que se necesitan menos piezas de las que salen dividiendo la superficie entre 0,04 m².
En una cocina de 14 m² con 60 × 60 cm salen {n(raw2, 1)} piezas limpias, {pcs2} con la merma y {bx2} cajas de 4.</p>"""),
        ("Qué merma elegir", """
<p>La merma cubre los cortes en los bordes, las piezas que se rompen al cortar y unas pocas de reserva. Un 5 % basta en una
habitación rectangular con piezas pequeñas colocadas a junta recta. El 10 % es lo normal en casi todas las obras. Sube al
15 % si colocas en diagonal, en espiga, con piezas de gran formato (60 × 120 cm o más) o en una estancia con muchas esquinas,
pilares o bañera, porque cada corte deja un trozo que no se puede reutilizar.</p>
<p>Compra todas las cajas a la vez y comprueba que tienen el mismo <b>tono</b> y <b>calibre</b> impresos en el cartón: dos
lotes distintos pueden diferir en color o en un milímetro de medida, y se nota. Guarda dos o tres piezas sobrantes para
reparar una rotura años después, cuando el modelo ya no se fabrique.</p>"""),
        ("Juntas, rejuntado y cemento cola", f"""
<p>No existe la junta cero: incluso el porcelánico rectificado necesita al menos 1,5 o 2 mm, y en exteriores o con
calefacción por suelo radiante conviene 3 mm o más, además de dejar juntas perimetrales junto a las paredes. El material
de rejuntado se calcula con la longitud de juntas por metro cuadrado: (largo + ancho) ÷ (largo × ancho) de la pieza en mm,
por el grosor de la pieza y el ancho de la junta en mm, por 1,6 kg/dm³ de densidad del mortero. Para el baño del ejemplo,
con piezas de 9 mm, salen {n(g, 2)} kg.</p>
<p>El cemento cola depende de la llana: con una llana dentada de 6 mm se gastan unos 3 kg/m², con una de 10 mm entre 4 y
5 kg/m², y en piezas grandes con doble encolado (cola en la pared y en la pieza) 1 o 2 kg/m² más. Ajusta la cifra en «Más
opciones» con la ficha técnica de tu adhesivo.</p>"""),
        ("Suelos antideslizantes: la clase que pide el CTE", """
<p>El Código Técnico de la Edificación (DB-SUA 1) clasifica los suelos por su resistencia al deslizamiento Rd: clase 1 entre
15 y 35, clase 2 entre 35 y 45 y clase 3 por encima de 45. En edificios de uso público exige clase 1 en zonas interiores
secas, clase 2 en zonas húmedas como baños, cocinas o entradas desde la calle (clase 3 si hay pendiente o escaleras) y
clase 3 en exteriores, piscinas y duchas. En una vivienda no es obligatorio, pero es la mejor referencia para elegir el
suelo del baño o de la terraza.</p>"""),
    ]


FAQ = [
    ("¿Cuántos azulejos de 30 × 60 entran en un metro cuadrado?",
     "5,56 piezas sin junta. Con junta de 2 mm, unas 5,5. En la práctica se compran por cajas, que en este formato suelen traer "
     "8 piezas (1,44 m²)."),
    ("¿Cuánto porcentaje de merma hay que añadir?",
     "Un 10 % en una colocación recta normal, un 5 % en habitaciones muy regulares con pieza pequeña y un 15 % en diagonal, "
     "espiga o gran formato."),
    ("¿Se descuentan las puertas y la bañera?",
     "Lo que no se alicata, sí: escríbelo en «Descontar» (Más opciones). El plato de ducha o la bañera se restan del suelo; "
     "en las paredes, resta puertas y ventanas."),
    ("¿Qué ancho de junta pongo?",
     "Entre 1,5 y 3 mm en porcelánico rectificado de interior, 3 a 5 mm en piezas no rectificadas o rústicas y en exteriores. "
     "El fabricante indica la mínima en la caja o la ficha."),
    ("¿Cuánto material de rejuntado necesito?",
     "Poco: para piezas de 30 × 60 cm con junta de 2 mm, unos 0,14 kg por m². Con piezas pequeñas y juntas anchas el consumo "
     "se multiplica, por eso la calculadora lo calcula con tus medidas."),
]

PRESETS = [
    ("20x20", "20 × 20 cm", {"pl": "20", "pa": "20", "caja": "25"}),
    ("30x30", "30 × 30 cm", {"pl": "30", "pa": "30", "caja": "11"}),
    ("30x60", "30 × 60 cm", {"pl": "60", "pa": "30", "caja": "8"}),
    ("45x45", "45 × 45 cm", {"pl": "45", "pa": "45", "caja": "7"}),
    ("60x60", "60 × 60 cm", {"pl": "60", "pa": "60", "caja": "4"}),
    ("60x120", "60 × 120 cm", {"pl": "120", "pa": "60", "caja": "2"}),
    ("20x120", "20 × 120 cm (madera)", {"pl": "120", "pa": "20", "caja": "5"}),
    ("otro", "Otra medida"),
]

TOOL = {
    "slug": "calculadora-azulejos",
    "lang": "es",
    "twin": "tile-calculator",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "layout-grid",
    "order": 20,
    "name": "Calculadora de azulejos",
    "k": "baldosas porcelánico cajas m2 juntas merma alicatar solar suelo pared rejuntado cemento cola",
    "title": "Calculadora de azulejos: piezas y cajas con juntas",
    "desc": "Calcula cuántos azulejos o baldosas necesitas con la junta y la merma, cuántas cajas comprar y el rejuntado y cemento cola.",
    "h1": "Calculadora de azulejos y baldosas",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "l", "type": "number", "label": "Largo", "value": "3", "unit": "m", "step": "0.01"},
        {"id": "a", "type": "number", "label": "Ancho", "value": "2", "unit": "m", "step": "0.01"},
        {"id": "fmt", "type": "select", "label": "Pieza", "value": "30x60", "options": PRESETS, "custom": "otro"},
        {"id": "pl", "type": "number", "label": "Largo pieza", "value": "60", "unit": "cm", "step": "0.1", "w": "s"},
        {"id": "pa", "type": "number", "label": "Ancho pieza", "value": "30", "unit": "cm", "step": "0.1", "w": "s"},
        {"id": "junta", "type": "number", "label": "Junta", "value": "2", "unit": "mm", "step": "0.5", "w": "s"},
        {"id": "merma", "type": "seg", "label": "Merma", "value": "10", "options": [("5", "5 %"), ("10", "10 %"), ("15", "15 %")]},
        {"id": "caja", "type": "number", "label": "Piezas/caja", "value": "8", "w": "s"},
        {"id": "resta", "type": "number", "label": "Descontar", "value": "0", "unit": "m²", "step": "0.01", "more": True},
        {"id": "esp", "type": "number", "label": "Grosor pieza", "value": "9", "unit": "mm", "w": "s", "more": True},
        {"id": "cola", "type": "number", "label": "Cemento cola", "value": "4", "unit": "kg/m²", "step": "0.1", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("CTE · Documento Básico SUA, sección SUA 1 (resbaladicidad de los suelos)", CTE_SUA)],
    "related": ["calculadora-tarima-suelo", "calculadora-pintura", "hormigon-mortero", "papel-pintado"],
    "tests": [
        ({}, {"n.pcs": 37, "n.boxes": 5, "n.grout": 0.864, "n.glue": 24}),
        ({"l": "4", "a": "3,5", "pl": "60", "pa": "60", "caja": "4"}, {"n.pcs": 43, "n.boxes": 11}),
        ({"merma": "15"}, {"n.pcs": 38}),
        ({"junta": "0"}, {"n.pcs": 37, "n.grout": 0}),
        ({"l": ""}, {"err": "Escribe el largo y el ancho de la superficie."}),
        ({"resta": "7"}, {"err": "Lo que descuentas es mayor que la superficie."}),
    ],
}
