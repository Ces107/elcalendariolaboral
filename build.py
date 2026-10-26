#!/usr/bin/env python3
"""Calendario laboral 2027 - generador.

Lee data/2027.json y escribe: index.html (app), <slug>/index.html (19 paginas SEO),
ics/*.ics, og/*.png, icons/*.png, sitemap.xml y sw.js.

    python build.py          # genera todo
    python build.py --no-img # sin regenerar PNG
"""
import datetime as dt
import hashlib
import html
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
# Where the site is served. Defaults: ces107.github.io/calendario-laboral-2027/. For the own domain:
#   CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py
SITE = os.environ.get("CL_SITE", "https://ces107.github.io").rstrip("/")
BASE = os.environ.get("CL_BASE", "/calendario-laboral-2027/")
HOST = SITE.split("://", 1)[1]
URL = SITE + BASE
YEAR = 2027
MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
          "septiembre", "octubre", "noviembre", "diciembre"]
MON3 = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
WD = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
WD3 = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
DAYS = [dt.date(YEAR, 1, 1) + dt.timedelta(i) for i in range(365)]
E = html.escape


def load():
    return json.loads((ROOT / "data" / "2027.json").read_text("utf-8"))


# ---------------------------------------------------------------- data logic

def region_holidays(data, slug, zone=None):
    """Festivos de una comunidad (y zona opcional: isla de Canarias, Arán)."""
    out = []
    for h in data["holidays"]:
        if h["regions"] == "all" or slug in h["regions"]:
            out.append({"date": h["date"], "name": h["name"], "code": h["code"],
                        "kind": "n" if h["regions"] == "all" else "r"})
    z = data["zones"].get(slug)
    if z and zone:
        opt = next(o for o in z["options"] if o["slug"] == zone)
        if "remove" in opt:
            out = [h for h in out if h["date"] != opt["remove"]]
        if "add" in opt:
            out.append({**opt["add"], "code": 3, "kind": "r"})
    out.sort(key=lambda h: h["date"])
    return out


def runs(off):
    """Tramos consecutivos [inicio, fin, libre]."""
    res, s = [], 0
    for i in range(1, len(off) + 1):
        if i == len(off) or off[i] != off[s]:
            res.append([s, i - 1, off[s]])
            s = i
    return res


def puentes(hols):
    """Fines de semana largos (0 dias) y puentes de 1-2 dias de vacaciones.
    Misma logica que app.js (bridges)."""
    hd = {h["date"] for h in hols}
    off = [d.weekday() >= 5 or d.isoformat() in hd for d in DAYS]
    rs = runs(off)

    def has_hol(r):
        return any(DAYS[i].isoformat() in hd for i in range(r[0], r[1] + 1))

    items, covered = [], set()
    for k, r in enumerate(rs):
        if r[2] and has_hol(r) and r[1] - r[0] + 1 >= 3:
            items.append({"s": r[0], "e": r[1], "cost": 0, "take": []})
            covered.add(k)
    for k, r in enumerate(rs):
        if not r[2] and r[1] - r[0] + 1 == 1 and 0 < k < len(rs) - 1:
            a, b = rs[k - 1], rs[k + 1]
            if has_hol(a) or has_hol(b):
                items.append({"s": a[0], "e": b[1], "cost": 1, "take": [r[0]]})
                covered.update(x for x, rr in ((k - 1, a), (k + 1, b)) if has_hol(rr))
    for k, r in enumerate(rs):
        if not r[2] and r[1] - r[0] + 1 == 2 and 0 < k < len(rs) - 1:
            a, b = rs[k - 1], rs[k + 1]
            hk = [x for x, rr in ((k - 1, a), (k + 1, b)) if has_hol(rr)]
            if hk and not all(x in covered for x in hk):
                items.append({"s": a[0], "e": b[1], "cost": 2, "take": [r[0], r[0] + 1]})
                covered.update(hk)
    items.sort(key=lambda it: (it["s"], it["e"]))
    for it in items:
        it["len"] = it["e"] - it["s"] + 1
        it["names"] = [h["name"] for h in hols if DAYS[it["s"]].isoformat() <= h["date"] <= DAYS[it["e"]].isoformat()]
    return items


