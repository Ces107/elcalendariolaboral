"""Coste de una empleada de hogar 2026: Social Security contribution bands of the Sistema Especial (Orden PJC/297/2026)."""

ORDEN = "https://www.boe.es/buscar/act.php?id=BOE-A-2026-7296"
SS = "https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/CotizacionRecaudacionTrabajadores/36537"
LGSS = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11724"
RD1620 = "https://www.boe.es/buscar/act.php?id=BOE-A-2011-17975"
SMI = "https://www.boe.es/buscar/act.php?id=BOE-A-2026-3815"

# Orden PJC/297/2026 art. 15.1: (top of the monthly pay band, contribution base); band 8 = actual pay
BANDS = [(329.00, 306.00), (510.00, 436.00), (693.00, 602.00), (877.00, 785.00), (1061.00, 970.00), (1242.00, 1151.00), (1424.40, 1424.40)]


def eur(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".") + " €"


def bands_html():
    rows, lo = [], 0
    for k, (top, base) in enumerate(BANDS):
        rows.append(f"<tr><td>{k + 1}.º</td><td>{'hasta' if not lo else eur(lo + 0.01) + ' a'} {eur(top)}</td><td class=\"num\">{eur(base)}</td></tr>")
        lo = top
    rows.append(f"<tr><td>8.º</td><td>desde {eur(lo + 0.01)}</td><td class=\"num\">la retribución</td></tr>")
    return ('<table class="tbl"><thead><tr><th>Tramo</th><th>Retribución al mes</th><th>Base</th></tr></thead>'
            f"<tbody>{''.join(rows)}</tbody></table>")


JS = r"""
function (v, H, C) {
  var B = C.d.b, R = C.d.r;
  function base(x) { for (var i = 0; i < B.length; i++) if (x <= B[i][0] + 1e-9) return [i + 1, B[i][1]]; return [8, H.r2(x)]; }
  var s = v.sueldo, h = isNaN(v.horas) ? 40 : v.horas;
  if (!(s > 0)) return { err: 'Escribe el sueldo bruto al mes.' };
  if (!(h > 0 && h <= 40)) return { err: 'Horas semanales: de 1 a 40.' };
  var ret = H.r2(v.pagas === '14' ? s * 14 / 12 : s); /* monthly pay with the extra pays prorated (LGSS art. 147.1) */
  var min = H.r2(C.d.smi12 * h / 40), b1 = base(ret), b2 = base(min), tb = b1[1] >= b2[1] ? b1 : b2, bs = tb[1];
  var red = v.red === '45' ? 0.45 : v.red === '20' ? 0.2 : 0, tmp = v.tipo === 't';
  var e = {
    cc: H.r2(bs * R.ccE * (1 - red)), mei: H.r2(bs * R.meiE), at: H.r2(bs * R.at),
    des: H.r2(bs * (tmp ? R.desEt : R.desE) * (1 - R.bon)), fog: H.r2(bs * R.fog * (1 - R.bon))
  };
  var w = { cc: H.r2(bs * R.ccW), mei: H.r2(bs * R.meiW), des: H.r2(bs * (tmp ? R.desWt : R.desW)) };
  var te = H.r2(e.cc + e.mei + e.at + e.des + e.fog), tw = H.r2(w.cc + w.mei + w.des), cost = H.r2(ret + te);
  return {
    label: 'Te cuesta al mes', big: H.eur(cost),
    sub: H.eur(H.r2(cost * 12)) + ' al año · tramo ' + tb[0] + ' · base ' + H.eur(bs),
    rows: [
      ['Sueldo al mes (con extras)', H.eur(ret)],
      ['Contingencias comunes 23,60 %' + (red ? ' −' + red * 100 + ' %' : ''), H.eur(e.cc)],
      ['Accidentes 1,50 %', H.eur(e.at)],
      ['Desempleo ' + (tmp ? '6,70' : '5,50') + ' % −80 %', H.eur(e.des)],
      ['MEI 0,75 % · FOGASA 0,20 % −80 %', H.eur(H.r2(e.mei + e.fog))],
      ['Cuotas a tu cargo', H.eur(te), 'tot'],
      ['Cuotas de la empleada', H.eur(tw), 'sub'],
      ['Neto para ella al mes', H.eur(H.r2(ret - tw)), 'sub']
    ],
    html: ret < min - 0.005 ? '<p class="herr">Por debajo del salario mínimo para ' + H.num(h, 1).replace(',0', '') + ' h/semana: ' + H.eur(min) + ' al mes con extras.</p>' : '',
    note: 'Tú ingresas todas las cuotas y descuentas su parte del sueldo. Sin retención de IRPF: los hogares no retienen.',
    n: { ret: ret, tramo: tb[0], base: bs, te: te, tw: tw, cost: cost }
  };
}
"""

