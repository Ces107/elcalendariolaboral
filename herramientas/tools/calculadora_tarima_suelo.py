"""Tarima y suelo laminado: m2 with waste, packs, skirting board lengths and underlay rolls. English twin:
flooring_calculator.py (same JS, sq ft boxes and 8 ft baseboard)."""
import math

from herramientas.tools import _bricolaje as F

UNE56810 = "https://www.en-standard.eu/une-56810-2023-wood-flooring-installation-specifications/"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var us = EN && v.u === 'us';
  var A2 = us ? 'sq ft' : 'm²', LN = us ? 'ft' : 'm';
  var T = EN ? { dims: 'Enter the length and width of the room.', neg: 'The area left out is larger than the room.', pk: 'Enter the area per box.',
      label: 'Flooring', boxes: ' boxes', box1: ' box', area: 'Floor area', w: 'Waste', need: 'To buy', got: 'Area in the boxes', sk: 'Baseboard',
      bars: ' lengths of ', ul: 'Underlayment', rolls: ' rolls', roll1: ' roll' }
    : { dims: 'Escribe el largo y el ancho de la habitación.', neg: 'Lo que descuentas es mayor que la habitación.', pk: 'Escribe los m² de cada paquete.',
      label: 'Tarima', boxes: ' paquetes', box1: ' paquete', area: 'Superficie', w: 'Merma', need: 'A comprar', got: 'm² en los paquetes', sk: 'Rodapié',
      bars: ' barras de ', ul: 'Base aislante', rolls: ' rollos', roll1: ' rollo' };
  if (!(v.l > 0 && v.a > 0)) return { err: T.dims };
  var off = v.resta > 0 ? v.resta : 0, area = v.l * v.a - off;
  if (area <= 0) return { err: T.neg };
  if (!(v.pm2 > 0)) return { err: T.pk };
  var m = +v.merma || 0, need = area * (1 + m / 100), pk = Math.ceil(need / v.pm2 - 1e-9), got = pk * v.pm2;
  var rows = [[T.area, fv(area, 2) + ' ' + A2], [T.w, '+' + m + (EN ? '%' : ' %'), 'sub'], [T.need, fx(need, 2) + ' ' + A2],
    [EN ? 'Boxes' : 'Paquetes', pk + ' × ' + fv(v.pm2, 2) + ' ' + A2, 'tot'], [T.got, fv(got, 2) + ' ' + A2]];
  var bars = 0, skl = 0, rolls = 0;
  if (v.rod) {
    var door = us ? 2.7 : 0.8, nd = v.puertas > 0 ? Math.floor(v.puertas) : 0;
    skl = Math.max(0, 2 * (v.l + v.a) - nd * door);
    var bl = v.barra > 0 ? v.barra : (us ? 8 : 2.4);
    bars = Math.ceil(skl * 1.1 / bl - 1e-9);
    rows.push([T.sk, fv(skl, 2) + ' ' + LN + ' · ' + bars + T.bars + fv(bl, 2) + ' ' + LN]);
  }
  if (v.base) {
    var rl = v.rollo > 0 ? v.rollo : (us ? 100 : 15);
    rolls = Math.ceil(area * 1.05 / rl - 1e-9);
    rows.push([T.ul, rolls + (rolls === 1 ? T.roll1 : T.rolls) + ' × ' + fv(rl, 1) + ' ' + A2]);
  }
  return {
    label: T.label, big: pk + (pk === 1 ? T.box1 : T.boxes), sub: fv(got, 2) + ' ' + A2 + ' · ' + fv(area, 2) + ' ' + A2 + ' + ' + m + (EN ? '%' : ' %'),
    rows: rows,
    n: { area: r(area, 3), packs: pk, skirting: r(skl, 3), bars: bars, rolls: rolls }
  };
}
"""


def floor(l, a, waste, pm2, doors=1, door=0.8, bar=2.4, roll=15):
    area = l * a
    pk = math.ceil(area * (1 + waste / 100) / pm2 - 1e-9)
    sk = 2 * (l + a) - doors * door
    return area, pk, sk, math.ceil(sk * 1.1 / bar - 1e-9), math.ceil(area * 1.05 / roll - 1e-9)


def blocks(ctx):
    n = F.n
    area, pk, sk, bars, rolls = floor(5, 4, 10, 2.22)
    area2, pk2, *_ = floor(5, 4, 15, 2.22)
    return [
        ("Cuántos m² y paquetes de tarima necesito", f"""
<p>Multiplica el largo por el ancho de la habitación, suma la merma y divide entre los m² de cada paquete, redondeando hacia
arriba. Un salón de 5 × 4 m tiene {n(area)} m²; con un 10 % de merma hay que comprar {n(area * 1.1, 1)} m², que con paquetes
de 2,22 m² son <b>{pk} paquetes</b> ({n(pk * 2.22, 2)} m²). Si colocas en diagonal o en espiga, con un 15 % de merma, salen
{pk2} paquetes.</p>
<p>El rodapié se mide por el perímetro, descontando las puertas: (5 + 4) × 2 − 0,8 = {n(sk, 1)} m. Con un 10 % para los
cortes a inglete en las esquinas, son {bars} barras de 2,4 m. La base aislante (espuma, polietileno o corcho) cubre toda la
superficie: con rollos de 15 m² y un 5 % de solapes y recortes, {rolls} rollos.</p>"""),
        ("Qué merma poner", """
