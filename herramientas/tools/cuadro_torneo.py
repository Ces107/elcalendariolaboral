"""Cuadro de torneo eliminatorio: standard seeding (1 v 16, 8 v 9...), byes to the top seeds, optional random draw and
third-place match, click a name to advance it (stored in the URL), printable. EN twin: tournament-bracket-generator."""
from herramientas.tools import _deporte as D

JS = r"""
(function () {
  /* click a player in a match to make them the winner: the choices live in the hidden 'g' field (one digit per match:
     0 none, 1 top, 2 bottom); a new choice clears the matches further down that path */
  if (typeof document !== 'undefined' && !window.__ctClicks) {
    window.__ctClicks = 1;
    document.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('.ct-p[data-m]') : null;
      if (!b) return;
      var box = document.getElementById('g'), m = +b.getAttribute('data-m'), s = b.getAttribute('data-s'), tot = +b.getAttribute('data-t');
      var g = (box.value || '').replace(/[^012]/g, '').split('');
      while (g.length < tot) g.push('0');
      g[m] = g[m] === s ? '0' : s;
      (b.getAttribute('data-d') || '').split(',').forEach(function (k) { if (k !== '') g[+k] = '0'; });
      box.value = g.join('').replace(/0+$/, '');
      box.dispatchEvent(new Event('input', { bubbles: true }));
    });
  }
  return function (v, H, C) {
    var EN = %EN%;
    var T = EN ? {
      p: 'Player', np: 'Enter 3 to 64 names separated by commas, or just how many players.', many: 'Up to 64 names.', dup: 'Repeated name: ',
      bye: 'bye', R: ['Final', 'Semi-finals', 'Quarter-finals', 'Round of 16', 'Round of 32', 'Round of 64'], third: 'Third place',
      champ: 'Champion', players: 'players', byes: 'byes', matches: 'matches', draw: 'Bracket', tbd: '…',
      note: 'Tap a name to send it to the next round; tap again to undo. The results travel in the page link.'
    } : {
      p: 'Jugador', np: 'Escribe de 3 a 64 nombres separados por comas, o solo cuántos son.', many: 'Como mucho 64 nombres.', dup: 'Nombre repetido: ',
      bye: 'exento', R: ['Final', 'Semifinales', 'Cuartos de final', 'Octavos de final', 'Dieciseisavos', 'Treintaidosavos'], third: 'Tercer puesto',
      champ: 'Campeón', players: 'participantes', byes: 'exentos', matches: 'partidos', draw: 'Cuadro', tbd: '…',
      note: 'Toca un nombre para pasarlo a la ronda siguiente; vuelve a tocarlo para deshacer. Los resultados viajan en el enlace de la página.'
    };
    %RND%
    var raw = String(v.nombres).split(/[,;\n]+/).map(function (s) { return s.trim().replace(/\s+/g, ' '); }).filter(Boolean), names;
    if (raw.length === 1 && /^\d+$/.test(raw[0])) { names = []; for (var q = 1; q <= +raw[0] && q <= 99; q++) names.push(T.p + ' ' + q); }
    else names = raw;
    var N = names.length;
    if (N < 3) return { err: T.np };
    if (N > 64) return { err: T.many };
    var low = names.map(function (s) { return s.toLowerCase(); });
    for (var i = 0; i < N; i++) if (low.indexOf(low[i]) !== i) return { err: T.dup + H.esc(names[i]) };
    var S = 2; while (S < N) S *= 2;
    var L = Math.round(Math.log(S) / Math.LN2);
    /* seed order of the S slots: [1, 2] -> [1, 4, 3, 2] -> [1, 8, 5, 4, 3, 6, 7, 2]... (seed s meets size + 1 - s;
       1 at the top, 2 at the bottom), then the better seed first inside each first-round match */
    var ord = [1, 2];
    while (ord.length < S) { var nx = [], z = ord.length * 2 + 1; ord.forEach(function (s, j) { if (j % 2) nx.push(z - s, s); else nx.push(s, z - s); }); ord = nx; }
    for (i = 0; i < S; i += 2) if (ord[i] > ord[i + 1]) { var sw = ord[i]; ord[i] = ord[i + 1]; ord[i + 1] = sw; }
    var seeded = []; for (i = 0; i < N; i++) seeded.push(i);
    if (v.orden === 'sorteo') seeded = shuf(seeded, rng(low.join('|') + '#' + (v.sorteo >= 0 ? v.sorteo : 0)));
    var slot = ord.map(function (s) { return s <= N ? seeded[s - 1] : -1; });   /* -1 = bye */
    /* matches: round r (0 = first) has S / 2^(r+1) matches; global index in round order */
    var g = String(v.g || '').replace(/[^012]/g, ''), base = [], tot = 0;
    for (var r = 0; r < L; r++) { base.push(tot); tot += S >> (r + 1); }
    var third = v.tercero && L >= 2, tIdx = tot;
    if (third) tot++;
    var rounds = [], win = [], lose = [];
    for (r = 0; r < L; r++) {
      var ms = [], cnt = S >> (r + 1);
      for (var m = 0; m < cnt; m++) {
        var a, b, k = base[r] + m;
        if (r === 0) { a = slot[2 * m]; b = slot[2 * m + 1]; }
        else { a = win[base[r - 1] + 2 * m]; b = win[base[r - 1] + 2 * m + 1]; }
        var w = null, l = null;
        if (r === 0 && (a === -1 || b === -1)) w = a === -1 ? b : a;   /* bye */
        else if (a !== null && a !== undefined && b !== null && b !== undefined && a >= 0 && b >= 0) {
          if (g[k] === '1') { w = a; l = b; } else if (g[k] === '2') { w = b; l = a; }
        }
        win[k] = w; lose[k] = l;
        /* matches downstream of k (to clear when k changes) */
        var down = [], kr = r, km = m;
        while (kr < L - 1) { km = km >> 1; kr++; down.push(base[kr] + km); }
        if (third && r <= L - 2) down.push(tIdx);
        ms.push({ k: k, a: a, b: b, w: w, d: down.join(',') });
      }
      rounds.push(ms);
    }
    var tm = null;
    if (third) {
      var sa = lose[base[L - 2]], sb = lose[base[L - 2] + 1], tw = null;
      if (sa !== null && sb !== null && sa !== undefined && sb !== undefined) tw = g[tIdx] === '1' ? sa : g[tIdx] === '2' ? sb : null;
      tm = { k: tIdx, a: sa, b: sb, w: tw, d: '' };
    }
    function who(x, mt, side) {
      if (x === -1) return '<span class="ct-p ct-x">' + T.bye + '</span>';
      if (x === null || x === undefined) return '<span class="ct-p ct-e">' + T.tbd + '</span>';
      var other = side === '1' ? mt.b : mt.a, click = other !== null && other !== undefined && other >= 0 && mt.a !== -1 && mt.b !== -1;
      var sd = v.orden === 'sorteo' ? '' : '<small>' + (x + 1) + '</small>';
      return click ? '<button type="button" class="ct-p' + (mt.w === x ? ' ct-w' : mt.w !== null ? ' ct-l' : '') + '" data-m="' + mt.k + '" data-s="' + side + '" data-t="' + tot + '" data-d="' + mt.d + '">' + sd + H.esc(names[x]) + '</button>'
        : '<span class="ct-p' + (mt.w === x ? ' ct-w' : '') + '">' + sd + H.esc(names[x]) + '</span>';
    }
    var h = '<div class="ct-b">';
    for (r = 0; r < L; r++) {
      var nmR = L - 1 - r < T.R.length ? T.R[L - 1 - r] : (EN ? 'Round ' : 'Ronda ') + (r + 1);
      h += '<div class="ct-c"><h4>' + nmR + '</h4><div class="ct-ms">' + rounds[r].map(function (mt) {
        return '<div class="ct-m">' + who(mt.a, mt, '1') + who(mt.b, mt, '2') + '</div>';
      }).join('') + '</div></div>';
    }
    var champ = win[base[L - 1]];
    h += '<div class="ct-c ct-f"><h4>' + T.champ + '</h4><div class="ct-ms"><div class="ct-m ct-ch">' +
      (champ !== null && champ !== undefined ? '<span class="ct-p ct-w">' + H.esc(names[champ]) + '</span>' : '<span class="ct-p ct-e">' + T.tbd + '</span>') + '</div></div></div></div>';
    if (tm) h += '<div class="ct-3"><h4>' + T.third + '</h4><div class="ct-m">' + who(tm.a, tm, '1') + who(tm.b, tm, '2') + '</div></div>';
    var played = N - 1 + (third ? 1 : 0), byes = S - N;
    return {
      label: T.draw + ' · ' + (L - 1 < T.R.length ? T.R[L - 1] : '') , big: champ !== null && champ !== undefined ? H.esc(names[champ]) : S + (EN ? '-player draw' : ' plazas'),
      sub: N + ' ' + T.players + (byes ? ' · ' + byes + ' ' + T.byes : '') + ' · ' + played + ' ' + T.matches,
      html: h, note: T.note, print: true,
      n: { size: S, byes: byes, matches: played, r1: rounds[0].map(function (mt) { return [mt.a < 0 ? '-' : names[mt.a], mt.b < 0 ? '-' : names[mt.b]]; }).slice(0, 4),
           champ: champ !== null && champ !== undefined ? names[champ] : null, third: tm && tm.w !== null ? names[tm.w] : null }
    };
  };
})()
"""

