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
S["es"].update({
    "dh_link": "Calculadora de días hábiles",
    "dh_title": "Calculadora de días hábiles y laborables entre fechas",
    "dh_desc": "Calcula los días hábiles o laborables entre dos fechas, o qué día vence un plazo de días hábiles, con los festivos de tu comunidad y tu municipio.",
    "dh_h1": "Calculadora de días hábiles", "dh_crumb": "Días hábiles",
    "dh_intro": "Cuenta los días hábiles entre dos fechas o calcula cuándo vence un plazo, con los festivos de tu comunidad y tu municipio.",
    "nat_only": "Solo festivos nacionales", "all_region": "Toda la comunidad", "isla": "isla", "zona": "zona",
    "workweek": "Días hábiles", "mon_fri": "Lunes a viernes", "mon_sat": "Lunes a sábado",
    "mode_a": "Entre dos fechas", "mode_b": "Sumar días hábiles",
    "from": "Desde", "to": "Hasta", "start": "Fecha inicial", "n_work": "Días hábiles",
    "res_a": {"one": "día hábil", "other": "días hábiles"},
    "nat_days": {"one": "{n} día natural", "other": "{n} días naturales"},
    "n_hol_in": {"one": "{n} festivo", "other": "{n} festivos"},
    "after": {"one": "{n} día hábil después del {d}", "other": "{n} días hábiles después del {d}"},
    "no_loc": "sin festivos locales de 2026", "out": "Fuera de 2026-2027",
    "h_hols_in": "Festivos en esas fechas", "none_in": "Ningún festivo entre esas fechas.",
    "caveat": "Orientativo. Para plazos legales, consulta el calendario oficial de días inhábiles.",
    "dh_faq": [
        ("¿Qué días son inhábiles en un plazo administrativo?",
         "Según la Ley 39/2015 (artículo 30), los sábados, los domingos y los festivos nacionales, autonómicos y locales. Si un día "
         "es hábil donde vives e inhábil en la sede del organismo, o al revés, se considera inhábil."),
        ("¿Y los días laborables?",
         "Normalmente, de lunes a viernes menos los festivos. Si trabajas los sábados, elige «Lunes a sábado»."),
        ("¿Desde qué día se cuenta un plazo?",
         "Desde el día siguiente a la notificación o la publicación. Por eso, al sumar días hábiles, la cuenta empieza el día "
         "siguiente a la fecha inicial. Si el último día es inhábil, el plazo pasa al siguiente día hábil."),
        ("Entre dos fechas, ¿cuentan el primer y el último día?",
         "Sí: los dos cuentan si son hábiles."),
        ("¿Sirve para plazos judiciales?",
         "No del todo: en los judiciales también son inhábiles todo agosto y del 24 de diciembre al 6 de enero (artículo 183 de la "
         "Ley Orgánica del Poder Judicial), salvo actuaciones urgentes. Esta calculadora no los descuenta."),
    ],
})
S["es"].update({
    "dl_link": "Días laborables 2027",
    "dl_title": "Días laborables 2027 por comunidad y mes (y horas)",
    "dl_desc": "Días laborables de 2027 en cada comunidad autónoma, mes a mes, con el total del año y las horas de trabajo con jornada de 8 horas. Según el BOE.",
    "dl_h1": "Días laborables 2027", "dl_crumb": "Días laborables 2027",
    "dl_intro": "De lunes a viernes, menos los festivos nacionales y autonómicos del BOE. Sin los 2 locales de cada municipio.",
    "dl_h2": "Días laborables por comunidad", "col_total": "Total", "col_hours": "Horas (8 h)", "no_island": "sin fiesta insular",
    "dl_faq": [
        ("¿Cuántos días laborables tiene 2027?",
         "2027 tiene {wd} días de lunes a viernes. Quitando los festivos nacionales y autonómicos que caen entre semana, quedan "
         "entre {lo} y {hi}, según la comunidad, sin contar los 2 festivos locales."),
        ("¿Cuántas horas laborables tiene 2027?",
         "Con jornadas de 8 horas, entre {hlo} y {hhi} horas. Si restas 22 días laborables de vacaciones, quedan entre {vlo} y {vhi}."),
        ("¿Se cuentan los festivos locales?",
         'No, porque cambian en cada municipio. Resta los 2 de tu ciudad si caen entre semana: están en '
         '<a href="{loc}">festivos locales 2027</a>.'),
        ("¿Qué meses de 2027 tienen más días laborables?",
         "{mmax}: {nmax} en la mayoría de comunidades. Con menos días, {mmin}: {nmin}."),
    ],
})
ONLY_WK = [x for x in ("es", "ca", "gl", "eu") if x in S]
PATH_WK = "semana/"
ONLY_DH = [x for x in ("es", "ca", "gl", "eu") if "dh_link" in S.get(x, {})]
PATH_DH = "dias-habiles/"
ONLY_DL = [x for x in ("es", "ca", "gl", "eu") if "dl_link" in S.get(x, {})]
PATH_DL = "dias-laborables-2027/"


