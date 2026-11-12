"""Shared data and code of pack H (online sellers and creators): Etsy fees, KDP printing cost and royalties, KDP cover
size, money formatting in several currencies for the Spanish and English twins.

Ignored by the registry (leading underscore). Each tool's compute must be self-contained, so the JS lives here as
strings that the tool files paste into their compute function, and the tables travel as the tool's `data` (C.d). The
Python twins compute the worked examples of the explanation blocks at build time (same formulas, so text and tool agree).

Sources (checked 12 Nov 2026, "as of November 2026" on the pages):
- Etsy payment processing by bank country: https://help.etsy.com/hc/articles/115015628847
- Etsy regulatory operating fee from 22 Jun 2026 (Spain 0.88 %, France 1.14 %, Italy 0.80 %, UK 0.48 %):
  https://community.etsy.com/forum/announcements-290/topic/regulatory-operating-fee-updates-for-some-markets-181930/
- Etsy title and tag character rules: Etsy Open API v3 spec (createDraftListing: title / tags)
- KDP paperback printing cost: https://kdp.amazon.com/en_US/help/topic/G201834340
- KDP paperback royalty 50/60 % thresholds: https://kdp.amazon.com/en_US/help/topic/G201834330
- KDP eBook list price bands: https://kdp.amazon.com/en_US/help/topic/G200634560 ; delivery costs (updated 21 Apr 2026):
  https://kdp.amazon.com/en_US/help/topic/G200634500
- KDP cover: https://kdp.amazon.com/en_US/help/topic/G201953020
"""

ETSY_FEES = "https://help.etsy.com/hc/articles/115015628847"
ETSY_ROF = "https://community.etsy.com/forum/announcements-290/topic/regulatory-operating-fee-updates-for-some-markets-181930/"
ETSY_API = "https://developers.etsy.com/documentation/reference/"
ETSY_IMG = "https://help.etsy.com/hc/articles/115015663347"
KDP_PRINT = "https://kdp.amazon.com/en_US/help/topic/G201834340"
KDP_ROY = "https://kdp.amazon.com/en_US/help/topic/G201834330"
KDP_EB = "https://kdp.amazon.com/en_US/help/topic/G200634560"
KDP_DEL = "https://kdp.amazon.com/en_US/help/topic/G200634500"
KDP_COVER = "https://kdp.amazon.com/en_US/help/topic/G201953020"
KDP_APLUS = "https://kdp.amazon.com/en_US/help/topic/GCKLH8V7ULLD5EXY"

KDP_EBCOVER = "https://kdp.amazon.com/en_US/help/topic/GZCSY2RL5G699Y4D"
PINTEREST = "https://help.pinterest.com/en/business/article/pinterest-product-specs"
YT_THUMB = "https://support.google.com/youtube/answer/72431"
INSTAGRAM = "https://help.instagram.com/1631821640426723"

