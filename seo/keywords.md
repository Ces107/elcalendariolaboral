# Keyword research: elcalendariolaboral.es

Checked 2026-10-26. This file is for whoever builds the site. Queries stay in Spanish, notes are in English. Target URLs follow the evergreen scheme in `seo/plan.md` §2: the year goes in the title, not the slug.

## How priority was judged (no invented volumes)

There is no Search Console data yet: the domain did not answer HTTP on 2026-10-26, so it is not indexed. No paid keyword tool was used either. Priority comes from four signals:

1. **Google autocomplete** (`suggestqueries.google.com`, `hl=es&gl=es`, queried 2026-10-26). Autocomplete only shows queries with real, repeated demand, and they are roughly ordered by popularity. **Caveat:** the suggestions are biased towards the requester's location, which here is the Comunitat Valenciana. Valencia, Castellón, Alicante, Elche and "gva" show up everywhere for that reason, so read them as "regional modifiers are huge" and not as "Valencia is the biggest market". Madrid, Andalucía and Cataluña still appear in almost every list even with that bias, which tells us they are big.
2. **Seasonality.** The year flips in Spanish searches: "calendario laboral 2027" rises from mid-October (BOE published 13-10-2026), peaks from December to the first week of January, and stays high in March–April (Semana Santa) and before every puente. "Calendario escolar" peaks from June to September, with a second peak in December (Navidad dates) and March (Semana Santa).
3. **Intent fit**, meaning how well a static calendar tool answers the query. Our pages give exact dates plus a planner, so we can satisfy "festivos/puentes/días laborables" queries better than news articles do.
4. **Competition visible in the results**: news sites (Time Out, El Español, eldiario.es, Diario de León, ESdiario), HR SaaS blogs (PayFit, Jibble, Coverflex), aggregators (calendarr, diainternacionalde, calendarioslaborales.com, calendar.center, cuandoenelmundo), official pages (BOE, gencat, gva, jcyl, BOCM).

Scale used below: **P1** = must have before mid-November 2026. **P2** = before Christmas. **P3** = long tail or seasonal, do it when cheap.

## Phrasing patterns people actually type (from autocomplete)

- Year forms: `2027`, `2026-2027`, `2026-27`, `26-27`, `2026/2027`, `2026 2027`, `2026 a 2027`. School pages must contain **both** "2026-2027" and "26-27".
- Region forms: `comunidad valenciana` / `comunitat valenciana` / `gva` / `valencia`; `cataluña` / `catalunya` / `gencat` / `calendari laboral`; `pais vasco` / `euskadi` / `bizkaia`; `baleares` / `mallorca` / `palma de mallorca`; `castilla y leon` / `cyl` / `jcyl`; `comunidad de madrid` / `madrid capital`; `junta de andalucia`; `xunta de galicia`; `boc` (Canarias). Titles use the common Spanish name; the body and FAQ carry the other forms once.
- Format modifiers (very frequent): `pdf`, `excel`, `para imprimir`, `boe`, `oficial`, `cuando sale`, `capital`, `ciudad`, `ayuntamiento`. Sector modifiers (`construccion`, `metal`, `ccoo`, `ugt`) are convenio calendars, so leave them out.
- Question forms: `cuando es`, `es festivo`, `donde es festivo`, `cuando cae`, `que dia es`, `hay puente`, `como cae`, `cuantos dias laborables tiene 2027`, `cuando empiezan las clases`, `cuando acaba el colegio`.

## Clusters

### A. Calendario laboral 2027 (core, P1)

