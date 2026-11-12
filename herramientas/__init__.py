"""Tools hub: /utilidades/ (Spanish) and /en/tools/ (English, written once a tool has lang "en").

A tool is ONE declarative file, herramientas/tools/<slug>.py, holding a TOOL dict (texts, inputs spec, a pure JS
compute function, explanation blocks, FAQ, sources, related tools, node test cases). This package renders every
tool with one template (tool_page) and one browser runtime (herramientas/js/h.js). The contract is documented in
seo/herramientas-PROGRESS.md; check_tool() enforces it at build time.

Called by pages.write_pages (Spanish build only): write_pages(data, write, cities).
"""
import datetime as dt
import html
import importlib
import json
import pkgutil
import re
import subprocess
from pathlib import Path

import build as B
from build import E

HERE = Path(__file__).resolve().parent
GEN = HERE / "_gen"                      # generated t-<slug>.js before minifying (git-ignored)
ASSETS_OUT = B.ROOT / "utilidades" / "a"  # published runtime, css and per-tool scripts
HUB = {"es": "utilidades/", "en": "en/tools/"}
HUB_UPDATED = "2026-11-12"

# Hub categories, in display order. A tool's "cat" must be one of these keys (add new ones here).
CATS = {
    "es": [("trabajo", "Trabajo y nómina"), ("fechas", "Fechas y calendario"), ("dinero", "Dinero e impuestos"),
           ("vivienda", "Vivienda y alquiler"), ("vehiculos", "Coche y tráfico"), ("tramites", "Trámites y documentos"),
           ("texto", "Texto y números"), ("vendedores", "Vendedores online"), ("ocio", "Ocio y sorteos")],
    "en": [("work", "Work"), ("dates", "Dates"), ("money", "Money"), ("sellers", "Online sellers"), ("text", "Text and numbers")],
}

# Pages outside this package that the Spanish hub lists too (utilidades.py, vacaciones.py).
LEGACY = [
    {"path": "dias-habiles/", "name": "Días hábiles entre fechas", "cat": "fechas", "icon": "calendar-stats", "k": "plazos laborables"},
    {"path": "dias-laborables-2027/", "name": "Días laborables 2027", "cat": "trabajo", "icon": "briefcase", "k": "horas año"},
    {"path": "vacaciones-2027/", "name": "Maximizar vacaciones 2027", "cat": "trabajo", "icon": "calendar-event", "k": "puentes optimizar"},
    {"path": "semana/", "name": "Número de semana", "cat": "fechas", "icon": "calendar-week", "k": "iso semana"},
    {"path": "cambio-de-hora/", "name": "Cambio de hora", "cat": "fechas", "icon": "clock-hour-4", "k": "horario verano invierno"},
]

# Runtime strings (h.js reads them from #h-data.s) and template labels.
L = {
    "es": {"hub": "Utilidades", "home": "España", "more": "Más opciones", "faq": "Preguntas frecuentes", "upd": "Actualizado",
           "src": "Fuente", "srcs": "Fuentes", "related": "Otras utilidades", "print": "Imprimir o PDF", "ics": "Descargar .ics",
           "link": "Copiar enlace", "copied": "Enlace copiado", "err": "Revisa los datos.", "nat_only": "Solo festivos nacionales",
           "all_region": "Toda la comunidad", "isla": "isla", "zona": "zona", "region": "Comunidad", "municipio": "Municipio",
           "search": "Buscar utilidad", "search_ph": "finiquito, turnos, IBAN…", "none": "Ninguna utilidad coincide.",
           "noscript": "Esta calculadora necesita JavaScript.", "all": "Todas las utilidades", "credits": "Créditos",
           "all_credits": "todos los créditos"},
    "en": {"hub": "Tools", "home": "Tools", "more": "More options", "faq": "Frequently asked questions", "upd": "Updated",
           "src": "Source", "srcs": "Sources", "related": "More tools", "print": "Print or PDF", "ics": "Download .ics",
           "link": "Copy link", "copied": "Link copied", "err": "Check the numbers.", "nat_only": "National holidays only",
           "all_region": "Whole region", "isla": "island", "zona": "area", "region": "Region", "municipio": "Town",
           "search": "Search tools", "search_ph": "fees, size, royalties…", "none": "No tool matches.",
           "noscript": "This calculator needs JavaScript.", "all": "All tools", "credits": "Credits", "all_credits": "all credits"},
}
REQUIRED = ("slug", "lang", "cat", "icon", "name", "title", "desc", "h1", "updated", "inputs", "js", "blocks", "faq", "sources")
INPUT_TYPES = ("number", "money", "date", "month", "select", "seg", "check", "text", "time", "place")
MON = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
MON_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


