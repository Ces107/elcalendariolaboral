"""Comisiones de Vinted y Wallapop: lo que paga el comprador (tasa de protección + envío) y lo que recibe el vendedor.
Vinted publishes its fee (vinted.es/pricelist, updated 05.10.2026: usually 5 % + 0,70 €, VAT included). Wallapop does not
publish a table: its presets are the commonly reported tiers (0,69 € + 7,5 %, min 1,69 €, 50 € flat up to 2.500 €) and
stay editable. Spanish only (Spain-specific platforms and tax rules)."""

VINTED = "https://www.vinted.es/pricelist"
AEAT_238 = ("https://sede.agenciatributaria.gob.es/Sede/todas-gestiones/impuestos-tasas/declaraciones-informativas/"
            "modelo-238-decl_____informacion-parte-operadores-plataformas/preguntas-frecuentes/presentacion-modelo-238.html")
LIRPF = "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764"


def fee(p, pct, fix, lo=0.0, hi=0.0):
    f = fix + p * pct / 100
    f = max(f, lo)
    return min(f, hi) if hi else f


def blocks(ctx):
    v20, w20, w10, w800 = fee(20, 5, 0.70), fee(20, 7.5, 0.69, 1.69, 50), fee(10, 7.5, 0.69, 1.69, 50), fee(800, 7.5, 0.69, 1.69, 50)
    e = ctx.eur
    return [
        ("Quién paga qué", f"""
<p>En Vinted y en Wallapop, si vendes como particular, <b>no pagas comisión por vender</b>: la tasa la paga el comprador
encima del precio, junto con el envío. Por una prenda de 20 € en Vinted, el comprador paga 20 € + {e(v20)} de tasa
(0,70 € + 5 %) + el envío, y tú recibes los 20 € íntegros en tu monedero cuando confirma que le ha llegado bien. En
Wallapop, por el mismo artículo de 20 € la protección ronda los {e(w20)}.</p>
<p>Lo que sí reduce lo que te queda es el envío si lo pagas tú (las dos plataformas permiten ofrecer envío gratis o
rebajado) y los servicios de visibilidad que contrates, como destacar un artículo. La calculadora separa lo que paga el
comprador de lo que recibes, para que pongas un precio que siga siendo atractivo con la tasa incluida.</p>"""),
        ("Las tasas de cada plataforma", f"""
<p><b>Vinted</b> publica su <a href="{VINTED}" rel="noopener">lista de precios</a> (actualizada el 5 de octubre de 2026): la
«tasa de Vinted», obligatoria en cada compra con el botón Comprar, es normalmente el <b>5 % del precio + 0,70 €</b>, IVA
incluido, y puede variar según el artículo, el valor del pedido o si es un lote. La verificación opcional de artículos
cuesta 10 € (5 € la de electrónica) y también la paga el comprador.</p>
<p><b>Wallapop</b> no publica una tabla oficial: muestra el importe exacto en la pantalla de pago. Los tramos que se ven al
comprar son, de forma orientativa, 0,69 € + 7,5 % del precio, con un mínimo de 1,69 € (artículos de hasta unos 13 €) y
50 € fijos de unos 657 € a 2.500 €, que es el máximo protegido. Con esos tramos, un artículo de 10 € paga {e(w10)} y uno de
800 €, {e(w800)}. Si ves otra cifra al pagar, cámbiala en «Más opciones». Las ventas en mano no tienen tasa.</p>"""),
        ("Hacienda y los vendedores de segunda mano", f"""
<p>Desde 2024, las plataformas informan a la Agencia Tributaria (<a href="{AEAT_238}" rel="noopener">modelo 238</a>, normas
DAC7) de los vendedores que en un año hacen <b>30 ventas o más, o superan 2.000 €</b>. Que te incluyan no significa que
debas pagar: vender tu ropa o tus cosas usadas por menos de lo que te costaron no da ganancia. Si vendes algo por más de lo
que pagaste, la diferencia es una ganancia patrimonial de la base del ahorro (<a href="{LIRPF}" rel="noopener">Ley del
IRPF</a>). Comprar para revender de forma habitual ya es una actividad económica: alta de autónomo, IVA y una cuenta de
vendedor profesional, con otras condiciones.</p>"""),
    ]


FAQ = [
    ("¿Vinted cobra comisión al vendedor?",
     "No a los particulares: la tasa (normalmente 5 % + 0,70 €) la paga el comprador. El vendedor recibe el precio íntegro, "
     "salvo que pague el envío o contrate destacados."),
    ("¿Cuánto cobra Wallapop por un envío?",
     "El comprador paga el envío más una protección que Wallapop calcula según el precio; de forma orientativa, 0,69 € + 7,5 %, "
     "con un mínimo de 1,69 €. El importe exacto aparece antes de pagar."),
    ("¿Cuándo recibo el dinero de una venta?",
     "Cuando el comprador confirma que el artículo ha llegado bien o pasa el plazo para reclamar (dos días en Vinted). Después "
     "puedes pasarlo del monedero a tu cuenta bancaria."),
    ("¿Tengo que declarar lo que vendo en Vinted o Wallapop?",
     "Solo si ganas dinero: vender por encima de lo que te costó es una ganancia patrimonial. Las plataformas informan a "
     "Hacienda de quien hace 30 ventas o pasa de 2.000 € al año."),
    ("¿Me conviene ofrecer envío gratis?",
     "Hace el artículo más atractivo, pero el envío sale de tu bolsillo. Marca «Lo pago yo» y comprueba lo que te queda antes."),
]

