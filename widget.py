"""Embeddable widget, Spanish only, called by pages.write_pages:

    /widget/                    picker (comunidad, municipio or isla), preview and the code to copy
    /widget/embed/<key>/        what the iframe loads: one comunidad, island or city. Standalone HTML, a few KB, inline
                                CSS and JS, no external request, no ads; noindex, canonical to the region or city page

key = <comunidad> | <comunidad>-<isla> (zones that add a holiday: Canarias islands, Arán) | <comunidad>-<ciudad>
(the cities with published local holidays). The credit link "Calendario laboral 2027 · elcalendariolaboral.es" is a
plain <a> in every embed and in the copied code, outside the iframe.
"""
import json

import build as B
from build import E

ONLY = ["es"]
CREDIT = "Calendario laboral 2027 · elcalendariolaboral.es"
KIND_CSS = {"n": ("#f4b8b1", "#dc8479"), "r": ("#f6d27a", "#d4a234"), "i": ("#a9dfd6", "#4fae9f"), "l": ("#cbbdf5", "#9580e3")}
SNIPPET = ('<iframe src="{src}" title="{title}" width="100%" height="{h}" '
           'style="max-width:600px;min-width:280px;border:1px solid #d5dae1;border-radius:6px" loading="lazy"></iframe>\n'
           '<p style="margin:4px 0 0;font-size:13px"><a href="{href}">' + CREDIT + '</a></p>')
LINK = '<a href="{href}">{title}</a>'
DEFAULT = "madrid"

CSS = ("*{box-sizing:border-box}html,body{height:100%;margin:0}"
       "body{font:400 14px/1.4 system-ui,-apple-system,'Segoe UI',Roboto,sans-serif;color:#1b1f24;background:#fff;"
       "font-variant-numeric:tabular-nums;-webkit-text-size-adjust:100%}"
       ".w{display:flex;flex-direction:column;height:100%;max-width:600px;padding:12px 14px 10px}"
       "h1{display:flex;align-items:center;gap:8px;margin:0;font-size:16px;line-height:1.25}"
       "h1 i{flex:none;width:10px;height:10px;border-radius:2px;background:#c8102e}"
       ".nx{margin:4px 0 8px;font-size:13px;color:#5b6472}.nx b{color:#1b1f24;font-weight:600}"
       "ol{flex:1;min-height:0;overflow:auto;list-style:none;margin:0;padding:0;border-top:1px solid #e6e9ee}"
       "li{display:flex;gap:8px;align-items:baseline;padding:5px 4px;border-bottom:1px solid #e6e9ee}"
       "li:before{content:'';flex:none;width:9px;height:9px;border:1px solid;border-radius:2px;transform:translateY(1px)}"
       + "".join(f".{k}:before{{background:{bg};border-color:{bd}}}" for k, (bg, bd) in KIND_CSS.items())
       + ".we:before{background:transparent;border-width:2px}"
       "time{flex:none;width:84px;font-weight:600}.we time{font-weight:400;color:#5f6774}"
       "li.on{background:#eaf1f8}.z{color:#5b6472}"
       ".cr{margin:8px 0 0;font-size:12px}.cr a{color:#0b4f8c;text-underline-offset:2px}")

# next holiday from the viewer's date; without JS the line shows the first holiday of the year
JS = ("(function(){var d=new Date(),p=function(n){return(n<10?'0':'')+n},t=d.getFullYear()+'-'+p(d.getMonth()+1)+'-'+p(d.getDate()),"
      "l=document.querySelectorAll('li[data-d]'),x=document.getElementById('nx');"
      "for(var i=0;i<l.length;i++){var s=l[i].getAttribute('data-d');if(s<t)continue;"
      "var n=Math.round((Date.parse(s)-Date.parse(t))/864e5),b=document.createElement('b');l[i].className+=' on';"
      "b.textContent=l[i].querySelector('time').textContent;x.textContent='Próximo festivo: ';x.appendChild(b);"
      "x.appendChild(document.createTextNode(' · '+l[i].querySelector('span').textContent+' · '+(n===0?'hoy':n===1?'mañana':'faltan '+n+' días')));return}"
      "x.hidden=true})();")


def height(n):
    """iframe height for n lines: one line per holiday at 280-600 px (a long name wraps; the list then scrolls)."""
    return 112 + 29 * n