CSS = """
#g-f{display:none}.ct-b{display:flex;gap:.5rem;overflow-x:auto;padding-bottom:.4rem}
.ct-c{display:flex;flex-direction:column;min-width:8.6rem;flex:1 0 8.6rem}.ct-c h4{font-size:.85rem;margin:.2rem 0 .4rem;color:var(--mut,#666);text-align:center}
.ct-ms{display:flex;flex-direction:column;justify-content:space-around;flex:1;gap:.4rem}
.ct-m{border:1px solid var(--line,#ccc);border-radius:6px;overflow:hidden;background:var(--card,#fff)}
.ct-p{display:block;width:100%;text-align:left;padding:.35rem .5rem;font:inherit;font-size:.9rem;border:0;background:none;color:inherit;cursor:default;
white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ct-p+.ct-p{border-top:1px solid var(--line,#ddd)}
button.ct-p{cursor:pointer}button.ct-p:hover{background:var(--hl,rgba(0,0,0,.05))}.ct-p small{color:var(--mut,#888);margin-right:.35rem;font-size:.75rem}
.ct-w{font-weight:700}.ct-l{opacity:.55;text-decoration:line-through}.ct-x,.ct-e{color:var(--mut,#999);font-style:italic}
.ct-ch .ct-p{text-align:center;font-size:1rem}.ct-3{max-width:12rem;margin-top:.8rem}.ct-3 h4{font-size:.85rem;color:var(--mut,#666);margin:.2rem 0}
@media print{.ct-b{overflow:visible}.ct-c{min-width:0}}
"""

