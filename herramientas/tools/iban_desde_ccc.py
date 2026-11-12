"""IBAN desde CCC: compute a Spanish IBAN from the 20-digit account number (CCC) and validate both (ISO 13616, mod 97-10)."""

BDE = "https://www.bde.es/wbe/es/entidades-profesionales/supervisadas/"
SEPA = "https://www.ecb.europa.eu/paym/integration/retail/sepa/html/index.en.html"
SWIFT = "https://www.swift.com/standards/data-standards/iban-international-bank-account-number"
BANKS = {"0049": "Banco Santander", "0182": "BBVA", "2100": "CaixaBank", "0081": "Banco Sabadell", "0128": "Bankinter",
         "2080": "Abanca", "1465": "ING", "0073": "Openbank", "3058": "Cajamar", "2085": "Ibercaja", "2095": "Kutxabank",
         "2103": "Unicaja", "0019": "Deutsche Bank", "0061": "Banca March", "1491": "Triodos Bank", "3035": "Laboral Kutxa",
         "0237": "Cajasur", "0239": "EVO Banco", "0216": "Targobank", "0186": "Banco Mediolanum", "3025": "Caja de Ingenieros",
         "0083": "Renta 4 Banco", "0075": "Banco Popular (hoy Santander)", "0030": "Banesto (hoy Santander)",
         "2038": "Bankia (hoy CaixaBank)", "2048": "Liberbank (hoy Unicaja)"}

BLOCKS = [
    ("Del número de cuenta al IBAN", """
<p>El IBAN español tiene 24 caracteres: <b>ES</b>, dos dígitos de control y los 20 dígitos de la cuenta de siempre (el CCC).
Para pasar de uno a otro solo hay que calcular esos dos dígitos. Con la cuenta 2100 0418 45 0200051332 el IBAN es
<b>ES91 2100 0418 4502 0005 1332</b>. Se escribe en grupos de cuatro en papel y sin espacios en los formularios.</p>
<p>Los 20 dígitos del CCC se dividen en cuatro partes: <b>entidad</b> (4 cifras, el banco), <b>oficina</b> (4), <b>dígitos de
control</b> (2) y <b>número de cuenta</b> (10). Los dígitos de control del CCC son anteriores al IBAN y siguen existiendo: el
primero comprueba entidad y oficina y el segundo, el número de cuenta. La calculadora revisa los dos y, si el IBAN es correcto
pero el CCC interno no, también te lo dice.</p>"""),
    ("Cómo se calculan los dígitos de control", """
<p><b>IBAN</b> (norma ISO 13616, método mod 97-10): se pone la cuenta delante y «ES00» detrás, se cambian las letras por números
(E = 14, S = 28), se divide ese número de 26 cifras entre 97 y el control es 98 menos el resto. En el ejemplo,
21000418450200051332142800 entre 97 da resto 7 y el control es 98 − 7 = 91. Un IBAN es válido cuando, al hacer la misma
operación con su control, el resto es 1. Así se detecta cualquier cifra cambiada y casi cualquier par de cifras intercambiado.</p>
<p><b>CCC</b> (módulo 11): cada cifra se multiplica por un peso (1, 2, 4, 8, 5, 10, 9, 7, 3, 6), se suman los productos y el
dígito es 11 menos el resto de dividir entre 11; si sale 11 se pone 0 y si sale 10 se pone 1. El primero se calcula sobre «00»
seguido de entidad y oficina; el segundo, sobre los 10 dígitos del número de cuenta.</p>
<p>Un IBAN bien formado no garantiza que la cuenta exista ni quién es el titular. El nombre del banco sale del código de
entidad; si el banco se fusionó con otro, la cuenta sigue funcionando con el código antiguo.</p>"""),
]

FAQ = [
    ("¿Cómo saco el IBAN de mi número de cuenta?",
     "Escribe los 20 dígitos de la cuenta: la calculadora añade ES y los dos dígitos de control. El IBAN también aparece en la app de "
     "tu banco y en cualquier recibo domiciliado."),
    ("¿Cuántos dígitos tiene un IBAN español?",
     "24 caracteres: ES, 2 dígitos de control y los 20 dígitos de la cuenta (entidad, oficina, control y número)."),
    ("¿El IBAN y el BIC son lo mismo?",
     "No. El IBAN identifica la cuenta; el BIC o SWIFT identifica al banco. Para transferencias en euros dentro de la zona SEPA basta el IBAN."),
    ("¿Qué banco es mi IBAN?",
     "Lo indican las cuatro cifras que siguen al control: 2100 es CaixaBank, 0049 Santander, 0182 BBVA, 0081 Sabadell, 1465 ING."),
    ("Si el IBAN es válido, ¿la transferencia llegará?",
     "Solo si además la cuenta existe y está abierta. La validación detecta errores al teclear, no confirma la cuenta ni el titular."),
]

