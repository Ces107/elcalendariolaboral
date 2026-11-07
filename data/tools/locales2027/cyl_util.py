"""Helpers for the Castilla y León provincial bulletins (parse_bop-*.py).

Text comes from PyMuPDF spans with coordinates (never pdftotext -layout). Fonts
without a ToUnicode map (BOP León, BOP Burgos) are decoded by glyphdecode.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402

MONTH_RE = (r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|"
            r"octubre|noviembre|diciembre)")


def spans(doc, pn, decode=False):
    """[(x0, y0, x1, y1, text, bold)] for page pn."""
    page = doc[pn]
    out = []
    if decode:
        import glyphdecode
        for bb, font, chars in glyphdecode.decoded_spans(doc, page):
            t = "".join(c for _, c in chars)
            if t.strip():
                out.append((bb[0], bb[1], bb[2], bb[3], t, "Bold" in font))
        return out
    d = page.get_text("dict")
    for b in d["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    x0, y0, x1, y1 = s["bbox"]
                    out.append((x0, y0, x1, y1, s["text"], bool(s["flags"] & 16) or "Bold" in s["font"]))
    return out


def lines(sp, tol=2.5):
    """Group spans into printed lines by their baseline (y1). -> [(y, [spans sorted by x])]."""
    rows = []
    for s in sorted(sp, key=lambda s: (s[3], s[0])):
        if rows and abs(rows[-1][0] - s[3]) <= tol:
            rows[-1][1].append(s)
        else:
            rows.append([s[3], [s]])
    return [(y, sorted(ss, key=lambda s: s[0])) for y, ss in rows]


def text_of(ss):
    return re.sub(r"\s+", " ", " ".join(s[4] for s in ss)).strip()


def clean(t):
    return re.sub(r"\s+", " ", t).strip(" .,;:")


DATE_GROUP = re.compile(
    r"(\d{1,2})((?:\s*(?:,|y|e)\s*\d{1,2})*)\s+(?:de\s+)?(?:de\s+)?" + MONTH_RE + r"\b", re.I)


def parse_free(text):
    """Spanish free text -> [(iso, name|None)].

    '24 de junio, San Juan y 5 de octubre, San Froilán'
    '27 y 28 de mayo'   '14 y 15 de septiembre, festividad del Cristo'
    Parenthesised remarks ('por traslado del 17 de enero') are ignored for dates.
    'X. Se traslada al 9 de diciembre' replaces the preceding date.
    """
    t = re.sub(r"\([^)]*\)", " ", text)
    moved = re.search(r"[Ss]e traslada al?\s+(?:d[ií]a\s+)?(\d{1,2})\s+de\s+" + MONTH_RE, t)
    if moved:
        t = t[:moved.start()]
    groups = list(DATE_GROUP.finditer(t))
    out = []
    for i, m in enumerate(groups):
        days = [m.group(1)] + re.findall(r"\d{1,2}", m.group(2) or "")
        month = m.group(3)
        end = groups[i + 1].start() if i + 1 < len(groups) else len(t)
        name = t[m.end():end]
        name = re.sub(r"^\s*[,:.]?\s*", "", name)
        name = re.sub(r"\s+y\s*$", "", name.strip())
        name = clean(name) or None
        if name in ("y", "e"):  # '10 de febrero y 9 de julio': no name between the dates
            name = None
        for dd in days:
            out.append([common.iso(int(dd), month), name])
    if moved:
        new = common.iso(int(moved.group(1)), moved.group(2))
        if out:
            out[-1][0] = new
        else:
            out.append([new, None])
    return [tuple(x) for x in out]


def numeric_date(s):
    """'04.06.2027' / '04/06/2027' -> iso; returns (iso|None, year)."""
    m = re.search(r"(\d{1,2})[./](\d{1,2})[./](\d{4})", s)
    if not m:
        return None, None
    y = int(m.group(3))
    if y != common.YEAR:
        return None, y
    return common.iso(int(m.group(1)), int(m.group(2))), y


def fmt_dates(hs):
    return ", ".join(h[0] if isinstance(h, (tuple, list)) else h["date"] for h in hs)


def sub_note(subs):
    """subs: [(locality, [(iso, name)])] -> note sentence."""
    if not subs:
        return ""
    parts = []
    for loc, hs in subs:
        parts.append(f"{loc} {fmt_dates(hs)}" if hs else f"{loc} (no dates)")
    return ("The bulletin also lists other localities of the municipality with their own days: "
            + "; ".join(parts) + ".")


def hol(pairs):
    return [{"date": d, "name": n} for d, n in pairs]


def bulletin_name(s):
    """'ALDEHUELA, (LA)' / 'ARENAL (EL)' -> 'La Aldehuela' style lookup string (keeps original too)."""
    s = clean(s).replace("*", "").strip()
    m = re.match(r"^(.*?)[,\s]*\((EL|LA|LOS|LAS|LO)\s*\)\s*$", s, re.I)
    if m:
        return f"{m.group(2)} {m.group(1)}".strip()
    return s


SMALL = {"de", "del", "la", "las", "los", "el", "y", "e", "en", "a", "al", "o", "u"}


def nice(s):
    """'NTRA. SRA. DE LA ASUNCIÓN' -> 'Ntra. Sra. de la Asunción' (only for all-caps text)."""
    if not s or not s.isupper():
        return s
    out = []
    for i, w in enumerate(s.lower().split()):
        out.append(w if (i and w in SMALL) else w[:1].upper() + w[1:])
    return " ".join(out)


def build_rows(ine, cpro, recs):
    """recs: [{"muni": bulletin municipality name, "locality": None|str,
               "holidays": [{"date","name"}], "note": str}]
    One row per municipality: the head record (locality None) gives the holidays;
    other localities go to row["localities"] and to the note. A municipality listed
    only through its localities gets holidays [] and an explanatory note."""
    groups, order = {}, []
    for r in recs:
        look = bulletin_name(r["muni"])
        code, how = ine.match(cpro, look)
        key = code or ("?" + look)
        if key not in groups:
            groups[key] = {"name": r["muni"], "cpro": cpro, "ine": code, "match": how,
                           "holidays": None, "status": "boletin", "note": "", "localities": []}
            order.append(key)
        g = groups[key]
        if r.get("locality"):
            g["localities"].append({"name": r["locality"], "holidays": r["holidays"],
                                    **({"note": r["note"]} if r.get("note") else {})})
        else:
            if g["holidays"] is not None:
                raise ValueError(f"two head records for {r['muni']} ({code})")
            g["holidays"] = r["holidays"]
            g["name"] = r["muni"]
            g["note"] = r.get("note", "")
    rows = []
    for k in order:
        g = groups[k]
        notes = [g["note"]] if g["note"] else []
        if g["holidays"] is None:
            g["holidays"] = []
            notes.insert(0, "The bulletin gives no municipality-wide days, only days for each locality.")
        elif len(g["holidays"]) == 1:
            notes.insert(0, "The bulletin lists only one local day.")
        if g["localities"]:
            notes.append(sub_note([(l["name"], l["holidays"]) for l in g["localities"]]))
        else:
            del g["localities"]
        g["note"] = " ".join(n for n in notes if n).strip()
        rows.append(g)
    return rows
