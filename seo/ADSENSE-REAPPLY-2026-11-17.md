# AdSense re-review plan, 17 Nov 2026 ("Contenido de poco valor")

Read-only pass: web research plus a live fetch of 48 pages of https://elcalendariolaboral.es on 17 Nov 2026
(script and raw HTML in the session scratchpad). This builds on `RESEARCH-2026-11.md`, `AUDIT-2026-11.md` and
`ADSENSE-READINESS-2026-11-10.md` and does not repeat their Google-guidance research.

## 0. Verdict in five lines

1. **Don't request the review now.** Since the flag (on or before 6 Nov, `seo/ads.md`), the site has moved further
   from what the flag asked for. It gained about 4,096 data-built municipality pages and 50 province pages (7 Nov,
   `c6add0af8f`), 165 calculator pages (12 Nov), half of them off-topic and 51 in English, a 47-product shop, and
   self-promo blocks on every page. The sitemap went from 305 URLs (6 Nov) to **4,724**.
2. A reviewer today sees a holiday-calendar site that also sells Etsy templates, promotes a puzzle game, and hosts
   beer, jam, concrete, KDP-royalty and Etsy-listing calculators, some in US units. That reads as AdSense farming
   and owner-business funnelling, whatever the quality of each page.
3. The core (comunidades, cities, guides, on-topic tools) is solid. Its text is computed from official data, every
   page cites its source, the pages load fast, and the trust pages exist.
4. Fix the site in three steps: **cut** the off-topic and English tools and the shop/house promos, **shrink** the
   programmatic footprint, and **add** 3 to 5 dated editorial analyses with original findings.
5. Request the review about 10 to 14 days after those changes are live and Search Console shows them. Target
   **1 to 8 Dec 2026**. The reasoning is in section 5.

## 1. What the research says (2025-2026, anecdotes marked)

Official sources (Google):
- A site-level enforcement needs "a review for each site", and serving resumes only after it. The button "will be
  inactive if your site has been reviewed and rejected several times recently". Google publishes no fixed wait and
  no penalty beyond that. https://support.google.com/adsense/answer/7003627
- Status "Ready" holds only while you "follow the AdSense Program policies at all times". An approved site can
  revert, which matches our case. https://support.google.com/adsense/answer/12170222
- The fix steps for low-value content (already in RESEARCH §6) are: substantial and original content, no
  doorway-like similar pages ("expand or merge"), content organised by topic, nothing off-theme.
  https://support.google.com/adsense/answer/10015918
- The not-approved page, Spanish version, lists affiliate programmes without added value and ad code on
  auto-generated pages without original content as causes. https://support.google.com/adsense/answer/81904?hl=es

Publisher reports (anecdotes, n=1 each, none with a verified approval after the change):
- A tool site with 65+ tools rejected for low value, although every tool page had explanations and FAQs. The owner
  blames site age, traffic and Google's distrust of "spammy utility sites". (Dec 2025)
  https://dev.to/bdubs/i-applied-for-adsense-and-got-rejected-for-low-value-content-hog
- A downloader tool site: "a tool on its own is not content". The owner added three guides of about 800 words and
  named the operator on About. Outcome not reported.
  https://dev.to/mobeenahmedgondal/what-adsenses-low-value-content-rejection-taught-me-about-my-tool-site-5eg3
- A site with 6,346 templated posts flagged low value. The owner set them to noindex, removed their ads, and cut the
  sitemap from 6,924 to 25 URLs. He holds that "AdSense judges the whole site, not just the pages that show ads ...
  Pages without ads still count" (his reading, not a cited Google statement). Outcome not yet reported (Oct 2026).
  https://sandeepkumarchaudhary.com/blog/adsense-low-value-content-rejection-what-i-changed
- Developers noindexing templated city or location pages for AdSense. Outcomes unknown.
  https://github.com/lafronzt/nyc-affordability/pull/114 , https://github.com/rahanshah4-del/nexora-website/pull/85
