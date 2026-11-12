"""Catalan text and pages (CL_LANG=ca), called by pages.py, guia.py and munipages.py when B.LANG == "ca".

The Spanish modules write every sentence in Spanish; this module holds the same computed sentences written in Catalan
(not translated word by word: Optimot / TERMCAT forms, the press usage noted in data/i18n.json), so no Catalan page
mixes in Spanish text. Every date, count and name still comes from the data files.

    region_lead / region_notes / region_faq      the 19 comunitats
    home_lead / home_notes / home_faq            /ca/
    city_* (7 rich city pages of CA_REGIONS)     Barcelona, l'Hospitalet, Badalona, Mataró, Reus, València, Palma
    hub_*                                        /ca/festivos-locales/
    muni_page / prov_page                        every municipality and province of Catalunya, País Valencià, Illes Balears
    page_puentes, trust_pages                    /ca/puentes/, /ca/sobre/, /ca/contacto/, /ca/aviso-legal/, /ca/cookies/

Terms: festiu / festius locals, dies feiners (TERMCAT 'dia feiner'), pont / fer pont, cap de setmana llarg, agafar
vacances, estatal (not 'nacional', ambiguous next to the Diada Nacional), galetes (TERMCAT 'cookie'), el web
(Optimot), years with the article ('el 2027', 'del 2027'), full dates without it ('13 d'octubre de 2026').
"""
import datetime as dt
import re
from collections import Counter

import build as B
from build import E, t, tn

P = None  # pages module, set by pages.write_pages

VOW = "aeiouàáèéíïòóúüAEIOUÀÁÈÉÍÏÒÓÚÜ"
# Catalan names of the provinces that have Catalan pages (Spanish names in muni.catalogue)
PROV = {"alicante": "Alacant", "castellon": "Castelló", "valencia": "València", "barcelona": "Barcelona", "girona": "Girona",
        "lleida": "Lleida", "tarragona": "Tarragona", "illes-balears": "Illes Balears"}
# Local holiday names of the rich city pages that data/locales-2027.json gives in Spanish (Palma: BOIB Spanish text)
HOL = {"San Sebastián": "Sant Sebastià", "San Juan": "Sant Joan"}


def D(iso):
    return dt.date.fromisoformat(iso)


def join(xs):
    xs = list(xs)
    return "" if not xs else xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " i " + xs[-1]


def few(xs, k=6):
    xs = list(xs)
    return join(xs) if len(xs) <= k else f'{", ".join(xs[:k])} i {len(xs) - k} més'


def cap(s):
    return s[:1].upper() + s[1:]


def _elides(w):
    """d'/l' before a vowel or h + vowel, but not before a semivowel i/u + vowel (de iogurt, de Huelva)."""
    s = w[1:] if w[:1] in "hH" else w
    if not s or s[0] not in VOW:
        return False
    return not (s[0] in "iIuU" and len(s) > 1 and s[1] in VOW)


def de(n):
    """'de Barcelona', 'd'Alcoi', 'del Vendrell', 'de la Seu d'Urgell', 'de l'Hospitalet…', 'des Castell', 'de sa Pobla'."""
    for art, out in (("Els ", "dels "), ("El ", "del "), ("Les ", "de les "), ("La ", "de la "), ("Ses ", "de ses "),
                     ("Sa ", "de sa "), ("Es ", "des ")):
        if n.startswith(art):
            return out + n[len(art):]
    if n.startswith(("L'", "S'")):
        return "de " + n[0].lower() + n[1:]
    return ("d'" if _elides(n) else "de ") + n


def wd(d):
    return B.T["_wd"][d.weekday()]


def name_of(x):
    """Catalan form of a municipality: the Valencian half of the bilingual official name (Alacant, Elx, Xàbia), the
    official name otherwise (València)."""
    on = x.get("official_name") or x["name"]
    if "/" in on:
        parts = [p.strip() for p in on.split("/")]
        es = (x.get("m") or {}).get("name_es") or x["name"]
        return next((p for p in parts if p != es), parts[0])
    return on


def prov_name(p):
    return PROV.get(p["slug"], p["name"])


def prov_label(p):
    if p["uni"]:
        return f'Municipis {de(prov_name(p)) if not prov_name(p).startswith("Illes") else "de les " + prov_name(p)}'
    return f'Província {de(prov_name(p))}'


def prov_place(p):
    """'la província de Barcelona' / 'les Illes Balears' (subject or object, lower case)."""
    n = prov_name(p)
    if p["uni"]:
        return "les " + n if n.startswith("Illes") else n
    return f"la província {de(n)}"


def of_place(p):
    """'de la província de Barcelona' / 'de les Illes Balears'."""
    pl = prov_place(p)
    return ("de " + pl) if pl.startswith(("la ", "les ")) else de(pl)


def in_place(p):
    """'a la província de Barcelona' / 'a les Illes Balears'."""
    pl = prov_place(p)
    return "a " + pl


def rn(r):
    return B.R(r)


def boe():
    return P.DATA["source"]["boe"]


def src_link():
    s = P.DATA["source"]
    return f'<a href="{s["url"]}" rel="noopener">{s["id"]}</a>'


def brk(it):
    s = f'{B.drange(it["s"], it["e"])}: {it["len"]} dies de festa'
    return s + (f' amb {it["cost"]} de vacances ({B.dlist(it["take"])})' if it["cost"] else " sense agafar vacances")


def notes(items):
    return '<ul class="notes">' + "".join(f"<li>{x.replace('..', '.')}</li>" for x in items if x) + "</ul>"


def chip(path):
    return B.lang_chip(path, ["es", "ca"])


# ---------------------------------------------------------------- comunitats

def subj(r):
    """'Catalunya' / 'El País Valencià' / 'Les Illes Balears', and whether the verb goes in the plural."""
    i = rn(r)["region_in"]
    s = i[2:] if i.startswith("a ") else ("el " + i[3:] if i.startswith("al ") else i)
    return cap(s), s.startswith("les ")


def region_lead(r):
    import guia
    s = guia.stats()[r["slug"]]
    nat = sum(1 for h in s["hols"] if h["kind"] == "n")
    own = s["n"] - nat
    sj, pl = subj(r)
    extra = ", més la festa de cada illa i els 2 locals de cada municipi" if s["can"] else ", més els 2 locals de cada municipi"
    return guia.lead(f'{E(sj)} {"tenen" if pl else "té"} <b>{s["n"]} festius</b> laborals el 2027: {nat} de comuns a tot Espanya '
                     f'i {own} de propis{extra}.')


def _zone_note(slug):
    return B.I18N["zones"][slug]["note"]["ca"]