def L(key):
    return S[B.LANG][key]


def ln(key, n, **kw):
    v = L(key)
    return (v["one"] if n == 1 else v["other"]).format(n=n, **kw)


AND = {"es": "y", "ca": "i", "gl": "e", "eu": "eta"}


def join(xs):
    return xs[0] if len(xs) == 1 else f'{", ".join(xs[:-1])} {AND[B.LANG]} {xs[-1]}'


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
    return {"wd3": B.T["_wd3"], "mon3": B.T["_mon3"], "wd": B.T["_wd"], "months": B.T["_months"], "eu": B.LANG == "eu"}


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


# ---------------------------------------------------------------- 2 /dias-habiles/

LO, HI, LOC_FROM = dt.date(2026, 1, 1), dt.date(2027, 12, 31), "2027-01-01"  # data years; city locals only for 2027


def load_year(year):
    """data/<year>.json with names in this language (missing translations stay Spanish)."""
    d = B.localize(json.loads((B.ROOT / "data" / f"{year}.json").read_text("utf-8")))
    tr = NAMES_2026.get(B.LANG, {}) if year == 2026 else {}
    for h in d["holidays"]:
        h["name"] = tr.get(h["name"], h["name"])
    for z in d["zones"].values():
        for o in z["options"]:
            if "add" in o:
                o["add"]["name"] = tr.get(o["add"]["name"], o["add"]["name"])
    return d


NAMES_2026 = {}  # 2026-only holiday names in ca/gl/eu (2027 names come from data/i18n.json)


def is_off(d, off, sat=False):
    """Sunday, Saturday unless it is a working day, or a holiday. Same as isOff() in util.js."""
    return d.weekday() == 6 or (d.weekday() == 5 and not sat) or d.isoformat() in off


def count_workdays(a, b, off, sat=False):
    """Working days from a to b, both included (swapped when a > b). Same as countWorkdays() in util.js."""
    if a > b:
        a, b = b, a
    return sum(1 for k in range((b - a).days + 1) if not is_off(a + dt.timedelta(k), off, sat))


def add_workdays(a, n, off, sat=False):
    """The n-th working day after a (the count starts the next day, Ley 39/2015 art. 30); n = 0 gives a.
    Same as addWorkdays() in util.js."""
    d = a
    while n > 0:
        d += dt.timedelta(1)
        if not is_off(d, off, sat):
            n -= 1
    return d


