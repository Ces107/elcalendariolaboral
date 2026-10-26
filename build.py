#!/usr/bin/env python3
"""Calendario laboral 2027 - generador.

Lee data/2027.json y escribe: index.html (app), <slug>/index.html (19 paginas de comunidad, la misma app
con la comunidad elegida), privacidad/, ics/*.ics, og/*.png, icons/*.png, sitemap.xml, manifest y sw.js.

    python build.py          # genera todo
    python build.py --no-img # sin regenerar PNG

Idiomas: todo texto visible sale de T[LANG] (solo "es" esta lleno; lo que falte cae al castellano) y los
nombres de comunidades, zonas y festivos de data/i18n.json si existe (ver localize()).
    CL_LANG=ca CL_LANGS=es,ca python build.py   # escribiria /ca/ con hreflang a / y /ca/
"""
import copy
import datetime as dt
import hashlib
import html
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Where the site is served. Defaults: ces107.github.io/calendario-laboral-2027/. For the own domain:
#   CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py
SITE = os.environ.get("CL_SITE", "https://ces107.github.io").rstrip("/")
ASSETS = os.environ.get("CL_BASE", "/calendario-laboral-2027/")  # css, js, ics, og, icons: shared by every language
HOST = SITE.split("://", 1)[1]
LANG = os.environ.get("CL_LANG", "es")
LANGS = [x for x in os.environ.get("CL_LANGS", "es").split(",") if x] or ["es"]  # trees that exist, for hreflang
if LANG not in LANGS:
    LANGS.append(LANG)


def lang_base(lang):
    return ASSETS if lang == "es" else f"{ASSETS}{lang}/"


BASE = lang_base(LANG)  # pages of this language
URL = SITE + BASE
OUT = ROOT if LANG == "es" else ROOT / LANG
YEAR = 2027
DAYS = [dt.date(YEAR, 1, 1) + dt.timedelta(i) for i in range(365)]
E = html.escape

