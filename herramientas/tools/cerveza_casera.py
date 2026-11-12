"""Cerveza casera: alcohol (ABV) from original and final gravity, bitterness (IBU, Tinseth) and colour (SRM/EBC,
Morey). English twin: homebrew_calculator.py."""
from herramientas.tools._cocina import CAT, js

TINSETH = "https://www.realbeer.com/hops/research.html"
MOREY = "https://beersmith.com/blog/2008/04/29/beer-color-understanding-srm-lovibond-and-ebc/"
HOPS = "https://beersmith.com/blog/2021/09/23/hop-utilization-models-for-beer-brewing-compared/"
BJCP = "https://www.bjcp.org/style/2021/beer/"
CREDITS = [("Glenn Tinseth · hop utilization formula", "Fórmula publicada", TINSETH),
           ("Daniel Morey · beer colour equation (SRM = 1,4922 · MCU^0,6859)", "Fórmula publicada", MOREY)]
CREDITS_EN = [("Glenn Tinseth · hop utilization formula", "Published formula", TINSETH),
              ("Daniel Morey · beer color equation (SRM = 1.4922 · MCU^0.6859)", "Published formula", MOREY)]

BODY = r"""
  var plato = v.esc === 'p';
  function sg(x) {
    if (!ok(x)) return NaN;
    if (plato) return x >= 0 && x <= 40 ? 1 + x / (258.6 - (x / 258.2) * 227.1) : NaN;
    if (x >= 0.98 && x <= 1.2) return x;
    if (x >= 980 && x <= 1200) return x / 1000;   /* '1.050' is read as 1050 (thousands) */
    if (x > 2 && x <= 200) return 1 + x / 1000;   /* gravity points: 50 = 1.050 */
    return NaN;
  }
  function pl(g) { return -616.868 + 1111.14 * g - 630.272 * g * g + 135.997 * g * g * g; }
  function sgs(g) { return EN ? g.toFixed(3) : g.toFixed(3).replace('.', ','); }
  var og = sg(v.og);
  if (!ok(og) || og < 1) return { err: T.e_og };
  if (v.calc === 'abv') {
    var fg = sg(v.fg);
    if (!ok(fg)) return { err: T.e_fg };
    if (fg > og) return { err: T.e_fgog };
    var abv = (og - fg) * 131.25, alt = 76.08 * (og - fg) / (1.775 - og) * fg / 0.794, att = og > 1 ? (og - fg) / (og - 1) * 100 : 0;
    return {
      label: T.abv_l, big: nf(abv, 1) + ' %', sub: T.abv_sub.replace('{o}', sgs(og)).replace('{f}', sgs(fg)),
      rows: [[T.abv_std, nf(abv, 2) + ' %'], [T.abv_alt, nf(alt, 2) + ' %'], [T.att, nf(att, 0) + ' %'],
             [T.plato, nf(pl(og), 1) + ' °P → ' + nf(pl(fg), 1) + ' °P', 'sub'], [T.abw, nf(abv * 0.789, 2) + ' %', 'sub']],
      note: T.abv_note, n: { abv: H.r2(abv), alt: H.r2(alt), att: H.r2(att) }
    };
  }
  var VU = { l: 1, gal: 3.78541 }, Lt = ok(v.vol) ? v.vol * (VU[v.vu] || 1) : NaN;
  if (!ok(Lt) || Lt <= 0 || Lt > 10000) return { err: T.e_vol };
  if (v.calc === 'ibu') {
    var WU = { g: 1, oz: 28.3495 }[v.hu] || 1, tot = 0, rows = [], any = false;
    for (var i = 1; i <= 3; i++) {
      var g = v['h' + i + 'g'], a = v['h' + i + 'a'], t = v['h' + i + 't'];
      if (!ok(g) || g === 0) continue;
      if (g < 0 || !ok(a) || a <= 0 || a > 25) return { err: T.e_aa.replace('{i}', i) };
      if (!ok(t) || t < 0 || t > 180) return { err: T.e_t.replace('{i}', i) };
      var u = 1.65 * Math.pow(0.000125, og - 1) * (1 - Math.exp(-0.04 * t)) / 4.15;
      var ibu = u * a / 100 * g * WU * 1000 / Lt;
      tot += ibu; any = true;
      rows.push([T.hop.replace('{i}', i) + ' · ' + nz(g, 1) + ' ' + (v.hu || 'g') + ' · ' + nz(a, 1) + ' % AA · ' + t + ' min', nf(ibu, 1) + ' IBU']);
    }
    if (!any) return { err: T.e_hops };
    var bugu = og > 1 ? tot / ((og - 1) * 1000) : 0;
    rows.push([T.total, nf(tot, 1) + ' IBU', 'tot'], [T.bugu, nf(bugu, 2), 'sub']);
    return { label: T.ibu_l, big: nf(tot, 0) + ' IBU', sub: T.ibu_sub.replace('{v}', nz(Lt, 1)).replace('{o}', sgs(og)), rows: rows,
             note: T.ibu_note, n: { ibu: H.r2(tot), bugu: H.r2(bugu) } };
  }
  var KG = { kg: 1, lb: 0.453592 }[v.gu] || 1, ebcIn = v.cu !== 'l', mcu = 0, anym = false;
  for (var j = 1; j <= 4; j++) {
    var kg = v['m' + j + 'k'], c = v['m' + j + 'c'];
    if (!ok(kg) || kg === 0) continue;
    if (kg < 0 || !ok(c) || c < 0 || c > 3000) return { err: T.e_malt.replace('{i}', j) };
    var lov = ebcIn ? (c + 1.2) / 2.65 : c;
    mcu += kg * KG * 2.20462 * lov / (Lt / 3.78541); anym = true;
  }
  if (!anym) return { err: T.e_malts };
  var srm = 1.4922 * Math.pow(mcu, 0.6859), ebc = srm * 1.97;
  var st = [[2, [248, 222, 110]], [4, [244, 190, 60]], [7, [230, 145, 20]], [12, [200, 100, 10]], [20, [150, 52, 6]], [30, [95, 20, 6]], [40, [45, 10, 8]]];
  var x = Math.max(2, Math.min(40, srm)), k = 0;
  while (k < st.length - 2 && x > st[k + 1][0]) k++;
  var f = (x - st[k][0]) / (st[k + 1][0] - st[k][0]), rgb = [0, 1, 2].map(function (q) { return Math.round(st[k][1][q] + f * (st[k + 1][1][q] - st[k][1][q])); });
  var name = T.cols[srm < 3 ? 0 : srm < 6 ? 1 : srm < 10 ? 2 : srm < 17 ? 3 : srm < 25 ? 4 : srm < 35 ? 5 : 6];
  return {
    label: T.srm_l, big: nf(ebc, 0) + ' EBC', sub: nf(srm, 1) + ' SRM · ' + name,
    rows: [[T.mcu, nf(mcu, 1)], ['SRM', nf(srm, 1)], ['EBC', nf(ebc, 0), 'tot']],
    html: '<div class="hbeer" style="background:rgb(' + rgb.join(',') + ')" aria-hidden="true"></div>',
    note: T.srm_note, n: { srm: H.r2(srm), ebc: H.r2(ebc), mcu: H.r2(mcu) }
  };
"""
JS = js(BODY)
CSS = ".hbeer{height:42px;border-radius:8px;margin:.6em 0;border:1px solid rgba(0,0,0,.15)}"

