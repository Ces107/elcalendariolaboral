"""Regalías de KDP (Amazon): tapa blanda (coste de impresión, 60 % / 50 % según el precio, distribución ampliada) y eBook
(70 % / 35 %, coste de entrega por MB, IVA). English twin: kdp_royalty_calculator.py. Tables in _sellers.py."""
from herramientas.tools import _sellers as S

INK = [("bw", "Negro"), ("sc", "Color estándar"), ("pc", "Color prémium")]


def data(ctx=None):
    d = S.kdp_data()
    d["trims"] = {S.trim_value(w, h): S.is_large(w, h) for w, h in S.TRIMS}
    return d


def blocks(ctx):
    m = S.fm
    a = S.kdp_pb("eu", "bw", 120, False, 9.99)
    b = S.kdp_pb("eu", "bw", 120, False, 9.98)
    c = S.kdp_pb("eu", "bw", 300, False, 14.99)
    col = S.kdp_pb("eu", "pc", 100, True, 19.99)
    eb7 = 0.7 * (4.99 / 1.04 - 0.12 * 2)
    eb3 = 0.35 * 4.99 / 1.04
    return [
        ("Cuánto ganas por libro", f"""
<p>Un libro de bolsillo de 6 × 9 pulgadas, 120 páginas en blanco y negro, vendido en Amazon.es a 9,99 €: imprimirlo cuesta
{m(a["cost"])} (0,75 € fijos + 120 × 0,012 €) y KDP te paga el 60 % del precio menos esa impresión, <b>{m(a["roy"])}</b> por
ejemplar. Si lo pones a 9,98 €, un céntimo menos, la regalía cae al 50 % y te quedan {m(b["roy"])}: pierdes
{m(a["roy"] - b["roy"])} por libro. Con 300 páginas a 14,99 € la impresión sube a {m(c["cost"])} y ganas {m(c["roy"])}.</p>
<p>El color se paga caro: un cuaderno de 8,5 × 11 pulgadas a todo color prémium con 100 páginas cuesta {m(col["cost"])} de
imprimir y a 19,99 € deja {m(col["roy"])}. Antes de fijar el precio, mira la línea «Precio mínimo»: por debajo, KDP no te
deja publicar.</p>"""),
        ("El umbral del 60 %", """
<p>Para tapa blanda, KDP paga el <b>60 %</b> del precio de venta solo si es de al menos <b>9,99 €</b> en Amazon.es, .de,
.fr, .it y .nl (9,99 $ en Amazon.com, 7,99 £ en Amazon.co.uk, 13,99 en Canadá y Australia, 1.000 ¥ en Japón, 40 zł en
Polonia y 110 kr en Suecia). Por debajo, el <b>50 %</b>. La fórmula es la misma en los dos casos: regalía = porcentaje ×
precio − coste de impresión. El precio que pones en KDP para las tiendas europeas es sin IVA: Amazon suma el IVA de libros
del país (4 % en España) y el comprador ve, por ejemplo, 10,39 € por un libro a 9,99 €.</p>
<p>La <b>distribución ampliada</b> (librerías y bibliotecas de Estados Unidos) paga el 40 % del precio de Amazon.com menos
la impresión; con libros finos y baratos suele salir a cero o negativa, y entonces KDP exige subir el precio.</p>"""),
        ("Cómo se calcula la impresión", f"""
<p>En las tiendas en euros, un libro en blanco y negro de 24 a 110 páginas cuesta 2,05 € fijos (2,48 € en tamaño grande);
a partir de ahí, 0,75 € más 0,012 € por página (0,016 € en grande). El color prémium cuesta 2,85 € hasta 40 páginas y luego
0,75 € + 0,0525 € por página (0,0715 € en grande); el color estándar, de 72 a 600 páginas, 0,75 € + 0,024 € por página. Es
tamaño grande todo lo que mida más de 6,12 pulgadas (155,5 mm) de ancho o más de 9 (228,6 mm) de alto: el 6,14 × 9,21 ya lo
es. El papel crema o blanco no cambia el precio.</p>"""),
        ("eBook: 70 % o 35 %", f"""
<p>Un eBook en Amazon.es a 4,99 € con el 70 %: KDP quita el IVA del 4 %, resta el coste de entrega (0,12 € por MB) y te paga
el 70 % del resto. Con un archivo de 2 MB son <b>{m(eb7)}</b>; con el 35 % serían {m(eb3)}, sin coste de entrega. El 70 %
solo se aplica entre 2,69 € y 12,99 € (2,99–12,99 $ en Amazon.com y 1,77–12,99 £ en Reino Unido) y si el eBook cuesta al
menos un 20 % menos que la edición impresa. Los libros con muchas imágenes pesan: a partir de unos 10 MB, el 35 % puede
salir mejor.</p>"""),
    ]