| Query family | Priority | Target page | Notes |
|---|---|---|---|
| calendario laboral 2027 · calendario laboral 2027 españa · calendario laboral 2027 boe | P1 | `/` | Head term. Autocomplete shows it first for "calendario laboral". Competing with news sites and PayFit. Our answer is the tool plus the BOE citation. |
| calendario laboral 2027 + comunidad (madrid, andalucía, cataluña/catalunya, comunidad valenciana/gva, galicia, país vasco/euskadi, canarias, castilla y león, aragón...) | P1 | `/<comunidad>/` (already exist) | All 19 exist. Every comunidad appears in autocomplete with `pdf`, `excel` or `para imprimir`. |
| calendario laboral 2027 + provincia/capital (valencia, castellón, alicante, elche, sevilla, barcelona, zaragoza, bizkaia, málaga, valladolid, vigo, murcia...) | P1 | `/<comunidad>/<ciudad>/` (new) | City = comunidad + its 2 local holidays. This is the biggest gap in the site today, because people search for **their town**. |
| calendario laboral 2027 + capital/ciudad/ayuntamiento (e.g. "madrid capital", "barcelona ciudad", "sevilla capital") | P1 | same city page | Use "capital" in the H1/title for capitals that share a name with their province or comunidad (Madrid, Valencia, Murcia, Zaragoza...). |
| calendario laboral 2027 pdf · excel · para imprimir (+ region) | P1 | each comunidad/city page: print CSS + downloadable PDF + .ics/.csv | Very frequent modifier. Competitors win this with a printable page (calendarr `/imprimir/`). |
| calendario laboral 2027 cuando sale · oficial | P2 | FAQ on `/` | It is already out (BOE 13-10-2026), so answer with the date and the link. |
| calendario 2027 · calendario 2027 con festivos · calendario 2027 para imprimir/pdf | P2 | `/` (print view + PDF) | Generic year calendar. calendarr owns it; we can rank with the "con festivos de tu comunidad" angle. |
| calendario laboral 2026 (still searched heavily until December) | P2 | `/2026/` (optional archive) | Current-year queries ("festivos noviembre 2026", "puente diciembre 2026") dominate October–December. One 2026 page from the 2026 BOE would catch this traffic now. Optional, since it needs its own data file. |

### B. Festivos 2027 (P1)

| Query family | Priority | Target | Notes |
|---|---|---|---|
| festivos 2027 · festivos 2027 españa · festivos nacionales 2027 · dias festivos 2027 | P1 | `/festivos/` | One national list with a "where it is a holiday" column for each date. Today the home page mixes this with the tool. |
| festivos 2027 + comunidad/ciudad (valencia capital, madrid, mallorca, palma, euskadi, catalunya, andalucía...) | P1 | comunidad/city pages | The title must contain "festivos 2027" as well as "calendario laboral 2027". |
| festivos locales 2027 / fiestas locales 2027 (+ ciudad: valencia, bilbao, zaragoza, coruña, toledo, sevilla, vigo, granada, santander, getafe, canarias) | P1 | city pages + `/festivos-locales/` hub | Autocomplete lists many cities, which shows demand right down to town level. Data comes from `data/locales-2027.json`. |
| festivos + month: festivos enero 2027, festivos noviembre 2026 | P3 | anchors on `/festivos/#enero` | Cheap to do: month H3s inside the festivos page. |
| single-holiday questions: "jueves santo 2027 es festivo", "jueves santo 2027 donde es festivo", "lunes de pascua 2027 es festivo", "festivo 12 de octubre 2027", "15 de agosto 2027", "19 de marzo 2027 festivo" | P2 | `/festivos/<festivo>/` (about 8 pages) | Each one gets a map/table of comunidades where it is or is not a holiday. Strong People-Also-Ask and featured-snippet bait, and news sites answer it badly. |

### C. Puentes 2027 (P1)

| Query family | Priority | Target | Notes |
|---|---|---|---|
| puentes 2027 · puentes 2027 españa · puentes 2027 + comunidad (madrid, catalunya, galicia, país vasco, andalucía, aragón, comunidad valenciana) | P1 | `/puentes/` + section on each comunidad page | Autocomplete shows comunidad variants, so give each comunidad page a "Puentes 2027 en X" H2 with its own anchor. |
| puente de mayo 2027 · puente de diciembre 2027 · puente de octubre 2027 · puente del pilar 2027 · hay puente de mayo en 2027 · como cae el puente de mayo 2027 | P2 | anchors in `/puentes/` (`#mayo`, `#octubre`, `#diciembre`) | 1 May 2027 is a Saturday, so the answer is "no puente in most regions". Answering it honestly is fine. |
| dias de vacaciones 2027 · como aprovechar los puentes 2027 | P2 | planner on `/` and `/puentes/` | Our planner is the differentiator. Use the "pide X días, libra Y" framing. |

