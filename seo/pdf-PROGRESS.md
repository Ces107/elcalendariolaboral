# PDF calendars + ad slots — progress

## Done
- fonts/ Public Sans static TTF (OFL), embedded as subsets
- pdfs.py: 410 PDFs (27 comunidades/zones x landscape+portrait+monthly, 155 cities x landscape+portrait, 19 school 2026-27), deterministic, max ~121 KB, 25 MB total
- pdfhub.py: /calendario-laboral-2027-pdf/ hub (sitemap, BreadcrumbList, footer link); PDF menu next to Imprimir/Excel (app.js swaps island/zone); PDF button on school pages
- build.ad(): ADS_ON=False + AD_SLOTS (cal, list, vac, hub), CSS reserves 300px, hidden in print
- test_pdf.py green; existing checks green

## Next
- seo/ads.md, Playwright 390/1440, push, curl live
