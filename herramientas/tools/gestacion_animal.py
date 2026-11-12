"""Gestación animal: expected birth date (and usual window) from the mating date, for dogs, cats, rabbits, horses,
donkeys, cattle, sheep, goats and pigs. The English twin (animal_gestation_calculator.py) reuses SPECIES and make_js."""
import json

MSD = "https://www.msdvetmanual.com/es/multimedia/table/periodos-de-gestaci%C3%B3n-aproximados"
MSD_EN = "https://www.msdvetmanual.com/multimedia/table/approximate-gestation-periods"
NMSU = "https://pubs.nmsu.edu/_b/B130/"
DONKEY = "https://www.thedonkeysanctuary.org.uk/for-owners/mares-and-foals"

# key, average days, usual range (lo, hi), Spanish name, birth word, English name, English birth word
SPECIES = [
    ("perra", 63, 58, 72, "Perra", "parto", "Dog", "whelping"),
    ("gata", 65, 58, 70, "Gata", "parto", "Cat", "queening"),
    ("coneja", 31, 28, 35, "Coneja", "parto", "Rabbit", "kindling"),
    ("cerda", 114, 111, 117, "Cerda", "parto", "Sow (pig)", "farrowing"),
    ("oveja", 147, 143, 152, "Oveja", "parto", "Ewe (sheep)", "lambing"),
    ("cabra", 150, 145, 155, "Cabra", "parto", "Goat", "kidding"),
    ("vaca", 283, 279, 292, "Vaca", "parto", "Cow", "calving"),
    ("yegua", 340, 320, 370, "Yegua", "parto", "Mare (horse)", "foaling"),
    ("burra", 365, 335, 440, "Burra", "parto", "Jenny (donkey)", "foaling"),
]

L_ES = {
    "mon": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
    "wd": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
    "de": " de ", "label": "Parto previsto", "between": "Lo normal: entre el ", "and": " y el ",
    "avg": "Gestación media", "range": "Rango habitual", "days": " días", "from": "Cubrición",
    "prep": "Preparar la zona de parto", "today": "Hoy", "dayn": "día ", "left": "faltan ", "past": "ya pasó la fecha prevista",
    "late": "pasado el rango habitual: consulta al veterinario", "err": "Pon la fecha de la cubrición.",
    "note": "Promedios de manuales veterinarios: cada animal, raza y camada varía. No sustituye la revisión veterinaria.",
    "ics": "parto-previsto.ics", "sum": "Parto previsto", "win": "Ventana de parto", "num_sep": ",",
}


def species_options(lang):
    return [(k, (es if lang == "es" else en)) for k, _, _, _, es, _, en, _ in SPECIES]


