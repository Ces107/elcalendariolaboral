"""Americano / mexicano de pádel: fair rotation of partners, opponents and rests for 4-24 players on 1-6 courts, live
scores per match (stored in the URL, so the link is the scoreboard) and the ranking. ES page; the EN twin
(padel-americano-generator) imports JS and the same inputs."""
from herramientas.tools import _deporte as D

JS = r"""
(function () {
  /* live scores: the score boxes live in #out (outside the form). On change, write them all into the hidden 'sc'
     field and fire its input event, so the runtime recomputes, re-renders and keeps them in the URL; then put the
     focus back on the box the user moved to. */
  if (typeof document !== 'undefined' && !window.__apScores) {
    window.__apScores = 1;
    document.addEventListener('input', function (e) { if (e.target.classList && e.target.classList.contains('ap-s')) e.target.classList.remove('au'); });
    document.addEventListener('change', function (e) {
      if (!e.target.classList || !e.target.classList.contains('ap-s')) return;
      setTimeout(function () {
        var a = document.activeElement, k = a && a.classList && a.classList.contains('ap-s') ? a.getAttribute('data-k') + '|' + a.getAttribute('data-s') : '';
        var box = document.getElementById('sc'), all = document.querySelectorAll('.ap-s'), m = [];
        for (var i = 0; i < all.length; i++) {
          var x = all[i], j = +x.getAttribute('data-k'), s = +x.getAttribute('data-s'), w = x.value.replace(/\D/g, '').slice(0, 3);
          if (!m[j]) m[j] = ['', ''];
          if (!x.classList.contains('au')) m[j][s] = w;
        }
        for (i = 0; i < m.length; i++) m[i] = m[i] ? (m[i][0] + (m[i][1] !== '' ? '-' + m[i][1] : '')).replace(/^-/, '-') : '';
        box.value = m.join(',').replace(/,+$/, '');
        box.dispatchEvent(new Event('input', { bubbles: true }));
        if (k) { var p = k.split('|'), b = document.querySelector('.ap-s[data-k="' + p[0] + '"][data-s="' + p[1] + '"]'); if (b) { b.focus(); try { b.select(); } catch (er) { /* number */ } } }
      }, 0);
    });
  }
  var cache = {};
  %RND%
  /* americano: for each round, rest the players with fewest rests, then local search (pair swaps, 12 random starts)
     for the 2v2 split with the fewest repeated partners (weight 100) and opponents (weight 3); 8 whole-schedule
     attempts, keep the one with fewest partner repeats and the flattest opponent counts */
  function americano(N, K, R, seed) {
    var key = N + '/' + K + '/' + R + '/' + seed;
    if (cache[key]) return cache[key];
    var best = null;
    for (var at = 0; at < 8; at++) {
      var rnd = rng(seed + '#' + at), part = [], opp = [], bye = [], rounds = [], i, j;
      for (i = 0; i < N; i++) { part.push([]); opp.push([]); bye.push(0); for (j = 0; j < N; j++) { part[i].push(0); opp[i].push(0); } }
      var all = []; for (i = 0; i < N; i++) all.push(i);
      for (var rd = 0; rd < R; rd++) {
        var ord = shuf(all, rnd).sort(function (a, b) { return bye[b] - bye[a]; });
        var play = ord.slice(0, 4 * K), sit = ord.slice(4 * K);
        var cost = function (p) {
          var c = 0;
          for (var m = 0; m < K; m++) {
            var a = p[4 * m], b = p[4 * m + 1], x = p[4 * m + 2], y = p[4 * m + 3];
            c += 100 * (part[a][b] + part[x][y]) + 3 * (opp[a][x] + opp[a][y] + opp[b][x] + opp[b][y]);
          }
          return c;
        };
        var bp = null, bc = 1e18;
        for (var t = 0; t < 12 && bc > 0; t++) {
          var p = shuf(play, rnd), c = cost(p), imp = true;
          while (imp) {
            imp = false;
            for (i = 0; i < p.length; i++) for (j = i + 1; j < p.length; j++) {
              if ((i >> 1) === (j >> 1)) continue;
              var q = p[i]; p[i] = p[j]; p[j] = q;
              var c2 = cost(p);
              if (c2 < c) { c = c2; imp = true; } else { q = p[i]; p[i] = p[j]; p[j] = q; }
            }
          }
          if (c < bc) { bc = c; bp = p.slice(); }
        }
        var ms = [];
        for (var m = 0; m < K; m++) {
          var a = bp[4 * m], b = bp[4 * m + 1], x = bp[4 * m + 2], y = bp[4 * m + 3];
          part[a][b]++; part[b][a]++; part[x][y]++; part[y][x]++;
          opp[a][x]++; opp[x][a]++; opp[a][y]++; opp[y][a]++; opp[b][x]++; opp[x][b]++; opp[b][y]++; opp[y][b]++;
          ms.push([[a, b], [x, y]]);
        }
        for (i = 0; i < sit.length; i++) bye[sit[i]]++;
        rounds.push({ m: ms, s: sit });
      }
      var rep = 0, omax = 0, omin = 1e9;
      for (i = 0; i < N; i++) for (j = i + 1; j < N; j++) { rep += Math.max(0, part[i][j] - 1); omax = Math.max(omax, opp[i][j]); omin = Math.min(omin, opp[i][j]); }
      var score = rep * 1000 + omax - omin;
      if (!best || score < best.score) best = { score: score, rep: rep, omax: omax, omin: omin, rounds: rounds };
      if (rep === 0 && omax - omin <= 1) break;
    }
    cache[key] = best;
    return best;
  }
  return function (v, H, C) {
    var EN = %EN%;
    var T = EN ? {
      p: 'Player', np: 'Enter 4 to 24 names separated by commas, or just the number of players.', many: 'Up to 24 players.',
      dup: 'Repeated name: ', court: 'Court', rest: 'Sitting out', rnd: 'Round', rounds: 'rounds', players: 'players', courts: 'courts',
      court1: 'court', pts: 'points', free: 'free scoring', rk: 'Ranking', nm: 'Player', pt: 'Pts', pl: 'P', w: 'W', avg: 'Avg',
      am: 'Americano', mx: 'Mexicano', rep: 'repeated partners', noR: 'Enter how many rounds (1 to 40).', noK: 'Enter how many courts (1 to 6).',
      next: 'Round {r} appears when every score of round {p} is in.', all: 'Everyone partners everyone once in {n} rounds.',
      noteA: 'Type one side of each score and the other fills in. The scores travel inside the page link: share it and everyone sees the same table.',
      vs: 'vs', ronda: 'R'
    } : {
      p: 'Jugador', np: 'Escribe de 4 a 24 nombres separados por comas, o solo el número de jugadores.', many: 'Como mucho 24 jugadores.',
      dup: 'Nombre repetido: ', court: 'Pista', rest: 'Descansa', rnd: 'Ronda', rounds: 'rondas', players: 'jugadores', courts: 'pistas',
      court1: 'pista', pts: 'puntos', free: 'puntuación libre', rk: 'Clasificación', nm: 'Jugador', pt: 'Ptos', pl: 'PJ', w: 'G', avg: 'Media',
      am: 'Americano', mx: 'Mexicano', rep: 'parejas repetidas', noR: 'Indica cuántas rondas (de 1 a 40).', noK: 'Indica cuántas pistas (de 1 a 6).',
      next: 'La ronda {r} aparece cuando estén todos los resultados de la ronda {p}.', all: 'Todos juegan de pareja con todos una vez en {n} rondas.',
      noteA: 'Escribe los puntos de una pareja y la otra se completa sola. Los resultados van dentro del enlace de la página: compártelo y todos verán la misma tabla.',
      vs: 'vs', ronda: 'R'
    };
    var raw = String(v.jug).split(/[,;\n]+/).map(function (s) { return s.trim().replace(/\s+/g, ' '); }).filter(Boolean), names;
    if (raw.length === 1 && /^\d+$/.test(raw[0])) { names = []; for (var q = 1; q <= +raw[0] && q <= 99; q++) names.push(T.p + ' ' + q); }
    else names = raw;
    var N = names.length;
    if (N < 4) return { err: T.np };
    if (N > 24) return { err: T.many };
    var low = names.map(function (s) { return s.toLowerCase(); });
    for (var i = 0; i < N; i++) {
      if (low.indexOf(low[i]) !== i) return { err: T.dup + H.esc(names[i]) };
      if (names[i].length > 30) names[i] = names[i].slice(0, 30);
    }
    if (!(v.pistas >= 1 && v.pistas <= 6) || v.pistas % 1) return { err: T.noK };
    if (!(v.rondas >= 1 && v.rondas <= 40) || v.rondas % 1) return { err: T.noR };
    var K = Math.min(v.pistas, Math.floor(N / 4)), R = v.rondas, P = +v.pts || 0, mex = v.modo === 'mx';
    var seed = low.join('|') + '#' + (v.sorteo >= 0 ? v.sorteo : '');
    /* scores: 'a-b' per match, comma separated, in round order; one side + fixed total -> the other side */
    var sc = String(v.sc || '').split(',').map(function (s) {
      var m = /^(\d{0,3})(?:-(\d{0,3}))?$/.exec(s.trim());
      if (!m) return null;
      var a = m[1] === '' ? null : +m[1], b = m[2] === undefined || m[2] === '' ? null : +m[2], au = -1;
      if (P > 0 && a !== null && b === null && a <= P) { b = P - a; au = 1; }
      else if (P > 0 && b !== null && a === null && b <= P) { a = P - b; au = 0; }
      return a === null || b === null ? (a === null && b === null ? null : { a: a, b: b, part: 1 }) : { a: a, b: b, au: au };
    });
    var pts = [], pj = [], won = [], bye = [];
    for (i = 0; i < N; i++) { pts.push(0); pj.push(0); won.push(0); bye.push(0); }
    function score(m, s) {
      if (!s || s.part) return false;
      var t = [s.a, s.b];
      for (var z = 0; z < 2; z++) for (var y = 0; y < 2; y++) { var pl = m[z][y]; pts[pl] += t[z]; pj[pl]++; if (t[z] > t[1 - z]) won[pl]++; }
      return true;
    }
    function rank() {
      var o = []; for (var x = 0; x < N; x++) o.push(x);
      return o.sort(function (a, b) { return pts[b] - pts[a] || won[b] - won[a] || a - b; });
    }
    var rounds = [], sched = null, shown = R, k = 0, complete;
    if (!mex) {
      sched = americano(N, K, R, seed);
      for (var rd = 0; rd < R; rd++) {
        rounds.push(sched.rounds[rd]);
        for (var mm = 0; mm < K; mm++) score(sched.rounds[rd].m[mm], sc[k++]);
      }
    } else {
      var rnd = rng(seed), part = [];
      for (i = 0; i < N; i++) { part.push([]); for (var j = 0; j < N; j++) part[i].push(0); }
      var start = []; for (i = 0; i < N; i++) start.push(i);
      if (v.sorteo >= 0) start = shuf(start, rnd);
      for (rd = 0; rd < R; rd++) {
        var ord = rd === 0 ? start.slice() : rank();
        /* rest: fewest rests so far, ties at random */
        var pri = shuf(ord.slice(), rnd).sort(function (a, b) { return bye[b] - bye[a]; }), sit = pri.slice(4 * K);
        var play = ord.filter(function (x) { return sit.indexOf(x) < 0; }), ms = [];
        for (mm = 0; mm < K; mm++) {
          var g = play.slice(4 * mm, 4 * mm + 4), opts = [[[g[0], g[3]], [g[1], g[2]]], [[g[0], g[2]], [g[1], g[3]]], [[g[0], g[1]], [g[2], g[3]]]];
          var pick = opts[0], pc = 1e9;
          for (var o = 0; o < 3; o++) { var cst = part[opts[o][0][0]][opts[o][0][1]] + part[opts[o][1][0]][opts[o][1][1]]; if (cst < pc) { pc = cst; pick = opts[o]; } }
          part[pick[0][0]][pick[0][1]]++; part[pick[0][1]][pick[0][0]]++; part[pick[1][0]][pick[1][1]]++; part[pick[1][1]][pick[1][0]]++;
          ms.push(pick);
        }
        for (i = 0; i < sit.length; i++) bye[sit[i]]++;
        rounds.push({ m: ms, s: sit });
        complete = true;
        for (mm = 0; mm < K; mm++) if (!score(ms[mm], sc[k++])) complete = false;
        if (!complete) { shown = rd + 1; break; }
      }
    }
    var played = pj.some(function (x) { return x > 0; });
    function nm(x) { return H.esc(names[x]); }
    var h = '';
    if (played) {
      var rk = rank(), tb = '';
      rk.forEach(function (x, n) {
        tb += '<tr><td class="num">' + (n + 1) + '</td><th scope="row">' + nm(x) + '</th><td class="num"><b>' + pts[x] + '</b></td><td class="num">' + pj[x] +
          '</td><td class="num">' + won[x] + '</td><td class="num">' + (pj[x] ? H.num(pts[x] / pj[x], 1).replace(',', EN ? '.' : ',') : '–') + '</td></tr>';
      });
      h += '<h3 class="ap-h">' + T.rk + '</h3><table class="tbl ap-rk"><thead><tr><th>#</th><th>' + T.nm + '</th><th class="num">' + T.pt + '</th><th class="num">' + T.pl +
        '</th><th class="num">' + T.w + '</th><th class="num">' + T.avg + '</th></tr></thead><tbody>' + tb + '</tbody></table>';
    }
    k = 0;
    for (rd = 0; rd < rounds.length; rd++) {
      var rr = rounds[rd], rows = '';
      for (mm = 0; mm < rr.m.length; mm++, k++) {
        var m = rr.m[mm], s = sc[k], va = s && s.a !== null ? s.a : '', vb = s && s.b !== null ? s.b : '';
        rows += '<tr><td class="ap-c">' + (mm + 1) + '</td><td class="ap-t">' + nm(m[0][0]) + '<br>' + nm(m[0][1]) + '</td>' +
          '<td class="ap-x"><input class="inp ap-s' + (s && s.au === 0 ? ' au' : '') + '" inputmode="numeric" maxlength="3" data-k="' + k + '" data-s="0" value="' + va + '" aria-label="' + T.court + ' ' + (mm + 1) + ' · ' + nm(m[0][0]) + '">' +
          '<span>–</span><input class="inp ap-s' + (s && s.au === 1 ? ' au' : '') + '" inputmode="numeric" maxlength="3" data-k="' + k + '" data-s="1" value="' + vb + '" aria-label="' + T.court + ' ' + (mm + 1) + ' · ' + nm(m[1][0]) + '"></td>' +
          '<td class="ap-t">' + nm(m[1][0]) + '<br>' + nm(m[1][1]) + '</td></tr>';
      }
      h += '<div class="ap-r"><h3 class="ap-h">' + T.rnd + ' ' + (rd + 1) + '</h3><table class="tbl ap-m"><tbody>' + rows + '</tbody></table>' +
        (rr.s.length ? '<p class="ap-b">' + T.rest + ': ' + rr.s.map(nm).join(', ') + '</p>' : '') + '</div>';
    }
    if (mex && shown < R) h += '<p class="hnote">' + T.next.replace('{r}', shown + 1).replace('{p}', shown) + '</p>';
    var need = Math.ceil((N - 1) * N / (4 * K));
    var sub = [N + ' ' + T.players, K + ' ' + (K === 1 ? T.court1 : T.courts), P ? P + ' ' + T.pts : T.free].join(' · ');
    var c1 = rounds.length > 1 ? rounds[1].m[0] : null;
    return {
      label: (mex ? T.mx : T.am), big: R + ' ' + T.rounds, sub: sub, html: h,
      note: T.noteA + (!mex && R < need ? ' ' + T.all.replace('{n}', need) : '') + (!mex && sched.rep ? ' ' + sched.rep + ' ' + T.rep + '.' : ''),
      print: true,
      n: { players: N, courts: K, rounds: rounds.length, rep: sched ? sched.rep : null, omin: sched ? sched.omin : null, omax: sched ? sched.omax : null,
           leader: played ? names[rank()[0]] : null, top: played ? pts[rank()[0]] : null,
           c1: c1 ? [names[c1[0][0]], names[c1[0][1]], names[c1[1][0]], names[c1[1][1]]] : null }
    };
  };
})()
"""

