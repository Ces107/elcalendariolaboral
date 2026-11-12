"""Horas entre horas: time worked between two clock times (crossing midnight, minus a break), in h:mm and decimal; or
the sum of a list of durations ("8:30 + 7:45 - 0:30", decimals accepted) for weekly or monthly hour totals."""

ET = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"

JS = r"""
function (v, H, C) {
  function hm(m) { var s = m < 0 ? '−' : ''; m = Math.abs(Math.round(m)); return s + Math.floor(m / 60) + ' h ' + (m % 60 < 10 ? '0' : '') + m % 60 + ' min'; }
  function clock(m) { var s = m < 0 ? '−' : ''; m = Math.abs(Math.round(m)); return s + Math.floor(m / 60) + ':' + (m % 60 < 10 ? '0' : '') + m % 60; }
  function dec(m) { return H.num(m / 60, 2) + ' h'; }
  if (v.modo === 'sumar') {
    var s = String(v.lista || '').replace(/\s+/g, ' ').trim();
    if (!s) return { err: 'Escribe las horas, por ejemplo 8:30 + 7:45.' };
    var re = /([+\-−]?)\s*(\d{1,4})(?::(\d{1,2})|[.,](\d{1,2}))?/g, tot = 0, n = 0, m, rest = s;
    while ((m = re.exec(s))) {
      if (m[3] !== undefined && +m[3] > 59) return { err: 'Minutos de 0 a 59: ' + H.esc(m[0].trim()) };
      var mins = +m[2] * 60 + (m[3] !== undefined ? +m[3] : m[4] !== undefined ? Math.round(parseFloat('0.' + m[4]) * 60) : 0);
      tot += (m[1] === '-' || m[1] === '−') ? -mins : mins; n++;
    }
    rest = s.replace(re, '').replace(/[\s+;]/g, '');
    if (!n || rest) return { err: 'No entiendo «' + H.esc(rest || s) + '». Usa 8:30 o 7,5 separados por + o −.' };
    return { label: 'Total de horas', big: hm(tot), sub: clock(tot) + ' · ' + dec(tot),
      rows: [['Entradas', n], ['En minutos', H.num(tot, 0)], ['En decimal', dec(tot)], ['En días de 8 h', H.num(tot / 480, 2)]],
      n: { min: tot, items: n } };
  }
  function t(x) { var p = /^(\d{1,2}):(\d{2})$/.exec(x || ''); return p && +p[1] < 24 && +p[2] < 60 ? +p[1] * 60 + +p[2] : null; }
  var a = t(v.ini), b = t(v.fin), pz = v.pausa;
  if (a === null || b === null) return { err: 'Escribe las dos horas (hh:mm).' };
  if (isNaN(pz)) pz = 0;
  if (pz < 0) return { err: 'La pausa no puede ser negativa.' };
  if (a === b) return { err: 'Las dos horas son iguales.' };
  var gross = b > a ? b - a : b + 1440 - a, net = gross - pz;
  if (net <= 0) return { err: 'La pausa es más larga que el tiempo entre las dos horas.' };
  var rows = [['Tiempo entre horas', hm(gross)], ['Pausa', hm(pz)], ['Tiempo efectivo', hm(net), 'tot'], ['En decimal', dec(net)], ['En minutos', H.num(net, 0)]];
  if (b <= a) rows.push(['Cruza la medianoche', 'sí', 'z']);
  return { label: 'Horas trabajadas', big: hm(net), sub: v.ini + ' → ' + v.fin + (pz ? ' · ' + H.num(pz, 0) + ' min de pausa' : ''), rows: rows,
    note: net > 540 ? 'Más de 9 horas de trabajo efectivo: es el máximo diario ordinario del Estatuto de los Trabajadores, salvo que el convenio lo distribuya de otra forma.' : '',
    n: { min: net, gross: gross, night: b <= a } };
}
"""