def region_notes(r, cities):
    import guia
    import muni
    S = guia.stats()
    s = S[r["slug"]]
    names = rn(r)
    ins = {k: rn(x["r"])["region_in"] for k, x in S.items()}
    chosen = [h for h in s["hols"] if h["kind"] == "r"]

    def shared(h):
        o = [ins[k] for k, x in S.items() if k != r["slug"] and h["name"] in x["names"] and h["date"] in x["dates"]]
        if not o:
            return ""
        return f', també {join(o)}' if len(o) <= 4 else f', també a {len(o)} comunitats més'

    own_h = (f'<b>Els {len(chosen)} festius propis {names["region_of"]}:</b> ' if len(chosen) != 1
             else f'<b>El festiu propi {names["region_of"]}:</b> ')
    items = [own_h + "; ".join(f'{E(h["name"])}, {B.dlong(h["date"])}{shared(h)}' for h in chosen) + "."]
    nm = {"2027-03-25": "el Dijous Sant", "2027-03-26": "el Divendres Sant", "2027-03-29": "el Dilluns de Pasqua"}
    days = [d for d in guia.EASTER if d in s["dates"]]
    rr = guia.run_with(s["hols"], "2027-03-26")
    run = f'{B.drange(*rr)}, {rr[1] - rr[0] + 1} dies seguits sense agafar vacances' if rr else ""
    txt = f'<b>Setmana Santa:</b> {join(nm[d] for d in days)} {"són festius" if len(days) > 1 else "és festiu"}: {run}.'
    if "2027-03-25" not in s["dates"]:
        lack = [ins[k] for k, x in S.items() if "2027-03-25" not in x["dates"]]
        txt += f' El Dijous Sant és feiner, cosa que només passa {join(lack)}.'
    elif "2027-03-29" not in s["dates"]:
        txt += " El Dilluns de Pasqua és feiner."
    items.append(txt)
    if "2027-08-16" in s["dates"]:
        items.append("<b>15 d'agost:</b> cau en diumenge i es trasllada al dilluns 16 d'agost.")
    elif "2027-10-11" in s["dates"]:
        items.append("<b>15 d'agost:</b> cau en diumenge i se substitueix pel dilluns 11 d'octubre, que fa pont llarg amb el 12.")
    else:
        items.append("<b>15 d'agost:</b> cau en diumenge i aquí no es trasllada: no hi ha cap dia de festa de més.")
    sat = [h for h in s["hols"] if D(h["date"]).weekday() >= 5]
    if sat:
        items.append(f'<b>En cap de setmana:</b> {join(E(h["name"]) + " (" + B.dlong(h["date"]) + ")" for h in sat)}. '
                     f'No es passen a un altre dia.')
    b = guia.best(s["breaks"])
    lw = sum(1 for it in s["breaks"] if not it["cost"])
    if b:
        items.append(f'<b>{tn("n_pts", len(s["pts"])).capitalize()}:</b> el millor, {brk(b)}. A més, '
                     f'{lw} cap{"s" if lw != 1 else ""} de setmana llarg{"s" if lw != 1 else ""} sense agafar res. '
                     f'<a href="{B.BASE}puentes/#{r["slug"]}">Compara-ho amb les altres comunitats</a>.')
    labs = sorted(x["lab"] for x in S.values())
    same = sum(1 for x in S.values() if x["lab"] == s["lab"]) - 1
    items.append(f'<b>{s["lab"]} dies feiners</b> de dilluns a divendres, abans de restar-hi els 2 locals'
                 + (f', igual que {same} comunitat{"s" if same != 1 else ""} més' if same else "")
                 + f' (a tot Espanya, de {labs[0]} a {labs[-1]}).')
    z = P.DATA["zones"].get(r["slug"])
    if z and r["slug"] == "canarias":
        isl = "; ".join(f'{E(o["name"])}, {E(o["add"]["name"])} ({B.dm(o["add"]["date"])})' for o in z["options"] if "add" in o)
        items.append(f'<b>Festa de cada illa:</b> {isl}. {E(_zone_note("canarias"))}')
    elif z:
        items.append(f'<b>Aran:</b> {E(_zone_note(r["slug"]))}')
    if r["slug"] in B.CA_REGIONS and muni.MUNI_ON:
        ms = [x for x in muni.catalogue()["munis"] if x["region"] == r["slug"]]
        ok = sum(1 for x in ms if x["ok"])
        items.append(f'<b>Festius locals:</b> {ok} de {len(ms)} municipis amb data oficial del 2027. '
                     + ("La resta, pendent de publicació oficial: no n'avancem les dates." if ok < len(ms) else "Tots ja són publicats."))
    else:
        mine = [x for x in cities if x["r"]["slug"] == r["slug"]]
        items.append(f'<b>Festius locals:</b> {len(mine)} ciutat{"s" if len(mine) != 1 else ""} ja amb data oficial. '
                     f'La resta, pendent de publicació oficial.' if mine else
                     '<b>Festius locals:</b> pendents de publicació oficial per al 2027. Els publica l\'autoritat laboral '
                     'de la comunitat al butlletí oficial.')
    more = (f'<details class="more"><summary>Com es fixen els festius</summary>'
            f'<p>L\'Estatut dels treballadors permet fins a 14 festius laborals l\'any, retribuïts i no recuperables, 2 '
            f'dels quals són locals. El Govern fixa els estatals i cada comunitat en pot canviar alguns per festes pròpies: '
            f'la comunitat aprova el seu calendari al butlletí oficial ({guia.BULL[r["slug"]]}) i el BOE els recull tots a la '
            f'{src_link()}.</p>'
            f'<p>Els 2 festius locals els proposa el ple de cada ajuntament i els publica l\'autoritat laboral al butlletí '
            f'oficial. Fins aleshores, aquí surten com a pendents i no n\'avancem les dates.</p></details>')
    return B.section("claves", f'Claus del 2027 {names["region_in"]}', notes(items) + more)


def region_faq(r, f):
    names = rn(r)
    ri = names["region_in"]
    dates = {h["date"] for h in f["hols"]}
    n_txt = f'{f["n"]}' + (" (més la festa de la teva illa)" if f["can"] else "")
    own = ", ".join(f'{E(h["name"])} ({B.dm(h["date"])})' for h in f["own"])
    if "2027-03-29" in dates:
        q2 = (f"És festiu el Dilluns de Pasqua {ri}?", "Sí, el dilluns 29 de març de 2027.")
    else:
        q2 = (f"És festiu el Dijous Sant {ri}?",
              "Sí, el dijous 25 de març de 2027." if "2027-03-25" in dates
              else "No. El 25 de març de 2027 és feiner; el Divendres Sant (26 de març) sí que és festiu.")
    if "2027-08-16" in dates:
        a3 = "Cau en diumenge i es trasllada al dilluns 16 d'agost."
    elif "2027-10-11" in dates:
        a3 = "Cau en diumenge i se substitueix pel dilluns 11 d'octubre."
    else:
        a3 = "Cau en diumenge i no es trasllada, així que no hi ha cap festiu de més."
    if r["slug"] in B.CA_REGIONS:
        a4 = ("Cada ajuntament en fixa 2. Cerca el teu municipi a dalt de tot: cada municipi té la seva pàgina, amb les "
              "dates oficials o «pendent» si encara no s'han publicat.")
    else:
        a4 = (f'Cada ajuntament en fixa 2. Els de les ciutats ja publicades són a '
              f'<a href="{B.BASE}festivos-locales/#{r["slug"]}">festius locals 2027</a>.')
    return [(f"Quants festius hi ha {ri} el 2027?",
             f'{n_txt} segons el BOE: {len(f["nat"])} de comuns a tot Espanya i {len(f["own"])} de propis: {own}. '
             f'A més, cada municipi té 2 festius locals.'),
            q2, (f"Què passa amb el 15 d'agost del 2027 {ri}?", a3),
            (f"On trobo els festius del meu municipi {ri}?", a4)]


def quick_access(r):
    """Under the answer on a comunitat page: the search box, and for the Catalan-speaking comunitats their province pages."""
    import muni
    ps = [p for p in muni.catalogue()["provs"] if p["region"] == r["slug"] and p["path"]] if muni.MUNI_ON else []
    if not ps:
        return ""
    ex = None
    if r["slug"] in B.CA_REGIONS:
        caps = {p.get("capital_ine") for p in ps}
        big = sorted((x for p in ps for x in p["munis"] if x["ine"] not in caps), key=lambda x: -(x["m"].get("pop") or 0))[:2]
        ex = f'P. ex.: {", ".join(name_of(x) for x in big)}' if len(big) == 2 else None
        links = " · ".join(f'<a href="{B.BASE}{p["path"]}">{E(prov_label(p))} <span class="m">({len(p["munis"])})</span></a>' for p in ps)
        n = sum(len(p["munis"]) for p in ps)
        lab = f'<p class="qa-l"><b>Els {n} municipis:</b> {links}</p>'
    else:
        lab = ""
    return f'<div class="qa">{B.search_box("q-reg", big=True, region=r["slug"], ph=ex)}{lab}</div>'


def link(x):
    return f'<a href="{B.BASE}{x["path"]}">{E(name_of(x))}</a>'


def dates_of(x):
    if not x["ok"]:
        return "pendent"
    import munipages as MP
    return " · ".join(B.dmon(h["date"]) for h in MP.wide_of(x)) or "per localitat"


def muni_directory(r):
    """Comunitat page (Catalan-speaking comunitats): every province with its counts and its biggest municipalities."""
    import muni
    import munipages as MP
    if r["slug"] not in B.CA_REGIONS or not muni.MUNI_ON:
        return ""
    ps = [p for p in muni.catalogue()["provs"] if p["region"] == r["slug"] and p["path"] and p["munis"]]
    if not ps:
        return ""
    k = 24 if len(ps) == 1 else 12
    out = []
    for p in sorted(ps, key=lambda p: muni.fold(prov_name(p))):
        ok = sum(1 for x in p["munis"] if x["ok"])
        pen = len(p["munis"]) - ok
        cnt = " · ".join(s for s in (f"{ok} publicat{'s' if ok != 1 else ''}" if ok else "",
                                     f"{pen} pendent{'s' if pen != 1 else ''}" if pen else "") if s)
        li = "".join(f'<li>{link(x)} <span class="m{"" if x["ok"] else " pe"}">{dates_of(x)}</span></li>'
                     for x in MP.by_pop(p["munis"])[:k])
        out.append(f'<h3 class="h3"><a href="{B.BASE}{p["path"]}">{E(prov_label(p))}</a> <span class="m">{cnt}</span></h3>'
                   f'<ul class="links">{li}</ul>'
                   f'<p class="more-l"><a href="{B.BASE}{p["path"]}">Els {len(p["munis"])} municipis →</a></p>')
    return "".join(out)


