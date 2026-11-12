"""Gastos de compra de vivienda: ITP (used) or IVA + AJD (new) by comunidad, plus estimated notary, registry, agency fees."""

TRIB = "https://www.hacienda.gob.es/SGFAL/FinanciacionTerritorial/Autonomica/Capitulo-I-Tributacion-Autonomica-2026.pdf"
LIVA = "https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740"
LITP = "https://www.boe.es/buscar/act.php?id=BOE-A-1993-25359"
NOT = "https://www.boe.es/buscar/act.php?id=BOE-A-1989-28111"
REG = "https://www.boe.es/buscar/act.php?id=BOE-A-1989-28112"
L52019 = "https://www.boe.es/buscar/act.php?id=BOE-A-2019-3814"
# slug: (name, ITP: rate % or [[upper limit, %], ...] progressive (None = rest), AJD %, note)
CA = {
    "andalucia": ("Andalucía", 7, 1.2), "aragon": ("Aragón", [[400000, 8], [450000, 8.5], [500000, 9], [750000, 9.5], [None, 10]], 1.5),
    "asturias": ("Asturias", [[300000, 8], [500000, 9], [None, 10]], 1.2),
    "baleares": ("Illes Balears", [[400000, 8], [600000, 9], [1000000, 10], [2000000, 12], [None, 13]], 1.5),
    "canarias": ("Canarias", 6.5, 0.75), "cantabria": ("Cantabria", 9, 1.5),
    "castilla-la-mancha": ("Castilla-La Mancha", 9, 1.5), "castilla-y-leon": ("Castilla y León", [[250000, 8], [None, 10]], 1.5),
    "cataluna": ("Cataluña", [[600000, 10], [900000, 11], [1500000, 12], [None, 13]], 1.5),
    "comunitat-valenciana": ("Comunitat Valenciana", "val", 1.4),
    "extremadura": ("Extremadura", [[360000, 8], [600000, 10], [None, 11]], 1.5), "galicia": ("Galicia", 8, 1.5),
    "la-rioja": ("La Rioja", 7, 1), "madrid": ("Comunidad de Madrid", 6, 0.75), "murcia": ("Región de Murcia", 7.75, 1.5),
    "navarra": ("Navarra", 6, 0.5), "pais-vasco": ("País Vasco", 4, 0.5), "ceuta": ("Ceuta", 3, 0.25), "melilla": ("Melilla", 3, 0.25),
}

BLOCKS = [
    ("Cuánto cuesta comprar una casa además del precio", f"""
<p>Calcula entre un <b>7 % y un 15 % más</b> del precio según la comunidad. Casi todo es el impuesto: en una vivienda de segunda
mano se paga el <b>Impuesto de Transmisiones Patrimoniales (ITP)</b>, del 6 % en Madrid al 10-13 % en Cataluña; en una vivienda
nueva comprada al promotor, el <b>IVA del 10 %</b> más el <b>impuesto de Actos Jurídicos Documentados (AJD)</b>, del 0,75 % al
1,5 %. El resto, unos 1.000-2.000 €, son la notaría, el registro de la propiedad y la gestoría.</p>
<p>Ejemplo: un piso usado de 200.000 € en Andalucía paga 14.000 € de ITP (7 %); en Madrid, 12.000 € (6 %); en Galicia, 16.000 €
(8 %). Si es nuevo, en cualquier comunidad paga 20.000 € de IVA y, de AJD, 1.500 € en Madrid o 3.000 € en Galicia. Hay que tener
el dinero ahorrado: los bancos financian como mucho el 80 % del precio y casi nunca los gastos.</p>"""),
    ("Los tipos de cada comunidad en 2026", f"""
<p>Los tipos generales son los del informe <a href="{TRIB}" rel="noopener">Tributación Autonómica. Medidas 2026</a> del Ministerio
de Hacienda. Madrid aplica el 6 %; Canarias el 6,5 %; Andalucía y La Rioja el 7 %; Murcia el 7,75 %; Galicia el 8 %; Cantabria y
Castilla-La Mancha el 9 %; la Comunitat Valenciana el 9 % desde el 1 de junio de 2026 (11 % si el valor pasa de un millón).
Castilla y León aplica el 8 % hasta un límite y el 10 % al resto, y Cataluña, Asturias, Aragón, Extremadura y Baleares usan
escalas por tramos (en Cataluña, 10 % hasta 600.000 €, 11 % hasta 900.000 €, 12 % hasta 1,5 millones y 13 % por encima).</p>
<p>Navarra y el País Vasco tienen su propia normativa foral (6 % y 4 % para vivienda) y en Ceuta y Melilla la cuota se bonifica
al 50 %. Casi todas las comunidades tienen <b>tipos reducidos</b> para jóvenes, familias numerosas, personas con discapacidad o
viviendas baratas en municipios pequeños, que esta calculadora no aplica: si puedes acogerte, el impuesto baja mucho.</p>"""),
    ("Notaría, registro, gestoría e hipoteca", f"""
<p>La notaría y el registro cobran por <a href="{NOT}" rel="noopener">aranceles fijados por real decreto</a>, que crecen poco con el
precio; la calculadora los estima con esos aranceles (rebaja del 5 % incluida), más copias, folios e IVA. La gestoría, que liquida
el impuesto e inscribe la escritura, es opcional y cuesta unos 300-450 €. Si ya tienes un presupuesto, escríbelo en «Más opciones».</p>
<p>Desde la <a href="{L52019}" rel="noopener">Ley 5/2019 de crédito inmobiliario</a>, el banco paga la notaría, el registro, la
gestoría y el AJD de la hipoteca; a ti solo te toca la tasación (300-500 €) y, si lo pides, una copia de la escritura del préstamo.
Las arras, la comisión de la inmobiliaria (si la paga el comprador) y el seguro de hogar no están incluidos.</p>"""),
]

