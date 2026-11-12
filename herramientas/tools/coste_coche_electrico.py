"""Coste del coche eléctrico: €/100 km charging at home vs public chargers (user prices), monthly cost, comparison with a
combustion car and charging time by charger power."""

WLTP = "https://eur-lex.europa.eu/eli/reg/2017/1151/oj"
REBT = "https://www.boe.es/buscar/act.php?id=BOE-A-2002-18099"

BLOCKS = [
    ("Cuánto cuesta cada 100 km", """
<p>Un coche eléctrico gasta energía en kWh, como el horno o la lavadora. El coste cada 100 km es <b>consumo (kWh/100 km) ×
precio del kWh</b>, más lo que se pierde al cargar. La gracia está en el precio: el kWh de tu tarifa de casa, sobre todo en
horas valle, puede costar la tercera parte o menos que el de un cargador rápido de autopista. Por eso el dato clave no es el
coche sino <b>qué parte cargas en casa</b>.</p>
<p>Ejemplo con precios de muestra (pon los tuyos, la calculadora no trae tarifas): un compacto que gasta 16 kWh/100 km, con
un 10 % de pérdidas, consume 17,6 kWh de la red cada 100 km. A 0,15 €/kWh en casa son 2,64 €; a 0,49 €/kWh en un punto
público, 8,62 €. Si el 80 % de los kilómetros los cargas en casa, la media sale a 3,84 € cada 100 km, y con 1.000 km al mes,
38,37 €. Un coche de gasolina de 6,5 l/100 km con el litro a 1,55 € gastaría 100,75 € en esos mismos kilómetros.</p>"""),
    ("Tiempo de carga", f"""
<p>El tiempo es la energía que falta dividida entre la potencia del cargador. Para pasar una batería de 60 kWh del 20 % al
80 % hacen falta 36 kWh en la batería y unos 39,6 kWh de la red; con un wallbox de 7,4 kW son unas 5 h 21 min, con un enchufe
doméstico de 2,3 kW, más de 17 horas, y en un cargador rápido de 100 kW, unos 24 minutos en teoría.</p>
<p>Dos límites lo alargan en la práctica. En corriente alterna (casa, wallbox, cargadores de 11 o 22 kW de la calle) manda el
cargador de a bordo del coche: si admite 7,4 kW, un poste de 22 kW no carga más deprisa. En corriente continua la potencia
baja a medida que la batería se llena, sobre todo por encima del 80 %, por eso en ruta conviene cargar del 10-20 % al 80 % y
seguir. La instalación de un punto de recarga en casa debe cumplir la instrucción ITC-BT-52 del
<a href="{REBT}" rel="noopener">Reglamento Electrotécnico para Baja Tensión</a>; un instalador autorizado te dirá si basta con
tu potencia contratada.</p>"""),
    ("De dónde sale el consumo", f"""
<p>El consumo homologado del eléctrico (kWh/100 km en la ficha técnica) se mide con el ciclo WLTP del
<a href="{WLTP}" rel="noopener">Reglamento (UE) 2017/1151</a> e incluye la energía tomada de la red, es decir, ya cuenta las
pérdidas de carga: si usas ese dato, pon «Pérdidas» a 0. El dato del ordenador de a bordo, en cambio, suele medir lo que sale
de la batería, y ahí sí conviene sumar un 10-15 %. En invierno, con calefacción y la batería fría, el consumo sube; en
autopista a 120 km/h también.</p>"""),
]

FAQ = [
    ("¿Cuánto cuesta cargar un coche eléctrico en casa?",
     "La energía que falta por el precio de tu kWh. Llenar 40 kWh a 0,15 €/kWh cuesta unos 6,60 € contando un 10 % de pérdidas. "
     "Mira el precio del kWh en tu factura, en el periodo en que cargues."),
    ("¿Cuántos kWh gasta un eléctrico cada 100 km?",
     "Entre 13 y 17 kWh un compacto o un utilitario; un SUV grande o una furgoneta, de 18 a 25 kWh. En autopista y con frío, más."),
    ("¿Cuánto tarda en cargar con un enchufe normal?",
     "Un enchufe doméstico da unos 2,3 kW: unos 13 km de autonomía por hora de carga en un compacto de 16 kWh/100 km. Sirve para ir cargando por la "
     "noche, no para llenar una batería grande."),
    ("¿Qué potencia de wallbox necesito?",
     "Para cargar de noche, 7,4 kW (32 A en monofásico) es la más común. Más potencia solo sirve si el cargador de a bordo del "
     "coche la admite y la instalación de casa la soporta."),
    ("¿Por qué el cargador rápido no carga a su potencia máxima?",
     "Porque la batería acepta menos potencia cuando está fría o casi llena. La potencia máxima solo se alcanza un rato, con la "
     "batería templada y por debajo del 50-60 %."),
]