# ---------------------------------------------------------------- registry

_TOOLS = None


def registry():
    """Every tool module in herramientas/tools/ (files starting with _ are skipped), checked, in hub order."""
    global _TOOLS
    if _TOOLS is None:
        out = []
        for m in pkgutil.iter_modules([str(HERE / "tools")]):
            if m.name.startswith("_"):
                continue
            mod = importlib.import_module(f"herramientas.tools.{m.name}")
            t = {"order": 100, "twin": None, "related": [], "intro": "", "tests": [], "hol": (), "data": None, "crumb": None, "k": "",
                 "link": True, "css": "", "credits": [], "cat_name": None, "footer": False, "file": m.name, **mod.TOOL}
            t["crumb"] = t["crumb"] or t["name"]
            check_tool(t)
            out.append(t)
        slugs = [t["slug"] for t in out]
        dup = {s for s in slugs if slugs.count(s) > 1}
        assert not dup, f"duplicate tool slugs: {dup}"
        _TOOLS = sorted(out, key=lambda t: (t["order"], t["slug"]))
    return _TOOLS


def cats(lang):
    """Hub categories of a language: CATS first, then new ones declared by tools (cat + cat_name), in tool order."""
    out = list(CATS[lang])
    for t in registry():
        if t["lang"] == lang and t["cat"] not in dict(out):
            out.append((t["cat"], t["cat_name"]))
    return out


def check_tool(t):
    miss = [k for k in REQUIRED if k not in t]
    assert not miss, f'{t.get("slug")}: missing {miss}'
    s = t["slug"]
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", s), f"{s}: slug"
    assert t["lang"] in HUB, f"{s}: lang"
    assert t["cat"] in dict(CATS[t["lang"]]) or t["cat_name"], f'{s}: category {t["cat"]}: use a CATS key or give "cat_name"'
    assert (HERE / "icons" / f'{t["icon"]}.svg').exists(), f'{s}: icon herramientas/icons/{t["icon"]}.svg'
    for c in t["credits"]:
        assert len(c) == 3 and c[2].startswith("http"), f"{s}: credits are (name, licence, url)"
    assert len(t["title"]) <= 60, f'{s}: title {len(t["title"])} > 60'
    assert 70 <= len(t["desc"]) <= 155, f'{s}: meta description {len(t["desc"])} (70-155)'
    assert 1 <= len(t["name"].split()) <= 4, f"{s}: card name 1-4 words"
    assert t["sources"], f"{s}: at least one official source"
    ids = [i["id"] for i in t["inputs"]]
    assert len(ids) == len(set(ids)), f"{s}: duplicate input ids"
    for i in t["inputs"]:
        assert i["type"] in INPUT_TYPES, f'{s}: input type {i["type"]}'
        assert re.fullmatch(r"[a-z][a-z0-9]*", i["id"]), f'{s}: input id {i["id"]} (lowercase letters/digits)'


def path(t):
    return HUB[t["lang"]] + t["slug"] + "/"


def by_slug(slug):
    return next((t for t in registry() if t["slug"] == slug), None)


# ---------------------------------------------------------------- context given to tools

