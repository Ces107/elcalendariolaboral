# AdSense: manual ad units (ready, OFF)

Code: `build.py` → `ADS_ON`, `AD_CLIENT`, `AD_SLOTS`, `ad(pos)`. While `ADS_ON = False` (or a slot id is empty) no ad markup is written.
The AdSense loader script (`ADSENSE` in `head_html`) is already on every page for site verification; it shows nothing
unless Auto ads are on in the AdSense UI.

## Positions

| `AD_SLOTS` key | Where | Pages |
|---|---|---|
| `cal` | between the calendar section and the next section (puentes; on the home, the comunidad chips) | 19 comunidades, ~155 cities, home (es/ca/gl/eu) |
| `list` | after the holiday list ("Festivos 2027 en …"), before festivos locales/FAQ | comunidades, cities (es/ca/gl/eu) |
| `vac` | below the result card (above the calendar) | /vacaciones-2027/<comunidad>/ |
| `hub` | inside the hub body, before the FAQ (PDF hub: after the 3rd comunidad; /semana/: between the 2026 and 2027 tables) | /festivos-locales/, /calendario-laboral-2027-pdf/, /calendario-escolar/, /vacaciones-2027/; utility pages /semana/, /dias-habiles/, /dias-laborables-2027/, /cambio-de-hora/ (es/ca/gl/eu) |

Never: inside the month grid (`.year`), the share card (`.vres`), the widget embeds (`/widget/embed/…`, no loader, no slots),
print (`@media print { .ad { display: none } }`), the PDFs. Each unit is `<aside class="ad">` with a small "Publicidad"
label and a reserved `min-height: 300px` (no layout shift).

## When AdSense approves the site

1. AdSense → Ads → By ad unit → Display ads: create 4 units, responsive, named `ecl-cal`, `ecl-list`, `ecl-vac`, `ecl-hub`.
2. From each unit's code copy only the `data-ad-slot="…"` number.
3. `build.py`: paste them into `AD_SLOTS` (`"cal": "1234567890"`, …) and set `ADS_ON = True`.
4. Rebuild: `MSYS_NO_PATHCONV=1 CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py --no-img`
5. `python test_pdf.py` (it checks the unit markup; the "no ad while off" check skips itself when `ADS_ON` is True).
6. Commit and push to `main`; check a comunidad page on the phone: label + unit, calendar untouched.

## Auto ads: keep them out of the calendar

AdSense has no code attribute that keeps Auto ads out of a block, so do it in the UI:

- Ads → By site → elcalendariolaboral.es → **Auto ads: off** (recommended: the 4 manual units cover the pages).
- If Auto ads are wanted later: same screen → Edit → **Excluded areas**: on a comunidad page, a city page and
  /vacaciones-2027/madrid/ select the calendar block, the puentes/vacaciones tables and the result card; and
  **Page exclusions** for `elcalendariolaboral.es/widget/embed/*`. Turn off "Anchor ads" and "Vignette ads" (they cover the
  calendar on phones).
- Ads → Privacy & messaging: the European regulations message (TCF consent) must be published before serving in the EU.
