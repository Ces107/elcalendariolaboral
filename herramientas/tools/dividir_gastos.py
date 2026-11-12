"""Dividir gastos: who owes whom after a shared trip or flat, settled with at most n-1 transfers (greedy largest-first)."""

BLOCKS = [
    ("Cómo se reparten los gastos", """
<p>Escribe cada persona con lo que ha pagado, separadas por comas: <code>Ana 120, Luis 45,50, Marta 0</code>. Si alguien pagó
varias cosas, puedes repetir su nombre (<code>Ana 80, Ana 40</code>) y se suman. Quien no pagó nada se escribe con 0 para que
cuente en el reparto. La calculadora suma todo, divide entre las personas y te dice quién tiene que pagar a quién, con el
menor número de transferencias posible para el caso habitual.</p>
<p>Ejemplo de un fin de semana: Ana pagó la casa rural (100 €), Luis la compra (50 €), Marta la gasolina (30 €) y Pedro nada.
Son 180 €, 45 € por persona. A Ana le deben 55 €, a Luis 5 €, Marta debe 15 € y Pedro 45 €. Se arregla con tres
transferencias: Pedro paga 45 € a Ana, Marta 10 € a Ana y Marta 5 € a Luis. Sin calcularlo, lo normal es que cada uno pague a
cada uno y acaben haciéndose seis o siete Bizums.</p>"""),
    ("El método", """
<p>Primero se calcula el <b>saldo</b> de cada persona: lo que pagó menos su parte. Un saldo positivo es dinero que le deben;
uno negativo, lo que debe. Después se empareja a quien más debe con quien más le deben, se salda el menor de los dos importes
y se repite hasta que todos quedan a cero. Cada paso deja al menos a una persona en paz, así que nunca hacen falta más de
<b>n − 1 transferencias</b> para n personas, y casi siempre son menos.</p>
<p>Se calcula en céntimos para que todo cuadre: si 10 € se reparten entre tres, dos personas ponen 3,33 € y una 3,34 €, y la
suma de las transferencias es exactamente lo que se pagó de más. Encontrar el mínimo absoluto de transferencias en todos los
casos es un problema difícil de cálculo; este método da el mínimo en la mayoría de repartos reales de piso, viaje o cena.</p>
<p>Si un gasto no es de todos (por ejemplo, unas entradas que solo compraron dos), haz un reparto aparte con esas personas y
suma los resultados. Para un piso compartido, apunta los recibos del mes de cada uno y haz las cuentas una vez al mes.</p>"""),
]

FAQ = [
    ("¿Cómo se calcula quién debe a quién?",
     "Se suma lo que pagó cada uno, se divide el total entre todos y se compara: quien pagó menos que su parte debe la diferencia y "
     "quien pagó más la recibe. Las transferencias emparejan a los que más deben con los que más tienen que recibir."),
    ("¿Qué pasa si alguien no ha pagado nada?",
     "Escríbelo con 0. Cuenta en el reparto y le tocará pagar su parte entera a quien haya puesto de más."),
    ("¿Puedo apuntar varios gastos de la misma persona?",
     "Sí: repite el nombre con cada importe (Ana 30, Ana 12,50) y se suman. Los nombres no distinguen mayúsculas."),
    ("¿Los datos se guardan?",
     "No. El cálculo se hace en tu navegador. Con «Copiar enlace» guardas los gastos en la dirección para mandársela al grupo."),
    ("¿Y si algunos pagan más parte que otros?",
     "Una pareja que cuenta doble puede escribirse como dos personas. Si el reparto es por porcentajes, calcula antes cuánto le toca a "
     "cada uno y usa la diferencia con lo que pagó."),
]

