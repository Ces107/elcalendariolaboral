"""Precio sin IVA: remove or add Spanish VAT (21 / 10 / 4 %) and the recargo de equivalencia (5,2 / 1,4 / 0,5 %)."""

LIVA = "https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740"
AEAT = "https://sede.agenciatributaria.gob.es/Sede/iva/calculo-iva-repercutido-clientes/tipos-impositivos-iva.html"
RE = {"21": 5.2, "10": 1.4, "4": 0.5, "0": 0}

BLOCKS = [
    ("Cómo quitar el IVA de un precio", f"""
<p>Para sacar el precio sin IVA <b>no se resta el 21 %</b>: se divide entre 1,21. Un artículo de 121 € con IVA cuesta 100 € sin
IVA (121 / 1,21) y el IVA son 21 €. Si restas el 21 % de 121 te sale 95,59 €, que es un error habitual: el porcentaje se aplica
sobre la base, no sobre el total. Con el tipo reducido del 10 % se divide entre 1,10 y con el superreducido del 4 %, entre 1,04.</p>
<p>Al revés, para añadir el IVA a una base se multiplica: 100 € más IVA del 21 % son 121 €. La calculadora hace las dos
operaciones; elige «Con IVA» si el importe que tienes ya lo incluye (un ticket, un precio de tienda) o «Sin IVA» si es la base
(un presupuesto «+ IVA»).</p>"""),
    ("Qué tipo de IVA se aplica", f"""
<p>Según los <a href="{LIVA}#a90" rel="noopener">artículos 90 y 91 de la Ley del IVA</a>: el <b>21 %</b> es el tipo general (la
mayoría de productos y servicios, electricidad, ropa, electrónica, peluquería); el <b>10 %</b>, el reducido (hostelería y
restaurantes, transporte de viajeros, vivienda nueva, gafas, agua, muchos alimentos elaborados); y el <b>4 %</b>, el
superreducido (pan, leche, huevos, frutas, verduras, legumbres, queso, libros y periódicos, medicamentos, prótesis y vehículos
para personas con movilidad reducida). La lista detallada está en la <a href="{AEAT}" rel="noopener">web de la Agencia
Tributaria</a>. En Canarias no hay IVA sino IGIC, con un tipo general del 7 %; Ceuta y Melilla tienen el IPSI.</p>"""),
    ("Recargo de equivalencia", f"""
<p>Los comerciantes minoristas que son personas físicas y venden sin transformar el producto suelen estar en el <b>régimen de
recargo de equivalencia</b> (<a href="{LIVA}#a161" rel="noopener">artículo 161</a>): su proveedor les cobra, además del IVA, un
recargo del 5,2 % (sobre productos al 21 %), del 1,4 % (al 10 %) o del 0,5 % (al 4 %). A cambio, el minorista no presenta
declaraciones de IVA. Ejemplo: una compra de 1.000 € de base al 21 % con recargo cuesta 1.000 + 210 + 52 = <b>1.262 €</b>; y
de una factura de 1.262 € con IVA y recargo, la base es 1.262 / 1,262 = 1.000 €.</p>"""),
]

FAQ = [
    ("¿Cómo calculo el precio sin IVA?",
     "Divide el precio con IVA entre 1,21 (IVA del 21 %), 1,10 (10 %) o 1,04 (4 %). Por ejemplo, 50 € con IVA son 41,32 € sin IVA."),
    ("¿Por qué no basta con restar el 21 %?",
     "Porque el 21 % se calcula sobre el precio sin IVA, que es menor. Restar el 21 % del total quita demasiado: de 121 € quedarían "
     "95,59 € en lugar de 100 €."),
    ("¿Cuánto es el IVA de 100 €?",
     "Si 100 € es la base, el IVA al 21 % son 21 € y el total 121 €. Si 100 € ya incluye el IVA, la base es 82,64 € y el IVA 17,36 €."),
    ("¿Qué es el recargo de equivalencia?",
     "Un recargo que paga el comercio minorista a su proveedor junto con el IVA (5,2 %, 1,4 % o 0,5 %) para no tener que hacer "
     "declaraciones trimestrales de IVA."),
    ("¿Qué IVA tiene la comida de un restaurante?",
     "El 10 %, igual que las bebidas que se sirven en el local. Los alimentos básicos comprados en la tienda llevan el 4 % y el resto "
     "de alimentos el 10 %."),
]

