"""Punto de equilibrio: unidades y facturación para cubrir los costes fijos, con comisiones de venta y beneficio objetivo.
English twin: break_even_calculator.py (same core). Formula: cost-volume-profit analysis (OpenStax, Principles of
Managerial Accounting, 3.2; formula reimplemented, no text copied)."""
import math

OPENSTAX = "https://openstax.org/books/principles-managerial-accounting/pages/3-2-calculate-a-break-even-point-in-units-and-dollars"

CORE_JS = r"""
  /* fixed costs F, unit price P (before tax), variable cost per unit V, fee % of the price, target profit T */
  function be(F, P, V, fee, T) {
    var cm = P * (1 - fee / 100) - V;
    if (!(cm > 0)) return null;
    var u = (F + T) / cm, uc = Math.ceil(u - 1e-9);
    return { cm: cm, ratio: cm / P, u: u, uc: uc, rev: uc * P, revx: (F + T) / (cm / P),
      at: [0.5, 1, 1.5, 2].map(function (k) { var n = Math.max(1, Math.round(uc * k)); return [n, n * P, n * cm - F]; }) };
  }
"""


def be(F, P, V, fee=0.0, T=0.0):
    cm = P * (1 - fee / 100) - V
    u = (F + T) / cm
    return {"cm": cm, "u": u, "uc": math.ceil(u - 1e-9), "revx": (F + T) / (cm / P)}


def blocks(ctx):
    e = ctx.eur
    a = be(600, 25, 9)
    b = be(600, 25, 9, 13)
    c = be(600, 25, 9, 13, 400)
    return [
        ("Cuántas ventas necesitas", f"""
<p>Una tienda online con <b>600 € al mes de costes fijos</b> (cuota de autónomo, tienda, software, local o almacenaje) que
vende un producto a 25 € sin IVA y le cuesta 9 € fabricarlo y enviarlo gana 16 € por unidad para cubrir esos fijos: es el
<b>margen de contribución</b>. 600 ÷ 16 = {ctx.num(a["u"], 1)}, así que necesita vender <b>{a["uc"]} unidades al mes</b>
(unas {math.ceil(a["uc"] / 30 * 7)} por semana) para no perder dinero. A partir de la unidad {a["uc"] + 1}, cada venta deja 16 € de
beneficio.</p>
<p>Si vende en un marketplace que se queda un 13 % del precio, el margen de contribución baja a {e(b["cm"])} y el punto de
equilibrio sube a <b>{b["uc"]} unidades</b>. Para ganar además 400 € al mes harían falta {c["uc"]}. Las comisiones no
parecen gran cosa en una venta y cambian por completo el número de ventas que necesitas.</p>"""),
        ("La fórmula", f"""
<p>Punto de equilibrio en unidades = costes fijos ÷ (precio − coste variable por unidad). En facturación = costes fijos ÷
ratio de margen de contribución, donde el ratio es (precio − coste variable) ÷ precio. En el ejemplo, 16 ÷ 25 = 0,64 y
600 ÷ 0,64 = {e(a["revx"])} de ventas al mes. Con un beneficio objetivo, súmalo a los costes fijos: (600 + 400) ÷ margen. Es
el análisis coste-volumen-beneficio de cualquier manual de contabilidad de gestión, como el de <a href="{OPENSTAX}"
rel="noopener">OpenStax</a>.</p>"""),
        ("Qué poner en cada casilla", """
<ul>
<li><b>Costes fijos</b>: lo que pagas aunque no vendas nada en el mes: cuota de autónomo, alquiler, suscripciones, seguros,
gestoría, la parte fija de los anuncios.</li>
<li><b>Precio</b>: el precio de venta sin IVA, porque el IVA no es tuyo.</li>
<li><b>Coste por unidad</b>: materiales, embalaje, envío si lo pagas tú, impresión bajo demanda; todo lo que crece con
cada venta.</li>
<li><b>Comisiones</b>: el porcentaje del precio que se queda la plataforma o la pasarela de pago (Etsy, Amazon, PayPal,
TPV).</li>
</ul>
<p>Si no sabes qué costes son fijos y cuáles variables, pregúntate si se duplicarían al duplicar las ventas: si sí, son
variables.</p>"""),
    ]