<p>Un 5 % basta en habitaciones rectangulares con tablas de longitud corta colocadas en recto, si aprovechas el recorte del
final de cada hilada para empezar la siguiente. El 10 % es lo prudente en casi todas las obras, con pasillos, pilares o
habitaciones irregulares. En diagonal, en espiga o en espiga húngara (punta de Hungría) sube al 15 % o más, porque cada
pieza del borde se corta en ángulo y el recorte no sirve para otra hilada.</p>
<p>Coloca las tablas en el sentido de la luz que entra por la ventana principal o de la dimensión más larga de la estancia:
las juntas se notan menos y la habitación parece mayor. Abre los paquetes y deja que el material se aclimate en la
habitación uno o dos días antes de instalarlo.</p>"""),
        ("Juntas de dilatación y rodapié", """
<p>La madera y el laminado se dilatan con la humedad, así que en un suelo flotante hay que dejar una junta perimetral de
unos 8 a 10 mm junto a las paredes, los pilares y los marcos, que luego tapa el rodapié. La norma española de colocación de
suelos de madera (UNE 56810) pide esa junta perimetral en las instalaciones flotantes y juntas de dilatación intermedias en
estancias grandes; los fabricantes de laminado las exigen a partir de unos 8 a 12 m de largo o en los pasos de puerta. Por
eso el rodapié no se clava al suelo, sino a la pared.</p>"""),
    ]


FAQ = [
    ("¿Cuántos m² trae un paquete de tarima?",
     "Depende del modelo: el laminado suele venir en paquetes de 1,9 a 2,5 m², la tarima de madera multicapa en paquetes de 1,5 a 3 m². "
     "El dato viene en la etiqueta del paquete."),
    ("¿Qué porcentaje de merma lleva la tarima?",
     "Un 10 % en colocación recta normal, un 5 % en habitaciones muy regulares y un 15 % en diagonal o espiga."),
    ("¿Cuánto rodapié necesito?",
     "El perímetro de la habitación menos el ancho de las puertas, más un 10 % para cortes. Para una habitación de 4 × 3 m con una puerta, unos 14,5 m: 7 barras de 2,4 m."),
    ("¿Hace falta base aislante debajo del laminado?",
     "Sí, en suelos flotantes: amortigua el ruido de pisadas y absorbe pequeñas irregularidades. Sobre una solera, añade además una lámina antihumedad si la base no la incluye."),
    ("¿Se puede poner tarima sobre baldosa?",
     "Sí, en flotante, si la baldosa está bien adherida y plana. Revisa la altura de las puertas: el suelo sube de 8 a 15 mm."),
]

TOOL = {
    "slug": "calculadora-tarima-suelo",
    "lang": "es",
    "twin": "flooring-calculator",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "layout-board",
    "order": 25,
    "name": "Calculadora de tarima",
    "k": "tarima laminado parquet suelo flotante paquetes m2 merma rodapié base aislante vinílico",
    "title": "Calculadora de tarima y suelo laminado: m² y paquetes",
    "desc": "Calcula los m² y paquetes de tarima, laminado o vinílico con la merma, los metros y barras de rodapié y los rollos de base aislante.",
    "h1": "Calculadora de tarima y suelo laminado",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "l", "type": "number", "label": "Largo", "value": "5", "unit": "m", "step": "0.01"},
        {"id": "a", "type": "number", "label": "Ancho", "value": "4", "unit": "m", "step": "0.01"},
        {"id": "pm2", "type": "number", "label": "m² por paquete", "value": "2,22", "unit": "m²", "step": "0.01", "w": "s"},
        {"id": "merma", "type": "seg", "label": "Merma", "value": "10", "options": [("5", "5 %"), ("10", "10 %"), ("15", "15 %")]},
        {"id": "rod", "type": "check", "label": "Rodapié", "value": True},
        {"id": "puertas", "type": "number", "label": "Puertas", "value": "1", "w": "s", "show": ("rod", ["1", "True", "true"])},
        {"id": "base", "type": "check", "label": "Base aislante", "value": True},
        {"id": "resta", "type": "number", "label": "Descontar", "value": "0", "unit": "m²", "step": "0.01", "more": True},
        {"id": "barra", "type": "number", "label": "Barra rodapié", "value": "2,4", "unit": "m", "step": "0.01", "w": "s", "more": True},
        {"id": "rollo", "type": "number", "label": "Rollo base", "value": "15", "unit": "m²", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("UNE 56810:2023 · Suelos de madera. Colocación. Especificaciones (ficha de la norma)", UNE56810)],
    "related": ["calculadora-azulejos", "calculadora-pintura", "papel-pintado", "escalera-huella-contrahuella"],
    "tests": [
        ({}, {"n.area": 20, "n.packs": 10, "n.skirting": 17.2, "n.bars": 8, "n.rolls": 2}),
        ({"merma": "15"}, {"n.packs": 11}),
        ({"rod": False, "base": False}, {"n.packs": 10, "n.bars": 0, "n.rolls": 0}),
        ({"l": "4", "a": "3"}, {"n.skirting": 13.2, "n.bars": 7}),
        ({"resta": "25"}, {"err": "Lo que descuentas es mayor que la habitación."}),
        ({"pm2": ""}, {"err": "Escribe los m² de cada paquete."}),
    ],
}
