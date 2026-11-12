"""Conversor de tallas de ropa y calzado: EU / España, Reino Unido, EE. UU., Alemania, Italia, cm, letras; mujer, hombre
e infantil. English twin: size_conversion_chart.py. Tables and method in _sizes.py."""
from herramientas.tools import _sizes as Z

FROM = [("eu", "EU / España"), ("uk", "Reino Unido"), ("us", "EE. UU."), ("cm", "cm"), ("let", "Letra"), ("de", "Alemania"), ("it", "Italia")]


def n(x):
    return f"{x:g}".replace(".", ",") if isinstance(x, (int, float)) else x


def blocks(ctx):
    T = Z.tables("es")
    w = {r[0]: r for r in T["calz-mujer"]["rows"]}
    m = {r[0]: r for r in T["calz-hombre"]["rows"]}
    return [
        ("Equivalencias de calzado", f"""
<p>Un 38 europeo de mujer es un <b>{n(w[38][1])} británico</b> y un <b>{n(w[38][2])} estadounidense</b>, para un pie de unos
{n(w[38][3])} cm. Un 42 de hombre es un {n(m[42][1])} en Reino Unido y un {n(m[42][2])} en Estados Unidos. La talla
europea (punto de París) mide la horma en unidades de 2/3 de centímetro: horma en cm = talla × 2 ÷ 3. La británica cuenta
tercios de pulgada a partir de 8 1/3 pulgadas (adultos) o de 4 pulgadas (niños), y la americana suma un número a la
británica: uno en hombre, dos en mujer. Por eso un mismo número no significa lo mismo en mujer y en hombre en EE. UU.</p>
<p>Las tablas que da la calculadora salen de esas definiciones, así que valen para comparar sistemas, pero cada marca
redondea a su manera y puede variar media talla. Lo más fiable es medirte el pie: de pie, del talón a la punta del dedo más
largo, y buscar esa longitud en la columna «cm». La norma ISO 9407 (Mondopoint) etiqueta el calzado justo así, por la
longitud del pie en milímetros.</p>"""),
        ("Ropa: España no es Alemania", """
<p>En ropa de mujer, la talla española y la francesa van <b>dos números por encima</b> de la alemana y de la que usan muchas
marcas nórdicas: una 38 española es una 36 alemana, una 42 italiana, una 10 británica y una 6 estadounidense. Si compras en
una tienda alemana o holandesa, baja dos números; en una italiana, súmale cuatro a tu talla española. En hombre, chaquetas,
americanas y jerséis se miden por el contorno de pecho: una 50 europea son unas 40 pulgadas en Reino Unido y Estados Unidos.
Los pantalones de hombre van por cintura en pulgadas (la «W»): una 46 europea es una W31, una 48 es una W32.</p>
<p>En ropa infantil, la talla europea es la altura del niño en centímetros (92, 98, 104…), y en Estados Unidos se usa la edad:
2T, 3T y 4T para los pequeños. Elige por altura, no por edad: es lo que miden las tallas EU.</p>"""),
        ("Si vendes ropa o calzado", """
<p>En Etsy, Vinted o tu propia tienda, indica siempre el sistema (EU, UK, US) y las medidas en centímetros de la prenda
plana: ancho de pecho, largo, cintura y largo de pierna. Es lo que más reduce devoluciones. Si vendes a compradores de Estados
Unidos, pon la talla americana en el título o en una etiqueta, que es la que buscan.</p>"""),
    ]


FAQ = [
    ("¿Qué talla es un 38 de zapato en Estados Unidos?",
     "En mujer, un 7; en hombre, un 6. En Reino Unido, un 5 en los dos casos. Puede variar media talla según la marca."),
    ("¿Cómo convierto mi talla de ropa española a la inglesa?",
     "En mujer, resta 28: una 38 española es una 10 británica y una 6 estadounidense."),
    ("¿La talla europea de ropa es igual en Alemania y en España?",
     "No en mujer: la alemana va dos números por debajo. Una 40 española es una 38 alemana."),
    ("¿Cómo sé la talla de zapato de un niño?",
     "Mide el pie de pie, del talón al dedo más largo, y suma 1 cm de holgura. Un pie de 13 cm usa más o menos un 21 europeo."),
    ("¿Qué es la talla W en los pantalones?",
     "La cintura en pulgadas (waist). Una W32 equivale a la talla 48 europea de hombre; la L es el largo de pierna."),
]