T_ES = {
    "e_og": "Densidad inicial: escribe 1.050, 1,050 o 50 (o grados Plato si los elegiste).", "e_fg": "Escribe la densidad final.",
    "e_fgog": "La densidad final no puede ser mayor que la inicial.", "e_vol": "Escribe el volumen del lote.",
    "e_aa": "Lúpulo {i}: alfa ácidos entre 0,1 y 25 %.", "e_t": "Lúpulo {i}: minutos de hervor entre 0 y 180.",
    "e_hops": "Escribe al menos un lúpulo (gramos, % alfa y minutos).", "e_malt": "Malta {i}: revisa el color.", "e_malts": "Escribe al menos una malta (kg y color).",
    "abv_l": "Alcohol", "abv_sub": "DI {o} → DF {f}", "abv_std": "Fórmula estándar", "abv_alt": "Fórmula para densidades altas",
    "att": "Atenuación aparente", "plato": "Grados Plato", "abw": "Alcohol en peso",
    "abv_note": "Si añades azúcar para carbonatar en botella, suma unos 0,3-0,5 puntos de alcohol.",
    "hop": "Lúpulo {i}", "total": "Total", "bugu": "Relación amargor/densidad (BU:GU)",
    "ibu_l": "Amargor (Tinseth)", "ibu_sub": "{v} L de mosto a DI {o}",
    "ibu_note": "Volumen al final del hervor. Los lúpulos añadidos al apagar el fuego (0 min) y en seco no suman IBU con esta fórmula.",
    "malt": "Malta {i}", "mcu": "MCU", "srm_l": "Color (Morey)",
    "cols": ["Paja clara", "Dorado", "Ámbar claro", "Ámbar · cobre", "Marrón", "Marrón oscuro", "Negro"],
    "srm_note": "Aproximación: el color real cambia con el hervor, la levadura y el filtrado.",
}
T_EN = {
    "e_og": "Original gravity: enter 1.050 or 50 (or degrees Plato if selected).", "e_fg": "Enter the final gravity.",
    "e_fgog": "Final gravity cannot be higher than original gravity.", "e_vol": "Enter the batch volume.",
    "e_aa": "Hop {i}: alpha acids between 0.1 and 25 %.", "e_t": "Hop {i}: boil time between 0 and 180 minutes.",
    "e_hops": "Enter at least one hop (amount, % alpha acid and minutes).", "e_malt": "Grain {i}: check the colour.", "e_malts": "Enter at least one grain (amount and colour).",
    "abv_l": "Alcohol by volume", "abv_sub": "OG {o} → FG {f}", "abv_std": "Standard formula", "abv_alt": "High-gravity formula",
    "att": "Apparent attenuation", "plato": "Degrees Plato", "abw": "Alcohol by weight",
    "abv_note": "Priming sugar for bottle conditioning adds roughly 0.3-0.5 % ABV on top.",
    "hop": "Hop {i}", "total": "Total", "bugu": "Bitterness ratio (BU:GU)",
    "ibu_l": "Bitterness (Tinseth)", "ibu_sub": "{v} L of wort at OG {o}",
    "ibu_note": "Use the post-boil volume. Flameout (0 min) and dry hops add no IBU in this formula.",
    "malt": "Grain {i}", "mcu": "MCU", "srm_l": "Colour (Morey)",
    "cols": ["Pale straw", "Gold", "Light amber", "Amber · copper", "Brown", "Dark brown", "Black"],
    "srm_note": "An estimate: real colour also shifts with the boil, yeast and clarity.",
}


