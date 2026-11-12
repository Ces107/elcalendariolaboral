"""Fecha de jubilación: ordinary retirement age and date (LGSS art. 205 + DT 7ª), early retirement dates (arts. 207, 208)."""

LGSS = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11724"
SS = "https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/PrestacionesPensionesTrabajadores/10963/28393/28396"

# DT 7ª LGSS: year -> (months cotizados that keep 65, required age in months otherwise)
TABLE = {2013: (423, 781), 2014: (426, 782), 2015: (429, 783), 2016: (432, 784), 2017: (435, 785), 2018: (438, 786),
         2019: (441, 788), 2020: (444, 790), 2021: (447, 792), 2022: (450, 794), 2023: (453, 796), 2024: (456, 798),
         2025: (459, 800), 2026: (459, 802), 2027: (462, 804)}


def ym(m):
    y, r = divmod(m, 12)
    return f"{y} años" + (f" y {r} {'mes' if r == 1 else 'meses'}" if r else "")


def table_html():
    rows = "".join(f"<tr><td>{y if y < 2027 else 'Desde 2027'}</td><td>{ym(a)} o más</td><td>65 años</td><td>{ym(b)}</td></tr>"
                   for y, (a, b) in TABLE.items() if y >= 2024)
    return ('<table class="tbl"><thead><tr><th>Año</th><th>Cotizado</th><th>Edad</th><th>Si cotizaste menos</th></tr></thead>'
            f"<tbody>{rows}</tbody></table>")


JS = r"""
function (v, H, C) {
  var T = C.d.t;
  function tbl(y) { return T[String(Math.min(2027, y))]; }
  function ym(m) { m = Math.floor(m + 1e-9); var y = Math.floor(m / 12), r = m % 12; return y + ' años' + (r ? ' y ' + r + (r === 1 ? ' mes' : ' meses') : ''); }
  function age(b, d) { /* full months of age at d (birthday rule: same day of month, or the last day if it does not exist) */
    var m = (d.getUTCFullYear() - b.getUTCFullYear()) * 12 + d.getUTCMonth() - b.getUTCMonth();
    if (d.getUTCDate() < b.getUTCDate() && d.getUTCDate() !== H.monthDays(d.getUTCFullYear(), d.getUTCMonth() + 1)) m--;
    return m;
  }
  function fd(d) { return d ? ('0' + d.getUTCDate()).slice(-2) + '/' + ('0' + (d.getUTCMonth() + 1)).slice(-2) + '/' + d.getUTCFullYear() : '—'; }
  var b = v.nac, ref = v.ref;
  if (!b) return { err: 'Escribe tu fecha de nacimiento.' };
  if (!ref) return { err: 'Escribe la fecha de los años cotizados.' };
  var y = isNaN(v.anos) ? 0 : v.anos, mo = isNaN(v.meses) ? 0 : v.meses;
  if (y < 0 || mo < 0 || mo > 11 || y > 60) return { err: 'Cotizado: años de 0 a 60 y meses de 0 a 11.' };
  var c0 = y * 12 + mo;
  if (age(b, ref) < 16 * 12) return { err: 'Revisa la fecha de nacimiento: a esa fecha tendrías menos de 16 años.' };
  if (c0 > age(b, ref) - 14 * 12) return { err: 'Revisa los años cotizados: son más de los que da tu edad.' };
  if (b.getUTCFullYear() < 1948) return { err: 'Esta calculadora es para jubilaciones desde 2013 (nacidos desde 1948).' };
  function cot(d) { return c0 + (v.sigue ? H.diff(ref, d) / 30.436875 : 0); } /* sigue: also counts back for past dates */
  function find(off, minCot) { /* first day with the age (ordinary age of that year and cotización, minus off months) and minCot months */
    var d = new Date(Date.UTC(b.getUTCFullYear() + 60, b.getUTCMonth(), 1));
    for (var i = 0; i < 365 * 16; i++, d = H.add(d, 1)) {
      var c = cot(d), t = tbl(d.getUTCFullYear()), req = (c >= t[0] ? 780 : t[1]) - off;
      if (age(b, d) >= req && c >= minCot) return { d: d, req: req, c: c };
    }
    return null;
  }
  var o = find(0, 180), vol = find(24, 420), inv = find(48, 396);
  if (!o) return { err: 'Con lo cotizado no llegas a los 15 años que exige la pensión de jubilación contributiva.' };
  if (vol && vol.d >= o.d) vol = null;
  if (inv && inv.d >= o.d) inv = null;
  var cm = Math.floor(o.c + 1e-9), pct = cm < 180 ? 0 : Math.min(100, 50 + 0.19 * Math.min(248, cm - 180) + 0.18 * Math.max(0, cm - 428));
  var left = age(ref, o.d), past = o.d <= ref;
  return {
    label: 'Jubilación ordinaria', big: fd(o.d),
    sub: 'a los ' + ym(o.req) + (past ? ' · ya la tienes' : ' · faltan ' + ym(Math.max(0, left))),
    rows: [
      ['Edad ordinaria', ym(o.req)],
      ['Cotizado ese día', ym(o.c)],
      ['Anticipada voluntaria', vol ? fd(vol.d) + ' · ' + ym(age(b, vol.d)) : 'no (35 años)'],
      ['Anticipada involuntaria', inv ? fd(inv.d) + ' · ' + ym(age(b, inv.d)) : 'no (33 años)'],
      ['% de la base reguladora', o.d.getUTCFullYear() >= 2027 ? H.num(H.r2(pct), 2) + ' %' : '—', 'sub']
    ],
    note: 'La anticipada lleva coeficientes reductores y exige años de cotización efectiva, sin pagas extra. ' +
      (v.sigue ? 'Supone que sigues cotizando hasta jubilarte.' : 'Supone que no cotizas más.'),
    n: { ord: H.iso(o.d), req: o.req, vol: vol ? H.iso(vol.d) : null, inv: inv ? H.iso(inv.d) : null, pct: H.r2(pct) }
  };
}
"""

