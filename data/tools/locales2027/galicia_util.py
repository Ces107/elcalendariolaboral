"""Small helpers shared by the four Galician BOP parsers (notes on weekend / overlapping days)."""
import datetime as dt

# Decreto 68/2026 (DOG 122, 2-VII-2026) as reprinted in BOPPO 192: Galicia 2027 general holidays
GALICIA_GENERAL_2027 = {
    "2027-01-01", "2027-01-06", "2027-03-19", "2027-03-25", "2027-03-26", "2027-05-01",
    "2027-05-17", "2027-10-12", "2027-11-01", "2027-12-06", "2027-12-08", "2027-12-25",
}
WD = {5: "Saturday", 6: "Sunday"}


def auto_note(holidays):
    """Factual notes: local day on a weekend, or on a Galician general holiday. Dates unchanged."""
    bits = []
    for h in holidays:
        d = dt.date.fromisoformat(h["date"])
        if d.weekday() in WD:
            bits.append(f"{d.day}/{d.month} falls on a {WD[d.weekday()]}")
        if h["date"] in GALICIA_GENERAL_2027:
            bits.append(f"{d.day}/{d.month} is also a Galician general holiday in 2027")
    if not bits:
        return ""
    return "; ".join(bits) + "; recorded as published in the bulletin."


def add_notes(rows):
    for r in rows:
        n = auto_note(r["holidays"])
        if n:
            r["note"] = (r.get("note", "") + " " + n).strip()
    return rows
