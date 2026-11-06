# Google guidance research, Nov 2026 (for the AdSense "Contenido de poco valor" flag)

One pass on 2026-11-06, ~24 fetches, mostly primary sources. "Unverified" means not re-checked in this pass, either
prior knowledge or a secondary source only. WebFetch summarises pages, so quotes are close but not always word-for-word.

## 1. Helpful, reliable, people-first content
- Self-assessment: does the page offer "original information, reporting, research, or analysis", a "substantial,
  complete" treatment, and value beyond other results? Would you bookmark it or share it?
  https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Warning signs listed there: content made mainly for search visits, mass production across many topics,
  summarising others without adding value, and **changing dates to look fresh with no substantive change**.
- Who/How/Why: clear authorship (bylines where expected, linked to author background; fake personas are deceptive);
  explain how content is produced; disclose automation where readers would wonder; the "why" must be helping people.
- AI/automation: allowed, but "generate many pages without adding value for users may violate" the spam policy;
  manually fact-check, and review titles, meta descriptions, structured data and alt text too. Rater guidelines
  4.6.5 (scaled content abuse) and 4.6.6 (little effort/originality/added value) apply.
  https://developers.google.com/search/docs/fundamentals/using-gen-ai-content

## 2. Spam policies
https://developers.google.com/search/docs/essentials/spam-policies
- **Scaled content abuse:** "when many pages are generated for the primary purpose of manipulating search rankings
  and not helping users ... creating large amounts of unoriginal content that provides little to no value to users,
  no matter how it's created." Examples: AI/other tools generating "many pages without adding value for users".
- **Doorway abuse:** pages "created to rank for specific, similar search queries". Examples: "multiple domain names
  or pages targeted at specific regions or cities that funnel users to one page" and "substantially similar pages that
  are closer to search results than a clearly defined, browseable hierarchy".
