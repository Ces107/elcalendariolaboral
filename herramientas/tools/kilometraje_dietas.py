"""Kilometraje y dietas: tax-exempt mileage (0,26 €/km, Orden HFP/792/2023) and meal allowances (RIRPF art. 9)."""

RIRPF = "https://www.boe.es/buscar/act.php?id=BOE-A-2007-6820"
HFP = "https://www.boe.es/buscar/doc.php?id=BOE-A-2023-16461"
AEAT = "https://sede.agenciatributaria.gob.es/Sede/irpf.html"

BLOCKS = [
    ("Lo que puede pagar la empresa sin que tribute", f"""
<p>Cuando viajas por trabajo con tu coche, la empresa puede pagarte hasta <b>0,26 € por kilómetro</b>, más peajes y aparcamiento
justificados, sin que cuente como salario ni lleve retención de IRPF. Es la cuantía del <a href="{RIRPF}#a9" rel="noopener">artículo 9
del Reglamento del IRPF</a>, actualizada por la <a href="{HFP}" rel="noopener">Orden HFP/792/2023</a> (antes eran 0,19 €). Un viaje
de 300 km son 78 € exentos. Si la empresa paga más, por ejemplo 0,30 €/km, los 0,04 € de diferencia por kilómetro tributan como
nómina.</p>
<p>Para las comidas y el alojamiento fuera de tu municipio de trabajo y de residencia, las <b>dietas exentas</b> son:</p>
<table class="tbl"><thead><tr><th>Manutención</th><th>España</th><th>Extranjero</th></tr></thead><tbody>
<tr><td>Sin pernoctar</td><td class=num>26,67 €/día</td><td class=num>48,08 €/día</td></tr>
<tr><td>Con pernocta</td><td class=num>53,34 €/día</td><td class=num>91,35 €/día</td></tr>
<tr><td>Alojamiento</td><td class=num>lo justificado</td><td class=num>lo justificado</td></tr></tbody></table>
<p>El hotel está exento por lo que se justifique con factura, sin límite fijo. Las dietas no se aplican si el desplazamiento al
mismo sitio dura más de nueve meses seguidos.</p>"""),
    ("Ejemplo y requisitos", """
<p>Una comercial hace en un mes 1.200 km con su coche, paga 18 € de peajes, come fuera seis días sin dormir fuera y pasa dos
noches en Valencia. Exento: 1.200 × 0,26 + 18 = 330 € de kilometraje, 6 × 26,67 = 160,02 € de dietas sin pernocta y 2 × 53,34 =
106,68 € con pernocta, más el hotel con su factura. En total, 596,70 € más el hotel que puede cobrar sin retención.</p>
<p>La empresa tiene que poder <b>acreditar el día, el lugar y el motivo</b> de cada desplazamiento; si Hacienda no lo ve probado,
lo trata como salario. Por eso conviene una hoja de gastos con fecha, origen, destino, kilómetros y cliente. Los desplazamientos
de casa al centro de trabajo habitual no cuentan. Los autónomos aplican los mismos importes de manutención como gasto
deducible si pagan con medios electrónicos y el gasto se produce en un establecimiento de hostelería.</p>"""),
]

FAQ = [
    ("¿Cuánto se paga por kilómetro en 2026?",
     "El máximo exento de IRPF es 0,26 €/km desde el 18 de julio de 2023. La empresa puede pagar más, pero el exceso tributa como salario. "
     "Muchos convenios fijan su propio precio por kilómetro."),
    ("¿Las dietas se declaran en la renta?",
     "Las exentas no. Aparecen en el certificado de retenciones como dietas exceptuadas de gravamen y no suman a tus ingresos."),
    ("¿Cuánto es la dieta de un día sin dormir fuera?",
     "26,67 € al día en España y 48,08 € en el extranjero, siempre fuera del municipio donde trabajas y de donde vives."),
    ("¿Se puede cobrar kilometraje y dieta el mismo día?",
     "Sí, son conceptos distintos: el kilometraje compensa el uso del coche y la dieta, la comida y el alojamiento."),
    ("¿Qué pasa si voy en tren o avión?",
     "Entonces está exento el importe del billete justificado con factura, en lugar de los 0,26 €/km."),
]

