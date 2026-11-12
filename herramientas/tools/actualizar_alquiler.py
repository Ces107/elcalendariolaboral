"""Actualizar el alquiler: annual rent update with the IPC or the IRAV (INE), the last index published at the update
date, and the legal caps (2 % 2022-2023, 3 % 2024, 2 % RDL 29/2026 until 31 Dec 2027)."""

# INE: IPC general nacional, variación anual (serie IPC290750; 2026-10 = indicador adelantado) and IRAV (serie IRAV1).
# Downloaded 12 Nov 2026 from servicios.ine.es/wstempus. Bump "updated" and add a month when INE publishes a new one.
IPC = {'2022-01': 6.1, '2022-02': 7.6, '2022-03': 9.8, '2022-04': 8.3, '2022-05': 8.7, '2022-06': 10.2, '2022-07': 10.8,
       '2022-08': 10.5, '2022-09': 8.9, '2022-10': 7.3, '2022-11': 6.8, '2022-12': 5.7, '2023-01': 5.9, '2023-02': 6.0,
       '2023-03': 3.3, '2023-04': 4.1, '2023-05': 3.2, '2023-06': 1.9, '2023-07': 2.3, '2023-08': 2.6, '2023-09': 3.5,
       '2023-10': 3.5, '2023-11': 3.2, '2023-12': 3.1, '2024-01': 3.4, '2024-02': 2.8, '2024-03': 3.2, '2024-04': 3.3,
       '2024-05': 3.6, '2024-06': 3.4, '2024-07': 2.8, '2024-08': 2.3, '2024-09': 1.5, '2024-10': 1.8, '2024-11': 2.4,
       '2024-12': 2.8, '2025-01': 2.9, '2025-02': 3.0, '2025-03': 2.3, '2025-04': 2.2, '2025-05': 2.0, '2025-06': 2.3,
       '2025-07': 2.7, '2025-08': 2.7, '2025-09': 3.0, '2025-10': 3.1, '2025-11': 3.0, '2025-12': 2.9, '2026-01': 2.3,
       '2026-02': 2.3, '2026-03': 3.4, '2026-04': 3.2, '2026-05': 3.2, '2026-06': 3.2, '2026-07': 3.6, '2026-08': 4.3,
       '2026-09': 4.9, '2026-10': 4.9}
IRAV = {'2024-11': 2.2, '2024-12': 2.28, '2025-01': 2.19, '2025-02': 2.08, '2025-03': 1.98, '2025-04': 2.09, '2025-05': 1.99,
        '2025-06': 2.1, '2025-07': 2.15, '2025-08': 2.19, '2025-09': 2.22, '2025-10': 2.25, '2025-11': 2.29, '2025-12': 2.32,
        '2026-01': 2.14, '2026-02': 2.16, '2026-03': 2.47, '2026-04': 2.4, '2026-05': 2.48, '2026-06': 2.44, '2026-07': 2.49,
        '2026-08': 2.47, '2026-09': 2.54}
PROV = "2026-10"  # IPC flash estimate, final value due 13 Nov 2026
CAPS = [("2022-03-31", "2023-12-31", 2, "RDL 6/2022 y 20/2022"), ("2024-01-01", "2024-12-31", 3, "Ley 12/2023"),
        ("2026-03-22", "2026-04-28", 2, "RDL 8/2026, derogado"), ("2026-10-08", "2027-12-31", 2, "RDL 29/2026")]
MES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
LAU = "https://www.boe.es/buscar/act.php?id=BOE-A-1994-26003"
RDL29 = "https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20823"
INE_IRAV = "https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177092&menu=ultiDatos&idp=1254735976607"
INE_IPC = "https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736176802&menu=ultiDatos&idp=1254735976607"


def mlabel(k):
    return f"{MES[int(k[5:]) - 1]} de {k[:4]}"


def months_desc():
    return sorted(IPC, reverse=True)