def inputs(lang):
    es = lang == "es"
    sa, si, sc = ("calc", ["abv"]), ("calc", ["ibu"]), ("calc", ["srm"])
    ab = ("calc", ["abv", "ibu"])
    out = [
        {"id": "calc", "type": "seg", "label": "Calcular" if es else "Calculate", "value": "abv",
         "options": [("abv", "Alcohol" if es else "ABV"), ("ibu", "Amargor (IBU)" if es else "IBU"), ("srm", "Color" if es else "Colour")]},
        {"id": "og", "type": "number", "label": "Densidad inicial" if es else "OG", "value": "1.050", "w": "s", "step": "0.001", "show": ab},
        {"id": "fg", "type": "number", "label": "Densidad final" if es else "FG", "value": "1.010", "w": "s", "step": "0.001", "show": sa},
        {"id": "vol", "type": "number", "label": "Volumen" if es else "Volume", "value": 20, "unit": "L" if es else "", "w": "s", "step": "0.1", "show": ("calc", ["ibu", "srm"])},
    ]
    for i, (g, a, t) in enumerate([(25, 10, 60), (15, 5, 10), (0, 5, 0)], 1):
        out += [
            {"id": f"h{i}g", "type": "number", "label": (f"Lúpulo {i}" if es else f"Hop {i}"), "value": g, "unit": "g" if es else "", "w": "s", "step": "0.1", "show": si},
            {"id": f"h{i}a", "type": "number", "label": "Alfa" if es else "Alpha", "value": a, "unit": "%", "w": "s", "step": "0.1", "show": si},
            {"id": f"h{i}t", "type": "number", "label": "Minutos" if es else "Minutes", "value": t, "unit": "min", "w": "s", "show": si},
        ]
    for i, (k, c) in enumerate([(4, 6), (0.3, 120), (0, 0), (0, 0)], 1):
        out += [
            {"id": f"m{i}k", "type": "number", "label": (f"Malta {i}" if es else f"Grain {i}"), "value": k, "unit": "kg" if es else "", "w": "s", "step": "0.01", "show": sc},
            {"id": f"m{i}c", "type": "number", "label": "Color" if es else "Colour", "value": c, "unit": "EBC" if es else "", "w": "s", "step": "0.1", "show": sc},
        ]
    if es:
        out.append({"id": "esc", "type": "select", "label": "Densidad en", "value": "sg", "more": True,
                    "options": [("sg", "Densidad (1,050)"), ("p", "Grados Plato (°P)")]})
    else:
        out[3:3] = [{"id": "vu", "type": "select", "label": "Unit", "value": "l", "w": "s", "show": ("calc", ["ibu", "srm"]),
                     "options": [("l", "litres"), ("gal", "US gal")]}]
        out += [
            {"id": "hu", "type": "select", "label": "Hops in", "value": "g", "more": True, "options": [("g", "grams"), ("oz", "ounces")]},
            {"id": "gu", "type": "select", "label": "Grain in", "value": "kg", "more": True, "options": [("kg", "kg"), ("lb", "lb")]},
            {"id": "cu", "type": "select", "label": "Colour in", "value": "e", "more": True, "options": [("e", "EBC"), ("l", "°Lovibond")]},
            {"id": "esc", "type": "select", "label": "Gravity in", "value": "sg", "more": True,
             "options": [("sg", "Specific gravity (1.050)"), ("p", "Degrees Plato (°P)")]},
        ]
    return out