FAQ = [
    ("¿Cuánto paga KDP por un libro de tapa blanda?",
     "El 60 % del precio de venta menos el coste de impresión si el precio es de 9,99 € o más; el 50 % si es menor. Un libro de "
     "120 páginas en blanco y negro a 9,99 € deja unos 3,80 € en Amazon.es."),
    ("¿Por qué no puedo poner mi libro a 4,99 €?",
     "Porque KDP no deja publicar a un precio cuya regalía no cubra la impresión. El mínimo es la impresión ÷ 0,5; si eso pasa de "
     "9,99 €, la impresión ÷ 0,6."),
    ("¿El precio de KDP lleva IVA?",
     "En tapa blanda para Europa, no: Amazon añade el IVA de libros encima. En eBook, sí: el precio que pones incluye el IVA y "
     "KDP lo descuenta antes de calcular la regalía."),
    ("¿Cuánto cuesta imprimir un libro en KDP?",
     "En euros, 0,75 € más 0,012 € por página en blanco y negro (2,05 € fijos hasta 110 páginas). Un libro de 200 páginas cuesta "
     "3,15 €."),
    ("¿Cuándo me paga Amazon las regalías?",
     "Unos 60 días después del final del mes de la venta, por transferencia, cuando superas el mínimo de pago de cada tienda."),
]

JS = r"""
function (v, H, C) {
""" + S.FMT_JS + S.KDP_JS + r"""
  var D = C.d, mk = D.mk[v.mk], cur = mk.cur, e = function (x) { return fm(x, cur); };
  if (isNaN(v.precio) || v.precio <= 0) return { err: 'Escribe el precio de venta.' };
  if (v.fmt === 'eb') {
    var g = mk.g;
    if (!D.eb[g]) return { err: 'eBook: elige Amazon.com, .co.uk, .ca, .com.au o una tienda en euros.' };
    var E = D.eb[g], vat = E.vat === null ? D.ebvat[v.mk] : E.vat, mb = isNaN(v.mb) || v.mb < 0 ? 0 : v.mb;
    var min35 = E.min35[mb < 3 ? 0 : mb < 10 ? 1 : 2];
    if (v.precio < min35) return { err: 'Precio mínimo para ' + H.num(mb, 1) + ' MB: ' + e(min35) + '.' };
    if (v.precio > E.max) return { err: 'Precio máximo: ' + e(E.max) + '.' };
    var net = v.precio / (1 + vat / 100), del = Math.max(0.01, mb * E.mb), in70 = v.precio >= E.band[0] && v.precio <= E.band[1];
    var r70 = 0.7 * (net - del), r35 = 0.35 * net, best = in70 && r70 > r35 ? r70 : r35;
    var rows = [['Precio sin IVA ' + pc(vat, false, vat % 1 ? 1 : 0), e(net)], ['Entrega ' + H.num(mb, 1) + ' MB', in70 ? '−' + e(del) : '—']];
    rows.push(['Regalía 70 %', in70 ? e(r70) : 'solo de ' + e(E.band[0]) + ' a ' + e(E.band[1]), in70 && r70 >= r35 ? 'tot' : '']);
    rows.push(['Regalía 35 %', e(r35), in70 && r70 >= r35 ? '' : 'tot']);
    return { label: 'Regalía por eBook', big: e(best), sub: (best === r35 ? '35 %' : '70 %') + ' · ' + mk.lab,
      rows: rows, n: { roy: best, r70: in70 ? r70 : null, r35: r35 } };
  }
  var pages = v.pages, lim = D.pages[v.ink];
  if (isNaN(pages) || pages % 1) return { err: 'Escribe el número de páginas.' };
  if (pages < lim[0] || pages > lim[1]) return { err: 'Con esta tinta, de ' + lim[0] + ' a ' + lim[1] + ' páginas.' };
  if (v.ink === 'sc' && !D.cost[mk.g].sc) return { err: 'Color estándar no disponible en esta tienda.' };
  var large = !!D.trims[v.trim], r = kdpPb(D, mk.g, v.ink, pages, large, v.precio);
  var rows2 = [['Impresión' + (large ? ' · tamaño grande' : ''), e(r.cost)], ['Regalía ' + (r.rate * 100) + ' %', e(r.roy), 'tot']];
  if (r.rate < 0.6) rows2.push(['A ' + e(r.t60) + ' (60 %)', e(r.at60), 'sub']);
  rows2.push(['Precio mínimo', e(r.min)]);
  if (mk.vat !== null) rows2.push(['En tienda con IVA ' + pc(mk.vat, false, mk.vat % 1 ? 1 : 0), e(v.precio * (1 + mk.vat / 100))]);
  if (v.mk === 'com') rows2.push(['Distribución ampliada 40 %', r.ed > 0 ? e(r.ed) : 'sube el precio']);
  if (r.roy < 0) return { err: 'A este precio no cubres la impresión (' + e(r.cost) + '). Mínimo: ' + e(r.min) + '.' };
  return { label: 'Regalía por libro', big: e(r.roy), sub: 'Impresión ' + e(r.cost) + ' · ' + (r.rate * 100) + ' % de ' + e(v.precio),
    rows: rows2, n: { roy: r.roy, cost: r.cost, min: r.min, rate: r.rate } };
}
"""

