"""Etapas del Camino de Santiago a tu ritmo: Francés, Portugués central, Norte and Primitivo stage lists (Gronze,
Nov 2026), plan by km per day (stages merged, or split when much longer than the target), rest days, dates, .ics and
the Compostela 100 km check. EN twin: camino-de-santiago-planner."""
from herramientas.tools import _deporte as D

GRONZE = "https://www.gronze.com/"

# (from, to, km) as published by gronze.com (Nov 2026). Francés = the 33 stages also used by the KDP Camino journal.
FRANCES = [
    ("Saint-Jean-Pied-de-Port", "Roncesvalles", 24.2), ("Roncesvalles", "Zubiri", 21.4),
    ("Zubiri", "Pamplona", 20.4), ("Pamplona", "Puente la Reina", 23.9), ("Puente la Reina", "Estella", 21.6),
    ("Estella", "Los Arcos", 21.3), ("Los Arcos", "Logroño", 27.6), ("Logroño", "Nájera", 28.5),
    ("Nájera", "Santo Domingo de la Calzada", 20.7), ("Santo Domingo de la Calzada", "Belorado", 22.0),
    ("Belorado", "San Juan de Ortega", 23.9), ("San Juan de Ortega", "Burgos", 25.8),
    ("Burgos", "Hornillos del Camino", 20.3), ("Hornillos del Camino", "Castrojeriz", 19.9),
    ("Castrojeriz", "Frómista", 24.7), ("Frómista", "Carrión de los Condes", 18.8),
    ("Carrión de los Condes", "Terradillos de los Templarios", 26.3),
    ("Terradillos de los Templarios", "Bercianos del Real Camino", 23.2),
    ("Bercianos del Real Camino", "Mansilla de las Mulas", 26.3), ("Mansilla de las Mulas", "León", 18.4),
    ("León", "San Martín del Camino", 24.6), ("San Martín del Camino", "Astorga", 23.7),
    ("Astorga", "Foncebadón", 25.8), ("Foncebadón", "Ponferrada", 26.8), ("Ponferrada", "Villafranca del Bierzo", 23.2),
    ("Villafranca del Bierzo", "O Cebreiro", 27.8), ("O Cebreiro", "Triacastela", 20.6),
    ("Triacastela", "Sarria", 17.8), ("Sarria", "Portomarín", 22.2), ("Portomarín", "Palas de Rei", 24.8),
    ("Palas de Rei", "Arzúa", 28.5), ("Arzúa", "O Pedrouzo", 19.3), ("O Pedrouzo", "Santiago de Compostela", 19.4),
]
PORTUGUES = [
    ("Lisboa", "Vila Franca de Xira", 34.2), ("Vila Franca de Xira", "Azambuja", 20.0), ("Azambuja", "Santarém", 33.0),
    ("Santarém", "Golegã", 30.7), ("Golegã", "Tomar", 30.3), ("Tomar", "Alvaiázere", 31.4), ("Alvaiázere", "Alvorge", 22.7),
    ("Alvorge", "Cernache", 26.1), ("Cernache", "Coimbra", 11.3), ("Coimbra", "Sernadelo", 24.8), ("Sernadelo", "Águeda", 23.5),
    ("Águeda", "Albergaria-a-Velha", 15.8), ("Albergaria-a-Velha", "São João da Madeira", 28.8),
    ("São João da Madeira", "Grijó", 19.0), ("Grijó", "Porto", 15.1), ("Porto", "Vilarinho", 26.5), ("Vilarinho", "Barcelos", 28.1),
    ("Barcelos", "Ponte de Lima", 34.5), ("Ponte de Lima", "Rubiães", 17.4), ("Rubiães", "Tui", 19.1), ("Tui", "Redondela", 31.9),
    ("Redondela", "Pontevedra", 19.8), ("Pontevedra", "Caldas de Reis", 21.1), ("Caldas de Reis", "Padrón", 18.6),
    ("Padrón", "Santiago de Compostela", 24.4),
]
# official variants: 10A Portugalete, 29A by Tol, 35A by Miraz; Arzúa onwards = Camino Francés
NORTE = [
    ("Bayonne", "Saint-Jean-de-Luz", 28.3), ("Saint-Jean-de-Luz", "Irún", 15.4), ("Irún", "San Sebastián", 24.7),
    ("San Sebastián", "Zarautz", 22.1), ("Zarautz", "Deba", 21.0), ("Deba", "Markina-Xemein", 23.3), ("Markina-Xemein", "Gernika", 25.4),
    ("Gernika", "Lezama", 19.8), ("Lezama", "Bilbao", 11.0), ("Bilbao", "Portugalete", 19.2), ("Portugalete", "Castro Urdiales", 32.1),
    ("Castro Urdiales", "Laredo", 30.5), ("Laredo", "Güemes", 28.7), ("Güemes", "Santander", 15.3),
    ("Santander", "Santillana del Mar", 36.3), ("Santillana del Mar", "Comillas", 22.2), ("Comillas", "Colombres", 28.0),
    ("Colombres", "Llanes", 22.9), ("Llanes", "Ribadesella", 30.0), ("Ribadesella", "Colunga", 20.1), ("Colunga", "Villaviciosa", 17.5),
    ("Villaviciosa", "Gijón", 29.8), ("Gijón", "Avilés", 25.4), ("Avilés", "Muros de Nalón", 21.2), ("Muros de Nalón", "Soto de Luiña", 15.3),
    ("Soto de Luiña", "Cadavedo", 18.5), ("Cadavedo", "Luarca", 15.9), ("Luarca", "La Caridad", 30.5), ("La Caridad", "Ribadeo", 21.3),
    ("Ribadeo", "Gondán", 20.9), ("Gondán", "Mondoñedo", 15.6), ("Mondoñedo", "Abadín", 16.6), ("Abadín", "Vilalba", 20.8),
    ("Vilalba", "Baamonde", 18.5), ("Baamonde", "Sobrado dos Monxes", 39.8), ("Sobrado dos Monxes", "Arzúa", 22.0),
    ("Arzúa", "O Pedrouzo", 19.3), ("O Pedrouzo", "Santiago de Compostela", 19.4),
]
# 5A by Hospitales; Melide-Arzúa = Gronze's Palas de Rei-Arzúa (28.5) minus Palas-Melide (14.8)
PRIMITIVO = [
    ("Oviedo", "Grado", 25.2), ("Grado", "Salas", 22.3), ("Salas", "Tineo", 19.8), ("Tineo", "Borres", 15.9),
    ("Borres", "Berducedo", 24.1), ("Berducedo", "Grandas de Salime", 20.4), ("Grandas de Salime", "A Fonsagrada", 25.2),
    ("A Fonsagrada", "O Cádavo", 24.3), ("O Cádavo", "Lugo", 29.5), ("Lugo", "A Ponte Ferreira", 26.5), ("A Ponte Ferreira", "Melide", 20.0),
    ("Melide", "Arzúa", 13.7), ("Arzúa", "O Pedrouzo", 19.3), ("O Pedrouzo", "Santiago de Compostela", 19.4),
]
ROUTES = {"fr": FRANCES, "pt": PORTUGUES, "no": NORTE, "pr": PRIMITIVO}
DEFAULT_FROM = {"fr": "Saint-Jean-Pied-de-Port", "pt": "Porto", "no": "Irún", "pr": "Oviedo"}
FROM_ID = {"fr": "dfr", "pt": "dpt", "no": "dno", "pr": "dpr"}


