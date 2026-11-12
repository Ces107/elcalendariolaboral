"""Incubación de huevos: hatch date, last turning day, candling days and a day-by-day plan for chicken, duck, Muscovy,
quail, goose, turkey, guinea fowl, pheasant, partridge and pigeon eggs. English twin: egg_incubation_calculator.py."""
import json

MSU = "https://extension.msstate.edu/agriculture/livestock/poultry/hatchery-management-guide-for-game-bird-and-small-poultry-flock-owners"
MSD = "https://www.msdvetmanual.com/multimedia/table/approximate-incubation-periods"

# key, days, last turning day, forced-air temperature °C (100 °F / 99 °F), wet bulb °C, ES name, EN name
BIRDS = [
    ("gallina", 21, 18, 37.8, "29,5–30,5", "Gallina", "Chicken"),
    ("pato", 28, 25, 37.8, "29,5–30", "Pato (no mudo)", "Duck"),
    ("mudo", 35, 31, 37.8, "29,5–30", "Pato mudo (criollo)", "Muscovy duck"),
    ("codorniz", 17, 15, 37.8, "29,5–30", "Codorniz japonesa", "Coturnix quail"),
    ("oca", 30, 25, 37.2, "30–31", "Oca o ganso", "Goose"),
    ("pavo", 28, 25, 37.2, "29–30", "Pavo", "Turkey"),
    ("pintada", 28, 25, 37.8, "29,5–30,5", "Pintada (gallina de Guinea)", "Guinea fowl"),
    ("faisan", 24, 21, 37.8, "30–31", "Faisán", "Pheasant"),
    ("perdiz", 24, 20, 37.8, "27–28", "Perdiz chukar", "Chukar partridge"),
    ("paloma", 17, 15, 37.8, "29,5–30,5", "Paloma", "Pigeon"),
]

WB_F = {"gallina": "85–87", "pato": "85–86", "mudo": "85–86", "codorniz": "85–86", "oca": "86–88", "pavo": "84–86",
        "pintada": "85–87", "faisan": "86–88", "perdiz": "81–83", "paloma": "85–87"}  # MSU wet bulb, °F

L_ES = {
    "mon": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    "wd": ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"],
    "label": "Eclosión prevista", "start": "Puesta en incubadora", "turn": "Último volteo", "lock": "Sin volteo, más humedad",
    "c1": "Primer miraje", "c2": "Segundo miraje", "hatch": "Eclosión", "temp": "Temperatura", "wb": "bulbo húmedo",
    "days": " días", "day": "Día", "date": "Fecha", "task": "Tarea", "t_turn": "Voltear 3-5 veces (número impar)",
    "t_lock": "No voltear · subir humedad", "t_c": "Mirar al trasluz", "t_h": "Eclosión", "today": "hoy",
    "err": "Pon la fecha en que metes los huevos.", "sub": "Volteo hasta el ", "note": "Datos de incubadora con ventilador (Mississippi State University). Los huevos de razas pesadas o guardados más de 7 días pueden tardar 1 día más.",
    "ics": "incubacion.ics", "x": "Incubación", "inc": "Incubación · ",
}


def bird_options(lang):
    return [(k, (es if lang == "es" else en)) for k, _, _, _, _, es, en in BIRDS]


