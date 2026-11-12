"""Potencia contratada: recommended contracted power (kW) from the appliances used at the same time, the next value of
the normalised table (BOE 2006), a check against the general breaker (IGA, ITC-BT-10 / ITC-BT-25) and the regulated
yearly cost of the power term (2.0TD peajes 2026 + cargos 2026 + taxes). Spanish only."""
from herramientas.tools import _bricolaje as F

REBT = "https://www.boe.es/buscar/act.php?id=BOE-A-2002-18099"
NORM = "https://www.boe.es/buscar/doc.php?id=BOE-A-2006-16908"
MITECO = "https://www.miteco.gob.es/es/energia/energia-electrica/electricidad/peajes.html"

# Resolución DGPEM 14-3-2006, modified 8-9-2006 (BOE-A-2006-16908): single-phase 230 V, amps -> kW
NORMAL = [(1.5, 0.345), (3, 0.69), (3.5, 0.805), (5, 1.15), (7.5, 1.725), (10, 2.3), (15, 3.45), (20, 4.6), (25, 5.75),
          (30, 6.9), (35, 8.05), (40, 9.2), (45, 10.35), (50, 11.5), (63, 14.49)]
# 2.0TD 2026, €/kW·year: peajes (Resolución CNMC 18-12-2025) + cargos (Orden TED/1524/2025)
P1 = 23.324952 + 4.379461
P2 = 0.443770 + 0.281653
IEE, IVA = 0.0511269632, 0.21
APPS = [("base", "Nevera, luces, TV", 500, True), ("placa", "Placa (2 fuegos)", 3000, True), ("horno", "Horno", 2200, False),
        ("micro", "Microondas", 1200, False), ("lavadora", "Lavadora", 2000, True), ("lavavaj", "Lavavajillas", 1800, False),
        ("secadora", "Secadora", 2500, False), ("termo", "Termo eléctrico", 1500, False), ("hervidor", "Hervidor o cafetera", 2000, False),
        ("plancha", "Plancha o secador", 2000, False), ("aerot", "Aerotermia", 2500, False)]

JS = r"""
function (v, H, C) {
  var EN = false;
  %FMT%
  var D = C.d, rows = [], S = 0;
  D.apps.forEach(function (a) { if (v[a[0]]) { S += a[2]; rows.push([a[1], fx(a[2], 0) + ' W', 'sub']); } });
  var nac = v.aire > 0 ? Math.floor(v.aire) : 0, ncal = v.calef > 0 ? Math.floor(v.calef) : 0, oth = v.otros > 0 ? v.otros : 0;
  if (nac) { S += nac * 1000; rows.push(['Aire acondicionado × ' + nac, fx(nac * 1000, 0) + ' W', 'sub']); }
  if (ncal) { S += ncal * 2000; rows.push(['Calefactores × ' + ncal, fx(ncal * 2000, 0) + ' W', 'sub']); }
  if (oth) { S += oth; rows.push(['Otros', fx(oth, 0) + ' W', 'sub']); }
  var ev = +v.coche || 0, night = ev && v.noche;
  if (ev && !night) { S += ev; rows.push(['Coche eléctrico', fx(ev, 0) + ' W', 'sub']); }
  if (!S) return { err: 'Marca lo que puede funcionar a la vez.' };
  var p1 = Math.ceil(S / 100 - 1e-9) / 10;
  var base = v.base ? 500 : 0, p2 = night ? Math.max(p1, Math.ceil((base + ev) / 100 - 1e-9) / 10) : p1;
  var norm = null;
  for (var i = 0; i < D.norm.length; i++) if (D.norm[i][1] >= p1 - 1e-9) { norm = D.norm[i]; break; }
  rows.push(['Suma a la vez', fx(S, 0) + ' W', 'tot']);
  rows.push(['Potencia punta (P1)', fx(p1, 1) + ' kW', 'tot']);
  if (night) rows.push(['Potencia valle (P2)', fx(p2, 1) + ' kW']);
  rows.push(['Normalizada', norm ? fx(norm[1], 2) + ' kW (' + fv(norm[0], 1) + ' A)' : 'más de 14,49 kW: trifásica']);
  var tax = (1 + D.iee) * (1 + D.iva);
  function cost(a, b) { return (a * D.p1 + b * D.p2) * tax; }
  var c = cost(p1, p2);
  rows.push(['Coste fijo al año', '≈ ' + H.eur(c)]);
  var note = [];
  var cur = v.actual > 0 ? v.actual : 0;
  if (cur) {
    var dlt = cost(cur, cur) - c;
    rows.push(['Con ' + fv(cur, 2) + ' kW', '≈ ' + H.eur(cost(cur, cur)) + (dlt > 0.005 ? ' (ahorras ' + H.eur(dlt) + ')' : dlt < -0.005 ? ' (' + H.eur(-dlt) + ' más)' : '')]);
  }
  var iga = +v.iga || 0, cap = iga * 230 / 1000;
  if (iga && Math.max(p1, p2) > cap + 1e-9) note.push('Tu interruptor general de ' + iga + ' A admite ' + fv(cap, 2) + ' kW: para contratar más hay que adaptar la instalación y emitir un nuevo certificado (consulta a un instalador autorizado).');
  if (p1 > 15) note.push('Más de 15 kW no cabe en la tarifa 2.0TD.');
  note.push('Coste: peajes y cargos 2026 de la tarifa 2.0TD, impuesto eléctrico y IVA; tu comercializadora añade su margen.');
  return {
    label: 'Potencia recomendada', big: fx(p1, 1) + ' kW',
    sub: norm ? 'Normalizada: ' + fx(norm[1], 2) + ' kW' : 'Suministro trifásico',
    rows: rows, note: note.join(' '),
    n: { w: S, p1: p1, p2: p2, norm: norm ? norm[1] : 0, cost: r(c, 2) }
  };
}
"""