INPUTS_ES = [
    {"id": "nombres", "type": "text", "label": "Participantes", "value": "Ana, Luis, Marta, Pedro, Sara, Javi, Lucía, Dani, Irene, Raúl", "w": "xl",
     "placeholder": "Ana, Luis, Marta… o 16"},
    {"id": "orden", "type": "seg", "label": "Orden", "value": "serie", "options": [("serie", "Cabezas de serie"), ("sorteo", "Sorteo")]},
    {"id": "tercero", "type": "check", "label": "3.º y 4.º puesto", "value": False},
    {"id": "sorteo", "type": "number", "label": "Sorteo nº", "value": "", "more": True, "w": "s", "show": ("orden", ["sorteo"])},
    {"id": "g", "type": "text", "label": "Ganadores", "value": "", "more": True},
]


def blocks(ctx):
    return [
        ("Cómo se monta un cuadro eliminatorio", """
<p>Un cuadro eliminatorio necesita un número de plazas que sea potencia de 2: 4, 8, 16, 32 o 64. Si los inscritos no
llegan, las plazas que sobran son <b>exentos</b> (byes): el rival de ese hueco pasa directamente a la segunda ronda. Con
10 participantes el cuadro es de 16 plazas, hay 6 exentos y la primera ronda real solo tiene 2 partidos; a partir de
octavos ya no queda ningún hueco. En total siempre se juegan <b>participantes − 1 partidos</b> (9 con 10 inscritos), más
uno si hay partido por el tercer puesto.</p>
<p>Escribe los nombres en orden de nivel o de ranking y elige «Cabezas de serie»: el 1 y el 2 quedan en mitades opuestas
y solo pueden cruzarse en la final, el 3 y el 4 en cuartos opuestos, y los exentos van a los mejores clasificados, como en
los torneos oficiales. Con «Sorteo» el orden se baraja; el número de sorteo hace que el mismo cuadro se pueda repetir.</p>"""),
        ("El orden de los cruces", """
<p>La colocación sigue la regla clásica: en cada ronda, el cabeza de serie <i>s</i> se mide al que sumado a él da el número
de plazas más uno. En un cuadro de 16 la primera ronda es 1–16, 8–9, 5–12, 4–13, 3–14, 6–11, 7–10 y 2–15, en ese orden de
arriba abajo. Si todos ganan los favoritos, en cuartos se juegan 1–8, 4–5, 3–6 y 2–7, y en semifinales 1–4 y 2–3. Con 10
inscritos, los seis primeros cabezas de serie están exentos y los únicos partidos de la primera ronda son 8–9 y 7–10.</p>"""),
        ("Apuntar los resultados y compartir", """
<p>Durante el torneo, toca el nombre del ganador de cada partido y pasará a la ronda siguiente; si te equivocas, vuelve a
tocarlo. Al cambiar un resultado se borran los cruces que dependían de él, para que nadie avance por error. Los resultados
quedan guardados dentro del enlace: con «Copiar enlace» lo mandas al grupo y todos ven el cuadro al día. «Imprimir o PDF»
saca el cuadro en una hoja para colgar en el club o rellenar a mano.</p>"""),
    ]


