"""Números a letras: an amount in euros (or a plain number) written in Spanish words, as invoices, contracts and cheques need."""

RAE = "https://www.rae.es/dpd/cardinales"
RAE_UNO = "https://www.rae.es/dpd/uno"

BLOCKS = [
    ("Cómo se escribe una cantidad en letras", """
<p>Escribe la cifra con coma o punto decimal y obtendrás el texto listo para copiar: 1.234,50 € se escribe <b>mil doscientos
treinta y cuatro euros con cincuenta céntimos</b>. Debajo tienes la misma cantidad en mayúsculas y con la cifra entre
paréntesis, que es la forma habitual en contratos, recibos y facturas: «MIL DOSCIENTOS TREINTA Y CUATRO EUROS CON CINCUENTA
CÉNTIMOS (1.234,50 €)». Con «Número» se escribe la cifra sola, sin moneda, por ejemplo para una cláusula o un acta.</p>
<p>Escribir el importe en letras evita que alguien añada o cambie una cifra. Si en un documento la cantidad en letras y la
cifra no coinciden, en la letra de cambio vale la escrita en letras (artículo 7 de la Ley Cambiaria y del Cheque), y la misma
regla rige para pagarés y cheques.</p>"""),
    ("Las reglas que aplica", f"""
<p>Sigue las normas de la <a href="{RAE}" rel="noopener">Real Academia Española para los numerales cardinales</a>. Del 16 al 29
se escriben en una palabra (dieciséis, veintidós, veintitrés) y desde el 31 en tres (treinta y uno). «Cien» es solo el 100 justo;
desde el 101, «ciento». El 1.000 es «mil», no «un mil», pero el millón sí lleva «un»: un millón, dos millones.</p>
<p>Delante de un sustantivo masculino, <a href="{RAE_UNO}" rel="noopener">«uno» pierde la o</a>: un euro, veintiún euros, treinta y un
euros, doscientos un euros, y lo mismo delante de mil y de millones: veintiún mil, treinta y un millones. Cuando la cantidad
son millones justos, se intercala «de»: un millón de euros, tres millones de euros; pero «un millón doscientos mil euros», sin
«de», porque detrás del millón hay más cifras. Mil millones es un millardo, y un billón español son un millón de millones.</p>"""),
    ("Ejemplos", """
<ul>
<li>21 € · veintiún euros</li>
<li>101 € · ciento un euros</li>
<li>1.000.000 € · un millón de euros</li>
<li>2.021.001 € · dos millones veintiún mil un euros</li>
<li>15.300,05 € · quince mil trescientos euros con cinco céntimos</li>
<li>0,99 € · cero euros con noventa y nueve céntimos</li>
</ul>
<p>Los céntimos se escriben siempre en letras («con cincuenta céntimos»). En cheques de otros países a veces se escriben como
fracción («con 50/100»); en España no es necesario, pero tampoco es incorrecto.</p>"""),
]

FAQ = [
    ("¿Se escribe veintiún euros o veintiuno euros?",
     "Veintiún euros. Delante de un sustantivo masculino, uno y sus compuestos pierden la o: un euro, veintiún euros, cuarenta y un euros."),
    ("¿Es «un millón de euros» o «un millón euros»?",
     "Un millón de euros: con millones justos se pone «de». Si siguen más cifras no: un millón quinientos mil euros."),
    ("¿Cómo se escriben los céntimos en una factura?",
     "Con «con» y en letras: doscientos euros con cuarenta céntimos. Si son cero, basta con «doscientos euros»."),
    ("¿Se pone «un mil» o «mil»?",
     "Mil. «Un mil» no se usa en español en importes: 1.500 € son mil quinientos euros."),
    ("¿Qué vale si la cifra y la cantidad en letras no coinciden?",
     "En letras de cambio, cheques y pagarés prevalece la cantidad escrita en letras. En otros documentos depende del caso, por eso "
     "conviene que las dos coincidan."),
]

