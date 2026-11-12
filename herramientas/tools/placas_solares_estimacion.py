"""Placas solares: yearly and monthly production estimate of a rooftop PV system by provincia, orientation and tilt, from
PVGIS 5.3 (EU JRC) yields per kWp, plus a rough saving with self-consumption and surplus compensation. Spanish only.

PV table: PVGIS 5.3 PVcalc API (radiation PVGIS-SARAH3, 2005-2023), 1 kWp crystalline silicon, 14 % system losses,
free-standing, at each provincial capital. Downloaded 12 Nov 2026 (re.jrc.ec.europa.eu/api/v5_3/PVcalc).
Per provincia: (name, [opt, opt_angle, S0, S15, S30, S45, SE30, SW30, E30, W30] kWh/kWp/year, monthly kWh/kWp at S30).
"""
from herramientas.tools import _bricolaje as F

PVGIS = "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en"
RD244 = "https://www.boe.es/buscar/act.php?id=BOE-A-2019-5089"
JRC_REUSE = "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/pvgis-tools_en"

PV = {
    "coruna": ("A Coruña", [1289, 36, 1099, 1222, 1283, 1277, 1202, 1226, 1025, 1057], [62, 80, 110, 125, 138, 132, 149, 143, 124, 95, 65, 61]),
    "alava": ("Álava (Vitoria)", [1273, 35, 1094, 1212, 1268, 1261, 1195, 1209, 1025, 1045], [64, 76, 106, 117, 130, 133, 149, 143, 121, 101, 65, 62]),
    "albacete": ("Albacete", [1656, 36, 1404, 1569, 1648, 1642, 1566, 1549, 1339, 1314], [109, 113, 139, 146, 160, 161, 172, 167, 146, 130, 106, 101]),
    "alicante": ("Alicante", [1611, 35, 1379, 1535, 1606, 1591, 1492, 1537, 1258, 1309], [106, 108, 136, 145, 160, 162, 168, 162, 139, 125, 99, 96]),
    "almeria": ("Almería", [1722, 35, 1475, 1641, 1717, 1701, 1611, 1635, 1370, 1398], [116, 122, 147, 155, 166, 166, 171, 167, 147, 133, 112, 113]),
    "asturias": ("Asturias (Oviedo)", [1205, 38, 1009, 1131, 1195, 1199, 1134, 1118, 968, 944], [69, 82, 107, 115, 120, 111, 121, 123, 114, 96, 69, 67]),
    "avila": ("Ávila", [1530, 35, 1316, 1460, 1526, 1513, 1460, 1436, 1261, 1225], [85, 97, 127, 136, 153, 156, 174, 167, 143, 120, 84, 84]),
    "badajoz": ("Badajoz", [1609, 34, 1382, 1534, 1604, 1588, 1525, 1517, 1314, 1300], [100, 112, 136, 142, 158, 158, 173, 168, 146, 123, 99, 91]),
    "baleares": ("Baleares (Palma)", [1598, 36, 1358, 1515, 1592, 1582, 1501, 1503, 1276, 1281], [101, 106, 139, 148, 161, 161, 168, 160, 135, 122, 96, 95]),
    "barcelona": ("Barcelona", [1570, 38, 1304, 1472, 1558, 1560, 1450, 1477, 1211, 1248], [100, 104, 136, 143, 160, 162, 168, 157, 131, 112, 92, 92]),
    "bizkaia": ("Bizkaia (Bilbao)", [1171, 36, 1000, 1111, 1165, 1162, 1103, 1102, 946, 947], [60, 74, 101, 111, 124, 118, 126, 123, 113, 93, 63, 60]),
    "burgos": ("Burgos", [1470, 35, 1259, 1398, 1464, 1455, 1389, 1392, 1197, 1196], [73, 89, 120, 132, 153, 155, 175, 169, 140, 114, 75, 70]),
    "cantabria": ("Cantabria (Santander)", [1201, 37, 1020, 1137, 1195, 1193, 1123, 1136, 958, 974], [60, 74, 104, 117, 130, 123, 131, 126, 116, 93, 63, 59]),
    "castellon": ("Castellón", [1617, 38, 1350, 1520, 1606, 1606, 1501, 1520, 1260, 1285], [106, 111, 137, 147, 161, 161, 166, 158, 136, 123, 102, 98]),
    "ceuta": ("Ceuta", [1590, 31, 1407, 1539, 1589, 1556, 1489, 1534, 1288, 1345], [104, 104, 132, 140, 158, 164, 170, 162, 139, 120, 101, 95]),
    "ciudad-real": ("Ciudad Real", [1638, 35, 1400, 1559, 1632, 1621, 1552, 1541, 1333, 1314], [102, 111, 138, 145, 159, 160, 173, 169, 147, 131, 102, 95]),
    "cuenca": ("Cuenca", [1607, 37, 1357, 1520, 1599, 1595, 1522, 1498, 1301, 1267], [102, 107, 133, 138, 154, 159, 176, 169, 144, 125, 96, 96]),
    "caceres": ("Cáceres", [1614, 35, 1377, 1534, 1608, 1596, 1531, 1513, 1316, 1288], [100, 112, 137, 144, 158, 159, 173, 168, 145, 122, 98, 92]),
    "cadiz": ("Cádiz", [1707, 33, 1476, 1635, 1704, 1680, 1603, 1626, 1372, 1401], [114, 118, 143, 154, 168, 166, 175, 169, 149, 132, 110, 106]),
    "cordoba": ("Córdoba", [1651, 35, 1413, 1572, 1645, 1631, 1554, 1560, 1328, 1333], [110, 112, 139, 143, 159, 161, 170, 166, 145, 129, 107, 105]),
    "gipuzkoa": ("Gipuzkoa (San Sebastián)", [1180, 37, 1000, 1115, 1173, 1172, 1103, 1113, 941, 955], [60, 76, 102, 112, 122, 118, 126, 126, 115, 92, 63, 60]),
    "girona": ("Girona", [1466, 38, 1210, 1368, 1452, 1459, 1375, 1351, 1162, 1129], [98, 101, 124, 131, 144, 146, 152, 145, 123, 109, 89, 91]),
    "granada": ("Granada", [1675, 34, 1440, 1599, 1671, 1654, 1590, 1568, 1367, 1336], [116, 114, 138, 140, 158, 162, 172, 168, 147, 133, 110, 112]),
    "guadalajara": ("Guadalajara", [1602, 37, 1349, 1512, 1593, 1590, 1518, 1492, 1298, 1259], [98, 108, 134, 142, 156, 158, 174, 168, 145, 122, 94, 93]),
    "huelva": ("Huelva", [1699, 34, 1463, 1623, 1696, 1676, 1602, 1609, 1375, 1382], [114, 117, 143, 150, 166, 164, 174, 169, 150, 131, 110, 107]),
    "huesca": ("Huesca", [1636, 39, 1344, 1525, 1620, 1629, 1519, 1521, 1269, 1272], [96, 117, 143, 148, 162, 161, 173, 168, 146, 123, 96, 87]),
    "jaen": ("Jaén", [1659, 35, 1429, 1585, 1655, 1638, 1583, 1551, 1359, 1321], [109, 114, 140, 143, 160, 162, 172, 168, 146, 133, 105, 104]),
    "la-rioja": ("La Rioja (Logroño)", [1418, 37, 1200, 1341, 1410, 1407, 1335, 1330, 1140, 1133], [79, 92, 122, 129, 142, 144, 161, 155, 131, 109, 76, 71]),
    "las-palmas": ("Las Palmas", [1583, 25, 1470, 1564, 1580, 1517, 1484, 1546, 1314, 1388], [115, 115, 144, 144, 146, 135, 136, 144, 144, 136, 112, 110]),
    "leon": ("León", [1559, 37, 1303, 1466, 1548, 1549, 1465, 1456, 1245, 1227], [83, 106, 136, 143, 158, 158, 174, 169, 145, 114, 87, 76]),
    "lleida": ("Lleida", [1588, 37, 1325, 1492, 1577, 1577, 1481, 1487, 1246, 1254], [88, 113, 145, 146, 162, 158, 169, 163, 142, 123, 94, 74]),
    "lugo": ("Lugo", [1308, 35, 1129, 1248, 1304, 1294, 1206, 1268, 1028, 1108], [64, 82, 112, 123, 139, 137, 155, 150, 125, 98, 63, 58]),
    "madrid": ("Madrid", [1620, 37, 1360, 1527, 1610, 1608, 1532, 1506, 1305, 1265], [103, 110, 136, 143, 157, 159, 173, 167, 145, 123, 97, 96]),
    "melilla": ("Melilla", [1597, 33, 1391, 1534, 1595, 1573, 1492, 1529, 1277, 1325], [114, 112, 135, 137, 148, 152, 157, 155, 137, 130, 108, 108]),
    "murcia": ("Murcia", [1630, 35, 1390, 1549, 1624, 1614, 1530, 1540, 1302, 1316], [115, 111, 138, 143, 159, 160, 166, 158, 136, 126, 108, 105]),
    "malaga": ("Málaga", [1698, 34, 1465, 1624, 1694, 1675, 1599, 1609, 1370, 1380], [118, 118, 142, 148, 164, 165, 171, 166, 148, 132, 112, 109]),
    "navarra": ("Navarra (Pamplona)", [1406, 36, 1194, 1331, 1399, 1396, 1320, 1327, 1129, 1137], [72, 90, 116, 127, 142, 146, 164, 158, 133, 109, 73, 68]),
    "ourense": ("Ourense", [1351, 34, 1168, 1291, 1348, 1335, 1257, 1299, 1076, 1127], [68, 87, 113, 126, 142, 140, 160, 155, 130, 99, 65, 62]),
    "palencia": ("Palencia", [1555, 36, 1316, 1470, 1546, 1542, 1471, 1458, 1263, 1239], [81, 103, 134, 140, 158, 157, 176, 170, 146, 120, 85, 76]),
    "pontevedra": ("Pontevedra", [1352, 35, 1155, 1284, 1347, 1339, 1274, 1279, 1094, 1099], [71, 86, 110, 125, 141, 140, 157, 153, 129, 98, 70, 67]),
    "salamanca": ("Salamanca", [1588, 36, 1350, 1506, 1581, 1573, 1504, 1491, 1292, 1270], [89, 107, 135, 142, 159, 159, 175, 171, 147, 122, 90, 84]),
    "tenerife": ("Santa Cruz de Tenerife", [1767, 25, 1642, 1747, 1763, 1686, 1687, 1711, 1513, 1541], [124, 125, 155, 157, 161, 158, 173, 172, 156, 144, 119, 119]),
    "segovia": ("Segovia", [1507, 35, 1292, 1435, 1502, 1492, 1435, 1416, 1241, 1210], [83, 93, 123, 132, 150, 153, 174, 168, 141, 118, 82, 83]),
    "sevilla": ("Sevilla", [1672, 35, 1432, 1593, 1667, 1651, 1575, 1579, 1348, 1351], [116, 116, 140, 146, 160, 160, 170, 165, 146, 130, 110, 108]),
    "soria": ("Soria", [1532, 37, 1289, 1445, 1523, 1522, 1443, 1431, 1232, 1207], [92, 101, 127, 136, 151, 152, 170, 164, 139, 120, 86, 84]),
    "tarragona": ("Tarragona", [1567, 38, 1295, 1465, 1554, 1559, 1451, 1466, 1212, 1233], [104, 107, 134, 141, 157, 157, 163, 154, 132, 115, 96, 95]),
    "teruel": ("Teruel", [1595, 37, 1343, 1506, 1586, 1583, 1503, 1484, 1279, 1247], [102, 108, 134, 140, 154, 155, 170, 161, 141, 126, 98, 97]),
    "toledo": ("Toledo", [1633, 36, 1383, 1547, 1625, 1619, 1542, 1531, 1317, 1294], [102, 113, 138, 146, 159, 158, 173, 167, 147, 127, 101, 94]),
    "valencia": ("Valencia", [1632, 37, 1367, 1537, 1622, 1620, 1513, 1539, 1270, 1305], [110, 111, 138, 146, 162, 161, 168, 160, 138, 123, 103, 101]),
    "valladolid": ("Valladolid", [1560, 36, 1323, 1477, 1552, 1547, 1478, 1463, 1269, 1244], [81, 104, 133, 140, 158, 158, 174, 170, 147, 122, 87, 77]),
    "zamora": ("Zamora", [1590, 36, 1351, 1508, 1583, 1575, 1512, 1478, 1298, 1248], [84, 110, 139, 145, 162, 161, 177, 173, 150, 121, 87, 75]),
    "zaragoza": ("Zaragoza", [1623, 38, 1344, 1519, 1610, 1615, 1516, 1511, 1275, 1266], [96, 115, 141, 148, 163, 159, 172, 168, 145, 124, 96, 83]),
}

