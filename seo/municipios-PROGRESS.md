# Municipality catalogue + 2026 local holidays (reference): progress

Goal: a page per municipality (8,132) and per province. Where 2027 local holidays are not published yet, the page shows the 2026 ones as "referencia 2026, no oficial para 2027".

## Files

- `data/municipios.json`: INE catalogue (one municipality per line). Built by `data/tools/build_municipios.py <diccionarioYY.xlsx>`.
- `data/provincias.json`: 52 provinces / ciudades autónomas.
- `data/locales-2026.json`: 2026 local holidays, official bulletins only. Built by `data/tools/merge_locales_2026.py` from `data/tools/parts-2026/*.json` (one part per source, each made by a `data/tools/loc2026_*.py` parser).
- Downloads live outside the repo (scratch `muni-agent/` folder). Run parsers with `python -E -P` (no script-dir / cwd on sys.path; `-I` drops the user site-packages where openpyxl/PyMuPDF live).

## Catalogue decisions

- Source: INE `diccionario26.xlsx` (municipios a 1-1-2026): 8,132 municipalities.
- `name`: INE name with the article moved to the front ("Coruña, A" → "A Coruña"); bilingual "A/B" kept as published. `ine_name`: raw INE string.
- `name_es`: Spanish half of a bilingual name (heuristic + hand-reviewed `ES_PICK` for Álava/Navarra); `NAME_ES` overrides single-language names the site already shows in Spanish (València → Valencia). Single-language co-official names stay as they are (Lleida, Girona, A Coruña, Ourense); the Spanish exonym goes in `aliases`.
- `slug`: from `name_es`, ascii, elided articles glued ("Callosa d'en Sarrià" → `callosa-den-sarria`); existing slugs from `locales-2027.json` reused (all 202 matched). No duplicate (province, slug).
- Canarias municipalities carry `island` (slug of `data/2027.json` zones.canarias).
- Province names follow the site (`Illes Balears`, `Bizkaia`, `Gipuzkoa`, `Álava`, `A Coruña`, `Castellón`, `Alicante`).

## 2026 sources and coverage

