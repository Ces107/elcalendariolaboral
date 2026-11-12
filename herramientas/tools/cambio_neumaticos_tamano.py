"""Comparar medidas de neumáticos: overall diameter, sidewall, revolutions and speedometer error of a tyre size change
(formula only). Spanish page; the English twin is tire-size-calculator (same compute)."""
from herramientas.tools import _coche as K

R39 = "https://eur-lex.europa.eu/eli/reg/2010/39(2)/oj/eng"
RACE = "https://www.race.es/equivalencia-de-neumaticos"

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  function D(a, p, rr) { return rr * 25.4 + 2 * a * p / 100; }
  var A = [v.a1, v.p1, v.r1, v.a2, v.p2, v.r2];
  for (var i = 0; i < 6; i++) if (isNaN(A[i])) return { err: EN ? 'Enter width, aspect ratio and rim size of both tires.' : 'Escribe ancho, perfil y llanta de las dos medidas.' };
  if (v.a1 < 100 || v.a1 > 400 || v.a2 < 100 || v.a2 > 400) return { err: EN ? 'Width in millimetres, for example 205.' : 'Ancho en milímetros, por ejemplo 205.' };
  if (v.p1 < 20 || v.p1 > 100 || v.p2 < 20 || v.p2 > 100) return { err: EN ? 'Aspect ratio in %, for example 55.' : 'Perfil en %, por ejemplo 55.' };
  if (v.r1 < 8 || v.r1 > 30 || v.r2 < 8 || v.r2 > 30) return { err: EN ? 'Rim size in inches, for example 16.' : 'Llanta en pulgadas, por ejemplo 16.' };
  var d1 = D(v.a1, v.p1, v.r1), d2 = D(v.a2, v.p2, v.r2), s1 = v.a1 * v.p1 / 100, s2 = v.a2 * v.p2 / 100, df = (d2 / d1 - 1) * 100;
  var sp = isNaN(v.vm) || v.vm <= 0 ? 100 : v.vm, real = sp * d2 / d1, km = EN ? 1609344 : 1e6;
  function row(lab, x1, x2, dec, u) { return '<tr><td>' + lab + '</td><td class="num">' + fv(x1, dec) + u + '</td><td class="num">' + fv(x2, dec) + u + '</td><td class="num">' + (x2 - x1 >= 0 ? '+' : '') + fv(x2 - x1, dec) + u + '</td></tr>'; }
  var t1 = v.a1 + '/' + v.p1 + ' R' + v.r1, t2 = v.a2 + '/' + v.p2 + ' R' + v.r2;
  var html = '<table class="tbl"><thead><tr><th></th><th>' + H.esc(t1) + '</th><th>' + H.esc(t2) + '</th><th>' + (EN ? 'Change' : 'Diferencia') + '</th></tr></thead><tbody>' +
    row(EN ? 'Diameter' : 'Diámetro', d1, d2, 1, ' mm') +
    (EN ? row('Diameter', d1 / 25.4, d2 / 25.4, 2, '″') : '') +
    row(EN ? 'Sidewall' : 'Flanco', s1, s2, 1, ' mm') +
    row(EN ? 'Width' : 'Ancho', v.a1, v.a2, 0, ' mm') +
    row(EN ? 'Circumference' : 'Circunferencia', Math.PI * d1, Math.PI * d2, 0, ' mm') +
    row(EN ? 'Revs per mile' : 'Vueltas por km', km / (Math.PI * d1), km / (Math.PI * d2), 1, '') + '</tbody></table>';
  var ok = Math.abs(df) <= 3;
  return {
    label: EN ? 'Diameter change' : 'Diferencia de diámetro', big: (df >= 0 ? '+' : '') + fv(df, 2) + (EN ? '%' : ' %'),
    sub: (EN ? 'Speedometer reads ' + fv(sp, 0) + ' → true speed ' : 'Marca ' + fv(sp, 0) + ' → vas a ') + fv(real, 1) +
      (EN ? '' : ' km/h') + (ok ? (EN ? ' · within ±3%' : ' · dentro de ±3 %') : (EN ? ' · more than 3%' : ' · más del 3 %')),
    html: html,
    note: EN ? 'Load index and speed rating must be at least those on the original tires.' : 'El índice de carga y el código de velocidad deben ser iguales o mayores que los de la ficha técnica.',
    n: { d1: r(d1, 2), d2: r(d2, 2), diff: r(df, 4), real: r(real, 2), ok: ok }
  };
}
"""


def blocks(ctx):
    return [
        ("Cómo se calcula", """
<p>Una medida como <b>205/55 R16</b> dice el ancho del neumático en milímetros (205), la altura del flanco como porcentaje
del ancho (55 %) y el diámetro de la llanta en pulgadas (16). El diámetro exterior es <b>llanta × 25,4 + 2 × ancho × perfil ÷
100</b>: 16 × 25,4 = 406,4 mm de llanta más dos flancos de 112,75 mm, en total 631,9 mm. Lo que importa al cambiar de medida
es que ese diámetro casi no varíe, porque de él dependen el velocímetro, el cuentakilómetros, los sistemas de ayuda a la
conducción y que la rueda quepa en el paso de rueda.</p>
<p>Ejemplo: pasar de 205/55 R16 a 225/45 R17 para montar una llanta más grande da 634,3 mm de diámetro, un <b>0,38 %</b> más:
prácticamente igual, con un flanco más bajo (101 mm) y 20 mm más de ancho. En cambio, montar 225/50 R17 da 656,8 mm, un
<b>3,94 %</b> más: cuando el velocímetro marque 100, irás a 103,9 km/h, y el cuentakilómetros contará de menos.</p>"""),
        ("El velocímetro y el margen del 3 %", f"""