FAQ = [
    ("¿Qué es el punto de equilibrio?",
     "El número de ventas en el que los ingresos cubren justo todos los costes: ni ganas ni pierdes. Por debajo pierdes dinero; "
     "por encima, cada venta deja su margen de contribución como beneficio."),
    ("¿Cómo se calcula el punto de equilibrio en unidades?",
     "Costes fijos ÷ (precio − coste variable por unidad). Con 600 € de fijos, un precio de 25 € y 9 € de coste: 37,5, es decir, "
     "38 unidades."),
    ("¿Se incluye el IVA en el precio?",
     "No. Usa el precio sin IVA: el IVA lo cobras para Hacienda y no cubre costes."),
    ("¿Cómo bajo mi punto de equilibrio?",
     "Subiendo el precio, bajando el coste por unidad o reduciendo costes fijos. Subir el precio suele ser lo que más mueve: "
     "un 10 % más de precio puede recortar bastante más de un 10 % las ventas necesarias."),
    ("¿Cuenta mi sueldo como coste fijo?",
     "Si quieres que el negocio te pague un sueldo, sí: súmalo a los costes fijos o ponlo como beneficio deseado."),
]

JS = r"""
function (v, H, C) {
""" + CORE_JS + r"""
  var F = v.fijos, P = v.precio, V = isNaN(v.variable) ? 0 : v.variable, fee = isNaN(v.com) ? 0 : v.com, T = isNaN(v.obj) ? 0 : v.obj;
  if (isNaN(F) || F < 0) return { err: 'Escribe los costes fijos del mes.' };
  if (isNaN(P) || P <= 0) return { err: 'Escribe el precio de venta.' };
  if (V < 0 || T < 0 || fee < 0 || fee >= 100) return { err: 'Revisa los importes.' };
  var r = be(F, P, V, fee, T), e = H.eur;
  if (!r) return { err: 'El precio no cubre el coste por unidad: cada venta pierde dinero.' };
  var tb = '<table class="tbl"><thead><tr><th>Unidades</th><th class="num">Ventas</th><th class="num">Resultado</th></tr></thead><tbody>' +
    r.at.map(function (x) { return '<tr><td>' + x[0] + '</td><td class="num">' + e(x[1]) + '</td><td class="num"' + (x[2] < 0 ? ' style="color:var(--red)"' : '') + '>' + e(x[2]) + '</td></tr>'; }).join('') +
    '</tbody></table>';
  return {
    label: T ? 'Unidades para ganar ' + e(T) : 'Punto de equilibrio', big: r.uc + ' ' + (r.uc === 1 ? 'unidad' : 'unidades'),
    sub: 'Facturación ' + e(r.rev) + ' · unas ' + Math.ceil(r.uc / 30) + ' al día',
    rows: [['Margen por unidad', e(r.cm)], ['Ratio de margen', H.num(r.ratio * 100, 1) + ' %'], ['Equilibrio en ventas', e(r.revx), 'tot']],
    html: tb, n: { uc: r.uc, cm: r.cm, revx: r.revx }
  };
}
"""

TOOL = {
    "slug": "punto-equilibrio",
    "lang": "es",
    "twin": "break-even-calculator",
    "cat": "vendedores",
    "icon": "chart-line",
    "order": 80,
    "name": "Punto de equilibrio",
    "k": "umbral rentabilidad unidades ventas costes fijos margen contribución",
    "title": "Calcular el punto de equilibrio: unidades y ventas",
    "desc": "Calcula cuántas unidades tienes que vender al mes para cubrir tus costes fijos, con el precio, el coste por unidad y las comisiones de venta.",
    "h1": "Calculadora de punto de equilibrio",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "fijos", "type": "money", "label": "Costes fijos / mes", "value": "600"},
        {"id": "precio", "type": "money", "label": "Precio sin IVA", "value": "25"},
        {"id": "variable", "type": "money", "label": "Coste por unidad", "value": "9"},
        {"id": "com", "type": "number", "label": "Comisiones", "value": "0", "unit": "%", "step": "0.1", "w": "s"},
        {"id": "obj", "type": "money", "label": "Beneficio deseado", "value": "0", "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("OpenStax · Principles of Managerial Accounting, 3.2 Break-even point", OPENSTAX)],
    "related": ["precio-venta-margen", "comisiones-etsy", "regalias-kdp"],
    "tests": [
        ({}, {"n.uc": 38, "n.cm": 16, "n.revx": 937.5}),
        ({"com": "13"}, {"n.uc": 48, "n.cm": 12.75}),
        ({"obj": "400"}, {"n.uc": 63}),
        ({"precio": "9"}, {"err": "El precio no cubre el coste por unidad: cada venta pierde dinero."}),
        ({"fijos": ""}, {"err": "Escribe los costes fijos del mes."}),
        ({"fijos": "0"}, {"n.uc": 0}),
    ],
}