def embed_html(title, place, hols, href, extra=""):
    items = "".join(f'<li class="{h["kind"]}{" we" if B._d(h["date"]).weekday() >= 5 else ""}" data-d="{h["date"]}">'
                    f'<time datetime="{h["date"]}">{B.dshort(h["date"])}</time><span>{E(h["name"])}</span></li>' for h in hols) + extra
    first = hols[0]
    return (f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>{E(title)}</title>\n'
            f'<meta name="robots" content="noindex">\n<link rel="canonical" href="{href}">\n<style>{CSS}</style>\n</head>\n'
            f'<body>\n<div class="w"><h1><i aria-hidden="true"></i>Festivos 2027 · {E(place)}</h1>'
            f'<p class="nx" id="nx">Próximo festivo: <b>{B.dshort(first["date"])}</b> · {E(first["name"])}</p>'
            f'<ol>{items}</ol>'
            f'<p class="cr"><a href="{href}" target="_blank" rel="noopener">{CREDIT}</a></p></div>\n'
            f'<script>{JS}</script>\n</body>\n</html>\n')


def entries(data, cities):
    """[(key, region, label in the municipio picker or None, place, holidays, href, extra line)] in picker order."""
    out = []
    for r in data["regions"]:
        slug = r["slug"]
        hols = B.region_holidays(data, slug)
        extra = ('<li class="i z"><time>+1</time><span>Fiesta de tu isla</span></li>' if slug == "canarias" else "")
        out.append((slug, r, None, r["name"], hols, B.URL + f"{slug}/", extra))
        for o in data["zones"].get(slug, {}).get("options", []):
            if "add" in o:
                kind = "Isla" if slug == "canarias" else "Zona"
                out.append((f'{slug}-{o["slug"]}', r, f'{o["name"]} ({kind.lower()})', o["name"],
                            B.region_holidays(data, slug, o["slug"]), B.URL + f"{slug}/", ""))
        for x in sorted((x for x in cities if x["r"]["slug"] == slug), key=lambda x: x["title_name"]):
            out.append((f'{slug}-{x["slug"]}', r, x["title_name"], x["title_name"], x["hols"], B.URL + x["path"], ""))
    keys = [e[0] for e in out]
    assert len(keys) == len(set(keys)), "widget: repeated embed key"
    return out


def of_place(r, label, place):
    return f"de {place}" if label else B.R(r)["region_of"]


def widget_page(es, write):
    by = {}
    for key, r, label, place, hols, href, extra in es:
        n = len(hols) + (1 if extra else 0)
        by[key] = {"src": f"{B.SITE}{B.ASSETS}widget/embed/{key}/", "h": height(n), "href": href,
                   "title": f"Calendario laboral 2027 {of_place(r, label, place)}"}
    groups = {}
    for key, r, label, *_ in es:
        if label:
            groups.setdefault(r["slug"], []).append([key, label])
    d0 = by[DEFAULT]
    reg = "".join(f'<option value="{x["slug"]}"{" selected" if x["slug"] == DEFAULT else ""}>{E(x["name"])}</option>' for x in B.REGIONS)
    city = f'<option value="{DEFAULT}">Toda la comunidad</option>' + "".join(f'<option value="{k}">{E(lab)}</option>' for k, lab in groups.get(DEFAULT, []))
    pickers = (f'<div class="pickers"><div class="field"><label for="wreg">{B.t("region_label")}</label><select id="wreg">{reg}</select></div>'
               f'<div class="field"><label for="wcity">Municipio o isla</label><select id="wcity">{city}</select></div></div>')
    code = E(SNIPPET.format(**d0))
    link = E(LINK.format(**d0))
    body = (f'<div class="wg"><div class="wg-p"><iframe id="wprev" src="{B.ASSETS}widget/embed/{DEFAULT}/" title="{E(d0["title"])}" '
            f'height="{d0["h"]}" loading="lazy"></iframe></div>'
            f'<div class="wg-c"><label for="wcode">Código para tu web</label><textarea id="wcode" rows="8" readonly spellcheck="false">{code}</textarea>'
            f'<div class="tools"><button class="btn p" type="button" data-copy="wcode">Copiar código</button></div>'
            f'<label for="wlink">Solo enlace (sin iframe)</label><textarea id="wlink" rows="2" readonly spellcheck="false">{link}</textarea>'
            f'<div class="tools"><button class="btn" type="button" data-copy="wlink">Copiar enlace</button></div></div></div>')
    path = "widget/"
    h1 = "Calendario laboral 2027 para tu web"
    crumbs = [(B.t("spain"), ""), ("Widget para tu web", path)]
    ctx = '<p class="ctx">Gratis · sin anuncios ni cookies · 280–600 px</p>'
    cfg = json.dumps({"by": by, "groups": groups, "snippet": SNIPPET, "link": LINK, "base": f"{B.ASSETS}widget/embed/"},
                     ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    script = (f'<script id="wg-data" type="application/json">{cfg}</script>\n<script>{PAGE_JS}</script>')
    main = (f'<div class="hero wrap">{B.crumbs_html(crumbs)}<h1>{E(h1)}</h1>{ctx}{pickers}</div>'
            f'<div class="wrap body"><section class="sec" id="widget" aria-label="Widget">{body}</section></div>{script}')
    title = "Calendario laboral 2027 para tu web: widget gratis"
    desc = ("Pon el calendario laboral 2027 de tu comunidad o tu ciudad en tu web: un widget gratis, ligero y sin anuncios, "
            "con los festivos oficiales del BOE.")
    import pages
    lds = pages.ld(pages.crumbs_ld(crumbs), {"@type": "WebApplication", "name": h1, "url": B.URL + path, "applicationCategory": "UtilitiesApplication",
                                             "operatingSystem": "Web", "inLanguage": "es-ES", "isAccessibleForFree": True,
                                             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}, "description": desc})
    head = B.head_html(title, desc, path, f"{B.SITE}{B.ASSETS}og/espana.png", lds, langs=ONLY)
    write(path, B.page(head, "pg wgt", "", main, B_DATA, js=False), B_DATA["updated"], ONLY)


