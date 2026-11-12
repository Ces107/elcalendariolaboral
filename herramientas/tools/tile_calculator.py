"""Tile calculator (English twin of calculadora-azulejos): same compute, feet/inches or metres/centimetres."""
from herramientas.tools import _bricolaje as F
from herramientas.tools.calculadora_azulejos import JS, tiles

ANSI = "https://tcnatile.com/products/publications/2026-tcna-handbook-for-ceramic-glass-and-stone-tile-installation/"
CTE_SUA_EN = "https://www.codigotecnico.org/pdf/Documentos/SUA/DBSUA.pdf"


def blocks(ctx):
    n = lambda x, d=0: F.n(x, d, True)  # noqa: E731
    area_m = 80 * 0.09290304
    cell = (12 * 0.0254 + 0.125 * 0.0254) * (24 * 0.0254 + 0.125 * 0.0254)
    raw = area_m / cell
    pcs = int(-(-raw * 1.1 // 1))
    raw_m, pcs_m, bx_m = tiles(6, 60, 30, 2, 10, 8)
    g_lb = (304.8 + 609.6) / (304.8 * 609.6) * 9.525 * 3.175 * 1.6 * area_m * 2.20462
    return [
        ("How many tiles do I need", f"""
<p>Divide the floor or wall area by the space one tile takes <b>including its grout joint</b>, add a waste allowance and round up
to whole boxes. A 10 × 8 ft bathroom floor (80 sq ft) laid with 12 × 24 in porcelain and 1/8 in joints takes {n(raw, 1)} tiles;
with 10% waste that is <b>{pcs} tiles</b>, or six boxes of eight. In metric, a 3 × 2 m floor with 30 × 60 cm tiles and 2 mm joints
needs {n(raw_m, 1)} tiles, {pcs_m} with waste, {bx_m} boxes.</p>
<p>The joint matters more with small tiles: a 4 × 4 in tile with a 1/8 in joint occupies about 6% more area than the tile alone,
so dividing the area by the bare tile size overestimates the count. For mosaic sheets, enter the sheet size and set the joint
to zero, since the spacing is already built into the sheet.</p>"""),
        ("Choosing the waste allowance", """
<p>Waste covers cuts along the edges, tiles that crack while cutting and a few spares. Use 5% only for a plain rectangular room
with small tiles in a straight grid. 10% is the normal figure. Go to 15% for diagonal or herringbone layouts, large-format tiles
(24 × 48 in, 60 × 120 cm and up) and rooms with many corners, columns or a tub, because each cut leaves an offcut you cannot
reuse elsewhere.</p>
<p>Buy every box at once and check that the shade (or lot) and caliber codes printed on the cartons match: two production runs can
differ slightly in colour or size, and it shows on the floor. Keep a few spare tiles for future repairs, when the line may be
discontinued.</p>"""),
        ("Grout joints and how much grout", f"""
<p>Even rectified porcelain needs a joint: the TCNA Handbook and the ANSI A108 installation standards in North America, like most
European guides, advise against butt-jointing tiles. A 1/16 or 1/8 in joint is usual for rectified tile indoors, 3/16 to 1/4 in
for hand-made or rustic tile, and wider joints plus perimeter movement joints outdoors or over underfloor heating.</p>
<p>Grout is worked out from the length of joint per unit of area: (tile length + tile width) ÷ (length × width), times the tile
thickness and the joint width, times the density of cement grout (about 1.6 kg per litre). For the 80 sq ft example with 3/8 in
thick tiles that comes to roughly {n(g_lb, 1)} lb, so a single small bag. Small tiles with wide joints can need ten times as much.</p>"""),
    ]


FAQ = [
    ("How many 12 × 24 tiles are in a box?",
     "Usually eight, which covers 16 sq ft, but some brands pack six or seven. Check the carton or the product page before ordering."),
    ("How much extra tile should I buy?",
     "10% for a standard straight layout, 5% for a very simple room with small tiles, 15% for diagonal, herringbone or large-format tile."),
    ("Do I subtract the tub or cabinets?",
     "Yes. Enter the area you will not tile in «Leave out» under More options: a 60 × 30 in tub is 12.5 sq ft."),
    ("What grout joint width should I use?",
     "1/16 to 1/8 in for rectified porcelain indoors, 3/16 to 1/4 in for non-rectified, rustic or outdoor tile. The tile maker states the minimum."),
    ("Does the calculator work for wall tile?",
     "Yes: enter the width and height of the wall as length and width, then leave out windows and doors."),
]

FR_J = [("0.0625", "1/16 in"), ("0.125", "1/8 in"), ("0.1875", "3/16 in"), ("0.25", "1/4 in")]
FR_T = [("0.25", "1/4 in"), ("0.3125", "5/16 in"), ("0.375", "3/8 in"), ("0.5", "1/2 in")]

TOOL = {
    "slug": "tile-calculator",
    "lang": "en",
    "twin": "calculadora-azulejos",
    "cat": F.CAT_EN[0], "cat_name": F.CAT_EN[1],
    "icon": "layout-grid",
    "order": 20,
    "name": "Tile calculator",
    "k": "how many tiles floor wall boxes grout waste porcelain ceramic square feet",
    "title": "Tile Calculator: How Many Tiles and Boxes Do I Need?",
    "desc": "Work out how many floor or wall tiles and boxes to buy, with grout joints, waste and grout quantity, in feet or metres.",
    "h1": "Tile calculator",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "u", "type": "seg", "label": "Units", "value": "us", "options": [("us", "ft · in"), ("m", "m · cm")]},
        {"id": "l", "type": "number", "label": "Length", "value": "10", "step": "0.01"},
        {"id": "a", "type": "number", "label": "Width", "value": "8", "step": "0.01"},
        {"id": "plin", "type": "number", "label": "Tile length", "value": "24", "unit": "in", "step": "0.01", "w": "s", "show": ("u", ["us"])},
        {"id": "pain", "type": "number", "label": "Tile width", "value": "12", "unit": "in", "step": "0.01", "w": "s", "show": ("u", ["us"])},
        {"id": "pl", "type": "number", "label": "Tile length", "value": "60", "unit": "cm", "step": "0.1", "w": "s", "show": ("u", ["m"])},
        {"id": "pa", "type": "number", "label": "Tile width", "value": "30", "unit": "cm", "step": "0.1", "w": "s", "show": ("u", ["m"])},
        {"id": "jin", "type": "select", "label": "Joint", "value": "0.125", "options": FR_J, "show": ("u", ["us"])},
        {"id": "junta", "type": "number", "label": "Joint", "value": "2", "unit": "mm", "step": "0.5", "w": "s", "show": ("u", ["m"])},
        {"id": "merma", "type": "seg", "label": "Waste", "value": "10", "options": [("5", "5%"), ("10", "10%"), ("15", "15%")]},
        {"id": "caja", "type": "number", "label": "Tiles/box", "value": "8", "w": "s"},
        {"id": "resta", "type": "number", "label": "Leave out", "value": "0", "step": "0.01", "more": True},
        {"id": "espin", "type": "select", "label": "Thickness", "value": "0.375", "options": FR_T, "more": True, "show": ("u", ["us"])},
        {"id": "esp", "type": "number", "label": "Thickness", "value": "9", "unit": "mm", "w": "s", "more": True, "show": ("u", ["m"])},
    ],
    "js": F.make(JS, True),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("TCNA Handbook for Ceramic, Glass, and Stone Tile Installation", ANSI),
                ("Spanish Building Code CTE, DB-SUA 1 (slip resistance classes of floors)", CTE_SUA_EN)],
    "related": ["flooring-calculator", "paint-calculator", "concrete-calculator", "wallpaper-calculator"],
    "tests": [
        ({}, {"n.pcs": 44, "n.boxes": 6}),
        ({"u": "m", "l": "3", "a": "2"}, {"n.pcs": 37, "n.boxes": 5, "n.grout": 0.864}),
        ({"merma": "15"}, {"n.pcs": 46}),
        ({"a": "0"}, {"err": "Enter the length and width of the area."}),
        ({"plin": ""}, {"err": "Enter the tile size."}),
    ],
}
