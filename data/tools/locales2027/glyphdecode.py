"""Decode PDF text drawn with subset Identity-H fonts that carry no ToUnicode map
(BOP León 144/2026 annex: Arial / Arial Bold subsets, text extracts as garbage).

Each embedded glyph outline is matched against the same glyph in the system's
reference font (C:/Windows/Fonts/arial.ttf, arialbd.ttf): identical contours ->
that glyph's Unicode code point. Character codes in the PDF are CIDs = GIDs
(Identity CIDToGIDMap), so the result is a code -> char table per font.
"""
import io
import os

from fontTools.ttLib import TTFont

REF = {
    "ArialMT": r"C:\Windows\Fonts\arial.ttf",
    "Arial-BoldMT": r"C:\Windows\Fonts\arialbd.ttf",
    "Calibri": r"C:\Windows\Fonts\calibri.ttf",
    "Calibri-Bold": r"C:\Windows\Fonts\calibrib.ttf",
}


def _sig(font, gname):
    gs = font.getGlyphSet()
    from fontTools.pens.recordingPen import DecomposingRecordingPen
    pen = DecomposingRecordingPen(gs)
    gs[gname].draw(pen)
    return tuple((op, tuple(tuple(round(c) for c in p) for p in pts)) for op, pts in pen.value)


def _ref_index(path):
    f = TTFont(path)
    cmap = f.getBestCmap()
    idx = {}
    for cp, gname in sorted(cmap.items()):
        s = _sig(f, gname)
        if s and s not in idx:
            idx[s] = chr(cp)
    return idx


_cache = {}


def font_table(doc, xref, basefont):
    """-> {code:int -> unicode char} for a Type0 font xref."""
    base = basefont.split("+", 1)[-1]
    ref = REF.get(base)
    if not ref:
        return None
    if ref not in _cache:
        _cache[ref] = _ref_index(ref)
    idx = _cache[ref]
    _, _, _, buf = doc.extract_font(xref)
    f = TTFont(io.BytesIO(buf))
    order = f.getGlyphOrder()
    out = {}
    for gid, gname in enumerate(order):
        s = _sig(f, gname)
        if not s:
            out[gid] = " "  # empty outline: space
            continue
        ch = idx.get(s)
        if not ch:
            ch = _nearest(s, idx)
        if ch:
            out[gid] = ch
    return out


def _flat(sig):
    return [p for _, pts in sig for p in pts]


def _nearest(sig, idx):
    """Fallback for glyphs whose outline differs slightly between font versions:
    same contour structure (ops) and smallest mean point distance."""
    ops = tuple(op for op, _ in sig)
    pts = _flat(sig)
    best, bd = None, None
    for rs, ch in idx.items():
        if tuple(op for op, _ in rs) != ops:
            continue
        rp = _flat(rs)
        if len(rp) != len(pts):
            continue
        dist = sum(abs(a[0] - b[0]) + abs(a[1] - b[1]) for a, b in zip(pts, rp)) / max(1, len(pts))
        if bd is None or dist < bd:
            best, bd = ch, dist
    return best if bd is not None and bd < 40 else None


def decoded_spans(doc, page):
    """Yield (bbox, font, text) with decoded text for every span of the page."""
    tables = {}
    for (xref, ext, typ, basefont, refname, enc) in page.get_fonts():
        if typ == "Type0" and enc == "Identity-H":
            t = font_table(doc, xref, basefont)
            if t:
                tables[basefont.split("+", 1)[-1]] = t
    raw = page.get_text("rawdict")
    for b in raw["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                t = tables.get(s["font"])
                if all(c["c"] == " " for c in s["chars"]):
                    t = None  # WinAnsi companion font: real spaces
                chars = []
                for c in s["chars"]:
                    ch = c["c"]
                    if t is not None:
                        o = ord(ch)
                        w = c["bbox"][2] - c["bbox"][0]
                        if o == 32 and w < 0.4 * s["size"]:
                            # a real space from the WinAnsi companion font merged into the
                            # span (same font name); Type0 glyph 32 is a wider letter
                            chars.append((c["bbox"], " "))
                            continue
                        ch = t.get(o, "\ufffd") if o < 0x100 or o in t else ch
                    chars.append((c["bbox"], ch))
                yield s["bbox"], s["font"], chars
