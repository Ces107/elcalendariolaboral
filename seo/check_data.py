#!/usr/bin/env python3
"""Validate the SEO data files: data/escolar-*.json and data/locales-2027.json.

Usage:  python seo/check_data.py            (exit 1 on errors; warnings are printed but do not fail)

Rules
- JSON shape (required keys, enums, known comunidad slugs, unique slugs).
- Every date is ISO YYYY-MM-DD and lies inside the file's range
  (course 2026-2027 -> 2026-08-01..2027-07-31; locales 2027 -> 2027-01-01..2027-12-31).
- Ranges have start <= end.
- Every non-null entry (anything with dates) carries a source with an https URL and a 'checked' date.
- Unpublished entries carry no dates and explain why in 'note'.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STAGES = {"infantil", "primaria", "eso", "bachillerato", "fp", "fp_basica", "epa", "eoi", "musica", "danza",
          "artisticas", "especial", "escuelas_infantiles", "deportivas", "idiomas", "adultos"}
BREAKS = {"navidad", "semana_santa", "otro"}
errors, warnings = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


def load(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(path.name, f"invalid JSON ({e})")
        return None


def date(where, value, lo, hi):
    if not isinstance(value, str) or not ISO.match(value):
        err(where, f"not an ISO date: {value!r}")
        return None
    try:
        d = dt.date.fromisoformat(value)
    except ValueError:
        err(where, f"impossible date: {value}")
        return None
    if not lo <= d <= hi:
        err(where, f"{value} outside {lo}..{hi}")
    return d


def source(where, src, required=True):
    if src is None:
        if required:
            err(where, "dates present but no source")
        return False
    if not isinstance(src, dict):
        err(where, "source must be an object")
        return False
    url = src.get("url")
    if not isinstance(url, str) or not url.startswith("https://"):
        err(where, f"source.url missing or not https: {url!r}")
    if not src.get("title"):
        warn(where, "source.title empty")
    chk = src.get("checked")
    if not isinstance(chk, str) or not ISO.match(chk):
        err(where, f"source.checked missing/not ISO: {chk!r}")
    return True


def region_slugs():
    base = load(DATA / "2027.json") or {}
    return [r["slug"] for r in base.get("regions", [])], base


def check_calendar_block(where, blk, lo, hi, inherited_source):
    """stages / breaks / non_teaching_days of a region or province. Returns number of dates found."""
    n = 0
    for i, s in enumerate(blk.get("stages") or []):
        w = f"{where}.stages[{i}]"
        ids = s.get("stages")
        if not ids or not isinstance(ids, list):
            err(w, "stages ids missing")
        else:
            for x in ids:
                if x not in STAGES:
                    warn(w, f"unusual stage id {x!r}")
        a = date(w + ".start", s.get("start"), lo, hi) if s.get("start") is not None else None
        b = date(w + ".end", s.get("end"), lo, hi) if s.get("end") is not None else None
        if a and b and a > b:
            err(w, "start > end")
        if a and a.month not in (8, 9, 10):
            warn(w, f"course start in unusual month {a}")
        if b and b.month not in (5, 6, 7):
            warn(w, f"course end in unusual month {b}")
        n += (a is not None) + (b is not None)
    for i, b_ in enumerate(blk.get("breaks") or []):
        w = f"{where}.breaks[{i}]"
        if b_.get("type") not in BREAKS:
            err(w, f"type must be one of {sorted(BREAKS)}")
        if b_.get("type") == "otro" and not b_.get("name"):
            err(w, "type 'otro' needs a name")
        a = date(w + ".start", b_.get("start"), lo, hi)
        b = date(w + ".end", b_.get("end"), lo, hi)
        if a and b and a > b:
            err(w, "start > end")
        if b_.get("type") == "navidad" and a and a.month != 12:
            warn(w, f"navidad starts {a}")
        n += 2
    for i, d in enumerate(blk.get("non_teaching_days") or []):
        w = f"{where}.non_teaching_days[{i}]"
        date(w, d.get("date"), lo, hi)
        if not d.get("name") and not d.get("text"):
            warn(w, "no name/text")
        n += 1
    if n and not (blk.get("source") or inherited_source):
        err(where, "has dates but neither it nor its region has a source")
    if blk.get("source"):
        source(where, blk["source"])
    return n


def check_escolar(path, slugs, expect_all):
    doc = load(path)
    if doc is None:
        return
    name = path.name
    m = re.search(r"(\d{4})-(\d{2,4})", name)
    y1 = int(m.group(1))
    lo, hi = dt.date(y1, 8, 1), dt.date(y1 + 1, 7, 31)
    if doc.get("course") != f"{y1}-{y1 + 1}":
        err(name, f"course should be '{y1}-{y1 + 1}'")
    regs = doc.get("regions")
    if not isinstance(regs, list):
        err(name, "regions must be a list")
        return
    seen = set()
    for r in regs:
        w = f"{name}:{r.get('slug')}"
        if r.get("slug") not in slugs:
            err(w, "unknown slug")
        if r.get("slug") in seen:
            err(w, "duplicate slug")
        seen.add(r.get("slug"))
        st = r.get("status")
        if st not in ("verified", "partial", "unpublished"):
            err(w, f"bad status {st!r}")
        if r.get("source") is not None:
            source(w, r["source"])
        for j, xs in enumerate(r.get("extra_sources") or []):
            source(f"{w}.extra_sources[{j}]", xs)
        n = check_calendar_block(w, r, lo, hi, None)
        for k, p in enumerate(r.get("provinces") or []):
            if not p.get("name"):
                err(f"{w}.provinces[{k}]", "name missing")
            n += check_calendar_block(f"{w}.provinces[{p.get('name', k)}]", p, lo, hi, r.get("source"))
        if st == "unpublished":
            if n:
                err(w, "status unpublished but has dates")
            if not r.get("note"):
                err(w, "unpublished needs a note")
        elif st in ("verified", "partial"):
            if not n:
                err(w, f"status {st} but no dates")
            if st == "verified" and not r.get("source"):
                err(w, "verified needs a region source")
            if st == "verified" and not r.get("stages") and not r.get("provinces"):
                err(w, "verified needs course start/end")
    if expect_all:
        missing = set(slugs) - seen
        if missing:
            err(name, f"missing comunidades: {sorted(missing)}")


def check_locales(path, slugs, base):
    doc = load(path)
    if doc is None:
        return
    name = path.name
    year = doc.get("year")
    if year != 2027:
        err(name, "year must be 2027")
    lo, hi = dt.date(2027, 1, 1), dt.date(2027, 12, 31)
    cities = doc.get("cities")
    if not isinstance(cities, list):
        err(name, "cities must be a list")
        return
    regional = {}
    for h in base.get("holidays", []):
        for s in (slugs if h["regions"] == "all" else h["regions"]):
            regional.setdefault(s, set()).add(h["date"])
    seen = set()
    for c in cities:
        w = f"{name}:{c.get('slug')}"
        for k in ("slug", "name", "province", "region"):
            if not c.get(k):
                err(w, f"{k} missing")
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", c.get("slug") or ""):
            err(w, "slug must be lowercase-ascii-with-dashes")
        if c.get("slug") in seen:
            err(w, "duplicate slug")
        seen.add(c.get("slug"))
        if c.get("region") not in slugs:
            err(w, f"unknown region {c.get('region')!r}")
        if not isinstance(c.get("capital"), bool):
            err(w, "capital must be true/false")
        st = c.get("status")
        if st not in ("boletin", "ayuntamiento", "unpublished"):
            err(w, f"bad status {st!r}")
        hol = c.get("holidays")
        if st == "unpublished":
            if hol is not None:
                err(w, "unpublished but holidays not null")
            if not c.get("note"):
                err(w, "unpublished needs a note")
            if c.get("source") is not None:
                source(w, c["source"], required=False)
            continue
        if not isinstance(hol, list) or not hol:
            err(w, f"status {st} needs a non-empty holidays list")
            continue
        source(w, c.get("source"))
        if len(hol) != 2:
            warn(w, f"{len(hol)} local holidays (usually 2)")
        dates = []
        for i, h in enumerate(hol):
            d = date(f"{w}.holidays[{i}]", h.get("date"), lo, hi)
            if not h.get("name"):
                err(f"{w}.holidays[{i}]", "name missing")
            if d:
                dates.append(h["date"])
                if d.weekday() == 6:
                    warn(f"{w}.holidays[{i}]", f"{d} is a Sunday")
                if h["date"] in regional.get(c.get("region"), set()):
                    warn(f"{w}.holidays[{i}]", f"{d} is already a BOE holiday in {c.get('region')}")
        if len(set(dates)) != len(dates):
            err(w, "repeated dates")


def main():
    slugs, base = region_slugs()
    if len(slugs) != 19:
        err("2027.json", f"expected 19 regions, got {len(slugs)}")
    for p in sorted(DATA.glob("escolar-*.json")):
        check_escolar(p, slugs, expect_all=p.name == "escolar-2026-27.json")
    loc = DATA / "locales-2027.json"
    if loc.exists():
        check_locales(loc, slugs, base)
    else:
        warn("locales-2027.json", "file not found")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
