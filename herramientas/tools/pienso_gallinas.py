"""Pienso para gallinas: feed per day, month or year for a backyard flock, sacks, cost and feed cost per dozen eggs."""
HYLINE = "https://www.hyline.com/filesimages/Hy-Line-Products/Hy-Line-Product-PDFs/Brown/BRN%20STD%20ENG.pdf"
RD = "https://www.boe.es/buscar/act.php?id=BOE-A-2021-12609"

JS = r"""
function (v, H, C) {
  var n = v.gallinas, g = v.gramos, d = +v.periodo || 30, pc = isNaN(v.pct) ? 100 : v.pct;
  if (!(n > 0)) return { err: 'Escribe cuántas gallinas tienes.' };
  if (n > 1e6) return { err: 'Demasiadas gallinas.' };
  if (!(g > 0 && g <= 300)) return { err: 'Gramos por gallina: de 1 a 300 g al día.' };
  if (!(pc > 0 && pc <= 100)) return { err: 'Parte de pienso: de 1 a 100 %.' };
  var kg = n * g * pc / 100 * d / 1000, sk = v.saco > 0 ? v.saco : 25, ps = isNaN(v.precio) ? 0 : v.precio;
  var lay = isNaN(v.puesta) ? 0 : v.puesta, eggs = n * lay / 100 * d, per = { 7: 'a la semana', 30: 'al mes', 365: 'al año' }[d] || 'en ' + d + ' días';
  var rows = [['Al día', H.num(n * g * pc / 100 / 1000, 2) + ' kg'], ['Sacos de ' + H.num(sk, 0) + ' kg', H.num(kg / sk, 1) + ' · compra ' + Math.ceil(kg / sk - 1e-9)],
    ['Agua aprox.', H.num(n * g * 2 / 1000, 1) + ' L al día', 'sub']];
  var cost = ps > 0 ? kg * ps / sk : 0;
  if (ps > 0) rows.push(['Coste del pienso', H.eur(cost) + ' · ' + H.eur(ps / sk) + '/kg', 'tot']);
  if (lay > 0) {
    rows.push(['Huevos', H.num(eggs, 0) + ' · ' + H.num(eggs / 12, 1) + ' docenas']);
    if (ps > 0) rows.push(['Pienso por docena', H.eur(cost / (eggs / 12)), 'tot']);
  }
  return { label: 'Pienso ' + per, big: H.num(kg, 1) + ' kg', sub: H.num(n, 0) + ' gallinas × ' + H.num(g, 0) + ' g' + (pc < 100 ? ' × ' + H.num(pc, 0) + ' %' : '') + ' × ' + d + ' días',
    rows: rows, note: 'Con frío comen más y con calor menos. Pon el pienso a demanda y ajusta con lo que sobra en el comedero.',
    n: { kg: H.r2(kg), eggs: H.r2(eggs), cost: H.r2(cost), dz: lay > 0 && ps > 0 ? H.r2(cost / (eggs / 12)) : null } };
}
"""


def blocks(ctx):
    return [
        ("Cuánto pienso come una gallina", f"""
<p>Una gallina ponedora come entre <b>100 y 120 gramos de pienso al día</b>; las guías de las estirpes comerciales de huevo
marrón dan de 105 a 116 g de media durante la puesta. Con 115 g, <b>seis gallinas comen unos 0,7 kg al día, 20,7 kg al mes y
unos 250 kg al año</b>: diez sacos de 25 kg. Las razas pesadas, las gallinas en invierno y las que viven en sitios fríos comen más;
con calor por encima de 28-30 °C el consumo baja y la puesta también.</p>
<p>Si las gallinas pastan, comen hierba, insectos o sobras de la cocina, el pienso que necesitan baja. Pon en «Parte de pienso» qué
porcentaje de su comida es pienso (un 70-80 % es razonable con un buen corral), pero no bajes mucho: las sobras y el pasto no tienen
el calcio ni la proteína que necesita una ponedora, y sin ellos ponen menos y con la cáscara más fina.</p>"""),
        ("Ejemplo: cuánto cuesta una docena de huevos", """
<p>Seis gallinas que comen 115 g al día cada una, con pienso de ponedoras a 13 € el saco de 25 kg (0,52 €/kg): en un mes gastan
20,7 kg, <b>10,76 €</b>. Si ponen al 75 % (de media, tres de cada cuatro gallinas ponen un huevo al día), son 135 huevos, 11,25
docenas: el pienso sale a <b>0,96 € la docena</b>. En invierno, con menos horas de luz, la puesta puede bajar a la mitad y la docena
duplica su coste aunque coman lo mismo.</p>"""),
        ("Datos y normativa", f"""
<p>Los gramos por día son los de la <a href="{HYLINE}" rel="noopener">guía de manejo de la ponedora Hy-Line Brown</a>, una de las
estirpes más comunes en los corrales. El agua se estima en el doble del pienso, la proporción habitual a unos 20 °C; con calor beben
bastante más, así que el bebedero nunca debe quedarse vacío. Usa pienso de ponedoras desde que empiezan a poner (hacia las 18-20
semanas) y pienso de recría antes; el de pollitos no lleva calcio suficiente para formar la cáscara.</p>
<p>Las gallinas de autoconsumo también son una explotación ganadera: el <a href="{RD}" rel="noopener">Real Decreto 637/2021</a>,
de ordenación de las granjas avícolas, regula las pequeñas explotaciones de autoconsumo, que deben inscribirse en el registro de tu
comunidad autónoma.</p>"""),
    ]


