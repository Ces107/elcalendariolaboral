"""Utility pages, called by pages.write_pages for every language; each page exists in the languages of its ONLY list:

    /semana/                ISO 8601 week of today (util.js; the HTML carries the build date as a fallback) and the
                            week tables of 2026 and 2027

Shared parts (head, header, footer, sections, FAQ, JSON-LD) are the ones of build.py and pages.py. util.js holds the
browser code; its pure functions are exported for node (test_utilidades.py runs them).
"""
import datetime as dt
import json

import build as B
from build import E

TODAY = dt.date.today()  # static fallback only: util.js writes the visitor's date
UPDATED = "2026-10-27"
YEARS = (2026, 2027)

# ---------------------------------------------------------------- strings

S = {
    "es": {
        "util": "Utilidades",
        "wk_link": "¿En qué semana estamos?",
        "wk_title": "¿En qué semana estamos? Número de semana de hoy",
        "wk_desc": "El número de semana de hoy según la ISO 8601, con su lunes y su domingo, y el calendario de semanas de 2026 y 2027 con las fechas de cada una.",
        "wk_h1": "¿En qué semana estamos?", "wk_crumb": "Número de semana",
        "wk_intro": "Semanas de lunes a domingo, numeradas según la ISO 8601, la norma que se usa en España.",
        "week": "Semana", "weeks_of": "Semanas de {y}", "col_week": "Semana", "col_mon_sun": "Lunes – domingo",
        "n_weeks": "{n} semanas",
        "left": {"one": "queda {n} día de {y}", "other": "quedan {n} días de {y}"},
        "wk_faq": [
            ("¿Cómo se numeran las semanas del año?",
             "Según la norma ISO 8601, la que se usa en España y en Europa: cada semana va de lunes a domingo y la semana 1 es la que "
             "contiene el primer jueves del año, es decir, la del 4 de enero."),
            ("¿Cuántas semanas tiene {y1}? ¿Y {y2}?",
             "{y1} tiene {n1} semanas y {y2} tiene {n2}. La semana 1 de {y2} empieza el {w1}."),
            ("¿En qué semana cae el 1 de enero de {y2}?",
             "En la semana {jw} de {jy}, que va del {jmon} al {jsun}."),
            ("¿Cómo saco el número de semana en Excel?",
             "Con =ISO.NUM.DE.SEMANA(A1) (en inglés, =ISOWEEKNUM(A1)). NUM.DE.SEMANA, sin «ISO», empieza la semana en domingo y "
             "puede dar otro número."),
        ],
    },
}
ONLY_WK = [x for x in ("es", "ca", "gl", "eu") if x in S]
PATH_WK = "semana/"


def L(key):
    return S[B.LANG][key]


def ln(key, n, **kw):
    v = L(key)
    return (v["one"] if n == 1 else v["other"]).format(n=n, **kw)


def langs_arg(only):
    """write() and head_html() take None for 'every language'."""
    return None if set(only) >= set(B.LANGS) else only


# ---------------------------------------------------------------- dates

def ds(d, year=None):
    """dshort, with the year when the date is outside `year` (or always when year is None)."""
    s = B.dshort(d)
    if year is not None and d.year == year:
        return s
    return f"{d.year} {s}" if B.LANG == "eu" else f"{s} {d.year}"


def rng(a, b, year=None):
    if a.month == b.month and a.year == b.year and B.LANG != "eu":
        return f'{B.T["_wd3"][a.weekday()]} {a.day} – {ds(b, year)}'
    return f"{ds(a, year)} – {ds(b, year)}"


def dlong_y(d):
    """lunes 4 de enero de 2027 (Spanish only: the FAQ strings of other languages carry their own pattern)."""
    if B.LANG == "es":
        return f'{B.dlong(d)} de {d.year}'
    return ds(d)


def weeks(year):
    """[(week, monday, sunday)] of an ISO year."""
    d, out = dt.date.fromisocalendar(year, 1, 1), []
    while d.isocalendar()[0] == year:
        out.append((d.isocalendar()[1], d, d + dt.timedelta(6)))
        d += dt.timedelta(7)
    return out


# ---------------------------------------------------------------- shared html

def js_cfg(cfg):
    js = json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<script id="u-data" type="application/json">{js}</script>\n'
            f'<script src="{B.ASSETS}util.js?v={B.short_hash(B.ROOT / "util.js")}"></script>')


def base_cfg():
    return {"wd3": B.T["_wd3"], "mon3": B.T["_mon3"], "wd": B.T["_wd"], "eu": B.LANG == "eu"}


