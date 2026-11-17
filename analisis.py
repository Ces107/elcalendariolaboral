"""Editorial analyses computed from our own dataset (Spanish only): /analisis/ and five dated articles.

    /analisis/                                                   hub: the five articles, a summary and their dates
    /analisis/festivos-locales-mas-repetidos-2027/               most repeated local dates and saints, by province
    /analisis/festivos-locales-en-fin-de-semana-2027/            local days on Saturday/Sunday (or on a holiday already)
    /analisis/dias-laborables-2027-por-provincia/                Monday-Friday working days per municipality and province
    /analisis/cuando-publica-cada-provincia-sus-festivos-locales/  bulletin dates 2026 vs 2027 and what is still pending
    /analisis/mejores-puentes-2027-por-comunidad/                best puentes per comunidad and what they cost

Why: original analysis computed from our own data, the one thing a copy of the BOE cannot offer. These pages
are the one thing a copy of the BOE cannot give: findings computed across ~4,000 municipalities.

Rule (as guia.py and festivos.py): every count, date, name and ranking is computed at build time from
data/2027.json, data/2026.json, data/locales-2027-all.json (through muni.catalogue(), the same view the municipality
pages use), data/locales-2026.json, data/municipios.json and data/provincias.json. Nothing is hardcoded but the
publication date, the byline and two legal references (Estatuto de los Trabajadores arts. 37.2 and 38). When the data
is refreshed the text follows; the visible "Actualizado" is the later of the publication date and the data date (never
the build date).

Integration (build.py, Spanish build, after pages.write_pages):
    import analisis
    pages_written += analisis.write(sys.modules[__name__], data, fix)
Standalone (writes analisis/ in the repo, or under --out DIR):
    python analisis.py [--out DIR]
"""
import datetime as dt
import html
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PUBLISHED = "2026-11-17"   # first publication of the six pages; bump nothing here for data refreshes
BYLINE = "Redacción de elcalendariolaboral.es"
HUB = "analisis/"
ET_URL = "https://www.boe.es/buscar/act.php?id=BOE-A-2015-11430"
OG = "og/espana.png"

B = None      # build module
DATA = None   # data/2027.json, localized
OUT = None    # output root (B.OUT unless --out)
_ST = None    # computed facts, shared by the pages, the hub and home_block()

PAGES = [  # (slug, short label for links and cards)
    ("festivos-locales-mas-repetidos-2027", "Los festivos locales más repetidos"),
    ("festivos-locales-en-fin-de-semana-2027", "Festivos locales en fin de semana"),
    ("dias-laborables-2027-por-provincia", "Días laborables por provincia"),
    ("cuando-publica-cada-provincia-sus-festivos-locales", "Cuándo publica cada provincia"),
    ("mejores-puentes-2027-por-comunidad", "Mejores puentes por comunidad"),
]


# ---------------------------------------------------------------- small helpers

def E(s):
    return html.escape(str(s))


def D(iso):
    return dt.date.fromisoformat(iso)


def num(n):
    """Spanish style: 4264, 12.345 (no separator under 10,000)."""
    return f"{n:,}".replace(",", ".") if n >= 10000 else str(n)


def pct(a, b, dec=1):
    if not b:
        return "0 %"
    v = round(100 * a / b, dec)
    s = f"{v:.{dec}f}".replace(".", ",")
    if dec and s.endswith(",0"):
        s = s[:-2]
    return f"{s} %"


def pl(n, one, many):
    return f"{num(n)} {one if n == 1 else many}"


def join(xs):
    xs = [x for x in xs if x]
    if not xs:
        return ""
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


def few(xs, k=5):
    xs = list(xs)
    return join(xs) if len(xs) <= k else f'{", ".join(xs[:k])} y {len(xs) - k} más'


def dm(iso):
    """'8 de septiembre'"""
    return B.dm(iso)


def dl(iso):
    """'miércoles 8 de septiembre'"""
    return B.dlong(iso)


def dy(iso):
    """'22 de septiembre de 2026'"""
    d = D(iso)
    return f"{B.dm(d)} de {d.year}"


def wd(iso):
    return B.T["_wd"][D(iso).weekday()]


def fit_desc(s, limit=155):
    """Meta description within the site's 155 characters (test_data.py): drop trailing sentences, then words."""
    while len(s) > limit and ". " in s.rstrip(". "):
        s = s.rstrip(". ").rsplit(". ", 1)[0] + "."
    return s if len(s) <= limit else s[:limit - 1].rsplit(" ", 1)[0] + "…"


def wd26(iso):
    """Weekday of the same day and month in 2026."""
    return B.T["_wd"][D(iso).replace(year=2026).weekday()]


def tm(iso, txt):
    return f'<time datetime="{iso}">{txt}</time>'


def fold(s):
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def median(xs):
    return statistics.median(xs) if xs else 0


def fmt_med(v):
    return str(int(v)) if float(v).is_integer() else f"{v:.1f}".replace(".", ",")


def mlink(x):
    return f'<a href="{B.BASE}{x["path"]}">{E(x["name"])}</a>'


def plink(p):
    if p["path"]:
        return f'<a href="{B.BASE}{p["path"]}">{E(p["name"])}</a>'
    return f'<a href="{B.BASE}{p["region"]}/">{E(p["name"])}</a>'


def rlink(slug):
    return f'<a href="{B.BASE}{slug}/">{E(REG[slug]["name"])}</a>'


def by_pop(xs):
    return sorted(xs, key=lambda x: (-(x["m"].get("pop") or 0), x["name"]))


def top_name(S, d, share=0.0):
    """'San Isidro (81)': the bulletin name most used for that date, or '' (none, or under `share` of the date's days)."""
    c = S["rep"]["names"].get(d)
    if not c:
        return ""
    n, k = c.most_common(1)[0]
    return f"{E(n)} ({num(k)})" if k >= share * S["rep"]["by_date"][d] else ""


def bull_provs(S):
    """Provinces whose 2027 days come from a bulletin: the per-province tables leave out the 1-7 council pages of a
    province still waiting for its bulletin (a row of 1 municipality is not a province figure)."""
    return {ps for ps, v in S["pub"].items() if v["d27"]}


def saint_dates(S, key):
    for k, v in S["rep"]["saints"]:
        if k == key:
            return v
    return None


def para(*ps):
    return "".join(f"<p>{p}</p>" for p in ps if p)


def guide(*ps):
    return f'<div class="guide">{para(*ps)}</div>'


def table(head, rows, cls="tbl hub"):
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    tr = "".join("<tr>" + "".join((f'<th scope="row">{c}</th>' if k == 0 else f"<td>{c}</td>") for k, c in enumerate(r)) + "</tr>"
                 for r in rows)
    return f'<div class="tscroll"><table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def notes(items):
    return '<ul class="notes">' + "".join(f"<li>{x}</li>" for x in items if x) + "</ul>"


GENERIC = re.compile(r"^(fiestas? locale?s?|festa local|festes locals|festividad local|fiesta|fiestas|jai|jaia|"
                     r"fiestas patronales|fiesta patronal|festes patronals|fiestas mayores)\b")


def named(h):
    """The bulletin's name for the day, or None when it gives only the date or a generic 'Fiesta local'."""
    n = (h.get("name") or "").strip()
    return None if not n or GENERIC.match(fold(n)) else n


# Same saint, different language or wording in the bulletins: merged for the saints table only (the dates table keeps
# every bulletin name as printed). Keys and values are fold()ed.
SAINT_SAME = {
    "san xoan": "san juan", "sant joan": "san juan", "san juan bautista": "san juan", "san joan": "san juan",
    "sant roc": "san roque", "san roquito": "san roque", "san martino": "san martin", "sant marti": "san martin",
    "sant pere": "san pedro", "san pedro y san pablo": "san pedro", "san pedro apostol": "san pedro",
    "sant bartomeu": "san bartolome", "san bartolomeu": "san bartolome", "sant sebastia": "san sebastian",
    "virxe do carme": "virgen del carmen", "el carmen": "virgen del carmen", "nuestra senora del carmen": "virgen del carmen",
    "santiago apostol": "santiago", "sant jaume": "santiago", "martes de entroido": "martes de carnaval",
    "carnaval": "martes de carnaval", "san isidro labrador": "san isidro", "sant isidre": "san isidro",
    "san miguel arcangel": "san miguel", "sant miquel": "san miguel", "san antonio de padua": "san antonio",
    "santa ana": "santa ana", "santa ana y san joaquin": "santa ana", "luns de pascua": "lunes de pascua",
    "andra mari": "natividad de la virgen", "la natividad de la virgen": "natividad de la virgen",
    "natividad de nuestra senora": "natividad de la virgen", "san blas obispo": "san blas", "sant blai": "san blas",
    "santa cruz": "la cruz", "exaltacion de la santa cruz": "la cruz", "la santa cruz": "la cruz", "la vera cruz": "la cruz",
    "san ignacio": "san ignacio de loyola", "san prudencio obispo": "san prudencio",
}
STRIP = re.compile(r"^(festividad|fiesta|festa|dia|romeria|celebracion|fiestas|festes) (de |del |de la |da |do )?")


def saint_key(name):
    k = re.sub(r"\(.*?\)", "", fold(name)).strip()
    k = STRIP.sub("", k).strip()
    k = re.sub(r"^(la|el) (?=(santa cruz|natividad))", "", k)
    return SAINT_SAME.get(k, k)


# ---------------------------------------------------------------- data

REG = {}


def load(name):
    p = ROOT / "data" / name
    return json.loads(p.read_text("utf-8")) if p.exists() else None


def base_hols(region, zone, data=None, cache={}):  # noqa: B006  per-build cache of comunidad (+ island/Arán) holidays
    data = data or DATA
    key = (id(data), region, zone)
    if key not in cache:
        try:
            cache[key] = B.region_holidays(data, region, zone)
        except StopIteration:
            cache[key] = B.region_holidays(data, region)
    return cache[key]


BULLETIN_NO = re.compile(r"\b(núm|nº|n\.º|n°)\.?\s*[\d.]+", re.I)


def is_bulletin(key, s):
    """A single official bulletin issue (not a council web page, not an open-data compilation)."""
    return bool(s and s.get("published") and not key.startswith(("site:", "madrid-councils")) and BULLETIN_NO.search(s.get("title", ""))
                and "open data" not in s.get("title", "").lower())


def bull_label(s):
    import muni
    return muni.short_src(s.get("title", ""), "Boletín oficial")