FAQ = [
    ("¿Cuánto come una gallina al día?",
     "Entre 100 y 120 g de pienso, unos 115 g de media en una ponedora. Al año, unos 42 kg por gallina."),
    ("¿Cuánto dura un saco de 25 kg de pienso?",
     "Con 6 gallinas a 115 g, unos 36 días; con 10 gallinas, unos 22 días; con 3, unos 72 días."),
    ("¿Cuánta agua beben las gallinas?",
     "Aproximadamente el doble de lo que comen: un cuarto de litro al día por gallina en tiempo templado, y bastante más en verano."),
    ("¿Puedo darles solo sobras y grano?",
     "No es recomendable: el maíz o el trigo solos y las sobras tienen poca proteína y casi nada de calcio. Una gallina que pone necesita "
     "unos 4 g de calcio al día, que vienen del pienso de ponedoras o de conchilla aparte."),
    ("¿Cuántos huevos pone una gallina?",
     "Una ponedora híbrida joven pone casi un huevo al día en su mejor momento y unos 250-300 al año; las razas tradicionales, menos. "
     "La puesta baja con la muda y en los días cortos de invierno."),
]

TOOL = {
    "slug": "pienso-gallinas",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "grain",
    "order": 100,
    "name": "Pienso para gallinas",
    "k": "gallinas ponedoras corral cuanto come una gallina gramos saco coste huevos docena",
    "title": "Cuánto pienso come una gallina: calculadora y coste",
    "desc": "Calcula los kg de pienso que comen tus gallinas al día, al mes o al año, cuántos sacos comprar y cuánto te cuesta en pienso cada docena de huevos.",
    "h1": "Calculadora de pienso para gallinas",
    "crumb": "Pienso para gallinas",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "gallinas", "type": "number", "label": "Gallinas", "value": 6, "w": "s"},
        {"id": "gramos", "type": "number", "label": "Por gallina", "value": 115, "unit": "g/día", "w": "s"},
        {"id": "periodo", "type": "seg", "label": "Periodo", "value": "30", "options": [("7", "Semana"), ("30", "Mes"), ("365", "Año")]},
        {"id": "precio", "type": "money", "label": "Precio del saco", "value": "", "w": "s", "placeholder": "13"},
        {"id": "saco", "type": "number", "label": "Saco", "value": 25, "unit": "kg", "w": "s"},
        {"id": "puesta", "type": "number", "label": "Puesta", "value": 75, "unit": "%", "w": "s", "more": True},
        {"id": "pct", "type": "number", "label": "Parte de pienso", "value": 100, "unit": "%", "w": "s", "more": True},
    ],
    "js": JS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Hy-Line Brown · guía de manejo de ponedoras comerciales", HYLINE),
                ("Real Decreto 637/2021, ordenación de las granjas avícolas", RD)],
    "related": ["incubacion-huevos", "consumo-pellets-lena", "calendario-siembra"],
    "tests": [
        ({"precio": "13"}, {"n.kg": 20.7, "n.cost": 10.76, "n.eggs": 135, "n.dz": 0.96}),
        ({"periodo": "365"}, {"n.kg": 251.85, "n.dz": None}),
        ({"pct": "50", "periodo": "7"}, {"n.kg": 2.42}),
        ({"gallinas": "0"}, {"err": "Escribe cuántas gallinas tienes."}),
        ({"gramos": "500"}, {"err": "Gramos por gallina: de 1 a 300 g al día."}),
    ],
}
