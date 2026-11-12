"""Validar CIF / NIF de empresas: control character of a legal-entity NIF (Orden EHA/451/2008) and its legal form."""

EHA = "https://www.boe.es/buscar/act.php?id=BOE-A-2008-3580"
RD1065 = "https://www.boe.es/buscar/act.php?id=BOE-A-2007-15984"
CENSO = "https://sede.agenciatributaria.gob.es/Sede/censos-nif-domicilio-fiscal.html"
FORMS = {"A": "Sociedad anónima", "B": "Sociedad de responsabilidad limitada", "C": "Sociedad colectiva", "D": "Sociedad comanditaria",
         "E": "Comunidad de bienes o herencia yacente", "F": "Sociedad cooperativa", "G": "Asociación o fundación",
         "H": "Comunidad de propietarios", "J": "Sociedad civil", "N": "Entidad extranjera", "P": "Corporación local",
         "Q": "Organismo público", "R": "Congregación o institución religiosa", "S": "Órgano de la Administración del Estado o de una comunidad",
         "U": "Unión temporal de empresas", "V": "Otro tipo de entidad", "W": "Establecimiento permanente de entidad no residente"}

BLOCKS = [
    ("Cómo se comprueba un CIF", f"""
<p>El antiguo CIF, hoy <b>NIF de personas jurídicas y entidades</b>, tiene nueve caracteres: una letra que indica la forma
jurídica, siete cifras y un carácter de control, que puede ser una cifra o una letra. El control se calcula con las siete
cifras centrales, así que un error al copiar casi siempre se detecta. Ejemplo: en B12345674, la B indica una sociedad
limitada, las cifras son 1234567 y el control correcto es 4.</p>
<p>El cálculo es este. Se suman las cifras en posición par (2.ª, 4.ª y 6.ª): 2 + 4 + 6 = 12. Cada cifra en posición impar (1.ª,
3.ª, 5.ª y 7.ª) se multiplica por 2 y se suman las cifras del resultado: 1 → 2; 3 → 6; 5 → 10 → 1 + 0 = 1; 7 → 14 → 1 + 4 = 5;
en total 14. La suma es 26, su última cifra es 6 y el control es 10 − 6 = <b>4</b> (si la última cifra es 0, el control es 0).
Cuando el control va en letra, se usa la tabla J A B C D E F G H I para 0 a 9: aquí sería la D.</p>"""),
    ("¿Cifra o letra al final?", f"""
<p>Depende de la letra inicial. Las sociedades anónimas y limitadas (A, B), las comunidades de bienes (E) y las comunidades de
propietarios (H) llevan siempre una <b>cifra</b>. Las entidades extranjeras (N), corporaciones locales (P), organismos públicos (Q),
congregaciones religiosas (R), órganos de la Administración (S) y establecimientos permanentes (W) llevan siempre una
<b>letra</b>. El resto puede llevar cualquiera de las dos. La calculadora aplica estas reglas y te dice cuál toca.</p>
<p>Las letras de la forma jurídica son las de la <a href="{EHA}" rel="noopener">Orden EHA/451/2008</a>, que sustituyó en 2008 al
antiguo CIF. Desde entonces el número es aleatorio y ya no indica la provincia. El NIF de las personas físicas (DNI y NIE) se
comprueba de otra manera, con la letra del módulo 23; si escribes uno aquí, la calculadora lo comprueba también.</p>
<p>Que el control cuadre solo prueba que el número está bien formado. Para saber si una empresa existe y a qué nombre está,
consulta el <a href="{CENSO}" rel="noopener">censo de la Agencia Tributaria</a> o el Registro Mercantil.</p>"""),
]

FAQ = [
    ("¿Es lo mismo CIF que NIF?",
     "Sí. Desde 2008 el CIF de las empresas se llama NIF de personas jurídicas, pero el formato es el mismo: letra, siete cifras y control."),
    ("¿Qué significa la letra B del CIF?",
     "Que es una sociedad de responsabilidad limitada (SL). La A es sociedad anónima, la G asociación, la H comunidad de propietarios y la "
     "J sociedad civil."),
    ("¿Por qué algunos CIF acaban en letra?",
     "Porque el carácter de control de organismos públicos, ayuntamientos, entidades religiosas o extranjeras se escribe con letra "
     "(J, A, B… I para 0 a 9). En las SL y SA siempre es una cifra."),
    ("¿Un CIF válido garantiza que la empresa existe?",
     "No. Solo indica que el número está bien construido. La existencia y la razón social se comprueban en la Agencia Tributaria o el "
     "Registro Mercantil."),
    ("¿Cómo pido un NIF para una empresa nueva?",
     "Con el modelo 036 en la Agencia Tributaria: primero se asigna un NIF provisional y, una vez inscrita la sociedad, el definitivo."),
]

