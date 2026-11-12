"""Salida y puesta del sol: sunrise, sunset, solar noon, day length and civil twilight for the 52 provincial capitals,
any date, in Spanish official time (Canarias one hour less). NOAA solar equations; coordinates from Wikidata (CC0)."""
import datetime as dt
import json
from pathlib import Path

from herramientas.tools import _astro as A

ROOT = Path(__file__).resolve().parents[2]
NAMES = {"alicante": "Alicante", "castellon": "Castellón de la Plana", "gipuzkoa": "San Sebastián", "navarra": "Pamplona",
         "valencia": "Valencia", "illes-balears": "Palma", "a-coruna": "A Coruña"}


def capitals():
    """[(slug, city, lat, lon, canarias)] for the 52 provinces, sorted by city name (Spanish order)."""
    prov = json.loads((ROOT / "data" / "provincias.json").read_text("utf-8"))["provincias"]
    co = json.loads((ROOT / "data" / "tools" / "coords.json").read_text("utf-8"))["coords"]
    out = []
    for p in prov:
        lat, lon = co[p["capital_ine"]]
        out.append((p["slug"], NAMES.get(p["slug"], p["capital_name"]), round(lat, 4), round(lon, 4), p["code"] in ("35", "38")))
    key = lambda s: s.lower().translate(str.maketrans("áéíóúñ", "aeioun"))  # noqa: E731
    return sorted(out, key=lambda x: key(x[1]))


CAPS = capitals()
BY = {c[0]: c for c in CAPS}
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def day(slug, d):
    _, _, lat, lon, can = BY[slug]
    tz = A.TZ_CAN if can else A.TZ_PEN
    s = A.sun(d, lat, lon)
    return A.local_hm(d, s["rise"], tz), A.local_hm(d, s["set"], tz), s["set"] - s["rise"]


def hm_len(m):
    m = round(m)
    return f"{m // 60} h {m % 60:02d} min"


def extremes(slug, year=2027):
    """Earliest/latest sunrise and sunset of the year in local time (they do not fall on the solstices: equation of time)."""
    _, _, lat, lon, can = BY[slug]
    tz = A.TZ_CAN if can else A.TZ_PEN
    vals = []
    for i in range(365):
        d = dt.date(year, 1, 1) + dt.timedelta(i)
        off = dt.datetime(d.year, d.month, d.day, 12, tzinfo=tz).utcoffset().total_seconds() / 60
        s = A.sun(d, lat, lon)
        vals.append((d, s["rise"] + off, s["set"] + off))
    hhmm = lambda m: f"{int(round(m)) // 60:02d}:{int(round(m)) % 60:02d}"  # noqa: E731
    pick = lambda f, k: (lambda x: (x[0], hhmm(x[1]), hhmm(x[2])))(f(vals, key=k))  # noqa: E731
    return (pick(min, lambda x: x[1]), pick(max, lambda x: x[2]), pick(max, lambda x: x[1]), pick(min, lambda x: x[2]))


def fd(d):
    return f"{d.day} de {MESES[d.month - 1]}"