def prov_links(region, province=None):
    """City page: the other municipalities of its province (Catalan province pages)."""
    import muni
    if region not in B.CA_REGIONS or not muni.MUNI_ON:
        return ""
    ps = [p for p in muni.catalogue()["provs"] if p["region"] == region and p["path"] and (province is None or p["name"] == province)]
    if not ps:
        return ""
    lab = "Tots els municipis" if province is None else "La resta de municipis"
    return (f'<p class="more-l">{lab}: ' + " · ".join(f'<a href="{B.BASE}{p["path"]}">{E(prov_label(p))} ({len(p["munis"])})</a>'
                                                      for p in ps) + "</p>")


# ---------------------------------------------------------------- home

def home_lead():
    import guia
    S = guia.stats()
    nat = sum(1 for h in S["madrid"]["hols"] if h["kind"] == "n")
    return guia.lead(f'El 2027 hi ha <b>{nat} festius comuns</b> a tot Espanya. Cada comunitat n\'arriba a 12 amb els seus '
                     f'(les Canàries, a 11 més la festa de cada illa) i cada municipi n\'hi suma 2 de locals: 14 dies en total.')


def _ins(slugs):
    import guia
    S = guia.stats()
    return [rn(S[k]["r"])["region_in"] for k in slugs]


def _having(date):
    import guia
    return [k for k, s in guia.stats().items() if date in s["dates"]]


def _lacking(date):
    import guia
    return [k for k, s in guia.stats().items() if date not in s["dates"]]


def _names(slugs):
    import guia
    S = guia.stats()
    return [S[k]["r"]["name"] for k in slugs]


def home_notes():
    import guia
    S = guia.stats()
    nat = [h for h in S["madrid"]["hols"] if h["kind"] == "n"]
    jt, lp, sj = _having("2027-03-25"), _having("2027-03-29"), _having("2027-03-19")
    m16, m11 = _having("2027-08-16"), _having("2027-10-11")
    rest = [k for k, s in S.items() if "2027-08-16" not in s["dates"] and "2027-10-11" not in s["dates"]]
    sat = [h for h in nat if D(h["date"]).weekday() == 5]
    b = guia.best(B.all_breaks(nat))
    labs = sorted(s["lab"] for s in S.values())
    items = [
        f'<b>Dijous Sant (25 de març):</b> festiu a {len(jt)} comunitats; feiner {join(_ins(_lacking("2027-03-25")))}.',
        f'<b>Dilluns de Pasqua (29 de març):</b> festiu {join(_ins(lp))}.',
        f'<b>Sant Josep (19 de març):</b> festiu {join(_ins(sj))}.',
        f'<b>El 15 d\'agost cau en diumenge:</b> {join(_names(m16))} el passen al dilluns 16'
        + (f'; {join(_names(m11))}, al dilluns 11 d\'octubre' if m11 else "")
        + f'. {cap(few(_ins(rest), 5))} no hi ha cap dia de més.',
        (f'<b>{join(E(h["name"]) + " (" + B.dm(h["date"]) + ")" for h in sat)} '
         f'{"cauen" if len(sat) > 1 else "cau"} en dissabte</b> i no es passen a un altre dia.') if sat else "",
        f'<b>El millor pont estatal:</b> {brk(b)}.' if b else "",
        f'<b>Dies feiners:</b> entre {labs[0]} i {labs[-1]} de dilluns a divendres segons la comunitat, abans de restar-hi els 2 locals.',
    ]
    more = (f'<details class="more"><summary>Com es fixen els festius</summary>'
            f'<p>L\'Estatut dels treballadors permet fins a 14 festius laborals l\'any, retribuïts i no recuperables, 2 dels '
            f'quals són locals. El Govern publica els estatals al BOE; cada comunitat en pot canviar alguns per festes '
            f'pròpies, i cada ajuntament proposa els seus 2 locals.</p>'
            f'<p><a href="{B.BASE}puentes/">Ponts 2027 de cada comunitat</a> · '
            f'<a href="{B.BASE}festivos-locales/">Festius locals 2027</a></p></details>')
    return B.section("claves", "El que canvia el 2027", notes(items) + more)


def home_faq(regs, nat):
    import guia
    S = guia.stats()
    counts = sorted({f["n"] for s, f in regs.items() if s != "canarias"})
    weekend = [h for h in nat if D(h["date"]).weekday() >= 5]
    labs = [B.workdays(f["hols"], 1 if f["can"] else 0) for f in regs.values()]
    m16, m11 = _having("2027-08-16"), _having("2027-10-11")
    wdays = sum(1 for d in B.DAYS if d.weekday() < 5)
    return [("Quants festius hi ha el 2027?",
             f'{len(nat)} de comuns a tot Espanya i {"/".join(map(str, counts))} a cada comunitat (a les Canàries, '
             f'{regs["canarias"]["n"]} més la festa de cada illa). A més, cada municipi té 2 festius locals.'),
            ("Quan es va publicar el calendari laboral del 2027?",
             f'Al BOE del 13 d\'octubre de 2026: {src_link()}.'),
            ("Quins festius cauen en cap de setmana el 2027?",
             join(f'{E(h["name"])} ({B.dlong(h["date"])})' for h in weekend) + ". "
             f'El 15 d\'agost és diumenge: {join(_names(m16))} el passen al dilluns 16'
             + (f'; {join(_names(m11))}, a l\'11 d\'octubre.' if m11 else ".")),
            ("Quants dies feiners té el 2027?",
             f"{wdays} de dilluns a divendres. Si en restes els festius, en queden entre {min(labs)} i {max(labs)}, segons la "
             f"comunitat, sense comptar-hi els 2 locals."),
            ("Quan és la Setmana Santa del 2027?",
             "Del diumenge 21 al diumenge 28 de març. El Dijous Sant és el 25 i el Divendres Sant, el 26.")]


# ---------------------------------------------------------------- rich city pages (CA_REGIONS)

def hol_name(n):
    return HOL.get(n, n)


def source_label(c):
    if c["status"] == "ayuntamiento":
        return f'Ple de l\'Ajuntament {de(c["ca_name"])}'
    m = re.search(r"\(([^()]*\b(?:BO[A-Z]*|DO[A-Z]*)\b[^()]*)\)\s*$", c["source"]["title"])
    return m.group(1) if m else "Butlletí oficial"


def city_titles(x):
    r, sn = x["r"], x["title_name"]
    h1, h2 = x["holidays"]
    d1, d2 = B.dm(h1["date"]), B.dm(h2["date"])
    m1, m2 = B.dmon(h1["date"]), B.dmon(h2["date"])
    title = B.pick(60, f"Calendari laboral {sn} 2027: festius {d1} i {d2}", f"Calendari laboral {sn} 2027: festius {m1} i {m2}",
                   f"Festius {sn} 2027: {m1} i {m2}", f"Calendari laboral {sn} 2027")
    names = rn(r)
    tail = (f'Amb els {x["boe"]} {names["region_of"]}: {x["n"]} festius, {tn("n_pts", len(x["pts"]))} i '
            f'{x["lab"]} dies feiners.')
    desc = B.pick(155,
                  f'Festius locals {de(sn)} el 2027: {B.dlong(h1["date"])} ({h1["name"]}) i {B.dlong(h2["date"])} ({h2["name"]}). {tail}',
                  f'Festius locals {de(sn)} el 2027: {B.dlong(h1["date"])} i {B.dlong(h2["date"])}. {tail}',
                  f'Festius locals {de(sn)} el 2027: {d1} i {d2}. {tail}',
                  f'Festius locals {de(sn)} el 2027: {m1} i {m2}. {x["n"]} festius i {x["lab"]} dies feiners.')
    return title, desc.replace("..", ".")


def city_lead(x):
    import guia
    h1, h2 = x["holidays"]
    return guia.lead(f'Festius locals {de(x["title_name"])} el 2027: <b>{B.dlong(h1["date"])}</b> ({E(h1["name"])}) i '
                     f'<b>{B.dlong(h2["date"])}</b> ({E(h2["name"])}). Amb els {x["boe"]} {rn(x["r"])["region_of"]}, '
                     f'{x["n"]} festius en total.')