### D. Días laborables 2027 (P2)

| Query family | Priority | Target | Notes |
|---|---|---|---|
| dias laborables 2027 · dias laborables 2027 españa · cuantos dias laborables tiene 2027 · dias laborables año 2027 | P2 | `/dias-laborables/` | Computed from our data for each comunidad: 261 Monday–Friday days, minus the holidays that fall on weekdays. Nobody official publishes this, and news sites get it wrong (we saw miscounts). |
| dias laborables 2027 por meses · enero 2027 · madrid · catalunya · barcelona | P2 | the same page: a month × comunidad table, plus a block on each comunidad page | Easy to generate. Good featured-snippet table. |

### E. Calendario escolar 2026-2027 (P1 now, peak in June–September and around the breaks)

| Query family | Priority | Target | Notes |
|---|---|---|---|
| calendario escolar 2026-2027 · 2026-27 · 26-27 · 2026/2027 | P1 | `/calendario-escolar/` | Results are polluted by Mexico's SEP (excelsior, chilango...). Write "España" in the title and use the `es` locale. |
| calendario escolar 26-27 + comunidad (comunidad valenciana/gva, madrid, castilla y león, andalucía, aragón, galicia, cataluña...) and + provincia/ciudad (castellón, alicante, elche, sevilla) | P1 | `/calendario-escolar/<comunidad>/` | Data comes from `data/escolar-2026-27.json`. Andalucía and Castilla-La Mancha set dates by province, so they get province sections. |
| calendario escolar 26-27 pdf · dog · orden · xunta | P2 | the same page, linking to the official boletín | Always link the official order. That builds trust and catches "orden calendario escolar" queries. |
| inicio curso escolar 2026 · cuando empiezan las clases (+ comunidad) | P3 (peak July–September 2027 for 27-28) | the same page | The first line of each page answers "Las clases empiezan el …". |
| fin de curso 2027 · cuando acaba el colegio 2027 · vacaciones de verano 2027 colegios | P2 (peak May–June 2027) | the same page | The end date per stage. |

### F. Vacaciones escolares: Navidad, Semana Santa, semana blanca (P1 for Navidad right now)

| Query family | Priority | Target | Notes |
|---|---|---|---|
| vacaciones navidad 2026 · vacaciones navidad 2026 colegio · + comunidad (madrid, catalunya, canarias, comunidad valenciana/gva) · calendario escolar navidad 2026 · vacaciones navidad 2026 2027 | **P1, peak from now to 23 Dec** | `/vacaciones-escolares/navidad/` (one table of 19 comunidades) + anchor on each school page | The most time-sensitive opportunity: it is searched now and calendar.center shows one national range sourced from a third party. |
| vacaciones semana santa 2027 · + colegios · + comunidad · dias de vacaciones semana santa 2027 | P1 (peak February–March 2027) | `/vacaciones-escolares/semana-santa/` | Comparison table across comunidades. Each break differs: Madrid has 11 days, Valencia runs 25 March to 5 April, and so on. |
| semana blanca 2027 (+ málaga, madrid, andalucía, aragón, castilla-la mancha, cataluña, país vasco, toledo) | P2 (peak January–February) | `/vacaciones-escolares/semana-blanca/` | Only the comunidades that have one. Andalucía's is provincial. |
| dias no lectivos 2026/2027 (+ madrid, sevilla, valencia, galicia, asturias, carnaval) | P2 | school pages, "Días no lectivos" list | |
| vacaciones escolares 2027 (+ españa, madrid, valencia) | P2 | `/vacaciones-escolares/` hub | |

### G. Calendario escolar 2027-2028 (P3 now, P1 from about April 2027)

`calendario escolar 2027-2028` and `27-28` + madrid, aragón, castilla y león/cyl, andalucía, galicia, cantabria, canarias, valencia already appear in autocomplete in October 2026. Comunidades usually publish between March and June. Make `/calendario-escolar/2027-2028/` a URL that shows "pendiente de publicación" plus the earlier course's dates for reference. It can start collecting links now, and gets filled in the day each order is published.

