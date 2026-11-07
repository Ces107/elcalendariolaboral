# Visible SEO pass + municipality pages: progress

Brief (7 Nov 2026): search, next-holiday card, calendar/print/share actions, titles and OG images, structured data,
404, segmented sitemaps, design pass (Phase 1); province and municipality pages from `data/municipios.json`,
`data/provincias.json`, `data/locales-2026.json`, `data/locales-2027-all.json` (Phase 2).
Rules kept: `seo/ads.md` (new page types get no ads), `seo/AUDIT-2026-11.md` (no templated thin text), no Co-Authored-By.

## Status

| Step | State |
|---|---|
| Phase 1 | done, pushed (3469bad0) + icons as CSS masks, compact JSON-LD (Phase 2 commit) |
| Phase 2 | built: 50 province pages, 7,964 lean municipality pages + 13 city pages promoted; see "Phase 2" below |

## Log

- 2026-11-07: read the audit/research/ads docs, baseline screenshots (390 / 1366: no horizontal scroll, CLS 0-0.003),
  city page 60 KB (year grid 24 KB, cal-data 7 KB).
- 2026-11-07: **pushed 3469bad0** (Phase 1 batch 1): header + home search (`buscar.json`, `buscar.py`), hero panel
  (next-holiday tile server-rendered + JS countdown, stats tiles), Google Calendar/.ics/print/share in the hero,
  answer-first titles/descriptions, OG images with date chips, WebPage on every indexable page, segmented
  sitemaps (`sitemap_index.xml`, `sitemap.xml` = copy), robots.txt, 404 with search, `/buscar/` fallback.
  Verified live with curl. Tests read `sitemap-*.xml`.
- 2026-11-07: data arrived: `locales-2027-all.json` (4,264 official), `locales-2026.json` (5,249 refs). Phase 2
  generator = `muni.py` (catalogue + province + municipality pages), switch `CL_MUNI`/`MUNI_ON`.
- 2026-11-07: Phase 2 built. `muni.py` = catalogue (paths, status, 2027 official from locales-2027-all, 2026 reference,
  Aran zone, islands from municipios.json, slug collisions -> -<province>), `overlay_locales()` (13 "unpublished" cities
  of locales-2027.json now in a bulletin get their rich page, no ads; council -> bulletin source when dates identical).
  `munipages.py` = province + municipality pages (lean header/footer, compact grid/list/puentes, no ads).
  Conflicts locales-2027 vs locales-2027-all: 0 (Siero/Mieres parish days are not conflicts: wide days compared).

## Phase 2: numbers (build of 2026-11-07)

| | Pages | Indexable / in sitemap | Words in main (median, without grid) | 5-gram Jaccard random pairs (median / p90) | Same region | HTML median | Total |
|---|---|---|---|---|---|---|---|
| Municipality, official 2027 (lean) | 4,096 | all | 558 | 0.251 / 0.351 | 0.359 | 19.4 KB (4.4 KB gzip) | 81 MB |
| City pages (rich, 155 + 13) | 168 | all | 803 | 0.293 / 0.505 | 0.547 | 62.9 KB | 11 MB |
| Municipality, pending (lean) | 3,868 | noindex, not in sitemap | 439 | 0.374 / 0.614 | 0.662 | 17.3 KB | 69 MB |
| Province pages | 50 | all | | | | 33 KB median | |

Sitemap: 4,471 URLs (general 68, comunidades 76, provincias 50, municipios 4,264, festivos 13). Search index
`buscar.json` 437 KB raw / 101 KB gzip (8,132 municipalities + 50 provinces + 19 comunidades), fetched on first focus.
Size target was <=15 KB per municipality page: reached 19 KB (head 2.8 KB, hero 4 KB, grid 3.5 KB, list 2.5 KB);
further cuts would remove content. GitHub Pages limit 1 GB: site ~310 MB with PDFs.

## Next / left

- Rebuild when the pending bulletins land (DOGV ~mid Nov, BOA late Nov, BON, BOCM mid Dec, DOGC Dec, Cantabria,
  Albacete/Cuenca/Guadalajara): pages flip to index automatically (`python build.py`).
- After AdSense approval: ads on the new pages (`seo/ads.md`).
- La Rioja has no 2026 reference (Cloudflare); its 165/174 have 2027 official anyway.