def compute():
    """Every number the six pages print. Pure function of the data files."""
    import muni
    global _ST
    if _ST is not None:
        return _ST
    cat = muni.catalogue()
    all27 = load("locales-2027-all.json") or {"municipios": {}, "sources": {}, "updated": DATA["updated"]}
    loc26 = load("locales-2026.json") or {"municipios": {}, "sources": {}, "updated": None}
    d26 = load("2026.json")
    provs = {p["slug"]: p for p in cat["provs"]}
    REG.clear()
    REG.update({r["slug"]: r for r in DATA["regions"]})
    ok = [x for x in cat["munis"] if x["ok"]]
    multi = [x for x in ok if len(x["hol27"] or []) > 2]  # parish-by-parish lists (Asturias): no single municipal pair
    use = [x for x in ok if len(x["hol27"] or []) <= 2]
    locs = {k for k, v in all27["municipios"].items() if v.get("localities")}
    for x in use:
        base = base_hols(x["region"], x["zone"])
        bd = {h["date"] for h in base}
        wide, part = muni.wide_and_partial(x["hol27"] or [])
        cls = []
        for h in wide:
            w = D(h["date"]).weekday()
            cls.append("sab" if w == 5 else "dom" if w == 6 else "coin" if h["date"] in bd else "lab")
        x["A"] = {"base": base, "wide": wide, "part": part, "cls": cls, "loc": x["ine"] in locs}
    full = [x for x in use if len(x["A"]["wide"]) == 2]
    for x in full:
        a = x["A"]
        hols = sorted(a["base"] + [{"date": h["date"], "name": h.get("name") or "Fiesta local", "code": 0, "kind": "l"}
                                   for h in a["wide"] if h["date"] not in {b["date"] for b in a["base"]}], key=lambda h: h["date"])
        a["hols"] = hols
        a["lab"] = B.workdays(hols)
        a["blab"] = B.workdays(a["base"])
        a["eff"] = a["blab"] - a["lab"]  # local days that really take a weekday off (0, 1 or 2)
    S = {"cat": cat, "provs": provs, "ok": ok, "multi": multi, "use": use, "full": full, "all27": all27, "loc26": loc26,
         "d26": d26, "upd27": all27.get("updated") or DATA["updated"], "upd26": loc26.get("updated"),
         "n_ine": len(cat["munis"]), "weekdays": sum(1 for d in B.DAYS if d.weekday() < 5)}
    S["pending_regions"] = [r["slug"] for r in DATA["regions"]
                            if not any(x["region"] == r["slug"] and x["status"] == "boletin" for x in ok)]
    _repeated(S)
    _weekend(S)
    _workdays(S)
    _publication(S)
    _bridges(S)
    _ST = S
    return S


def _repeated(S):
    by_date, names = Counter(), defaultdict(Counter)
    prov_dates = defaultdict(Counter)
    prov_n = Counter()
    entries = named_n = 0
    saints = defaultdict(lambda: {"n": 0, "dates": Counter(), "forms": Counter(), "regs": Counter()})
    month = Counter()
    for x in S["use"]:
        if not x["A"]["wide"]:
            continue
        prov_n[x["prov"]["slug"]] += 1
        for h in x["A"]["wide"]:
            entries += 1
            by_date[h["date"]] += 1
            month[D(h["date"]).month] += 1
            prov_dates[x["prov"]["slug"]][h["date"]] += 1
            n = named(h)
            if n:
                named_n += 1
                names[h["date"]][n] += 1
                s = saints[saint_key(n)]
                s["n"] += 1
                s["dates"][h["date"]] += 1
                s["forms"][n] += 1
                s["regs"][(h["date"], x["region"])] += 1
    pairs = Counter(tuple(sorted(h["date"] for h in x["A"]["wide"])) for x in S["full"])
    top = sorted(by_date.items(), key=lambda kv: (-kv[1], kv[0]))
    common = []  # one date in >= 80 % of a province's published municipalities: a province-wide day
    for ps, c in prov_dates.items():
        d, n = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        if prov_n[ps] >= 5 and n / prov_n[ps] >= 0.8:
            common.append((ps, d, n, prov_n[ps]))
    S["rep"] = {"by_date": by_date, "top": top, "names": names, "prov_dates": prov_dates, "prov_n": prov_n, "entries": entries,
                "named": named_n, "saints": sorted(saints.items(), key=lambda kv: (-kv[1]["n"], kv[0])), "month": month,
                "pairs": pairs, "common": sorted(common, key=lambda c: -c[2]),
                "munis": sum(prov_n.values())}


def _weekend(S):
    c = Counter()
    per = defaultdict(lambda: Counter())
    dates = Counter()
    lose = []
    for x in S["use"]:
        a = x["A"]
        if not a["wide"]:
            continue
        p = per[x["prov"]["slug"]]
        p["munis"] += 1
        for h, k in zip(a["wide"], a["cls"]):
            c[k] += 1
            p[k] += 1
            if k in ("sab", "dom"):
                dates[h["date"]] += 1
        lost = sum(1 for k in a["cls"] if k != "lab")
        if lost:
            p["lose"] += 1
            lose.append(x)
        if len(a["wide"]) == 2 and lost == 2:
            p["both"] += 1
    coin = [(x, h) for x in S["use"] for h, k in zip(x["A"]["wide"], x["A"]["cls"]) if k == "coin"]
    # 2026: the same count on the 2026 bulletins (all municipalities that had them), with the 2026 comunidad holidays
    c26, same = Counter(), Counter()
    m26 = 0
    ok27 = {x["ine"]: x for x in S["use"] if x["A"]["wide"]}
    import muni
    d26 = S["d26"]
    for ine, v in (S["loc26"].get("municipios") or {}).items():
        hs = v.get("holidays") or []
        if not hs or len(hs) > 2:
            continue
        m = S["cat"]["by_ine"].get(ine)
        if not m:
            continue
        wide = muni.wide_and_partial(hs)[0]
        if not wide:
            continue
        m26 += 1
        bd = {h["date"] for h in base_hols(m["region"], m["zone"], d26)} if d26 else set()
        lost = 0
        for h in wide:
            w = D(h["date"]).weekday()
            k = "sab" if w == 5 else "dom" if w == 6 else "coin" if h["date"] in bd else "lab"
            c26[k] += 1
            lost += k != "lab"
        c26["lose"] += bool(lost)
        if ine in ok27:
            same["n"] += 1
            same["lose26"] += bool(lost)
            same["lose27"] += any(k != "lab" for k in ok27[ine]["A"]["cls"])
    S["we"] = {"c": c, "per": per, "dates": dates, "lose": lose, "coin": coin, "c26": c26, "m26": m26, "same": same,
               "munis": sum(p["munis"] for p in per.values())}


def _workdays(S):
    per = defaultdict(list)
    for x in S["full"]:
        per[x["prov"]["slug"]].append(x)
    labs = [x["A"]["lab"] for x in S["full"]]
    reg = {}
    for r in DATA["regions"]:
        hols = B.region_holidays(DATA, r["slug"])
        reg[r["slug"]] = B.workdays(hols)  # Canarias: without its island's day (each municipality adds its own)
    eff = Counter(x["A"]["eff"] for x in S["full"])
    S["wd"] = {"per": per, "labs": labs, "dist": Counter(labs), "reg": reg, "eff": eff}


def _publication(S):
    mj = S["cat"]
    ine_prov = {x["ine"]: x["prov"]["slug"] for x in mj["munis"]}
    out = {}

    def scan(dataset, year):
        use = defaultdict(Counter)
        for ine, v in (dataset.get("municipios") or {}).items():
            ps = ine_prov.get(ine)
            if ps and (v.get("holidays") or v.get("localities") or v.get("nucleos")):
                use[ps][v.get("source")] += 1
        res = {}
        srcs = dataset.get("sources") or {}
        for ps, cnt in use.items():
            bulls = [(k, n) for k, n in cnt.most_common() if is_bulletin(k, srcs.get(k))]
            other = [(k, n) for k, n in cnt.most_common() if not is_bulletin(k, srcs.get(k))]
            main = bulls[0][0] if bulls else None
            s = srcs.get(main) if main else (srcs.get(other[0][0]) if other else None)
            res[ps] = {"main": main, "date": srcs[main]["published"] if main else None, "src": s,
                       "n_bull": sum(n for _, n in bulls), "n_other": sum(n for _, n in other),
                       "other_date": (s or {}).get("published") if not main else None,
                       "fixes": bool(main and (srcs[main].get("modifications") or re.search(r"modific|correcci", srcs[main]["title"], re.I)))}
        return res

    p27, p26 = scan(S["all27"], 2027), scan(S["loc26"], 2026)
    for ps, p in S["provs"].items():
        a, b = p27.get(ps), p26.get(ps)
        ok = sum(1 for x in p["munis"] if x["ok"])
        d27 = a["date"] if a else None
        d26 = b["date"] if b else None
        delta = (D(d27) - D(d26).replace(year=D(d26).year + 1)).days if d27 and d26 else None
        out[ps] = {"p": p, "d27": d27, "d26": d26, "delta": delta, "a": a, "b": b, "ok": ok, "all": len(p["munis"]),
                   "council": sum(1 for x in p["munis"] if x["status"] == "ayuntamiento"),
                   "n26": (b or {}).get("n_bull", 0) + (b or {}).get("n_other", 0), "agg26": bool(b and not b["main"])}
    S["pub"] = out


def _bridges(S):
    res = {}
    for r in DATA["regions"]:
        hols = B.region_holidays(DATA, r["slug"])
        pts = B.puentes(hols)
        lw = B.long_weekends(hols)
        ranked = sorted(pts, key=lambda it: (-it["len"] / it["cost"], -it["len"], it["s"]))
        days = set()
        for it in pts:
            days.update(range(it["s"], it["e"] + 1))
        res[r["slug"]] = {"hols": hols, "pts": pts, "lw": lw, "ranked": ranked, "cost": sum(it["cost"] for it in pts),
                          "free": len(days), "own": [h for h in hols if h["kind"] == "r"]}
    isl = {}
    for o in DATA["zones"].get("canarias", {}).get("options", []):
        hols = B.region_holidays(DATA, "canarias", o["slug"])
        pts = B.puentes(hols)
        ranked = sorted(pts, key=lambda it: (-it["len"] / it["cost"], -it["len"], it["s"]))
        isl[o["slug"]] = {"name": o["name"], "add": o.get("add"), "pts": pts, "ranked": ranked}
    # local days: municipalities whose own two days sit inside a puente (a puente the comunidad alone does not give)
    loc = defaultdict(lambda: {"n": 0, "add": 0, "best": None})
    for x in S["full"]:
        a = x["A"]
        g = loc[x["region"]]
        g["n"] += 1
        li = {(D(h["date"]) - B.DAYS[0]).days for h in a["wide"]}
        mine = [it for it in B.puentes(a["hols"]) if any(it["s"] <= i <= it["e"] for i in li)]
        bkeys = {(it["s"], it["e"], it["cost"]) for it in B.puentes(a["base"])}
        mine = [it for it in mine if (it["s"], it["e"], it["cost"]) not in bkeys]
        if mine:
            g["add"] += 1
            top = max(mine, key=lambda it: (it["len"] / it["cost"], it["len"]))
            cur = g["best"]
            k = (top["len"], -top["cost"], x["m"].get("pop") or 0)
            if cur is None or k > cur[0]:
                g["best"] = (k, top, x)
    S["br"] = {"reg": res, "isl": isl, "loc": loc}


# ---------------------------------------------------------------- page frame

def path_of(slug):
    return f"{HUB}{slug}/"