BLOCKS = [
    ("Cuánto cuesta una empleada de hogar", f"""
<p>Al sueldo se suma la cotización a la Seguridad Social del <b>Sistema Especial para Empleados de Hogar</b>. No se cotiza por el
sueldo exacto sino por la <b>base del tramo</b> en que cae la retribución mensual, contando la parte de las pagas extra. Los ocho
tramos de 2026 los fija el <a href="{ORDEN}#a1-7" rel="noopener">artículo 15 de la Orden PJC/297/2026</a>, con efectos desde el 1
de enero. Sobre esa base pagas un 23,60 % de contingencias comunes, un 1,50 % de accidentes de trabajo, un 0,75 % del mecanismo de
equidad intergeneracional y, con las bonificaciones del 80 %, una parte pequeña del desempleo y del FOGASA. La empleada paga un
4,70 %, un 0,15 % y un 1,55 % (1,60 % con contrato temporal).</p>
<p>Si das de alta a una empleada, tienes una <b>reducción del 20 %</b> en la cuota de contingencias comunes, o del <b>45 %</b> si sois
familia numerosa y la contratas para cuidar de la familia (una persona por familia), según la
<a href="{SS}" rel="noopener">Seguridad Social</a>.</p>"""),
    ("Tramos de cotización 2026", bands_html()),
    ("Ejemplo", """
<p>Una empleada 20 horas a la semana por 700 € al mes más dos pagas extra. Su retribución mensual con extras es 700 × 14 / 12 =
816,67 €: tramo 4.º, base 785 €.</p>
<ul>
<li>Contingencias comunes: 785 × 23,60 % = 185,26 €, menos el 20 % = 148,21 €.</li>
<li>Accidentes: 11,78 €. MEI: 5,89 €. Desempleo: 785 × 5,50 % = 43,18 €, con el 80 % de bonificación = 8,64 €. FOGASA: 0,31 €.</li>
<li>Total a tu cargo: <b>174,83 € al mes</b>. Con el sueldo, te cuesta 991,50 € al mes, <b>11.898 € al año</b>.</li>
<li>Ella paga 50,25 € de cuotas (4,70 % + 0,15 % + 1,55 % de 785 €), que descuentas de su sueldo.</li>
</ul>"""),
    ("Salario mínimo", f"""
<p>El mínimo para una empleada interna o a jornada completa es el SMI de 2026, 1.221 € al mes en 14 pagas, y a tiempo parcial su
parte proporcional (<a href="{SMI}" rel="noopener">Real Decreto 126/2026</a>). Si se le paga por horas en régimen externo, con todo
incluido, el mínimo es de 9,55 € la hora. La Seguridad Social tampoco acepta una base inferior a la del tramo que corresponde al SMI
de tus horas, aunque el sueldo declarado sea menor. La relación laboral se rige por el
<a href="{RD1620}" rel="noopener">Real Decreto 1620/2011</a>.</p>"""),
]

