"""Revisar un anuncio de Etsy antes de publicarlo: título (140 caracteres, caracteres válidos, % : & + una sola vez,
palabras repetidas, mayúsculas) y etiquetas (13, 20 caracteres, caracteres válidos, duplicadas).
English twin: etsy_listing_checker.py. Rules: Etsy Open API v3 (title / tags), see _sellers.py."""
from herramientas.tools import _sellers as S

STOP = "de del la las el los un una unos unas y o para con sin por en al a que su sus tu mi".split()

MSG = {
    "tEmpty": "Escribe el título.",
    "tLong": "Título: sobran {} caracteres (máximo 140).",
    "tChars": "Título: Etsy no acepta {}.",
    "tOnce": "Título: {} — Etsy solo admite una vez cada uno de % : & +.",
    "tCaps": "{} palabras en mayúsculas: déjalo en una o dos.",
    "tRep": "Palabras repetidas en el título: {}.",
    "tWords": "{} palabras: en el móvil solo se ven las primeras; pon delante qué es el producto.",
    "gNone": "Pega tus etiquetas separadas por comas.",
    "gMany": "{} etiquetas: el máximo es 13.",
    "gFew": "Te quedan {} etiquetas libres: úsalas todas.",
    "gLong": "Más de 20 caracteres: {}.",
    "gChars": "Etiquetas con caracteres no válidos: {}.",
    "gDup": "Etiquetas duplicadas: {}.",
    "gOne": "{} etiquetas de una sola palabra: mejor frases de 2-3 palabras.",
}

EX_T = "Taza personalizada con nombre, taza de café con nombre, regalo para mamá, taza cerámica 350 ml"
EX_G = "taza personalizada, taza con nombre, regalo para mama, taza de ceramica, regalo dia de la madre, taza"


def blocks(ctx):
    return [
        ("Qué revisa", """
<p>Pega el título y las etiquetas tal como los vas a subir. La herramienta aplica las mismas reglas con las que Etsy rechaza
un anuncio y señala en rojo lo que no te dejará guardar: más de <b>140 caracteres</b> en el título, caracteres no admitidos
(como <code>$</code>, <code>^</code> o los emojis), repetir <b>%</b>, <b>:</b>, <b>&amp;</b> o <b>+</b>, más de <b>13
etiquetas</b>, etiquetas de más de <b>20 caracteres</b> o con símbolos distintos de letras, números, espacios, guion y
apóstrofo. En amarillo, lo que Etsy acepta pero te resta: palabras repetidas en el título, mayúsculas, etiquetas sin usar,
etiquetas duplicadas o de una sola palabra.</p>"""),
        ("Un ejemplo corregido", f"""
<p>Este título es típico de las tiendas que empiezan: <i>{EX_T}</i>. Tiene {len(EX_T)} caracteres y 16 palabras, así que cabe, pero repite
«taza» tres veces y «nombre» dos. Etsy ya no premia repetir palabras: el buscador lee el título, las etiquetas, la categoría
y los atributos juntos, y una palabra que ya aparece una vez no suma por estar dos. Mejor: <i>Taza personalizada con nombre,
cerámica 350 ml, regalo para mamá o día de la madre</i>, y las variantes («taza de café con nombre», «taza regalo mamá») a
las etiquetas.</p>
<p>Sus etiquetas, <i>{EX_G}</i>, dejan siete huecos libres de trece, «regalo dia de la madre» tiene 22 caracteres y Etsy no la acepta («regalo
día madre» sí cabe), y la última es una sola palabra que no compite con nadie.
Cada etiqueta es una búsqueda completa que la gente escribe: «taza nombre niño», «regalo abuela taza», «taza boda
invitados». Usa las trece y no repitas la categoría, que Etsy ya cuenta.</p>"""),
        ("Las reglas exactas de Etsy", f"""
<p>Según la documentación de la <a href="{S.ETSY_API}" rel="noopener">API abierta de Etsy (v3)</a>, un título válido solo
contiene letras, números, signos de puntuación, símbolos matemáticos, espacios y ™ © ®, y los caracteres %, :, &amp; y +
solo pueden aparecer una vez cada uno. Las etiquetas solo admiten letras, números, espacios, guion (-), apóstrofo (') y
™ © ®: nada de puntos, barras ni almohadillas. Son reglas técnicas, no de posicionamiento: si las incumples, el anuncio no se
guarda o la etiqueta se rechaza.</p>
<p>Las tildes y la ñ son letras y están permitidas. Para buscar repeticiones, esta herramienta compara sin tildes ni
mayúsculas: «Mamá» y «mama» cuentan como la misma palabra, y «de», «con» o «para» no cuentan. Si una palabra aparece dos
veces porque forma parte de dos búsquedas distintas, el aviso es orientativo: decide tú.</p>"""),
    ]


