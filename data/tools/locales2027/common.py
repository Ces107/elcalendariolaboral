"""Shared helpers for the 2027 local-holiday ingestion (data/locales-2027-all.json).

Every script here is run as   python -I <script> <workdir> [...]
<workdir> is a scratch folder OUTSIDE the repo that holds:
  dl/<source-id>/...      downloaded bulletins (untrusted data, never executed)
  dl/ine/dic26.xlsx       INE "diccionario" of municipality codes (1 Jan 2026)
  parsed/<source-id>.json one file per bulletin, written by save_parsed()

-I drops the user site-packages, so PyMuPDF/openpyxl are added back explicitly
from the user's own site dir (never from the workdir).
"""
import datetime as _dt
import difflib
import json
import os
import re
import site
import sys
import unicodedata

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_usp = site.getusersitepackages()
if _usp not in sys.path:
    sys.path.append(_usp)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
YEAR = 2027

# INE province code -> (province name used on the site, region slug)
PROVINCES = {
    "01": ("Álava", "pais-vasco"), "02": ("Albacete", "castilla-la-mancha"),
    "03": ("Alicante", "comunitat-valenciana"), "04": ("Almería", "andalucia"),
    "05": ("Ávila", "castilla-y-leon"), "06": ("Badajoz", "extremadura"),
    "07": ("Illes Balears", "baleares"), "08": ("Barcelona", "cataluna"),
    "09": ("Burgos", "castilla-y-leon"), "10": ("Cáceres", "extremadura"),
    "11": ("Cádiz", "andalucia"), "12": ("Castellón", "comunitat-valenciana"),
    "13": ("Ciudad Real", "castilla-la-mancha"), "14": ("Córdoba", "andalucia"),
    "15": ("A Coruña", "galicia"), "16": ("Cuenca", "castilla-la-mancha"),
    "17": ("Girona", "cataluna"), "18": ("Granada", "andalucia"),
    "19": ("Guadalajara", "castilla-la-mancha"), "20": ("Gipuzkoa", "pais-vasco"),
    "21": ("Huelva", "andalucia"), "22": ("Huesca", "aragon"),
    "23": ("Jaén", "andalucia"), "24": ("León", "castilla-y-leon"),
    "25": ("Lleida", "cataluna"), "26": ("La Rioja", "la-rioja"),
    "27": ("Lugo", "galicia"), "28": ("Madrid", "madrid"),
    "29": ("Málaga", "andalucia"), "30": ("Murcia", "murcia"),
    "31": ("Navarra", "navarra"), "32": ("Ourense", "galicia"),
    "33": ("Asturias", "asturias"), "34": ("Palencia", "castilla-y-leon"),
    "35": ("Las Palmas", "canarias"), "36": ("Pontevedra", "galicia"),
    "37": ("Salamanca", "castilla-y-leon"), "38": ("Santa Cruz de Tenerife", "canarias"),
    "39": ("Cantabria", "cantabria"), "40": ("Segovia", "castilla-y-leon"),
    "41": ("Sevilla", "andalucia"), "42": ("Soria", "castilla-y-leon"),
    "43": ("Tarragona", "cataluna"), "44": ("Teruel", "aragon"),
    "45": ("Toledo", "castilla-la-mancha"), "46": ("Valencia", "comunitat-valenciana"),
    "47": ("Valladolid", "castilla-y-leon"), "48": ("Bizkaia", "pais-vasco"),
    "49": ("Zamora", "castilla-y-leon"), "50": ("Zaragoza", "aragon"),
    "51": ("Ceuta", "ceuta"), "52": ("Melilla", "melilla"),
}

# month names: es, gl, ca, eu, plus abbreviations seen in bulletins
MONTHS = {}
for i, names in enumerate([
    "enero xaneiro gener urtarrila ene xan gen urt",
    "febrero febreiro febrer otsaila feb otsa",
    "marzo marzo marc martxoa mar mart",
    "abril abril abril apirila abr apir",
    "mayo maio maig maiatza may mai",
    "junio xuno xunio juny ekaina jun xun ekai",
    "julio xullo juliol uztaila jul xul uzt",
    "agosto agosto agost abuztua ago abu",
    "septiembre setembro setembre iraila sep set sept ira",
    "octubre outubro octubre urria oct out urr",
    "noviembre novembro novembre azaroa nov aza",
    "diciembre decembro desembre abendua dic dec des abe",
], start=1):
    for n in names.split():
        MONTHS.setdefault(n, i)


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def month_num(word):
    w = strip_accents(word).lower().strip(" .,;:")
    w = w.replace("ç", "c")
    return MONTHS.get(w)


def iso(day, month):
    """day:int, month:int|str -> '2027-MM-DD' (validated)."""
    m = month if isinstance(month, int) else month_num(month)
    if not m:
        raise ValueError(f"bad month {month!r}")
    return _dt.date(YEAR, m, int(day)).isoformat()


ARTICLES = {"el", "la", "los", "las", "l", "els", "les", "o", "a", "os", "as", "lo", "es", "sa", "ses"}