def upd_date(S):
    return max(PUBLISHED, S["upd27"], DATA["updated"])


def byline(S):
    u = upd_date(S)
    return (f'<p class="upd">{E(BYLINE)} · Publicado: {tm(PUBLISHED, B.dmy(PUBLISHED))} · Actualizado: {tm(u, B.dmy(u))}'
            f' · Datos de festivos locales a {tm(S["upd27"], B.dmy(S["upd27"]))}</p>')


def method_box(items):
    return B.section("metodo", "Método y fuentes", notes(items) +
                     f'<p class="m">Cómo trabajamos y cómo avisarnos de un error: <a href="{B.BASE}sobre/">quién hace esta web</a> · '
                     f'<a href="{B.BASE}contacto/">contacto</a>.</p>')


def related(skip):
    li = "".join(f'<li><a href="{B.BASE}{path_of(s)}">{E(n)}</a></li>' for s, n in PAGES if s != skip)
    return B.section("mas-analisis", "Más análisis 2027", f'<ul class="links">{li}</ul>'
                     f'<p class="more-l"><a href="{B.BASE}{HUB}">Todos los análisis</a> · <a href="{B.BASE}festivos-locales/">Festivos locales 2027</a>'
                     f' · <a href="{B.BASE}puentes/">Puentes 2027</a></p>')


def article_ld(S, path, title, desc, based_on):
    u = upd_date(S)
    org = f"{B.SITE}{B.ASSETS}#org"
    return {"@type": "Article", "headline": title[:110], "description": desc, "inLanguage": "es-ES",
            "datePublished": PUBLISHED, "dateModified": u, "mainEntityOfPage": B.URL + path,
            "image": f"{B.SITE}{B.ASSETS}{OG}",
            "author": {"@type": "Organization", "name": BYLINE, "url": f"{B.URL}sobre/"},
            "publisher": {"@type": "Organization", "@id": org, "name": B.t("site_name"), "url": f"{B.SITE}{B.ASSETS}",
                          "logo": {"@type": "ImageObject", "url": f"{B.SITE}{B.ASSETS}icons/icon-512.png"}},
            "isBasedOn": [u for u in based_on if u]}


def render(S, path, title, desc, h1, crumb, lead, sections, based_on, ad_after=1):
    """head first (B.ad reads the page's ADS_PAGE), then one ad slot after the `ad_after`-th section."""
    import pages as P
    crumbs = [("España", ""), ("Análisis", HUB)] + ([(crumb, path)] if path != HUB else [])
    lds = [P.crumbs_ld(crumbs), P.webpage_ld(title, path, upd_date(S))]
    if path != HUB:
        lds.append(article_ld(S, path, title, desc, based_on))
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}{OG}", P.ld(*lds), langs=["es"])
    body = list(sections)
    if ad_after is not None:
        body.insert(min(ad_after, len(body)), B.ad("hub"))
    hero = f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{lead}{byline(S)}</div>'
    main = f'{hero}<div class="wrap body narrow">{"".join(body)}</div>'
    return B.page(head, "pg", "analisis", main, DATA, js=False)  # header_html marks the "Análisis" nav item


# ---------------------------------------------------------------- 1. most repeated local days

def page_repeated(S):
    R = S["rep"]
    slug = PAGES[0][0]
    path = path_of(slug)
    top = R["top"]
    n_m, n_e = R["munis"], R["entries"]
    distinct = len(R["by_date"])
    (d1, c1), (d2, c2), (d3, c3) = top[0], top[1], top[2]
    tie = [d for d, c in top if c == c1]
    top10 = sum(c for _, c in top[:10])

    def nm(d):
        t = top_name(S, d, 0.25)  # a name only when a real share of the bulletins print it
        return f" ({t.rsplit(' (', 1)[0]})" if t else ""

    def provs_of(d):
        return sorted(((ps, c[d]) for ps, c in R["prov_dates"].items() if c.get(d)), key=lambda kv: (-kv[1], kv[0]))

    p1 = provs_of(d1)
    months = sorted(R["month"].items(), key=lambda kv: -kv[1])
    mname = lambda m: B.T["_months"][m - 1]  # noqa: E731
    summer = sum(R["month"].get(m, 0) for m in (6, 7, 8, 9))
    pair, pair_n = R["pairs"].most_common(1)[0] if R["pairs"] else ((), 0)
    in_shared = sum(v for v in R["pairs"].values() if v > 1)
    saints = [(k, v) for k, v in R["saints"] if v["n"] >= 2][:12]
    pend = [REG[s]["name"] for s in S["pending_regions"]]
    pend_prov = [v["p"]["name"] for v in S["pub"].values() if not v["d27"] and v["p"]["region"] not in S["pending_regions"]]

    # San Roque / any saint split across two dates: the biggest such split among the top saints
    split = next(((k, v) for k, v in saints if len(v["dates"]) >= 2 and v["dates"].most_common(2)[1][1] >= 0.2 * v["n"]), None)
    split_txt = ""
    if split:
        k, v = split
        (sa, na), (sb, nb) = v["dates"].most_common(2)
        nm_s = v["forms"].most_common(1)[0][0]
        split_txt = (f'Un mismo santo no siempre cae el mismo día. {E(nm_s)} aparece en {pl(v["n"], "municipio", "municipios")} con nombre, '
                     f'repartido sobre todo entre el {dl(sa)} ({num(na)}) y el {dl(sb)} ({num(nb)}).')
        moved = {s_ for s_ in REG if any(h["date"] == "2027-08-16" for h in B.region_holidays(DATA, s_))}
        if {sa, sb} == {"2027-08-16", "2027-08-17"} and moved:
            n17 = sum(c for (d, rg), c in v["regs"].items() if d == "2027-08-17")
            in_m = sum(c for (d, rg), c in v["regs"].items() if d == "2027-08-17" and rg in moved)
            split_txt += (f' El 15 de agosto de 2027 es domingo y {pl(len(moved), "comunidad pasa", "comunidades pasan")} la Asunción '
                          f'al lunes 16: de los {num(n17)} municipios que celebran {E(nm_s)} el martes 17, {num(in_m)} están en esas '
                          f'comunidades, donde el lunes ya es festivo.')

    common_txt = ""
    if R["common"]:
        cs = [f'{E(S["provs"][ps]["name"])} ({dm(d)}, {num(n)} de {num(t)})' for ps, d, n, t in R["common"]]
        common_txt = (f'Parte del ranking no lo decide cada pueblo por separado. En {join(cs)}, un mismo día aparece en al '
                      f'menos el 80 % de los municipios publicados: es una fiesta de toda la provincia o del territorio histórico, '
                      f'y por eso pesa tanto en la tabla.')

    lead = (f'<p class="lead">El festivo local más repetido de 2027 es el <b>{dl(d1)}</b>{nm(d1)}: lo tienen '
            f'<b>{pl(c1, "municipio", "municipios")}</b> de los {num(n_m)} con fiestas locales ya publicadas. Le siguen el '
            f'{dm(d2)} ({num(c2)}) y el {dm(d3)} ({num(c3)}).</p>')
    intro = guide(
        f'Cada municipio fija dos fiestas locales al año. Para 2027 ya tenemos las de {num(n_m)} de los {num(S["n_ine"])} '
        f'municipios de España, sacadas de los boletines oficiales y, en {pl(sum(1 for x in S["ok"] if x["status"] == "ayuntamiento"), "caso", "casos")}, '
        f'del acuerdo publicado por el propio ayuntamiento. En total son {num(n_e)} días de fiesta local repartidos en '
        f'{pl(distinct, "fecha distinta", "fechas distintas")} del calendario.',
        f'La concentración es alta: las 10 fechas más repetidas suman {num(top10)} de esos {num(n_e)} días '
        f'({pct(top10, n_e)}). El {dm(d1)} encabeza la lista' + (f', empatado con {join(dm(d) for d in tie[1:])}' if len(tie) > 1 else "")
        + f'. Las provincias donde más municipios lo tienen son {join(f"{E(S["provs"][ps]["name"])} ({num(c)})" for ps, c in p1[:3])}.',
        common_txt,
        f'Por meses, {mname(months[0][0])} reúne el {pct(months[0][1], n_e)} de las fiestas locales y {mname(months[1][0])} el '
        f'{pct(months[1][1], n_e)}. De junio a septiembre cae el {pct(summer, n_e)}, y entre noviembre y diciembre solo el '
        f'{pct(R["month"].get(11, 0) + R["month"].get(12, 0), n_e)}: las fiestas patronales siguen el calendario de verano y cosecha.',
    )
    rows = []
    for d, c in top[:15]:
        pr = provs_of(d)
        rows.append([tm(d, dm(d)), wd(d), num(c), pct(c, n_m), top_name(S, d) or "—",
                     f'{E(S["provs"][pr[0][0]]["name"])} ({num(pr[0][1])})' if pr else "—"])
    t1 = B.section("ranking", "Las 15 fechas más repetidas",
                   table(["Fecha", "Día", "Municipios", "% de los publicados", "Nombre más citado (veces)", "Provincia con más"], rows)
                   + '<p class="m">"Nombre más citado": cuántos boletines dan ese nombre al día; el resto lo publica sin nombre, como "Fiesta '
                     'local" o con otro nombre. "—": ningún boletín le da nombre.</p>')
    srow = []
    for k, v in saints:
        d, n = v["dates"].most_common(1)[0]
        fs = v["forms"].most_common(2)
        lbl = E(fs[0][0]) + (f' / {E(fs[1][0])}' if len(fs) > 1 and fold(fs[1][0]) != fold(fs[0][0]) and fs[1][1] >= 0.2 * v["n"] else "")
        srow.append([lbl, num(v["n"]), num(len(v["dates"])), f'{tm(d, dm(d))} ({num(n)})'])
    t2 = B.section("santos", "Los nombres que más se repiten",
                   guide(f'Solo el {pct(R["named"], n_e)} de los días lleva nombre en el boletín; el resto se publica como fecha sin más '
                         f'o como «fiesta local», «fiestas patronales» u otro nombre genérico (esos no los contamos como nombre). Con esa parte, estos son los santos y fiestas más citados. Unimos las formas que '
                         f'nombran lo mismo en otra lengua o con otras palabras (San Xoán y San Juan, Sant Roc y San Roque).',
                         split_txt)
                   + table(["Fiesta", "Municipios", "Fechas distintas", "Fecha más usada"], srow))
    prow = []
    for ps in sorted((p for p in R["prov_n"] if p in bull_provs(S) and R["prov_n"][p] >= 5), key=lambda s: fold(S["provs"][s]["name"])):
        c = R["prov_dates"][ps]
        d, n = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        ties = sum(1 for v in c.values() if v == n)
        prow.append([plink(S["provs"][ps]), num(R["prov_n"][ps]), f'{tm(d, dm(d))}' + (f' <span class="m">(empate ×{ties})</span>' if ties > 1 else ""),
                     f'{num(n)} ({pct(n, R["prov_n"][ps], 0)})', num(len(c))])
    t3 = B.section("provincias", "Por provincia",
                   guide('La fecha más repetida en cada provincia con boletín de 2027, cuántos municipios la tienen y cuántas fechas '
                         'distintas usa la provincia en total. Entran las provincias con boletín y al menos 5 municipios; Ceuta y '
                         'Melilla son un solo municipio, y las provincias sin boletín solo tienen algún acuerdo municipal suelto.')
                   + table(["Provincia", "Municipios", "Fecha más repetida", "La tienen", "Fechas distintas"], prow))
    pair_txt = ""
    if pair_n > 1:
        pair_txt = (f'Las parejas de días también se repiten: {pl(in_shared, "municipio comparte", "municipios comparten")} sus dos '
                    f'fechas exactas con al menos otro municipio. La pareja más común es {dm(pair[0])} y {dm(pair[1])}, '
                    f'en {pl(pair_n, "municipio", "municipios")}.')
    mean = guide(
        f'<b>Qué significa para ti.</b> Si trabajas en un municipio y vives en otro, lo normal es que tus dos días no coincidan: hay '
        f'{num(distinct)} fechas distintas en juego. Mira siempre las fiestas del municipio donde está tu centro de trabajo, que son '
        f'las que cuentan para tu calendario laboral. Y si tu empresa tiene centros en varias provincias, el {dm(d1)} y el {dm(d2)} '
        f'son los días en los que más oficinas cerrarán a la vez.',
        pair_txt,
        f'<b>Límites.</b> El ranking cambia a medida que se publican más boletines. Hoy faltan comunidades enteras '
        f'({few(pend, 6)}) y provincias sueltas de otras ({few(pend_prov, 4)}), así que las fiestas habituales de esas zonas todavía no pesan en el ranking. '
        f'Tampoco contamos los días que solo valen en una pedanía o un núcleo del municipio.' if pend else
        '<b>Límites.</b> Tampoco contamos los días que solo valen en una pedanía o un núcleo del municipio.',
    )
    meth = method_box([
        f'<b>Datos:</b> fiestas locales de 2027 de {num(len(S["ok"]))} municipios con publicación oficial (boletín o acuerdo publicado por el '
        f'ayuntamiento), datos a {dy(S["upd27"])}. Cada municipio enlaza a su boletín en su propia página.',
        f'<b>Qué contamos:</b> los días que valen en todo el término municipal. Los días de una sola parroquia, pedanía o núcleo '
        f'quedan fuera ({pl(sum(1 for x in S["use"] if x["A"]["loc"] or x["A"]["part"]), "municipio tiene", "municipios tienen")} alguno).',
        f'<b>Excluidos:</b> {pl(len(S["multi"]), "municipio", "municipios")} cuyo boletín reparte más de dos días por parroquias, sin una pareja común '
        f'a todo el municipio ({few((E(x["name"]) for x in S["multi"]), 6)}).' if S["multi"] else "",
        '<b>Nombres:</b> tal como los imprime el boletín. Para la tabla de santos unimos las variantes en otras lenguas y las fórmulas '
        '("Festividad de…"); las fechas se cuentan siempre por separado.',
        '<b>Empates:</b> a igual número de municipios, ordenamos por fecha.',
    ])
    title = f"Festivos locales más repetidos de 2027: {dm(d1)} en {num(c1)} municipios"
    desc = (f"El {dm(d1)} es el festivo local más repetido de 2027: {num(c1)} de {num(n_m)} municipios. Le siguen el {dm(d2)} y el "
            f"{dm(d3)}. Fechas, santos y provincias.")
    page = render(S, path, B.pick(60, title, f"Festivos locales más repetidos de 2027: el {dm(d1)}",
                                  "Festivos locales más repetidos de 2027"), fit_desc(desc),
                  "Los festivos locales más repetidos de 2027", "Festivos más repetidos", lead,
                  [B.section("claves", "Lo que dicen los datos", intro), t1, t2, t3,
                   B.section("para-ti", "Qué significa y qué no sabemos", mean), meth, related(slug)],
                  [DATA["source"]["url"]] + sorted({(x["src27"] or {}).get("url") for x in S["ok"] if (x["src27"] or {}).get("url")})[:20])
    summary = f'El {dm(d1)} es el festivo local más repetido de 2027 ({num(c1)} municipios). Fechas, santos y provincias.'
    return path, page, summary, (num(c1), f"municipios con fiesta local el {dm(d1)}")