# ---------------------------------------------------------------- strings
# One table per language. Only "es" is filled; t() falls back to it key by key.
T = {"es": {
    "og_locale": "es_ES", "site_name": "El Calendario Laboral",
    "months": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "mon3": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"],
    "wd": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "wd3": ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"],
    "wd1": "LMXJVSD",
    "long_day": "{wd} {d} de {m}",
    # head
    "title_home": "Calendario laboral 2027: festivos y puentes por comunidad",
    "desc_home": "Los festivos de 2027 de tu comunidad, tus puentes y cuántos días libres sacas con tus vacaciones. Según el BOE. Añádelos a tu calendario.",
    "title_region": "Calendario laboral 2027 {name}: festivos y puentes",
    "desc_region": "Los {n} festivos de 2027 en {place}, con su día de la semana, y los {p} puentes del año. Según el BOE del 13 de octubre de 2026.",
    "ld_app": "El Calendario Laboral 2027", "ld_list": "Festivos 2027 en {place}", "ld_event": "Festivo laboral 2027 en {place}",
    "crumb_home": "Calendario laboral 2027",
    "title_privacy": "Privacidad · El Calendario Laboral",
    "desc_privacy": "Privacidad de El Calendario Laboral: no guardamos datos tuyos en servidores.",
    # page
    "share": "Compartir", "print": "Imprimir", "theme": "Modo oscuro",
    "h1": "Calendario laboral 2027", "spain": "España", "region_label": "Comunidad autónoma",
    "zone_prompt": "Elige tu isla", "zone_general": "Zona general", "zone_label": "Zona", "island_feast": "Fiesta de tu isla",
    "meta_fest": "{n} festivos", "meta_pts1": "{n} puente", "meta_pts": "{n} puentes", "meta_lab": "{n} laborables",
    "meta_nat": "{n} festivos nacionales", "pick_region": "Elige tu comunidad",
    "legend": "Leyenda", "k_n": "Nacional", "k_r": "Autonómico", "k_l": "Local", "k_v": "Vacaciones",
    "h_fest": "Festivos", "h_pts": "Puentes", "h_year": "Año 2027", "h_vac": "Vacaciones",
    "local_add": "+ Festivo local", "local_add_aria": "Añadir festivo local", "local_add2_aria": "Añadir otro festivo local",
    "local_name": "Festivo local", "local_rm_aria": "Quitar festivo local del {d}",
    "vmode": "Marcar vacaciones", "done": "Hecho", "vhint": "Toca los días que te coges.", "vclear": "Borrar",
    "vac_days1": "{n} día de vacaciones", "vac_days": "{n} días de vacaciones",
    "step_minus": "Un día menos", "step_plus": "Un día más", "step_input": "Días de vacaciones", "days": "días",
    "take1": "Coge el {a}", "take2": "Coge el {a} y el {b}",
    "add_vac": "Añadir a mis vacaciones", "rm_vac": "Quitar de mis vacaciones", "no_bridges": "Este año no hay puentes.",
    "gcal": "Añadir a Google Calendar", "ics_btn": "Descargar .ics", "ics_file": "festivos-2027",
    "ics_calname": "Festivos 2027 · {label}", "vac_event": "Vacaciones",
    "toast_added1": "{n} día en tus vacaciones", "toast_added": "{n} días en tus vacaciones", "toast_removed": "Quitado de tus vacaciones",
    "toast_local": "Festivo local: {d}", "toast_cleared": "Vacaciones borradas", "toast_copied": "Enlace copiado",
    "foot_regions": "Por comunidad", "foot_data": "Datos:", "foot_boe": "BOE del 13 de octubre de 2026", "foot_privacy": "Privacidad",
    "privacy_slug": "privacidad",
    "privacy_h1": "Privacidad",
    "privacy_body": [
        "No guardamos ningún dato tuyo en servidores. Tu comunidad, tus festivos locales y tus vacaciones se quedan en tu navegador o en tu móvil, y puedes borrarlos cuando quieras.",
        "No hay cuentas, ni cookies propias, ni analítica, ni publicidad. Si algún día añadimos alguna de estas cosas, lo pondremos aquí y te pediremos permiso antes.",
        "La tipografía se carga desde Google Fonts. «Añadir a Google Calendar» te lleva a Google, con su propia política de privacidad. El archivo .ics se crea en tu dispositivo.",
    ],
    "privacy_src": "Festivos: {link}, {boe}. Contacto: {mail}.",
    # images and manifest
    "og_l1": "Calendario laboral 2027", "og_home": "Festivos y puentes", "og_home_sub": "19 comunidades · BOE 13-10-2026",
    "og_sub": "{n} festivos · {p} puentes",
    "app_name": "Calendario laboral 2027", "app_short": "Laboral 2027", "app_desc": "Festivos, puentes y vacaciones 2027 por comunidad.",
}}
# Strings app.js needs (embedded as #cal-i18n).
JS_KEYS = ["months", "mon3", "wd", "wd3", "wd1", "long_day", "title_home", "title_region", "spain", "zone_prompt", "zone_general",
           "island_feast", "meta_fest", "meta_pts1", "meta_pts", "meta_lab", "meta_nat", "pick_region", "local_name", "local_rm_aria",
           "vmode", "done", "vhint", "vac_days1", "vac_days", "days", "take1", "take2", "add_vac", "rm_vac", "no_bridges",
           "ics_file", "ics_calname", "vac_event", "toast_added1", "toast_added", "toast_removed", "toast_local", "toast_cleared",
           "toast_copied"]


def t(key, **kw):
    s = T.get(LANG, {}).get(key)
    if s is None:
        s = T["es"][key]
    return s.format(**kw) if kw else s


def tn(key, n, **kw):
    """Singular key <key>1 when n == 1."""
    return t(key + "1" if n == 1 and (key + "1") in T["es"] else key, n=n, **kw)


# ---------------------------------------------------------------- data

def load():
    return json.loads((ROOT / "data" / "2027.json").read_text("utf-8"))


def load_i18n():
    p = ROOT / "data" / "i18n.json"
    return json.loads(p.read_text("utf-8")) if p.exists() else {}


def localize(data, lang=LANG, i18n=None):
    """Copy of data with names in `lang`, read from data/i18n.json:
    {"ca": {"regions": {"cataluna": "Catalunya"}, "official": {"madrid": "..."},
            "holidays": {"<nombre en castellano>": "..."}, "zones": {"canarias": "Illa", "canarias.tenerife": "Tenerife"}}}
    Anything missing keeps the Spanish name."""
    tr = (load_i18n() if i18n is None else i18n).get(lang, {})
    if not tr:
        return data
    d = copy.deepcopy(data)
    for r in d["regions"]:
        r["name"] = tr.get("regions", {}).get(r["slug"], r["name"])
        r["short"] = tr.get("regions", {}).get(r["slug"], r["short"])
        r["official"] = tr.get("official", {}).get(r["slug"], r["official"])
    hn = tr.get("holidays", {})
    for h in d["holidays"]:
        h["name"] = hn.get(h["name"], h["name"])
    for slug, z in d["zones"].items():
        z["label"] = tr.get("zones", {}).get(slug, z["label"])
        for o in z["options"]:
            o["name"] = tr.get("zones", {}).get(f"{slug}.{o['slug']}", o["name"])
            if "add" in o:
                o["add"]["name"] = hn.get(o["add"]["name"], o["add"]["name"])
    return d


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