def faq(qas):
    import pages
    return pages.faq_html(qas), pages.faq_ld(qas)


def ld(*objs):
    import pages
    return pages.ld(*objs)


def crumbs(name, path):
    import pages
    items = [(B.t("spain"), ""), (name, path)]
    return B.crumbs_html(items), pages.crumbs_ld(items)


def app_ld(name, path, desc):
    return {"@type": "WebApplication", "name": name, "url": B.URL + path, "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Web", "inLanguage": B.IN_LANG[B.LANG], "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "description": desc}


def card(big_id, big, label, sub, label_first=False):
    """The big-number card of the vacation optimizer (.vres), without its share buttons."""
    n = f'<b class="vh-n" id="{big_id}">{big}</b>'
    t = f'<span class="vh-t" id="{big_id}-t">{label}</span>'
    return (f'<div class="vres"><div class="vres-t"><p class="vhd">{t + n if label_first else n + t}</p>'
            f'<p class="vh-s">{sub}</p></div></div>')


# ---------------------------------------------------------------- 1 /semana/

def week_page(data, write):
    y, w, _ = TODAY.isocalendar()
    mon = TODAY - dt.timedelta(TODAY.weekday())
    left = (dt.date(TODAY.year, 12, 31) - TODAY).days
    sub = (f'<span id="wr">{rng(mon, mon + dt.timedelta(6))}</span> · '
           f'<span id="wl">{ln("left", left, y=TODAY.year)}</span>')
    h1 = L("wk_h1")
    ch, cld = crumbs(L("wk_crumb"), PATH_WK)
    hero = (f'<div class="hero wrap">{ch}<h1>{E(h1)}</h1><p class="ctx">{E(L("wk_intro"))}</p>'
            f'{card("wn", w, L("week"), sub, label_first=True)}</div>')
    secs = []
    for year in YEARS:
        ws = weeks(year)
        rows = "".join(f'<tr data-w="{year}-{n}"{" class=on" if (year, n) == (y, w) else ""}><th scope="row">{n}</th>'
                       f'<td>{rng(a, b, year)}</td></tr>' for n, a, b in ws)
        tbl = (f'<table class="tbl vrank wk"><thead><tr><th scope="col">{L("col_week")}</th><th scope="col">{L("col_mon_sun")}</th></tr></thead>'
               f'<tbody>{rows}</tbody></table>')
        secs.append(B.section(f"s{year}", L("weeks_of").format(y=year), tbl, f'<p class="m">{L("n_weeks").format(n=len(ws))}</p>'))
    y1, y2 = YEARS
    jy, jw, _ = dt.date(y2, 1, 1).isocalendar()
    jmon = dt.date.fromisocalendar(jy, jw, 1)
    fmt = {"y1": y1, "y2": y2, "n1": len(weeks(y1)), "n2": len(weeks(y2)), "w1": dlong_y(dt.date.fromisocalendar(y2, 1, 1)),
           "jw": jw, "jy": jy, "jmon": dlong_y(jmon), "jsun": dlong_y(jmon + dt.timedelta(6))}
    qas = [(q.format(**fmt), a.format(**fmt)) for q, a in L("wk_faq")]
    fh, fld = faq(qas)
    main = (f'{hero}<div class="wrap body narrow">{secs[0]}{B.ad("hub")}{secs[1]}{fh}</div>'
            + js_cfg({**base_cfg(), "page": "week", "left": L("left")}))
    head = B.head_html(L("wk_title"), L("wk_desc"), PATH_WK, f"{B.SITE}{B.ASSETS}og/espana.png", ld(cld, fld),
                       langs=langs_arg(ONLY_WK))
    write(PATH_WK, B.page(head, "pg", "", main, data, js=False), UPDATED, langs_arg(ONLY_WK))


# ---------------------------------------------------------------- footer and entry point

def footer_links():
    """The 'Utilidades' block of the footer: the pages in this language, or the Spanish ones marked hreflang=es."""
    s = S.get(B.LANG, S["es"])
    items = [(PATH_WK, ONLY_WK, "wk_link")]
    li = []
    for path, only, key in items:
        if B.LANG in only:
            li.append(f'<li><a href="{B.BASE}{path}">{E(s[key])}</a></li>')
        else:
            li.append(f'<li><a href="{B.ASSETS}{path}" hreflang="es" lang="es">{E(S["es"][key])}</a></li>')
    return f'<h2>{E(s["util"])}</h2><ul>{"".join(li)}</ul>'


def write_pages(data, write):
    if B.LANG in ONLY_WK:
        week_page(data, write)
