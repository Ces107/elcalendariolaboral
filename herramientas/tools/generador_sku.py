"""Generador de SKU: códigos de referencia para todas las combinaciones de variantes (color, talla, material), sin
colisiones, con CSV para copiar. English twin: sku_generator.py (same core)."""
from herramientas.tools import _sellers as S

GS1 = "https://www.gs1.org/standards/id-keys/gtin"

CORE_JS = r"""
  /* letters/digits only, no accents; code = first n chars of the first word + initials of the rest; words with
     digits (500ML, 350) and sizes (S, XL, 3XL) kept whole. Collisions inside a list grow the prefix, then add a digit. */
  function clean(s) { return s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase().replace(/[^A-Z0-9 ]+/g, ' ').trim(); }
  function code(s, n) {
    var w = clean(s).split(/\s+/).filter(function (x) { return x; });
    if (!w.length) return '';
    if (w.length === 1 && /^(X*[SML]|XX+L|\d*X+L)$/.test(w[0])) return w[0];
    return w.map(function (x, i) { return /\d/.test(x) ? x : i ? x.charAt(0) : x.slice(0, n); }).join('');
  }
  function codes(list, n) {
    var c = list.map(function (x) { return code(x, n); }), grow = n;
    while (grow < n + 6) {
      var seen = {}, dup = false;
      c.forEach(function (x) { if (seen[x]) dup = true; seen[x] = 1; });
      if (!dup) return c;
      grow++;
      var cnt = {}; c.forEach(function (x) { cnt[x] = (cnt[x] || 0) + 1; });
      c = c.map(function (x, i) { return cnt[x] > 1 ? code(list[i], grow) : x; });
    }
    var k = {}; return c.map(function (x) { k[x] = (k[x] || 0) + 1; return k[x] > 1 ? x + k[x] : x; });
  }
  function split(s) { var o = [], seen = {}; String(s || '').split(/[,;\n]+/).forEach(function (x) { x = x.trim(); var k = clean(x); if (x && k && !seen[k]) { seen[k] = 1; o.push(x); } }); return o; }
  function skus(base, lists, n, sep, num) {
    var b = codes([base], n)[0], cl = lists.map(function (l) { return codes(l, n); }), out = [[[], []]];
    lists.forEach(function (l, j) {
      var nx = []; out.forEach(function (o) { l.forEach(function (x, i) { nx.push([o[0].concat([cl[j][i]]), o[1].concat([x])]); }); }); out = nx;
    });
    return out.map(function (o, i) {
      var parts = (b ? [b] : []).concat(o[0]).filter(function (x) { return x; });
      if (num) parts.push(('00' + (i + 1)).slice(-3));
      return [parts.join(sep), o[1]];
    });
  }
  function csvq(s) { return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s; }
"""


def blocks(ctx):
    return [
        ("Cómo se forma cada código", """
<p>Escribe el producto y, en cada variante, sus valores separados por comas. El generador crea un SKU para cada
combinación: con «Camiseta básica», tres colores (Rojo, Azul, Negro) y cuatro tallas (S, M, L, XL) salen 12 códigos, de
<code>CAMB-ROJ-S</code> a <code>CAMB-NEG-XL</code>. Cada palabra se reduce a sus primeras letras, sin tildes ni símbolos; las
palabras siguientes aportan su inicial («Azul marino» → <code>AZUM</code>), y las tallas y medidas con números
(<code>XL</code>, <code>3XL</code>, <code>500ML</code>) se quedan enteras. Si dos valores darían el mismo código, el generador
alarga el prefijo hasta distinguirlos, así que nunca hay dos SKU iguales.</p>
<p>Abajo tienes la lista en CSV (SKU y variantes) para pegarla en una hoja de cálculo o en la importación masiva de tu
tienda: Etsy, Shopify, WooCommerce o Amazon Seller Central tienen un campo SKU por variante.</p>"""),
        ("Buenas prácticas para un SKU", """
<ul>
<li><b>De lo general a lo concreto</b>: producto, modelo, color, talla. Así, al ordenar la lista alfabéticamente, las
variantes de un mismo producto quedan juntas.</li>
<li><b>Corto y sin espacios</b>: entre 8 y 16 caracteres caben en cualquier campo y en cualquier etiqueta de almacén.</li>
<li><b>Sin empezar por cero</b>: Excel y Google Sheets borran los ceros iniciales de <code>0012</code> y lo convierten en
<code>12</code>.</li>
<li><b>Sin letras que se confundan</b>: la O y el 0, la I y el 1 se confunden al leer una etiqueta a mano.</li>
<li><b>Nunca reutilices un SKU</b> de un producto retirado: tus informes de ventas mezclarían los dos.</li>
</ul>"""),
        ("SKU no es código de barras", f"""
<p>El SKU es un código interno: lo inventas tú y solo sirve en tu tienda y tu almacén. El código de barras que pide Amazon o
una tienda física es un <a href="{GS1}" rel="noopener">GTIN (EAN-13 en Europa)</a>, que asigna GS1 a cada producto y es único
en todo el mundo. Puedes tener los dos: el GTIN identifica el producto ante terceros y el SKU te sirve a ti para encontrarlo,
contarlo y analizar las ventas por variante.</p>"""),
    ]


