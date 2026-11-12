#!/usr/bin/env python3
"""Tools (herramientas/): every TOOL definition passes check_tool(), and its compute function gives the expected
results for its own test cases, run in node with the same runtime helpers the browser uses (js/h.js).
With --pages, also checks the generated pages (run `python -m herramientas.build <slug>` first). Slugs given: only
those tools (every definition is still loaded and checked).

    MSYS_NO_PATHCONV=1 python herramientas/test_herramientas.py [--pages] [slug ...]
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build as B  # noqa: E402

sys.modules.setdefault("build", B)
import herramientas as HT  # noqa: E402
import pages  # noqa: E402

fails = []
data = B.localize(B.load())
pages.DATA = data
cities = pages.published_cities(pages.load_locales(), {r["slug"]: r for r in data["regions"]})
ctx = HT.Ctx(data, cities)

ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]
TOOLS = [t for t in HT.registry() if not ONLY or t["slug"] in ONLY]
if ONLY and len(TOOLS) != len(set(ONLY)):
    fails.append(f"unknown slugs: {sorted(set(ONLY) - {t['slug'] for t in TOOLS})}")
jobs = []
for t in TOOLS:
    C = {}
    if t["hol"] or any(i["type"] == "place" for i in t["inputs"]):
        C["hol"] = ctx.hol(t["hol"] or (2026, 2027))
    d = HT._call(t["data"], ctx)
    if d:
        C["d"] = d
    if not t["tests"]:
        fails.append(f'{t["slug"]}: no test cases')
    jobs.append({"slug": t["slug"], "js": t["js"], "inputs": t["inputs"], "C": C, "cases": [{"in": a, "want": b} for a, b in t["tests"]]})

HARNESS = r"""
const H = require(process.argv[1]);
const jobs = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = [];
function get(o, p) { return p.split('.').reduce((x, k) => (x == null ? undefined : x[k]), o); }
for (const j of jobs) {
  let f;
  try { f = eval('(' + j.js + ')'); } catch (e) { out.push(j.slug + ': compute does not parse: ' + e.message); continue; }
  j.cases.forEach((c, n) => {
    const v = {};
    for (const s of j.inputs) {
      let raw = s.id in c.in ? c.in[s.id] : (s.type === 'place' ? {} : s.value);
      v[s.id] = H.read(s, raw, j.C);
      if (s.type === 'place') { v[s.id + '_label'] = 'test'; v[s.id + '_r'] = (raw || {}).r || ''; v[s.id + '_m'] = (raw || {}).m || ''; }
    }
    let r;
    try { r = f(v, H, j.C); } catch (e) { out.push(j.slug + ' case ' + n + ': throws ' + e.message); return; }
    for (const k of Object.keys(c.want)) {
      const got = get(r, k), want = c.want[k];
      const ok = want === null ? got == null : typeof want === 'number' ? typeof got === 'number' && Math.abs(got - want) < 0.006 : JSON.stringify(got) === JSON.stringify(want);
      if (!ok) out.push(j.slug + ' case ' + n + ': ' + k + ' = ' + JSON.stringify(got) + ', expected ' + JSON.stringify(want));
    }
  });
}
console.log(JSON.stringify(out));
"""
node = shutil.which("node")
if node:
    res = subprocess.run([node, "-e", HARNESS, str(ROOT / "herramientas" / "js" / "h.js")], input=json.dumps(jobs, default=str),
                         capture_output=True, text=True, encoding="utf-8", timeout=120)
    if res.returncode:
        fails.append("node: " + res.stderr[:500])
    else:
        fails += json.loads(res.stdout.strip().splitlines()[-1])
else:
    print("node not found: compute checks skipped")

# pure helpers of the runtime
HELP = r"""
const H = require(process.argv[1]); const a = [];
const eq = (x, y, m) => { if (JSON.stringify(x) !== JSON.stringify(y)) a.push(m + ': ' + JSON.stringify(x) + ' != ' + JSON.stringify(y)); };
eq(H.num(1234567.891), '1.234.567,89', 'num'); eq(H.eur(-0.001), '0,00 €', 'eur -0'); eq(H.val('1.234,5'), 1234.5, 'val es');
eq(H.val('1234.5'), 1234.5, 'val dot'); eq(H.val('36.000'), 36000, 'val thousands'); eq(H.val('1.5'), 1.5, 'val decimal dot'); eq(isNaN(H.val('')), true, 'val empty'); eq(H.parse('2027-02-30'), null, 'parse invalid');
eq(H.monthDays(2028, 2), 29, 'leap'); eq(H.diff(H.parse('2026-12-31'), H.parse('2027-01-01')), 1, 'diff');
eq(H.wd(H.parse('2027-01-04')), 0, 'monday');
console.log(JSON.stringify(a));
"""
if node:
    res = subprocess.run([node, "-e", HELP, str(ROOT / "herramientas" / "js" / "h.js")], capture_output=True, text=True, encoding="utf-8")
    fails += json.loads(res.stdout.strip().splitlines()[-1]) if res.returncode == 0 else ["node helpers: " + res.stderr[:300]]

if "--pages" in sys.argv:
    for t in TOOLS:
        f = B.ROOT / HT.path(t) / "index.html"
        if not f.exists():
            fails.append(f"{f}: missing (run build.py)")
            continue
        h = f.read_text("utf-8")
        for need in ('"@type":"BreadcrumbList"', '"@type":"FAQPage"', 'rel="canonical"', 'id="h-data"', 't.js?v=', "h.css?v="):
            if need not in h:
                fails.append(f'{t["slug"]}: page lacks {need}')
        if "WebApplication" in h:
            fails.append(f'{t["slug"]}: WebApplication schema (removed on purpose)')
        words = pages.main_words(h)
        if words < pages.THIN_ADS:
            print(f'  {t["slug"]}: {words} words, no ads')
        m = re.search(r'<div id="out".*?</div>', h, re.S)
        if m and "adsbygoogle" in m.group(0):
            fails.append(f'{t["slug"]}: ad inside the result')
    hub = B.ROOT / "utilidades" / "index.html"
    if not hub.exists() or "hub-q" not in hub.read_text("utf-8"):
        fails.append("hub /utilidades/ missing")

print("\n".join(fails) if fails else f"ok · {len(TOOLS)} tools · {sum(len(t['tests']) for t in TOOLS)} cases")
sys.exit(1 if fails else 0)