JS = r"""
function (v, H, C) {
  var x = v.importe, t = +v.tipo, re = v.re ? C.d.re[v.tipo] : 0;
  if (!(x >= 0)) return { err: 'Escribe un importe.' };
  var base, iva, rec, total;
  if (v.modo === 'con') { base = H.r2(x / (1 + (t + re) / 100)); iva = H.r2(base * t / 100); rec = H.r2(base * re / 100); total = x; base = H.r2(total - iva - rec); }
  else { base = x; iva = H.r2(x * t / 100); rec = H.r2(x * re / 100); total = H.r2(base + iva + rec); }
  var rows = [['Base imponible', H.eur(base)], ['IVA ' + t + ' %', H.eur(iva)]];
  if (re) rows.push(['Recargo ' + H.num(re, 1) + ' %', H.eur(rec)]);
  rows.push(['Total', H.eur(total), 'tot']);
  return {
    label: v.modo === 'con' ? 'Precio sin IVA' : 'Precio con IVA', big: H.eur(v.modo === 'con' ? base : total),
    sub: (v.modo === 'con' ? 'IVA incluido: ' : 'IVA: ') + H.eur(iva) + (re ? ' · recargo ' + H.eur(rec) : ''),
    rows: rows, n: { base: base, iva: iva, rec: rec, total: total }
  };
}
"""

TOOL = {
    "slug": "precio-sin-iva",
    "lang": "es",
    "cat": "dinero",
    "icon": "percentage",
    "order": 20,
    "name": "Precio sin IVA",
    "k": "quitar iva calcular iva 21 10 4 inverso base imponible recargo de equivalencia añadir",
    "title": "Calcular el precio sin IVA (21 %, 10 %, 4 %) y con IVA",
    "desc": "Quita o añade el IVA a un precio al 21 %, 10 % o 4 %, con recargo de equivalencia opcional. Base imponible, cuota de IVA y total al momento.",
    "h1": "Precio sin IVA y con IVA",
    "updated": "2026-11-12",
    "data": {"re": RE},
    "inputs": [
        {"id": "importe", "type": "money", "label": "Importe", "value": 121, "w": "l"},
        {"id": "modo", "type": "seg", "label": "El importe", "value": "con", "options": [("con", "Con IVA"), ("sin", "Sin IVA")]},
        {"id": "tipo", "type": "seg", "label": "IVA", "value": "21", "options": [("21", "21 %"), ("10", "10 %"), ("4", "4 %"), ("0", "0 %")]},
        {"id": "re", "type": "check", "label": "Recargo de equivalencia", "value": False, "more": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Ley 37/1992 del IVA, arts. 90, 91 y 161 (BOE)", LIVA), ("Agencia Tributaria · Tipos impositivos del IVA", AEAT)],
    "related": ["factura-retencion-irpf", "numeros-a-letras", "cuota-autonomos-2026", "precio-venta-margen"],
    "tests": [
        ({"importe": "121"}, {"n.base": 100, "n.iva": 21}),
        ({"importe": "100", "modo": "sin"}, {"n.total": 121}),
        ({"importe": "110", "tipo": "10"}, {"n.base": 100}),
        ({"importe": "1262", "re": "1"}, {"n.base": 1000, "n.rec": 52}),
        ({"importe": "100", "modo": "sin", "tipo": "4", "re": "1"}, {"n.total": 104.5}),
        ({"importe": "x"}, {"err": "Escribe un importe."}),
    ],
}