def city_notes(x, cities):
    import guia
    r = x["r"]
    name = x["title_name"]
    base = B.region_holidays(P.DATA, r["slug"], x["zone"])
    breaks = B.all_breaks(x["hols"])
    items = []
    for h in x["holidays"]:
        d = D(h["date"])
        i = guia.idx(h["date"])
        it = next((b for b in breaks if b["s"] <= i <= b["e"]), None)
        others = [n for n in (it["names"] if it else []) if n != h["name"]]
        withs = f', amb {join(E(n) for n in others)}' if others else ""
        if d.weekday() == 5:
            eff = "cau en dissabte: si treballes de dilluns a divendres, no et dona cap dia lliure més"
        elif it and it["cost"]:
            eff = f'pont de {it["len"]} dies agafant-ne {it["cost"]} de vacances ({B.dlist(it["take"])}): {B.drange(it["s"], it["e"])}{withs}'
        elif it:
            eff = f'cap de setmana llarg de {it["len"]} dies sense agafar vacances: {B.drange(it["s"], it["e"])}{withs}'
        else:
            eff = f'cau en {wd(d)}, a mitja setmana, sense pont'
        items.append(f'<b>{cap(B.dlong(h["date"]))} · {E(h["name"])}:</b> {eff}.')
    blab, bpts = B.workdays(base, 0), B.puentes(base)
    items.append(f'<b>{E(name)} davant la resta {rn(r)["region_of"]}:</b> {x["lab"]} dies feiners de dilluns a divendres, '
                 f'davant de {blab}; {tn("n_pts", len(x["pts"]))}, davant de {len(bpts)}.')
    b, rb = guia.best(breaks), guia.best(B.all_breaks(base))
    if b:
        same = rb and (b["s"], b["e"]) == (rb["s"], rb["e"])
        items.append(f'<b>Millor pont{" (el mateix que a tota la comunitat)" if same else ""}:</b> {brk(b)}.')
    for h in x["holidays"]:
        sh = [y["title_name"] for y in cities if y is not x and y["r"]["slug"] == r["slug"]
              and any(z["date"] == h["date"] for z in y["holidays"])]
        if sh:
            items.append(f'<b>El {B.dm(h["date"])} també és festiu local a</b> {few(E(n) for n in sh)}.')
    src = x["c"]["source"]
    st = " L'ha aprovat el ple; falta que es publiqui al butlletí oficial." if x["pending_bulletin"] else ""
    items.append(f'<b>Font oficial:</b> <a href="{E(src["url"])}" rel="noopener">{E(x["src_label"])}</a>, comprovada el '
                 f'{B.dmy(src["checked"])}.{st}')
    return B.section("claves", f'Què canvien els festius locals {de(name)}', notes(items))


def city_faq(x):
    c, name = x["c"], x["title_name"]
    h1, h2 = x["holidays"]
    src = c["source"]
    how = ("Els va aprovar el ple de l'ajuntament; falta que es publiquin al butlletí oficial." if x["pending_bulletin"]
           else f'Publicats al {E(x["src_label"])}.')
    import muni
    pm = (muni.catalogue()["by_path"].get(x["path"]) or {}).get("prov")
    whole = ("a totes " + prov_place(pm) if pm["uni"] else "a tota " + prov_place(pm)) if pm else "a tota la província"
    return [(f"Quins són els festius locals {de(name)} el 2027?",
             f'{cap(B.dlong(h1["date"]))}, {E(h1["name"])}, i {B.dlong(h2["date"])}, {E(h2["name"])}. {how} '
             f'<a href="{E(src["url"])}" rel="noopener">Font</a>.'),
            (f"Quants dies feiners té {name} el 2027?",
             f'{x["lab"]} de dilluns a divendres, un cop descomptats els festius que cauen entre setmana.'),
            (f'El {B.dm(h1["date"])} és festiu {whole}?',
             f'No. Els festius locals només valen al municipi {de(name)}.')]


# ---------------------------------------------------------------- /festivos-locales/

def hub_text(cities):
    import muni
    import guia
    cat = muni.catalogue()
    m_ok, m_all = sum(1 for x in cat["munis"] if x["ok"]), len(cat["munis"])
    days = [(x, h) for x in cities for h in x["holidays"]]
    by_date = Counter(h["date"] for _, h in days)
    top = by_date.most_common(4)
    wdc = Counter(D(h["date"]).weekday() for _, h in days)
    bridge = 0
    for x, h in days:
        i = guia.idx(h["date"])
        it = next((b for b in B.all_breaks(x["hols"]) if b["s"] <= i <= b["e"]), None)
        bridge += bool(it and it["cost"])
    months = Counter(D(h["date"]).month for _, h in days)
    m, mn = months.most_common(1)[0]
    items = [
        "<b>Els dies més repetits:</b> " + "; ".join(f'{B.dm(d)}, a {n} municipis' for d, n in top) + ".",
        f'<b>En dilluns o divendres:</b> {wdc[0] + wdc[4]} dels {len(days)} dies locals, que donen un cap de setmana llarg '
        f'sense agafar res.',
        f'<b>Amb pont:</b> {bridge} dies locals cauen en dimarts o dijous (o al costat d\'un altre festiu) i fan pont '
        f'agafant 1 o 2 dies.',
        f'<b>En dissabte:</b> {wdc[5]} dies locals; per a qui treballa de dilluns a divendres no sumen cap dia lliure.',
        f'<b>El mes amb més festes locals:</b> {B.T["_months"][m - 1]}, amb {mn}.',
    ]
    lead = guia.lead(f'{m_ok} municipis ja tenen els <b>2 festius locals del 2027</b> publicats oficialment; {m_all - m_ok} '
                     f'continuen pendents i no els posem data fins que surti al butlletí o a l\'acord del ple.')
    sec = B.section("claves", "El que diuen els festius locals del 2027", notes(items)
                    + f'<p class="m">Calculat amb les {len(cities)} ciutats de la taula.</p>')
    provs = [p for p in cat["provs"] if p["path"] and p["munis"] and p["region"] in B.CA_REGIONS]
    li = "".join(f'<li><a href="{B.BASE}{p["path"]}">{E(prov_label(p))}</a> <span class="m">{sum(1 for x in p["munis"] if x["ok"])}'
                 f' de {len(p["munis"])}</span></li>' for p in sorted(provs, key=lambda p: muni.fold(prov_name(p))))
    psec = B.section("provincias", "Catalunya, País Valencià i Illes Balears: tots els municipis", f'<ul class="links">{li}</ul>')
    title = "Festius locals 2027 de cada municipi (oficials)"
    desc = (f"Els 2 festius locals del 2027 de {m_ok} municipis, amb la font oficial, per ciutat i per província. "
            f"La resta, tan bon punt es publiquin.")
    ctx = f'<p class="ctx">{m_ok} de {m_all} municipis publicats · <time datetime="{{d}}">actualitzat {{dd}}</time></p>'
    qas = [("Qui fixa els festius locals?",
            "Cada ajuntament proposa 2 dies l'any i l'autoritat laboral de la comunitat els publica al butlletí oficial."),
           ("Per què no surt el meu municipi?",
            "Perquè encara no hi ha publicació oficial. Només donem dates d'un butlletí o d'un acord del ple publicat per "
            "l'ajuntament.")]
    return title, desc, lead, ctx, sec, psec, qas


# ---------------------------------------------------------------- municipality and province pages

WDH = "<th>dl<th>dt<th>dc<th>dj<th>dv<th>ds<th>dg"


def effect(h, f):
    import munipages as MP
    d = D(h["date"])
    i = (d - B.DAYS[0]).days
    same = [b["name"] for b in f["base"] if b["date"] == h["date"]]
    if same:
        return f'coincideix amb {E(same[0])}, que ja és festiu a la comunitat'
    if d.weekday() >= 5:
        return f'cau en {wd(d)} i no suma cap dia lliure entre setmana'
    it = next((b for b in f["breaks"] if b["s"] <= i <= b["e"]), None)
    if it and it["cost"]:
        return f'pont de {it["len"]} dies ({B.drange(it["s"], it["e"])}) demanant {B.dlist(it["take"])}'
    if it:
        return f'cap de setmana llarg de {it["len"]} dies ({B.drange(it["s"], it["e"])}) sense demanar vacances'
    return f'cau en {wd(d)} i no fa pont d\'1 o 2 dies'


def notes_official(x, f, p, st):
    import guia
    import munipages as MP
    items = []
    wide = f["wide"]
    for h in wide:
        items.append(f'<b>{cap(B.dlong(h["date"]))}:</b> {effect(h, f)}.')
    for h in wide:
        sh = [y for y in st["by_date"].get(h["date"], []) if y is not x]
        if sh:
            ex = MP.by_pop(sh)[:3]
            items.append(f'<b>El {B.dm(h["date"])} {in_place(p)}:</b> també és festa local a {len(sh)} '
                         f'municipi{"s" if len(sh) != 1 else ""} més, com ara {join(link(y) for y in ex)}.')
        else:
            items.append(f'<b>El {B.dm(h["date"])} {in_place(p)}:</b> cap altre municipi amb data publicada no el té.')
    mine = sorted(h["date"] for h in wide)
    twins = [y for y in st["ok"] if y is not x and len(mine) == 2 and sorted(h["date"] for h in MP.wide_of(y)) == mine]
    if twins:
        tw = MP.by_pop(twins)
        items.append(f'<b>Els mateixos dies que</b> {join(link(y) for y in tw[:5])}' + (f' i {len(tw) - 5} més' if len(tw) > 5 else "") + ".")
    top = st["dates"].most_common(1)
    if top and top[0][0] not in mine and top[0][1] > 1:
        items.append(f'<b>El dia més repetit {in_place(p)}</b> és el {B.dlong(top[0][0])} ({top[0][1]} municipis); aquí és feiner.')
    diff = f["lab"] - (st["med"] or f["lab"])
    items.append(f'<b>{f["lab"]} dies feiners</b> de dilluns a divendres: '
                 + (f'{abs(diff)} {"més" if diff > 0 else "menys"} que la mediana {of_place(p)} ({st["med"]})' if diff
                    else f'igual que la mediana {of_place(p)}') + f'. Sense els locals, {f["blab"]}.')
    b = guia.best(f["breaks"])
    if b:
        same = any((b["s"], b["e"]) == (y["s"], y["e"]) for y in f["bpts"])
        items.append(f'<b>Millor pont{" (el de tota la comunitat)" if same else ""}:</b> {brk(b)}.')
    return items