# Image sizes (checked 12 Nov 2026): id, platform, label es, label en, width, height, note es, note en
IMG = [
    ("etsy-foto", "Etsy", "Foto de anuncio (4:3)", "Listing photo (4:3)", 2667, 2000,
     "Etsy pide 2000 px o más por lado y la primera foto horizontal o cuadrada; mínimo 635 px; mejor < 1 MB",
     "Etsy asks for 2,000 px or more on each side, first photo landscape or square; 635 px minimum; keep under 1 MB"),
    ("etsy-banner", "Etsy", "Banner grande", "Big banner", 1600, 400, "Mínimo 1200 × 300", "Minimum 1,200 × 300"),
    ("etsy-mini", "Etsy", "Banner mini", "Mini banner", 1600, 213, "Mínimo 1200 × 160", "Minimum 1,200 × 160"),
    ("etsy-logo", "Etsy", "Logo de la tienda", "Shop logo", 500, 500, "", ""),
    ("etsy-perfil", "Etsy", "Foto de perfil", "Profile photo", 400, 400, "", ""),
    ("pin", "Pinterest", "Pin (2:3)", "Pin (2:3)", 1000, 1500, "Los pines más anchos que 2:3 se recortan en el feed",
     "Pins wider than 2:3 may be cropped in the feed"),
    ("ig-post", "Instagram", "Post vertical (4:5)", "Portrait post (4:5)", 1080, 1350, "", ""),
    ("ig-sq", "Instagram", "Post cuadrado", "Square post", 1080, 1080, "", ""),
    ("ig-story", "Instagram", "Historia o reel (9:16)", "Story or reel (9:16)", 1080, 1920, "", ""),
    ("yt-thumb", "YouTube", "Miniatura de vídeo (16:9)", "Video thumbnail (16:9)", 3840, 2160, "Mínimo 640 px de ancho",
     "Minimum 640 px wide"),
    ("yt-short", "YouTube", "Miniatura de Short (9:16)", "Shorts thumbnail (9:16)", 2160, 3840, "Mínimo 640 px de alto",
     "Minimum 640 px tall"),
    ("yt-banner", "YouTube", "Banner del canal", "Channel banner", 2560, 1440,
     "Texto y logo en el centro, 1546 × 423 px, visible en todos los dispositivos",
     "Keep text and logo in the central 1,546 × 423 px, visible on every device"),
    ("kdp-ebook", "Amazon KDP", "Portada de eBook", "eBook cover", 1600, 2560, "Solo la cubierta delantera", "Front cover only"),
    ("aplus-overlay", "Amazon KDP", "A+ imagen con texto encima", "A+ image & text overlay", 1940, 600, "Mínimo 970 × 300; máx. 3 MB",
     "Minimum 970 × 300; max 3 MB"),
    ("aplus-3", "Amazon KDP", "A+ tres imágenes", "A+ three images", 600, 600, "Mínimo 300 × 300; máx. 3 MB", "Minimum 300 × 300; max 3 MB"),
]

IMG_JS = r"""
  /* centre crop of an iw x ih image to the target ratio tw:th, and the resize factor to reach tw x th */
  function crop(iw, ih, tw, th) {
    var R = tw / th, cw, ch;
    if (iw / ih > R) { ch = ih; cw = Math.round(ih * R); } else { cw = iw; ch = Math.round(iw / R); }
    return { cw: cw, ch: ch, x: Math.round((iw - cw) / 2), y: Math.round((ih - ch) / 2), k: tw / cw, lost: 1 - cw * ch / (iw * ih) };
  }
  function cropSvg(iw, ih, c, alt) {
    var s = 300 / Math.max(iw, ih), W = iw * s, Hh = ih * s;
    return '<svg class="ic-p" viewBox="0 0 ' + W.toFixed(1) + ' ' + Hh.toFixed(1) + '" role="img" aria-label="' + alt + '">' +
      '<rect width="' + W.toFixed(1) + '" height="' + Hh.toFixed(1) + '" class="ic-i"/>' +
      '<rect x="' + (c.x * s).toFixed(1) + '" y="' + (c.y * s).toFixed(1) + '" width="' + (c.cw * s).toFixed(1) + '" height="' + (c.ch * s).toFixed(1) + '" class="ic-c"/></svg>';
  }
"""
IMG_CSS = (".ic-p{display:block;width:100%;max-width:320px;height:auto;margin:14px 0}.ic-i{fill:#d9dee5}"
           ".ic-c{fill:#fff;stroke:#c8102e;stroke-width:2;stroke-dasharray:6 4}")


def img_data(lang):
    i = 2 if lang == "es" else 3
    return {r[0]: [r[4], r[5], r[6 if lang == "es" else 7], r[1] + " · " + r[i]] for r in IMG}


def img_table(lang):
    es = lang == "es"
    n = (lambda x: f"{x:,}".replace(",", ".")) if es else (lambda x: f"{x:,}")  # noqa: E731
    head = '<tr><th>Plataforma</th><th>Imagen</th><th class="num">Píxeles</th></tr>' if es else \
        '<tr><th>Platform</th><th>Image</th><th class="num">Pixels</th></tr>'
    rows = "".join(f'<tr><td>{r[1]}</td><td>{r[2] if es else r[3]}</td><td class="num">{n(r[4])} × {n(r[5])}</td></tr>' for r in IMG)
    return f'<table class="tbl"><thead>{head}</thead><tbody>{rows}</tbody></table>'


