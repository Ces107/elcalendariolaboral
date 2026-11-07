"""Merge data/tools/parts-2026/*.json into data/locales-2026.json (2026 local holidays, reference only).

    python -E -P data/tools/merge_locales_2026.py

A municipality present in two parts keeps the first part in PRIORITY order (regional compilation first) and the
conflict is printed. Every holiday must be a non-Sunday 2026 date; two dates unless a "note" explains why not.
"""
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "data" / "tools" / "parts-2026"
# Parts kept on disk but not merged. jcyl-2026: the Junta's open-data CSV has wrong INE codes and 2024/2025 dates in
# places; it only filled 11 gaps not in any BOP, so it is left out to keep the file bulletin-only.
EXCLUDE = {"jcyl-2026"}


def main():
    munis = {m["ine"]: m for m in json.loads((ROOT / "data" / "municipios.json").read_text("utf-8"))["municipios"]}
    parts = [json.loads(p.read_text("utf-8")) for p in sorted(PARTS.glob("*.json")) if p.stem not in EXCLUDE]
    parts.sort(key=lambda p: (p.get("priority", 1), p["source_id"]))
    sources, out, problems = {}, {}, []
    for p in parts:
        sid = p["source_id"]
        sources[sid] = p["source"]
        for ine, v in p["municipios"].items():
            if ine not in munis:
                problems.append(f"{sid}: unknown INE {ine}")
                continue
            ds = [h["date"] for h in v["holidays"]]
            if ine in out:
                if [h["date"] for h in out[ine]["holidays"]] != ds:
                    problems.append(f"{sid}: {ine} {munis[ine]['name']} {ds} conflicts with {out[ine]['source']} "
                                    f"{[h['date'] for h in out[ine]['holidays']]} (kept the first)")
                continue
            sundays = []
            for d in ds:
                day = dt.date.fromisoformat(d)
                if day.year != 2026:
                    problems.append(f"{sid}: {ine} {d} not 2026")
                if day.weekday() == 6:
                    sundays.append(d)
                    problems.append(f"{sid}: {ine} {munis[ine]['name']} {d} is a Sunday (kept as published, noted)")
            if len(ds) != 2 and not v.get("note"):
                problems.append(f"{sid}: {ine} {munis[ine]['name']} has {len(ds)} dates and no note")
            rec = {"holidays": [{"date": h["date"], "name": h.get("name", "")} for h in v["holidays"]], "source": sid}
            if v.get("nucleos"):  # núcleos / pedanías / parroquias with their own days: [{"name", "holidays"}]
                rec["nucleos"] = v["nucleos"]
            note = v.get("note", "")
            if sundays and "Sunday" not in note:
                note = (note + f" The bulletin gives {', '.join(sundays)}, which falls on a Sunday.").strip()
            if note:
                rec["note"] = note
            out[ine] = rec
    data = {
        "year": 2026,
        "updated": dt.date.today().isoformat(),
        "about": "Fiestas locales de 2026 (2 por municipio) tomadas solo de publicaciones oficiales (boletín autonómico o "
                 "provincial, o datos abiertos de la administración que las fija). Solo como referencia en las páginas de "
                 "municipios sin fiestas de 2027 publicadas: referencia 2026, no oficial para 2027. Clave: código INE.",
        "sources": dict(sorted(sources.items())),
        "municipios": dict(sorted(out.items())),
    }
    head = json.dumps({k: v for k, v in data.items() if k != "municipios"}, ensure_ascii=False, indent=1)[:-2]
    lines = ",\n".join(f'"{k}":' + json.dumps(v, ensure_ascii=False, separators=(",", ":")) for k, v in data["municipios"].items())
    (ROOT / "data" / "locales-2026.json").write_text(f'{head},\n "municipios": {{\n{lines}\n}}}}\n', "utf-8", newline="\n")
    json.loads((ROOT / "data" / "locales-2026.json").read_text("utf-8"))
    by_region = {}
    for ine in out:
        r = munis[ine]["region"]
        by_region[r] = by_region.get(r, 0) + 1
    tot = {}
    for m in munis.values():
        tot[m["region"]] = tot.get(m["region"], 0) + 1
    print(f"{len(out)} municipios with 2026 holidays out of {len(munis)}")
    for r in sorted(tot):
        print(f"  {r:22} {by_region.get(r, 0):5} / {tot[r]}")
    for x in problems:
        print("PROBLEM", x)
    return 1 if any("unknown" in x or "not 2026" in x for x in problems) else 0


if __name__ == "__main__":
    sys.exit(main())