def notes_pending(x, f, p, st, r):
    import guia
    import munipages as MP
    from muni import short_src, wide_and_partial
    items = []
    if x["ref26"] or x.get("nuc26"):
        w26 = wide_and_partial(x["ref26"])[0]
        ds = ["el " + B.dlong(h["date"]) for h in w26]  # 2026 names left out: the 2026 sources are often in Spanish
        s = x["src26"] or {}
        sl = (f'<a href="{E(s["url"])}" rel="noopener">{E(short_src(s.get("title"), "Butlletí oficial"))}</a>' if s.get("url")
              else E(short_src(s.get("title"), "Butlletí oficial")))
        ref = "<b>Referència del 2026 (no és el calendari oficial del 2027):</b>"
        if ds:
            items.append(f'{ref} van ser {join(ds)} de 2026 ({sl}).')
        nuc = x.get("nuc26") or []
        if nuc:
            li = "".join(f'<li><b>{E(n["name"])}</b> <span class="m">' + ", ".join(
                B.dmon(h["date"]) + " 2026" for h in n.get("holidays") or [])
                + "</span></li>" for n in nuc)
            items.append(("" if ds else f"{ref} ") + f'<details class="more"><summary>El 2026 cada nucli va tenir la seva festa '
                         f'({len(nuc)})</summary><ul class="links">{li}</ul></details>')
        if s.get("published"):
            items.append(f'<b>Quan surten:</b> les del 2026 es van publicar el {B.dmy(s["published"])}. Aquesta pàgina canvia '
                         f'tan bon punt es publiquin les del 2027.')
    if st["ok"]:
        top = st["dates"].most_common(1)[0]
        items.append(f'<b>{cap(in_place(p))}</b> ja tenen data {len(st["ok"])} de {len(p["munis"])} municipis'
                     + (f'; el dia més repetit és el {B.dlong(top[0])} ({top[1]}).' if top[1] > 1 else
                        f' ({join(link(y) for y in MP.by_pop(st["ok"])[:3])}).'))
    b = guia.best(f["breaks"])
    if b:
        items.append(f'<b>Millor pont {rn(r)["region_of"]}:</b> {brk(b)}.')
    items.append("<b>Ponts i dies feiners</b> d'aquesta pàgina: només amb els festius de la comunitat, sense els locals.")
    return items


def mini_year(hols):
    import munipages as MP
    return MP.mini_year(hols).replace("<th>L<th>M<th>X<th>J<th>V<th>S<th>D", WDH)


def muni_page(x, cat, write, REG, UPDATED):
    import guia
    import munipages as MP
    from muni import short_src, wide_and_partial
    m, p, r = x["m"], x["prov"], REG[x["region"]]
    f = MP.facts(x)
    name, ok = name_of(x), x["ok"]
    names = rn(r)
    nm_t = f'{name} ({prov_name(p)})' if cat["dup_names"][x["name"]] > 1 else name
    st = MP.prov_stats(p)
    wide, part = f["wide"], f["part"]
    kinds = ["n", "r", "l"]
    crumbs = [(t("spain"), ""), (r["name"], f'{r["slug"]}/')] + ([(prov_label(p), p["path"])] if p["path"] else []) + [(name, x["path"])]
    isl = ", amb la Festa d'Aran el 17 de juny en lloc del Dilluns de Pasqua" if x["zone"] == "aran" else ""
    upd_date = UPDATED or P.DATA["updated"]
    nb = len(f["base"])
    if ok and wide:
        ds = [f'<b>{B.dlong(h["date"])}</b>' + (f' ({E(h["name"])})' if h.get("name") else "") for h in wide]
        lead = (f'{"Els festius locals" if len(wide) > 1 else "El festiu local"} {de(name)} el 2027 '
                f'{"són" if len(wide) > 1 else "és"} {join("el " + d for d in ds)}. Amb els {nb} {names["region_of"]}{isl}, '
                f'{len(f["hols"])} festius i {f["lab"]} dies feiners.')
        items = notes_official(x, f, p, st)
    elif ok:
        lead = (f'El butlletí no fixa per al 2027 cap festiu local comú a tot el municipi {de(name)}: cada localitat té els '
                f'seus. Amb els {nb} {names["region_of"]}{isl}, {f["blab"]} dies feiners abans dels locals.')
        items = [f'<b>Ponts i dies feiners</b> d\'aquesta pàgina: amb els festius {names["region_of"]}; els de cada localitat, a sota.']
    else:
        lead = (f'Les festes locals del 2027 {de(name)} encara no s\'han publicat al butlletí oficial. Amb els {nb} festius '
                f'{names["region_of"]}{isl}, {f["blab"]} dies feiners abans de restar-hi els locals.')
        items = notes_pending(x, f, p, st, r)
    if part:
        items.append("<b>Només en una part del municipi:</b> " + "; ".join(f'{B.dm(h["date"])}, {E(MP.hname(h))}' for h in part) + ".")
    locs = x.get("localities") or []
    loc_html = ""
    if locs:
        li = "".join(f'<li><b>{E(lo["name"])}</b> <span class="m">' + ", ".join(
            B.dmon(h["date"]) + (f' ({E(h["name"])})' if h.get("name") else "") for h in lo["holidays"]) + "</span></li>" for lo in locs)
        loc_html = f'<h3 class="h3">Només a cada localitat</h3><ul class="links">{li}</ul>'
    src = x["src27"] or {}
    if ok and src:
        stt = " · acord de l'ajuntament, pendent del butlletí" if x["status"] == "ayuntamiento" else ", segons el butlletí"
        s_html = (f'Locals: <a href="{E(src.get("url") or "")}" rel="noopener" title="{E(src.get("title", ""))}">'
                  f'{E(short_src(src.get("title"), "Ajuntament " + de(name)))}</a>{stt}')
    else:
        s_html = "Locals 2027: pendents de publicació oficial"
    srcline = (f'<p class="src">{s_html} · Comunitat: {src_link()}'
               f' · Actualitzat: <time datetime="{upd_date}">{B.dmy(upd_date)}</time></p>')
    where = E(prov_name(p)) + (f', {E(r["name"])}' if prov_name(p) != r["name"] else "")
    offn = f' · nom oficial: {E(x["official_name"])}' if x["official_name"] != name else ""
    stats = B.stats_html([(None, tn("n_hol", len(f["hols"])) + ("" if ok else " sense locals")), (None, tn("n_lab", f["lab"])),
                          (None, tn("n_pts", len(f["pts"])))])
    ics = MP.region_ics(x)
    gc = [(f'{B.dmon(h["date"])} · {MP.hname(h)}', B.gcal_event(h["date"], MP.hname(h), name)) for h in wide] if ok else []
    gc.append((f'Festius {names["region_of"]} (subscripció)',
               "https://calendar.google.com/calendar/r?cid=" + B.quote(f"webcal://{B.HOST}{ics}", safe="")))
    acts = B.actions_html(ics, f'festius-2027-{m["slug"]}.ics', f"Calendari laboral {name} 2027", gc)
    acts = acts.replace('data-x="dl"', f'data-ics="{E(name)}" data-key="{m["ine"]}"', 1)
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}{chip(x["path"])}'
            + B.hero_grid(f'<h1>Calendari laboral {E(name)} 2027</h1><p class="lead">{lead}</p>',
                          B.next_card(f["hols"], prev=B.prev26(x["region"], x["zone"], wide_and_partial(x["ref26"] or [])[0])) + stats + acts,
                          f'<p class="ctx">{where}{offn}</p>{srcline}') + '</div>')
    pts = MP.pts_rows(f["breaks"]) or f'<tr><td colspan="3">{t("no_bridges")}</td></tr>'
    close = x.get("near") or []
    seen = {id(y) for y, _ in close}
    big = [y for y in MP.by_pop(p["munis"]) if y is not x and id(y) not in seen][:4 if close else 8]
    lk = lambda y: link(y) if y["region"] in B.CA_REGIONS else (  # noqa: E731
        f'<a href="{B.ASSETS}{y["path"]}" hreflang="es" lang="es">{E(y["name"])}</a>')
    near_html = "".join(f'<li>{lk(y)} <span class="m">{d} km · {dates_of(y)}</span></li>' for y, d in close)
    big_html = "".join(f'<li>{link(y)} <span class="m">{dates_of(y)}</span></li>' for y in big)
    up = ('<p class="more-l">' + (f'<a href="{B.BASE}{p["path"]}">{E(prov_label(p))}: els {len(p["munis"])} municipis</a> · ' if p["path"] else "")
          + f'<a href="{B.BASE}{r["slug"]}/">Calendari laboral 2027 {names["region_in"]}</a></p>')
    body = (B.section("festivos", f'Festius 2027 {de(name)}', MP.hl_rows(f["hols"]) + loc_html)
            + B.section("claves", f'Què canvien els festius {de(name)}' if ok and wide else f'{E(name)} el 2027', notes(items))
            + B.ad("hub", adsense=False)  # our promos only, as munipages.muni_page (seo/ads.md)
            + B.section("calendario", "Calendari 2027", MP.legend(kinds) + mini_year(f["hols"]), cls="cal")
            + B.section("puentes", f'Ponts 2027 {de(name)}', f'<table class="tbl ptm"><thead><tr><th scope="col">Pont<th scope="col" class="num">Dies de festa'
                        f'<th scope="col">Vacances</thead><tbody>{pts}</tbody></table>')
            + (B.section("cerca", f'A prop {de(name)}', f'<ul class="links">{near_html}</ul>') if close else "")
            + B.section("mas", f'Més municipis {of_place(p)}', f'<ul class="links">{big_html}</ul>{up}'))
    main = f'{hero}<div class="wrap body">{body}</div>'
    if ok and wide:
        d_ = [B.dmon(h["date"]) for h in wide[:3]]
        title = B.pick(60, f"Calendari laboral {nm_t} 2027: festius {join(d_)}", f"Festius {nm_t} 2027: {join(d_)}",
                       f"Calendari laboral {nm_t} 2027", f"Festius {nm_t} 2027")
        nmx = lambda h: f' ({h["name"]})' if h.get("name") else ""  # noqa: E731
        tail = f'Amb els {nb} {names["region_of"]}: {len(f["hols"])} festius, {tn("n_pts", len(f["pts"]))} i {f["lab"]} dies feiners.'
        desc = B.pick(155, f'Festius locals {de(name)} ({prov_name(p)}) el 2027: {join(B.dlong(h["date"]) + nmx(h) for h in wide)}. {tail}',
                      f'Festius locals {de(name)} ({prov_name(p)}) el 2027: {join(B.dlong(h["date"]) for h in wide)}. {tail}',
                      f'Festius locals {de(name)} el 2027: {join(d_)}. {tail}',
                      f'Festius locals {de(name)} el 2027: {join(d_)}. {len(f["hols"])} festius i {f["lab"]} dies feiners.')
    else:
        title = B.pick(60, f"Calendari laboral {nm_t} 2027", f"Festius {nm_t} 2027")
        desc = B.pick(155, f'Calendari laboral 2027 {de(name)} ({prov_name(p)}): festius {names["region_of"]}, ponts i dies '
                           f'feiners. Locals {"per localitat" if ok else "pendents de publicació"}.',
                      f'Calendari laboral 2027 {de(name)}: festius {names["region_of"]} i ponts.')
    desc = desc.replace("..", ".")
    head = B.head_html(title, desc, x["path"], f'{B.SITE}{B.ASSETS}og/{x["region"]}.png',
                       P.ld(P.crumbs_ld(crumbs), P.webpage_ld(title, x["path"], upd_date)), langs=["es", "ca"], index=ok, ads=False)
    write(x["path"], B.page(head, "pg mu", "", main, P.DATA, js=False, lean=True), upd_date, ["es", "ca"])