class Ctx:
    """What a tool's callables (blocks, faq, data) receive: the 2027 data, published cities, holiday data."""

    def __init__(self, data, cities):
        self.data, self.cities, self._hol = data, cities, {}

    def hol(self, years=(2026, 2027)):
        """National, comunidad, zone and city holidays for H.holidays() (same data as /dias-habiles/)."""
        years = tuple(years)
        if years not in self._hol:
            import utilidades as U
            datas = [U.load_year(2026) if y == 2026 else self.data for y in years if y in (2026, 2027)]
            c = U.dh_data(datas, self.cities)
            keep = lambda x: x[0][:4] in {str(y) for y in years}  # noqa: E731
            c = {"nat": [x for x in c["nat"] if keep(x)], "reg": {k: [x for x in v if keep(x)] for k, v in c["reg"].items()},
                 "zon": {k: [[z[0], z[1], [x for x in z[2] if keep(x)], [d for d in z[3] if d[:4] in {str(y) for y in years}]] for z in v]
                         for k, v in c["zon"].items()},
                 "cit": {k: [[x[0], x[1], x[2], [h for h in x[3] if keep(h)]] for x in v] for k, v in c["cit"].items()}}
            self._hol[years] = c
        return self._hol[years]

    @staticmethod
    def eur(x, dec=2):
        s = f"{abs(x):,.{dec}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
        return ("−" if x < 0 else "") + s + " €"

    @staticmethod
    def num(x, dec=0):
        s = f"{abs(x):,.{dec}f}".replace(",", " ").replace(".", ",").replace(" ", ".")
        return ("−" if x < 0 else "") + s


def _call(x, ctx):
    return x(ctx) if callable(x) else x


# ---------------------------------------------------------------- form rendering (one template for every tool)

def icon(name, cls="hic"):
    svg = (HERE / "icons" / f"{name}.svg").read_text("utf-8")
    svg = re.sub(r"\s+", " ", svg).replace("> <", "><").strip()
    svg = re.sub(r' class="[^"]*"', "", svg).replace('width="24" height="24"', 'width="24" height="24" aria-hidden="true" focusable="false"')
    svg = svg.replace('<path stroke="none" d="M0 0h24v24H0z" fill="none"/>', "")
    return svg.replace("<svg ", f'<svg class="{cls}" ', 1)


def _months(lang, lo="2026-01", hi="2027-12"):
    y, m = int(lo[:4]), int(lo[5:])
    out = []
    while f"{y}-{m:02d}" <= hi:
        out.append((f"{y}-{m:02d}", f"{(MON if lang == 'es' else MON_EN)[m - 1]} {y}"))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def field(i, t, ctx):
    lang, id_ = t["lang"], i["id"]
    lab = E(i.get("label", ""))
    v = i.get("value", "")
    hid = " hidden" if i.get("show") and str(next((x.get("value", "") for x in t["inputs"] if x["id"] == i["show"][0]), "")) not in i["show"][1] else ""
    w = f' hw-{i["w"]}' if i.get("w") else ""
    attrs = "".join(f' {k}="{E(str(i[k]))}"' for k in ("min", "max", "step", "maxlength", "pattern", "placeholder") if k in i)
    ty = i["type"]
    if ty in ("number", "money"):
        unit = i.get("unit", "€" if ty == "money" else "")
        im = "decimal" if ty == "money" or "." in str(i.get("step", "")) else "numeric"
        inp = f'<input class="inp" id="{id_}" type="text" inputmode="{im}" value="{E(str(v))}"{attrs}>'
        ctl = f'<span class="hu">{inp}<span class="hu-u">{E(unit)}</span></span>' if unit else inp
    elif ty == "date":
        ctl = f'<input class="din" id="{id_}" type="date" value="{E(str(v))}"{attrs}>'
    elif ty == "time":
        ctl = f'<input class="din hw-s" id="{id_}" type="time" value="{E(str(v))}"{attrs}>'
    elif ty == "text":
        ctl = f'<input class="inp" id="{id_}" type="text" value="{E(str(v))}" autocomplete="off" spellcheck="false"{attrs}>'
    elif ty in ("select", "month"):
        opts = i.get("options") or _months(lang, i.get("min", "2026-01"), i.get("max", "2027-12"))
        ctl = f'<select id="{id_}">' + "".join(f'<option value="{E(str(o[0]))}"{" selected" if str(o[0]) == str(v) else ""}>{E(o[1])}</option>'
                                               for o in opts) + "</select>"
    elif ty == "seg":
        bs = "".join(f'<button type="button" class="btn{" on" if str(o[0]) == str(v) else ""}" data-v="{E(str(o[0]))}" '
                     f'aria-pressed="{"true" if str(o[0]) == str(v) else "false"}">{E(o[1])}</button>' for o in i["options"])
        return f'<div class="field{w}" id="{id_}-f"{hid}><span class="flabel">{lab}</span><div class="tools hseg" role="group" data-seg="{id_}">{bs}</div></div>'
    elif ty == "check":
        return (f'<div class="field hchk{w}" id="{id_}-f"{hid}><label><input type="checkbox" id="{id_}"{" checked" if v in (True, "1") else ""}> '
                f'{lab}</label></div>')
    elif ty == "place":
        S = L[lang]
        regs = "".join(f'<option value="{r["slug"]}">{E(r["name"])}</option>' for r in ctx.data["regions"])
        return (f'<div class="field" id="{id_}-f"><label for="{id_}-r">{E(i.get("label", S["region"]))}</label>'
                f'<select id="{id_}-r"><option value="">{S["nat_only"]}</option>{regs}</select></div>'
                f'<div class="field" id="{id_}-mf" hidden><label for="{id_}-m">{S["municipio"]}</label><select id="{id_}-m"></select></div>')
    else:
        raise ValueError(ty)
    return f'<div class="field{w}" id="{id_}-f"{hid}><label for="{id_}">{lab}</label>{ctl}</div>'


