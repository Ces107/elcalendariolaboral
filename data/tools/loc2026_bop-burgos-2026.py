"""Burgos province 2026 local holidays: Resolución de 22-8-2025 de la Oficina Territorial de Trabajo de Burgos sobre
calendario de fiestas locales retribuidas y no recuperables para el año 2026 (BOP Burgos núm. 165, 3-9-2025, CVE
BOPBUR-2025-04120), copy hosted by the Junta de Castilla y León (Trabajo y Prevención, 'Calendario laboral 2026').

Download (outside the repo):
    https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/911/2/02%20BOP%20FIESTAS%20LOCALES%20BURGOS%2026,0.pdf
Run (Windows only: the annex is a scanned table, read with the Windows OCR engine through PowerShell):
    python -E -P data/tools/loc2026_bop-burgos-2026.py <downloaded.pdf> [work_dir]

The annex (pages 4-15) is 12 scanned images of a table "ENTIDAD LOCAL | FECHA | FESTIVIDAD", one row per date
(dd/mm/2026). The images are extracted with PyMuPDF into work_dir (default: a temp dir), OCR'd with
Windows.Media.Ocr (es-ES), and the words regrouped into printed rows by their coordinates. OCR misreads found by
comparing every row with the scans by eye are fixed in FIX. "LOCALIDAD (MUNICIPIO)" rows are localities (entidades
locales menores) of that municipality.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
from muni_match import Matcher, write_part  # noqa: E402

PROV = "09"
SOURCE = {
    "title": "Resolución de 22 de agosto de 2025, de la Oficina Territorial de Trabajo de Burgos, sobre calendario de "
             "fiestas locales retribuidas y no recuperables para el año 2026 en la provincia de Burgos (BOP Burgos núm. "
             "165, de 3-9-2025, CVE BOPBUR-2025-04120)",
    "url": "https://trabajoyprevencion.jcyl.es/web/jcyl/binarios/911/2/02%20BOP%20FIESTAS%20LOCALES%20BURGOS%2026,0.pdf",
    "published": "2025-09-03",
}
# OCR text (name | date | festividad as read) -> corrected text, each checked against the scan by eye
FIX = {"BARRIOS DE BUREBA LOS | 03/08/2026 | FIESTA LOCAL": "BARRIOS DE BUREBA (LOS) | 03/08/2026 | FIESTA LOCAL",
       " | 02/07/2026 | FIESTA LOCAL": "ZAZUAR | 02/07/2026 | FIESTA LOCAL",
       "VILLAESCUSA LA SOMBRíA | 15/05/2026 | SAN ISISDRO": "VILLAESCUSA LA SOMBRÍA | 15/05/2026 | SAN ISIDRO"}
# "CIRUELOS DE CERVERA (AYTO VALDEANDE)": Ciruelos de Cervera is itself a municipality (09105); the bracket names the
# council it is grouped with, so it is taken as Ciruelos de Cervera (as the Junta's open-data calendar does).
ALIAS = {"CIRUELOS DE CERVERA (AYTO VALDEANDE)": "09105"}
# Rows read correctly but printed with an obvious error, kept with a note: name -> note
PRINTED = {"MONASTERIO DE LA SIERRA": "The annex prints the first day as 29/06/2025 (sic) in the 2026 list; taken as "
                                      "29 June 2026 (the Junta's open-data calendar also gives 29/06/2026)."}

OCR_PS1 = r"""
param([string]$ImagePath, [string]$OutPath)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$t) { $m = $asTask.MakeGenericMethod($t); $task = $m.Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result }
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('es'))
$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($ImagePath)) ([Windows.Storage.StorageFile])
$stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
$decoder = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
$bmp = Await ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
$res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
$out = foreach ($line in $res.Lines) { foreach ($w in $line.Words) { "{0}`t{1}`t{2}" -f [int]$w.BoundingRect.X, [int]$w.BoundingRect.Y, $w.Text } }
[System.IO.File]::WriteAllLines($OutPath, [string[]]$out, (New-Object System.Text.UTF8Encoding($false)))
$stream.Dispose()
"""


def ocr_pages(pdf, work):
    work.mkdir(parents=True, exist_ok=True)
    ps1 = work / "ocr.ps1"
    ps1.write_text(OCR_PS1, "utf-8")
    doc = pymupdf.open(pdf)
    out = []
    for pno in range(3, 15):  # printed pages 4-15
        imgs = [i for i in doc[pno].get_images(full=True) if i[2] > 500]
        assert len(imgs) == 1, (pno, imgs)
        pix = pymupdf.Pixmap(doc, imgs[0][0])
        if pix.n > 3:
            pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
        png, txt = work / f"p{pno + 1:02d}.png", work / f"p{pno + 1:02d}.tsv"
        pix.save(str(png))
        if not txt.exists():
            subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps1), str(png),
                            str(txt)], check=True)
        words = []
        for ln in txt.read_text("utf-8-sig").splitlines():
            x, y, t = ln.split("\t", 2)
            words.append((int(y), int(x), t))
        out.append((pno + 1, sorted(words)))
    return out


def clean(name):
    """OCR name -> as printed: capitals (OCR mixes í/Í), spaces inside brackets, a bracket the OCR dropped"""
    name = re.sub(r"\s+", " ", name.upper()).strip()
    name = re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", name))
    if name.count("(") > name.count(")"):
        name += ")"
    if name.count(")") > name.count("("):  # "PUEBLA DE ARGANZÓN LA)"
        name = re.sub(r"\s(\w+)\)$", r" (\1)", name)
    return name


SMALL = {"de", "del", "la", "las", "los", "el", "y", "e", "en", "a"}


def recase(s):
    """'CASTRILLO DE MURCIA' -> 'Castrillo de Murcia'"""
    words = s.strip().lower().split()
    return " ".join(w if (i and w in SMALL) else w[:1].upper() + w[1:] for i, w in enumerate(words))


def rows(pdf, work):
    """[(page, name, date, festividad)] with two-line names joined"""
    out = []
    for page, words in ocr_pages(pdf, work):
        lines = []
        for y, x, t in words:
            if lines and abs(lines[-1][0] - y) < 9:
                lines[-1][1].append((x, t))
            else:
                lines.append([y, [(x, t)]])
        pending = None
        for y, cells in lines:
            cells.sort()
            name = " ".join(t for x, t in cells if x < 340)
            date = " ".join(t for x, t in cells if 340 <= x < 452)
            fest = " ".join(t for x, t in cells if x >= 452)
            if name.startswith("ENTIDAD LOCAL"):
                continue
            if not name and not date and fest and out:  # second line of a two-line festividad
                p, n, d, f = out[-1]
                out[-1] = (p, n, d, f + " " + fest.upper())
                continue
            if not date and not fest:  # first line of a two-line name
                pending = (pending + " " if pending else "") + name
                continue
            if pending:
                name, pending = pending + " " + name, None
            key = f"{name} | {date} | {fest}"
            if key in FIX:
                name, date, fest = (s.strip() for s in FIX[key].split("|"))
            out.append((page, clean(name), date.strip(), re.sub(r"\s+", " ", fest.upper()).strip()))
        assert not pending, (page, pending)
    return out


def iso(date, row):
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", date)
    assert m, row
    assert m.group(3) == "2026" or row[1] in PRINTED, row
    return f"2026-{m.group(2)}-{m.group(1)}"


def main(pdf, work=None):
    work = Path(work) if work else Path(tempfile.mkdtemp(prefix="bopbur2026_"))
    mt = Matcher()
    ents = {}
    for row in rows(pdf, work):
        page, name, date, fest = row
        ents.setdefault(name, []).append((iso(date, row), fest))
    own, nuc, unmatched = {}, {}, []
    for name, pairs in ents.items():
        ine = ALIAS.get(name) or mt.match(name, province=PROV)
        if ine:
            own[ine] = pairs
            continue
        m = re.fullmatch(r"(.+?)\s*\((.+)\)", name)
        parent = m and (ALIAS.get(m.group(2)) or mt.match(m.group(2), province=PROV))
        if parent:
            nuc.setdefault(parent, []).append((m.group(1).strip(), pairs))
        else:
            unmatched.append(f"{name}: {pairs}")
    by_ine = {}
    for ine in sorted(set(own) | set(nuc)):
        rec = {"holidays": [{"date": d, "name": n} for d, n in sorted(dict(own.get(ine, [])).items())]}
        notes = []
        if ine in nuc:
            rec["nucleos"] = [{"name": recase(n), "holidays": [{"date": d, "name": f} for d, f in sorted(dict(p).items())]}
                              for n, p in nuc[ine]]
            notes.append("The list also gives days for localities of the municipality; see nucleos." if ine in own else
                         "The list gives days only for localities of the municipality, not for the whole "
                         "municipality; see nucleos.")
        if ine in own and len(rec["holidays"]) != 2:
            notes.append(f"The list gives {len(rec['holidays'])} day(s) for the municipality.")
        for name, note in PRINTED.items():
            if (ALIAS.get(name) or mt.match(name, province=PROV)) == ine:
                notes.append(note)
        if notes:
            rec["note"] = " ".join(notes)
        by_ine[ine] = rec
    missing = [f"{m['ine']} {m['name']}: not listed" for m in mt.munis if m["province_code"] == PROV and m["ine"] not in by_ine]
    print("rows:", sum(len(p) for p in ents.values()), "entities:", len(ents), "not listed:", len(missing))
    write_part("bop-burgos-2026", SOURCE, by_ine, region="castilla-y-leon", unmatched=unmatched + missing)


if __name__ == "__main__":
    main(*sys.argv[1:])
