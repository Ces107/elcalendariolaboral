"""Temperatura del horno: °C <-> °F <-> gas mark, conventional vs fan (convection). English twin:
oven_temperature_conversion.py."""
from herramientas.tools._cocina import CAT, js

NIST = "https://www.nist.gov/pml/owm/metric-si/unit-conversion"
NIST_T = "https://www.nist.gov/pml/weights-and-measures/si-units-temperature"

BODY = r"""
  var t = v.t, u = v.u === 'f' || v.u === 'g' ? v.u : 'c', fanIn = v.modo === 'v';
  if (!ok(t)) return { err: T.e_t };
  var F;
  if (u === 'g') {
    if (t < 0.25 || t > 10) return { err: T.e_gas };
    F = t >= 1 ? 250 + 25 * t : (t >= 0.5 ? 250 : 225);
  } else F = u === 'f' ? t : t * 9 / 5 + 32;
  var C = (F - 32) * 5 / 9;
  if (C < 30 || C > 320) return { err: T.e_range };
  if (fanIn) { C += 20; F = C * 9 / 5 + 32; }
  function gas(f) {
    if (f < 237.5) return '¼'; if (f < 262.5) return '½';
    var g = Math.round((f - 250) / 25); return g < 1 ? '1' : g > 10 ? '10' : String(g);
  }
  function r5(c) { return Math.round(c / 5) * 5; }
  var fanC = C - 20, fanF = F - 25;
  var word = T.words[C < 135 ? 0 : C < 165 ? 1 : C < 185 ? 2 : C < 205 ? 3 : C < 225 ? 4 : 5];
  var rows = [
    [T.conv, nf(C, 0) + ' °C · ' + nf(F, 0) + ' °F', 'tot'],
    [T.gasl, F >= 225 && F <= 525 ? T.gas + ' ' + gas(F) : '—'],
    [T.fan, nf(fanC, 0) + ' °C' + (EN ? ' · ' + nf(fanC * 9 / 5 + 32, 0) + ' °F' : '')]
  ];
  if (EN) rows.push([T.conv_us, nf(fanF, 0) + ' °F · ' + nf((fanF - 32) * 5 / 9, 0) + ' °C']);
  rows.push([T.dial, r5(C) + ' °C · ' + r5(fanC) + ' °C ' + T.fan_s, 'sub'], [T.word, word, 'sub']);
  var shown = EN ? (u === 'c' ? nf(F, 0) + ' °F' : nf(C, 0) + ' °C') : (u === 'c' ? nf(F, 0) + ' °F' : nf(C, 0) + ' °C');
  return {
    label: T.lab.replace('{x}', (u === 'g' ? T.gas + ' ' + nz(t, 2) : nz(t, 1) + (u === 'f' ? ' °F' : ' °C'))) + (fanIn ? ' ' + T.fan_s : ''),
    big: fanIn ? nf(C, 0) + ' °C · ' + nf(F, 0) + ' °F' : shown,
    sub: fanIn ? T.sub_fan : T.sub,
    rows: rows, note: T.note,
    n: { c: H.r2(C), f: H.r2(F), gas: gas(F), fan: H.r2(fanC) }
  };
"""
JS = js(BODY)

T_ES = {
    "e_t": "Escribe la temperatura.", "e_gas": "Gas: de ¼ (0,25) a 10.", "e_range": "Temperatura fuera de lo normal para un horno (30-320 °C).",
    "conv": "Horno convencional", "gasl": "Horno de gas (Reino Unido)", "gas": "Gas", "fan": "Con ventilador (−20 °C)", "conv_us": "",
    "dial": "En el mando (de 5 en 5)", "fan_s": "con ventilador", "word": "En las recetas",
    "words": ["Muy suave", "Suave", "Moderado", "Moderado-fuerte", "Fuerte", "Muy fuerte"],
    "lab": "{x}", "sub": "Horno convencional (arriba y abajo)", "sub_fan": "Equivale en horno convencional a",
    "note": "La rebaja de 20 °C con ventilador es la orientación habitual de los fabricantes; tu horno puede calentar distinto.",
}
T_EN = {
    "e_t": "Enter the temperature.", "e_gas": "Gas mark: ¼ (0.25) to 10.", "e_range": "That is outside a normal oven range (85-610 °F).",
    "conv": "Conventional oven", "gasl": "Gas mark (UK)", "gas": "Gas", "fan": "Fan oven, UK (−20 °C)", "conv_us": "Convection, US (−25 °F)",
    "dial": "Dial (nearest 5 °C)", "fan_s": "fan", "word": "Recipe term",
    "words": ["Very cool", "Cool / slow", "Moderate", "Moderately hot", "Hot", "Very hot"],
    "lab": "{x}", "sub": "Conventional oven", "sub_fan": "Conventional oven equivalent",
    "note": "Fan and convection reductions are the usual manufacturer guidance; every oven runs a little differently, so an oven thermometer helps.",
}


def inputs(lang):
    es = lang == "es"
    return [
        {"id": "t", "type": "number", "label": "Temperatura" if es else "Temperature", "value": 180 if es else 350, "w": "s", "step": "0.5"},
        {"id": "u", "type": "seg", "label": "En" if es else "In", "value": "c" if es else "f",
         "options": [("c", "°C"), ("f", "°F"), ("g", "Gas")]},
        {"id": "modo", "type": "seg", "label": "Receta para" if es else "Recipe oven", "value": "c",
         "options": [("c", "Convencional" if es else "Conventional"), ("v", "Ventilador" if es else "Fan / convection")]},
    ]