### H. Semana Santa and fixed dates (P2, evergreen once a year)

| Query | Priority | Target | Answer |
|---|---|---|---|
| semana santa 2027 · fecha · cuando es · fechas españa · semana santa 2027 y 2028 | P2 | `/semana-santa/` | Domingo de Ramos 21 March, Jueves Santo 25 March, Viernes Santo 26 March, Domingo de Resurrección 28 March, Lunes de Pascua 29 March 2027. Add a table of where each day is a labour holiday (BOE) and of school breaks per comunidad. Include 2028 (Easter 16 April 2028) as a row. |
| jueves santo 2027 cuando cae / es festivo en valencia | P2 | the same page, anchor | It is not a holiday in Cataluña or the Comunitat Valenciana (BOE). |
| lunes de pascua 2027 es festivo / donde | P2 | the same page, anchor | Baleares, Cataluña, Navarra, País Vasco, La Rioja and Comunitat Valenciana (BOE). |

## Competitors: what they do well and badly

| Site | Does well | Does badly / opening for us |
|---|---|---|
| **calendarr.com** (`/espana/calendario-2027/`, `/espana/festivos-2027/`, `/imprimir/`) | Strong domain, a URL for every year and every month, printable version, individual holiday pages. | No calendario laboral by comunidad from the year pages, no city pages, no school calendar, no puentes and no FAQ. Regional holidays appear as unlinked text. |
| **calendarioslaborales.com** (`/calendario-laboral-<region>-2026.htm`) | Clean slug per comunidad and **per provincia**, hub pages, an HTML sitemap. | 2027 pages not visible yet. `.htm` URLs with the year baked into each slug, so they churn every year. "madrid" and "comunidad-de-madrid" compete with each other. Thin copy, repeated "Ver calendario" anchors, a map that is only an image. No school calendar. |
| **diainternacionalde.com** (`/calendario-laboral/<region>/2027`) | Covers every comunidad, and municipal pages exist. | Its own notes say several regions are incomplete, the counts disagree with the BOE, and the pages are full of ads. |
| **calendar.center** (`/es/vacaciones/navidad/2026-2027/`) | A clean URL for each break type and course, a countdown, a "días lectivos" counter. | Despite "todas las comunidades" in the title it shows **one** national range, cites a third-party site instead of the BOE or the boletines, and has no comunidad pages. |
| **News** (Time Out, El Español, eldiario.es, ESdiario, Diario de León, El Debate) | Freshness, authority, Top Stories, fast pickup of plenos (local holidays). | Long articles that bury the dates, figures that conflict with each other (we saw 4 vs 5 puentes, 9 vs 12 holidays), no tool, outdated after a week. |
| **HR SaaS** (PayFit, Jibble, Coverflex) | Domain authority, evergreen guides. | Jibble had a wrong weekday (25 Dec 2027 is a Saturday). Generic content, no comunidad or city depth. |
| **Official** (BOE, gva, gencat, jcyl, BOCM, Xunta, ayuntamientos) | Authority. The source of truth for "boe", "gva" and "oficial" queries. | PDFs, no puentes, no planner, nothing that compares comunidades, poor on mobile. We beat them on usability and should link to them generously, since that link is our trust signal. |
| **cuandoenelmundo.com** | A PDF generator for each comunidad. | We saw a wrong Easter date for 2027 on it. |

## Catalan, Galician and Basque (checked 2026-10-26)

Method: Google autocomplete with `hl=ca` / `hl=gl` / `hl=eu` (`gl=es`), plus the titles and headings of the pages that rank, read directly. The same location bias applies (Comunitat Valenciana).

### Catalan (`/ca/`): real demand, the strongest of the three

Autocomplete returns full lists for every head term, so Catalan is a real search language here, not a courtesy.