def norm(s):
    s = strip_accents(s).lower()
    s = s.replace("’", "'").replace("`", "'")
    s = re.sub(r"[^a-z0-9ñ]+", " ", s.replace("ñ", "n"))
    return re.sub(r"\s+", " ", s).strip()


def name_keys(name):
    """All lookup keys for a municipality name (INE or bulletin spelling)."""
    keys = set()
    parts = [p for p in re.split(r"\s*/\s*|\s+-\s+|\s*\(\s*|\s*\)\s*", name) if p.strip()]
    for p in [name] + parts:
        p = p.strip()
        m = re.match(r"^(.*),\s*(\S+)$", p)  # INE "Coruña, A" / "Alfàs del Pi, l'"
        if m and norm(m.group(2)) in ARTICLES:
            art = m.group(2)
            joined = f"{art}{m.group(1)}" if art.endswith("'") else f"{art} {m.group(1)}"
            for q in (joined, m.group(1)):
                keys.add(norm(q))
        n = norm(p)
        if n:
            keys.add(n)
            w = n.split(" ", 1)
            if len(w) == 2 and w[0] in ARTICLES:
                keys.add(w[1])
    return {k for k in keys if k}


class INE:
    """INE municipality dictionary with name matching per province."""

    def __init__(self, workdir):
        import openpyxl
        path = os.path.join(workdir, "dl", "ine", "dic26.xlsx")
        wb = openpyxl.load_workbook(path, read_only=True)
        self.by_code = {}
        self.by_prov = {}
        for r in wb.active.iter_rows(min_row=3, values_only=True):
            if not r or not r[1] or not r[2]:
                continue
            code = f"{r[1]}{r[2]}"
            self.by_code[code] = r[4]
            self.by_prov.setdefault(r[1], []).append(code)
        self.keys = {}  # (cpro, key) -> set(codes)
        for code, name in self.by_code.items():
            for k in name_keys(name):
                self.keys.setdefault((code[:2], k), set()).add(code)
        self.manual = {}  # (cpro, norm(bulletin name)) -> code

    def add_manual(self, cpro, bulletin_name, code):
        assert code in self.by_code, code
        self.manual[(cpro, norm(bulletin_name))] = code

    def match(self, cpro, name, fuzzy=True):
        """-> (code|None, method). method in manual/exact/fuzzy:<score>/ambiguous/none."""
        n = norm(name)
        if (cpro, n) in self.manual:
            return self.manual[(cpro, n)], "manual"
        hits = set()
        for k in name_keys(name):
            hits |= self.keys.get((cpro, k), set())
        if len(hits) == 1:
            return hits.pop(), "exact"
        if len(hits) > 1:
            return None, "ambiguous:" + ",".join(sorted(hits))
        if not fuzzy:
            return None, "none"
        cands = {}
        for code in self.by_prov.get(cpro, []):
            for k in name_keys(self.by_code[code]):
                cands[k] = code
        best = difflib.get_close_matches(n, list(cands), n=2, cutoff=0.86)
        if best:
            score = difflib.SequenceMatcher(None, n, best[0]).ratio()
            return cands[best[0]], f"fuzzy:{score:.2f}:{best[0]}"
        return None, "none"


def save_parsed(workdir, source_id, meta, rows, spotcheck, extra=None):
    """Write parsed/<source_id>.json.

    meta: {"title","url","published"(YYYY-MM-DD), "region"}
    rows: [{"name": bulletin spelling, "cpro": "30", "ine": "30001"|None,
            "match": method, "holidays": [{"date","name"|None}],
            "status": "boletin"|"ayuntamiento", "note": str (optional)}]
    spotcheck: free text describing the >=5 random rows re-checked against the PDF.
    """
    for r in rows:
        for h in r["holidays"]:
            assert re.fullmatch(r"2027-\d\d-\d\d", h["date"]), (r, h)
        r["holidays"].sort(key=lambda h: h["date"])
    out = dict(meta, id=source_id, rows=rows, spotcheck=spotcheck, **(extra or {}))
    d = os.path.join(workdir, "parsed")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"{source_id}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    unmatched = [r["name"] for r in rows if not r.get("ine")]
    fuzzy = [(r["name"], r["match"]) for r in rows if str(r.get("match", "")).startswith("fuzzy")]
    print(f"{source_id}: {len(rows)} rows, {len(unmatched)} without INE, {len(fuzzy)} fuzzy")
    for x in unmatched:
        print("  NO INE:", x)
    for x in fuzzy:
        print("  FUZZY:", x)
    return out


def coverage(ine, rows, cpros):
    """Which INE municipalities of the given provinces are missing from rows."""
    have = {r["ine"] for r in rows if r.get("ine")}
    miss = [(c, ine.by_code[c]) for p in cpros for c in ine.by_prov.get(p, []) if c not in have]
    return miss


def workdir_from_argv():
    if len(sys.argv) < 2:
        sys.exit("usage: python -I script.py <workdir>")
    return os.path.abspath(sys.argv[1])