FAQ = [
    ("¿Qué es un SKU?",
     "Stock Keeping Unit: un código interno que identifica cada variante de un producto (por ejemplo, la camiseta roja en "
     "talla M) para controlar el inventario y las ventas."),
    ("¿Cómo creo un SKU?",
     "Combina abreviaturas fijas de producto y variantes en el mismo orden, separadas por guiones: CAMB-ROJ-M. Este generador lo "
     "hace para todas las combinaciones a la vez."),
    ("¿Es obligatorio el SKU en Etsy o Amazon?",
     "En Etsy es opcional; en Amazon Seller Central cada oferta tiene un SKU de vendedor, y si no lo pones Amazon genera uno."),
    ("¿El SKU y el EAN son lo mismo?",
     "No. El EAN o GTIN es un código de barras oficial de GS1, único en el mundo; el SKU lo eliges tú y solo vale dentro de tu "
     "negocio."),
    ("¿Cuántos caracteres debe tener un SKU?",
     "No hay un estándar, pero de 8 a 16 caracteres, solo letras, números y guiones, funciona en cualquier plataforma."),
]

JS = r"""
function (v, H, C) {
""" + CORE_JS + r"""
  var lists = [split(v.a1), split(v.a2), split(v.a3)].filter(function (l) { return l.length; });
  if (!clean(v.base || '') && !lists.length) return { err: 'Escribe el producto o al menos una variante.' };
  var total = lists.reduce(function (a, l) { return a * l.length; }, 1);
  if (total > 500) return { err: 'Son ' + total + ' combinaciones: el máximo es 500.' };
  var sep = v.sep === 'n' ? '' : v.sep, r = skus(v.base || '', lists, +v.len, sep, v.num), long = 0;
  r.forEach(function (x) { long = Math.max(long, x[0].length); });
  var rows = r.map(function (x) { return '<tr><td><code>' + H.esc(x[0]) + '</code></td><td>' + H.esc(x[1].join(' · ')) + '</td></tr>'; }).join('');
  var csv = 'sku,producto' + lists.map(function (l, i) { return ',variante' + (i + 1); }).join('') + '\n' +
    r.map(function (x) { return [x[0], v.base || ''].concat(x[1]).map(csvq).join(','); }).join('\n');
  return {
    label: 'SKU generados', big: r.length, sub: 'Máximo ' + long + ' caracteres · ' + H.esc(r[0][0]),
    html: '<table class="tbl sku"><thead><tr><th>SKU</th><th>Variante</th></tr></thead><tbody>' + rows + '</tbody></table>' +
      '<label class="flabel" for="sku-csv">CSV</label><textarea id="sku-csv" class="sku-csv" readonly rows="6">' + H.esc(csv) + '</textarea>',
    n: { count: r.length, first: r[0][0], last: r[r.length - 1][0], long: long }
  };
}
"""

CSS = (".sku td code{font-size:14px}.sku-csv{display:block;width:100%;margin-top:6px;font:13px/1.4 ui-monospace,Consolas,monospace;"
       "border:1px solid var(--line);border-radius:4px;padding:8px}")

TOOL = {
    "slug": "generador-sku",
    "lang": "es",
    "twin": "sku-generator",
    "cat": "vendedores",
    "icon": "barcode",
    "order": 100,
    "name": "Generador de SKU",
    "k": "sku referencia código producto variantes inventario csv",
    "title": "Generador de SKU gratis: códigos para cada variante",
    "desc": "Crea códigos SKU para todas las combinaciones de color, talla y material de tus productos, sin duplicados, y cópialos en CSV para Etsy o Shopify.",
    "h1": "Generador de SKU",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "base", "type": "text", "label": "Producto", "value": "Camiseta básica", "w": "l", "maxlength": 60},
        {"id": "a1", "type": "text", "label": "Variante 1", "value": "Rojo, Azul, Negro", "w": "l"},
        {"id": "a2", "type": "text", "label": "Variante 2", "value": "S, M, L, XL", "w": "l"},
        {"id": "a3", "type": "text", "label": "Variante 3", "value": "", "w": "l", "more": True},
        {"id": "len", "type": "seg", "label": "Letras", "value": "3", "options": [("2", "2"), ("3", "3"), ("4", "4")]},
        {"id": "sep", "type": "seg", "label": "Separador", "value": "-", "options": [("-", "-"), ("_", "_"), ("n", "Sin")]},
        {"id": "num", "type": "check", "label": "Número correlativo", "value": False, "more": True},
    ],
    "js": JS,
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("GS1 · Global Trade Item Number (GTIN)", GS1), ("Etsy Open API v3 · inventario (sku)", S.ETSY_API)],
    "related": ["revisar-anuncio-etsy", "tallas-ropa-calzado", "precio-venta-margen"],
    "tests": [
        ({}, {"n.count": 12, "n.first": "CAMB-ROJ-S", "n.last": "CAMB-NEG-XL"}),
        ({"a1": "Azul, Azul marino, Azul", "a2": ""}, {"n.count": 2, "n.last": "CAMB-AZUM"}),
        ({"a1": "Rojo, Rosa, Roble", "a2": "", "len": "2"}, {"n.first": "CAB-ROJ", "n.last": "CAB-ROB"}),
        ({"sep": "n", "num": "1"}, {"n.first": "CAMBROJS001"}),
        ({"base": "", "a1": "", "a2": ""}, {"err": "Escribe el producto o al menos una variante."}),
        ({"base": "Taza 350 ml", "a1": "Blanca, Negra", "a2": ""}, {"n.first": "TAZ350M-BLA"}),
    ],
}