def make_js(L):
    sp = {k: [a, lo, hi, es, en] for k, a, lo, hi, es, _, en, _ in SPECIES}
    return r"""
function (v, H, C) {
  var L = """ + json.dumps(L, ensure_ascii=False) + r""", S = """ + json.dumps(sp, ensure_ascii=False) + r""";
  var s = S[v.especie] || S.perra, d0 = v.fecha;
  if (!d0) return { err: L.err };
  function f(d) { return L.wd[H.wd(d)] + ' ' + (L.lang === 'en' ? d.getUTCDate() + ' ' + L.mon[d.getUTCMonth()] + ' ' + d.getUTCFullYear()
    : d.getUTCDate() + L.de + L.mon[d.getUTCMonth()] + L.de + d.getUTCFullYear()); }
  function sh(d) { return L.lang === 'en' ? d.getUTCDate() + ' ' + L.mon[d.getUTCMonth()].slice(0, 3) : d.getUTCDate() + '/' + (d.getUTCMonth() + 1) + '/' + d.getUTCFullYear(); }
  var due = H.add(d0, s[0]), lo = H.add(d0, s[1]), hi = H.add(d0, s[2]), prep = H.add(lo, -7);
  var rows = [[L.from, f(d0)], [L.avg, s[0] + L.days], [L.range, s[1] + '–' + s[2] + L.days], [L.prep, f(prep), 'sub'], [L.label, f(due), 'tot']];
  var now = H.today ? H.today() : null, n = null;
  if (now) {
    n = H.diff(d0, now);
    if (n >= 0 && n <= s[2] + 30) rows.push([L.today, n > s[2] ? L.late : n > s[0] ? L.dayn + n + ' · ' + L.past : L.dayn + n + ' · ' + L.left + (s[0] - n) + L.days + (L.togo || '')]);
  }
  function ev(a, b, t, u) { return 'BEGIN:VEVENT\r\nUID:' + u + H.icsDate(d0) + '@elcalendariolaboral.es\r\nDTSTAMP:20261112T000000Z\r\nDTSTART;VALUE=DATE:' + H.icsDate(a) +
    '\r\nDTEND;VALUE=DATE:' + H.icsDate(H.add(b, 1)) + '\r\nSUMMARY:' + H.icsEsc(t) + '\r\nTRANSP:TRANSPARENT\r\nEND:VEVENT\r\n'; }
  var name = L.lang === 'en' ? s[4] : s[3];
  var ics = 'BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//elcalendariolaboral.es//gestacion//' + (L.lang === 'en' ? 'EN' : 'ES') + '\r\nCALSCALE:GREGORIAN\r\n' +
    ev(due, due, L.sum + ' · ' + name, 'g') + ev(lo, hi, L.win + ' · ' + name, 'w') + 'END:VCALENDAR\r\n';
  return { label: L.label + ' · ' + name, big: f(due), sub: L.between + sh(lo) + L.and + sh(hi), rows: rows, note: L.note,
    ics: { name: L.ics, text: ics }, n: { due: H.iso(due), lo: H.iso(lo), hi: H.iso(hi), days: s[0] } };
}
"""


def blocks(ctx):
    rows = "".join(f"<tr><td>{es}</td><td class=\"num\">{a} días</td><td class=\"num\">{lo}–{hi} días</td><td class=\"num\">{a / 30.44:.1f} meses</td></tr>".replace(".", ",")
                   for k, a, lo, hi, es, _, _, _ in SPECIES)
    return [
        ("Cuánto dura la gestación de cada animal", f"""
<p>La fecha de parto se calcula sumando a la fecha de la cubrición (la monta o la inseminación) los días que dura de media la
gestación de la especie. Una perra pare a los <b>63 días</b> de media, una gata a los 65, una coneja al mes (31 días), una cerda a
los 114 (los famosos «tres meses, tres semanas y tres días»), una oveja hacia los 147, una cabra a los 150, una vaca a los
<b>283</b> y una yegua hacia los 340 días, unos once meses. La burra es la más larga de los animales de granja: un año de media, y
puede pasar de los catorce meses sin que haya ningún problema.</p>
<table class="tbl"><thead><tr><th>Especie</th><th>Media</th><th>Rango habitual</th><th>Meses</th></tr></thead><tbody>{rows}</tbody></table>
<p>El rango importa tanto como la media: en la perra, contando desde la monta y no desde la ovulación, el parto puede llegar entre
los 58 y los 72 días, porque los espermatozoides sobreviven varios días esperando a que ovule. Con varias cubriciones, cuenta desde
la primera para el inicio de la ventana y desde la última para el final.</p>"""),
        ("Ejemplo", """
<p>Una vaca inseminada el <b>1 de diciembre de 2026</b> tiene la fecha prevista de parto el <b>10 de septiembre de 2027</b>
(283 días después), con la ventana normal entre el 6 y el 19 de septiembre. Una perra cubierta el 1 de diciembre de 2026 pariría
hacia el 2 de febrero de 2027, normalmente entre el 28 de enero y el 11 de febrero; conviene tener preparada la paridera una semana
antes del primer día de la ventana.</p>"""),
        ("De dónde salen los días", f"""
<p>Las medias son las del <a href="{MSD}" rel="noopener">Manual Veterinario MSD</a> (tabla de periodos de gestación aproximados),
con la vaca y la yegua de la guía de la <a href="{NMSU}" rel="noopener">Universidad Estatal de Nuevo México</a>, que usa 283 y 340
días para calcular partos. Los rangos son los habituales de la bibliografía veterinaria; el de la burra (de 11 a 14,5 meses) es el
que da <a href="{DONKEY}" rel="noopener">The Donkey Sanctuary</a>. Influyen la raza (las vacas de razas grandes y los toros de carne
alargan la gestación unos días), el tamaño de la camada (camadas pequeñas duran algo más), la edad de la madre y la época del año
en la yegua: las cubiertas en primavera suelen parir algo antes que las de verano.</p>
<p>Es una estimación para organizarse, no un diagnóstico. Si el parto se adelanta mucho, se pasa del rango o la hembra muestra
signos de dificultad, llama al veterinario.</p>"""),
    ]