def dh_data(datas, cities):
    """Holidays for util.js: national, per comunidad, zones (islands, Arán) and cities (2027 locals), both years."""
    nat, reg, zon, cit = [], {}, {}, {}
    for d in datas:
        nat += [[h["date"], h["name"], "n"] for h in d["holidays"] if h["regions"] == "all"]
        for r in d["regions"]:
            reg.setdefault(r["slug"], []).extend([h["date"], h["name"], h["kind"]] for h in B.region_holidays(d, r["slug"]))
            for o in d["zones"].get(r["slug"], {}).get("options", []):
                if "add" not in o:
                    continue
                zs = zon.setdefault(r["slug"], {})
                z = zs.setdefault(o["slug"], [o["slug"], o["name"], [], []])
                z[2].append([o["add"]["date"], o["add"]["name"], "i" if r["slug"] == "canarias" else "r"])
                if "remove" in o:
                    z[3].append(o["remove"])
    for x in sorted(cities, key=lambda x: x["title_name"]):
        cit.setdefault(x["r"]["slug"], []).append([x["slug"], x["title_name"], x["zone"] or "", [[h["date"], h["name"]] for h in x["holidays"]]])
    return {"nat": sorted(nat), "reg": {k: sorted(v) for k, v in reg.items()}, "zon": {k: list(v.values()) for k, v in zon.items()}, "cit": cit}


def dmy_long(d):
    """2 de noviembre de 2026 · 2 de novembre de 2026 · 2026ko azaroaren 2a (holiday list when the range spans years)."""
    return f"{d.year}ko {B.dm(d)}" if B.LANG == "eu" else f"{B.dm(d)} de {d.year}"


def hl_item(iso, name, kind, multi):
    """One holiday of the range: the markup of build.hol_item(). Same as hlItem() in util.js."""
    d = dt.date.fromisoformat(iso)
    we = " we" if d.weekday() >= 5 else ""
    return (f'<li class="k-{kind}"><span class="d"><time datetime="{iso}">{dmy_long(d) if multi else B.dm(d)}</time> '
            f'<span class="m{we}">{B.T["_wd"][d.weekday()]}</span></span><span class="h">{E(name)}</span>'
            f'<span class="s">{B.sw(kind)}{B.t(B.KINDS[kind])}</span></li>')


def date_field(id_, label, value):
    return (f'<div class="field"><label for="{id_}">{label}</label><input type="date" class="din" id="{id_}" value="{value}" '
            f'min="{LO}" max="{HI}" required></div>')


