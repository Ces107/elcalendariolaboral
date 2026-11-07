"""Debug helper: python -I dump.py <pdf> [first_page] [last_page] [words]
Prints each page's text (PyMuPDF reading order) or, with 'words', one line per
printed line built from word coordinates (x0 shown), to inspect column layouts."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: F401  (adds user site-packages, utf-8 stdout)
import fitz

doc = fitz.open(sys.argv[1])
a = int(sys.argv[2]) if len(sys.argv) > 2 else 1
b = int(sys.argv[3]) if len(sys.argv) > 3 else doc.page_count
mode = sys.argv[4] if len(sys.argv) > 4 else "text"
for pno in range(a - 1, min(b, doc.page_count)):
    page = doc[pno]
    print(f"===== page {pno + 1}")
    if mode == "words":
        lines = {}
        for w in page.get_text("words"):
            key = round((w[1] + w[3]) / 2 / 3)
            lines.setdefault(key, []).append(w)
        for k in sorted(lines):
            ws = sorted(lines[k], key=lambda w: w[0])
            print(" | ".join(f"{w[0]:.0f}:{w[4]}" for w in ws))
    else:
        print(page.get_text())