def fmt_day(d, wd=True):
    return (WD3[d.weekday()] + " " if wd else "") + f"{d.day} {MON3[d.month - 1]}"


def fmt_range(i, j):
    a, b = DAYS[i], DAYS[j]
    if a.month == b.month:
        return f"{WD3[a.weekday()]} {a.day} – {WD3[b.weekday()]} {b.day} {MON3[b.month - 1]}"
    return f"{fmt_day(a)} – {fmt_day(b)}"


# ---------------------------------------------------------------- html parts

MONTHS_T = [m.capitalize() for m in MONTHS]
LOGO = ('<svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true"><rect x="1.5" y="3.5" width="23" height="21" rx="4" fill="none" '
        'stroke="currentColor" stroke-width="2"/><path d="M1.5 9.5h23" stroke="currentColor" stroke-width="2"/>'
        '<path d="M7.5 1.5v4M18.5 1.5v4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="13" cy="16.5" r="3.6" style="fill:var(--red)"/></svg>')
ICON_SHARE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15V3m0 0L7.5 7.5M12 3l4.5 4.5M5 12v7a1.5 1.5 0 0 0 1.5 1.5h11A1.5 1.5 0 0 0 19 19v-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
ICON_PRINT = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 9V3.5h10V9M7 17H4.5V10a1 1 0 0 1 1-1h13a1 1 0 0 1 1 1v7H17M7 14h10v6.5H7z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>'
ICON_THEME = ('<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="1.8"/>'
              '<path d="M12 4a8 8 0 0 1 0 16z" fill="currentColor"/></svg>')
HEAD_JS = ("<script>try{var t=localStorage.getItem('cl27.theme');if(t)document.documentElement.dataset.theme=t}catch(e){}</script>")
THEME_JS = ("<script>(function(){var b=document.getElementById('theme');if(!b)return;b.onclick=function(){var r=document.documentElement,"
            "d=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches,n=d?'light':'dark';r.dataset.theme=n;"
            "try{localStorage.setItem('cl27.theme',n)}catch(e){}}})();"
            "if('serviceWorker'in navigator)addEventListener('load',function(){navigator.serviceWorker.register('" + BASE + "sw.js',{scope:'" + BASE + "'}).catch(function(){})});</script>")


def top_html(app=True):
    tools = ""
    if app:
        tools += (f'<button class="ib" id="sh" type="button" aria-label="Compartir">{ICON_SHARE}</button>'
                  f'<button class="ib" id="pr" type="button" aria-label="Imprimir">{ICON_PRINT}</button>')
    tools += f'<button class="ib" id="theme" type="button" aria-label="Modo oscuro">{ICON_THEME}</button>'
    return (f'<header class="top"><div class="wrap top-in"><a class="logo" href="{BASE}">{LOGO}<span>elcalendariolaboral<i>.es</i></span></a>'
            f'<div class="tools">{tools}</div></div></header>')


def key_html(region=True):
    hide = "" if region else " hidden"
    return ('<ul class="key" aria-label="Leyenda"><li><i class="k n"></i>Nacional</li>'
            f'<li id="k-r"{hide}><i class="k r"></i>Autonómico</li><li id="k-l" hidden><i class="k l"></i>Local</li>'
            '<li id="k-v" hidden><i class="k v"></i>Vacaciones</li></ul>')


def month_html(m, hmap):
    first = dt.date(YEAR, m, 1)
    nd = ((dt.date(YEAR + (m == 12), m % 12 + 1, 1)) - first).days
    cells = [f'<span class="wd">{c}</span>' for c in "LMXJVSD"]
    cells += ["<i></i>"] * first.weekday()
    for d in range(1, nd + 1):
        day = dt.date(YEAR, m, d)
        iso = day.isoformat()
        cls = ["we"] if day.weekday() >= 5 else []
        t = ""
        if iso in hmap:
            cls.append(hmap[iso]["kind"])
            t = f' title="{E(hmap[iso]["name"])}"'
        c = f' class="{" ".join(cls)}"' if cls else ""
        cells.append(f'<b data-d="{iso}"{c}{t}>{d}</b>')
    cells += ["<i></i>"] * (42 - first.weekday() - nd)
    return f'<section class="m" id="m{m}"><h3>{MONTHS_T[m - 1]}</h3><div class="g">{"".join(cells)}</div></section>'