def prov_page(p, cat, write, REG, UPDATED):
    import munipages as MP
    from muni import fold, short_src
    r = REG[p["region"]]
    names = rn(r)
    st = MP.prov_stats(p)
    munis = sorted(p["munis"], key=lambda y: fold(name_of(y)))
    n, n_ok = len(munis), len(st["ok"])
    pend = n - n_ok
    base = B.region_holidays(P.DATA, r["slug"])
    lab = B.workdays(base)
    place = prov_place(p)
    h1 = f'Festius locals 2027 {"als municipis de " + place if p["uni"] else "a " + place}'
    items = []
    if n_ok:
        top = st["dates"].most_common(5)
        items.append("<b>Els dies més repetits:</b> " + "; ".join(f'{B.dlong(d)}, a {c} municipi{"s" if c != 1 else ""}' for d, c in top) + ".")
        wdc, mo = Counter(), Counter()
        for d, c in st["dates"].items():
            wdc[D(d).weekday()] += c
            mo[D(d).month] += c
        tot = sum(wdc.values())
        items.append(f'<b>Dia de la setmana:</b> {wdc[0] + wdc[4]} dels {tot} dies locals cauen en dilluns o divendres (cap de '
                     f'setmana llarg) i {wdc[5] + wdc[6]} en dissabte o diumenge, sense cap dia lliure de més.')
        m1 = mo.most_common(1)[0]
        items.append(f'<b>El mes amb més festes locals:</b> {B.T["_months"][m1[0] - 1]}, amb {m1[1]}.')
        capx = cat["by_ine"].get(p.get("capital_ine"))
        if capx and capx["ok"]:
            items.append(f'<b>La capital,</b> {link(capx)}: {join(B.dlong(h["date"]) for h in MP.wide_of(capx))}.')
        rng = (f'de {st["labs"][0]} a {st["labs"][-1]} segons el municipi (mediana {st["med"]})' if st["labs"][0] != st["labs"][-1]
               else f'{st["labs"][0]} a tots els municipis publicats')
        items.append(f'<b>Dies feiners</b> amb els locals: {rng}; {lab} només amb els festius {names["region_of"]}.')
    if pend:
        y26 = sorted({(x["src26"] or {}).get("published") for x in munis if not x["ok"] and x["src26"]} - {None})
        items.append(f'<b>Pendents:</b> {pend} municipi{"s" if pend != 1 else ""} sense data oficial per al 2027'
                     + (f'; les del 2026 es van publicar el {B.dmy(y26[0])}' if y26 else "")
                     + ". Les seves pàgines canvien quan surti el butlletí.")
    if st["srcs"]:
        items.append("<b>Font:</b> " + "; ".join(f'<a href="{E(st["urls"].get(s, ""))}" rel="noopener" title="{E(s)}">'
                                                f'{E(short_src(s, s[:60]))}</a>' for s in st["srcs"][:4]) + ".")
    if n_ok:
        lead = (f'<b>{n_ok} de {n} municipis</b> {of_place(p)} tenen publicats els festius locals del 2027'
                + (f'; {pend} continuen pendents.' if pend else ".") + f' S\'hi sumen els {len(base)} {names["region_of"]}.')
    else:
        lead = (f'Els festius locals del 2027 dels {n} municipis {of_place(p)} encara no s\'han publicat al butlletí oficial. '
                f'Mentrestant, valen els {len(base)} festius {names["region_of"]}.')

    def ul(xs):
        return ('<ul class="links" data-sortable>' + "".join(
            f'<li data-a="{E(fold(name_of(x)))}">{link(x)} <span class="m">{dates_of(x)}</span></li>' for x in MP.by_pop(xs)) + "</ul>")
    pub, pen = [x for x in munis if x["ok"]], [x for x in munis if not x["ok"]]
    rows = ((f'<h3 class="h3">Amb festius del 2027 publicats ({len(pub)})</h3>{ul(pub)}' if pub else "")
            + (f'<h3 class="h3">Pendents de publicació ({len(pen)})</h3>{ul(pen)}' if pen else ""))
    az = ('<p class="srt" role="group" aria-label="Ordre"><button type="button" class="btn sm on" data-sort="pop" aria-pressed="true">'
          'Per població</button><button type="button" class="btn sm" data-sort="az" aria-pressed="false">A–Z</button></p>')
    chips = "".join(f'<li class="k-{h["kind"]}">{B.sw(h["kind"])}{B.dmon(h["date"])} · {E(h["name"])}</li>' for h in base)
    crumbs = [(t("spain"), ""), (r["name"], f'{r["slug"]}/'), (prov_label(p), p["path"])]
    upd_date = UPDATED or P.DATA["updated"]
    stats = B.stats_html([(None, f"{n} municipis"), (None, f"{n_ok} publicat{'s' if n_ok != 1 else ''}"),
                          (None, f"{pend} pendent{'s' if pend != 1 else ''}")])
    meta = (f'<p class="upd">Actualitzat: <time datetime="{upd_date}">{B.dmy(upd_date)}</time> · Comunitat: {src_link()}</p>')
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}{chip(p["path"])}'
            + B.hero_grid(f'<h1>{E(h1)}</h1><p class="lead">{lead}</p>', stats + B.search_box("q-prov"), meta) + '</div>')
    body = (B.section("claves", "El que diuen les dates", notes(items))
            + B.ad("hub", adsense=False)  # our promos only, as munipages.prov_page (seo/ads.md)
            + B.section("comunidad", f'Els {len(base)} festius {names["region_of"]}', f'<ul class="dchips">{chips}</ul>'
                        f'<p class="more-l"><a href="{B.BASE}{r["slug"]}/">Calendari laboral 2027 {names["region_in"]}</a></p>')
            + B.section("municipios", f'Els {n} municipis', f'{az}{rows}'))
    main = f'{hero}<div class="wrap body narrow">{body}</div>'
    pn = prov_name(p)
    if n_ok:
        top2 = [B.dmon(d) for d, _ in st["dates"].most_common(2)]
        title = B.pick(60, f'Festius locals 2027 {pn}: {n_ok} municipi{"s" if n_ok != 1 else ""} publicat{"s" if n_ok != 1 else ""}',
                       f'Festius locals 2027 {pn}')
        desc = B.pick(155, f'Festius locals 2027 dels {n} municipis {of_place(p)}: {n_ok} ja publicat{"s" if n_ok != 1 else ""}, '
                           f'els dies més repetits ({join(top2)}) i els {len(base)} festius {names["region_of"]}.',
                      f'Festius locals 2027 dels {n} municipis {of_place(p)}: {n_ok} publicats i els {len(base)} {names["region_of"]}.')
    else:
        title = B.pick(60, f'Festius locals 2027 {pn}: els {n} municipis', f'Festius locals 2027 {pn}')
        desc = B.pick(155, f'Festius locals 2027 dels {n} municipis {of_place(p)}: pendents del butlletí oficial. Mentrestant, '
                           f'els {len(base)} festius {names["region_of"]}.', f'Festius locals 2027 {pn}: pendents del butlletí.')
    desc = desc.replace("..", ".")
    head = B.head_html(title, desc, p["path"], f'{B.SITE}{B.ASSETS}og/{r["slug"]}.png',
                       P.ld(P.crumbs_ld(crumbs), P.webpage_ld(title, p["path"], upd_date)), langs=["es", "ca"], ads=False)
    write(p["path"], B.page(head, "pg", "", main, P.DATA, js=False, lean=True), upd_date, ["es", "ca"])


