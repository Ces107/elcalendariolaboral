"""Comisiones de Etsy para vendedores en España: publicación, transacción, procesamiento, tasa regulatoria, Offsite Ads,
IVA sobre las comisiones, lo que te queda y el precio mínimo. English twin: etsy_fee_calculator.py."""
from herramientas.tools import _sellers as S

LEY_IVA = "https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740"


def blocks(ctx):
    e = S.etsy(25, 5, cost=8, post=4.5)
    a = S.etsy(25, 5, cost=8, post=4.5, ads=15)
    f = e["f"]
    m = S.fm
    return [
        ("Cuánto se queda Etsy en España", f"""
<p>Por un artículo de 25 € con 5 € de envío, Etsy se queda <b>{m(e["fees"])}</b>, el {S.pc(e["pct"])} de lo que paga el
cliente, si vendes desde España sin NIF-IVA intracomunitario. Ese total sale de: publicación {m(f["list"])}, transacción
{m(f["tx"])} (6,5 % de 30 €), procesamiento del pago {m(f["proc"])} (4 % + 0,30 €), tasa regulatoria {m(f["rof"])}
(0,88 %) y {m(e["vat"])} de IVA al 21 % sobre todas ellas. Te ingresan {m(e["net"])}; si el producto te cuesta 8 € y la
etiqueta de envío 4,50 €, ganas <b>{m(e["profit"])}</b>.</p>
<p>Si esa venta llega por un anuncio externo (Offsite Ads, 15 %), la comisión sube a {m(a["fees"])} y el beneficio baja a
{m(a["profit"])}. Por eso conviene calcular el precio con los anuncios activados: una venta con Offsite Ads se lleva
aquí más del 40 % de tu beneficio.</p>"""),
        ("Cada comisión, una a una", """
<ul>
<li><b>Publicación</b>: 0,20 USD por anuncio, que Etsy cobra en euros al cambio del día (unos 0,17 €). Dura cuatro meses y
se vuelve a cobrar con cada venta si el anuncio tiene más unidades.</li>
<li><b>Transacción</b>: 6,5 % del precio del artículo más el envío y el envoltorio de regalo que cobres.</li>
<li><b>Procesamiento del pago</b> (Etsy Payments) con cuenta bancaria en España: 4 % del total del pedido, envío incluido, más
0,30 € fijos por pedido. Es la misma tarifa que en Francia, Alemania, Italia o Portugal.</li>
<li><b>Tasa regulatoria</b>: desde el 22 de junio de 2026 es el 0,88 % del pedido para tiendas en España (antes 0,72 %).</li>
<li><b>Offsite Ads</b>: 15 % de la venta si llega por un anuncio de Etsy en Google, Instagram o Pinterest; 12 % y obligatorio
si tu tienda facturó más de 10.000 USD en los últimos 12 meses. Tope de 100 USD por pedido.</li>
<li><b>Conversión de divisa</b>: 2,5 % si el anuncio está en una moneda distinta de la de tu cuenta de pagos. Publica en
euros y no la pagas.</li>
</ul>"""),
        ("El IVA de las comisiones", f"""
<p>Etsy factura desde Irlanda. Si no tienes un NIF-IVA intracomunitario válido (alta en el Registro de Operadores
Intracomunitarios), te cobra un 21 % de IVA español sobre todas las comisiones, procesamiento incluido, y no puedes
recuperarlo. Si estás dado de alta como operador intracomunitario y lo indicas en la configuración de tu tienda, Etsy deja
de cobrarlo: el IVA lo declaras tú por <a href="{LEY_IVA}#a84" rel="noopener">inversión del sujeto pasivo</a> en el modelo
303 (y la operación en el 349), y en la práctica se compensa. En el ejemplo de arriba eso son {m(e["vat"])} por venta.</p>
<p>Desmarca «IVA en comisiones» si ya tienes NIF-IVA. Los demás impuestos de la venta (tu propio IVA si eres autónomo)
no cambian las comisiones de Etsy, pero sí lo que te queda: tenlos en cuenta en el coste.</p>"""),
        ("Precio mínimo para no perder", f"""
<p>Todas las comisiones porcentuales suman k = (6,5 % + 4 % + 0,88 % + anuncios) × 1,21 y las fijas, (0,17 € + 0,30 €) ×
1,21. El precio que deja beneficio cero es (coste + envío real + fijas) ÷ (1 − k) menos el envío que cobras. Con 8 € de
coste, 4,50 € de etiqueta y 5 € de envío cobrado sale {m(e["be"])}; con Offsite Ads del 15 %, {m(a["be"])}. La
calculadora lo muestra en la última línea.</p>"""),
    ]