JS = r"""
function (v, H, C) {
  var c = v.cons, km = isNaN(v.km) ? 0 : v.km, pc = v.pcasa, pp = v.ppub, sh = isNaN(v.casa) ? 100 : v.casa, l = isNaN(v.perd) ? 0 : v.perd;
  if (isNaN(c) || c <= 0) return { err: 'Escribe el consumo en kWh/100 km.' };
  if (c > 100) return { err: 'Consumo en kWh cada 100 km (por ejemplo 16).' };
  if (sh < 0 || sh > 100) return { err: '% en casa: de 0 a 100.' };
  if (isNaN(pc) && sh > 0) return { err: 'Escribe el precio del kWh en casa.' };
  if (isNaN(pp) && sh < 100) return { err: 'Escribe el precio del kWh en el punto de carga.' };
  if (pc < 0 || pp < 0 || km < 0 || l < 0) return { err: 'Sin números negativos.' };
  var f = 1 + l / 100, eh = sh > 0 ? c * f * pc : 0, ep = sh < 100 ? c * f * pp : 0, mix = eh * sh / 100 + ep * (1 - sh / 100);
  var rows = [];
  if (sh > 0) rows.push(['Cargando en casa', H.eur(H.r2(eh)) + ' /100 km']);
  if (sh < 100) rows.push(['En punto público', H.eur(H.r2(ep)) + ' /100 km']);
  if (sh > 0 && sh < 100) rows.push(['Media (' + H.num(sh, 0) + ' % en casa)', H.eur(H.r2(mix)) + ' /100 km', 'tot']);
  var mon = km / 100 * mix, comb = null;
  if (km) rows.push(['Al mes · ' + H.num(km, 0) + ' km', H.eur(H.r2(mon)), 'tot']);
  if (!isNaN(v.lcomb) && v.lcomb > 0 && !isNaN(v.pcomb) && v.pcomb > 0) {
    comb = v.lcomb * v.pcomb;
    rows.push(['Coche de combustión', H.eur(H.r2(comb)) + ' /100 km', 'sub']);
    if (km) rows.push(['Ahorro al mes', H.eur(H.r2(km / 100 * (comb - mix))), 'z']);
  }
  var html = '', ch = null;
  if (!isNaN(v.bat) && v.bat > 0 && !isNaN(v.kw) && v.kw > 0) {
    var a = isNaN(v.desde) ? 0 : v.desde, b = isNaN(v.hasta) ? 100 : v.hasta;
    if (a < 0 || b > 100 || a >= b) return { err: 'Carga: «Desde» menor que «Hasta», entre 0 y 100 %.' };
    var eb = v.bat * (b - a) / 100, eg = eb * f, t = eg / v.kw, hh = Math.floor(t), mm = Math.round((t - hh) * 60);
    if (mm === 60) { hh++; mm = 0; }
    ch = { kwh: eg, h: t };
    html = '<table class="tbl"><tbody><tr><td>Carga del ' + H.num(a, 0) + ' al ' + H.num(b, 0) + ' %</td><td class="num">' + H.num(eb, 1) + ' kWh</td></tr>' +
      '<tr><td>De la red</td><td class="num">' + H.num(eg, 1) + ' kWh</td></tr>' +
      '<tr><td>Tiempo a ' + H.num(v.kw, v.kw % 1 ? 1 : 0) + ' kW</td><td class="num">' + hh + ' h ' + (mm < 10 ? '0' : '') + mm + ' min</td></tr>' +
      (sh > 0 ? '<tr><td>Coste en casa</td><td class="num">' + H.eur(H.r2(eg * pc)) + '</td></tr>' : '') +
      (sh < 100 ? '<tr><td>Coste en punto público</td><td class="num">' + H.eur(H.r2(eg * pp)) + '</td></tr>' : '') + '</tbody></table>';
  }
  return {
    label: 'Cada 100 km', big: H.eur(H.r2(mix)),
    sub: H.num(c * f, 1) + ' kWh de la red' + (km ? ' · ' + H.eur(H.r2(mon)) + ' al mes' : ''),
    rows: rows, html: html, note: 'Precios de ejemplo: cámbialos por los de tu tarifa y tus cargadores.',
    n: { home: H.r2(eh), pub: H.r2(ep), mix: H.r2(mix), month: H.r2(mon), comb: comb === null ? null : H.r2(comb), kwh: ch ? ch.kwh : null, hours: ch ? H.r2(ch.h) : null }
  };
}
"""

