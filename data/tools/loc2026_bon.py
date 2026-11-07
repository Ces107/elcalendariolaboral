"""Navarra 2026 local holidays.

- 3 December (San Francisco Javier, Día de Navarra) is the local holiday common to the whole Comunidad Foral
  (Resolución 390/2025, de 5 de junio, cited in Resolución 682/2025).
- Each locality's own day: Resolución 682/2025, de 17 de noviembre, del Director General de Economía Social y Trabajo
  (BON núm. 241, 2-12-2025), modified by Resolución 765/2025, de 22 de diciembre (BON núm. 1, 2-1-2026).

Download (outside the repo):
    https://bon.navarra.es/es/anuncio/-/texto/2025/241/12   (r682.html)
    https://bon.navarra.es/es/anuncio/-/texto/2026/1/25     (r765.html)
Run: python -E -P data/tools/loc2026_bon.py r682.html r765.html

The annex lists localities (municipalities and concejos/villages). A locality whose name is a municipality gives that
municipality's own day; "VILLAGE (Municipality)" rows go to the municipality's "nucleos". Rules printed as weekday
expressions ("Lunes siguiente al primer domingo de mayo") are converted only when they are unambiguous calendar rules
(the printed text is kept in the note); anything else ("Viernes de carnaval") is left out and listed as unmatched.
"""
import datetime as dt
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, norm, write_part  # noqa: E402

MES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                   "septiembre", "octubre", "noviembre", "diciembre"], 1)}
DIA = {d: i for i, d in enumerate(["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"])}
ORD = {"primer": 1, "segundo": 2, "tercer": 3, "cuarto": 4, "quinto": 5}
EASTER = dt.date(2026, 4, 5)
FIXED = {"lunes de pentecostés": EASTER + dt.timedelta(days=50), "segundo día de pentecostés": EASTER + dt.timedelta(days=50),
         "martes de carnaval": EASTER - dt.timedelta(days=47), "lunes de carnaval": EASTER - dt.timedelta(days=48),
         "festividad de la ascensión": EASTER + dt.timedelta(days=39)}
NAVARRA = {"date": "2026-12-03", "name": "San Francisco Javier, Día de Navarra"}
SOURCE = {
    "title": "Resolución 682/2025, de 17 de noviembre, del Director General de Economía Social y Trabajo, por la que se "
             "determinan las fiestas locales para el año 2026 en el ámbito de la Comunidad Foral de Navarra (BON núm. 241, "
             "de 2-12-2025), modificada por la Resolución 765/2025, de 22 de diciembre (BON núm. 1, de 2-1-2026); 3 de "
             "diciembre común a toda Navarra por la Resolución 390/2025, de 5 de junio",
    "url": "https://bon.navarra.es/es/anuncio/-/texto/2025/241/12",
    "published": "2025-12-02",
    "modifications": ["https://bon.navarra.es/es/anuncio/-/texto/2026/1/25"],
}


