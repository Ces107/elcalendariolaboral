"""Próxima ITV: next inspection dates by vehicle category and age (RD 920/2017, art. 6), with an .ics reminder."""

RD920 = "https://www.boe.es/buscar/act.php?id=BOE-A-2017-12841"
DGT = "https://www.dgt.es/nuestros-servicios/tu-vehiculo/tus-vehiculos/inspeccion-tecnica-de-vehiculos/"
# type: (label, exempt years, [(from age in years, months between inspections)])
RULES = {
    "m1": ("Turismo o autocaravana", 4, [(4, 24), (10, 12)]),
    "moto": ("Moto, triciclo o quad", 4, [(4, 24)]),
    "ciclo": ("Ciclomotor de 2 ruedas", 3, [(3, 24)]),
    "n1": ("Furgoneta ≤ 3,5 t", 2, [(2, 24), (6, 12), (10, 6)]),
    "pesado": ("Camión o remolque > 3,5 t", 0, [(0, 12), (10, 6)]),
    "bus": ("Autobús o microbús", 0, [(0, 12), (5, 6)]),
    "taxi": ("Taxi, ambulancia o escolar", 0, [(0, 12), (5, 6)]),
    "auto": ("Autoescuela", 2, [(2, 12), (5, 6)]),
    "carav": ("Caravana remolcada", 6, [(6, 24)]),
    "tr40": ("Tractor > 40 km/h", 4, [(4, 24), (16, 12)]),
    "tract": ("Tractor y maquinaria agrícola", 8, [(8, 24), (16, 12)]),
}

BLOCKS = [
    ("Cuándo toca la ITV", f"""
<p>Un <b>turismo particular</b> pasa la primera ITV al cumplir 4 años desde la primera matriculación, después cada dos años y,
a partir de los 10 años, todos los años. Un coche matriculado el 15 de marzo de 2016 pasó la ITV en marzo de 2020, 2022, 2024
y 2026, y desde ahí le toca cada marzo: la siguiente, el 15 de marzo de 2027. Las <b>furgonetas</b> de hasta 3,5 toneladas
empiezan a los 2 años, son anuales desde los 6 y semestrales desde los 10. Las <b>motos</b> y los quads, a los 4 años y luego
cada dos; los <b>ciclomotores</b>, a los 3 años y luego cada dos.</p>
<p>Las fechas salen del <a href="{RD920}#a6" rel="noopener">artículo 6 del Real Decreto 920/2017</a>, que fija la frecuencia por
categoría y antigüedad. La antigüedad se cuenta desde la fecha de primera matriculación que figura en el permiso de
circulación, no desde la fecha de compra: un coche importado de segunda mano conserva la de su primer país.</p>"""),
    ("Con la fecha de tu última ITV", """
<p>Si ya has pasado alguna inspección, escribe su fecha en «Última ITV»: la siguiente se cuenta desde el día en que la pasaste
con resultado favorable, no desde la matriculación. Así, si te retrasaste tres meses, tu calendario se ha movido tres meses.
La fecha exacta es la que figura en la tarjeta ITV o en la pegatina del parabrisas, que la estación calcula del mismo modo.</p>
<p>Hay una excepción que ayuda a no perder días: si pasas la ITV dentro de los <b>30 días anteriores</b> a que caduque, la
validez se cuenta desde la fecha de caducidad y no desde el día de la inspección. Adelantarla unas semanas no te cuesta nada;
adelantarla dos meses, sí. Con «Descargar .ics» añades las próximas fechas al calendario del móvil con un aviso un mes antes.</p>"""),
    ("Categorías especiales", """
<p>Los <b>taxis, ambulancias y vehículos de transporte escolar</b> pasan la ITV cada año desde el principio y cada seis meses
desde los 5 años; los de <b>autoescuela</b>, a los 2 años, anual hasta los 5 y luego semestral. Los <b>camiones y remolques</b>
de más de 3,5 toneladas y los <b>autobuses</b> no tienen periodo de exención: la primera inspección llega al año. Las
<b>caravanas</b> remolcadas (O2) están exentas 6 años y después van cada dos. Los vehículos mixtos siguen la frecuencia de las
furgonetas (categoría N) y los quads la de las motos.</p>
<p>Los vehículos históricos tienen su propio régimen: los de menos de 30 años siguen el de su categoría, entre 30 y 40 años
pasan cada dos años, entre 40 y 45 cada tres y desde 45 cada cuatro; los de más de 60 años y los ciclomotores históricos están
exentos.</p>"""),
]