FAQ = [
    ("¿Cuántos caracteres puede tener un título de Etsy?",
     "140 como máximo, espacios incluidos. En los resultados del móvil solo se ven unas pocas palabras, así que empieza por lo "
     "que es el producto."),
    ("¿Cuántas etiquetas puedo poner en Etsy?",
     "13 por anuncio, de hasta 20 caracteres cada una. Pueden ser frases de varias palabras, y conviene que lo sean."),
    ("¿Por qué Etsy no me deja guardar el título?",
     "Casi siempre por repetir %, :, &amp; o + (solo se permite una vez cada uno), por un símbolo no admitido como $ o un emoji, "
     "o por pasar de 140 caracteres."),
    ("¿Sirve repetir palabras en el título?",
     "No. Etsy combina el título con las etiquetas, la categoría y los atributos; repetir una palabra no la hace más relevante "
     "y ocupa espacio que podrías usar para otra búsqueda."),
    ("¿Las etiquetas tienen que coincidir con el título?",
     "No hace falta. Pon en el título lo esencial y usa las etiquetas para sinónimos, ocasiones y variantes que no caben arriba."),
]

JS = r"""
function (v, H, C) {
""" + S.LISTING_JS + r"""
  var STOP = {}; C.d.stop.forEach(function (w) { STOP[w] = 1; });
  var M = C.d.msg, r = checkListing(v.titulo, v.tags, STOP);
  var ne = r.issues.filter(function (x) { return x[0] === 'e'; }).length, nw = r.issues.length - ne;
  var li = r.issues.map(function (x) {
    return '<li class="ck-' + x[0] + '">' + H.esc(M[x[1]].replace('{}', x[2] === undefined ? '' : x[2])) + '</li>';
  }).join('');
  var chips = r.tags.map(function (g) {
    return '<li class="' + (g[1] > 20 || g[2] ? 'ck-e' : '') + '">' + H.esc(g[0]) + ' <b>' + g[1] + '</b></li>';
  }).join('');
  return {
    label: 'Revisión del anuncio', big: ne ? ne + (ne === 1 ? ' error' : ' errores') : (nw ? 'Se puede mejorar' : 'Listo'),
    sub: nw + (nw === 1 ? ' aviso' : ' avisos'),
    rows: [['Título', r.tlen + ' / 140'], ['Palabras', r.words], ['Etiquetas', r.tags.length + ' / 13']],
    html: (li ? '<ul class="ck">' + li + '</ul>' : '') + (chips ? '<ul class="ck-g">' + chips + '</ul>' : ''),
    n: { e: ne, w: nw, tlen: r.tlen, tags: r.tags.length, codes: r.issues.map(function (x) { return x[1]; }).join(' ') }
  };
}
"""

CSS = (".ck{list-style:none;padding:0;margin:14px 0}.ck li{padding:6px 10px 6px 12px;margin:4px 0;border-left:4px solid #e0a800;background:var(--bg2)}"
       ".ck li.ck-e{border-left-color:var(--red)}.ck-g{list-style:none;padding:0;display:flex;flex-wrap:wrap;gap:6px}"
       ".ck-g li{border:1px solid var(--line);border-radius:14px;padding:3px 10px;font-size:14px}.ck-g li b{color:var(--mut);font-weight:400}"
       ".ck-g li.ck-e{border-color:var(--red);color:var(--red)}#titulo,#tags{width:min(640px,100%)}")

TOOL = {
    "slug": "revisar-anuncio-etsy",
    "lang": "es",
    "twin": "etsy-listing-checker",
    "cat": "vendedores",
    "icon": "list-check",
    "order": 20,
    "name": "Revisar anuncio de Etsy",
    "k": "etsy título etiquetas tags seo caracteres",
    "title": "Revisar título y etiquetas de Etsy: 140 caracteres y 13 tags",
    "desc": "Comprueba tu anuncio de Etsy antes de publicarlo: título de 140 caracteres, % : & una sola vez, 13 etiquetas de 20 caracteres y palabras repetidas.",
    "h1": "Revisar título y etiquetas de Etsy",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "titulo", "type": "text", "label": "Título", "value": EX_T, "w": "xl"},
        {"id": "tags", "type": "text", "label": "Etiquetas (comas)", "value": EX_G, "w": "xl"},
    ],
    "data": {"stop": STOP, "msg": MSG},
    "js": JS,
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Etsy Open API v3 · createDraftListing (title, tags)", S.ETSY_API)],
    "related": ["comisiones-etsy", "tamanos-imagen-redes", "generador-sku", "precio-venta-margen"],
    "tests": [
        ({}, {"n.e": 1, "n.tlen": len(EX_T), "n.tags": 6, "n.codes": "tRep tWords gFew gLong"}),
        ({"titulo": "Pendientes 50% plata & oro & cobre: 100% hechos a mano: ok", "tags": ""}, {"n.e": 3}),
        ({"titulo": "x" * 141, "tags": "a"}, {"n.codes": "tLong gFew"}),
        ({"titulo": "Taza $ barata", "tags": "taza, taza, una etiqueta demasiado larga, oferta!"}, {"n.e": 4}),
        ({"titulo": "", "tags": ",".join(f"etiqueta {i}" for i in range(14))}, {"n.codes": "tEmpty gMany"}),
    ],
}