def blocks(ctx):
    j21, d21 = dt.date(2027, 6, 21), dt.date(2027, 12, 21)
    rows = ""
    for s in ("madrid", "a-coruna", "barcelona", "sevilla", "illes-balears", "las-palmas"):
        r1, s1, l1 = day(s, j21)
        r2, s2, l2 = day(s, d21)
        rows += f"<tr><td>{BY[s][1]}</td><td>{r1} · {s1}</td><td>{hm_len(l1)}</td><td>{r2} · {s2}</td><td>{hm_len(l2)}</td></tr>"
    mr, ms, ml = day("madrid", j21)
    e, la, lr, es = extremes("madrid")
    cr, cs, _ = day("a-coruna", j21)
    br, bs, _ = day("barcelona", j21)
    return [
        ("Horas de sol en 2027", f"""
<p>En Madrid, el 21 de junio de 2027 el sol sale a las <b>{mr}</b> y se pone a las <b>{ms}</b>: {hm_len(ml)} de luz, el día más
largo del año. Elige otra capital o cualquier fecha y la tabla de debajo del resultado da las horas de todo ese mes, lista para
imprimir. Las horas son las oficiales de cada lugar: hora peninsular en la Península, Baleares, Ceuta y Melilla, y una hora menos
en Canarias, con el horario de verano ya aplicado.</p>
<table class="tbl"><thead><tr><th>Capital</th><th>21 jun: sale · se pone</th><th>Luz</th><th>21 dic: sale · se pone</th><th>Luz</th></tr></thead>
<tbody>{rows}</tbody></table>"""),
        ("Por qué en Galicia anochece más tarde", f"""
<p>Toda la Península usa la misma hora oficial, pero el sol pasa por el meridiano de cada sitio a una hora distinta: unos 4
minutos más tarde por cada grado de longitud hacia el oeste. A Coruña está más de 10 grados al oeste de Barcelona, así que el 21 de
junio el sol sale allí a las {cr} y se pone a las {cs}, frente a las {br} y las {bs} de Barcelona. La duración del día depende
sobre todo de la latitud: cuanto más al norte, más largos los días de verano y más cortos los de invierno.</p>
<p>Otra curiosidad: el amanecer más temprano no cae en el día más largo. En Madrid, en 2027, el sol sale más pronto el
{fd(e[0])} ({e[1]}) y se pone más tarde el {fd(la[0])} ({la[2]}); el amanecer más tardío es el {fd(lr[0])} ({lr[1]}) y el
atardecer más temprano, el {fd(es[0])} ({es[2]}). La causa es la ecuación del tiempo: por la órbita elíptica de la Tierra y la
inclinación de su eje, el mediodía solar se adelanta y se retrasa a lo largo del año hasta unos 16 minutos.</p>"""),
        ("Cómo se calcula", """
<p>Las horas salen de las ecuaciones de posición solar de la NOAA (la agencia estadounidense de océanos y atmósfera, basadas en las
de Jean Meeus): la declinación del sol y la ecuación del tiempo de ese día dan el mediodía solar y el ángulo horario en el que el
centro del sol está 0,833 grados bajo el horizonte, que es cuando su borde superior asoma teniendo en cuenta la refracción del aire.
El crepúsculo civil empieza y acaba con el sol a 6 grados bajo el horizonte: hasta entonces hay luz suficiente para estar al aire
libre sin luz artificial.</p>
<p>Las coordenadas son las del centro de cada capital, a nivel del mar y sin montañas en el horizonte, como en las tablas del
Observatorio Astronómico Nacional. Comparadas con las del Observatorio Naval de Estados Unidos, coinciden al minuto o difieren en
uno. El cambio a horario de verano se hace el último domingo de marzo y el de invierno, el último domingo de octubre, según el
Real Decreto 236/2002.</p>"""),
    ]


FAQ = [
    ("¿Qué día de 2027 tiene más horas de sol?",
     f"El 21 de junio, con {hm_len(day('madrid', dt.date(2027, 6, 21))[2])} de luz en Madrid. El más corto es el 21 o 22 de diciembre, "
     f"con {hm_len(day('madrid', dt.date(2027, 12, 21))[2])}."),
    ("¿Qué es el mediodía solar?",
     "El momento en que el sol está más alto en el cielo y cruza el meridiano del lugar. En la Península cae entre las 12:30 y las 14:45 "
     "de la hora oficial, porque España usa la hora de Europa central estando al oeste de su meridiano."),
    ("¿Qué diferencia hay entre amanecer y alba?",
     "El amanecer (orto) es cuando asoma el borde del sol. El alba o inicio del crepúsculo civil llega una media hora antes, con el sol "
     "6 grados bajo el horizonte y ya bastante claridad."),
    ("¿Por qué en Canarias amanece a una hora parecida a la de Madrid?",
     "Canarias tiene una hora menos, pero está unos 12 grados más al oeste, lo que retrasa el sol unos 47 minutos: las dos cosas casi se "
     "compensan. Lo que queda depende de la latitud: en invierno, con días más largos, amanece antes en Las Palmas (07:49 el 21 de "
     "diciembre, frente a las 08:34 de Madrid) y en verano, después (07:06 frente a 06:45 el 21 de junio)."),
    ("¿Las horas cambian si estoy en un pueblo de la provincia?",
     "Muy poco: unos 4 minutos por cada grado de longitud hacia el oeste y algo más o menos según la latitud. Para un pueblo a 50 km de la "
     "capital, la diferencia es de uno a tres minutos."),
]