def year_html(hmap):
    return '<div class="year" id="year">' + "".join(month_html(m, hmap) for m in range(1, 13)) + "</div>"


def hol_li(h):
    d = dt.date.fromisoformat(h["date"])
    return (f'<li class="{h["kind"]}"><time datetime="{h["date"]}">{d.day} {MON3[d.month - 1]}</time>'
            f'<span>{E(h["name"])}</span><em>{WD3[d.weekday()]}</em></li>')


def take_txt(take):
    return "Coge el " + " y el ".join(f"{WD3[DAYS[i].weekday()]} {DAYS[i].day}" for i in take)


def puente_li(it, k):
    """Same markup as item() in app.js, so the page does not jump when the script takes over."""
    sub = take_txt(it["take"]) if it["cost"] else " · ".join(it["names"])
    return (f'<li><button type="button" class="it" data-k="p{k}" aria-expanded="false"><span class="a">'
            f'<time>{fmt_range(it["s"], it["e"])}</time><small>{E(sub)}</small></span>'
            f'<span class="z"><b>{it["len"]}</b> días</span></button></li>')


def footer_html(data, current=None):
    regs = "".join(f'<a href="{BASE}{r["slug"]}/"{" aria-current=page" if r["slug"] == current else ""}>{E(r["name"])}</a>'
                   for r in data["regions"])
    s = data["source"]
    return (f'<footer class="foot"><div class="wrap"><nav class="regs" aria-label="Por comunidad">{regs}</nav>'
            f'<p>Datos: <a href="{s["url"]}" rel="noopener">BOE del 13 de octubre de 2026</a> · '
            f'<a href="{BASE}privacidad/">Privacidad</a></p></div></footer>')


def head_html(title, desc, canonical, og_img, extra=""):
    return f"""<!doctype html>
<html lang="es" data-base="{BASE}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121212" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="El Calendario Laboral">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="{BASE}manifest.webmanifest">
<link rel="icon" href="{BASE}icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="{BASE}icons/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{BASE}app.css?v={{CSSV}}">
{HEAD_JS}
{extra}
</head>
"""


def ics_text(hols, label, slug_key):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//{HOST}//Calendario laboral 2027//ES",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:Festivos 2027 · {label}"]
    for h in hols:
        d = dt.date.fromisoformat(h["date"])
        n = d + dt.timedelta(1)
        name = h["name"].replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
        lines += ["BEGIN:VEVENT", f"UID:{d:%Y%m%d}-{slug_key}@{HOST}", "DTSTAMP:20261026T000000Z",
                  f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{n:%Y%m%d}", f"SUMMARY:{name}",
                  "TRANSP:TRANSPARENT", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def gcal(ics_path):
    return "https://calendar.google.com/calendar/r?cid=" + quote("webcal://" + HOST + BASE + ics_path, safe="")


def meta_html(n_hol, n_pts, n_lab):
    return f'<a href="#festivos">{n_hol} festivos</a><a href="#puentes">{n_pts} puentes</a><span>{n_lab} laborables</span>'


# ---------------------------------------------------------------- region page


def region_page(data, r):
    slug, name = r["slug"], r["name"]
    hols = region_holidays(data, slug)
    pts = puentes(hols)
    n_hol = len(hols) + (1 if slug == "canarias" else 0)
    title = f"Calendario laboral 2027 {name}: festivos y puentes"
    desc = (f"Los {n_hol} festivos de 2027 en {r['official']}, con su día de la semana, y los {len(pts)} puentes del año. "
            f"Según el BOE del 13 de octubre de 2026.")
    canon = f"{URL}{slug}/"
    events = [{"@type": "ListItem", "position": i + 1, "item": {
        "@type": "Event", "name": f"{h['name']} ({name})", "startDate": h["date"], "endDate": h["date"],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": r["official"], "address": {"@type": "PostalAddress", "addressRegion": r["official"], "addressCountry": "ES"}},
        "description": f"Festivo laboral 2027 en {r['official']}"}} for i, h in enumerate(hols)]
    ld = [
        {"@context": "https://schema.org", "@type": "ItemList", "name": f"Festivos 2027 en {r['official']}",
         "numberOfItems": len(events), "itemListElement": events},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Calendario laboral 2027", "item": URL},
            {"@type": "ListItem", "position": 2, "name": name, "item": canon}]},
    ]
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return head_html(title, desc, canon, f"{URL}og/{slug}.png", ld_html) + app_body(data, r)


