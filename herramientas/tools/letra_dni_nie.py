"""Letra del DNI y del NIE: compute the control letter (number mod 23) or check a full DNI/NIE."""

INTERIOR = "https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/tramites-y-gestiones/dni/calculo-del-digito-de-control-del-nif-nie/"
RD1553 = "https://www.boe.es/buscar/act.php?id=BOE-A-2005-21163"
RD1065 = "https://www.boe.es/buscar/act.php?id=BOE-A-2007-15984"
LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"

BLOCKS = [
    ("Cómo se calcula la letra del DNI", f"""
<p>La letra del DNI es un <b>dígito de control</b>: se divide el número entre 23 y el resto, de 0 a 22, indica la letra en esta
tabla. El DNI 12345678 da resto 14 y le corresponde la <b>Z</b>: 12345678Z.</p>
<table class="tbl"><thead><tr><th>Resto</th>{"".join(f"<th>{i}</th>" for i in range(12))}</tr></thead>
<tbody><tr><th>Letra</th>{"".join(f"<td>{LETTERS[i]}</td>" for i in range(12))}</tr></tbody></table>
<table class="tbl"><thead><tr><th>Resto</th>{"".join(f"<th>{i}</th>" for i in range(12, 23))}</tr></thead>
<tbody><tr><th>Letra</th>{"".join(f"<td>{LETTERS[i]}</td>" for i in range(12, 23))}</tr></tbody></table>
<p>Faltan a propósito la I, la Ñ, la O y la U, para que no se confundan con otros caracteres. Es el algoritmo que publica el
<a href="{INTERIOR}" rel="noopener">Ministerio del Interior</a>; la misma letra es la del NIF de la persona en Hacienda.</p>"""),
    ("NIE de extranjeros y NIF especiales", f"""
<p>El NIE empieza por X, Y o Z, seguidas de siete cifras y la letra. Para calcular la letra se sustituye la inicial por un
número (X = 0, Y = 1, Z = 2) y se aplica la misma división entre 23. Ejemplo: Y1234567 se calcula como 11234567, que da resto
10, letra <b>X</b>: Y1234567X. Los NIE con X se asignaron hasta julio de 2008; desde entonces se reparten con Y y, cuando se
agoten, con Z.</p>
<p>Hay además NIF de personas físicas que empiezan por K (españoles menores de 14 años sin DNI), L (españoles residentes en el
extranjero sin DNI) y M (extranjeros sin NIE), regulados en el <a href="{RD1065}#a20" rel="noopener">Real Decreto 1065/2007</a>.
Su letra final se calcula sobre las siete cifras, igual que la del DNI. La calculadora también los reconoce.</p>
<p>Un DNI con la letra correcta no significa que exista ni que sea de quien lo da: solo que está bien escrito. Sirve para
detectar errores al teclear un formulario, una factura o un contrato.</p>"""),
]

FAQ = [
    ("¿Cómo sé si un DNI es correcto?",
     "Escríbelo con su letra: si la letra coincide con la que sale de dividir el número entre 23, está bien escrito. Si no, alguna cifra "
     "o la letra están mal."),
    ("¿Por qué el DNI no tiene la letra I, Ñ, O ni U?",
     "Se quitaron de la tabla para evitar confusiones con el 1, el 0 y la N y la V al leerlos o escribirlos a mano."),
    ("¿Qué hago si mi DNI tiene menos de 8 cifras?",
     "Se completa con ceros a la izquierda: el DNI 1234567 es el 01234567. La letra no cambia."),
    ("¿La letra del NIE se calcula igual?",
     "Sí, cambiando la X por 0, la Y por 1 o la Z por 2 delante de las siete cifras y dividiendo entre 23."),
    ("¿Es lo mismo DNI que NIF?",
     "Para las personas españolas, el NIF es el número del DNI con su letra. El de empresas y otras entidades (lo que antes era el CIF) "
     "tiene otro formato: compruébalo en la utilidad de validar CIF."),
]

JS = r"""
function (v, H, C) {
  var L = 'TRWAGMYFPDXBNJZSQVHLCKE';
  var s = String(v.doc).toUpperCase().replace(/[\s.\-]/g, '');
  if (!s) return { err: 'Escribe el número del DNI o del NIE.' };
  var m = /^([XYZKLM]?)(\d{1,8})([A-Z]?)$/.exec(s);
  if (!m) return { err: 'Formato: 12345678Z, X1234567L o solo las cifras.' };
  var pre = m[1], digits = m[2], given = m[3], kind = 'DNI';
  if (pre) {
    if (digits.length > 7) return { err: 'Tras la letra inicial van 7 cifras.' };
    digits = ('0000000' + digits).slice(-7);
    kind = 'XYZ'.indexOf(pre) >= 0 ? 'NIE' : 'NIF ' + pre;
  } else digits = ('00000000' + digits).slice(-8);
  var num = +(('XYZ'.indexOf(pre) >= 0 ? 'XYZ'.indexOf(pre) : '') + digits), r = num % 23, letter = L.charAt(r), full = pre + digits + letter;
  var ok = !given || given === letter;
  return {
    label: given ? (ok ? kind + ' correcto' : kind + ' incorrecto') : 'Letra del ' + kind, big: given && !ok ? given + ' ✗' : letter,
    sub: given ? (ok ? full : 'La letra debería ser ' + letter + ': ' + full) : full,
    rows: [['Número', (pre ? pre + ' = ' + ('XYZ'.indexOf(pre) >= 0 ? 'XYZ'.indexOf(pre) : '—') + ' · ' : '') + H.num(num, 0)], ['Resto de ÷ 23', String(r)], ['Letra', letter, 'tot']],
    n: { letter: letter, ok: ok, full: full }
  };
}
"""

TOOL = {
    "slug": "letra-dni-nie",
    "lang": "es",
    "cat": "tramites",
    "icon": "id",
    "order": 10,
    "name": "Letra del DNI",
    "k": "calcular letra dni nie nif validar comprobar módulo 23 extranjero",
    "title": "Calcular la letra del DNI y del NIE, y validarlo",
    "desc": "Calcula la letra del DNI o del NIE a partir del número, o comprueba si un DNI o NIE completo está bien escrito. Con el método del módulo 23 explicado.",
    "h1": "Calcular la letra del DNI o del NIE",
    "updated": "2026-11-12",
    "inputs": [{"id": "doc", "type": "text", "label": "DNI o NIE", "value": "12345678", "maxlength": 14, "placeholder": "12345678 o X1234567"}],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Ministerio del Interior · Cálculo del dígito de control del NIF/NIE", INTERIOR),
                ("Real Decreto 1553/2005, del DNI (BOE)", RD1553), ("Real Decreto 1065/2007, arts. 18-20 (NIF)", RD1065)],
    "related": ["validar-cif-nif", "iban-desde-ccc", "numeros-a-letras"],
    "tests": [
        ({"doc": "12345678"}, {"n.letter": "Z"}),
        ({"doc": "12345678-A"}, {"n.ok": False, "n.full": "12345678Z"}),
        ({"doc": "x1234567l"}, {"n.ok": True}),
        ({"doc": "Y1234567"}, {"n.letter": "X", "n.full": "Y1234567X"}),
        ({"doc": "1234567"}, {"n.full": "01234567L"}),
        ({"doc": "ABC"}, {"err": "Formato: 12345678Z, X1234567L o solo las cifras."}),
    ],
}