CSS = """
#sc-f{display:none}.ap-h{font-size:1rem;margin:1.1rem 0 .35rem}.ap-r{break-inside:avoid}
.ap-m td{vertical-align:middle;padding:.35rem .4rem}.ap-c{width:1.6rem;color:var(--mut,#666);text-align:center}
.ap-t{line-height:1.25}.ap-m .ap-t:last-child{text-align:right}.ap-x{white-space:nowrap;text-align:center;width:7.2rem}
.ap-s{width:2.8rem;text-align:center;padding:.3rem .2rem;font-weight:700}.ap-s.au{color:var(--mut,#777);font-weight:400}
.ap-x span{margin:0 .2rem}.ap-b{font-size:.9rem;color:var(--mut,#666);margin:.2rem 0 0}.ap-rk td,.ap-rk th{padding:.3rem .45rem}
@media print{.ap-s{border:1px solid #999}.ap-s.au{color:#000}}
"""

INPUTS_ES = [
    {"id": "modo", "type": "seg", "label": "Formato", "value": "am", "options": [("am", "Americano"), ("mx", "Mexicano")]},
    {"id": "jug", "type": "text", "label": "Jugadores", "value": "Ana, Luis, Marta, Pedro, Sara, Javi, Lucía, Dani", "w": "xl",
     "placeholder": "Ana, Luis, Marta… o 12"},
    {"id": "pistas", "type": "number", "label": "Pistas", "value": "2", "w": "s"},
    {"id": "rondas", "type": "number", "label": "Rondas", "value": "7", "w": "s"},
    {"id": "pts", "type": "seg", "label": "Puntos", "value": "24",
     "options": [("16", "16"), ("21", "21"), ("24", "24"), ("32", "32"), ("0", "Libre")]},
    {"id": "sorteo", "type": "number", "label": "Variante", "value": "", "more": True, "w": "s"},
    {"id": "sc", "type": "text", "label": "Resultados", "value": "", "more": True},
]


