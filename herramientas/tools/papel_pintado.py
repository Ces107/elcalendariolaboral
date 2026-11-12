"""Papel pintado: rolls for a room or a wall from the strips that fit in a roll, with the pattern repeat (straight or
offset match) and the trimming allowance. English twin: wallpaper_calculator.py (same JS, US double rolls)."""
import math

from herramientas.tools import _bricolaje as F

EN233 = "https://iteh.es/catalog/standards/cen/848e59fa-e595-4da5-b533-4e3a4ed9cee2/en-233-2016"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var us = EN && v.u === 'us', k = us ? 0.3048 : 1;
  var T = EN ? { room: 'Enter the length and width of the room.', wall: 'Enter the wall width.', h: 'Enter the wall height.',
      roll: 'Enter the roll width and length.', short: 'The roll is shorter than one drop.', label: 'Wallpaper', rolls: ' rolls', roll1: ' roll',
      p: 'Width to cover', cut: 'Drop length', per: 'Drops per roll', strips: 'Drops', left: 'Left over', n: 'Rolls' }
    : { room: 'Escribe el largo y el ancho de la habitación.', wall: 'Escribe el ancho de la pared.', h: 'Escribe la altura de la pared.',
      roll: 'Escribe el ancho y el largo del rollo.', short: 'El rollo es más corto que una tira.', label: 'Papel pintado', rolls: ' rollos', roll1: ' rollo',
      p: 'Ancho a cubrir', cut: 'Largo de cada tira', per: 'Tiras por rollo', strips: 'Tiras', left: 'Sobra', n: 'Rollos' };
  var P;
  if (v.modo === 'hab') {
    if (!(v.l > 0 && v.a > 0)) return { err: T.room };
    var nd = v.puertas > 0 ? Math.floor(v.puertas) : 0;
    P = 2 * (v.l + v.a) * k - nd * 0.8;
  } else {
    if (!(v.pw > 0)) return { err: T.wall };
    P = v.pw * k;
  }
  if (!(v.h > 0)) return { err: T.h };
  if (P <= 0) return { err: T.room };
  var h = v.h * k;
  var rw = us ? v.rwin * 0.0254 : v.rw / 100, rl = us ? v.rlft * 0.3048 : v.rl;
  if (!(rw > 0 && rl > 0)) return { err: T.roll };
  var rep = us ? (v.repin > 0 ? v.repin * 0.0254 : 0) : (v.rep > 0 ? v.rep / 100 : 0);
  var trim = us ? (v.trimin >= 0 ? v.trimin * 0.0254 : 0.1) : (v.sobra >= 0 ? v.sobra / 100 : 0.1);
  var cut = h + trim;
  if (rep > 0) cut = Math.ceil(cut / rep - 1e-9) * rep + (v.casado === 'des' ? rep / 2 : 0);
  var per = Math.floor(rl / cut + 1e-9);
  if (per < 1) return { err: T.short };
  var strips = Math.ceil(P / rw - 1e-9), rolls = Math.ceil(strips / per - 1e-9);
  var left = rolls * per - strips;
  function len(m) { return us ? fx(m / 0.3048, 2) + ' ft' : fx(m, 2) + ' m'; }
  return {
    label: T.label, big: rolls + (rolls === 1 ? T.roll1 : T.rolls),
    sub: strips + ' × ' + len(cut) + ' · ' + per + ' ' + T.per.toLowerCase(),
    rows: [[T.p, len(P)], [T.cut, len(cut)], [T.per, String(per)], [T.strips, String(strips)], [T.n, String(rolls), 'tot'],
      [T.left, String(left) + ' × ' + len(cut)]],
    n: { strips: strips, per: per, rolls: rolls, cut: r(cut, 4) }
  };
}
"""


def rolls(P, h, rw, rl, rep=0.0, offset=False, trim=0.10):
    cut = h + trim
    if rep:
        cut = math.ceil(cut / rep - 1e-9) * rep + (rep / 2 if offset else 0)
    per = int(rl / cut + 1e-9)
    strips = math.ceil(P / rw - 1e-9)
    return strips, per, math.ceil(strips / per - 1e-9), cut


def blocks(ctx):
    n = F.n
    s, per, r, cut = rolls(13.2, 2.5, 0.53, 10.05)
    s2, per2, r2, cut2 = rolls(13.2, 2.5, 0.53, 10.05, 0.64, True)
    return [
        ("Cuántos rollos de papel pintado necesito", f"""
<p>El papel se calcula por <b>tiras</b>, no por metros cuadrados. Una habitación de 4 × 3 m con una puerta tiene
13,2 m de pared a cubrir (14 m de perímetro menos 0,8 m de la puerta). Con el rollo europeo de 0,53 × 10,05 m hacen falta
{s} tiras; cada tira mide 2,5 m de altura más 10 cm para recortar arriba y abajo, así que de cada rollo salen {per} tiras y
hay que comprar <b>{r} rollos</b>.</p>
<p>Calcular por superficie engaña: esas paredes suman 33 m² y un rollo cubre 5,3 m², lo que daría 7 rollos. Pero de un rollo
de 10,05 m solo salen tres tiras de 2,6 m y sobran 2,25 m que no sirven para una pared entera. Los recortes sí valen para
encima de las puertas y debajo y encima de las ventanas, por eso las ventanas no se descuentan.</p>"""),
        ("El casado del dibujo", f"""