def fmt_day(d):
    return f'{t("wd3")[d.weekday()]} {d.day} {t("mon3")[d.month - 1]}'


def fmt_range(i, j):
    a, b = DAYS[i], DAYS[j]
    if a.month == b.month:
        return f'{t("wd3")[a.weekday()]} {a.day} – {t("wd3")[b.weekday()]} {b.day} {t("mon3")[b.month - 1]}'
    return f"{fmt_day(a)} – {fmt_day(b)}"


# ---------------------------------------------------------------- html parts

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
            "if('serviceWorker'in navigator)addEventListener('load',function(){navigator.serviceWorker.register('" + ASSETS + "sw.js',{scope:'" + ASSETS + "'}).catch(function(){})});</script>")


def top_html(app=True):
    tools = ""
    if app:
        tools += (f'<button class="ib" id="sh" type="button" aria-label="{t("share")}">{ICON_SHARE}</button>'
                  f'<button class="ib" id="pr" type="button" aria-label="{t("print")}">{ICON_PRINT}</button>')
    tools += f'<button class="ib" id="theme" type="button" aria-label="{t("theme")}">{ICON_THEME}</button>'
    return (f'<header class="top"><div class="wrap top-in"><a class="logo" href="{BASE}">{LOGO}<span>elcalendariolaboral<i>.es</i></span></a>'
            f'<div class="tools">{tools}</div></div></header>')


def key_html(region=True):
    hide = "" if region else " hidden"
    return (f'<ul class="key" aria-label="{t("legend")}"><li><i class="k n"></i>{t("k_n")}</li>'
            f'<li id="k-r"{hide}><i class="k r"></i>{t("k_r")}</li><li id="k-l" hidden><i class="k l"></i>{t("k_l")}</li>'
            f'<li id="k-v" hidden><i class="k v"></i>{t("k_v")}</li></ul>')


def month_html(m, hmap):
    first = dt.date(YEAR, m, 1)
    nd = ((dt.date(YEAR + (m == 12), m % 12 + 1, 1)) - first).days
    cells = [f'<span class="wd">{c}</span>' for c in t("wd1")]
    cells += ["<i></i>"] * first.weekday()
    for d in range(1, nd + 1):
        day = dt.date(YEAR, m, d)
        iso = day.isoformat()
        cls = ["we"] if day.weekday() >= 5 else []
        tt = ""
        if iso in hmap:
            cls.append(hmap[iso]["kind"])
            tt = f' title="{E(hmap[iso]["name"])}"'
        c = f' class="{" ".join(cls)}"' if cls else ""
        cells.append(f'<b data-d="{iso}"{c}{tt}>{d}</b>')
    cells += ["<i></i>"] * (42 - first.weekday() - nd)
    return f'<section class="m" id="m{m}"><h3>{t("months")[m - 1].capitalize()}</h3><div class="g">{"".join(cells)}</div></section>'


def year_html(hmap):
    return '<div class="year" id="year">' + "".join(month_html(m, hmap) for m in range(1, 13)) + "</div>"


def hol_li(h):
    d = dt.date.fromisoformat(h["date"])
    return (f'<li class="{h["kind"]}"><time datetime="{h["date"]}">{d.day} {t("mon3")[d.month - 1]}</time>'
            f'<span>{E(h["name"])}</span><em>{t("wd3")[d.weekday()]}</em></li>')


def take_txt(take):
    days = [f'{t("wd3")[DAYS[i].weekday()]} {DAYS[i].day}' for i in take]
    return t("take1", a=days[0]) if len(days) == 1 else t("take2", a=days[0], b=days[1])


