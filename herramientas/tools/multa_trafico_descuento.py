"""Multa de tráfico: 50 % prompt-payment discount and deadlines (LTSV art. 94-95), with the speed-fine table (Anexo IV)."""

LTSV = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11722"
DGT = "https://sede.dgt.gob.es/es/multas/"
CP = "https://www.boe.es/buscar/act.php?id=BOE-A-1995-25444"
# Anexo IV: for each speed limit, the top speed of the 100 €, 300 € (2 pt), 400 € (4 pt) and 500 € (6 pt) bands; above: 600 € (6 pt)
SPEED = {20: [40, 50, 60, 70], 30: [50, 60, 70, 80], 40: [60, 70, 80, 90], 50: [70, 80, 90, 100], 60: [90, 110, 120, 130],
         70: [100, 120, 130, 140], 80: [110, 130, 140, 150], 90: [120, 140, 150, 160], 100: [130, 150, 160, 170],
         110: [140, 160, 170, 180], 120: [150, 170, 180, 190], 130: [150, 170, 180, 190]}


def blocks(ctx):
    rows = "".join(f"<tr><td>{lim}</td><td>{lim + 1}–{u[0]}</td><td>{u[0] + 1}–{u[1]}</td><td>{u[1] + 1}–{u[2]}</td>"
                   f"<td>{u[2] + 1}–{u[3]}</td><td>{u[3] + 1}+</td></tr>" for lim, u in SPEED.items() if lim != 130)
    return [
        ("Pagar la multa con descuento", f"""
<p>Si pagas la multa en los <b>20 días naturales</b> siguientes a la notificación, se reduce un <b>50 %</b>: una de 200 € se queda
en 100 € y una de 500 €, en 250 €. Los 20 días se cuentan desde el día siguiente a recibir la notificación (o a la entrega en mano
de la denuncia por el agente) y valen también sábados, domingos y festivos. Es el <a href="{LTSV}#a94" rel="noopener">procedimiento
abreviado del artículo 94 de la Ley de Tráfico</a>.</p>
<p>A cambio, renuncias a presentar alegaciones y la sanción queda firme el día en que pagas: si crees que la multa es injusta,
solo podrás recurrir ante los tribunales. <b>Los puntos se pierden igual</b>: el descuento solo afecta al dinero. Si no pagas ni
alegas, en 30 días naturales la denuncia se convierte en sanción firme por el importe entero, y si tampoco la pagas, Tráfico la
cobra por vía ejecutiva con un recargo y puede embargar cuentas o la devolución de la renta.</p>"""),
        ("Multas por exceso de velocidad", f"""
<p>El <a href="{LTSV}" rel="noopener">anexo IV de la Ley de Tráfico</a> fija la multa y los puntos según la velocidad
captada por el radar y el límite de la vía. Por ejemplo, a 145 km/h en una autovía de 120 km/h la multa es de 100 € sin puntos
(50 € con pronto pago); a 155 km/h, 300 € y 2 puntos; a 185 km/h, 500 € y 6 puntos. En una calle de 50, ir a 75 son 300 € y
2 puntos.</p>
<table class="tbl"><thead><tr><th>Límite</th><th>100 €</th><th>300 € · 2 pt</th><th>400 € · 4 pt</th><th>500 € · 6 pt</th><th>600 € · 6 pt</th></tr></thead>
<tbody>{rows}</tbody></table>
<p>Superar el límite en más de 60 km/h en vía urbana o de 80 km/h en interurbana ya no es una multa sino un <b>delito</b>
(<a href="{CP}#a379" rel="noopener">artículo 379 del Código Penal</a>), castigado con prisión, multa o trabajos en beneficio de la
comunidad y la retirada del carné de uno a cuatro años.</p>"""),
    ]


FAQ = [
    ("¿Cuántos días tengo para pagar una multa con descuento?",
     "20 días naturales contados desde el día siguiente a la notificación. Si el último día cae en festivo, no se amplía: son días naturales."),
    ("¿Si pago con descuento me quitan los puntos?",
     "Sí. El pronto pago reduce el importe a la mitad, pero la pérdida de puntos se mantiene."),
    ("¿Puedo recurrir una multa después de pagarla con descuento?",
     "En vía administrativa no: al pagar renuncias a las alegaciones. Solo queda el recurso contencioso-administrativo ante un juzgado."),
    ("¿Cuánto es la multa por ir a 140 en una autovía?",
     "100 € sin pérdida de puntos (50 € si pagas en 20 días), porque está entre 121 y 150 km/h en una vía limitada a 120."),
    ("¿Dónde pago una multa de la DGT?",
     "En la sede electrónica de la DGT, en la app miDGT, en Correos, en bancos colaboradores o por teléfono con tarjeta. Las multas "
     "municipales se pagan al ayuntamiento que las pone."),
]

