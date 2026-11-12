#!/usr/bin/env python3
"""PDFs (pdfs.py) and ad slots (build.ad). Run after build.py:  python test_pdf.py

Every PDF of pdfhub.entries exists, is under 300 KB, opens with pymupdf, embeds its fonts, has the right page count
and the text of every holiday it should show; it is linked from its page (comunidad/city/school) and from the hub.
Ads: off (no ad markup in any page) while ADS_ON is False; with a slot id the unit has the label and the slot.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import build as B  # noqa: E402

sys.modules["build"] = B
import pymupdf  # noqa: E402

import escolar  # noqa: E402
import pages  # noqa: E402
import pdfhub  # noqa: E402

data = B.localize(B.load())
B.REGIONS = data["regions"]
pages.DATA = data
cities = pages.published_cities(pages.load_locales(), {r["slug"]: r for r in data["regions"]})
sch = [x["slug"] for x in escolar.load("escolar-2026-27.json")["regions"]]
entries = pdfhub.entries(data, cities, sch)
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def flat(s):
    return re.sub(r"\s+", " ", s)


hub = (ROOT / pdfhub.PATH / "index.html").read_text("utf-8")
html_cache = {}
total = 0
for f, page, label, hols in entries:
    p = ROOT / f
    if not p.exists():
        check(False, f"{f}: missing")
        continue
    size = p.stat().st_size
    total += size
    check(size < 300_000, f"{f}: {size // 1024} KB")
    doc = pymupdf.open(p)
    n = doc.page_count
    check(n == (12 if f.endswith("-mensual.pdf") else n) and n >= 1, f"{f}: {n} pages")
    for k in range(n):
        for font in doc.get_page_fonts(k):
            check(font[1] != "n/a" and "PublicSans" in font[3], f"{f}: font not embedded {font[3]}")
    txt = flat(" ".join(pg.get_text() for pg in doc))
    check("elcalendariolaboral" in txt, f"{f}: no wordmark")
    if hols is not None:
        check(data["source"]["id"] in txt, f"{f}: no BOE id")
        for h in hols:
            check(flat(h["name"]) in txt, f"{f}: missing {h['name']}")
            if not f.endswith("-mensual.pdf"):
                check(B.dshort(h["date"]) in txt, f"{f}: missing date {B.dshort(h['date'])}")
    href = f"{B.ASSETS}{f}"
    check(f'href="{href}"' in hub, f"{f}: not linked from the hub")
    pg = html_cache.setdefault(page, (ROOT / page / "index.html").read_text("utf-8"))
    key = page.strip("/").replace("/", "-").replace("calendario-escolar-", "")
    if f"/{key}/" in f:  # the comunidad/city/school page links its own files (zones: swapped by app.js)
        check(f'href="{href}"' in pg, f"{f}: not linked from /{page}")

# hub page: in the sitemap, linked from the footer, BreadcrumbList
sm = "".join(p.read_text("utf-8") for p in sorted(ROOT.glob("sitemap-*.xml")))  # sitemap.xml is the index
check(f"<loc>{B.SITE}{B.ASSETS}{pdfhub.PATH}</loc>" in sm, "hub not in sitemap")
check('"BreadcrumbList"' in hub, "hub: no BreadcrumbList")
check("calendario laboral 2027 pdf" in re.search(r"<title>(.*?)</title>", hub).group(1).lower(), "hub title")
for p in (ROOT / "index.html", ROOT / "madrid" / "index.html", ROOT / "ca" / "index.html"):
    check(f'href="{B.ASSETS}{pdfhub.PATH}"' in p.read_text("utf-8"), f"{p}: no footer link to the hub")

# ads: off now; the unit when on
if not B.ADS_ON:
    for p in ROOT.rglob("index.html"):
        if ".git" not in p.parts:
            check('class="adsbygoogle"' not in p.read_text("utf-8"), f"{p}: ad unit while ADS_ON is False")
B.ADS_ON, B.AD_SLOTS["cal"] = True, "1234567890"
B.ADS_PAGE = True
u = B.ad("cal")
check('data-ad-slot="1234567890"' in u and "Publicidad" in u and 'class="ad ad-cal ad-g"' in u, "ad unit markup")
# house ads: our 4 promos ride in every position (one shown), stacked on the AdSense unit or alone without it
check(u.count('class="hp"') == 4 and u.count(" hidden>") == 3 and "amazon.es/dp/B0HQ8FVGZS" in u and B.TESELO_WEB in u
      and "etsy.com/es/shop/CalmaPlanners" in u and 'href="/shopping/"' in u.replace(B.ASSETS + "shopping/", "/shopping/"),
      "house ads in the unit")
check(B.house_only(u).startswith('<aside class="ad ad-cal" aria-label="Nuestros productos">')
      and "adsbygoogle" not in B.house_only(u) and B.house_only(u).count('class="hp"') == 4, "thin guard keeps the house ads")
B.AD_SLOTS["list"] = ""
h = B.ad("list")
check("adsbygoogle" not in h and h.count('class="hp"') == 4, "ad without slot id: house ads only")
B.ADS_PAGE = False
h = B.ad("cal")
check("adsbygoogle" not in h and h.count('class="hp"') == 4, "page without AdSense (noindex, legal, tool): house ads only")
check(B.ad("hub", "en").count('class="hp"') == 3 and "amazon.com/dp/B0HQ96KT81" in B.ad("hub", "en"), "English tool pages: 3 promos")
B.ADS_PAGE = True
check("adsbygoogle" not in B.ad("hub", adsense=False), "adsense=False: house ads only")
s = B.ad("hub", topic="school")
check("amazon.es/dp/B0HR1RPDCP" in s and 'data-k="agenda" data-w="3">' in s, "school topic: teacher's notebook first")
check('data-k="etsy" data-w="3">' in B.ad("hub", topic="pdf"), "pdf topic: Etsy first")
for f in ("agenda-2027", "profesor", "planner-en", "etsy", "teselo", "tienda"):
    check((ROOT / "promo" / f"{f}.webp").exists(), f"promo/{f}.webp missing")
# built pages: the promos where the positions are, the right product first, never in widget embeds or the shop
for path, want in (("", 'class="hp"'), ("madrid/", 'class="hp"'), ("calendario-escolar/", "promo/profesor.webp"),
                   ("calendario-laboral-2027-pdf/", 'data-k="etsy" data-w="3">'), ("vacaciones-2027/", 'data-k="agenda" data-w="3">'),
                   ("comunitat-valenciana/ademuz/", 'class="hp"'), ("en/tools/age-calculator/", "amazon.com/dp/B0HQ96KT81")):
    check(want in (ROOT / path / "index.html").read_text("utf-8"), f"/{path}: house ads ({want})")
for p in [ROOT / "shopping" / "index.html", *(ROOT / "widget" / "embed").glob("*/index.html")]:
    check('class="hp"' not in p.read_text("utf-8"), f"{p.relative_to(ROOT)}: house ads where there must be none")
css = (ROOT / "app.css").read_text("utf-8")
check(re.search(r"@media print \{ \.ad \{ display: none", css), "ads hidden in print")

print("\n".join(fails[:40]))
print(f"{len(fails)} fallos" if fails else f"OK: {len(entries)} PDF, {total / 1e6:.1f} MB, max {max((ROOT / f).stat().st_size for f, *_ in entries) // 1024} KB")
sys.exit(1 if fails else 0)
