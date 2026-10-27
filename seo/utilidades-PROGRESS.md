# Utility pages (Nov-Jan traffic): progress

Module: `utilidades.py` (called from `pages.write_pages` for every language; `ONLY` per page lists the languages it
exists in). Browser code: `util.js` (pure functions exported for node + DOM code). Test: `test_utilidades.py`.
Data: `data/2026.json` (BOE-A-2025-21667, for ranges that start in 2026), `data/2027.json`, `data/locales-2027.json`.

Build: `MSYS_NO_PATHCONV=1 CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py --no-pdf` (~35 s; --no-pdf
leaves pdf/ untouched). Checks: test_data, seo/check_data, data/check_i18n, test_vacopt, test_pdf, test_utilidades.

## Done
- [x] data/2026.json from the BOE table (12 per comunidad, Canarias 11 + island; island and Arán notes)

## Next
- [ ] 1 /semana/
- [ ] 2 /dias-habiles/
- [ ] 3 /dias-laborables-2027/
- [ ] 4 /cambio-de-hora/
- [ ] ca/gl/eu for the four pages
- [ ] links: footer, home; IndexNow; PROYECTOS-DINERO.md line
