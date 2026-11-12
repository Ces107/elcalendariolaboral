"""Marco de plantación: plants per hectare (and in a given plot) for a rectangular/square layout (10.000 / (a x b)) or an
equilateral staggered layout, «tresbolillo» (10.000 / (0,866 d²))."""
CAJAMAR = "https://www.cajamar.es/storage/documents/boletin-huerto-27-1496042495-bd7c8.pdf"
ESYRCE = "https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/esyrce/"

PRESETS = [
    ("olt", "Olivar tradicional 10 × 10", "r", 10, 10),
    ("oli", "Olivar intensivo 7 × 5", "r", 7, 5),
    ("ols", "Olivar en seto 4 × 1,5", "r", 4, 1.5),
    ("alm", "Almendro 7 × 6", "r", 7, 6),
    ("pis", "Pistacho 7 × 6", "r", 7, 6),
    ("cit", "Cítricos 6 × 4", "r", 6, 4),
    ("fru", "Frutal en vaso 5 × 3", "r", 5, 3),
    ("vin", "Viña en espaldera 2,5 × 1,2", "r", 2.5, 1.2),
    ("tom", "Tomate 1 × 0,5", "r", 1, 0.5),
    ("pin", "Pinos en tresbolillo 3 m", "t", 3, 3),
]

JS = r"""
function (v, H, C) {
  var tres = v.tipo === 't', a = v.a, b = v.b;
  if (tres) a = b;
  if (!(a > 0) || !(b > 0)) return { err: 'Escribe las distancias en metros.' };
  if (a > 100 || b > 100) return { err: 'Distancias de hasta 100 m.' };
  function f(x) { return H.num(x, 2).replace(/,?0+$/, ''); }
  var per = tres ? b * b * Math.sqrt(3) / 2 : a * b, ha = 1e4 / per;
  var area = v.sup > 0 ? (v.ud === 'm2' ? v.sup : v.sup * 1e4) : 0;
  var rows = [['Superficie por planta', H.num(per, 2) + ' m²']];
  if (tres) rows.push(['Distancia entre filas', H.num(b * Math.sqrt(3) / 2, 2) + ' m'], ['Frente al marco real ' + f(b) + ' × ' + f(b), '+' + H.num(ha - 1e4 / (b * b), 0) + ' plantas/ha']);
  else rows.push(['En un cuadrado de 100 × 100 m', (Math.floor(100 / a + 1e-9) + 1) + ' filas de ' + (Math.floor(100 / b + 1e-9) + 1) + ' plantas']);
  if (area) rows.push(['Plantas en tu parcela', H.num(Math.floor(area / per + 1e-9), 0) + ' en ' + (v.ud === 'm2' ? H.num(area, 0) + ' m²' : H.num(area / 1e4, 2) + ' ha'), 'tot']);
  return { label: tres ? 'Tresbolillo de ' + f(b) + ' m' : 'Marco ' + f(a) + ' × ' + f(b) + ' m', big: H.num(ha, 0) + ' plantas/ha',
    sub: H.num(ha / 100, 2) + ' plantas por área (100 m²)', rows: rows,
    note: 'Sin descontar caminos, cabeceras ni lindes: en una parcela real caben algo menos.',
    n: { ha: H.r2(ha), per: H.r2(per), plot: area ? Math.floor(area / per + 1e-9) : null } };
}
"""


def blocks(ctx):
    rows = "".join(f"<tr><td>{n}</td><td class=\"num\">{ctx.num(10000 / (a * b if t == 'r' else a * a * 0.8660254), 0)}</td></tr>"
                   for _, n, t, a, b in PRESETS)
    return [
        ("Cuántas plantas caben por hectárea", f"""
<p>En un <b>marco real</b> (rectangular o cuadrado) cada planta ocupa un rectángulo de «distancia entre filas × distancia entre
plantas». Una hectárea tiene 10.000 m², así que <b>plantas por hectárea = 10.000 ÷ (a × b)</b>. Un olivar a 7 × 5 m tiene 286
plantas/ha (10.000 ÷ 35); uno tradicional a 10 × 10, cien; un seto a 4 × 1,5, 1.667.</p>
<p>En <b>tresbolillo</b> las plantas forman triángulos equiláteros: cada fila está desplazada media distancia respecto a la anterior
y las filas se acercan a 0,866 veces la distancia entre plantas. Así caben un 15,5 % más de plantas que en un marco cuadrado de la
misma distancia: <b>plantas por hectárea = 10.000 ÷ (0,866 × d²)</b>. A 6 m, son 321 plantas/ha frente a las 278 del 6 × 6.</p>
<table class="tbl"><thead><tr><th>Marco de ejemplo</th><th>Plantas/ha</th></tr></thead><tbody>{rows}</tbody></table>"""),
        ("Ejemplo", """
<p>Una parcela de <b>2,5 ha</b> para almendros a 7 × 6 m: cada árbol ocupa 42 m², la densidad es 10.000 ÷ 42 = <b>238
árboles/ha</b> y en la parcela caben 595. Si la finca son 3 hanegadas de huerta (2.493 m²) y quieres plantar cítricos a 6 × 4 m,
cabrían 103 árboles antes de descontar caminos. Para pedir planta al vivero, suma un 2-3 % para reponer marras.</p>"""),
        ("Cómo elegir el marco", f"""
<p>El marco depende del vigor de la variedad y del patrón, del agua disponible (los marcos estrechos casi siempre necesitan riego),
de la maquinaria que tiene que pasar entre filas y de la forma de poda. Las cifras de la tabla son solo ejemplos habituales; la
densidad recomendada para cada cultivo y variedad la da el vivero o el técnico, y la superficie plantada de cada cultivo en España
está en la encuesta oficial de superficies y rendimientos del Ministerio (<a href="{ESYRCE}" rel="noopener">ESYRCE</a>).</p>
<p>Para replantear un tresbolillo en el campo basta una cuerda con marcas a la distancia elegida: se marca la primera fila, y cada
planta de la fila siguiente va donde se cruzan dos arcos de esa longitud trazados desde las dos plantas vecinas de la fila anterior.
El <a href="{CAJAMAR}" rel="noopener">boletín de huerto de Cajamar</a> lo explica con dibujos.</p>"""),
    ]