def blocks(ctx):
    return [
        ("Cómo funciona la americana", """
<p>Escribe los nombres, el número de pistas y de rondas, y el generador reparte parejas y rivales para que cada jugador
juegue con compañeros distintos en cada ronda y se cruce con todos los demás lo más parecido posible. Con 8 jugadores,
2 pistas y 7 rondas, cada uno juega exactamente una vez con cada uno de los otros siete: es el reparto perfecto de una
americana. Si sobran jugadores (10 en 2 pistas, por ejemplo), descansan por turnos y nadie descansa dos veces antes de que
todos lo hayan hecho una.</p>
<p>En una americana <b>cada partido se juega a un total de puntos fijo</b>, normalmente 16, 21, 24 o 32: con 24, la
pareja que gana 15 a 9 suma 15 puntos para cada uno de sus dos jugadores y la otra, 9. Al final no gana una pareja, sino
el jugador con más puntos acumulados. Por eso basta con escribir los puntos de una pareja: la otra se completa sola
(en gris) y la clasificación se recalcula al momento con puntos, partidos jugados, partidos ganados y media por partido.</p>"""),
        ("Americano o mexicano", """
<p>En el <b>americano</b> todas las rondas se conocen desde el principio: se puede imprimir la hoja con los cruces y
colgarla en el club. En el <b>mexicano</b> solo se conoce la primera ronda (en el orden en que escribas los nombres, así que
ponlos de más a menos nivel); cada ronda siguiente se forma con la clasificación del momento: los cuatro primeros juegan en
la pista 1, del quinto al octavo en la pista 2, y así sucesivamente. Dentro de cada pista juegan el 1.º y el 4.º contra el
2.º y el 3.º, salvo que esa pareja ya se haya repetido, en cuyo caso se prueba otra combinación. El resultado son partidos
cada vez más igualados, que es lo que busca el formato.</p>
<p>Un ejemplo con los 8 nombres que trae la herramienta, a 24 puntos. En la primera ronda del mexicano juegan Ana y Pedro
contra Luis y Marta en la pista 1, y Sara y Dani contra Javi y Lucía en la pista 2. Si ganan Ana y Pedro 15-9 y Sara y
Dani 13-11, la clasificación queda: Ana y Pedro, 15 puntos; Sara y Dani, 13; Javi y Lucía, 11; Luis y Marta, 9. La segunda
ronda pone en la pista 1 a los cuatro primeros (Ana y Dani contra Pedro y Sara) y en la pista 2 a los cuatro últimos
(Javi y Marta contra Lucía y Luis).</p>"""),
        ("Compartir el marcador e imprimir", """
<p>Los resultados se guardan dentro del enlace de la página, sin cuentas ni servidores: pulsa «Copiar enlace» y mándalo al
grupo; quien lo abra verá los mismos cruces, los resultados ya apuntados y la clasificación. Si el organizador sigue
anotando, vuelve a mandar el enlace al final. «Imprimir o PDF» saca una hoja con todas las rondas y casillas para apuntar
a mano. En «Más opciones», «Variante» cambia el reparto (útil si dos amigos quieren evitar un cruce concreto) manteniendo
el mismo número de rondas.</p>"""),
    ]


