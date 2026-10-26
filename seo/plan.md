# SEO build plan: elcalendariolaboral.es

Written 2026-10-26 from the research in `seo/keywords.md`. It is a spec for `build.py`. The data it needs lives in `data/` and is checked by `python seo/check_data.py`.

## 0. Principles

1. **Answer first, tool second, text last.** Every page opens with one sentence that answers the query and carries the number or date (for example "Madrid tiene 14 festivos en 2027: 12 del BOE y 2 locales."). The tool comes next. Any explanatory copy goes **below** the tool as short FAQ answers of 1–3 sentences each. No intro paragraphs.
2. **A source on every page.** One line, "Fuente: BOE-A-2026-21254 · comprobado 26-10-2026", that links to the official document. For school and local data, cite that entry's own `source.url`. Competitors contradict each other, so being visibly exact is how we win.
3. **Never show data we do not have.** If a field is `null` in the data files, show "Pendiente de publicación oficial" plus a link to the body that publishes it. Do not fill it with last year's dates.
4. **Year-agnostic URLs, year in the title.** `/madrid/` keeps its authority from year to year. The year lives in `<title>`, H1 and copy. When the next BOE comes out (October 2027), the evergreen URL switches to 2028 and the old year moves to `/2027/<path>/`.
5. **Everything is static HTML.** All content an engine needs is in the HTML at build time, as it is today. JS only adds interaction.

## 1. Priorities (impact ÷ effort)

| # | Action | Impact | Effort | When |
|---|---|---|---|---|
| 1 | Make the site live (DNS + GitHub Pages + HTTPS), then **verify Search Console and Bing**, submit the sitemap | blocks everything | S (owner) | now |
| 2 | Fix titles/meta so they hold both "calendario laboral 2027" and "festivos 2027 {region}" (patterns in §3) | high | S | now |
| 3 | **City pages** `/<comunidad>/<ciudad>/` from `data/locales-2027.json`, plus `/festivos-locales/` hub | very high: town-level demand, weak supply | M | before mid-November |
| 4 | **Navidad school break table** `/vacaciones-escolares/navidad/` (19 comunidades) | high, time-boxed (searched now until 23 Dec) | S | this week |
| 5 | **School calendar** `/calendario-escolar/` + `/calendario-escolar/<comunidad>/` from `data/escolar-2026-27.json` | very high (second head term) | M | November |
| 6 | `/puentes/`, `/festivos/`, `/dias-laborables/` hub pages (pure reuse of `2027.json`) | high | S each | November |
| 7 | Print CSS + per-page **PDF** (`calendario-laboral-2027-<slug>.pdf`) + CSV ("excel") | high (`pdf`, `excel`, `para imprimir` modifiers everywhere) | M | November |
| 8 | Structured data: BreadcrumbList, WebSite/Organization, Dataset, FAQPage. Remove the Event+PostalAddress markup (§5) | medium | S | with #2 |
| 9 | `/semana-santa/` + one page per holiday question (`/festivos/jueves-santo/` …) | medium (PAA bait, February–March peak) | S | December |
| 10 | Self-host the font, add a 404 page, sitemap `lastmod` taken from the data's change date | medium (Core Web Vitals and crawl) | S | any time |
| 11 | `/calendario-escolar/2027-2028/` placeholder page that collects links, filled in as orders appear | medium (peak from April 2027) | S | January |
| 12 | `/2026/` archive (needs `data/2026.json` from the 2026 BOE) | medium now, nil after December | M | optional |
| 13 | Backlink outreach (§10) | high long-term | ongoing | from launch |
| 14 | `/ca/` `/gl/` `/eu/` versions with hreflang, per-language sitemaps and a switcher (§13). Catalan first. | high for ca, medium for gl/eu | M | with the redesign |

## 2. URL structure (canonical)

Everything is lowercase ASCII with dashes and a trailing slash. One URL per intent. `<link rel="canonical">` is the absolute self URL. No query-string variants are indexable: the island/zone selectors (`?isla=`) stay client-side and the canonical points to the clean URL.

```
/                                         calendario laboral 2027 España (exists)
/<comunidad>/                             calendario laboral 2027 <comunidad> (exists, 19)
/<comunidad>/<ciudad>/                    calendario laboral 2027 <ciudad> = comunidad + 2 locales   [NEW]
/festivos/                                festivos 2027 España: list + "where" column                 [NEW]
/festivos/<festivo>/                      e.g. jueves-santo, lunes-de-pascua, 19-de-marzo, 12-de-octubre,
                                          15-de-agosto, 24-de-junio, 6-de-enero, 1-de-noviembre        [NEW]
/festivos-locales/                        hub: every city with its 2 locales, grouped by comunidad    [NEW]
/puentes/                                 puentes 2027 España + per comunidad (anchors #madrid …)     [NEW]
/dias-laborables/                         días laborables 2027: month × comunidad table              [NEW]
/semana-santa/                            Semana Santa 2027: dates, labour holidays, school breaks   [NEW]
/calendario-escolar/                      calendario escolar 2026-2027 España (hub, 19 comunidades)  [NEW]
/calendario-escolar/<comunidad>/          calendario escolar 2026-2027 <comunidad>                    [NEW]
/calendario-escolar/2027-2028/            next course (placeholder until published)                   [NEW]
/calendario-escolar/2027-2028/<comunidad>/  only once officially published
/vacaciones-escolares/navidad/            Navidad 2026-27 school break, 19 comunidades                 [NEW]
/vacaciones-escolares/semana-santa/       Semana Santa 2027 school break, 19 comunidades               [NEW]
/vacaciones-escolares/semana-blanca/      only comunidades that have one                               [NEW]
/2026/ , /2026/<comunidad>/               optional archive of the previous year                        [OPTIONAL]
/privacidad/                              exists (add noindex? no: it is harmless, keep it out of the sitemap)
/404.html                                 GitHub Pages custom 404 with links to the hubs             [NEW]
```

