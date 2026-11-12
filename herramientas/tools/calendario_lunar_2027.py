"""Calendario lunar 2027: the four moon phases of a year with their official time (Península / Canarias), a month grid
with the moon of every day, full-moon count and blue moons, .ics. Meeus ch. 49. The English twin (moon_phases_2027.py)
reuses make_js() with its own strings and time-zone list."""
import datetime as dt
import json

from herramientas.tools import _astro as A

L_ES = {
    "ph": ["Luna nueva", "Cuarto creciente", "Luna llena", "Cuarto menguante"],
    "ab": ["LN", "CC", "LL", "CM"],
    "mon": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    "m3": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    "wd": ["L", "M", "X", "J", "V", "S", "D"],
    "names": None,
    "big_l": "Lunas llenas en ", "full": "lunas llenas", "new": "lunas nuevas", "blue": "Luna azul (segunda llena del mes)",
    "today": "Hoy", "ill": "iluminada", "month": "Mes", "cal": "Calendario lunar ",
    "stages": ["Luna nueva", "Creciente", "Cuarto creciente", "Gibosa creciente", "Luna llena", "Gibosa menguante", "Cuarto menguante", "Menguante"],
    "err": "Año entre 1900 y 2100.", "tzname": {"Europe/Madrid": "hora peninsular", "Atlantic/Canary": "hora de Canarias"},
    "note": "Horas oficiales con el horario de verano aplicado. La luna de cada casilla es la de las 12:00.",
    "ics": "calendario-lunar-", "lang": "ES",
}