# ---------------------------------------------------------------- app body (home and every region page)

ZONE_PROMPT = "Elige tu isla"


def keep_last(s):
    """The selector chevron sticks to the last word (same as keepLast in app.js)."""
    head, _, last = s.rpartition(" ")
    return (E(head) + " " if head else "") + f'<span class="nw">{E(last)}</span>'


def zone_text(slug, opt):
    if opt is None:
        return ZONE_PROMPT
    return "Zona general" if opt["slug"] == "general" else opt["name"]


def app_body(data, r=None):
    """One page for everything: the home is the app with no region, a region page is the app with it chosen.
    The lists are rendered here too, so the content is in the HTML before app.js runs."""
    slug = r["slug"] if r else ""
    hols = region_holidays(data, slug) if r else [h for h in region_holidays(data, "madrid") if h["kind"] == "n"]
    hmap = {}
    for h in hols:
        hmap.setdefault(h["date"], h)
    zone = data["zones"].get(slug)
    is_can = slug == "canarias"
    hide = "" if r else " hidden"
    options = '<option value="">España</option>' + "".join(
        f'<option value="{x["slug"]}"{" selected" if x["slug"] == slug else ""}>{E(x["name"])}</option>' for x in data["regions"])
    if zone:
        cur = None if is_can else zone["options"][0]
        zopts = (f'<option value="">{ZONE_PROMPT}</option>' if is_can else "") + "".join(
            f'<option value="{o["slug"]}"{" selected" if o is cur else ""}>{E(o["name"])}</option>' for o in zone["options"])
        zone_html = (f'<div class="pick zone" id="zone-f"><span class="pv" id="zt">{keep_last(zone_text(slug, cur))}</span>'
                     f'<select id="zone" aria-label="{E(zone["label"])}">{zopts}</select></div>')
    else:
        zone_html = '<div class="pick zone" id="zone-f" hidden><span class="pv" id="zt"></span><select id="zone" aria-label="Zona"></select></div>'
    if r:
        pts = puentes(hols)
        n_lab = sum(1 for d in DAYS if d.weekday() < 5 and d.isoformat() not in hmap) - (1 if is_can else 0)
        meta = meta_html(len(hols) + (1 if is_can else 0), len(pts), n_lab)
    else:
        pts = []
        meta = f'<span>{len(hols)} festivos nacionales</span><button type="button" class="lnk" id="pickr">Elige tu comunidad</button>'
    hl = "".join(hol_li(h) for h in hols)
    if is_can:
        hl += '<li class="z"><time>+1</time><span><button type="button" class="lnk" data-zone>Fiesta de tu isla</button></span><em></em></li>'
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return f"""<body class="app" data-region="{slug}">
{top_html()}
<main>
<section class="hero wrap">
  <div class="pick reg"><h1><span class="h1a">Calendario laboral 2027</span> <span class="pv" id="rn">{keep_last(r["name"] if r else "España")}</span></h1><select id="region" aria-label="Comunidad autónoma">{options}</select></div>
  {zone_html}
  <p class="meta" id="meta">{meta}</p>
</section>
<div class="wrap body">
  <section class="blk" id="festivos" aria-labelledby="h-fest"><h2 id="h-fest">Festivos</h2><ol class="hlist" id="hlist">{hl}</ol>
    <div class="locs" id="locs"{hide}><span aria-hidden="true">+ Festivo local</span><input type="date" id="l0" min="2027-01-01" max="2027-12-31" aria-label="Añadir festivo local"><input type="date" id="l1" min="2027-01-01" max="2027-12-31" aria-label="Añadir otro festivo local"></div>
  </section>
  <section class="blk" id="puentes" aria-labelledby="h-pts"{hide}><h2 id="h-pts">Puentes</h2><ol class="plist" id="plist">{"".join(puente_li(it, k) for k, it in enumerate(pts))}</ol></section>
  <section class="cal" id="ano" aria-labelledby="h-ano"><h2 class="sr" id="h-ano">Año 2027</h2>
    <div class="calbar">{key_html(bool(r))}<button class="tbtn" id="vmode" type="button"{hide}><span id="vlabel">Marcar vacaciones</span><span id="vcount"></span></button></div>
    <p class="vhint" id="vhint" hidden><span id="vstat" aria-live="polite">Toca los días que te coges.</span> <button type="button" class="lnk" id="vclear" hidden>Borrar</button></p>
    {year_html(hmap)}
  </section>
  <section class="blk" id="vacaciones" aria-labelledby="h-vac"{hide}><h2 id="h-vac">Vacaciones</h2>
    <div class="step"><button type="button" id="vm" aria-label="Un día menos">−</button><input id="vn" type="number" inputmode="numeric" min="1" max="30" value="4" aria-label="Días de vacaciones" aria-describedby="h-vac"><button type="button" id="vp" aria-label="Un día más">+</button><span aria-hidden="true">días</span></div>
    <ol class="plist" id="vlist"></ol>
  </section>
  <p class="exp" id="exp"{hide}><a class="btn p" id="gc" href="#" rel="noopener" target="_blank">Añadir a Google Calendar</a><a class="btn" id="dl" href="#" download="festivos-2027.ics">Descargar .ics</a></p>
</div>
</main>
{footer_html(data, slug or None)}
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script id="cal-data" type="application/json">{compact}</script>
<script src="{BASE}app.js?v={{JSV}}"></script>
{THEME_JS}
</body>
</html>
"""


