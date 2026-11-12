"""Amigo invisible: a client-side Secret Santa draw with exclusions; every person gets a private link that reveals
only their own match (obfuscated in the URL, no server, no e-mail)."""

FAQ = [
    ("¿El organizador puede ver a quién le toca cada uno?",
     "No a simple vista: la página no muestra el resultado del sorteo, solo un enlace por persona, y el nombre de quien te toca va "
     "codificado dentro del enlace. Si el organizador también participa, que no abra los enlaces de los demás y ya está: el suyo "
     "le dice lo mismo que a todos, solo a quién regala él."),
    ("¿Cómo evito que a una pareja le toque regalarse entre sí?",
     "Escríbela en «Exclusiones» como Ana-Luis. La exclusión vale en los dos sentidos: ni Ana regala a Luis ni Luis a Ana. Puedes "
     "poner varias separadas por comas: Ana-Luis, Marta-Pedro."),
    ("¿Qué pasa si cambio un nombre después de mandar los enlaces?",
     "El sorteo se vuelve a hacer y los enlaces nuevos ya no casan con los antiguos. Cierra la lista antes de enviar nada y manda "
     "todos los enlaces del mismo sorteo; si te equivocas, vuelve a mandarlos todos."),
    ("¿Se guardan los nombres en algún sitio?",
     "No. El sorteo se hace en tu navegador y no hay servidor, registro ni correos: cada enlace lleva dentro su propio resultado. "
     "Por eso funciona aunque cierres la página o la recargues."),
    ("¿Qué es «Un solo círculo»?",
     "Con esa opción el sorteo forma una cadena única: Ana regala a Marta, Marta a Pedro, Pedro a Luis y Luis a Ana. Así nunca "
     "quedan dos personas regalándose mutuamente, y el día de la entrega se puede ir abriendo en orden."),
]

BLOCKS = [
    ("Cómo se hace el sorteo", """
<p>Escribe los nombres separados por comas y, si hace falta, las parejas que no deben tocarse entre sí. El sorteo sale al
momento: verás una fila por persona con su <b>enlace privado</b>, un botón para copiarlo y otro para mandarlo por WhatsApp.
Cada persona abre su enlace y ve solo a quién le toca regalar, con el presupuesto y la fecha de la entrega si los has puesto.
Nadie tiene que registrarse ni dar su correo.</p>
<p>El resultado viaja dentro del propio enlace, codificado para que no se lea de un vistazo ni aparezca en la vista previa del
chat. Por eso no hace falta guardar nada: el enlace funciona aunque cierres la página. Lo único que conviene es mandar todos
los enlaces del mismo sorteo, porque si cambias la lista o recargas la página se hace un sorteo nuevo.</p>"""),
    ("Un ejemplo", """
<p>Cinco compañeros de oficina, Ana, Luis, Marta, Pedro y Sara, con un presupuesto de 20 € y entrega el viernes 18 de diciembre.
Ana y Luis son pareja, así que se escribe la exclusión <code>Ana-Luis</code>. El sorteo da, por ejemplo: Ana regala a Pedro,
Luis a Sara, Marta a Ana, Pedro a Luis y Sara a Marta. Ana recibe un enlace que al abrirlo dice «Hola, Ana» y, tras pulsar «Ver»,
«Pedro · 20 € · 18 de diciembre». Ni Ana ni el organizador ven el resto de parejas.</p>
<p>Con muchas exclusiones puede no haber reparto posible: tres personas en las que una no puede regalar a ninguna de las otras
dos, por ejemplo. En ese caso la herramienta lo avisa en lugar de saltarse una exclusión.</p>"""),
    ("Cómo funciona por dentro", """
<p>El programa prueba repartos al azar hasta encontrar uno en el que nadie se regala a sí mismo y se respetan todas las
exclusiones (en matemáticas, un <i>desarreglo</i> con restricciones). Si no existe ninguno, revisa todas las combinaciones antes
de decir que es imposible, así que el aviso es fiable. El azar sale del generador criptográfico del navegador: dos sorteos con
los mismos nombres dan resultados distintos.</p>
<p>Si quieres repetir exactamente un sorteo (para un grupo que lo hace cada año, o para comprobarlo), escribe un número en
«Nº de sorteo» dentro de «Más opciones»: con los mismos nombres, exclusiones y número, el reparto es siempre el mismo.
Cualquiera que conozca los tres datos podría rehacerlo, así que úsalo solo si os fiáis.</p>"""),
]