FAQ = [
    ("¿Cuánto se paga a la Seguridad Social por una empleada de hogar?",
     "Depende del tramo de su sueldo. Con 700 € al mes en 14 pagas y la reducción del 20 %, unos 175 € al mes a cargo del empleador y 50 € a cargo de la empleada."),
    ("¿Hay que darla de alta aunque trabaje pocas horas?",
     "Sí, desde la primera hora. El empleador la da de alta antes de que empiece a trabajar, en Importass o en la sede de la Seguridad Social."),
    ("¿Quién paga la Seguridad Social, la familia o la empleada?",
     "La familia ingresa todas las cuotas cada mes y descuenta del sueldo la parte que corresponde a la empleada."),
    ("¿Tengo que retenerle IRPF?",
     "No. Los hogares no tienen obligación de retener. La empleada declara su sueldo en la renta si supera los límites."),
    ("¿Qué tramo me corresponde si pago por horas?",
     "Multiplica lo que pagas por hora por las horas del mes, y busca ese importe en la tabla. Si el pago por horas ya incluye las pagas extra, elige «12» en Pagas."),
    ("¿Las empleadas de hogar cotizan por desempleo?",
     "Sí, desde octubre de 2022. El empleador tiene una bonificación del 80 % en su parte del desempleo y del FOGASA."),
]

TOOL = {
    "slug": "coste-empleada-hogar",
    "lang": "es",
    "cat": "trabajo",
    "icon": "home-heart",
    "order": 67,
    "name": "Coste empleada de hogar",
    "k": "seguridad social cuota cotización tramos 2026 interna externa por horas",
    "title": "Coste de empleada de hogar 2026: cuotas Seguridad Social",
    "desc": "Calcula cuánto te cuesta una empleada de hogar en 2026: tramo y base de cotización, cuotas a tu cargo y a cargo de ella, reducción del 20 % o 45 %.",
    "h1": "Coste de una empleada de hogar 2026",
    "updated": "2026-11-12",
    "data": {"b": [list(x) for x in BANDS], "smi12": 1424.50,
             "r": {"ccE": 0.236, "ccW": 0.047, "meiE": 0.0075, "meiW": 0.0015, "at": 0.015, "desE": 0.055, "desW": 0.0155,
                   "desEt": 0.067, "desWt": 0.016, "fog": 0.002, "bon": 0.8}},
    "inputs": [
        {"id": "sueldo", "type": "money", "label": "Sueldo bruto al mes", "value": 700},
        {"id": "pagas", "type": "seg", "label": "Pagas", "value": "14", "options": [("14", "14"), ("12", "12")]},
        {"id": "horas", "type": "number", "label": "Horas semanales", "value": 20, "unit": "h", "w": "s"},
        {"id": "red", "type": "select", "label": "Reducción", "value": "20",
         "options": [("20", "20 % · alta"), ("45", "45 % · familia numerosa"), ("0", "Ninguna")]},
        {"id": "tipo", "type": "seg", "label": "Contrato", "value": "i", "options": [("i", "Indefinido"), ("t", "Temporal")], "more": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Orden PJC/297/2026, de 30 de marzo, de cotización 2026, arts. 15, 16 y 35 (BOE-A-2026-7296)", ORDEN),
                ("Seguridad Social · Sistema Especial para Empleados de Hogar", SS),
                ("Ley General de la Seguridad Social, art. 147 y DA 61ª, tarifa de accidentes (BOE)", LGSS),
                ("Real Decreto 126/2026, salario mínimo (BOE)", SMI), ("Real Decreto 1620/2011 (BOE)", RD1620)],
    "related": ["smi-jornada-parcial", "calculadora-finiquito", "horas-extra"],
    "tests": [
        ({"sueldo": "700", "pagas": "14", "horas": "20"}, {"n.ret": 816.67, "n.tramo": 4, "n.base": 785, "n.te": 174.83, "n.tw": 50.25, "n.cost": 991.5}),
        ({"sueldo": "1424,50", "pagas": "12", "horas": "40", "red": "0"}, {"n.tramo": 8, "n.base": 1424.5}),
        ({"sueldo": "300", "pagas": "12", "horas": "20"}, {"n.tramo": 4, "n.base": 785}),
        ({"sueldo": "250", "pagas": "12", "horas": "5"}, {"n.tramo": 1, "n.base": 306}),
        ({"sueldo": "0"}, {"err": "Escribe el sueldo bruto al mes."}),
    ],
}
