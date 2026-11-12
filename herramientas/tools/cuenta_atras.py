"""Cuenta atrás: live countdown to Navidad, Nochebuena, Año Nuevo, Reyes, Jueves Santo, the Christmas lottery or any
date and time, with a name, shareable through the link (the framework keeps the form in the URL). The compute is
pure; the returned IIFE also starts a 1-second ticker in the browser that refreshes elements with data-cd (no DOM in
node). The English twin (countdown.py) reuses make_js() with its own presets."""
import json

from herramientas.tools import _astro as A

L_ES = {
    "lang": "es", "wd": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "mon": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "ev": {"navidad": [12, 25, "Navidad"], "nochebuena": [12, 24, "Nochebuena"], "ano": [1, 1, "Año Nuevo"], "reyes": [1, 6, "Reyes"],
           "loteria": [12, 22, "Sorteo de Navidad"], "jueves": ["E", -3, "Jueves Santo"]},
    "e_d": "Elige la fecha.", "e_r": "Fecha fuera de rango (años 1000 a 9999).", "e_t": "Hora no válida.",
    "left": "Faltan", "until": " para ", "today": "¡Es hoy!", "past": "Ya pasó", "ago": "hace ", "mine": "Mi fecha",
    "d1": "día", "dn": "días", "w1": "semana", "wn": "semanas", "and": " y ", "u": ["d", "h", "min", "s"],
    "r_date": "Fecha", "r_w": "En semanas", "r_h": "En horas", "r_m": "En minutos", "at": " a las ",
    "note": "La cuenta usa la hora de tu dispositivo.",
}


def make_js(L):
    return r"""
(function () {
  var L = """ + json.dumps(L, ensure_ascii=False) + r""";
  function p2(n) { return (n < 10 ? '0' : '') + n; }
  function fmt(ms) {
    if (ms <= 0) return L.today;
    var s = Math.floor(ms / 1000), d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60);
    return (d ? d + ' ' + L.u[0] + ' ' : '') + p2(h) + ' ' + L.u[1] + ' ' + p2(m) + ' ' + L.u[2] + ' ' + p2(s % 60) + ' ' + L.u[3];
  }
  if (typeof document !== 'undefined') setInterval(function () {
    Array.prototype.forEach.call(document.querySelectorAll('[data-cd]'), function (el) { el.textContent = fmt(+el.getAttribute('data-cd') - Date.now()); });
  }, 1000);
""" + A.EASTER_JS + r"""
  return function (v, H, C) {
""" + A.DATE_JS + r"""
    var now = v.desde ? new Date(v.desde.getUTCFullYear(), v.desde.getUTCMonth(), v.desde.getUTCDate()) : new Date();
    if (v.desde && (v.desde.getUTCFullYear() < 1000 || v.desde.getUTCFullYear() > 9999)) return { err: L.e_r };
    var today = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())), y = today.getUTCFullYear();
    var name, day, hh = 0, mi = 0, p = L.ev[v.ev];
    function cand(yy) {
      if (p[0] === 'E') return H.add(easter(yy), p[1]);
      if (p[0] === 'T') { var n1 = new Date(Date.UTC(yy, 10, 1)); return H.add(n1, ((3 - H.wd(n1)) + 7) % 7 + 21); } /* 4th Thursday of November */
      return new Date(Date.UTC(yy, p[0] - 1, p[1]));
    }
    if (p) {
      name = p[2]; day = cand(y);
      if (day < today) day = cand(y + 1);
    } else {
      if (!v.d) return { err: L.e_d };
      day = v.d;
      if (day.getUTCFullYear() < 1000 || day.getUTCFullYear() > 9999) return { err: L.e_r };
      var t = /^(\d{1,2}):(\d{2})$/.exec(v.h || '00:00');
      if (!t || +t[1] > 23 || +t[2] > 59) return { err: L.e_t };
      hh = +t[1]; mi = +t[2]; name = String(v.txt || '').trim() || L.mine;
    }
    var target = new Date(day.getUTCFullYear(), day.getUTCMonth(), day.getUTCDate(), hh, mi).getTime(), ms = target - now.getTime();
    var days = H.diff(today, day), isToday = days === 0 && ms <= 0, past = days < 0;
    var when = fdate(day, true) + (hh || mi ? L.at + p2(hh) + ':' + p2(mi) : '');
    if (past) return { label: L.past + ': ' + H.esc(name), big: L.ago + pl(-days, L.d1, L.dn), sub: when, n: { days: days, today: false } };
    if (isToday) return { label: H.esc(name), big: L.today, sub: when, n: { days: 0, today: true } };
    var wk = Math.floor(days / 7), wr = days % 7;
    return {
      label: L.left + L.until + H.esc(name), big: '<span data-cd="' + target + '">' + fmt(ms) + '</span>', sub: when,
      rows: [[L.left, pl(days, L.d1, L.dn), 'tot'], [L.r_w, pl(wk, L.w1, L.wn) + (wr ? L.and + pl(wr, L.d1, L.dn) : '')],
        [L.r_h, nf(Math.floor(ms / 36e5))], [L.r_m, nf(Math.floor(ms / 6e4))]],
      note: L.note, n: { days: days, today: false, date: H.iso(day) }
    };
  };
})()
"""


