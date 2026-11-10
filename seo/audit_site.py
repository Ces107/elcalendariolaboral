"""AdSense-readiness lint of the built site (run after build.py, from the repo root): python seo/audit_site.py [--json out]

Per page: robots, canonical, title/description, AdSense loader and manual units, visible words in <main> without the
month grids, internal links. Then: indexable pages vs sitemap, ads on noindex/thin pages, broken internal links,
duplicate titles/descriptions, a word-count table per page group. Exit 1 on a hard failure (broken link, ads on a
noindex page, sitemap URL missing or noindex, indexable page with a canonical elsewhere).
"""
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://elcalendariolaboral.es"
SKIP_DIRS = {"pdf", "ics", "csv", "og", "icons", "fonts", "data", "seo", "__pycache__", ".git", "node_modules", ".well-known"}
THIN = 250  # visible words in <main> without the month grids, below which an indexable page counts as thin

RX_ROBOTS = re.compile(r'<meta name="robots" content="([^"]*)"')
RX_CANON = re.compile(r'<link rel="canonical" href="([^"]*)"')
RX_TITLE = re.compile(r"<title>(.*?)</title>", re.S)
RX_DESC = re.compile(r'<meta name="description" content="([^"]*)"')
RX_MAIN = re.compile(r"<main\b.*?</main>", re.S)
RX_GRID = re.compile(r"<caption>Enero</caption>.*?<caption>Diciembre</caption>.*?(?:</table>|</div>)", re.S)  # the 12 months
RX_HREF = re.compile(r'(?:href|src)="([^"#?]*)')


def group(rel):
    p = rel.strip("/").split("/")
    if rel in ("", "index.html"):
        return "home"
    if p[0] in ("ca", "gl", "eu"):
        return f"{p[0]}/" + (group("/".join(p[1:])) if len(p) > 1 else "home")
    if p[0] == "widget":
        return "widget" if len(p) == 1 else "widget-embed"
    return p[0] if len(p) == 1 else (f"{p[0]}/*" if p[0] in GROUPED else "municipio/ciudad/provincia")


GROUPED = {"festivos", "vacaciones-2027", "calendario-escolar", "vacaciones-escolares", "semana-santa", "festivos-locales"}


def words(main):
    t = RX_GRID.sub(" ", main)
    t = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return len(re.findall(r"[^\W\d_]{2,}", t))  # words of 2+ letters: no day numbers


def sitemap_urls():
    urls = set()
    for f in ROOT.glob("sitemap-*.xml"):
        urls |= set(re.findall(r"<loc>([^<]+)</loc>", f.read_text("utf-8")))
    return urls


def pages():
    for f in ROOT.rglob("*.html"):
        rel = f.relative_to(ROOT)
        if rel.parts[0] in SKIP_DIRS:
            continue
        yield rel.as_posix(), f