def dh_page(data, write, cities):
    datas = [load_year(2026), data]
    cfg = dh_data(datas, cities)
    a, b = TODAY, dt.date(TODAY.year, 12, 31)
    off = {x[0]: x for x in cfg["nat"]}
    n = count_workdays(a, b, off)
    inr = [x for x in cfg["nat"] if a.isoformat() <= x[0] <= b.isoformat()]
    k = sum(1 for x in inr if not (dt.date.fromisoformat(x[0]).weekday() >= 5))
    regs = "".join(f'<option value="{r["slug"]}">{E(r["name"])}</option>' for r in data["regions"])
    pick1 = (f'<div class="pickers">'
             f'<div class="field"><label for="dreg">{B.t("region_label")}</label><select id="dreg"><option value="">{L("nat_only")}</option>{regs}</select></div>'
             f'<div class="field" id="dmun-f" hidden><label for="dmun">{B.t("municipio")}</label><select id="dmun"></select></div>'
             f'<div class="field"><label for="dsat">{L("workweek")}</label><select id="dsat"><option value="0">{L("mon_fri")}</option>'
             f'<option value="1">{L("mon_sat")}</option></select></div></div>')
    modes = (f'<div class="tools dmode" role="group"><button type="button" class="btn on" data-mode="a" aria-pressed="true">{L("mode_a")}</button>'
             f'<button type="button" class="btn" data-mode="b" aria-pressed="false">{L("mode_b")}</button></div>')
    pick2 = (f'<div class="pickers" id="dpa">{date_field("da", L("from"), a)}{date_field("db", L("to"), b)}</div>'
             f'<div class="pickers" id="dpb" hidden>{date_field("dc", L("start"), a)}'
             f'<div class="field"><label for="dn">{L("n_work")}</label><span class="stepper"><button type="button" id="dnm" aria-label="{B.t("one_less")}">−</button>'
             f'<input id="dn" type="number" inputmode="numeric" min="0" max="999" value="10"><button type="button" id="dnp" aria-label="{B.t("one_more")}">+</button></span></div></div>')
    sub = (f'<span id="dsub">{rng(a, b)} · {ln("nat_days", (b - a).days + 1)} · {ln("n_hol_in", k)}</span>'
           f'<br><span class="m">{L("caveat")}</span>')
    res = card("dres", n, ln("res_a", n), sub)
    h1 = L("dh_h1")
    ch, cld = crumbs(L("dh_crumb"), PATH_DH)
    hero = f'<div class="hero wrap">{ch}<h1>{E(h1)}</h1><p class="ctx">{E(L("dh_intro"))}</p>{pick1}{modes}{pick2}{res}</div>'
    multi = a.year != b.year
    items = "".join(hl_item(*x, multi) for x in inr)
    hol_sec = B.section("festivos", L("h_hols_in"), f'<ol class="hl" id="dhl">{items}</ol><p class="m" id="dnone"{" hidden" if items else ""}>{L("none_in")}</p>')
    qas = L("dh_faq")
    fh, fld = faq(qas)
    keys = ["res_a", "nat_days", "n_hol_in", "after", "no_loc", "out", "all_region", "isla", "zona"]
    js = {**base_cfg(), **cfg, "page": "dh", "min": str(LO), "max": str(HI), "loc": LOC_FROM, "mof": B.T["_mof"],
          "k": {x: B.t(B.KINDS[x]) for x in B.KINDS}, "s": {x: L(x) for x in keys}}
    main = f'{hero}<div class="wrap body narrow">{hol_sec}{B.ad("hub")}{fh}</div>' + js_cfg(js)
    head = B.head_html(L("dh_title"), L("dh_desc"), PATH_DH, f"{B.SITE}{B.ASSETS}og/espana.png",
                       ld(cld, app_ld(h1, PATH_DH, L("dh_desc")), fld), langs=langs_arg(ONLY_DH))
    write(PATH_DH, B.page(head, "pg vac", "", main, data, js=False), UPDATED, langs_arg(ONLY_DH))


# ---------------------------------------------------------------- 3 /dias-laborables-2027/

def per_month(hols, year=B.YEAR):
    """Working days (Monday to Friday, not a holiday) in each month of `year`."""
    hd = {h["date"] for h in hols}
    out = [0] * 12
    d = dt.date(year, 1, 1)
    while d.year == year:
        if d.weekday() < 5 and d.isoformat() not in hd:
            out[d.month - 1] += 1
        d += dt.timedelta(1)
    return out


def dl_rows(data):
    """[(slug, label, zone label or None, months)]: each comunidad, then its islands / Arán as sub-rows."""
    out = []
    for r in data["regions"]:
        out.append((r["slug"], r["name"], None, per_month(B.region_holidays(data, r["slug"]))))
        for o in data["zones"].get(r["slug"], {}).get("options", []):
            if "add" in o:
                out.append((r["slug"], r["name"], o["name"], per_month(B.region_holidays(data, r["slug"], o["slug"]))))
    return out


