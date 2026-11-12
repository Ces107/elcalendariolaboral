"""Medidas agrarias tradicionales: fanega, hanegada, tahúlla, obrada, ferrado... to m² and hectares, by comunidad.

Values: the official provincial equivalences (Real Orden of 9 Dec 1852, tables of the Instituto Geográfico y Estadístico)
as listed by the Ministerio de Fomento, Hojas divulgadoras 1918 n.º 17-19 «Pesas y medidas», and the Ministerio de
Agricultura's journal Agricultura n.º 726 (1993), pp. 24-28 (Ruiz Lorente and Caballero de la Calle, after Besnier,
«Medidas y pesos agrarios», MAPA 1964). Where the 1918 scan is garbled, the value was rebuilt from the number of
varas/canas it states (vara castellana 0,835905 m -> 0,698737 m² per square vara) and checked against the 1993 list.
"""
HD1918 = "https://www.mapa.gob.es/ministerio/pags/biblioteca/hojas/hd_1918_17-19.pdf"
AGRI1993 = "https://www.mapa.gob.es/ministerio/pags/Biblioteca/Revistas/pdf_Agri%2FAgri_1993_726_24_28.pdf"
RAE = "https://dle.rae.es/tah%C3%BAlla"

# comunidad key -> (name, [(unit key, unit name, where, m²)]). First unit = default of the region.
LAND = [
    ("gen", "General (Castilla)", [
        ("fmr", "Fanega de marco real", "Castilla, 9.216 varas²", 6439.56),
        ("cel", "Celemín", "1/12 de fanega", 536.63),
        ("cua", "Cuartillo", "1/48 de fanega", 134.16),
        ("est", "Estadal cuadrado", "16 varas²", 11.18),
        ("var", "Vara cuadrada", "vara de Castilla", 0.6987),
        ("ha", "Hectárea", "100 áreas", 10000),
        ("are", "Área", "100 m²", 100),
        ("otr", "Otra (escribe sus m²)", "", 0),
    ]),
    ("and", "Andalucía", [
        ("fmr", "Fanega", "Almería (secano), Cádiz, Granada", 6439.56),
        ("tah", "Tahúlla", "Almería (regadío)", 1118.23),
        ("fco", "Fanega", "Córdoba", 6121.23),
        ("aco", "Aranzada", "Córdoba", 3672.74),
        ("fja", "Fanega", "Jaén", 6262.78),
        ("fma", "Fanega", "Málaga", 6037.09),
        ("fse", "Fanega", "Sevilla", 5944.72),
        ("ase", "Aranzada", "Sevilla", 4755.78),
        ("fhu", "Fanega", "Huelva", 3689.33),
        ("mar", "Marjal", "Granada", 528.42),
    ]),
    ("ara", "Aragón", [
        ("cza", "Cahíz", "Zaragoza", 6675.22),
        ("hza", "Hanega", "Zaragoza (3 cuartales)", 715.18),
        ("qza", "Cuartal", "Zaragoza", 238.39),
        ("chu", "Cahíz", "Huesca", 5721.45),
        ("fhu", "Fanega", "Huesca", 715.18),
        ("fte", "Fanega", "Teruel", 1117.98),
        ("yte", "Yugada", "Teruel", 4471.92),
    ]),
    ("ast", "Asturias", [
        ("dbu", "Día de bueyes", "Asturias, 1.800 varas²", 1257.73),
    ]),
    ("bal", "Baleares", [
        ("qrt", "Cuarterada (quarterada)", "Baleares, 400 destres", 7103.12),
        ("cto", "Cuartón (quartó)", "1/4 de cuarterada", 1775.78),
        ("des", "Destre", "Baleares", 17.76),
    ]),
    ("can", "Canarias", [
        ("fgd", "Fanegada", "Canarias", 5248.29),
        ("alm", "Almud", "1/12 de fanegada", 437.36),
    ]),
    ("cnt", "Cantabria", [
        ("car", "Carro", "Cantabria", 179),
        ("fmr", "Fanega", "Santander", 6439.56),
    ]),
    ("clm", "Castilla-La Mancha", [
        ("fcr", "Fanega o cuerda", "Ciudad Real (la más usada)", 6440),
        ("fmr", "Fanega de marco real", "Ciudad Real, Cuenca", 6439.56),
        ("fal", "Fanega", "Alcázar de San Juan y su antiguo partido", 6987),
        ("fpu", "Fanega de puño", "Almodóvar, Puertollano", 4293),
        ("fab", "Fanega", "Albacete", 7005.69),
        ("fgu", "Fanega", "Guadalajara", 3105.20),
        ("ft4", "Fanega de 400 estadales", "Toledo", 3757.65),
        ("ft5", "Fanega de 500 estadales", "Toledo", 4697.07),
        ("cel", "Celemín", "1/12 de fanega de marco real", 536.63),
    ]),
    ("cyl", "Castilla y León", [
        ("fmr", "Fanega", "Burgos, Salamanca", 6439.56),
        ("ova", "Obrada", "Valladolid", 4658.25),
        ("opa", "Obrada", "Palencia", 5383.19),
        ("ose", "Obrada", "Segovia", 3940.70),
        ("fav", "Fanega", "Ávila", 3930.40),
        ("fpa", "Fanega de puño", "Ávila", 4192.12),
        ("hav", "Huebra", "Ávila", 2235.96),
        ("hsa", "Huebra", "Salamanca", 4471.92),
        ("pav", "Peonada de prado", "Ávila", 3912.93),
        ("avi", "Aranzada de viña", "Ávila", 4171.92),
        ("hse", "Hemina de secano", "León", 939.41),
        ("hre", "Hemina de regadío", "León", 626.22),
        ("fso", "Fanega", "Soria", 2235.96),
        ("fza", "Fanega", "Zamora", 3353.94),
    ]),
    ("cat", "Cataluña", [
        ("moj", "Mojada (mujada)", "Barcelona", 4896.50),
        ("jor", "Jornal", "Lleida y Barcelona", 4358.04),
        ("ves", "Vesana", "Girona", 2187.43),
        ("crt", "Cana de rey", "Tarragona", 6084),
    ]),
    ("val", "Comunidad Valenciana", [
        ("hng", "Hanegada (fanecada)", "Valencia y Castellón, 200 brazas", 831.10),
        ("czd", "Cahizada", "6 hanegadas", 4986.58),
        ("bra", "Braza real", "Valencia", 4.16),
        ("tah", "Tahúlla", "Alicante (Vega Baja)", 1118.23),
        ("jal", "Jornal", "Alicante", 4804.15),
    ]),
    ("ext", "Extremadura", [
        ("fmr", "Fanega", "Badajoz, Cáceres", 6439.56),
        ("cel", "Celemín", "1/12 de fanega", 536.63),
    ]),
    ("gal", "Galicia", [
        ("fco", "Ferrado", "A Coruña (900 varas²)", 639.58),
        ("fc6", "Ferrado", "A Coruña (625 varas²)", 444.16),
        ("flu", "Ferrado", "Lugo", 436.71),
        ("fou", "Ferrado", "Ourense", 628.86),
        ("fpo", "Ferrado", "Pontevedra", 628.86),
        ("cav", "Cavadura", "Ourense", 436.71),
    ]),
    ("mad", "Madrid", [
        ("fmm", "Fanega (marco de Madrid)", "Madrid", 3423.81),
        ("fvm", "Fanega (con vara de Madrid)", "Madrid", 3482.18),
    ]),
    ("mur", "Murcia", [
        ("tah", "Tahúlla", "Murcia, 1.600 varas²", 1118.23),
        ("och", "Ochava", "1/8 de tahúlla", 139.78),
        ("fmu", "Fanega", "Murcia", 6707.88),
    ]),
    ("nav", "Navarra", [
        ("rob", "Robada", "Navarra", 898.46),
    ]),
    ("pv", "País Vasco", [
        ("fal", "Fanega", "Álava", 2510.80),
        ("fgi", "Fanega", "Gipuzkoa", 3432.79),
        ("gol", "Golde", "Gipuzkoa", 3333),
        ("pbi", "Peonada", "Bizkaia", 380.42),
    ]),
    ("rio", "La Rioja", [
        ("fri", "Fanega", "La Rioja", 1901.96),
    ]),
]