SYM = {"USD": "$", "EUR": "€", "GBP": "£", "CAD": "C$", "AUD": "A$", "JPY": "¥", "PLN": "zł", "SEK": "kr"}

# ---------------------------------------------------------------- money formatting (JS + Python twin)

FMT_JS = r"""
  var SYM = { USD: '$', EUR: '€', GBP: '£', CAD: 'C$', AUD: 'A$', JPY: '¥', PLN: 'zł', SEK: 'kr' };
  function grp(x, dec, th, dp) {
    var a = (Math.abs(x) + 1e-9).toFixed(dec).split('.'), i = a[0].replace(/\B(?=(\d{3})+(?!\d))/g, th);
    var z = +a.join('') === 0;
    return (x < 0 && !z ? '−' : '') + i + (a[1] ? dp + a[1] : '');
  }
  function fm(x, cur, en, dec) {
    if (dec === undefined) dec = cur === 'JPY' ? 0 : 2;
    var s = SYM[cur] || cur;
    if (!en) return grp(x, dec, '.', ',') + ' ' + s;
    var n = grp(x, dec, ',', '.');
    if (cur === 'PLN' || cur === 'SEK') return n + ' ' + s;
    return n.charAt(0) === '−' ? '−' + s + n.slice(1) : s + n;
  }
  function pc(x, en, dec) { return grp(x, dec === undefined ? 1 : dec, en ? ',' : '.', en ? '.' : ',') + (en ? '%' : ' %'); }
"""


def fm(x, cur="EUR", en=False, dec=None):
    """Python twin of fm() for the explanation texts."""
    dec = (0 if cur == "JPY" else 2) if dec is None else dec
    s = f"{abs(x) + 1e-9:,.{dec}f}"
    if not en:
        s = s.replace(",", " ").replace(".", ",").replace(" ", ".")
    neg = "−" if x < 0 and float(f"{abs(x):.{dec}f}") else ""
    sym = SYM.get(cur, cur)
    if not en:
        return f"{neg}{s} {sym}"
    return f"{neg}{s} {sym}" if cur in ("PLN", "SEK") else f"{neg}{sym}{s}"


def pc(x, en=False, dec=1):
    s = f"{x:,.{dec}f}"
    return s + "%" if en else s.replace(",", " ").replace(".", ",").replace(" ", ".") + " %"


# ---------------------------------------------------------------- Etsy

ETSY_JS = r"""
  /* o: price, ship, wrap, list (listing fee in shop currency), pp (% processing), pf (fixed processing), rof (%),
     ads (%), vat (% on fees), conv (bool), cost, post (postage paid). Transaction 6.5 % of price + shipping + gift wrap;
     processing on the total sale; Offsite Ads capped at 100 USD per order (converted with the listing-fee rate). */
  function etsy(o) {
    var sale = o.price + o.ship + o.wrap, usd = o.list / 0.20;
    var f = { list: o.list, tx: 0.065 * sale, proc: o.pp / 100 * sale + o.pf, rof: o.rof / 100 * sale,
      ads: Math.min(o.ads / 100 * sale, 100 * usd), conv: o.conv ? 0.025 * sale : 0 };
    var base = f.list + f.tx + f.proc + f.rof + f.ads + f.conv, vat = base * o.vat / 100, fees = base + vat;
    var net = sale - fees, profit = net - o.cost - o.post;
    var k = (1 + o.vat / 100) * (0.065 + o.pp / 100 + o.rof / 100 + o.ads / 100 + (o.conv ? 0.025 : 0));
    var fixed = (1 + o.vat / 100) * (o.list + o.pf);
    var be = k < 1 ? (o.cost + o.post + fixed) / (1 - k) - o.ship - o.wrap : NaN;
    return { sale: sale, f: f, base: base, vat: vat, fees: fees, net: net, profit: profit, pct: sale > 0 ? fees / sale * 100 : 0,
      margin: sale > 0 ? profit / sale * 100 : 0, be: be };
  }
"""