def form_html(t, ctx):
    main = "".join(field(i, t, ctx) for i in t["inputs"] if not i.get("more"))
    more = "".join(field(i, t, ctx) for i in t["inputs"] if i.get("more"))
    more = (f'<details class="vopt hmore"><summary>{L[t["lang"]]["more"]}{B.CHEV}</summary><div class="vopt-b">{more}</div></details>'
            if more else "")
    return (f'<form id="hform" class="hform" autocomplete="off" onsubmit="return false"><div class="pickers">{main}</div>{more}</form>'
            f'<div id="out" class="hout" aria-live="polite"><noscript><p class="herr">{L[t["lang"]]["noscript"]}</p></noscript></div>')


def runtime_cfg(t, ctx):
    S = L[t["lang"]]
    spec = []
    for i in t["inputs"]:
        s = {k: i[k] for k in ("id", "type", "value", "today", "show", "custom") if k in i}
        if i.get("options"):
            s["options"] = [[str(o[0]), "", o[2]] if len(o) > 2 else [str(o[0])] for o in i["options"]]  # value, -, sets
        spec.append(s)
    cfg = {"slug": t["slug"], "inputs": spec, "link": t["link"],
           "s": {k: S[k] for k in ("print", "ics", "link", "copied", "err", "nat_only", "all_region", "isla", "zona")}}
    if t["hol"] or any(i["type"] == "place" for i in t["inputs"]):
        cfg["hol"] = ctx.hol(t["hol"] or (2026, 2027))
    d = _call(t["data"], ctx)
    if d:
        cfg["d"] = d
    return cfg


# ---------------------------------------------------------------- assets: h.js, h.css, t-<slug>.js

def minify(src, dst):
    """esbuild (same version as build.minify_js); without it, the source is copied."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(f'npx -y esbuild@0.24.0 "{src}" --minify --target=es2015 --log-level=error --outfile="{dst}"',
                       shell=True, check=True, timeout=300, capture_output=True)
    except Exception as e:  # noqa: BLE001
        print("esbuild unavailable, copying", src.name, e)
        dst.write_bytes(src.read_bytes())


def build_shared():
    """utilidades/a/h.js and h.css: the runtime and styles shared by every tool (lead / full build only)."""
    minify(HERE / "js" / "h.js", ASSETS_OUT / "h.js")
    minify(HERE / "h.css", ASSETS_OUT / "h.css")


def build_tool_js(t):
    """<tool folder>/t.js = H.run(<compute>), minified. Lives in the tool's own generated folder (parallel-safe)."""
    GEN.mkdir(exist_ok=True)
    src = GEN / f'{t["slug"]}.js'
    src.write_text(f'/* {t["slug"]}: herramientas/tools/{t["file"]}.py */\nH.run({t["js"].strip()});\n', "utf-8", newline="\n")
    minify(src, B.ROOT / path(t) / "t.js")


