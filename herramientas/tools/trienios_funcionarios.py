"""Trienios de funcionarios 2026: amount per group (RDL 14/2025 over the extended PGE 2023), monthly, extra pays, year."""

RDL14 = "https://www.boe.es/buscar/act.php?id=BOE-A-2025-24445"
SEPG = ("https://www.sepg.pap.hacienda.gob.es/sitios/sepg/es-ES/CostesPersonal/EstadisticasInformes/Documents/A%c3%91O%202026/"
        "Retribuciones%20del%20personal%20funcionario%202026.%20Real%20Decreto-ley%2014%202025%2c%20de%202%20de%20diciembre..pdf")
LPGE23 = "https://www.boe.es/buscar/act.php?id=BOE-A-2022-22128"
EBEP = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11719"

# 2026, RDL 14/2025 art. 2.1 (SEPG table): group -> (sueldo mensual, trienio mensual, sueldo paga extra, trienio paga extra)
G = {"A1": (1387.24, 53.39, 856.05, 32.96), "A2": (1199.52, 43.54, 874.83, 31.74), "B": (1048.55, 38.20, 906.26, 33.03),
     "C1": (900.63, 32.96, 778.42, 28.45), "C2": (749.58, 22.44, 742.75, 22.20), "E": (686.07, 16.90, 686.07, 16.90)}
NAMES = {"A1": "A1", "A2": "A2", "B": "B", "C1": "C1", "C2": "C2", "E": "E · Agrupaciones profesionales"}


def eur(x):
    return f"{x:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".") + " €"


def table_html():
    rows = "".join(f"<tr><td>{g}</td><td class=\"num\">{eur(t)}</td><td class=\"num\">{eur(te)}</td><td class=\"num\">{eur(t * 12 + te * 2)}</td></tr>"
                   for g, (s, t, se, te) in G.items())
    return ('<table class="tbl"><thead><tr><th>Grupo</th><th>Al mes</th><th>Cada paga extra</th><th>Al año</th></tr></thead>'
            f"<tbody>{rows}</tbody></table><p>Importe de <b>un</b> trienio en 2026. Fuente: tabla de la Secretaría de Estado de "
            "Presupuestos y Gastos para el Real Decreto-ley 14/2025.</p>")


JS = r"""
function (v, H, C) {
  var G = C.d.g;
  function yrs(a, b) { /* full years from a to b */
    var y = b.getUTCFullYear() - a.getUTCFullYear();
    if (b.getUTCMonth() < a.getUTCMonth() || (b.getUTCMonth() === a.getUTCMonth() && b.getUTCDate() < a.getUTCDate())) y--;
    return y;
  }
  function addY(d, n) { var y = d.getUTCFullYear() + n, m = d.getUTCMonth(); return new Date(Date.UTC(y, m, Math.min(d.getUTCDate(), H.monthDays(y, m + 1)))); }
  var n, next = null;
  if (v.modo === 'f') {
    if (!v.inicio) return { err: 'Elige la fecha de inicio de los servicios.' };
    if (!v.ref) return { err: 'Elige la fecha de cálculo.' };
    var y = yrs(v.inicio, v.ref);
    if (y < 0) return { err: 'La fecha de inicio es posterior a la de cálculo.' };
    n = Math.floor(y / 3); next = addY(v.inicio, 3 * (n + 1));
  } else {
    n = v.n;
    if (isNaN(n) || n < 0 || n > 20 || Math.floor(n) !== n) return { err: 'Trienios: un número entero de 0 a 20.' };
  }
  var n2 = v.otro && !isNaN(v.n2) ? v.n2 : 0;
  if (n2 < 0 || n2 > 20 || Math.floor(n2) !== n2) return { err: 'Trienios en otro grupo: de 0 a 20.' };
  var g = G[v.g], g2 = G[v.g2];
  var mes = H.r2(n * g[1] + n2 * g2[1]), extra = H.r2(n * g[3] + n2 * g2[3]), year = H.r2(mes * 12 + extra * 2);
  var rows = [['Un trienio ' + v.g, H.eur(g[1]) + ' /mes']];
  if (n2) rows.push(['Un trienio ' + v.g2, H.eur(g2[1]) + ' /mes']);
  rows.push(['Al mes', H.eur(mes)], ['Paga extra junio', H.eur(extra)], ['Paga extra diciembre', H.eur(extra)], ['Al año · 14 pagas', H.eur(year), 'tot']);
  rows.push(['Sueldo base ' + v.g, H.eur(g[0]) + ' /mes', 'sub']);
  if (next) rows.push(['Próximo trienio', H.iso(next).split('-').reverse().join('/'), 'sub']);
  return {
    label: (n + n2) + ' ' + H.plural(n + n2, 'trienio', 'trienios') + ' al mes', big: H.eur(mes),
    sub: H.eur(year) + ' al año con las pagas extra · 2026',
    rows: rows,
    note: 'Cuantías de 2026 (Real Decreto-ley 14/2025, +1,5 %). Si el IPC de 2026 llega al 1,5 %, subirán otro 0,5 % con atrasos en 2027.',
    n: { n: n, mes: mes, extra: extra, year: year, next: next ? H.iso(next) : null }
  };
}
"""