- `<comunidad>` = slugs from `data/2027.json`. `<ciudad>` = `slug` from `data/locales-2027.json`. A capital that shares its comunidad's slug gives `/madrid/madrid/` and `/murcia/murcia/`. That is accepted: it is unambiguous and the title says "Madrid capital".
- **Only generate a city page when its `status` is `boletin` or `ayuntamiento`.** Unpublished cities get no page, because the page would be a thin duplicate of the comunidad page. List them in the hub as "pendiente" with no link. Add each page the day its data arrives.
- Province queries ("calendario laboral 2027 alicante") are served by the capital's city page. Mention "provincia de X" once in its copy and link the other towns of that province.
- Use `/festivos/` and not `/festivos-2027/`, for the reason in principle 4. Query matching comes from the title and H1, and Google does not need the year in the slug.
- GitHub Pages cannot send 301s. Do not rename existing URLs. If a rename is ever unavoidable, publish a stub with `<meta http-equiv="refresh" content="0;url=…">` plus a canonical to the new URL.

## 3. Templates per page type

Title limit is 60 characters and meta description limit is 155. The builder picks the **first candidate that fits** and `test_data.py` asserts the lengths. `{R}` = comunidad short name (`name` in 2027.json). `{C}` = city name.

### 3.1 Home `/`
- **title**: `Calendario laboral 2027: festivos y puentes en España` (53)
- **meta**: `Calendario laboral 2027 de España según el BOE: festivos de tu comunidad y tu ciudad, puentes y un planificador que te dice cuántos días libras.` (≤155)
- **H1**: `Calendario laboral 2027`. Answer line: `9 festivos comunes en toda España y 12 en cada comunidad (BOE 13-10-2026). Elige la tuya:`
- **H2s**: `Festivos 2027 en España` · `Puentes 2027` · `Planificador de vacaciones` · `Por comunidad` · `Calendario escolar 2026-2027` (teaser with links) · `Preguntas frecuentes`
- **FAQ (5)**: ¿Cuántos festivos hay en 2027? · ¿Cuándo se publicó el calendario laboral 2027? (BOE 13-10-2026, link) · ¿Qué festivos caen en fin de semana en 2027? (1 May and 25 Dec are Saturdays; 15 Aug is a Sunday and some comunidades move it to 16 Aug, Extremadura to 11 Oct) · ¿Cuántos días laborables tiene 2027? (link `/dias-laborables/`) · ¿Cuándo es Semana Santa 2027? (21–28 March, link)

### 3.2 Comunidad `/<comunidad>/` (exists, retitle)
- **title** candidates: `Calendario laboral 2027 {R}: festivos y puentes` → `Calendario laboral 2027 {R}: festivos` (Comunidad Valenciana falls back to the second, 57)
- **meta**: `Festivos 2027 en {R}: los 12 del BOE con su día, puentes y planificador de vacaciones. Añade los 2 locales de tu ciudad y expórtalo.` (check ≤155 for every R)
- **H1**: `Calendario laboral 2027 {R}`. Answer line: `{R} tiene {n} festivos en 2027: {a} nacionales y {b} de la comunidad, más 2 locales.`
- **H2s**: `Festivos 2027 en {R}` (table) · `Puentes 2027 en {R}` · `Calendario 2027` (grid) · `Festivos locales: elige tu ciudad` (links to city pages; this is the main internal-link block) · `Calendario escolar {R} 2026-2027` (3 lines: start, Navidad, Semana Santa, then a link) · `Preguntas frecuentes`
- **FAQ (3–4)**: ¿Cuántos festivos tiene {R} en 2027? · ¿Es festivo el Jueves Santo / Lunes de Pascua en {R}? (whichever applies) · ¿Qué pasa con el 15 de agosto de 2027 en {R}? · ¿Dónde consulto los festivos de mi municipio?
- Body must hold the name variants once (`Comunitat Valenciana`, `GVA`; `Catalunya`; `Euskadi`; `Illes Balears`), inside the FAQ or the source line.