def towns(route):
    """[[town, km from the route start], ...] ending in Santiago."""
    st = ROUTES[route]
    out, cum = [[st[0][0], 0.0]], 0.0
    for a, b, km in st:
        cum = round(cum + km, 1)
        out.append([b, cum])
    return out


def total(route, frm=None):
    t = towns(route)
    k0 = next(c for n, c in t if n == (frm or t[0][0]))
    return round(t[-1][1] - k0, 1)


DATA = {"r": {k: towns(k) for k in ROUTES}}

JS = r"""
function (v, H, C) {
  var EN = %EN%;
  %FMT%
  var T = EN ? {
    kmd: 'Enter how many km a day you plan to walk (5 to 50).', rest: 'Rest every: 0 (none) to 30 walking days.', date: 'Pick a start date.',
    day: 'Day', date_l: 'Date', stage: 'Stage', km: 'km', tot: 'Total', restd: 'Rest day in', between: 'between {a} and {b}', approx: '≈ km {k}',
    days: 'days', walk: 'walking', rests: 'rest', arr: 'arrival', avg: 'a day on average', short: 'Under 100 km: not enough for the Compostela on foot.',
    edge: 'About {k} km with these stage distances: right on the 100 km limit; start one stage earlier to be safe.',
    split: 'Stages split in two or more: find lodging around that point (albergues and guesthouses are frequent along the way).',
    ok: 'From here you walk {k} km: enough for the Compostela (last 100 km on foot, two stamps a day).', last: 'Santiago', R: { fr: 'Camino Francés', pt: 'Camino Portugués', no: 'Camino del Norte', pr: 'Camino Primitivo' },
    MON: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], WD: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  } : {
    kmd: 'Indica cuántos km al día quieres andar (de 5 a 50).', rest: 'Descanso cada: de 0 (ninguno) a 30 días de marcha.', date: 'Elige la fecha de salida.',
    day: 'Día', date_l: 'Fecha', stage: 'Etapa', km: 'km', tot: 'Total', restd: 'Descanso en', between: 'entre {a} y {b}', approx: '≈ km {k}',
    days: 'días', walk: 'andando', rests: 'de descanso', arr: 'llegada', avg: 'al día de media', short: 'Menos de 100 km: no basta para la Compostela a pie.',
    edge: 'Unos {k} km con estas distancias de etapa: justo en el límite de los 100 km; sal una etapa antes para ir con margen.',
    split: 'Etapas partidas en dos o más: busca alojamiento por ese punto (en el Camino hay albergues y casas rurales cada pocos kilómetros).',
    ok: 'Desde aquí andas {k} km: suficiente para la Compostela (los últimos 100 km a pie, con dos sellos al día).', last: 'Santiago', R: { fr: 'Camino Francés', pt: 'Camino Portugués', no: 'Camino del Norte', pr: 'Camino Primitivo' },
    MON: ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'], WD: ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom']
  };
  var route = C.d.r[v.ruta] ? v.ruta : 'fr', list = C.d.r[route], from = v[{ fr: 'dfr', pt: 'dpt', no: 'dno', pr: 'dpr' }[route]];
  var i0 = 0;
  for (var i = 0; i < list.length - 1; i++) if (list[i][0] === from) i0 = i;
  var tgt = v.kmd, every = isNaN(v.desc) ? 0 : v.desc;
  if (!(tgt >= 5 && tgt <= 50)) return { err: T.kmd };
  if (!(every >= 0 && every <= 30) || every % 1) return { err: T.rest };
  if (!v.inicio) return { err: T.date };
  /* candidate stops: every stage town, plus points inside the stages (equal parts of about the daily target, at least
     the halfway point of stages of 16 km or more: most have a village with lodging around there). In-stage points
     cost 5 km extra in the choice below, so a real stage town wins when it is nearly as good */
  var pts = [], split = false;
  for (i = i0; i < list.length; i++) {
    if (i > i0) {
      var len = list[i][1] - list[i - 1][1], k = Math.max(len > 1.35 * tgt ? Math.round(len / tgt) : 1, len >= 16 ? 2 : 1);
      for (var s = 1; s < k; s++) pts.push({ n: null, a: list[i - 1][0], b: list[i][0], km: list[i - 1][1] + len * s / k });
    }
    pts.push({ n: list[i][0], km: list[i][1] });
  }
  /* each day: the stop that best matches the daily target, also pulled towards the ideal cumulative distance
     (start + target x days) so short and long stages even out; ties: the shorter day */
  var days = [], at = 0, d = v.inicio, walked = 0, k0 = pts[0].km;
  function fd(x) { return T.WD[H.wd(x)] + ' ' + (EN ? T.MON[x.getUTCMonth()] + ' ' + x.getUTCDate() : x.getUTCDate() + ' ' + T.MON[x.getUTCMonth()]); }
  function nm(p) { return p.n !== null ? p.n : T.approx.replace('{k}', fx(p.km - list[i0][1], 0)) + ' (' + T.between.replace('{a}', p.a).replace('{b}', p.b) + ')'; }
  while (at < pts.length - 1 && days.length < 400) {
    var best = at + 1, bd = 1e9;
    for (var j = at + 1; j < pts.length; j++) {
      var dist = pts[j].km - pts[at].km, dd = Math.abs(dist - tgt) + 0.3 * Math.abs(pts[j].km - k0 - tgt * (walked + 1)) + (pts[j].n === null ? 5 : 0);
      if (dd < bd - 1e-9) { bd = dd; best = j; }
      if (dist > tgt * 2) break;
    }
    if (pts[best].n === null) split = true;
    days.push({ t: 'w', d: d, a: pts[at], b: pts[best], km: pts[best].km - pts[at].km });
    walked++; at = best; d = H.add(d, 1);
    if (every && walked % every === 0 && at < pts.length - 1) { days.push({ t: 'r', d: d, a: pts[at] }); d = H.add(d, 1); }
  }
  var total = list[list.length - 1][1] - list[i0][1], cum = 0, rows = '', ics = [], nw = 0, nr = 0;
  days.forEach(function (x, n) {
    if (x.t === 'r') {
      nr++;
      rows += '<tr class="cs-r"><td>' + (n + 1) + '</td><td>' + fd(x.d) + '</td><td colspan="3">' + T.restd + ' ' + H.esc(nm(x.a)) + '</td></tr>';
      ics.push([x.d, T.restd + ' ' + nm(x.a)]);
      return;
    }
    nw++; cum += x.km;
    rows += '<tr><td>' + (n + 1) + '</td><td>' + fd(x.d) + '</td><td>' + H.esc(nm(x.a)) + ' → <b>' + H.esc(nm(x.b)) + '</b></td><td class="num">' + fx(x.km, 1) + '</td><td class="num">' + fx(cum, 0) + '</td></tr>';
    ics.push([x.d, T.day + ' ' + (n + 1) + ': ' + nm(x.a) + ' → ' + nm(x.b) + ' (' + fx(x.km, 1) + ' km)']);
  });
  var last = days[days.length - 1].d;
  var cal = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//elcalendariolaboral.es//camino//ES\r\nCALSCALE:GREGORIAN\r\n' + ics.map(function (e, n) {
    return 'BEGIN:VEVENT\r\nUID:camino-' + n + '-' + H.icsDate(e[0]) + '@elcalendariolaboral.es\r\nDTSTAMP:' + H.icsDate(e[0]) + 'T000000Z\r\nDTSTART;VALUE=DATE:' + H.icsDate(e[0]) +
      '\r\nDTEND;VALUE=DATE:' + H.icsDate(H.add(e[0], 1)) + '\r\nSUMMARY:' + H.icsEsc(e[1]) + '\r\nEND:VEVENT';
  }).join('\r\n') + '\r\nEND:VCALENDAR\r\n';
  var notes = [total < 95 ? T.short : total < 100 ? T.edge.replace('{k}', fx(total, 0)) : T.ok.replace('{k}', fx(total, 0))];
  if (split) notes.push(T.split);
  return {
    label: T.R[route] + ' · ' + H.esc(list[i0][0]) + ' → ' + T.last, big: days.length + ' ' + T.days,
    sub: nw + ' ' + T.walk + (nr ? ' + ' + nr + ' ' + T.rests : '') + ' · ' + fx(total, 0) + ' km · ' + fx(total / nw, 1) + ' km ' + T.avg + ' · ' + T.arr + ' ' + fd(last) + ' ' + last.getUTCFullYear(),
    html: '<table class="tbl cs-t"><thead><tr><th>' + T.day + '</th><th>' + T.date_l + '</th><th>' + T.stage + '</th><th class="num">' + T.km + '</th><th class="num">' + T.tot + '</th></tr></thead><tbody>' + rows + '</tbody></table>',
    note: notes.join(' '), print: true, ics: { name: 'camino.ics', text: cal },
    n: { days: days.length, walk: nw, rest: nr, km: r(total, 1), arr: H.iso(last), first: nm(days[0].b), split: split }
  };
}
"""