PAGE_JS = """(function(){var C=JSON.parse(document.getElementById('wg-data').textContent),$=function(i){return document.getElementById(i)},
reg=$('wreg'),city=$('wcity'),prev=$('wprev'),code=$('wcode'),link=$('wlink');
function fill(t,d){return t.replace(/\\{(\\w+)\\}/g,function(m,k){return d[k]!=null?String(d[k]).replace(/"/g,'&quot;'):m})}
function show(k){var d=C.by[k];if(!d)return;prev.src=C.base+k+'/';prev.height=d.h;prev.title=d.title;code.value=fill(C.snippet,d);link.value=fill(C.link,d);
try{history.replaceState(null,'','#'+k)}catch(e){}}
function cities(r,sel){var o=[new Option('Toda la comunidad',r)];(C.groups[r]||[]).forEach(function(x){o.push(new Option(x[1],x[0]))});
city.innerHTML='';o.forEach(function(x){city.appendChild(x)});city.value=sel||r;city.disabled=o.length<2}
reg.addEventListener('change',function(){cities(reg.value);show(reg.value)});
city.addEventListener('change',function(){show(city.value)});
var h=location.hash.slice(1);if(C.by[h]){var r=Object.keys(C.groups).filter(function(g){return C.groups[g].some(function(x){return x[0]===h})})[0]||h;reg.value=r;cities(r,h);show(h)}else cities(reg.value);
var tt;function toast(m){var t=$('toast');t.textContent=m;t.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){t.classList.remove('on')},2200)}
Array.prototype.forEach.call(document.querySelectorAll('[data-copy]'),function(b){b.addEventListener('click',function(){var a=$(b.getAttribute('data-copy'));
function done(){toast('Copiado')}function old(){a.focus();a.select();try{document.execCommand('copy');done()}catch(e){}}
if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(a.value).then(done,old);else old()})});
Array.prototype.forEach.call([code,link],function(a){a.addEventListener('focus',function(){a.select()})});})();"""

B_DATA = None


def write_pages(data, write, cities):
    global B_DATA
    B_DATA = data
    es = entries(data, cities)
    for key, r, label, place, hols, href, extra in es:
        d = B.ROOT / "widget" / "embed" / key
        d.mkdir(parents=True, exist_ok=True)
        title = f"Calendario laboral 2027 {of_place(r, label, place)}"
        (d / "index.html").write_text(embed_html(title, place, hols, href, extra), "utf-8", newline="\n")
    widget_page(es, write)
