"""Lotería de Navidad: what a prize leaves after the special 20 % tax above 40,000 EUR per décimo (LIRPF DA 33ª)."""

LIRPF = "https://www.boe.es/buscar/act.php?id=BOE-A-2006-20764#datrigesimatercera"
SELAE = "https://www.loteriasyapuestas.es/es/loteria-nacional"
EXEMPT, RATE, PRICE = 40000, 0.20, 20
PRIZES = [  # value, label, prize per 20 EUR décimo (Sorteo Extraordinario de Navidad, programme per serie / 10)
    ("gordo", "Gordo · 1.º premio", 400000),
    ("p2", "2.º premio", 125000),
    ("p3", "3.er premio", 50000),
    ("p4", "4.º premio", 20000),
    ("p5", "5.º premio", 6000),
    ("a1", "Aproximación al Gordo", 2000),
    ("a2", "Aproximación al 2.º", 1250),
    ("a3", "Aproximación al 3.º", 960),
    ("ped", "Pedrea · centena · terminación", 100),
    ("rei", "Reintegro", 20),
]


def net(prize, share=1.0):
    gross = prize * share
    tax = RATE * max(0.0, gross - EXEMPT * share)
    return gross, tax, gross - tax


def blocks(ctx):
    e = ctx.eur
    rows = "".join(f"<tr><td>{lab}</td><td class=num>{e(p, 0)}</td><td class=num>{e(net(p)[1], 0)}</td><td class=num><b>{e(net(p)[2], 0)}</b></td></tr>"
                   for _, lab, p in PRIZES)
    g, t, n = net(400000, 2.5 / 20)
    g4, t4, n4 = net(400000, 1 / 4)
    return [
        ("Cuánto se cobra de cada premio", f"""
<p>Del <b>Gordo de Navidad</b> (400.000 € al décimo de 20 €) cobras <b>328.000 €</b>: los primeros 40.000 € están exentos y
Hacienda retiene el 20 % de los 360.000 € restantes, 72.000 €. El banco o la administración te paga ya el neto, así que no
tienes que hacer nada más. Los premios de 40.000 € o menos por décimo (el 4.º y el 5.º premio, la pedrea, las aproximaciones
y el reintegro) se cobran enteros.</p>
<table class="tbl"><thead><tr><th>Premio (décimo de 20 €)</th><th>Bruto</th><th>Hacienda</th><th>Cobras</th></tr></thead>
<tbody>{rows}</tbody></table>
<p>El sorteo del 22 de diciembre de 2026 reparte por serie 4 millones al primer premio, 1,25 millones al segundo, 500.000 € al
tercero, 200.000 € a cada uno de los dos cuartos y 60.000 € a cada uno de los ocho quintos. Cada serie tiene diez décimos, de
ahí los importes por décimo de la tabla. Son los importes del programa de los últimos años; para 2026 Loterías anuncia 205
series y 2.870 millones en premios (el 70 % de la emisión, 14 millones por serie, como ese programa), pero <b>no hemos podido
consultar el programa oficial de 2026</b>: compruébalo en <a href="{SELAE}" rel="noopener">loteriasyapuestas.es</a>.</p>"""),
        ("Participaciones y décimos compartidos", f"""
<p>La exención de 40.000 € es <b>por décimo</b>, no por persona: si el décimo se reparte, cada uno tiene exenta la parte que le
toca. Una participación de 3 € que «juega 2,50 €» es la octava parte de un décimo: del Gordo le corresponden
{e(g, 0)}, tiene exentos {e(EXEMPT * 2.5 / 20, 0)} y paga el 20 % de {e(g - EXEMPT * 2.5 / 20, 0)}, es decir {e(t, 0)}; cobra
<b>{e(n, 0)}</b>. Los 0,50 € restantes de la participación son el donativo o recargo del club o la peña y no juegan.</p>
<p>Si cuatro amigos compran un décimo a medias de 5 € cada uno, cada uno cobra {e(n4, 0)} del Gordo ({e(g4, 0)} brutos menos
{e(t4, 0)} de retención). El total que cobran los cuatro es el mismo que el del décimo entero: 328.000 €. Para que la
retención se reparta bien, conviene ir juntos al banco o declarar la titularidad compartida al cobrar, como prevé la ley.</p>"""),
        ("Qué dice la ley", f"""
<p>Es el <a href="{LIRPF}" rel="noopener">gravamen especial sobre los premios de determinadas loterías y apuestas</a>, la
disposición adicional trigésima tercera de la Ley 35/2006 del IRPF. Se aplica de forma independiente a cada décimo, fracción o
cupón premiado; están exentos los premios de hasta 40.000 € y, por encima, tributa al 20 % solo la parte que excede. Si el
premio es de titularidad compartida, la parte exenta y la base se reparten entre los cotitulares según su cuota.</p>
<p>La entidad que paga practica una retención del 20 % que coincide con el impuesto, de modo que no hay que presentar la
autoliquidación ni sumar el premio en la declaración de la renta: estos premios no se integran en la base imponible del IRPF.
La misma regla vale para la Lotería del Niño, la Primitiva, el Euromillones, la ONCE y los sorteos de la Cruz Roja.</p>"""),
    ]


