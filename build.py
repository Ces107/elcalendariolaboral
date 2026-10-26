#!/usr/bin/env python3
"""Calendario laboral 2027 - generador.

Lee data/2027.json y escribe, para cada idioma (es en la raiz; ca, gl y eu en /ca/, /gl/, /eu/ con los mismos slugs):
portada, 19 comunidades, paginas de ciudad, /festivos-locales/ y privacidad. El castellano escribe ademas lo comun:
ics/, csv/, og/, icons/, sitemap.xml (con alternates por idioma), manifest y sw.js.

    CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py          # todo
    CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py --no-img # sin regenerar PNG

Textos: T["es"] aqui; ca/gl/eu salen de data/i18n.json (ver strings()). Si una cadena no existe alli ni se puede
sacar de un patron de ese idioma, queda en castellano (NO_TR lo lista).
"""
import copy
import datetime as dt
import hashlib
import html
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SITE = os.environ.get("CL_SITE", "https://ces107.github.io").rstrip("/")
ASSETS = os.environ.get("CL_BASE", "/calendario-laboral-2027/")  # css, js, ics, og, icons: shared by every language
HOST = SITE.split("://", 1)[1]
LANG = os.environ.get("CL_LANG", "es")
LANGS = [x for x in os.environ.get("CL_LANGS", "es,ca,gl,eu").split(",") if x] or ["es"]
if LANG not in LANGS:
    LANGS.append(LANG)
LANG_NAMES = {"es": "Español", "ca": "Català", "gl": "Galego", "eu": "Euskara"}
IN_LANG = {"es": "es-ES", "ca": "ca-ES", "gl": "gl-ES", "eu": "eu-ES"}


def lang_base(lang):
    return ASSETS if lang == "es" else f"{ASSETS}{lang}/"


BASE = lang_base(LANG)
URL = SITE + BASE
OUT = ROOT if LANG == "es" else ROOT / LANG
YEAR = 2027
DAYS = [dt.date(YEAR, 1, 1) + dt.timedelta(i) for i in range(365)]
E = html.escape


def load():
    return json.loads((ROOT / "data" / "2027.json").read_text("utf-8"))


def load_i18n():
    p = ROOT / "data" / "i18n.json"
    return json.loads(p.read_text("utf-8")) if p.exists() else {}


I18N = load_i18n()

# ---------------------------------------------------------------- strings
# Spanish. Plural values are {"one": ..., "other": ...}.
ES = {
    "og_locale": "es_ES", "site_name": "El Calendario Laboral",
    "title_home": "Calendario laboral 2027: festivos y puentes en España",
    "desc_home": "Calendario laboral 2027 de España según el BOE: festivos de tu comunidad y tu ciudad, puentes y un planificador que te dice cuántos días libras.",
    "title_region": "Calendario laboral 2027 {region}: festivos y puentes",
    "title_region2": "Calendario laboral 2027 {region}: festivos",
    "desc_region": "Festivos 2027 en {region}: los {n} del BOE con su día, {p} puentes y planificador de vacaciones. Añade los 2 locales de tu ciudad y expórtalo.",
    "h1": "Calendario laboral 2027", "h1_region": "Calendario laboral 2027 {region_of}",
    "spain": "España", "in_spain": "en España",
    "nav_regions": "Comunidades", "nav_locals": "Festivos locales", "nav_bridges": "Puentes",
    "region_label": "Comunidad autónoma", "pick_region": "Elige tu comunidad",
    "h_hol": "Festivos 2027 en {region}", "h_pts": "Puentes y fines de semana largos 2027 en {region}", "h_loc": "Festivos locales 2027 en {region}",
    "h_cal": "Calendario 2027", "h_vac": "Vacaciones", "h_faq": "Preguntas frecuentes",
    "col_date": "Fecha", "col_day": "Día", "col_hol": "Festivo", "col_scope": "Ámbito", "col_bridge": "Puente",
    "col_free": "Días libres", "col_vac": "Días de vacaciones", "col_city": "Ciudad", "col_src": "Fuente",
    "k_n": "Nacional", "k_r": "Autonómico", "k_i": "Insular", "k_l": "Local", "k_v": "Vacaciones", "legend": "Leyenda",
    "municipio": "Municipio", "pending_short": "(pendiente)", "add_short": "Añadir", "rm_short": "Quitar",
    "free_n": "{n} días libres", "see_cal": "Ver en el calendario",
    "clear": "Borrar", "vac_cleared": "Vacaciones borradas",
    "vac_days": {"one": "{n} día de vacaciones", "other": "{n} días de vacaciones"},
    "vac_added": {"one": "{n} día en tus vacaciones", "other": "{n} días en tus vacaciones"},
    "vac_removed": "Quitado de tus vacaciones",
    "add_vac": "Añadir a mis vacaciones", "rm_vac": "Quitar de mis vacaciones",
    "no_vac": "sin coger vacaciones", "no_bridges": "Este año no hay puentes.",
    "how_many": "¿Cuántos días de vacaciones?", "one_more": "Un día más", "one_less": "Un día menos",
    "print": "Imprimir", "csv": "Excel (CSV)", "add_cal": "Añadir a tu calendario", "ics_dl": "Descargar .ics",
    "gcal": "Añadir a Google Calendar", "apple": "Apple / Outlook",
    "next_hol": "Próximo festivo", "days_left": {"one": "Falta {n} día", "other": "Faltan {n} días"},
    "tomorrow": "Mañana", "today": "Hoy",
    "add_local": "Añadir festivo local", "remove_local": "Quitar festivo local", "local_holiday": "Festivo local",
    "local_toast": "Festivo local: {date}",
    "island": "Isla", "zone": "Zona", "zone_general": "Zona general", "pick_island": "Elige tu isla", "island_holiday": "Fiesta de tu isla",
    "privacy": "Privacidad", "data_source": "Datos: BOE del 13 de octubre de 2026", "locals": "Locales",
    "n_hol": {"one": "{n} festivo", "other": "{n} festivos"}, "n_pts": {"one": "{n} puente", "other": "{n} puentes"},
    "n_days": {"one": "{n} día", "other": "{n} días"},
    "n_lab": {"one": "{n} día laborable", "other": "{n} días laborables"},
    "n_nat": {"one": "{n} festivo nacional", "other": "{n} festivos nacionales"},
    "menu": "Menú", "crumbs": "Migas de pan", "pending": "aprobado por el pleno, pendiente del boletín",
    "unpublished": "pendiente de publicar",
    "ics_file": "festivos-2027", "ics_calname": "Festivos 2027 · {label}", "vac_event": "Vacaciones",
    "title_privacy": "Privacidad · El Calendario Laboral",
    "desc_privacy": "Privacidad de El Calendario Laboral: no guardamos datos tuyos en servidores.",
    "privacy_p1": "No guardamos ningún dato tuyo en servidores. Tu comunidad, tus festivos locales y tus vacaciones se quedan en tu navegador o en tu móvil, y puedes borrarlos cuando quieras.",
    "privacy_ads": "No hay cuentas, ni cookies propias, ni analítica. La web muestra anuncios de Google AdSense. Google puede usar cookies o identificadores para servir y medir anuncios. En la UE, el EEE y el Reino Unido, un aviso de consentimiento de Google te pregunta antes de mostrar anuncios personalizados.",
    "privacy_p3": "La tipografía se carga desde Google Fonts. «Añadir a Google Calendar» te lleva a Google, con su propia política de privacidad. El archivo .ics se crea en tu dispositivo.",
    "privacy_links": 'Cómo usa Google los datos: <a href="https://policies.google.com/technologies/partner-sites" rel="noopener">policies.google.com</a>. Tus preferencias de anuncios: <a href="https://adssettings.google.com" rel="noopener">adssettings.google.com</a>.',
    "og_l1": "Calendario laboral 2027", "og_home": "Festivos y puentes", "og_home_sub": "19 comunidades · BOE 13-10-2026",
    "og_sub": "{n} festivos · {p} puentes",
    "app_name": "Calendario laboral 2027", "app_short": "Laboral 2027", "app_desc": "Festivos, puentes y vacaciones 2027 por comunidad.",
}
# Spanish "de <comunidad>" for the H1
ES_OF = {"pais-vasco": "del País Vasco", "comunitat-valenciana": "de la Comunidad Valenciana"}