BLOCKS = [
    ("Cuánto vale un trienio en 2026", f"""
<p>Un trienio de un funcionario del <b>grupo A1 vale 53,39 € al mes</b> en 2026; del A2, 43,54 €; del B, 38,20 €; del C1, 32,96 €;
del C2, 22,44 €, y de las agrupaciones profesionales (antiguo grupo E), 16,90 €. Además, cada una de las dos pagas extra lleva su
parte de trienios, algo menor. La calculadora multiplica esas cuantías por tus trienios y suma, si los tienes, los que cumpliste en
otro grupo, que se cobran siempre con el importe del grupo en que se perfeccionaron.</p>
<p>Si eliges «Fecha», cuenta los trienios completos desde el inicio de tus servicios y te da la fecha del siguiente. Cuenta como
servicio el tiempo trabajado como interino o en otra administración si te lo han reconocido.</p>"""),
    ("Importes por grupo", table_html()),
    ("Ejemplo", """
<p>Una funcionaria del A2 con 5 trienios de A2 y 2 trienios de cuando era C1:</p>
<ul>
<li>Al mes: 5 × 43,54 + 2 × 32,96 = 217,70 + 65,92 = <b>283,62 €</b>.</li>
<li>En cada paga extra: 5 × 31,74 + 2 × 28,45 = 158,70 + 56,90 = 215,60 €.</li>
<li>Al año: 283,62 × 12 + 215,60 × 2 = <b>3.834,64 €</b> brutos.</li>
</ul>"""),
    ("De dónde salen las cuantías", f"""
<p>El <a href="{EBEP}#a23" rel="noopener">artículo 23 del Estatuto Básico del Empleado Público</a> define el trienio como una cantidad
igual para cada subgrupo por cada tres años de servicio, y deja su importe a la Ley de Presupuestos. No hay Presupuestos para 2026:
siguen prorrogados los de 2023 (<a href="{LPGE23}" rel="noopener">Ley 31/2022</a>), y las subidas se han aprobado aparte. El
<a href="{RDL14}" rel="noopener">Real Decreto-ley 14/2025</a> subió las retribuciones un 2,5 % en 2025 y un 1,5 % en 2026 (artículo
2.1), con un 0,5 % más si el IPC de 2026 llega al 1,5 %, que se pagaría con atrasos en el primer trimestre de 2027 tras un Acuerdo
del Consejo de Ministros. Las cuantías de esta página son las de la tabla oficial de la Secretaría de Estado de Presupuestos y
Gastos para ese 1,5 %. Sueldo y trienios son retribuciones básicas: los mismos importes en el Estado, las comunidades autónomas y
los ayuntamientos.</p>"""),
]