FAQ = [
    ("¿Cuánto se lleva Hacienda del Gordo de Navidad?",
     "72.000 € por décimo: el 20 % de lo que pasa de 40.000 €. De los 400.000 € brutos cobras 328.000 €, el 82 % del premio."),
    ("¿Tengo que declarar el premio en la renta?",
     "No. El banco retiene el 20 % al pagarte y con eso queda pagado el gravamen especial. El premio no se suma a la base del IRPF; "
     "lo que hagas después con el dinero (por ejemplo, los intereses que genere) sí tributa como cualquier otro ingreso."),
    ("¿La exención de 40.000 € es por persona o por décimo?",
     "Por décimo. Si tienes dos décimos premiados del mismo número, cada uno tiene su exención de 40.000 €. Si compartes un décimo, "
     "cada titular tiene exenta su parte proporcional."),
    ("¿Cuánto cobra una participación de 5 € del Gordo?",
     "Depende de lo que juegue. Si juega 4 € (un quinto del décimo), le tocan 80.000 € brutos, tiene exentos 8.000 € y paga 14.400 €: "
     "cobra 65.600 €. Mira en la participación el importe que juega, no el precio pagado."),
    ("¿Dónde y hasta cuándo se cobra?",
     "Los premios de hasta 2.000 € por décimo se cobran en cualquier administración de lotería; los mayores, en las entidades "
     "bancarias colaboradoras. Hay tres meses desde el día siguiente al sorteo; después el premio caduca."),
]

JS = r"""
function (v, H, C) {
  var EX = 40000, RATE = 0.2;
  var pd = v.pd, play = v.jugado, price = v.precio, n = v.n, people = v.pers;
  if (!(pd >= 0)) return { err: 'Escribe el premio por décimo.' };
  if (!(price > 0)) return { err: 'Precio del décimo: mayor que 0.' };
  if (!(play > 0)) return { err: 'Juegas: importe mayor que 0.' };
  if (play > price + 1e-9) return { err: 'Juegas: como mucho el precio del décimo (' + H.eur(price) + ').' };
  if (!(n >= 1) || n % 1) return { err: 'Décimos: un número entero desde 1.' };
  if (!(people >= 1) || people % 1) return { err: 'Personas: un número entero desde 1.' };
  var exMax = price < 0.5 ? EX * price / 0.5 : EX;        /* DA 33.2: bets under 0.50 EUR, proportional exemption */
  var share = play / price / people;                       /* part of ONE décimo that is yours */
  var gross = H.r2(pd * share * n), exempt = H.r2(Math.min(gross, exMax * share * n));
  var base = H.r2(Math.max(0, gross - exempt)), tax = H.r2(base * RATE), net = H.r2(gross - tax);
  var pct = gross > 0 ? tax / gross * 100 : 0;
  return {
    label: 'Cobras', big: H.eur(net),
    sub: tax > 0 ? 'Hacienda retiene ' + H.eur(tax) + ' · ' + H.num(pct, 1) + ' % del premio' : 'Sin retención: no pasa de ' + H.eur(exMax * share * n),
    rows: [['Premio bruto', H.eur(gross)], ['Exento', H.eur(exempt)], ['Base del gravamen', H.eur(base)],
      ['Retención 20 %', '− ' + H.eur(tax)], ['Neto', H.eur(net), 'tot']],
    note: share < 1 ? 'Tu parte: ' + H.num(share * 100, share * 100 % 1 ? 2 : 0) + ' % de ' + (n > 1 ? n + ' décimos' : 'un décimo') + '.' : '',
    n: { gross: gross, exempt: exempt, tax: tax, net: net }
  };
}
"""

TOOL = {
    "slug": "loteria-navidad-premio-neto",
    "lang": "es",
    "cat": "dinero",
    "icon": "ticket",
    "order": 10,
    "name": "Premio neto lotería",
    "k": "gordo navidad niño décimo participación hacienda impuesto 20 retención 40000",
    "title": "Lotería de Navidad 2026: cuánto se cobra del premio",
    "desc": "Calcula cuánto cobras del Gordo y del resto de premios de la Lotería de Navidad 2026 tras el 20 % de Hacienda: décimo, participación o décimo compartido.",
    "h1": "Premio neto de la Lotería de Navidad",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "premio", "type": "select", "label": "Premio", "value": "gordo", "custom": "x",
         "options": [(v, lab, {"pd": p}) for v, lab, p in PRIZES] + [("x", "Otro importe")]},
        {"id": "pd", "type": "money", "label": "Por décimo", "value": 400000, "w": "l"},
        {"id": "jugado", "type": "money", "label": "Juegas", "value": 20, "w": "s"},
        {"id": "pers", "type": "number", "label": "Personas", "value": 1, "w": "s", "min": 1},
        {"id": "n", "type": "number", "label": "Décimos", "value": 1, "more": True, "w": "s", "min": 1},
        {"id": "precio", "type": "money", "label": "Precio del décimo", "value": PRICE, "more": True, "w": "s"},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Ley 35/2006 del IRPF, disposición adicional 33.ª (BOE)", LIRPF),
                ("Loterías y Apuestas del Estado · Lotería Nacional", SELAE)],
    "related": ["amigo-invisible", "precio-sin-iva", "dividir-gastos", "cuenta-atras"],
    "tests": [
        ({"pd": "400000"}, {"n.gross": 400000, "n.tax": 72000, "n.net": 328000}),
        ({"pd": "400000", "jugado": "2,5"}, {"n.gross": 50000, "n.exempt": 5000, "n.tax": 9000, "n.net": 41000}),
        ({"pd": "400000", "pers": "4"}, {"n.gross": 100000, "n.tax": 18000, "n.net": 82000}),
        ({"pd": "125000", "n": "3"}, {"n.gross": 375000, "n.exempt": 120000, "n.tax": 51000, "n.net": 324000}),
        ({"pd": "6000"}, {"n.tax": 0, "n.net": 6000}),
        ({"pd": "400000", "jugado": "25"}, {"err": "Juegas: como mucho el precio del décimo (20,00 €)."}),
    ],
}