# Strings only Spanish has, aria-only labels without a translation in data/i18n.json. The ca/gl/eu pages keep the
# Spanish text (or drop an aria-label) for these; the report lists them.
NO_TR = ["menu", "pending", "pending_short", "unpublished", "h_faq"]


def _strip_n(s):
    return s.replace("{n} ", "").replace(" {n}", "").replace("{n}", "").strip()


def strings(lang):
    """T for one language. ca/gl/eu: i18n.json ui keys verbatim, or derived from a pattern of the same language
    (noted inline); anything else falls back to Spanish."""
    if lang == "es" or not I18N:
        return dict(ES)
    U = lambda k: I18N["ui"][k][lang]  # noqa: E731
    M, W = I18N["months"][lang], I18N["weekdays"][lang]
    nreg = U("n_regions")
    locals_word = {"ca": "Festius locals", "gl": "Festivos locais", "eu": "Tokiko jaiegunak"}[lang]  # as written in ui.plus_two_local
    hol_word = U("holidays")
    h_hol = U("holidays_in_region")

    def swap(word):  # ui.holidays_in_region with "Festius" replaced by another noun of the same language
        k = h_hol.lower().find(hol_word.lower())
        out = h_hol[:k] + (word if k == 0 else word.lower()) + h_hol[k + len(hol_word):]
        return out[0].upper() + out[1:]

    site = U("site_title")
    t = dict(ES)
    t.update({
        "og_locale": {"ca": "ca_ES", "gl": "gl_ES", "eu": "eu_ES"}[lang],
        "title_home": U("title_home"), "desc_home": U("meta_home"),
        "title_region": U("title_region"), "title_region2": U("title_region").split(":")[0],
        "desc_region": U("meta_region"),
        "h1": site, "h1_region": f"{site} {{region_in}}",
        "spain": U("spain"), "in_spain": U("in_spain"),
        # ui.n_regions without the number; Basque has no bare plural there, so ui.by_region
        "nav_regions": U("by_region") if lang == "eu" else _strip_n(nreg.replace("19", "{n}")).capitalize(),
        "nav_locals": locals_word, "nav_bridges": U("bridges"),
        "region_label": U("region_label"), "pick_region": U("pick_region"),
        "h_hol": h_hol, "h_pts": swap(U("bridges")), "h_loc": swap(locals_word.lower() if lang != "eu" else "tokiko jaiegunak"),
        # ui.site_title without "laboral" / "lan-"
        "h_cal": {"ca": site.replace(" laboral", ""), "gl": site.replace(" laboral", ""), "eu": site.replace("lan-", "")}[lang],
        "h_vac": U("vacation"),
        "col_date": "2027", "col_day": {"ca": "Dia", "gl": "Día", "eu": "Eguna"}[lang],  # ui.n_days / holiday names ("Errege eguna")
        "col_hol": {"ca": "Festiu", "gl": "Festivo", "eu": "Jaieguna"}[lang],  # ui.n_holidays one / ui.local_holiday
        "col_scope": "",
        "col_bridge": {"ca": "Pont", "gl": "Ponte", "eu": "Zubia"}[lang],  # ui.n_bridges one
        "col_free": {"ca": "Dies de festa", "gl": "Días libres", "eu": "Egun libreak"}[lang],  # ui.meta_home
        "col_vac": U("vacation_days"),
        "col_city": {"ca": "Municipi", "gl": "Concello", "eu": "Udalerria"}[lang],  # ui.plus_two_local
        "col_src": U("data_source").split(":")[0],
        "k_n": U("key_national"), "k_r": U("key_regional"), "k_i": U("island"), "k_l": U("key_local"), "k_v": U("vacation"), "legend": U("legend"),
        "clear": U("clear"),
        "municipio": {"ca": "Municipi", "gl": "Concello", "eu": "Udalerria"}[lang],  # ui.plus_two_local
        # the verb of ui.add_gcal / ui.remove_local
        "add_short": {"ca": "Afegeix", "gl": "Engadir", "eu": "Gehitu"}[lang], "rm_short": {"ca": "Treu", "gl": "Quitar", "eu": "Kendu"}[lang],
        "free_n": {"ca": "{n} dies de festa", "gl": "{n} días libres", "eu": "{n} egun libre"}[lang],  # ui.meta_home
        "see_cal": {"ca": site.replace(" laboral", ""), "gl": site.replace(" laboral", ""), "eu": site.replace("lan-", "")}[lang],
        "n_days": U("n_days"), "vac_cleared": U("vacation_cleared"),
        "vac_days": U("n_vacation_days"), "vac_added": U("added_to_vacation"), "vac_removed": U("removed_from_vacation"),
        "add_vac": U("add_to_vacation"), "rm_vac": U("remove_from_vacation"),
        "no_vac": U("no_vacation"), "no_bridges": U("no_bridges"),
        "how_many": U("how_many_days"), "one_more": U("one_more_day"), "one_less": U("one_less_day"),
        "print": U("print"),
        # ui.meta_home "Afegeix-los al teu calendari" / "Engádeos ao teu calendario" / "Gehitu zure egutegira", as a command
        "add_cal": {"ca": "Afegeix al teu calendari", "gl": "Engadir ao teu calendario", "eu": "Gehitu zure egutegira"}[lang],
        "ics_dl": U("download_ics"), "gcal": U("add_gcal"),
        "next_hol": U("next_holiday"), "days_left": U("days_left"), "tomorrow": U("tomorrow"), "today": U("today"),
        "add_local": U("add_local"), "remove_local": U("remove_local"), "local_holiday": U("local_holiday"),
        "local_toast": U("local_toast"),
        "island": U("island"), "zone": U("zone"), "zone_general": U("zone_general"), "pick_island": U("pick_island"),
        "island_holiday": U("island_holiday"),
        "privacy": U("privacy"), "data_source": U("data_source"), "locals": U("locals"),
        "n_hol": U("n_holidays"), "n_pts": U("n_bridges"), "n_lab": U("n_workdays"), "n_nat": U("n_national"),
        "crumbs": None,
        "ics_calname": f"{hol_word} 2027 · {{label}}", "vac_event": U("vacation"),
        "title_privacy": f'{U("privacy")} · El Calendario Laboral', "desc_privacy": U("privacy_meta"),
        "privacy_p1": U("privacy_p1"), "privacy_p3": U("privacy_p3"),
        "privacy_ads": U("privacy_ads"), "privacy_links": U("privacy_links"),
        "og_l1": site, "og_home": U("og_title"), "app_desc": U("manifest_description"),
    })
    t["_months"], t["_mon3"], t["_wd"], t["_wd3"] = M["full"], M["short"], W["full"], W["short"]
    t["_mof"] = M["gen"] if lang == "eu" else M["of"]
    t["_wdh"] = [x.capitalize() for x in W["two"]]
    # Basque one-letter days repeat (A A A O O L I), so phones get the two-letter set
    t["_wd1"] = t["_wdh"] if lang == "eu" else [x.capitalize() if len(x) > 1 else x for x in W["one"]]
    return t