BLOCKS = [
    ("Cuándo te puedes jubilar", f"""
<p>Desde 2027 la edad ordinaria de jubilación en España es de <b>67 años</b>, o de <b>65 años si has cotizado 38 años y 6 meses o
más</b>. En 2026 todavía es de 66 años y 10 meses, o 65 con 38 años y 3 meses cotizados. Lo dice el
<a href="{LGSS}#a205" rel="noopener">artículo 205 de la Ley General de la Seguridad Social</a> con el calendario de la
<a href="{LGSS}#dtseptima" rel="noopener">disposición transitoria séptima</a>, que sube la edad un poco cada año desde 2013.</p>
<p>La calculadora busca el primer día en que tu edad alcanza la exigida en ese año con lo que llevarás cotizado ese día. Por eso
importa si sigues trabajando: cada mes cotizado de más puede adelantar la jubilación a los 65. Para cobrar la pensión contributiva
hacen falta, además, al menos 15 años cotizados, dos de ellos en los últimos 15.</p>"""),
    ("Edad exigida cada año", table_html()),
    ("Ejemplo", """
<p>Nacida el 10 de junio de 1965, con 35 años cotizados el 12 de noviembre de 2026 y sin dejar de trabajar. El 10 de junio de 2030
cumple 65 años y habrá cotizado unos 38 años y 6 meses: llega justo al mínimo, así que se jubila a los <b>65</b> ese mismo día. Si
le faltaran unos meses de cotización, se jubilaría el día en que los complete, y si no los completa antes de cumplir 67, a los 67,
el 10 de junio de 2032.</p>
<p>Con la anticipada involuntaria (despido colectivo u objetivo, y seis meses inscrita como demandante de empleo) podría
jubilarse cuatro años antes de su edad, el 10 de junio de 2028, a los 63, porque tendrá más de 33 años cotizados.</p>"""),
    ("Jubilación anticipada", f"""
<p><b>Voluntaria</b> (<a href="{LGSS}#a208" rel="noopener">artículo 208</a>): hasta dos años antes de tu edad ordinaria, con 35 años
de cotización efectiva y siempre que la pensión resultante supere la mínima. <b>Involuntaria</b>
(<a href="{LGSS}#a207" rel="noopener">artículo 207</a>): hasta cuatro años antes, con 33 años cotizados, si el trabajo terminó por
despido colectivo, objetivo, concurso u otra causa ajena a tu voluntad. En las dos, la pensión baja por cada mes de adelanto con
los coeficientes de esos artículos, y para estos años mínimos no cuentan las pagas extra ni más de un año de servicio militar.</p>
<p>El porcentaje que se muestra es el del <a href="{LGSS}#a210" rel="noopener">artículo 210</a>, que se aplica entero desde 2027:
50 % por los primeros 15 años, 0,19 % por cada mes de los 248 siguientes y 0,18 % por los demás. Con 37 años cotizados llegas al
100 % de la base reguladora.</p>"""),
]