def blocks(ctx):
    e, n = ctx.eur, ctx.num
    last_ipc, last_irav = max(IPC), max(IRAV)
    recent = sorted(IPC)[-12:]
    rows = "".join(f"<tr><td>{mlabel(k)}</td><td class=num>{n(IPC[k], 1)} %{' *' if k == PROV else ''}</td>"
                   f"<td class=num>{n(IRAV[k], 2) + ' %' if k in IRAV else '—'}</td></tr>" for k in reversed(recent))
    return [
        ("Cuánto sube el alquiler ahora", f"""
<p>La renta se actualiza una vez al año, en la fecha en que se cumple cada anualidad del contrato, y solo si el contrato lo
prevé. Se multiplica por el índice pactado (el IPC o el IRAV) del <b>último mes publicado</b> en esa fecha. Con los datos
del INE a noviembre de 2026, el IPC interanual de {mlabel(last_ipc)} es del {n(IPC[last_ipc], 1)} % y el IRAV de
{mlabel(last_irav)}, del {n(IRAV[last_irav], 2)} %.</p>
<p>Pero desde el 8 de octubre de 2026 rige el <a href="{RDL29}" rel="noopener">Real Decreto-ley 29/2026</a>: hasta el 31 de
diciembre de 2027, si no hay un nuevo acuerdo con el inquilino, la subida no puede pasar del <b>2 %</b>, y no hay subida
ninguna si la renta ya está por encima del precio de referencia de la zona. Un alquiler de 800 € que se actualiza en
diciembre de 2026 pasa como mucho a {e(816)}, no a {e(800 * (1 + IPC[last_ipc] / 100))}. Es un decreto-ley pendiente de
convalidación: la Diputación Permanente del Congreso lo vota el 12 de noviembre de 2026 y, a esa fecha, el BOE no ha publicado
ni su convalidación ni su derogación. Si se deroga, desmarca «Tope legal» en «Más opciones».</p>
<table class="tbl"><thead><tr><th>Mes del índice</th><th>IPC</th><th>IRAV</th></tr></thead><tbody>{rows}</tbody></table>
<p class="hnote">* Indicador adelantado; el INE publica el dato definitivo a mediados del mes siguiente.</p>"""),
        ("IPC o IRAV: cuál se aplica", f"""
<p>El índice es el que diga el contrato. Los firmados <b>antes del 26 de mayo de 2023</b> suelen remitir al IPC y se
actualizan con él, salvo los topes temporales: un 2 % para las actualizaciones entre el 31 de marzo de 2022 y el 31 de
diciembre de 2023, un 3 % en 2024 y ahora el 2 % del decreto de 2026. Si el contrato no dice nada sobre actualización, la
renta no sube.</p>
<p>En los contratos firmados desde el 26 de mayo de 2023, la Ley 12/2023 añadió al <a href="{LAU}#a18" rel="noopener">artículo 18
de la Ley de Arrendamientos Urbanos</a> que la subida no puede superar el IRAV, el <a href="{INE_IRAV}" rel="noopener">Índice
de Referencia para la Actualización Anual de los Contratos de Arrendamiento de Vivienda</a> que el INE publica cada mes desde
diciembre de 2024. Aunque el contrato diga IPC, con la casilla «Contrato desde 26-5-2023» la calculadora aplica el menor de
los dos. El IRAV se mueve menos que el IPC porque combina la inflación, la inflación subyacente y la evolución de los
alquileres.</p>"""),
        ("Ejemplo paso a paso", f"""
<p>Contrato de 2021 con cláusula de IPC, renta de 950 € y anualidad el 1 de julio de 2026. El 1 de julio el último IPC
publicado era el de mayo de 2026 ({n(IPC["2026-05"], 1)} %), porque el de junio sale a mediados de julio. Nueva renta:
950 × 1,032 = <b>{e(950 * 1.032)}</b>, {e(950 * 0.032)} más al mes y {e(950 * 0.032 * 12)} más al año. Si el mismo contrato
se hubiera firmado en 2024 con IRAV, la referencia sería el IRAV de mayo ({n(IRAV["2026-05"], 2)} %): {e(950 * (1 + IRAV["2026-05"] / 100))}.</p>
<p>La calculadora elige el mes del índice suponiendo que el INE publica cada dato hacia el día 15 del mes siguiente. Si tu
contrato fija otro mes de referencia (por ejemplo, «el IPC de dos meses antes»), elígelo en «Mes del índice».</p>"""),
    ]