def _es_dates(t):
    M, W = I18N["months"]["es"], I18N["weekdays"]["es"]
    t["_months"], t["_mon3"], t["_wd"], t["_wd3"], t["_mof"] = M["full"], M["short"], W["full"], W["short"], M["of"]
    t["_wdh"] = [x.capitalize() for x in W["short"]]
    t["_wd1"] = W["one"]


T = strings(LANG)
if LANG == "es":
    _es_dates(T)


def t(key, **kw):
    s = T.get(key)
    if s is None:
        s = ES.get(key, "")
    return s.format(**kw) if kw else s


def tn(key, n, **kw):
    v = T.get(key) or ES[key]
    s = v["one"] if n == 1 else v["other"]
    return s.format(n=n, **kw)


def R(r):
    """Region names for templates: region, region_in, region_of (+ seo, the usual form in this language, or None)."""
    slug = r["slug"]
    if LANG == "es":
        return {"region": r["name"], "region_in": f'en {r["name"]}', "region_of": ES_OF.get(slug, f'de {r["name"]}'), "seo": None}
    x = I18N["regions"][slug][LANG]
    return {"region": x["name"], "region_in": x["in"], "region_of": x["of"], "seo": x.get("seo")}


def fill(s, names, **kw):
    return s.format(**names, **kw) if "{" in s else s


# ---------------------------------------------------------------- dates in this language

def _d(x):
    return x if isinstance(x, dt.date) else dt.date.fromisoformat(x)


def eu_da(n):
    return str(n) if n in (11, 31) else f"{n}a"  # Basque day with article, bare for 11 and 31 (i18n date_patterns.eu)


def dm(x):
    """1 de enero · 1 de gener · 1 de xaneiro · urtarrilaren 1a"""
    d = _d(x)
    m = T["_mof"][d.month - 1]
    return f"{m} {eu_da(d.day)}" if LANG == "eu" else f"{d.day} {m}"


def dlong(x):
    d = _d(x)
    wd = T["_wd"][d.weekday()]
    return f"{dm(d)}, {wd}" if LANG == "eu" else f"{wd} {dm(d)}"


def dshort(x):
    """vie 1 ene · dv. 1 gen. · urt. 1, or."""
    d = _d(x)
    w, m = T["_wd3"][d.weekday()], T["_mon3"][d.month - 1]
    return f"{m} {d.day}, {w}" if LANG == "eu" else f"{w} {d.day} {m}"


def dmon(x):
    d = _d(x)
    m = T["_mon3"][d.month - 1]
    return f"{m} {d.day}" if LANG == "eu" else f"{d.day} {m}"


def drange(i, j):
    a, b = DAYS[i], DAYS[j]
    if a.month == b.month and LANG != "eu":
        return f'{T["_wd3"][a.weekday()]} {a.day} – {dshort(b)}'
    return f"{dshort(a)} – {dshort(b)}"


def dlist(idx):
    """Days to take: 'lun 4, mar 5 ene' (same as dlist() in app.js)."""
    if len(idx) == 2 and DAYS[idx[0]].month == DAYS[idx[1]].month and LANG != "eu":
        a = DAYS[idx[0]]
        return f'{T["_wd3"][a.weekday()]} {a.day}, {dshort(DAYS[idx[1]])}'
    return ", ".join(dshort(DAYS[i]) for i in idx)