FAQ = [
    ("¿Cuánto es un trienio de C1 en 2026?",
     "32,96 € al mes y 28,45 € en cada paga extra: 452,42 € al año por cada trienio."),
    ("¿Cuánto es un trienio de A1 en 2026?",
     "53,39 € al mes y 32,96 € en cada paga extra: 706,60 € al año por cada trienio."),
    ("¿Los interinos cobran trienios?",
     "Sí. El Estatuto Básico del Empleado Público reconoce los trienios al personal interino por el tiempo de servicios prestados."),
    ("Si cambio de grupo, ¿qué pasa con mis trienios?",
     "Conservas los que ya tienes con el importe del grupo en que los cumpliste. Los nuevos se cobran con el importe del grupo nuevo."),
    ("¿Cuándo se empieza a cobrar un trienio nuevo?",
     "Al cumplir los tres años. Como la nómina se calcula con la situación del primer día del mes, normalmente aparece en la nómina del mes siguiente."),
    ("¿Habrá subida de los trienios en 2027?",
     "Depende de la ley que la apruebe: no hay Presupuestos para 2027. Lo seguro es el 0,5 % adicional de 2026 si el IPC del año llega al 1,5 %."),
]

TOOL = {
    "slug": "trienios-funcionarios",
    "lang": "es",
    "cat": "trabajo",
    "icon": "coins",
    "order": 64,
    "name": "Trienios de funcionarios",
    "k": "antigüedad funcionario A1 A2 C1 C2 grupo E interino 2026",
    "title": "Trienios de funcionarios 2026: importe por grupo",
    "desc": "Calcula cuánto cobras por trienios en 2026: A1 53,39 €, A2 43,54 €, C1 32,96 €, C2 22,44 € al mes, con pagas extra y trienios de otro grupo.",
    "h1": "Calculadora de trienios de funcionarios 2026",
    "updated": "2026-11-12",
    "data": {"g": {k: list(v) for k, v in G.items()}},
    "inputs": [
        {"id": "g", "type": "select", "label": "Grupo", "value": "A2", "options": [(k, NAMES[k]) for k in G]},
        {"id": "modo", "type": "seg", "label": "Por", "value": "n", "options": [("n", "Número"), ("f", "Fecha")]},
        {"id": "n", "type": "number", "label": "Trienios", "value": 5, "w": "s", "show": ("modo", ["n"])},
        {"id": "inicio", "type": "date", "label": "Inicio servicios", "value": "2010-09-01", "show": ("modo", ["f"])},
        {"id": "ref", "type": "date", "label": "A fecha", "value": "2026-11-12", "today": True, "show": ("modo", ["f"])},
        {"id": "otro", "type": "check", "label": "Trienios de otro grupo", "value": False, "more": True},
        {"id": "g2", "type": "select", "label": "Otro grupo", "value": "C1", "options": [(k, NAMES[k]) for k in G], "more": True,
         "show": ("otro", ["true"])},
        {"id": "n2", "type": "number", "label": "Trienios ahí", "value": 2, "w": "s", "more": True, "show": ("otro", ["true"])},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Real Decreto-ley 14/2025, art. 2 (BOE-A-2025-24445)", RDL14),
                ("Retribuciones del personal funcionario 2026 (Secretaría de Estado de Presupuestos y Gastos)", SEPG),
                ("Ley 31/2022 de Presupuestos Generales del Estado para 2023 (BOE)", LPGE23), ("Estatuto Básico del Empleado Público, art. 23 (BOE)", EBEP)],
    "related": ["dias-asuntos-propios", "antiguedad-empresa", "fecha-jubilacion"],
    "tests": [
        ({"g": "A2", "n": "5", "otro": "1", "g2": "C1", "n2": "2"}, {"n.mes": 283.62, "n.extra": 215.6, "n.year": 3834.64}),
        ({"g": "A1", "n": "1"}, {"n.mes": 53.39, "n.year": 706.6}),
        ({"g": "E", "n": "0"}, {"n.mes": 0, "n.year": 0}),
        ({"g": "C1", "modo": "f", "inicio": "2010-09-01", "ref": "2026-11-12"}, {"n.n": 5, "n.next": "2028-09-01", "n.mes": 164.8}),
        ({"g": "C2", "modo": "f", "inicio": "2023-11-13", "ref": "2026-11-12"}, {"n.n": 0, "n.next": "2026-11-13"}),
        ({"g": "A1", "n": "-1"}, {"err": "Trienios: un número entero de 0 a 20."}),
    ],
}
