"""Horas de conducción (tacógrafo): what is left today, this week and this fortnight under Regulation (EC) 561/2006."""

R561 = "https://eur-lex.europa.eu/eli/reg/2006/561/oj/spa"
R561_SUM = "https://eur-lex.europa.eu/ES/legal-content/summary/driving-time-and-rest-periods-in-the-road-transport-sector.html"
R2020 = "https://eur-lex.europa.eu/eli/reg/2020/1054/oj/spa"
RD1561 = "https://www.boe.es/buscar/act.php?id=BOE-A-1995-21781"

JS = r"""
function (v, H, C) {
  function p(s, name) { /* '4:30', '4h30', '4,5', '4.5', '270m' -> minutes; '' -> 0 */
    s = String(s || '').trim().toLowerCase().replace(/\s/g, '');
    if (!s) return 0;
    var m = /^(\d{1,3})(?:[:h](\d{1,2}))?h?$/.exec(s);
    if (m && (!m[2] || +m[2] < 60)) return +m[1] * 60 + (m[2] ? +m[2] : 0);
    m = /^(\d{1,3})[.,](\d{1,2})$/.exec(s);
    if (m) return Math.round(parseFloat(m[1] + '.' + m[2]) * 60);
    m = /^(\d{1,4})m(in)?$/.exec(s);
    if (m) return +m[1];
    throw name;
  }
  function f(min) { min = Math.max(0, Math.round(min)); return Math.floor(min / 60) + ':' + ('0' + min % 60).slice(-2) + ' h'; }
  var t, b, w, a;
  try { t = p(v.hoy, 'Hoy'); b = p(v.pausa, 'Desde la pausa'); w = p(v.semana, 'Esta semana'); a = p(v.ant, 'Semana anterior'); }
  catch (e) { return { err: e + ': escribe horas y minutos, por ejemplo 4:30.' }; }
  if (t > 24 * 60) return { err: 'Hoy: no más de 24 horas.' };
  if (w < t) return { err: 'Esta semana incluye lo conducido hoy: no puede ser menos que «Hoy».' };
  if (b > t) return { err: 'Desde la pausa: no puede ser más que lo conducido hoy.' };
  var ext = +v.ext || 0, can10 = ext < 2;
  var d9 = Math.max(0, 540 - t), d10 = can10 ? Math.max(0, 600 - t) : 0;
  var wk = Math.max(0, 3360 - w), fo = Math.max(0, 5400 - a - w), br = Math.max(0, 270 - b);
  var left = Math.min(can10 ? Math.max(d9, d10) : d9, wk, fo), next = Math.max(0, Math.min(3360, 5400 - w));
  var bad = [];
  if (t > 600 || (t > 540 && !can10)) bad.push('Hoy pasas del máximo diario (' + (can10 ? '10' : '9') + ' h).');
  if (w > 3360) bad.push('Esta semana pasas de 56 h.');
  if (a > 3360) bad.push('La semana anterior pasó de 56 h.');
  if (a + w > 5400) bad.push('Las dos semanas suman más de 90 h.');
  if (b > 270) bad.push('Llevas más de 4:30 h sin la pausa de 45 min.');
  var cap = can10 ? d10 : d9;
  var why = left === fo && fo < Math.min(cap, wk) ? 'lo limita la quincena (90 h)' : left === wk && wk < cap ? 'lo limita la semana (56 h)' :
    can10 && left > d9 ? 'usando una ampliación a 10 h' : 'jornada de 9 h';
  return {
    label: 'Puedes conducir hoy', big: f(left),
    sub: H.esc(why) + (left > 0 ? ' · pausa de 45 min dentro de ' + f(Math.min(br, left)) : ''),
    rows: [
      ['Hoy hasta 9 h', f(d9)],
      ['Hoy hasta 10 h', can10 ? f(d10) : 'ya usaste 2'],
      ['Semana (56 h)', f(wk)],
      ['Quincena (90 h)', f(fo)],
      ['Antes de la pausa', f(br)],
      ['Máximo la semana que viene', f(next), 'sub']
    ],
    html: bad.length ? '<p class="herr">' + bad.join(' ') + '</p>' : '',
    note: 'La semana va de lunes 00:00 a domingo 24:00. «La semana que viene» supone que no conduces más esta semana.',
    n: { left: left, d9: d9, d10: d10, wk: wk, fo: fo, br: br, next: next, bad: bad.length }
  };
}
"""