def dmy(iso):
    d = _d(iso)
    return f'{d.day} {T["_mon3"][d.month - 1]} {d.year}'


# ---------------------------------------------------------------- data

def localize(data, lang=LANG, i18n=None):
    """Copy of data with names in `lang` (data/i18n.json top-level views). Missing names stay Spanish."""
    tr = (I18N if i18n is None else i18n).get(lang, {})
    if not tr or lang == "es":
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
            out.append({**opt["add"], "code": 3, "kind": "i" if slug == "canarias" else "r"})
    out.sort(key=lambda h: h["date"])
    return out


def runs(off):
    res, s = [], 0
    for i in range(1, len(off) + 1):
        if i == len(off) or off[i] != off[s]:
            res.append([s, i - 1, off[s]])
            s = i
    return res


def _bridge_items(hols):
    """Todos los tramos: fines de semana largos (coste 0) y huecos de 1-2 laborables junto a un festivo."""
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


def puentes(hols):
    """Puentes de verdad: cogiendo 1 o 2 laborables. Misma logica que bridges() en app.js."""
    return [it for it in _bridge_items(hols) if it["cost"]]


def long_weekends(hols):
    """Fines de semana largos sin coger nada, salvo los que ya caen dentro de un puente."""
    items = _bridge_items(hols)
    pts = [it for it in items if it["cost"]]
    return [it for it in items if not it["cost"] and not any(p["s"] <= it["s"] and it["e"] <= p["e"] for p in pts)]


def all_breaks(hols):
    """Puentes and long weekends in one list, by date (the puentes table)."""
    return sorted(puentes(hols) + long_weekends(hols), key=lambda it: (it["s"], it["e"]))


def workdays(hols, minus=0):
    hd = {h["date"] for h in hols}
    return sum(1 for d in DAYS if d.weekday() < 5 and d.isoformat() not in hd) - minus


def page_holidays(data, r=None, city=None):
    if not r:
        return [h for h in region_holidays(data, "madrid") if h["kind"] == "n"]
    hols = region_holidays(data, r["slug"], city["zone"] if city else None)
    if city:
        hols = sorted(hols + [{"date": h["date"], "name": h["name"], "code": 0, "kind": "l"} for h in city["holidays"]],
                      key=lambda h: h["date"])
    return hols


def pick(limit, *cands):
    """First candidate that fits in `limit` characters (titles 60, descriptions 155); else the shortest."""
    for c in cands:
        if c and len(c) <= limit:
            return c
    return min((c for c in cands if c), key=len)


# ---------------------------------------------------------------- html parts

ADSENSE = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-9914165605609514" '
           'crossorigin="anonymous"></script>')
SW_JS = ("<script>if('serviceWorker'in navigator)addEventListener('load',function(){navigator.serviceWorker.register('"
         + ASSETS + "sw.js',{scope:'" + ASSETS + "'}).catch(function(){})});</script>")
CHEV = '<svg class="chev" width="10" height="10" viewBox="0 0 10 10" aria-hidden="true"><path d="M1.5 3.5 5 7l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'
GLOBE = ('<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.3"/>'
         '<path d="M1.5 8h13M8 1.5c2 2 2.8 4.2 2.8 6.5S10 12.5 8 14.5M8 1.5C6 3.5 5.2 5.7 5.2 8S6 12.5 8 14.5" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>')
BURGER = '<svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><path d="M3 5h14M3 10h14M3 15h14" stroke="currentColor" stroke-width="1.8"/></svg>'
KINDS = {"n": "k_n", "r": "k_r", "i": "k_i", "l": "k_l"}

PAGE_PATH = ""  # path of the page being written, below the language base (for the language selector)
PAGE_LANGS = LANGS  # languages that have this page; the selector sends the others to their home
REGIONS = []    # localized regions, for menus and footer


def lang_links():
    return "".join(f'<a href="{lang_base(x)}{PAGE_PATH if x in PAGE_LANGS else ""}" hreflang="{x}" lang="{x}"{" aria-current=true" if x == LANG else ""}>{LANG_NAMES[x]}</a>'
                   for x in LANGS)


def wordmark():
    return f'<a class="brand" href="{BASE}"><i class="mark" aria-hidden="true"></i>elcalendariolaboral<span class="tld">.es</span></a>'


def header_html(here=""):
    """Wordmark, nav (Comunidades menu, Festivos locales, Puentes) and the language menu."""
    regs = "".join(f'<a href="{BASE}{r["slug"]}/">{E(r["name"])}</a>' for r in REGIONS)
    pts_href = "#puentes" if here == "app" else f"{BASE}#puentes"
    return (f'<header class="hd"><div class="wrap hd-in">{wordmark()}'
            f'<nav class="nav" id="nav">'
            f'<details class="dd dd-reg"><summary>{t("nav_regions")}{CHEV}</summary><div class="menu menu-reg">{regs}</div></details>'
            f'<a href="{BASE}festivos-locales/"{" aria-current=page" if here == "locals" else ""}>{t("nav_locals")}</a>'
            f'<a href="{pts_href}">{t("nav_bridges")}</a></nav>'
            f'<details class="dd dd-lang"><summary>{GLOBE}<span class="ln-l">{LANG_NAMES[LANG]}</span><span class="ln-s">{LANG.upper()}</span>{CHEV}</summary>'
            f'<div class="menu menu-lang">{lang_links()}</div></details>'
            f'<button class="burger" id="burger" type="button" aria-expanded="false" aria-controls="nav" aria-label="{t("menu")}">{BURGER}</button>'
            f'</div></header>')