def data(ctx):
    return {"L": {k: [[u, n, w, m] for u, n, w, m in us] for k, _, us in LAND}}


def inputs():
    out = [
        {"id": "cant", "type": "number", "label": "Cantidad", "value": 1, "step": "0.01", "w": "s"},
        {"id": "de", "type": "seg", "label": "En", "value": "u", "options": [("u", "Medida"), ("ha", "Hectáreas"), ("m2", "m²")]},
        {"id": "reg", "type": "select", "label": "Zona", "value": "gen", "options": [(k, n) for k, n, _ in LAND]},
    ]
    for k, _, us in LAND:
        out.append({"id": "u" + k, "type": "select", "label": "Medida", "value": us[0][0], "show": ("reg", [k]), "w": "l",
                    "options": [(u, f"{n} · {w}" if w else n) for u, n, w, _ in us]})
    out.append({"id": "otro", "type": "number", "label": "m² de tu medida", "value": "", "unit": "m²", "w": "s", "show": ("ugen", ["otr"])})
    return out


JS = r"""
function (v, H, C) {
  var reg = v.reg || 'gen', L = C.d.L[reg] || C.d.L.gen, key = v['u' + reg], u = L.filter(function (x) { return x[0] === key; })[0] || L[0];
  var q = v.cant, per = u[3];
  if (reg === 'gen' && u[0] === 'otr') { per = v.otro; if (!(per > 0)) return { err: 'Escribe cuántos m² tiene tu medida.' }; }
  if (isNaN(q)) return { err: 'Escribe una cantidad.' };
  if (q < 0) return { err: 'La cantidad no puede ser negativa.' };
  var m2 = v.de === 'ha' ? q * 1e4 : v.de === 'm2' ? q : q * per;
  function f(x) { var s = H.num(x, x >= 1000 ? 0 : x >= 10 ? 2 : 3); return s.indexOf(',') < 0 ? s : s.replace(/0+$/, '').replace(/,$/, ''); }
  var name = u[0] === 'otr' ? 'tu medida' : u[1].toLowerCase();
  var rows = [['Metros cuadrados', H.num(m2, 2) + ' m²'], ['Hectáreas', H.num(m2 / 1e4, 4) + ' ha'], ['Áreas', H.num(m2 / 100, 2) + ' a']];
  if (!L.some(function (x) { return x[0] === 'fmr'; })) rows.push(['Fanegas de marco real', f(m2 / 6439.56), 'sub']);
  L.forEach(function (x) {
    if (x[3] <= 0 || x[0] === 'ha' || x[0] === 'are') return;
    rows.push([H.esc(x[1]) + (x[2] ? ' <small>' + H.esc(x[2]) + '</small>' : ''), f(m2 / x[3]), x[0] === u[0] ? 'tot' : '']);
  });
  var big = v.de === 'u' ? H.num(m2, 2) + ' m²' : f(m2 / per) + ' ' + (u[0] === 'otr' ? 'medidas' : name + (m2 / per === 1 ? '' : 's'));
  var sub = v.de === 'u' ? H.num(q, q % 1 ? 2 : 0) + ' × ' + H.num(per, 2) + ' m² = ' + H.num(m2 / 1e4, 4) + ' ha'
    : H.num(m2, 2) + ' m² ÷ ' + H.num(per, 2) + ' m² por ' + name;
  return { label: u[0] === 'otr' ? 'Tu medida' : u[1] + (u[2] ? ' · ' + u[2] : ''), big: big, sub: sub, rows: rows,
    note: 'Equivalencias oficiales de cada provincia (Real Orden de 1852). Muchos pueblos usaban una medida propia: si la escritura o el catastro dan los m², manda esa cifra.',
    n: { m2: H.r2(m2), ha: m2 / 1e4, per: per, units: m2 / per } };
}
"""


