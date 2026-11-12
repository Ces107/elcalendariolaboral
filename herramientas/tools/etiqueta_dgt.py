"""Etiqueta ambiental de la DGT: CERO, ECO, C, B or none by vehicle type, engine, first registration date or Euro level
(DGT classification; Resolución DGT de 13 de abril de 2016, annex, and later yearly resolutions)."""

DGT = "https://www.dgt.es/nuestros-servicios/tu-vehiculo/informacion-publica-de-vehiculos/distintivo-ambiental/"
SEDE = "https://sede.dgt.gob.es/es/vehiculos/informacion-de-vehiculos/distintivo-ambiental/index.html"
RES16 = "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2016-3828"

BLOCKS = [
    ("Qué etiqueta le toca a tu coche", f"""
<p>La DGT reparte los vehículos en cuatro distintivos según lo que contaminan; el resto, más o menos la mitad más
contaminante del parque, se queda <b>sin etiqueta</b>. Para un turismo o una furgoneta ligera de combustión, la regla depende
del combustible y de la fecha de primera matriculación:</p>
<table class="tbl"><thead><tr><th>Etiqueta</th><th>Gasolina</th><th>Diésel</th></tr></thead><tbody>
<tr><td><b>C</b> verde</td><td>desde enero de 2006 (Euro 4, 5 y 6)</td><td>desde septiembre de 2015 (Euro 6)</td></tr>
<tr><td><b>B</b> amarilla</td><td>desde enero de 2001 (Euro 3)</td><td>desde 2006 (Euro 4 y 5)</td></tr>
<tr><td>Sin etiqueta</td><td>antes de 2001</td><td>antes de 2006</td></tr></tbody></table>
<p>La <b>ECO</b> es para los híbridos no enchufables, los enchufables con menos de 40 km de autonomía eléctrica y los de gas
(GLP, GNC o GNL), siempre que cumplan además los requisitos de la C. La <b>CERO</b> azul, para los eléctricos de batería, los de
autonomía extendida, los híbridos enchufables con 40 km o más de autonomía eléctrica y los de pila de combustible.</p>
<p>Los vehículos de más de 8 plazas y los pesados (autobuses, camiones) tienen la C desde 2014 (Euro VI) y la B desde 2006
(Euro IV y V), sean de gasolina o diésel. Las motos y ciclomotores se clasifican por su norma Euro: Euro 3 o posterior, C;
Euro 2, B.</p>"""),
    ("Las fechas son una aproximación: manda la norma Euro", f"""
<p>La clasificación oficial, publicada en el anexo de la <a href="{RES16}" rel="noopener">Resolución de la DGT de 13 de abril de
2016</a> y mantenida en las resoluciones posteriores, no habla de años sino de normas Euro: un turismo de gasolina Euro 4 es C
aunque se matriculara en 2005, y uno de 2006 que se homologó como Euro 3 se queda en B. Las fechas de la tabla son las que da la
propia DGT porque coinciden con el momento en que cada norma pasó a ser obligatoria para todos los coches nuevos. Si conoces la
norma Euro de tu vehículo (aparece en la ficha técnica, en el apartado de emisiones o en la homologación), elígela en «Más
opciones» y la calculadora la usará en lugar de la fecha.</p>
<p>Ejemplo: un diésel matriculado en marzo de 2015 sale con la B por fecha, pero muchos modelos de ese año ya eran Euro 6.
Si su ficha dice Euro 6, le corresponde la C.</p>"""),
    ("Cómo comprobarlo con la matrícula", f"""
<p>La respuesta de esta calculadora es orientativa. La etiqueta que vale es la que figura en el Registro de Vehículos, y se
consulta gratis con la matrícula en la <a href="{SEDE}" rel="noopener">sede electrónica de la DGT</a> o en la app miDGT. Si te
corresponde una, la pegatina se compra en Correos, talleres autorizados y algunas gestorías por unos 5 €; en los coches va en
el ángulo inferior derecho del parabrisas, y en las motos, en cualquier lugar visible.</p>
<p>La etiqueta importa porque las zonas de bajas emisiones (ZBE) que los municipios de más de 50.000 habitantes están obligados
a crear la usan para decidir quién entra. Cada ayuntamiento fija sus propias restricciones: consulta la ordenanza de la ciudad
a la que vas.</p>"""),
]