def footer_html(data):
    regs = "".join(f'<li><a href="{BASE}{r["slug"]}/">{E(r["name"])}</a></li>' for r in REGIONS)
    s = data["source"]
    return (f'<footer class="ft"><div class="wrap ft-in">'
            f'<section class="ft-reg"><h2>{t("nav_regions")}</h2><ul class="cols">{regs}</ul></section>'
            f'<section><h2>{t("nav_locals")}</h2><ul><li><a href="{BASE}festivos-locales/">{t("nav_locals")} 2027</a></li></ul>'
            + (f'<h2>Calendario escolar</h2><ul><li><a href="{BASE}calendario-escolar/">Calendario escolar 2026-2027</a></li>'
               f'<li><a href="{BASE}vacaciones-escolares/navidad/">Vacaciones de Navidad 2026-2027</a></li>'
               f'<li><a href="{BASE}vacaciones-escolares/semana-santa/">Vacaciones de Semana Santa 2027</a></li>'
               f'<li><a href="{BASE}vacaciones-escolares/carnaval/">Carnaval y semana blanca 2027</a></li></ul>' if LANG == "es" else "")
            + '</section>'
            f'<section><h2>El Calendario Laboral</h2><ul><li><a href="{s["url"]}" rel="noopener">{t("data_source")}</a></li>'
            f'<li><a href="{ASSETS}widget/"{"" if LANG == "es" else " hreflang=es lang=es"}>Widget para tu web</a></li>'
            f'<li><a href="{BASE}privacidad/">{t("privacy")}</a></li></ul>'
            f'<p class="ft-lang">{lang_links()}</p></section>'
            f'</div><div class="wrap ft-b">© 2026 {HOST}</div></footer>')


def head_html(title, desc, path, og_img, extra="", hreflang=True, langs=None):
    """path: page path below the language base ('' for the home). hreflang for every language in `langs` (default all)
    + x-default; a page in one language only gets no alternates."""
    global PAGE_PATH, PAGE_LANGS
    PAGE_PATH = path
    PAGE_LANGS = langs or LANGS
    canonical = URL + path
    alts = "".join(f'<link rel="alternate" hreflang="{x}" href="{SITE}{lang_base(x)}{path}">' for x in PAGE_LANGS) if hreflang and len(PAGE_LANGS) > 1 else ""
    if len(PAGE_LANGS) > 1 and hreflang:
        alts += f'<link rel="alternate" hreflang="x-default" href="{SITE}{lang_base("es")}{path}">'
    canon = f'<link rel="canonical" href="{canonical}">' if hreflang else '<meta name="robots" content="noindex">'
    return f"""<!doctype html>
<html lang="{LANG}" data-base="{BASE}" data-assets="{ASSETS}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{canon}{alts}
<meta name="theme-color" content="#ffffff">
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="{ASSETS}app.css?v={{CSSV}}">
{ADSENSE}
{extra}
</head>
"""


def crumbs_html(items):
    out = []
    for k, (name, path) in enumerate(items):
        if k == len(items) - 1:
            out.append(f'<li aria-current="page">{E(name)}</li>')
        else:
            out.append(f'<li><a href="{BASE}{path}">{E(name)}</a></li>')
    aria = f' aria-label="{t("crumbs")}"' if T.get("crumbs") else ""
    return f'<nav class="crumbs"{aria}><ol>{"".join(out)}</ol></nav>'


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


# ---------------------------------------------------------------- calendar, lists and tables (same markup as app.js)

def sw(kind):
    return f'<i class="sw {kind}" aria-hidden="true"></i>'


def scope_txt(kind):
    return t(KINDS[kind])


def month_items(m, hols):
    """Holidays under a month card: '1 Año Nuevo'. Same as monthItems() in app.js."""
    out = []
    for h in hols:
        d = _d(h["date"])
        if d.month == m:
            we = " we" if d.weekday() >= 5 else ""
            out.append(f'<li class="k-{h["kind"]}{we}"><b>{d.day}</b> {E(h["name"])}</li>')
    return "".join(out)