# ---------------------------------------------------------------- 2. local days on a weekend

def page_weekend(S):
    W = S["we"]
    slug = PAGES[1][0]
    path = path_of(slug)
    c = W["c"]
    n_m = W["munis"]
    days = sum(c.values())
    lost_days = c["sab"] + c["dom"] + c["coin"]
    n_lose = len(W["lose"])
    both = sum(p["both"] for p in W["per"].values())
    c26 = W["c26"]
    days26 = sum(v for k, v in c26.items() if k in ("sab", "dom", "coin", "lab"))
    lost26 = c26["sab"] + c26["dom"] + c26["coin"]
    same = W["same"]
    topd = sorted(W["dates"].items(), key=lambda kv: (-kv[1], kv[0]))[:8]
    nat_sat = [h for h in DATA["holidays"] if h["regions"] == "all" and D(h["date"]).weekday() == 5]
    lead = (f'<p class="lead"><b>{pl(n_lose, "municipio", "municipios")}</b> de los {num(n_m)} con fiestas de 2027 publicadas '
            f'({pct(n_lose, n_m)}) tienen al menos un festivo local en sábado, en domingo o el mismo día que otro festivo. '
            f'Para quien trabaja de lunes a viernes, ese día no suma descanso.</p>')
    def pd(d):
        return f'el {dl(d)} ({num(W["dates"][d])})'

    cw = [(ps, d, n, t) for ps, d, n, t in S["rep"]["common"] if D(d).weekday() >= 5]
    common_we = (f'En {join(E(S["provs"][ps]["name"]) for ps, *_ in cw)}, el {join(sorted({dl(d) for _, d, _, _ in cw}))} es fiesta de todo '
                 f'el territorio, así que lo pierden casi todos sus municipios a la vez.' if cw else
                 'Cuando un día así es fiesta de toda una provincia o territorio, todos sus municipios lo pierden a la vez.')
    # a saint whose usual date falls on a weekend, and where the councils put it instead (named days only)
    isidro_txt = ""
    for k, v in S["rep"]["saints"][:30]:
        d0 = v["dates"].most_common(1)[0][0]
        if v["n"] >= 20 and D(d0).weekday() >= 5 and len(v["dates"]) >= 2:
            ds = v["dates"].most_common(3)
            isidro_txt = (f'Se ve con {E(v["forms"].most_common(1)[0][0])}: de los {num(v["n"])} municipios que lo nombran en el boletín, '
                          + join(f'{num(n)} lo {"dejan" if i == 0 else "ponen"} el {dl(d)}' for i, (d, n) in enumerate(ds)) + '.')
            break
    ex = by_pop(W["lose"])[:8]
    ex_txt = "; ".join(f'{mlink(x)} ({join(dm(h["date"]) + " " + ("en sábado" if k == "sab" else "en domingo" if k == "dom" else "coincide con otro festivo") for h, k in zip(x["A"]["wide"], x["A"]["cls"]) if k != "lab")})' for x in ex)
    intro = guide(
        f'De los {num(days)} días de fiesta local que hemos contado para 2027, {num(c["sab"])} caen en sábado, {num(c["dom"])} en domingo '
        f'y {num(c["coin"])} coinciden con un festivo que ya fija la comunidad o el Estado. En total, {pl(lost_days, "día", "días")} '
        f'({pct(lost_days, days)}) que no añaden un día libre entre semana. En {pl(both, "municipio", "municipios")} pasa con los dos.',
        ('Los sábados pesan mucho más que los domingos. ' if c["sab"] > 3 * c["dom"] else "")
        + f'Las fechas que más arrastran son {join(pd(d) for d, _ in topd[:3])}. ' + common_we,
        'Los ayuntamientos proponen la fecha sabiendo en qué día de la semana cae, y ninguna norma general traslada al lunes un '
        'festivo local que cae en fin de semana. ' + isidro_txt
        + (f' En 2027 también caen en sábado {pl(len(nat_sat), "festivo nacional", "festivos nacionales")}, '
           f'{join(f"{E(h["name"])} ({dm(h["date"])})" for h in nat_sat)}, que tampoco se recuperan.' if nat_sat else ""),
    )
    shift = defaultdict(list)
    for d, _ in topd[:3]:
        shift[(wd26(d), wd(d))].append(dm(d))
    shift_txt = " ".join(f'El {join([ds[0]] + ["el " + x for x in ds[1:]])} {"cayó" if len(ds) == 1 else "cayeron"} en {a} en 2026 y '
                         f'{"cae" if len(ds) == 1 else "caen"} en {b} en 2027.' for (a, b), ds in shift.items()) + " "
    cmp_txt = ""
    if W["m26"]:
        cmp_txt = guide(
            f'<b>Comparación con 2026.</b> Con las fiestas locales de 2026 de {num(W["m26"])} municipios, {num(c26["sab"])} días cayeron en '
            f'sábado, {num(c26["dom"])} en domingo y {num(c26["coin"])} coincidieron con otro festivo: el {pct(lost26, days26)} del total, '
            f'frente al {pct(lost_days, days)} de 2027. ' +
            (f'Mirando solo los {num(same["n"])} municipios que tienen datos de los dos años, los que pierden al menos un día pasan de '
             f'{num(same["lose26"])} en 2026 a {num(same["lose27"])} en 2027.' if same["n"] else ""),
            'La diferencia viene sobre todo del calendario: una fiesta fija en un día del mes avanza un día de la semana de un año a '
            'otro (dos tras un 29 de febrero). ' + shift_txt + 'Por eso los municipios que pierden un día un año suelen recuperarlo al '
            'siguiente.')
    rows = []
    for ps, p in sorted(((k, v) for k, v in W["per"].items() if k in bull_provs(S)),
                        key=lambda kv: (-kv[1]["lose"] / kv[1]["munis"], fold(S["provs"][kv[0]]["name"]))):
        rows.append([plink(S["provs"][ps]), num(p["munis"]), num(p["sab"]), num(p["dom"]), num(p["coin"]),
                     f'{num(p["lose"])} ({pct(p["lose"], p["munis"], 0)})'])
    t1 = B.section("provincias", "Por provincia",
                   guide('Provincias con boletín de 2027, ordenadas por la parte de sus municipios que pierde al menos un festivo local '
                         'entre semana. "En sábado", "En domingo" y "Coinciden" cuentan días, no municipios.')
                   + table(["Provincia", "Municipios", "En sábado", "En domingo", "Coinciden", "Pierden alguno"], rows))
    trow = [[tm(d, dm(d)), wd(d), num(n), top_name(S, d) or "—"] for d, n in topd]
    t2 = B.section("fechas", "Las fechas de fin de semana más repetidas",
                   table(["Fecha", "Día", "Municipios", "Nombre más citado (veces)"], trow)
                   + (f'<p class="m">Ejemplos, de más a menos habitantes: {ex_txt}.</p>' if ex_txt else ""))
    coin_txt = ""
    if W["coin"]:
        cc = Counter(h["date"] for _, h in W["coin"])
        d0, n0 = sorted(cc.items(), key=lambda kv: (-kv[1], kv[0]))[0]
        xs0 = [x for x, h in W["coin"] if h["date"] == d0]
        bname = next((b["name"] for b in xs0[0]["A"]["base"] if b["date"] == d0), "otro festivo")
        regs0 = Counter(x["region"] for x in xs0)
        coin_txt = (f'<b>Días que coinciden.</b> De los {pl(len(W["coin"]), "festivo local que cae", "festivos locales que caen")} sobre otro festivo, '
                    f'{num(n0)} son el {dl(d0)}, que en {join(rlink(r) for r, _ in regs0.most_common())} ya es festivo ({E(bname)}). '
                    f'El boletín publica el día como fiesta local igualmente; para el trabajador no suma un día libre más.'
                    + (f' Los otros {num(len(W["coin"]) - n0)} se reparten en '
                       f'{pl(len(cc) - 1, "fecha", "fechas")}.' if len(W["coin"]) > n0 else ""))
    mean = guide(
        f'<b>Qué significa para ti.</b> Si trabajas de lunes a viernes en uno de estos {num(n_lose)} municipios, en 2027 tendrás un día '
        f'laborable más de lo que parece al leer "dos fiestas locales". Si trabajas los sábados (comercio, hostelería, turnos), ese '
        f'sábado sí es festivo para ti. Tu convenio puede añadir otros días; aquí solo contamos el calendario oficial.',
        coin_txt,
        '<b>Límites.</b> Solo entran municipios con fiestas de 2027 ya publicadas, y solo los días que valen en todo el término '
        'municipal. Los días de una pedanía o un núcleo no cuentan.',
    )
    meth = method_box([
        f'<b>2027:</b> {num(n_m)} municipios con fiestas locales oficiales (boletín o acuerdo publicado por el ayuntamiento), datos a {dy(S["upd27"])}. '
        f'Festivos de comunidad: <a href="{DATA["source"]["url"]}" rel="noopener">{E(DATA["source"]["id"])}</a>.',
        f'<b>2026:</b> fiestas locales oficiales de 2026 de {num(W["m26"])} municipios (data/locales-2026.json, datos a {dy(S["upd26"])}) con los '
        f'festivos de comunidad de 2026 ({E((S["d26"] or {}).get("source", {}).get("id", "BOE"))}).' if W["m26"] else "",
        '<b>"Coincide":</b> el festivo local cae en un día laborable que ya es festivo en la comunidad, o en la isla en Canarias, o en '
        'Arán en Cataluña. Cada municipio se compara con los festivos de su propia isla o zona.',
        f'<b>Excluidos:</b> {pl(len(S["multi"]), "municipio", "municipios")} con días repartidos por parroquias, y los días de una sola pedanía.' if S["multi"] else "",
    ])
    title = f"Festivos locales en fin de semana en 2027: {num(n_lose)} municipios"
    desc = (f"{num(n_lose)} de {num(n_m)} municipios ({pct(n_lose, n_m)}) tienen en 2027 un festivo local en sábado, domingo o sobre otro "
            f"festivo. Por provincia, fechas y comparación con 2026.")
    page = render(S, path, B.pick(60, title, "Festivos locales en fin de semana en 2027"), fit_desc(desc),
                  "Festivos locales que caen en fin de semana en 2027", "Festivos en fin de semana", lead,
                  [B.section("claves", "Lo que dicen los datos", intro + cmp_txt), t1, t2,
                   B.section("para-ti", "Qué significa y qué no sabemos", mean), meth, related(slug)],
                  [DATA["source"]["url"], (S["d26"] or {}).get("source", {}).get("url")])
    summary = (f'{num(n_lose)} municipios ({pct(n_lose, n_m)}) tienen un festivo local en sábado, domingo o sobre otro festivo. '
               f'Por provincia y frente a 2026.')
    return path, page, summary, (num(n_lose), "municipios pierden un festivo local entre semana")