- Keyword stuffing includes "blocks of text that list cities and regions".
- **Thin affiliation** (copied merchant content plus affiliate links) and **site reputation abuse** (third-party
  content placed to ride the host's ranking; EEA enforcement changed Aug 2026) do not apply to us.
- Programmatic pages: no doc says "programmatic is OK". The test is purpose plus added value. The May 2026 AI guide adds:
  don't "create pages for every query or fan-out variation", which "violates ... scaled content abuse".
  https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Fix route the policy gives: exclude low-value scaled content from Search (noindex) or improve it.

## 3. Structured data status (changelog: https://developers.google.com/search/updates)
- **FAQPage: rich result DEAD for everyone.** It was restricted to gov/health sites in Aug 2023, has not shown in
  Search since **7 May 2026** (notice dated 8 May 2026), and the documentation was removed on 15 Jun 2026. Per
  secondary coverage, the Rich Results Test and Search Console reports went in Jun 2026 and API support in Aug 2026.
  The markup is still valid schema.org and harmless, but it earns no Google display. https://developers.google.com/search/docs/appearance/structured-data/faqpage
- **Dataset:** since 5 Nov 2025 it is used only by Dataset Search, not by Google Search features.
- **Deprecated 2025-2026:** Book actions, Course info, ClaimReview, Estimated salary, Learning video, Special
  announcement and Vehicle listing (announced Jun 2025, docs removed Sep 2025); Practice problem (Nov 2025, docs removed
  Jan 2026); FAQ (May 2026). Breadcrumbs became a **desktop-only** display (Jan 2025).
- **Event:** the June 2025 update added eligible and ineligible examples. Ineligible: non-event products, discounts,
  business hours, coupons, member-only events, events with minors on school premises, virtual-only events. Public
  holidays are not mentioned. A day off is not a ticketed or attendable event, so **don't mark holidays as Event**
  (an inference, but a safe one). https://developers.google.com/search/docs/appearance/structured-data/event
- BreadcrumbList, Organization (logo, sameAs) and WebSite (site name) are all still supported. **Unverified** this
  pass: Organization and site-name docs not re-fetched. Article `datePublished`/`dateModified` are still used for
  byline dates (see 4).
- Images: schema.org markup and `og:image` both feed the thumbnails in Search and Discover (Mar 2026).

## 4. Sitemaps, canonical, indexing, hreflang, titles, dates
- Sitemaps: `lastmod` is used only "if it's consistently and verifiably accurate". It should reflect the last
  *significant* change (main content, structured data, links), and a copyright-year change doesn't count.
  "Google ignores `<priority>` and `<changefreq>`." Limit: 50 MB / 50,000 URLs per file. List only the canonical URLs
  you want shown. https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- hreflang: the tags must be reciprocal (ignored otherwise); each page lists itself plus every alternate; use
  absolute URLs; codes are ISO 639-1 (`ca`, `gl`, `eu`, `es` or `es-ES`); `x-default` is for the fallback or
  selector. Localized pages "are only considered duplicates if the main content of the page remains untranslated".
  https://developers.google.com/search/docs/specialty/international/localized-versions
- noindex vs robots: noindex works only if the page is crawlable, so never also block it in robots.txt; canonical is
  a hint and noindex is a directive; don't canonicalise translations to the Spanish page (use hreflang). **Unverified**
  this pass (long-standing docs, not re-fetched).
- Title links and snippets: unique, descriptive `<title>`, no boilerplate repetition or keyword stuffing; Google
  rewrites titles that are weak. Meta descriptions should be page-specific. A new "read more" deep-links section was
  added in Apr 2026. https://developers.google.com/search/docs/appearance/title-link ,
  https://developers.google.com/search/docs/appearance/snippet (title rules **unverified**, not re-fetched)
- Byline dates: show a prominent, labelled visible date ("Actualizado ..."); put `datePublished`/`dateModified` on
  a CreativeWork type; the visible and markup values must match; "don't specify future dates, or the date of the action
  described on the page", so the date must be the page's publish/update date and never the holiday date.
  https://developers.google.com/search/docs/appearance/publication-dates

## 5. Page experience / Core Web Vitals
- Good, at the 75th percentile, mobile and desktop separately: **LCP <= 2.5 s, INP <= 200 ms, CLS <= 0.1**. Poor:
  LCP > 4 s, INP > 500 ms, CLS > 0.25 (the poor cut-offs for LCP and INP are **unverified**; they are shown only as
  images). https://web.dev/articles/vitals
- Ads and CLS: reserve the slot space (`min-height`, or `aspect-ratio` for responsive slots) at the largest or most
  likely size; **don't collapse** the space when no ad fills (show a placeholder); put injected slots lower in the
  page rather than near the top of the viewport. https://web.dev/articles/optimize-cls
- The AI guide repeats the point: separate the main content from other elements and keep latency low.

## 6. AdSense
- **Fix steps for low-value content** (the official page, which is what the "Contenido de poco valor" notice points to):
  https://support.google.com/adsense/answer/10015918
  1. Each page needs "enough unique content so that we can determine what your site is about", with "substantial
     value and originality" compared with similar sites.
  2. No pages with little or no content, no doorway pages, no cloaking.
  3. No duplicated content within a page or across pages. **Many similar pages: expand each one or merge them into
     one.** Replace long repeated blocks with a short summary and a link.
  4. Working navigation on every device, content organised by topic, no repetition across categories.
  5. No broken or misleading links, nothing off-theme, works in all browsers.
  6. Re-read the program policies, then **request review from the Sites page**. Review "usually takes a few days".
     Google publishes no minimum wait between requests. The community advice is to fix things properly first, because
     repeated quick resubmits just fail again (**unverified** folklore).
- Valuable inventory: no Google ads on screens "without publisher-content or with low-value content", "under
  construction", or "used for alerts, navigation or other behavioral purposes"; thank-you, exit and error pages are
  examples; "Don't place ads on automatically generated content without manual review or curation."
  https://support.google.com/publisherpolicies/answer/11112688
- Replicated content: no ads on copied, embedded or scraped content without added commentary or curation.
  https://support.google.com/publisherpolicies/answer/11190248 . Also not allowed: more ads than publisher content
  (whitespace, headers, footers and nav links don't count as content). https://support.google.com/publisherpolicies/answer/11169917
- Readiness: "unique content that's relevant to your visitors", clear navigation, an inviting layout, your own
  expertise added. https://support.google.com/adsense/answer/7299563 . Eligibility: "high-quality, original, and
  attract an audience". https://support.google.com/adsense/answer/9724
- **Languages:** the site's primary language must be supported. Spanish and Catalan are; **Galician and Basque are
  NOT on the list.** https://support.google.com/adsense/answer/9727
- About, contact and privacy pages: not stated as hard rules in the official pages fetched. Community and third-party
  sources treat them as de-facto required (a privacy policy plus the consent CMP is required in the EEA anyway).
- Community note (not official): "tool" or web-app sites often fail the automated review; text-rich sites pass.
  https://support.google.com/adsense/community-guide/241032356
- Auto ads plus manual units: they can be combined. The details were not re-fetched (**unverified**).

## 7. AI search (AI Overviews / AI Mode)
- "No additional requirements ... nor other special optimizations necessary." No special schema, no llms.txt (Jun 2026
  clarification). The page must be indexed and snippet-eligible. Controls: nosnippet, data-nosnippet, max-snippet,
  noindex; Google-Extended covers training and grounding in other Google systems.
  https://developers.google.com/search/docs/appearance/ai-features
- May 2026 guide: write non-commodity, first-hand, expert content "beyond common knowledge"; use clear headings and
  sections; ignore "chunking", llms.txt and inauthentic mentions; **don't make pages per query or fan-out variation**;
  check that the site is "included in Search generative AI features" in Search Console and use its Generative AI
  performance report. https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- GEO practice (reputable industry consensus, **not Google-official**): answer first in the opening lines, cite primary
  sources (BOE/DOGV/BOJA and so on), make the entity and author clear, keep a visible update date, use exact figures
  and tables.

## 8. E-E-A-T and trust signals
- Trust is the core of E-E-A-T. The helpful-content page asks for "clear sourcing, evidence of the expertise involved,
  background about the author or the site ... links to an author page or to a site's About page".
- AdSense reviewers use the same lens. Community guides say anonymous "we" sites score low on trust and that a named
  person with verifiable credentials helps (community source).
- "About this result" draws on what the web says about the site and on its own About page. **Unverified** this pass.

## Implications for elcalendariolaboral.es
1. **Treat the ~155 city pages as the prime doorway/scaled-content suspect.** Any city page that differs from the others
   only in name and dates gets either real unique content (fiesta origin and history, the official source such as the
   BOP/ayuntamiento acuerdo with a link, the date the city approved it, what changes vs 2026, where the holiday falls in
   the week, a bridge-day count) or noindex. Merge the weakest ones into their province or comunidad page, per
   AdSense step 3.
2. **The gl and eu translations block AdSense outright** (unsupported languages). Serve no ads on gl/eu pages, or keep
   them out of the site AdSense reviews. Machine-templated gl/eu/ca city pages should be noindex (and left out of the
   sitemap) until each has reviewed, curated text. Keep hreflang only among indexable equivalents.
3. Catalan is AdSense-eligible, but translated city pages still fall under the "automatically generated content without
   manual review or curation" rule. Index only the reviewed ca pages.
4. **No ads on tool, utility and navigation screens** (vacation planner UI, ICS/CSV/PDF download pages, widget embed
   pages, index or listing pages of links, thank-you or 404 pages). Ads go only on pages with substantial editorial text.
5. Before re-requesting review, make sure each indexable page has an answer-first intro, an explanation in our own words
   (labour-law context, how bridges and traslados work, comunidad-specific notes), and a cited official source per
   holiday. Don't just add more pages.
6. Cut repeated boilerplate: long legal or "how we work" blocks repeated on every page become one sentence and a link.
7. **FAQPage:** keep the visible FAQs only if they are genuinely useful. The JSON-LD is optional and gives no rich
   result (dead since May 2026). Never expect a snippet boost from it.
8. **Don't mark holidays as Event.** Use BreadcrumbList, Organization plus WebSite (site name and logo), and
   Article/WebPage with `dateModified`. Dataset markup only matters for Dataset Search (optional, for the CSV/ICS files).
9. Dates: a visible "Actualizado: <fecha>" matching `dateModified` and the sitemap `lastmod`. Bump them **only** when
   the holiday data or text really changes, never on a rebuild. Drop changefreq and priority.
10. Add or strengthen an **About** page (who maintains it, data method, sources such as the BOE resolution and each
    comunidad's decree, the error-report process), plus Contact, Privacy/cookies with a CMP, and a short methodology or
    corrections note. A named maintainer helps (keep it semi-anonymous per the brand rule, e.g. first name and role).
11. Reserve fixed-height ad slots (no collapse), keep CLS <= 0.1, keep the main content above the ads, and use Auto ads
    with ad load capped so ads never outweigh content.
12. Unique `<title>` and meta description per page that state the city and year plus something specific (e.g.
    "Festivos Elche 2027: 2 locales + 12 de la Comunitat"), not a pure template swap.
13. In Search Console, confirm that "Search generative AI features" inclusion is on, then watch the Generative AI
    performance report.
14. Re-request the AdSense review only after steps 1-6 are live and crawled (allow about 1-2 weeks so Google sees the
    noindex and the new content; this is our own judgment, Google states no wait). A review takes "a few days".