FAQ = [
    ("¿Cuánto hay que tener ahorrado para comprar un piso?",
     "En torno al 30 % del precio: el 20 % que no financia el banco más un 10-12 % de impuestos y gastos. Para 200.000 €, unos 60.000-64.000 €."),
    ("¿Se paga ITP en una vivienda nueva?",
     "No. La primera venta por el promotor paga IVA (10 %) y AJD. La segunda y siguientes ventas, aunque la casa sea casi nueva, pagan ITP."),
    ("¿Sobre qué valor se paga el ITP?",
     "Sobre el mayor entre el precio escriturado y el valor de referencia del Catastro. Si el valor de referencia es más alto que el precio, "
     "el impuesto se calcula sobre él."),
    ("¿Quién paga la notaría al comprar una casa?",
     "La escritura de compraventa la paga el comprador salvo pacto, y la copia del vendedor y la plusvalía municipal el vendedor. Las de la "
     "hipoteca las paga el banco."),
    ("¿Cuándo hay que pagar el ITP?",
     "En la mayoría de comunidades, en los 30 días hábiles siguientes a la firma de la escritura (un mes en algunas), con el modelo 600 o "
     "el de tu comunidad."),
]

JS = r"""
function (v, H, C) {
  var R = C.d.ca[v.ca], p = v.precio;
  if (!R) return { err: 'Elige la comunidad.' };
  if (!(p > 0)) return { err: 'Escribe el precio de la vivienda.' };
  if (p > 1e9) return { err: 'Precio demasiado alto.' };
  function scale(x, s) { var t = 0, lo = 0; for (var i = 0; i < s.length; i++) { var hi = s[i][0] === null ? Infinity : s[i][0]; if (x > lo) t += (Math.min(x, hi) - lo) * s[i][1] / 100; lo = hi; } return t; }
  function aran(x, base, s) { return base + scale(Math.max(0, x - 6010.12), s); }
  var rows = [], tax = 0, rate;
  if (v.tipo === 'usada') {
    if (R[1] === 'val') { rate = p > 1e6 ? 11 : 9; tax = p * rate / 100; rows.push(['ITP ' + H.num(rate, 0) + ' %', H.eur(tax)]); }
    else if (typeof R[1] === 'number') { tax = p * R[1] / 100; rows.push(['ITP ' + H.num(R[1], 2).replace(/,?0+$/, '') + ' %', H.eur(tax)]); }
    else { tax = scale(p, R[1]); rows.push(['ITP por tramos · ' + H.num(tax / p * 100, 2) + ' % medio', H.eur(tax)]); }
  } else {
    var ivaR = v.ca === 'canarias' ? 7 : v.vpo ? 4 : 10, iva = p * ivaR / 100, ajd = p * R[2] / 100;
    tax = iva + ajd;
    rows.push([(v.ca === 'canarias' ? 'IGIC ' : 'IVA ') + ivaR + ' %', H.eur(iva)], ['AJD ' + H.num(R[2], 2).replace(/,?0+$/, '') + ' %', H.eur(ajd)]);
  }
  /* notary (RD 1426/1989) and registry (RD 1427/1989) fees, scales in % (the decrees give per mil), 5 % cut, + copies/entries, + 21 % VAT */
  var not = v.notaria >= 0 ? v.notaria : H.r2((aran(p, 90.15, [[24040.49, 0.45], [54090.98, 0.15], [144242.91, 0.1], [595001.98, 0.05], [null, 0.03]]) * 0.95 + 250) * 1.21);
  var reg = v.registro >= 0 ? v.registro : H.r2((aran(p, 24.04, [[24040.49, 0.175], [54090.98, 0.125], [144242.91, 0.075], [595001.98, 0.03], [null, 0.02]]) * 0.95 + 150) * 1.21);
  var ges = v.gestoria >= 0 ? v.gestoria : 0, tas = v.hip ? (v.tasacion >= 0 ? v.tasacion : 0) : 0;
  rows.push(['Notaría' + (v.notaria >= 0 ? '' : ' (estimada)'), H.eur(not)], ['Registro' + (v.registro >= 0 ? '' : ' (estimado)'), H.eur(reg)]);
  if (ges) rows.push(['Gestoría', H.eur(ges)]);
  if (tas) rows.push(['Tasación', H.eur(tas)]);
  var total = H.r2(tax + not + reg + ges + tas);
  rows.push(['Total gastos', H.eur(total), 'tot']);
  return {
    label: 'Gastos de compra', big: H.eur(total),
    sub: H.num(total / p * 100, 1) + ' % del precio · necesitas ' + H.eur(p + total) + (v.hip ? ' (' + H.eur(p * 0.2 + total) + ' ahorrados si el banco financia el 80 %)' : ''),
    rows: rows, note: 'Tipos generales de ' + H.esc(R[0]) + ' en 2026, sin reducciones por edad, familia o vivienda protegida.',
    n: { tax: H.r2(tax), total: total }
  };
}
"""

