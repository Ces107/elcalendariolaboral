#!/usr/bin/env python3
"""Utility pages (utilidades.py, util.js): data/2026.json, the working-day functions in Python and in JS (node), the
ISO weeks, and the generated pages. Run build.py first (same CL_SITE / CL_BASE).

    MSYS_NO_PATHCONV=1 CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python test_utilidades.py
"""
import datetime as dt
import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

import build as B
import pages
import utilidades as U

ROOT = Path(__file__).resolve().parent
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


D = dt.date.fromisoformat

# ---------------------------------------------------------------- data/2026.json (BOE-A-2025-21667)
d26 = json.loads((ROOT / "data" / "2026.json").read_text("utf-8"))
d27 = B.load()
check(d26["source"]["id"] == "BOE-A-2025-21667" and d26["source"]["url"].startswith("https://www.boe.es/"), "2026: source")
check([r["slug"] for r in d26["regions"]] == [r["slug"] for r in d27["regions"]], "2026: regions differ from 2027")
for r in d26["regions"]:
    hols = B.region_holidays(d26, r["slug"])
    want = 11 if r["slug"] == "canarias" else 12  # Canarias: 11 + the island's own
    check(len(hols) == want, f'2026 {r["slug"]}: {len(hols)} holidays, expected {want}')
    check(len({h["date"] for h in hols}) == len(hols), f'2026 {r["slug"]}: two holidays on one day')
for h in d26["holidays"]:
    check(h["date"].startswith("2026-") and h["code"] in (1, 2, 3), f"2026: {h}")
for z in d26["zones"].values():
    for o in z["options"]:
        check("add" not in o or o["add"]["date"].startswith("2026-"), f"2026 zone {o['slug']}")
nat26 = {h["date"] for h in d26["holidays"] if h["regions"] == "all"}
check({"2026-01-01", "2026-01-06", "2026-04-03", "2026-05-01", "2026-08-15", "2026-10-12", "2026-12-08", "2026-12-25"} <= nat26,
      "2026: national holidays missing")

# ---------------------------------------------------------------- working days: hand-checked cases (Madrid)
pages.DATA = d27
cities = pages.published_cities(pages.load_locales(), {r["slug"]: r for r in d27["regions"]})
cfg = U.dh_data([U.load_year(2026), d27], cities)
mad = {x[0] for x in cfg["reg"]["madrid"]}
cases = [  # (fn, a, b or n, sat, expected)
    ("count", "2026-12-28", "2027-01-08", False, 8),            # across years: 1 and 6 Jan off
    ("count", "2027-01-08", "2026-12-28", False, 8),            # a > b: swapped
    ("count", "2026-12-08", "2026-12-25", False, 12),           # starts and ends on a holiday
    ("count", "2027-01-01", "2027-01-01", False, 0),            # one day, a holiday
    ("count", "2027-01-04", "2027-01-04", False, 1),            # one day, a working day
    ("count", "2026-12-05", "2026-12-06", True, 1),             # Saturday counts when it is a working day
    ("add", "2026-12-08", 0, False, "2026-12-08"),              # N = 0 on a holiday: the same day
    ("add", "2026-12-04", 3, False, "2026-12-11"),              # weekend + 7 and 8 Dec skipped
    ("add", "2026-12-04", 3, True, "2026-12-10"),               # Saturday 5 is a working day
    ("add", "2026-12-30", 3, False, "2027-01-05"),              # across years
]
for fn, a, x, sat, exp in cases:
    got = U.count_workdays(D(a), D(x), mad, sat) if fn == "count" else U.add_workdays(D(a), x, mad, sat).isoformat()
    check(got == exp, f"python {fn}({a}, {x}, sat={sat}) = {got}, expected {exp}")