CSS = ".cs-t td{vertical-align:top}.cs-t td:nth-child(2){white-space:nowrap}.cs-r td{color:var(--mut,#666);font-style:italic}"


def inputs(lang):
    es = lang == "es"
    out = [
        {"id": "ruta", "type": "select", "label": "Camino" if es else "Route", "value": "fr",
         "options": [("fr", "Francés"), ("pt", "Portugués"), ("no", "Norte"), ("pr", "Primitivo")] if es else
                    [("fr", "French Way"), ("pt", "Portuguese Way"), ("no", "Northern Way"), ("pr", "Primitivo")]},
    ]
    for k, st in ROUTES.items():
        tw = towns(k)[:-1]
        out.append({"id": FROM_ID[k], "type": "select", "label": "Desde" if es else "From", "value": DEFAULT_FROM[k], "w": "l",
                    "show": ("ruta", [k]),
                    "options": [(n, f"{n} · {D.n(round(tw[-1][1] + st[-1][2] - c, 1), 0, not es)} km") for n, c in tw]})
    out += [
        {"id": "kmd", "type": "number", "label": "Km al día" if es else "Km a day", "value": "22", "unit": "km", "w": "s"},
        {"id": "inicio", "type": "date", "label": "Salida" if es else "Start", "value": "", "today": True},
        {"id": "desc", "type": "number", "label": "Descanso cada" if es else "Rest every", "value": "0", "unit": "días" if es else "days", "w": "s"},
    ]
    return out