def blocks(ctx):
    rows = "".join(f"<tr><td>{n}</td><td>{w}</td><td class=\"num\">{ctx.num(m, 2)} m²</td></tr>"
                   for k, rn, us in LAND if k != "gen" for u, n, w, m in us)
    return [
        ("Cuánto mide una fanega, una hanegada o una tahúlla", """
<p>No hay una sola respuesta: antes del sistema métrico cada provincia, y a veces cada pueblo, medía la tierra con su propia
vara. La <b>fanega de marco real</b> de Castilla tiene <b>6.439,56 m²</b> (casi dos tercios de hectárea) y es la que se usa en
Extremadura, Burgos, Salamanca, Cádiz o Granada; en La Mancha se redondea a 6.440 m² y se llama también cuerda. La
<b>hanegada valenciana</b> es mucho más pequeña, <b>831,10 m²</b>, unas doce por hectárea. La <b>tahúlla</b> de la huerta
de Murcia, la Vega Baja y Almería mide <b>1.118,23 m²</b>, y la <b>obrada</b> castellana va de 3.940 m² en Segovia a 5.383 m²
en Palencia.</p>
<p>Elige la zona y la medida, escribe la cantidad y verás los metros cuadrados, las hectáreas y lo que equivale en las demás
medidas de esa zona. Con «Hectáreas» o «m²» haces la cuenta al revés: cuántas hanegadas o fanegas son 2 ha.</p>"""),
        ("Ejemplos", """
<ul>
<li><b>Un campo de 12 hanegadas en la Ribera</b>: 12 × 831,10 = 9.973,2 m², casi una hectárea justa (0,9973 ha).</li>
<li><b>Tres tahúllas en Murcia</b>: 3 × 1.118,23 = 3.354,7 m², 0,34 ha, o 24 ochavas.</li>
<li><b>Una finca de 25 fanegas en Tierra de Campos (Palencia)</b>, si se cuenta en obradas de 5.383,19 m²: 13,46 ha. Las mismas 25
en fanegas de marco real serían 16,10 ha: por eso conviene saber qué fanega usaba el pueblo.</li>
<li><b>10 hectáreas en Badajoz</b> son 15,53 fanegas de 6.439,56 m².</li>
</ul>"""),
        ("De dónde salen los valores", f"""
<p>La Real Orden de 9 de diciembre de 1852 fijó la equivalencia en metros de las pesas y medidas de cada provincia cuando
entró en vigor el sistema métrico. Las cifras de esta tabla son las que publicó el Ministerio de Fomento en las
<a href="{HD1918}" rel="noopener">Hojas divulgadoras de 1918, «Pesas y medidas»</a>, completadas con el resumen de la revista
<a href="{AGRI1993}" rel="noopener">Agricultura (Ministerio de Agricultura, 1993)</a>, que recoge el libro «Medidas y pesos
agrarios» del propio ministerio y encuestas a las cámaras agrarias. Cada medida se calcula a partir de su vara: la vara de
Castilla mide 0,835905 m, así que una vara cuadrada son 0,6987 m² y la fanega de 9.216 varas cuadradas da los 6.439,56 m².</p>
<p>La realidad era más variada que la tabla. En Galicia hay más de medio centenar de ferrados distintos (de unos 400 a más
de 600 m²), en Zaragoza conviven hanegas de 475 y 714 m², y en Ciudad Real se usan fanegas de 3.220, 4.293, 4.400, 6.440, 6.666 y
6.987 m² según el pueblo. Si conoces la medida de tu pueblo, elige «General» y «Otra» y escribe sus metros cuadrados.</p>"""),
        ("Todas las medidas de la tabla", f"""
<table class="tbl"><thead><tr><th>Medida</th><th>Dónde</th><th>Superficie</th></tr></thead><tbody>{rows}</tbody></table>"""),
    ]


