# AdSense readiness, 10 Nov 2026 (before the "Contenido de poco valor" re-review)

Re-review to be requested by César around 13–16 Nov (not requested from here). Measured on the built site with
`python seo/audit_site.py` (8 s, exit 1 on a hard failure). Words = words of 2+ letters in `<main>`, without the
12-month grid and scripts. Previous pass: `seo/AUDIT-2026-11.md` (6 Nov).

## Site as built tonight

| Group | Pages | Indexable | AdSense loader | Manual units | Words (median) | HTML (median) |
|---|---|---|---|---|---|---|
| Municipality, official 2027 (lean) | 4,096 | 4,096 | 0 | 0 | 459 | 21 KB |
| Municipality, pending (lean) | 3,868 | 0 (noindex) | 0 | 0 | 372 | 19 KB |
| City pages (rich) | 168 | 168 | 155 | 310 | 647 | 64 KB |
| City pages ca/gl/eu | 504 | 0 (noindex) | 0 | 0 | 534–604 | 58 KB |
| Province pages | 50 | 50 | 0 | 0 | 735 | 31 KB |
| Comunidades (es) | 19 | 19 | 19 | 38 | 690–1,069 | 61–72 KB |
| Comunidades, home, utilities, privacy ca/gl/eu | 78 | 78 | 0 | 0 | 360–650 | 50–60 KB |
| Guides: /festivos/ + 5, /semana-santa/, /puentes/, /como-se-fijan-los-festivos/ | 9 | 9 | 9 | 9 | 492–1,465 | 18–38 KB |
| School: hub, 19 regions, 3 breaks | 23 | 23 | 19 | 0 | 166–5,310 | 20–36 KB |
| Trust: sobre, contacto, aviso legal, privacidad, cookies | 5 (+3 privacy ca/gl/eu) | all | 0 | 0 | 87–279 | 10–12 KB |
| Widget embeds | 195 | 0 | 0 | 0 | – | 4 KB |

Totals: 9,045 HTML pages, 4,476 indexable, 4,472 in the sitemap (the 4 privacy pages are written outside
`pages.write`), loader on 203 pages, 357 manual units (max 2 per page), 0 broken internal links.

## Findings tonight, and what changed

| # | Finding | Severity | Fix (commit) |
|---|---|---|---|
| 1 | César could not find a Valencian town: the comunidad page's locales block listed only Valencia + "pendientes: Alicante, Elche, Castellón" (7f4f96e had added a small search + province links, live). | high (users) | Big search under the answer with the comunidad's results first and two example towns as placeholder; right after the calendar, every province with "N publicados · M pendientes" and its 12 biggest towns (6 if the comunidad has more than 3 provinces, 24 if one), each with its 2027 dates or "pendiente", plus "Los N municipios →" (4d155c962). All 19 comunidades. |
| 2 | `/festivos-locales/` wrote an ad unit on a page without the AdSense loader: an empty 300 px "Publicidad" box. | high | Unit removed; the audit now fails on units without loader (ea8be787e, aba55b2da). |
| 3 | 8 indexable pages carried the loader with < 250 words (school hub + Galicia/Navarra/País Vasco, cambio de hora, días laborables, Navidad and Semana Santa breaks). | high | Navidad and Semana Santa got 4 facts computed from their table (longest/shortest, first day, back to school, working days a parent has to cover) and keep their ads; the school hub and días laborables got 2–3 computed facts. A build guard `pages.no_thin_ads` removes loader + units from any page under 250 words; tonight it applies to 6 pages (school hub, 3 school regions, cambio de hora, días laborables) (4d155c962). |
| 4 | Owner's full name on /sobre/, /aviso-legal/, /privacidad/ (brand is semi-anonymous). | medium | "Proyecto independiente con sede en Valencia (España)" + contact address; no personal name anywhere in the HTML (4d155c962). |
| 5 | Stale numbers: /sobre/ and /como-se-fijan-los-festivos/ said 168 municipalities with official dates, the festivos-locales hub said 168 "ciudades"; the catalogue has 4,264 of 8,132. | medium | Counts from the catalogue; the hub also lists all 50 province pages with "publicados de total" (4d155c962, ea8be787e). |
| 6 | No cookies page (Spain's LSSI art. 22 / AEPD guide; AdSense sets cookies on ad pages). | medium | /cookies/: the 5 localStorage keys the site uses, the Google cookies on ad pages (`__gads`, `__gpi`, `IDE`, consent `FCCDCF`/`FCNEC`), how to reset; linked from both footers and the privacy page (4d155c962). |
| 7 | 6 broken internal links: the language menu of /404.html and /buscar/ pointed to /ca/404.html, /gl/buscar/… | low | Those two pages are Spanish-only, the menu sends other languages to their home (4d155c962). |
| 8 | Province pages 366 px wide at 360 px (hero grid `1fr` could not shrink below the search box). | low | `minmax(0, 1fr)` for the hero grid and the stat tiles (a2cabf7a5). All 16 page types checked headless at 360 px: no horizontal scroll, CLS ≤ 0.001 (ads blocked). |
| 9 | `test_pdf.py` (852) and `test_utilidades.py` (55) failed. | low | They only failed without `CL_SITE`/`CL_BASE` (old ces107.github.io defaults): build.py now defaults to the live site; both pass (ea2be405b). |

Checked and fine: robots.txt, `ads.txt` (pub-9914165605609514, live), sitemap index with 5 segments (general 69,
comunidades 76, provincias 50, municipios 4,264, festivos 13); every sitemap URL exists, is indexable and
self-canonical; no ads on any noindex page; unique titles and descriptions on all indexable pages; nav, footer and
lean footer link sobre/contacto/aviso legal/privacidad/cookies; next-holiday countdown, Google Calendar (single
local days + comunidad subscription) and .ics on every municipality page; CTR titles with the dates
("Calendario laboral Arévalo 2027: festivos 9 feb y 7 jul"). Core Web Vitals: no new scripts, the directory is
server-rendered (no CLS), comunidad HTML +3 to +8 KB; the 7 Nov Lighthouse numbers should hold.

## For César before pressing "Solicitar revisión"

1. **Auto ads**: they are on with every format, on top of the 4 manual units; the preview put 12 in-page ads inside the
   calendar. For the review, a cluttered calendar reads as "more ads than content". Suggested: Auto ads → Edit →
   Excluded areas (calendar block, puentes/vacaciones tables) and turn off anchor + vignette, or Auto ads off until
   approval. Your call.
2. Search Console: re-submit `sitemap_index.xml` and request indexing of /comunitat-valenciana/ and /festivos-locales/.
3. Wait until the push of 10 Nov is live (it is: see the night journal) and that Search Console shows no crawl errors.

## Risks left

- **Scale.** 4,096 indexable municipality pages built from data (no ads on them). Each has its own bulletin dates,
  source, bridges, nearby towns and a "what changes" block (5-gram overlap 0.22 random pairs / 0.37 same region,
  `seo/build-PROGRESS.md`), but a reviewer may still read the set as templated. If the verdict comes back the same,
  the cheapest next step is noindex for municipalities under ~5,000 inhabitants (keeps ~700 pages) until approval.
- ca/gl/eu comunidad, home and utility pages stay indexable (no ads); they are translations without own text.
- The legal notice has no personal name or NIF by design (semi-anonymous brand); LSSI art. 10 asks for the holder's
  name. Low risk for AdSense, a legal choice for César.
- Pages left without ads by the guard (6) earn nothing until they reach 250 words; días laborables is a seasonal
  query worth enriching after approval.