TESTS = [
    ({}, {"n.abv": 5.25, "n.alt": 5.34, "n.att": 80}),
    ({"og": "1,080", "fg": "15"}, {"n.abv": 8.53}),
    ({"calc": "ibu"}, {"n.ibu": 31.97}),
    ({"calc": "srm"}, {"n.srm": 7.37, "n.ebc": 14.52}),
    ({"fg": "1.060"}, {"err": T_ES["e_fgog"]}),
    ({"calc": "ibu", "h1g": "0", "h2g": "0"}, {"err": T_ES["e_hops"]}),
]

FAQ = [
    ("¿Cómo se calcula el alcohol de la cerveza con el densímetro?",
     "Resta la densidad final a la inicial y multiplica por 131,25. Con 1,050 de inicial y 1,010 de final: 0,040 × 131,25 = 5,25 % "
     "de alcohol. Para cervezas fuertes (más de 1,070) la fórmula para densidades altas es más precisa y suele dar unas décimas más."),
    ("¿Qué son los IBU?",
     "International Bitterness Units: miligramos de iso-alfa ácidos por litro de cerveza. Una lager suave ronda 10-20 IBU, una pale "
     "ale 30-45 y una IPA 40-70 o más. La fórmula de Tinseth estima cuánto alfa ácido se isomeriza según el tiempo de hervor y la "
     "densidad del mosto."),
    ("¿Por qué el amargor sale distinto en cada programa?",
     "Hay varias fórmulas (Tinseth, Rager, Garetz) y cada programa ajusta cosas como el tipo de lúpulo (pellet o flor) o el tiempo "
     "que el mosto tarda en enfriarse. Tinseth es la más usada en casa; tómala como una estimación, no como una medida de laboratorio."),
    ("¿Qué diferencia hay entre SRM y EBC?",
     "Son dos escalas del color: la estadounidense (SRM) y la europea (EBC). EBC ≈ SRM × 1,97. Una lager dorada está en 3-6 SRM "
     "(6-12 EBC), una ámbar en 10-17 SRM y una stout por encima de 30 SRM (60 EBC)."),
    ("¿Puedo escribir la densidad sin el punto?",
     "Sí: 1.050, 1,050 y 50 (puntos de densidad) dan lo mismo. Si tu refractómetro da grados Plato, elígelos en «Más opciones». "
     "Recuerda que con alcohol presente el refractómetro necesita corrección para la densidad final; usa el densímetro para la DF."),
]