FAQ = [
    ("¿Cuántos olivos caben en una hectárea?",
     "Depende del marco: 100 a 10 × 10 m, 204 a 7 × 7 m, 286 a 7 × 5 m y unos 1.667 en seto a 4 × 1,5 m."),
    ("¿Qué es plantar al tresbolillo?",
     "Colocar las plantas de cada fila en el hueco de la fila anterior, formando triángulos equiláteros. Con la misma distancia entre "
     "plantas caben un 15,5 % más que en cuadrado."),
    ("¿Cómo se calcula la distancia de plantación para una densidad?",
     "Divide 10.000 entre la densidad y tendrás los m² por planta. Para 400 plantas/ha, 25 m²: por ejemplo, 5 × 5 m o 6,25 × 4 m."),
    ("¿Cuántas cepas de viña hay por hectárea?",
     "En espaldera a 2,5 × 1,2 m, 3.333 cepas/ha; en vaso tradicional a 2,5 × 2,5 m, 1.600; en marcos de secano más abiertos (3 × 3 m), 1.111."),
    ("¿El cálculo descuenta caminos y cabeceras?",
     "No: da la densidad teórica. En la parcela real hay que dejar cabeceras para girar con el tractor y distancias a lindes, así que "
     "caben algo menos plantas."),
]

TOOL = {
    "slug": "marco-plantacion",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "grid-dots",
    "order": 80,
    "name": "Marco de plantación",
    "k": "plantas por hectarea tresbolillo marco real densidad olivos almendros viña arboles",
    "title": "Marco de plantación: plantas por hectárea y tresbolillo",
    "desc": "Calcula cuántas plantas o árboles caben por hectárea y en tu parcela según el marco de plantación, en marco real o al tresbolillo.",
    "h1": "Calculadora de marco de plantación",
    "crumb": "Marco de plantación",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ej", "type": "select", "label": "Ejemplo", "value": "oli", "custom": "otro",
         "options": [(k, n, {"tipo": t, "a": a, "b": b}) for k, n, t, a, b in PRESETS] + [("otro", "Mi marco")]},
        {"id": "tipo", "type": "seg", "label": "Marco", "value": "r", "options": [("r", "Real"), ("t", "Tresbolillo")]},
        {"id": "a", "type": "number", "label": "Entre filas", "value": 7, "unit": "m", "step": "0.1", "w": "s", "show": ("tipo", ["r"])},
        {"id": "b", "type": "number", "label": "Entre plantas", "value": 5, "unit": "m", "step": "0.1", "w": "s"},
        {"id": "sup", "type": "number", "label": "Parcela", "value": "", "step": "0.01", "w": "s"},
        {"id": "ud", "type": "seg", "label": "En", "value": "ha", "options": [("ha", "ha"), ("m2", "m²")]},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Ministerio de Agricultura · ESYRCE, encuesta de superficies y rendimientos", ESYRCE),
                ("Cajamar · Boletín del huerto, marcos de plantación", CAJAMAR)],
    "related": ["medidas-agrarias", "riego-goteo", "abonado-npk", "calendario-siembra"],
    "tests": [
        ({}, {"n.ha": 285.71, "n.per": 35}),
        ({"a": "10", "b": "10"}, {"n.ha": 100}),
        ({"tipo": "t", "b": "6"}, {"n.ha": 320.75}),
        ({"a": "7", "b": "6", "sup": "2.5"}, {"n.plot": 595}),
        ({"a": "6", "b": "4", "sup": "2493", "ud": "m2"}, {"n.plot": 103}),
        ({"b": "0"}, {"err": "Escribe las distancias en metros."}),
    ],
}