TESTS = [
    ({}, {"n.f": 356, "n.gas": "4", "n.fan": 160}),
    ({"t": "350", "u": "f"}, {"n.c": 176.67}),
    ({"t": "6", "u": "g"}, {"n.f": 400, "n.c": 204.44}),
    ({"t": "160", "modo": "v"}, {"n.c": 180}),
    ({"t": "0,5", "u": "g"}, {"n.f": 250, "n.gas": "½"}),
    ({"t": "900"}, {"err": T_ES["e_range"]}),
]

FAQ = [
    ("¿Cuántos grados Fahrenheit son 180 °C?",
     "356 °F. Las recetas americanas lo redondean a 350 °F (177 °C), que es la temperatura más común para bizcochos y galletas."),
    ("¿Cómo paso de Fahrenheit a Celsius?",
     "Resta 32 y multiplica por 5/9. 350 °F − 32 = 318; 318 × 5 ÷ 9 = 176,7 °C. Al revés: multiplica por 9/5 y suma 32."),
    ("¿Cuánto bajo la temperatura si mi horno tiene ventilador?",
     "Unos 20 °C respecto a la receta para horno convencional (calor arriba y abajo). Si la receta dice 180 °C, pon 160 °C con aire. "
     "En EE. UU. la regla es bajar 25 °F. Si la receta ya está escrita para horno con ventilador, no bajes nada."),
    ("¿Qué es «gas 4» en una receta inglesa?",
     "Las marcas de los hornos de gas británicos. Gas 4 son 350 °F, unos 180 °C. Cada marca suma 25 °F desde gas 1 (275 °F, 140 °C) "
     "hasta gas 9 (475 °F, 240 °C)."),
    ("¿Qué es un horno moderado o fuerte?",
     "Términos de recetario: suave es 150-160 °C, moderado 170-180 °C, fuerte 200-220 °C y muy fuerte a partir de 230 °C. Son "
     "aproximados; si la receta da los grados, usa los grados."),
]

GAS = [("¼", 225), ("½", 250), ("1", 275), ("2", 300), ("3", 325), ("4", 350), ("5", 375), ("6", 400), ("7", 425), ("8", 450), ("9", 475)]


def gas_table(lang):
    def c(f):
        x = (f - 32) * 5 / 9
        return f"{x:.0f}"
    head = ("<th>Gas</th><th>°F</th><th>°C</th><th>°C con ventilador</th>" if lang == "es" else
            "<th>Gas mark</th><th>°F</th><th>°C</th><th>Fan °C</th>")
    body = "".join(f"<tr><td>{g}</td><td class=\"num\">{f}</td><td class=\"num\">{c(f)}</td><td class=\"num\">{int(c(f)) - 20}</td></tr>" for g, f in GAS)
    return f'<table class="tbl"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def blocks_es(ctx):
    return [
        ("Cómo se convierte", f"""
<p>Escribe la temperatura de la receta y en qué escala viene. De Fahrenheit a Celsius: <b>°C = (°F − 32) × 5 ÷ 9</b>; de
Celsius a Fahrenheit: <b>°F = °C × 9 ÷ 5 + 32</b>. Así 180 °C son 356 °F y 425 °F son 218 °C. Las recetas no usan grados
exactos: los mandos de los hornos suelen ir de 10 en 10 o de 20 en 20, y una diferencia de 5 °C no cambia un bizcocho. Por eso la
calculadora te da también la cifra redondeada.</p>
<p>Si la receta es inglesa y dice «gas mark 6», elige «Gas»: son 400 °F, unos 200 °C en horno convencional o 180 °C con
ventilador. Esta es la tabla completa:</p>
{gas_table("es")}"""),
        ("Horno con ventilador o convencional", """
<p>Con ventilador (aire, convección) el calor se reparte mejor y la comida se hace antes, así que se baja la temperatura. La
orientación habitual de los fabricantes europeos es <b>20 °C menos</b> que en convencional (calor arriba y abajo); en Estados Unidos
se dice 25 °F menos, que es casi lo mismo (unos 14 °C). Si la receta indica «180 °C ventilador», ya está ajustada: en un horno
sin ventilador equivale a 200 °C. Elige «Ventilador» en «Receta para» y la calculadora hace la cuenta al revés.</p>
<p>Los hornos también se desvían de lo que marca el mando, a veces más de 10 °C. Un termómetro de horno barato te dice cuánto se
desvía el tuyo.</p>"""),
    ]


TOOL = {
    "slug": "temperatura-horno",
    "lang": "es",
    "twin": "oven-temperature-conversion",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "temperature",
    "order": 70,
    "name": "Temperatura del horno",
    "k": "grados fahrenheit celsius gas mark ventilador convencional receta inglesa americana",
    "title": "Grados Fahrenheit a Celsius para el horno, y gas",
    "desc": "Convierte la temperatura del horno de °F a °C y marcas de gas, y ajústala para horno con ventilador o convencional. Con tabla completa.",
    "h1": "Conversor de temperatura del horno",
    "crumb": "Temperatura del horno",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "data": {"en": False, "t": T_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("NIST · Unidades SI de temperatura", NIST_T), ("NIST · Conversión de unidades", NIST)],
    "related": ["tiempo-asado", "tazas-a-gramos", "porcentaje-panadero", "escalar-receta"],
    "tests": TESTS,
}
