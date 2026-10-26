"""Printable A4 PDFs, Spanish build only (called by build.main after the pages):

    pdf/<key>/calendario-laboral-2027-<key>.pdf            year on one page, landscape (the page's PDF button)
    pdf/<key>/calendario-laboral-2027-<key>-vertical.pdf   year on one page, portrait
    pdf/<key>/calendario-laboral-2027-<key>-mensual.pdf    a month per page, 12 pages (comunidades and zones only)
    pdf/<slug>/calendario-escolar-2026-2027-<slug>.pdf     school year Sep-Jun (a page per province where the
                                                           comunidad has no regional calendar)

<key>: comunidad slug, comunidad-zone (canarias-tenerife, cataluna-aran) or comunidad-city, the same keys as ics/ and csv/.
Same look as the site: Public Sans (fonts/, embedded as a subset), the red mark, the holiday tints. Output is
deterministic (rl_config.invariant), so an unchanged calendar gives an unchanged file.
"""
import datetime as dt
import re

from reportlab import rl_config
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import build as B
from pdfhub import file_of, school_file

rl_config.invariant = 1
F, FS, FB = "PS", "PS-SB", "PS-B"
_fonts = False


def fonts():
    global _fonts
    if not _fonts:
        for name, f in ((F, "Regular"), (FS, "SemiBold"), (FB, "Bold")):
            pdfmetrics.registerFont(TTFont(name, str(B.ROOT / "fonts" / f"PublicSans-{f}.ttf")))
        _fonts = True


C = {k: HexColor(v) for k, v in {
    "ink": "#1b1f24", "ink2": "#3a414b", "mut": "#5b6472", "line": "#d5dae1", "line2": "#e6e9ee", "bg2": "#f5f6f8",
    "we": "#eef0f3", "we_i": "#5f6774", "red": "#c8102e", "white": "#ffffff", "o": "#9aa1ab"}.items()}
K = {k: (HexColor(a), HexColor(b), HexColor(c)) for k, (a, b, c) in {  # fill, border, ink (app.css --n, --n-b, --n-i)
    "n": ("#f4b8b1", "#dc8479", "#5c0f0a"), "r": ("#f6d27a", "#d4a234", "#4a2f00"), "i": ("#a9dfd6", "#4fae9f", "#073f38"),
    "l": ("#cbbdf5", "#9580e3", "#2c1872"), "v": ("#b9d3f2", "#5f93d3", "#0a3260")}.items()}
M = 28  # page margin, pt


def url_of(path):
    return f"{B.SITE}{B.ASSETS}{path}"


def label_of(path):
    return f"{B.HOST}{B.ASSETS}{path}"




# ---------------------------------------------------------------- drawing parts

def new(path, size, title, subject):
    out = B.ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(out), pagesize=size, pageCompression=1, initialFontName=F, initialFontSize=9)
    c.setTitle(title)
    c.setAuthor(B.HOST)
    c.setSubject(subject)
    c.setCreator(B.HOST)
    c.setKeywords("calendario laboral 2027, festivos 2027, pdf, imprimir")
    return c


def text(c, x, y, s, font=F, size=9, color="ink", anchor="l"):
    c.setFont(font, size)
    c.setFillColor(C[color] if isinstance(color, str) else color)
    {"l": c.drawString, "r": c.drawRightString, "c": c.drawCentredString}[anchor](x, y, s)


def width(s, font=F, size=9):
    return pdfmetrics.stringWidth(s, font, size)


def fit(s, w, font, size, lo=6):
    """Largest size <= size (down to lo) at which s fits in w."""
    while size > lo and width(s, font, size) > w:
        size -= 0.5
    return size


def header(c, W, H, title, sub):
    """Wordmark, title, context line. Returns the y below them."""
    y = H - M - 10
    c.setFillColor(C["red"])
    c.roundRect(M, y - 0.5, 9, 9, 1.5, stroke=0, fill=1)
    text(c, M + 15, y, "elcalendariolaboral", FB, 11)
    text(c, M + 15 + width("elcalendariolaboral", FB, 11), y, ".es", F, 11, "mut")
    size = fit(title, W - 2 * M, FB, 20, 12)
    text(c, M, y - 30, title, FB, size)
    text(c, M, y - 46, sub, F, 10, "mut")
    return y - 58


