# Vacation optimizer 2027: progress

Feature: /vacaciones-2027/ (hub) + /vacaciones-2027/<comunidad>/ (19 static pages, plan for 22 days precomputed,
23 in the FAQ and ranking), city or island via `?m=<slug>`, share card (canvas PNG 1080x1350 / 1200x630).

Objective ("días libres seguidos"): sum of the lengths of the breaks. A break = maximal run of days off (weekend,
holiday, vacation) holding >= 1 vacation day, at least 5 days long by default (min/max adjustable). Without a
minimum the optimum is a lone Friday every week (75 days with 22, a plan nobody takes); from 5 on it is puentes and
whole weeks (Madrid 56, Cataluña 53). Spec in the docstring of `vacopt.py`.

URL params: `d` days (default 22), `m` city/island slug, `x` blocked months 1-12 joined by `.`, `min`, `max`,
`t` taken days MMDD joined by `.`. Hub accepts `?c=<comunidad>` and redirects to the region page.

## Done
- [x] `vacopt.py` reference DP + `vac.js` port (optimize, breakName) — same plans
- [x] `test_vacopt.py`: 19 regions x 1..30, all cities, 120 random constrained cases, brute force on short years

## Next
- [ ] `vacaciones.py` pages (hub + 19), OG images, CSS additions, hooked into pages.write_pages (ES only)
- [ ] links: region vacation section, city pages (?m=), home, footer, nav
- [ ] Playwright: 390x844 + 1440, card renders, no console errors, no overflow; screenshots in scratchpad/cal/vac/
- [ ] seo/press-vacaciones.md, PROYECTOS-DINERO.md log line