FAQ = [
    ("¿Cuánto dura el embarazo de una perra?",
     "Unos 63 días (nueve semanas) desde la ovulación. Contando desde la monta, el parto puede llegar entre los 58 y los 72 días. Las "
     "razas pequeñas y las camadas grandes suelen parir antes."),
    ("¿Cuántos meses está preñada una vaca?",
     "Algo más de nueve meses: 283 días de media, como una persona. Según la raza, entre 279 y 292 días."),
    ("¿Cuánto tiempo está preñada una yegua?",
     "Unos 11 meses (340 días de media), con partos normales entre los 320 y los 370 días. Una burra tarda más: alrededor de un año."),
    ("¿Cuántos días dura la gestación de una cerda?",
     "114 días de media, la regla de «tres meses, tres semanas y tres días». Lo normal es entre 111 y 117."),
    ("¿Cuánto tarda en parir una coneja?",
     "Alrededor de 31 días tras la monta, entre 28 y 35. Si llega al día 32 sin parir, conviene consultar al veterinario."),
    ("¿Cómo sé si está preñada de verdad?",
     "La fecha solo es una cuenta. La confirmación es la ecografía o el análisis que haga el veterinario: en la perra a partir de "
     "las 3-4 semanas, en la vaca desde unos 30 días tras la inseminación."),
]

TOOL = {
    "slug": "gestacion-animal",
    "lang": "es",
    "twin": "animal-gestation-calculator",
    "cat": "campo",
    "cat_name": "Campo, huerto y animales",
    "icon": "pig",
    "order": 20,
    "name": "Calculadora de gestación animal",
    "k": "perra gata coneja vaca yegua burra oveja cabra cerda parto preñez cubricion",
    "title": "Calculadora de gestación animal: fecha de parto",
    "desc": "Fecha probable de parto de perra, gata, coneja, vaca, yegua, burra, oveja, cabra o cerda desde la cubrición, con la ventana normal y aviso al calendario.",
    "h1": "Calculadora de gestación animal",
    "crumb": "Gestación animal",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "especie", "type": "select", "label": "Especie", "value": "perra", "options": species_options("es")},
        {"id": "fecha", "type": "date", "label": "Cubrición", "value": "2026-11-12", "today": True, "min": "2000-01-01", "max": "2035-12-31"},
    ],
    "js": make_js(L_ES),
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Manual Veterinario MSD · periodos de gestación aproximados", MSD),
                ("New Mexico State University · Guide B-130 (vaca 283 días, yegua 340)", NMSU),
                ("The Donkey Sanctuary · mares and foals", DONKEY)],
    "related": ["incubacion-huevos", "edad-perro-gato", "carga-ganadera"],
    "tests": [
        ({"especie": "vaca", "fecha": "2026-12-01"}, {"n.due": "2027-09-10", "n.lo": "2027-09-06", "n.hi": "2027-09-19"}),
        ({"especie": "perra", "fecha": "2026-12-01"}, {"n.due": "2027-02-02", "n.lo": "2027-01-28", "n.hi": "2027-02-11"}),
        ({"especie": "cerda", "fecha": "2027-01-01"}, {"n.due": "2027-04-25", "n.days": 114}),
        ({"especie": "burra", "fecha": "2028-02-29"}, {"n.due": "2029-02-28"}),
        ({"especie": "gata", "fecha": ""}, {"err": "Pon la fecha de la cubrición."}),
    ],
}
