#!/usr/bin/env python3
"""Standalone build of the tools section, without the 8,000-page site build. Same head, header and footer as build.py.

    python -m herramientas.build slug [slug ...]   only those tools: <folder>/index.html + <folder>/t.js  (parallel agents)
    python -m herramientas.build                   everything: shared runtime/css, every tool, hubs, credits,
                                                   sitemap-utilidades.xml and its line in sitemap_index.xml   (lead)
    python -m herramientas.build --hub             shared runtime/css, hubs, credits and the sitemap (no tool pages)

A broken tool file (import error, check_tool failure, duplicate slug) is skipped with a warning on stderr unless it is
required: the given slugs in slug mode, the HT_ONLY slugs in full / --hub mode; a required broken tool stops the build.

Run from the repository root (MSYS_NO_PATHCONV=1 in Git Bash). Links into the tools from the rest of the site (header,
footer, home, comunidades, /dias-habiles/) only change with the full site build (build.py).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import build as B  # noqa: E402

sys.modules.setdefault("build", B)
import pages  # noqa: E402
import herramientas as HT  # noqa: E402


def setup():
    data = B.localize(B.load())
    B.REGIONS = data["regions"]
    fonts = {w: B.short_hash(ROOT / "fonts" / f"public-sans-{w}.woff2") for w in ("400", "600", "700")}
    cssv, jsv = B.short_hash(ROOT / "app.css"), B.short_hash(ROOT / "app.min.js")
    m = re.search(r'data-sidx="(\w+)"', (ROOT / "index.html").read_text("utf-8"))
    sidxv = m.group(1) if m else "0"
    pages._fix = lambda s: (s.replace("{CSSV}", cssv).replace("{JSV}", jsv).replace("{SIDXV}", sidxv)  # noqa: E731
                            .replace("{F400}", fonts["400"]).replace("{F600}", fonts["600"]).replace("{F700}", fonts["700"]))
    pages.DATA = data
    pages._written.clear()
    cities = pages.published_cities(pages.load_locales(), {r["slug"]: r for r in data["regions"]})
    return data, cities


def write_sitemap():
    """sitemap-utilidades.xml from every tool and hub on disk (the same entries build.write_sitemaps makes)."""
    ws = []
    for t in HT.registry():
        if (ROOT / HT.path(t) / "index.html").exists():
            ws.append((HT.path(t), t["updated"], ["es"]))
    for lang, p in HT.HUB.items():
        if (ROOT / p / "index.html").exists():
            ws.append((p, max([HT.HUB_UPDATED] + [t["updated"] for t in HT.registry() if t["lang"] == lang]), ["es"]))
    (ROOT / "sitemap-utilidades.xml").write_text(B.sitemap(ws), "utf-8", newline="\n")
    line = f"  <sitemap><loc>{B.SITE}{B.ASSETS}sitemap-utilidades.xml</loc><lastmod>{max(w[1] for w in ws)}</lastmod></sitemap>"
    for name in ("sitemap_index.xml", "sitemap.xml"):
        f = ROOT / name
        s = f.read_text("utf-8")
        s = re.sub(r"  <sitemap><loc>[^<]*sitemap-utilidades\.xml</loc>.*?</sitemap>\n", "", s)
        f.write_text(s.replace("</sitemapindex>", line + "\n</sitemapindex>"), "utf-8", newline="\n")
    return len(ws)


def main(argv):
    hub_only = "--hub" in argv
    slugs = [a for a in argv if not a.startswith("-")] or None
    if slugs:
        HT.strict(slugs)  # the requested tools fail hard; other broken tool files are skipped with a warning
    data, cities = setup()
    if hub_only:
        HT.build_shared()  # utilidades/a/h.js + h.css: the shared runtime goes out with the hubs
        HT.write_hubs(HT.Ctx(data, cities), pages.write)
    else:
        HT.write_pages(data, pages.write, cities, slugs)
    for w in pages._written:
        f = ROOT / w[0] / "index.html"
        print(f"  {w[0]}  {pages.main_words(f.read_text('utf-8'))} words  {f.stat().st_size // 1024} KB")
    if pages.thin_no_ads:
        print("  no ads (< 250 words):", pages.thin_no_ads)
    if slugs is None:
        print(f"  sitemap-utilidades.xml: {write_sitemap()} urls")


if __name__ == "__main__":
    main(sys.argv[1:])