FAQ = [
    ("¿Cuántas rondas tiene una americana de 8 jugadores?",
     "Siete, para que cada jugador juegue una vez con cada uno de los otros siete. Con 12 jugadores en 3 pistas serían 11 y con 16 en "
     "4 pistas, 15; si no hay tiempo, juega menos rondas: el generador sigue evitando repetir pareja."),
    ("¿A cuántos puntos se juega cada partido?",
     "Lo más habitual es a 24 puntos (unos 15 minutos) o a 32 (unos 20). A 16 o 21 se usa cuando hay muchos jugadores o poco tiempo de "
     "pista. Elige «Libre» si contáis juegos o jugáis a tiempo: entonces hay que escribir los dos marcadores."),
    ("¿Qué pasa si somos un número impar o sobran jugadores?",
     "Cada ronda juegan cuatro por pista y el resto descansa. Los descansos se reparten por turnos, así que al final la diferencia entre "
     "quien más y quien menos ha descansado es como mucho de una ronda. Mira la columna «Media» si queréis compararlos por partido jugado."),
    ("¿Cómo se desempata la clasificación?",
     "Primero por puntos acumulados; si siguen iguales, por partidos ganados, y después por el orden en que se escribieron los nombres. "
     "Muchos clubes juegan un último punto de oro entre los empatados: apúntalo en vuestro último partido."),
    ("¿Se pierden los resultados si cierro la página?",
     "No, si guardas o compartes el enlace: los resultados van dentro de él. Si cambias la lista de jugadores, el reparto se rehace y los "
     "resultados anteriores ya no casan, así que cierra la lista antes de empezar."),
    ("¿En el mexicano puedo corregir un resultado antiguo?",
     "Sí, pero las rondas siguientes se recalculan con la nueva clasificación, y pueden cambiar las parejas de rondas ya jugadas. Corrige "
     "solo la ronda en curso."),
]

