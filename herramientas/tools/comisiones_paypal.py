"""Comisiones de PayPal en España: cobrar una venta (2,90 % + 0,35 €, recargo internacional), pago con tarjeta sin cuenta,
QR, enviar a amigos y familiares, conversión de divisa, y cuánto pedir para recibir una cifra. Spanish only: rates of
accounts registered in Spain, from PayPal's fee pages (merchant and consumer PDFs, last updated 4 Nov 2026)."""

MERCHANT = "https://www.paypal.com/es/webapps/mpp/merchant-fees"
MERCHANT_PDF = "https://www.paypalobjects.com/marketing/ua/pdf/ES/es/es-merchant-fees-04-nov-2026.pdf"
CONSUMER_PDF = "https://www.paypalobjects.com/marketing/ua/pdf/ES/es/es-es-consumer-fees-04-nov-2026.pdf"


def blocks(ctx):
    e = ctx.eur
    nat = 100 * 0.029 + 0.35
    us = 100 * (0.029 + 0.0199) + 0.35
    ask = (100 + 0.35) / (1 - 0.029)
    return [
        ("Cuánto cobra PayPal por una venta", f"""
<p>Si te pagan 100 € por un producto o servicio desde España o cualquier país del Espacio Económico Europeo, PayPal se queda
<b>{e(nat)}</b> (2,90 % + 0,35 € fijos) y recibes {e(100 - nat)}. Si el cliente paga desde Estados Unidos o cualquier país
fuera del EEE y del Reino Unido, se suma un 1,99 %: la comisión sube a {e(us)}. Desde el Reino Unido, el recargo es del
1,29 %. Para recibir 100 € limpios de un cliente español tienes que pedir <b>{e(ask)}</b>: elige «Quiero recibir».</p>
<p>Hay dos casos más baratos: cuando el cliente paga con tarjeta sin tener cuenta PayPal (1,20 % + 0,35 €) y los cobros con
código QR en persona (1,40 % + 0,05 € hasta 10 €; 0,90 % + 0,10 € a partir de 10,01 €). Si el dinero llega en otra moneda y
lo conviertes a euros, PayPal aplica un 3,0 % sobre el tipo de cambio base.</p>"""),
        ("Enviar dinero a amigos y familiares", """
<p>Enviar dinero a amigos y familiares dentro del EEE desde tu saldo o tu cuenta bancaria es <b>gratis</b> si no hay cambio de
moneda, y recibirlo también. A otros países cuesta una tarifa fija de 1,99 € (Estados Unidos, Canadá y el resto de Europa) o
3,99 € (resto del mundo), que paga quien envía. No uses «amigos y familiares» para cobrar una venta: ese pago no tiene
Protección del Vendedor ni del Comprador, y PayPal puede limitar la cuenta si detecta cobros comerciales por esa vía.</p>"""),
        ("De dónde salen las cifras", f"""
<p>Son las tarifas publicadas para cuentas registradas en España en la <a href="{MERCHANT_PDF}" rel="noopener">tabla de
tarifas para vendedores</a> y la <a href="{CONSUMER_PDF}" rel="noopener">de consumidores</a>, con fecha de 4 de noviembre de
2026. PayPal llama «nacional» a cualquier pago entre dos cuentas del EEE: un cliente de Francia o de Alemania paga lo mismo
que uno de Sevilla. Las cuentas con un volumen alto pueden negociar tarifas propias, y las donaciones a organizaciones
benéficas registradas tienen un 1,90 % + 0,35 €. Si reembolsas una venta, hacerlo no cuesta nada, pero PayPal no te devuelve
la comisión que cobró al recibirla.</p>"""),
    ]


FAQ = [
    ("¿Cuánto cobra PayPal por recibir dinero en España?",
     "Por una venta, el 2,90 % + 0,35 € si el cliente es del EEE; un 1,99 % más si es de fuera de Europa y un 1,29 % más si es "
     "del Reino Unido. Recibir dinero de amigos y familiares es gratis."),
    ("¿Cuánto tengo que cobrar para recibir 50 € por PayPal?",
     "51,85 € a un cliente del EEE: (50 + 0,35) ÷ (1 − 0,029). La calculadora lo hace con «Quiero recibir»."),
    ("¿Es gratis enviar dinero por PayPal a un amigo?",
     "Sí dentro del EEE y en euros. Fuera, 1,99 € o 3,99 € según el país, más un 3 % si hay cambio de moneda."),
    ("¿PayPal devuelve la comisión si reembolso un pago?",
     "No. Reembolsar no tiene coste, pero las comisiones que pagaste al recibir el pago no se devuelven, ni en reembolsos "
     "totales ni parciales."),
    ("¿Cuesta pasar el dinero de PayPal al banco?",
     "A una cuenta bancaria de España, no (estándar o instantánea) si no hay cambio de moneda. A una tarjeta, el 1 % del importe "
     "con mínimos y máximos."),
]