JS = r"""
function (v, H, C) {
  var MON = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  var KEY = 'amigo-invisible·elcalendariolaboral';
  function fdate(s) { var d = H.parse(s); return d ? d.getUTCDate() + ' de ' + MON[d.getUTCMonth()] + ' de ' + d.getUTCFullYear() : ''; }
  function enc(s, salt) {
    var b = unescape(encodeURIComponent(s)), o = String.fromCharCode(salt);
    for (var i = 0; i < b.length; i++) o += String.fromCharCode(b.charCodeAt(i) ^ KEY.charCodeAt((i + salt) % KEY.length) ^ ((salt * (i + 7)) & 255));
    return btoa(o).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
  function dec(c) {
    try {
      var b = atob(c.replace(/-/g, '+').replace(/_/g, '/')), salt = b.charCodeAt(0), o = '';
      for (var i = 1; i < b.length; i++) o += String.fromCharCode(b.charCodeAt(i) ^ KEY.charCodeAt((i - 1 + salt) % KEY.length) ^ ((salt * (i + 6)) & 255));
      var x = JSON.parse(decodeURIComponent(escape(o)));
      return x && typeof x[0] === 'string' && typeof x[1] === 'string' ? x : null;
    } catch (e) { return null; }
  }
  var code = String(v.r || '').trim().replace(/^.*[?&]r=/, '');
  if (code) {   /* a participant opened their private link */
    var x = dec(code);
    if (!x) return { err: 'Este enlace no es válido: pide al organizador que te lo vuelva a mandar.' };
    var info = [x[2] ? H.eur(+x[2]).replace(',00', '') : '', x[3] ? fdate(x[3]) : ''].filter(Boolean).join(' · ');
    return {
      html: '<style>#hform{display:none}</style><div class="ai-r"><p class="ai-hi">Hola, <b>' + H.esc(x[0]) + '</b></p>' +
        (x[4] ? '<p class="ai-ev">' + H.esc(x[4]) + '</p>' : '') +
        '<details class="ai-d"><summary class="btn p">Ver a quién regalas</summary><p class="ai-n">' + H.esc(x[1]) + '</p>' +
        (info ? '<p class="ai-i">' + info + '</p>' : '') + '</details><p class="ai-o"><a href="./">Organizar otro sorteo</a></p></div>',
      n: { giver: x[0], to: x[1] }
    };
  }
  var names = String(v.nombres).split(/[,;\n]+/).map(function (s) { return s.trim().replace(/\s+/g, ' '); }).filter(Boolean);
  var low = names.map(function (s) { return s.toLowerCase(); }), N = names.length;
  if (N < 3) return { err: 'Escribe al menos 3 nombres separados por comas.' };
  if (N > 60) return { err: 'Como mucho 60 personas.' };
  for (var i = 0; i < N; i++) {
    if (names[i].length > 40) return { err: 'Nombre demasiado largo: ' + H.esc(names[i].slice(0, 40)) + '…' };
    if (low.indexOf(low[i]) !== i) return { err: 'Nombre repetido: ' + H.esc(names[i]) + '. Añade la inicial del apellido.' };
  }
  var ban = names.map(function () { return {}; });
  var items = String(v.excl).split(/[,;\n]+/).map(function (s) { return s.trim(); }).filter(Boolean);
  for (var k = 0; k < items.length; k++) {
    var pair = null, seps = ['/', '+', ' y ', '-', '–'], it = items[k].toLowerCase();
    for (var s = 0; s < seps.length && !pair; s++) {   /* any split point: names may contain hyphens (José-Luis) */
      for (var at = it.indexOf(seps[s]); at > 0 && !pair; at = it.indexOf(seps[s], at + 1)) {
        var p = [low.indexOf(it.slice(0, at).trim()), low.indexOf(it.slice(at + seps[s].length).trim())];
        if (p[0] >= 0 && p[1] >= 0 && p[0] !== p[1]) pair = p;
      }
    }
    if (!pair) return { err: 'Exclusión «' + H.esc(items[k]) + '»: escribe Nombre-Nombre con nombres de la lista.' };
    ban[pair[0]][pair[1]] = ban[pair[1]][pair[0]] = 1;
  }
  /* randomness: crypto per page load, or the fixed draw number */
  var seedStr = low.join('|') + '#' + items.join('|').toLowerCase() + '#' + (v.circ ? 'c' : 'f') + '#';
  if (v.sorteo >= 0) seedStr += 'n' + v.sorteo;
  else {
    if (!H._ai) {
      var a = new Uint32Array(2);
      if (typeof crypto !== 'undefined' && crypto.getRandomValues) crypto.getRandomValues(a); else { a[0] = Math.random() * 4294967296; a[1] = Date.now(); }
      H._ai = a[0] + '.' + a[1];
    }
    seedStr += H._ai;
  }
  var h = 2166136261;
  for (i = 0; i < seedStr.length; i++) { h ^= seedStr.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
  function rnd() { h = (h + 0x6D2B79F5) >>> 0; var t = h; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
  function shuffled(n) { var o = []; for (var q = 0; q < n; q++) o.push(q); for (q = n - 1; q > 0; q--) { var j = Math.floor(rnd() * (q + 1)), tmp = o[q]; o[q] = o[j]; o[j] = tmp; } return o; }
  function ok(g, r) { return g !== r && !ban[g][r]; }
  var to = [], used = {}, steps = 0, order = shuffled(N), cap = 2e6;
  function free(k) {   /* giver order[k] picks among unused allowed receivers */
    if (k === N) return true;
    if (++steps > cap) return false;
    var g = order[k], c = shuffled(N);
    for (var q = 0; q < N; q++) if (!used[c[q]] && ok(g, c[q])) { used[c[q]] = 1; to[g] = c[q]; if (free(k + 1)) return true; used[c[q]] = 0; }
    return false;
  }
  function circle(path) {   /* one Hamiltonian cycle through every person */
    var last = path[path.length - 1];
    if (path.length === N) return ok(last, path[0]);
    if (++steps > cap) return false;
    var c = shuffled(N);
    for (var q = 0; q < N; q++) if (!used[c[q]] && ok(last, c[q])) { used[c[q]] = 1; path.push(c[q]); if (circle(path)) return true; path.pop(); used[c[q]] = 0; }
    return false;
  }
  var found;
  if (v.circ) {
    var start = order[0], path = [start]; used[start] = 1;
    found = circle(path);
    if (found) for (i = 0; i < N; i++) to[path[i]] = path[(i + 1) % N];
  } else found = free(0);
  if (!found) return { err: steps > cap ? 'Demasiadas exclusiones para resolverlo: quita alguna.' : 'Con esas exclusiones no hay reparto posible: quita alguna.' };
  var budget = v.pres > 0 ? H.r2(v.pres) : '', date = v.fecha ? H.iso(v.fecha) : '', ev = String(v.evento || '').trim().slice(0, 60);
  var base = typeof location !== 'undefined' && /^https?:/.test(location.protocol) ? location.origin + location.pathname : 'https://elcalendariolaboral.es/utilidades/amigo-invisible/';
  var rows = '', links = [], valid = true;
  for (i = 0; i < N; i++) {
    if (!ok(i, to[i]) || to.indexOf(to[i]) !== i) valid = false;
    var url = base + '?r=' + enc(JSON.stringify([names[i], names[to[i]], budget, date, ev]), Math.floor(rnd() * 256));
    links.push(url);
    var msg = 'Hola, ' + names[i] + ': este es tu enlace del amigo invisible' + (ev ? ' (' + ev + ')' : '') + '. Ábrelo tú solo: ' + url;
    rows += '<tr><th scope="row">' + H.esc(names[i]) + '</th><td><input class="inp ai-u" readonly value="' + H.esc(url) + '" onfocus="this.select()" aria-label="Enlace de ' + H.esc(names[i]) + '"></td>' +
      '<td class="ai-b"><button type="button" class="btn" data-u="' + H.esc(url) + '" onclick="var b=this;navigator.clipboard&&navigator.clipboard.writeText(b.getAttribute(\'data-u\')).then(function(){b.textContent=\'Copiado\'})">Copiar</button> ' +
      '<a class="btn" href="https://wa.me/?text=' + encodeURIComponent(msg) + '" target="_blank" rel="noopener">WhatsApp</a></td></tr>';
  }
  var cyc = 0, seen = {};
  for (i = 0; i < N; i++) if (!seen[i]) { cyc++; for (var j = i; !seen[j]; j = to[j]) seen[j] = 1; }
  var sub = [N + ' personas', items.length ? items.length + ' ' + H.plural(items.length, 'exclusión', 'exclusiones') : '', budget ? H.eur(budget).replace(',00', '') : '', date ? fdate(date) : '']
    .filter(Boolean).join(' · ');
  return {
    label: 'Sorteo hecho', big: 'Enlaces listos', sub: sub,
    html: '<table class="tbl ai-t"><tbody>' + rows + '</tbody></table>',
    note: 'Cada enlace muestra solo a quién regala esa persona. Si cambias la lista o recargas la página, el sorteo se repite: manda todos los enlaces de una vez.',
    n: { count: N, valid: valid, cycles: cyc, first: dec(links[0].split('?r=')[1]) }
  };
}
"""