FAQ = [
    ("¿Cuánto me pueden subir el alquiler en 2027?",
     "Mientras siga en vigor el Real Decreto-ley 29/2026, como mucho un 2 % en cada actualización hasta el 31 de diciembre de 2027 "
     "salvo nuevo acuerdo, y nada si la renta supera el índice de precios de referencia. Sin ese tope, lo que marque el índice del contrato."),
    ("¿Qué mes del IPC se usa para actualizar la renta?",
     "El último publicado en la fecha de la actualización, salvo que el contrato diga otro. Para una anualidad a principios de mes "
     "suele ser el de dos meses antes; a partir de mediados de mes, el del mes anterior."),
    ("¿Puede bajar el alquiler si el IPC es negativo?",
     "Sí, si la cláusula dice que la renta se actualiza con la variación del IPC, se aplica tanto si sube como si baja. Pasó en "
     "algunas actualizaciones de 2015, 2016 y 2020."),
    ("¿El casero tiene que avisarme?",
     "Sí. La actualización se exige desde el mes siguiente a la notificación por escrito del arrendador, con el porcentaje aplicado "
     "y, si se pide, el certificado del INE (artículo 18 de la LAU)."),
    ("¿Se aplica a los locales comerciales?",
     "No. Los topes y el IRAV son para el alquiler de vivienda. En locales y oficinas se aplica lo que digan las partes en el contrato."),
]

JS = r"""
function (v, H, C) {
  var MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function lab(k) { return MES[+k.slice(5) - 1] + ' de ' + k.slice(0, 4); }
  function prev(k, n) { var y = +k.slice(0, 4), m = +k.slice(5) - n; while (m < 1) { m += 12; y--; } return y + '-' + (m < 10 ? '0' : '') + m; }
  var D = C.d, rent = v.renta, d = v.fecha;
  if (!(rent > 0)) return { err: 'Escribe la renta mensual.' };
  if (!d) return { err: 'Elige la fecha de la actualización.' };
  var dIso = H.iso(d), keys = Object.keys(D.ipc).sort(), last = keys[keys.length - 1], note = [];
  var ref = v.mes !== 'auto' ? v.mes : prev(dIso.slice(0, 7), d.getUTCDate() >= 15 ? 1 : 2);
  if (ref < keys[0]) return { err: 'Solo hay datos desde ' + lab(keys[0]) + '.' };
  var tab = v.idx === 'irav' ? D.irav : D.ipc;
  var tk = Object.keys(tab).sort();
  if (v.idx === 'irav' && ref < tk[0]) return { err: 'El IRAV existe desde ' + lab(tk[0]) + ': usa el IPC para fechas anteriores.' };
  if (ref > tk[tk.length - 1]) { note.push('El índice de ' + lab(ref) + ' aún no está publicado: se usa ' + lab(tk[tk.length - 1]) + '.'); ref = tk[tk.length - 1]; }
  var pct = tab[ref], why = (v.idx === 'irav' ? 'IRAV' : 'IPC') + ' de ' + lab(ref);
  if (ref === D.prov) note.push('El IPC de ' + lab(ref) + ' es el indicador adelantado.');
  if (v.idx === 'ipc' && v.nuevo && D.irav[ref] !== undefined && D.irav[ref] < pct) { pct = D.irav[ref]; why = 'IRAV de ' + lab(ref) + ' (límite del art. 18 LAU)'; }
  if (v.tope) D.caps.forEach(function (c) {
    if (dIso >= c[0] && dIso <= c[1] && pct > c[2]) { pct = c[2]; why = 'tope del ' + c[2] + ' % (' + c[3] + ')'; }
  });
  var nw = H.r2(rent * (1 + pct / 100)), up = H.r2(nw - rent);
  return {
    label: 'Nueva renta', big: H.eur(nw),
    sub: (up >= 0 ? '+' : '') + H.eur(up) + ' al mes · ' + (up >= 0 ? '+' : '') + H.eur(up * 12) + ' al año',
    rows: [['Renta actual', H.eur(rent)], ['Índice aplicado', H.num(pct, Math.round(pct * 100) % 10 ? 2 : Math.round(pct * 100) % 100 ? 1 : 0) + ' %'], ['Referencia', why],
      ['Subida mensual', H.eur(up)], ['Nueva renta', H.eur(nw), 'tot']],
    note: note.join(' '),
    n: { pct: pct, rent: nw, ref: ref }
  };
}
"""

