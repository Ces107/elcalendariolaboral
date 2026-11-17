# /analisis/: editorial analyses from our own dataset (17 Nov 2026)

Fix 5 (and the home row of fix 6) of `seo/ADSENSE-REAPPLY-2026-11-17.md`: five dated articles plus a hub, every figure
computed at build time from the data files. Module: `analisis.py` (new, Spanish only). Nothing else was edited.

## Pages

| Path | What it computes |
|---|---|
| `/analisis/` | Hub: the five articles with a one-line computed summary, dates, how they are made. No ad slot. |
| `/analisis/festivos-locales-mas-repetidos-2027/` | Dates ranked by municipalities, month split, province-wide days, top pair of dates, saints (names merged across languages), per province |
| `/analisis/festivos-locales-en-fin-de-semana-2027/` | Local days on Saturday / Sunday / on a comunidad holiday, per province, top dates, examples, 2026 comparison |
| `/analisis/dias-laborables-2027-por-provincia/` | Mon-Fri working days per municipality: distribution, per province (median/min/max with tie counts), capitals, comunidad base |
| `/analisis/cuando-publica-cada-provincia-sus-festivos-locales/` | Bulletin date per province 2027 vs 2026, pending list ordered by last year's date, coverage, 2026 corrections |
| `/analisis/mejores-puentes-2027-por-comunidad/` | Best puente per comunidad (ties marked), cost of doing all, Canarias islands, what local days add |

Each article: lead with the main finding, byline "Redacción de elcalendariolaboral.es", "Publicado 17 nov 2026 ·
Actualizado <max(published, data date)> · Datos de festivos locales a <locales-2027-all.json updated>", 2-4 tables,
"Qué significa y qué no sabemos" (what it means for you + limits), "Método y fuentes" box, related analyses.
JSON-LD: BreadcrumbList + WebPage + Article (author = the Redacción organisation, publisher = #org, isBasedOn = bulletin
URLs). One ad position per article through `B.ad("hub")`, built after `head_html` so it reads the page's own ADS_PAGE
(with `ADS_ON` False today it renders nothing, like every other page). Pages pass `pages.no_thin_ads`.

## Run

    python analisis.py                 # writes analisis/ in the repo (same setup as herramientas/build.py)
    python analisis.py --out DIR       # writes DIR/analisis/... (used for testing)

Do not leave the standalone output in the repo without the build integration: `test_data.py` fails on indexable pages
missing from the sitemap.

## Integration (lead)

    # build.py main(), Spanish build, after pages_written = pages.write_pages(data, fix):
    if LANG == "es":
        import analisis
        pages_written += analisis.write(sys.modules[__name__], data, fix)   # [(path, lastmod, ["es"])], segment "general"
    # home (pages.home_page, Spanish): analisis.home_block(B, DATA) -> <section id="analisis"> with 3 cards (.stats)
    #   and a link to the hub; works before write() (the home is rendered first). Empty string outside Spanish.
    # nav (build.header_html): analisis.nav_link() -> <a href="/analisis/">Análisis</a>

The home cards are computed from the same numbers as the articles (377 municipalities on 8 Sep · 776 lose a weekday
local day · 249–251 working days today).

## Numbers today (data of 7 Nov 2026; they change with every data refresh)

- Coverage: 4264 municipalities with official 2027 locals (of 8132). Counted: 4252 with at least one municipality-wide
  day (6 Asturian concejos with parish-by-parish days and 6 municipalities with locality-only days left out);
  4227 with exactly two (working days, puentes).
- Repeated: 8479 local days on 294 dates; 8 Sep 377, 15 May 287, 24 Jun 268; top 10 dates = 27.8 %; only 34.8 % of
  days have a name in the bulletin; Bizkaia/Gipuzkoa (31 Jul) and Álava (28 Apr) are territory-wide days.
- Weekend: 776 municipalities (18.3 %) lose at least one weekday local day: 804 Saturday, 19 Sunday, 35 on another
  holiday (30 of them Monday 16 Aug in comunidades that move the Asunción). 2026: 4.9 % of days vs 10.1 % in 2027;
  same 3830 municipalities: 337 → 680.
- Working days: 249-251, median 249 (3455 at 249, 689 at 250, 83 at 251). Comunidad base 251 or 252.
- Publication: 36 provinces with a 2027 bulletin, 16 pending (first Asturias 10 Jun 2026, last Ceuta 3 Nov 2026).
- Puentes: 3-5 per comunidad; the 4-8 Dec puente (1 day) is the best or tied best everywhere; Castilla-La Mancha ties
  with 27-31 May. Local days add a puente in 2513 of 4214 municipalities (comunidades with a bulletin).

## Checks run (scratch script, not committed)

Built twice into temp dirs: byte-identical output; articles 812-1208 words in `<main>` (707-784 without tables), hub
278; 0 HTML nesting errors (html.parser stack); no None/NaN/{}; every JSON-LD parses; titles ≤ 60 and descriptions ≤ 155
(the `test_data.py` limits); every internal link resolves to a file on disk; one ad position per article with
`ADS_ON` forced True, none on the hub. Counts cross-checked against a raw read of `locales-2027-all.json`
(Sat 804 / Sun 19 identical; 4252 vs 4250 municipalities because `muni.catalogue()` lays the 202 city records of
`locales-2027.json` over the bulletin file, as the city pages do).

## Data caveats found

- **Asturias parish lists are counted as municipality-wide on the live pages.** `muni.wide_and_partial` only matches
  "en la parroquia/el valle…", so Llanes (6 days), Piloña (6), Salas (4), San Martín del Rey Aurelio (3), Valdés and
  Tineo get all their parish days as locals: `/asturias/llanes/` says "18 festivos, 245 días laborables". The analyses
  exclude them; munipages.py needs a fix (or a `localities` split in the data).
- 19 local days fall on a Sunday (e.g. Pedrafita do Cebreiro 13 Jun "San Antón", Guijo de Coria 26 Dec, Alamedilla and
  Pórtugos twice each): worth a check against the bulletins.
- 35 local days fall on a holiday already given: 30 on Monday 16 Aug (San Roque in Ávila, León, Segovia, Zamora, Las
  Palmas…), plus Santa Olalla de Bureba 12 Oct, Fresno de Cantespino 6 Dec (name "San Nicolás de Bari Documento":
  parsing residue), Cangas 19 Mar, San Esteban de Nogales 23 Apr, Zaldibia 7 Oct.
- Big coverage gaps inside published bulletins: Burgos 182 of 371, León 164/211, Zamora 194/248, Ávila 195/248,
  Salamanca 315/362, Palencia 155/191, Valladolid 197/225.
- `locales-2026.json` has no La Rioja; the three Basque provinces' 2026 date is the Open Data Euskadi compilation
  (19 Nov 2025), not a bulletin date (shown as "datos abiertos", no difference computed).
- 25 municipalities have one municipality-wide day plus locality days (e.g. Ayala), 6 only locality days.
