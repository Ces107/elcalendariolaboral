"""Grava, tierra y césped: m3, tonnes and bags of gravel, sand, topsoil, bark or substrate for an area and depth, or the
seed / turf rolls for a lawn. English twin: gravel_calculator.py (same JS, yd3, tons, US bags)."""
import math

from herramientas.tools import _bricolaje as F

CTE_SEAE = "https://www.codigotecnico.org/pdf/Documentos/SE/DBSE-AE.pdf"

# loose bulk density, kg/m3 (CTE DB SE-AE tabla C.6 for sand 1.400-1.900 and sand and gravel 1.500-2.000; the rest typical)
MATS = [("grava", "Grava", 1600), ("gravilla", "Gravilla decorativa", 1500), ("arena", "Arena", 1600), ("canto", "Canto rodado", 1600),
        ("zahorra", "Zahorra", 1900), ("tierra", "Tierra vegetal", 1300), ("sustrato", "Sustrato o compost", 600), ("corteza", "Corteza de pino", 300)]

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var us = EN && v.u === 'us', FT2 = 0.09290304, FT3 = 0.028316846592;
  var T = EN ? { dims: 'Enter the length and width.', neg: 'The area left out is larger than the area.', d: 'Enter the depth.', den: 'Enter the density.',
      area: 'Area', vol: 'Volume', w: 'Weight', bags: 'Bags', big: 'Bulk bags (1 m³)', seed: 'Seed', sod: 'Sod', lv: 'Volume', ls: 'Lawn' }
    : { dims: 'Escribe el largo y el ancho.', neg: 'Lo que descuentas es mayor que la superficie.', d: 'Escribe el espesor.', den: 'Escribe la densidad.',
      area: 'Superficie', vol: 'Volumen', w: 'Peso', bags: 'Sacos', big: 'Sacas de 1 m³', seed: 'Semilla', sod: 'Tepes', lv: 'Volumen', ls: 'Césped' };
  if (!(v.l > 0 && v.a > 0)) return { err: T.dims };
  var off = v.resta > 0 ? v.resta : 0, area = v.l * v.a - off;
  if (area <= 0) return { err: T.neg };
  var aM = us ? area * FT2 : area, A2 = us ? 'sq ft' : 'm²';
  var mg = v.merma > 0 ? v.merma : 0, rows = [[T.area, fv(area, 2) + ' ' + A2]];
  if (v.uso === 'ces') {
    if (v.ces === 'tepe') {
      var m2 = aM * (1 + mg / 100), sq = us ? m2 / FT2 : m2, pal = us ? Math.ceil(sq / 500 - 1e-9) : Math.ceil(m2 - 1e-9);
      rows.push([T.sod, fx(sq, 1) + ' ' + A2 + (mg ? ' (+' + fv(mg, 0) + (EN ? '%)' : ' %)') : ''), 'tot']);
      rows.push([us ? 'Pallets (500 sq ft)' : 'Rollos de 1 m²', String(pal)]);
      return { label: T.ls, big: us ? pal + ' pallets' : pal + ' rollos', sub: fx(sq, 1) + ' ' + A2, rows: rows, n: { m2: r(m2, 3), units: pal } };
    }
    var g = us ? (v.dosus > 0 ? v.dosus : 7) * 453.592 / (1000 * FT2) : (v.dosis > 0 ? v.dosis : 35);
    var kg = g * aM * (1 + mg / 100) / 1000;
    rows.push([T.seed, us ? fx(kg / 0.45359237, 1) + ' lb' : fx(kg, 2) + ' kg', 'tot']);
    rows.push([EN ? 'Rate' : 'Dosis', us ? fv(v.dosus > 0 ? v.dosus : 7, 1) + ' lb / 1,000 sq ft' : fv(g, 0) + ' g/m²']);
    return { label: T.ls, big: us ? fx(kg / 0.45359237, 1) + ' lb' : fx(kg, 2) + ' kg', sub: (EN ? 'seed for ' : 'de semilla para ') + fv(area, 1) + ' ' + A2,
      rows: rows, n: { kg: r(kg, 3) } };
  }
  if (!(v.e > 0)) return { err: T.d };
  var den = us ? (v.densus > 0 ? v.densus * 16.01846337 : 0) : (v.dens > 0 ? v.dens : 0);
  if (!den) return { err: T.den };
  var vol = aM * (us ? v.e * 0.0254 : v.e / 100) * (1 + mg / 100), kgT = vol * den;
  rows.push([T.vol, us ? fx(vol / FT3, 1) + ' ft³ · ' + fx(vol / 0.764554858, 2) + ' yd³' : fx(vol, 3) + ' m³', 'tot']);
  rows.push([T.w, us ? fx(kgT / 0.45359237 / 2000, 2) + ' tons · ' + fx(kgT / 0.45359237, 0) + ' lb' : fx(kgT / 1000, 2) + ' t · ' + fx(kgT, 0) + ' kg']);
  var nb;
  if (den >= 1000) {
    var bk = us ? (v.sacous > 0 ? v.sacous : 50) * 0.45359237 : (v.saco > 0 ? v.saco : 25);
    nb = Math.ceil(kgT / bk - 1e-9);
    rows.push([T.bags, nb + ' × ' + (us ? fv(bk / 0.45359237, 0) + ' lb' : fv(bk, 0) + ' kg')]);
  } else {
    var bl = us ? (v.bolus > 0 ? v.bolus : 2) * FT3 : (v.bol > 0 ? v.bol : 50) / 1000;
    nb = Math.ceil(vol / bl - 1e-9);
    rows.push([T.bags, nb + ' × ' + (us ? fv(bl / FT3, 1) + ' ft³' : fv(bl * 1000, 0) + ' L')]);
  }
  if (!us) rows.push([T.big, String(Math.ceil(vol - 1e-9))]);
  return {
    label: T.lv, big: us ? fx(vol / 0.764554858, 2) + ' yd³' : fx(vol, 2) + ' m³',
    sub: us ? fx(kgT / 0.45359237 / 2000, 2) + ' tons' : fx(kgT / 1000, 2) + ' t',
    rows: rows,
    n: { vol: r(vol, 4), kg: r(kgT, 1), bags: nb }
  };
}
"""


def blocks(ctx):
    n = F.n
    vol = 4 * 3 * 0.05 * 1.05
    rows = "".join(f"<tr><td>{name}</td><td class=num>{n(d)} kg/m³</td><td class=num>{n(d * 0.05 / 1000 * 1000, 0)} kg</td></tr>"
                   for _, name, d in MATS)
    return [
        ("Cuánta grava o tierra necesito", f"""