FAQ = [
    ("¿Qué etiqueta tiene un coche de gasolina de 2005?",
     "Por fecha, la B. Si su ficha técnica indica que es Euro 4, le corresponde la C: algunos modelos de 2005 ya cumplían esa norma."),
    ("¿Qué etiqueta tiene un diésel de 2015?",
     "Depende del mes y de la norma: desde septiembre de 2015 todos los diésel nuevos eran Euro 6 (etiqueta C). Los de antes, B, "
     "salvo que ya estuvieran homologados como Euro 6."),
    ("¿Un coche de GLP tiene etiqueta ECO?",
     "Sí, si cumple también los requisitos de la C: un GLP de gasolina Euro 4 o posterior es ECO; uno más antiguo, no. En un "
     "coche transformado, cuenta lo que figure en el Registro de Vehículos después de legalizar la reforma en la ITV."),
    ("¿Los híbridos enchufables tienen etiqueta CERO?",
     "Solo si su autonomía eléctrica homologada es de 40 km o más. Con menos de 40 km, la ECO."),
    ("¿Qué pasa si mi coche no tiene etiqueta?",
     "Puedes circular con normalidad fuera de las zonas restringidas. En las ZBE y en episodios de contaminación, cada ciudad decide "
     "si puede entrar y en qué horario."),
    ("¿Dónde consulto la etiqueta de mi coche?",
     "En la sede electrónica de la DGT, con la matrícula, o en la app miDGT. Es gratis y es el dato oficial."),
]

JS = r"""
function (v, H, C) {
  var T = { '0': ['CERO', 'Cero emisiones · azul'], ECO: ['ECO', 'Eco · azul y verde'], C: ['C', 'Verde'], B: ['B', 'Amarilla'], '': ['Sin etiqueta', 'No le corresponde distintivo'] };
  var t = v.tipo, m = v.mot, why = '', near = false, tag;
  function d(y, mo) { return Date.UTC(y, mo - 1, 1); }
  function byFuel(f) {   /* combustion classification of the base engine: 'C' | 'B' | '' */
    var e = v.euro ? +v.euro : 0, ms = v.fecha ? v.fecha.getTime() : NaN;
    if (t === 'pes') {
      if (e) { why = 'Euro ' + ['', 'I', 'II', 'III', 'IV', 'V', 'VI'][e]; return e >= 6 ? 'C' : e >= 4 ? 'B' : ''; }
      why = 'matriculado ' + (ms >= d(2014, 1) ? 'desde 2014' : ms >= d(2006, 1) ? 'entre 2006 y 2013' : 'antes de 2006');
      near = Math.abs(ms - d(2014, 1)) < 366 * 864e5 || Math.abs(ms - d(2006, 1)) < 366 * 864e5;
      return ms >= d(2014, 1) ? 'C' : ms >= d(2006, 1) ? 'B' : '';
    }
    if (e) { why = (f === 'g' ? 'gasolina' : 'diésel') + ' Euro ' + e; return f === 'g' ? (e >= 4 ? 'C' : e === 3 ? 'B' : '') : (e >= 6 ? 'C' : e >= 4 ? 'B' : ''); }
    var c1 = f === 'g' ? d(2006, 1) : d(2015, 9), b1 = f === 'g' ? d(2001, 1) : d(2006, 1);
    why = (f === 'g' ? 'gasolina' : 'diésel') + ' matriculado ' + (ms >= c1 ? (f === 'g' ? 'desde enero de 2006' : 'desde septiembre de 2015') :
      ms >= b1 ? (f === 'g' ? 'entre 2001 y 2005' : 'entre 2006 y agosto de 2015') : (f === 'g' ? 'antes de 2001' : 'antes de 2006'));
    near = Math.abs(ms - c1) < 366 * 864e5 || Math.abs(ms - b1) < 366 * 864e5;
    return ms >= c1 ? 'C' : ms >= b1 ? 'B' : '';
  }
  if (m === 'elec') { tag = '0'; why = 'eléctrico, autonomía extendida o pila de combustible'; }
  else if (t === 'l') {
    var e = +v.eurol;
    if (!e) return { err: 'Elige la norma Euro de la moto (está en su ficha técnica).' };
    tag = e >= 3 ? 'C' : e === 2 ? 'B' : ''; why = 'moto o ciclomotor Euro ' + e;
  } else {
    if (!v.fecha) return { err: 'Escribe la fecha de primera matriculación.' };
    if (v.fecha.getUTCFullYear() < 1950) return { err: 'Fecha de matriculación fuera de rango.' };
    var f = m === 'diesel' || ((m === 'hev' || m === 'phev') && v.base === 'd') ? 'd' : 'g';
    var b = byFuel(f);
    if (m === 'phev') {
      if (isNaN(v.aut) || v.aut < 0) return { err: 'Escribe la autonomía eléctrica homologada en km.' };
      if (v.aut >= 40) { tag = '0'; why = 'híbrido enchufable con ' + H.num(v.aut, 0) + ' km eléctricos'; near = false; }
      else { tag = b === 'C' ? 'ECO' : b; why = 'híbrido enchufable con menos de 40 km eléctricos · ' + why; }
    } else if (m === 'hev' || m === 'gas') {
      tag = b === 'C' ? 'ECO' : b; why = (m === 'hev' ? 'híbrido no enchufable' : 'gas (GLP, GNC o GNL)') + ' · ' + why;
      if (b !== 'C') why += ' · no cumple los requisitos de la C, así que no llega a ECO';
    } else tag = b;
  }
  var cls = { '0': 'z0', ECO: 'zeco', C: 'zc', B: 'zb', '': 'zn' }[tag];
  return {
    label: 'Distintivo ambiental', big: T[tag][0], sub: T[tag][1] + ' · ' + why,
    html: '<div class="dgt-tag ' + cls + '" aria-hidden="true">' + (tag === '' ? '—' : tag === '0' ? '0' : tag) + '</div>',
    note: (near && !v.euro ? 'Fecha cerca de un cambio de norma: si conoces la norma Euro, elígela en «Más opciones». ' : '') +
      'Orientativo: la etiqueta oficial se consulta con la matrícula en la sede de la DGT.',
    n: { tag: tag }
  };
}
"""