def make_js(L):
    return r"""
function (v, H, C) {
""" + A.MOON_JS + A.TZ_JS + r"""
  var L = """ + json.dumps(L, ensure_ascii=False) + r""";
  var y = parseInt(v.ano, 10), tz = v.zona === 'can' ? 'Atlantic/Canary' : v.zona === 'pen' ? 'Europe/Madrid' : v.zona;
  if (!(y >= 1900 && y <= 2100)) return { err: L.err };
  if (tz === 'local') { try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'; } catch (e) { tz = 'UTC'; } }
  try { tzParts(0, tz); } catch (e) { tz = 'UTC'; }
  var all = phasesIn(Date.UTC(y - 1, 10, 1), Date.UTC(y + 1, 2, 1)), mine = [], byDay = {}, perMonth = [], fullBy = {};
  all.forEach(function (p) {
    var t = tzParts(Math.round(p[1] / 6e4) * 6e4, tz);
    if (t.y !== y) return;
    var o = { q: p[0], ms: p[1], m: t.m, d: t.d, hm: p2(t.h) + ':' + p2(t.mi) };
    mine.push(o); byDay[t.m + '-' + t.d] = o;
    (perMonth[t.m] = perMonth[t.m] || []).push(o);
    if (p[0] === 2) (fullBy[t.m] = fullBy[t.m] || []).push(o);
  });
  var nFull = mine.filter(function (o) { return o.q === 2; }).length, nNew = mine.filter(function (o) { return o.q === 0; }).length;
  var blue = [];
  Object.keys(fullBy).forEach(function (m) { if (fullBy[m].length > 1) blue.push(fullBy[m][1]); });
  /* traditional full-moon names (English page): Harvest = full moon nearest the September equinox (~22 Sep) */
  var nameOf = {};
  if (L.names) {
    var fulls = mine.filter(function (o) { return o.q === 2; }), eq = Date.UTC(y, 8, 22, 12), hv = null;
    fulls.forEach(function (o) { if (!hv || Math.abs(o.ms - eq) < Math.abs(hv.ms - eq)) hv = o; });
    fulls.forEach(function (o, i) {
      var nm = L.names[o.m - 1];
      if (o === hv) nm = L.harvest;
      else if (hv && i > 0 && fulls[i - 1] === hv) nm = L.hunter;
      else if (o.m === 9 && hv && hv.m === 10) nm = L.names[8];
      if (blue.indexOf(o) >= 0) nm = L.bluename;
      nameOf[o.ms] = nm;
    });
  }
  /* month grids */
  var grid = '';
  for (var m = 1; m <= 12; m++) {
    var nd = H.monthDays(y, m), lead = H.wd(new Date(Date.UTC(y, m - 1, 1))), cells = [];
    for (var k = 0; k < lead; k++) cells.push('<td class="o"></td>');
    for (var d = 1; d <= nd; d++) {
      var noon = Date.UTC(y, m - 1, d, 12), pt = tzParts(noon, tz), off = Date.UTC(pt.y, pt.m - 1, pt.d, pt.h, pt.mi) - noon;
      var a = illum(noon - off, all), ph = byDay[m + '-' + d];
      cells.push('<td' + (ph ? ' class="ph" title="' + L.ph[ph.q] + ' ' + ph.hm + '"' : ' title="' + Math.round(a[1] * 100) + ' %"') + '>' + d +
        moonSvg(a[0], 16) + (ph ? '<small>' + L.ab[ph.q] + ' ' + ph.hm + '</small>' : '') + '</td>');
    }
    while (cells.length % 7) cells.push('<td class="o"></td>');
    var rows = '';
    for (var r = 0; r < cells.length; r += 7) rows += '<tr>' + cells.slice(r, r + 7).join('') + '</tr>';
    grid += '<div class="cq-m ml"><table><caption>' + L.mon[m - 1] + '</caption><thead><tr>' + L.wd.map(function (w) { return '<th>' + w + '</th>'; }).join('') +
      '</tr></thead><tbody>' + rows + '</tbody></table></div>';
  }
  /* phase table: one row per month */
  var tb = '<table class="tbl mt"><thead><tr><th>' + L.month + '</th>' + L.ph.map(function (p, q) { return '<th>' + moonSvg(q * 90, 14) + p + '</th>'; }).join('') +
    (L.names ? '<th>' + L.namecol + '</th>' : '') + '</tr></thead><tbody>';
  for (m = 1; m <= 12; m++) {
    var cols = [[], [], [], []], nm = [];
    (perMonth[m] || []).forEach(function (o) { cols[o.q].push(o.d + ' · ' + o.hm); if (nameOf[o.ms]) nm.push(nameOf[o.ms]); });
    tb += '<tr><td>' + L.mon[m - 1] + '</td>' + cols.map(function (c) { return '<td>' + (c.join('<br>') || '–') + '</td>'; }).join('') +
      (L.names ? '<td>' + nm.join(', ') + '</td>' : '') + '</tr>';
  }
  tb += '</tbody></table>';
  /* .ics: one event per phase at its exact time */
  var ev = mine.map(function (o) {
    var s = new Date(Math.round(o.ms / 6e4) * 6e4).toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z';
    return 'BEGIN:VEVENT\r\nUID:' + s + '-' + o.q + '@elcalendariolaboral.es\r\nDTSTAMP:20261112T000000Z\r\nDTSTART:' + s + '\r\nDURATION:PT1M\r\nSUMMARY:' +
      H.icsEsc(L.ph[o.q] + (nameOf[o.ms] ? ' · ' + nameOf[o.ms] : '')) + '\r\nTRANSP:TRANSPARENT\r\nEND:VEVENT';
  });
  var ics = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//elcalendariolaboral.es//Moon ' + y + '//' + L.lang + '\r\nCALSCALE:GREGORIAN\r\nX-WR-CALNAME:' + H.icsEsc(L.cal + y) + '\r\n' +
    ev.join('\r\n') + (ev.length ? '\r\n' : '') + 'END:VCALENDAR\r\n';
  /* today's moon when the year is the current one */
  var rowsOut = [], now = Date.now(), tn = tzParts(now, tz);
  if (tn.y === y) {
    var an = illum(now, all), st = Math.floor(((an[0] + 22.5) % 360) / 45);
    rowsOut.push([L.today, L.stages[st] + ' · ' + Math.round(an[1] * 100) + ' % ' + L.ill]);
  }
  blue.forEach(function (o) { rowsOut.push([L.blue, o.d + ' ' + L.m3[o.m - 1] + ' · ' + o.hm]); });
  var first = mine.filter(function (o) { return o.q === 2; })[0];
  return {
    label: L.big_l + y, big: nFull,
    sub: nNew + ' ' + L['new'] + ' · ' + (L.tzname[tz] || tz.replace(/_/g, ' ')),
    rows: rowsOut,
    html: tb + '<h2 class="cq-h">' + L.cal + y + '</h2><div class="cq-y">' + grid + '</div>',
    note: L.note, print: true, ics: { name: L.ics + y + '.ics', text: ics },
    n: { full: nFull, nw: nNew, blue: blue.length, first: first ? first.m * 100 + first.d : 0, firsthm: first ? first.hm : '',
      list: mine.filter(function (o) { return o.q === 2; }).map(function (o) { return o.m + '-' + o.d + ' ' + o.hm; }) }
  };
}
"""


