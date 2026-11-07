"""Spot-check the four Galician parsed files against the PDFs by an independent reading.

A Coruña / Ourense / Pontevedra: plain page text (get_text), the lines after the concello's name.
Lugo: word coordinates (get_text('words')): every dd/mm/2027 token whose vertical centre lies on the
concello name's printed line. 8 random rows per bulletin (seed 2027) plus the 2 capitals.
Usage: python -I spotcheck_galicia.py <workdir>
"""
import json
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import pymupdf  # noqa: E402

W = common.workdir_from_argv()
DM = re.compile(r"^(\d{1,2}) de (\w+)")


def text_lines(pdf):
    out = []
    for p in pymupdf.open(pdf):
        out += [line.strip() for line in p.get_text().splitlines() if line.strip()]
    return out


def by_text(pdf, name, n):
    lines = text_lines(pdf)
    i = lines.index(name)
    got = []
    for line in lines[i + 1:]:
        m = DM.match(line)
        if m:
            got.append(common.iso(int(m.group(1)), m.group(2)))
            if len(got) == n:
                break
    return got


def by_coords(pdf, name, n):
    for p in pymupdf.open(pdf):
        words = p.get_text("words")
        first = name.split()[0]
        for w in words:
            if w[4] != first or w[0] > 120:
                continue
            yc = (w[1] + w[3]) / 2
            line = sorted([x for x in words if abs((x[1] + x[3]) / 2 - yc) < 3], key=lambda x: x[0])
            txt = " ".join(x[4] for x in line)
            if not txt.startswith(name):
                continue
            ds = [x[4] for x in line if re.fullmatch(r"\d\d/\d\d/2027", x[4])]
            return [f"2027-{d[3:5]}-{d[:2]}" for d in ds]
    return None


CFG = [("bop-coruna-187", by_text, "CORUÑA, A"), ("bop-lugo-221", by_coords, "Lugo"),
       ("bop-ourense-197", by_text, "OURENSE"), ("boppo-192", by_text, "PONTEVEDRA")]
rng = random.Random(2027)
report = {}
for sid, fn, cap in CFG:
    d = json.load(open(os.path.join(W, "parsed", sid + ".json"), encoding="utf-8"))
    pdf = os.path.join(W, "dl", sid, "bop.pdf")
    sample = rng.sample(d["rows"], 8) + [r for r in d["rows"] if r["name"] == cap]
    res = []
    for r in sample:
        want = [h["date"] for h in r["holidays"]]
        got = fn(pdf, r["name"], len(want))
        ok = got is not None and sorted(got) == want
        res.append(f"{r['name']} {'OK' if ok else 'MISMATCH ' + str(got)} ({', '.join(w[5:] for w in want)})")
    report[sid] = res
    print(sid)
    for x in res:
        print("  ", x)
json.dump(report, open(os.path.join(W, "coord", "galicia_spotcheck.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
