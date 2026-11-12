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
MSYS_NO_PATHCONV=1 python -m herramientas.build --hub                   # LEAD: shared runtime/css + hubs + credits + sitemap
```

`python -m herramientas.build` with slugs takes a few seconds and never touches other tools' folders, the hubs or
the sitemap: safe for parallel agents. The lead runs it without arguments at merge time (and `build.py`, the full
site build, also renders all tools, the hubs and the sitemap segment). Every definition is validated on load
(`check_tool`); run the test right after editing.

**Broken tool files** (import error, `check_tool` failure, two files with one slug) never stop other people's work:

| mode | a broken tool file that is required | any other broken tool file |
|---|---|---|
| slug mode: `build <slugs>`, `test_herramientas.py [--pages] <slugs>` | required = the given slugs: **error, exit 1** | skipped, one `warning:` block on stderr |
| full / `--hub` / `build.py`, `HT_ONLY` set | required = the `HT_ONLY` slugs: **error, the build stops** | skipped, loud `!!! BROKEN TOOL FILE(S) SKIPPED` block on stderr |
| full / `--hub` / `build.py`, no `HT_ONLY` | none | skipped, loud block on stderr |
| `test_herramientas.py` with no slugs and no `HT_ONLY` | every file: each broken one is a test failure | - |

**For the lead's merge**: a skipped tool is absent from everything the build writes (its page is not rebuilt, and it
is left out of the hubs, sitemap, credits, footer and related links), so a draft never gets published and never
stops the merge; read the stderr block and tell its owner. A merged tool (in `HT_ONLY`) that breaks stops the build
instead of silently dropping a live page from the hubs and the sitemap. `herramientas.BROKEN` holds the skipped
slugs and errors.

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
| `number` | text input, numeric keyboard, optional `unit` suffix | Number (`NaN` if empty/invalid; read by page language, see below) |
| `money` | same, `€` suffix by default, decimal keyboard | Number |
| `date` | date picker; `today: True` = visitor's date by default | `Date` (UTC midnight) or `null` |
| `month` | select of months `min`..`max` ("2026-01".."2027-12" by default); `today: True` | `"YYYY-MM"` |
| `select` | select; `options: [(value, label)]` or `(value, label, {"other_id": raw})` presets that fill other inputs; `custom: "<value>"` = option shown when those inputs are edited by hand | string |
| `seg` | segmented buttons, `options: [(value, label)]` | string |
| `check` | checkbox | boolean |
| `text`, `time` | text / time input | string |
| `place` | comunidad + municipio selects (municipios = published cities, islands, Arán) | holiday list `[[iso, name, kind]]`; also `v[id+"_label"]`, `v[id+"_r"]`, `v[id+"_m"]` |

Typed numbers (`number`, `money`, and `H.val(s[, lang])` in compute code) follow the page language (`H.lang`, set
from the tool's `lang`; node tests set it too). Both languages strip spaces, `%`, `€ $ £ ¥ ₹`, `US$`, `EUR USD GBP CAD
AUD` and read `−` as a minus; when both `.` and `,` appear, the last one is the decimal mark (`1.234,56` = `1,234.50`
style on any page).
- `es`: `,` decimal (`1,5`, `1.234,56 €`); `.` = thousands only in full groups (`36.000`, `1.234.567`), otherwise a
  decimal point (`12.5`, `12.50`).
- `en`: `.` decimal; `,` = thousands in full groups (`1,234`, `$1,234.50`, `1,234,567`); a single comma that is not a
  full group is a decimal comma (`12,5` = 12.5). `£12.5`, `€3`, `-$5.25`, `20 USD` all work.
- Output formatting is unchanged: `H.num` / `H.eur` always write Spanish style; English tools format their own output.

### compute function (`js`)

`function (v, H, C) { ... }`, ES2015, no DOM, no network. `v`: values by input id (types above). `C`: `{d: <data>,
hol: <holiday data>}`. `H`: helpers from `h.js`: `parse iso add diff leap yearDays monthDays wd r2 esc num eur val
plural holidays holidayMap icsEsc icsDate lang`. Return:

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

**Publishing only reviewed tools**: `HT_ONLY=slug1,slug2,...` (environment) limits the registry, so hubs, sitemap,
credits, footer and related links only show those tools. Use it with `python -m herramientas.build --hub` and with
`build.py` while unreviewed pack tools sit in `herramientas/tools/`. Without it, every tool file on disk that loads is
published. The `HT_ONLY` tools are also the required ones in full / hub mode (see "Broken tool files").

| slug | state | sources |
|---|---|---|
| cuadrante-turnos | live 2026-11-12 | ET arts. 34, 36, 37 (BOE-A-2015-11430); RD 1561/1995; calendario laboral 2027 BOE-A-2026-21254 |
| registro-jornada | live 2026-11-12 | ET art. 34.9, 12.4.c, 35; RDL 8/2019 (BOE-A-2019-3481); LISOS art. 7.5; guía MITES. Digital-registry royal decree: not confirmed in BOE as of 12 Nov 2026, page says so |
| calculadora-vacaciones | live 2026-11-12 | ET art. 38; ILO C132 |
| calculadora-finiquito | live 2026-11-12 | ET arts. 38, 49.1.c, 53.1.b, 56.1, DT 11.ª; Ley IRPF art. 7.e (exención 180.000 €) |
| calculadora-paro | live 2026-11-12 | SEPE (70 % first 180 days, 60 % from day 181); LGSS arts. 269-270; IPREM 2026 = 600 €/month (PGE 2023 prorrogados, confirmed only by secondary sources: page says "según la normativa vigente a 12 de noviembre de 2026"); topes 560/749 · 1.225/1.400/1.575 |

Testing without a browser: a jsdom smoke script (load the page, run h.js + t.js, change inputs, print the result
text): `plusUltra/coord/b1112/jsdom-smoke.js` (`npm i jsdom@24.1.3` in a scratch folder, then
`node jsdom-smoke.js utilidades/<slug>/ "?query" '[["inputId","value"]]'`). It caught the "36.000" parsing bug.

Links into the tools from the rest of the site (full build only): header "Utilidades" (hidden 861-1080 px, no room),
footer block (hub + tools with `footer: True`), home (after the utility links), each comunidad page (cuadrante,
registro, vacaciones), /dias-habiles/.