def asset(rel):
    """URL of a published file below the site root, versioned by its content."""
    f = B.ROOT / rel
    return f'{B.ASSETS}{rel}?v={B.short_hash(f) if f.exists() else "0"}'


# ---------------------------------------------------------------- page template

def ld(*objs):
    import pages
    return pages.ld(*objs)


def crumbs(lang, items):
    """items: [(name, path)] below the root; Spanish pages start at España (home), English at the tools hub."""
    import pages
    if lang == "es":
        items = [(L["es"]["home"], "")] + items
    return B.crumbs_html(items), pages.crumbs_ld(items)


def faq_html(lang, qas):
    items = "".join(f'<details><summary>{E(q)}</summary><p>{a}</p></details>' for q, a in qas)
    return B.section("faq", L[lang]["faq"], f'<div class="faq">{items}</div>')


def faq_ld(qas):
    import pages
    return pages.faq_ld(qas)


def upd_line(lang, date, sources, credits=()):
    S = L[lang]
    d = dt.date.fromisoformat(date)
    ds = f"{d.day} {B.T['_mon3'][d.month - 1]} {d.year}" if lang == "es" else f"{d.day} {MON_EN[d.month - 1][:3]} {d.year}"
    src = ", ".join(f'<a href="{E(u)}" rel="noopener">{E(n)}</a>' for n, u in sources)
    out = f'<p class="upd">{S["upd"]}: <time datetime="{date}">{ds}</time> · {S["srcs"] if len(sources) > 1 else S["src"]}: {src}</p>'
    if credits:
        cr = ", ".join(f'<a href="{E(u)}" rel="noopener">{E(n)}</a> ({E(lic)})' for n, lic, u in credits)
        out += f'<p class="upd">{S["credits"]}: {cr} · <a href="{B.BASE}{CREDITS_PATH}">{S["all_credits"]}</a></p>'
    return out


def card(name, href, ic, k="", small=False):
    return (f'<li data-k="{E(name + " " + k)}"><a class="hc{" hc-s" if small else ""}" href="{href}">{icon(ic)}<span>{E(name)}</span></a></li>')


def related_html(t):
    cards = []
    for r in t["related"]:
        x = by_slug(r)
        if x:
            cards.append(card(x["name"], B.BASE + path(x), x["icon"], small=True))
            continue
        lg = next((g for g in LEGACY if g["path"] == r), None)
        if lg:
            cards.append(card(lg["name"], B.BASE + lg["path"], lg["icon"], small=True))
    hub = f'<p class="more-l"><a href="{B.BASE}{HUB[t["lang"]]}">{L[t["lang"]]["all"]} →</a></p>'
    return B.section("relacionadas" if t["lang"] == "es" else "related", L[t["lang"]]["related"],
                     (f'<ul class="hgrid hgrid-s">{"".join(cards)}</ul>' if cards else "") + hub)


def alternates(t):
    """hreflang pair when the tool has a twin in the other language."""
    tw = by_slug(t["twin"]) if t["twin"] else None
    if not tw:
        return ""
    a = {t["lang"]: path(t), tw["lang"]: path(tw)}
    return ("".join(f'<link rel="alternate" hreflang="{x}" href="{B.SITE}{B.ASSETS}{p}">' for x, p in a.items())
            + f'<link rel="alternate" hreflang="x-default" href="{B.SITE}{B.ASSETS}{a.get("es", path(t))}">')