<p>Multiplica el largo por el ancho y por el espesor en metros: salen los metros cúbicos. Por la densidad del material salen
los kilos. Un camino o un patio de 4 × 3 m con 5 cm de grava son 0,6 m³; con un 5 % de margen, {n(vol, 2)} m³, que pesan
<b>{n(vol * 1.6, 2)} toneladas</b>: {math.ceil(vol * 1600 / 25)} sacos de 25 kg, o una saca grande de 1 m³ que suele salir
bastante más barata a partir de unos 20 sacos.</p>
<p>Los espesores habituales son de 3 a 5 cm de gravilla decorativa sobre malla antihierbas, 5 a 8 cm de grava en caminos que
se pisan, 10 a 15 cm de zahorra compactada como base de una solera o de un camino de coches, 5 a 10 cm de corteza de pino
para que no salgan hierbas y 10 a 20 cm de tierra vegetal para plantar césped o un huerto.</p>
<table class="tbl"><thead><tr><th>Material</th><th>Densidad</th><th>Por m² a 5 cm</th></tr></thead><tbody>{rows}</tbody></table>"""),
        ("Densidades: por qué pesa tanto", """
<p>Los áridos se venden por peso y se calculan por volumen, así que la densidad aparente (la del material suelto, con sus
huecos) lo es todo. El Código Técnico da para la arena entre 1.400 y 1.900 kg/m³ y para la arena con grava entre 1.500 y
2.000 kg/m³ (DB SE-AE, tabla C.6): la calculadora usa 1.600 para grava y arena, que es el valor medio de lo que sirve un
almacén. La tierra vegetal pesa algo menos, unos 1.300 kg/m³ seca y suelta, pero bastante más mojada. La corteza y el
sustrato son ligeros y se venden por litros, así que para ellos la calculadora da sacos de 50 L. Si tu proveedor indica otra
densidad, cámbiala en la casilla.</p>
<p>La zahorra se compacta: un 15 a 20 % del volumen suelto desaparece al pasar la bandeja vibrante. Súmalo en «Margen» si
calculas una base compactada.</p>"""),
        ("Césped: semilla o tepe", """