def etsy(price, ship, wrap=0.0, list_=0.17, pp=4.0, pf=0.30, rof=0.88, ads=0.0, vat=21.0, conv=False, cost=0.0, post=0.0):
    """Python twin of etsy() (worked examples)."""
    sale = price + ship + wrap
    f = {"list": list_, "tx": 0.065 * sale, "proc": pp / 100 * sale + pf, "rof": rof / 100 * sale,
         "ads": min(ads / 100 * sale, 100 * list_ / 0.20), "conv": 0.025 * sale if conv else 0.0}
    base = sum(f.values())
    v = base * vat / 100
    fees = base + v
    k = (1 + vat / 100) * (0.065 + pp / 100 + rof / 100 + ads / 100 + (0.025 if conv else 0))
    be = (cost + post + (1 + vat / 100) * (list_ + pf)) / (1 - k) - ship - wrap
    return {"sale": sale, "f": f, "base": base, "vat": v, "fees": fees, "net": sale - fees, "profit": sale - fees - cost - post,
            "pct": fees / sale * 100, "be": be}


# ---------------------------------------------------------------- Etsy listing checker

# Rules from the Etsy Open API v3 spec (createDraftListing): title chars = letters, numbers, punctuation, math symbols,
# spaces, ™©®, and % : & + only once each; tags = letters, numbers, spaces, - ' ™©®; title <= 140; 13 tags <= 20 chars.
LISTING_JS = r"""
  function rx(src, fb) { try { return new RegExp(src, 'gu'); } catch (e) { return fb; } }
  var BAD_T = rx('[^\\p{L}\\p{M}\\p{Nd}\\p{P}\\p{Sm}\\p{Zs}\u2122\u00a9\u00ae]', /[$^`<>~|]/g);
  var BAD_G = rx('[^\\p{L}\\p{M}\\p{Nd}\\p{Zs}\\-\'\u2122\u00a9\u00ae]', /[^A-Za-z0-9\u00c0-\u024f \-'\u2122\u00a9\u00ae]/g);
  function uniq(a) { var o = [], s = {}; a.forEach(function (x) { if (!s[x]) { s[x] = 1; o.push(x); } }); return o; }
  function norm(w) { return w.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  /* -> {issues: [[level e|w, code, arg]], tlen, words, tags: [[tag, len, bad]]} */
  function checkListing(title, tagsRaw, STOP) {
    var is = [], t = String(title || '').replace(/\s+/g, ' ').trim(), tlen = Array.from(t).length;
    if (!tlen) is.push(['e', 'tEmpty']);
    if (tlen > 140) is.push(['e', 'tLong', tlen - 140]);
    var bad = uniq(t.match(BAD_T) || []);
    if (bad.length) is.push(['e', 'tChars', bad.join(' ')]);
    ['%', ':', '&', '+'].forEach(function (c) { var k = t.split(c).length - 1; if (k > 1) is.push(['e', 'tOnce', c + ' ×' + k]); });
    var words = t.split(/[\s,.;:|\/\-–—()&+!?¡¿"]+/).filter(function (w) { return w; });
    var caps = words.filter(function (w) { return w.length > 1 && w === w.toUpperCase() && w !== w.toLowerCase(); });
    if (caps.length > 3) is.push(['w', 'tCaps', caps.length]);
    var cnt = {}, rep = [];
    words.forEach(function (w) { var k = norm(w); if (k.length > 2 && !STOP[k]) cnt[k] = (cnt[k] || 0) + 1; });
    Object.keys(cnt).forEach(function (k) { if (cnt[k] > 1) rep.push(k + ' ×' + cnt[k]); });
    if (rep.length) is.push(['w', 'tRep', rep.join(', ')]);
    if (words.length > 15) is.push(['w', 'tWords', words.length]);
    var raw = String(tagsRaw || '').split(/[,\n;]+/).map(function (x) { return x.replace(/\s+/g, ' ').trim(); }).filter(function (x) { return x; });
    var tags = raw.map(function (g) { var b = uniq(g.match(BAD_G) || []); return [g, Array.from(g).length, b.join(' ')]; });
    if (!tags.length) is.push(['w', 'gNone']);
    if (tags.length > 13) is.push(['e', 'gMany', tags.length]);
    else if (tags.length && tags.length < 13) is.push(['w', 'gFew', 13 - tags.length]);
    var longT = tags.filter(function (x) { return x[1] > 20; }).map(function (x) { return x[0]; });
    if (longT.length) is.push(['e', 'gLong', longT.join(', ')]);
    var badT = tags.filter(function (x) { return x[2]; }).map(function (x) { return x[0] + ' (' + x[2] + ')'; });
    if (badT.length) is.push(['e', 'gChars', badT.join(', ')]);
    var seen = {}, dup = [];
    tags.forEach(function (x) { var k = norm(x[0]); if (seen[k]) dup.push(x[0]); seen[k] = 1; });
    if (dup.length) is.push(['e', 'gDup', uniq(dup).join(', ')]);
    var one = tags.filter(function (x) { return x[0].indexOf(' ') < 0; }).length;
    if (one > 3) is.push(['w', 'gOne', one]);
    return { issues: is, tlen: tlen, words: words.length, tags: tags };
  }
"""

