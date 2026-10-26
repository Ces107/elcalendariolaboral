#!/usr/bin/env python3
"""Vacation optimizer: vacopt.py (reference) and vac.js (browser) give the same plans.  Uso: python test_vacopt.py

- 19 comunidades x 1..30 days, default rules: same total, same days used, same breaks (node runs vac.js).
- A sample with constraints (taken days, blocked months, min and max length) and the cities.
- Every plan: vacation only on working days, breaks are maximal runs of days off, totals add up, lengths in range.
- Brute force on short synthetic years agrees with the DP (exactness).
"""
import itertools
import json
import random
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402
import vacopt as V  # noqa: E402

data = build.load()
fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def valid(off, plan, n, taken=(), blocked=(), max_len=0, min_len=V.MIN_BREAK, tag=""):
    vac = set()
    total = 0
    cap = max_len or V.N
    for b in plan["breaks"]:
        s, e = b["s"], b["e"]
        check(s == 0 or (not off[s - 1] and s - 1 not in vac), f"{tag}: break {s} not maximal on the left")
        check(e == V.N - 1 or not off[e + 1], f"{tag}: break {e} not maximal on the right")
        take = [k for k in range(s, e + 1) if not off[k]]
        check(take == b["take"] and take, f"{tag}: break {s}-{e} take")
        check(all(not off[k] for k in b["take"]), f"{tag}: vacation on a weekend or holiday")
        has_t = any(k in taken for k in take)
        new = [k for k in take if k not in taken]
        check((has_t and not new) or (b["len"] <= cap and (b["len"] >= min(min_len, cap) or has_t)), f"{tag}: break {s}-{e} length {b['len']}")
        check(not any(V.DAYS[k].month - 1 in blocked for k in new), f"{tag}: vacation in a blocked month")
        vac |= set(take)
        total += b["len"]
    check(total == plan["total"], f"{tag}: total {total} != {plan['total']}")
    check(len(vac) == plan["used"] <= max(n, len(set(taken))), f"{tag}: used {plan['used']}")
    check(set(taken) <= vac, f"{tag}: taken days missing")


# ---------------------------------------------------------------- cases
cases = []
for r in data["regions"]:
    hols = [h["date"] for h in build.region_holidays(data, r["slug"])]
    for n in range(1, 31):
        cases.append({"id": f"{r['slug']}/{n}", "hols": hols, "n": n})
rnd = random.Random(2027)
import pages  # noqa: E402
pages.DATA = data
regions = {r["slug"]: r for r in data["regions"]}
cities = pages.published_cities(pages.load_locales(), regions)
for x in cities:
    cases.append({"id": f"{x['path']}22", "hols": [h["date"] for h in x["hols"]], "n": 22})
for k in range(120):
    r = rnd.choice(data["regions"])
    hols = [h["date"] for h in build.region_holidays(data, r["slug"])]
    off = V.off_days(hols)
    work = [i for i in range(V.N) if not off[i]]
    cases.append({"id": f"rand{k}/{r['slug']}", "hols": hols, "n": rnd.randint(1, 30),
                  "taken": sorted(rnd.sample(work, rnd.choice([0, 0, 1, 3, 6]))),
                  "blocked": sorted(rnd.sample(range(12), rnd.choice([0, 1, 2, 4]))),
                  "max": rnd.choice([0, 0, 5, 7, 9, 12, 16]), "min": rnd.choice([3, 4, 5, 5, 7, 9])})

py = {}
for c in cases:
    off = V.off_days(c["hols"])
    kw = dict(taken=c.get("taken", ()), blocked_months=c.get("blocked", ()), max_len=c.get("max", 0), min_len=c.get("min", V.MIN_BREAK))
    p = V.optimize(off, c["n"], **kw)
    check(p is not None, f"{c['id']}: no plan")
    if p:
        valid(off, p, c["n"], set(kw["taken"]), set(kw["blocked_months"]), kw["max_len"], kw["min_len"], c["id"])
        py[c["id"]] = p

# monotone in n under the default rules
for r in data["regions"]:
    tots = [py[f"{r['slug']}/{n}"]["total"] for n in range(1, 31)]
    check(all(a <= b for a, b in zip(tots, tots[1:])), f"{r['slug']}: total not monotone {tots}")

# ---------------------------------------------------------------- vac.js under node
js = r"""
const V = require(process.argv[process.argv.length - 1]);
const cases = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const out = {}; let worst = 0;
for (const c of cases) {
  const off = V.offDays(c.hols);
  const t = process.hrtime.bigint();
  const p = V.optimize(off, c.n, c.taken || [], c.blocked || [], c.max || 0, c.min == null ? V.MIN_BREAK : c.min);
  worst = Math.max(worst, Number(process.hrtime.bigint() - t) / 1e6);
  out[c.id] = p;
}
process.stdout.write(JSON.stringify({ out, worst }));
"""
try:
    res = subprocess.run(["node", "-e", js, str(ROOT / "vac.js")], input=json.dumps(cases), capture_output=True, text=True, encoding="utf-8", check=True)
    jsres = json.loads(res.stdout)
    for c in cases:
        a, b = py.get(c["id"]), jsres["out"].get(c["id"])
        if a is None or b is None:
            check(a is None and b is None, f"{c['id']}: py {a} js {b}")
            continue
        check(a["total"] == b["total"], f"{c['id']}: total py {a['total']} != js {b['total']}")
        check(a["used"] == b["used"], f"{c['id']}: used py {a['used']} != js {b['used']}")
        check([(x["s"], x["e"]) for x in a["breaks"]] == [(x["s"], x["e"]) for x in b["breaks"]], f"{c['id']}: different breaks")
    check(jsres["worst"] < 50, f"vac.js: slowest plan {jsres['worst']:.1f} ms >= 50 ms")
    print(f"node: {len(cases)} plans, slowest {jsres['worst']:.1f} ms")
except FileNotFoundError:
    fails.append("node not found: vac.js not compared")

# ---------------------------------------------------------------- exactness: brute force on short years
saved = V.N, V.DAYS
for k in range(150):
    L = rnd.randint(8, 16)
    V.N = L
    V.DAYS = saved[1][:L]
    off = [rnd.random() < 0.35 for _ in range(L)]
    n = rnd.randint(1, 5)
    mn, mx = rnd.choice([1, 3, 5]), rnd.choice([0, 0, 6])
    p = V.optimize(off, n, min_len=mn, max_len=mx)
    work = [i for i in range(L) if not off[i]]
    best = 0
    for size in range(0, min(n, len(work)) + 1):
        for sel in itertools.combinations(work, size):
            s = set(sel)
            o = [off[i] or i in s for i in range(L)]
            tot, i, ok = 0, 0, True
            while i < L:
                if o[i]:
                    j = i
                    while j + 1 < L and o[j + 1]:
                        j += 1
                    if any(x in s for x in range(i, j + 1)):
                        ln = j - i + 1
                        if ln < min(mn, mx or L) or (mx and ln > mx):
                            ok = False
                        tot += ln
                    i = j + 1
                else:
                    i += 1
            if ok:
                best = max(best, tot)
    check(p is not None and p["total"] == best, f"brute force {k}: dp {p and p['total']} != {best} off={off} n={n} min={mn} max={mx}")
V.N, V.DAYS = saved

print(f"{len(fails)} fallos" if fails else f"OK: {len(cases)} plans equal in Python and JS, all valid; brute force agrees")
for f in fails[:40]:
    print(" -", f)
sys.exit(1 if fails else 0)