FAQ = [
    ("¿Cuántos metros tiene una fanega de tierra?",
     "La fanega de marco real de Castilla tiene 6.439,56 m² (0,644 ha). Es la más extendida, pero en Madrid la fanega mide 3.424 m², en "
     "Ávila 3.930 m², en Soria 2.236 m² y en Albacete 7.006 m². En la Comunidad Valenciana la «fanecada» o hanegada son 831,10 m²."),
    ("¿Cuántas hanegadas tiene una hectárea?",
     "12,03 hanegadas de 831,10 m². En la práctica se dice que 12 hanegadas son una hectárea, aunque faltan unos 27 m²."),
    ("¿Cuántos metros es una tahúlla?",
     "1.118,23 m² en Murcia, la Vega Baja del Segura y las tierras de regadío de Almería: 1.600 varas cuadradas de Castilla. Una "
     "hectárea son 8,94 tahúllas. Se divide en 8 ochavas de 139,78 m²."),
    ("¿Qué es una obrada?",
     "La tierra que una yunta labraba en un día. En Castilla y León mide 4.658,25 m² en Valladolid, 5.383,19 m² en Palencia y "
     "3.940,70 m² en Segovia."),
    ("¿Tienen validez legal estas medidas?",
     "No. Desde la Ley de Pesas y Medidas de 1849 la unidad legal es el sistema métrico, y el catastro y el registro de la propiedad "
     "trabajan en metros cuadrados y hectáreas. Las medidas antiguas se siguen usando en el campo y aparecen en escrituras viejas, "
     "pero cualquier compraventa debe expresar la superficie en m² o ha."),
    ("¿Cuántos metros cuadrados tiene un ferrado gallego?",
     "Depende de la comarca: 639,58 m² en A Coruña (900 varas cuadradas) o 444,16 m² (625 varas), 436,71 m² en Lugo y 628,86 m² en "
     "Ourense y Pontevedra. Hay muchos más ferrados locales, casi todos entre 400 y 650 m²."),
]