def full_moons(year, tz):
    return [t.astimezone(tz) for q, t in A.phases(year) if q == 2]


MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def blocks(ctx):
    fm = full_moons(2027, A.TZ_PEN)
    lst = ", ".join(f"{t.day} de {MES[t.month - 1]} ({t + dt.timedelta(seconds=30):%H:%M})" for t in fm)
    nm = [t.astimezone(A.TZ_PEN) for q, t in A.phases(2027) if q == 0]
    may = next(t for t in fm if t.month == 5)
    e27 = A.easter(2027)
    pfm = max(t for t in fm if t.date() <= e27)
    return [
        ("Lunas llenas de 2027", f"""
<p>En 2027 hay <b>{len(fm)} lunas llenas</b>, en hora peninsular: {lst}. La primera luna nueva del año es el
{nm[0].day} de {MES[nm[0].month - 1]} y la última, el {nm[-1].day} de {MES[nm[-1].month - 1]}. No hay luna azul (dos llenas en el
mismo mes): la última fue el 31 de mayo de 2026 y la próxima será el 31 de diciembre de 2028. Cambia el año para ver cualquier otro de
2024 a 2035, y elige «Canarias» para ver las horas de las islas, una menos.</p>
<p>La luna llena manda en el calendario de las fiestas móviles: el Domingo de Resurrección es el domingo siguiente a la primera luna
llena de primavera. En 2027 esa luna llena es la del {pfm.day} de {MES[pfm.month - 1]}, y por eso la Pascua cae el
{e27.day} de {MES[e27.month - 1]}.</p>"""),
        ("Huerto, poda y pesca", f"""
<p>Muchos agricultores siguen el calendario lunar por tradición: sembrar en luna creciente lo que crece hacia arriba (lechugas,
tomates, judías) y en menguante lo que crece bajo tierra (patatas, zanahorias, ajos), y podar, cortar madera o trasplantar en
menguante, cuando se dice que la savia «baja». Son costumbres heredadas; los ensayos agronómicos no han encontrado un efecto medible
de la fase lunar sobre la germinación, así que úsalas como guía de calendario, no como garantía.</p>
<p>En la pesca sí hay una relación física: con luna nueva y luna llena, el Sol y la Luna se alinean y sus mareas se suman (mareas
vivas, con más diferencia entre pleamar y bajamar), y en los cuartos se contrarrestan (mareas muertas). En 2027, la luna llena del
{may.day} de mayo trae mareas vivas a la costa durante los días siguientes. La hora exacta de la marea en cada puerto la publica Puertos
del Estado.</p>"""),
        ("Cómo se calculan las fases", """
<p>Las fases son instantes concretos: luna nueva cuando la Luna y el Sol tienen la misma longitud eclíptica vista desde la Tierra,
cuarto creciente a 90 grados, luna llena a 180 y cuarto menguante a 270. Esta calculadora usa la serie del capítulo 49 de
«Astronomical Algorithms» de Jean Meeus, que suma a la fase media más de 40 términos periódicos (la excentricidad de las órbitas,
la inclinación lunar y la atracción de los planetas) y la diferencia entre el tiempo dinámico y el de los relojes. Comparadas con la
lista del Observatorio Naval de Estados Unidos para 2027, las 49 fases difieren menos de un minuto.</p>
<p>Entre dos fases, la Luna de cada casilla se dibuja interpolando el ángulo de fase a las 12:00 de ese día, así que el porcentaje de
superficie iluminada es aproximado (un 1-2 %). El ciclo completo, de luna nueva a luna nueva, dura de media 29,53 días, pero cada mes
lunar varía unas horas porque la órbita de la Luna es elíptica.</p>"""),
    ]


