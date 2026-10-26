"""Validate data/i18n.json against data/2027.json.

Checks: every region, holiday (including island/Aran holidays) and zone text in 2027.json has
ca/gl/eu translations; every ui key has es/ca/gl/eu; placeholders survive translation; the owner's
naming rule for six regions; month and weekday lists are complete.

Run: python data/check_i18n.py   (exit 1 on any problem)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANGS = ("ca", "gl", "eu")
ALL = ("es",) + LANGS
RULE = {  # owner's explicit choice, same in every non-Spanish version
    "galicia": "Galiza", "comunitat-valenciana": "País Valencià", "baleares": "Illes Balears",
    "pais-vasco": "Euskal Herria", "navarra": "Nafarroa", "cataluna": "Catalunya",
}
REGION_FIELDS = ("name", "short", "official", "in", "of")
# {region}, {region_in} and {region_of} are interchangeable: each language picks the form its grammar needs.
PH_ALIASES = {"region_in": "region", "region_of": "region"}

errors = []


def err(msg):
    errors.append(msg)


def ok_text(v):
    return isinstance(v, str) and v.strip() != ""


def texts(v):
    """A ui value is a string or a plural dict {"one": ..., "other": ...}."""
    if isinstance(v, dict):
        return [v.get("one"), v.get("other")]
    return [v]


def placeholders(s):
    return {PH_ALIASES.get(p, p) for p in re.findall(r"\{(\w+)\}", s or "")}


def main():
    data = json.loads((HERE / "2027.json").read_text(encoding="utf-8"))
    i18n = json.loads((HERE / "i18n.json").read_text(encoding="utf-8"))

    # Regions
    regions = i18n.get("regions", {})
    for r in data["regions"]:
        slug = r["slug"]
        tr = regions.get(slug)
        if not tr:
            err(f"region {slug}: missing")
            continue
        for lang in LANGS:
            entry = tr.get(lang) or {}
            for f in REGION_FIELDS:
                if not ok_text(entry.get(f)):
                    err(f"region {slug}.{lang}.{f}: missing")
            if slug in RULE and entry.get("name") != RULE[slug]:
                err(f"region {slug}.{lang}.name: must be {RULE[slug]!r} (owner rule), got {entry.get('name')!r}")
    for slug in regions:
        if slug not in {r["slug"] for r in data["regions"]}:
            err(f"region {slug}: not in 2027.json")

    # Holidays, including the ones zones add
    names = {h["name"] for h in data["holidays"]}
    for z in data.get("zones", {}).values():
        for o in z["options"]:
            if o.get("add"):
                names.add(o["add"]["name"])
    hol = i18n.get("holidays", {})
    for n in sorted(names):
        for lang in LANGS:
            if not ok_text((hol.get(n) or {}).get(lang)):
                err(f"holiday {n!r}.{lang}: missing")
    for n in hol:
        if n not in names:
            err(f"holiday {n!r}: not in 2027.json (renamed upstream?)")

    # Zones: label, note, option names
    zones = i18n.get("zones", {})
    for zslug, z in data.get("zones", {}).items():
        tz = zones.get(zslug) or {}
        for f in ("label", "note"):
            for lang in LANGS:
                if not ok_text((tz.get(f) or {}).get(lang)):
                    err(f"zone {zslug}.{f}.{lang}: missing")
        for o in z["options"]:
            to = (tz.get("options") or {}).get(o["slug"]) or {}
            for lang in LANGS:
                if not ok_text(to.get(lang)):
                    err(f"zone {zslug}.options.{o['slug']}.{lang}: missing")

    # UI strings: all four languages, same placeholders as Spanish
    for key, tr in i18n.get("ui", {}).items():
        for lang in ALL:
            v = tr.get(lang)
            if v is None or not all(ok_text(t) for t in texts(v)):
                err(f"ui {key}.{lang}: missing")
        es = " ".join(t or "" for t in texts(tr.get("es")))
        want = placeholders(es)
        for lang in LANGS:
            for t in texts(tr.get(lang)):
                got = placeholders(t)
                if t and got != want:
                    err(f"ui {key}.{lang}: placeholders {sorted(got)} != es {sorted(want)}")

    # Months and weekdays
    for lang in ALL:
        m = (i18n.get("months") or {}).get(lang) or {}
        for f in ("full", "short"):
            if len(m.get(f) or []) != 12 or not all(ok_text(x) for x in m.get(f) or []):
                err(f"months.{lang}.{f}: need 12 names")
        w = (i18n.get("weekdays") or {}).get(lang) or {}
        for f in ("full", "short", "two", "one"):
            if len(w.get(f) or []) != 7 or not all(ok_text(x) for x in w.get(f) or []):
                err(f"weekdays.{lang}.{f}: need 7 names (Monday first)")
        if not ok_text((i18n.get("date_patterns") or {}).get(lang, {}).get("long")):
            err(f"date_patterns.{lang}.long: missing")

    if errors:
        print("\n".join(errors))
        print(f"FAIL · {len(errors)} problems")
        return 1
    print(f"ok · {len(data['regions'])} regions · {len(names)} holidays · {len(i18n['ui'])} ui strings · {', '.join(ALL)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
