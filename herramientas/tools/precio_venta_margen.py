"""Precio de venta a partir del coste con margen o recargo (markup), IVA y comisión de la plataforma, con redondeo a ,99.
English twin: selling_price_calculator.py (sales tax / VAT as a number)."""

LEY_IVA = "https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740"

CORE_JS = r"""
  /* cost c, mode 'margen'|'recargo' (margin on net price | markup on cost), pct, tax %, platform fee % of the gross price,
     round up to .99. Returns net (before tax), gross, tax, fee, profit, margin %, markup %. */
  function price(c, mode, pct, tax, fee, r99) {
    var t = tax / 100, f = fee / 100 * (1 + t), p = pct / 100, net;
    if (mode === 'margen') { if (p + f >= 1) return null; net = c / (1 - p - f); }
    else { if (f >= 1) return null; net = c * (1 + p) / (1 - f); }
    var gross = net * (1 + t);
    if (r99) { gross = Math.floor(gross + 0.01) + 0.99; if (gross - 1 >= net * (1 + t) - 1e-9 && gross - 1 > 0) gross -= 1; net = gross / (1 + t); }
    var fe = gross * fee / 100, profit = net - c - fe;
    return { net: net, gross: gross, tax: gross - net, fee: fe, profit: profit, margin: net > 0 ? profit / net * 100 : 0,
      markup: c > 0 ? profit / c * 100 : 0 };
  }
"""


def price(c, mode, pct, tax, fee=0.0):
    t, f, p = tax / 100, fee / 100 * (1 + tax / 100), pct / 100
    net = c / (1 - p - f) if mode == "margen" else c * (1 + p) / (1 - f)
    gross = net * (1 + t)
    fe = gross * fee / 100
    return {"net": net, "gross": gross, "fee": fe, "profit": net - c - fe}


def blocks(ctx):
    e = ctx.eur
    m = price(10, "margen", 40, 21)
    k = price(10, "recargo", 40, 21)
    f = price(10, "margen", 40, 21, 13)
    return [
        ("Margen o recargo: no es lo mismo", f"""
<p>Un producto que te cuesta 10 € y quieres venderlo con un <b>40 % de margen</b>: el margen se calcula sobre el precio de
venta, así que el precio sin IVA es 10 ÷ (1 − 0,40) = <b>{e(m["net"])}</b>, y con el 21 % de IVA, {e(m["gross"])}. Ganas
{e(m["profit"])}, que es el 40 % de {e(m["net"])}. Si en cambio aplicas un <b>40 % de recargo</b> (markup) sobre el coste,
el precio sin IVA es 10 × 1,40 = {e(k["net"])} ({e(k["gross"])} con IVA) y ganas {e(k["profit"])}: solo un 28,6 % de margen.
Confundirlos es el error de precio más común: un recargo del 40 % parece mucho y deja poco.</p>
<p>La equivalencia es fija: margen = recargo ÷ (1 + recargo) y recargo = margen ÷ (1 − margen). Un 50 % de margen es un
100 % de recargo (vender al doble del coste); un 25 % de recargo es un 20 % de margen.</p>"""),
        ("Con la comisión de la plataforma", f"""
<p>Si vendes en un marketplace que cobra un porcentaje del precio final, ese porcentaje también se come margen. Con el mismo
producto de 10 € y un 13 % de comisiones (lo habitual en Etsy con IVA en comisiones), para mantener un 40 % de margen real
el precio sin IVA sube a {e(f["net"])} y el precio final a {e(f["gross"])}. La comisión se calcula sobre el precio con
IVA, porque es lo que paga el cliente; por eso la fórmula es precio = coste ÷ (1 − margen − comisión × (1 + IVA)).</p>
<p>Marca «Acabar en ,99» para redondear al alza el precio final (20,17 € pasa a 20,99 €): la calculadora recalcula el
margen real con el precio redondeado.</p>"""),
        ("Qué IVA aplicar", f"""
<p>El tipo general es el <b>21 %</b>; el reducido del <b>10 %</b> se aplica, entre otros, a alimentos que no son de primera
necesidad, hostelería y transporte de viajeros; el superreducido del <b>4 %</b>, a pan, leche, huevos, frutas y verduras,
libros, periódicos, medicamentos de uso humano y prótesis (<a href="{LEY_IVA}#a90" rel="noopener">artículos 90 y 91 de la Ley
del IVA</a>). Si vendes como particular o fuera de la UE sin repercutir IVA, elige 0 %. Si estás en recargo de equivalencia,
el precio al cliente lleva el IVA normal y tú no lo declaras: calcula con el IVA del producto.</p>"""),
    ]