# ---------------------------------------------------------------- 3. working days per province

def page_workdays(S):
    Wd = S["wd"]
    slug = PAGES[2][0]
    path = path_of(slug)
    labs = Wd["labs"]
    n = len(labs)
    lo, hi, med = min(labs), max(labs), median(labs)
    at_lo = [x for x in S["full"] if x["A"]["lab"] == lo]
    at_hi = [x for x in S["full"] if x["A"]["lab"] == hi]
    eff = Wd["eff"]
    reg = Wd["reg"]
    rmin, rmax = min(reg.values()), max(reg.values())
    rlo = [s for s, v in reg.items() if v == rmin]
    rhi = [s for s, v in reg.items() if v == rmax]
    dist = sorted(Wd["dist"].items())
    mode, mode_n = max(Wd["dist"].items(), key=lambda kv: (kv[1], -kv[0]))
    isl = [o for o in DATA["zones"].get("canarias", {}).get("options", []) if "add" in o]
    isl_wk = sum(1 for o in isl if D(o["add"]["date"]).weekday() < 5)
    pmed = {ps: median([x["A"]["lab"] for x in xs]) for ps, xs in Wd["per"].items() if ps in bull_provs(S)}
    top_med = max(pmed.values()) if pmed else 0
    hp = sorted((ps for ps, v in pmed.items() if v == top_med), key=lambda s: fold(S["provs"][s]["name"]))
    cw = {ps for ps, d, *_ in S["rep"]["common"] if D(d).weekday() >= 5}
    high_txt = ""
    if pmed and top_med > med:
        high_txt = (f'Por eso la mediana más alta, {fmt_med(top_med)}, es la de {join(plink(S["provs"][s]) for s in hp)}'
                    + (': allí la fiesta común de todo el territorio cae en sábado.' if hp and set(hp) <= cw else '.'))
    lead = (f'<p class="lead">En 2027, un municipio con sus fiestas locales ya publicadas tiene entre <b>{lo} y {hi} días laborables</b> '
            f'de lunes a viernes. La mediana es {fmt_med(med)} y el valor más común, {mode} ({pl(mode_n, "municipio", "municipios")} de {num(n)}).</p>')
    intro = guide(
        f'2027 tiene {S["weekdays"]} días de lunes a viernes. A eso se le restan los festivos que caen entre semana: los nacionales, '
        f'los de la comunidad y las dos fiestas locales. Hemos hecho la cuenta para los {num(n)} municipios que ya tienen sus dos '
        f'días publicados, con los festivos de su comunidad y, en Canarias, los de su isla.',
        f'La diferencia entre municipios sale de tres cosas. <b>Primera, la comunidad:</b> sin contar fiestas locales, una comunidad '
        f'deja entre {rmin} y {rmax} días laborables ({join(rlink(s) for s in rhi)} {"tiene" if len(rhi) == 1 else "tienen"} {rmax}; '
        + (f'{join(rlink(s) for s in rlo)}, {rmin}' if len(rlo) <= 5 else f'las otras {len(rlo)}, {rmin}') +
        '). Depende de cuántos festivos propios caen entre semana y de si la comunidad pasa al lunes los que caen en domingo, como '
        'el 15 de agosto.' if rmin != rmax else
        f'La diferencia entre municipios sale de tres cosas. <b>Primera, la comunidad:</b> sin contar fiestas locales, todas las '
        f'comunidades dejan {rmin} días laborables en 2027, así que aquí no hay diferencia.',
        f'<b>Segunda, el día de la semana de las fiestas locales:</b> en {pl(eff.get(2, 0), "municipio", "municipios")} '
        f'({pct(eff.get(2, 0), n)}) los dos días caen entre semana y restan dos laborables; en {num(eff.get(1, 0))} solo resta uno, '
        f'y en {num(eff.get(0, 0))} ninguno, porque caen en fin de semana o sobre otro festivo '
        f'(<a href="{B.BASE}{path_of(PAGES[1][0])}">análisis de festivos locales en fin de semana</a>). {high_txt}',
        f'<b>Tercera, Canarias:</b> cada isla tiene su fiesta insular. Canarias deja {reg["canarias"]} días laborables sin ella; en 2027 la '
        f'fiesta de la isla cae entre semana en {num(isl_wk)} de las {num(len(isl))} islas, y en esas islas cada municipio parte de '
        f'{reg["canarias"] - 1} antes de restar sus fiestas locales.' if isl else "",
    )
    caps = [x for x in S["full"] if x["m"].get("capital")]
    cap_c = Counter(x["A"]["lab"] for x in caps)
    cap_hi = by_pop([x for x in caps if x["A"]["lab"] > (mode if cap_c else 0)])
    spread = max((max(x["A"]["lab"] for x in xs) - min(x["A"]["lab"] for x in xs)) for xs in Wd["per"].values()) if Wd["per"] else 0
    cap_we = [x for x in cap_hi if x["A"]["eff"] < 2]
    cap_base = [x for x in cap_hi if x["A"]["eff"] == 2]
    cap_txt = ""
    if caps:
        cap_txt = guide(
            f'<b>Las capitales.</b> De las {num(len(caps))} capitales de provincia con sus dos fiestas publicadas, '
            + join(f'{num(c)} {"tiene" if c == 1 else "tienen"} {v}' for v, c in sorted(cap_c.items())) + '. '
            + (f'Por encima de {mode} quedan {join(f"{mlink(x)} ({x["A"]["lab"]})" for x in cap_hi)}. ' if cap_hi else "")
            + (f'En {join(mlink(x) for x in cap_we)} es porque alguna fiesta local cae en fin de semana o sobre otro festivo. '
               if cap_we else "")
            + (f'En {join(mlink(x) for x in cap_base)} las dos fiestas caen entre semana, pero su comunidad parte de más días '
               f'laborables. ' if cap_base else ""),
            f'<b>Vecinos con cifras distintas.</b> En {pl(sum(1 for xs in Wd["per"].values() if len({x["A"]["lab"] for x in xs}) > 1), "provincia", "provincias")} '
            f'conviven municipios con días laborables distintos. La mayor diferencia dentro de una misma provincia es de '
            f'{pl(spread, "día", "días")}' + (': lo que separa a un municipio con sus dos fiestas entre semana de otro que tiene las dos en '
                                             'fin de semana o sobre otro festivo.' if spread == 2 else '.'))
    rows = []
    for ps, xs in sorted(((k, v) for k, v in Wd["per"].items() if k in bull_provs(S)), key=lambda kv: fold(S["provs"][kv[0]]["name"])):
        ls = [x["A"]["lab"] for x in xs]
        mn, mx = min(ls), max(ls)
        xmn = by_pop([x for x in xs if x["A"]["lab"] == mn])
        xmx = by_pop([x for x in xs if x["A"]["lab"] == mx])
        bl = sorted({x["A"]["blab"] for x in xs})
        rows.append([plink(S["provs"][ps]), num(len(xs)), "–".join(map(str, (bl[0], bl[-1]))) if len(bl) > 1 else str(bl[0]),
                     fmt_med(median(ls)), f'{mn} <span class="m">{mlink(xmn[0])}{" y " + pl(len(xmn) - 1, "más", "más") if len(xmn) > 1 else ""}</span>',
                     f'{mx} <span class="m">{mlink(xmx[0])}{" y " + pl(len(xmx) - 1, "más", "más") if len(xmx) > 1 else ""}</span>'])
    t1 = B.section("provincias", "Días laborables 2027 por provincia",
                   guide('Provincias con boletín de 2027. Base: días laborables de la comunidad (y de la isla en Canarias) sin fiestas '
                         'locales. En mínimo y máximo, el municipio más poblado de los que empatan y cuántos más tienen esa cifra.')
                   + table(["Provincia", "Municipios", "Base sin locales", "Mediana", "Mínimo", "Máximo"], rows))
    drow = [[str(v), num(c), pct(c, n)] for v, c in dist]
    t2 = B.section("distribucion", "Cuántos municipios hay en cada cifra",
                   table(["Días laborables", "Municipios", "%"], drow)
                   + guide(f'Con {lo} días: {few((mlink(x) for x in by_pop(at_lo)), 5)}. '
                           f'Con {hi}: {few((mlink(x) for x in by_pop(at_hi)), 5)}.'))
    rrow = [[rlink(r["slug"]), str(reg[r["slug"]]) + (" (sin la fiesta de la isla)" if r["slug"] == "canarias" else "")]
            for r in sorted(DATA["regions"], key=lambda r: (-reg[r["slug"]], fold(r["name"])))]
    t3 = B.section("comunidades", "La base de cada comunidad",
                   guide('Días laborables de lunes a viernes con los festivos nacionales y de comunidad, antes de restar las fiestas '
                         'locales. Es el punto de partida de cada municipio.')
                   + table(["Comunidad", "Días laborables sin locales"], rrow))
    mean = guide(
        '<b>Qué significa para ti.</b> Si tu jornada se calcula por días laborables (horas anuales, cuadrantes, plazos de vacaciones '
        'en días hábiles), dos municipios vecinos pueden tener uno o dos días de diferencia. Para tu cuenta exacta, abre la página de '
        'tu municipio: muestra sus días laborables con sus dos fiestas. Si tu convenio fija 22 días laborables de vacaciones, '
        'restan sobre esta cifra.',
        '<b>Límites.</b> Contamos días de lunes a viernes; no restamos vacaciones, días de convenio ni puentes que conceda la empresa. '
        'Los municipios con fiestas de 2027 aún sin publicar no entran, así que la mediana de una provincia con pocos municipios '
        'publicados puede moverse.' + (f' Faltan, entre otras, {few([REG[s]["name"] for s in S["pending_regions"]], 6)}.' if S["pending_regions"] else ""),
    )
    nloc = sum(1 for x in S["full"] if x["A"]["loc"])
    meth = method_box([
        f'<b>Fórmula:</b> días de lunes a viernes de 2027 ({S["weekdays"]}) menos los festivos nacionales, de comunidad, de isla o zona y '
        f'locales que caen en lunes a viernes. Un festivo local que coincide con otro festivo no resta dos veces.',
        f'<b>Datos:</b> {num(n)} municipios con sus dos fiestas locales de 2027 publicadas (datos a {dy(S["upd27"])}); festivos de comunidad del '
        f'<a href="{DATA["source"]["url"]}" rel="noopener">{E(DATA["source"]["id"])}</a>.',
        f'<b>Núcleos:</b> en {pl(nloc, "municipio", "municipios")} el boletín da otros días para alguna pedanía o núcleo; usamos los días del '
        f'municipio, que son los del núcleo principal.' if nloc else "",
        f'<b>Excluidos:</b> los municipios con un solo día común publicado o con días repartidos por parroquias '
        f'({num(len(S["ok"]) - n)} en total).',
        '<b>Mediana:</b> el valor central de los municipios de la provincia; con un número par de municipios, la media de los dos centrales.',
    ])
    title = f"Días laborables 2027 por provincia: de {lo} a {hi} según el municipio"
    desc = (f"Días laborables de 2027 en {num(n)} municipios: entre {lo} y {hi}, mediana {fmt_med(med)}. Por provincia, con la base de "
            f"cada comunidad y por qué cambia.")
    page = render(S, path, B.pick(60, title, f"Días laborables 2027 por provincia: de {lo} a {hi}", "Días laborables 2027 por provincia"), fit_desc(desc),
                  "Días laborables 2027 por provincia", "Días laborables por provincia", lead,
                  [B.section("claves", "Lo que dicen los datos", intro + cap_txt), t1, t2, t3,
                   B.section("para-ti", "Qué significa y qué no sabemos", mean), meth, related(slug)],
                  [DATA["source"]["url"]])
    summary = f'Entre {lo} y {hi} días laborables según el municipio (mediana {fmt_med(med)}). Por provincia y por qué cambia.'
    return path, page, summary, (f"{lo}–{hi}", "días laborables según el municipio")