JS = r"""
function (v, H, C) {
  var F = C.d.forms, LT = 'JABCDEFGHI', DL = 'TRWAGMYFPDXBNJZSQVHLCKE';
  var s = String(v.nif).toUpperCase().replace(/[\s.\-\/]/g, '');
  if (!s) return { err: 'Escribe el CIF o NIF.' };
  var p = /^([XYZKLM]?)(\d{7,8})([A-Z])$/.exec(s);
  if (p && (p[1] ? p[2].length === 7 : p[2].length === 8)) {   /* a person: DNI / NIE / K L M */
    var x = +(('XYZ'.indexOf(p[1]) >= 0 ? 'XYZ'.indexOf(p[1]) : '') + p[2]), good = DL.charAt(x % 23), ok0 = good === p[3];
    return { label: ok0 ? 'NIF de persona física correcto' : 'NIF de persona física incorrecto', big: ok0 ? 'Correcto' : 'Incorrecto',
      sub: ok0 ? s : 'La letra debería ser ' + good + ': ' + p[1] + p[2] + good, n: { ok: ok0, expect: good } };
  }
  var m = /^([A-HJ-NP-SUVW])(\d{7})([0-9A-J])?$/.exec(s);
  if (!m) return { err: 'Formato: letra, 7 cifras y control (B12345674).' };
  var d = m[2], even = 0, odd = 0;
  for (var i = 0; i < 7; i++) {
    var n = +d.charAt(i);
    if (i % 2) even += n; else { var t = 2 * n; odd += Math.floor(t / 10) + t % 10; }
  }
  var c = (10 - (even + odd) % 10) % 10, L = m[1];
  var mode = 'ABEH'.indexOf(L) >= 0 ? 'num' : 'KNPQRSW'.indexOf(L) >= 0 || d.slice(0, 2) === '00' ? 'let' : 'any';
  var want = mode === 'num' ? String(c) : mode === 'let' ? LT.charAt(c) : c + ' o ' + LT.charAt(c), got = m[3] || '';
  var ok = got ? (mode !== 'let' && got === String(c)) || (mode !== 'num' && got === LT.charAt(c)) : null;
  var full = L + d + (mode === 'let' ? LT.charAt(c) : String(c));
  return {
    label: got ? (ok ? 'CIF correcto' : 'CIF incorrecto') : 'Carácter de control', big: got ? (ok ? 'Correcto' : 'Incorrecto') : want,
    sub: H.esc(F[L] || 'Forma jurídica desconocida') + (got && !ok ? ' · el control debería ser ' + want : got ? '' : ' · ' + full),
    rows: [['Letra ' + L, H.esc(F[L] || '—')], ['Suma posiciones pares', String(even)], ['Suma posiciones impares ×2', String(odd)],
      ['Control', want, 'tot']],
    n: { ok: ok, control: want, form: F[L] || '' }
  };
}
"""

TOOL = {
    "slug": "validar-cif-nif",
    "lang": "es",
    "cat": "tramites",
    "icon": "building",
    "order": 20,
    "name": "Validar CIF",
    "k": "comprobar cif nif empresa sociedad dígito de control letra forma jurídica",
    "title": "Validar CIF online: comprobar el NIF de una empresa",
    "desc": "Comprueba si un CIF o NIF de empresa es correcto, calcula su dígito de control y descubre la forma jurídica por la letra: SL, SA, asociación…",
    "h1": "Validar un CIF o NIF de empresa",
    "updated": "2026-11-12",
    "data": {"forms": FORMS},
    "inputs": [{"id": "nif", "type": "text", "label": "CIF o NIF", "value": "B12345674", "maxlength": 14, "placeholder": "B12345674"}],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Orden EHA/451/2008, NIF de personas jurídicas (BOE)", EHA), ("Real Decreto 1065/2007, arts. 18-23 (BOE)", RD1065),
                ("Agencia Tributaria · Censos, NIF y domicilio fiscal", CENSO)],
    "related": ["letra-dni-nie", "iban-desde-ccc", "factura-retencion-irpf"],
    "tests": [
        ({"nif": "B12345674"}, {"n.ok": True, "n.form": "Sociedad de responsabilidad limitada"}),
        ({"nif": "B12345675"}, {"n.ok": False, "n.control": "4"}),
        ({"nif": "P1234567D"}, {"n.ok": True}),
        ({"nif": "Q1234567"}, {"n.control": "D", "n.ok": None}),
        ({"nif": "12345678Z"}, {"n.ok": True}),
        ({"nif": "B123"}, {"err": "Formato: letra, 7 cifras y control (B12345674)."}),
    ],
}