TOOL = {
    "slug": "gastos-compra-vivienda",
    "lang": "es",
    "cat": "vivienda",
    "icon": "home",
    "order": 20,
    "name": "Gastos compra vivienda",
    "k": "itp iva ajd impuestos comprar piso casa notaría registro gestoría hipoteca ahorro comunidad",
    "title": "Gastos de compra de vivienda 2026: ITP, IVA y notaría",
    "desc": "Calcula los impuestos y gastos de comprar una casa en 2026 en tu comunidad: ITP si es usada, IVA y AJD si es nueva, notaría, registro y gestoría.",
    "h1": "Gastos de compra de una vivienda",
    "updated": "2026-11-12",
    "data": {"ca": CA},
    "inputs": [
        {"id": "precio", "type": "money", "label": "Precio", "value": 200000, "w": "l"},
        {"id": "tipo", "type": "seg", "label": "Vivienda", "value": "usada", "options": [("usada", "Usada"), ("nueva", "Nueva")]},
        {"id": "ca", "type": "select", "label": "Comunidad", "value": "madrid", "options": [(k, x[0]) for k, x in CA.items()]},
        {"id": "hip", "type": "check", "label": "Con hipoteca", "value": True},
        {"id": "vpo", "type": "check", "label": "Protegida (IVA 4 %)", "value": False, "show": ("tipo", ["nueva"]), "more": True},
        {"id": "notaria", "type": "money", "label": "Notaría", "value": "", "more": True, "w": "s"},
        {"id": "registro", "type": "money", "label": "Registro", "value": "", "more": True, "w": "s"},
        {"id": "gestoria", "type": "money", "label": "Gestoría", "value": 350, "more": True, "w": "s"},
        {"id": "tasacion", "type": "money", "label": "Tasación", "value": 400, "more": True, "w": "s", "show": ("hip", ["true", "True"])},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Ministerio de Hacienda · Tributación Autonómica. Medidas 2026", TRIB), ("Ley del ITP y AJD (BOE)", LITP),
                ("Ley 37/1992 del IVA, art. 91 (BOE)", LIVA), ("Arancel notarial, RD 1426/1989 (BOE)", NOT),
                ("Arancel de los registradores, RD 1427/1989 (BOE)", REG), ("Ley 5/2019 de crédito inmobiliario (BOE)", L52019)],
    "related": ["actualizar-alquiler", "intereses-demora", "precio-sin-iva", "cuota-autonomos-2026"],
    "tests": [
        ({"precio": "200000", "ca": "madrid"}, {"n.tax": 12000}),
        ({"precio": "200000", "ca": "madrid", "tipo": "nueva"}, {"n.tax": 21500}),
        ({"precio": "700000", "ca": "cataluna"}, {"n.tax": 71000}),
        ({"precio": "300000", "ca": "castilla-y-leon"}, {"n.tax": 25000}),
        ({"precio": "1200000", "ca": "comunitat-valenciana"}, {"n.tax": 132000}),
        ({"precio": "0", "ca": "madrid"}, {"err": "Escribe el precio de la vivienda."}),
    ],
}