def dl_page(data, write):
    rows = dl_rows(data)
    head_m = "".join(f'<th scope="col" class="num">{m.capitalize()}</th>' for m in B.T["_mon3"])
    trs = []
    for slug, name, zone, ms in rows:
        tot = sum(ms)
        if zone:
            th = f'<th scope="row">{E(zone)}</th>'
        else:
            note = f' <span class="m">{L("no_island")}</span>' if slug == "canarias" else ""
            th = f'<th scope="row"><a href="{B.BASE}{slug}/">{E(name)}</a>{note}</th>'
        cells = "".join(f'<td class="num">{n}</td>' for n in ms)
        trs.append(f'<tr{" class=sub" if zone else f" id={slug}"}>{th}{cells}<td class="num"><b>{tot}</b></td><td class="num">{tot * 8}</td></tr>')
    tbl = (f'<div class="tscroll"><table class="tbl hub dl"><thead><tr><th scope="col">{B.t("region_label")}</th>{head_m}'
           f'<th scope="col" class="num">{L("col_total")}</th><th scope="col" class="num">{L("col_hours")}</th></tr></thead>'
           f'<tbody>{"".join(trs)}</tbody></table></div>')
    mains = [sum(ms) for slug, _, zone, ms in rows if not zone and slug != "canarias"] + \
            [sum(ms) for slug, _, zone, ms in rows if zone and slug == "canarias"]  # Canarias: with the island's day
    lo, hi = min(mains), max(mains)
    regs = [ms for _, _, zone, ms in rows if not zone]
    mode = [max(sorted({ms[k] for ms in regs}), key=[ms[k] for ms in regs].count) for k in range(12)]  # usual value per month
    nmax, nmin = max(mode), min(mode)
    kmax, kmin = [k for k in range(12) if mode[k] == nmax], [k for k in range(12) if mode[k] == nmin]
    wd = sum(1 for d in B.DAYS if d.weekday() < 5)
    fmt = {"wd": wd, "lo": lo, "hi": hi, "hlo": f"{lo * 8:,}".replace(",", "."), "hhi": f"{hi * 8:,}".replace(",", "."),
           "vlo": f"{(lo - 22) * 8:,}".replace(",", "."), "vhi": f"{(hi - 22) * 8:,}".replace(",", "."),
           "loc": f"{B.BASE}festivos-locales/", "mmax": join([B.T["_months"][k] for k in kmax]).capitalize(), "nmax": nmax,
           "mmin": join([B.T["_months"][k] for k in kmin]), "nmin": nmin}
    qas = [(q.format(**fmt), a.format(**fmt)) for q, a in L("dl_faq")]
    fh, fld = faq(qas)
    h1 = L("dl_h1")
    ch, cld = crumbs(L("dl_crumb"), PATH_DL)
    src = data["source"]
    hero = (f'<div class="hero wrap">{ch}<h1>{E(h1)}</h1><p class="ctx">{E(L("dl_intro"))} '
            f'<a href="{src["url"]}" rel="noopener">{src["id"]}</a></p></div>')
    sec = B.section("comunidades", L("dl_h2"), tbl)
    main = f'{hero}<div class="wrap body">{sec}{B.ad("hub")}<div class="narrow">{fh}</div></div>'
    head = B.head_html(L("dl_title"), L("dl_desc"), PATH_DL, f"{B.SITE}{B.ASSETS}og/espana.png", ld(cld, fld),
                       langs=langs_arg(ONLY_DL))
    write(PATH_DL, B.page(head, "pg", "", main, data, js=False), data["updated"], langs_arg(ONLY_DL))


# ---------------------------------------------------------------- footer and entry point

def footer_links():
    """The 'Utilidades' block of the footer: the pages in this language, or the Spanish ones marked hreflang=es."""
    s = S.get(B.LANG, S["es"])
    items = [(PATH_DL, ONLY_DL, "dl_link"), (PATH_DH, ONLY_DH, "dh_link"), (PATH_WK, ONLY_WK, "wk_link")]
    li = []
    for path, only, key in items:
        if B.LANG in only:
            li.append(f'<li><a href="{B.BASE}{path}">{E(s[key])}</a></li>')
        else:
            li.append(f'<li><a href="{B.ASSETS}{path}" hreflang="es" lang="es">{E(S["es"][key])}</a></li>')
    return f'<h2>{E(s["util"])}</h2><ul>{"".join(li)}</ul>'


def write_pages(data, write, cities):
    if B.LANG in ONLY_WK:
        week_page(data, write)
    if B.LANG in ONLY_DH:
        dh_page(data, write, cities)
    if B.LANG in ONLY_DL:
        dl_page(data, write)
