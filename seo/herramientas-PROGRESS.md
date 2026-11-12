# Tools section (herramientas/) · contract and progress

Live at https://elcalendariolaboral.es/utilidades/ (Spanish hub) and /en/tools/ (English hub, written automatically once
one tool has `"lang": "en"`). Package: `herramientas/`. Owner of the framework: U1 (batch b1112).

## How it works

- **A tool = ONE file**: `herramientas/tools/<module_name>.py` with a `TOOL = {...}` dict (schema below). Module name =
  slug with `_` instead of `-`. Files starting with `_` are ignored.
- Everything is **derived from the tool files** (auto-discovery in `herramientas.registry()`): hub cards and categories,
  hub search, related cards, `sitemap-utilidades.xml`, footer links (`"footer": True`, lead decides), the credits
  page. Nobody edits a shared registry to add a tool.
- **One template** renders every tool (`herramientas.tool_page`): breadcrumbs, H1, the form (generated from
  `inputs`), the result box, then the explanation blocks, one ad unit (only if the page has ≥ 250 words; never in the
  form or the result), FAQ, "Actualizado · Fuente(s)" line, credits line, related tools.
- **One runtime** (`herramientas/js/h.js` → `utilidades/a/h.js`) wires the form, calls your compute function on every
  change, renders its result, keeps the form in the URL (shareable link button) and handles print / .ics download.
  Shared CSS: `herramientas/h.css` → `utilidades/a/h.css`. **Both are frozen for pack agents**: tool-specific CSS goes
  in the tool's `css` field; anything the runtime lacks → ask the lead in your journal.
- SEO done by the template: canonical, robots, OG (default image), BreadcrumbList + FAQPage JSON-LD, WebPage date
  (from `updated`), hreflang pair when `twin` is set. **No WebApplication schema** (removed on purpose, AdSense review).

## File layout

| path | what | who writes it |
|---|---|---|
| `herramientas/tools/<module>.py` | the tool definition | the tool's agent |
| `herramientas/icons/<name>.svg` | Tabler icon (MIT), outline, 24px: `curl -o herramientas/icons/<name>.svg https://unpkg.com/@tabler/icons@3.19.0/icons/outline/<name>.svg` | the tool's agent (new files only) |
| `utilidades/<slug>/index.html`, `utilidades/<slug>/t.js` | generated page + its compute script (ES) | build |
| `en/tools/<slug>/index.html`, `en/tools/<slug>/t.js` | generated (EN) | build |
| `utilidades/index.html`, `en/tools/index.html`, `utilidades/creditos/`, `sitemap-utilidades.xml`, `utilidades/a/*` | hubs, credits, sitemap, shared runtime/css | lead (full mode) |
| `herramientas/__init__.py`, `js/h.js`, `h.css`, `build.py`, `test_herramientas.py` | framework | U1 / lead only |

## Build and test (no full site build)

```
cd elcalendariolaboral
MSYS_NO_PATHCONV=1 python -m herramientas.build <slug> [<slug> ...]      # only your tools: index.html + t.js
MSYS_NO_PATHCONV=1 python herramientas/test_herramientas.py --pages <slug> [...]   # your node test cases + page checks
MSYS_NO_PATHCONV=1 python -m herramientas.build                         # LEAD: everything + hubs + sitemap-utilidades.xml
```

`python -m herramientas.build` with slugs takes a few seconds and never touches other tools' folders, the hubs or
the sitemap: safe for parallel agents. The lead runs it without arguments at merge time (and `build.py`, the full
site build, also renders all tools, the hubs and the sitemap segment). Every definition is validated on load
(`check_tool`): a broken tool file breaks everyone's build, so run the test right after editing.

**Commit rule** (lead / U1 only; pack agents do not run git): `git add` explicit paths only, never `-A`, `.` or
`commit -a`: `herramientas/tools/<module>.py herramientas/icons/<new>.svg utilidades/<slug>/` (+ `en/tools/<slug>/`).

## TOOL schema