CSS = """
.dgt-tag{width:72px;height:72px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:700 26px/1 system-ui,sans-serif;margin:8px 0;border:3px solid #fff;box-shadow:0 0 0 2px #888}
.dgt-tag.z0{background:#1f5fae;color:#fff}.dgt-tag.zeco{background:linear-gradient(90deg,#1f5fae 50%,#2e9a48 50%);color:#fff}
.dgt-tag.zc{background:#2e9a48;color:#fff}.dgt-tag.zb{background:#f2c200;color:#222}.dgt-tag.zn{background:#ddd;color:#555}
"""

TOOL = {
    "slug": "etiqueta-dgt",
    "lang": "es",
    "cat": "vehiculos",
    "icon": "leaf",
    "order": 25,
    "name": "Etiqueta DGT",
    "k": "distintivo ambiental pegatina eco cero c b zbe zona bajas emisiones qué etiqueta tiene mi coche",
    "title": "¿Qué etiqueta de la DGT tiene mi coche? CERO, ECO, C o B",
    "desc": "Averigua qué etiqueta ambiental de la DGT (CERO, ECO, C o B) le corresponde a tu coche, moto o furgoneta por combustible y fecha de matriculación.",
    "h1": "¿Qué etiqueta de la DGT tiene mi coche?",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "tipo", "type": "select", "label": "Vehículo", "value": "m1", "options": [
            ("m1", "Turismo o furgoneta ligera"), ("l", "Moto o ciclomotor"), ("pes", "Más de 8 plazas o pesado")]},
        {"id": "mot", "type": "select", "label": "Motor", "value": "gasolina", "options": [
            ("gasolina", "Gasolina"), ("diesel", "Diésel"), ("hev", "Híbrido no enchufable"), ("phev", "Híbrido enchufable"),
            ("gas", "GLP, GNC o GNL"), ("elec", "Eléctrico o hidrógeno")]},
        {"id": "base", "type": "seg", "label": "Motor térmico", "value": "g", "options": [("g", "Gasolina"), ("d", "Diésel")],
         "show": ("mot", ["hev", "phev"])},
        {"id": "aut", "type": "number", "label": "Autonomía eléctrica", "value": "50", "unit": "km", "w": "s", "show": ("mot", ["phev"])},
        {"id": "fecha", "type": "date", "label": "Matriculación", "value": "2012-05-01", "min": "1950-01-01", "max": "2030-12-31",
         "show": ("tipo", ["m1", "pes"])},
        {"id": "eurol", "type": "select", "label": "Norma Euro", "value": "4", "show": ("tipo", ["l"]), "options": [
            ("1", "Euro 1 o anterior"), ("2", "Euro 2"), ("3", "Euro 3"), ("4", "Euro 4"), ("5", "Euro 5 o posterior")]},
        {"id": "euro", "type": "select", "label": "Norma Euro", "value": "", "more": True, "show": ("tipo", ["m1", "pes"]), "options": [
            ("", "Por fecha"), ("1", "Euro 1 / I"), ("2", "Euro 2 / II"), ("3", "Euro 3 / III"), ("4", "Euro 4 / IV"), ("5", "Euro 5 / V"), ("6", "Euro 6 / VI")]},
    ],
    "js": JS,
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("DGT · Distintivo ambiental (clasificación y fechas)", DGT),
                ("Resolución de la DGT de 13 de abril de 2016, anexo de clasificación (BOE-A-2016-3828)", RES16),
                ("Sede electrónica de la DGT · consulta del distintivo por matrícula", SEDE)],
    "credits": [],
    "related": ["proxima-itv", "multa-trafico-descuento", "coste-coche-electrico", "coste-viaje-coche"],
    "tests": [
        ({}, {"n.tag": "C"}),
        ({"mot": "diesel", "fecha": "2015-06-01"}, {"n.tag": "B"}),
        ({"mot": "diesel", "fecha": "2015-06-01", "euro": "6"}, {"n.tag": "C"}),
        ({"fecha": "1999-03-01"}, {"n.tag": ""}),
        ({"mot": "phev", "aut": "30", "fecha": "2020-01-10"}, {"n.tag": "ECO"}),
        ({"mot": "hev", "base": "d", "fecha": "2012-01-10"}, {"n.tag": "B"}),
    ],
}