JS = r"""
function (v, H, C) {
""" + A.TZ_JS + A.SUN_JS + r"""
  var WD = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];
  var MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var c = C.d.c[v.ciudad];
  if (!c) return { err: 'Elige una capital.' };
  if (!v.fecha) return { err: 'Elige una fecha.' };
  var y = v.fecha.getUTCFullYear(), m = v.fecha.getUTCMonth() + 1, d = v.fecha.getUTCDate();
  if (y < 1900 || y > 2100) return { err: 'Fecha entre 1900 y 2100.' };
  var tz = c[3] ? 'Atlantic/Canary' : 'Europe/Madrid';
  function one(dd) {
    var t0 = Date.UTC(y, m - 1, dd), s = sunUtc(y, m, dd, c[1], c[2], 90.833), t = sunUtc(y, m, dd, c[1], c[2], 96);
    var rp = tzParts(Math.round((t0 + s.rise * 6e4) / 6e4) * 6e4, tz);
    return { rise: hm(t0 + s.rise * 6e4, tz), set: hm(t0 + s.set * 6e4, tz), noon: hm(t0 + s.noon * 6e4, tz),
      dawn: hm(t0 + t.rise * 6e4, tz), dusk: hm(t0 + t.set * 6e4, tz), len: s.set - s.rise, rmin: rp.h * 60 + rp.mi,
      off: Math.round((Date.UTC(rp.y, rp.m - 1, rp.d, rp.h, rp.mi) - Math.round((t0 + s.rise * 6e4) / 6e4) * 6e4) / 36e5) };
  }
  function dur(x) { x = Math.round(x); return Math.floor(x / 60) + ' h ' + p2(x % 60) + ' min'; }
  var r = one(d), pd = new Date(Date.UTC(y, m - 1, d - 1));
  var prev = sunUtc(pd.getUTCFullYear(), pd.getUTCMonth() + 1, pd.getUTCDate(), c[1], c[2], 90.833);
  var dl = Math.round(r.len - (prev.set - prev.rise)), smin = +r.set.slice(0, 2) * 60 + +r.set.slice(3);
  var nd = H.monthDays(y, m), rows = '';
  for (var i = 1; i <= nd; i++) {
    var o = one(i), w = H.wd(new Date(Date.UTC(y, m - 1, i)));
    rows += '<tr' + (i === d ? ' class="on"' : '') + '><td>' + i + ' ' + WD[w].slice(0, 3) + '</td><td>' + o.rise + '</td><td>' + o.set + '</td><td>' + dur(o.len) + '</td></tr>';
  }
  return {
    label: 'Sale y se pone el sol', big: r.rise + ' · ' + r.set,
    sub: H.esc(c[0]) + ' · ' + WD[H.wd(v.fecha)] + ' ' + d + ' de ' + MES[m - 1] + ' de ' + y + ' · ' + dur(r.len) + ' de luz',
    rows: [['Amanecer', r.rise], ['Mediodía solar', r.noon], ['Atardecer', r.set], ['Duración del día', dur(r.len), 'tot'],
      ['Frente al día anterior', (dl > 0 ? '+' : dl < 0 ? '−' : '') + Math.abs(dl) + ' min'], ['Alba (crepúsculo civil)', r.dawn, 'z'],
      ['Fin del crepúsculo civil', r.dusk, 'z'], ['Hora oficial', (c[3] ? 'Canarias' : 'peninsular') + ' · UTC+' + r.off, 'z']],
    html: '<h2 class="cq-h">' + H.esc(c[0]) + ' · ' + MES[m - 1] + ' de ' + y + '</h2><table class="tbl sol"><thead><tr><th>Día</th><th>Sale</th><th>Se pone</th><th>Luz</th></tr></thead><tbody>' + rows + '</tbody></table>',
    note: 'Horas a nivel del mar en el centro de la ciudad, sin relieve en el horizonte.',
    print: true,
    n: { rise: r.rmin, set: smin, len: Math.round(r.len), off: r.off }
  };
}
"""