TOOL = {
    "slug": "actualizar-alquiler",
    "lang": "es",
    "cat": "vivienda",
    "icon": "home-dollar",
    "order": 10,
    "name": "Actualizar el alquiler",
    "k": "ipc irav subida renta casero inquilino actualización anual 2026 2027 tope 2%",
    "title": "Actualizar el alquiler con el IPC o el IRAV (2026)",
    "desc": "Calcula la subida anual del alquiler con el IPC o el IRAV del INE y el tope del 2 % del decreto de 2026: nueva renta, subida al mes y al año.",
    "h1": "Actualizar el alquiler con el IPC o el IRAV",
    "updated": "2026-11-12",
    "data": {"ipc": IPC, "irav": IRAV, "prov": PROV, "caps": CAPS},
    "inputs": [
        {"id": "renta", "type": "money", "label": "Renta", "value": 800, "unit": "€/mes"},
        {"id": "fecha", "type": "date", "label": "Actualización", "value": "2026-12-01", "today": True, "min": "2022-01-01", "max": "2027-12-31"},
        {"id": "idx", "type": "seg", "label": "Índice", "value": "ipc", "options": [("ipc", "IPC"), ("irav", "IRAV")]},
        {"id": "nuevo", "type": "check", "label": "Contrato desde 26-5-2023", "value": False},
        {"id": "tope", "type": "check", "label": "Tope legal", "value": True, "more": True},
        {"id": "mes", "type": "select", "label": "Mes del índice", "value": "auto", "more": True,
         "options": [("auto", "Automático")] + [(k, mlabel(k)) for k in months_desc()]},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Real Decreto-ley 29/2026, disposición final sexta (BOE)", RDL29),
                ("Ley 29/1994 de Arrendamientos Urbanos, art. 18 (BOE)", LAU),
                ("INE · Índice de Referencia de Arrendamientos de Vivienda (IRAV)", INE_IRAV),
                ("INE · Índice de Precios de Consumo", INE_IPC)],
    "credits": [("INE · IPC e IRAV (API Tempus)", "datos abiertos, reutilización con cita", "https://www.ine.es/dyngs/DataLab/manual.html?cid=45")],
    "related": ["gastos-compra-vivienda", "intereses-demora", "dividir-gastos", "precio-sin-iva"],
    "tests": [
        ({"renta": "800", "fecha": "2026-11-20"}, {"n.pct": 2, "n.rent": 816, "n.ref": "2026-10"}),
        ({"renta": "800", "fecha": "2026-11-20", "tope": False}, {"n.pct": 4.9, "n.rent": 839.2}),
        ({"renta": "800", "fecha": "2026-06-10"}, {"n.pct": 3.2, "n.rent": 825.6, "n.ref": "2026-04"}),
        ({"renta": "800", "fecha": "2026-06-10", "nuevo": "1"}, {"n.pct": 2.4, "n.rent": 819.2}),
        ({"renta": "1000", "fecha": "2024-05-20", "mes": "2024-04"}, {"n.pct": 3, "n.rent": 1030}),
        ({"renta": "", "fecha": "2026-06-10"}, {"err": "Escribe la renta mensual."}),
    ],
}