TOOL = {
    "slug": "regalias-kdp",
    "lang": "es",
    "twin": "kdp-royalty-calculator",
    "cat": "vendedores",
    "icon": "book",
    "order": 30,
    "name": "Regalías de KDP",
    "k": "amazon kdp regalías royalties impresión tapa blanda ebook autopublicar",
    "title": "Calculadora de regalías de KDP: tapa blanda y eBook",
    "desc": "Calcula tu regalía en Amazon KDP: coste de impresión por páginas y tinta, 60 % desde 9,99 € o 50 %, eBook al 70 % o 35 % con IVA y entrega.",
    "h1": "Calculadora de regalías de Amazon KDP",
    "intro": "Tarifas de KDP a noviembre de 2026.",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "fmt", "type": "seg", "label": "Formato", "value": "pb", "options": [("pb", "Tapa blanda"), ("eb", "eBook")]},
        {"id": "mk", "type": "select", "label": "Tienda", "value": "es", "options": [(k, lab) for k, lab, *_ in S.KDP_MK]},
        {"id": "precio", "type": "number", "label": "Precio", "value": "9,99", "step": "0.01", "w": "s"},
        {"id": "ink", "type": "select", "label": "Tinta", "value": "bw", "options": INK, "show": ("fmt", ["pb"])},
        {"id": "trim", "type": "select", "label": "Tamaño", "value": "6x9", "show": ("fmt", ["pb"]),
         "options": [(S.trim_value(w, h), S.trim_label(w, h)) for w, h in S.TRIMS]},
        {"id": "pages", "type": "number", "label": "Páginas", "value": "120", "w": "s", "show": ("fmt", ["pb"])},
        {"id": "mb", "type": "number", "label": "Archivo", "value": "2", "unit": "MB", "step": "0.1", "w": "s", "show": ("fmt", ["eb"])},
    ],
    "data": data,
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("KDP · Coste de impresión de tapa blanda", S.KDP_PRINT), ("KDP · Regalías de tapa blanda", S.KDP_ROY),
                ("KDP · Requisitos de precio de eBooks", S.KDP_EB), ("KDP · Costes de entrega de eBooks", S.KDP_DEL)],
    "related": ["portada-kdp-lomo", "precio-venta-margen", "punto-equilibrio", "comisiones-etsy"],
    "tests": [
        ({}, {"n.roy": 3.804, "n.cost": 2.19, "n.rate": 0.6}),
        ({"precio": "9,98"}, {"n.roy": 2.80, "n.rate": 0.5}),
        ({"mk": "com", "ink": "pc", "trim": "8.5x11", "pages": "100", "precio": "19.99"}, {"n.roy": 2.994, "n.cost": 9.0, "n.min": 15.0}),
        ({"pages": "20"}, {"err": "Con esta tinta, de 24 a 828 páginas."}),
        ({"fmt": "eb", "mk": "com", "precio": "4.99", "mb": "2"}, {"n.roy": 3.283}),
        ({"fmt": "eb", "mk": "es", "precio": "4,99", "mb": "1"}, {"n.roy": 3.274654}),
    ],
}