FAQ = [
    ("¿Cuántos exentos hay en un cuadro de 12 participantes?",
     "Cuatro: el cuadro es de 16 plazas y 16 − 12 = 4. Los cuatro primeros cabezas de serie pasan directamente a octavos (la segunda ronda)."),
    ("¿Cuántos partidos se juegan en un torneo eliminatorio?",
     "Uno menos que participantes, porque cada partido elimina a uno y solo queda el campeón: 15 partidos con 16 jugadores, 31 con 32."),
    ("¿Por qué el 1 y el 2 van en lados opuestos?",
     "Para que los dos favoritos solo puedan encontrarse en la final. Es la regla de las federaciones de tenis, pádel y casi todos los deportes."),
    ("¿Se puede hacer un sorteo puro sin cabezas de serie?",
     "Sí: elige «Sorteo». Los nombres se barajan y se colocan en el cuadro; los exentos siguen repartidos para que no coincidan dos en el mismo partido."),
    ("¿Hace falta partido por el tercer puesto?",
     "Es opcional. Márcalo si hay medallas o premios para los tres primeros: lo juegan los dos que pierden las semifinales."),
]

TOOL = {
    "slug": "cuadro-torneo",
    "lang": "es",
    "twin": "tournament-bracket-generator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "tournament",
    "order": 30,
    "name": "Cuadro de torneo",
    "k": "cuadro eliminatorio torneo bracket cabezas de serie exentos byes eliminatoria imprimible",
    "title": "Cuadro de torneo eliminatorio con exentos e imprimible",
    "desc": "Crea el cuadro de un torneo eliminatorio de 3 a 64 participantes: cabezas de serie, exentos, tercer puesto y resultados. Gratis e imprimible.",
    "h1": "Cuadro de torneo eliminatorio",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Single-elimination tournament · seeding and byes (Wikipedia)", "https://en.wikipedia.org/wiki/Single-elimination_tournament"),
                ("ITF · World Tennis Tour Regulations, colocación de cabezas de serie", "https://www.itftennis.com/en/about-us/governance/rules-and-regulations/")],
    "credits": [D.MULBERRY],
    "related": ["liguilla-round-robin", "americano-padel"],
    "tests": [
        ({}, {"n.size": 16, "n.byes": 6, "n.matches": 9, "n.r1": [["Ana", "-"], ["Dani", "Irene"], ["Sara", "-"], ["Pedro", "-"]]}),
        ({"nombres": "8"}, {"n.size": 8, "n.byes": 0, "n.r1": [["Jugador 1", "Jugador 8"], ["Jugador 4", "Jugador 5"], ["Jugador 3", "Jugador 6"], ["Jugador 2", "Jugador 7"]]}),
        ({"nombres": "4", "g": "121"}, {"n.champ": "Jugador 1"}),
        ({"nombres": "4", "g": "1222", "tercero": True}, {"n.champ": "Jugador 3", "n.third": "Jugador 2"}),
        ({"nombres": "Ana, Luis"}, {"err": "Escribe de 3 a 64 nombres separados por comas, o solo cuántos son."}),
        ({"nombres": "65"}, {"err": "Como mucho 64 nombres."}),
    ],
}