JS = r"""
function (v, H, C) {
  var KM = 0.26, L = v.ext ? [48.08, 91.35] : [26.67, 53.34];
  var km = isNaN(v.km) ? 0 : v.km, ek = isNaN(v.eurkm) ? KM : v.eurkm, a = isNaN(v.dsp) ? 0 : v.dsp, b = isNaN(v.dcp) ? 0 : v.dcp, pe = isNaN(v.peaje) ? 0 : v.peaje;
  if (km < 0 || ek < 0 || a < 0 || b < 0 || pe < 0) return { err: 'Sin números negativos.' };
  if (a % 1 || b % 1) return { err: 'Días: números enteros.' };
  if (!(km || a || b)) return { err: 'Escribe los kilómetros o los días de viaje.' };
  var exKm = H.r2(km * KM + pe), paidKm = H.r2(km * ek + pe), overKm = H.r2(Math.max(0, paidKm - exKm));
  var exD1 = H.r2(a * L[0]), exD2 = H.r2(b * L[1]), over = overKm, rows = [];
  if (km) rows.push(['Kilometraje ' + H.num(km, km % 1 ? 1 : 0) + ' km × 0,26 €', H.eur(H.r2(km * KM))]);
  if (pe) rows.push(['Peajes y aparcamiento', H.eur(pe)]);
  if (a) rows.push(['Dietas sin pernocta ' + a + ' × ' + H.eur(L[0]), H.eur(exD1)]);
  if (b) rows.push(['Dietas con pernocta ' + b + ' × ' + H.eur(L[1]), H.eur(exD2)]);
  var total = H.r2(exKm + exD1 + exD2);
  rows.push(['Total exento', H.eur(total), 'tot']);
  if (v.dieta >= 0 && (a || b)) { var od = H.r2(a * Math.max(0, v.dieta - L[0]) + b * Math.max(0, v.dieta - L[1])); over = H.r2(over + od); }
  if (over > 0) rows.push(['Tributa como salario', H.eur(over), 'z']);
  return {
    label: 'Exento de IRPF', big: H.eur(total),
    sub: (km && ek !== KM ? 'La empresa paga ' + H.eur(paidKm) + ' por los km · ' : '') + (b ? 'más el alojamiento justificado' : v.ext ? 'tarifas de extranjero' : 'tarifas de España'),
    rows: rows, n: { total: total, over: over }
  };
}
"""

TOOL = {
    "slug": "kilometraje-dietas",
    "lang": "es",
    "cat": "trabajo",
    "icon": "road",
    "order": 70,
    "name": "Kilometraje y dietas",
    "k": "0,26 €/km dietas exentas irpf manutención pernocta desplazamiento coche propio empresa",
    "title": "Kilometraje y dietas exentas 2026: 0,26 €/km y manutención",
    "desc": "Calcula el kilometraje (0,26 €/km) y las dietas que la empresa puede pagarte sin IRPF: 26,67 € o 53,34 € al día en España, y lo que tributa del exceso.",
    "h1": "Kilometraje y dietas exentas",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "km", "type": "number", "label": "Kilómetros", "value": 300, "unit": "km", "w": "s"},
        {"id": "eurkm", "type": "money", "label": "Pagado", "value": 0.26, "unit": "€/km", "w": "s"},
        {"id": "dsp", "type": "number", "label": "Días sin pernocta", "value": 0, "w": "s"},
        {"id": "dcp", "type": "number", "label": "Noches fuera", "value": 0, "w": "s"},
        {"id": "ext", "type": "check", "label": "Extranjero", "value": False},
        {"id": "peaje", "type": "money", "label": "Peajes y parking", "value": 0, "more": True, "w": "s"},
        {"id": "dieta", "type": "money", "label": "Dieta pagada al día", "value": "", "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Reglamento del IRPF, art. 9 (BOE)", RIRPF), ("Orden HFP/792/2023, 0,26 €/km (BOE)", HFP)],
    "related": ["factura-retencion-irpf", "cuota-autonomos-2026", "coste-viaje-coche", "multa-trafico-descuento"],
    "tests": [
        ({"km": "300"}, {"n.total": 78, "n.over": 0}),
        ({"km": "100", "eurkm": "0,30"}, {"n.total": 26, "n.over": 4}),
        ({"km": "0", "dsp": "2"}, {"n.total": 53.34}),
        ({"km": "0", "dcp": "3", "ext": "1"}, {"n.total": 274.05}),
        ({"km": "0", "dcp": "1", "dieta": "60"}, {"n.over": 6.66}),
        ({"km": "-5"}, {"err": "Sin números negativos."}),
    ],
}
