"""Consumo de pellets o leña: kg per season and cost from the stove power and use, a yearly heat demand, or the heating oil
it replaces. Net calorific value of wood at moisture M (wet basis): q = q_dry (100 - M)/100 - 0,02443 M MJ/kg
(EN ISO 18125), q_dry = 19 MJ/kg; pellets 4,6 kWh/kg (ENplus A1 minimum)."""
IDAE = "https://www.idae.es/tecnologias/energias-renovables/uso-termico/biomasa"
ENPLUS = "https://enplus-pellets.eu/es/"
ISO = "https://www.iso.org/standard/61517.html"

DEVICES = [("ep", "Estufa de pellets", "p", 88), ("cp", "Caldera de pellets", "p", 90), ("el", "Estufa de leña", "l", 75),
           ("cl", "Caldera de leña", "l", 80), ("ic", "Chimenea con cassette", "l", 70), ("ca", "Chimenea abierta", "l", 20)]

JS = r"""
function (v, H, C) {
  var pel = v.comb !== 'l', ef = v.ef, M = isNaN(v.hum) ? 20 : v.hum;
  if (!(ef > 0 && ef <= 100)) return { err: 'Rendimiento: de 1 a 100 %.' };
  if (!pel && !(M >= 0 && M < 60)) return { err: 'Humedad de la leña: de 0 a 60 %.' };
  var pci = pel ? 4.6 : (19 * (100 - M) / 100 - 0.02443 * M) / 3.6, heat;
  if (v.modo === 'kw') {
    if (!(v.kw > 0) || !(v.horas > 0) || !(v.dias > 0)) return { err: 'Escribe la potencia, las horas al día y los días.' };
    if (v.horas > 24) return { err: 'Un día tiene 24 horas.' };
    var load = isNaN(v.carga) ? 60 : v.carga;
    if (!(load > 0 && load <= 100)) return { err: 'Potencia media: de 1 a 100 %.' };
    heat = v.kw * v.horas * v.dias * load / 100;
  } else if (v.modo === 'kwh') {
    if (!(v.kwh > 0)) return { err: 'Escribe la energía útil en kWh.' };
    heat = v.kwh;
  } else {
    if (!(v.litros > 0)) return { err: 'Escribe los litros de gasóleo al año.' };
    heat = v.litros * 10 * 0.85;
  }
  var kg = heat / (ef / 100) / pci, pr = isNaN(v.precio) ? 0 : v.precio, sac = 15;
  var rows = [['Calor útil', H.num(heat, 0) + ' kWh'], ['Poder calorífico', H.num(pci, 2) + ' kWh/kg' + (pel ? ' (pellet ENplus A1)' : ' (leña al ' + H.num(M, 0) + ' %)')],
    ['Rendimiento', H.num(ef, 0) + ' %']];
  if (pel) rows.push(['Sacos de 15 kg', H.num(Math.ceil(kg / sac - 1e-9), 0) + ' · ' + H.num(kg / 1000, 2) + ' t']);
  else rows.push(['Toneladas', H.num(kg / 1000, 2) + ' t']);
  if (v.modo === 'kw') rows.push(['Consumo por hora', H.num(kg / (v.horas * v.dias), 2) + ' kg/h']);
  if (v.modo !== 'gas') rows.push(['Equivale a gasóleo', H.num(heat / (10 * 0.85), 0) + ' L (caldera al 85 %)', 'sub']);
  if (pr > 0) rows.push(['Coste', H.eur(kg * pr) + ' · ' + H.num(kg * pr / heat, 3) + ' €/kWh útil', 'tot']);
  return { label: pel ? 'Pellets por temporada' : 'Leña por temporada', big: H.num(kg, 0) + ' kg',
    sub: pr > 0 ? H.eur(kg * pr) + ' a ' + H.num(pr, 2) + ' €/kg' : 'Pon el precio por kg para ver el coste',
    rows: rows, note: 'La leña rinde mucho menos si está húmeda: compra leña seca (menos del 20 %) y guárdala a cubierto y ventilada.',
    n: { kg: H.r2(kg), heat: H.r2(heat), pci: H.r2(pci) } };
}
"""