def make_js(L):
    en = L.get("lang") == "en"
    b = {k: [d, t, c, WB_F[k] if en else wb, es, en_] for k, d, t, c, wb, es, en_ in BIRDS}
    return r"""
function (v, H, C) {
  var L = """ + json.dumps(L, ensure_ascii=False) + r""", B = """ + json.dumps(b, ensure_ascii=False) + r""";
  var s = B[v.ave] || B.gallina, d0 = v.fecha, en = L.lang === 'en';
  if (!d0) return { err: L.err };
  function f(d) { return L.wd[H.wd(d)] + ' ' + d.getUTCDate() + ' ' + L.mon[d.getUTCMonth()]; }
  var n = s[0], tl = s[1], hatch = H.add(d0, n), last = H.add(d0, tl);
  var c1 = Math.round(n / 3), c2 = tl, temp = s[2] + (v.aire ? 1 : 0);
  var name = en ? s[5] : s[4], t = H.today ? H.diff(d0, H.today()) : -1;
  var tr = '';
  for (var k = 0; k <= n; k++) {
    var task = k === n ? L.t_h : k > tl ? L.t_lock : L.t_turn;
    if (k === c1 || k === c2) task += ' · ' + L.t_c;
    tr += '<tr' + (k === t ? ' class="hd-now"' : k > tl ? ' class="hd-lock"' : '') + '><td class="num">' + k + '</td><td>' + f(H.add(d0, k)) +
      (k === t ? ' · ' + L.today : '') + '</td><td>' + task + '</td></tr>';
  }
  var html = '<details class="hplan"><summary>' + L.x + ' · ' + n + L.days + '</summary><table class="tbl"><thead><tr><th>' + L.day + '</th><th>' + L.date +
    '</th><th>' + L.task + '</th></tr></thead><tbody>' + tr + '</tbody></table></details>';
  function ev(d, e, txt, u) { return 'BEGIN:VEVENT\r\nUID:' + u + H.icsDate(d0) + '@elcalendariolaboral.es\r\nDTSTAMP:20261112T000000Z\r\nDTSTART;VALUE=DATE:' + H.icsDate(d) +
    '\r\nDTEND;VALUE=DATE:' + H.icsDate(H.add(e, 1)) + '\r\nSUMMARY:' + H.icsEsc(txt) + '\r\nTRANSP:TRANSPARENT\r\nEND:VEVENT\r\n'; }
  var ics = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//elcalendariolaboral.es//incubacion//' + (en ? 'EN' : 'ES') + '\r\nCALSCALE:GREGORIAN\r\n' +
    ev(H.add(d0, c1), H.add(d0, c1), L.inc + L.c1, 'a') + ev(last, last, L.inc + L.turn, 'b') + ev(H.add(last, 1), H.add(hatch, -1), L.inc + L.lock, 'c') +
    ev(hatch, hatch, L.inc + L.hatch + ' · ' + name, 'd') + 'END:VCALENDAR\r\n';
  return { label: L.label + ' · ' + name, big: f(hatch) + ' ' + hatch.getUTCFullYear(), sub: n + L.days + ' · ' + L.sub + f(last),
    rows: [[L.start, f(d0)], [L.c1 + ' (' + L.day.toLowerCase() + ' ' + c1 + ')', f(H.add(d0, c1))], [L.turn + ' (' + L.day.toLowerCase() + ' ' + tl + ')', f(last)],
      [L.lock, f(H.add(last, 1)) + ' → ' + f(hatch), 'sub'], [L.temp, (en ? Math.round(temp * 9 / 5 + 32) + ' °F' : H.num(temp, 1) + ' °C') + ' · ' + L.wb + ' ' + s[3] + (en ? ' °F' : ' °C')], [L.hatch, f(hatch), 'tot']],
    html: html, note: L.note, print: true, ics: { name: L.ics, text: ics },
    n: { hatch: H.iso(hatch), last: H.iso(last), c1: c1, days: n, temp: temp } };
}
"""


CSS = ".hplan summary{cursor:pointer;font-weight:600;margin:.8rem 0 .4rem}.hplan tr.hd-lock td{background:color-mix(in srgb,currentColor 6%,transparent)}.hplan tr.hd-now td{font-weight:700}"


def blocks(ctx):
    rows = "".join(f"<tr><td>{es}</td><td class=\"num\">{d}</td><td class=\"num\">{t}</td><td class=\"num\">{str(c).replace('.', ',')} °C</td></tr>"
                   for k, d, t, c, wb, es, en in BIRDS)
    return [
        ("Cuántos días tarda en nacer cada huevo", f"""
<p>Un huevo de gallina eclosiona a los <b>21 días</b> de meterlo en la incubadora; los de pato y pavo a los <b>28</b>, el pato mudo
a los 35, la oca entre 28 y 34 (30 de media), la codorniz japonesa a los <b>17</b> y la pintada a los 28. El día 0 es el día en que
metes los huevos, y el pollito suele picar el cascarón la víspera de la fecha prevista.</p>
<table class="tbl"><thead><tr><th>Ave</th><th>Días</th><th>Último volteo</th><th>Temperatura</th></tr></thead><tbody>{rows}</tbody></table>
<p>La calculadora te da la fecha de eclosión, el último día de volteo, los dos mirajes y un plan día a día que puedes imprimir o
pasar a tu calendario.</p>"""),
        ("Volteo, temperatura y humedad", f"""
<p>Hay que <b>voltear los huevos</b> desde el primer día hasta dos o tres días antes de la eclosión para que el embrión no se pegue a
la membrana: con volteador automático, al menos cada dos horas; a mano, un número impar de veces al día (3, 5 o 7), para que el
huevo no pase dos noches seguidas del mismo lado. Marca una X en un lado del huevo para comprobar que lo giras de verdad. A partir del
último día de volteo («encierro» o lockdown) no se abre la incubadora y se sube la humedad para que la membrana no se seque.</p>
<p>Con ventilador, la temperatura es de <b>37,8 °C</b> (100 °F) para casi todas las aves y 37,2 °C para oca y pavo; en una
incubadora sin ventilador (aire quieto) se mide a la altura de la parte alta del huevo y se pone algo más alta, entre 1 y 1,5 °C.
La humedad se da como temperatura de bulbo húmedo: unos 29,5-30,5 °C, que con 37,8 °C equivalen a una humedad relativa cercana al
55-60 %.</p>"""),
        ("Ejemplo y fuentes", f"""
<p>Si metes huevos de gallina el <b>lunes 1 de marzo de 2027</b>, el primer miraje toca el día 7 (8 de marzo), el último volteo el
día 18 (19 de marzo) y la eclosión el día 21, el <b>lunes 22 de marzo</b>. Los días, el último volteo y las temperaturas son los de la
guía de incubación de la <a href="{MSU}" rel="noopener">Universidad Estatal de Misisipi</a> para incubadoras de aire forzado,
coherentes con la tabla de <a href="{MSD}" rel="noopener">periodos de incubación del Manual Veterinario MSD</a>. El primer miraje
se pone en el primer tercio de la incubación (día 7 en la gallina), cuando ya se ven los vasos sanguíneos; el segundo, el último día
de volteo, para retirar los huevos que no se han desarrollado.</p>"""),
    ]


