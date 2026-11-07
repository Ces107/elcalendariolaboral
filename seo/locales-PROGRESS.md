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