def puente_li(it, k):
    """Same markup as item() in app.js, so the page does not jump when the script takes over."""
    sub = take_txt(it["take"]) if it["cost"] else " · ".join(it["names"])
    return (f'<li><button type="button" class="it" data-k="p{k}" aria-expanded="false"><span class="a">'
            f'<time>{fmt_range(it["s"], it["e"])}</time><small>{E(sub)}</small></span>'
            f'<span class="z"><b>{it["len"]}</b> {t("days")}</span></button></li>')


def footer_html(data, current=None):
    regs = "".join(f'<a href="{BASE}{r["slug"]}/"{" aria-current=page" if r["slug"] == current else ""}>{E(r["name"])}</a>'
                   for r in data["regions"])
    s = data["source"]
    return (f'<footer class="foot"><div class="wrap"><nav class="regs" aria-label="{t("foot_regions")}">{regs}</nav>'
            f'<p>{t("foot_data")} <a href="{s["url"]}" rel="noopener">{t("foot_boe")}</a> · '
            f'<a href="{BASE}{t("privacy_slug")}/">{t("foot_privacy")}</a></p></div></footer>')


def head_html(title, desc, path, og_img, extra=""):
    """path: page path below the language base ('' for the home, 'madrid/', ...). Emits hreflang for every LANGS tree."""
    canonical = URL + path
    alts = "".join(f'<link rel="alternate" hreflang="{x}" href="{SITE}{lang_base(x)}{path}">' for x in LANGS)
    if len(LANGS) > 1:
        alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{lang_base("es")}{path}">'
    return f"""<!doctype html>
<html lang="{LANG}" data-base="{BASE}" data-assets="{ASSETS}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canonical}">{alts}
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101010" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:locale" content="{t("og_locale")}">
<meta property="og:site_name" content="{t("site_name")}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="manifest" href="{ASSETS}manifest.webmanifest">
<link rel="icon" href="{ASSETS}icons/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="{ASSETS}icons/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{ASSETS}app.css?v={{CSSV}}">
{HEAD_JS}
{extra}
</head>
"""


def ics_text(hols, label, slug_key):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", f"PRODID:-//{HOST}//Calendario laboral 2027//ES",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{t('ics_calname', label=label)}"]
    for h in hols:
        d = dt.date.fromisoformat(h["date"])
        n = d + dt.timedelta(1)
        name = h["name"].replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
        lines += ["BEGIN:VEVENT", f"UID:{d:%Y%m%d}-{slug_key}@{HOST}", "DTSTAMP:20261026T000000Z",
                  f"DTSTART;VALUE=DATE:{d:%Y%m%d}", f"DTEND;VALUE=DATE:{n:%Y%m%d}", f"SUMMARY:{name}",
                  "TRANSP:TRANSPARENT", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def meta_html(n_hol, n_pts, n_lab):
    return (f'<a href="#festivos">{t("meta_fest", n=n_hol)}</a><a href="#puentes">{tn("meta_pts", n_pts)}</a>'
            f'<span>{t("meta_lab", n=n_lab)}</span>')


# ---------------------------------------------------------------- region page

def region_page(data, r):
    slug, name = r["slug"], r["name"]
    hols = region_holidays(data, slug)
    pts = puentes(hols)
    n_hol = len(hols) + (1 if slug == "canarias" else 0)
    title = t("title_region", name=name)
    desc = t("desc_region", n=n_hol, place=r["official"], p=len(pts))
    canon = f"{URL}{slug}/"
    events = [{"@type": "ListItem", "position": i + 1, "item": {
        "@type": "Event", "name": f"{h['name']} ({name})", "startDate": h["date"], "endDate": h["date"],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": r["official"], "address": {"@type": "PostalAddress", "addressRegion": r["official"], "addressCountry": "ES"}},
        "description": t("ld_event", place=r["official"])}} for i, h in enumerate(hols)]
    ld = [
        {"@context": "https://schema.org", "@type": "ItemList", "name": t("ld_list", place=r["official"]),
         "numberOfItems": len(events), "itemListElement": events},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t("crumb_home"), "item": URL},
            {"@type": "ListItem", "position": 2, "name": name, "item": canon}]},
    ]
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return head_html(title, desc, f"{slug}/", f"{SITE}{ASSETS}og/{slug}.png", ld_html) + app_body(data, r)


# ---------------------------------------------------------------- app body (home and every region page)

def keep_last(s):
    """The selector chevron sticks to the last word (same as keepLast in app.js)."""
    head, _, last = s.rpartition(" ")
    return (E(head) + " " if head else "") + f'<span class="nw">{E(last)}</span>'