def inputs(L, lab, opts, d_value, txt_ph):
    return [
        {"id": "ev", "type": "select", "label": lab[0], "value": opts[0][0], "options": opts},
        {"id": "d", "type": "date", "label": lab[1], "value": d_value, "min": "1000-01-01", "max": "9999-12-31", "show": ("ev", ["fecha"])},
        {"id": "h", "type": "time", "label": lab[2], "value": "00:00", "show": ("ev", ["fecha"])},
        {"id": "txt", "type": "text", "label": lab[3], "value": "", "maxlength": 40, "placeholder": txt_ph, "show": ("ev", ["fecha"])},
        {"id": "desde", "type": "date", "label": lab[4], "value": "", "more": True, "min": "1000-01-01", "max": "9999-12-31"},
    ]


def blocks(ctx):
    return [
        ("Cómo funciona", """
<p>Elige una fecha de la lista (Navidad, Nochebuena, Año Nuevo, Reyes, el Sorteo de Navidad o el Jueves Santo) y la cuenta atrás
empieza al momento, en días, horas, minutos y segundos. Para cualquier otra cosa, una boda, un viaje, un examen, el parto o el
primer día de vacaciones, elige «Otra fecha», escribe el día, la hora si la hay y un nombre. Con «Copiar enlace» guardas todo en
la dirección: quien la abra verá la misma cuenta atrás, con el nombre que hayas puesto, desde su propio móvil.</p>
<p>Las fechas de la lista se renuevan solas: pasado el 6 de enero, la cuenta de Reyes salta al año siguiente, y el Jueves Santo se
calcula cada año a partir de la fecha de la Pascua. Por ejemplo, desde el 12 de noviembre de 2026 faltan 43 días para Navidad,
50 para Año Nuevo y 133 para el Jueves Santo de 2027, que cae el 25 de marzo.</p>"""),
        ("Días que faltan y horas exactas", """
<p>Los días que faltan se cuentan como en el calendario: de hoy al día de destino, sin contar hoy. Las horas, minutos y segundos se
cuentan hasta las 00:00 de ese día (o hasta la hora que pongas), con el reloj de tu dispositivo y su zona horaria, así que en
Canarias la cuenta de Año Nuevo llega a cero una hora después que en la Península, justo con sus campanadas. Si el móvil tiene la
hora mal, la cuenta también lo estará: con la hora automática activada, el móvil la toma de la red y no se desvía.</p>
<p>En «Más opciones», «Contar desde» calcula los días que faltaban o faltarán desde otra fecha: cuántos días quedaban para la boda
el día que se reservó el salón, o cuántos faltarán para el viaje cuando empiecen las vacaciones.</p>"""),
    ]


