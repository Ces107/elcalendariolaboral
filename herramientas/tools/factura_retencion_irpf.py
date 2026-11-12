"""Factura con retención de IRPF: base, IVA, retención (15 / 7 / 19 / 1 %) and the total to collect, both ways."""

LIRPF = "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764"
RIRPF = "https://www.boe.es/buscar/act.php?id=BOE-A-2007-6820"
RFACT = "https://www.boe.es/buscar/act.php?id=BOE-A-2012-14696"

BLOCKS = [
    ("Cómo se calcula una factura con retención", f"""
<p>Un autónomo profesional que factura a una empresa o a otro autónomo suma el IVA y <b>resta la retención de IRPF</b>, las dos
calculadas sobre la base. Con una base de 1.000 €, IVA del 21 % y retención del 15 %: 1.000 + 210 − 150 = <b>1.060 €</b> a
cobrar. El cliente paga 1.060 € e ingresa los 150 € de retención en Hacienda a tu nombre (modelo 111); tú los descuentas en tu
declaración de la renta como pagos a cuenta y declaras los 210 € de IVA en el modelo 303.</p>
<p>Si sabes lo que quieres cobrar y necesitas la base, elige «Cobrar»: la base es el importe dividido entre (1 + IVA − retención).
Para cobrar 1.000 € limpios con 21 % de IVA y 15 % de retención, la base es 1.000 / 1,06 = 943,40 €.</p>"""),
    ("Qué retención aplicar", f"""
<p>Los tipos están en el <a href="{RIRPF}#a95" rel="noopener">artículo 95 del Reglamento del IRPF</a> y el
<a href="{RIRPF}#a100" rel="noopener">100</a>:</p>
<ul>
<li><b>15 %</b>: actividades profesionales en general (abogados, diseñadores, consultores, programadores dados de alta en
epígrafes profesionales, formadores, traductores).</li>
<li><b>7 %</b>: el año en que empiezas la actividad profesional y los dos siguientes, si no la ejerciste en el año anterior.
Hay que comunicárselo al cliente por escrito.</li>
<li><b>19 %</b>: el alquiler de un local u oficina a una empresa o profesional.</li>
<li><b>1 %</b>: actividades empresariales en estimación objetiva (módulos) de ciertos epígrafes, cuando facturan a empresas.</li>
<li><b>Sin retención</b>: facturas a particulares, actividades empresariales en estimación directa (comercio, hostelería,
construcción) y clientes extranjeros.</li>
</ul>"""),
    ("Lo que debe llevar la factura", f"""
<p>El <a href="{RFACT}" rel="noopener">Reglamento de facturación</a> exige número y fecha, datos y NIF de emisor y cliente,
descripción, base imponible, tipo y cuota de IVA y el total. La retención no es obligatoria en el reglamento de facturación,
pero se indica siempre («Retención IRPF 15 %: −150,00 €») para que el cliente la ingrese. Si la operación está exenta de IVA
(formación reglada, servicios médicos), hay que citar el artículo de la ley que la exime, y la retención sigue aplicándose.</p>"""),
]

FAQ = [
    ("¿Cuánto cobro de una factura de 1.000 € con IVA y retención?",
     "Con IVA del 21 % y retención del 15 %, 1.060 €. Con retención del 7 % (nuevos autónomos), 1.140 €."),
    ("¿Quién puede aplicar el 7 % de retención?",
     "Los profesionales que inician actividad, en el año de inicio y los dos siguientes, siempre que no hayan ejercido una actividad "
     "profesional en el año anterior al inicio."),
    ("¿Se aplica retención a las facturas a particulares?",
     "No. Solo retienen las empresas, los autónomos en su actividad y las entidades. A un particular le facturas base más IVA."),
    ("¿La retención se calcula sobre el total con IVA?",
     "No, sobre la base imponible, igual que el IVA. Por eso el total es base + IVA − retención."),
    ("¿Qué retención lleva el alquiler de un local?",
     "El 19 % de la renta, si el inquilino es una empresa o un profesional. El alquiler de vivienda a un particular no lleva retención."),
]

JS = r"""
function (v, H, C) {
  var x = v.importe, i = +v.iva / 100, r = +v.ret / 100;
  if (!(x > 0)) return { err: 'Escribe un importe.' };
  var base = v.modo === 'cobrar' ? H.r2(x / (1 + i - r)) : x;
  var iva = H.r2(base * i), ret = H.r2(base * r), total = H.r2(base + iva - ret);
  var rows = [['Base imponible', H.eur(base)], ['IVA ' + v.iva + ' %', '+ ' + H.eur(iva)]];
  if (r) rows.push(['Retención IRPF ' + v.ret + ' %', '− ' + H.eur(ret)]);
  rows.push(['Total a cobrar', H.eur(total), 'tot']);
  return {
    label: v.modo === 'cobrar' ? 'Base de la factura' : 'Total a cobrar', big: H.eur(v.modo === 'cobrar' ? base : total),
    sub: 'Factura: ' + H.eur(base + iva) + ' con IVA' + (r ? ' · Hacienda recibe ' + H.eur(ret) + ' a tu nombre' : ''),
    rows: rows, print: true, n: { base: base, iva: iva, ret: ret, total: total }
  };
}
"""

TOOL = {
    "slug": "factura-retencion-irpf",
    "lang": "es",
    "cat": "dinero",
    "icon": "file-invoice",
    "order": 30,
    "name": "Factura con retención",
    "k": "autónomo irpf 15 7 19 iva base total a cobrar retención profesional calcular factura",
    "title": "Calcular factura de autónomo: IVA y retención IRPF",
    "desc": "Calcula una factura de autónomo con IVA y retención de IRPF del 15 %, 7 % o 19 %: base, cuotas y total a cobrar, o la base para cobrar un neto.",
    "h1": "Factura con IVA y retención de IRPF",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "importe", "type": "money", "label": "Importe", "value": 1000, "w": "l"},
        {"id": "modo", "type": "seg", "label": "Es la", "value": "base", "options": [("base", "Base"), ("cobrar", "Cobrar")]},
        {"id": "iva", "type": "seg", "label": "IVA", "value": "21", "options": [("21", "21 %"), ("10", "10 %"), ("4", "4 %"), ("0", "0 %")]},
        {"id": "ret", "type": "seg", "label": "Retención", "value": "15", "options": [("15", "15 %"), ("7", "7 %"), ("19", "19 %"), ("1", "1 %"), ("0", "0 %")]},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Reglamento del IRPF, arts. 95 y 100 (BOE)", RIRPF), ("Ley 35/2006 del IRPF, art. 101 (BOE)", LIRPF),
                ("Reglamento de facturación, RD 1619/2012 (BOE)", RFACT)],
    "related": ["precio-sin-iva", "cuota-autonomos-2026", "numeros-a-letras", "validar-cif-nif"],
    "tests": [
        ({"importe": "1000"}, {"n.total": 1060, "n.ret": 150}),
        ({"importe": "1000", "ret": "7"}, {"n.total": 1140}),
        ({"importe": "1060", "modo": "cobrar"}, {"n.base": 1000}),
        ({"importe": "1000", "iva": "0"}, {"n.total": 850}),
        ({"importe": "1000", "ret": "19"}, {"n.total": 1020}),
        ({"importe": "0"}, {"err": "Escribe un importe."}),
    ],
}
