"""Vacation optimizer pages, Spanish only, called by pages.write_pages:

    /vacaciones-2027/               hub: comunidad picker, days off with 22 and 23 days per comunidad, FAQ
    /vacaciones-2027/<comunidad>/   the optimizer, with the plan for 22 days in the HTML (vac.js recomputes it for
                                    the inputs: days, municipio or island ?m=, blocked months, break length, taken days)

The plan comes from vacopt.py (objective and rules in its docstring); vac.js is the same algorithm in the browser.
Images: og/vacaciones-2027.png and og/vacaciones-2027-<comunidad>.png (og_images(), from build.py without --no-img).
"""
import json
import re

import build as B
import vacopt as V
from build import E

ONLY = ["es"]
PATH = "vacaciones-2027/"
DEF_N = 22
DATA = None
CITIES = []


def ndays(n):
    return "1 día" if n == 1 else f"{n} días"


def region_in(r):
    of = B.ES_OF.get(r["slug"], f'de {r["name"]}')
    return "en " + of[4:] if of.startswith("del ") else "en " + of[3:]


def hol_dicts(slug):
    return B.region_holidays(DATA, slug)


def plan(hols, n=DEF_N):
    return V.optimize(V.off_days([h["date"] for h in hols]), n)


def facts():
    """Per comunidad: plans for 22 and 23 days (no island, no city)."""
    out = []
    for r in DATA["regions"]:
        hols = hol_dicts(r["slug"])
        out.append({"r": r, "hols": hols, "p22": plan(hols, 22), "p23": plan(hols, 23)})
    return out


def ranking(fs):
    return sorted(fs, key=lambda f: (-f["p22"]["total"], -f["p23"]["total"], DATA["regions"].index(f["r"])))


# ---------------------------------------------------------------- html parts (same markup as vac.js)

def take_txt(b):
    t = b["take"]
    return B.drange(t[0], t[-1]) if len(t) > 1 else B.dshort(B.DAYS[t[0]])


def break_row(b, hols):
    return (f'<tr><td class="c-p"><span class="rng">{B.drange(b["s"], b["e"])}</span><span class="m nm">{E(V.break_name(b, hols))}</span></td>'
            f'<td class="num">{ndays(b["len"])}</td><td class="c-v"><span class="mo">{ndays(len(b["take"]))} de vacaciones: </span>'
            f'<b class="dk">{len(b["take"])}</b> <span class="m">{take_txt(b)}</span></td></tr>')


def ranked(p):
    return sorted(p["breaks"], key=lambda b: (-b["len"], b["s"]))


def calendar(hols, p):
    hmap = {}
    for h in hols:
        hmap.setdefault(h["date"], h)
    extra = {}
    for b in p["breaks"]:
        for k in range(b["s"], b["e"] + 1):
            iso = B.DAYS[k].isoformat()
            extra[iso] = (["v"] if k in b["take"] else []) + ["br"]
    html = '<div class="year" id="year">' + "".join(B.month_html(m, hmap, hols) for m in range(1, 13)) + "</div>"

    def sub(mo):
        iso, cls = mo.group(1), (mo.group(3) or "").split()
        add = extra.get(iso)
        if not add:
            return mo.group(0)
        if iso in hmap:
            add = [a for a in add if a != "v"]
        c = " ".join(cls + add)
        tt = '' if iso in hmap or "v" not in add else ' title="Vacaciones"'
        return f'<td data-d="{iso}" class="{c}"{tt}'
    return re.sub(r'<td data-d="(\d{4}-\d\d-\d\d)"( class="([^"]*)")?', sub, html)


def legend(slug):
    kinds = ["n", "r"] + (["i"] if slug == "canarias" else []) + ["l"]
    li = "".join(f'<li>{B.sw(k)}{B.t(B.KINDS[k])}</li>' for k in kinds)
    return (f'<ul class="legend" aria-label="{B.t("legend")}">{li}<li>{B.sw("v")}Vacaciones</li>'
            f'<li id="k-tk" hidden>{B.sw("tk")}Ya cogidos<button type="button" class="lnk" id="tkclear">{B.t("clear")}</button></li></ul>')