def main():
    out = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
    rows, links = {}, defaultdict(set)
    for rel, f in pages():
        h = f.read_text("utf-8", errors="replace")
        url_path = "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        rob = (RX_ROBOTS.search(h) or [None, ""])[1]
        m = RX_MAIN.search(h)
        rows[url_path] = {
            "group": group(url_path.strip("/")), "noindex": "noindex" in rob,
            "canon": (RX_CANON.search(h) or [None, ""])[1], "title": html.unescape((RX_TITLE.search(h) or [None, ""])[1]).strip(),
            "desc": html.unescape((RX_DESC.search(h) or [None, ""])[1]), "loader": "adsbygoogle.js" in h,
            "units": h.count('class="adsbygoogle"'), "words": words(m.group(0)) if m else 0, "bytes": len(h.encode()),
        }
        for u in RX_HREF.findall(h):
            if u.startswith("/") and not u.startswith("//"):
                links[unquote(u)].add(url_path)
    sm = sitemap_urls()
    smp = {urlsplit(u).path for u in sm}
    fail, warn = [], []

    def exists(p):
        q = ROOT / p.lstrip("/")
        return q.is_file() or (q / "index.html").is_file()

    broken = {u: sorted(src)[:3] for u, src in links.items() if not exists(u)}
    if broken:
        fail.append(f"{len(broken)} broken internal links, e.g. " + "; ".join(f"{u} <- {s[0]}" for u, s in list(broken.items())[:8]))
    for p, r in rows.items():
        if r["noindex"] and (r["loader"] or r["units"]):
            fail.append(f"ads on noindex page {p}")
        if r["units"] and not r["loader"]:
            fail.append(f"ad units without the AdSense loader (empty 'Publicidad' boxes) on {p}")
        if not r["noindex"] and r["canon"] and r["canon"] != SITE + p and p != "/404.html":
            fail.append(f"indexable {p} has canonical {r['canon']}")
    for p in sorted(smp):
        if p not in rows:
            fail.append(f"sitemap URL without page: {p}")
        elif rows[p]["noindex"]:
            fail.append(f"sitemap URL is noindex: {p}")
    idx = {p for p, r in rows.items() if not r["noindex"] and p != "/404.html"}
    NOT_IN_SITEMAP = {"/privacidad/", "/ca/privacidad/", "/gl/privacidad/", "/eu/privacidad/"}  # written by build.py, not pages.write
    missing = sorted(idx - smp - NOT_IN_SITEMAP)
    if missing:
        warn.append(f"{len(missing)} indexable pages not in the sitemap, e.g. {missing[:10]}")
    thin_ads = sorted(p for p in idx if rows[p]["words"] < THIN and (rows[p]["loader"] or rows[p]["units"]))
    if thin_ads:
        warn.append(f"{len(thin_ads)} indexable pages with ads and < {THIN} words: {thin_ads[:15]}")
    thin = sorted(p for p in idx if rows[p]["words"] < THIN)
    if thin:
        warn.append(f"{len(thin)} indexable pages with < {THIN} words: {thin[:15]}")
    many = sorted(p for p, r in rows.items() if r["units"] > 2)
    if many:
        warn.append(f"{len(many)} pages with more than 2 manual units: {many[:10]}")
    for k in ("title", "desc"):
        c = Counter(rows[p][k] for p in idx)
        d = [v for v, n in c.items() if n > 1]
        if d:
            warn.append(f"{len(d)} duplicate {k}s among indexable pages, e.g. {d[:3]}")
        e = [p for p in idx if not rows[p][k]]
        if e:
            fail.append(f"{len(e)} indexable pages without {k}: {e[:5]}")

    for p, r in rows.items():  # split the 8,000 place pages by kind
        if r["group"].endswith("municipio/ciudad/provincia"):
            seg = p.strip("/").split("/")[-1]
            kind = ("provincia" if seg.startswith("provincia-de-") or seg == "municipios" else "ciudad" if r["bytes"] > 40000
                    else "municipio-pendiente" if r["noindex"] else "municipio-oficial")
            r["group"] = r["group"].replace("municipio/ciudad/provincia", kind)
    by = defaultdict(list)
    for p, r in rows.items():
        by[r["group"]].append(r)
    print(f"{'group':34} {'pages':>6} {'index':>6} {'loader':>6} {'units':>6} {'words med':>9} {'min':>5} {'KB med':>6}")
    for g in sorted(by, key=lambda g: -len(by[g])):
        rs = by[g]
        ws = sorted(r["words"] for r in rs)
        bs = sorted(r["bytes"] for r in rs)
        print(f"{g:34} {len(rs):6} {sum(not r['noindex'] for r in rs):6} {sum(r['loader'] for r in rs):6} "
              f"{sum(r['units'] for r in rs):6} {ws[len(ws) // 2]:9} {ws[0]:5} {bs[len(bs) // 2] // 1024:6}")
    print(f"\npages {len(rows)} · indexable {len(idx)} · sitemap {len(sm)} · loader {sum(r['loader'] for r in rows.values())} · "
          f"units {sum(r['units'] for r in rows.values())} · internal link targets {len(links)}")
    for w in warn:
        print("WARN", w)
    for x in fail:
        print("FAIL", x)
    if out:
        Path(out).write_text(json.dumps(rows, ensure_ascii=False), "utf-8")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