JS = r"""
function (v, H, C) {
  function amount(s) {
    if (s.indexOf(',') >= 0) s = s.replace(/\./g, '').replace(',', '.');
    else if (/^\d{1,3}(\.\d{3})+$/.test(s)) s = s.replace(/\./g, '');
    return Math.round(parseFloat(s) * 100);
  }
  var txt = String(v.pagos), re = /([^\d;,\n]*[^\d\s;,\n.][^\d;,\n]*?)\s*[:=]?\s*(\d[\d.]*(?:,\d{1,2})?)(?:\s*€)?/g, m, who = [], key = {}, paid = [];
  var rest = txt;
  while ((m = re.exec(txt))) {
    var name = m[1].replace(/^[\s,;.:\-]+|[\s,;.:\-]+$/g, '').replace(/\s+/g, ' '), k = name.toLowerCase(), c = amount(m[2]);
    if (!name || isNaN(c)) continue;
    if (!(k in key)) { key[k] = who.length; who.push(name); paid.push(0); }
    paid[key[k]] += c;
    rest = rest.replace(m[0], '');
  }
  if (/[^\s,;.:\-€]/.test(rest)) return { err: 'No entiendo «' + H.esc(rest.replace(/^[\s,;]+/, '').slice(0, 30).trim()) + '»: escribe Nombre importe, separados por comas.' };
  var n = who.length;
  if (n < 2) return { err: 'Escribe al menos dos personas con lo que pagó cada una (Ana 60, Luis 0).' };
  var total = paid.reduce(function (a, b) { return a + b; }, 0), base = Math.floor(total / n), extra = total - base * n;
  var bal = paid.map(function (p, i) { return p - base - (i < extra ? 1 : 0); });
  var b = bal.slice(), tr = [];
  for (var guard = 0; guard < 2 * n; guard++) {
    var dI = -1, cI = -1;
    for (var i = 0; i < n; i++) { if (b[i] < 0 && (dI < 0 || b[i] < b[dI])) dI = i; if (b[i] > 0 && (cI < 0 || b[i] > b[cI])) cI = i; }
    if (dI < 0 || cI < 0) break;
    var x = Math.min(-b[dI], b[cI]);
    tr.push([dI, cI, x]); b[dI] += x; b[cI] -= x;
  }
  var e = function (c) { return H.eur(c / 100); };
  var html = tr.length ? '<ul class="dg-t">' + tr.map(function (t) {
    return '<li><b>' + H.esc(who[t[0]]) + '</b> <span aria-hidden="true">→</span><span class="vh"> paga a </span> <b>' + H.esc(who[t[1]]) + '</b> <span class="num">' + e(t[2]) + '</span></li>';
  }).join('') + '</ul>' : '';
  html += '<table class="tbl"><thead><tr><th>Persona</th><th class="num">Pagó</th><th class="num">Saldo</th></tr></thead><tbody>' + who.map(function (w, i) {
    return '<tr><td>' + H.esc(w) + '</td><td class="num">' + e(paid[i]) + '</td><td class="num">' + (bal[i] > 0 ? '+' : '') + e(bal[i]) + '</td></tr>';
  }).join('') + '</tbody></table>';
  return {
    label: tr.length ? 'Transferencias' : 'Cuentas', big: tr.length ? String(tr.length) : 'En paz',
    sub: 'Total ' + e(total) + ' · ' + n + ' personas · ' + e(base) + (extra ? '–' + e(base + 1) : '') + ' cada una',
    html: html,
    n: { count: tr.length, total: total / 100, list: tr.map(function (t) { return who[t[0]] + '>' + who[t[1]] + ':' + t[2] / 100; }) }
  };
}
"""

CSS = ".dg-t{list-style:none;padding:0;margin:12px 0;font-size:1.1rem}.dg-t li{padding:6px 0;border-bottom:1px solid var(--line,#e5e7eb)}.dg-t .num{float:right;font-weight:700}"

TOOL = {
    "slug": "dividir-gastos",
    "lang": "es",
    "cat": "dinero",
    "icon": "users-group",
    "order": 40,
    "name": "Dividir gastos",
    "k": "repartir gastos viaje piso compartido cuentas grupo quién debe bizum cena",
    "title": "Dividir gastos entre amigos: quién debe a quién",
    "desc": "Reparte los gastos de un viaje, una cena o un piso compartido: escribe lo que pagó cada uno y te dice quién paga a quién con las mínimas transferencias.",
    "h1": "Dividir gastos: quién debe a quién",
    "updated": "2026-11-12",
    "inputs": [{"id": "pagos", "type": "text", "label": "Quién pagó", "value": "Ana 100, Luis 50, Marta 30, Pedro 0", "w": "xl",
                "placeholder": "Ana 100, Luis 50, Marta 0"}],
    "js": JS,
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Banco de España · Portal del Cliente Bancario", "https://clientebancario.bde.es/pcb/es/")],
    "related": ["amigo-invisible", "coste-viaje-coche", "presupuesto-viaje", "kilometraje-dietas"],
    "tests": [
        ({"pagos": "Ana 60, Luis 30, Marta 0"}, {"n.count": 1, "n.list": ["Marta>Ana:30"]}),
        ({"pagos": "Ana 100, Luis 50, Marta 30, Pedro 0"}, {"n.count": 3, "n.list": ["Pedro>Ana:45", "Marta>Ana:10", "Marta>Luis:5"]}),
        ({"pagos": "Ana 10, Luis 10"}, {"n.count": 0}),
        ({"pagos": "Ana 10, Luis 0, Marta 0"}, {"n.count": 2, "n.list": ["Luis>Ana:3.33", "Marta>Ana:3.33"]}),
        ({"pagos": "Ana 20, ana 10,50, Luis 0, Pedro 1.200"}, {"n.total": 1230.5, "n.count": 2}),
        ({"pagos": "Ana 50"}, {"err": "Escribe al menos dos personas con lo que pagó cada una (Ana 60, Luis 0)."}),
    ],
}