ORI = [("s30", "Sur, 30°"), ("opt", "Sur, inclinación óptima"), ("s15", "Sur, 15°"), ("s45", "Sur, 45°"), ("se30", "Sureste, 30°"),
       ("sw30", "Suroeste, 30°"), ("e30", "Este, 30°"), ("w30", "Oeste, 30°"), ("s0", "Plana, 0°")]
IDX = {"opt": 0, "s0": 2, "s15": 3, "s30": 4, "s45": 5, "se30": 6, "sw30": 7, "e30": 8, "w30": 9}
MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

JS = r"""
function (v, H, C) {
  var EN = false;
  %FMT%
  var D = C.d, row = D.pv[v.prov];
  if (!row) return { err: 'Elige la provincia.' };
  var np = v.paneles > 0 ? v.paneles : 0, wp = v.wp > 0 ? v.wp : 0;
  if (!(np > 0 && wp > 0)) return { err: 'Escribe el número de paneles y su potencia.' };
  var kwp = np * wp / 1000, y1 = row[1][D.idx[v.ori] || 4], sh = v.sombra > 0 && v.sombra < 100 ? v.sombra : 0;
  var yk = y1 * (1 - sh / 100), E = yk * kwp, f = yk / row[1][4];
  var mon = row[2].map(function (m) { return m * f * kwp; });
  var best = 0, worst = 0;
  mon.forEach(function (m, i) { if (m > mon[best]) best = i; if (m < mon[worst]) worst = i; });
  var rows = [['Potencia', fx(kwp, 2) + ' kWp'], ['Por kWp', fx(yk, 0) + ' kWh/año'], ['Producción', fx(E, 0) + ' kWh/año', 'tot'],
    ['Media diaria', fx(E / 365, 1) + ' kWh'], ['Mejor mes', D.mes[best] + ' · ' + fx(mon[best], 0) + ' kWh'], ['Peor mes', D.mes[worst] + ' · ' + fx(mon[worst], 0) + ' kWh']];
  var cons = v.consumo > 0 ? v.consumo : 0, sav = null;
  if (cons) {
    var auto = Math.min(E * (v.auto >= 0 && v.auto <= 100 ? v.auto : 40) / 100, cons), exc = E - auto;
    var pb = v.pcompra > 0 ? v.pcompra : 0, pc = v.pcomp > 0 ? v.pcomp : 0;
    var comp = Math.min(exc * pc, (cons - auto) * pb);
    sav = auto * pb + comp;
    rows.push(['Cubre de tu consumo', fx(Math.min(100, E / cons * 100), 0) + ' %']);
    rows.push(['Autoconsumo', fx(auto, 0) + ' kWh · ' + H.eur(auto * pb)]);
    rows.push(['Excedentes', fx(exc, 0) + ' kWh · ' + H.eur(comp)]);
    rows.push(['Ahorro estimado', '≈ ' + H.eur(sav) + ' al año', 'tot']);
  }
  var mx = Math.max.apply(null, mon);
  var bars = '<div class="pvm">' + mon.map(function (m, i) {
    return '<div><span style="height:' + Math.round(m / mx * 100) + '%"></span><b>' + D.mes[i] + '</b></div>'; }).join('') + '</div>';
  return {
    label: 'Producción estimada', big: fx(E, 0) + ' kWh/año',
    sub: D.pv[v.prov][0] + ' · ' + fx(kwp, 2) + ' kWp · ' + fx(yk, 0) + ' kWh/kWp',
    rows: rows, html: bars,
    note: 'Estimación con datos de PVGIS (Comisión Europea, JRC) para la capital de provincia, con un 14 % de pérdidas del sistema. No incluye sombras salvo las que indiques.',
    n: { kwp: r(kwp, 3), yk: r(yk, 1), e: r(E, 1), sav: sav === null ? null : r(sav, 2) }
  };
}
"""