JS = r"""
function (v, H, C) {
  var MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function fmt(d) { return d.getUTCDate() + ' de ' + MES[d.getUTCMonth()] + ' de ' + d.getUTCFullYear(); }
  var fine, pts = 0, what = '', delito = false;
  if (v.tipo === 'vel') {
    var lim = +v.limite, sp = Math.floor(v.velocidad), u = C.d.speed[lim];
    if (!u) return { err: 'Elige el límite de la vía.' };
    if (!(sp > 0)) return { err: 'Escribe la velocidad captada.' };
    if (sp <= lim) return { label: 'Sin multa', big: '0 €', sub: 'No superas el límite de ' + lim + ' km/h.', n: { fine: 0, pts: 0, pay: 0 } };
    var band = [100, 300, 400, 500, 600], pp = [0, 2, 4, 6, 6], k = 0;
    while (k < 4 && sp > u[k]) k++;
    fine = band[k]; pts = pp[k];
    delito = sp - lim > (lim <= 50 ? 60 : 80);
    what = sp + ' km/h en vía de ' + lim + ' · ' + (k < 4 ? 'grave' : 'muy grave');
  } else {
    fine = +v.multa;
    if (!(fine > 0)) return { err: 'Escribe el importe de la multa.' };
  }
  var pay = H.r2(fine / 2), rows = [['Multa', H.eur(fine)], ['Descuento 50 %', '− ' + H.eur(fine - pay)], ['Pagas', H.eur(pay), 'tot']];
  if (v.tipo === 'vel') rows.push(['Puntos', pts ? '−' + pts : '0']);
  var sub = what;
  if (v.notif) {
    var last = H.add(v.notif, 20), firm = H.add(v.notif, 30), left = H.today ? H.diff(H.today(), last) : null;
    rows.push(['Pronto pago hasta', fmt(last)], ['Alegaciones hasta', fmt(last)], ['Firme si no haces nada', fmt(firm)]);
    if (left !== null) sub = (sub ? sub + ' · ' : '') + (left < 0 ? 'plazo de descuento vencido' : 'quedan ' + left + ' ' + H.plural(left, 'día', 'días') + ' para el descuento');
  }
  return {
    label: 'Con pronto pago', big: H.eur(pay), sub: sub, rows: rows,
    note: delito ? 'Ese exceso es delito (art. 379 del Código Penal): no se tramita como multa sino en un juzgado.' : '',
    n: { fine: fine, pts: pts, pay: pay, delito: delito, last: v.notif ? H.iso(H.add(v.notif, 20)) : '' }
  };
}
"""

TOOL = {
    "slug": "multa-trafico-descuento",
    "lang": "es",
    "cat": "vehiculos",
    "icon": "traffic-cone",
    "order": 20,
    "name": "Multa con descuento",
    "k": "pronto pago 50 % dgt plazo 20 días radar exceso velocidad puntos multa tráfico",
    "title": "Multa de tráfico con descuento del 50 %: plazo y importe",
    "desc": "Calcula cuánto pagas por una multa de tráfico con el 50 % de pronto pago y hasta qué día, o la multa y los puntos por exceso de velocidad según el radar.",
    "h1": "Multa de tráfico con pronto pago",
    "updated": "2026-11-12",
    "data": {"speed": SPEED},
    "inputs": [
        {"id": "tipo", "type": "seg", "label": "Multa", "value": "imp", "options": [("imp", "Importe"), ("vel", "Velocidad")]},
        {"id": "multa", "type": "select", "label": "Importe", "value": "200", "show": ("tipo", ["imp"]),
         "options": [("100", "100 € · leve o grave"), ("200", "200 € · grave"), ("300", "300 €"), ("400", "400 €"), ("500", "500 € · muy grave"),
                     ("600", "600 €"), ("1000", "1.000 € · alcohol o drogas")]},
        {"id": "limite", "type": "select", "label": "Límite", "value": "120", "show": ("tipo", ["vel"]),
         "options": [(str(k), f"{k} km/h") for k in SPEED]},
        {"id": "velocidad", "type": "number", "label": "Radar", "value": 145, "unit": "km/h", "w": "s", "show": ("tipo", ["vel"])},
        {"id": "notif", "type": "date", "label": "Notificada el", "value": "", "today": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Ley de Tráfico (RDL 6/2015), arts. 94 y 95 y anexo IV (BOE)", LTSV), ("DGT · Multas", DGT), ("Código Penal, art. 379 (BOE)", CP)],
    "related": ["proxima-itv", "kilometraje-dietas", "etiqueta-dgt", "coste-viaje-coche"],
    "tests": [
        ({"multa": "200", "notif": "2026-11-02"}, {"n.pay": 100, "n.last": "2026-11-22"}),
        ({"tipo": "vel", "limite": "120", "velocidad": "145"}, {"n.fine": 100, "n.pts": 0, "n.pay": 50}),
        ({"tipo": "vel", "limite": "120", "velocidad": "185"}, {"n.fine": 500, "n.pts": 6}),
        ({"tipo": "vel", "limite": "50", "velocidad": "75"}, {"n.fine": 300, "n.pts": 2}),
        ({"tipo": "vel", "limite": "50", "velocidad": "115"}, {"n.fine": 600, "n.delito": True}),
        ({"tipo": "vel", "limite": "90", "velocidad": "90"}, {"n.fine": 0}),
    ],
}