JS = r"""
function (v, H, C) {
  var e = H.eur, p = v.precio, sh = isNaN(v.envio) ? 0 : v.envio, cost = isNaN(v.coste) ? 0 : v.coste;
  if (isNaN(p) || p <= 0) return { err: 'Escribe el precio de venta.' };
  if (sh < 0 || cost < 0 || v.pct < 0 || v.fix < 0) return { err: 'Los importes no pueden ser negativos.' };
  var pct = isNaN(v.pct) ? 0 : v.pct, fix = isNaN(v.fix) ? 0 : v.fix, lo = isNaN(v.min) ? 0 : v.min, hi = isNaN(v.max) ? 0 : v.max;
  var f = Math.max(fix + p * pct / 100, lo);
  if (hi > 0) f = Math.min(f, hi);
  var me = v.paga === 'yo', buyer = p + f + (me ? 0 : sh), get = p - (me ? sh : 0), profit = get - cost;
  var rows = [['Precio', e(p)], ['Tasa del comprador', e(f)], ['Envío · ' + (me ? 'lo pagas tú' : 'lo paga el comprador'), e(sh)],
    ['Paga el comprador', e(buyer), 'sub'], ['Recibes', e(get), 'tot']];
  if (cost) rows.push(['Beneficio', e(profit), profit < 0 ? 'z' : 'tot']);
  return { label: 'Recibes', big: e(get), sub: 'El comprador paga ' + e(buyer) + ' · tasa ' + e(f),
    rows: rows, n: { fee: f, buyer: buyer, get: get, profit: profit } };
}
"""

TOOL = {
    "slug": "comisiones-vinted-wallapop",
    "lang": "es",
    "cat": "vendedores",
    "icon": "package",
    "order": 50,
    "name": "Comisiones Vinted y Wallapop",
    "k": "vinted wallapop tasa protección comprador envío vender segunda mano",
    "title": "Comisiones de Vinted y Wallapop: cuánto recibes",
    "desc": "Calcula lo que paga el comprador en Vinted o Wallapop (tasa de protección y envío) y lo que recibes tú al vender, con envío gratis o sin él.",
    "h1": "Comisiones de Vinted y Wallapop",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "plat", "type": "seg", "label": "Plataforma", "value": "vinted", "custom": "x",
         "options": [("vinted", "Vinted", {"pct": "5", "fix": "0,70", "min": "0", "max": "0"}),
                     ("wallapop", "Wallapop", {"pct": "7,5", "fix": "0,69", "min": "1,69", "max": "50"}), ("x", "Otra")]},
        {"id": "precio", "type": "money", "label": "Precio", "value": "20"},
        {"id": "envio", "type": "money", "label": "Envío", "value": "3,50"},
        {"id": "paga", "type": "seg", "label": "Paga el envío", "value": "comprador", "options": [("comprador", "Comprador"), ("yo", "Lo pago yo")]},
        {"id": "coste", "type": "money", "label": "Te costó", "value": ""},
        {"id": "pct", "type": "number", "label": "Tasa", "value": "5", "unit": "%", "step": "0.1", "more": True, "w": "s"},
        {"id": "fix", "type": "money", "label": "Fijo", "value": "0,70", "more": True, "w": "s"},
        {"id": "min", "type": "money", "label": "Mínimo", "value": "0", "more": True, "w": "s"},
        {"id": "max", "type": "money", "label": "Máximo", "value": "0", "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Vinted · Lista de precios (5 oct 2026)", VINTED), ("Agencia Tributaria · Modelo 238 (DAC7)", AEAT_238),
                ("Ley 35/2006 del IRPF", LIRPF)],
    "related": ["comisiones-paypal", "precio-venta-margen", "comisiones-etsy", "tallas-ropa-calzado"],
    "tests": [
        ({}, {"n.fee": 1.70, "n.buyer": 25.20, "n.get": 20}),
        ({"pct": "7,5", "fix": "0,69", "min": "1,69", "max": "50"}, {"n.fee": 2.19, "n.buyer": 25.69}),
        ({"pct": "7,5", "fix": "0,69", "min": "1,69", "max": "50", "precio": "10"}, {"n.fee": 1.69}),
        ({"pct": "7,5", "fix": "0,69", "min": "1,69", "max": "50", "precio": "1000"}, {"n.fee": 50}),
        ({"paga": "yo", "coste": "12"}, {"n.get": 16.5, "n.profit": 4.5, "n.buyer": 21.70}),
        ({"precio": ""}, {"err": "Escribe el precio de venta."}),
    ],
}
