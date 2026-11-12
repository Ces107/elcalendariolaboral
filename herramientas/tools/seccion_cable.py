"""Sección de cable: copper conductor section for a load by admissible current (REBT ITC-BT-19, tabla 1, 40 °C) and by
voltage drop (ITC-BT-19 2.2.2: 3 % / 5 %), with the breaker that coordinates (Ib <= In <= Iz), the ITC-BT-25 minimum of
the circuit and the protective conductor (ITC-BT-19 tabla 2). Spanish only."""
from herramientas.tools import _bricolaje as F

REBT = "https://www.boe.es/buscar/act.php?id=BOE-A-2002-18099"
GUIA = "https://www.plcmadrid.es/wp-content/uploads/rebt/itc19/ITC-BT-19.pdf"

SECS = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
# ITC-BT-19 tabla 1, copper, columns 1..11 (None = not given). Transcribed from the REBT 2002 table.
COLS = {
    2: [11.5, 16, 21, 27, 37, 49, 64, 77, 94],
    3: [13, 17.5, 23, 30, 40, 54, 70, 86, 103],
    4: [13.5, 18.5, 24, 32, 44, 59, 77, 96, 117, 149, 180, 208, 236, 268, 315, 360],
    5: [15, 21, 27, 36, 50, 66, 84, 104, 125, 160, 194, 225, 260, 297, 350, 404],
    6: [16, 22, 30, 37, 52, 70, 88, 110, 133, 171, 207, 240, 278, 317, 374, 423],
    8: [18, 25, 34, 44, 60, 80, 106, 131, 159, 202, 245, 284, 338, 386, 455, 524],
    9: [21, 29, 38, 49, 68, 91, 116, 144, 175, 224, 271, 314, 363, 415, 490, 565],
    10: [24, 33, 45, 57, 76, 105, 123, 154, 188, 244, 296, 348, 404, 464, 552, 640],
}
# installation method -> column for (3 loaded PVC, 2 PVC, 3 XLPE, 2 XLPE)
METHOD = {"A": [2, 3, 5, 6], "B": [4, 5, 8, 9], "C": [5, 6, 8, 9], "E": [6, 8, 9, 10]}
BREAKERS = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250]
GAMMA = {"pvc": 48, "xlpe": 44}  # copper conductivity at 70 °C / 90 °C, m/(ohm·mm2)

JS = r"""
function (v, H, C) {
  var EN = false;
  %FMT%
  var D = C.d, tri = v.fase === 'tri', U = tri ? 400 : 230;
  if (!(v.p > 0)) return { err: 'Escribe la potencia en vatios.' };
  if (!(v.l > 0)) return { err: 'Escribe la longitud del cable.' };
  var cos = v.cos > 0 && v.cos <= 1 ? v.cos : 1, pct = +v.cdt || 3, xl = v.aisl === 'xlpe';
  var Ib = tri ? v.p / (Math.sqrt(3) * U * cos) : v.p / (U * cos);
  var col = D.method[v.met || 'B'][(xl ? 2 : 0) + (tri ? 0 : 1)], iz = D.cols[col];
  var In = null;
  for (var b = 0; b < D.brk.length; b++) if (D.brk[b] >= Ib - 1e-9) { In = D.brk[b]; break; }
  if (In === null) return { err: 'Más de ' + D.brk[D.brk.length - 1] + ' A: es una instalación para proyecto.' };
  function first(minA) { for (var i = 0; i < iz.length; i++) if (iz[i] >= minA - 1e-9) return i; return -1; }
  var iA = first(In);
  if (iA < 0) return { err: 'La intensidad supera la tabla para ese método: elige otro montaje o consulta a un instalador autorizado.' };
  var g = D.gamma[xl ? 'xlpe' : 'pvc'], e = pct / 100 * U;
  var sDrop = tri ? v.l * v.p / (g * e * U) : 2 * v.l * v.p / (g * e * U);
  var iD = -1;
  for (var j = 0; j < D.secs.length; j++) if (D.secs[j] >= sDrop - 1e-9) { iD = j; break; }
  if (iD < 0) return { err: 'La caída de tensión pide más de 300 mm²: acorta el recorrido o sube la tensión.' };
  var circ = D.circ[v.circ] || 0, iC = circ ? D.secs.indexOf(circ) : 0;
  var k = Math.max(iA, iD, iC);
  if (k >= iz.length) return { err: 'Esa sección no está en la tabla para ese montaje: elige otro o consulta a un instalador autorizado.' };
  var S = D.secs[k], why = k === iC && circ && iC > Math.max(iA, iD) ? 'mínimo del circuito (ITC-BT-25)' : k === iD && iD > iA ? 'caída de tensión' : 'intensidad admisible';
  var dU = tri ? v.l * v.p / (g * S * U) : 2 * v.l * v.p / (g * S * U), real = dU / U * 100;
  var pe = S <= 16 ? S : S <= 35 ? 16 : S / 2;
  return {
    label: 'Sección mínima', big: fv(S, 1) + ' mm²', sub: 'Por ' + why + ' · PIA ' + In + ' A',
    rows: [['Intensidad', fx(Ib, 1) + ' A'], ['Por intensidad (Iz ≥ ' + In + ' A)', fv(D.secs[iA], 1) + ' mm² · ' + fv(iz[iA], 1) + ' A'],
      ['Por caída de tensión (' + pct + ' %)', fx(sDrop, 2) + ' mm² → ' + fv(D.secs[iD], 1) + ' mm²'],
      ['Sección', fv(S, 1) + ' mm²', 'tot'], ['Intensidad admisible', fv(iz[k], 1) + ' A (columna ' + col + ')'],
      ['Caída real', fx(dU, 1) + ' V · ' + fx(real, 2) + ' %'], ['Interruptor automático', In + ' A'], ['Conductor de protección', fv(pe, 1) + ' mm²']],
    note: 'Estimación con la tabla 1 de la ITC-BT-19 (cobre, 40 °C, sin agrupar con otros circuitos). Consulta a un instalador autorizado antes de tirar el cable.',
    n: { ib: r(Ib, 3), sA: D.secs[iA], sD: D.secs[iD], s: S, inA: In, pct: r(real, 3) }
  };
}
"""

