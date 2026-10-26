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
sm = (ROOT / "sitemap.xml").read_text("utf-8")
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
u = B.ad("cal")
check('data-ad-slot="1234567890"' in u and "Publicidad" in u and 'class="ad ad-cal"' in u, "ad unit markup")
check(B.ad("list") == "", "ad without slot id must be empty")
css = (ROOT / "app.css").read_text("utf-8")
check(re.search(r"@media print \{ \.ad \{ display: none", css), "ads hidden in print")

print("\n".join(fails[:40]))
print(f"{len(fails)} fallos" if fails else f"OK: {len(entries)} PDF, {total / 1e6:.1f} MB, max {max((ROOT / f).stat().st_size for f, *_ in entries) // 1024} KB")
sys.exit(1 if fails else 0)
