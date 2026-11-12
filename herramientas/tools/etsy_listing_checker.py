"""Etsy listing checker: title (140 characters, allowed characters, % : & + once, repeated words, caps) and tags (13, 20
characters, allowed characters, duplicates). Spanish twin: revisar_anuncio_etsy.py. Rules: Etsy Open API v3."""
from herramientas.tools import _sellers as S

STOP = "the and for with of a an in on to or your my by from".split()

MSG = {
    "tEmpty": "Type the title.",
    "tLong": "Title: {} characters too many (140 max).",
    "tChars": "Title: Etsy does not accept {}.",
    "tOnce": "Title: {} — Etsy allows each of % : & + only once.",
    "tCaps": "{} words in capitals: keep it to one or two.",
    "tRep": "Repeated words in the title: {}.",
    "tWords": "{} words: phones show only the first few, so lead with what the item is.",
    "gNone": "Paste your tags, separated by commas.",
    "gMany": "{} tags: the limit is 13.",
    "gFew": "{} tag slots unused: fill all 13.",
    "gLong": "Over 20 characters: {}.",
    "gChars": "Tags with characters Etsy rejects: {}.",
    "gDup": "Duplicate tags: {}.",
    "gOne": "{} one-word tags: 2-3 word phrases match real searches better.",
}

EX_T = "Personalized Mug with Name, Custom Coffee Mug with Name, Gift for Mom, Ceramic Mug 11 oz"
EX_G = "personalized mug, custom name mug, gift for mom, ceramic coffee mug, mothers day gift idea, mug"


def blocks(ctx):
    return [
        ("What it checks", """
<p>Paste the title and tags exactly as you will upload them. The checker applies the rules Etsy uses to reject a listing
and flags in red anything it will not save: a title over <b>140 characters</b>, characters Etsy does not allow (such as
<code>$</code>, <code>^</code> or emoji), a second <b>%</b>, <b>:</b>, <b>&amp;</b> or <b>+</b>, more than <b>13 tags</b>,
tags over <b>20 characters</b>, or tags with anything other than letters, numbers, spaces, hyphens and apostrophes. In
yellow, what Etsy accepts but costs you reach: repeated title words, shouting capitals, unused tag slots, duplicates and
one-word tags.</p>"""),
        ("A worked example", f"""
<p>A typical first listing: <i>{EX_T}</i>. It is {len(EX_T)} characters and 16 words, so it fits, but "mug" appears three
times and "name" twice. Repeating words no longer helps on Etsy: search reads the title, tags, category and attributes
together, and a word that is already there once gains nothing from a second copy. A tighter version: <i>Personalized Name
Mug, Ceramic 11 oz Coffee Cup, Gift for Mom or Mother's Day</i>, with the variants ("custom coffee mug", "mom mug gift")
moved to tags.</p>
<p>The tags, <i>{EX_G}</i>, leave seven of thirteen slots empty, "mothers day gift idea" is 21 characters so Etsy rejects
it ("mothers day mug" fits), and the last one is a single word that competes with every mug on the site. Treat each tag as
a full search someone types: "name mug for kids", "grandma mug gift", "wedding guest mug". Use all thirteen and skip the
category, which Etsy already counts.</p>"""),
        ("Etsy's exact rules", f"""
<p>According to the <a href="{S.ETSY_API}" rel="noopener">Etsy Open API v3 reference</a>, a valid title contains only
letters, numbers, punctuation, mathematical symbols, spaces and ™ © ®, and the characters %, :, &amp; and + may appear only
once each. Tags take only letters, numbers, spaces, hyphens, apostrophes and ™ © ®: no full stops, slashes or hashes. These
are technical limits, not ranking advice: break them and the listing will not save or the tag is refused.</p>
<p>The repeated-word check ignores case, accents and small words such as "the", "for" and "with". If a word appears twice
because it belongs to two different searches, the warning is only advice: your call.</p>"""),
    ]