TOOL = {
    "slug": "amanecer-atardecer",
    "lang": "es",
    "cat": "cielo",
    "cat_name": "Sol y luna",
    "icon": "sunrise",
    "order": 20,
    "name": "Amanecer y atardecer",
    "k": "salida puesta sol orto ocaso horas de luz crepúsculo",
    "title": "Salida y puesta del sol hoy en tu ciudad: horas exactas",
    "desc": "A qué hora sale y se pone el sol en las 52 capitales de provincia, cualquier día: horas de luz, mediodía solar, crepúsculo y tabla del mes.",
    "h1": "Salida y puesta del sol",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ciudad", "type": "select", "label": "Ciudad", "value": "madrid", "options": [(c[0], c[1]) for c in CAPS]},
        {"id": "fecha", "type": "date", "label": "Fecha", "value": "2027-06-21", "today": True, "min": "1900-01-01", "max": "2100-12-31"},
    ],
    "data": {"c": {c[0]: [c[1], c[2], c[3], 1 if c[4] else 0] for c in CAPS}},
    "js": JS,
    "css": ".sol{max-width:420px;margin-top:10px}.sol td,.sol th{text-align:left;padding:3px 10px 3px 0}.sol tr.on td{font-weight:700;background:var(--bg2)}",
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Observatorio Astronómico Nacional (IGN) · salidas y puestas de sol", "https://astronomia.ign.es/web/guest/hora-salidas-y-puestas-de-sol"),
                ("Real Decreto 236/2002 · hora de verano", "https://www.boe.es/eli/es/rd/2002/03/01/236"),
                ("US Naval Observatory · Sun and Moon data", "https://aa.usno.navy.mil/data/RS_OneDay")],
    "credits": [("NOAA Global Monitoring Laboratory · Solar Calculator (ecuaciones)", "dominio público", "https://gml.noaa.gov/grad/solcalc/"),
                ("Wikidata · coordenadas de los municipios (P625)", "CC0 1.0", "https://www.wikidata.org/wiki/Property:P625")],
    "related": ["calendario-lunar-2027", "cambio-de-hora/", "dia-de-la-semana", "semana/"],
    "tests": [
        # US Naval Observatory: Madrid 2027-06-21 06:45 / 21:48 CEST
        ({"ciudad": "madrid", "fecha": "2027-06-21"}, {"n.rise": 405, "n.set": 1308, "n.off": 2}),
        # USNO: Las Palmas de Gran Canaria 2027-12-21 07:49 / 18:10 WET
        ({"ciudad": "las-palmas", "fecha": "2027-12-21"}, {"n.rise": 469, "n.set": 1090, "n.off": 0}),
        # USNO: Barcelona 2027-06-21 06:18 / 21:28
        ({"ciudad": "barcelona", "fecha": "2027-06-21"}, {"n.rise": 378, "n.set": 1288}),
        # USNO: Málaga 2027-01-01 08:30 / 18:12 CET
        ({"ciudad": "malaga", "fecha": "2027-01-01"}, {"n.rise": 510, "n.set": 1092, "n.off": 1}),
        ({"ciudad": "madrid", "fecha": "1850-01-01"}, {"err": "Fecha entre 1900 y 2100."}),
        ({"ciudad": "madrid", "fecha": ""}, {"err": "Elige una fecha."}),
    ],
}