FAQ = [
    ("¿Cuándo pasa la primera ITV un coche nuevo?",
     "A los 4 años de su primera matriculación. Después cada dos años hasta los 10 y, desde entonces, todos los años."),
    ("¿Puedo circular con la ITV caducada?",
     "No. Es una infracción grave con multa de 200 €, que sube a 500 € si la última inspección fue negativa. Con la ITV caducada solo "
     "puedes circular para ir a la estación a pasarla."),
    ("¿Cuánto antes puedo pasar la ITV sin perder días?",
     "Hasta 30 días naturales antes de la fecha de caducidad: en ese caso la nueva validez se cuenta desde la caducidad, no desde el "
     "día en que la pasas."),
    ("¿Las autocaravanas pasan la ITV como un coche?",
     "Sí, son de la categoría M1: exentas 4 años, después cada dos años y anual desde los 10. Las caravanas remolcadas son distintas: "
     "exentas 6 años y luego cada dos."),
    ("¿Cada cuánto pasa la ITV una moto?",
     "A los 4 años de la matriculación y después cada dos años, tenga la antigüedad que tenga. Los ciclomotores de hasta 50 cm³, a "
     "los 3 años y luego cada dos."),
]

JS = r"""
function (v, H, C) {
  var MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var R = C.d.rules[v.tipo];
  function addM(d, m) {   /* same day m months later, clamped to the month's last day */
    var y = d.getUTCFullYear(), mo = d.getUTCMonth() + m, yy = y + Math.floor(mo / 12), mm = ((mo % 12) + 12) % 12;
    return new Date(Date.UTC(yy, mm, Math.min(d.getUTCDate(), H.monthDays(yy, mm + 1))));
  }
  function fmt(d) { return d.getUTCDate() + ' de ' + MES[d.getUTCMonth()] + ' de ' + d.getUTCFullYear(); }
  function age(d) { var y = d.getUTCFullYear() - v.matr.getUTCFullYear(); if (addM(v.matr, 12 * y) > d) y--; return y; }
  function freq(d) { var a = age(d), f = R[2][0][1]; R[2].forEach(function (x) { if (a >= x[0]) f = x[1]; }); return f; }
  function fname(m) { return m === 24 ? 'bienal' : m === 12 ? 'anual' : m === 6 ? 'semestral' : 'cada ' + m + ' meses'; }
  if (!R) return { err: 'Elige el tipo de vehículo.' };
  if (!v.matr) return { err: 'Escribe la fecha de primera matriculación.' };
  if (v.ult && v.ult < v.matr) return { err: 'La última ITV no puede ser anterior a la matriculación.' };
  var first = R[1] ? addM(v.matr, 12 * R[1]) : addM(v.matr, R[2][0][1]);
  var list = [], d = v.ult ? addM(v.ult, freq(v.ult)) : first;
  if (v.ult && v.ult < first && R[1]) d = first;   /* a voluntary inspection while still exempt does not start the clock */
  for (var k = 0; k < 40 && list.length < 8; k++) { list.push(d); d = addM(d, freq(d)); }
  var now = H.today ? H.today() : null, next = list[0];
  if (now) for (k = 0; k < list.length; k++) if (list[k] >= now) { next = list[k]; break; }
  var left = now ? H.diff(now, next) : null, show = list.slice(Math.max(0, list.indexOf(next)), Math.max(0, list.indexOf(next)) + 6);
  var html = '<table class="tbl"><thead><tr><th>ITV</th><th>Antigüedad</th><th>Siguiente</th></tr></thead><tbody>' + show.map(function (x) {
    return '<tr><td>' + fmt(x) + '</td><td class="num">' + age(x) + ' años</td><td>' + fname(freq(x)) + '</td></tr>';
  }).join('') + '</tbody></table>';
  var ev = show.map(function (x) {
    return 'BEGIN:VEVENT\r\nUID:itv-' + H.icsDate(x) + '@elcalendariolaboral.es\r\nDTSTAMP:20261112T000000Z\r\nDTSTART;VALUE=DATE:' + H.icsDate(x) +
      '\r\nDTEND;VALUE=DATE:' + H.icsDate(H.add(x, 1)) + '\r\nSUMMARY:' + H.icsEsc('Caduca la ITV') +
      '\r\nBEGIN:VALARM\r\nACTION:DISPLAY\r\nDESCRIPTION:' + H.icsEsc('Pide cita para la ITV') + '\r\nTRIGGER:-P30D\r\nEND:VALARM\r\nEND:VEVENT';
  });
  return {
    label: v.ult ? 'Próxima ITV' : 'ITV', big: fmt(next),
    sub: (left === null ? '' : left < 0 ? 'Caducada hace ' + (-left) + ' días · ' : left === 0 ? 'Hoy · ' : 'Dentro de ' + left + ' ' + H.plural(left, 'día', 'días') + ' · ') +
      age(next) + ' años · después, ' + fname(freq(next)),
    html: html, note: v.ult ? '' : 'Sin «Última ITV», las fechas se cuentan desde la matriculación: si alguna vez la pasaste tarde, escribe la fecha real.',
    ics: { name: 'itv.ics', text: 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//elcalendariolaboral.es//ITV//ES\r\nCALSCALE:GREGORIAN\r\n' + ev.join('\r\n') + '\r\nEND:VCALENDAR\r\n' },
    n: { list: list.slice(0, 6).map(H.iso) }
  };
}
"""