def stepper(n=DEF_N):
    return (f'<div class="field"><label for="dn">Días de vacaciones</label><span class="stepper"><button type="button" id="dm" aria-label="{B.t("one_less")}">−</button>'
            f'<input id="dn" type="number" inputmode="numeric" min="1" max="30" value="{n}"><button type="button" id="dp" aria-label="{B.t("one_more")}">+</button></span></div>')


def region_select(current):
    first = "" if current else f'<option value="" selected disabled>{B.t("pick_region")}</option>'
    opts = first + "".join(f'<option value="{x["slug"]}"{" selected" if x["slug"] == current else ""}>{E(x["name"])}</option>' for x in B.REGIONS)
    return f'<div class="field"><label for="vreg">{B.t("region_label")}</label><select id="vreg">{opts}</select></div>'


def zones_of(slug):
    return [[o["slug"], o["name"], o["add"]["date"], o["add"]["name"], o.get("remove")]
            for o in DATA["zones"].get(slug, {}).get("options", []) if "add" in o]


def cities_of(slug):
    return [[x["slug"], x["title_name"], x["zone"], [[h["date"], h["name"]] for h in x["holidays"]], x["c"]["name"]]
            for x in sorted((x for x in CITIES if x["r"]["slug"] == slug), key=lambda x: x["title_name"])]


def mun_select(slug):
    zs, cs = zones_of(slug), cities_of(slug)
    if not zs and not cs:
        return ""
    kind = "isla" if slug == "canarias" else "zona"
    opts = '<option value="">Toda la comunidad</option>' + "".join(f'<option value="{z[0]}">{E(z[1])} ({kind})</option>' for z in zs) \
        + "".join(f'<option value="{c[0]}">{E(c[1])}</option>' for c in cs)
    return f'<div class="field"><label for="vmun">{"Municipio o isla" if zs and slug == "canarias" else B.t("municipio")}</label><select id="vmun">{opts}</select></div>'


def options_html():
    ms = "".join(f'<button type="button" class="btn sm" data-m="{k}" aria-pressed="false">{B.T["_mon3"][k].capitalize()}</button>' for k in range(12))
    mins = "".join(f'<option value="{k}"{" selected" if k == V.MIN_BREAK else ""}>{ndays(k)}</option>' for k in (3, 4, 5, 6, 7, 9))
    maxs = '<option value="0">–</option>' + "".join(f'<option value="{k}">{ndays(k)}</option>' for k in (5, 7, 9, 10, 12, 16, 23, 30))
    return (f'<details class="vopt" id="vopt"><summary>Más opciones{B.CHEV}</summary><div class="vopt-b">'
            f'<div class="field"><span class="flabel" id="lx">No usar en</span><div class="mchips" role="group" aria-labelledby="lx">{ms}</div></div>'
            f'<div class="field"><label for="vmin">Escapada mínima</label><select id="vmin">{mins}</select></div>'
            f'<div class="field"><label for="vmax">Escapada máxima</label><select id="vmax">{maxs}</select></div>'
            f'</div></details>')


def result_html(p, place):
    return (f'<div class="vres"><div class="vres-t"><p class="vhd"><b class="vh-n" id="vtot">{p["total"]}</b><span class="vh-t">días libres</span></p>'
            f'<p class="vh-s" id="vsub">con {ndays(p["used"])} de vacaciones · {E(place)}</p>'
            f'<div class="tools vshare"><button class="btn p" id="sshare" type="button">Compartir</button>'
            f'<a class="btn" id="swa" href="https://wa.me/" target="_blank" rel="noopener">WhatsApp</a>'
            f'<button class="btn" id="sreto" type="button">Reta a un compañero</button>'
            f'<button class="btn" id="slink" type="button">Copiar enlace</button>'
            f'<details class="dd dd-cal"><summary class="btn">Imagen{B.CHEV}</summary><div class="menu menu-cal">'
            f'<a href="#" data-img="1080x1350">Vertical · 1080×1350</a><a href="#" data-img="1200x630">Horizontal · 1200×630</a></div></details>'
            f'</div></div><img class="vcard" id="vcard" width="216" height="270" alt="" hidden></div>')