CSS = (".pvm{display:flex;gap:3px;align-items:flex-end;height:90px;margin:10px 0 0}.pvm div{flex:1;display:flex;flex-direction:column;"
       "justify-content:flex-end;height:100%;text-align:center}.pvm span{display:block;background:var(--brand);border-radius:2px 2px 0 0;"
       "min-height:2px}.pvm b{font-weight:400;font-size:11px;color:var(--mut);margin-top:2px}")


def blocks(ctx):
    n, e = F.n, ctx.eur
    rows = "".join(f"<tr><td>{v[0]}</td><td class=num>{n(v[1][4])}</td><td class=num>{n(v[1][0])} ({v[1][1]}°)</td>"
                   f"<td class=num>{n(v[1][8])}</td></tr>" for k, v in PV.items())
    mad = PV["madrid"][1]
    ovi = PV["asturias"][1]
    e_mad = mad[4] * 2.7
    auto = e_mad * 0.4
    exc = e_mad - auto
    sav = auto * 0.15 + min(exc * 0.06, (4000 - auto) * 0.15)
    return [
        ("Cuánta energía producen las placas en tu provincia", f"""
<p>Una instalación de 6 paneles de 450 W (2,7 kWp) orientada al sur con 30° de inclinación produce en Madrid unos
<b>{n(e_mad)} kWh al año</b>: {n(mad[4])} kWh por cada kWp instalado. En Oviedo la misma instalación daría unos
{n(ovi[4] * 2.7)} kWh, y en Santa Cruz de Tenerife, unos {n(PV['tenerife'][1][4] * 2.7)}. La diferencia entre el norte
cantábrico y el sur peninsular o Canarias ronda el 40 %.</p>
<p>Si en casa consumes 4.000 kWh al año y aprovechas directamente el 40 % de lo que producen las placas (lo habitual sin
batería, porque se produce de día), autoconsumes {n(auto)} kWh, que a 0,15 €/kWh son {e(auto * 0.15)}. Los otros
{n(exc)} kWh van a la red; con compensación simplificada de excedentes a 0,06 €/kWh restan {e(exc * 0.06)} de la factura.
Ahorro estimado: unos <b>{e(sav)} al año</b>.</p>"""),
        ("Orientación e inclinación", """
<p>La orientación sur con 30 a 38° de inclinación es la que más produce en la península; la tabla de abajo da la inclinación
óptima de cada capital. Orientar al este o al oeste reduce la producción anual entre un 14 y un 22 %, pero reparte la
producción a primera hora o por la tarde, cuando suele haber más consumo, y por eso a veces compensa. Una cubierta plana con
los paneles tumbados pierde entre un 13 y un 18 % frente a la inclinación óptima y se ensucia más; en Canarias, más cerca del
ecuador, la pérdida es menor y la inclinación óptima baja a unos 25°.</p>
<p>Las sombras son lo que más daño hace: una chimenea o un árbol que tapa parte de un panel por la tarde puede restar más de
lo que parece, porque los paneles en serie se limitan entre sí. Si tienes sombras parciales, indica en «Más opciones» un
porcentaje de pérdida orientativo o pide un estudio con medición de sombras.</p>"""),
        ("De dónde salen los datos", f"""
<p>Los rendimientos son de <b>PVGIS 5.3</b>, el sistema de información fotovoltaica del Centro Común de Investigación (JRC)
de la Comisión Europea, con la radiación por satélite SARAH-3 de 2005 a 2023, para 1 kWp de silicio cristalino, un 14 % de
pérdidas del sistema (cableado, inversor, suciedad) y la capital de cada provincia. Son medias: un año concreto puede salir un
5 % arriba o abajo. Para tu dirección exacta, PVGIS permite hacer el cálculo en su web gratis.</p>
<p>El ahorro se calcula con el modelo de autoconsumo del Real Decreto 244/2019: lo que consumes al momento te ahorra el precio
completo del kWh, y los excedentes se compensan en la factura a un precio menor, sin que la compensación supere la energía
que compras en el mes (aquí se aproxima en cómputo anual).</p>
<table class="tbl"><thead><tr><th>Provincia</th><th>Sur 30°</th><th>Óptima</th><th>Este 30°</th></tr></thead><tbody>{rows}</tbody></table>
<p class="hnote">kWh al año por kWp instalado. Fuente: PVGIS 5.3, Comisión Europea, JRC.</p>"""),
    ]