BLOCKS = [
    ("Calcular horas trabajadas", """
<p>De 08:00 a 17:30 con media hora para comer son <b>9 horas de trabajo efectivo</b> (9,00 en decimal): 9 h 30 min entre las dos
horas menos los 30 minutos de pausa. Si la salida es anterior a la entrada, la calculadora entiende que el turno cruza la medianoche:
de 22:00 a 06:00 son 8 horas. El resultado sale en horas y minutos, en minutos y en horas decimales, que es como las piden muchas
nóminas, hojas de cálculo y programas de fichaje (7 h 45 min son 7,75 h, no 7,45).</p>
<p>Para sumar las horas de la semana o del mes, cambia a «Sumar horas» y escríbelas seguidas: <code>8:30 + 7:45 + 9:15 − 0:30</code>
da 25 h 00 min. Acepta horas con minutos (8:30), horas enteras (8), en decimal con coma o punto (7,5 son 7 h 30 min) y restas para descontar pausas o
ausencias. Es útil para cuadrar el registro de jornada o comprobar las horas extra de un mes.</p>"""),
    ("Lo que dice el Estatuto de los Trabajadores", f"""
<p>El <a href="{ET}#a34" rel="noopener">artículo 34</a> fija una jornada máxima de 40 horas semanales de trabajo efectivo de
promedio en cómputo anual y un máximo de 9 horas ordinarias al día, salvo que el convenio o un acuerdo distribuyan el tiempo de otra
forma. Entre el final de una jornada y el comienzo de la siguiente debe haber al menos 12 horas. Cuando la jornada diaria continuada
pasa de seis horas, hay derecho a una pausa de al menos 15 minutos, que solo cuenta como tiempo de trabajo si así lo dice el convenio
o el contrato.</p>
<p>El mismo artículo obliga a la empresa a registrar cada día la hora de entrada y salida de cada persona. Con esta calculadora puedes
comprobar las horas de cada día del registro, y con la suma, las de la semana: las que pasen de la jornada pactada son horas extra
(art. 35), con un máximo de 80 al año.</p>"""),
]

FAQ = [
    ("¿Cómo paso horas y minutos a decimal?",
     "Divide los minutos entre 60 y súmalos a las horas: 7 h 45 min son 7 + 45/60 = 7,75 h. La calculadora lo hace en la fila «En decimal»."),
    ("¿Cuántas horas son de 22:00 a 6:00?",
     "Ocho horas. Si la hora final es anterior a la inicial, se entiende que el turno pasa por la medianoche."),
    ("¿La pausa para el bocadillo cuenta como trabajo?",
     "Solo si el convenio o el contrato lo dicen. El Estatuto da derecho a 15 minutos de descanso en jornadas continuadas de más de seis "
     "horas, pero no obliga a pagarlos como trabajo."),
    ("¿Cómo sumo las horas de toda la semana?",
     "Elige «Sumar horas» y escribe las de cada día separadas por +, por ejemplo 8 + 8:30 + 7:45 + 8 + 6:15. Total: 38 h 30 min."),
    ("¿Cuántas horas puedo trabajar al día?",
     "Nueve horas ordinarias de trabajo efectivo como regla general (art. 34.3 del Estatuto), salvo que el convenio las distribuya de otra "
     "forma, y siempre con 12 horas de descanso entre jornadas."),
]

TOOL = {
    "slug": "horas-entre-horas",
    "lang": "es",
    "cat": "fechas",
    "icon": "clock-plus",
    "order": 90,
    "name": "Calcular horas",
    "k": "sumar horas restar horas trabajadas minutos decimal jornada turno",
    "title": "Calcular horas trabajadas: sumar y restar horas y minutos",
    "desc": "Calcula las horas entre dos horas con pausa y turnos de noche, o suma y resta horas y minutos. Resultado en h:mm, minutos y horas decimales.",
    "h1": "Calcular horas y minutos",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "modo", "type": "seg", "label": "Calcular", "value": "entre", "options": [("entre", "Entre dos horas"), ("sumar", "Sumar horas")]},
        {"id": "ini", "type": "time", "label": "Entrada", "value": "08:00", "show": ("modo", ["entre"])},
        {"id": "fin", "type": "time", "label": "Salida", "value": "17:30", "show": ("modo", ["entre"])},
        {"id": "pausa", "type": "number", "label": "Pausa", "value": 30, "unit": "min", "w": "s", "show": ("modo", ["entre"])},
        {"id": "lista", "type": "text", "label": "Horas", "value": "8:30 + 7:45 + 9:15 - 0:30", "w": "xl", "maxlength": 400, "show": ("modo", ["sumar"])},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Estatuto de los Trabajadores, arts. 34 y 35", ET)],
    "related": ["registro-jornada", "horas-extra", "cuadrante-turnos", "dias-entre-fechas"],
    "tests": [
        ({"ini": "08:00", "fin": "17:30", "pausa": "30"}, {"n.min": 540, "n.night": False}),
        ({"ini": "22:00", "fin": "06:00", "pausa": "0"}, {"n.min": 480, "n.night": True}),
        ({"modo": "sumar", "lista": "8:30 + 7:45 + 9:15 - 0:30"}, {"n.min": 1500, "n.items": 4}),
        ({"modo": "sumar", "lista": "7,5 8.25"}, {"n.min": 945}),
        ({"modo": "sumar", "lista": "8 + 8:30 + 7:45 + 8 + 6:15"}, {"n.min": 2310}),
        ({"modo": "sumar", "lista": "8:75"}, {"err": "Minutos de 0 a 59: 8:75"}),
        ({"ini": "08:00", "fin": "09:00", "pausa": "90"}, {"err": "La pausa es más larga que el tiempo entre las dos horas."}),
    ],
}
