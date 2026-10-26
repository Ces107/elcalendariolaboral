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