FAQ = [
    ("¿Cuántos días faltan para Navidad?",
     "Desde el 12 de noviembre de 2026, 43 días. La cuenta atrás de arriba se actualiza sola con la fecha de hoy y cuenta hasta las "
     "00:00 del 25 de diciembre."),
    ("¿Puedo poner una cuenta atrás para mi boda?",
     "Sí: elige «Otra fecha», escribe el día, la hora de la ceremonia y el nombre, por ejemplo «Boda de Ana y Luis», y copia el enlace "
     "para mandarlo a los invitados."),
    ("¿Se guarda mi cuenta atrás?",
     "No se guarda en ningún servidor: todo va en el enlace. Guárdalo en favoritos o en la pantalla de inicio del móvil para volver a verla."),
    ("¿Cuándo es el Sorteo de Navidad?",
     "Siempre el 22 de diciembre. Elige «Sorteo de Navidad» en la lista para ver cuánto falta."),
    ("¿Por qué no coincide con otra cuenta atrás?",
     "Porque cada una puede contar hasta una hora distinta (00:00, la cena o la ceremonia) o usar otra zona horaria. Esta usa la hora y "
     "la zona de tu dispositivo."),
]

OPTS_ES = [("navidad", "Navidad"), ("nochebuena", "Nochebuena"), ("ano", "Año Nuevo"), ("reyes", "Reyes"), ("loteria", "Sorteo de Navidad"),
           ("jueves", "Jueves Santo"), ("fecha", "Otra fecha")]

TOOL = {
    "slug": "cuenta-atras",
    "lang": "es",
    "twin": "countdown",
    "cat": "fechas",
    "icon": "hourglass",
    "order": 50,
    "name": "Cuenta atrás",
    "k": "cuantos dias faltan navidad año nuevo reyes boda vacaciones countdown",
    "title": "Cuenta atrás online: cuántos días faltan para una fecha",
    "desc": "Cuenta atrás en días, horas, minutos y segundos para Navidad, Año Nuevo, Reyes o tu fecha (boda, viaje, examen), con enlace para compartir.",
    "h1": "Cuenta atrás",
    "updated": "2026-11-12",
    "inputs": inputs(L_ES, ["Para", "Fecha", "Hora", "Nombre", "Contar desde"], OPTS_ES, "2027-07-31", "Mi boda"),
    "js": make_js(L_ES),
    "css": ".t-cuenta-atras .hbig-n{font-variant-numeric:tabular-nums}",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Calendario laboral 2027 (BOE): Navidad, Año Nuevo y Reyes", "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-21254"),
                ("Real Decreto 236/2002 · hora de verano", "https://www.boe.es/eli/es/rd/2002/03/01/236")],
    "related": ["dias-entre-fechas", "fecha-semana-santa", "edad-exacta", "calendario-lunar-2027"],
    "tests": [
        ({"ev": "navidad", "desde": "2026-11-12"}, {"n.days": 43, "n.date": "2026-12-25"}),
        ({"ev": "ano", "desde": "2026-11-12"}, {"n.days": 50, "n.date": "2027-01-01"}),
        ({"ev": "jueves", "desde": "2026-11-12"}, {"n.days": 133, "n.date": "2027-03-25"}),
        ({"ev": "reyes", "desde": "2027-01-07"}, {"n.days": 364, "n.date": "2028-01-06"}),
        ({"ev": "navidad", "desde": "2026-12-25"}, {"n.today": True}),
        ({"ev": "fecha", "d": "2027-07-31", "h": "18:30", "desde": "2026-11-12"}, {"n.days": 261}),
        ({"ev": "fecha", "d": "2026-01-01", "desde": "2026-11-12"}, {"n.days": -315}),
    ],
}