BLOCKS = [
    ("Cuántas horas puedes conducir", f"""
<p>Con el <a href="{R561}" rel="noopener">Reglamento (CE) 561/2006</a> un conductor profesional puede conducir como máximo
<b>9 horas al día</b>, que pueden ser <b>10 horas dos veces por semana</b>; <b>56 horas a la semana</b> y <b>90 horas en dos semanas
seguidas</b>. Después de 4 horas y media de conducción tiene que parar <b>45 minutos</b>. La calculadora resta lo que ya llevas de
cada uno de esos cuatro límites y te dice el que manda: a veces es el día, pero un jueves de una semana cargada suele ser la
quincena.</p>
<p>Escribe los tiempos como en el tacógrafo, en horas y minutos (<code>4:30</code>). «Esta semana» incluye lo conducido hoy y
«Días de 10 h» son las ampliaciones que ya gastaste en otros días de esta semana.</p>"""),
    ("Ejemplo", """
<p>Un camionero lleva 6:00 h hoy, la última pausa la hizo hace 1:30 h, suma 47:00 h esta semana y la semana pasada hizo 50:00 h.
No ha ampliado ningún día.</p>
<ul>
<li>Día: con ampliación le quedan 10:00 − 6:00 = <b>4:00 h</b> (3:00 h sin ampliar).</li>
<li>Semana: 56:00 − 47:00 = <b>9:00 h</b>.</li>
<li>Quincena: 90:00 − 50:00 − 47:00 = <b>0:00 h</b>. Ya ha agotado las 90 horas: hoy no puede conducir más, aunque el día y la
semana le dejarían.</li>
</ul>
<p>Si la semana pasada hubiera hecho 40:00 h, la quincena le dejaría 3:00 h y ese sería su máximo de hoy. La semana que viene podrá
conducir 90:00 − 47:00 = 43:00 h, no 56, si esta semana no conduce más.</p>"""),
    ("Pausas y descansos", f"""
<p><b>Pausa</b> (artículo 7): 45 minutos tras 4:30 h de conducción, o una de 15 minutos seguida de otra de 30 repartidas dentro de
ese tiempo. Una pausa más corta de 15 minutos no cuenta.</p>
<p><b>Descanso diario</b> (artículo 8): 11 horas seguidas dentro de cada periodo de 24 horas, o 3 + 9 horas. Se puede reducir a 9
horas como máximo tres veces entre dos descansos semanales.</p>
<p><b>Descanso semanal</b>: 45 horas, o 24 horas reducido, que se compensa con un descanso equivalente antes de que acabe la tercera
semana. Nunca pueden pasar más de seis periodos de 24 horas desde el descanso semanal anterior. En dos semanas seguidas hacen falta
dos descansos normales, o uno normal y uno reducido.</p>
<p>Estas reglas son de tiempo de <i>conducción</i>. El tiempo de <i>trabajo</i> (carga, espera, papeles) tiene otro tope en España: 60
horas en una semana y 48 de promedio en cuatro meses, según el <a href="{RD1561}" rel="noopener">Real Decreto 1561/1995</a>.</p>"""),
    ("A quién se aplica", f"""
<p>A los vehículos de mercancías de más de 3,5 toneladas y a los de viajeros de más de nueve plazas, conductor incluido. Desde el 1
de julio de 2026, por el <a href="{R2020}" rel="noopener">Reglamento (UE) 2020/1054</a>, también a las furgonetas de más de 2,5
toneladas que hacen transporte internacional o cabotaje, que deben llevar tacógrafo inteligente.</p>"""),
]