FAQ = [
    ("¿Cuánto cobra Etsy por venta en España en 2026?",
     "Un 6,5 % de transacción, un 4 % + 0,30 € de procesamiento, una tasa regulatoria del 0,88 % y 0,20 USD de publicación. "
     "Sin NIF-IVA, súmale un 21 % de IVA sobre todo: en total suele quedarse entre el 13 % y el 16 % de lo que paga el cliente."),
    ("¿Etsy cobra comisión sobre los gastos de envío?",
     "Sí. La transacción (6,5 %), el procesamiento (4 %), la tasa regulatoria y Offsite Ads se calculan sobre el precio más el "
     "envío. Subir el envío y bajar el precio no reduce las comisiones."),
    ("¿Puedo desactivar Offsite Ads?",
     "Sí, mientras tu tienda haya facturado menos de 10.000 USD en los últimos 12 meses: en Configuración de la tienda, "
     "Publicidad externa. Por encima de esa cifra son obligatorios, al 12 %."),
    ("¿Por qué Etsy me cobra IVA si vendo fuera de España?",
     "El IVA de las comisiones depende de dónde está tu tienda, no del cliente. Etsy lo cobra a vendedores de la UE sin NIF-IVA "
     "intracomunitario; con él, no aparece en la factura y lo declaras tú."),
    ("¿Qué es la tasa regulatoria de Etsy?",
     "Un porcentaje sobre cada pedido con el que Etsy repercute impuestos sobre servicios digitales de algunos países. En "
     "España es el 0,88 % desde el 22 de junio de 2026."),
]

JS = r"""
function (v, H, C) {
""" + S.FMT_JS + S.ETSY_JS + r"""
  var n = ['precio', 'envio', 'coste', 'envreal', 'regalo', 'pub', 'tasa'];
  for (var i = 0; i < n.length; i++) {
    var x = v[n[i]];
    if (n[i] !== 'precio' && isNaN(x)) v[n[i]] = 0;
    else if (isNaN(x) || x < 0) return { err: 'Revisa ' + (n[i] === 'precio' ? 'el precio.' : 'los importes.') };
    if (v[n[i]] < 0) return { err: 'Los importes no pueden ser negativos.' };
  }
  if (v.precio <= 0) return { err: 'Escribe el precio del artículo.' };
  var r = etsy({ price: v.precio, ship: v.envio, wrap: v.regalo, list: v.pub, pp: 4, pf: 0.30, rof: v.tasa, ads: +v.ads,
    vat: v.iva ? 21 : 0, conv: v.div, cost: v.coste, post: v.envreal });
  var e = function (x) { return fm(x, 'EUR'); }, f = r.f;
  var rows = [
    ['Publicación', e(f.list)],
    ['Transacción 6,5 %', e(f.tx)],
    ['Procesamiento 4 % + 0,30 €', e(f.proc)],
    ['Tasa regulatoria ' + pc(v.tasa, false, 2), e(f.rof)]
  ];
  if (f.ads) rows.push(['Offsite Ads ' + v.ads + ' %', e(f.ads)]);
  if (f.conv) rows.push(['Conversión 2,5 %', e(f.conv)]);
  if (r.vat) rows.push(['IVA 21 %', e(r.vat)]);
  rows.push(['Comisiones · ' + pc(r.pct), e(r.fees), 'tot']);
  rows.push(['Te ingresa Etsy', e(r.net), 'sub']);
  if (v.coste || v.envreal) rows.push(['Beneficio · ' + pc(r.margin), e(r.profit), r.profit < 0 ? 'z' : 'tot']);
  rows.push(['Precio mínimo sin pérdidas', isNaN(r.be) ? '—' : e(Math.max(0, r.be))]);
  return {
    label: v.coste || v.envreal ? 'Beneficio por venta' : 'Te queda', big: e(v.coste || v.envreal ? r.profit : r.net),
    sub: 'Cliente paga ' + e(r.sale) + ' · Etsy ' + e(r.fees),
    rows: rows,
    n: { fees: r.fees, net: r.net, profit: r.profit, be: r.be, vat: r.vat }
  };
}
"""