def zone_text(opt):
    if opt is None:
        return t("zone_prompt")
    return t("zone_general") if opt["slug"] == "general" else opt["name"]


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
    options = f'<option value="">{t("spain")}</option>' + "".join(
        f'<option value="{x["slug"]}"{" selected" if x["slug"] == slug else ""}>{E(x["name"])}</option>' for x in data["regions"])
    if zone:
        cur = None if is_can else zone["options"][0]
        zopts = (f'<option value="">{t("zone_prompt")}</option>' if is_can else "") + "".join(
            f'<option value="{o["slug"]}"{" selected" if o is cur else ""}>{E(o["name"])}</option>' for o in zone["options"])
        zone_html = (f'<div class="pick zone" id="zone-f"><span class="pv" id="zt">{keep_last(zone_text(cur))}</span>'
                     f'<select id="zone" aria-label="{E(zone["label"])}">{zopts}</select></div>')
    else:
        zone_html = f'<div class="pick zone" id="zone-f" hidden><span class="pv" id="zt"></span><select id="zone" aria-label="{t("zone_label")}"></select></div>'
    if r:
        pts = puentes(hols)
        n_lab = sum(1 for d in DAYS if d.weekday() < 5 and d.isoformat() not in hmap) - (1 if is_can else 0)
        meta = meta_html(len(hols) + (1 if is_can else 0), len(pts), n_lab)
    else:
        pts = []
        meta = f'<span>{t("meta_nat", n=len(hols))}</span><button type="button" class="lnk" id="pickr">{t("pick_region")}</button>'
    hl = "".join(hol_li(h) for h in hols)
    if is_can:
        hl += f'<li class="z"><time>+1</time><span><button type="button" class="lnk" data-zone>{t("island_feast")}</button></span><em></em></li>'
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    strings = json.dumps({k: t(k) for k in JS_KEYS}, ensure_ascii=False, separators=(",", ":"))
    return f"""<body class="app" data-region="{slug}">
{top_html()}
<main>
<section class="hero wrap">
  <div class="pick reg"><h1><span class="h1a">{t("h1")}</span> <span class="pv" id="rn">{keep_last(r["name"] if r else t("spain"))}</span></h1><select id="region" aria-label="{t("region_label")}">{options}</select></div>
  {zone_html}
  <p class="meta" id="meta">{meta}</p>
</section>
<div class="wrap body">
  <section class="blk" id="festivos" aria-labelledby="h-fest"><h2 id="h-fest">{t("h_fest")}</h2><ol class="hlist" id="hlist">{hl}</ol>
    <div class="locs" id="locs"{hide}><span aria-hidden="true">{t("local_add")}</span><input type="date" id="l0" min="2027-01-01" max="2027-12-31" aria-label="{t("local_add_aria")}"><input type="date" id="l1" min="2027-01-01" max="2027-12-31" aria-label="{t("local_add2_aria")}"></div>
  </section>
  <section class="blk" id="puentes" aria-labelledby="h-pts"{hide}><h2 id="h-pts">{t("h_pts")}</h2><ol class="plist" id="plist">{"".join(puente_li(it, k) for k, it in enumerate(pts))}</ol></section>
  <section class="cal" id="ano" aria-labelledby="h-ano"><h2 class="sr" id="h-ano">{t("h_year")}</h2>
    <div class="calbar">{key_html(bool(r))}<button class="tbtn" id="vmode" type="button"{hide}><span id="vlabel">{t("vmode")}</span><span id="vcount"></span></button></div>
    <p class="vhint" id="vhint" hidden><span id="vstat" aria-live="polite">{t("vhint")}</span> <button type="button" class="lnk" id="vclear" hidden>{t("vclear")}</button></p>
    {year_html(hmap)}
  </section>
  <section class="blk" id="vacaciones" aria-labelledby="h-vac"{hide}><h2 id="h-vac">{t("h_vac")}</h2>
    <div class="step"><button type="button" id="vm" aria-label="{t("step_minus")}">−</button><input id="vn" type="number" inputmode="numeric" min="1" max="30" value="4" aria-label="{t("step_input")}" aria-describedby="h-vac"><button type="button" id="vp" aria-label="{t("step_plus")}">+</button><span aria-hidden="true">{t("days")}</span></div>
    <ol class="plist" id="vlist"></ol>
  </section>
  <p class="exp" id="exp"{hide}><a class="btn p" id="gc" href="#" rel="noopener" target="_blank">{t("gcal")}</a><a class="btn" id="dl" href="#" download="{t("ics_file")}.ics">{t("ics_btn")}</a></p>
</div>
</main>
{footer_html(data, slug or None)}
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script id="cal-data" type="application/json">{compact}</script>
<script id="cal-i18n" type="application/json">{strings}</script>
<script src="{ASSETS}app.js?v={{JSV}}"></script>
{THEME_JS}
</body>
</html>
"""


