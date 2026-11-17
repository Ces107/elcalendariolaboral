"""Comunitat Valenciana 2027: since 2026 each Dirección Territorial de Vivienda, Empleo, Juventud e Igualdad
approves its province's local holidays and publishes them in the BOP (no single DOGV resolution as in 2026).

The annex is prose, one paragraph per municipality:
    "ALICANTE: 8 de abril, jueves, Festividad de Santa Faz; 24 de junio, jueves, Fogueres de Sant Joan."
    "CASTELLÓN DE LA PLANA:  1 de marzo, lunes de la Magdalena y 29 de junio, festividad de San Pedro."
    "AIGÜES: 26 y 27 de agosto, jueves y viernes respectivamente."
    "BENIARRÉS: Lunes 11 de octubre; martes 7 de diciembre"
    "• Eatim de La Xara, dependiente de Dènia : 3 de septiembre, ..."   (entidad local menor -> localities)

parse_annex() returns one dict per paragraph with the dates found, the holiday names (what is printed after each
date, weekday words and connectors removed) and a weekday check: every weekday word printed in the paragraph is
compared with the real weekday of the dates. Anything odd is reported, never corrected silently: the per-bulletin
script decides (with a note) what to do with each reported paragraph.
"""
import datetime as dt
import re

import common

WD = {"lunes": 0, "martes": 1, "miercoles": 2, "jueves": 3, "viernes": 4, "sabado": 5, "domingo": 6}
WD_ES = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MONTH_RE = ("enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre")
# "5 de abril", "5de abril", "05 de abril", "Lunes 16 agosto", "26 y 27 de agosto", "5 de abril de 2026"
DATE_RE = re.compile(r"(?<![\d])(\d{1,3})(?:\s+y\s+(\d{1,2}))?\s*(?:de\s+)?(" + MONTH_RE + r")\b(\s+de\s+20\d\d)?",
                     re.I)
WD_RE = re.compile(r"\b(lunes|martes|mi[eé]rcoles|jueves|viernes|s[aá]bado|domingo)\b", re.I)
HEAD_RE = re.compile(r"^\s*(?:•\s*)?([A-ZÁÉÍÓÚÀÈÒÜÏÑÇ][A-ZÁÉÍÓÚÀÈÒÜÏÑÇ0-9 ´’'`.,()\-/]+?)\s*:\s*(.*)$")
EATIM_RE = re.compile(r"^\s*(?:•\s*)?Eatim de (.+?), dependiente de (.+?)\s*:\s*(.*)$", re.I)
NAME_PREFIX = re.compile(r"^(?:festividad|festivitat)\s+(?:de\s+(?:la\s+|los\s+|las\s+)?|del\s+)?|^de\s+", re.I)


def clean_lines(text, drop):
    """Annex text with page furniture removed. drop: regexes of header/footer lines."""
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if not s or s == "•":
            out.append("" if not s else "•")
            continue
        if any(re.search(p, s) for p in drop):
            continue
        out.append(s)
    return out


def paragraphs(lines):
    """Join continuation lines: a new paragraph starts with 'NAME:' in capitals or with an Eatim bullet."""
    paras, cur = [], None
    pending_bullet = False
    for s in lines:
        if s == "":
            continue
        if s == "•":
            pending_bullet = True
            continue
        starts = bool(EATIM_RE.match(s)) or bool(HEAD_RE.match(s) and HEAD_RE.match(s).group(1).upper() == HEAD_RE.match(s).group(1))
        if starts:
            if cur:
                paras.append(cur)
            cur = ("• " if pending_bullet else "") + s
        elif cur is not None:
            # words split at line end with a soft hyphen ("festivi-\ndad")
            cur = cur[:-1] + s if cur.endswith(("­", "-")) and not cur.endswith(" -") else cur + " " + s
        pending_bullet = False
    if cur:
        paras.append(cur)
    return [p.replace("­", "") for p in paras]


def _name(seg):
    """Name printed after a date: the date's own weekday (", lunes", "jueves y viernes") and the next date's leading
    weekday ("; viernes") are dropped; weekdays that are part of a name stay ("Jueves Santo", "lunes de Pascua",
    "último jueves", "Santo Domingo")."""
    w = WD_RE.pattern[3:-3]
    s = re.sub(r"^\s*,?\s*(?:" + w + r")(?:\s+y\s+(?:" + w + r"))?(?!\s+(?:de\b|santo\b))\b", " ", seg, flags=re.I)
    s = re.sub(r"[;,:]?\s*(?:" + w + r")\s*,?\s*$", " ", s, flags=re.I)
    s = re.sub(r"\brespectivamente\b", " ", s, flags=re.I)
    s = re.sub(r"^[\s,;:.y]+|[\s,;:.]+$", "", s)
    s = re.sub(r"[\s,;:.]+y$", "", s).strip(" ,;:.")
    s = re.sub(r"^y\s+", "", s)
    s = re.sub(r"\s+", " ", s).strip(" ,;:.")
    if not s or len(s) < 3:
        return None
    s = NAME_PREFIX.sub("", s).strip(" ,“”\"")
    return (s[0].upper() + s[1:]) if s else None