def rank_table(fs, current=None):
    rows = "".join(f'<tr{" class=on" if f["r"]["slug"] == current else ""}><th scope="row"><a href="{B.BASE}{PATH}{f["r"]["slug"]}/">{E(f["r"]["name"])}</a></th>'
                   f'<td class="num"><b>{f["p22"]["total"]}</b></td><td class="num">{f["p23"]["total"]}</td></tr>' for f in ranking(fs))
    return (f'<table class="tbl vrank"><thead><tr><th scope="col">{B.t("region_label")}</th><th scope="col" class="num">22 días</th>'
            f'<th scope="col" class="num">23 días</th></tr></thead><tbody>{rows}</tbody></table>')


QA_HOW = ("¿Cómo se cuentan los días libres?",
          "Cada escapada entera: tus días de vacaciones más los fines de semana y festivos pegados a ellos. Cuentan las escapadas de 5 días "
          "o más (se cambia en «Más opciones»); un fin de semana suelto no suma.")
QA_NAT = ("¿Y si tengo 30 días naturales?", "30 días naturales equivalen a 22 laborables: el plan de 22 días es el tuyo.")


def vac_script(cfg):
    js = json.dumps(cfg, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<script id="vac-data" type="application/json">{js}</script>\n'
            f'<script src="{B.ASSETS}vac.js?v={B.short_hash(B.ROOT / "vac.js")}"></script>')


def base_cfg():
    return {"base": f"{B.BASE}{PATH}", "site": B.SITE, "host": B.HOST, "wd3": B.T["_wd3"], "mon3": B.T["_mon3"], "wd": B.T["_wd"],
            "k_v": "Vacaciones", "k_tk": "Ya cogido"}


def region_page(f, fs, write):
    r, hols, p, p23 = f["r"], f["hols"], f["p22"], f["p23"]
    slug, name = r["slug"], r["name"]
    path = f"{PATH}{slug}/"
    tot, k = p["total"], len(p["breaks"])
    title = B.pick(60, f"Vacaciones 2027 en {name}: {tot} días libres con 22", f"Vacaciones 2027 {name}: {tot} días libres con 22",
                   f"Vacaciones 2027 {name}: {tot} días libres")
    desc = B.pick(155,
                  f"Días libres 2027 en {name} con 22 días de vacaciones: {tot} seguidos en {k} escapadas, con los puentes, Semana Santa y Navidad. Con 23, {p23['total']}.",
                  f"Días libres 2027 en {name} con 22 días de vacaciones: {tot} seguidos en {k} escapadas. Con 23, {p23['total']}. Plan día a día.")
    h1 = f"Maximiza tus vacaciones 2027 {region_in(r)}"
    crumbs = [(B.t("spain"), ""), ("Vacaciones 2027", PATH), (name, path)]
    pickers = f'<div class="pickers">{region_select(slug)}{mun_select(slug)}{stepper()}</div>'
    hero = f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{pickers}{options_html()}{result_html(p, name)}</div>'
    cal = B.section("calendario", B.t("h_cal"), legend(slug) + calendar(hols, p), "", "cal")
    rows = "".join(break_row(b, hols) for b in ranked(p))
    esc_sec = B.section("escapadas", "Tus escapadas", f'<table class="tbl pts">{pts_head()}<tbody id="blist">{rows}</tbody></table>')
    rank = B.section("comunidades", "Días libres por comunidad", rank_table(fs, slug))
    nc = len(cities_of(slug))
    listing = ", ".join(f'{V.break_name(b, hols)} ({ndays(b["len"])})' for b in p["breaks"])
    qas = [(f"¿Cuántos días libres tengo en 2027 con 22 días de vacaciones {region_in(r)}?",
            f"{tot} días libres seguidos, en {k} escapadas: {E(listing)}. Con 23 días de vacaciones, {p23['total']}."),
           QA_HOW, QA_NAT]
    if nc or slug == "canarias":
        what = "tu isla o tu municipio" if slug == "canarias" else "tu municipio"
        qas.append(("¿Cuenta los festivos de mi ciudad?",
                    f"Sí: elige {what} y el plan suma sus festivos" + (f" ({nc} municipios de {E(name)} con festivos locales publicados)." if nc else ".")))
    import pages
    lds = pages.ld(pages.crumbs_ld(crumbs), pages.faq_ld(qas), app_ld(h1, path, desc))
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}og/vacaciones-2027-{slug}.png", lds, langs=ONLY)
    cfg = {**base_cfg(), "region": slug, "name": name, "hols": [[h["date"], h["name"], h["kind"]] for h in hols],
           "zones": zones_of(slug), "cities": cities_of(slug)}
    main = (f'{hero}<div class="wrap body">{B.ad("vac")}{cal}{esc_sec}{rank}{pages.faq_html(qas)}'
            f'<p class="pfoot">{B.HOST}{B.BASE}{path} · {E(DATA["source"]["boe"])}</p></div>{vac_script(cfg)}')
    write(path, B.page(head, "pg vac", "vac", main, DATA, js=False), DATA["updated"], ONLY)