FAQ = [
    ("¿Cómo calculo el precio de venta con un margen?",
     "Divide el coste entre (1 − margen). Con 10 € de coste y un 30 % de margen: 10 ÷ 0,70 = 14,29 € sin IVA."),
    ("¿Qué diferencia hay entre margen y markup?",
     "El margen es el beneficio sobre el precio de venta; el markup o recargo, sobre el coste. Un 50 % de margen equivale a un "
     "100 % de recargo."),
    ("¿El margen se calcula con o sin IVA?",
     "Sin IVA. El IVA no es tuyo: lo cobras y lo ingresas a Hacienda, así que el margen sale del precio sin IVA."),
    ("¿Qué margen es razonable para un producto artesanal?",
     "Depende de tus costes fijos, pero por debajo del 30 % de margen real (tras comisiones) cuesta cubrir el tiempo, las "
     "devoluciones y los anuncios."),
    ("¿Cómo paso de margen a recargo?",
     "Recargo = margen ÷ (1 − margen). Un 40 % de margen es un 66,7 % de recargo."),
]

JS = r"""
function (v, H, C) {
""" + CORE_JS + r"""
  var c = v.coste, fee = isNaN(v.com) ? 0 : v.com;
  if (isNaN(c) || c <= 0) return { err: 'Escribe el coste.' };
  if (isNaN(v.pct) || v.pct < 0) return { err: 'Escribe el porcentaje.' };
  if (fee < 0 || fee >= 100) return { err: 'Comisión: de 0 a 99 %.' };
  if (v.modo === 'margen' && v.pct >= 100) return { err: 'El margen tiene que ser menor que el 100 %.' };
  var r = price(c, v.modo, v.pct, +v.iva, fee, v.r99);
  if (!r) return { err: 'Con esa comisión no se puede llegar a ese margen.' };
  var e = H.eur, rows = [['Precio sin IVA', e(r.net)], ['IVA ' + v.iva + ' %', e(r.tax)]];
  if (fee) rows.push(['Comisión ' + H.num(fee, 1) + ' %', '−' + e(r.fee)]);
  rows.push(['Beneficio', e(r.profit), 'tot'], ['Margen real', H.num(r.margin, 1) + ' %'], ['Recargo sobre coste', H.num(r.markup, 1) + ' %']);
  return { label: 'Precio de venta con IVA', big: e(r.gross), sub: 'Sin IVA ' + e(r.net) + ' · ganas ' + e(r.profit),
    rows: rows, n: { net: r.net, gross: r.gross, profit: r.profit, margin: r.margin } };
}
"""

TOOL = {
    "slug": "precio-venta-margen",
    "lang": "es",
    "twin": "selling-price-calculator",
    "cat": "vendedores",
    "icon": "tag",
    "order": 70,
    "name": "Precio de venta",
    "k": "margen markup recargo pvp coste beneficio iva",
    "title": "Calcular precio de venta con margen o recargo e IVA",
    "desc": "Calcula el precio de venta a partir del coste con el margen o el recargo que quieres, con IVA del 21, 10 o 4 % y comisión de la plataforma.",
    "h1": "Calcular el precio de venta con margen",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "coste", "type": "money", "label": "Coste", "value": "10"},
        {"id": "modo", "type": "seg", "label": "Sobre", "value": "margen", "options": [("margen", "Margen"), ("recargo", "Recargo")]},
        {"id": "pct", "type": "number", "label": "Porcentaje", "value": "40", "unit": "%", "step": "0.1", "w": "s"},
        {"id": "iva", "type": "select", "label": "IVA", "value": "21", "options": [("21", "21 %"), ("10", "10 %"), ("4", "4 %"), ("0", "Sin IVA")]},
        {"id": "r99", "type": "check", "label": "Acabar en ,99", "value": False},
        {"id": "com", "type": "number", "label": "Comisión venta", "value": "0", "unit": "%", "step": "0.1", "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Ley 37/1992 del IVA, arts. 90 y 91", LEY_IVA)],
    "related": ["punto-equilibrio", "comisiones-etsy", "comisiones-paypal", "precio-sin-iva"],
    "tests": [
        ({}, {"n.net": 16.666667, "n.gross": 20.166667, "n.profit": 6.666667, "n.margin": 40}),
        ({"modo": "recargo"}, {"n.net": 14, "n.gross": 16.94}),
        ({"r99": "1"}, {"n.gross": 20.99, "n.net": 17.347107}),
        ({"com": "10", "pct": "30"}, {"n.net": 17.271157, "n.margin": 30}),
        ({"pct": "100"}, {"err": "El margen tiene que ser menor que el 100 %."}),
        ({"coste": ""}, {"err": "Escribe el coste."}),
    ],
}
