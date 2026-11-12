"""Gastos de compra de vivienda: ITP (used) or IVA + AJD (new) by comunidad, plus estimated notary, registry, agency fees."""

TRIB = "https://www.hacienda.gob.es/SGFAL/FinanciacionTerritorial/Autonomica/Capitulo-I-Tributacion-Autonomica-2026.pdf"
LIVA = "https://www.boe.es/buscar/act.php?id=BOE-A-1992-28740"
LITP = "https://www.boe.es/buscar/act.php?id=BOE-A-1993-25359"
NOT = "https://www.boe.es/buscar/act.php?id=BOE-A-1989-28111"
REG = "https://www.boe.es/buscar/act.php?id=BOE-A-1989-28112"
L52019 = "https://www.boe.es/buscar/act.php?id=BOE-A-2019-3814"
# Regional texts checked 2026-11-12 (verifier V1): scales and foral rates read in the consolidated official text.
ARA = "https://www.boe.es/buscar/act.php?id=BOA-d-2005-90006"          # Aragón DLeg 1/2005, art. 121-1
AST = "https://www.asturias.es/documents/4911212/4919217/consulta_1_2018.pdf/73a57008-17d2-f53c-87cc-e927cff59ad5"  # art. 26 DLeg 2/2014: one rate on the whole value
BAL = "https://www.boe.es/buscar/act.php?id=BOE-A-2014-6925"           # Illes Balears DLeg 1/2014, art. 10 (consolidated 13-06-2026)
EXT = "https://www.boe.es/buscar/act.php?id=BOE-A-2018-8159"           # Extremadura DLeg 1/2018, art. 36 (consolidated 04-08-2026)
CYL = "https://www.boe.es/buscar/act.php?id=BOCL-h-2013-90254"         # Castilla y León DLeg 1/2013, arts. 24-25
CAT = "https://www.boe.es/buscar/act.php?id=BOE-A-2025-10270"          # Cataluña DL 5/2025, art. 641-1 Código tributario
NAV = "https://www.boe.es/buscar/act.php?id=BON-n-1999-90001"          # Navarra DFLeg 129/1999, arts. 8 and 22 (consolidated 20-04-2026)
BIZ = "https://www.bizkaia.eus/documents/880307/15187815/ca_1_2011.pdf/50b78491-3852-b68f-f9d5-2db574a48917"  # Bizkaia NF 1/2011, arts. 13 and 44
IGIC = "https://www.boe.es/buscar/act.php?id=BOE-A-2012-9282"          # Canarias Ley 4/2012, arts. 51 and 58
# slug: (name, ITP: rate % | [[upper limit, %], ...] marginal scale (None = rest) | {"p": [...]} one rate on the whole value, AJD %, note)
CA = {
    "andalucia": ("Andalucía", 7, 1.2), "aragon": ("Aragón", [[400000, 8], [450000, 8.5], [500000, 9], [750000, 9.5], [None, 10]], 1.5),
    "asturias": ("Asturias", {"p": [[300000, 8], [500000, 9], [None, 10]]}, 1.2,
                 "En Asturias el tipo del tramo (8 % hasta 300.000 €, 9 % hasta 500.000 €, 10 % por encima) se aplica a todo el valor."),
    "baleares": ("Illes Balears", [[400000, 8], [600000, 9], [1000000, 10], [2000000, 12], [None, 13]], 1.5),
    "canarias": ("Canarias", 6.5, 0.75), "cantabria": ("Cantabria", 9, 1.5),
    "castilla-la-mancha": ("Castilla-La Mancha", 9, 1.5), "castilla-y-leon": ("Castilla y León", [[250000, 8], [None, 10]], 1.5),
    "cataluna": ("Cataluña", [[600000, 10], [900000, 11], [1500000, 12], [None, 13]], 1.5),
    "comunitat-valenciana": ("Comunitat Valenciana", "val", 1.4),
    "extremadura": ("Extremadura", [[360000, 8], [600000, 10], [None, 11]], 1.5), "galicia": ("Galicia", 8, 1.5),
    "la-rioja": ("La Rioja", 7, 1), "madrid": ("Comunidad de Madrid", 6, 0.75), "murcia": ("Región de Murcia", 7.75, 1.5),
    "navarra": ("Navarra", 6, 0.5,
                "Navarra: 5 % para familias con dos o más hijos (hasta 180.304 €) y 4 % en municipios en riesgo de despoblación, no aplicados."),
    "pais-vasco": ("País Vasco", 4, 0.5,
                   "Tipos de Bizkaia: 4 % la vivienda y 2,5 % si tiene hasta 120 m² construidos o eres familia numerosa (no aplicado). "
                   "En Gipuzkoa y Álava el 4 % sale de guías fiscales: no lo hemos verificado en su texto oficial."),
    "ceuta": ("Ceuta", 3, 0.25, "Ceuta: tipos estatales (6 % y 0,5 %) con la bonificación del 50 % del art. 57 bis de la ley del ITP."),
    "melilla": ("Melilla", 3, 0.25, "Melilla: tipos estatales (6 % y 0,5 %) con la bonificación del 50 % del art. 57 bis de la ley del ITP."),
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
<a href="{CYL}" rel="noopener">Castilla y León</a> aplica el 8 % hasta 250.000 € y el 10 % al resto. Cataluña, Aragón, Extremadura
y Baleares usan escalas por tramos: en <a href="{CAT}" rel="noopener">Cataluña</a>, 10 % hasta 600.000 €, 11 % hasta 900.000 €, 12 %
hasta 1,5 millones y 13 % por encima; en <a href="{ARA}" rel="noopener">Aragón</a>, del 8 % hasta 400.000 € al 10 % desde 750.000 €;
en <a href="{EXT}" rel="noopener">Extremadura</a>, 8 %, 10 % desde 360.000 € y 11 % desde 600.000 €; en
<a href="{BAL}" rel="noopener">Baleares</a>, del 8 % hasta 400.000 € al 13 % desde 2 millones. En <a href="{AST}" rel="noopener">Asturias</a>
no es una escala: el valor decide un único tipo (8 %, 9 % o 10 %) que se aplica a todo el precio.</p>
<p>Navarra y el País Vasco tienen normativa foral: en <a href="{NAV}" rel="noopener">Navarra</a>, 6 % de ITP y 0,5 % de AJD; en
<a href="{BIZ}" rel="noopener">Bizkaia</a>, 4 % para vivienda (2,5 % hasta 120 m² construidos) y 0,5 % de AJD. En Ceuta y Melilla se
aplican los tipos estatales con una bonificación del 50 %, y la vivienda nueva no paga IVA sino IPSI. Casi todas las comunidades
tienen <b>tipos reducidos</b> para jóvenes, familias numerosas, personas con discapacidad o viviendas baratas en municipios
pequeños, que esta calculadora no aplica: si puedes acogerte, el impuesto baja mucho.</p>"""),
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
    else if (R[1].p) { /* one rate, chosen by the value, on the whole value (Asturias) */
      for (var j = 0; j < R[1].p.length; j++) { if (R[1].p[j][0] === null || p <= R[1].p[j][0]) { rate = R[1].p[j][1]; break; } }
      tax = p * rate / 100; rows.push(['ITP ' + H.num(rate, 0) + ' % sobre todo el valor', H.eur(tax)]);
    }
    else { tax = scale(p, R[1]); rows.push(['ITP por tramos · ' + H.num(tax / p * 100, 2) + ' % medio', H.eur(tax)]); }
  } else {
    var cm = v.ca === 'ceuta' || v.ca === 'melilla', can = v.ca === 'canarias';
    var ivaR = cm ? 0 : can ? (v.vpo ? 0 : 7) : v.vpo ? 4 : 10, iva = p * ivaR / 100, ajd = p * R[2] / 100;
    tax = iva + ajd;
    rows.push(cm ? ['IPSI (no incluido)', '—'] : [(can ? 'IGIC ' : 'IVA ') + ivaR + ' %', H.eur(iva)], ['AJD ' + H.num(R[2], 2).replace(/,?0+$/, '') + ' %', H.eur(ajd)]);
  }
  var xn = R[3] && v.tipo === 'usada' ? ' ' + R[3] : '';
  if (v.tipo !== 'usada' && cm) xn = ' En Ceuta y Melilla no hay IVA: la vivienda nueva paga IPSI, con el tipo que fija cada ciudad, y no está sumado. AJD con bonificación del 50 %.';
  if (v.tipo !== 'usada' && can) xn = ' Canarias: IGIC del 7 %; 0 % en VPO y 3 % o 5 % para vivienda habitual con requisitos de edad, familia y precio (no aplicados).';
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
    rows: rows, note: 'Tipos generales de ' + H.esc(R[0]) + ' en 2026, sin reducciones por edad, familia o vivienda protegida.' + xn,
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
        {"id": "vpo", "type": "check", "label": "Protegida (VPO)", "value": False, "show": ("tipo", ["nueva"]), "more": True},
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
                ("Arancel de los registradores, RD 1427/1989 (BOE)", REG), ("Ley 5/2019 de crédito inmobiliario (BOE)", L52019),
                ("Aragón · DLeg 1/2005, art. 121-1 (BOE)", ARA), ("Asturias · consulta 1/2018 sobre el art. 26 del DLeg 2/2014", AST),
                ("Illes Balears · DLeg 1/2014, art. 10 (BOE)", BAL), ("Extremadura · DLeg 1/2018, art. 36 (BOE)", EXT),
                ("Castilla y León · DLeg 1/2013, arts. 24-25 (BOE)", CYL), ("Cataluña · Decreto-ley 5/2025, art. 641-1 (BOE)", CAT),
                ("Navarra · DFLeg 129/1999, arts. 8 y 22 (BOE)", NAV), ("Bizkaia · Norma Foral 1/2011, arts. 13 y 44", BIZ),
                ("Canarias · Ley 4/2012, arts. 51 y 58 (IGIC, BOE)", IGIC)],
    "related": ["actualizar-alquiler", "intereses-demora", "precio-sin-iva", "cuota-autonomos-2026"],
    "tests": [
        ({"precio": "200000", "ca": "madrid"}, {"n.tax": 12000}),
        ({"precio": "200000", "ca": "madrid", "tipo": "nueva"}, {"n.tax": 21500}),
        ({"precio": "700000", "ca": "cataluna"}, {"n.tax": 71000}),
        ({"precio": "300000", "ca": "castilla-y-leon"}, {"n.tax": 25000}),
        ({"precio": "1200000", "ca": "comunitat-valenciana"}, {"n.tax": 132000}),
        ({"precio": "400000", "ca": "asturias"}, {"n.tax": 36000}),
        ({"precio": "500000", "ca": "aragon"}, {"n.tax": 40750}),
        ({"precio": "200000", "ca": "ceuta", "tipo": "nueva"}, {"n.tax": 500}),
        ({"precio": "200000", "ca": "canarias", "tipo": "nueva"}, {"n.tax": 15500}),
        ({"precio": "0", "ca": "madrid"}, {"err": "Escribe el precio de la vivienda."}),
    ],
}
