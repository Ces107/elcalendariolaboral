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

- [x] `vacaciones.py`: hub + 19 region pages (ES only, no hreflang), og/vacaciones-2027*.png, CSS block at the end of app.css
- [x] links: nav "Vacaciones" (ES), footer, home puentes section, "Optimizar todo el año →" in every region/city planner
- [x] header fits 861-1140 px (install and language as icons there)
- [x] test_vacopt.py also checks the generated pages (static total, 22 cells, never on weekend/holiday, og, links)
- [x] Playwright (scratchpad pw_vac.py): 390x844 + 1440, no console errors, no overflow, card PNGs render, shared URL reproduces the plan

## Next (ideas, not started)
- [ ] ca/gl/eu: no i18n strings for this page yet; stays Spanish-only
- [ ] OG quantize can turn regional yellow pinkish on small areas (cosmetic)