<p>Para sembrar, la dosis habitual de una mezcla de césped es de 30 a 40 g de semilla por m², y hasta 50 g/m² para resembrar
calvas o en mezclas de ray-grass. La calculadora usa 35 g/m²: un jardín de 50 m² necesita unos 1,8 kg. El tepe (césped en
rollo) se vende por m², normalmente en rollos de 1 m², y se pide con un 5 % de margen para los recortes de los bordes. Debe
colocarse el mismo día que llega, sobre tierra preparada y regada.</p>"""),
    ]


FAQ = [
    ("¿Cuántos kilos de grava hay en un metro cúbico?",
     "Unos 1.600 kg de grava suelta, entre 1.500 y 2.000 según el tamaño y la humedad. Un m³ de arena, también unos 1.600 kg."),
    ("¿Cuántos sacos de grava de 25 kg necesito por m²?",
     "A 5 cm de espesor, unos 80 kg por m²: algo más de 3 sacos de 25 kg por cada metro cuadrado."),
    ("¿Qué espesor de grava se pone en un jardín?",
     "De 3 a 5 cm de gravilla decorativa sobre malla antihierbas. Más grava no tapa mejor las hierbas y hace que se hunda al pisar."),
    ("¿Cuánta semilla de césped por metro cuadrado?",
     "Entre 30 y 40 g/m² para siembra nueva; para resembrar, unos 20 a 25 g/m² en las zonas claras. El fabricante indica la dosis de su mezcla."),
    ("¿Cuánta tierra vegetal necesito para poner césped?",
     "Una capa de 10 cm: 0,1 m³ por m², unos 130 kg. Para 50 m², 5 m³, unas 6,5 toneladas."),
]

TOOL = {
    "slug": "calculadora-cesped-grava",
    "lang": "es",
    "twin": "gravel-calculator",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "shovel",
    "order": 35,
    "name": "Grava, tierra y césped",
    "k": "grava arena tierra vegetal corteza zahorra m3 toneladas sacos jardín césped semilla tepe",
    "title": "Calcular grava, tierra o arena: m³, toneladas y sacos",
    "desc": "Calcula los m³, las toneladas y los sacos de grava, arena, tierra vegetal o corteza para tu jardín, y la semilla o los tepes de césped.",
    "h1": "Calculadora de grava, tierra y césped",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "uso", "type": "seg", "label": "Calcular", "value": "ari", "options": [("ari", "Grava o tierra"), ("ces", "Césped")]},
        {"id": "l", "type": "number", "label": "Largo", "value": "4", "unit": "m", "step": "0.01"},
        {"id": "a", "type": "number", "label": "Ancho", "value": "3", "unit": "m", "step": "0.01"},
        {"id": "mat", "type": "select", "label": "Material", "value": "grava", "custom": "otro", "show": ("uso", ["ari"]),
         "options": [(k, name, {"dens": str(d)}) for k, name, d in MATS] + [("otro", "Otro")]},
        {"id": "e", "type": "number", "label": "Espesor", "value": "5", "unit": "cm", "step": "0.5", "w": "s", "show": ("uso", ["ari"])},
        {"id": "dens", "type": "number", "label": "Densidad", "value": "1600", "unit": "kg/m³", "w": "s", "show": ("uso", ["ari"])},
        {"id": "ces", "type": "seg", "label": "Césped", "value": "sem", "options": [("sem", "Semilla"), ("tepe", "Tepe")], "show": ("uso", ["ces"])},
        {"id": "dosis", "type": "number", "label": "Dosis", "value": "35", "unit": "g/m²", "w": "s", "more": True},
        {"id": "merma", "type": "number", "label": "Margen", "value": "5", "unit": "%", "w": "s", "more": True},
        {"id": "resta", "type": "number", "label": "Descontar", "value": "0", "unit": "m²", "step": "0.01", "more": True},
        {"id": "saco", "type": "number", "label": "Saco", "value": "25", "unit": "kg", "w": "s", "more": True},
        {"id": "bol", "type": "number", "label": "Saco ligero", "value": "50", "unit": "L", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("CTE · DB SE-AE, anejo C, tabla C.6 (peso específico de materiales a granel)", CTE_SEAE)],
    "related": ["hormigon-mortero", "calculadora-azulejos", "calculadora-tarima-suelo", "escalera-huella-contrahuella"],
    "tests": [
        ({}, {"n.vol": 0.63, "n.kg": 1008, "n.bags": 41}),
        ({"mat": "corteza", "dens": "300", "e": "8"}, {"n.vol": 1.008, "n.bags": 21}),
        ({"uso": "ces"}, {"n.kg": 0.441}),
        ({"uso": "ces", "ces": "tepe"}, {"n.m2": 12.6, "n.units": 13}),
        ({"e": ""}, {"err": "Escribe el espesor."}),
        ({"l": "0"}, {"err": "Escribe el largo y el ancho."}),
    ],
}