def head(lang, title, desc, p, extra, ads, index=True):
    h = B.head_html(title, desc, p, f"{B.SITE}{B.ASSETS}og/espana.png", extra + f'<link rel="stylesheet" href="{asset("utilidades/a/h.css")}">',
                    langs=["es"], ads=ads, index=index)
    if lang == "en":
        h = h.replace('<html lang="es"', '<html lang="en"', 1).replace(f'content="{B.t("og_locale")}"', 'content="en_GB"', 1)
    return h


def shell(lang, hd, main, data, cls):
    if lang == "es":
        return B.page(hd, f"pg ht {cls}".strip(), "", main, data, js=False)
    S = L["en"]
    return hd + (f'<body class="pg ht {cls}"><a class="skip" href="#main">{S["hub"]}</a>'
                 f'<header class="hd"><div class="wrap hd-in">{B.wordmark()}<nav class="nav hnav-en"><a href="{B.BASE}{HUB["en"]}">{S["hub"]}</a>'
                 f'<a href="{B.BASE}{HUB["es"]}" hreflang="es" lang="es">Español</a></nav></div></header>'
                 f'<main id="main">{main}</main>'
                 f'<footer class="ft"><div class="wrap"><ul class="ft-l"><li><a href="{B.BASE}{HUB["en"]}">{S["all"]}</a></li>'
                 f'<li><a href="{B.ASSETS}sobre/" hreflang="es" lang="es">About (Spanish)</a></li><li><a href="{B.ASSETS}contacto/" hreflang="es" lang="es">Contact</a></li>'
                 f'<li><a href="{B.ASSETS}privacidad/" hreflang="es" lang="es">Privacy</a></li></ul></div>'
                 f'<div class="wrap ft-b">© 2026 {B.HOST}</div></footer></body></html>\n')