# ---------------------------------------------------------------- app page

def app_page(data):
    title = "Calendario laboral 2027: festivos y puentes por comunidad"
    desc = ("Los festivos de 2027 de tu comunidad, tus puentes y cuántos días libres sacas con tus vacaciones. "
            "Según el BOE. Añádelos a tu calendario.")
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "El Calendario Laboral 2027", "url": URL,
          "applicationCategory": "UtilitiesApplication", "operatingSystem": "Web, Android", "inLanguage": "es",
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "description": desc}
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return head_html(title, desc, URL, f"{URL}og/espana.png", ld_html) + app_body(data)


# ---------------------------------------------------------------- privacy page

def privacy_page(data):
    title = "Privacidad · El Calendario Laboral"
    src = data["source"]
    body = f"""<body>
{top_html(app=False)}
<main class="wrap doc">
<h1>Privacidad</h1>
<p>No guardamos ningún dato tuyo en servidores. Tu comunidad, tus festivos locales y tus vacaciones se quedan en tu navegador o en tu móvil, y puedes borrarlos cuando quieras.</p>
<p>No hay cuentas, ni cookies propias, ni analítica, ni publicidad. Si algún día añadimos alguna de estas cosas, lo pondremos aquí y te pediremos permiso antes.</p>
<p>La tipografía se carga desde Google Fonts. «Añadir a Google Calendar» te lleva a Google, con su propia política de privacidad. El archivo .ics se crea en tu dispositivo.</p>
<p>Festivos: <a href="{src["url"]}" rel="noopener">{src["id"]}</a>, {E(src["boe"])}. Contacto: <a href="mailto:cesar0407p@gmail.com">cesar0407p@gmail.com</a>.</p>
</main>
{footer_html(data)}
{THEME_JS}
</body>
</html>
"""
    return head_html(title, "Privacidad de El Calendario Laboral: no guardamos datos tuyos en servidores.",
                     f"{URL}privacidad/", f"{URL}og/espana.png") + body


# ---------------------------------------------------------------- images