```python
TOOL = {
    # identity
    "slug": "cuadrante-turnos",      # URL /utilidades/<slug>/ (or /en/tools/<slug>/), lowercase-hyphen
    "lang": "es",                    # "es" | "en"
    "twin": None,                    # slug of the same tool in the other language -> hreflang pair (both files set it)
    "cat": "trabajo",                # hub category: a key of herramientas.CATS[lang] ...
    "cat_name": None,                # ... or a new key + its display name here (no shared edit needed)
    "icon": "calendar-repeat",       # herramientas/icons/<icon>.svg
    "order": 100,                    # position in its category (lower first)
    "name": "Cuadrante de turnos",   # card + related label, 1-4 words
    "k": "6x3 4x4 rotativo",         # extra hub-search keywords (optional)
    "footer": False,                 # site footer link (lead only)
    # SEO / texts (Spanish pages in Spanish, English pages written natively)
    "title": "...",                  # <= 60 chars, the query people type
    "desc": "...",                   # 70-155 chars, written for CTR
    "h1": "...", "crumb": None,      # crumb defaults to name
    "intro": "",                     # optional one short line under the H1 (keep the tool above the fold)
    "updated": "2026-11-12",         # visible date, dateModified, sitemap lastmod: bump only on real changes
    # the tool
    "inputs": [ ... ],               # form spec, below
    "js": r"""function (v, H, C) { ... return {...}; }""",   # pure compute function, below
    "hol": (2027,),                  # optional: ship holiday data of these years (needed by "place" inputs; default 2026+2027)
    "data": None,                    # optional dict, or callable(ctx) -> dict: extra data for compute as C.d
    "css": "",                       # optional tool-specific CSS (inline <style>)
    "link": True,                    # "Copiar enlace" button
    # content below the tool (>= 250 words of real, specific text in total: AdSense is reviewing "low-value content")
    "blocks": [("Heading", "<p>html</p>"), ...],   # or callable(ctx) -> list; answer first, worked example with real numbers, legal basis / method
    "faq": [("Question?", "Answer html"), ...],     # 4-6 real questions (or callable(ctx))
    "sources": [("BOE · Estatuto de los Trabajadores, art. 38", "https://www.boe.es/..."), ...],  # official sources, >= 1
    "credits": [("Name", "MIT", "https://...")],   # adapted formulas / data / code (permissive licences only)
    "related": ["registro-jornada", "dias-habiles/"],  # tool slugs, or paths of older pages listed in herramientas.LEGACY
    "tests": [({"seq": "XXXXXXLLL", "start": "2027-01-04"}, {"n.worked": 242, "err": None}), ...],  # 3-6 node cases
}
```

### inputs

Each input: `{"id": "start", "type": ..., "label": "Inicio", "value": <default raw value>, ...}`. ids: lowercase
letters/digits, unique. Common keys: `more: True` (inside "Más opciones"), `show: ("other_id", ["v1", "v2"])`
(visible only for those values of another input), `w: "s"|"l"|"xl"` (width), `min`, `max`, `step`, `maxlength`,
`placeholder`.

| type | renders | compute gets `v[id]` |
|---|---|---|
| `number` | text input, numeric keyboard, optional `unit` suffix | Number (`NaN` if empty/invalid; "1.234,5" accepted) |
| `money` | same, `€` suffix by default, decimal keyboard | Number |
| `date` | date picker; `today: True` = visitor's date by default | `Date` (UTC midnight) or `null` |
| `month` | select of months `min`..`max` ("2026-01".."2027-12" by default); `today: True` | `"YYYY-MM"` |
| `select` | select; `options: [(value, label)]` or `(value, label, {"other_id": raw})` presets that fill other inputs; `custom: "<value>"` = option shown when those inputs are edited by hand | string |
| `seg` | segmented buttons, `options: [(value, label)]` | string |
| `check` | checkbox | boolean |
| `text`, `time` | text / time input | string |
| `place` | comunidad + municipio selects (municipios = published cities, islands, Arán) | holiday list `[[iso, name, kind]]`; also `v[id+"_label"]`, `v[id+"_r"]`, `v[id+"_m"]` |

### compute function (`js`)

`function (v, H, C) { ... }`, ES2015, no DOM, no network. `v`: values by input id (types above). `C`: `{d: <data>,
hol: <holiday data>}`. `H`: helpers from `h.js`: `parse iso add diff leap yearDays monthDays wd r2 esc num eur val
plural holidays holidayMap icsEsc icsDate`. Return:

```js
{ err: 'Mensaje' }                         // instead of a result (invalid input): shown in a red box
{ label: 'Finiquito', big: H.eur(x),       // big number card (big may be a number or a string)
  sub: 'line under the number',
  rows: [['Salario', H.eur(a)], ['Total', H.eur(t), 'tot']],   // breakdown table; 3rd item = row class: tot | sub | z
  html: '<div>...</div>',                  // any extra markup (escape user text with H.esc)
  note: 'small print',
  print: true,                             // "Imprimir o PDF" button (print CSS hides the form and the text below)
  ics: { name: 'x.ics', text: 'BEGIN:VCALENDAR...' },   // "Descargar .ics" button
  n: { total: 1234.56 } }                  // raw numbers for the tests (not rendered)
```

Tests: `tests` = `[(inputs, expected)]`. Inputs are raw form values (strings as typed, `{"r": "madrid", "m": ""}` for
place); missing inputs take their `value`. Expected: dotted paths into the result (`"n.total"`, `"err"`,
`"n.cnt.L"`), numbers compared ±0.006.

## Credits

Per-tool `credits` render on the tool page and are aggregated at `/utilidades/creditos/` (noindex) with the icon set
(Tabler Icons, MIT, https://tabler.io/icons) and the holiday data (BOE and official bulletins).

## Status

| slug | state | sources |
|---|---|---|
| cuadrante-turnos | built | ET arts. 34, 36, 37 (BOE-A-2015-11430); RD 1561/1995; calendario laboral 2027 BOE-A-2026-21254 |
| registro-jornada | todo (U1) | |
| calculadora-vacaciones | todo (U1) | |
| calculadora-finiquito | todo (U1) | |
| calculadora-paro | todo (U1) | |

Links into the tools from the rest of the site (full build only): header "Utilidades" (hidden 861-1080 px, no room),
footer block (hub + tools with `footer: True`), home (after the utility links), each comunidad page (cuadrante,
registro, vacaciones), /dias-habiles/.
