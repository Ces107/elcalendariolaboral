# Local holidays 2027: research progress

Data: `data/locales-2027.json`. Rules: dates only from a bulletin (`boletin`) or the council's own publication (`ayuntamiento`); press is a pointer in `note`. Exactly 2 dates per city (`test_data.py`); a parish/valley with its own day is explained in `note` (Siero/Lugones, Mieres/Turón). Canarias cities need their island in `pages.ISLAND_CITIES`.

Multi-column bulletin PDFs: `pdftotext -layout` shifts columns by a row (Lugo city had Mondoñedo's San Lucas until 2026-10-26). Read tables with PyMuPDF (`page.find_tables()`) or word coordinates on the same printed line.

## Regional lists already used (all municipalities of the territory)

| Region | Source | Status |
|---|---|---|
| Murcia | BORM 171, 27-07-2026 (all 45) | done: capital + 18 more |
| Canarias | BOC 168, 21-08-2026 (all 88) | done: 2 capitals + 29 more (islands mapped) |
| Asturias | BOPA 110, 10-06-2026 (all 78) | done: Oviedo, Gijón + 5 |
| País Vasco | BOTHA 116 (Álava), BOB 181 (Bizkaia), BOG 187 (Gipuzkoa) | done: 3 capitals + 27 more |
| Galicia | BOP A Coruña 187, BOP Lugo 221, BOP Ourense 197, BOPPO 192 | done: 4 capitals + Vigo + 25 more |
| Castilla y León | BOPs Ávila, León, Palencia, Salamanca, Segovia, Soria, Zamora | capitals done + 3 Salamanca towns; Burgos, Valladolid provinces pending |
| Castilla-La Mancha | BOP Toledo 203, BOP Ciudad Real 202 | done: 2 capitals + 7; Albacete, Cuenca, Guadalajara pending |
| La Rioja | BOR 160, 21-08-2026 | Logroño |
| Navarra | BON 103 (3 Dec for all) | Pamplona's own day pending (proposals due 15-11-2026) |

## Pending regional compilations (re-check weekly Nov–Jan)

- Andalucía: BOJA order of the Consejería de Empleo (not out on 2026-10-26).
- Cataluña: DOGC order (2026's was EMT/208/2025, 17-12-2025); open data b4eh-r8up.
- Comunidad de Madrid: BOCM resolution of the DG de Trabajo (2026's came out 12-12-2025).
- Comunitat Valenciana: DOGV resolution (usually Nov–Dec).
- Aragón: BOA resolution (proposals due 15-10-2026).
- Extremadura: DOE resolution. Cantabria: BOC resolution. Baleares: each council in BOIB.
- Ceuta (BOCCE) and Melilla (BOME, full Consejo de Gobierno agreement of 24-09-2026).

## Madrid municipalities to re-check soon (from the 2026-10-26 sweep)

Aranjuez (pleno 28-10), Collado Villalba (pleno 29-10), Rivas (pleno 29-10), San Sebastián de los Reyes (pleno 15-10, acta not posted), Pinto and Tres Cantos (October pleno), Alcobendas, Alcalá, Getafe (press only).

## Log

- 2026-10-26: 76 → 202 municipalities; official 42 → 155. Batches: bulletins (101), Lugo fix + 10 towns, Madrid sweep (2 official, 13 pending added). Research for Andalucía, Cataluña, C. Valenciana and Aragón/Cantabria/CLM/CyL/Extremadura/Navarra/Baleares/Ceuta/Melilla in progress.
- 2026-11-07: new file `data/locales-2027-all.json`, keyed by INE code (diccionario 1-1-2026, 8,132 municipalities): **4,264 municipalities, 4,250 from a bulletin + 14 from a council's own publication**, 41 sources. It ingests every row of each published list, not only the big towns. New since 26-10: BOJA 210 (Andalucía), DOE 207 (Extremadura), BOIB 122 (Baleares: the regional resolution with all 67 municipalities), BOCCE 6666 (Ceuta), BOME Extra 43 (Melilla), BOP Burgos 145 and BOP Valladolid 129 (both from July/August, previously missed), and the Aranjuez council news. Rebuild: `python -I data/tools/locales2027/parse_<source>.py <workdir>` for each source, then `python -I data/tools/locales2027/merge.py <workdir> --write` (downloads live in the workdir, outside the repo). Each parsed source records its spot-check (≥5 random rows re-read against the PDF independently of the parser) in its `spotcheck` field.

### Coverage of `locales-2027-all.json` (2026-11-07)

| Region | Municipalities (INE) | In file | Status | Source(s) | Not covered |
|---|---|---|---|---|---|
| Andalucía | 785 | 766 | boletin | BOJA 210, 29-10-2026 | 19 not in the annex (Arcos de la Frontera, Constantina, Marinaleda, Minas de Riotinto…) |
| Aragón | 731 | 0 | — | — | BOA list expected mid/late Nov 2026 (2026's: BOA 20-11-2025) |
| Asturias | 78 | 78 | boletin | BOPA 110, 10-06-2026 | — |
| Baleares | 67 | 67 | boletin | BOIB 122, 29-09-2026 | — |
| Canarias | 88 | 88 | boletin | BOC 168, 21-08-2026 | — (island holiday not in this file) |
| Cantabria | 102 | 0 | — | — | BOC list expected Dec 2026 |
| Castilla-La Mancha | 919 | 305 | boletin | BOP Toledo 203 (22-10), BOP Ciudad Real 202 (20-10) | Toledo: Illán de Vacas not listed. Albacete (no list up to BOP 129, 6-11-2026), Cuenca and Guadalajara (2026's: BOP 24-11-2025) pending |
| Castilla y León | 2,248 | 1,782 | 1,781 boletin + 1 ayuntamiento | BOPs Ávila 129, Burgos 145, León 144, Palencia 83, Salamanca 129, Segovia 80, Soria 81, Valladolid 129, Zamora 88 | 467 municipalities the bulletins do not list or list as "no comunicado" (incl. Burgos city, Astorga, Benavente, Toro, Ledesma, Olmedo); Valladolid city keeps its sede entry. Segovia's 9 "*" towns (2026 days repeated) left out |
| Cataluña | 947 | 5 | ayuntamiento | site entries (Barcelona, L'Hospitalet, Badalona, Reus, Mataró) | DOGC order / open data b4eh-r8up have no 2027 rows; expected mid/late Dec 2026 |
| Ceuta | 1 | 1 | boletin | BOCCE 6666, 03-11-2026 | — |
| C. Valenciana | 542 | 1 | ayuntamiento | València (site entry) | DOGV resolution expected mid-Nov 2026 (2026's: DOGV 14-11-2025) |
| Extremadura | 388 | 388 | boletin | DOE 207, 27-10-2026 | 56 pedanías/ELMs printed as separate rows are not attached to a municipality |
| Galicia | 313 | 313 | boletin | BOP A Coruña 187, Lugo 221, Ourense 197, BOPPO 192 | — |
| La Rioja | 174 | 165 | boletin | BOR 160, 21-08-2026 | 9 not named ("las dos fiestas tradicionales", no dates): Cárdenas, Cellorigo, Foncea, Lagunilla del Jubera, Pazuengos, Pedroso, Robres del Castillo, Santurde de Rioja, Santurdejo |
| Madrid | 179 | 7 | ayuntamiento | 6 site entries + Aranjuez (news 29-10-2026) | BOCM expected mid-Dec 2026 (2026's: BOCM 12-12-2025). Collado Villalba page doubtful (prints "jueves 23 de julio de 2027", which is a Friday) |
| Melilla | 1 | 1 | boletin | BOME Extra 43, 30-09-2026 | — |
| Murcia | 45 | 45 | boletin | BORM 171, 27-07-2026 | — |
| Navarra | 272 | 0 | — | BON 103 is regional only | Resolution of the DG de Economía Social y Trabajo with every municipality's day expected late Nov–Dec 2026 (2026's: Res. 682/2025, 17-11-2025) |
| País Vasco | 252 | 252 | boletin | BOTHA 116, BOB 181, BOG 187 | — |
| **Total** | **8,132** | **4,264** | | | |

Format notes for the build: `holidays[].name` is null when the bulletin prints only the date (most BOPs); names are carried over from `locales-2027.json` where its date matches. Not every row has 2 dates: territory days (Álava 28 Apr, Bizkaia/Gipuzkoa 31 Jul, a Saturday in 2027) are included; split municipalities (Ayala, Pasaia, Ezkio-Itsaso, Bidania-Goiatz, Cervera del Río Alhama, 258 rows in all) carry their village days in `localities`; Asturias concejos with parish days (Siero, Mieres, Llanes, Piloña, Salas, Tineo, Valdés, San Martín del Rey Aurelio) list all 3–6 dates, as printed; 25 rows have a single date (e.g. Labastida, whose own day is printed without its day number) and 6 have only village days. Canarias entries still need their island for `pages.ISLAND_CITIES`.

### 2026-11-17 refresh

**4,264 → 4,799 municipalities** (boletin 4,250 → 4,762; ayuntamiento 14 → 37), 41 → 61 sources. No existing entry changed its dates; the only edits to existing rows are 68 Segovia festivity names cleaned (see anomalies).

New in a bulletin (all rows of each list):
- **Comunitat Valenciana changed procedure for 2027**: no single DOGV resolution; each Dirección Territorial de Vivienda, Empleo, Juventud e Igualdad publishes its province's list in the BOP. Alicante: BOP Alicante 210, 04-11-2026, edicto 8352 (140 of 141; Muro de Alcoy "SIN DETERMINAR") → `parse_bop-alicante-210.py`. Castellón: BOP Castellón 136, 10-11-2026, anuncio 04772-2026 (135 of 135) → `parse_bop-castellon-136.py`. Shared prose parser `cv_util.py` (dates, names, check of the weekday printed next to each date). Misprints are kept as published with a note, never corrected: Agost (second day printed without day number: only 3 Mar), Tàrbena ("9 de agosto, lunes; 9 de agosto, martes": only 9 Aug), El Ràfol d'Almúnia ("143de agosto": only 12 Aug), Callosa de Segura ("5 de abril de 2026"), wrong printed weekdays for Benejúzar, Benissa, Hondón de las Nieves, La Vall d'Alcalà (Alicante) and Aín (Castellón). Dénia carries its EATIMs La Xara and Jesús Pobre in `localities`. Valencia province: not in BOP Valencia (all issues 28-10 to 17-11 scanned) nor DOGV (scanned via the DOGV API `dogv-portal/dogv?date=YYYY-MM-DD&lang=es`, 15-09 to 17-11).
- **Cuenca**: BOP Cuenca 130, 13-11-2026, anuncio 2719 (237 of 238; Pinarejo printed with 2026 dates, left out; 4 EATIMs left out) → `parse_bop-cuenca-130.py` (same table rules as 2026; pedanías in `localities`, 4 municipalities only per núcleo).

Council agreements (status `ayuntamiento`, one source each, `parse_sweep-2026-11-17.py`, every date re-read by a pattern from the downloaded council document and its printed weekday checked): Zaragoza (acta Pleno 30-09-2026), Alcalá de Henares, Rivas-Vaciamadrid, San Sebastián de los Reyes (acta Pleno 15-10-2026), Guadalajara, Burgos (Junta de Gobierno; it missed the Oficina Territorial's 30-06 deadline, hence absent from BOP Burgos 145), Torrelavega (council note prints "miércoles 16 de septiembre": date kept, note added), Burjassot (certificate of the Pleno of 31-03-2026), and 15 Catalan councils: Sabadell, Lleida (+ Raimat, Sucs), Girona, Sant Cugat (+ Valldoreix), Cornellà, Sant Boi, Rubí, Manresa, Vilanova i la Geltrú, Granollers, El Prat, Esplugues, Badia del Vallès, Sant Adrià de Besòs, Blanes. Left out (not official enough): Santander (committee proposal only, Pleno result not found), Getafe (only the council's X post: 6 and 17 May), Alcobendas (official pages 403 to scripts; search extracts say 25 Jan + 15 May), Viladecans (Ple agenda only), Figueres (civic-centre programme), Vic (dates only in an image), Terrassa/Arganda/Móstoles (press only).

`locales-2027.json`: Cuenca (bulletin) and Lleida (council page) updated by hand because their entries carry `localities`, which `muni.overlay_locales` does not lay over the rich city page; both have `"new": true` (no ads, like the overlay). The other 11 capitals/cities now covered (Zaragoza, Guadalajara, Burgos, Girona, Alicante, Castellón, Elche, Sabadell, Alcalá, SS de los Reyes, Rivas) are laid over automatically. **The 13 city pages need a build**: `test_data.py` fails only on them (missing `data-locals` and 13 widget embeds); run with those 13 skipped it passes everything else. `seo/check_data.py` 0 errors, `data/check_i18n.py` ok.

Still pending on 2026-11-17 (checked):
| Territory | Checked | Usually published |
|---|---|---|
| Valencia province | BOP Valencia to 17-11 (n. 221), DOGV to 17-11 | Alicante/Castellón came 04-11/10-11: imminent |
| Aragón | aragon.es calendar page lists no 2027 locals; boa.aragon.es unreachable from this network (connection reset, also in Chrome) | 2026's: BOA 20-11-2025 |
| Navarra | BON summaries 205–229 (14-10 to 17-11) | 2026's: BON 241, 02-12-2025 |
| Albacete | BOP Albacete full issues 125–133 | 2026's: BOP 138, 26-11-2025 |
| Guadalajara province | BOP Guadalajara daily lists 26-10 to 17-11 | 2026's: BOP 225, 24-11-2025 |
| Madrid | BOCM summaries 257–276 (26-10 to 17-11) | 2026's: BOCM 12-12-2025 |
| Cataluña | open data b4eh-r8up has no 2027 rows | 2026's: DOGC 17-12-2025 |
| Cantabria | no 2027 local list found | 2026's: BOC 11-12-2025 |

Network notes: dogv.gva.es resolves to a private IP on this network; use `curl --resolve dogv.gva.es:443:195.77.20.106`. BOP Valencia and BOP Castellón are JSF apps (read with the browser: day-by-day calendar for Valencia, bulletin list for Castellón; the Castellón anuncio PDF is `bop.dipcas.es/PortalBOP/api/descargarAnuncio/es/<id>`). BOP Alicante PDFs: `dip-alicante.es/bop2/pdftotal/YYYY/MM/DD_<issue>/YYYY_<edicto 6 digits>.pdf`. BOP Cuenca search: `dipucuenca.es/boletin1` Liferay form (`p_r_p_searchText`, `p_r_p_dateFrom/To`).

Rebuild: copy the previous workdir's `parsed/*.json` + `dl/ine/dic26.xlsx`, run `parse_bop-alicante-210.py`, `parse_bop-castellon-136.py`, `parse_bop-cuenca-130.py`, `parse_bop-segovia-80.py`, `parse_sweep-2026-11-17.py`, then `merge.py <W> --write` (merge reproduced the 2026-11-07 file byte for byte before the new sources were added).

#### Data anomalies checked (request from the analysis agent)
1. **19 Sunday local days**: all re-read in the bulletin PDFs and printed exactly so (BOJA: Ohanes, Alamedilla ×2, Pórtugos ×2, Benatae, Fernán-Núñez, Pujerra; DOE: Acedera, Castañar de Ibor, Guijo de Coria 26 Dec, Morcillo, Piedras Albas; BOIB: Formentera 25 Jul; BOP Lugo: Pedrafita do Cebreiro "13/06/2027 San Antón"; BOP Segovia: Navares de las Cuevas; BOP Zamora: Fuentesecas, Malva, Santa María de Valverde). Not parse errors; nothing changed.
2. **Local days equal to a regional/national holiday** (besides Mon 16 Aug): Santa Olalla de Bureba 12 Oct (BOP Burgos prints 12/10/2027), San Esteban de Nogales 23 Apr San Jorge (BOP León), Cangas 19 Mar "Venres das Dores" (BOPPO), Zaldibia 7 Oct (BOG), Fresno de Cantespino 6 Dec San Nicolás de Bari (BOP Segovia): all as printed. The name residue "Documento" was a real parser bug: the vertical signature footer in BOP Segovia's right margin (x ≥ 545) was read into the festivity column. Fixed in `parse_bop-segovia-80.py`; it had polluted 68 names (Página, firmado, Cód, Validación, esPublico, Gestiona, page numbers…), now clean; no date changed. A scan of all names in the file for footer residue finds nothing else.
3. **Castilla y León gaps**: for every municipality missing from Ávila, Burgos, León, Palencia, Salamanca, Valladolid and Zamora, its name was searched in the full bulletin text (León and Burgos glyph-decoded; check validated: 164/164 and 181/182 listed rows found by the same search). No missed municipality: Palencia (35) and Valladolid (29) missing ones are printed as "no comunicado"; every other hit was a substring of another name (Sotillo de la Adrada, Doñinos de Ledesma, Cubo de Benavente…) or page furniture. The gaps are real absences; complementary BOP lists for 2027 were not searched yet (next step).
