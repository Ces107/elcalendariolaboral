"""Tamaño de portada de KDP (tapa blanda) y ancho del lomo por tamaño, páginas y papel, con esquema a escala.
English twin: kdp_cover_calculator.py. Formula: KDP help G201953020 (see _sellers.py)."""
from herramientas.tools import _sellers as S

PAPER = [("bw", "Blanco · tinta negra"), ("cr", "Crema · tinta negra"), ("sc", "Color estándar"), ("pc", "Color prémium")]


def n(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


def blocks(ctx):
    a = S.cover(6, 9, 120, "bw")
    b = S.cover(5.5, 8.5, 200, "cr")
    c = S.cover(8.5, 11, 24, "pc")
    return [
        ("Medidas de la portada completa", f"""
<p>La portada de un libro de tapa blanda en KDP es un solo PDF con contraportada, lomo y portada, más <b>0,125 pulgadas
(3,2 mm) de sangrado</b> por arriba, por abajo y por los dos lados exteriores. Ancho = sangrado + contraportada + lomo +
portada + sangrado; alto = sangrado + alto del libro + sangrado. Para un libro de 6 × 9 pulgadas con 120 páginas en papel
blanco, el lomo mide {n(a["sp"], 3)} pulgadas ({n(a["sp"] * 25.4, 1)} mm) y la portada completa,
<b>{n(a["W"], 3)} × {n(a["H"])} pulgadas</b> ({n(a["W"] * 25.4, 1)} × {n(a["H"] * 25.4, 1)} mm). A 300 ppp, un lienzo de
{round(a["W"] * 300)} × {round(a["H"] * 300)} píxeles.</p>
<p>Con 200 páginas en papel crema y formato 5,5 × 8,5, el lomo pasa a {n(b["sp"], 3)} pulgadas y la portada a
{n(b["W"], 3)} × {n(b["H"])}. Un cuaderno de 8,5 × 11 con solo 24 páginas a color tiene un lomo de {n(c["sp"], 3)}
pulgadas: no cabe texto.</p>"""),
        ("El lomo según el papel", """
<ul>
<li><b>Blanco, tinta negra</b>: páginas × 0,002252 pulgadas (0,0572 mm por página).</li>
<li><b>Crema, tinta negra</b>: páginas × 0,0025 pulgadas (0,0635 mm). El crema es más grueso: el mismo libro sale con un
lomo un 11 % más ancho.</li>
<li><b>Color estándar</b>: páginas × 0,002252 pulgadas (0,0572 mm).</li>
<li><b>Color prémium</b>: páginas × 0,002347 pulgadas (0,0596 mm).</li>
</ul>
<p>«Páginas» son caras, no hojas: un PDF de interior de 120 páginas son 60 hojas. Si cambias el número de páginas después de
diseñar la portada, el lomo cambia y KDP la rechaza: rehaz la portada con la cifra final.</p>"""),
        ("Zonas seguras y texto en el lomo", """
<p>KDP solo permite texto en el lomo a partir de <b>79 páginas</b> (su Cover Creator pide 80), y ese texto debe quedar al
menos a 0,0625 pulgadas (1,6 mm) de cada borde del lomo. En portada y contraportada, deja el texto importante a 0,125
pulgadas (3,2 mm) dentro del corte, que es la línea discontinua del esquema: lo que quede en la franja rosa se recorta. La
esquina inferior derecha de la contraportada es para el código de barras que añade KDP si no pones el tuyo; no pongas nada
importante ahí.</p>
<p>El archivo debe ser un PDF con las imágenes a 300 ppp como mínimo. Para tapa dura KDP usa otra plantilla, con margen de
envoltura: esta calculadora es para tapa blanda.</p>"""),
    ]


FAQ = [
    ("¿Cuánto mide el lomo de un libro de 100 páginas en KDP?",
     "0,2252 pulgadas (5,7 mm) en papel blanco, 0,25 (6,4 mm) en crema y 0,2347 (6 mm) en color prémium."),
    ("¿Qué tamaño tiene la portada de un libro de 6 × 9?",
     "Ancho = 12,25 pulgadas + el lomo; alto = 9,25 pulgadas. Con 120 páginas blancas, 12,52 × 9,25 pulgadas (318 × 235 mm)."),
    ("¿Cuántas páginas hacen falta para poner texto en el lomo?",
     "79 como mínimo según KDP (80 si usas Cover Creator). Por debajo, deja el lomo liso o solo con color."),
    ("¿Cuánto sangrado lleva la portada de KDP?",
     "0,125 pulgadas (3,2 mm) por arriba, por abajo y en los dos bordes exteriores. No lleva sangrado en el lomo."),
    ("¿Qué resolución necesita la portada?",
     "300 ppp. Multiplica el ancho y el alto en pulgadas por 300 para saber los píxeles del lienzo."),
]

JS = r"""
function (v, H, C) {
""" + S.COVER_JS + r"""
  var w = v.w, h = v.h, p = v.pages, lim = PGL[v.paper];
  if (!(w >= 4 && w <= 8.5) || !(h >= 6 && h <= 11.69)) return { err: 'Tamaño de KDP: ancho de 4 a 8,5 y alto de 6 a 11,69 pulgadas.' };
  if (isNaN(p) || p % 1) return { err: 'Escribe el número de páginas.' };
  if (p < lim[0] || p > lim[1]) return { err: 'Con este papel, de ' + lim[0] + ' a ' + lim[1] + ' páginas.' };
  var r = cover(w, h, p, v.paper), mm = function (x) { return H.num(x * 25.4, 1) + ' mm'; }, inch = function (x, d) { return H.num(x, d || 3) + ' in'; };
  return {
    label: 'Portada completa', big: H.num(r.W, 3) + ' × ' + H.num(r.Ht, 3) + ' in',
    sub: mm(r.W) + ' × ' + mm(r.Ht) + ' · ' + Math.round(r.W * 300) + ' × ' + Math.round(r.Ht * 300) + ' px a 300 ppp',
    rows: [['Lomo', inch(r.sp) + ' · ' + mm(r.sp), 'tot'], ['Texto en el lomo', r.text ? 'Sí' : 'No (menos de 79 páginas)'],
      ['Sangrado', '0,125 in · 3,2 mm'], ['Zona segura portada', inch(w - 0.25, 2) + ' × ' + inch(h - 0.25, 2)]],
    html: coverSvg(w, h, r, { back: 'Contraportada', front: 'Portada', spine: 'Lomo', alt: 'Esquema de la portada' }) +
      '<ul class="kc-leg"><li><i style="background:#f6d5d9"></i>Sangrado</li><li><i style="background:#e8eef6"></i>Lomo</li>' +
      '<li><i style="border:1px dashed #0b4f8c"></i>Zona segura</li></ul>',
    n: { sp: r.sp, W: r.W, H: r.Ht }
  };
}
"""

TOOL = {
    "slug": "portada-kdp-lomo",
    "lang": "es",
    "twin": "kdp-cover-calculator",
    "cat": "vendedores",
    "icon": "ruler-measure",
    "order": 40,
    "name": "Portada KDP y lomo",
    "k": "amazon kdp portada lomo sangrado medidas plantilla tapa blanda",
    "title": "Calculadora de portada KDP y ancho del lomo",
    "desc": "Calcula el tamaño de la portada completa de tu libro en KDP y el ancho del lomo según formato, páginas y papel, en pulgadas, mm y píxeles a 300 ppp.",
    "h1": "Tamaño de portada y lomo para KDP",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "trim", "type": "select", "label": "Tamaño", "value": "6x9", "custom": "x",
         "options": [(S.trim_value(w, h), S.trim_label(w, h), {"w": n(w, 2).rstrip("0").rstrip(","), "h": n(h, 2).rstrip("0").rstrip(",")})
                     for w, h in S.TRIMS] + [("x", "Personalizado")]},
        {"id": "w", "type": "number", "label": "Ancho", "value": "6", "unit": "in", "step": "0.01", "w": "s"},
        {"id": "h", "type": "number", "label": "Alto", "value": "9", "unit": "in", "step": "0.01", "w": "s"},
        {"id": "pages", "type": "number", "label": "Páginas", "value": "120", "w": "s"},
        {"id": "paper", "type": "select", "label": "Papel", "value": "bw", "options": PAPER},
    ],
    "js": JS,
    "css": S.COVER_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("KDP · Crear una portada de tapa blanda", S.KDP_COVER), ("KDP · Coste de impresión y tamaños", S.KDP_PRINT)],
    "related": ["regalias-kdp", "tamanos-imagen-redes", "precio-venta-margen"],
    "tests": [
        ({}, {"n.sp": 0.27024, "n.W": 12.52024, "n.H": 9.25}),
        ({"w": "5,5", "h": "8,5", "pages": "200", "paper": "cr"}, {"n.sp": 0.5, "n.W": 11.75, "n.H": 8.75}),
        ({"w": "8.5", "h": "11", "pages": "100", "paper": "pc"}, {"n.W": 17.4847}),
        ({"pages": "20"}, {"err": "Con este papel, de 24 a 828 páginas."}),
        ({"w": "3"}, {"err": "Tamaño de KDP: ancho de 4 a 8,5 y alto de 6 a 11,69 pulgadas."}),
        ({"pages": "700", "paper": "sc"}, {"err": "Con este papel, de 72 a 600 páginas."}),
    ],
}