def parse_entry(body):
    """body: text after 'NAME:'. -> dict(dates=[iso], names=[str|None], printed_wd=[int], issues=[str])."""
    issues = []
    toks = list(DATE_RE.finditer(body))
    dates, spans = [], []
    for i, m in enumerate(toks):
        d1, d2, mon, yr = m.group(1), m.group(2), m.group(3), m.group(4)
        if yr and "2027" not in yr:
            issues.append(f"year printed as '{yr.strip()}'")
        nxt = toks[i + 1].start() if i + 1 < len(toks) else len(body)
        seg = body[m.end():nxt]
        for d in [d1] + ([d2] if d2 else []):
            try:
                iso = common.iso(int(d), mon.lower().replace("setiembre", "septiembre"))
            except ValueError:
                issues.append(f"impossible date '{d} de {mon}'")
                continue
            dates.append(iso)
            spans.append(seg)
    names = [_name(s) for s in spans]
    # weekday check: only the weekday printed next to each date ("5 de abril, lunes", "Lunes 5 de abril",
    # "26 y 27 de agosto, jueves y viernes"); weekdays inside names ("Santo Domingo", "último jueves") are ignored
    wd = lambda w: WD[common.strip_accents(w).lower()]  # noqa: E731
    k = 0
    for i, m in enumerate(toks):
        n = 2 if m.group(2) else 1
        got = dates[k:k + n]
        k += n
        if len(got) != n:
            continue
        after = body[m.end():]
        before = body[:m.start()]
        a = re.match(r"^\s*,?\s*(" + WD_RE.pattern[3:-3] + r")(?:\s+y\s+(" + WD_RE.pattern[3:-3] + r"))?\b", after, re.I)
        b = re.search(r"\b(" + WD_RE.pattern[3:-3] + r")\s*,?\s*$", before, re.I)
        printed = [a.group(1)] + ([a.group(2)] if a.group(2) else []) if a else ([b.group(1)] if b and n == 1 else [])
        for d, w in zip(got, printed):
            real = dt.date.fromisoformat(d).weekday()
            if wd(w) != real:
                issues.append(f"{d} printed '{w.lower()}' but is a {WD_ES[real]}")
    if len(set(dates)) != len(dates):
        issues.append("same date printed twice")
    return {"dates": dates, "names": names, "issues": issues}


def parse_annex(paras):
    """-> list of dict(kind='muni'|'eatim', name, parent?, body, dates, names, issues)."""
    out = []
    for p in paras:
        m = EATIM_RE.match(p)
        if m:
            r = parse_entry(m.group(3))
            out.append(dict(kind="eatim", name=m.group(1).strip(), parent=m.group(2).strip(), body=m.group(3), **r))
            continue
        m = HEAD_RE.match(p)
        r = parse_entry(m.group(2))
        out.append(dict(kind="muni", name=m.group(1).strip(" ,"), body=m.group(2).strip(), **r))
    return out


def bulletin_name(name):
    """'ALFÀS DEL PÍ (L’)' -> "L'ALFÀS DEL PÍ" style key the matcher understands; ´ and ’ -> '."""
    n = name.replace("´", "'").replace("’", "'").replace("`", "'")
    m = re.match(r"^(.*?)\s*\(\s*(L'|EL|LA|LOS|LAS|ELS|LES)\s*\)$", n, re.I)
    if m:
        art = m.group(2)
        n = f"{art}{m.group(1)}" if art.endswith("'") else f"{art} {m.group(1)}"
    m = re.match(r"^(.*?),\s*(L|EL|LA)$", n, re.I)  # "ATZÚBIA, L"
    if m:
        n = f"{m.group(2)}'{m.group(1)}" if m.group(2).upper() == "L" else f"{m.group(2)} {m.group(1)}"
    return n


def match(ine, matcher, cpro, name):
    """INE code via common.INE (bulletin spellings) then data/tools/muni_match.py (site names + aliases)."""
    bn = bulletin_name(name)
    code, how = ine.match(cpro, bn, fuzzy=False)
    if code:
        return code, how
    c = matcher.candidates(bn, province=cpro)
    if len(c) == 1:
        return c.pop(), "muni_match"
    code, how = ine.match(cpro, bn, fuzzy=True)
    return code, how