TOOL = {
    "slug": "americano-padel",
    "lang": "es",
    "twin": "padel-americano-generator",
    "cat": D.CAT_ES[0], "cat_name": D.CAT_ES[1],
    "icon": "ball-tennis",
    "order": 10,
    "name": "Americano de pádel",
    "k": "americana mexicana padel torneo parejas rotación pistas clasificación cuadrante",
    "title": "Americano de pádel: generador de americanas y mexicanas",
    "desc": "Crea una americana o mexicana de pádel gratis: rotación de parejas y pistas para 4 a 24 jugadores, marcador por ronda, clasificación e impresión.",
    "h1": "Generador de americanas de pádel",
    "updated": "2026-11-12",
    "inputs": INPUTS_ES,
    "js": D.make(JS, False),
    "css": CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Social golfer problem · CSPLib prob010 (problema de repartir grupos sin repetir compañeros)", "https://www.csplib.org/Problems/prob010/"),
                ("Social Golfer Problem · Wolfram MathWorld", "https://mathworld.wolfram.com/SocialGolferProblem.html")],
    "credits": [D.MULBERRY],
    "related": ["liguilla-round-robin", "cuadro-torneo", "amigo-invisible"],
    "tests": [
        ({}, {"n.players": 8, "n.rounds": 7, "n.rep": 0, "n.omin": 2, "n.omax": 2}),
        ({"jug": "12", "pistas": "3", "rondas": "11"}, {"n.players": 12, "n.rep": 0}),
        ({"jug": "10", "pistas": "2", "rondas": "9", "sc": "15-9,13"}, {"n.rep": 0, "n.top": 15}),
        ({"modo": "mx", "sc": "15-9,13"}, {"n.rounds": 2, "n.c1": ["Ana", "Dani", "Pedro", "Sara"], "n.leader": "Ana"}),
        ({"jug": "Ana, Luis, Marta"}, {"err": "Escribe de 4 a 24 nombres separados por comas, o solo el número de jugadores."}),
        ({"jug": "25"}, {"err": "Como mucho 24 jugadores."}),
    ],
}