FAQ = [
    ("¿Cuántos días tarda en nacer un pollito?",
     "21 días desde que el huevo entra en la incubadora a 37,8 °C. Puede adelantarse o retrasarse un día si la temperatura no ha sido "
     "estable o si los huevos llevaban más de una semana guardados."),
    ("¿Cuándo se dejan de voltear los huevos de gallina?",
     "El día 18. Desde ahí hasta la eclosión no se voltean ni se abre la incubadora, y se sube la humedad."),
    ("¿Cuánto tarda en eclosionar un huevo de pato?",
     "28 días el pato común (pekín, corredor, khaki), 35 el pato mudo o criollo. Se dejan de voltear los días 25 y 31."),
    ("¿Cuántos días tarda un huevo de codorniz?",
     "17 días la codorniz japonesa, con el último volteo el día 15. La codorniz de Virginia (bobwhite) tarda 23-24."),
    ("¿Qué pasa si se va la luz durante la incubación?",
     "Unas horas de frío al principio suelen alargar la incubación sin matar los embriones; tapa la incubadora con una manta y no "
     "la abras. El calor excesivo es mucho más peligroso que un enfriamiento corto."),
    ("¿Cuándo se hace el miraje de los huevos?",
     "En la gallina, hacia el día 7 (ya se ven las venas y el embrión) y el día 18, antes del encierro, para quitar los huevos claros "
     "o los embriones muertos."),
]

TOOL = {
    "slug": "incubacion-huevos",
    "lang": "es",
    "twin": "egg-incubation-calculator",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "egg-cracked",
    "order": 30,
    "name": "Incubación de huevos",
    "k": "incubadora gallina pato codorniz oca pavo pintada eclosion volteo miraje calendario 21 dias",
    "title": "Calendario de incubación de huevos: eclosión y volteo",
    "desc": "Fecha de eclosión, último volteo, mirajes y plan día a día para huevos de gallina (21 días), pato, codorniz, oca, pavo o pintada. Imprimible y .ics.",
    "h1": "Calendario de incubación de huevos",
    "crumb": "Incubación de huevos",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ave", "type": "select", "label": "Ave", "value": "gallina", "options": bird_options("es")},
        {"id": "fecha", "type": "date", "label": "Puesta", "value": "2026-11-12", "today": True, "min": "2000-01-01", "max": "2035-12-31"},
        {"id": "aire", "type": "check", "label": "Sin ventilador", "value": False, "more": True},
    ],
    "js": make_js(L_ES),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Mississippi State University Extension · Hatchery management guide", MSU),
                ("Manual Veterinario MSD · periodos de incubación", MSD)],
    "related": ["pienso-gallinas", "gestacion-animal", "calendario-lunar-2027"],
    "tests": [
        ({"ave": "gallina", "fecha": "2027-03-01"}, {"n.hatch": "2027-03-22", "n.last": "2027-03-19", "n.c1": 7}),
        ({"ave": "mudo", "fecha": "2027-03-01"}, {"n.hatch": "2027-04-05", "n.days": 35}),
        ({"ave": "codorniz", "fecha": "2027-12-20"}, {"n.hatch": "2028-01-06", "n.last": "2028-01-04"}),
        ({"ave": "oca", "fecha": "2027-03-01", "aire": True}, {"n.temp": 38.2}),
        ({"ave": "pavo", "fecha": ""}, {"err": "Pon la fecha en que metes los huevos."}),
    ],
}