def yearly(p1, p2=None):
    p2 = p1 if p2 is None else p2
    return (p1 * P1 + p2 * P2) * (1 + IEE) * (1 + IVA)


def blocks(ctx):
    n, e = F.n, ctx.eur
    rows = "".join(f"<tr><td class=num>{n(a, 1).replace(',0', '')} A</td><td class=num>{n(k, 3 if k < 1 else 2)} kW</td>"
                   f"<td class=num>{e(yearly(k))}</td></tr>" for a, k in NORMAL if k >= 2.3)
    return [
        ("Qué potencia contratar", f"""
<p>Suma la potencia de los aparatos que pueden estar encendidos <b>a la vez</b> y contrata el primer valor que la supere.
La nevera, las luces y la televisión piden unos 500 W; si a la vez cocinas con dos fuegos de la placa (3.000 W) y pones la
lavadora mientras calienta el agua (2.000 W), llegas a 5,5 kW: con 5,75 kW no saltará el limitador, con 4,6 kW sí. Si
puedes esperar a que acabe la lavadora para encender el horno, 4,6 kW bastan.</p>
<p>Cada kilovatio cuesta dinero todo el año aunque no lo uses. Con los peajes y cargos de 2026 de la tarifa 2.0TD, cada kW
en punta paga {n(P1, 2)} € al año y cada kW en valle {n(P2, 2)} €, más el impuesto eléctrico y el IVA: bajar de 5,75 a
4,6 kW ahorra unos {e(yearly(5.75) - yearly(4.6))} al año sin contar el margen de la comercializadora.</p>"""),
        ("Potencias normalizadas", f"""
<p>La tabla de potencias normalizadas para baja tensión (resolución de 14 de marzo de 2006, modificada el 8 de septiembre de
2006) asocia cada calibre del interruptor de control de potencia a 230 V con una potencia. Con los contadores inteligentes el
limitador va dentro del contador y la distribuidora programa la potencia contratada, pero esta tabla sigue siendo la
referencia de casi todas las ofertas.</p>
<table class="tbl"><thead><tr><th>Calibre</th><th>Potencia</th><th>Coste fijo al año*</th></tr></thead><tbody>{rows}</tbody></table>
<p class="hnote">* La misma potencia en punta y en valle, peajes y cargos 2026, impuesto eléctrico (5,11 %) e IVA (21 %),
sin el margen de la comercializadora.</p>"""),
        ("Punta y valle, y el límite de tu instalación", """
<p>Desde junio de 2021 la tarifa 2.0TD permite contratar dos potencias: una para punta y llano (de 8:00 a 24:00 los días
laborables) y otra para el valle (de 0:00 a 8:00 y todo el fin de semana). La potencia de valle cuesta muy poco, por eso, si
cargas el coche eléctrico de noche, marca «Carga de noche»: la calculadora deja el coche fuera de la punta y sube solo la
potencia de valle.</p>
<p>La potencia que puedes contratar tiene un techo: el interruptor general automático (IGA) de tu cuadro. El Reglamento
Electrotécnico para Baja Tensión (ITC-BT-10) prevé al menos 5.750 W por vivienda nueva con electrificación básica y
9.200 W con electrificación elevada (calefacción o aire acondicionado eléctricos, más de 160 m², recarga de coche...).
Si necesitas más de lo que admite tu IGA, hace falta revisar la instalación y emitir un nuevo certificado: consulta a un
instalador autorizado antes de pedir el cambio.</p>"""),
    ]