<p>Por homologación, el velocímetro de un coche nunca puede marcar menos de la velocidad real: el
<a href="{R39}" rel="noopener">Reglamento n.º 39 de la CEPE/ONU</a> exige que la velocidad indicada quede entre la real y la
real + 10 % + 4 km/h. Por eso casi todos los coches marcan algo de más. Si montas ruedas más grandes, ese margen se come y el
velocímetro puede llegar a marcar menos de lo que vas: con un radar no sirve de excusa. Con ruedas más pequeñas pasa lo
contrario, marca aún más de la cuenta y el coche va algo más revolucionado.</p>
<p>Para la ITV, un neumático se considera equivalente al de la ficha técnica si su diámetro exterior no difiere más de un
3 %, y su índice de carga y su código de velocidad son iguales o superiores (criterio del Manual de Procedimiento de
Inspección de las Estaciones ITV, explicado por el <a href="{RACE}" rel="noopener">RACE</a>). Si la medida no figura en la
ficha ni es equivalente, es una reforma que hay que legalizar. Esta calculadora solo hace la geometría; antes de cambiar,
mira la ficha técnica de tu coche y pregunta en la ITV o al taller.</p>"""),
    ]


FAQ = [
    ("¿Qué significa 205/55 R16?",
     "205 mm de ancho, flanco del 55 % del ancho (112,75 mm), construcción radial (R) y llanta de 16 pulgadas. Detrás suelen "
     "venir el índice de carga y el código de velocidad, por ejemplo 91V."),
    ("¿Puedo poner neumáticos más anchos?",
     "Solo si la medida figura en la ficha técnica o es equivalente: diámetro dentro del 3 %, índices de carga y velocidad "
     "iguales o mayores y sin rozar con la carrocería. Si no, es una reforma."),
    ("¿Cuánto se desvía el velocímetro al cambiar de rueda?",
     "Lo mismo que el diámetro, en porcentaje. Un 2 % más de diámetro significa que a 100 marcados vas a 102 km/h."),
    ("¿Qué medidas son equivalentes a 205/55 R16?",
     "Con diámetro dentro del ±3 % (612,9 a 650,9 mm): por ejemplo 195/65 R15, 225/45 R17 o 225/40 R18. Comprueba siempre las que "
     "admite tu ficha técnica."),
    ("¿Las ruedas más grandes gastan más?",
     "Más anchas y pesadas, sí: más resistencia a la rodadura y más inercia. Una llanta más grande con el mismo diámetro exterior "
     "suele empeorar algo el confort y el consumo."),
]

INPUTS_ES = [
    {"id": "a1", "type": "number", "label": "Ancho actual", "value": "205", "unit": "mm", "w": "s"},
    {"id": "p1", "type": "number", "label": "Perfil actual", "value": "55", "unit": "%", "w": "s"},
    {"id": "r1", "type": "number", "label": "Llanta actual", "value": "16", "unit": "″", "w": "s"},
    {"id": "a2", "type": "number", "label": "Ancho nuevo", "value": "225", "unit": "mm", "w": "s"},
    {"id": "p2", "type": "number", "label": "Perfil nuevo", "value": "45", "unit": "%", "w": "s"},
    {"id": "r2", "type": "number", "label": "Llanta nueva", "value": "17", "unit": "″", "w": "s"},
    {"id": "vm", "type": "number", "label": "Velocímetro", "value": "100", "unit": "km/h", "w": "s", "more": True},
]

TOOL = {
    "slug": "cambio-neumaticos-tamano",
    "lang": "es",
    "twin": "tire-size-calculator",
    "cat": "vehiculos",
    "icon": "wheel",
    "order": 55,
    "name": "Comparar neumáticos",
    "k": "medidas neumáticos equivalentes diámetro rueda llanta velocímetro error 3 % itv",
    "title": "Comparar medidas de neumáticos: diámetro y velocímetro",
    "desc": "Compara dos medidas de neumático: diámetro, flanco, vueltas por km y error del velocímetro, y si la diferencia queda dentro del 3 %.",
    "h1": "Comparar medidas de neumáticos",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": K.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Reglamento n.º 39 de la CEPE/ONU · velocímetro (EUR-Lex)", R39),
                ("RACE · Equivalencia de neumáticos (Manual de Procedimiento de Inspección ITV)", RACE)],
    "credits": [],
    "related": ["proxima-itv", "velocidad-media-tiempo", "consumo-l100km-mpg", "etiqueta-dgt"],
    "tests": [
        ({}, {"n.d1": 631.9, "n.d2": 634.3, "n.diff": 0.3798, "n.real": 100.38, "n.ok": True}),
        ({"a2": "225", "p2": "50", "r2": "17"}, {"n.diff": 3.9405, "n.real": 103.94, "n.ok": False}),
        ({"a2": "195", "p2": "65", "r2": "15"}, {"n.d2": 634.5, "n.diff": 0.4115}),
        ({"a1": "175", "p1": "65", "r1": "14", "a2": "205", "p2": "55", "r2": "16"}, {"n.d1": 583.1, "n.diff": 8.3691}),
        ({"a1": ""}, {"err": "Escribe ancho, perfil y llanta de las dos medidas."}),
    ],
}