JS = r"""
function (v, H, C) {
  var W = [1, 2, 4, 8, 5, 10, 9, 7, 3, 6];
  function dc(s) { var t = 0; for (var i = 0; i < 10; i++) t += +s.charAt(i) * W[i]; var d = 11 - t % 11; return d === 11 ? 0 : d === 10 ? 1 : d; }
  function mod97(s) { var r = 0; for (var i = 0; i < s.length; i++) r = (r * 10 + +s.charAt(i)) % 97; return r; }
  function grp(s) { return s.replace(/(.{4})/g, '$1 ').trim(); }
  var s = String(v.cuenta).toUpperCase().replace(/[\s.\-]/g, ''), given = null;
  if (!s) return { err: 'Escribe los 20 dígitos de la cuenta o el IBAN.' };
  if (/^ES\d{22}$/.test(s)) { given = s.slice(2, 4); s = s.slice(4); }
  else if (/^[A-Z]{2}/.test(s)) return { err: 'Solo IBAN españoles (ES + 22 cifras).' };
  if (!/^\d{20}$/.test(s)) return { err: 'El CCC tiene 20 dígitos (' + s.replace(/\D/g, '').length + ' escritos).' };
  var ent = s.slice(0, 4), ofi = s.slice(4, 8), d = s.slice(8, 10), acc = s.slice(10);
  var d1 = dc('00' + ent + ofi), d2 = dc(acc), ccOk = d === '' + d1 + d2;
  var chk = 98 - mod97(s + '142800'), ck = (chk < 10 ? '0' : '') + chk, iban = 'ES' + ck + s;
  var ibOk = given === null ? null : given === ck, bank = C.d.banks[ent] || 'Entidad ' + ent;
  var label = given === null ? 'IBAN' : ibOk ? (ccOk ? 'IBAN correcto' : 'IBAN correcto, CCC con error') : 'IBAN incorrecto';
  var sub = H.esc(bank) + (given !== null && !ibOk ? ' · el control debería ser ' + ck : '') + (!ccOk ? ' · los dígitos de control del CCC deberían ser ' + d1 + d2 : '');
  return {
    label: label, big: given !== null && !ibOk ? 'ES' + given + ' ✗' : grp(iban), sub: sub,
    rows: [['Electrónico', iban], ['Entidad', ent + ' · ' + H.esc(bank)], ['Oficina', ofi], ['Control CCC', d + (ccOk ? ' ✓' : ' ✗ (' + d1 + d2 + ')')],
      ['Cuenta', acc], ['Control IBAN', ck, 'tot']],
    n: { iban: iban, ccOk: ccOk, ibOk: ibOk }
  };
}
"""

TOOL = {
    "slug": "iban-desde-ccc",
    "lang": "es",
    "cat": "tramites",
    "icon": "building-bank",
    "order": 30,
    "name": "Calcular IBAN",
    "k": "iban ccc número de cuenta validar comprobar es dígitos de control banco entidad",
    "title": "Calcular el IBAN desde el número de cuenta y validarlo",
    "desc": "Calcula el IBAN español a partir de los 20 dígitos de la cuenta (CCC) o comprueba si un IBAN es correcto. Con banco, oficina y dígitos de control.",
    "h1": "Calcular y validar un IBAN español",
    "updated": "2026-11-12",
    "data": {"banks": BANKS},
    "inputs": [{"id": "cuenta", "type": "text", "label": "Cuenta o IBAN", "value": "2100 0418 45 0200051332", "w": "xl", "maxlength": 34,
                "placeholder": "2100 0418 45 0200051332"}],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("SWIFT · IBAN (ISO 13616), registro oficial", SWIFT), ("Banco Central Europeo · SEPA", SEPA),
                ("Banco de España · Entidades supervisadas", BDE)],
    "related": ["validar-cif-nif", "letra-dni-nie", "factura-retencion-irpf"],
    "tests": [
        ({"cuenta": "2100 0418 45 0200051332"}, {"n.iban": "ES9121000418450200051332", "n.ccOk": True}),
        ({"cuenta": "ES91 2100 0418 4502 0005 1332"}, {"n.ibOk": True, "n.ccOk": True}),
        ({"cuenta": "ES92 2100 0418 4502 0005 1332"}, {"n.ibOk": False}),
        ({"cuenta": "21000418460200051332"}, {"n.ccOk": False}),
        ({"cuenta": "1234"}, {"err": "El CCC tiene 20 dígitos (4 escritos)."}),
        ({"cuenta": "DE89370400440532013000"}, {"err": "Solo IBAN españoles (ES + 22 cifras)."}),
    ],
}