FAQ = [
    ("¿Cuántas veces puedo conducir 10 horas a la semana?",
     "Dos veces por semana, de lunes a domingo. Los demás días el máximo es de 9 horas."),
    ("¿Puedo partir la pausa de 45 minutos?",
     "Sí, en dos: primero una de al menos 15 minutos y después una de al menos 30, las dos dentro de las 4 horas y media de conducción."),
    ("¿Qué es la semana para el tacógrafo?",
     "La semana natural: de las 00:00 del lunes a las 24:00 del domingo. Las 90 horas se cuentan en dos semanas naturales seguidas, "
     "por eso la semana anterior limita esta."),
    ("Si hice 56 horas la semana pasada, ¿cuánto puedo hacer esta?",
     "34 horas como máximo, porque las dos semanas no pueden pasar de 90."),
    ("¿Cuánto tengo que descansar entre jornadas?",
     "11 horas seguidas, o 3 + 9. Tres veces entre dos descansos semanales puedes reducirlo a 9 horas."),
    ("¿Las furgonetas necesitan tacógrafo?",
     "Las de más de 2,5 toneladas que hacen transporte internacional o cabotaje, desde el 1 de julio de 2026. Las de reparto dentro de "
     "España por debajo de 3,5 toneladas, no."),
]

TOOL = {
    "slug": "horas-conduccion-tacografo",
    "lang": "es",
    "cat": "trabajo",
    "icon": "truck",
    "order": 60,
    "name": "Horas de conducción",
    "k": "tacógrafo camionero 561/2006 pausa descanso 9 horas 56 90",
    "title": "Horas de conducción y tacógrafo: cuánto te queda hoy",
    "desc": "Calcula cuántas horas puedes conducir hoy, esta semana y en la quincena con el tacógrafo: 9 o 10 h, 56 h, 90 h y pausa de 45 min (Reglamento 561/2006).",
    "h1": "Calculadora de horas de conducción",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "hoy", "type": "text", "label": "Hoy", "value": "6:00", "maxlength": 6, "w": "s", "placeholder": "h:mm"},
        {"id": "pausa", "type": "text", "label": "Desde la pausa", "value": "1:30", "maxlength": 6, "w": "s", "placeholder": "h:mm"},
        {"id": "semana", "type": "text", "label": "Esta semana", "value": "30:00", "maxlength": 6, "w": "s", "placeholder": "h:mm"},
        {"id": "ant", "type": "text", "label": "Semana anterior", "value": "45:00", "maxlength": 6, "w": "s", "placeholder": "h:mm"},
        {"id": "ext", "type": "seg", "label": "Días de 10 h", "value": "0", "options": [("0", "0"), ("1", "1"), ("2", "2")]},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Reglamento (CE) 561/2006, arts. 6-8 (EUR-Lex)", R561), ("Resumen oficial del Reglamento 561/2006 (EUR-Lex)", R561_SUM),
                ("Reglamento (UE) 2020/1054", R2020), ("Real Decreto 1561/1995 (BOE)", RD1561)],
    "related": ["registro-jornada", "horas-extra", "cuadrante-turnos"],
    "tests": [
        ({"hoy": "6:00", "pausa": "1:30", "semana": "47:00", "ant": "50:00", "ext": "0"}, {"n.left": 0, "n.fo": 0, "n.d10": 240, "n.wk": 540}),
        ({"hoy": "6:00", "pausa": "1:30", "semana": "47:00", "ant": "40:00", "ext": "0"}, {"n.left": 180, "n.next": 2580}),
        ({"hoy": "4:30", "pausa": "4:30", "semana": "20", "ant": "30", "ext": "2"}, {"n.left": 270, "n.d10": 0, "n.br": 0}),
        ({"hoy": "8,5", "pausa": "", "semana": "8:30", "ant": "", "ext": "1"}, {"n.left": 90, "n.d9": 30, "n.bad": 0}),
        ({"hoy": "10:15", "pausa": "5:00", "semana": "57:00", "ant": "40:00"}, {"n.left": 0, "n.bad": 4}),
        ({"hoy": "5:00", "semana": "3:00"}, {"err": "Esta semana incluye lo conducido hoy: no puede ser menos que «Hoy»."}),
        ({"hoy": "abc"}, {"err": "Hoy: escribe horas y minutos, por ejemplo 4:30."}),
    ],
}