def blocks(ctx):
    fr = total("fr")
    sarria = total("fr", "Sarria")
    tui = total("pt", "Tui")
    porto = total("pt", "Porto")
    irun = total("no", "Irún")
    ovi = total("pr", "Oviedo")
    return [
        ("Cómo se reparten las etapas", f"""
<p>Elige el Camino y el punto de salida, escribe cuántos kilómetros quieres andar al día y la fecha en que empiezas. La
herramienta parte de las etapas clásicas de cada Camino y, día a día, elige el final de etapa que más se acerca a tu
objetivo: si andas mucho, junta dos etapas cortas; si andas poco y una etapa es mucho más larga que tu ritmo, la parte en
dos o tres tramos iguales y te indica el kilómetro aproximado donde buscar alojamiento. Con «Descanso cada» añades un día
sin andar cada cierto número de jornadas, en el pueblo donde te toque. El resultado se puede imprimir o descargar en .ics
para tenerlo en el calendario del móvil.</p>
<p>Ejemplo: el Camino Francés completo desde Saint-Jean-Pied-de-Port suma unos {D.n(fr, 0)} km en 33 etapas. A 22 km al
día la herramienta sigue casi exactamente esas etapas: 33 días de marcha, o 37 con un descanso cada 7 días. A 15 km al día
salen 51 jornadas (muchas etapas partidas en dos) y a 30 km, 26. Desde Sarria son {D.n(sarria, 0)} km, la
distancia mínima más popular para la Compostela, que la mayoría hace en 5 días.</p>"""),
        ("Los cuatro Caminos y sus distancias", f"""
<p>El <b>Francés</b> es el más transitado y el que más servicios tiene. El <b>Portugués</b> central viene de Lisboa por
Coimbra y Porto: desde Porto son {D.n(porto, 0)} km y desde Tui, ya en Galicia, {D.n(tui, 0)} km, el inicio clásico para los
últimos 100. El del <b>Norte</b> sigue la costa cantábrica desde Irún ({D.n(irun, 0)} km) y se une al Francés en Arzúa; es
más duro por los continuos desniveles y tiene menos albergues. El <b>Primitivo</b>, el más antiguo, sale de Oviedo, cruza la
montaña asturiana y llega a Melide, donde también se une al Francés: unos {D.n(ovi, 0)} km, con etapas de mucho desnivel.
En el Primitivo se usa la etapa por la ruta de Hospitales (la alternativa por Pola de Allande suma 4,5 km) y en el Norte
las variantes oficiales.</p>"""),
        ("La Compostela y los kilómetros mínimos", """
<p>Para recibir la Compostela en la Oficina del Peregrino hay que recorrer a pie o a caballo al menos los <b>últimos 100
km</b> hasta Santiago (200 km en bicicleta) y sellar la credencial al menos dos veces al día en ese tramo final, con la
fecha. La herramienta avisa si el recorrido elegido no llega a esa distancia. Las distancias de etapa son aproximadas y
proceden de la guía Gronze; pueden variar uno o dos kilómetros según el albergue que elijas o los desvíos de cada año.</p>"""),
    ]