TOOL = {
    "slug": "proxima-itv",
    "lang": "es",
    "cat": "vehiculos",
    "icon": "car",
    "order": 10,
    "name": "Próxima ITV",
    "k": "inspección técnica cuándo pasar itv coche moto furgoneta caducada frecuencia",
    "title": "¿Cuándo me toca la ITV? Calcula la próxima fecha",
    "desc": "Calcula cuándo te toca la próxima ITV del coche, la moto o la furgoneta según la fecha de matriculación y la última inspección (RD 920/2017).",
    "h1": "¿Cuándo me toca la ITV?",
    "updated": "2026-11-12",
    "data": {"rules": {k: [lab, ex, fr] for k, (lab, ex, fr) in RULES.items()}},
    "inputs": [
        {"id": "tipo", "type": "select", "label": "Vehículo", "value": "m1", "options": [(k, x[0]) for k, x in RULES.items()]},
        {"id": "matr", "type": "date", "label": "Matriculación", "value": "2018-06-01", "min": "1950-01-01", "max": "2030-12-31"},
        {"id": "ult", "type": "date", "label": "Última ITV", "value": "", "min": "1960-01-01", "max": "2030-12-31"},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Real Decreto 920/2017, art. 6 (BOE)", RD920), ("DGT · Inspección técnica de vehículos", DGT)],
    "related": ["multa-trafico-descuento", "kilometraje-dietas", "coste-viaje-coche", "etiqueta-dgt"],
    "tests": [
        ({"tipo": "m1", "matr": "2016-03-15"}, {"n.list": ["2020-03-15", "2022-03-15", "2024-03-15", "2026-03-15", "2027-03-15", "2028-03-15"]}),
        ({"tipo": "m1", "matr": "2013-01-01", "ult": "2025-06-10"}, {"n.list.0": "2026-06-10"}),
        ({"tipo": "n1", "matr": "2020-05-01"}, {"n.list": ["2022-05-01", "2024-05-01", "2026-05-01", "2027-05-01", "2028-05-01", "2029-05-01"]}),
        ({"tipo": "n1", "matr": "2020-05-31", "ult": "2029-05-31"}, {"n.list": ["2030-05-31", "2030-11-30", "2031-05-30", "2031-11-30", "2032-05-30", "2032-11-30"]}),
        ({"tipo": "pesado", "matr": "2025-01-10"}, {"n.list.0": "2026-01-10", "n.list.1": "2027-01-10"}),
        ({"tipo": "m1", "matr": "2020-01-01", "ult": "2019-01-01"}, {"err": "La última ITV no puede ser anterior a la matriculación."}),
    ],
}
