# AdSense: manual ad units (ready, OFF)

Code: `build.py` → `ADS_ON`, `AD_CLIENT`, `AD_SLOTS`, `ad(pos)`. While `ADS_ON = False` (or a slot id is empty) no ad markup is written.
The AdSense loader script (`ADSENSE` in `head_html`) is already on every page for site verification; it shows nothing
unless Auto ads are on in the AdSense UI.

## Where ads may appear (since 2026-11-06, AdSense "low value content" fix)

Only Spanish pages with editorial content get the loader (so Auto ads too) and the units: home, comunidades, Spanish
city pages, /puentes/, /como-se-fijan-los-festivos/, /festivos/ and its 5 holiday pages, /semana-santa/ (one `hub`
unit each, mid-page, `festivos.py`), /calendario-escolar/ (+ regions, loader only),
/dias-laborables-2027/, /cambio-de-hora/. Never: ca/gl/eu (`build.ADS_LANGS`; gl and eu are not AdSense languages),
noindex pages, the vacation planner, PDF hub, festivos-locales hub, widget, /semana/, /dias-habiles/, privacy, legal,
404 (`head_html(..., ads=False)`). See `seo/AUDIT-2026-11.md`.

Since 2026-11-07 (`seo/build-PROGRESS.md`), also without ads until AdSense approves the site: the 50 province pages and
the ~8,000 municipality pages of `munipages.py`, the 13 city pages that got their 2027 locals from
`locales-2027-all.json` (`c["new"]` in `muni.overlay_locales`), and `/buscar/`. To turn them on after approval: in
`munipages.py` change `ads=False` in both `head_html` calls (they have no `ad()` slots yet: add one `hub` unit after the
"Qué cambian" notes, never next to the hero actions), and in `pages.city_page` drop `ads=not c.get("new")`.

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

## House ads (since 2026-11-12)

Every `ad(pos)` position also carries our own promos (`build.house_ads`, texts in `build.HOUSE_TXT`, images in `promo/`):
Agenda semanal 2027 on Amazon (school pages: Cuaderno del profesor; English tools: the 2027 Weekly Planner on amazon.com),
Calma Planners on Etsy, Teselo (web game) and the /shopping/ page (not on English pages). All cards are in the HTML; a
small inline script shows one at random per view (`data-w` weight 3 for the relevant product, no card twice on a page);
without JS the build's pick shows.

- With AdSense (`ad-g`): the card sits on the `<ins>` in one grid cell, label "Nuestros productos". `ins[data-ad-status=filled]`
  hides the card and shows the "Publicidad" label (`:has()`, or the script's `.on` class); `unfilled` collapses the unit.
  The card fills the reserved 280 px, so nothing moves.
- Without AdSense (gl/eu, noindex, tools, `ads=False`, thin pages: `pages.no_thin_ads` keeps the promos via
  `build.house_only`): a compact card, label "Nuestros productos" (ca/gl/eu/en translated).
- Promo text does not count as content (`pages.main_words` and `seo/audit_site.py` drop the `<aside class="ad">`).
- Teselo on Google Play: set `TESELO_PLAY_PUBLIC = True` once the listing is public (adds a "Google Play" button).

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
