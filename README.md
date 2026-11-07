# elcalendariolaboral.es

Calendario laboral 2027 de España: festivos por comunidad (BOE-A-2026-21254), puentes, planificador de vacaciones y exportación a calendario.

Fuente única: `data/2027.json`. Generar: `CL_SITE=https://elcalendariolaboral.es CL_BASE=/ python build.py`. Test: `python test_data.py`.

Municipios (8.132) y provincias: `data/municipios.json`, `data/provincias.json`, `data/locales-2027-all.json`,
`data/locales-2026.json` → `muni.py` (catálogo, buscador) y `munipages.py` (páginas). `CL_MUNI=0` las omite.
Buscador: `buscar.py` → `buscar.json`. Estado y medidas: `seo/build-PROGRESS.md`.