# ---------------------------------------------------------------- 4. when each province publishes

def page_publication(S):
    Pb = S["pub"]
    slug = PAGES[3][0]
    path = path_of(slug)
    rows_all = [v for v in Pb.values()]
    with27 = [v for v in rows_all if v["d27"]]
    pending = sorted([v for v in rows_all if not v["d27"]], key=lambda v: (v["d26"] or "9999", fold(v["p"]["name"])))
    first = min(with27, key=lambda v: (v["d27"], fold(v["p"]["name"])))
    last = max(with27, key=lambda v: (v["d27"], fold(v["p"]["name"])))
    firsts = [v for v in with27 if v["d27"] == first["d27"]]
    lasts = [v for v in with27 if v["d27"] == last["d27"]]
    cmp_ = [v for v in with27 if v["delta"] is not None and not v["agg26"]]
    earlier = [v for v in cmp_ if v["delta"] < -7]
    later = [v for v in cmp_ if v["delta"] > 7]
    similar = [v for v in cmp_ if -7 <= v["delta"] <= 7]
    partial = [v for v in with27 if v["ok"] < v["all"]]
    fixes26 = [v for v in rows_all if v["b"] and v["b"]["fixes"]]
    sep30 = sum(1 for v in with27 if v["d27"] <= "2026-09-30")
    ok_total = sum(v["ok"] for v in rows_all)
    all_total = sum(v["all"] for v in rows_all)
    pend_munis = sum(v["all"] - v["ok"] for v in pending)

    def pn(v):
        return E(v["p"]["name"])

    lead = (f'<p class="lead">A {dy(S["upd27"])}, <b>{pl(len(with27), "provincia tiene", "provincias tienen")}</b> sus fiestas locales de 2027 '
            f'en un boletín oficial y <b>{num(len(pending))} siguen pendientes</b>. La primera fue {join(pn(v) for v in firsts)} '
            f'({dy(first["d27"])}); la última hasta ahora, {join(pn(v) for v in lasts)} ({dy(last["d27"])}).</p>')
    def grp(xs, key):
        xs = sorted(xs, key=key)
        return f' ({few((pn(v) for v in xs), 4)})' if xs else ""

    by_reg = defaultdict(list)
    for v in with27:
        by_reg[v["p"]["region"]].append(v)
    multi = {r: vs for r, vs in by_reg.items() if len(vs) > 1}
    one_day = sorted((r for r, vs in multi.items() if len({v["d27"] for v in vs}) == 1), key=lambda r: fold(REG[r]["name"]))
    spread = sorted(((r, min(vs, key=lambda v: v["d27"]), max(vs, key=lambda v: v["d27"])) for r, vs in multi.items()
                     if len({v["d27"] for v in vs}) > 1), key=lambda t: -(D(t[2]["d27"]) - D(t[1]["d27"])).days)
    reg_txt = ""
    if one_day:
        reg_txt += (f'En {join(rlink(r) for r in one_day)}, todas las provincias salen el mismo día porque hay un solo boletín para la '
                    f'comunidad. ')
    if spread:
        reg_txt += (f'En cambio, en {join(rlink(r) for r, _, _ in spread)} cada provincia publica por su cuenta: ' + "; ".join(
            f'{E(REG[r]["name"])} fue del {dm(a["d27"])} ({pn(a)}) al {dm(b["d27"])} ({pn(b)}), '
            f'{pl((D(b["d27"]) - D(a["d27"])).days, "día", "días")} de diferencia' for r, a, b in spread) + '.')
    intro = guide(
        f'Las fiestas locales no salen en el BOE. Las determina la autoridad laboral de cada comunidad a propuesta del pleno de cada '
        f'ayuntamiento, y se publican en el boletín de la comunidad o en el de la provincia, cada uno con su calendario. Hemos anotado '
        f'la fecha del boletín de cada provincia en 2026 y en 2027. Hoy tenemos fiestas de 2027 para {num(ok_total)} de los '
        f'{num(all_total)} municipios ({pct(ok_total, all_total)}).',
        f'Antes del 1 de octubre de 2026 ya habían publicado {pl(sep30, "provincia", "provincias")}. ' +
        (f'Frente al año anterior, {pl(len(earlier), "provincia", "provincias")} {"ha" if len(earlier) == 1 else "han"} publicado más de '
         f'una semana antes{grp(earlier, lambda v: v["delta"])}, {num(len(later))} más de una semana después{grp(later, lambda v: -v["delta"])} '
         f'y {num(len(similar))} con menos de una semana de diferencia.' if cmp_ else ""),
        reg_txt,
    )
    pend_txt = ""
    if pending:
        items = [f'{plink(v["p"])}: ' + (f'en 2026 salió el {dy(v["d26"])}' if v["d26"] and not v["agg26"] else
                                         "las fiestas de 2026 están en datos abiertos, sin fecha de boletín" if v["agg26"] else
                                         "sin fiestas de 2026 en nuestros datos") +
                 (f'; {pl(v["council"], "ayuntamiento ya ha publicado", "ayuntamientos ya han publicado")} su acuerdo' if v["council"] else "")
                 for v in pending]
        pend_txt = B.section("pendientes", f'Las {num(len(pending))} provincias pendientes',
                             guide(f'Suman {num(pend_munis)} municipios sin fiestas de 2027 oficiales en nuestros datos. Las ordenamos por la fecha '
                                   f'en que publicaron el año pasado: es una pista de cuándo pueden salir, no una previsión. Mientras tanto, '
                                   f'cada municipio muestra sus fiestas de 2026 como referencia y lo indica.')
                             + notes(items))
    rows = []
    for v in sorted(rows_all, key=lambda v: (v["d27"] or "9999", fold(v["p"]["name"]))):
        a = v["a"] or {}
        lab27 = f'{tm(v["d27"], B.dmy(v["d27"]))} <span class="m">{E(bull_label(a["src"]))}</span>' if v["d27"] else "pendiente"
        lab26 = (f'{tm(v["d26"], B.dmy(v["d26"]))}' + (' <span class="m">(datos abiertos)</span>' if v["agg26"] else "")) if v["d26"] else (
            f'{B.dmy(v["b"]["other_date"])} <span class="m">(datos abiertos)</span>' if v["b"] and v["b"].get("other_date") else "—")
        dlt = "—" if v["delta"] is None or v["agg26"] else ("igual" if v["delta"] == 0 else f'{"+" if v["delta"] > 0 else "−"}{abs(v["delta"])} días')
        rows.append([plink(v["p"]), E(REG[v["p"]["region"]]["name"]), lab27, lab26, dlt, f'{num(v["ok"])} de {num(v["all"])}'])
    t1 = B.section("tabla", "Fecha de publicación por provincia",
                   guide('Ordenadas por la fecha del boletín de 2027. "Diferencia" compara el día del año: +10 días es que en 2027 salió diez días '
                         'más tarde que en 2026.')
                   + table(["Provincia", "Comunidad", "Boletín 2027", "Boletín 2026", "Diferencia", "Municipios 2027"], rows))
    part_txt = ""
    if partial:
        ps = sorted(partial, key=lambda v: v["ok"] / v["all"])
        part_txt = (f'Publicar no siempre es publicarlo todo. En {pl(len(partial), "provincia", "provincias")} con boletín, alguno de sus municipios '
                    f'aún no tiene días de 2027 en nuestros datos; los casos con más hueco son '
                    f'{few((f"{pn(v)} ({num(v["ok"])} de {num(v["all"])})" for v in ps), 4)}. O el boletín no da días para esos '
                    f'municipios, o nuestra lectura aún no los recoge; mientras tanto sus páginas siguen como pendientes y muestran 2026 '
                    f'como referencia.')
    mean = guide(
        '<b>Qué significa para ti.</b> Si tu provincia está pendiente, no planifiques con las fechas de otro año ni con lo que adelante '
        'la prensa: el día cuenta cuando sale en el boletín. Cada página de municipio se actualiza cuando entra su publicación.',
        part_txt,
        (f'<b>Las fechas se corrigen.</b> {pl(len(fixes26), "provincia tuvo", "provincias tuvieron")} correcciones o modificaciones de '
         f'su boletín de 2026 después de la primera publicación ({few((pn(v) for v in sorted(fixes26, key=lambda v: fold(v["p"]["name"]))), 6)}). '
         f'Por eso cada municipio enlaza a su fuente y anotamos la fecha de comprobación.') if fixes26 else "",
    )
    agg = [v for v in rows_all if v["agg26"]]
    no26 = sorted((v for v in rows_all if not v["b"]), key=lambda v: fold(v["p"]["name"]))
    meth = method_box([
        f'<b>2027:</b> fecha del boletín oficial del que salen las fiestas de cada provincia (data/locales-2027-all.json, datos a {dy(S["upd27"])}). '
        f'Si una provincia tiene más de un boletín, usamos el que da los días a más municipios.',
        '<b>2026:</b> la misma fecha para las fiestas de 2026 (data/locales-2026.json). Es la primera publicación; las correcciones '
        'posteriores no cambian la fecha.',
        (f'<b>Sin comparación:</b> en {few((pn(v) for v in agg), 4)} las fiestas de 2026 salen de un conjunto de datos abiertos, '
         f'no de un boletín con fecha, así que no calculamos la diferencia.') if agg else "",
        (f'<b>Sin datos de 2026:</b> {few((pn(v) for v in no26), 4)}; aparece con "—".') if no26 else "",
        '<b>Pendiente:</b> ninguna fiesta de 2027 de la provincia en un boletín. Los acuerdos de pleno publicados por un ayuntamiento '
        'cuentan para su municipio, no para la provincia.',
        '<b>Esta lista cambia</b> cada vez que entra un boletín nuevo: la fecha de "Actualizado" lo indica.',
    ])
    title = f"Cuándo publica cada provincia sus festivos locales: {num(len(pending))} pendientes"
    desc = (f"Fecha del boletín de festivos locales de 2027 en cada provincia frente a 2026: {num(len(with27))} publicadas y "
            f"{num(len(pending))} pendientes a {B.dmy(S['upd27'])}.")
    srcs = sorted({(v["a"]["src"] or {}).get("url") for v in with27 if v["a"] and v["a"]["src"]} - {None, ""})
    page = render(S, path, B.pick(60, title, f"Festivos locales 2027: {num(len(pending))} provincias aún sin publicar",
                                  "Cuándo publica cada provincia sus festivos locales"), fit_desc(desc),
                  "Cuándo publica cada provincia sus festivos locales", "Fechas de publicación", lead,
                  [B.section("claves", "Lo que dicen los datos", intro), t1, pend_txt,
                   B.section("para-ti", "Qué significa y qué no sabemos", mean), meth, related(slug)],
                  srcs[:20])
    summary = (f'{num(len(with27))} provincias ya tienen boletín de 2027 y {num(len(pending))} siguen pendientes. Fechas de 2026 y 2027 '
               f'por provincia.')
    return path, page, summary, (num(len(pending)), "provincias aún sin festivos locales de 2027")


