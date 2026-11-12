"""Frigorías para el aire acondicionado: cooling capacity for a room from m2, ceiling height, sun, people and kitchen,
in frigorías/h, kW and BTU/h, and the commercial split size that covers it. Spanish only."""
from herramientas.tools import _bricolaje as F

ESTAR = "https://www.energystar.gov/products/room_air_conditioners"
RITE = "https://www.boe.es/buscar/act.php?id=BOE-A-2007-15820"

SIZES = [(2.6, 9000), (3.5, 12000), (5.3, 18000), (7.0, 24000)]  # nominal split sizes: kW and BTU/h

JS = r"""
function (v, H, C) {
  var EN = false;
  %FMT%
  if (!(v.m2 > 0)) return { err: 'Escribe los m² de la habitación.' };
  if (!(v.alto > 0)) return { err: 'Escribe la altura del techo.' };
  var hf = Math.max(1, v.alto / 2.7), base = v.m2 * 100 * hf;
  var sun = +v.sol || 0, roof = v.cubierta ? 0.15 : 0;
  var adj = base * (sun + roof);
  var ppl = v.pers > 2 ? (Math.floor(v.pers) - 2) * 150 : 0;
  var kit = v.cocina ? 1000 : 0, eq = v.equipos > 0 ? v.equipos * 0.86 : 0;
  var fr = base + adj + ppl + kit + eq, kw = fr / 860, btu = kw * 3412.14;
  var S = C.d.sizes, pick = null;
  for (var i = 0; i < S.length; i++) if (S[i][0] >= kw - 1e-9) { pick = S[i]; break; }
  var rows = [['Base ' + fv(v.m2, 1) + ' m² × 100' + (hf > 1 ? ' × ' + fv(hf, 2) : ''), fx(base, 0) + ' fg/h']];
  if (sun) rows.push([sun > 0 ? 'Mucho sol' : 'Sombra', (sun > 0 ? '+' : '−') + fx(Math.abs(base * sun), 0) + ' fg/h', 'sub']);
  if (roof) rows.push(['Bajo cubierta', '+' + fx(base * roof, 0) + ' fg/h', 'sub']);
  if (ppl) rows.push(['Personas extra', '+' + fx(ppl, 0) + ' fg/h', 'sub']);
  if (kit) rows.push(['Cocina', '+' + fx(kit, 0) + ' fg/h', 'sub']);
  if (eq) rows.push(['Equipos', '+' + fx(eq, 0) + ' fg/h', 'sub']);
  rows.push(['Total', fx(fr, 0) + ' fg/h', 'tot']);
  rows.push(['Potencia frigorífica', fx(kw, 2) + ' kW · ' + fx(btu, 0) + ' BTU/h']);
  rows.push(['Equipo', pick ? fv(pick[0], 1) + ' kW (' + fx(pick[1], 0) + ' BTU) · ' + fx(pick[0] * 860, 0) + ' fg/h' : 'más de 7 kW: dos equipos o conductos']);
  if (pick) rows.push(['Consumo a plena carga', '≈ ' + fx(pick[0] / 3.3, 2) + ' kW eléctricos']);
  return {
    label: 'Frigorías necesarias', big: fx(fr, 0) + ' fg/h',
    sub: fx(kw, 2) + ' kW · ' + fx(btu, 0) + ' BTU/h',
    rows: rows,
    note: 'Estimación para viviendas con aislamiento normal. Para locales, grandes ventanales o techos muy altos, pide un cálculo de cargas térmicas.',
    n: { fr: r(fr, 1), kw: r(kw, 3), pick: pick ? pick[0] : 0 }
  };
}
"""


def need(m2, alto=2.6, sol=0, roof=False, pers=2, cocina=False, eq=0):
    base = m2 * 100 * max(1, alto / 2.7)
    return base * (1 + sol + (0.15 if roof else 0)) + max(0, pers - 2) * 150 + (1000 if cocina else 0) + eq * 0.86