FAQ = [
    ("¿Cuántas lunas llenas hay en 2027?",
     "Doce, una por mes, la primera el 22 de enero y la última el 13 de diciembre. Un año tiene 13 cuando una cae a principios de enero y "
     "otra a finales de diciembre; el próximo será 2028."),
    ("¿Qué es una luna azul?",
     "La segunda luna llena de un mismo mes. Ocurre más o menos cada dos o tres años, porque el mes lunar (29,5 días) es un poco más corto "
     "que casi todos los meses del calendario. No cambia de color: es solo un nombre."),
    ("¿La luna creciente tiene forma de C o de D?",
     "Desde España, la luna creciente se ilumina por la derecha y su forma recuerda a una D; la menguante, iluminada por la izquierda, a una "
     "C. Por eso se dice que la luna es «mentirosa». En el hemisferio sur es al revés."),
    ("¿Las fases son a la misma hora en toda España?",
     "El instante es el mismo en todo el mundo; lo que cambia es la hora de reloj. En Canarias es una hora menos que en la Península, "
     "Baleares, Ceuta y Melilla."),
    ("¿Qué luna es mejor para sembrar?",
     "Según la tradición, creciente para hortalizas de hoja y fruto y menguante para las de raíz y para podar. No hay pruebas científicas "
     "sólidas de que influya; lo que sí importa es la temperatura del suelo y la humedad."),
]

TOOL = {
    "slug": "calendario-lunar-2027",
    "lang": "es",
    "twin": "moon-phases-2027",
    "cat": "cielo",
    "cat_name": "Sol y luna",
    "icon": "moon",
    "order": 10,
    "name": "Calendario lunar 2027",
    "k": "fases de la luna llena nueva cuarto creciente menguante hoy siembra huerto pesca",
    "title": "Calendario lunar 2027: fases de la luna mes a mes",
    "desc": "Fases de la luna en 2027 con día y hora en España: luna llena, nueva, cuarto creciente y menguante. Calendario mensual imprimible y .ics.",
    "h1": "Calendario lunar 2027",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ano", "type": "select", "label": "Año", "value": "2027", "options": [(str(y), str(y)) for y in range(2024, 2036)]},
        {"id": "zona", "type": "seg", "label": "Hora", "value": "pen", "options": [("pen", "Península"), ("can", "Canarias")]},
    ],
    "js": make_js(L_ES),
    "css": A.MOON_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Observatorio Astronómico Nacional (IGN) · Anuario", "https://astronomia.ign.es/web/guest/oan/anuario"),
                ("US Naval Observatory · fases de la Luna", "https://aa.usno.navy.mil/data/MoonPhases"),
                ("Puertos del Estado · predicción de mareas", "https://www.puertos.es/servicios/oceanografia")],
    "credits": [("Jean Meeus, «Astronomical Algorithms», cap. 49 (fórmula reimplementada)", "fórmula publicada", "https://en.wikipedia.org/wiki/Jean_Meeus")],
    "related": ["amanecer-atardecer", "fecha-semana-santa", "signo-zodiaco-chino", "cambio-de-hora/"],
    "tests": [
        # US Naval Observatory 2027 (UTC, to the minute): full moons 01-22 12:17 ... 12-13 16:09 -> +1 h CET / +2 h CEST.
        # Meeus differs < 1 min from every USNO phase (-18 s .. +41 s): 02-20 23:23:35 and 09-15 23:03:37 UTC round up here.
        ({"ano": "2027", "zona": "pen"}, {"n.full": 12, "n.blue": 0, "n.first": 122, "n.firsthm": "13:17",
                                          "n.list": ["1-22 13:17", "2-21 00:24", "3-22 11:44", "4-21 00:27", "5-20 12:59", "6-19 02:44",
                                                     "7-18 17:45", "8-17 09:29", "9-16 01:04", "10-15 15:47", "11-14 04:26", "12-13 17:09"]}),
        ({"ano": "2027", "zona": "can"}, {"n.firsthm": "12:17", "n.nw": 13}),
        # 2028: 13 full moons (12 Jan and 31 Dec) and a blue moon on 31 Dec 2028
        ({"ano": "2028", "zona": "pen"}, {"n.full": 13, "n.blue": 1}),
        ({"ano": "2026", "zona": "pen"}, {"n.full": 13, "n.blue": 1}),
        ({"ano": "1800", "zona": "pen"}, {"err": "Año entre 1900 y 2100."}),
    ],
}