DATA = {"circ": {"c1": 1.5, "c2": 2.5, "c3": 6, "c4": 4, "c5": 2.5, "c8": 6}, "secs": SECS, "cols": {str(k): v for k, v in COLS.items()}, "method": METHOD, "brk": BREAKERS, "gamma": GAMMA}


def blocks(ctx):
    n = F.n
    sd = 2 * 20 * 3450 / (48 * 0.03 * 230 * 230)
    real = 2 * 20 * 3450 / (48 * 2.5 * 230) / 230 * 100
    rows = "".join(f"<tr><td class=num>{n(s, 1).replace(',0', '')} mm²</td><td class=num>{n(COLS[5][i], 1).replace(',0', '')} A</td>"
                   f"<td class=num>{n(COLS[4][i], 1).replace(',0', '')} A</td><td class=num>{n(COLS[9][i], 1).replace(',0', '')} A</td></tr>"
                   for i, s in enumerate(SECS[:8]))
    return [
        ("Qué sección de cable necesito", f"""
<p>La sección se elige por dos condiciones y gana la más exigente. Primero, el cable debe aguantar la corriente sin
calentarse: la <b>intensidad admisible</b> de la tabla 1 de la ITC-BT-19 del Reglamento Electrotécnico para Baja Tensión,
que depende del montaje y del aislamiento, debe ser al menos la del interruptor automático que lo protege. Segundo, la
<b>caída de tensión</b> no puede pasar del 3 % en los circuitos de una vivienda (en otras instalaciones, 3 % en alumbrado y
5 % en el resto).</p>
<p>Ejemplo: un circuito monofásico de 3.450 W (15 A) de 20 m, con cable de PVC bajo tubo empotrado en obra. Lo protege un
automático de 16 A, y el cable de 1,5 mm² solo admite 15 A, así que hace falta 2,5 mm² (21 A). Por caída de tensión
bastarían {n(sd, 2)} mm². Resultado: <b>2,5 mm²</b>, con una caída real del {n(real, 2)} %.</p>
<table class="tbl"><thead><tr><th>Sección</th><th>Tubo, 2 conductores PVC</th><th>Tubo, 3 conductores PVC</th><th>Tubo, 2 conductores XLPE</th></tr></thead><tbody>{rows}</tbody></table>
<p class="hnote">Intensidades admisibles de la tabla 1 de la ITC-BT-19 para cobre, conductores aislados en tubo en montaje superficial o empotrado en obra (método B), 40 °C.</p>"""),
        ("Las fórmulas", """
<p>La intensidad es I = P ÷ (U × cos φ) en monofásica a 230 V e I = P ÷ (√3 × U × cos φ) en trifásica a 400 V. Para
radiadores, termos y hornos el cos φ es 1; para motores, bombas y aires acondicionados ronda 0,8 o 0,9 (está en la placa del
aparato).</p>
<p>La sección por caída de tensión sale de S = 2 × L × P ÷ (γ × e × U) en monofásica y S = L × P ÷ (γ × e × U) en trifásica,
donde L es la longitud del cable en metros (solo ida), e la caída admisible en voltios y γ la conductividad del cobre a la
temperatura de trabajo: 48 m/(Ω·mm²) con aislamiento de PVC (70 °C) y 44 con XLPE (90 °C). La fórmula desprecia la reactancia
del cable, algo razonable en las secciones pequeñas de una vivienda.</p>"""),
        ("Mínimos del reglamento en viviendas", """
<p>La ITC-BT-25 fija las secciones mínimas de cada circuito de una vivienda, para dos conductores y tierra de PVC bajo tubo:
1,5 mm² y automático de 10 A para iluminación (C1), 2,5 mm² y 16 A para enchufes (C2), 6 mm² y 25 A para cocina y horno (C3),
4 mm² y 20 A para lavadora, lavavajillas y termo (C4), 2,5 mm² y 16 A para baño y cocina (C5), y 6 mm² y 25 A para calefacción
(C8) y aire acondicionado (C9). Elige el circuito en «Más opciones» y la calculadora no baja de ese mínimo.</p>
<p>El conductor de protección (tierra) tiene la misma sección que las fases hasta 16 mm², 16 mm² hasta 35, y la mitad por
encima (ITC-BT-19, tabla 2). Si varios circuitos van por el mismo tubo, o la temperatura es mayor de 40 °C, la intensidad
admisible baja y hacen falta factores de corrección de la norma UNE-HD 60364-5-52: por eso esta calculadora es una
estimación, y una instalación nueva o una ampliación la debe hacer y certificar un instalador autorizado.</p>"""),
    ]


