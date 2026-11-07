# Lighthouse 13, 7 Nov 2026: before / after

Live URLs (elcalendariolaboral.es), Lighthouse 13.6 headless (Playwright Chromium 1217), one run at a time on a shared,
busy PC: Performance and TBT vary ±10 points between runs; treat them as indicative. "before" = live before this pass,
"after" = live with commit 8d8e52113 (minified deferred JS, versioned fonts with 3 preloads, CSP, ad preconnect).
The last change (font-display: optional, commit after 8d8e52113) aims at the festivos desktop CLS and was not re-measured.
Reports: `before-*`, `after-*` (intermediate, with content-visibility, reverted) and `final-*` (.report.json/.html).

| Page | Device | Performance | Accessibility | Best practices | SEO | LCP | CLS | TBT |
|---|---|---|---|---|---|---|---|---|
| home | mobile | 69 → **70** | 100 → **100** | 100 → **100** | 100 → **100** | 1.2 s → 1.1 s | 0 → 0 | 2,830 ms → 2,770 ms |
| home | desktop | 79 → **83** | 100 → **100** | 100 → **100** | 100 → **100** | 0.6 s → 0.6 s | 0.002 → 0 | 460 ms → 370 ms |
| comunidad | mobile | 69 → **71** | 100 → **100** | 100 → **100** | 100 → **100** | 2.4 s → 1.0 s | 0 → 0 | 1,960 ms → 2,430 ms |
| comunidad | desktop | 94 → **99** | 100 → **100** | 100 → **100** | 100 → **100** | 0.7 s → 0.8 s | 0.017 → 0.003 | 170 ms → 80 ms |
| ciudad | mobile | 64 → **71** | 100 → **100** | 100 → **100** | 100 → **100** | 3.4 s → 0.9 s | 0 → 0 | 1,660 ms → 2,260 ms |
| ciudad | desktop | 97 → **90** | 100 → **100** | 100 → **100** | 100 → **100** | 0.6 s → 1.0 s | 0.014 → 0 | 130 ms → 210 ms |
| municipio-oficial | mobile | 91 → **89** | 100 → **100** | 100 → **100** | 100 → **100** | 0.9 s → 1.1 s | 0 → 0 | 360 ms → 420 ms |
| municipio-oficial | desktop | 95 → **95** | 100 → **100** | 100 → **100** | 100 → **100** | 0.7 s → 0.5 s | 0.011 → 0 | 150 ms → 160 ms |
| municipio-pendiente | mobile | 82 → **77** | 100 → **100** | 100 → **100** | 63 → **63** | 1.0 s → 1.0 s | 0 → 0 | 720 ms → 1,100 ms |
| municipio-pendiente | desktop | 100 → **100** | 100 → **100** | 100 → **100** | 63 → **63** | 0.5 s → 0.4 s | 0.001 → 0.002 | 0 ms → 0 ms |
| provincia | mobile | 86 → **82** | 100 → **100** | 100 → **100** | 100 → **100** | 1.1 s → 0.9 s | 0 → 0 | 560 ms → 730 ms |
| provincia | desktop | 99 → **100** | 100 → **100** | 100 → **100** | 100 → **100** | 0.5 s → 0.3 s | 0.004 → 0 | 70 ms → 0 ms |
| festivos | mobile | 73 → **75** | 100 → **100** | 100 → **100** | 100 → **100** | 0.9 s → 0.9 s | 0 → 0 | 1,780 ms → 1,340 ms |
| festivos | desktop | 96 → **87** | 100 → **100** | 100 → **100** | 100 → **100** | 0.4 s → 0.4 s | 0.009 → 0.079 | 160 ms → 280 ms |
| semana-santa | mobile | 72 → **72** | 100 → **100** | 100 → **100** | 100 → **100** | 0.9 s → 0.9 s | 0 → 0 | 2,080 ms → 1,930 ms |
| semana-santa | desktop | 90 → **87** | 100 → **100** | 100 → **100** | 100 → **100** | 1.4 s → 0.3 s | 0.038 → 0.003 | 200 ms → 310 ms |

## What limits the scores

- Best practices: 100 in every lab run. The 81 on PageSpeed comes when an ad is actually served there (deprecated API
  and third-party cookie warnings from AdSense / ad creatives); nothing of ours. HSTS / COOP / X-Frame-Options cannot be
  sent by GitHub Pages (`seo/AUDIT-2026-11.md`); the CSP is a `<meta>` and shows no violations on 8 page types, with
  AdSense and the consent message loading.
- Mobile performance on pages with ads: 70-75. The AdSense loader, show_ads_impl and the Funding Choices consent script
  take ~2 s of main thread under the 4x CPU throttle (TBT). Pages without ads (municipality, province) score 77-93 mobile
  and 95-100 desktop. Mobile 100 with AdSense on the page is not reachable without delaying or removing the ads.
- SEO 63 on pending municipality pages is by design: they are noindex until their bulletin is out.
- Accessibility 100 everywhere (the 96 seen in the intermediate run came from content-visibility, now reverted).