def month_html(m, hmap, hols, year=YEAR, idp="", items=None, show_year=False):
    """One month card. The school calendar passes the year, idp=None (no ids: several grids per page), its own list
    under the month and show_year (the caption reads "Enero 2027")."""
    first = dt.date(year, m, 1)
    nd = ((dt.date(year + (m == 12), m % 12 + 1, 1)) - first).days
    cells = [""] * first.weekday()
    for d in range(1, nd + 1):
        day = dt.date(year, m, d)
        iso = day.isoformat()
        cls = ["we"] if day.weekday() >= 5 else []
        tt = ""
        if iso in hmap:
            cls.append(hmap[iso]["kind"])
            tt = f' title="{E(hmap[iso]["name"])}"'
        c = f' class="{" ".join(cls)}"' if cls else ""
        cells.append(f'<td data-d="{iso}"{c}{tt}>{d}</td>')
    weeks = -(-len(cells) // 7)
    cells += [""] * (weeks * 7 - len(cells))
    rows = "".join("<tr>" + "".join(c or "<td></td>" for c in cells[w * 7:w * 7 + 7]) + "</tr>" for w in range(weeks))
    head = "".join(f'<th scope="col" abbr="{T["_wd"][k]}"><span class="wl">{x}</span><span class="ws">{T["_wd1"][k]}</span></th>'
                   for k, x in enumerate(T["_wdh"]))
    name = T["_months"][m - 1].capitalize() + (f" {year}" if show_year else "")
    ids = (f' id="{idp}m{m}"', f' id="{idp}mh{m}"') if idp is not None else ("", "")
    return (f'<div class="mon"{ids[0]}><table><caption>{name}</caption><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'
            f'<ul class="mh"{ids[1]}>{month_items(m, hols) if items is None else items}</ul></div>')


def year_html(hols):
    hmap = {}
    for h in hols:
        hmap.setdefault(h["date"], h)
    return '<div class="year" id="year">' + "".join(month_html(m, hmap, hols) for m in range(1, 13)) + "</div>"


def legend_html(kinds):
    li = "".join(f'<li>{sw(k)}{t(KINDS[k])}</li>' for k in kinds)
    return (f'<ul class="legend" aria-label="{t("legend")}">{li}<li id="k-v" hidden>{sw("v")}<span id="vcount"></span>'
            f'<button type="button" class="lnk" id="vclear">{t("clear")}</button></li></ul>')


def hol_item(h):
    """One line of the full list. Same as holItem() in app.js."""
    d = _d(h["date"])
    we = " we" if d.weekday() >= 5 else ""
    k = h["kind"]
    return (f'<li class="k-{k}"><span class="d"><time datetime="{h["date"]}">{dm(d)}</time> <span class="m{we}">{T["_wd"][d.weekday()]}</span></span>'
            f'<span class="h">{E(h["name"])}</span><span class="s">{sw(k)}{scope_txt(k)}</span></li>')


def island_item():
    return (f'<li class="k-z"><span class="d">+1</span><span class="h">{t("island_holiday")} '
            f'<button type="button" class="lnk" data-zone>{t("pick_island")}</button></span><span class="s">{sw("i")}{t("k_i")}</span></li>')


def pts_head():
    return (f'<thead><tr><th scope="col">{t("col_bridge")}</th><th scope="col" class="num">{t("col_free")}</th>'
            f'<th scope="col">{t("col_vac")}</th></tr></thead>')


def pts_row(it):
    """Same markup as ptsRow() in app.js."""
    nm = " · ".join(it["names"])
    if it["cost"]:
        vac = (f'<span class="mo">{tn("vac_days", it["cost"])}: </span><b class="dk">{it["cost"]}</b> '
               f'<span class="m">{E(dlist(it["take"]))}</span>')
    else:
        vac = f'<b class="dk">0</b> <span class="m">{t("no_vac")}</span>'
    return (f'<tr{" class=lw" if not it["cost"] else ""}><td class="c-p"><span class="rng">{drange(it["s"], it["e"])}</span>'
            f'<span class="m nm">{E(nm)}</span></td><td class="num">{tn("n_days", it["len"])}</td><td class="c-v">{vac}</td></tr>')


JS_KEYS = ["k_n", "k_r", "k_i", "k_l", "no_vac", "no_bridges", "island_holiday", "pick_island", "remove_local", "local_holiday",
           "local_toast", "vac_days", "vac_added", "vac_removed", "vac_cleared", "add_vac", "rm_vac", "n_hol", "n_lab", "n_days",
           "next_hol", "days_left", "tomorrow", "today", "ics_file", "ics_calname", "vac_event", "add_local", "add_short", "rm_short",
           "free_n", "see_cal"]


def js_strings():
    out = {k: (T.get(k) if T.get(k) is not None else ES[k]) for k in JS_KEYS}
    out.update({"months": T["_months"], "mon3": T["_mon3"], "wd": T["_wd"], "wd3": T["_wd3"], "mof": T["_mof"], "eu": LANG == "eu"})
    return json.dumps(out, ensure_ascii=False, separators=(",", ":"))


def section(id_, title, body, tools="", cls=""):
    return (f'<section class="sec{" " + cls if cls else ""}" id="{id_}" aria-labelledby="h-{id_}"><div class="sec-h"><h2 id="h-{id_}">{title}</h2>'
            f'{tools}</div>{body}</section>')


def tools_html(key=None, ics_name=""):
    """Print, and for a region or city also the CSV and the calendar menu."""
    out = f'<button class="btn" type="button" data-print>{t("print")}</button>'
    if key:
        webcal = f"webcal://{HOST}{ASSETS}ics/{key}.ics"
        out += (f'<a class="btn" href="{ASSETS}csv/{key}.csv" download="calendario-laboral-2027-{key}.csv">{t("csv")}</a>'
                f'<details class="dd dd-cal"><summary class="btn">{t("add_cal")}{CHEV}</summary><div class="menu menu-cal">'
                f'<a id="dl" href="{ASSETS}ics/{key}.ics" download="{ics_name}">{t("ics_dl")}</a>'
                f'<a id="gc" href="https://calendar.google.com/calendar/r?cid={quote(webcal, safe="")}" rel="noopener" target="_blank">{t("gcal")}</a>'
                f'<a id="wc" href="{webcal}">{t("apple")}</a></div></details>')
    return f'<div class="tools">{out}</div>'


def scripts(data):
    compact = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return (f'<script id="cal-data" type="application/json">{compact}</script>\n'
            f'<script id="cal-i18n" type="application/json">{js_strings()}</script>\n'
            f'<script src="{ASSETS}app.js?v={{JSV}}"></script>\n{SW_JS}')


def page(head, body_cls, header_here, main, data, attrs="", js=True):
    tail = scripts(data) if js else f'<script src="{ASSETS}app.js?v={{JSV}}"></script>\n{SW_JS}'
    return head + f"""<body class="{body_cls}"{attrs}>
<a class="skip" href="#main">{E(t("h1"))}</a>
{header_html(header_here)}
<main id="main">
{main}
</main>
{footer_html(data)}
<div class="toast" id="toast" role="status" aria-live="polite"></div>
{tail}
</body>
</html>
"""


def region_select(current):
    first = "" if current else f'<option value="" selected disabled>{t("pick_region")}</option>'
    opts = first + "".join(f'<option value="{x["slug"]}"{" selected" if x["slug"] == current else ""}>{E(x["name"])}</option>' for x in REGIONS)
    return f'<div class="field"><label for="region">{t("region_label")}</label><select id="region">{opts}</select></div>'


def city_select(r, cities, pending, current=None):
    """Municipio: published cities go to their page; pending ones are listed disabled (Spanish only)."""
    if not cities and not (pending and LANG == "es"):
        return ""
    opts = f'<option value="{BASE}{r["slug"]}/">{E(r["name"])}</option>'
    items = [(x["title_name"], f'<option value="{BASE}{x["path"]}"{" selected" if current == x["slug"] else ""}>{E(x["title_name"])}</option>') for x in cities]
    if LANG == "es":
        items += [(n, f'<option disabled>{E(n)} {t("pending_short")}</option>') for n in pending]
    opts += "".join(o for _, o in sorted(items, key=lambda z: z[0]))
    return f'<div class="field"><label for="city">{t("municipio")}</label><select id="city">{opts}</select></div>'


# ---------------------------------------------------------------- app page (region and city)

def app_main(data, r, city=None, hero_extra="", more="", cities=(), pending=()):
    """Region or city page: hero with pickers, calendar, puentes, planner, full list, then `more` (locals, FAQ)."""
    slug = r["slug"]
    names = R(r)
    hols = page_holidays(data, r, city)
    is_can = slug == "canarias" and not city
    zone = data["zones"].get(slug) if not city else None
    breaks = all_breaks(hols)
    n = len(hols) + (1 if is_can else 0)
    lab = workdays(hols, 1 if is_can else 0)
    key = f'{slug}-{city["slug"]}' if city else slug
    place = city["title_name"] if city else names["region"]
    pnames = {**names, "region": place, "region_in": city["in"] if city else names["region_in"]}

    if city:
        h1, crumbs = city["h1"], city["crumbs"]
    else:
        h1 = fill(t("h1_region"), names)
        crumbs = crumbs_html([(t("spain"), ""), (r["name"], f"{slug}/")])
    ctx = (f'<p class="ctx"><span>{E(r["official"])}</span> · <span id="c-n">{tn("n_hol", n)}</span> · '
           f'<span id="c-l">{tn("n_lab", lab)}</span></p>')
    sel = region_select(slug) + city_select(r, cities, pending, city["slug"] if city else None)
    if zone:
        zopts = (f'<option value="">{t("pick_island")}</option>' if is_can else "") + "".join(
            f'<option value="{o["slug"]}">{E(t("zone_general") if o["slug"] == "general" else o["name"])}</option>' for o in zone["options"])
        sel += f'<div class="field"><label for="zone">{t("island") if is_can else t("zone")}</label><select id="zone">{zopts}</select></div>'
    hero = (f'<div class="hero wrap">{crumbs}<h1>{E(h1)}</h1>{ctx}{hero_extra}<p class="next" id="next" hidden></p>'
            f'<div class="pickers">{sel}</div></div>')

    kinds = ["n", "r"] + (["i"] if slug == "canarias" else []) + ["l"]
    cal_sec = section("calendario", t("h_cal"), legend_html(kinds) + year_html(hols), tools_html(key, f'{t("ics_file")}-{key}.ics'), "cal")
    prow = "".join(pts_row(it) for it in breaks) or f'<tr><td colspan="3">{t("no_bridges")}</td></tr>'
    pts_sec = section("puentes", E(fill(t("h_pts"), pnames)), f'<table class="tbl pts">{pts_head()}<tbody id="plist">{prow}</tbody></table>')
    plan = (f'<div class="step"><label for="vn">{t("how_many")}</label><span class="stepper"><button type="button" id="vm" aria-label="{t("one_less")}">−</button>'
            f'<input id="vn" type="number" inputmode="numeric" min="1" max="30" value="4"><button type="button" id="vp" aria-label="{t("one_more")}">+</button></span></div>'
            f'<table class="tbl plan"><thead><tr><th scope="col">{t("col_vac")}</th><th scope="col" class="num">{t("col_free")}</th><td></td><td></td></tr></thead>'
            f'<tbody id="vlist"></tbody></table>')
    vac_sec = section("vacaciones", t("h_vac"), plan)
    items = "".join(hol_item(h) for h in hols) + (island_item() if is_can else "")
    addloc = "" if city else (f'<div class="tbl-f"><button type="button" class="btn" id="addloc">+ {t("add_local")}</button>'
                              f'<input type="date" id="locin" min="2027-01-01" max="2027-12-31" aria-label="{t("local_holiday")}" tabindex="-1" class="vh"></div>')
    hol_sec = section("festivos", E(fill(t("h_hol"), pnames)), f'<ol class="hl" id="hlist">{items}</ol>{addloc}')
    foot = f'<p class="pfoot">{HOST}{BASE}{city["path"] if city else slug + "/"} · {E(data["source"]["boe"])}</p>'
    return f'{hero}<div class="wrap body">{cal_sec}{pts_sec}{vac_sec}{hol_sec}{more}{foot}</div>{POP}'


POP = '<div class="pop" id="pop" role="dialog" hidden><p class="pop-d" id="pop-d"></p><p class="pop-h" id="pop-h"></p><div class="pop-a" id="pop-a"></div></div>'


def app_attrs(r, city=None):
    a = f' data-region="{r["slug"]}"'
    if city:
        locs = [{"date": h["date"], "name": h["name"]} for h in city["holidays"]]
        a += (f' data-city="{city["slug"]}" data-cityname="{E(city["title_name"])}" data-zone="{city["zone"] or ""}"'
              f' data-locals="{E(json.dumps(locs, ensure_ascii=False, separators=(",", ":")))}"')
    return a


# ---------------------------------------------------------------- privacy and 404

def privacy_page(data):
    src = data["source"]
    link = f'<a href="{src["url"]}" rel="noopener">{src["id"]}</a>'
    main = (f'<div class="wrap doc">{crumbs_html([(t("spain"), ""), (t("privacy"), "privacidad/")])}<h1>{t("privacy")}</h1>'
            f'<p>{E(t("privacy_p1"))}</p><p>{E(t("privacy_ads"))}</p><p>{E(t("privacy_p3"))}</p>'
            f'<p>{t("privacy_links")}</p>'
            f'<p>{t("data_source").split(":")[0]}: {link}, {E(src["boe"])}. '
            f'<a href="mailto:cesar0407p@gmail.com">cesar0407p@gmail.com</a></p></div>')
    head = head_html(t("title_privacy"), t("desc_privacy"), "privacidad/", f"{SITE}{ASSETS}og/espana.png")
    return page(head, "pg", "", main, data, js=False)


def page_404(data):
    """GitHub Pages serves /404.html for every missing path. Absolute links, so it works at any depth."""
    homes = "".join(f'<a class="btn" href="{lang_base(x)}" hreflang="{x}" lang="{x}">{LANG_NAMES[x]}</a>' for x in LANGS)
    chips = "".join(f'<li><a href="{BASE}{r["slug"]}/">{E(r["name"])}</a></li>' for r in REGIONS)
    main = (f'<div class="wrap doc"><p class="e404">404</p><h1>Página no encontrada</h1>'
            f'<div class="tools">{homes}</div></div><div class="wrap body narrow">'
            + section("comunidades", t("pick_region"), f'<ul class="chips">{chips}</ul>') + '</div>')
    head = head_html("Página no encontrada · El Calendario Laboral", t("desc_home"), "404.html", f"{SITE}{ASSETS}og/espana.png", hreflang=False)
    return page(head, "pg", "", main, data, js=False)


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


INK, BG, MUT, LINE, WE = (27, 31, 36), (255, 255, 255), (90, 98, 112), (216, 220, 226), (238, 240, 243)
NAT, REG, RED = (244, 184, 177), (246, 210, 122), (200, 16, 46)


def og_image(path, label, sub, hols):
    """Same look as the page: the wordmark with its red mark, dark type on white, the year as a grid of squares."""
    from PIL import Image, ImageDraw
    W, H, S = 1200, 630, 2
    im = Image.new("RGB", (W * S, H * S), BG)
    d = ImageDraw.Draw(im)
    X = 72 * S
    d.rectangle((X, 76 * S, X + 18 * S, 94 * S), fill=RED)
    d.text((X + 30 * S, 70 * S), "elcalendariolaboral", font=font(26 * S, "b"), fill=INK)
    w = d.textlength("elcalendariolaboral", font=font(26 * S, "b"))
    d.text((X + 30 * S + w, 70 * S), ".es", font=font(26 * S, "r"), fill=MUT)
    d.text((X, 150 * S), t("og_l1"), font=font(36 * S, "sb"), fill=MUT)
    size = 76 if len(label) <= 11 else (60 if len(label) <= 16 else (46 if len(label) <= 20 else 34))
    d.text((X, 200 * S), label, font=font(size * S, "b"), fill=INK)
    d.text((X, 330 * S), sub, font=font(30 * S, "sb"), fill=MUT)
    kind = {h["date"]: h["kind"] for h in hols}
    x0, y0, c, gx, gy = 700 * S, 58 * S, 17 * S, 30 * S, 22 * S
    for m in range(12):
        col, row = m % 3, m // 3
        ox, oy = x0 + col * (7 * c + gx), y0 + row * (6 * c + gy + 24 * S)
        d.text((ox, oy - 4 * S), T["_months"][m][:3].capitalize(), font=font(15 * S, "b"), fill=INK)
        first = dt.date(YEAR, m + 1, 1)
        nd = ((dt.date(YEAR + (m == 11), (m + 1) % 12 + 1, 1)) - first).days
        for dd in range(nd):
            day = first + dt.timedelta(dd)
            idx = first.weekday() + dd
            cx, cy = ox + (idx % 7) * c, oy + 24 * S + (idx // 7) * c
            k = kind.get(day.isoformat())
            fill_ = NAT if k == "n" else REG if k else (WE if day.weekday() >= 5 else BG)
            d.rectangle((cx + S, cy + S, cx + c - S, cy + c - S), fill=fill_, outline=LINE)
    im = im.resize((W, H), Image.LANCZOS).quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    im.save(path, optimize=True)


def icons(out):
    """The wordmark's red square with '27' in white."""
    from PIL import Image, ImageDraw

    def draw(size, maskable=False, bg_full=False):
        S = 4 * size
        im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if maskable or bg_full:
            d.rectangle((0, 0, S, S), fill=RED)
        else:
            d.rounded_rectangle((0, 0, S - 1, S - 1), int(S * 0.16), fill=RED)
        f = font(int(S * (0.42 if maskable else 0.52)), "b")
        box = d.textbbox((0, 0), "27", font=f)
        d.text(((S - (box[2] - box[0])) / 2 - box[0], (S - (box[3] - box[1])) / 2 - box[1]), "27", font=f, fill=BG)
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


def sitemap(urls_by_path):
    """One sitemap, every language, each url with its xhtml:link alternates."""
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for p, lm, *only in urls_by_path:
        langs = only[0] if only else LANGS  # a page in fewer languages lists only those (one language: no alternates)
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{SITE}{lang_base(x)}{p}"/>' for x in langs) if len(langs) > 1 else ""
        if len(langs) > 1:
            alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{lang_base("es")}{p}"/>'
        for x in langs:
            sm.append(f"  <url><loc>{SITE}{lang_base(x)}{p}</loc><lastmod>{lm}</lastmod>{alts}</url>")
    sm.append("</urlset>")
    return "\n".join(sm) + "\n"


def main():
    global REGIONS
    if LANG == "es" and not os.environ.get("CL_CHILD"):
        for x in LANGS:
            if x != "es":
                env = {**os.environ, "CL_LANG": x, "CL_CHILD": "1", "CL_LANGS": ",".join(LANGS)}
                subprocess.run([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]], env=env, check=True)
    data = localize(load())
    REGIONS = data["regions"]
    cssv, jsv = short_hash(ROOT / "app.css"), short_hash(ROOT / "app.js")
    fix = lambda s: s.replace("{CSSV}", cssv).replace("{JSV}", jsv)  # noqa: E731

    OUT.mkdir(exist_ok=True)
    (OUT / "privacidad").mkdir(exist_ok=True)
    (OUT / "privacidad" / "index.html").write_text(fix(privacy_page(data)), "utf-8", newline="\n")
    sys.modules.setdefault("build", sys.modules[__name__])  # pages.py does "import build": reuse this module
    import pages
    pages_written = pages.write_pages(data, fix)
    if LANG != "es":
        print(f"ok · {LANG} · {len(pages_written) + 1} pages in {OUT}")
        return

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

    pages.write_shared(data, "--no-img" not in sys.argv)
    (ROOT / "404.html").write_text(fix(page_404(data)), "utf-8", newline="\n")
    (ROOT / "sitemap.xml").write_text(sitemap(pages_written), "utf-8", newline="\n")

    manifest = {
        "name": t("app_name"), "short_name": t("app_short"), "lang": LANG, "description": t("app_desc"),
        "id": ASSETS, "start_url": ASSETS + "?source=pwa", "scope": ASSETS, "display": "standalone",
        "background_color": "#ffffff", "theme_color": "#ffffff", "categories": ["productivity", "utilities"],
        "icons": [{"src": ASSETS + "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": ASSETS + "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
                  {"src": ASSETS + "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
    }
    (ROOT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8", newline="\n")

    ver = "v4-" + short_hash(ROOT / "index.html", ROOT / "app.css", ROOT / "app.js", ROOT / "data" / "2027.json")
    shell = [f"{ASSETS}app.css?v={cssv}", f"{ASSETS}app.js?v={jsv}", f"{ASSETS}manifest.webmanifest",
             f"{ASSETS}icons/icon-192.png", f"{ASSETS}icons/icon-512.png"]
    sw = (ROOT / "sw.src.js").read_text("utf-8").replace("__VERSION__", ver).replace("__SHELL__", json.dumps(shell))
    (ROOT / "sw.js").write_text(sw, "utf-8", newline="\n")
    print(f"ok · {sum(len(w[2]) if len(w) > 2 else len(LANGS) for w in pages_written)} urls · sw {ver}")


if __name__ == "__main__":
    main()
