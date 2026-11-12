"""Riego por goteo: total flow of a drip line (plants x drippers x L/h) and daily watering time for a need given in litres
per plant or as ETc = ETo x Kc (FAO 56), with application efficiency."""
FAO56 = "https://www.fao.org/4/x0490e/x0490e00.htm"
SIAR = "https://www.mapa.gob.es/es/desarrollo-rural/temas/gestion-sostenible-regadios/sistema-informacion-agroclimatica-regadio/"
FAOIRR = "https://www.fao.org/4/s8684e/s8684e00.htm"

JS = r"""
function (v, H, C) {
  var pl = v.plantas, g = v.goteros, q = v.caudal, ef = isNaN(v.efic) ? 90 : v.efic;
  if (!(pl > 0)) return { err: 'Escribe cuántas plantas riegas.' };
  if (!(g > 0) || !(q > 0)) return { err: 'Escribe los goteros por planta y su caudal.' };
  if (!(ef > 0 && ef <= 100)) return { err: 'Eficiencia: de 1 a 100 %.' };
  var Q = pl * g * q, net;
  if (v.modo === 'et') {
    if (!(v.sup > 0)) return { err: 'Escribe la superficie regada en m².' };
    if (!(v.eto >= 0) || !(v.kc > 0)) return { err: 'Escribe la ETo y el Kc.' };
    net = v.eto * v.kc * v.sup;
  } else {
    if (!(v.lpd >= 0)) return { err: 'Escribe los litros por planta y día.' };
    net = v.lpd * pl;
  }
  var gross = net / (ef / 100), h = gross / Q, sec = isNaN(v.sectores) || v.sectores < 1 ? 1 : Math.round(v.sectores);
  function hm(x) { var m = Math.round(x * 60); return m < 60 ? m + ' min' : Math.floor(m / 60) + ' h ' + (m % 60 ? m % 60 + ' min' : ''); }
  var rows = [['Caudal del sector', H.num(Q, 0) + ' L/h · ' + H.num(Q / 1000, 2) + ' m³/h'],
    ['Agua por planta', H.num(gross / pl, 2) + ' L/día'], ['Agua al día', H.num(gross, 0) + ' L · ' + H.num(gross / 1000, 2) + ' m³'],
    ['Agua a la semana', H.num(gross * 7 / 1000, 2) + ' m³']];
  if (v.modo === 'et') rows.splice(1, 0, ['Necesidad ETc', H.num(v.eto * v.kc, 2) + ' mm/día · ' + H.num(v.eto * v.kc * v.sup, 0) + ' L netos'],
    ['Pluviometría', H.num(Q / v.sup, 2) + ' mm/h']);
  if (sec > 1) rows.push([sec + ' sectores iguales por turnos', 'programa total ' + hm(h * sec), 'sub']);
  rows.push(['Tiempo de riego', hm(h) + ' al día', 'tot']);
  return { label: 'Tiempo de riego diario', big: hm(h), sub: H.num(Q, 0) + ' L/h · ' + H.num(gross, 0) + ' L al día con ' + H.num(ef, 0) + ' % de eficiencia',
    rows: rows, note: 'Si el tiempo pasa de 2 o 3 horas seguidas, reparte el riego en dos turnos o sube el caudal: en suelo arenoso el agua se pierde por debajo de las raíces.',
    n: { Q: Q, min: H.r2(h * 60), gross: H.r2(gross) } };
}
"""


def blocks(ctx):
    return [
        ("Cuánto tiempo regar con goteo", f"""
<p>El tiempo de riego sale de dividir el agua que necesita cada planta entre lo que le dan sus goteros en una hora:
<b>tiempo (h) = litros por planta ÷ (goteros × caudal del gotero) ÷ eficiencia</b>. Una tomatera con un gotero de 2 L/h que necesita
3 L al día tiene que regar 1 h 40 min (3 ÷ 0,9 = 3,33 L, entre 2 L/h). El caudal del sector, plantas × goteros × caudal, es el que
tiene que dar la bomba o la toma: 50 plantas con un gotero de 2 L/h piden 100 L/h.</p>
<p>La eficiencia (90 % por defecto en goteo) cubre el agua que no llega a las raíces por diferencias de caudal entre goteros,
evaporación o drenaje. Con goteros autocompensantes y la instalación limpia puedes subirla al 95 %; con goteros viejos o en suelo
muy arenoso, bájala al 80-85 %.</p>"""),
        ("Calcular la necesidad con ETo y Kc", f"""
<p>Si no sabes cuántos litros necesita cada planta, calcúlalo como hacen los técnicos de riego: la <b>evapotranspiración del
cultivo</b> es <b>ETc = ETo × Kc</b>. La ETo es la evaporación de un césped de referencia en tu zona y tu día, en milímetros (1 mm =
1 litro por m²); la publican a diario las estaciones del <a href="{SIAR}" rel="noopener">SiAR del Ministerio de Agricultura</a> y
los servicios de riego de cada comunidad. El Kc depende del cultivo y de su fase: según la <a href="{FAO56}" rel="noopener">guía
FAO-56</a>, el tomate en plena producción tiene un Kc de 1,15 y el olivo adulto ronda 0,65-0,70.</p>
<p>Ejemplo: un huerto de 100 m² de tomates con ETo de 6 mm/día y Kc 1,15 consume 6,9 mm, es decir 690 L netos al día; con un 90 %
de eficiencia hay que aportar 767 L. Si las 50 tomateras tienen un gotero de 2 L/h (100 L/h en total), el riego dura 7 h 40 min,
señal de que hacen falta más goteros o más caudal. La pluviometría del sector, 1 mm/h, ayuda a ver esto: el goteo aporta poca agua
por hora y sobre poca superficie.</p>"""),
        ("Consejos y fuentes", f"""
<p>En goteo, la ETc ya cuenta la superficie que mojan las plantas; en árboles jóvenes, que sombrean poco suelo, el riego real es
menor que el de la fórmula. Ajusta el tiempo cada semana (o cada día en verano) con la ETo, descuenta la lluvia útil y vigila la
humedad a la altura de las raíces. El método sigue el manual de <a href="{FAOIRR}" rel="noopener">métodos de riego de la FAO</a> y
la guía FAO-56 (Allen y otros, 1998).</p>"""),
    ]


