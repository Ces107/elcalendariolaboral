"""Tamaños de imagen para vendedores y creadores (Etsy, Pinterest, Instagram, YouTube, Amazon KDP y A+) con el recorte
centrado de tu foto y el factor de escala. English twin: social_media_image_sizes.py. Data in _sellers.IMG."""
from herramientas.tools import _sellers as S


def blocks(ctx):
    return [
        ("Todas las medidas", f"""
<p>Estas son las medidas recomendadas por cada plataforma en noviembre de 2026, en píxeles (ancho × alto). Elige el destino
arriba y escribe el tamaño de tu foto: la calculadora te dice cuánto hay que recortar por los lados o por arriba y abajo
para llegar a la proporción correcta, y si después tienes que reducirla o te faltan píxeles.</p>
{S.img_table("es")}"""),
        ("Un ejemplo con la foto del móvil", """
<p>Un móvil saca fotos de 4032 × 3024 píxeles (proporción 4:3). Para una <b>foto de anuncio de Etsy</b> en 4:3 no hay que
recortar nada: basta con reducirla al 66 % para dejarla en 2667 × 2000 y que pese menos de 1 MB. Para un <b>pin de
Pinterest</b> (2:3, vertical) hay que quedarse con una franja central de 2016 × 3024: se pierde la mitad de la foto, así que
conviene hacerla en vertical desde el principio. Para la <b>miniatura de YouTube</b> (16:9) se recortan 378 píxeles por
arriba y otros tantos por abajo; si la foto fuera de 1920 × 1080, habría que ampliarla al doble para llegar a 3840 × 2160 y
perdería nitidez: mejor partir de una imagen grande.</p>"""),
        ("Consejos para que no se recorte lo importante", f"""
<p>Etsy enseña la misma foto recortada en cuadrado, vertical y horizontal según la página, así que deja aire alrededor del
producto y nunca pegues texto a los bordes (<a href="{S.ETSY_IMG}" rel="noopener">guía de imágenes de Etsy</a>). En el banner
de YouTube solo la franja central de 1546 × 423 píxeles se ve en todos los dispositivos: logo y texto, ahí. En Instagram la
cuadrícula del perfil muestra los posts recortados en vertical, por lo que lo esencial debe quedar en el centro. Para la
portada de un eBook de Kindle, KDP recomienda 1600 × 2560 píxeles (<a href="{S.KDP_EBCOVER}" rel="noopener">ayuda de
KDP</a>); los módulos A+ aceptan JPG o PNG de hasta 3 MB.</p>"""),
    ]


FAQ = [
    ("¿Qué tamaño deben tener las fotos de Etsy?",
     "Al menos 2000 píxeles de ancho y de alto, con la primera foto horizontal o cuadrada. En 4:3, 2667 × 2000 px. Por debajo de "
     "635 px Etsy la posiciona peor."),
    ("¿Cuál es el tamaño de un pin de Pinterest?",
     "1000 × 1500 píxeles, proporción 2:3. Los pines más anchos pueden aparecer recortados en el feed."),
    ("¿Qué tamaño tiene la miniatura de YouTube?",
     "Proporción 16:9; YouTube recomienda 3840 × 2160 píxeles y un mínimo de 640 de ancho. Desde el móvil, máximo 2 MB."),
    ("¿Qué tamaño de imagen uso para una historia de Instagram?",
     "1080 × 1920 píxeles, proporción 9:16, la misma que para los reels."),
    ("¿Qué medidas tiene la portada de un eBook en KDP?",
     "1600 × 2560 píxeles (ancho × alto), solo la cubierta delantera."),
]

JS = r"""
function (v, H, C) {
""" + S.IMG_JS + r"""
  var t = C.d[v.dest], tw = t[0], th = t[1], n = function (x) { return H.num(x, 0); };
  var out = { label: H.esc(t[3]), big: n(tw) + ' × ' + n(th) + ' px', sub: 'Proporción ' + H.num(tw / th, 2) + ':1', n: { tw: tw, th: th } };
  if (t[2]) out.note = H.esc(t[2]);
  var iw = v.iw, ih = v.ih;
  if (!(iw > 0 && ih > 0)) return out;
  if (iw % 1 || ih % 1 || iw > 100000 || ih > 100000) return { err: 'Escribe el tamaño de tu imagen en píxeles.' };
  var c = crop(iw, ih, tw, th);
  out.rows = [['Recorte centrado', n(c.cw) + ' × ' + n(c.ch) + ' px'],
    ['Se recorta', c.lost < 0.001 ? 'Nada' : H.num(c.lost * 100, 0) + ' % · ' + (c.x ? n(c.x) + ' px por lado' : n(c.y) + ' px arriba y abajo')],
    [c.k <= 1 ? 'Reducir al' : 'Ampliar', c.k <= 1 ? H.num(c.k * 100, 0) + ' %' : '× ' + H.num(c.k, 2) + ' · pierde nitidez', c.k > 1 ? 'z' : 'tot']];
  out.html = cropSvg(iw, ih, c, 'Recorte sobre tu imagen');
  out.n.cw = c.cw; out.n.ch = c.ch; out.n.k = c.k;
  return out;
}
"""

TOOL = {
    "slug": "tamanos-imagen-redes",
    "lang": "es",
    "twin": "social-media-image-sizes",
    "cat": "vendedores",
    "icon": "photo",
    "order": 90,
    "name": "Tamaños de imagen",
    "k": "medidas fotos etsy pinterest instagram youtube miniatura banner kdp a+ píxeles",
    "title": "Tamaños de imagen 2026: Etsy, Pinterest, Instagram, YouTube",
    "desc": "Medidas en píxeles para fotos de Etsy, pines, posts e historias de Instagram, miniaturas de YouTube y portadas KDP, con el recorte exacto de tu foto.",
    "h1": "Tamaños de imagen para Etsy, redes y KDP",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "dest", "type": "select", "label": "Destino", "value": "etsy-foto", "options": [(r[0], r[1] + " · " + r[2]) for r in S.IMG]},
        {"id": "iw", "type": "number", "label": "Tu ancho", "value": "4032", "unit": "px", "w": "s"},
        {"id": "ih", "type": "number", "label": "Tu alto", "value": "3024", "unit": "px", "w": "s"},
    ],
    "data": lambda ctx: S.img_data("es"),
    "js": JS,
    "css": S.IMG_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Etsy · Requisitos de imágenes", S.ETSY_IMG), ("Pinterest · Especificaciones", S.PINTEREST),
                ("YouTube · Miniaturas personalizadas", S.YT_THUMB), ("Instagram · Resolución de fotos", S.INSTAGRAM),
                ("KDP · Portada de eBook", S.KDP_EBCOVER), ("KDP · Contenido A+", S.KDP_APLUS)],
    "related": ["revisar-anuncio-etsy", "portada-kdp-lomo", "comisiones-etsy"],
    "tests": [
        ({}, {"n.tw": 2667, "n.cw": 4032, "n.ch": 3024, "n.k": 0.661458}),
        ({"dest": "pin"}, {"n.cw": 2016, "n.ch": 3024, "n.k": 0.496032}),
        ({"dest": "yt-thumb", "iw": "1920", "ih": "1080"}, {"n.cw": 1920, "n.k": 2}),
        ({"dest": "ig-story", "iw": "", "ih": ""}, {"n.tw": 1080, "n.th": 1920}),
        ({"iw": "12.5"}, {"err": "Escribe el tamaño de tu imagen en píxeles."}),
    ],
}