# ---------------------------------------------------------------- KDP

# Marketplaces: id, label, currency, printing-cost group. Paperback VAT added on top of the list price (books rate of
# the marketplace country) for the "shop price" line; None = no VAT line.
KDP_MK = [
    ("es", "Amazon.es", "EUR", "eu", 4), ("de", "Amazon.de", "EUR", "eu", 7), ("fr", "Amazon.fr", "EUR", "eu", 5.5),
    ("it", "Amazon.it", "EUR", "eu", 4), ("nl", "Amazon.nl", "EUR", "eu", 9), ("com", "Amazon.com", "USD", "com", None),
    ("uk", "Amazon.co.uk", "GBP", "uk", 0), ("ca", "Amazon.ca", "CAD", "ca", None), ("au", "Amazon.com.au", "AUD", "au", None),
    ("jp", "Amazon.co.jp", "JPY", "jp", None), ("pl", "Amazon.pl", "PLN", "pl", 5), ("se", "Amazon.se", "SEK", "se", 6),
]
# Printing cost (KDP G201834340), per group:
#   bw: [fixed 24-110 pages regular, same large, fixed 110-828 regular=large, per page regular, per page large]
#   pc: [fixed 24-40 regular, same large, fixed 42-828, per page regular, per page large]
#   sc: [fixed 72-600, per page regular, per page large]  (no standard color on Amazon.com.au)
KDP_COST = {
    "com": {"bw": [2.30, 2.84, 1.00, 0.012, 0.017], "pc": [3.60, 4.20, 1.00, 0.065, 0.08], "sc": [1.00, 0.0255, 0.0402]},
    "ca": {"bw": [2.99, 3.53, 1.26, 0.016, 0.021], "pc": [4.66, 5.26, 1.26, 0.085, 0.10], "sc": [1.26, 0.037, 0.052]},
    "uk": {"bw": [1.93, 2.15, 0.85, 0.010, 0.012], "pc": [2.59, 3.24, 0.85, 0.0435, 0.0598], "sc": [0.85, 0.020, 0.027]},
    "eu": {"bw": [2.05, 2.48, 0.75, 0.012, 0.016], "pc": [2.85, 3.61, 0.75, 0.0525, 0.0715], "sc": [0.75, 0.024, 0.035]},
    "pl": {"bw": [9.58, 11.61, 3.51, 0.056, 0.075], "pc": [12.86, 15.32, 3.51, 0.267, 0.337], "sc": [3.51, 0.112, 0.164]},
    "se": {"bw": [22.84, 27.67, 8.37, 0.134, 0.179], "pc": [30.65, 36.51, 8.37, 0.636, 0.804], "sc": [8.37, 0.268, 0.3691]},
    "au": {"bw": [4.74, 5.28, 2.42, 0.022, 0.027], "pc": [5.82, 6.42, 2.42, 0.085, 0.100], "sc": None},
    "jp": {"bw": [422, 530, 206, 2, 3], "pc": [475, 475, 206, 4, 5], "sc": [206, 3.50, 4.50]},
}
# 60 % royalty from this list price up (below it: 50 %), KDP G201834330
KDP_60 = {"com": 9.99, "eu": 9.99, "uk": 7.99, "ca": 13.99, "au": 13.99, "jp": 1000, "pl": 40, "se": 110}
# eBooks (G200634560 / G200634500): 70 % band, delivery cost per MB, 35 % minimum by file size (<3, 3-10, >=10 MB), max;
# VAT included in the list price and removed before the royalty (books rate of the marketplace country).
KDP_EBOOK = {
    "com": {"band": [2.99, 12.99], "mb": 0.15, "min35": [0.99, 1.99, 2.99], "max": 200, "vat": 0},
    "uk": {"band": [1.77, 12.99], "mb": 0.10, "min35": [0.77, 1.25, 1.49], "max": 150, "vat": 0},
    "eu": {"band": [2.69, 12.99], "mb": 0.12, "min35": [0.89, 1.79, 2.69], "max": 215, "vat": None},
    "ca": {"band": [2.99, 12.99], "mb": 0.15, "min35": [0.99, 1.99, 2.99], "max": 200, "vat": 0},
    "au": {"band": [3.99, 15.99], "mb": 0.15, "min35": [0.99, 1.99, 3.99], "max": 220, "vat": 10},
}
EB_VAT_EU = {"es": 4, "de": 7, "fr": 5.5, "it": 4, "nl": 9}
# KDP paperback trim sizes (inches); large trim = wider than 6.12 in or taller than 9 in.
TRIMS = [(5, 8), (5.06, 7.81), (5.25, 8), (5.5, 8.5), (6, 9), (6.14, 9.21), (6.69, 9.61), (7, 10), (7.44, 9.69), (7.5, 9.25),
         (8, 10), (8.25, 6), (8.25, 8.25), (8.5, 8.5), (8.5, 11), (8.27, 11.69)]