FAQ = [
    ("¿Qué sección de cable para 16 amperios?",
     "2,5 mm² de cobre en una vivienda: con tubo empotrado y PVC admite 21 A. El de 1,5 mm² (15 A) no basta para un automático de 16 A."),
    ("¿Qué cable necesita una placa de inducción?",
     "El circuito de cocina y horno (C3) pide 6 mm² con automático de 25 A según la ITC-BT-25. Si la placa supera 5.750 W, consulta a un instalador autorizado."),
    ("¿Cuánta caída de tensión se admite?",
     "Un 3 % desde el origen de la instalación interior en cualquier circuito de una vivienda. En otras instalaciones, 3 % en alumbrado y 5 % en los demás usos."),
    ("¿Qué sección para un cargador de coche eléctrico de 7,4 kW?",
     "Son 32 A en monofásica: con PVC en tubo, 6 mm² (36 A) como mínimo, más si el recorrido es largo. Lo debe instalar y certificar un instalador autorizado."),
    ("¿Se puede usar cable de 1,5 mm² para enchufes?",
     "No. Los enchufes de uso general (C2) van en 2,5 mm² con automático de 16 A; el 1,5 mm² es para la iluminación (C1)."),
]

TOOL = {
    "slug": "seccion-cable",
    "lang": "es",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "plug-connected",
    "order": 62,
    "name": "Sección de cable",
    "k": "sección cable mm2 rebt itc-bt-19 caída de tensión amperios potencia automático pia cobre monofásica trifásica",
    "title": "Calcular sección de cable (REBT ITC-BT-19)",
    "desc": "Calcula la sección del cable por intensidad admisible y caída de tensión según la ITC-BT-19 del REBT, con el automático que le corresponde.",
    "h1": "Calculadora de sección de cable",
    "updated": "2026-11-12",
    "data": DATA,
    "inputs": [
        {"id": "fase", "type": "seg", "label": "Suministro", "value": "mono", "options": [("mono", "230 V"), ("tri", "400 V trifásica")]},
        {"id": "p", "type": "number", "label": "Potencia", "value": "3450", "unit": "W"},
        {"id": "l", "type": "number", "label": "Longitud", "value": "20", "unit": "m", "step": "0.1"},
        {"id": "cdt", "type": "seg", "label": "Caída máx.", "value": "3", "options": [("3", "3 %"), ("5", "5 %")]},
        {"id": "met", "type": "select", "label": "Montaje", "value": "B",
         "options": [("B", "Tubo empotrado en obra o en superficie"), ("A", "Tubo en pared aislante"), ("C", "Cable sobre la pared"),
                     ("E", "Cable al aire o en bandeja")]},
        {"id": "aisl", "type": "seg", "label": "Aislamiento", "value": "pvc", "options": [("pvc", "PVC"), ("xlpe", "XLPE")]},
        {"id": "cos", "type": "number", "label": "cos φ", "value": "1", "step": "0.01", "w": "s", "more": True},
        {"id": "circ", "type": "select", "label": "Circuito", "value": "0", "more": True,
         "options": [("0", "Ninguno"), ("c1", "C1 iluminación"), ("c2", "C2 enchufes"), ("c3", "C3 cocina y horno"),
                     ("c4", "C4 lavadora y termo"), ("c5", "C5 baño y cocina"), ("c8", "C8/C9 calefacción o aire")]},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("REBT, Real Decreto 842/2002: ITC-BT-19 (tablas 1 y 2, caída de tensión) e ITC-BT-25 (BOE)", REBT)],
    "related": ["potencia-contratada", "consumo-electrodomesticos", "placas-solares-estimacion", "frigorias-aire-acondicionado"],
    "tests": [
        ({}, {"n.ib": 15, "n.sA": 2.5, "n.sD": 2.5, "n.s": 2.5, "n.inA": 16, "n.pct": 2.174}),
        ({"p": "5400", "l": "15"}, {"n.inA": 25, "n.sA": 4, "n.s": 4}),
        ({"p": "5400", "l": "15", "circ": "c3"}, {"n.s": 6}),
        ({"fase": "tri", "p": "15000", "cos": "0,9", "l": "50", "cdt": "5", "met": "E", "aisl": "xlpe"}, {"n.inA": 25, "n.s": 2.5}),
        ({"p": "2000", "l": "60"}, {"n.sA": 1.5, "n.sD": 4, "n.s": 4}),
        ({"p": "14490"}, {"n.inA": 63, "n.sA": 16}),
        ({"l": "0"}, {"err": "Escribe la longitud del cable."}),
    ],
}