FAQ = [
    ("¿Cuánta potencia necesita una casa normal?",
     "La mayoría de pisos sin calefacción eléctrica funcionan con 3,45 o 4,6 kW si no se encienden a la vez horno, placa y "
     "lavadora. Con aire acondicionado, termo eléctrico o vitrocerámica de uso intensivo, 5,75 kW."),
    ("¿Qué pasa si me quedo corto de potencia?",
     "El limitador del contador corta el suministro cuando la suma supera la potencia contratada. Se rearma solo o tras apagar algo, "
     "según el contador."),
    ("¿Cuesta dinero cambiar la potencia?",
     "Se pide a la comercializadora. Al subir, la distribuidora puede cobrar derechos de acometida por cada kW nuevo, y si tu "
     "instalación no admite la nueva potencia hará falta un certificado de un instalador. Bajar suele ser más barato, pero piénsalo "
     "bien: volver a subir se paga otra vez."),
    ("¿Cuánto consume un aire acondicionado?",
     "Un split de unas 3.000 frigorías consume alrededor de 1 kW eléctrico en marcha; la calculadora cuenta 1.000 W por equipo."),
    ("¿La potencia contratada es lo mismo que el consumo?",
     "No. La potencia (kW) es lo que puedes tener encendido a la vez y se paga cada día; el consumo (kWh) es la energía que gastas y se "
     "paga por lo usado."),
]

TOOL = {
    "slug": "potencia-contratada",
    "lang": "es",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "bolt",
    "order": 60,
    "name": "Potencia a contratar",
    "k": "potencia contratada kw luz limitador salta icp electrodomésticos 3,45 4,6 5,75 punta valle 2.0td",
    "title": "Qué potencia contratar: calculadora de kW de luz",
    "desc": "Calcula la potencia de luz que necesitas según los electrodomésticos que usas a la vez, la potencia normalizada y su coste fijo al año.",
    "h1": "Calculadora de potencia contratada",
    "updated": "2026-11-12",
    "data": {"apps": [[a[0], a[1], a[2]] for a in APPS], "norm": NORMAL, "p1": P1, "p2": P2, "iee": IEE, "iva": IVA},
    "inputs": [{"id": a[0], "type": "check", "label": a[1], "value": a[3]} for a in APPS] + [
        {"id": "aire", "type": "number", "label": "Aires acond.", "value": "0", "w": "s"},
        {"id": "calef", "type": "number", "label": "Calefactores", "value": "0", "w": "s"},
        {"id": "coche", "type": "select", "label": "Coche eléctrico", "value": "0",
         "options": [("0", "No"), ("2300", "Enchufe 10 A"), ("3680", "Cargador 16 A"), ("7360", "Cargador 32 A")]},
        {"id": "noche", "type": "check", "label": "Carga de noche", "value": True, "show": ("coche", ["2300", "3680", "7360"])},
        {"id": "otros", "type": "number", "label": "Otros", "value": "0", "unit": "W", "more": True},
        {"id": "actual", "type": "number", "label": "Contratada hoy", "value": "", "unit": "kW", "step": "0.01", "more": True},
        {"id": "iga", "type": "select", "label": "Interruptor general", "value": "0", "more": True,
         "options": [("0", "No lo sé"), ("25", "25 A"), ("32", "32 A"), ("40", "40 A"), ("50", "50 A"), ("63", "63 A")]},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("REBT, Real Decreto 842/2002: ITC-BT-10 (previsión de cargas) e ITC-BT-25 (circuitos en viviendas) (BOE)", REBT),
                ("Resolución de 8 de septiembre de 2006, tabla de potencias normalizadas en baja tensión (BOE)", NORM),
                ("MITECO · Peajes (Resolución CNMC 18-12-2025) y cargos (Orden TED/1524/2025) para 2026", MITECO)],
    "related": ["consumo-electrodomesticos", "seccion-cable", "frigorias-aire-acondicionado", "placas-solares-estimacion"],
    "tests": [
        ({}, {"n.w": 5500, "n.p1": 5.5, "n.norm": 5.75}),
        ({"horno": True}, {"n.w": 7700, "n.p1": 7.7, "n.norm": 8.05}),
        ({"placa": False, "lavadora": False, "coche": "7360"}, {"n.p1": 0.5, "n.p2": 7.9, "n.norm": 0.69}),
        ({"coche": "3680", "noche": False}, {"n.w": 9180, "n.p1": 9.2, "n.norm": 9.2}),
        ({"base": False, "placa": False, "lavadora": False}, {"err": "Marca lo que puede funcionar a la vez."}),
        ({"actual": "4,6"}, {"n.cost": 198.87}),
        ({"coche": "7360", "iga": "25"}, {"n.p2": 7.9}),
    ],
}