PAGES = {"bw": (24, 828), "cr": (24, 776), "sc": (72, 600), "pc": (24, 828)}  # cream = black ink on cream paper
SPINE = {"bw": 0.002252, "cr": 0.0025, "sc": 0.002252, "pc": 0.002347}  # inches per page (G201953020)


def kdp_data():
    return {"mk": {m: {"cur": c, "g": g, "vat": v, "lab": lab} for m, lab, c, g, v in KDP_MK}, "cost": KDP_COST, "t60": KDP_60, "eb": KDP_EBOOK,
            "ebvat": EB_VAT_EU, "pages": PAGES}


def trim_label(w, h, en=False):
    n = lambda x: (f"{x:g}" if en else f"{x:g}".replace(".", ","))  # noqa: E731
    mm = f"{round(w * 25.4)} × {round(h * 25.4)} mm"
    a4 = " · A4" if (w, h) == (8.27, 11.69) else ""
    return f"{n(w)} × {n(h)} in · {mm}{a4}" if en else f"{n(w)} × {n(h)} pulgadas · {mm}{a4}"


def trim_value(w, h):
    return f"{w:g}x{h:g}"


def is_large(w, h):
    return w > 6.12 or h > 9


KDP_JS = r"""
  /* printing cost of a paperback: mk group g, ink bw|cr|sc|pc, pages, large trim */
  function kdpCost(D, g, ink, pages, large) {
    var c = D.cost[g], t;
    if (ink === 'cr') ink = 'bw';
    if (ink === 'sc') { t = c.sc; return t ? t[0] + pages * (large ? t[2] : t[1]) : NaN; }
    t = c[ink];
    var small = ink === 'bw' ? (g === 'au' ? 108 : 110) : 40;
    return pages <= small ? (large ? t[1] : t[0]) : t[2] + pages * (large ? t[4] : t[3]);
  }
  function kdpPb(D, g, ink, pages, large, price) {
    var cost = kdpCost(D, g, ink, pages, large), t60 = D.t60[g], rate = price >= t60 ? 0.6 : 0.5;
    var min = cost / 0.5 < t60 ? cost / 0.5 : Math.max(t60, cost / 0.6);
    return { cost: cost, rate: rate, roy: rate * price - cost, min: Math.ceil(min * 100 - 1e-6) / 100, t60: t60,
      at60: 0.6 * t60 - cost, ed: 0.4 * price - cost };
  }
"""