def blocks(ctx):
    return [
        ("Cuántos kilos de pellets o leña gasta una estufa", f"""
<p>Una estufa gasta los kilos de combustible que hacen falta para dar el calor que le pides: <b>kg = calor útil ÷ rendimiento ÷
poder calorífico</b>. El calor útil es la potencia de la estufa por las horas que funciona y por la fracción de potencia a la que
trabaja; casi nunca va al máximo, así que con un 50-60 % de media te acercarás al consumo real. Una <b>estufa de pellets de
9 kW</b> que funciona 6 horas al día durante 150 días a media potencia da 4.050 kWh de calor; con un rendimiento del 88 % y pellet de
4,6 kWh/kg gasta unos <b>1.000 kg por temporada</b>, 67 sacos de 15 kg. A plena potencia quema unos 2,2 kg por hora.</p>
<p>El <b>pellet certificado ENplus A1</b> garantiza al menos 4,6 kWh por kilo y menos del 10 % de humedad, así que su consumo es
muy estable. La leña depende de la humedad: seca (20 %) da unos 4,1 kWh/kg, al 30 % baja a 3,5 y recién cortada, con un 40-50 %,
apenas llega a 2,3-2,9, porque parte del calor se gasta en evaporar el agua.</p>"""),
        ("Ejemplo con leña y comparación", """
<p>La misma demanda de 4.050 kWh con una <b>estufa de leña cerrada</b> (75 % de rendimiento) y leña de encina seca al 20 % necesita
unos <b>1.320 kg</b>. Con leña al 35 % de humedad harían falta unos 1.690 kg: un 28 % más leña por el mismo calor. En una chimenea abierta, con un rendimiento del 15-20 %, se quemaría cuatro veces más.</p>
<p>Si vas a cambiar una caldera de gasóleo, elige «Gasóleo» y escribe los litros que gastas al año: 1.000 litros en una caldera al
85 % son 8.500 kWh útiles, que con una caldera de pellets al 90 % equivalen a unos 2.050 kg de pellet.</p>"""),
        ("Fórmulas y fuentes", f"""
<p>El poder calorífico de la leña se calcula con la fórmula de la norma EN ISO 18125 para la base húmeda: PCI = PCI seco × (100 −
M) ÷ 100 − 0,02443 × M (en MJ/kg, M = humedad en %), con un PCI seco de 19 MJ/kg, el habitual de la madera de frondosas y coníferas.
El pellet usa el mínimo de la certificación <a href="{ENPLUS}" rel="noopener">ENplus A1</a> (16,5 MJ/kg, 4,6 kWh/kg). Los
rendimientos por defecto son valores típicos de cada aparato; el de tu estufa viene en su ficha técnica. El
<a href="{IDAE}" rel="noopener">IDAE</a> recoge las características de la biomasa térmica y las ayudas para cambiar de caldera. El
gasóleo se cuenta a 10 kWh por litro.</p>"""),
    ]


FAQ = [
    ("¿Cuántos kilos de pellets gasta una estufa al día?",
     "Una estufa de 8-10 kW a media potencia durante 6 horas gasta unos 6-7,5 kg al día, medio saco. A plena potencia, entre 2 y 2,5 kg "
     "por hora."),
    ("¿Cuántos sacos de pellets necesito para un invierno?",
     "Con una estufa de 9 kW, 6 horas al día y 150 días a media potencia, unos 1.000 kg: 67 sacos de 15 kg. Si calientas toda la casa con "
     "una caldera, de 2 a 4 toneladas según la superficie y el clima."),
    ("¿Qué calienta más, la leña o el pellet?",
     "Por kilo, el pellet (4,6 kWh/kg frente a unos 4,1 de la leña seca). Además, las estufas de pellets rinden más (85-90 %) que las de "
     "leña (70-80 %), así que para el mismo calor se necesita menos pellet."),
    ("¿Cuánto calor da un kilo de pellets?",
     "Unos 4,6 kWh de energía, de los que una estufa al 88 % entrega unos 4 kWh en forma de calor: lo que da una estufa de 9 kW durante "
     "algo menos de media hora a plena potencia."),
    ("¿Cómo sé si la leña está seca?",
     "Con un medidor de humedad de puntas (menos del 20 % es leña seca), o por las grietas en los extremos, el peso y el sonido hueco al "
     "golpear dos troncos. La leña cortada necesita de uno a dos años a cubierto para secarse."),
]