def nth(wd, n, month):
    d = dt.date(2026, month, 1)
    d += dt.timedelta(days=(wd - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def last(wd, month):
    d = dt.date(2026, month + 1, 1) - dt.timedelta(days=1) if month < 12 else dt.date(2026, 12, 31)
    return d - dt.timedelta(days=(d.weekday() - wd) % 7)


def to_date(s):
    """Return (iso date, rule or None) or (None, None)."""
    s0 = s.strip()
    s = s0.lower()
    m = re.fullmatch(r"(\d{1,2}) de (\w+)", s)
    if m and m.group(2) in MES:
        return dt.date(2026, MES[m.group(2)], int(m.group(1))).isoformat(), None
    if s in FIXED:
        return FIXED[s].isoformat(), s0
    m = re.fullmatch(r"(\w+) (siguiente|anterior) al (\w+) domingo de (\w+)", s)
    if m and m.group(1) in DIA and m.group(3) in ORD and m.group(4) in MES:
        sun = nth(6, ORD[m.group(3)], MES[m.group(4)])
        wd = DIA[m.group(1)]
        d = sun + dt.timedelta(days=(wd - 6) % 7 or 7) if m.group(2) == "siguiente" else sun - dt.timedelta(days=(6 - wd) % 7 or 7)
        return d.isoformat(), s0
    m = re.fullmatch(r"(\w+) (\w+) de (\w+)", s)
    if m and m.group(1) in ORD and m.group(2) in DIA and m.group(3) in MES:
        return nth(DIA[m.group(2)], ORD[m.group(1)], MES[m.group(3)]).isoformat(), s0
    if m and m.group(1) == "último" and m.group(2) in DIA and m.group(3) in MES:
        return last(DIA[m.group(2)], MES[m.group(3)]).isoformat(), s0
    return None, None


def rows(path):
    t = Path(path).read_text("utf-8", errors="replace")
    for a, b in re.findall(r"<tr><td><p[^>]*>(.*?)</p></td><td><p[^>]*>(.*?)</p></td></tr>", t):
        a, b = (re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip() for x in (a, b))
        if a != "LOCALIDAD":
            yield a, b


def mods(path):
    t = html.unescape(re.sub(r"<[^>]+>", "\n", Path(path).read_text("utf-8", errors="replace")))
    for m in re.finditer(r"[–—-]\s*([^:\n–—]+?):\s*(\d{1,2} de \w+)\.", t):
        yield m.group(1).strip(), m.group(2)


def main(r682, r765):
    mt = Matcher()
    table = {}
    for loc, when in rows(r682):
        table[loc.upper()] = [loc, when]
    for loc, when in mods(r765):
        keys = [k for k in table if norm(k) == norm(loc)] or [k for k in table if norm(k.split(" (")[0]) == norm(loc)]
        assert len(keys) == 1, f"765 locality not unique in 682: {loc} {keys}"
        key = keys[0]
        table[key][1] = when
    own, nucleos, unmatched = {}, {}, []
    for key, (loc, when) in table.items():
        d, rule = to_date(when)
        if not d:
            unmatched.append(f"{loc}: '{when}' (not a fixed date, left out)")
            continue
        m = re.fullmatch(r"(.+?) \((.+)\)", loc)
        if m:
            p = m.group(2)
            parent = (mt.match(p, province="31") or mt.match("Valle de " + p, province="31")
                      or mt.match("Cendea de " + p, province="31"))
            if not parent:  # "Lizoain" -> "Lizoain-Arriasgoiti": a unique Navarra municipality starting with the name
                starts = [x["ine"] for x in mt.munis if x["province_code"] == "31" and norm(x["name_es"]).startswith(norm(p))]
                parent = starts[0] if len(starts) == 1 else None
            if not parent:
                unmatched.append(f"{loc}: {when} (parent municipality not found)")
                continue
            nucleos.setdefault(parent, []).append({"name": m.group(1).title(), "holidays": [{"date": d, "name": ""}],
                                                   **({"rule": rule} if rule else {})})
            continue
        ine = mt.match(loc, province="31") or mt.match(loc.title(), province="31")
        if not ine:
            unmatched.append(f"{loc}: {when} (village/concejo without parent in the table)")
            continue
        own[ine] = (d, rule, loc)
    out = {}
    for ine in set(own) | set(nucleos):
        rec = {"holidays": [NAVARRA]}
        notes = ["3 December (Día de Navarra) is the local holiday common to all Navarra."]
        if ine in own:
            d, rule, loc = own[ine]
            if d != NAVARRA["date"]:
                rec["holidays"] = sorted([{"date": d, "name": ""}, NAVARRA], key=lambda h: h["date"])
            else:
                notes.append("The locality's own day is also 3 December.")
            notes.append(f"Own day from the row '{loc}'" + (f", printed as '{rule}'." if rule else "."))
        else:
            notes.append("The table lists only villages/concejos of this municipality (see nucleos), not the "
                         "municipality as a whole.")
        if ine in nucleos:
            rec["nucleos"] = sorted(nucleos[ine], key=lambda n: n["name"])
        rec["note"] = " ".join(notes)
        out[ine] = rec
    write_part("bon-2026", SOURCE, out, region="navarra", unmatched=unmatched)


if __name__ == "__main__":
    main(*sys.argv[1:])