JS = r"""
function (v, H, C) {
  var e = H.eur, x = v.importe, intl = { eee: 0, uk: 1.29, resto: 1.99 }[v.origen] || 0, conv = v.div ? 3 : 0;
  if (isNaN(x) || x <= 0) return { err: 'Escribe el importe.' };
  if (v.tipo === 'amigos') {
    var f0 = v.destino === 'eee' ? 0 : v.destino === 'eur' ? 1.99 : 3.99, c0 = x * conv / 100;
    return { label: 'Te cuesta enviarlo', big: e(f0 + c0), sub: 'Recibe ' + e(x) + ' · pagas ' + e(x + f0 + c0),
      rows: [['Tarifa de envío', e(f0)], ['Conversión 3 %', e(c0)], ['Total que pagas', e(x + f0 + c0), 'tot']],
      n: { fee: f0 + c0, net: x } };
  }
  function rate(g) {
    if (v.tipo === 'qr') return g <= 10 ? [1.40, 0.05] : [0.90, 0.10];
    return [v.tipo === 'tarjeta' ? 1.20 : 2.90, 0.35];
  }
  var gross, fee, r;
  if (v.modo === 'quiero') {
    r = rate(x); gross = (x + r[1]) / (1 - (r[0] + intl + conv) / 100);
    if (v.tipo === 'qr' && gross > 10) { r = rate(11); gross = (x + r[1]) / (1 - (r[0] + intl + conv) / 100); }
  } else { gross = x; r = rate(x); }
  fee = gross * (r[0] + intl + conv) / 100 + r[1];
  var net = gross - fee;
  var rows = [['Comisión ' + H.num(r[0], 2) + ' % + ' + e(r[1]), e(gross * r[0] / 100 + r[1])]];
  if (intl) rows.push(['Recargo internacional ' + H.num(intl, 2) + ' %', e(gross * intl / 100)]);
  if (conv) rows.push(['Conversión 3 %', e(gross * conv / 100)]);
  rows.push(['Total comisión · ' + H.num(fee / gross * 100, 2) + ' %', e(fee), 'tot']);
  rows.push([v.modo === 'quiero' ? 'Pide' : 'Te pagan', e(gross), 'sub']);
  rows.push(['Recibes', e(net), 'tot']);
  return v.modo === 'quiero'
    ? { label: 'Pide', big: e(gross), sub: 'para recibir ' + e(net) + ' · comisión ' + e(fee), rows: rows, n: { gross: gross, fee: fee, net: net } }
    : { label: 'Recibes', big: e(net), sub: 'PayPal se queda ' + e(fee), rows: rows, n: { gross: gross, fee: fee, net: net } };
}
"""

COBRO = ["venta", "tarjeta", "qr"]

TOOL = {
    "slug": "comisiones-paypal",
    "lang": "es",
    "cat": "vendedores",
    "icon": "credit-card",
    "order": 60,
    "name": "Comisiones de PayPal",
    "k": "paypal tarifa cobrar recibir enviar amigos familiares internacional",
    "title": "Comisiones de PayPal 2026: cobrar, recibir y enviar",
    "desc": "Calcula la comisión de PayPal en España: 2,90 % + 0,35 € por venta, recargo internacional, QR, amigos y familiares, y cuánto pedir para recibir X €.",
    "h1": "Calculadora de comisiones de PayPal",
    "intro": "Tarifas para cuentas de España, a 4 de noviembre de 2026.",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "tipo", "type": "select", "label": "Operación", "value": "venta",
         "options": [("venta", "Cobrar una venta"), ("tarjeta", "Pago con tarjeta sin cuenta"), ("qr", "Cobro con QR"), ("amigos", "Enviar a amigos")]},
        {"id": "importe", "type": "money", "label": "Importe", "value": "100"},
        {"id": "modo", "type": "seg", "label": "Calcular", "value": "recibo", "options": [("recibo", "Me pagan"), ("quiero", "Quiero recibir")],
         "show": ("tipo", COBRO)},
        {"id": "origen", "type": "select", "label": "Cliente desde", "value": "eee", "show": ("tipo", COBRO),
         "options": [("eee", "España y EEE"), ("uk", "Reino Unido"), ("resto", "Resto del mundo")]},
        {"id": "destino", "type": "select", "label": "Destino", "value": "eee", "show": ("tipo", ["amigos"]),
         "options": [("eee", "España y EEE"), ("eur", "EE. UU., Canadá, resto de Europa"), ("resto", "Resto del mundo")]},
        {"id": "div", "type": "check", "label": "Cambio de divisa", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("PayPal · Tarifas para vendedores (ES, 4 nov 2026)", MERCHANT_PDF), ("PayPal · Tarifas para consumidores (ES, 4 nov 2026)", CONSUMER_PDF),
                ("PayPal · Tarifas de vendedor", MERCHANT)],
    "related": ["comisiones-vinted-wallapop", "comisiones-etsy", "precio-venta-margen"],
    "tests": [
        ({}, {"n.fee": 3.25, "n.net": 96.75}),
        ({"origen": "resto"}, {"n.fee": 5.24}),
        ({"modo": "quiero"}, {"n.gross": 103.347065, "n.net": 100}),
        ({"tipo": "qr", "importe": "8"}, {"n.fee": 0.162}),
        ({"tipo": "amigos", "destino": "resto", "importe": "50"}, {"n.fee": 3.99}),
        ({"importe": "0"}, {"err": "Escribe el importe."}),
    ],
}