### 3.3 City `/<comunidad>/<ciudad>/`
- **title** candidates: `Calendario laboral 2027 {C}: festivos y puentes` → `Calendario laboral 2027 {C}: festivos locales` → `Festivos 2027 {C}: calendario laboral`. For a capital whose name equals its comunidad or province, use `{C} capital`.
- **meta** candidates: `Festivos 2027 en {C}: los 12 del BOE y los 2 locales ({d1} y {d2}), con puentes, días laborables y descarga a tu calendario.` → the same with short dates (`22 ene y 5 abr`) → drop `, días laborables`. Long names such as Las Palmas de Gran Canaria and Donostia-San Sebastián need the fallback.
- **H1**: `Calendario laboral 2027 {C}`. Answer line: `Festivos locales de {C} en 2027: {d1, nombre} y {d2, nombre}. En total, 14 días.`
- **H2s**: `Festivos 2027 en {C}` (14 rows, local ones highlighted) · `Puentes 2027 en {C}` (recomputed with the locales, which is unique content and the point of the page) · `Días laborables 2027 en {C}` (month table) · `Calendario 2027` · `Otros municipios de {provincia}` · FAQ
- **FAQ (3)**: ¿Cuáles son los festivos locales de {C} en 2027? (cite the source: "acuerdo de pleno de {fecha}" / BOP) · ¿Cuántos días laborables tiene {C} en 2027? · ¿{d1} es festivo en toda la provincia? (no, only in the municipality)
- Status `ayuntamiento` (pleno agreed, not yet in a boletín): show "Aprobado por el pleno; pendiente de publicación en el boletín" next to the source.

### 3.4 `/festivos/`
- **title**: `Festivos 2027 en España: nacionales y por comunidad` (51)
- **H1** `Festivos 2027`. Table: date · day · holiday · **where** ("Toda España" / list of comunidades / "todas salvo Cataluña y C. Valenciana"). H3 per month (anchors `#enero` …). Links to each `/festivos/<festivo>/`.
- **FAQ**: ¿Cuáles son los festivos nacionales de 2027? · ¿Qué festivos de 2027 caen en sábado o domingo? · ¿Es festivo el 6 de enero de 2027?

### 3.5 `/festivos/<festivo>/` (about 8 pages, generated)
- **title**: `{Festivo} 2027: ¿es festivo? Dónde y qué día cae` (e.g. `Jueves Santo 2027: ¿es festivo? Dónde y qué día cae`, 51)
- **H1** `{Festivo} 2027`. Answer line: `Es el jueves 25 de marzo. Festivo en 17 comunidades; laborable en Cataluña y la Comunitat Valenciana.` Then a 19-row yes/no table and the puente it creates.
- One FAQ: ¿Qué puente hace {festivo} en 2027?

### 3.6 `/puentes/`
- **title**: `Puentes 2027 en España y en tu comunidad` (≤60)
- **H1** `Puentes 2027`. The national ones that cost no holiday days, then the ones that cost 1 day (7 Dec, 11 Oct), then one H2 per comunidad (anchor `#<slug>`) listing its puentes, plus the planner.
- **FAQ**: ¿Cuántos puentes hay en 2027? (state the counting rule: "3+ days off in a row including a holiday") · ¿Hay puente de mayo en 2027? (1 May is a Saturday) · ¿Cuál es el mejor puente de 2027? (Constitución + Inmaculada: ask for 7 Dec and get 5 days)

### 3.7 `/dias-laborables/`
- **title**: `Días laborables 2027: por meses y por comunidad` (47)
- **H1** `Días laborables 2027`. Answer line: `2027 tiene 261 días de lunes a viernes; restando festivos quedan entre {min} y {max} según la comunidad (sin contar los 2 locales).` Then a month × comunidad table (`<table>`, featured-snippet friendly).
- **FAQ**: ¿Cuántos días laborables tiene 2027? · ¿Qué mes tiene más días laborables?

### 3.8 `/semana-santa/`
- **title**: `Semana Santa 2027: fechas, festivos y vacaciones` (48)
- **H1** `Semana Santa 2027`. Answer line: `Del domingo 21 al domingo 28 de marzo de 2027.` Then a table (Domingo de Ramos 21-03, Jueves Santo 25-03, Viernes Santo 26-03, Pascua 28-03, Lunes de Pascua 29-03) showing which comunidades have each day as a labour holiday, a school-break table per comunidad (from the escolar data) and one row for 2028 (Easter Sunday 16-04-2028).