JS = r"""
function (v, H, C) {
""" + Z.SIZES_JS + r"""
  var f = findRow(C.d.t, v.tipo, v.desde, v.talla, H.val);
  if (f.err) return { err: 'Esta tabla no usa ese sistema: elige otro en «Desde».' };
  var t = f.t, fmt = function (c) { return typeof c === 'number' ? H.num(c, c % 1 ? 1 : 0) : H.esc(c); };
  var tb = '<table class="tbl tl"><thead><tr>' + t.head.map(function (h) { return '<th>' + H.esc(h) + '</th>'; }).join('') + '</tr></thead><tbody>' +
    t.rows.map(function (r, i) { return '<tr' + (i === f.row ? ' class="on"' : '') + '>' + r.map(function (c) { return '<td>' + fmt(c) + '</td>'; }).join('') + '</tr>'; }).join('') +
    '</tbody></table>';
  if (f.row < 0) return f.miss ? { err: 'No encuentro esa talla en la tabla.' } : { html: tb, n: { row: -1 } };
  var r = t.rows[f.row], parts = [];
  r.forEach(function (c, i) { if (i !== f.col && parts.length < 3) parts.push(H.esc(t.head[i].split(' ')[0]) + ' ' + fmt(c)); });
  return { label: H.esc(t.head[f.col]) + ' ' + fmt(r[f.col]), big: parts.join(' · '),
    rows: r.map(function (c, i) { return [H.esc(t.head[i]), fmt(c), i === f.col ? 'sub' : '']; }),
    html: tb, note: 'Orientativo: cada marca puede variar media talla.', n: { row: f.row, v: r } };
}
"""

TOOL = {
    "slug": "tallas-ropa-calzado",
    "lang": "es",
    "twin": "size-conversion-chart",
    "cat": "vendedores",
    "icon": "shirt",
    "order": 110,
    "name": "Conversor de tallas",
    "k": "tallas zapatos ropa uk us eu equivalencia niño mujer hombre",
    "title": "Conversor de tallas: ropa y zapatos EU, UK y US",
    "desc": "Convierte tallas de zapatos y de ropa entre España, Europa, Reino Unido, EE. UU., Alemania e Italia, para mujer, hombre y niños, con tabla completa.",
    "h1": "Conversor de tallas de ropa y calzado",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "tipo", "type": "select", "label": "Tipo", "value": "calz-mujer", "options": Z.KINDS_ES},
        {"id": "desde", "type": "select", "label": "Desde", "value": "eu", "options": FROM},
        {"id": "talla", "type": "text", "label": "Talla", "value": "38", "w": "s", "maxlength": 8},
    ],
    "data": lambda ctx: {"t": Z.tables("es")},
    "js": JS,
    "css": Z.SIZES_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ISO 9407:2019 · Shoe sizes, Mondopoint", Z.ISO9407)],
    "related": ["generador-sku", "comisiones-vinted-wallapop", "revisar-anuncio-etsy"],
    "tests": [
        ({}, {"n.v.1": 5, "n.v.2": 7, "n.v.3": 23.8}),
        ({"tipo": "calz-hombre", "talla": "42"}, {"n.v.1": 8, "n.v.2": 9}),
        ({"tipo": "calz-hombre", "desde": "uk", "talla": "9,5"}, {"n.v.0": 44}),
        ({"tipo": "ropa-mujer", "talla": "38"}, {"n.v.1": 36, "n.v.2": 42, "n.v.3": 10, "n.v.4": 6}),
        ({"tipo": "ropa-hombre", "desde": "let", "talla": "m"}, {"n.v.0": 48}),
        ({"tipo": "calz-mujer", "talla": "60"}, {"err": "No encuentro esa talla en la tabla."}),
    ],
}