def tool_page(t, ctx):
    lang, p, S = t["lang"], path(t), L[t["lang"]]
    ch, cld = crumbs(lang, [(S["hub"], HUB[lang]), (t["crumb"], p)])
    intro = f'<p class="ctx">{t["intro"]}</p>' if t["intro"] else ""
    hero = f'<div class="hero wrap">{ch}<h1>{E(t["h1"])}</h1>{intro}{form_html(t, ctx)}</div>'
    blocks = "".join(B.section(f"b{k}", E(h), f'<div class="guide hg">{body}</div>') for k, (h, body) in enumerate(_call(t["blocks"], ctx)))
    qas = _call(t["faq"], ctx)
    cfg = json.dumps(runtime_cfg(t, ctx), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    js = (f'<script id="h-data" type="application/json">{cfg}</script>\n<script defer src="{asset("utilidades/a/h.js")}"></script>\n'
          f'<script defer src="{asset(p + "t.js")}"></script>')
    style = f"<style>{t['css']}</style>" if t["css"] else ""
    lds = [cld, faq_ld(qas)]
    if lang == "en":
        lds.append({"@type": "WebPage", "name": t["title"], "url": B.SITE + B.ASSETS + p, "inLanguage": "en", "dateModified": t["updated"]})
    hd = head(lang, t["title"], t["desc"], p, style + alternates(t) + ld(*lds), ads=True)  # first: it sets B.ADS_PAGE for B.ad()
    # one ad unit, between the explanation and the FAQ: never inside the form or the result (pages.write drops it < 250 words)
    main = (f'{hero}<div class="wrap body narrow">{blocks}{B.ad("hub")}{faq_html(lang, qas)}'
            f'{upd_line(lang, t["updated"], t["sources"], t["credits"])}'
            f'{related_html(t)}</div>{js}')
    return shell(lang, hd, main, ctx.data, f"t-{t['slug']}")


HUB_TXT = {
    "es": ("Utilidades: calculadoras laborales y de fechas gratis",
           "Calculadoras gratis de finiquito, paro, vacaciones, cuadrante de turnos, registro de jornada y días hábiles, con los festivos de tu municipio.",
           "Calculadoras y generadores para el trabajo, las fechas y los trámites en España. Gratis, sin registro y sin enviar tus datos: "
           "todo se calcula en tu navegador.",
           [("Cómo calculan", "Cada utilidad explica su fórmula con un ejemplo y enlaza la norma oficial de la que sale (el Estatuto de los "
             "Trabajadores, la Ley General de la Seguridad Social, el SEPE o el BOE). Las que usan festivos leen los mismos datos que el "
             "calendario laboral de esta web: los nacionales y autonómicos del BOE y los locales de cada municipio publicado."),
            ("Tus datos", "Los números que escribes no salen de tu navegador: no hay registro ni se guardan en ningún servidor. Si copias el "
             "enlace de un resultado, los datos van en la propia dirección para que quien la abra vea lo mismo.")]),
    "en": ("Free online tools: calculators and generators",
           "Free calculators and generators for online sellers, dates and everyday paperwork. No sign-up: everything runs in your browser.",
           "Calculators and generators that run in your browser. Free, no sign-up, nothing sent to a server.", []),
}


def hub_page(lang, ctx):
    S = L[lang]
    title, desc, lead, notes = HUB_TXT[lang]
    items = [(t["cat"], t["name"], B.BASE + path(t), t["icon"], t["k"]) for t in registry() if t["lang"] == lang]
    if lang == "es":
        items += [(g["cat"], g["name"], B.BASE + g["path"], g["icon"], g["k"]) for g in LEGACY]
    secs, nav = [], []
    for key, name in cats(lang):
        mine = [x for x in items if x[0] == key]
        if not mine:
            continue
        nav.append(f'<a href="#c-{key}">{E(name)}</a>')
        secs.append(f'<section class="sec hcat" id="c-{key}"><div class="sec-h"><h2>{E(name)}</h2></div>'
                    f'<ul class="hgrid">{"".join(card(n, h, ic, k) for _, n, h, ic, k in mine)}</ul></section>')
    srch = (f'<form class="sb hsb" role="search" onsubmit="return false"><label class="vh" for="hub-q">{S["search"]}</label>'
            f'<div class="sb-f">{B.MAG}<input id="hub-q" type="search" autocomplete="off" spellcheck="false" placeholder="{E(S["search_ph"])}"></div></form>')
    p = HUB[lang]
    ch, cld = crumbs(lang, [(S["hub"], p)] if lang == "es" else [(S["hub"], p)])
    hero = (f'<div class="hero wrap">{ch}<h1>{E(S["hub"])}</h1><p class="ctx">{E(lead)}</p>{srch}'
            f'<p class="hnav">{" ".join(nav)}</p></div>')
    note = "".join(B.section(f"n{k}", E(h), f'<p class="hp">{b}</p>') for k, (h, b) in enumerate(notes))
    main = (f'{hero}<div class="wrap body">{"".join(secs)}<p class="m" id="hub-none" hidden>{S["none"]}</p>'
            f'<div class="narrow">{note}{upd_line(lang, HUB_UPDATED, [("BOE", "https://www.boe.es/")])}</div></div>'
            f'<script defer src="{asset("utilidades/a/h.js")}"></script>')
    lds = [cld, {"@type": "ItemList", "name": S["hub"], "numberOfItems": len(items),
                 "itemListElement": [{"@type": "ListItem", "position": k + 1, "name": x[1], "url": B.SITE + x[2]} for k, x in enumerate(items)]}]
    alt = ""
    if any(t["lang"] == "en" for t in registry()):
        alt = (f'<link rel="alternate" hreflang="es" href="{B.SITE}{B.ASSETS}{HUB["es"]}"><link rel="alternate" hreflang="en" href="{B.SITE}{B.ASSETS}{HUB["en"]}">'
               f'<link rel="alternate" hreflang="x-default" href="{B.SITE}{B.ASSETS}{HUB["es"]}">')
    hd = head(lang, title, desc, p, alt + ld(*lds), ads=False)
    return shell(lang, hd, main, ctx.data, "hub")


# ---------------------------------------------------------------- entry points and links for other pages

CREDITS_PATH = "utilidades/creditos/"
BASE_CREDITS = [("Tabler Icons", "MIT", "https://tabler.io/icons"),
                ("Datos de festivos: BOE y boletines autonómicos y provinciales", "dominio público", "https://www.boe.es/")]


def credits_page(ctx):
    """/utilidades/creditos/: every tool's credits (open formulas, data or code we adapted) + the icon set. noindex."""
    rows = [f'<li><b>{E(n)}</b> · {E(lic)} · <a href="{E(u)}" rel="noopener">{E(u)}</a></li>' for n, lic, u in BASE_CREDITS]
    for t in registry():
        for n, lic, u in t["credits"]:
            rows.append(f'<li><b>{E(n)}</b> · {E(lic)} · <a href="{E(u)}" rel="noopener">{E(u)}</a> · '
                        f'<a href="{B.BASE}{path(t)}">{E(t["name"])}</a></li>')
    ch, cld = crumbs("es", [(L["es"]["hub"], HUB["es"]), ("Créditos", CREDITS_PATH)])
    main = (f'<div class="hero wrap">{ch}<h1>Créditos de las utilidades</h1></div>'
            f'<div class="wrap body narrow"><ul class="notes">{"".join(rows)}</ul></div>')
    hd = head("es", "Créditos de las utilidades", "Iconos, datos y código de terceros que usan las utilidades de elcalendariolaboral.es, con su licencia.",
              CREDITS_PATH, ld(cld), ads=False, index=False)
    return shell("es", hd, main, ctx.data, "hub")


def write_tool(t, ctx, write):
    build_tool_js(t)
    write(path(t), tool_page(t, ctx), t["updated"], ["es"])


def write_hubs(ctx, write):
    write(HUB["es"], hub_page("es", ctx), max([HUB_UPDATED] + [t["updated"] for t in registry() if t["lang"] == "es"]), ["es"])
    if any(t["lang"] == "en" for t in registry()):  # the English hub exists once there is an English tool
        write(HUB["en"], hub_page("en", ctx), max(t["updated"] for t in registry() if t["lang"] == "en"), ["es"])
    write(CREDITS_PATH, credits_page(ctx), HUB_UPDATED)


def write_pages(data, write, cities, slugs=None):
    """Spanish build only. slugs=None: shared assets, every tool, hubs, credits (full build.py and the lead).
    slugs given: only those tools' pages and their t.js (what parallel agents run: herramientas/build.py)."""
    if B.LANG != "es":
        return
    ctx = Ctx(data, cities)
    if slugs is None:
        build_shared()
    elif not (ASSETS_OUT / "h.js").exists():
        build_shared()
    todo = registry() if slugs is None else [t for t in registry() if t["slug"] in slugs]
    miss = set(slugs or ()) - {t["slug"] for t in todo}
    assert not miss, f"unknown tool slugs: {sorted(miss)}"
    for t in todo:
        write_tool(t, ctx, write)
    if slugs is None:
        write_hubs(ctx, write)


def links(slugs):
    """'<a>Name</a> · <a>Name</a>' for the given tool slugs (Spanish pages linking into the tools)."""
    out = [f'<a href="{B.ASSETS}{path(t)}">{E(t["name"])}</a>' for t in map(by_slug, slugs) if t]
    return " · ".join(out)


def footer_items():
    """<li> items for the footer 'Utilidades' block: the hub and the top work tools."""
    top = [t for t in registry() if t["lang"] == "es" and t.get("footer")]
    li = "".join(f'<li><a href="{B.ASSETS}{path(t)}"{"" if B.LANG == "es" else " hreflang=es lang=es"}>{E(t["name"])}</a></li>' for t in top)
    return li + f'<li><a href="{B.ASSETS}{HUB["es"]}"{"" if B.LANG == "es" else " hreflang=es lang=es"}>{"Todas las utilidades" if B.LANG == "es" else "Utilidades"} →</a></li>'


def home_link():
    return f' · <a href="{B.ASSETS}{HUB["es"]}">Todas las utilidades →</a>'