FAQ = [
    ("How long can an Etsy title be?",
     "140 characters including spaces. Mobile search results show only the first few words, so start with what the item is."),
    ("How many tags can an Etsy listing have?",
     "13, each up to 20 characters. Multi-word phrases are allowed and usually work better than single words."),
    ("Why won't Etsy save my title?",
     "Usually a second %, :, &amp; or + (each is allowed once), a symbol such as $ or an emoji, or more than 140 characters."),
    ("Should I repeat keywords in my Etsy title?",
     "No. Etsy matches the title together with tags, category and attributes; repeating a word does not make it more relevant "
     "and uses space another search phrase could fill."),
    ("Do tags have to match the title?",
     "No. Keep the essentials in the title and use tags for synonyms, occasions and variants that do not fit up there."),
]

JS = r"""
function (v, H, C) {
""" + S.LISTING_JS + r"""
  var STOP = {}; C.d.stop.forEach(function (w) { STOP[w] = 1; });
  var M = C.d.msg, r = checkListing(v.title, v.tags, STOP);
  var ne = r.issues.filter(function (x) { return x[0] === 'e'; }).length, nw = r.issues.length - ne;
  var li = r.issues.map(function (x) {
    return '<li class="ck-' + x[0] + '">' + H.esc(M[x[1]].replace('{}', x[2] === undefined ? '' : x[2])) + '</li>';
  }).join('');
  var chips = r.tags.map(function (g) {
    return '<li class="' + (g[1] > 20 || g[2] ? 'ck-e' : '') + '">' + H.esc(g[0]) + ' <b>' + g[1] + '</b></li>';
  }).join('');
  return {
    label: 'Listing check', big: ne ? ne + (ne === 1 ? ' error' : ' errors') : (nw ? 'Can be better' : 'Ready'),
    sub: nw + (nw === 1 ? ' warning' : ' warnings'),
    rows: [['Title', r.tlen + ' / 140'], ['Words', r.words], ['Tags', r.tags.length + ' / 13']],
    html: (li ? '<ul class="ck">' + li + '</ul>' : '') + (chips ? '<ul class="ck-g">' + chips + '</ul>' : ''),
    n: { e: ne, w: nw, tlen: r.tlen, tags: r.tags.length, codes: r.issues.map(function (x) { return x[1]; }).join(' ') }
  };
}
"""

TOOL = {
    "slug": "etsy-listing-checker",
    "lang": "en",
    "twin": "revisar-anuncio-etsy",
    "cat": "sellers",
    "icon": "list-check",
    "order": 20,
    "name": "Etsy listing checker",
    "k": "etsy title tags seo characters limit",
    "title": "Etsy Title & Tag Checker: 140 Characters, 13 Tags",
    "desc": "Check an Etsy listing before you publish: 140-character title, % : & used once, 13 tags of 20 characters, banned symbols and repeated words.",
    "h1": "Etsy title and tag checker",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "title", "type": "text", "label": "Title", "value": EX_T, "w": "xl"},
        {"id": "tags", "type": "text", "label": "Tags (commas)", "value": EX_G, "w": "xl"},
    ],
    "data": {"stop": STOP, "msg": MSG},
    "js": JS,
    "css": __import__("herramientas.tools.revisar_anuncio_etsy", fromlist=["CSS"]).CSS.replace("#titulo", "#title"),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Etsy Open API v3 · createDraftListing (title, tags)", S.ETSY_API)],
    "related": ["etsy-fee-calculator", "social-media-image-sizes", "sku-generator", "selling-price-calculator"],
    "tests": [
        ({}, {"n.e": 1, "n.tlen": len(EX_T), "n.tags": 6, "n.codes": "tRep tWords gFew gLong"}),
        ({"title": "Silver Earrings 50% off & free gift & box: 100% handmade: ok", "tags": ""}, {"n.e": 3}),
        ({"title": "HANDMADE SILVER RING STERLING GIFT", "tags": "silver ring"}, {"n.codes": "tCaps gFew"}),
        ({"title": "Mug $ cheap", "tags": "mug, Mug, a tag that is far too long, sale!"}, {"n.e": 4}),
        ({"title": "", "tags": ",".join(f"tag {i}" for i in range(14))}, {"n.codes": "tEmpty gMany"}),
    ],
}