FAQ = [
    ("¿Cuánto produce un panel solar de 450 W al año?",
     "Entre 520 y 800 kWh según la provincia, orientado al sur con 30°: unos 725 kWh en Madrid, 540 en Asturias y 790 en Tenerife."),
    ("¿Cuántas placas necesito para mi consumo?",
     "Divide tu consumo anual entre lo que produce un kWp en tu provincia. Con 3.500 kWh al año en Madrid harían falta unos 2,2 kWp, "
     "5 paneles de 450 W, aunque sin batería solo aprovecharás directamente una parte."),
    ("¿Qué inclinación es la mejor?",
     "Entre 33 y 39° en la península y unos 25° en Canarias, orientados al sur. Entre 15 y 45° la pérdida anual es pequeña."),
    ("¿Producen las placas en invierno?",
     "Sí, pero menos: en diciembre, entre el 37 % (Lugo) y el 66 % (Almería) de lo que producen en julio; en Canarias, del 69 al 81 %."),
    ("¿Qué son los excedentes y cuánto me pagan?",
     "La energía que no consumes en el momento y va a la red. Con la compensación simplificada del RD 244/2019 tu comercializadora la "
     "descuenta de la factura a un precio pactado, normalmente bastante menor que el del kWh que compras."),
]

TOOL = {
    "slug": "placas-solares-estimacion",
    "lang": "es",
    "cat": F.CAT_ES[0], "cat_name": F.CAT_ES[1],
    "icon": "solar-panel",
    "order": 66,
    "name": "Producción placas solares",
    "k": "placas solares fotovoltaica kwh kwp producción provincia orientación inclinación autoconsumo ahorro pvgis",
    "title": "Placas solares: producción por provincia (kWh)",
    "desc": "Estima los kWh al año que producirían tus placas solares según la provincia, la orientación y la inclinación, con datos de PVGIS y el ahorro.",
    "h1": "Cuánto producen las placas solares en tu provincia",
    "updated": "2026-11-12",
    "data": {"pv": {k: [v[0], v[1], v[2]] for k, v in PV.items()}, "idx": IDX, "mes": MES},
    "css": CSS,
    "inputs": [
        {"id": "prov", "type": "select", "label": "Provincia", "value": "madrid", "options": [(k, v[0]) for k, v in PV.items()]},
        {"id": "paneles", "type": "number", "label": "Paneles", "value": "6", "w": "s"},
        {"id": "wp", "type": "number", "label": "Potencia panel", "value": "450", "unit": "W", "w": "s"},
        {"id": "ori", "type": "select", "label": "Orientación", "value": "s30", "options": ORI},
        {"id": "consumo", "type": "number", "label": "Tu consumo", "value": "4000", "unit": "kWh/año", "more": True},
        {"id": "auto", "type": "number", "label": "Autoconsumo", "value": "40", "unit": "%", "w": "s", "more": True},
        {"id": "pcompra", "type": "number", "label": "Precio kWh", "value": "0,15", "unit": "€/kWh", "step": "0.001", "w": "s", "more": True},
        {"id": "pcomp", "type": "number", "label": "Excedentes", "value": "0,06", "unit": "€/kWh", "step": "0.001", "w": "s", "more": True},
        {"id": "sombra", "type": "number", "label": "Sombras", "value": "0", "unit": "%", "w": "s", "more": True},
    ],
    "js": F.make(JS, False),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("PVGIS 5.3 · Comisión Europea, Centro Común de Investigación (JRC)", PVGIS),
                ("Real Decreto 244/2019, autoconsumo de energía eléctrica (BOE)", RD244)],
    "credits": [("PVGIS 5.3 (European Commission, Joint Research Centre): rendimientos por provincia", "CC BY 4.0, reutilización con cita", PVGIS)],
    "related": ["consumo-electrodomesticos", "potencia-contratada", "seccion-cable", "frigorias-aire-acondicionado"],
    "tests": [
        ({}, {"n.kwp": 2.7, "n.yk": 1610, "n.e": 4347, "n.sav": 417.31}),
        ({"prov": "asturias", "ori": "e30"}, {"n.yk": 968}),
        ({"sombra": "10"}, {"n.yk": 1449}),
        ({"consumo": "2000"}, {"n.sav": 300.0}),
        ({"consumo": ""}, {"n.sav": None}),
        ({"paneles": "0"}, {"err": "Escribe el número de paneles y su potencia."}),
        ({"prov": "x"}, {"err": "Elige la provincia."}),
    ],
}