def write_muni_pages(pages_mod, write):
    """Province pages and a page for every municipality without a rich city page, in the Catalan-speaking comunitats."""
    import munipages as MP
    from muni import catalogue, load
    MP.P = pages_mod
    MP.REG.update({r["slug"]: r for r in pages_mod.DATA["regions"]})
    cat = catalogue()
    a27 = load("locales-2027-all.json") or {}
    upd = a27.get("updated")
    cat["dup_names"] = Counter(x["name"] for x in cat["munis"])
    e27 = a27.get("municipios", {})
    for x in cat["munis"]:
        x["localities"] = (e27.get(x["ine"]) or {}).get("localities") if x["ok"] and x["kind"] == "page" else None
    MP.nearest(cat["munis"])
    for p in cat["provs"]:
        if p["path"] and p["region"] in B.CA_REGIONS:
            prov_page(p, cat, write, MP.REG, upd)
    n = 0
    for x in cat["munis"]:
        if x["kind"] == "page" and x["region"] in B.CA_REGIONS:
            muni_page(x, cat, write, MP.REG, upd)
            n += 1
    print(f"muni · ca · {n} municipality pages")


# ---------------------------------------------------------------- /ca/puentes/

def page_puentes(write, cities):
    import guia
    S = guia.stats()
    nat = [h for h in S["madrid"]["hols"] if h["kind"] == "n"]
    nb = B.all_breaks(nat)
    nkeys = {(it["s"], it["e"], it["cost"]) for it in nb}
    b = guia.best(nb)
    most = max(S.values(), key=lambda s: len(s["pts"]))
    least = min(S.values(), key=lambda s: len(s["pts"]))
    title = "Ponts i festius 2027 per comunitats"
    desc = (f'Ponts del 2027: els estatals i els de cada comunitat, quants dies de festa donen i quins dies cal demanar. '
            f'El millor, {B.drange(b["s"], b["e"])}.')
    desc = desc.replace("..", ".")
    crumbs = [(t("spain"), ""), ("Ponts 2027", "puentes/")]
    upd_date = guia.lastmod(P.DATA["updated"], B.CONTENT_UPDATED)
    hero = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}{chip("puentes/")}<h1>Ponts 2027</h1>'
            + guia.lead(f'Amb els festius estatals, el millor pont del 2027 és <b>{brk(b)}</b>. Cada comunitat hi suma els '
                        f'seus: de {len(least["pts"])} a {len(most["pts"])} ponts segons on treballis.')
            + guia.upd(upd_date) + '</div>')
    nat_sec = B.section("nacionales", "Ponts estatals 2027",
                        f'<table class="tbl pts">{B.pts_head()}<tbody>{"".join(B.pts_row(it) for it in nb)}</tbody></table>'
                        f'<p class="m">Valen a tot Espanya. A cada comunitat canvien segons els seus festius propis.</p>')
    first = [k for k in B.CA_REGIONS] + [k for k in S if k not in B.CA_REGIONS]
    regs = []
    for k in first:
        s = S[k]
        r = s["r"]
        own = [it for it in s["breaks"] if (it["s"], it["e"], it["cost"]) not in nkeys]
        rows = "".join(B.pts_row(it) for it in own) or '<tr><td colspan="3">Els mateixos que els estatals.</td></tr>'
        rb = guia.best(s["breaks"])
        regs.append(f'<details class="rg" id="{k}"><summary><span>{E(r["name"])}</span><span class="m">{tn("n_pts", len(s["pts"]))}'
                    f'{" · el millor: " + B.drange(rb["s"], rb["e"]) if rb else ""}</span></summary><div>'
                    f'<p class="m">Ponts i caps de setmana llargs que donen els seus festius propis:</p>'
                    f'<table class="tbl pts">{B.pts_head()}<tbody>{rows}</tbody></table>'
                    f'<p class="more-l"><a href="{B.BASE}{k}/#puentes">Calendari laboral 2027 {rn(r)["region_in"]}: tots els ponts</a></p>'
                    f'</div></details>')
    reg_sec = B.section("comunidades", "Ponts 2027 per comunitat", "".join(regs))
    how = B.section("como", "Com comptem els ponts", notes([
        "<b>Pont:</b> dies de festa seguits al voltant d'un festiu agafant 1 o 2 dies de vacances (per exemple, el dilluns "
        "entre un diumenge i un dimarts festiu).",
        "<b>Cap de setmana llarg:</b> 3 o més dies de festa seguits sense agafar res, perquè el festiu cau en dilluns o divendres.",
        "<b>Només festius laborals:</b> els del BOE i els de la teva comunitat. Els 2 locals canvien el resultat: els trobaràs "
        f'a la pàgina del teu municipi (<a href="{B.BASE}festivos-locales/">festius locals 2027</a>).',
    ]))
    qas = [("Quants ponts hi ha el 2027?",
            f'Amb els festius estatals, {sum(1 for it in nb if it["cost"])} ponts i {sum(1 for it in nb if not it["cost"])} caps de '
            f'setmana llargs. Amb els de cada comunitat, entre {len(least["pts"])} i {len(most["pts"])} ponts.'),
           ("Hi ha pont de maig el 2027?",
            "No a escala estatal: l'1 de maig de 2027 cau en dissabte. Només n'hi pot haver on una festa local caigui a prop."),
           ("Quin és el millor pont del 2027?", f'{cap(brk(b))}.'),
           ("Quina comunitat té més ponts el 2027?",
            f'{join(s["r"]["name"] for s in S.values() if len(s["pts"]) == len(most["pts"]))}, amb {len(most["pts"])}.')]
    main = f'{hero}<div class="wrap body narrow">{nat_sec}{reg_sec}{B.ad("hub")}{how}{P.faq_html(qas)}</div>'
    lds = [P.crumbs_ld(crumbs), P.webpage_ld(title, "puentes/", upd_date), P.faq_ld(qas)]
    head = B.head_html(title, desc, "puentes/", f"{B.SITE}{B.ASSETS}og/espana.png", P.ld(*lds), langs=["es", "ca"])
    write("puentes/", B.page(head, "pg", "", main, P.DATA, js=False), upd_date, ["es", "ca"])


# ---------------------------------------------------------------- trust pages