FAQ = [
    ("¿Cuántos días se tarda en hacer el Camino Francés?",
     "Entre 30 y 35 días andando unos 22-25 km al día desde Saint-Jean-Pied-de-Port, más los días de descanso que quieras. Desde Sarria, unos 5 días."),
    ("¿Cuántos kilómetros al día se andan en el Camino?",
     "La media está entre 20 y 25 km. Si no estás acostumbrado, empieza con 15-18 km los primeros días: las ampollas y las tendinitis aparecen por forzar al principio."),
    ("¿Desde dónde hay que salir para la Compostela?",
     "Desde cualquier punto a 100 km o más de Santiago, andando: Sarria en el Francés, Tui en el Portugués o Vilalba en el Norte. En el Primitivo, Lugo queda justo en el límite; salir de O Cádavo da margen."),
    ("¿Cada cuánto conviene descansar?",
     "Muchos peregrinos descansan un día por semana, a menudo en una ciudad con algo que ver: Pamplona, Burgos o León en el Francés."),
    ("¿Las distancias son exactas?",
     "Son las de las etapas de la guía Gronze. El recorrido real cambia un poco según dónde duermas y si hay desvíos; cuenta con un margen de un 5 %."),
    ("¿Qué pasa si una etapa es más larga de lo que quiero andar?",
     "La herramienta la divide en tramos iguales y te dice el kilómetro aproximado. Busca alojamiento cerca de ese punto en una guía o app del Camino."),
]