# ---------------------------------------------------------------- app page

def app_page(data):
    title, desc = t("title_home"), t("desc_home")
    ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": t("ld_app"), "url": URL,
          "applicationCategory": "UtilitiesApplication", "operatingSystem": "Web, Android", "inLanguage": LANG,
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "description": desc}
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
    return head_html(title, desc, "", f"{SITE}{ASSETS}og/espana.png", ld_html) + app_body(data)


# ---------------------------------------------------------------- privacy page

def privacy_page(data):
    src = data["source"]
    paras = "".join(f"<p>{E(p)}</p>" for p in t("privacy_body"))
    link = f'<a href="{src["url"]}" rel="noopener">{src["id"]}</a>'
    mail = '<a href="mailto:cesar0407p@gmail.com">cesar0407p@gmail.com</a>'
    body = f"""<body>
{top_html(app=False)}
<main class="wrap doc">
<h1>{t("privacy_h1")}</h1>
{paras}
<p>{t("privacy_src", link=link, boe=E(src["boe"]), mail=mail)}</p>
</main>
{footer_html(data)}
{THEME_JS}
</body>
</html>
"""
    return head_html(t("title_privacy"), t("desc_privacy"), f'{t("privacy_slug")}/', f"{SITE}{ASSETS}og/espana.png") + body


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


INK, BG, MUT, LINE, WE = (17, 17, 17), (255, 255, 255), (107, 107, 107), (226, 226, 222), (242, 242, 240)
NAT, REG, BRAND = (208, 49, 45), (208, 49, 45), (17, 17, 17)