TOOL = {
    "slug": "medidas-agrarias",
    "lang": "es",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "map-2",
    "order": 10,
    "name": "Medidas agrarias",
    "k": "fanega hanegada fanecada tahulla obrada ferrado peonada cuartal jornal cuarterada robada hectarea m2 conversor",
    "title": "Fanega, hanegada, tahúlla: conversor a m² y hectáreas",
    "desc": "Convierte fanegas, hanegadas, tahúllas, obradas, ferrados y otras medidas agrarias a m² y hectáreas con la equivalencia oficial de cada provincia.",
    "h1": "Conversor de medidas agrarias",
    "crumb": "Medidas agrarias",
    "updated": "2026-11-12",
    "inputs": inputs(),
    "js": JS,
    "data": data,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Ministerio de Fomento · Hojas divulgadoras 1918, «Pesas y medidas»", HD1918),
                ("Revista Agricultura (Ministerio de Agricultura) n.º 726, 1993, «La fanega como unidad de superficie»", AGRI1993)],
    "credits": [("Equivalencias oficiales de 1852 publicadas por el Ministerio de Fomento (1918) y el Ministerio de Agricultura (1964, 1993)",
                 "dominio público / documento oficial", HD1918)],
    "related": ["marco-plantacion", "abonado-npk", "riego-goteo", "carga-ganadera"],
    "tests": [
        ({"reg": "val", "uval": "hng", "cant": "12"}, {"n.m2": 9973.2, "err": None}),
        ({"reg": "mur", "umur": "tah", "cant": "3"}, {"n.m2": 3354.69}),
        ({"reg": "ext", "uext": "fmr", "cant": "10", "de": "ha"}, {"n.m2": 100000, "n.units": 15.5290}),
        ({"reg": "cyl", "ucyl": "ova", "cant": "2"}, {"n.m2": 9316.5}),
        ({"reg": "gen", "ugen": "otr", "otro": "500", "cant": "4"}, {"n.m2": 2000}),
        ({"reg": "gen", "ugen": "otr", "otro": "", "cant": "4"}, {"err": "Escribe cuántos m² tiene tu medida."}),
        ({"cant": "-3"}, {"err": "La cantidad no puede ser negativa."}),
    ],
}