def blocks_es(ctx):
    return [
        ("Alcohol: la fórmula del densímetro", """
<p>El densímetro mide cuánto azúcar disuelto hay en el mosto. Antes de fermentar (densidad inicial, DI) y al terminar
(densidad final, DF): la diferencia es el azúcar que la levadura convirtió en alcohol y CO₂. La fórmula estándar es
<b>ABV = (DI − DF) × 131,25</b>. Una cerveza que empieza en 1,050 y termina en 1,010 tiene un <b>5,25 %</b>. La fórmula para
densidades altas, <b>76,08 × (DI − DF) ÷ (1,775 − DI) × DF ÷ 0,794</b>, da 5,34 % en el mismo caso y se separa más en cervezas
fuertes: de 1,080 a 1,015 son 8,53 % con la estándar y 9,10 % con la otra. La atenuación aparente (80 % en el primer ejemplo)
indica cuánto azúcar ha consumido la levadura; la mayoría de cepas de ale atenúan entre el 70 y el 80 %.</p>"""),
        ("Amargor: la fórmula de Tinseth", """
<p>Glenn Tinseth publicó en los años noventa una fórmula ajustada con mediciones reales: la utilización del lúpulo es un factor de densidad,
<b>1,65 × 0,000125^(DI − 1)</b>, por un factor de tiempo, <b>(1 − e^(−0,04 × minutos)) ÷ 4,15</b>. Los IBU son esa utilización
por los miligramos de alfa ácidos por litro (gramos × % alfa × 10 ÷ litros). Con 20 L de mosto a 1,050, 25 g de un lúpulo al
10 % durante 60 minutos dan <b>28,8 IBU</b>; añadir 15 g al 5 % a falta de 10 minutos suma 3,1 más: unos 32 IBU, propio de una pale
ale suave. Cuanto más denso el mosto, menos amargor se extrae: el mismo lúpulo en un mosto de 1,080 da bastante menos.</p>"""),
        ("Color: la ecuación de Morey", """
<p>Cada malta tiene un color en grados Lovibond o EBC. Se calculan las MCU (libras de malta × grados Lovibond ÷ galones) y Daniel
Morey ajustó la curva con cervezas reales: <b>SRM = 1,4922 × MCU^0,6859</b>. Para 20 L con 4 kg de malta pale de 6 EBC y 300 g
de caramelo de 120 EBC salen 7,4 SRM, unos <b>15 EBC</b>: un dorado ámbar. El color de la malta en EBC se pasa a Lovibond con
(EBC + 1,2) ÷ 2,65. La muestra de color es orientativa: la pantalla y el grosor del vaso cambian mucho cómo se ve una cerveza.
Las guías de estilos del BJCP dan rangos de densidad, IBU y color para cada estilo.</p>"""),
    ]


TOOL = {
    "slug": "cerveza-casera",
    "lang": "es",
    "twin": "homebrew-calculator",
    "cat": CAT["es"][0], "cat_name": CAT["es"][1],
    "icon": "beer",
    "order": 40,
    "name": "Cerveza casera",
    "k": "alcohol densidad inicial final ABV IBU amargor lúpulo color SRM EBC homebrew",
    "title": "Calculadora de cerveza casera: alcohol, IBU y color",
    "desc": "Calcula el alcohol de tu cerveza casera con la densidad inicial y final, el amargor en IBU (Tinseth) y el color en SRM y EBC (Morey).",
    "h1": "Calculadora de cerveza casera",
    "crumb": "Cerveza casera",
    "updated": "2026-11-12",
    "inputs": inputs("es"),
    "js": JS,
    "css": CSS,
    "data": {"en": False, "t": T_ES},
    "blocks": blocks_es,
    "faq": FAQ,
    "sources": [("Glenn Tinseth · Hop utilization", TINSETH), ("BeerSmith · Modelos de utilización del lúpulo", HOPS),
                ("BeerSmith · SRM, Lovibond y EBC (ecuación de Morey)", MOREY), ("BJCP · Guía de estilos 2021", BJCP)],
    "credits": CREDITS,
    "related": ["ratio-cafe", "azucar-mermelada", "salmuera", "cantidades-fiesta"],
    "tests": TESTS,
}