### 3.9 `/calendario-escolar/` (hub)
- **title**: `Calendario escolar 2026-2027 en España por comunidad` (≤60, "España" keeps Mexico's SEP out)
- **H1** `Calendario escolar 2026-2027`. A 19-row table: comunidad · inicio Primaria · fin · Navidad · Semana Santa · link. Unpublished rows show "pendiente".
- **FAQ**: ¿Cuándo empiezan las clases en el curso 2026-2027? · ¿Cuándo son las vacaciones de Navidad 2026? · ¿Cuándo se publica el calendario escolar 2027-2028?

### 3.10 `/calendario-escolar/<comunidad>/`
- **title** candidates: `Calendario escolar 2026-2027 {R}: inicio y vacaciones` → `Calendario escolar 26-27 {R}: clases y vacaciones` → `Calendario escolar 2026-2027 {R}`
- **meta**: `Calendario escolar 2026-2027 de {R}: inicio y fin de clases por etapa, Navidad, Semana Santa y días no lectivos, según la orden oficial.`
- **H1** `Calendario escolar 2026-2027 {R}` (the body also says "curso 26-27" once). Answer line: `Las clases empiezan el {fecha} (Infantil y Primaria) y terminan el {fecha}.`
- Blocks: stage table (start/end) · breaks (Navidad, Semana Santa, others) · días no lectivos list · a 10-month school-year grid (Sep–Jun) that colours non-teaching days · provinces (Andalucía, Castilla-La Mancha) as a selector with anchors · source line linking the boletín order · "Los días festivos locales los fija cada consejo escolar municipal" when the data notes it.
- **FAQ (3)**: ¿Cuándo empiezan las clases en {R}? · ¿Cuándo son las vacaciones de Navidad en {R}? · ¿Cuándo son las vacaciones de Semana Santa 2027 en {R}?

### 3.11 `/vacaciones-escolares/navidad/` and `/semana-santa/`, `/semana-blanca/`
- **title**: `Vacaciones de Navidad 2026 en colegios por comunidad` (53) / `Vacaciones de Semana Santa 2027 en colegios` (44) / `Semana blanca 2027: comunidades y fechas`
- **H1** the same. A 19-row table: último día de clase · vuelta · días sin clase · source link. Sort by return date (that is the question parents ask).

## 4. On-page rules (all templates)

- One H1. H2s as in §3. The holiday list is an HTML `<table>` with `<caption>` (featured snippets read tables).
- **Visible "Actualizado: 26 oct 2026"** under the answer line, with the same date as `dateModified`. Use the data file's `updated` value, not the build time.
- Breadcrumb navigation, visible: `España › Comunidad Valenciana › Valencia`.
- FAQ: 3–5 questions, 1–3 sentence answers, at the bottom, rendered as `<details>` (collapsed, per the owner's minimal-text preference). The text is in the HTML, so Google reads it.
- Name variants and "pdf / excel / imprimir": put them in button labels (`Descargar PDF`, `Descargar Excel (CSV)`, `Imprimir`). That is natural keyword coverage with no prose.
- Copy budget: answer line ≤ 25 words, FAQ ≤ 60 words per answer, ≤ 250 words of prose per page in total.

## 5. Structured data (JSON-LD)

Reality check: since August 2023 Google shows **FAQ rich results only for authoritative government and health sites**, and **Event** rich results are meant for real attendable events. Holidays are not, and the current markup (Event + Place/PostalAddress with only a region) is weak and close to "misleading markup". So:

- **Remove** the per-holiday `Event` markup. Replace it with an `ItemList` whose items are `{"@type":"ListItem","position":n,"name":"Viernes Santo · viernes 26 de marzo de 2027"}` (harmless, and it describes the visible list).
- **BreadcrumbList on every page** (rich-result eligible: it replaces the URL in the result with a breadcrumb path).
- **WebSite + Organization on the home page** (helps Google show "El Calendario Laboral" as the site name).
- **Dataset** on the comunidad, city and escolar pages (eligible for Google Dataset Search, and honest: we publish data with downloads).
- **FAQPage**: keep it. It costs nothing, Bing and AI answer engines use it, and it mirrors the visible FAQ exactly.
- **WebPage** with `dateModified` and `isBasedOn` (the official document).

Templates (fill the placeholders at build time):

```json
{"@context":"https://schema.org","@type":"WebSite","name":"El Calendario Laboral","alternateName":"elcalendariolaboral.es","url":"https://elcalendariolaboral.es/","inLanguage":"es-ES"}
```
```json
{"@context":"https://schema.org","@type":"Organization","name":"El Calendario Laboral","url":"https://elcalendariolaboral.es/","logo":"https://elcalendariolaboral.es/icons/icon-512.png"}
```
```json
{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
 {"@type":"ListItem","position":1,"name":"España","item":"https://elcalendariolaboral.es/"},
 {"@type":"ListItem","position":2,"name":"Comunidad Valenciana","item":"https://elcalendariolaboral.es/comunitat-valenciana/"},
 {"@type":"ListItem","position":3,"name":"Valencia","item":"https://elcalendariolaboral.es/comunitat-valenciana/valencia/"}]}
```
```json
{"@context":"https://schema.org","@type":"Dataset","name":"Festivos laborales 2027 en Comunidad Valenciana",
 "description":"Los 12 festivos laborales de 2027 en la Comunitat Valenciana según el BOE-A-2026-21254, con día de la semana.",
 "url":"https://elcalendariolaboral.es/comunitat-valenciana/","inLanguage":"es-ES","dateModified":"2026-10-26",
 "temporalCoverage":"2027-01-01/2027-12-31","spatialCoverage":{"@type":"Place","name":"Comunitat Valenciana, España"},
 "isBasedOn":"https://www.boe.es/boe/dias/2026/10/13/pdfs/BOE-A-2026-21254.pdf",
 "license":"https://creativecommons.org/licenses/by/4.0/","creator":{"@type":"Organization","name":"El Calendario Laboral"},
 "distribution":[{"@type":"DataDownload","encodingFormat":"text/calendar","contentUrl":"https://elcalendariolaboral.es/ics/comunitat-valenciana.ics"},
                 {"@type":"DataDownload","encodingFormat":"text/csv","contentUrl":"https://elcalendariolaboral.es/csv/comunitat-valenciana.csv"}]}
```
```json
{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
 {"@type":"Question","name":"¿Cuántos festivos tiene la Comunidad Valenciana en 2027?",
  "acceptedAnswer":{"@type":"Answer","text":"12 festivos según el BOE: 9 nacionales y 3 autonómicos (19 de marzo, 29 de marzo y 9 de octubre), más 2 locales de cada municipio."}}]}
```
The BOE data is public. License our compilation CC BY 4.0 (it invites reuse with a link, which means backlinks), but only if the owner agrees. Otherwise drop `license`.

For escolar pages, `Dataset.isBasedOn` = the region's `source.url`, and `temporalCoverage` = `2026-09-01/2027-06-30`.

## 6. Internal linking graph

```
            ┌──────────── / (home) ───────────┐
            │  links: 19 comunidades, /festivos/, /puentes/, /dias-laborables/,
            │         /calendario-escolar/, /vacaciones-escolares/navidad/, /semana-santa/
            ▼
   /<comunidad>/ ──► /<comunidad>/<ciudad>/ (all verified cities of that comunidad)
        │  ▲            │ ──► sibling cities in the same province (max 10)
        │  │            └──► /<comunidad>/ , /calendario-escolar/<comunidad>/
        │  └── /festivos-locales/ (hub of all cities)
        ├──► /calendario-escolar/<comunidad>/ ◄──► /calendario-escolar/ (hub)
        ├──► /puentes/#<comunidad>   /dias-laborables/#<comunidad>
        └──► /festivos/<festivo>/ for the region-specific holidays it has
   /festivos/<festivo>/ ──► each comunidad where it is a holiday
   /vacaciones-escolares/* ──► each /calendario-escolar/<comunidad>/
```
- Footer (sitewide): the 19 comunidades plus the 6 hubs. This is in place today for comunidades; add the hubs.
- Anchor text = the query: "Calendario laboral 2027 Valencia", "Calendario escolar Madrid 2026-2027". Never "ver" or "aquí".
- Every page is ≤ 3 clicks from home. Every city page has ≥ 2 inbound links (comunidad page + hub).

## 7. Sitemap, robots, crawl

- `sitemap.xml` lists every indexable page. `lastmod` = the date that page's **data** last changed: `updated` in 2027.json, or the entry's `source.checked` for cities and escolar. Do not use the build date, which teaches Google to ignore our lastmod. Drop `changefreq` and `priority` (Google ignores them). Leave out `/privacidad/`.
- When the site grows past about 200 URLs, split into `sitemap-laboral.xml`, `sitemap-escolar.xml` and `sitemap-ciudades.xml` with a `sitemap_index.xml`, which lets you see indexation per section in Search Console.
- `robots.txt` is fine as it is (Allow all plus the sitemap line).
- Add `404.html` (GitHub Pages serves it) with links to the hubs.
- PDFs: `/pdf/calendario-laboral-2027-<slug>.pdf`. Google indexes PDFs and they rank for "… pdf" queries. Put the page URL inside the PDF footer.
- After every data update, ping IndexNow (Bing/Yandex) with the changed URLs: `https://api.indexnow.org/indexnow?url=…&key=…`, with the key file served at the site root. Google uses the sitemap plus Search Console.

## 8. Core Web Vitals and performance

Pages are about 38 KB of HTML with server-rendered content, which is a good base. To keep it:
- **Self-host Inter** (woff2, latin subset, 400/600/700) with `font-display: swap` and a `<link rel="preload">` on the 400 weight, or use the system font stack. The Google Fonts stylesheet is a render-blocking cross-origin request today.
- Inline critical CSS (above the fold) or keep `app.css` < 20 KB. The CSS cache-busting hash is already in place.
- Reserve the calendar grid's height (`aspect-ratio`/min-height) so JS hydration causes no CLS.
- All JS `defer`. The planner must not block the first paint, and the answer line plus table render without JS.
- INP: month navigation and selector changes must not re-render the whole page.
- The service worker is fine, but never cache HTML stale-first, or a data correction would not reach people. Use network-first for HTML.

## 9. Images and Open Graph

- One OG image per indexable page (1200×630 PNG, already generated per comunidad). Extend to city, escolar and hub pages. Content: big "Festivos 2027 · Valencia", the 14 dates in two columns, the domain. This is what spreads on WhatsApp, the main sharing channel for these pages.
- `og:image:alt`, plus `twitter:card` = summary_large_image (already done).
- No decorative images in the page body. If a map of comunidades is added, use inline SVG with real `<a>` links, not an image map (calendarioslaborales.com has image-only links).

## 10. Search Console, Bing Webmaster, first backlinks

### Owner steps (cannot be automated)
1. **Search Console**: add a *Domain property* `elcalendariolaboral.es` → copy the TXT record → add it at the DNS registrar → Verify. Then Sitemaps → submit `https://elcalendariolaboral.es/sitemap.xml`. URL Inspection → "Request indexing" for `/`, the 5 biggest comunidades (Madrid, Andalucía, Cataluña, Comunidad Valenciana, Galicia) and the Navidad page.
2. **Bing Webmaster Tools**: "Import from Google Search Console" (one click once step 1 is done). This also covers DuckDuckGo, Ecosia and ChatGPT search, all of which use Bing's index.
3. Turn on **"Enforce HTTPS"** in the GitHub Pages settings, and point both apex and `www` DNS at GitHub Pages so `www` redirects.
4. Optional: privacy-friendly analytics (GoatCounter, Cloudflare Web Analytics). Search Console alone is enough at first.

### Legitimate first backlinks (no spam, no paid links)
1. **Utility for HR people and gestorías**: offer a free embeddable widget ("Festivos 2027 de tu comunidad", an `<iframe>` or `<script>` with a visible credit link) and the CC BY CSV/ICS files. Post about it once in HR or gestoría communities (LinkedIn text drafted for the owner to post himself), in r/spain and r/askspain threads that ask "calendario laboral 2027", and in Forocoches or Menéame only where somebody asks.
2. **Ayuntamientos and AMPAs**: many town and school-association websites link "calendario laboral/escolar" resources. Email the webmaster or AMPA a short note: "La página X tiene un error / falta 2027; aquí está el calendario oficial con fuente BOE". Only send it where it really helps.
3. **Corrections as outreach**: we documented competitors' errors (wrong weekday, wrong Easter). Journalists and bloggers who covered the calendar can be told politely; they often add the source link.
4. **Open data**: publish the JSON on GitHub (the repo already exists) and add it to datos.gob.es-style lists or awesome-lists of Spanish open data. Developers link to accurate datasets.
5. **Wikipedia**: do not add self-links. If an article cites outdated holiday data, the official BOE link is what belongs there, not us.
6. **Product Hunt / Show HN–style launches** do not fit a Spanish calendar. Skip them.

## 11. Year rollover and data upkeep

- October each year: the BOE publishes, `data/<year+1>.json` is built, evergreen pages switch, and the old year moves to `/<year>/…`.
- Local holidays: re-run the research each week from November to January (regional compilations arrive in that window: DOGC, BOJA, BOCyL, BOCM…). Add a city page as soon as its entry turns non-null.
- School 2027-28: check the boletines each month from March 2027 and fill `data/escolar-2027-28.json`.
- `python seo/check_data.py` must pass before any commit that touches `data/`.

## 12. Measuring

Per section in Search Console (sitemap split, §7), look at impressions and clicks for: the head terms (`calendario laboral 2027`, `calendario escolar 2026-2027`), `+ comunidad`, city names, `pdf/excel`, and the holiday questions. Expect a ramp of 2–6 weeks after indexing. The December–January peak is the first real test.

## 13. Multilingual: Catalan (`/ca/`), Galician (`/gl/`), Basque (`/eu/`)

The research behind this is in `keywords.md` → "Catalan, Galician and Basque". In short: Catalan has real independent demand, Galician mostly overlaps with Spanish, and Basque is small, with Basque-territory users mostly searching in Spanish. Build all three from the same templates, but **spend content effort in this order: ca > gl ≈ eu**.

### 13.1 URL scheme

```
Spanish (default, unchanged)   /                /madrid/            /madrid/madrid/          /festivos/   /calendario-escolar/galicia/
Catalan                        /ca/             /ca/madrid/         /ca/madrid/madrid/       /ca/festivos/ /ca/calendario-escolar/galicia/
Galician                       /gl/             /gl/madrid/  …
Basque                         /eu/             /eu/madrid/  …
```
- **Spanish stays at the root.** Do not move it to `/es/`, because the existing URLs keep their signals.
- **Keep the slugs identical across languages; only the prefix changes.** The reasons:
  1. URL words are a very weak ranking signal, and the visible breadcrumb in the results comes from the localized `BreadcrumbList` names, not the slug.
  2. The hreflang mapping and the language switcher become a pure prefix swap (`/ca` + path), which leaves no mapping tables to get wrong.
  3. It keeps contested names (País Valencià vs Comunitat Valenciana, Galiza vs Galicia) out of URLs for good.

  Localized slugs (`/ca/festius/`, `/eu/jaiegunak/`) would be a small CTR gain at best. If ever wanted, add them later as a `slugs` map in `data/i18n.json`, but never change a URL once it is indexed.
- Every language version of a page is a full translation: the answer line, table headers, holiday names, FAQ, buttons, meta, JSON-LD and OG text. A half-translated page (Spanish table in a Catalan frame) is the one thing that makes Google treat it as a duplicate.

### 13.2 Head tags (every page, every language)

```html
<html lang="ca">                                   <!-- es | ca | gl | eu -->
<link rel="canonical" href="https://elcalendariolaboral.es/ca/cataluna/">   <!-- SELF, never the Spanish URL -->
<link rel="alternate" hreflang="es" href="https://elcalendariolaboral.es/cataluna/">
<link rel="alternate" hreflang="ca" href="https://elcalendariolaboral.es/ca/cataluna/">
<link rel="alternate" hreflang="gl" href="https://elcalendariolaboral.es/gl/cataluna/">
<link rel="alternate" hreflang="eu" href="https://elcalendariolaboral.es/eu/cataluna/">
<link rel="alternate" hreflang="x-default" href="https://elcalendariolaboral.es/cataluna/">
<meta property="og:locale" content="ca_ES">       <!-- es_ES | ca_ES | gl_ES | eu_ES -->
<meta property="og:locale:alternate" content="es_ES"> … (the other three)
```
Rules:
- Use language-only codes `es`, `ca`, `gl`, `eu`, with no region subtag: Spanish speakers anywhere get the Spanish page, and Valencian users get `ca`.
- The **same full set on every version, including a self-reference** (the reciprocal links are mandatory, or Google ignores the cluster).
- `x-default` = the Spanish URL.
- Only emit an alternate if that page exists in that language. If some page type ships in Spanish first, it gets no hreflang until its translations exist, and the translations are then added to every member at once.
- Builder helper (pseudo):
  ```python
  LANGS = ["es", "ca", "gl", "eu"]
  def url(lang, path): return SITE + ("" if lang == "es" else lang + "/") + path   # path like "cataluna/" or ""
  def alternates(path): return [(l, url(l, path)) for l in LANGS] + [("x-default", url("es", path))]
  ```
- JSON-LD carries `"inLanguage": "ca"` (etc.), localized `name`/`description`/FAQ text, and breadcrumb `item` URLs inside the same language.

### 13.3 Localized title and description patterns (first candidate ≤ 60 chars wins; test the lengths)

`{R}` = region display name in that language from `data/i18n.json`. `{in}` = the locative phrase (ca "a Catalunya", "a la Comunitat Valenciana", "a les Illes Balears"; gl "en Galicia", "na Comunidade Valenciana", "nas Illas Baleares", "no País Vasco"). `{G}` = the Basque genitive-locative ("Euskadiko", "Nafarroako", "Madrilgo", "Valentziako Erkidegoko", "Balear Uharteetako", "Bilboko", "Donostiako", "Gasteizko", "Iruñeko"). **Store `in` and `gen` per region and per city in `i18n.json`; do not generate them.** Catalan articles and Basque declension are irregular (Iruña → Iruñeko).

| Page | Catalan | Galician | Basque |
|---|---|---|---|
| home | `Calendari laboral 2027: festius i ponts per comunitats` | `Calendario laboral 2027: festivos e pontes en España` | `2027ko lan-egutegia: jaiegunak eta zubiak` |
| comunidad | `Calendari laboral 2027 {R}: festius i ponts` → `Calendari laboral 2027 {R}` | `Calendario laboral 2027 {R}: festivos e pontes` → `Festivos 2027 en {R}: calendario laboral` | `{G} 2027ko lan-egutegia: jaiegunak eta zubiak` → `{G} jaiegunak 2027: lan-egutegia` |
| city | `Festius 2027 {C}: calendari laboral i festes locals` → `Festius 2027 {C}: calendari laboral` | `Festivos 2027 en {C}: calendario laboral e locais` → `Festivos locais 2027 {C}` | `{G} jaiegunak 2027: lan-egutegia` |
| /festivos/ | `Festius 2027: estatals, per comunitat i locals` | `Festivos 2027: estatais, por comunidade e locais` | `Jaiegunak 2027: estatukoak, erkidegokoak eta tokikoak` |
| /puentes/ | `Ponts i festius 2027 per comunitats` (never "Ponts 2027" alone: it pulls French results) | `Pontes e festivos 2027 en España` (not "Pontes 2027" alone: Portuguese) | `2027ko zubiak eta jaiegunak, erkidegoka` |
| /dias-laborables/ | `Dies laborables 2027 per mesos i comunitats` | `Días laborables 2027 por meses e comunidade` | `2027ko lanegunak, hilabeteka eta erkidegoka` |
| /festivos-locales/ | `Festes locals 2027 de cada municipi` | `Festivos locais 2027 de cada concello` | `Tokiko jaiak 2027, udalerriz udalerri` |
| /semana-santa/ | `Setmana Santa 2027: dates, festius i vacances` | `Semana Santa 2027: datas, festivos e vacacións` | `Aste Santua 2027: datak, jaiegunak eta oporrak` |
| /calendario-escolar/ | `Calendari escolar 2026-2027 per comunitats` | `Calendario escolar 2026-2027 por comunidades` | `Eskola-egutegia 2026-2027, erkidegoka` |
| escolar region | `Calendari escolar 2026-2027 {R}: inici i vacances` → `Calendari escolar 26-27 {R}` | `Calendario escolar 2026-2027 {R}: inicio e vacacións` → `Calendario escolar 26-27 {R}` | `{G} eskola-egutegia 2026-2027: hasiera eta oporrak` → `{G} eskola-egutegia 2026-2027` |
| Navidad | `Vacances de Nadal 2026 a les escoles, per comunitat` | `Vacacións de Nadal 2026 nos colexios, por comunidade` | `Gabonetako oporrak 2026 ikastetxeetan, erkidegoka` |

Meta description patterns (≤155):
- **ca, comunidad**: `Els festius de 2027 {in} segons el BOE, amb el dia de la setmana, els ponts i un planificador de vacances. Afegeix-hi les 2 festes locals.`
- **gl, comunidad**: `Os festivos de 2027 {in} segundo o BOE, co día da semana, as pontes e un planificador de vacacións. Engade os 2 festivos locais do teu concello.`
- **eu, comunidad**: `{G} 2027ko jaiegunak BOEren arabera: asteko eguna, zubiak eta oporren planifikatzailea. Gehitu zure udalerriko 2 tokiko jaiak.`
- **ca, escolar**: `Calendari escolar 2026-2027 {in}: inici i final de curs per etapes, vacances de Nadal i Setmana Santa i dies no lectius, segons l'ordre oficial.`

These phrasings follow the ranking pages (3cat, beteve, democrata/ca, Mundo R, Euskaltel, euskadi.eus). The i18n agent's native-reviewed strings take precedence over these if they differ.

Body keyword variants to place once (FAQ or source line): ca `calendari laboral catalunya gencat`, `festius caib`, `calendari escolar gva`; gl `DOG`, `Xunta de Galicia`, `Entroido`; eu `lan egutegia` (spaced form), `jai egunak`, `EAE`, `BOPV`, `BON`.

Dates per language, with day and month names stored in i18n.json:
- ca `divendres, 26 de març de 2027` (and `d'abril`, `d'agost`, `d'octubre`: elide before a vowel)
- gl `venres, 26 de marzo de 2027`
- eu `2027ko martxoaren 26a, ostirala`

### 13.4 Region names (blocking issue for i18n.json)

Use the statutory or official names in titles and H1s:
- **Comunitat Valenciana** (ca), not "País Valencià".
- **Galicia** (gl), not "Galiza".
- **Euskadi** (eu), not "Euskal Herria". Euskal Herria covers Navarra and the French Basque Country, so it is factually wrong for the comunidad autónoma.
- Nafarroa, Illes Balears and Catalunya are fine.

Evidence (autocomplete, Xunta, euskadi.eus, Euskaltel) is in `keywords.md`. Alternative names may appear once in body text.

### 13.5 Sitemaps

Split by language and reference them from `sitemap_index.xml` (robots.txt points to the index):
```
sitemap_index.xml → sitemap-es.xml, sitemap-ca.xml, sitemap-gl.xml, sitemap-eu.xml
```
Each `<url>` lists every alternate, including itself:
```xml
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
 <url>
  <loc>https://elcalendariolaboral.es/ca/cataluna/</loc>
  <lastmod>2026-10-26</lastmod>
  <xhtml:link rel="alternate" hreflang="es" href="https://elcalendariolaboral.es/cataluna/"/>
  <xhtml:link rel="alternate" hreflang="ca" href="https://elcalendariolaboral.es/ca/cataluna/"/>
  <xhtml:link rel="alternate" hreflang="gl" href="https://elcalendariolaboral.es/gl/cataluna/"/>
  <xhtml:link rel="alternate" hreflang="eu" href="https://elcalendariolaboral.es/eu/cataluna/"/>
  <xhtml:link rel="alternate" hreflang="x-default" href="https://elcalendariolaboral.es/cataluna/"/>
 </url>
</urlset>
```
Hreflang in both the HTML head and the sitemap is redundant but allowed, as long as the two agree. Generate both from the same helper.

### 13.6 Search Console and Bing

- **One Domain property** (`elcalendariolaboral.es`, DNS TXT) covers every language. Submit `sitemap_index.xml`.
- Optional but useful: add URL-prefix properties `https://elcalendariolaboral.es/ca/`, `/gl/`, `/eu/`. Under a verified Domain property they verify automatically and give per-language performance reports without filters.
- Check Search Console → Pages → "Alternate page with proper canonical tag" (expected and fine) vs "Duplicate, Google chose different canonical" (bad: it means a translation is incomplete).
- Bing: import from Search Console. Bing also uses `<html lang>` and `content-language` rather than relying only on hreflang, so keep `lang` correct.

### 13.7 Language switcher UX (no auto-redirect)

- Put a small switcher in the header, labelled `ES · CA · GL · EU` (in the native forms Español, Català, Galego, Euskara as `title`/`aria-label`). It is a set of plain `<a href>` links to the **equivalent page** (prefix swap), with `hreflang` and `lang` attributes on each link. The current language is marked with `aria-current="true"`.
- **Never redirect by IP or `Accept-Language`.** Googlebot crawls mostly from the US without Accept-Language, so it would never see the translations, and Google's guidance explicitly advises against this. The root `/` always serves Spanish.
- Optional and non-intrusive: if `navigator.language` starts with `ca`, `gl` or `eu` and the user is on a Spanish page, show a one-line dismissible bar ("Disponible en català →"). Remember the dismissal in `localStorage` (try/catch). Never move the user automatically.
- Inside a language, every internal link (nav, footer, related cards, breadcrumbs) stays in that language. The switcher is the only cross-language link.

### 13.8 Which language pages get linked from where

| From | Link to |
|---|---|
| Every page (header switcher) | The same page in the other 3 languages |
| Spanish `/cataluna/`, `/comunitat-valenciana/`, `/baleares/` (and their cities and escolar pages) | A visible "En català" chip next to the H1, besides the switcher. This is where Catalan demand is, so it is worth an extra link. |
| Spanish `/galicia/` (+ cities, escolar) | "En galego" chip |
| Spanish `/pais-vasco/`, `/navarra/` (+ cities, escolar) | "Euskaraz" chip |
| Spanish home footer | "Català · Galego · Euskara" → `/ca/`, `/gl/`, `/eu/` |
| `/ca/`, `/gl/`, `/eu/` home pages | All 19 comunidades in that language. Catalan lists Catalunya, Comunitat Valenciana and Illes Balears first, Galician lists Galicia first, Basque lists Euskadi and Nafarroa first (the order follows demand, and the rest stay alphabetical). |

### 13.9 Scope and rollout order

1. `/ca/` for every page type (it has real demand). Catalan city pages first for Catalonia (CIDO-diba data), Valencia and Balears.
2. `/gl/` and `/eu/` for every page type from the same templates. Native strings come from `data/i18n.json`.
3. Per-language OG images (text in that language). `.ics` event names in that language are optional.
4. `test_data.py` checks, per page: the hreflang set is complete and reciprocal, the canonical is the self URL, `lang` matches the prefix, and the title and description lengths are within limits for every language.