| Cluster | Real phrasing (autocomplete / press) | Priority |
|---|---|---|
| Labour calendar | `calendari laboral 2027` · `… catalunya` · `… catalunya gencat` · `… comunitat valenciana` · `… barcelona` · `… girona` / `sabadell` / `mataro` / `vic` · `… catalunya per imprimir` · `calendari laboral valencia 2027` | P1 |
| Holidays | `festius 2027` · `festius 2027 catalunya` · `… barcelona` / `terrassa` / `lleida` / `girona` / `vic` · `festius 2027 balears` · `festius 2027 caib` · `dies festius 2027 catalunya` · `calendari dies festius catalunya 2027` · `festius comunitat valenciana 2027` · `festius desembre 2026` | P1 |
| Local holidays | `festes locals 2027` · `festes locals barcelona 2027` · `… catalunya` / `manresa` / `girona` / `vic` / `sabadell` / `tortosa` / `lleida` / `amposta` | P1 (city pages) |
| Puentes | `ponts 2027` **collides with French** ("ponts 2027 france", "ponts mai 2027", "education nationale"). Use `ponts festius 2027` and `ponts i festius 2027`, never `ponts 2027` alone in a title. | P2 |
| School | `calendari escolar 2026-2027` · `… catalunya` · `… barcelona` / `sabadell` / `terrassa` / `girona` · `… caib` · `… illes balears` · `calendari escolar 26 27 gva` · `calendari escolar 26-27 catalunya` · `… gencat` · `calendari escolar castello de la plana` | P1 |
| Semana Santa | `setmana santa 2027` · `… catalunya` · `… dates` · `… calendari escolar` · `… festius` · `… illes balears` | P2 |
| Working days | `dies laborables 2027` (only the bare term, so low) | P3 |
| Generic | `calendari 2027` · `… catalunya` · `… per imprimir` · `… amb festius` · `… festius catalunya` · `calendari 2027 excel` | P2 |

**Who ranks / phrasing examples:**
- 3cat (`3cat.cat/3catinfo/calendari-laboral/`; "Calendari escolar 2026-2027: vacances i festius d'aquest curs i dels dos següents").
- beteve ("Calendari escolar 2026-27 Catalunya: dates, festius i vacances").
- democrata.es/ca/ ("Calendari laboral 2027: tots els festius, ponts i dies lliures per comunitats autònomes"). This is the only multilingual competitor (es/ca/eu).
- ara.cat.
- Official: gencat (Ordre EMT/52/2026), CAIB/BOIB, GVA/DOGV, and **CIDO of the Diputació de Barcelona** (`cido.diba.cat/calendaris-oficials`), the official compilation of Catalan festes locals. Use it as the source of truth for Catalan city data.
- Valencian users write `comunitat valenciana` and `gva` (both Spanish and Catalan autocomplete). No suggestion uses "País Valencià".

### Galician (`/gl/`): mostly overlaps with Spanish

With `hl=gl`, autocomplete still returns Spanish-form queries: `festivos 2027 galicia`, `calendario laboral 2027 galicia`, `… xunta de galicia`, `calendario escolar galicia 26 27`, `… pdf`, `festivos galicia 2027 dog`, `festivos 2027 vigo`. The Galician-only forms with demand are `festivos locais galicia 2027` and `festivos locais santiago de compostela 2027`. `galiza` returns **no** suggestions. `pontes 2027` returns Portuguese results ("feriados e pontes 2027 portugal").

Several key terms are spelled the same in both languages ("calendario laboral", "calendario escolar", "festivos", "Semana Santa"), so the Galician pages compete with our own Spanish pages for the same words. hreflang (plan §13) decides which one Google shows, based on the user's language settings.

**Who ranks / phrasing examples:**
- Blog Mundo R ("Todos os festivos en Galicia 2027: calendario laboral"; H2s "Pontes en Galicia 2027", "Festivos locais en Galicia 2027", "Entroido en Galicia 2027").
- xunta.gal press notes in Galician ("A Xunta de Galicia aproba o calendario laboral para 2027 co 19 de marzo e o 17 de maio como festivos propios").
- DOG.

Priority: P2 for Galicia pages (Galicia + its cities + escolar Galicia), P3 for the other regions in Galician. Add **Entroido 2027** (school days off at Carnival, a Galician-specific query) to the Galician school page.