FAQ = [
    ("¿A qué edad me jubilo si nací en 1960?",
     "Depende de lo cotizado. Cumpliste 65 en 2025: con 38 años y 3 meses cotizados te jubilabas entonces. Si no, los nacidos en enero "
     "o febrero de 1960 se jubilan a los 66 años y 10 meses, a finales de 2026, y los nacidos desde marzo llegan a esa edad ya en 2027, "
     "cuando la edad exigida es de 67 años."),
    ("¿Cuántos años cotizados necesito para jubilarme a los 65?",
     "Desde 2027, 38 años y 6 meses. En 2026, 38 años y 3 meses."),
    ("¿Cuántos años hay que cotizar para cobrar la pensión?",
     "Al menos 15, y dos de ellos dentro de los 15 años anteriores a la jubilación. Para el 100 % de la base reguladora hacen falta 37."),
    ("¿Puedo jubilarme antes de la edad ordinaria?",
     "Sí: dos años antes si lo pides tú y has cotizado 35 años, o cuatro años antes si perdiste el empleo por una causa ajena a tu "
     "voluntad y has cotizado 33. La pensión se reduce por cada mes de adelanto."),
    ("¿Cuentan las pagas extra en los años cotizados?",
     "Para la edad ordinaria sí cuenta todo lo cotizado. Para los 35 o 33 años de la anticipada solo cuenta la cotización efectiva, sin "
     "la parte de las pagas extra."),
    ("¿Dónde veo cuánto he cotizado?",
     "En tu informe de vida laboral, que descargas en la sede electrónica de la Seguridad Social con certificado, Cl@ve o SMS."),
]

TOOL = {
    "slug": "fecha-jubilacion",
    "lang": "es",
    "cat": "trabajo",
    "icon": "old",
    "order": 61,
    "name": "Fecha de jubilación",
    "k": "edad jubilación 67 65 años cotizados anticipada pensión",
    "title": "¿Cuándo me jubilo? Calcular la edad y fecha de jubilación",
    "desc": "Calcula a qué edad y en qué fecha te jubilas según tus años cotizados: 65 o 67 años desde 2027, con la jubilación anticipada voluntaria e involuntaria.",
    "h1": "Calcular la fecha de jubilación",
    "updated": "2026-11-12",
    "data": {"t": {str(k): list(v) for k, v in TABLE.items()}},
    "inputs": [
        {"id": "nac", "type": "date", "label": "Nacimiento", "value": "1965-06-10", "min": "1948-01-01", "max": "2010-12-31"},
        {"id": "anos", "type": "number", "label": "Años cotizados", "value": 35, "unit": "años", "w": "s"},
        {"id": "meses", "type": "number", "label": "Meses", "value": 0, "unit": "meses", "w": "s"},
        {"id": "sigue", "type": "check", "label": "Sigo cotizando", "value": True},
        {"id": "ref", "type": "date", "label": "Cotizado a fecha", "value": "2026-11-12", "today": True, "more": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Ley General de la Seguridad Social, arts. 205, 207, 208, 210 y DT 7ª (BOE)", LGSS),
                ("Seguridad Social · Jubilación ordinaria", SS)],
    "related": ["antiguedad-empresa", "calculadora-paro", "trienios-funcionarios"],
    "tests": [
        ({"nac": "1965-06-10", "anos": "35", "meses": "0", "sigue": "1", "ref": "2026-11-12"}, {"n.ord": "2030-06-10", "n.req": 780, "n.inv": "2028-06-10", "n.vol": "2030-05-14"}),
        ({"nac": "1965-06-10", "anos": "20", "meses": "0", "sigue": "1", "ref": "2026-11-12"}, {"n.ord": "2032-06-10", "n.req": 804, "n.vol": None, "n.inv": None}),
        ({"nac": "1960-03-15", "anos": "40", "meses": "0", "sigue": "1", "ref": "2026-11-12"}, {"n.ord": "2025-03-15", "n.req": 780}),
        ({"nac": "1961-01-20", "anos": "30", "meses": "0", "sigue": "", "ref": "2026-11-12"}, {"n.ord": "2028-01-20", "n.req": 804}),
        ({"nac": "1970-01-01", "anos": "5", "meses": "0", "sigue": "", "ref": "2026-11-12"}, {"err": "Con lo cotizado no llegas a los 15 años que exige la pensión de jubilación contributiva."}),
        ({"nac": "", "anos": "5"}, {"err": "Escribe tu fecha de nacimiento."}),
    ],
}