CSS = """
.ai-t th{white-space:nowrap}.ai-t td{vertical-align:middle}.ai-u{width:100%;min-width:9rem;font-size:.8rem}
.ai-b{white-space:nowrap;text-align:right}.ai-b .btn{margin:2px 0}
.ai-r{text-align:center;padding:1rem 0}.ai-hi{font-size:1.25rem}.ai-ev{color:var(--mut,#666)}
.ai-d summary{display:inline-block;cursor:pointer;list-style:none;margin:.75rem 0}.ai-d summary::-webkit-details-marker{display:none}
.ai-n{font-size:2.2rem;font-weight:700;margin:.5rem 0}.ai-i{font-size:1.05rem}.ai-o{margin-top:1.5rem;font-size:.9rem}
@media (max-width:560px){.ai-t tr{display:grid;grid-template-columns:1fr auto}.ai-t td:nth-child(2){grid-column:1/-1;grid-row:2}}
"""

TOOL = {
    "slug": "amigo-invisible",
    "lang": "es",
    "cat": "ocio",
    "icon": "gift",
    "order": 10,
    "name": "Amigo invisible",
    "k": "sorteo navidad regalos secret santa amigo secreto exclusiones whatsapp",
    "title": "Amigo invisible online: sorteo gratis con exclusiones",
    "desc": "Haz el sorteo del amigo invisible gratis y sin registro: exclusiones de parejas, presupuesto y un enlace privado por persona para mandar por WhatsApp.",
    "h1": "Sorteo de amigo invisible",
    "updated": "2026-11-12",
    "link": False,
    "inputs": [
        {"id": "nombres", "type": "text", "label": "Participantes", "value": "Ana, Luis, Marta, Pedro, Sara", "w": "xl",
         "placeholder": "Ana, Luis, Marta…"},
        {"id": "excl", "type": "text", "label": "Exclusiones", "value": "Ana-Luis", "w": "l", "placeholder": "Ana-Luis, Marta-Pedro"},
        {"id": "pres", "type": "money", "label": "Presupuesto", "value": 20, "w": "s"},
        {"id": "fecha", "type": "date", "label": "Entrega", "value": ""},
        {"id": "evento", "type": "text", "label": "Nombre del grupo", "value": "", "more": True, "maxlength": 60, "placeholder": "Oficina 2026"},
        {"id": "circ", "type": "check", "label": "Un solo círculo", "value": False, "more": True},
        {"id": "sorteo", "type": "number", "label": "Nº de sorteo", "value": "", "more": True, "w": "s"},
        {"id": "r", "type": "text", "label": "Código recibido", "value": "", "more": True, "w": "l"},
    ],
    "js": JS,
    "css": CSS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Desarreglos (permutaciones sin puntos fijos) · OEIS A000166", "https://oeis.org/A000166"),
                ("Web Crypto API: getRandomValues (W3C)", "https://www.w3.org/TR/WebCryptoAPI/#Crypto-method-getRandomValues")],
    "credits": [("Mulberry32 PRNG (Tommy Ettinger)", "dominio público (CC0)", "https://gist.github.com/tommyettinger/46a874533244883189143505d203312c")],
    "related": ["dividir-gastos", "loteria-navidad-premio-neto", "cuenta-atras", "cantidades-fiesta"],
    "tests": [
        ({"nombres": "Ana, Luis, Marta, Pedro", "excl": "Ana-Luis", "sorteo": "7"}, {"n.count": 4, "n.valid": True, "n.first.0": "Ana"}),
        ({"nombres": "Ana, Luis, Marta, Pedro, Sara", "excl": "", "sorteo": "3", "circ": "1"}, {"n.valid": True, "n.cycles": 1}),
        ({"nombres": "Ana, Luis, Marta", "excl": "Ana-Luis, Ana/Marta", "sorteo": "1"},
         {"err": "Con esas exclusiones no hay reparto posible: quita alguna."}),
        ({"nombres": "Ana, Luis, ana", "excl": ""}, {"err": "Nombre repetido: ana. Añade la inicial del apellido."}),
        ({"nombres": "José-Luis, Marta, Pedro, Sara", "excl": "José-Luis-Marta", "sorteo": "2"}, {"n.valid": True, "n.count": 4}),
        ({"r": "Id1GCUljye7B1R81WiLR5Yq-jW4GKsv8iqNpESjI54vIAy5YYomsgto"}, {"n.giver": "Ana", "n.to": "Sara"}),
    ],
}