### Basque (`/eu/`): low volume, people mostly search in Spanish

| Real phrasing | Note |
|---|---|
| `lan egutegia 2027` · `2027ko lan egutegia` · `lan egutegia 2027 euskadi` · `gipuzkoako lan egutegia 2026` | Users type "lan egutegia" with a space. The press and Euskaltzaindia write `lan-egutegia`. Use the hyphen in titles and the spaced form once in the body. |
| `egutegia 2027` · `egutegia 2027 euskadi` · `2027 ko egutegia` | |
| `eskola egutegia 26 27` · `eskola egutegia 2026 27` · `eskola egutegia 2026` | School calendar. |
| `jaiegunak euskadi` · `2027 ko jai egunak` | Holidays. `jaiegunak 2027` alone returns nothing. |
| `zubiak 2027` | Nothing in autocomplete. Keep it as an H2, not a title lead. |

Basque-territory users mostly search **in Spanish** with the territory name: `calendario laboral 2027 bizkaia` (+ `bob`, `pdf`, `excel`, `gobierno vasco`), `calendario laboral 2027 gipuzkoa` (+ `bog`, `irun`), `calendario laboral euskadi 2027 bopv`, `calendario laboral navarra 2027 bon`. That means **Bizkaia/Gipuzkoa/Araba city pages in Spanish** matter more than the Basque translation.

**Who ranks / phrasing examples:**
- blog.euskaltel.com/eu/ ("Euskadiko jaiegun guztiak: 2027ko lan-egutegia"; H2s "Euskadiko 2027ko zubiak", "2027ko Euskadiko tokiko jaiak: Bizkaian, Gipuzkoan eta Araban", "Bizkaiko 2027ko jaiegunak"; also "nafarroako jaiegunak 2027" and "nafarroako eskola egutegia").
- democrata.es/eu/ ("2027ko lan-egutegia: autonomia-erkidegoen arabera festibo guztiak, zubiak eta opor-egunak").
- euskadi.eus ("2026-2027 ikasturteko eskola-egutegiaren ebazpena").
- datos.gob.es ("2026eko Euskadiko lan egutegia").

Priority: P2 for Euskadi + Nafarroa pages in Basque, P3 for the rest.

### Region names: what searchers and official sources use

| Comunidad | Catalan | Galician | Basque | Evidence |
|---|---|---|---|---|
| Comunitat Valenciana | **Comunitat Valenciana** (not "País Valencià") | Comunidade Valenciana | Valentziako Erkidegoa | Catalan autocomplete: `calendari laboral 2027 comunitat valenciana`, `… gva`. Statutory name. |
| Galicia | Galícia | **Galicia** (not "Galiza") | Galizia | `galiza` gets zero suggestions. Xunta and Mundo R write "Galicia". |
| País Vasco | País Basc | País Vasco | **Euskadi** (or Euskal Autonomia Erkidegoa). **Not "Euskal Herria"**, which names the seven Basque territories including Navarra and Iparralde, so it is factually wrong for this comunidad | `lan egutegia 2027 euskadi`; Euskaltel and euskadi.eus write "Euskadi". |
| Navarra | Navarra | Navarra | **Nafarroa** ✓ | Euskaltel: "Nafarroako jaiegunak 2027". |
| Baleares | **Illes Balears** ✓ | Illas Baleares | Balear Uharteak | `festius 2027 balears`, `caib`. |
| Cataluña | **Catalunya** ✓ | Cataluña | Katalunia | |

Recommendation sent to the i18n data: use the official or statutory names in titles and H1s (Comunitat Valenciana, Galicia, Euskadi). Alternative names can appear once in body text if wanted. A wrong region name in a title costs both clicks and trust.

**Takeaways:**
1. Precision, with a source cited on every page, is a real differentiator. Competitors visibly contradict each other.
2. City-level labour calendars and comunidad-level school calendars are where demand meets weak supply.
3. The `pdf`, `excel` and `para imprimir` modifiers call for a print view or download on every page.
4. Year-agnostic URLs (`/madrid/`, `/calendario-escolar/madrid/`) gain authority year after year. Competitors that put the year in the slug start from zero every year.