def font(size, weight="b"):
    from PIL import ImageFont
    names = {"b": ["segoeuib.ttf", "DejaVuSans-Bold.ttf"], "bl": ["seguibl.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"],
             "r": ["segoeui.ttf", "DejaVuSans.ttf"], "sb": ["seguisb.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]}[weight]
    for n in names:
        for p in (Path("C:/Windows/Fonts") / n, Path("/usr/share/fonts/truetype/dejavu") / n):
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


INK, BG, MUT, LINE = (17, 17, 17), (255, 255, 255), (107, 107, 107), (236, 236, 236)
NAT, REG, BRAND = (208, 49, 45), (208, 49, 45), (17, 17, 17)


def og_image(path, label, sub, hols):
    from PIL import Image, ImageDraw
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.text((64, 64), "CALENDARIO LABORAL", font=font(30, "b"), fill=MUT)
    d.text((64, 100), "2027", font=font(150, "bl"), fill=INK)
    size = 84 if len(label) <= 12 else (64 if len(label) <= 18 else 52)
    d.text((64, 300), label, font=font(size, "bl"), fill=INK)
    d.text((64, 420), sub, font=font(34, "sb"), fill=MUT)
    d.rounded_rectangle((64, 500, 64 + 26, 526), 5, fill=NAT)
    d.text((102, 496), "España", font=font(26, "sb"), fill=INK)
    d.ellipse((240, 500, 266, 526), fill=REG)
    d.text((278, 496), "Comunidad", font=font(26, "sb"), fill=INK)
    d.text((64, 568), (HOST + BASE).rstrip("/"), font=font(24, "r"), fill=MUT)
    # 12 mini months (3 cols x 4 rows)
    kind = {h["date"]: h["kind"] for h in hols}
    x0, y0, cw, ch, c, gx, gy = 740, 56, 13, 13, 3, 30, 30
    mw = 7 * (cw + c)
    for m in range(12):
        col, row = m % 3, m // 3
        ox = x0 + col * (mw + gx)
        oy = y0 + row * (6 * (ch + c) + gy + 22)
        d.text((ox, oy - 2), MONTHS[m][:3].upper(), font=font(16, "b"), fill=MUT)
        first = dt.date(YEAR, m + 1, 1)
        nd = ((dt.date(YEAR + (m == 11), (m + 1) % 12 + 1, 1)) - first).days
        for dd in range(nd):
            day = first + dt.timedelta(dd)
            idx = first.weekday() + dd
            cx, cy = ox + (idx % 7) * (cw + c), oy + 22 + (idx // 7) * (ch + c)
            k = kind.get(day.isoformat())
            if k == "n":
                d.rounded_rectangle((cx, cy, cx + cw, cy + ch), 3, fill=NAT)
            elif k == "r":
                d.ellipse((cx - 1, cy - 1, cx + cw + 1, cy + ch + 1), fill=REG)
            else:
                d.rounded_rectangle((cx, cy, cx + cw, cy + ch), 3, fill=(205, 202, 194) if day.weekday() >= 5 else LINE)
    im = im.quantize(colors=48, method=Image.Quantize.MEDIANCUT)
    im.save(path, optimize=True)


def icons(out):
    from PIL import Image, ImageDraw

    def draw(size, maskable=False, bg_full=False):
        S = 4 * size
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if maskable or bg_full:
            d.rectangle((0, 0, S, S), fill=BRAND)
            pad = int(S * (0.22 if maskable else 0.14))
        else:
            d.rounded_rectangle((0, 0, S - 1, S - 1), int(S * 0.22), fill=BRAND)
            pad = int(S * 0.16)
        x0, y0, x1, y1 = pad, int(pad * 1.25), S - pad, S - pad
        w = x1 - x0
        d.rounded_rectangle((x0, y0, x1, y1), int(w * 0.14), fill=BG)
        rw = int(w * 0.09)
        for fx in (0.27, 0.73):
            cx = x0 + int(w * fx)
            d.rounded_rectangle((cx - rw // 2, y0 - int(w * 0.12), cx + rw // 2, y0 + int(w * 0.12)), rw // 2, fill=BG)
        # 3x2 grid of day tiles
        g0x, g0y = x0 + int(w * 0.14), y0 + int((y1 - y0) * 0.26)
        tw = int(w * 0.2)
        gap = int(w * 0.07)
        for i in range(6):
            cx, cy = g0x + (i % 3) * (tw + gap), g0y + (i // 3) * (tw + gap)
            if i == 1:
                d.rounded_rectangle((cx, cy, cx + tw, cy + tw), int(tw * 0.22), fill=NAT)
            elif i == 5:
                d.ellipse((cx, cy, cx + tw, cy + tw), fill=REG)
            else:
                d.rounded_rectangle((cx, cy, cx + tw, cy + tw), int(tw * 0.22), fill=LINE)
        return im.resize((size, size), Image.LANCZOS)

    draw(192).save(out / "icon-192.png", optimize=True)
    draw(512).save(out / "icon-512.png", optimize=True)
    draw(512, maskable=True).save(out / "maskable-512.png", optimize=True)
    draw(180, bg_full=True).convert("RGB").save(out / "apple-touch-icon.png", optimize=True)


# ---------------------------------------------------------------- main

def short_hash(*paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(Path(p).read_bytes())
    return h.hexdigest()[:10]


def main():
    data = load()
    cssv, jsv = short_hash(ROOT / "app.css"), short_hash(ROOT / "app.js")
    fix = lambda s: s.replace("{CSSV}", cssv).replace("{JSV}", jsv)

    (ROOT / "index.html").write_text(fix(app_page(data)), "utf-8", newline="\n")
    (ROOT / "privacidad").mkdir(exist_ok=True)
    (ROOT / "privacidad" / "index.html").write_text(fix(privacy_page(data)), "utf-8", newline="\n")
    for r in data["regions"]:
        d = ROOT / r["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(fix(region_page(data, r)), "utf-8", newline="\n")

    ics = ROOT / "ics"
    ics.mkdir(exist_ok=True)
    for r in data["regions"]:
        (ics / f"{r['slug']}.ics").write_bytes(ics_text(region_holidays(data, r["slug"]), r["name"], r["slug"]).encode("utf-8"))
        for o in data["zones"].get(r["slug"], {}).get("options", []):
            if "add" in o:
                k = f"{r['slug']}-{o['slug']}"
                (ics / f"{k}.ics").write_bytes(ics_text(region_holidays(data, r["slug"], o["slug"]), f"{r['name']} · {o['name']}", k).encode("utf-8"))

    if "--no-img" not in sys.argv:
        (ROOT / "og").mkdir(exist_ok=True)
        (ROOT / "icons").mkdir(exist_ok=True)
        nat = [h for h in region_holidays(data, "madrid") if h["kind"] == "n"]
        og_image(ROOT / "og" / "espana.png", "Festivos y puentes", "19 comunidades · BOE 13-10-2026", nat)
        for r in data["regions"]:
            hols = region_holidays(data, r["slug"])
            n = len(hols) + (1 if r["slug"] == "canarias" else 0)
            og_image(ROOT / "og" / f"{r['slug']}.png", r["name"], f"{n} festivos · {len(puentes(hols))} puentes", hols)
        icons(ROOT / "icons")

    urls = [URL] + [f"{URL}{r['slug']}/" for r in data["regions"]] + [f"{URL}privacidad/"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc><lastmod>{data['updated']}</lastmod><changefreq>monthly</changefreq><priority>{'1.0' if u == URL else '0.8'}</priority></url>" for u in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", "utf-8", newline="\n")

    manifest = {
        "name": "Calendario laboral 2027", "short_name": "Laboral 2027", "lang": "es",
        "description": "Festivos, puentes y vacaciones 2027 por comunidad.",
        "id": BASE, "start_url": BASE + "?source=pwa", "scope": BASE, "display": "standalone",
        "background_color": "#ffffff", "theme_color": "#ffffff", "categories": ["productivity", "utilities"],
        "icons": [{"src": BASE + "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": BASE + "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": BASE + "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
    }
    (ROOT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8", newline="\n")

    ver = short_hash(ROOT / "index.html", ROOT / "app.css", ROOT / "app.js", ROOT / "data" / "2027.json")
    shell = [BASE, f"{BASE}app.css?v={cssv}", f"{BASE}app.js?v={jsv}", f"{BASE}manifest.webmanifest",
             f"{BASE}icons/icon-192.png", f"{BASE}icons/icon-512.png"]
    sw = (ROOT / "sw.src.js").read_text("utf-8").replace("__VERSION__", ver).replace("__SHELL__", json.dumps(shell))
    (ROOT / "sw.js").write_text(sw, "utf-8", newline="\n")
    print(f"ok · {len(urls)} urls · sw {ver}")


if __name__ == "__main__":
    main()