| Region | Source (part id) | Status | Municipios |
|---|---|---|---|
| Cataluña | Generalitat open data b4eh-r8up = Ordre EMT/208/2025, DOGC 9565 (dogc-2026) | done | 909 / 947 (38 "proposta no formulada"; Sitges 1 date; núcleos in `nucleos`) |
| Madrid | BOCM 296 (12-12-2025) + modifications BOCM 309 and BOCM 6/2026 (bocm-2026) | done | 179 / 179 |
| C. Valenciana | DOGV 10238 (14-11-2025) + modifications 2026-1043, 2026-6733 (dogv-2026) | done | 539 / 542 (Sacañet, Vilanova d'Alcolea, Paiporta "sin determinar") |
| Andalucía | BOJA 197 (14-10-2025) + BOJA 247/2025, 32, 33, 79/2026 (boja-2026) | done | 774 / 785 (11 in no bulletin) |
| Extremadura | DOE 204 (23-10-2025) + 9 amending resolutions to DOE 141/2026 (doe-2026) | done | 388 / 388 (56 ELMs not mapped) |
| Galicia | DOG 210 (30-10-2025), one Xunta resolution for the 4 provinces (dog-2026) | done | 313 / 313 |
| Asturias | BOPA 114 (16-06-2025) (bopa-2026) | done | 78 / 78 (8 concejos with partial-territory days, in note) |
| Cantabria | BOC 238 (11-12-2025) (boc-cantabria-2026) | done | 102 / 102 |
| País Vasco | Open Data Euskadi calendario_laboral_2026.csv (euskadi-2026) | done | 252 / 252 (4 with 1 shared date + per-part days in note) |
| Murcia | BORM 163 (17-07-2025) (borm-2026) | done | 45 / 45 (Pliego: weekday misprint noted) |
| Canarias | BOC 165 (21-08-2025) (boc-canarias-2026) | done | 88 / 88 |
| Aragón | BOA 225 (20-11-2025) + complementary BOA 56 (23-3-2026) (boa-2026) | done | 581 / 731 (rest not communicated; Cuatrocorz unmapped) |
| Navarra | Res. 682/2025 (BON 241, 2-12-2025) + Res. 765/2025 (BON 1/2026); 3 Dec common day (bon-2026) | done | 262 / 272 (234 with 2 dates; concejo-only municipalities get 3 Dec + nucleos) |
| Baleares | BOIB 129 (27-9-2025) + corrections BOIB 139, 150, 15/2026 (boib-2026) | done | 67 / 67 (19 set per núcleo/parroquia only) |
| Ceuta | BOCCE 6549 (19-9-2025) (bocce-2026) | done | 1 / 1 |
| Melilla | BOME 6315 (3-10-2025) (bome-2026) | done | 1 / 1 |
| Castilla y León | 9 BOPs Sep 2025 (+ Ávila BOP 231/2025 and 23/2026) (bop-<provincia>-2026) | done | 1,765 / 2,248 (Valladolid 194/225, León 171/211, Burgos 190/371 via OCR of a scanned table, Salamanca 288/362 — Salamanca city missing, Zamora 202/248, Palencia 138/191, Segovia 200/209 minus 8, Ávila 202/248, Soria 180/183; the rest "no comunicado"; 233 with nucleos) |
| Castilla-La Mancha | 5 BOPs Oct–Nov 2025 + 11 later corrections (bop-<provincia>-2026) | done | 913 / 919 (Toledo 203/204, Ciudad Real 102/102, Albacete 87/87, Guadalajara 283/288, Cuenca 238/238; Guadalajara has 34 Sunday dates as published) |
| La Rioja | BOR 159 (19-08-2025) | BLOCKED | larioja.org sits behind a Cloudflare JS challenge (403 for curl and WebFetch); no mirror found. Retry from a browser session later. |

Checks: Cataluña open data matched the DOGC order text for all 824 municipalities checked (0 differences). Madrid núcleos (Cerceda, Mataelpino → El Boalo; El Espartal → El Vellón; Valdeolmos/Alalpardo) are in `nucleos`. Murcia table rebuilt from word coordinates (pdftotext -layout shifted every second row). Navarra weekday rules ("Lunes siguiente al primer domingo de mayo", Pentecost, Carnival Monday/Tuesday, Ascension) converted to dates with the printed rule kept in `rule`/note; "Viernes de carnaval" (Arantza) and "Viernes de la semana siguiente a San Lucas" (Baztan) left out.

Sunday dates kept as published (merge adds a note): Alberuela de Tubo, El Viso, Játar, Vélez de Benaudalla, Manzanilla, Etayo, Cabañas Raras, Prado de la Guzpeña, Valdefuentes del Páramo, Pozuelo de la Orden, Muxía (printed "Luns da Barca" on 13-9, likely a misprint), Fuente la Reina.

## Schema of data/locales-2026.json

`municipios[<ine>] = {"holidays": [{"date","name"}], "source": <source id>, "nucleos"?: [{"name","holidays"}], "note"?}`. `holidays` may have 1 date or be empty when the bulletin only sets days per núcleo (then `nucleos` and `note` explain). `sources[<id>]` has title, url, published (+ modifications).

## How to rebuild

1. `python -E -P data/tools/build_municipios.py <diccionario26.xlsx>`
2. Each `data/tools/loc2026_*.py` with its downloaded bulletin(s) (URLs in each script's docstring) → `data/tools/parts-2026/*.json`.
3. `python -E -P data/tools/merge_locales_2026.py` → `data/locales-2026.json` (prints coverage and problems).

## Log

- 2026-11-07: catalogue built (8,132 / 52). Starting 2026 sources.
- 2026-11-07: Cataluña, Madrid, C. Valenciana parsed by me; sub-agents on Andalucía+Extremadura and Galicia+Asturias+Cantabria+País Vasco (resumed after a rate-limit stop). The CV/Murcia/Canarias/Baleares agent died at the rate limit; I took over CV from its downloads.
- 2026-11-07: Murcia, Canarias, Aragón, Navarra, Baleares, Ceuta, Melilla parsed by me; merge → 5,243 municipalities. CyL and CLM sub-agents running. La Rioja blocked (Cloudflare).
- 2026-11-07: CyL and CLM done. Final merge: **7,257 / 8,132** municipalities, 30 sources. `jcyl-2026` (Junta open-data gap-filler, 11 entries) is kept on disk but excluded in `merge_locales_2026.py` (wrong INE codes and 2024/2025 dates in that CSV).

## Next steps (resume here)

1. La Rioja (174): BOR 159, 19-08-2025, from a browser session (Cloudflare blocks scripts), then a `loc2026_bor.py`.
2. CyL later lists: search each BOP's own site for complementary 2026 lists (Salamanca city, Medina del Campo, Laguna de Duero, Sahagún are missing; Burgos 181 missing).
3. Optional: map Extremadura's 56 ELMs, Guadalajara's 34 pedanías and Albacete's 9 pedanías to their municipality's `nucleos` (needs an official pedanía→municipality list, e.g. the INE nomenclátor).