CHARGERS = [
    ("2.3", "Enchufe 2,3 kW", {"kw": "2,3"}),
    ("3.7", "Wallbox 3,7 kW", {"kw": "3,7"}),
    ("7.4", "Wallbox 7,4 kW", {"kw": "7,4"}),
    ("11", "Alterna 11 kW", {"kw": "11"}),
    ("22", "Alterna 22 kW", {"kw": "22"}),
    ("50", "Rápido 50 kW", {"kw": "50"}),
    ("100", "Rápido 100 kW", {"kw": "100"}),
    ("150", "Ultrarrápido 150 kW", {"kw": "150"}),
    ("otro", "Otra potencia"),
]

TOOL = {
    "slug": "coste-coche-electrico",
    "lang": "es",
    "cat": "vehiculos",
    "icon": "charging-pile",
    "order": 40,
    "name": "Coste coche eléctrico",
    "k": "cargar eléctrico casa wallbox punto de carga kwh 100 km tiempo de carga recarga cuánto cuesta",
    "title": "Coste de cargar un coche eléctrico: €/100 km y tiempo",
    "desc": "Calcula cuánto cuesta cada 100 km tu coche eléctrico cargando en casa o en punto público, el gasto al mes, el ahorro y el tiempo de carga.",
    "h1": "Coste de cargar un coche eléctrico",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "cons", "type": "number", "label": "Consumo", "value": "16", "unit": "kWh/100 km", "step": "0.1", "w": "s"},
        {"id": "km", "type": "number", "label": "Km al mes", "value": "1000", "unit": "km", "w": "s"},
        {"id": "pcasa", "type": "money", "label": "kWh en casa", "value": "0,15", "unit": "€/kWh", "w": "s"},
        {"id": "ppub", "type": "money", "label": "kWh en punto", "value": "0,49", "unit": "€/kWh", "w": "s"},
        {"id": "casa", "type": "number", "label": "En casa", "value": "80", "unit": "%", "w": "s"},
        {"id": "bat", "type": "number", "label": "Batería", "value": "60", "unit": "kWh", "w": "s"},
        {"id": "desde", "type": "number", "label": "Desde", "value": "20", "unit": "%", "w": "s"},
        {"id": "hasta", "type": "number", "label": "Hasta", "value": "80", "unit": "%", "w": "s"},
        {"id": "carg", "type": "select", "label": "Cargador", "value": "7.4", "options": CHARGERS, "custom": "otro"},
        {"id": "kw", "type": "number", "label": "Potencia", "value": "7,4", "unit": "kW", "step": "0.1", "w": "s"},
        {"id": "perd", "type": "number", "label": "Pérdidas", "value": "10", "unit": "%", "w": "s", "more": True},
        {"id": "lcomb", "type": "number", "label": "Coche combustión", "value": "6,5", "unit": "l/100 km", "step": "0.1", "w": "s", "more": True},
        {"id": "pcomb", "type": "money", "label": "Combustible", "value": "1,55", "unit": "€/l", "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": BLOCKS,
    "faq": FAQ,
    "sources": [("Reglamento (UE) 2017/1151 · ensayo WLTP de consumo y autonomía (EUR-Lex)", WLTP),
                ("REBT, ITC-BT-52 · infraestructura de recarga de vehículos eléctricos (BOE)", REBT)],
    "credits": [],
    "related": ["coste-viaje-coche", "potencia-contratada", "etiqueta-dgt", "consumo-l100km-mpg"],
    "tests": [
        ({}, {"n.home": 2.64, "n.pub": 8.62, "n.mix": 3.84, "n.month": 38.37, "n.comb": 10.08, "n.kwh": 39.6, "n.hours": 5.35}),
        ({"casa": "100", "ppub": ""}, {"n.mix": 2.64, "n.pub": 0}),
        ({"kw": "100", "perd": "0"}, {"n.kwh": 36, "n.hours": 0.36}),
        ({"cons": ""}, {"err": "Escribe el consumo en kWh/100 km."}),
        ({"desde": "90"}, {"err": "Carga: «Desde» menor que «Hasta», entre 0 y 100 %."}),
    ],
}