def og_image(path, label, sub, hols):
    """Same language as the page: black type on white, national = red disc, regional = red ring."""
    from PIL import Image, ImageDraw
    W, H, S = 1200, 630, 2
    im = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(im)
    X = 72 * S
    d.text((X, 76 * S), t("og_l1"), font=font(44 * S, "bl"), fill=INK)
    size = 80 if len(label) <= 11 else (62 if len(label) <= 16 else 48)
    d.text((X, 150 * S), label, font=font(size * S, "bl"), fill=INK)
    d.text((X, 286 * S), sub, font=font(30 * S, "sb"), fill=MUT)
    r = 11 * S
    d.ellipse((X, 470 * S, X + 2 * r, 470 * S + 2 * r), fill=NAT)
    d.text((X + 36 * S, 465 * S), t("k_n"), font=font(26 * S, "sb"), fill=INK)
    x2 = X + 210 * S
    d.ellipse((x2, 470 * S, x2 + 2 * r, 470 * S + 2 * r), outline=REG, width=3 * S)
    d.text((x2 + 36 * S, 465 * S), t("k_r"), font=font(26 * S, "sb"), fill=INK)
    d.text((X, 548 * S), (HOST + lang_base(LANG)).rstrip("/"), font=font(24 * S, "r"), fill=MUT)
    # the year: 3 columns x 4 rows of mini months, one dot per day
    kind = {h["date"]: h["kind"] for h in hols}
    x0, y0, c, gx, gy = 700 * S, 58 * S, 17 * S, 30 * S, 22 * S
    dot = 5 * S
    for m in range(12):
        col, row = m % 3, m // 3
        ox, oy = x0 + col * (7 * c + gx), y0 + row * (6 * c + gy + 24 * S)
        d.text((ox, oy - 4 * S), t("months")[m][:3].capitalize(), font=font(15 * S, "b"), fill=INK)
        first = dt.date(YEAR, m + 1, 1)
        nd = ((dt.date(YEAR + (m == 11), (m + 1) % 12 + 1, 1)) - first).days
        for dd in range(nd):
            day = first + dt.timedelta(dd)
            idx = first.weekday() + dd
            cx, cy = ox + (idx % 7) * c + c // 2, oy + 24 * S + (idx // 7) * c + c // 2
            k = kind.get(day.isoformat())
            if k == "n":
                d.ellipse((cx - 7 * S, cy - 7 * S, cx + 7 * S, cy + 7 * S), fill=NAT)
            elif k == "r":
                d.ellipse((cx - 7 * S, cy - 7 * S, cx + 7 * S, cy + 7 * S), outline=REG, width=2 * S)
            else:
                d.ellipse((cx - dot // 2 * 1, cy - dot // 2, cx + dot // 2, cy + dot // 2), fill=WE if day.weekday() >= 5 else LINE)
    im = im.resize((W, H), Image.LANCZOS).quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    im.save(path, optimize=True)


def icons(out):
    """Black tile, white page, one red disc and one red ring: the logo's day marks."""
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
        g0x, g0y = x0 + int(w * 0.14), y0 + int((y1 - y0) * 0.26)
        tw, gap = int(w * 0.2), int(w * 0.07)
        for i in range(6):
            cx, cy = g0x + (i % 3) * (tw + gap), g0y + (i // 3) * (tw + gap)
            if i == 1:
                d.ellipse((cx, cy, cx + tw, cy + tw), fill=NAT)
            elif i == 5:
                d.ellipse((cx, cy, cx + tw, cy + tw), outline=REG, width=max(2, int(tw * 0.14)))
            else:
                q = int(tw * 0.32)
                d.ellipse((cx + q, cy + q, cx + tw - q, cy + tw - q), fill=LINE)
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
    data = localize(load())
    cssv, jsv = short_hash(ROOT / "app.css"), short_hash(ROOT / "app.js")
    fix = lambda s: s.replace("{CSSV}", cssv).replace("{JSV}", jsv)

    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(fix(app_page(data)), "utf-8", newline="\n")
    (OUT / t("privacy_slug")).mkdir(exist_ok=True)
    (OUT / t("privacy_slug") / "index.html").write_text(fix(privacy_page(data)), "utf-8", newline="\n")
    for r in data["regions"]:
        d = OUT / r["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(fix(region_page(data, r)), "utf-8", newline="\n")
    if LANG != "es":
        print(f"ok · {LANG} · {len(data['regions']) + 2} pages in {OUT}")
        return

    # shared files: written once, by the Spanish build
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
        og_image(ROOT / "og" / "espana.png", t("og_home"), t("og_home_sub"), nat)
        for r in data["regions"]:
            hols = region_holidays(data, r["slug"])
            n = len(hols) + (1 if r["slug"] == "canarias" else 0)
            og_image(ROOT / "og" / f"{r['slug']}.png", r["name"], t("og_sub", n=n, p=len(puentes(hols))), hols)
        icons(ROOT / "icons")

    paths = [""] + [f"{r['slug']}/" for r in data["regions"]] + [f'{t("privacy_slug")}/']
    urls = [SITE + lang_base(x) + p for x in LANGS for p in paths]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    sm += [f"  <url><loc>{u}</loc><lastmod>{data['updated']}</lastmod><changefreq>monthly</changefreq><priority>{'1.0' if u == URL else '0.8'}</priority></url>" for u in urls]
    sm.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", "utf-8", newline="\n")

    manifest = {
        "name": t("app_name"), "short_name": t("app_short"), "lang": LANG, "description": t("app_desc"),
        "id": ASSETS, "start_url": ASSETS + "?source=pwa", "scope": ASSETS, "display": "standalone",
        "background_color": "#ffffff", "theme_color": "#ffffff", "categories": ["productivity", "utilities"],
        "icons": [{"src": ASSETS + "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": ASSETS + "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": ASSETS + "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
    }
    (ROOT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8", newline="\n")

    ver = short_hash(ROOT / "index.html", ROOT / "app.css", ROOT / "app.js", ROOT / "data" / "2027.json")
    shell = [ASSETS, f"{ASSETS}app.css?v={cssv}", f"{ASSETS}app.js?v={jsv}", f"{ASSETS}manifest.webmanifest",
             f"{ASSETS}icons/icon-192.png", f"{ASSETS}icons/icon-512.png"]
    sw = (ROOT / "sw.src.js").read_text("utf-8").replace("__VERSION__", ver).replace("__SHELL__", json.dumps(shell))
    (ROOT / "sw.js").write_text(sw, "utf-8", newline="\n")
    print(f"ok · {len(urls)} urls · sw {ver}")


if __name__ == "__main__":
    main()
