"""Calma Planners shop page: /shopping/ (Spanish). A catalogue that links out to Amazon and Etsy; nothing is sold here.

    python shopping.py            writes shopping/index.html (+ images on first run) and adds it to sitemap-general.xml
    python shopping.py --img      re-downloads / re-renders the product images

build.main() also calls write() on every full build, so the page keeps the current header and footer.
Products are listed by hand below: add a line when a book or listing goes live (ASIN / Etsy listing id + image).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PATH = "shopping/"
UPDATED = "2026-11-12"
BRAND = "Calma Planners"
ETSY_SHOP = "https://www.etsy.com/es/shop/CalmaPlanners"
AMAZON_ES = "https://www.amazon.es/s?k=%22Calma+Planners%22&i=stripbooks"
KDP = ROOT.parent / "agent-forge-pro" / "products" / "kdp"
ETSY_IMG = "https://i.etsystatic.com/68758832/r/il/{h}/{n}/il_570xN.{n}_{s}.jpg"

# (category id, label)
CATS = [("agendas", "Agendas y calendarios"), ("trabajo", "Trabajo y turnos"), ("dinero", "Dinero y presupuesto"),
        ("casa", "Casa y vida"), ("navidad", "Navidad"), ("negocio", "Para tu negocio"), ("libros-en", "In English")]

# Amazon books: (asin, store host, name, category, KDP folder for the cover)
AMAZON = [
    ("B0HQ8FVGZS", "amazon.es", "Agenda semanal 2027 con festivos de España", "agendas", "planner-2027-es"),
    ("B0HR1RPDCP", "amazon.es", "Cuaderno del profesor 2026-2027", "trabajo", "cuaderno-profesor-2026-27-es"),
    ("B0HR1MPM4P", "amazon.es", "Presupuesto familiar 2027", "dinero", "presupuesto-familiar-2027-es"),
    ("B0HPL4MC2C", "amazon.es", "Diario de hábitos: 52 semanas", "casa", "habit-tracker-journal-es"),
    ("B0HQ96KT81", "amazon.com", "2027 Weekly Planner", "libros-en", "planner-2027-en"),
    ("B0HQ87YW3N", "amazon.com", "Habit Tracker Journal: 52 Weeks", "libros-en", "habit-tracker-journal-en"),
]

# Etsy digital downloads: (listing id, image "hash/number/suffix", name, category, language of the files)
ETSY = [
    ("4615573194", "343fed/8891861485/give", "Calendario laboral 2027 imprimible por comunidad", "agendas", "es"),
    ("4609406068", "15e292/8793640140/1xn6", "Agenda 2027 imprimible", "agendas", "es"),
    ("4609379375", "8ef3f0/8841425765/ph9i", "Agenda minimalista imprimible 2027", "agendas", "en"),
    ("4609377955", "913108/8841410957/rp7f", "Agenda digital 2027 para iPad", "agendas", "en"),
    ("4609416934", "955a10/8793722066/7npx", "Calendario de pared imprimible 2027", "agendas", "en"),
    ("4609406658", "41f57c/8793647112/a3jh", "Calendario anual 2027 en una página", "agendas", "en"),
    ("4609417608", "dd2776/8841544147/hpxw", "Pack planificador 2027: 5 plantillas", "agendas", "en"),
    ("4615527417", "6c077b/8891558969/hn0f", "Registro de jornada 2027 Excel y PDF", "trabajo", "es"),
    ("4615528663", "d19f3e/8891573621/eqp8", "Cuadrante de turnos 2027", "trabajo", "es"),
    ("4615575014", "0a3687/8891879013/pijc", "Cuadrante de vacaciones del equipo 2027", "trabajo", "es"),
    ("4615529837", "dd41f0/8891584045/eckp", "Shift rota 2027", "trabajo", "en"),
    ("4615576524", "0c61c5/8844118640/ndmd", "Team holiday planner 2027", "trabajo", "en"),
    ("4609383395", "e13ced/8793635360/afca", "Presupuesto mensual 2027", "dinero", "es"),
    ("4609378747", "607716/8793601954/jlvg", "Planificador de presupuesto 2027", "dinero", "en"),
    ("4609386545", "346aa2/8841478905/klwi", "Presupuesto por nómina (quincenal)", "dinero", "en"),
    ("4609407636", "3be5f7/8793655448/1eml", "Pago de deudas: bola de nieve y avalancha", "dinero", "en"),
    ("4609388573", "b89ba6/8841493575/5tfj", "Objetivos de ahorro y fondo de emergencia", "dinero", "en"),
    ("4609410898", "b01e56/8793678858/9apf", "Facturas mensuales 2027", "dinero", "en"),
    ("4609389749", "680a62/8793683246/g9nh", "Control de suscripciones", "dinero", "en"),
    ("4609390291", "fc54f4/8793687102/2f5u", "Patrimonio neto 2027", "dinero", "en"),
    ("4609388035", "5c9600/8793670792/5y3w", "Presupuesto de estudiante", "dinero", "en"),
    ("4609413008", "61f155/8841513777/4721", "Presupuesto de boda", "dinero", "en"),
    ("4609409286", "3a1c39/8841486533/ryhf", "Menú semanal y lista de la compra", "casa", "es"),
    ("4609408728", "923e9d/8841482685/6cys", "Meal planner (hoja de cálculo)", "casa", "en"),
    ("4609415806", "f1a110/8793714774/ga4s", "Planificador de comidas imprimible", "casa", "en"),
    ("4609393413", "d9a43c/8793710618/sysu", "Calendario de limpieza", "casa", "en"),
    ("4609382729", "d1be08/8793629168/i8eq", "Registro de hábitos 2027", "casa", "en"),
    ("4609392921", "6c0a8d/8841525341/pmdm", "Registro de entrenamientos 2027", "casa", "en"),
    ("4609414040", "7c59c5/8793702584/lpq3", "Registro de lecturas 2027", "casa", "en"),
    ("4609385467", "4d01db/8793651528/bbij", "Objetivos de Año Nuevo 2027", "casa", "en"),
    ("4615544656", "ff3073/8843831862/kctz", "Planificador del Camino de Santiago", "casa", "en"),
    ("4609402434", "4cdadc/8793616306/iwac", "Amigo invisible: sorteo en Excel", "navidad", "es"),
    ("4609402984", "fbb033/8841439995/jvyv", "Lista de regalos de Navidad y Reyes", "navidad", "es"),
    ("4609376107", "a396b5/8793576194/5f3t", "Secret Santa: sorteo de nombres", "navidad", "en"),
    ("4609395830", "b6acfa/8793553776/p65s", "Lista de regalos de Navidad 2026", "navidad", "en"),
    ("4609398372", "f1424e/8841406687/5xcs", "Planificador de la cena de Navidad", "navidad", "en"),
    ("4609401880", "b48484/8793610960/kd4w", "Etiquetas para regalos de Navidad", "navidad", "en"),
    ("4615525521", "986b54/8843756474/omet", "Beneficios y comisiones de Etsy", "negocio", "en"),
    ("4609412482", "e5d631/8841509923/jn2b", "Ingresos de autónomo 2027", "negocio", "en"),
    ("4609413472", "1407c0/8841517325/b6in", "Control de inventario", "negocio", "en"),
    ("4609394525", "5f9279/8841537001/leyb", "Ingresos extra (side hustle)", "negocio", "en"),
]

CSS = """
.shop-h{display:flex;flex-direction:column;gap:12px;padding-top:16px}
.shop-h p{margin:0;color:var(--muted,#5b6470)}
.shop-go{display:flex;flex-wrap:wrap;gap:8px}
.shop-nav{display:flex;flex-wrap:wrap;gap:6px;margin:18px 0 6px;padding:0;list-style:none}
.shop-nav a{display:inline-flex;align-items:center;min-height:36px;padding:0 12px;border:1px solid var(--line,#dde1e6);border-radius:18px;color:inherit;text-decoration:none;font-size:14px;font-weight:600}
.shop-sec{margin-top:26px}
.shop-sec h2{margin:0 0 12px}
.shop-grid{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:14px}
.shop-it a{display:flex;flex-direction:column;height:100%;border:1px solid var(--line,#dde1e6);border-radius:6px;overflow:hidden;color:inherit;text-decoration:none;background:#fff}
.shop-it a:hover{border-color:#a9b1bc}
.shop.doc>*{max-width:none}
.shop-it .im{aspect-ratio:4/3;background:#f3f4f6;display:flex;align-items:center;justify-content:center;overflow:hidden}
.shop-it img{display:block;max-width:100%;max-height:100%;width:auto;height:auto;object-fit:contain}
.shop-it .tx{display:flex;flex-direction:column;gap:6px;padding:10px 10px 12px;flex:1}
.shop-it .nm{font-weight:600;font-size:14px;line-height:1.3}
.shop-it .mt{margin-top:auto;display:flex;gap:6px;align-items:center;font-size:12px;font-weight:600}
.shop-it .st{padding:2px 7px;border-radius:3px;background:#fff4e5;color:#8a4b00}
.shop-it .st.etsy{background:#fdecea;color:#a3311f}
.shop-it .lg{color:var(--muted,#5b6470)}
"""


def img_name(kind, key):
    return f"{kind}-{key}.webp"


def make_images(force=False):
    """Covers from the local KDP folders, Etsy main photos from the Etsy CDN (our own listings), all as 480 px WebP."""
    from PIL import Image
    out = ROOT / "shopping" / "img"
    out.mkdir(parents=True, exist_ok=True)
    for asin, _h, _n, _c, folder in AMAZON:
        dst = out / img_name("a", asin)
        if dst.exists() and not force:
            continue
        im = Image.open(KDP / folder / "preview" / "cover-front.png").convert("RGB")
        im.thumbnail((480, 480))
        im.save(dst, "WEBP", quality=82)
    tmp = ROOT / "shopping" / "_tmp.jpg"
    for lid, img, _n, _c, _l in ETSY:
        dst = out / img_name("e", lid)
        if dst.exists() and not force:
            continue
        h, n, s = img.split("/")
        subprocess.run(["curl", "-sfL", "-A", "Mozilla/5.0", "-o", str(tmp), ETSY_IMG.format(h=h, n=n, s=s)], check=True)
        im = Image.open(tmp).convert("RGB")
        im.thumbnail((480, 480))
        im.save(dst, "WEBP", quality=80)
    tmp.unlink(missing_ok=True)


def card(href, img, name, store, lang):
    E = __import__("build").E
    st = "Amazon" if store == "amazon" else "Etsy"
    lg = f'<span class="lg">{"PDF/Excel" if store == "etsy" else "Libro"}{" · EN" if lang == "en" else ""}</span>'
    return (f'<li class="shop-it"><a href="{href}" target="_blank" rel="noopener">'
            f'<span class="im"><img src="img/{img}" alt="" loading="lazy" width="480" height="360"></span>'
            f'<span class="tx"><span class="nm">{E(name)}</span>'
            f'<span class="mt"><span class="st {store}">{st}</span>{lg}</span></span></a></li>')


def main_html(B):
    items = {c: [] for c, _ in CATS}
    for asin, host, name, cat, _f in AMAZON:
        items[cat].append(card(f"https://www.{host}/dp/{asin}", img_name("a", asin), name, "amazon",
                               "en" if host == "amazon.com" else "es"))
    for lid, _img, name, cat, lang in ETSY:
        items[cat].append(card(f"https://www.etsy.com/es/listing/{lid}", img_name("e", lid), name, "etsy", lang))
    nav = "".join(f'<li><a href="#{c}">{lab}</a></li>' for c, lab in CATS if items[c])
    secs = "".join(f'<section class="shop-sec" id="{c}"><h2>{lab}</h2><ul class="shop-grid">{"".join(items[c])}</ul></section>'
                   for c, lab in CATS if items[c])
    n = len(AMAZON) + len(ETSY)
    return (f'<style>{CSS}</style><div class="wrap doc shop">'
            f'{B.crumbs_html([(B.t("spain"), ""), ("Tienda", PATH)])}'
            f'<div class="shop-h"><h1>{BRAND}: agendas, calendarios y plantillas</h1>'
            f'<p>{n} productos con los festivos de esta web. Se compran en Amazon (libros en papel) o en Etsy (descargas).</p>'
            f'<div class="shop-go"><a class="btn p" href="{ETSY_SHOP}" target="_blank" rel="noopener">Tienda en Etsy</a>'
            f'<a class="btn" href="{AMAZON_ES}" target="_blank" rel="noopener">Libros en Amazon</a>'
            f'<a class="btn" href="{B.BASE}utilidades/">Utilidades gratis</a></div></div>'
            f'<ul class="shop-nav">{nav}</ul>{secs}</div>')


def page_html(B, data):
    head = B.head_html(f"Tienda {BRAND}: agendas 2027, calendarios y plantillas",
                       "Agendas 2027 en papel con los festivos de España en Amazon y plantillas imprimibles y Excel en Etsy: "
                       "calendario laboral, cuadrante de turnos, registro de jornada y presupuesto.",
                       PATH, f"{B.SITE}{B.ASSETS}og/espana.png", ads=False, langs=["es"])
    return B.page(head, "pg", "", main_html(B), data, js=False)


def write(B, data, fix):
    if B.LANG != "es":
        return
    d = ROOT / "shopping"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(fix(page_html(B, data)), "utf-8", newline="\n")


def add_to_sitemap(B):
    f = ROOT / "sitemap-general.xml"
    s = f.read_text("utf-8")
    loc = f"{B.SITE}{B.ASSETS}{PATH}"
    if loc in s:
        return False
    entry = f"  <url><loc>{loc}</loc><lastmod>{UPDATED}</lastmod></url>\n"
    f.write_text(s.replace("</urlset>", entry + "</urlset>"), "utf-8", newline="\n")
    return True


if __name__ == "__main__":
    import build as B
    sys.modules.setdefault("build", B)
    data = B.localize(B.load())
    B.REGIONS = data["regions"]
    fonts = {w: B.short_hash(ROOT / "fonts" / f"public-sans-{w}.woff2") for w in ("400", "600", "700")}
    cssv, jsv = B.short_hash(ROOT / "app.css"), B.short_hash(ROOT / "app.min.js")
    m = re.search(r'data-sidx="(\w+)"', (ROOT / "index.html").read_text("utf-8"))
    sidxv = m.group(1) if m else "0"
    fix = lambda s: (s.replace("{CSSV}", cssv).replace("{JSV}", jsv).replace("{SIDXV}", sidxv)  # noqa: E731
                     .replace("{F400}", fonts["400"]).replace("{F600}", fonts["600"]).replace("{F700}", fonts["700"]))
    make_images("--img" in sys.argv)
    write(B, data, fix)
    print("shopping/index.html written ·", len(AMAZON) + len(ETSY), "products · sitemap added:", add_to_sitemap(B))