TOOL = {
    "slug": "etapas-camino-santiago",
    "lang": "es",
    "twin": "camino-de-santiago-planner",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "walk",
    "order": 80,
    "name": "Etapas del Camino",
    "k": "camino de santiago etapas planificar francés portugués norte primitivo km día compostela peregrino",
    "title": "Etapas del Camino de Santiago: planifica a tu ritmo",
    "desc": "Planifica tus etapas del Camino de Santiago (Francés, Portugués, Norte o Primitivo) por km al día, con días de descanso, fechas y calendario .ics.",
    "h1": "Planificador de etapas del Camino de Santiago",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": D.make(JS, False),
    "data": DATA,
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Gronze · etapas del Camino Francés, Portugués, Norte y Primitivo (nov. 2026)", GRONZE),
                ("Oficina del Peregrino · requisitos de la Compostela", "https://oficinadelperegrino.com/peregrinacion/la-compostela/")],
    "credits": [("Distancias de etapa: Gronze.com (datos de referencia, citados)", "datos factuales con cita", GRONZE)],
    "related": ["tiempo-ruta-montana", "amanecer-atardecer", "calculadora-vacaciones"],
    "tests": [
        ({"inicio": "2027-05-01"}, {"n.km": 763.7, "n.walk": 33, "n.first": "Roncesvalles"}),
        ({"inicio": "2027-05-01", "dfr": "Sarria", "kmd": "25"}, {"n.km": 114.2, "n.walk": 5, "n.arr": "2027-05-05"}),
        ({"inicio": "2027-05-01", "desc": "7", "kmd": "30"}, {"n.walk": 26, "n.rest": 3}),
        ({"inicio": "2027-05-01", "ruta": "pt", "dpt": "Tui", "kmd": "15"}, {"n.km": 115.8, "n.split": True}),
        ({"inicio": "", "ruta": "pr", "kmd": "4"}, {"err": "Indica cuántos km al día quieres andar (de 5 a 50)."}),
        ({"inicio": "2027-05-01", "ruta": "pr", "dpr": "Lugo"}, {"n.km": 98.9, "n.walk": 5}),
    ],
}