COVER_JS = r"""
  /* KDP paperback cover: bleed 0.125 in on the outside edges; spine = pages x paper factor (inches) */
  var SPF = { bw: 0.002252, cr: 0.0025, sc: 0.002252, pc: 0.002347 }, PGL = { bw: [24, 828], cr: [24, 776], sc: [72, 600], pc: [24, 828] };
  function cover(w, h, pages, paper) {
    var sp = pages * SPF[paper];
    return { sp: sp, W: 0.25 + w * 2 + sp, Ht: h + 0.25, text: pages >= 79 };
  }
  /* to-scale sketch: bleed (outer), trim, spine band, dashed safe areas 0.125 in inside the trim */
  function coverSvg(w, h, r, L) {
    var k = 40, W = r.W * k, Hh = r.Ht * k, b = 0.125 * k, s = r.sp * k, x1 = b + w * k, x2 = x1 + s, zw = (w - 0.25) * k;
    var R = function (x, y, ww, hh, c) { return '<rect x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" width="' + ww.toFixed(1) + '" height="' + hh.toFixed(1) + '" class="' + c + '"/>'; };
    var T = function (x, y, txt, rot) { return '<text x="' + x.toFixed(1) + '" y="' + y.toFixed(1) + '" text-anchor="middle"' + (rot ? ' transform="rotate(90 ' + x.toFixed(1) + ' ' + y.toFixed(1) + ')"' : '') + '>' + txt + '</text>'; };
    return '<svg class="kc" viewBox="-2 -2 ' + (W + 4).toFixed(1) + ' ' + (Hh + 4).toFixed(1) + '" role="img" aria-label="' + L.alt + '">' +
      R(0, 0, W, Hh, 'kc-b') + R(b, b, W - 2 * b, Hh - 2 * b, 'kc-t') + R(x1, b, s, Hh - 2 * b, 'kc-s') +
      R(2 * b, 2 * b, zw, Hh - 4 * b, 'kc-z') + R(x2 + b, 2 * b, zw, Hh - 4 * b, 'kc-z') +
      T(b + w * k / 2, Hh / 2, L.back) + T(x2 + w * k / 2, Hh / 2, L.front) + (s > 16 ? T(x1 + s / 2, Hh / 2, L.spine, true) : '') +
      '</svg>';
  }
"""
COVER_CSS = (".kc{display:block;width:100%;max-width:720px;height:auto;margin:16px 0;font:600 15px system-ui,sans-serif}"
             ".kc-b{fill:#f6d5d9;stroke:#c8102e;stroke-width:1}.kc-t{fill:#fff;stroke:#333;stroke-width:1}"
             ".kc-s{fill:#e8eef6;stroke:#0b4f8c;stroke-width:1}.kc-z{fill:none;stroke:#0b4f8c;stroke-width:1;stroke-dasharray:4 3}"
             ".kc text{fill:#333}.kc-leg{display:flex;flex-wrap:wrap;gap:6px 16px;list-style:none;padding:0;font-size:14px}"
             ".kc-leg i{display:inline-block;width:14px;height:10px;margin-right:6px;vertical-align:middle}")


def cover(w, h, pages, paper):
    sp = pages * SPINE[paper]
    return {"sp": sp, "W": 0.25 + 2 * w + sp, "H": h + 0.25}


def kdp_cost(g, ink, pages, large):
    c = KDP_COST[g]
    ink = "bw" if ink == "cr" else ink
    if ink == "sc":
        t = c["sc"]
        return t[0] + pages * (t[2] if large else t[1])
    t = c[ink]
    small = (108 if g == "au" else 110) if ink == "bw" else 40
    return (t[1] if large else t[0]) if pages <= small else t[2] + pages * (t[4] if large else t[3])


def kdp_pb(g, ink, pages, large, price):
    cost = kdp_cost(g, ink, pages, large)
    rate = 0.6 if price >= KDP_60[g] else 0.5
    return {"cost": cost, "rate": rate, "roy": rate * price - cost}