TOOL = {
    "slug": "consumo-pellets-lena",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "flame",
    "order": 90,
    "name": "Consumo de pellets",
    "k": "estufa pellets kilos sacos temporada leña humedad caldera biomasa gasoleo coste calefaccion",
    "title": "Consumo de pellets o leña: kilos por temporada y coste",
    "desc": "Calcula cuántos kilos y sacos de pellets o cuánta leña gasta tu estufa o caldera en un invierno y cuánto cuesta, según potencia, horas y humedad.",
    "h1": "Consumo de pellets o leña",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "ap", "type": "select", "label": "Aparato", "value": "ep", "custom": "ot",
         "options": [(k, n, {"comb": c, "ef": e}) for k, n, c, e in DEVICES] + [("ot", "Otro")]},
        {"id": "comb", "type": "seg", "label": "Combustible", "value": "p", "options": [("p", "Pellets"), ("l", "Leña")]},
        {"id": "hum", "type": "number", "label": "Humedad", "value": 20, "unit": "%", "w": "s", "show": ("comb", ["l"])},
        {"id": "modo", "type": "seg", "label": "Calcular por", "value": "kw", "options": [("kw", "Estufa"), ("kwh", "kWh"), ("gas", "Gasóleo")]},
        {"id": "kw", "type": "number", "label": "Potencia", "value": 9, "unit": "kW", "step": "0.1", "w": "s", "show": ("modo", ["kw"])},
        {"id": "horas", "type": "number", "label": "Horas al día", "value": 6, "unit": "h", "step": "0.5", "w": "s", "show": ("modo", ["kw"])},
        {"id": "dias", "type": "number", "label": "Días", "value": 150, "w": "s", "show": ("modo", ["kw"])},
        {"id": "carga", "type": "number", "label": "Potencia media", "value": 50, "unit": "%", "w": "s", "show": ("modo", ["kw"])},
        {"id": "kwh", "type": "number", "label": "Calor útil", "value": 6000, "unit": "kWh", "w": "s", "show": ("modo", ["kwh"])},
        {"id": "litros", "type": "number", "label": "Gasóleo al año", "value": 1000, "unit": "L", "w": "s", "show": ("modo", ["gas"])},
        {"id": "precio", "type": "money", "label": "Precio", "value": "", "unit": "€/kg", "w": "s", "placeholder": "0,35"},
        {"id": "ef", "type": "number", "label": "Rendimiento", "value": 88, "unit": "%", "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("IDAE · Biomasa para usos térmicos", IDAE), ("ENplus · certificación de pellets (A1: ≥ 16,5 MJ/kg)", ENPLUS),
                ("EN ISO 18125 · poder calorífico de biocombustibles sólidos", ISO)],
    "credits": [("Fórmula de PCI en base húmeda de EN ISO 18125 (reimplementada)", "fórmula publicada", ISO)],
    "related": ["pienso-gallinas", "medidas-agrarias", "riego-goteo"],
    "tests": [
        ({}, {"n.heat": 4050, "n.kg": 1000.49}),
        ({"comb": "l", "ef": "75"}, {"n.kg": 1321.42, "n.pci": 4.09}),
        ({"comb": "l", "ef": "75", "hum": "35"}, {"n.kg": 1691.18}),
        ({"modo": "gas", "ef": "90"}, {"n.heat": 8500, "n.kg": 2053.14}),
        ({"horas": "30"}, {"err": "Un día tiene 24 horas."}),
        ({"comb": "l", "hum": "70"}, {"err": "Humedad de la leña: de 0 a 60 %."}),
    ],
}