def doc_page(write, path, title, desc, h1, body, date):
    import guia
    crumbs = [(t("spain"), ""), (h1, path)]
    main = f'<div class="wrap doc guide">{B.crumbs_html(crumbs)}{chip(path)}<h1>{E(h1)}</h1>{guia.upd(date, src=False)}{body}</div>'
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}og/espana.png",
                       P.ld(P.crumbs_ld(crumbs), P.webpage_ld(title, path, date)), langs=["es", "ca"], ads=False)
    write(path, B.page(head, "pg", "", main, P.DATA, js=False), date, ["es", "ca"])


def trust_pages(write, cities):
    import muni
    src = P.DATA["source"]
    mail = f'<a href="mailto:{B.EMAIL}">{B.EMAIL}</a>'
    date = max(B.CONTENT_UPDATED, "2026-11-10")
    n_pub = sum(1 for x in muni.catalogue()["munis"] if x["ok"]) or len(cities)
    n_all = len(muni.catalogue()["munis"])
    doc_page(write, "sobre/", "Qui fa El Calendario Laboral i d'on surten les dades",
             "El Calendario Laboral és un web independent: festius del 2027 trets del BOE i dels butlletins oficials, amb la "
             "font al costat de cada data.",
             "Qui fa aquest web",
             f'<p>El Calendario Laboral és un web independent fet a València. No és un web oficial ni depèn de cap '
             f'administració.</p>'
             f'<h2>D\'on surten les dades</h2><ul>'
             f'<li><b>Festius estatals i de cada comunitat:</b> la resolució del BOE {src_link()} ({E(src["boe"])}).</li>'
             f'<li><b>Festius locals:</b> el butlletí oficial de la província o de la comunitat (a Catalunya, el DOGC; al '
             f'País Valencià, el DOGV; a les Illes Balears, el BOIB), o l\'acord del ple publicat per l\'ajuntament. Avui hi ha '
             f'{n_pub} de {n_all} municipis amb data oficial del 2027; cadascun enllaça la seva font.</li>'
             f'<li><b>Municipis i població:</b> la relació de municipis de l\'INE i les xifres oficials de població (revisió '
             f'del padró a 1 de gener de 2025), que fem servir per ordenar les llistes i el cercador '
             f'(<a href="https://www.ine.es/dynt3/inebase/es/index.htm?padre=517" rel="noopener">INE</a>).</li>'
             f'<li><b>Municipis propers:</b> la distància entre les coordenades de cada municipi de '
             f'<a href="https://www.wikidata.org/" rel="noopener">Wikidata</a> (CC0).</li>'
             f'</ul><h2>Com treballem</h2><ul>'
             f'<li>Cada data es copia del document oficial i s\'hi enllaça. Si una dada no s\'ha publicat, posem «pendent de '
             f'publicació oficial» i no n\'avancem dates de la premsa ni de l\'any anterior.</li>'
             f'<li>Els ponts i els dies feiners es calculen amb aquestes dates; la regla és a '
             f'<a href="{B.BASE}puentes/">ponts 2027</a>.</li>'
             f'<li>De novembre a gener, quan surten els festius locals, revisem els butlletins sovint. Cada pàgina mostra la '
             f'data de la darrera actualització.</li></ul>'
             f'<h2>Errors i avisos</h2><p>Si veus una data malament o el teu municipi ja ha publicat els festius, escriu a '
             f'{mail} amb l\'enllaç al butlletí o a l\'acord del ple. Ho comprovem amb la font i ho corregim.</p>'
             f'<h2>Com es paga</h2><p>Amb anuncis de Google AdSense. No canvien cap dada. No hi ha comptes ni registre: el que '
             f'tries es desa només al teu navegador (<a href="{B.BASE}privacidad/">privadesa</a>).</p>', date)
    doc_page(write, "contacto/", "Contacte · El Calendario Laboral",
             "Escriu a El Calendario Laboral per corregir una data o avisar dels festius locals del teu municipi.",
             "Contacte",
             f'<p>Correu: {mail}</p>'
             f'<h2>Per corregir una dada</h2><p>Indica la pàgina i l\'enllaç al document oficial (BOE, butlletí de la teva '
             f'comunitat o de la teva província, o acord del ple). Sense font oficial no podem canviar cap data.</p>'
             f'<h2>Per al widget o les dades</h2><p>El <a href="{B.ASSETS}widget/" hreflang="es" lang="es">widget</a> i els '
             f'fitxers CSV i ICS es poden fer servir al teu web enllaçant aquesta pàgina.</p>'
             f'<h2>Qui respon</h2><p>L\'equip d\'El Calendario Laboral, a València. Responem per correu, normalment en pocs '
             f'dies; no hi ha formulari ni desem les teves dades.</p>', date)
    doc_page(write, "aviso-legal/", "Avís legal · El Calendario Laboral",
             "Avís legal d'elcalendariolaboral.es: titular, contacte, condicions d'ús i responsabilitat sobre les dades.",
             "Avís legal",
             f'<h2>Titular</h2><p>{B.HOST} és El Calendario Laboral, projecte independent amb seu a València (Espanya). '
             f'Contacte: {mail}.</p>'
             f'<h2>Objecte</h2><p>Informar dels festius laborals i dels ponts d\'Espanya, amb eines gratuïtes per planificar '
             f'les vacances.</p>'
             f'<h2>Responsabilitat</h2><p>Les dades es prenen de fonts oficials i s\'hi enllacen. Tot i així, la informació és '
             f'orientativa: el text que val és el publicat al butlletí oficial. No responem de decisions preses només amb '
             f'aquest web.</p>'
             f'<h2>Propietat intel·lectual</h2><p>Les dates oficials són informació pública. El disseny, els textos i les '
             f'eines d\'aquest web són del titular; els pots enllaçar i fer servir el widget, citant-ne la font.</p>'
             f'<h2>Enllaços i publicitat</h2><p>El web enllaça a butlletins oficials i a altres llocs que no controlem. Mostra '
             f'anuncis de Google AdSense; les dades que fa servir Google s\'expliquen a la '
             f'<a href="{B.BASE}privacidad/">política de privadesa</a>.</p>'
             f'<h2>Llei aplicable</h2><p>Aquest web es regeix per la llei espanyola, inclosa la Llei 34/2002 de serveis de la '
             f'societat de la informació.</p>', date)
    cell = lambda *xs: "<tr>" + "".join(f"<td>{x}</td>" for x in xs) + "</tr>"  # noqa: E731
    keep = "Fins que l'esborris"
    doc_page(write, "cookies/", "Política de galetes · El Calendario Laboral",
             "Què desa elcalendariolaboral.es al teu navegador (res als servidors) i quines galetes fa servir Google AdSense a "
             "les pàgines amb anuncis.",
             "Galetes",
             '<p>Aquest web no instal·la galetes pròpies ni fa servir analítica.</p>'
             '<h2>El que es desa al teu navegador</h2><table class="tbl"><thead><tr><th scope="col">Clau</th>'
             '<th scope="col">Per a què</th><th scope="col">Durada</th></tr></thead><tbody>'
             + cell("<code>cl27.region</code>", "Obrir el web a la teva comunitat", keep)
             + cell("<code>cl27.zone.*</code>", "La teva illa o zona", keep)
             + cell("<code>cl27.loc.*</code>", "Els festius locals que hi afegeixes", keep)
             + cell("<code>cl27.vac.*</code>", "Els dies de vacances que marques", keep)
             + cell("<code>cl27.n</code>", "Quants dies de vacances planifiques", keep)
             + '</tbody></table><p>És emmagatzematge local (<i>localStorage</i>): no surt del teu dispositiu.</p>'
             '<h2>Galetes de Google a les pàgines amb anuncis</h2><p>La portada, les comunitats, les ciutats i les guies '
             'carreguen Google AdSense. Google i els seus socis poden fer servir galetes (per exemple <code>__gads</code>, '
             '<code>__gpi</code> o <code>IDE</code>) per mostrar anuncis, limitar quantes vegades en veus un i mesurar-los. A la '
             'UE, un avís de consentiment de Google et deixa acceptar, rebutjar o triar abans; la teva tria es desa en galetes de '
             'Google (<code>FCCDCF</code>, <code>FCNEC</code>).</p><p><a href="https://policies.google.com/technologies/cookies?hl=ca" '
             'rel="noopener">Com fa servir Google les galetes</a> · <a href="https://adssettings.google.com/" rel="noopener">'
             'Les teves preferències d\'anuncis</a></p>'
             '<h2>Com canviar-ho</h2><p>Esborra les galetes i les dades d\'aquest lloc al teu navegador: el que s\'hi havia desat '
             'desapareix i l\'avís de consentiment torna a sortir. Les pàgines de municipi i de província, les eines i els textos '
             f'legals no carreguen cap script de Google.</p><p>Més informació a <a href="{B.BASE}privacidad/">privadesa</a>.</p>', date)