# ---------------------------------------------------------------- 5. best puentes per comunidad

def page_bridges(S):
    Br = S["br"]
    slug = PAGES[4][0]
    path = path_of(slug)
    reg = Br["reg"]
    nat = [h for h in B.region_holidays(DATA, "madrid") if h["kind"] == "n"]
    npts = B.puentes(nat)
    nbest = sorted(npts, key=lambda it: (-it["len"] / it["cost"], -it["len"], it["s"]))[0] if npts else None
    counts = {s: len(v["pts"]) for s, v in reg.items()}
    most = max(counts.values())
    least = min(counts.values())
    smost = [s for s, c in counts.items() if c == most]
    sleast = [s for s, c in counts.items() if c == least]
    def score(it):
        return (it["len"] / it["cost"], it["len"])

    def key(it):
        return (it["s"], it["e"], it["cost"])

    tops = {s: [it for it in v["ranked"] if score(it) == score(v["ranked"][0])] for s, v in reg.items() if v["ranked"]}
    nkey = key(nbest) if nbest else None
    nkeys = {key(it) for it in npts}
    with_nat = [s for s, ts in tops.items() if nkey in {key(it) for it in ts}]
    own_best = {s: [it for it in ts if key(it) not in nkeys] for s, ts in tops.items()}
    own_best = {s: ts for s, ts in own_best.items() if ts}
    costs = sorted(((v["cost"], v["free"], s) for s, v in reg.items()), key=lambda t: (t[0], fold(REG[t[2]]["name"])))
    loc = Br["loc"]
    live = [r for r in loc if r not in S["pending_regions"]]
    tot_n = sum(loc[r]["n"] for r in live)
    tot_add = sum(loc[r]["add"] for r in live)

    def rng(it):
        return B.drange(it["s"], it["e"])

    def brk(it):
        return f'{rng(it)}: {it["len"]} días libres pidiendo {pl(it["cost"], "día", "días")} ({B.dlist(it["take"])})'

    def short(it):
        return f'{rng(it)}, {it["len"]} días por {pl(it["cost"], "día", "días")}'

    own_txt = ""
    if own_best:
        own_txt = (' ' + "; ".join(f'{rlink(s)} tiene uno propio que rinde lo mismo o más: {short(ts[0])}' for s, ts in
                                   sorted(own_best.items(), key=lambda kv: fold(REG[kv[0]]["name"]))) + '.')
    lo_c, hi_c = costs[0], costs[-1]

    lead = (f'<p class="lead">Con los festivos nacionales, el puente más rentable de 2027 es <b>{brk(nbest)}</b>. Cada comunidad añade los '
            f'suyos: de {least} a {most} puentes según dónde trabajes.</p>') if nbest else ""
    intro = guide(
        'Un puente, en estas cuentas, es un día laborable suelto (o dos) entre un festivo y el fin de semana: pides esos días y '
        'enlazas varios días libres seguidos. Medimos cada puente por su rendimiento: días libres que consigues por cada día de '
        'vacaciones que gastas. Lo hemos calculado con los festivos nacionales y de comunidad del BOE para las 19 comunidades.',
        f'{join(rlink(s) for s in smost)} {"es la comunidad" if len(smost) == 1 else "son las comunidades"} con más puentes ({most}); '
        + (f'{join(rlink(s) for s in sleast)}, {"la que menos" if len(sleast) == 1 else "las que menos"} ({least}).' if len(sleast) <= 4
           else f'{len(sleast)} comunidades se quedan en {least}.')
        + ((f' El puente nacional de {rng(nbest)} es el mejor, o empata con el mejor, en todas las comunidades.' if len(with_nat) == len(reg)
            else f' El puente nacional de {rng(nbest)} es el mejor, o empata con el mejor, en {num(len(with_nat))} de las '
                 f'{num(len(reg))} comunidades.') if nbest else "") + own_txt,
        f'Hacerlos todos tiene un coste. En la tabla, "Todos" suma los días de vacaciones que pedirías para hacer cada puente de tu '
        f'comunidad y los días libres que te darían en total, fines de semana incluidos: desde {lo_c[0]} días de vacaciones para '
        f'{lo_c[1]} días libres ({few((rlink(s) for c_, f_, s in costs if (c_, f_) == lo_c[:2]), 2)}) hasta {hi_c[0]} para {hi_c[1]} '
        f'({few((rlink(s) for c_, f_, s in costs if (c_, f_) == hi_c[:2]), 2)}). Es un buen punto de partida para '
        f'repartir los 30 días naturales de vacaciones que garantiza el <a href="{ET_URL}#a38" rel="noopener">artículo 38 del '
        f'Estatuto de los Trabajadores</a>.',
    )
    rows = []
    for r in DATA["regions"]:
        v = reg[r["slug"]]
        if not v["ranked"]:
            rows.append([rlink(r["slug"]), "0", "—", "—", "—"])
            continue
        b1 = v["ranked"][0]
        b2 = v["ranked"][1] if len(v["ranked"]) > 1 else None
        nt = len(tops[r["slug"]])

        def cell(it, tie=""):
            return f'{rng(it)} <span class="m">{it["len"]} días · pides {B.dlist(it["take"])}{tie}</span>'
        rows.append([rlink(r["slug"]), str(len(v["pts"])), cell(b1, " · empate" if nt > 1 else ""),
                     cell(b2, " · empate" if nt > 1 else "") if b2 else "—", f'{v["cost"]} → {v["free"]}'])
    t1 = B.section("tabla", "El mejor puente de cada comunidad",
                   guide('Ordenados por días libres por día de vacaciones; a igual rendimiento, el más largo, y si siguen empatados, el '
                         'primero del año ("empate"). "Todos": días de vacaciones → días libres en total si haces todos los puentes '
                         'de la comunidad.')
                   + table(["Comunidad", "Puentes", "El mejor", "El segundo", "Todos"], rows))
    isl_txt = ""
    if Br["isl"]:
        items = []
        for k, v in sorted(Br["isl"].items(), key=lambda kv: fold(kv[1]["name"])):
            base_keys = {(it["s"], it["e"], it["cost"]) for it in reg["canarias"]["pts"]}
            own = [it for it in v["ranked"] if (it["s"], it["e"], it["cost"]) not in base_keys]
            a = v["add"]
            items.append(f'<b>{E(v["name"])}</b> ({E(a["name"])}, {dl(a["date"])}): ' +
                         (f'añade {brk(own[0])}' if own else "no añade ningún puente a los de Canarias"))
        isl_txt = B.section("canarias", "Canarias: la fiesta de cada isla", notes(items))
    loc_rows = []
    for r in DATA["regions"]:
        g = loc.get(r["slug"])
        if not g or not g["n"] or r["slug"] not in live:
            continue
        b = g["best"]
        loc_rows.append([rlink(r["slug"]), num(g["n"]), f'{num(g["add"])} ({pct(g["add"], g["n"], 0)})',
                         f'{mlink(b[2])} <span class="m">{rng(b[1])}, {b[1]["len"]} días pidiendo {b[1]["cost"]}</span>' if b else "—"])
    t2 = B.section("locales", "Lo que añaden las fiestas locales",
                   guide(f'Los dos días locales cambian el mapa. De los {num(tot_n)} municipios con sus dos fiestas de 2027 publicadas '
                         f'en comunidades con boletín, {num(tot_add)} ({pct(tot_add, tot_n)}) consiguen al menos un puente que su comunidad '
                         f'sola no da (un puente cuenta como nuevo si incluye alguno de sus días locales y no coincide en fechas y '
                         f'días de vacaciones con ninguno de los de la comunidad). En la última columna, el puente más largo que da un festivo local en cada comunidad (a igualdad, el '
                         f'municipio más poblado).')
                   + table(["Comunidad", "Municipios publicados", "Con un puente local", "El más largo gracias a un festivo local"], loc_rows))
    mean = guide(
        f'<b>Qué significa para ti.</b> Empieza por el mejor puente de tu comunidad y suma después los de tus dos fiestas locales, que '
        f'están en la página de tu municipio. El <a href="{B.BASE}vacaciones-2027/">planificador de vacaciones 2027</a> hace la cuenta '
        f'con tus días concretos y te dice cuántos días seguidos sacas con los que tienes.',
        '<b>Límites.</b> Solo contamos puentes de uno o dos días de vacaciones; las semanas enteras (Semana Santa, Navidad) son otra '
        'cuenta. Tu convenio puede tener días libres propios, y en algunas empresas el puente lo da la empresa sin gastar vacaciones. '
        'Las fiestas locales de municipios aún sin publicar no entran.',
    )
    meth = method_box([
        f'<b>Datos:</b> festivos nacionales y de comunidad de 2027 del <a href="{DATA["source"]["url"]}" rel="noopener">{E(DATA["source"]["id"])}</a> '
        f'({E(DATA["source"]["boe"])}); fiestas de cada isla del decreto canario recogido en el mismo conjunto de datos; fiestas locales de '
        f'{num(tot_n)} municipios (datos a {dy(S["upd27"])}).',
        '<b>Puente:</b> uno o dos días laborables entre un festivo y el fin de semana (o entre dos festivos). Los fines de semana largos '
        'sin pedir nada no cuentan como puente. La misma regla usa la tabla de puentes de cada página.',
        '<b>Rendimiento:</b> días libres seguidos divididos por días de vacaciones pedidos. A igualdad, el más largo y después el '
        'primero del año.',
        '<b>Canarias</b> se calcula sin la fiesta de la isla en la tabla principal y con ella en su apartado. En Cataluña, Arán cambia '
        'un festivo y sus puentes pueden variar.',
    ])
    title = "Mejores puentes de 2027 por comunidad y cuántas vacaciones cuestan"
    desc = (f"El mejor puente de cada comunidad en 2027, cuántos días de vacaciones cuesta y qué añaden las fiestas locales: "
            f"de {least} a {most} puentes según la comunidad.")
    page = render(S, path, B.pick(60, title, "Mejores puentes 2027 por comunidad y lo que cuestan", "Mejores puentes de 2027 por comunidad"), fit_desc(desc),
                  "Los mejores puentes de 2027 por comunidad", "Mejores puentes", lead,
                  [B.section("claves", "Lo que dicen los datos", intro), t1, isl_txt, t2,
                   B.section("para-ti", "Qué significa y qué no sabemos", mean), meth, related(slug)],
                  [DATA["source"]["url"]])
    summary = (f'El mejor puente de cada comunidad, lo que cuesta en vacaciones y qué añaden las fiestas locales. '
               f'De {least} a {most} puentes.')
    return path, page, summary, (f"{least}–{most}", "puentes según la comunidad")