TOOL = {
    "slug": "comisiones-etsy",
    "lang": "es",
    "twin": "etsy-fee-calculator",
    "cat": "vendedores",
    "icon": "building-store",
    "order": 10,
    "name": "Comisiones de Etsy",
    "k": "etsy tarifas vender beneficio offsite ads iva",
    "title": "Calculadora de comisiones de Etsy en España (2026)",
    "desc": "Calcula cuánto se queda Etsy por venta desde España: 6,5 %, 4 % + 0,30 €, tasa regulatoria, Offsite Ads e IVA del 21 %. Beneficio y precio mínimo.",
    "h1": "Calculadora de comisiones de Etsy",
    "intro": "Tarifas para tiendas en España, a noviembre de 2026.",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "precio", "type": "money", "label": "Precio", "value": "25"},
        {"id": "envio", "type": "money", "label": "Envío cobrado", "value": "5"},
        {"id": "coste", "type": "money", "label": "Coste producto", "value": "8"},
        {"id": "envreal", "type": "money", "label": "Envío real", "value": "4,50"},
        {"id": "ads", "type": "seg", "label": "Offsite Ads", "value": "0", "options": [("0", "No"), ("15", "15 %"), ("12", "12 %")]},
        {"id": "iva", "type": "check", "label": "IVA en comisiones", "value": True},
        {"id": "regalo", "type": "money", "label": "Envoltorio", "value": "0", "more": True, "w": "s"},
        {"id": "pub", "type": "money", "label": "Publicación", "value": "0,17", "more": True, "w": "s"},
        {"id": "tasa", "type": "number", "label": "Tasa regulatoria", "value": "0,88", "unit": "%", "step": "0.01", "more": True, "w": "s"},
        {"id": "div", "type": "check", "label": "Conversión de divisa", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Etsy · Tarifas de procesamiento de pagos por país", S.ETSY_FEES),
                ("Etsy · Política de tarifas", "https://www.etsy.com/legal/fees/"),
                ("Etsy · Tasa regulatoria desde el 22 jun 2026", S.ETSY_ROF),
                ("Ley 37/1992 del IVA, art. 84", LEY_IVA)],
    "related": ["revisar-anuncio-etsy", "precio-venta-margen", "punto-equilibrio", "comisiones-paypal"],
    "tests": [
        ({}, {"n.fees": 4.69964, "n.net": 25.30036, "n.profit": 12.80036}),
        ({"iva": False}, {"n.vat": 0, "n.fees": 3.884}),
        ({"ads": "15"}, {"n.fees": 10.14464}),
        ({"precio": "0"}, {"err": "Escribe el precio del artículo."}),
        ({"precio": "abc"}, {"err": "Revisa el precio."}),
        ({"precio": "1000", "envio": "0", "ads": "15", "iva": False, "coste": "", "envreal": ""}, {"n.fees": 199.27}),
    ],
}