def pts_head():
    return (f'<thead><tr><th scope="col">Escapada</th><th scope="col" class="num">{B.t("col_free")}</th>'
            f'<th scope="col">{B.t("col_vac")}</th></tr></thead>')


def app_ld(name, path, desc):
    return {"@type": "WebApplication", "name": name, "url": B.URL + path, "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Web", "inLanguage": "es-ES", "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "description": desc}


def summary(fs):
    """'56 en 14 comunidades; 53 en Cataluña y Comunidad Valenciana' parts for the hub."""
    rk = ranking(fs)
    top, low = rk[0]["p22"]["total"], rk[-1]["p22"]["total"]
    tops = [f["r"]["name"] for f in rk if f["p22"]["total"] == top]
    lows = [f["r"]["name"] for f in rk if f["p22"]["total"] == low]
    return top, tops, low, lows


def join(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " y " + names[-1]


def hub_page(fs, write):
    top, tops, low, lows = summary(fs)
    title = "Cómo aprovechar las vacaciones 2027: puentes y días libres"
    desc = (f"Con 22 días de vacaciones, hasta {top} días libres seguidos en 2027. El plan óptimo de puentes y escapadas para tu comunidad y tu ciudad, día a día.")
    h1 = "Maximiza tus vacaciones 2027"
    crumbs = [(B.t("spain"), ""), ("Vacaciones 2027", PATH)]
    ctx = (f'<p class="ctx">Con 22 días de vacaciones: {top} días libres en {len(tops)} comunidades, {low} en {E(join(lows))}.</p>'
           if len(tops) > 3 else f'<p class="ctx">Con 22 días de vacaciones: hasta {top} días libres seguidos.</p>')
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{ctx}'
            f'<div class="pickers">{region_select(None)}{stepper()}</div></div>')
    rank = B.section("comunidades", "Días libres por comunidad", rank_table(fs))
    qas = [("¿Qué comunidad tiene más días libres en 2027?",
            f"Con 22 días de vacaciones, {E(join(tops))} llegan a {top} días libres seguidos; {E(join(lows))}, a {low}. "
            f"Los festivos locales de cada ciudad suman más."),
           QA_HOW, QA_NAT]
    import pages
    lds = pages.ld(pages.crumbs_ld(crumbs), pages.faq_ld(qas), app_ld(h1, PATH, desc))
    head = B.head_html(title, desc, PATH, f"{B.SITE}{B.ASSETS}og/vacaciones-2027.png", lds, langs=ONLY)
    cfg = {**base_cfg(), "hub": True, "regions": [r["slug"] for r in DATA["regions"]]}
    main = f'{hero}<div class="wrap body narrow">{rank}{B.ad("hub")}{pages.faq_html(qas)}</div>{vac_script(cfg)}'
    write(PATH, B.page(head, "pg vac", "vac", main, DATA, js=False), DATA["updated"], ONLY)


def write_pages(data, write, cities):
    global DATA, CITIES
    DATA, CITIES = data, cities
    fs = facts()
    hub_page(fs, write)
    for f in fs:
        region_page(f, fs, write)


# ---------------------------------------------------------------- images

def og(path, line1, big, sub, hols, p):
    """Like build.og_image: wordmark, text on the left, the year on the right with the plan in blue."""
    from PIL import Image, ImageDraw
    W, H, S = 1200, 630, 2
    im = Image.new("RGB", (W * S, H * S), B.BG)
    d = ImageDraw.Draw(im)
    X = 72 * S
    d.rectangle((X, 76 * S, X + 18 * S, 94 * S), fill=B.RED)
    d.text((X + 30 * S, 70 * S), "elcalendariolaboral", font=B.font(26 * S, "b"), fill=B.INK)
    w = d.textlength("elcalendariolaboral", font=B.font(26 * S, "b"))
    d.text((X + 30 * S + w, 70 * S), ".es", font=B.font(26 * S, "r"), fill=B.MUT)
    d.text((X, 150 * S), line1, font=B.font(34 * S, "sb"), fill=B.MUT)
    d.text((X, 196 * S), big, font=B.font(120 * S, "b"), fill=B.INK)
    bw = d.textlength(big, font=B.font(120 * S, "b"))
    d.text((X + bw + 16 * S, 238 * S), "días", font=B.font(36 * S, "b"), fill=B.INK)
    d.text((X + bw + 16 * S, 280 * S), "libres", font=B.font(36 * S, "b"), fill=B.INK)
    size = 30 if len(sub) <= 26 else 24
    d.text((X, 350 * S), sub, font=B.font(size * S, "sb"), fill=B.MUT)
    kind = {h["date"]: h["kind"] for h in hols}
    vac, br = set(), set()
    for b in p["breaks"]:
        br |= set(range(b["s"], b["e"] + 1))
        vac |= set(b["take"])
    COLS = {"n": B.NAT, "r": B.REG, "i": (169, 223, 214), "l": (203, 189, 245)}
    V_, BR = (95, 147, 211), (185, 211, 242)
    x0, y0, c, gx, gy = 700 * S, 58 * S, 17 * S, 30 * S, 22 * S
    import datetime as dt
    for m in range(12):
        col, row = m % 3, m // 3
        ox, oy = x0 + col * (7 * c + gx), y0 + row * (6 * c + gy + 24 * S)
        d.text((ox, oy - 4 * S), B.T["_months"][m][:3].capitalize(), font=B.font(15 * S, "b"), fill=B.INK)
        first = dt.date(B.YEAR, m + 1, 1)
        nd = ((dt.date(B.YEAR + (m == 11), (m + 1) % 12 + 1, 1)) - first).days
        for dd in range(nd):
            day = first + dt.timedelta(dd)
            i = (day - B.DAYS[0]).days
            idx = first.weekday() + dd
            cx, cy = ox + (idx % 7) * c, oy + 24 * S + (idx // 7) * c
            k = kind.get(day.isoformat())
            we = day.weekday() >= 5
            fill_ = V_ if i in vac else COLS[k] if k and not we else BR if i in br else B.WE if we else B.BG
            d.rectangle((cx + S, cy + S, cx + c - S, cy + c - S), fill=fill_, outline=B.LINE)
    im = im.resize((W, H), Image.LANCZOS).quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    im.save(path, optimize=True)


def og_images(data):
    global DATA
    DATA = data
    out = B.ROOT / "og"
    fs = facts()
    top, *_ = summary(fs)
    for f in fs:
        og(out / f"vacaciones-2027-{f['r']['slug']}.png", f"Vacaciones 2027 · {f['r']['name']}", str(f["p22"]["total"]),
           "con 22 días de vacaciones", f["hols"], f["p22"])
    mad = next(f for f in fs if f["r"]["slug"] == "madrid")
    og(out / "vacaciones-2027.png", "Vacaciones 2027", str(top), "con 22 días de vacaciones", mad["hols"], mad["p22"])