# ---------------------------------------------------------------- hub

def page_hub(S, items):
    path = HUB
    u = upd_date(S)
    li = "".join(f'<li><h3 class="h3"><a href="{B.BASE}{p}">{E(lbl)}</a></h3><p class="m">{E(B.dmy(PUBLISHED))} · actualizado '
                 f'{E(B.dmy(u))}</p><p>{summ}</p></li>' for p, lbl, summ in items)
    pend = [REG[s]["name"] for s in S["pending_regions"]]
    lead = (f'<p class="lead">Lo que dicen los calendarios laborales de 2027 cuando se miran todos a la vez: '
            f'{num(len(S["ok"]))} municipios con fiestas locales oficiales, los festivos de las 19 comunidades y los boletines de 2026 '
            f'para comparar.</p>')
    intro = guide(
        'Cada página de esta web responde a una pregunta concreta: qué días son festivos en un sitio. Estos análisis hacen la '
        'pregunta contraria: qué patrón aparece cuando se juntan todos los sitios. Qué fechas se repiten, cuántos festivos locales se '
        'pierden en fin de semana, cuántos días laborables quedan en cada provincia, cuándo publica cada boletín y qué puentes '
        'compensan más.',
        'Todas las cifras se calculan con los mismos datos que usan las páginas de cada municipio y se recalculan cuando entra un '
        'boletín nuevo. Cada análisis explica su método, qué municipios quedan fuera y por qué, y enlaza a las fuentes.'
        + (f' Mientras falten comunidades por publicar ({few(pend, 5)}), las cifras de fiestas locales describen solo la parte de '
           f'España ya publicada.' if pend else ""),
    )
    secs = [B.section("lista", "Análisis 2027", f'<ul class="notes">{li}</ul>'), B.section("como", "Cómo se hacen", intro)]
    title = "Análisis del calendario laboral 2027: festivos, puentes y datos"
    desc = (f"Cinco análisis con datos de {num(len(S['ok']))} municipios: festivos locales repetidos y en fin de semana, días "
            f"laborables, publicación y puentes.")
    return render(S, path, B.pick(60, title, "Análisis 2027: festivos locales, puentes y días laborables", "Análisis del calendario laboral 2027"), fit_desc(desc),
                  "Análisis del calendario laboral 2027", "", lead, secs, [], ad_after=None)


# ---------------------------------------------------------------- entry points

def nav_link():
    """For the main nav (Comunidades · Festivos · Puentes · Vacaciones · Escolar · Análisis · Herramientas)."""
    b = B or sys.modules["build"]
    return f'<a href="{b.BASE}{HUB}">Análisis</a>'


def cards(S):
    """The three home figures (repeated date, weekend losses, working days), from the same numbers as the articles."""
    d1, c1 = S["rep"]["top"][0]
    labs = S["wd"]["labs"]
    return [(path_of(PAGES[0][0]), num(c1), f"municipios con fiesta local el {dm(d1)}"),
            (path_of(PAGES[1][0]), num(len(S["we"]["lose"])), "municipios pierden un festivo local entre semana"),
            (path_of(PAGES[2][0]), f"{min(labs)}–{max(labs)}", "días laborables según el municipio")]


def home_block(b=None, data=None):
    """'Análisis 2027' row for the home: three cards with a computed figure each (existing .stats styles). Works before
    or after write(): pass build and the localized data if write() has not run yet (pages.home_page runs first)."""
    global B, DATA
    if b is not None:
        B, DATA = b, data
    if B is None or DATA is None or B.LANG != "es":
        return ""
    li = "".join(f'<li><a href="{B.BASE}{p}"><b>{E(big)}</b>{E(txt)}</a></li>' for p, big, txt in cards(compute()))
    return B.section("analisis", "Análisis 2027", f'<ul class="stats">{li}</ul>'
                     f'<p class="more-l"><a href="{B.BASE}{HUB}">Todos los análisis 2027 →</a></p>')


def write(b, data, fix):
    """Write /analisis/ and the five articles. Returns [(path, lastmod, ['es'])] for build.write_sitemaps."""
    global B, DATA, OUT, _ST
    B, DATA = b, data
    if B.LANG != "es":
        return []
    import pages as P
    OUT = OUT or B.OUT
    _ST = None
    S = compute()
    out, hub_items = [], []
    for fn, (slug, lbl) in zip((page_repeated, page_weekend, page_workdays, page_publication, page_bridges), PAGES):
        path, page, summary, _card = fn(S)
        _write(P, path, page, fix)
        hub_items.append((path, lbl, summary))
        out.append((path, upd_date(S), ["es"]))
    _write(P, HUB, page_hub(S, hub_items), fix)
    out.insert(0, (HUB, upd_date(S), ["es"]))
    return out


def _write(P, path, page, fix):
    page = P.no_thin_ads(path, page)  # the 250-word guard of pages.write (these pages are far above it)
    d = OUT / path
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(fix(page), "utf-8", newline="\n")


def _standalone(argv):
    """Same setup as herramientas/build.py: real head/header/footer, assets hashed like the last full build."""
    global OUT
    sys.path.insert(0, str(ROOT))
    import build as b
    sys.modules.setdefault("build", b)
    import pages as P
    data = b.localize(b.load())
    b.REGIONS = data["regions"]
    fonts = {w: b.short_hash(ROOT / "fonts" / f"public-sans-{w}.woff2") for w in ("400", "600", "700")}
    cssv, jsv = b.short_hash(ROOT / "app.css"), b.short_hash(ROOT / "app.min.js")
    m = re.search(r'data-sidx="(\w+)"', (ROOT / "index.html").read_text("utf-8"))
    sidxv = m.group(1) if m else "0"
    fix = lambda s: (s.replace("{CSSV}", cssv).replace("{JSV}", jsv).replace("{SIDXV}", sidxv)  # noqa: E731
                     .replace("{F400}", fonts["400"]).replace("{F600}", fonts["600"]).replace("{F700}", fonts["700"]))
    P.DATA, P._fix = data, fix
    if "--out" in argv:
        OUT = Path(argv[argv.index("--out") + 1]).resolve()
    ws = write(b, data, fix)
    for p, lm, _ in ws:
        f = OUT / p / "index.html"
        print(f"  {p}  {P.main_words(f.read_text('utf-8'))} words  {f.stat().st_size // 1024} KB  lastmod {lm}")
    if P.thin_no_ads:
        print("  no ads (< 250 words):", P.thin_no_ads)
    print("home_block:", len(home_block()), "chars ·", nav_link())


if __name__ == "__main__":
    _standalone(sys.argv[1:])
