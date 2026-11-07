"""Match municipality names printed in bulletins to INE codes from data/municipios.json.

    from muni_match import Matcher, write_part
    mt = Matcher()
    ine = mt.match("Coruña (A)", province="15")        # -> "15030" or None
    ine = mt.match("Alacant", region="comunitat-valenciana")

write_part(source_id, source_dict, {ine: {"holidays": [...], "note": ...}}) writes data/tools/parts-2026/<source_id>.json,
which merge_locales_2026.py combines into data/locales-2026.json.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "data" / "tools" / "parts-2026"

ARTS = r"(el|la|los|las|l|les|els|es|sa|ses|a|o|os|as|lo)"


def norm(s):
    """Lowercase ascii, articles moved/removed, punctuation collapsed."""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = s.replace("’", "'").replace("`", "'").replace("·", "").replace(".", " ")
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s*\((" + ARTS + r")\)\s*$", r", \1", s)          # "Coruña (A)" -> "coruna, a"
    s = re.sub(r",\s*" + ARTS + r"'?\s*$", "", s)                    # drop trailing ", la"
    s = re.sub(r"^" + ARTS + r"(\s+|')", "", s)                      # drop leading "la " / "l'"
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s


class Matcher:
    def __init__(self):
        self.munis = json.loads((ROOT / "data" / "municipios.json").read_text("utf-8"))["municipios"]
        self.by_ine = {m["ine"]: m for m in self.munis}
        self.index = {}
        for m in self.munis:
            names = {m["name"], m["ine_name"], m["name_es"], *m["aliases"]}
            for n in list(names):
                names.update(p.strip() for p in n.split("/"))
            for n in names:
                if n:
                    self.index.setdefault(norm(n), set()).add(m["ine"])

    def candidates(self, name, province=None, region=None):
        keys = {norm(name)}
        keys.update(norm(p) for p in re.split(r"\s*/\s*", name))
        out = set()
        for k in keys:
            out |= self.index.get(k, set())
        if province:
            out = {c for c in out if c[:2] == province}
        if region:
            out = {c for c in out if self.by_ine[c]["region"] == region}
        return out

    def match(self, name, province=None, region=None):
        c = self.candidates(name, province, region)
        return next(iter(c)) if len(c) == 1 else None


def write_part(source_id, source, municipios, region=None, unmatched=None):
    """source = {"title", "url", "published"}; municipios = {ine: {"holidays": [{"date","name"}], "note"?}}"""
    PARTS.mkdir(parents=True, exist_ok=True)
    for ine, v in municipios.items():
        assert re.fullmatch(r"\d{5}", ine), ine
        ds = [h["date"] for h in v["holidays"]]
        assert all(re.fullmatch(r"2026-\d\d-\d\d", d) for d in ds), (ine, ds)
        assert ds == sorted(set(ds)), (ine, ds)
    out = {"source_id": source_id, "source": source, "region": region, "count": len(municipios),
           "unmatched": unmatched or [], "municipios": dict(sorted(municipios.items()))}
    (PARTS / f"{source_id}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", "utf-8", newline="\n")
    print(f"{source_id}: {len(municipios)} municipios, {len(unmatched or [])} unmatched")