def swatch(c, x, y, s, kind, we=False):
    fill, border, _ = K[kind] if kind in K else (C["white"], C["ink"], None)
    c.setLineWidth(1.4 if we else 0.6)
    c.setStrokeColor(border)
    c.setFillColor(C["white"] if we else fill)
    c.roundRect(x, y, s, s, 1.5, stroke=1, fill=1)


def legend(c, x, y, items):
    """items: [(kind, label)]."""
    for kind, lab in items:
        swatch(c, x, y - 1, 8, kind)
        text(c, x + 12, y, lab, F, 8.5, "ink2")
        x += 12 + width(lab, F, 8.5) + 16


def footer(c, W, source, path):
    y = M - 6
    c.setStrokeColor(C["line"])
    c.setLineWidth(0.5)
    c.line(M, y + 12, W - M, y + 12)
    lab = label_of(path)
    right = width(lab, FS, 7.5)
    text(c, M, y, source, F, fit(source, W - 2 * M - right - 16, F, 7.5, 5.5), "mut")
    text(c, W - M, y, lab, FS, 7.5, "ink2", "r")
    c.linkURL(url_of(path), (W - M - right, y - 2, W - M, y + 8), relative=0)


def month_card(c, x, top, w, h, year, m, hmap, caption=None, weeks=6):
    """One month: the same card as .mon on the page. hmap: {iso: {"kind", "name"}}; kind "o" = outside the period."""
    c.setFillColor(C["bg2"])
    c.roundRect(x, top - h, w, h, 4, stroke=0, fill=1)
    pad = 5
    cap = caption or B.T["_months"][m - 1].capitalize()
    text(c, x + pad + 1, top - pad - 9, cap, FB, 9.5)
    cw = (w - 2 * pad) / 7
    hy = top - pad - 21
    for k, d in enumerate(B.T["_wd1"]):
        text(c, x + pad + cw * k + cw / 2, hy, d, FS, 6.5, "mut", "c")
    gy = hy - 4
    ch = (gy - (top - h + pad)) / weeks
    first = dt.date(year, m, 1)
    nd = ((dt.date(year + (m == 12), m % 12 + 1, 1)) - first).days
    fs = min(8.5, ch * 0.55)
    for d in range(nd):
        day = first + dt.timedelta(d)
        i = first.weekday() + d
        cx, cy = x + pad + cw * (i % 7), gy - ch * (i // 7 + 1)
        we = day.weekday() >= 5
        h_ = hmap.get(day.isoformat())
        kind = h_["kind"] if h_ else None
        ty = cy + ch / 2 - fs * 0.35
        if kind == "o":
            text(c, cx + cw / 2, ty, str(day.day), F, fs, "o", "c")
            continue
        c.setLineWidth(0)
        if kind in K and (not we or kind == "v"):
            c.setFillColor(K[kind][0])
            c.rect(cx + 0.8, cy + 0.8, cw - 1.6, ch - 1.6, stroke=0, fill=1)
            text(c, cx + cw / 2, ty, str(day.day), FB, fs, K[kind][2], "c")
        else:
            c.setFillColor(C["we"] if we else C["white"])
            stroke = kind in K
            if stroke:  # a holiday on Saturday or Sunday: outline only, as on the page
                c.setStrokeColor(K[kind][1])
                c.setLineWidth(1.3)
            c.rect(cx + 0.8 + (0.6 if stroke else 0), cy + 0.8 + (0.6 if stroke else 0),
                   cw - 1.6 - (1.2 if stroke else 0), ch - 1.6 - (1.2 if stroke else 0), stroke=1 if stroke else 0, fill=1)
            text(c, cx + cw / 2, ty, str(day.day), FB if stroke else F, fs, K[kind][2] if stroke else ("we_i" if we else "ink"), "c")


def year_grid(c, x, top, w, h, cols, hmap, gap=10):
    rows = 12 // cols
    cw, chh = (w - gap * (cols - 1)) / cols, (h - gap * (rows - 1)) / rows
    for m in range(1, 13):
        k = m - 1
        month_card(c, x + (cw + gap) * (k % cols), top - (chh + gap) * (k // cols), cw, chh, B.YEAR, m, hmap)


def hol_rows(hols, extra=None):
    """[(kind, weekend, date text, name)] for the list."""
    out = [(h["kind"], B._d(h["date"]).weekday() >= 5, B.dshort(h["date"]), h["name"]) for h in hols]
    return out + (extra or [])


def hol_list_h(w, rows, size):
    return sum(7 + (len(simpleSplit(name, F, size, w - 12)) + 1) * (size + 2.5) + 4 for _, _, _, name in rows)


def hol_list(c, x, top, w, rows, bottom):
    """Holiday list, two lines per holiday: date, then the name (wrapped), as large as fits above bottom."""
    size = 8.5
    while size > 6 and top - hol_list_h(w, rows, size) < bottom:
        size -= 0.25
    y = top
    for kind, we, d, name in rows:
        swatch(c, x, y - 7.5, 7.5, kind, we)
        text(c, x + 12, y - 7, d, FS, size, "we_i" if we else "ink")
        lines = simpleSplit(name, F, size, w - 12)
        for k, ln in enumerate(lines):
            text(c, x + 12, y - 7 - (k + 1) * (size + 2.5), ln, F, size, "ink2")
        y -= 7 + (len(lines) + 1) * (size + 2.5) + 4
        c.setStrokeColor(C["line2"])
        c.setLineWidth(0.5)
        c.line(x, y + 2, x + w, y + 2)
    return y


def hol_list_cols(c, x, top, w, rows, cols=2, size=8, gap=20):
    """Holiday list, one line per holiday, in columns (portrait page)."""
    per = -(-len(rows) // cols)
    cw = (w - gap * (cols - 1)) / cols
    dw = max(width(d, FS, size) for _, _, d, _ in rows) + 8
    for k, (kind, we, d, name) in enumerate(rows):
        cx, y = x + (cw + gap) * (k // per), top - (k % per) * (size + 7.5)
        swatch(c, cx, y - 7, 7, kind, we)
        text(c, cx + 11, y - 6.5, d, FS, size, "we_i" if we else "ink")
        text(c, cx + 11 + dw, y - 6.5, name, F, fit(name, cw - 11 - dw, F, size, 5.5), "ink2")
        c.setStrokeColor(C["line2"])
        c.setLineWidth(0.5)
        c.line(cx, y - 10.5, cx + cw, y - 10.5)


# ---------------------------------------------------------------- labour calendar

def hmap_of(hols):
    out = {}
    for h in hols:
        out.setdefault(h["date"], h)
    return out


def legend_items(kinds):
    return [(k, B.t(B.KINDS[k])) for k in kinds]


def annual(path, title, sub, hols, kinds, source, page_path, portrait=False, extra=None):
    W, H = A4 if portrait else landscape(A4)
    c = new(path, (W, H), title, f"{sub} · {source}")
    y = header(c, W, H, title, sub)
    legend(c, M, y - 6, legend_items(kinds))
    top = y - 22
    rows = hol_rows(hols, extra)
    hmap = hmap_of(hols)
    if portrait:
        list_h = (-(-len(rows) // 2)) * 15.5 + 6
        gh = top - (M + 22) - list_h - 14
        year_grid(c, M, top, W - 2 * M, gh, 3, hmap)
        hol_list_cols(c, M, top - gh - 14, W - 2 * M, rows)
    else:
        lw = 178
        year_grid(c, M, top, W - 2 * M - lw - 18, top - (M + 22), 4, hmap)
        x = W - M - lw
        text(c, x, top - 9, "Festivos 2027", FB, 10)
        hol_list(c, x, top - 18, lw, rows, M + 16)
    footer(c, W, source, page_path)
    c.showPage()
    c.save()


def monthly(path, title, sub, hols, kinds, source, page_path):
    W, H = landscape(A4)
    c = new(path, (W, H), title, f"{sub} · {source}")
    hmap = hmap_of(hols)
    for m in range(1, 13):
        y = H - M - 10
        c.setFillColor(C["red"])
        c.roundRect(M, y - 0.5, 9, 9, 1.5, stroke=0, fill=1)
        text(c, M + 15, y, "elcalendariolaboral", FB, 11)
        text(c, M + 15 + width("elcalendariolaboral", FB, 11), y, ".es", F, 11, "mut")
        text(c, W - M, y, title, FS, 10, "ink2", "r")
        text(c, M, y - 34, f'{B.T["_months"][m - 1].capitalize()} 2027', FB, 24)
        legend(c, W - M - sum(12 + width(lab, F, 8.5) + 16 for _, lab in legend_items(kinds)) + 16, y - 32, legend_items(kinds))
        top = y - 50
        first = dt.date(B.YEAR, m, 1)
        nd = ((dt.date(B.YEAR + (m == 12), m % 12 + 1, 1)) - first).days
        weeks = -(-(first.weekday() + nd) // 7)
        gw = W - 2 * M
        cw = gw / 7
        for k, d in enumerate(B.T["_wd"]):
            text(c, M + cw * k + 6, top - 10, d.capitalize(), FS, 9, "mut")
        gy = top - 18
        ch = (gy - (M + 22)) / weeks
        for d in range(nd):
            day = first + dt.timedelta(d)
            i = first.weekday() + d
            cx, cy = M + cw * (i % 7), gy - ch * (i // 7 + 1)
            we = day.weekday() >= 5
            h = hmap.get(day.isoformat())
            kind = h["kind"] if h else None
            fill = K[kind][0] if kind and not we else (C["we"] if we else C["white"])
            c.setFillColor(fill)
            c.setStrokeColor(K[kind][1] if kind else C["line"])
            c.setLineWidth(1.6 if kind and we else 0.6)
            c.roundRect(cx + 1.5, cy + 1.5, cw - 3, ch - 3, 3, stroke=1, fill=1)
            ink = K[kind][2] if kind else (C["we_i"] if we else C["ink"])
            text(c, cx + 8, cy + ch - 20, str(day.day), FB if kind else FS, 15, ink)
            if h:
                lines = simpleSplit(h["name"], FS, 8, cw - 16)[:3]
                for k, ln in enumerate(lines):
                    text(c, cx + 8, cy + 8 + (len(lines) - 1 - k) * 10, ln, FS, 8, ink)
        footer(c, W, source, page_path)
        c.showPage()
    c.save()


def zone_source(data, slug):
    m = re.search(r"\(([^()]*)\)\s*\.?$", data["zones"][slug]["note"])
    return m.group(1) if m else "boletín autonómico"


def write_all(data, cities, progress=print):
    """Every PDF. Returns [(file path, page path, kind, label, hols)] for the hub and the tests."""
    fonts()
    src = data["source"]
    boe = f'Fuente: {src["id"]} ({src["boe"]})'
    out = []
    regions = data["regions"]
    for r in regions:
        slug = r["slug"]
        names = B.R(r)
        title = B.fill(B.t("h1_region"), names)
        kinds = ["n", "r"] + (["i"] if slug == "canarias" else [])
        hols = B.region_holidays(data, slug)
        can = slug == "canarias"
        n = len(hols)
        sub = (f'{r["official"]} · {B.tn("n_hol", n)}' + (" + fiesta de tu isla" if can else "")
               + f' · {B.tn("n_lab", B.workdays(hols, 1 if can else 0))}')
        extra = [("i", False, "+1", "Fiesta de tu isla")] if can else None
        variants = [(slug, title, sub, hols, boe, extra, None)]
        for o in data["zones"].get(slug, {}).get("options", []):
            if "add" not in o:
                continue
            zh = B.region_holidays(data, slug, o["slug"])
            zsub = f'{o["name"]} · {B.tn("n_hol", len(zh))} · {B.tn("n_lab", B.workdays(zh))}'
            variants.append((f'{slug}-{o["slug"]}', f'{title} · {o["name"]}', zsub, zh,
                             f'Fuente: {src["id"]} + {zone_source(data, slug)}', None, o["name"]))
        for key, ttl, sb, hh, source, ex, zname in variants:
            for kind, portrait in (("", False), ("-vertical", True)):
                annual(file_of(key, kind), ttl, sb, hh, kinds, source, f"{slug}/", portrait, ex)
                out.append((file_of(key, kind), f"{slug}/", kind or "-horizontal", zname, hh))
            monthly(file_of(key, "-mensual"), ttl, sb, hh, kinds, source, f"{slug}/")
            out.append((file_of(key, "-mensual"), f"{slug}/", "-mensual", zname, hh))
        progress(f"pdf · {r['slug']}")
    for k, x in enumerate(cities):
        r = x["r"]
        key = f'{r["slug"]}-{x["slug"]}'
        kinds = ["n", "r"] + (["i"] if r["slug"] == "canarias" else []) + ["l"]
        sub = f'{r["official"]} · {B.tn("n_hol", x["n"])} · {B.tn("n_lab", x["lab"])}'
        source = f'Fuente: {src["id"]} + {x["src_label"]}'
        for kind, portrait in (("", False), ("-vertical", True)):
            annual(file_of(key, kind), x["h1"], sub, x["hols"], kinds, source, x["path"], portrait)
            out.append((file_of(key, kind), x["path"], kind or "-horizontal", x["title_name"], x["hols"]))
        if k % 25 == 24:
            progress(f"pdf · {k + 1}/{len(cities)} ciudades")
    out += school(data)
    progress(f"pdf · {len(out)} archivos")
    return out


# ---------------------------------------------------------------- school calendar

def school_page(c, W, H, title, sub, course, source, page_path):
    import escolar
    y = header(c, W, H, title, sub)
    legend(c, M, y - 6, [("v", "No lectivo"), ("c", "Primer y último día de clase")])
    top = y - 22
    hmap, marks = escolar.grid_marks(course)
    months = [(course.y0, m) for m in range(9, 13)] + [(course.y0 + 1, m) for m in range(1, 7)]
    lines = [(cls, d, name) for iso, cls, d, name in marks]
    list_h = (-(-len(lines) // 3)) * 12 + 4
    gh = top - (M + 22) - list_h - 12
    gap, cols = 10, 5
    cw, chh = (W - 2 * M - gap * (cols - 1)) / cols, (gh - gap) / 2
    for k, (yy, m) in enumerate(months):
        month_card(c, M + (cw + gap) * (k % cols), top - (chh + gap) * (k // cols), cw, chh, yy, m, hmap,
                   f'{B.T["_months"][m - 1].capitalize()} {yy}')
    per = -(-len(lines) // 3)
    lw = (W - 2 * M - 40) / 3
    ly = top - gh - 12
    for k, (cls, d, name) in enumerate(lines):
        iso = marks[k][0]
        x, yy = M + (lw + 20) * (k // per), ly - (k % per) * 12
        swatch(c, x, yy - 7, 7, "v" if cls == "k-v" else ("c" if cls == "k-c" else "v"), cls == "k-p")
        dtx = f'{d} {B.T["_mon3"][int(iso[5:7]) - 1]}'
        text(c, x + 11, yy - 6.5, dtx, FS, 7.5)
        text(c, x + 58, yy - 6.5, name, F, fit(name, lw - 58, F, 7.5, 5), "ink2")
    footer(c, W, source, page_path)
    c.showPage()


def school(data):
    import escolar
    e = escolar.load("escolar-2026-27.json")
    if not e:
        return []
    escolar.LAB = data
    escolar.DATA = e
    by = {x["slug"]: x for x in e["regions"]}
    out = []
    W, H = landscape(A4)
    for r in data["regions"]:
        x = by.get(r["slug"])
        if not x:
            continue
        slug = r["slug"]
        names = B.R(r)
        title = f'Calendario escolar 2026-2027 {names["region_of"]}'
        path = school_file(slug)
        page_path = f"calendario-escolar/{slug}/"
        c = new(path, (W, H), title, title)
        if escolar.provinces_mode(x):
            for name, _, course, p in escolar.provinces(x):
                sub = f"{name}" + (f" · {course.label}: {B.dmon(course.start)} – {B.dmon(course.end)}" if course.start and course.end else "")
                school_page(c, W, H, title, sub, course, f'Fuente: {escolar.src_label(p["source"])}', page_path)
        else:
            course = escolar.Course(x, slug, e["course"])
            sub = r["official"] + (f" · {course.label}: {B.dmon(course.start)} – {B.dmon(course.end)}" if course.start and course.end else "")
            school_page(c, W, H, title, sub, course, f'Fuente: {escolar.src_label(x["source"])}', page_path)
        c.save()
        out.append((path, page_path, "-escolar", None, None))
    return out