def blocks(ctx):
    n = F.n
    a = need(20)
    b = need(25, sol=0.10, pers=3)
    rows = "".join(f"<tr><td class=num>{m} m²</td><td class=num>{n(need(m), 0)} fg/h</td><td class=num>{n(need(m) / 860, 1)} kW</td>"
                   f"<td>{next((f'{n(k, 1)} kW' for k, _ in SIZES if k >= need(m) / 860 - 1e-9), 'dos equipos')}</td></tr>"
                   for m in (10, 12, 15, 20, 25, 30, 35, 40, 50, 60))
    return [
        ("Cuántas frigorías necesito", f"""
<p>La regla práctica en España es de <b>100 frigorías por hora y metro cuadrado</b> para una habitación de techo normal
(hasta 2,7 m) en una vivienda con aislamiento corriente. Un dormitorio de 20 m² necesita unas {n(a, 0)} frigorías, o sea
{n(a / 860, 2)} kW de potencia frigorífica: el equipo comercial que lo cubre es el de 2,6 kW (9.000 BTU).</p>
<p>A partir de ahí se corrige. Un salón de 25 m² muy soleado, orientado al sur o al oeste, con tres personas viendo la tele,
sube a {n(b, 0)} frigorías ({n(b / 860, 2)} kW): un 10 % más por el sol y 150 frigorías por la tercera
persona. Con esas cifras el equipo adecuado es el de 3,5 kW (12.000 BTU).</p>
<table class="tbl"><thead><tr><th>Superficie</th><th>Frigorías</th><th>Potencia</th><th>Equipo</th></tr></thead><tbody>{rows}</tbody></table>
<p class="hnote">Techo de 2,6 m, sin correcciones.</p>"""),
        ("Frigorías, kW y BTU", """
<p>Una frigoría es la energía que extrae una kilocaloría de calor, y las «frigorías por hora» son una potencia: 1 kW equivale a
860 frigorías/h y a 3.412 BTU/h. Los fabricantes anuncian los equipos en kW o en BTU (9.000, 12.000, 18.000, 24.000), y la
etiqueta energética europea da la potencia de diseño en kW. Esa potencia frigorífica no es lo que consume: un split moderno
saca unos 3 kW de frío por cada kW eléctrico, así que un equipo de 3,5 kW gasta alrededor de 1 kW a plena carga y bastante
menos cuando el inverter baja el ritmo.</p>"""),
        ("De dónde salen las correcciones", """
<p>Los ajustes son los que publica ENERGY STAR (agencia de protección ambiental de EE. UU.) para dimensionar equipos de aire
acondicionado: un 10 % menos si la habitación está muy sombreada, un 10 % más si es muy soleada, 600 BTU/h (unas 150
frigorías) por cada persona por encima de dos y 4.000 BTU/h (unas 1.000 frigorías) si es una cocina. Además, la calculadora
suma un 15 % si la habitación está bajo cubierta o en un ático, porque el tejado se calienta mucho más que un forjado entre
pisos, y escala la base si el techo pasa de 2,7 m. Los aparatos que dan calor (ordenadores, consolas, televisores grandes)
se suman en «Más opciones» por su potencia: cada vatio son 0,86 frigorías/h.</p>
<p>Un equipo sobredimensionado no enfría mejor: arranca y para a menudo, seca peor el aire y gasta más. En zonas muy
calurosas del interior (valle del Guadalquivir, Murcia, Badajoz) conviene elegir «Mucho sol» aunque la habitación no lo
sea del todo. Las instalaciones térmicas de edificios siguen el Reglamento de Instalaciones Térmicas en los Edificios
(RITE): un instalador habilitado debe montar los equipos partidos con carga de refrigerante.</p>"""),
    ]


FAQ = [
    ("¿Cuántas frigorías necesito para 20 m²?",
     "Unas 2.000 frigorías/h (2,3 kW) con techo normal y sin mucho sol. El equipo comercial más cercano por encima es el de 2,6 kW "
     "(9.000 BTU, unas 2.250 frigorías)."),
    ("¿Cuántos m² enfría un aire de 3.000 frigorías?",
     "Unos 30 m² con la regla de 100 frigorías por m², algo menos si la habitación es muy soleada o está bajo cubierta."),
    ("¿Cuántas frigorías son 12.000 BTU?",
     "12.000 BTU/h son 3,52 kW, unas 3.000 frigorías/h. Un equipo de 9.000 BTU son 2,64 kW (2.270 frigorías)."),
    ("¿Es mejor pasarse de frigorías?",
     "Un poco, sí; mucho, no. Un equipo demasiado grande arranca y para continuamente, deshumidifica peor y consume más."),
    ("¿Cuánta luz gasta un aire acondicionado de 3.000 frigorías?",
     "Alrededor de 1 kW eléctrico a plena potencia; con un inverter y la habitación ya fría, entre 0,3 y 0,6 kW. Mira el consumo "
     "en kWh con la calculadora de consumo de electrodomésticos."),
]

TOOL = {
    "slug": "frigorias-aire-acondicionado",
    "lang": "es",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "air-conditioning",
    "order": 70,
    "name": "Frigorías aire acondicionado",
    "k": "frigorías m2 btu kw split aire acondicionado habitación salón potencia frío",
    "title": "Calcular frigorías del aire acondicionado por m²",
    "desc": "Calcula las frigorías, los kW y los BTU que necesita tu aire acondicionado según los m², el sol, las personas y la altura del techo.",
    "h1": "Calculadora de frigorías para aire acondicionado",
    "updated": "2026-11-12",
    "data": {"sizes": SIZES},
    "inputs": [
        {"id": "m2", "type": "number", "label": "Superficie", "value": "20", "unit": "m²", "step": "0.1"},
        {"id": "alto", "type": "number", "label": "Altura techo", "value": "2,6", "unit": "m", "step": "0.01", "w": "s"},
        {"id": "sol", "type": "seg", "label": "Sol", "value": "0", "options": [("-0.1", "Sombra"), ("0", "Normal"), ("0.1", "Mucho sol")]},
        {"id": "pers", "type": "number", "label": "Personas", "value": "2", "w": "s"},
        {"id": "cocina", "type": "check", "label": "Es cocina", "value": False},
        {"id": "cubierta", "type": "check", "label": "Bajo cubierta", "value": False},
        {"id": "equipos", "type": "number", "label": "Aparatos", "value": "0", "unit": "W", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("ENERGY STAR · Room air conditioners: sizing adjustments (U.S. EPA)", ESTAR),
                ("Reglamento de Instalaciones Térmicas en los Edificios, RD 1027/2007 (BOE)", RITE)],
    "related": ["potencia-contratada", "consumo-electrodomesticos", "seccion-cable", "placas-solares-estimacion"],
    "tests": [
        ({}, {"n.fr": 2000, "n.pick": 2.6}),
        ({"m2": "25", "sol": "0.1", "pers": "3"}, {"n.fr": 2900, "n.pick": 3.5}),
        ({"m2": "25", "sol": "0.1", "pers": "4"}, {"n.fr": 3050, "n.pick": 5.3}),
        ({"m2": "20", "alto": "3,24"}, {"n.fr": 2400}),
        ({"m2": "15", "cocina": True, "cubierta": True}, {"n.fr": 2725, "n.pick": 3.5}),
        ({"m2": "80"}, {"n.pick": 0}),
        ({"m2": ""}, {"err": "Escribe los m² de la habitación."}),
    ],
}