# ---------------------------------------------------------------- the same in JS, plus random cases against Python
node = shutil.which("node")
if node:
    rnd = random.Random(7)
    jobs = [[fn, a, x, sat, "madrid", exp] for fn, a, x, sat, exp in cases]
    span = (U.HI - U.LO).days
    for _ in range(400):
        slug = rnd.choice(list(cfg["reg"]))
        off = {h[0] for h in cfg["reg"][slug]}
        a = U.LO + dt.timedelta(rnd.randrange(span))
        sat = rnd.random() < .3
        if rnd.random() < .5:
            b = U.LO + dt.timedelta(rnd.randrange(span))
            jobs.append(["count", a.isoformat(), b.isoformat(), sat, slug, U.count_workdays(a, b, off, sat)])
        else:
            n = rnd.randrange(0, 60)
            jobs.append(["add", a.isoformat(), n, sat, slug, U.add_workdays(a, n, off, sat).isoformat()])
    weeks = [(D("2025-12-01") + dt.timedelta(k)).isoformat() for k in range(0, 1200, 3)]
    js = r"""
const U = require(process.argv[1]); const inp = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = inp.jobs.map(([fn, a, x, sat, slug]) => {
  const off = {}; inp.reg[slug].forEach(h => { off[h[0]] = h; });
  return fn === 'count' ? U.countWorkdays(U.parse(a), U.parse(x), off, sat) : U.iso(U.addWorkdays(U.parse(a), x, off, sat));
});
const wk = inp.weeks.map(s => U.isoWeek(U.parse(s)));
process.stdout.write(JSON.stringify({ out, wk }));
"""
    res = subprocess.run([node, "-e", js, str(ROOT / "util.js")], input=json.dumps({"jobs": jobs, "reg": cfg["reg"], "weeks": weeks}),
                         capture_output=True, text=True, encoding="utf-8", timeout=60)
    check(res.returncode == 0, f"node: {res.stderr[:300]}")
    if res.returncode == 0:
        r = json.loads(res.stdout)
        for j, got in zip(jobs, r["out"]):
            check(got == j[5], f"js {j[0]}({j[1]}, {j[2]}, sat={j[3]}, {j[4]}) = {got}, expected {j[5]}")
        for s, got in zip(weeks, r["wk"]):
            check(tuple(got) == D(s).isocalendar()[:2], f"js isoWeek({s}) = {got}")
else:
    print("node not found: JS checks skipped")

# ---------------------------------------------------------------- generated pages
sm = (ROOT / "sitemap.xml").read_text("utf-8")
for path, only in ((U.PATH_WK, U.ONLY_WK), (U.PATH_DH, U.ONLY_DH)):
    for lang in only:
        url = f"{B.SITE}{B.lang_base(lang)}{path}"
        check(f"<loc>{url}</loc>" in sm, f"{url}: not in sitemap")
        f = ROOT / ("" if lang == "es" else lang) / path / "index.html"
        check(f.exists(), f"{f}: missing")
        if not f.exists():
            continue
        h = f.read_text("utf-8")
        head = h.split("</head>")[0]
        check(f'<link rel="canonical" href="{url}">' in head, f"{url}: canonical")
        check('"FAQPage"' in head and '"BreadcrumbList"' in head, f"{url}: FAQPage / BreadcrumbList")
        check(('hreflang="ca"' in head) == (len(only) > 1), f"{url}: hreflang")
        check("util.js?v=" in h, f"{url}: util.js")
    check(f'href="{B.ASSETS}{path}"' in (ROOT / "index.html").read_text("utf-8"), f"home: no footer link to /{path}")

wk = (ROOT / U.PATH_WK / "index.html").read_text("utf-8")
for year in U.YEARS:
    rows = re.findall(rf'data-w="{year}-(\d+)"', wk)
    check([int(x) for x in rows] == list(range(1, len(U.weeks(year)) + 1)), f"/semana/ {year}: weeks {rows[:3]}…")
check(len(U.weeks(2026)) == 53 and len(U.weeks(2027)) == 52, "ISO weeks: 2026 has 53, 2027 has 52")
check(U.weeks(2027)[0][1] == D("2027-01-04"), "week 1 of 2027 starts on Monday 4 January")

dh = (ROOT / U.PATH_DH / "index.html").read_text("utf-8")
check("Ley 39/2015" in dh, "/dias-habiles/: Ley 39/2015 FAQ")
check(U.L("caveat") in dh if B.LANG in U.ONLY_DH else True, "/dias-habiles/: caveat line")

print("\n".join(fails[:40]))
print(f"{len(fails)} fallos" if fails else f"OK: data 2026, {len(cases)} hand cases + random cases equal in Python and JS, pages")
sys.exit(1 if fails else 0)
