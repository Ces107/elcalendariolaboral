# Utility pages (Nov-Jan traffic): progress

Module: `utilidades.py` (called from `pages.write_pages` for every language; `ONLY_*` per page = languages with strings
in `S`). Browser code: `util.js` (pure functions exported for node + DOM code per page). Test: `test_utilidades.py`.
Data: `data/2026.json` (BOE-A-2025-21667, for ranges in 2026), `data/2027.json`, `data/locales-2027.json` (city locals,
2027 only). Small CSS block at the end of `app.css` (date inputs, table scroll, card label).

Build: `MSYS_NO_PATHCONV=1 CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py --no-pdf` (~35 s; --no-pdf
leaves pdf/ untouched). Checks (same env vars): test_data, seo/check_data, data/check_i18n, test_vacopt, test_pdf,
test_utilidades.

## Done (2026-10-27)
- [x] data/2026.json from the BOE table (12 per comunidad, Canarias 11 + island; island and Arán notes)
- [x] 1 /semana/ — ISO week (JS, build-date fallback), week tables 2026 (53) and 2027 (52) — 45fe524
- [x] 2 /dias-habiles/ — between dates / N working days (Ley 39/2015 count), comunidad + island/Arán + city (2027 locals),
      Saturday toggle, holiday list, caveat; Python + JS functions checked against each other — 7a9395d
- [x] 3 /dias-laborables-2027/ — comunidad x month, islands and Arán as sub-rows, total, hours at 8 h; link from each
      comunidad page ("Días laborables 2027" in the locales line) — b95c208
- [x] 4 /cambio-de-hora/ — next/last change (JS), table 2026-2028, RD 236/2002 — ef12068
- [x] ca/gl/eu for the four pages + home links line — 603eb0b
- [x] footer "Utilidades" block on every page; ad slot `hub` (off) on each page; seo/ads.md updated

## Next (ideas, not started)
- [ ] own OG images for the four pages (they use og/espana.png)
- [ ] 2028 holidays when the BOE publishes them (Oct 2027): extend /dias-habiles/ range (LO/HI in utilidades.py)
- [ ] when the 2027-2031 DST calendar order is published in the BOE, cite it on /cambio-de-hora/