FAQ = [
    ("¿Cuántos litros echa un gotero en una hora?",
     "Su caudal nominal: los más habituales son de 1,6, 2, 4 y 8 L/h, y viene marcado en el gotero o en la tubería. Para comprobarlo, pon "
     "un vaso debajo durante 6 minutos y multiplica los mililitros por 10."),
    ("¿Cuántos goteros puedo poner en una línea?",
     "Depende del caudal de la toma y del diámetro de la tubería. Suma los caudales: 100 goteros de 2 L/h son 200 L/h, y la toma tiene que "
     "darlos con presión suficiente. Si no llega, divide la instalación en sectores que se rieguen por turnos."),
    ("¿Cuánto tiempo hay que regar un árbol frutal por goteo?",
     "Divide los litros diarios que necesita entre el caudal total de sus goteros. Un árbol que necesita 40 L/día con 4 goteros de 4 L/h "
     "(16 L/h) riega 2 h 47 min con un 90 % de eficiencia."),
    ("¿Qué es la ETo y dónde la consulto?",
     "La evapotranspiración de referencia: el agua, en mm por día, que pierde un césped bien regado en tu zona. La dan las estaciones del "
     "SiAR del Ministerio de Agricultura y los servicios agroclimáticos de las comunidades."),
    ("¿Es mejor regar todos los días o pocos días más tiempo?",
     "En goteo, lo normal es regar a menudo y poco tiempo, para mantener húmedo el bulbo de raíces. En suelos arcillosos se puede espaciar "
     "más; en arenosos, mejor varios riegos cortos al día."),
]

TOOL = {
    "slug": "riego-goteo",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "droplets",
    "order": 70,
    "name": "Riego por goteo",
    "k": "goteros litros hora tiempo de riego caudal huerto eto kc evapotranspiracion",
    "title": "Calculadora de riego por goteo: litros y tiempo de riego",
    "desc": "Calcula el caudal de tu riego por goteo en L/h y cuánto tiempo regar al día según los goteros, los litros por planta o la ETo y el Kc del cultivo.",
    "h1": "Calculadora de riego por goteo",
    "crumb": "Riego por goteo",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "plantas", "type": "number", "label": "Plantas", "value": 50, "w": "s"},
        {"id": "goteros", "type": "number", "label": "Goteros por planta", "value": 1, "w": "s"},
        {"id": "caudal", "type": "number", "label": "Caudal gotero", "value": 2, "unit": "L/h", "step": "0.1", "w": "s"},
        {"id": "modo", "type": "seg", "label": "Necesidad", "value": "lp", "options": [("lp", "Litros por planta"), ("et", "ETo × Kc")]},
        {"id": "lpd", "type": "number", "label": "Por planta", "value": 3, "unit": "L/día", "step": "0.1", "w": "s", "show": ("modo", ["lp"])},
        {"id": "eto", "type": "number", "label": "ETo", "value": 5, "unit": "mm/día", "step": "0.1", "w": "s", "show": ("modo", ["et"])},
        {"id": "kc", "type": "number", "label": "Kc", "value": 1, "step": "0.05", "w": "s", "show": ("modo", ["et"])},
        {"id": "sup", "type": "number", "label": "Superficie", "value": 100, "unit": "m²", "w": "s", "show": ("modo", ["et"])},
        {"id": "efic", "type": "number", "label": "Eficiencia", "value": 90, "unit": "%", "w": "s", "more": True},
        {"id": "sectores", "type": "number", "label": "Sectores iguales", "value": 1, "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("FAO · Evapotranspiración del cultivo, estudio FAO Riego y Drenaje 56", FAO56),
                ("Ministerio de Agricultura · SiAR, Sistema de Información Agroclimática para el Regadío", SIAR),
                ("FAO · Irrigation Water Management: Irrigation Methods", FAOIRR)],
    "credits": [("FAO-56, Allen y otros (1998): ETc = ETo × Kc (fórmula publicada)", "fórmula publicada", FAO56)],
    "related": ["marco-plantacion", "abonado-npk", "calendario-siembra", "medidas-agrarias"],
    "tests": [
        ({}, {"n.Q": 100, "n.min": 100, "n.gross": 166.67}),
        ({"modo": "et", "eto": "6", "kc": "1.15", "sup": "100"}, {"n.gross": 766.67, "n.min": 460}),
        ({"plantas": "1", "goteros": "4", "caudal": "4", "lpd": "40"}, {"n.Q": 16, "n.min": 166.67}),
        ({"plantas": "0"}, {"err": "Escribe cuántas plantas riegas."}),
        ({"efic": "120"}, {"err": "Eficiencia: de 1 a 100 %."}),
    ],
}