<p>Si el papel tiene dibujo, cada tira debe empezar en el mismo punto del motivo que la anterior, y eso gasta papel. La
<b>repetición</b> (o raccord) viene en la etiqueta en centímetros. Con casado <b>recto</b> el dibujo se repite a la misma
altura en las dos tiras y cada tira se redondea a un múltiplo de la repetición. Con casado <b>desplazado</b> (salteado) el
motivo baja media repetición en cada tira y, de media, se pierde media repetición más por tira.</p>
<p>En la misma habitación, un papel con repetición de 64 cm y casado desplazado obliga a cortar tiras de {n(cut2, 2)} m: salen
{per2} por rollo y hacen falta {r2} rollos. Los papeles lisos o con dibujo libre (sin casado) se calculan con repetición 0.</p>"""),
        ("Rollos, lotes y medidas", """
<p>La norma europea EN 233 fija que un rollo estándar de papel pintado tiene 5,326 m² (con un 3 % de tolerancia) y un ancho
nominal de 500 a 530 mm: es el rollo de 0,53 × 10,05 m que se vende en casi toda Europa. Hay rollos anchos de 0,70 m y de
1,06 m, sobre todo en papel tejido no tejido, que se pegan encolando la pared y rinden más porque hay menos juntas.</p>
<p>Comprueba que todos los rollos llevan el mismo <b>número de lote</b>: el tono puede cambiar entre fabricaciones. Si te
falta un rollo de otro lote, úsalo en una pared distinta, nunca junto a una tira del primero. Comprar un rollo de reserva es
barato frente a no encontrar el mismo lote meses después.</p>"""),
    ]


FAQ = [
    ("¿Cuántos m² cubre un rollo de papel pintado?",
     "Un rollo europeo de 0,53 × 10,05 m tiene 5,3 m², pero en la práctica cubre menos por los recortes: con techos de 2,5 m salen "
     "tres tiras, unos 4 m² de pared."),
    ("¿Cuántos rollos necesito para una pared de 4 metros?",
     "Con 2,5 m de altura y rollo de 0,53 m, ocho tiras: tres rollos sin dibujo, y puede que cuatro si el casado es grande."),
    ("¿Se descuentan las ventanas?",
     "No. Los trozos que sobran de las tiras se usan encima y debajo de las ventanas. Solo se descuentan las puertas y los huecos de "
     "suelo a techo."),
    ("¿Qué es la repetición o raccord?",
     "La altura a la que se repite el dibujo. Viene en la etiqueta del rollo en centímetros, junto al símbolo del tipo de casado."),
    ("¿Cuánto margen dejo arriba y abajo?",
     "Unos 5 cm en cada extremo, 10 cm por tira, para corregir techos y suelos que no están rectos."),
]

TOOL = {
    "slug": "papel-pintado",
    "lang": "es",
    "twin": "wallpaper-calculator",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "wallpaper",
    "order": 40,
    "name": "Papel pintado",
    "k": "rollos papel pintado tiras repetición raccord casado pared habitación",
    "title": "Calculadora de papel pintado: cuántos rollos comprar",
    "desc": "Calcula cuántos rollos de papel pintado necesitas para una habitación o una pared, con la repetición del dibujo y el tipo de casado.",
    "h1": "Calculadora de papel pintado",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "modo", "type": "seg", "label": "Medir", "value": "hab", "options": [("hab", "Habitación"), ("pared", "Una pared")]},
        {"id": "l", "type": "number", "label": "Largo", "value": "4", "unit": "m", "step": "0.01", "show": ("modo", ["hab"])},
        {"id": "a", "type": "number", "label": "Ancho", "value": "3", "unit": "m", "step": "0.01", "show": ("modo", ["hab"])},
        {"id": "pw", "type": "number", "label": "Ancho pared", "value": "3,5", "unit": "m", "step": "0.01", "show": ("modo", ["pared"])},
        {"id": "h", "type": "number", "label": "Alto", "value": "2,5", "unit": "m", "step": "0.01"},
        {"id": "puertas", "type": "number", "label": "Puertas", "value": "1", "w": "s", "show": ("modo", ["hab"])},
        {"id": "rollo", "type": "select", "label": "Rollo", "value": "eu", "custom": "otro",
         "options": [("eu", "0,53 × 10,05 m", {"rw": "53", "rl": "10,05"}), ("70", "0,70 × 10,05 m", {"rw": "70", "rl": "10,05"}),
                     ("106", "1,06 × 10,05 m", {"rw": "106", "rl": "10,05"}), ("otro", "Otra medida")]},
        {"id": "rw", "type": "number", "label": "Ancho rollo", "value": "53", "unit": "cm", "step": "0.1", "w": "s"},
        {"id": "rl", "type": "number", "label": "Largo rollo", "value": "10,05", "unit": "m", "step": "0.01", "w": "s"},
        {"id": "rep", "type": "number", "label": "Repetición", "value": "0", "unit": "cm", "w": "s"},
        {"id": "casado", "type": "seg", "label": "Casado", "value": "rec", "options": [("rec", "Recto"), ("des", "Desplazado")]},
        {"id": "sobra", "type": "number", "label": "Margen corte", "value": "10", "unit": "cm", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("EN 233:2016 · Revestimientos murales en rollo: especificaciones (CEN)", EN233)],
    "related": ["calculadora-pintura", "calculadora-azulejos", "calculadora-tarima-suelo", "escalera-huella-contrahuella"],
    "tests": [
        ({}, {"n.strips": 25, "n.per": 3, "n.rolls": 9}),
        ({"h": "2,4", "rep": "70"}, {"n.cut": 2.8, "n.rolls": 9}),
        ({"h": "2,4"}, {"n.per": 4, "n.rolls": 7}),
        ({"rep": "53", "casado": "des"}, {"n.cut": 2.915, "n.rolls": 9}),
        ({"modo": "pared", "pw": "3,5"}, {"n.strips": 7, "n.rolls": 3}),
        ({"rw": "106"}, {"n.strips": 13, "n.rolls": 5}),
        ({"h": ""}, {"err": "Escribe la altura de la pared."}),
    ],
}