JS = r"""
function (v, H, C) {
  var U = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce', 'quince',
    'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve', 'veinte', 'veintiuno', 'veintidós', 'veintitrés', 'veinticuatro', 'veinticinco',
    'veintiséis', 'veintisiete', 'veintiocho', 'veintinueve'];
  var T = ['', '', '', 'treinta', 'cuarenta', 'cincuenta', 'sesenta', 'setenta', 'ochenta', 'noventa'];
  var C0 = ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'];
  function apo(s) { return s.replace(/uno$/, 'un').replace(/veintiun$/, 'veintiún'); }
  function w3(n, ap) {   /* 0 < n < 1000 */
    var c = Math.floor(n / 100), r = n % 100, out = [];
    if (c) out.push(n === 100 ? 'cien' : C0[c]);
    if (r) out.push(r < 30 ? U[r] : T[Math.floor(r / 10)] + (r % 10 ? ' y ' + U[r % 10] : ''));
    var s = out.join(' ');
    return ap ? apo(s) : s;
  }
  function w6(n, ap) {   /* 0 < n < 1e6 */
    var th = Math.floor(n / 1000), r = n % 1000, out = [];
    if (th) out.push(th === 1 ? 'mil' : w3(th, true) + ' mil');
    if (r) out.push(w3(r, ap));
    return out.join(' ');
  }
  function words(n, ap) {   /* integer 0 <= n < 1e15 */
    if (n === 0) return 'cero';
    var b = Math.floor(n / 1e12), m = Math.floor(n / 1e6) % 1e6, r = n % 1e6, out = [];
    if (b) out.push(b === 1 ? 'un billón' : w6(b, true) + ' billones');
    if (m) out.push(m === 1 ? 'un millón' : w6(m, true) + ' millones');
    if (r) out.push(w6(r, ap));
    return out.join(' ');
  }
  var s = String(v.cant).trim().replace(/\s|€/g, ''), neg = /^-/.test(s);
  s = s.replace(/^[-+]/, '');
  if (s.indexOf(',') >= 0) s = s.replace(/\./g, '').replace(',', '.');
  else if (/^\d{1,3}(\.\d{3})+$/.test(s)) s = s.replace(/\./g, '');
  if (!/^\d+(\.\d+)?$/.test(s)) return { err: 'Escribe una cifra, por ejemplo 1.234,50.' };
  var ip = s.split('.')[0].replace(/^0+(?=\d)/, ''), dp = s.split('.')[1] || '';
  if (ip.length > 15) return { err: 'Como mucho 999 billones.' };
  var n = +ip, txt, fig;
  if (v.modo === 'eur') {
    var cents = Math.round(+('0.' + (dp || '0')) * 100);
    if (cents === 100) { n += 1; cents = 0; }
    txt = words(n, true) + (n && n % 1e6 === 0 ? ' de' : '') + (n === 1 ? ' euro' : ' euros');
    if (cents) txt += ' con ' + words(cents, true) + (cents === 1 ? ' céntimo' : ' céntimos');
    fig = H.eur(n + cents / 100);
  } else {
    txt = words(n, false);
    if (dp) txt += ' coma ' + (dp.match(/^0*/)[0].split('').map(function () { return 'cero'; }).concat(/[1-9]/.test(dp) ? [words(+dp.replace(/^0+/, ''), false)] : [])).join(' ');
    fig = H.num(+s, dp.length);
  }
  if (neg) txt = 'menos ' + txt;
  txt = txt.charAt(0).toUpperCase() + txt.slice(1);
  var up = txt.toUpperCase(), both = up + ' (' + (neg ? '−' : '') + fig + ')';
  function cp(t) {
    return '<button type="button" class="btn nl-c" data-t="' + H.esc(t) + '" onclick="var b=this;navigator.clipboard&&navigator.clipboard.writeText(b.getAttribute(\'data-t\')).then(function(){b.textContent=\'Copiado\'})">Copiar</button>';
  }
  return {
    label: 'En letras', html: '<p class="nl-w">' + H.esc(txt) + ' ' + cp(txt) + '</p>' +
      '<table class="tbl hrows"><tbody><tr><th scope="row">Mayúsculas</th><td>' + H.esc(up) + ' ' + cp(up) + '</td></tr>' +
      '<tr><th scope="row">Con la cifra</th><td>' + H.esc(both) + ' ' + cp(both) + '</td></tr></tbody></table>',
    n: { text: txt }
  };
}
"""

CSS = ".nl-w{font-size:1.35rem;font-weight:600;line-height:1.35;margin:4px 0 8px;max-width:760px}.nl-c{margin-left:6px;padding:2px 10px;font-size:13px;vertical-align:middle}"

TOOL = {
    "slug": "numeros-a-letras",
    "lang": "es",
    "cat": "texto",
    "icon": "abc",
    "order": 10,
    "name": "Números a letras",
    "k": "cantidad en letras euros cheque factura contrato importe escribir número",
    "title": "Convertir números a letras: euros y céntimos",
    "desc": "Escribe cualquier cantidad en letras para facturas, contratos y cheques: euros con céntimos, en mayúsculas o con la cifra entre paréntesis.",
    "h1": "Números a letras",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "cant", "type": "text", "label": "Cantidad", "value": "1.234,50", "w": "l", "maxlength": 24},
        {"id": "modo", "type": "seg", "label": "Como", "value": "eur", "options": [("eur", "Euros"), ("num", "Número")]},
    ],
    "js": JS,
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("RAE · Diccionario panhispánico de dudas: cardinales", RAE), ("RAE · DPD: uno", RAE_UNO),
                ("Ley 19/1985 Cambiaria y del Cheque, art. 7 (BOE)", "https://www.boe.es/buscar/act.php?id=BOE-A-1985-12978")],
    "related": ["factura-retencion-irpf", "precio-sin-iva", "iban-desde-ccc", "letra-dni-nie"],
    "tests": [
        ({"cant": "1.234,50"}, {"n.text": "Mil doscientos treinta y cuatro euros con cincuenta céntimos"}),
        ({"cant": "21"}, {"n.text": "Veintiún euros"}),
        ({"cant": "1000000"}, {"n.text": "Un millón de euros"}),
        ({"cant": "2.021.001,01"}, {"n.text": "Dos millones veintiún mil un euros con un céntimo"}),
        ({"cant": "3,05", "modo": "num"}, {"n.text": "Tres coma cero cinco"}),
        ({"cant": "abc"}, {"err": "Escribe una cifra, por ejemplo 1.234,50."}),
    ],
}