- ForoBeta (Spanish publishers, Dec 2023):
  - A site was rejected because of empty sections linked from the menu, and approved once they were hidden ("si tu
    web tiene algún fallo ... NO SE NOTE").
  - Approvals happened with 5 to 10 URLs and refusals with 100+, so there is no word-count or page-count rule.
  - A 2-month-old site with 200 organic visits a day was still refused.
  https://forobeta.com/temas/como-solucionaste-el-poco-valor-de-contenido-en-adsense.981859/
- Some Spanish blogs report approval on a resubmission with almost no changes. Treat that as noise; it is not a
  strategy for a "last chance". https://unazonageek.com/internet/blogging/adsense-contenido-de-poco-valor-como-solucionarlo/
- WebmasterWorld advice: don't ask for review while flagged pages remain; check the Policy center for the pages it
  lists first. https://www.webmasterworld.com/google_adsense/5001464.htm
- SEO-blog "guides" disagree with one another: 600 to 2,000 words, 15 to 50 posts, waits of 2 to 4 weeks, 15 to 30
  days or 3 to 6 months. None cites Google, so I discard them as rules.

What the evidence points to (hypothesis):
- Reviewers judge the **site as a whole**: its purpose, coherence and share of templated pages, not single pages.
- Tool-only and programmatic pages are the most-reported failure pattern. Topical focus, visible original writing
  and a site that "explains itself" are the repeated fixes.
- Age and traffic ("constant presence on the Web", "user interest" in our notice) seem to count, and only time and
  real visitors fix them.

## 2. Live audit (17 Nov 2026, 48 pages fetched)

Words are the words of 2+ letters in `<main>`, including the calendar grid on calendar pages. "1st promo" is the
number of words before the first ad or promo slot. "AdS" means the AdSense loader is on the page.

| Type (pages) | Words | KB | AdS | 1st promo | Judgement |
|---|---|---|---|---|---|
| Home | 768 | 60 | yes | 701 | Clear answer, a good "Lo que cambia en 2027", but a 4-item self-promo block straight after the calendar |
| Comunidades (andalucia, c-valenciana, castilla-y-leon) | 1,083–1,299 | 74–79 | yes, 2 units | 765–821 | Rich and useful; 5-gram Jaccard between two of them 0.40 (shared template) |
| Cities (madrid, valencia, avila, yecla) | 828–911 | 68–70 | yes, 2 units | 781–839 | Good: bridges table, effect of local days, source. Jaccard avila/yecla 0.34 |
| Municipalities (matanza, onzonilla, leza, arraia-maeztu) | 494–538 | 23–24 | no | 340–405 | Correct and sourced, but templated. Jaccard **0.45** (same province), **0.62** (Leza vs Arraia-Maeztu) |
| Provinces (alicante, albacete) | 416–542 | 23–30 | no | **92–94** | Alicante: "0 publicados · 141 pendientes", so a placeholder with the promo block as the 2nd item |
| Hubs /utilidades/, /en/tools/ | 539 / 196 | 106 / 45 | no | – | 15 categories, from "Cocina y bebidas" to "Vendedores online". /en/tools/ says "Source: BOE" |
| Off-topic tools (cerveza-casera, azucar-mermelada, salmuera, hormigon-mortero, regalias-kdp, revisar-anuncio-etsy, signo-zodiaco-chino) | 615–879 | 26–33 | **yes** | 397–732 | Well written (worked examples, formulas), but off-theme for a labour-calendar domain |
| English tools (brine, concrete) | 614–774 | 21–22 | **yes** | 459–477 | US units (ft, yd³, 94 lb bags) on a .es Spanish-calendar site: reads as CPC arbitrage |
| On-topic tools (finiquito, cuadrante-turnos, calculadora-vacaciones) | 574–708 | 26–57 | yes | 358–541 | Fit the site; keep |
| /shopping/ | 411 | 31 | no | – | 47 products, **42 Etsy and 8 Amazon links**, many marked "EN". A store page, not content |
| Guides: /puentes/, /festivos/, /festivos/reyes/, /semana-santa/, /como-se-fijan-los-festivos/ | 702–1,514 | 22–42 | yes, 1 unit | 353–1,810 | The best pages on the site; computed, specific, sourced. No byline or author |
| /festivos-locales/ | 1,699 | 110 | no | – | Useful directory |
| School: hub, madrid, navidad | 265–286 | 23–37 | 2 of 3 | – | Thin; the guard already removed ads from the hub |
| Trust: sobre, contacto, aviso-legal, privacidad, cookies | 89–281 | 12–14 | no | – | Present and honest (method, sources, corrections, funding). Contact is a gmail address `helping.info.agent@`; "El equipo" is anonymous; no named editor |
| gl/eu (gl/andalucia, eu/semana) | 592–612 | 26–64 | no | 472–768 | Indexable, in the sitemap; AdSense does not support either language (RESEARCH §6) |

Site-wide facts:
- **Sitemap: 4,724 indexable URLs.** Of these, about 4,096 (**~87 %**) are lean municipality pages, 165 are tools
  (114 es + 51 en) and 58 are province pages. **12 of the 50 Spanish province pages have 0 published
  municipalities**: Albacete, Alicante, Castellón, Cuenca, Girona, Guadalajara, Huesca, Lleida, Navarra, Cantabria,
  Teruel and Zaragoza. Pending city pages (Zaragoza, Alicante, Pamplona and others) are correctly noindex.
- **Self-promo on every content page.** A "Nuestros productos" block shows the Amazon agenda, the Etsy shop, the
  Teselo puzzle game and the 47-product shop: once on lean pages, twice on cities and comunidades. While AdSense is
  not serving, every ad slot shows these house promos (`b859e74de6`, `3cd1018be1`). Every page also links Amazon
  (1–3 links) and Etsy (1–2 links), and loads the 24 KB Teselo canvas ad script.
- **Tool hub mix: 118 entries.** On-topic (Trabajo y nómina, Fechas y calendario): 31. Borderline (Dinero, Vivienda,
  Trámites, Estudiantes, Texto): 19. **Off-topic: 68** (Coche 9, Vendedores online 11, Ocio 2, Campo/animales 11,
  Deporte 10, Bricolaje 12, Sol y luna 2, Cocina 11). "Vendedores online" (Etsy fees, Etsy listing checker, KDP
  royalties, KDP covers, SKU generator) are tools for the owner's own businesses.
- Navigation: the main nav (Comunidades, Festivos, Puentes, Vacaciones, Utilidades) reaches any comunidad, guide or
  city in at most 2 clicks. The municipality search is on the home page. The footer has about 45 links, including
  shop, Amazon, install app and 4 languages.
- Technical: a viewport meta on all 48 pages; no render-blocking `<script>` in `<head>` (AdSense async, app deferred);
  HTML 12–110 KB; robots.txt allows everything. **Nothing technical blocks approval.**

## 3. Ranked fixes: must do before requesting review

| # | Fix | Evidence | Effort |
|---|---|---|---|
| 1 | **Take the 68 off-topic Spanish tools and all 51 /en/tools/ pages off this domain.** Move them to a separate tools domain, or delete them with 301s to /utilidades/. Noindex alone is the weaker option: the pages stay crawlable, linked and visible to a reviewer. Keep the 31 on-topic tools plus the useful borderline ones (IRPF, intereses de demora, horario escolar, días lectivos). Rename the hub "Herramientas laborales". | 15-category hub; US-unit English pages with the AdSense loader; Google step "nothing off-theme" / "organised by topic" | 2–4 h |
| 2 | **Remove all self-promo during the review.** Drop the "Nuestros productos" block, the Teselo game ad and script, the Etsy/Amazon footer links and the house ads in ad slots. Take /shopping/ out of the nav, footer and sitemap (noindex it, or remove it). Keep one plain line on /sobre/ ("Cómo se paga"). | Promo is the 2nd item on province pages (after 92 words); 42 Etsy links on /shopping/; game promo on a calendar site; Google lists "affiliate programs without added value" | 1–2 h |
| 3 | **Noindex the 12 province pages with 0 published municipalities** until their bulletin appears, as already done for pending cities. Show the 2026 publication date and the 12 regional holidays so users still get an answer. | "0 publicados · 141 pendientes" on an indexable page = placeholder/"under construction" | 0.5 h |
| 4 | **Shrink the programmatic share.** Noindex lean municipality pages under ~5,000 inhabitants, or with only generic "Fiesta local" names. That keeps roughly 700 pages (estimate from the 10 Nov note), and the rest stay reachable for users. This is the **riskiest SEO trade-off** (long-tail traffic in the Dec–Jan peak): César decides. If he refuses, at least drop municipality pages from the main sitemap until approval. | ~87 % of indexable URLs are data-built; same-province overlap 0.45–0.62; Google step 3 "many similar pages: expand or merge" | 1–2 h |
| 5 | **Write 3–5 dated editorial analyses with original findings from our own dataset.** Possible topics: (a) "Los festivos locales más repetidos de 2027" (top dates, saints, how many towns share each); (b) "Festivos locales que caen en sábado o domingo en 2027": how many municipalities lose a weekday holiday (e.g. Matanza, 15 May, Saturday) and per province; (c) "Días laborables 2027 por provincia": median, min, max, which towns work most and least; (d) "Cuándo publica cada provincia sus festivos locales": 2025 vs 2026 bulletin dates and the pending list; (e) "Los mejores puentes de 2027 por comunidad y cuántas vacaciones cuestan". Each needs 800–1,500 words, a table or chart, a method box, "Publicado/Actualizado" dates and a byline (pseudonymous but consistent, e.g. "Redacción · Valencia", or a first name plus role). Put them under /analisis/, link them from the home and nav, and give them an ad slot. | Google's "original information, research or analysis"; this is the one thing competitors copying the BOE cannot match | 3–5 h each, 12–20 h total |
| 6 | **Make the home explain the site.** Above the fold: answer, search, then an "Análisis 2027" row (fix 5) and a three-line "what we do / sources / who" summary. Nav: Comunidades · Festivos · Puentes · Vacaciones · Escolar · Análisis · Herramientas. | Home today = answer + grid + promo block | 1–2 h |
| 7 | **Noindex the gl/eu pages** (about 48 in the sitemaps: comunidades, home, utilities, festivos-locales) and drop the Galego/Euskara footer links until they have reviewed text of their own. Catalan can stay. | Unsupported AdSense languages; template translations | 0.5 h |
| 8 | **Auto ads:** in the AdSense UI, turn off vignette and anchor, and exclude the calendar and puentes tables (as already proposed on 10 Nov). Limit manual units to the guides, comunidades and cities. | Readiness note §"For César" item 1; can't be verified from the HTML | 0.3 h (César) |
| 9 | Search Console: resubmit the sitemap index; request indexing of the home, /analisis/ and 3–4 analyses; check that the removed and noindexed URLs drop out (Pages report). | Google re-evaluates only what it has re-crawled | 0.5 h + waiting |

Must-do total: about 22–35 h of work. Fixes 1, 2, 3 and 7 are mostly config flags in the existing builders
(`herramientas/`, `shopping.py`, `promo/`, `munipages.py`, `pages.no_thin_ads`).

## 4. Nice to have (after the must-dos, or after approval)

- A domain contact address (e.g. `contacto@elcalendariolaboral.es` forwarding through the registrar) instead of
  `helping.info.agent@gmail.com`, and a named editor or role on /sobre/. 0.5–1 h.
- School pages under 300 words (hub, Madrid, Navidad): add 2–3 computed facts or merge them into the school hub.
  2 h.
- Real outside presence: send the widget to 10–20 town halls, gestorías and HR blogs (`seo/outreach-widget.md`),
  and run a social profile with the analyses. Each real link and mention helps "constant presence" (hypothesis).
  Ongoing.
- After approval, bring back the borderline tools one at a time, never the off-topic ones on this domain. Keep house
  promos to one slot per page, below the content.
- Fix `/en/tools/`'s "Source: BOE" footer if the English section survives anywhere.

## 5. When to request the review

Recommendation: **after the must-dos have been live for 10 to 14 days and Search Console confirms they were
crawled. Target window: 1–8 Dec 2026.** Don't request before 1 Dec, even if everything ships tomorrow.

Reasoning:
- Google re-reads what it has crawled. Noindex and removals take days to weeks to show. The new analyses need to be
  indexed to count as "presence". An early request risks a review of today's cached site, which is worse than the
  flagged one.
- The button locks only after "several" recent rejections (official), so one refusal is not fatal for Google.
  César's own rule (a second rejection means abandoning the site) is what makes waiting worth it.
- Seasonality helps. Many provincial bulletins publish local holidays from mid-November to December: Alicante's 2026
  dates came out on 14 Nov 2025, according to our own page. By early December, more of the 12 placeholder provinces
  will hold real data, and search interest in "calendario laboral 2027" will be rising, which is the only fix we
  have for "user interest".
- Cost of waiting: almost none. Ads are not serving now either way, and a review takes about 15 days. A request on
  1–8 Dec means a decision around 16–23 Dec, still inside the Dec–Jan peak. If César insists on an earlier date, the
  minimum is fixes 1, 2, 3 and 7 live for 7 days, plus at least 2 analyses.
- Before pressing the button: open the AdSense Policy center and check whether it lists specific URLs. If it does,
  they must be fixed or removed first (WebmasterWorld advice; Google's "resolved the policy issue on your site").

## 6. Limits: what is evidence and what is hypothesis

- I cannot see the AdSense account. That means the exact flag date and wording, any page-level list in the Policy
  center, the Auto ads settings and the reviewer's notes, which Google never shows. I also cannot see Search Console
  (indexed pages, impressions, traffic). Google never states the criteria for "poco valor" beyond the help pages
  cited.
- **Evidence:** the live HTML numbers above (17 Nov fetch: counts, word counts, links, robots tags, sitemaps), the
  git dates of the additions, and the quoted Google help pages.
- **Hypothesis:** that reviewers weigh the whole site, including pages without ads; that the off-topic tools, the
  English pages and the self-promo hurt; that shrinking the municipality footprint helps; that age, traffic and
  seasonality matter. These are consistent with Google's wording and with several anecdotes, but no source proves
  causation, and every publisher report cited is a single case without a confirmed approval after the change.
- Reddit could not be fetched by my tools, and US-based web search returned no `site:` results for the domain.
  Forum evidence is therefore thinner than intended. Per the "enough data" rule, I did not run a second scrape.
- I invented no statistics. All percentages are computed from our own sitemaps and pages.
