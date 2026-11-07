"""Build data/municipios.json and data/provincias.json from the INE municipality dictionary.

Usage (run with -E -P so nothing is imported from the download folder):
    python -E -P data/tools/build_municipios.py <path to diccionarioYY.xlsx>

Source: INE, "Relacion de municipios y sus codigos por provincias" (codmun/diccionarioYY.xlsx).
Slugs of cities already in data/locales-2027.json are reused; unmatched ones are printed.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]

# CPRO -> (site name, slug, region slug, capital INE code)
PROVINCES = {
    "01": ("Álava", "alava", "pais-vasco", "01059"),
    "02": ("Albacete", "albacete", "castilla-la-mancha", "02003"),
    "03": ("Alicante", "alicante", "comunitat-valenciana", "03014"),
    "04": ("Almería", "almeria", "andalucia", "04013"),
    "05": ("Ávila", "avila", "castilla-y-leon", "05019"),
    "06": ("Badajoz", "badajoz", "extremadura", "06015"),
    "07": ("Illes Balears", "illes-balears", "baleares", "07040"),
    "08": ("Barcelona", "barcelona", "cataluna", "08019"),
    "09": ("Burgos", "burgos", "castilla-y-leon", "09059"),
    "10": ("Cáceres", "caceres", "extremadura", "10037"),
    "11": ("Cádiz", "cadiz", "andalucia", "11012"),
    "12": ("Castellón", "castellon", "comunitat-valenciana", "12040"),
    "13": ("Ciudad Real", "ciudad-real", "castilla-la-mancha", "13034"),
    "14": ("Córdoba", "cordoba", "andalucia", "14021"),
    "15": ("A Coruña", "a-coruna", "galicia", "15030"),
    "16": ("Cuenca", "cuenca", "castilla-la-mancha", "16078"),
    "17": ("Girona", "girona", "cataluna", "17079"),
    "18": ("Granada", "granada", "andalucia", "18087"),
    "19": ("Guadalajara", "guadalajara", "castilla-la-mancha", "19130"),
    "20": ("Gipuzkoa", "gipuzkoa", "pais-vasco", "20069"),
    "21": ("Huelva", "huelva", "andalucia", "21041"),
    "22": ("Huesca", "huesca", "aragon", "22125"),
    "23": ("Jaén", "jaen", "andalucia", "23050"),
    "24": ("León", "leon", "castilla-y-leon", "24089"),
    "25": ("Lleida", "lleida", "cataluna", "25120"),
    "26": ("La Rioja", "la-rioja", "la-rioja", "26089"),
    "27": ("Lugo", "lugo", "galicia", "27028"),
    "28": ("Madrid", "madrid", "madrid", "28079"),
    "29": ("Málaga", "malaga", "andalucia", "29067"),
    "30": ("Murcia", "murcia", "murcia", "30030"),
    "31": ("Navarra", "navarra", "navarra", "31201"),
    "32": ("Ourense", "ourense", "galicia", "32054"),
    "33": ("Asturias", "asturias", "asturias", "33044"),
    "34": ("Palencia", "palencia", "castilla-y-leon", "34120"),
    "35": ("Las Palmas", "las-palmas", "canarias", "35016"),
    "36": ("Pontevedra", "pontevedra", "galicia", "36038"),
    "37": ("Salamanca", "salamanca", "castilla-y-leon", "37274"),
    "38": ("Santa Cruz de Tenerife", "santa-cruz-de-tenerife", "canarias", "38038"),
    "39": ("Cantabria", "cantabria", "cantabria", "39075"),
    "40": ("Segovia", "segovia", "castilla-y-leon", "40194"),
    "41": ("Sevilla", "sevilla", "andalucia", "41091"),
    "42": ("Soria", "soria", "castilla-y-leon", "42173"),
    "43": ("Tarragona", "tarragona", "cataluna", "43148"),
    "44": ("Teruel", "teruel", "aragon", "44216"),
    "45": ("Toledo", "toledo", "castilla-la-mancha", "45168"),
    "46": ("Valencia", "valencia", "comunitat-valenciana", "46250"),
    "47": ("Valladolid", "valladolid", "castilla-y-leon", "47186"),
    "48": ("Bizkaia", "bizkaia", "pais-vasco", "48020"),
    "49": ("Zamora", "zamora", "castilla-y-leon", "49275"),
    "50": ("Zaragoza", "zaragoza", "aragon", "50297"),
    "51": ("Ceuta", "ceuta", "ceuta", "51001"),
    "52": ("Melilla", "melilla", "melilla", "52001"),
}
PROVINCE_ALIASES = {
    "01": ["Araba", "Araba/Álava"], "07": ["Baleares", "Islas Baleares"], "12": ["Castelló", "Castellón de la Plana"],
    "03": ["Alacant"], "15": ["La Coruña", "Coruña"], "17": ["Gerona"], "20": ["Guipúzcoa"], "25": ["Lérida"],
    "32": ["Orense"], "33": ["Principado de Asturias"], "46": ["València"], "48": ["Vizcaya"],
    "31": ["Comunidad Foral de Navarra", "Nafarroa"], "30": ["Región de Murcia"], "26": ["Rioja"],
}
CODAUTO = {"01": "andalucia", "02": "aragon", "03": "asturias", "04": "baleares", "05": "canarias", "06": "cantabria",
           "07": "castilla-y-leon", "08": "castilla-la-mancha", "09": "cataluna", "10": "comunitat-valenciana",
           "11": "extremadura", "12": "galicia", "13": "madrid", "14": "murcia", "15": "navarra", "16": "pais-vasco",
           "17": "la-rioja", "18": "ceuta", "19": "melilla"}

# Canarias: island of each municipality (needed for the insular holiday). Everything else in 35 is Gran Canaria, in 38 Tenerife.
ISLANDS = {
    "lanzarote": ["Arrecife", "Haría", "San Bartolomé", "Teguise", "Tías", "Tinajo", "Yaiza"],
    "fuerteventura": ["Antigua", "Betancuria", "La Oliva", "Pájara", "Puerto del Rosario", "Tuineje"],
    "la-palma": ["Barlovento", "Breña Alta", "Breña Baja", "Fuencaliente de la Palma", "Garafía", "Los Llanos de Aridane",
                 "El Paso", "Puntagorda", "Puntallana", "San Andrés y Sauces", "Santa Cruz de la Palma", "Tazacorte",
                 "Tijarafe", "Villa de Mazo"],
    "la-gomera": ["Agulo", "Alajeró", "Hermigua", "San Sebastián de La Gomera", "Valle Gran Rey", "Vallehermoso"],
    "el-hierro": ["Frontera", "Valverde", "El Pinar de El Hierro"],
}

# Spanish exonyms / common variants people search for (INE name as published -> extra aliases).
# Every key is asserted to exist in the INE file.
EXONYMS = {
    "Coruña, A": ["La Coruña", "Coruña"], "Ourense": ["Orense"], "Lleida": ["Lérida"], "Girona": ["Gerona"],
    "Donostia/San Sebastián": ["Donostia-San Sebastián", "Donosti"], "Vitoria-Gasteiz": ["Vitoria", "Gasteiz"],
    "Palma": ["Palma de Mallorca"], "Bilbao": ["Bilbo"], "Sanxenxo": ["Sangenjo"],
    "Vilagarcía de Arousa": ["Villagarcía de Arosa"], "Santiago de Compostela": ["Santiago"], "Ferrol": ["El Ferrol"],
    "Ponteareas": ["Puenteareas"], "Porriño, O": ["Porriño"], "Irun": ["Irún"], "Hondarribia": ["Fuenterrabía"],
    "Errenteria": ["Rentería"], "Pasaia": ["Pasajes"], "Barakaldo": ["Baracaldo"], "Santurtzi": ["Santurce"],
    "Getxo": ["Guecho"], "Leioa": ["Lejona"], "Gernika-Lumo": ["Guernica", "Gernika", "Guernica y Luno"],
    "Eivissa": ["Ibiza"], "Santa Eulària des Riu": ["Santa Eulalia del Río"],
    "Sant Antoni de Portmany": ["San Antonio Abad", "San Antonio"], "Ciutadella de Menorca": ["Ciudadela", "Ciutadella"],
    "Maó": ["Mahón", "Maó-Mahón"], "Vilafranca del Penedès": ["Villafranca del Penedés"],
    "Sant Cugat del Vallès": ["San Cugat del Vallés", "Sant Cugat"], "Sant Boi de Llobregat": ["San Baudilio de Llobregat"],
    "Hospitalet de Llobregat, L'": ["Hospitalet", "L'Hospitalet"], "Terrassa": ["Tarrasa"], "Mataró": ["Mataro"],
    "Mollet del Vallès": ["Mollet del Vallés"], "València": ["Valencia"], "Gandia": ["Gandía"], "Dénia": ["Denia"],
    "Vila-real": ["Villarreal"], "Oviedo": ["Uviéu"], "Gijón": ["Xixón"], "Avilés": ["Avilés"],
    "Palmas de Gran Canaria, Las": ["Las Palmas"], "San Cristóbal de La Laguna": ["La Laguna"],
    "Santa Cruz de Tenerife": ["Santa Cruz"], "Castelló de la Plana/Castellón de la Plana": ["Castellón", "Castelló"],
    "Alacant/Alicante": ["Alicante/Alacant"], "Elx/Elche": ["Elche/Elx"], "Ourense_": [], "Lugo": [], "Arteixo": ["Arteijo"], "Oleiros": [],
    "Sanxenxo_": [], "Carballo": [], "Ribeira": ["Santa Uxía de Ribeira", "Santa Eugenia de Ribeira"],
    "Vigo": [], "Lalín": [], "Ames": [], "Narón": [], "Figueres": ["Figueras"], "Manresa": [],
    "Vic": ["Vich"], "Granollers": [], "Igualada": [], "Sant Feliu de Llobregat": ["San Feliú de Llobregat"],
    "Cornellà de Llobregat": ["Cornellá de Llobregat", "Cornellá"], "Esplugues de Llobregat": ["Esplugas de Llobregat"],
    "Sant Adrià de Besòs": ["San Adrián de Besós"], "Santa Coloma de Gramenet": ["Santa Coloma"],
    "Vilanova i la Geltrú": ["Villanueva y Geltrú"], "Sitges": [], "Lloret de Mar": [], "Blanes": [],
    "Tortosa": [], "Valls": [], "Cambrils": [], "Salou": [], "Vendrell, El": [],
    "Sant Vicent del Raspeig/San Vicente del Raspeig": ["San Vicente"], "Torrent": ["Torrente"],
    "Paterna": [], "Sueca": [], "Alzira": ["Alcira"], "Xàtiva": ["Játiva"], "Ontinyent": ["Onteniente"],
    "Gernika-Lumo_": [], "Zumaia": ["Zumaya"], "Zarautz": ["Zarauz"], "Azpeitia": [], "Tolosa": [],
    "Bermeo": [], "Mungia": ["Munguía"], "Ondarroa": ["Ondárroa"], "Lekeitio": ["Lequeitio"],
    "Ferrol_": [], "Viveiro": ["Vivero"], "Vilalba": ["Villalba"], "Sarria": [], "Xinzo de Limia": ["Ginzo de Limia"],
    "Mondoñedo": [], "Ribadeo": [], "Burela": [], "Foz": [], "Cangas": ["Cangas do Morrazo"],
}
EXONYMS = {k: v for k, v in EXONYMS.items() if not k.endswith("_") and v}
# Single-language co-official names whose usual Spanish form the site already uses as the page name
NAME_ES = {"València": "Valencia"}


def ascii_fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def slugify(s):
    """"Callosa d'en Sarrià" -> 'callosa-den-sarria' (an elided article sticks to the next word)."""
    s = ascii_fold(s).lower().replace("'", "").replace("’", "").replace("·", "")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


ARTICLE_RE = re.compile(r"^(.*), (El|La|Los|Las|L'|l'|Les|les|Els|els|Es|Sa|Ses|Sos|A|O|Os|As|el|la|los|las)$")


def front_article(name):
    """'Coruña, A' -> 'A Coruña'; "Hospitalet de Llobregat, L'" -> "L'Hospitalet de Llobregat"."""
    m = ARTICLE_RE.match(name)
    if not m:
        return name
    body, art = m.groups()
    art = art[0].upper() + art[1:]
    if art.endswith("'"):
        return f"{art}{body}"
    return f"{art} {body}"


# Markers of Basque / Catalan-Valencian / Galician spelling (never Spanish)
NON_ES = re.compile(r"(tx|tz|ts|k|à|è|ò|ï|ny|x|ç|l·l|^erri|ibar$|beiti|goiti|zendea|harana|iruña)", re.I)
# Bilingual names where the heuristic picks the wrong half (reviewed by hand for Álava and Navarra)
ES_PICK = {
    "Pamplona/Iruña": "Pamplona", "Laudio/Llodio": "Llodio", "Donostia/San Sebastián": "San Sebastián",
    "Arrasate/Mondragón": "Mondragón", "Elburgo/Burgelu": "Elburgo", "Labastida/Bastida": "Labastida",
    "Moreda de Álava/Moreda Araba": "Moreda de Álava", "Valdegovía/Gaubea": "Valdegovía", "Aibar/Oibar": "Aibar",
    "Allín/Allin": "Allín", "Ayegui/Aiegi": "Ayegui", "Barañáin/Barañain": "Barañáin", "Burgui/Burgi": "Burgui",
    "Burlada/Burlata": "Burlada", "Castillonuevo/Gazteluberri": "Castillonuevo", "Gallués/Galoze": "Gallués",
    "Güesa/Gorza": "Güesa", "Hiriberri/Villanueva de Aezkoa": "Villanueva de Aezkoa", "Huarte/Uharte": "Huarte",
    "Isaba/Izaba": "Isaba", "Lizoain-Arriasgoiti/Lizoainibar-Arriasgoiti": "Lizoain-Arriasgoiti",
    "Lónguida/Longida": "Lónguida", "Sangüesa/Zangoza": "Sangüesa", "Urdazubi/Urdax": "Urdax",
    "Uztárroz/Uztarroze": "Uztárroz", "Val de Goñi/Goñerri": "Val de Goñi", "Valle de Egüés/Eguesibar": "Valle de Egüés",
    "Valle de Ollo/Ollaran": "Valle de Ollo", "Valle de Yerri/Deierri": "Valle de Yerri", "Villava/Atarrabia": "Villava",
    "Zizur Mayor/Zizur Nagusia": "Zizur Mayor", "Ayala/Aiara": "Ayala", "Baños de Ebro/Mañueta": "Baños de Ebro",
    "Elvillar/Bilar": "Elvillar", "San Millán/Donemiliaga": "San Millán", "Monreal/Elo": "Monreal",
    "Puente la Reina/Gares": "Puente la Reina", "Pueyo/Puiu": "Pueyo",
}


def es_part(parts, raw):
    """Pick the Spanish half of a bilingual 'A/B' INE name."""
    if raw in ES_PICK:
        return next(p for p in parts if p == ES_PICK[raw])
    na, nb = (len(NON_ES.findall(p)) for p in parts)
    if na == nb:
        # INE convention in Catalan/Valencian/Galician/Basque areas: co-official first, Spanish second
        return parts[1]
    return parts[0] if na < nb else parts[1]


def load_ine(path):
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.worksheets[0]
    rows = list(ws.iter_rows(values_only=True))
    title = rows[0][0]
    head = rows[1]
    assert head[:5] == ("CODAUTO", "CPRO", "CMUN", "DC", "NOMBRE"), head
    out = [r for r in rows[2:] if r and r[1] and r[4]]
    return title, out


def main(xlsx):
    title, rows = load_ine(xlsx)
    regions = [r["slug"] for r in json.loads((ROOT / "data" / "2027.json").read_text("utf-8"))["regions"]]
    loc = json.loads((ROOT / "data" / "locales-2027.json").read_text("utf-8"))["cities"]

    munis = []
    for codauto, cpro, cmun, dc, nombre in [r[:5] for r in rows]:
        cpro, cmun = str(cpro).zfill(2), str(cmun).zfill(3)
        ine = cpro + cmun
        pname, pslug, region, capcode = PROVINCES[cpro]
        assert CODAUTO[str(codauto).zfill(2)] == region, (ine, codauto, region)
        raw = nombre.strip()
        if "/" in raw:
            parts = [front_article(p.strip()) for p in raw.split("/")]
            # second part may carry its own article ("Fondó de les Neus, el/Hondón de las Nieves")
            display = "/".join(parts)
            name_es = es_part(parts, raw)
        else:
            parts = [front_article(raw)]
            display = parts[0]
            name_es = NAME_ES.get(raw, parts[0])
        aliases = []
        for a in [raw, display, name_es, *parts, *(raw.split("/") if "/" in raw else []), *EXONYMS.get(raw, [])]:
            a = a.strip()
            if a and a.lower() not in {x.lower() for x in aliases} and a != display:
                aliases.append(a)
        # article-less form for common article names ("Rozas de Madrid" for "Las Rozas de Madrid")
        for p in parts:
            m = re.match(r"^(El|La|Los|Las|A|O|As|Os|Es|Sa|Ses|Els|Les) (.+)$", p)
            if m and m.group(2).lower() not in {x.lower() for x in aliases}:
                aliases.append(m.group(2))
            m = re.match(r"^[Ll]'(.+)$", p)
            if m and m.group(1).lower() not in {x.lower() for x in aliases}:
                aliases.append(m.group(1))
        aliases = [a for a in aliases if a.lower() != display.lower()]
        m = {
            "ine": ine, "name": display, "ine_name": raw, "name_es": name_es, "aliases": aliases,
            "slug": slugify(name_es), "province": pname, "province_slug": pslug, "province_code": cpro,
            "region": region, "capital": ine == capcode,
        }
        if region == "canarias":
            isl = next((k for k, v in ISLANDS.items() if display.lower() in {x.lower() for x in v}), None)
            m["island"] = isl or ("gran-canaria" if cpro == "35" else "tenerife")
        munis.append(m)

    missing = (set(EXONYMS) | set(ES_PICK) | set(NAME_ES)) - {m["ine_name"] for m in munis}
    assert not missing, missing
    missing = set(EXONYMS) - {m["ine_name"] for m in munis}
    assert not missing, missing

    # Reuse slugs from locales-2027.json
    def key(s):
        return slugify(s).replace("-", "")

    unmatched = []
    for c in loc:
        cands = [m for m in munis if m["region"] == c["region"] and (
            m["slug"] == c["slug"] or key(m["name_es"]) == key(c["name"]) or key(m["name"]) == key(c["name"])
            or any(key(a) == key(c["name"]) for a in m["aliases"]))]
        if len(cands) > 1:
            cands = [m for m in cands if m["province"] == c["province"]] or cands
        if len(cands) > 1:
            cands = [m for m in cands if m["slug"] == c["slug"]] or cands
        if len(cands) != 1:
            unmatched.append((c["region"], c["slug"], c["name"], [x["ine"] for x in cands]))
            continue
        m = cands[0]
        if m["province"] != c["province"]:
            unmatched.append((c["region"], c["slug"], c["name"], f"province {m['province']} != {c['province']}"))
            continue
        if m["slug"] != c["slug"]:
            m["slug"] = c["slug"]
        m["locales_2027"] = True

    # Unique slug within province
    seen = {}
    for m in munis:
        seen.setdefault((m["province_slug"], m["slug"]), []).append(m)
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    for (ps, s), ms in dups.items():
        for m in ms:
            if not m.get("locales_2027"):
                m["slug"] = f"{s}-{m['ine']}"
    for m in munis:
        m.pop("locales_2027", None)
    munis.sort(key=lambda m: m["ine"])

    # Validation
    assert len(munis) == len(rows)
    assert all(m["region"] in regions for m in munis)
    keys = [(m["province_slug"], m["slug"]) for m in munis]
    assert len(keys) == len(set(keys)), "duplicate province/slug"
    assert len({m["ine"] for m in munis}) == len(munis)
    caps = [m for m in munis if m["capital"]]
    assert len(caps) == 52, len(caps)

    provs = []
    for cpro, (pname, pslug, region, capcode) in PROVINCES.items():
        ms = [m for m in munis if m["province_code"] == cpro]
        cap = next(m for m in ms if m["ine"] == capcode)
        provs.append({"code": cpro, "name": pname, "slug": pslug, "aliases": PROVINCE_ALIASES.get(cpro, []),
                      "region": region, "capital_ine": capcode, "capital_name": cap["name"],
                      "municipios": len(ms)})

    meta = {"source": {"title": "INE, Relación de municipios y sus códigos por provincias",
                       "detail": title, "url": "https://www.ine.es/daco/daco42/codmun/" + Path(xlsx).name}}
    out = {**meta, "count": len(munis),
           "fields": {"ine": "CPRO+CMUN", "name": "nombre oficial INE con el artículo delante (bilingüe 'A/B' tal cual)",
                      "ine_name": "nombre tal como lo publica el INE", "name_es": "forma castellana usual",
                      "island": "solo Canarias: isla (slug de data/2027.json zones.canarias)"},
           "municipios": munis}
    add_population(out)
    write_munis(out)
    (ROOT / "data" / "provincias.json").write_text(
        json.dumps({**meta, "count": len(provs), "provincias": provs}, ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"{len(munis)} municipios, {len(provs)} provincias, {len(dups)} duplicate slugs disambiguated")
    for k, ms in dups.items():
        print("  dup", k, [(m["ine"], m["name"], m["slug"]) for m in ms])
    print("unmatched locales-2027 cities:", unmatched)
    isl = {}
    for m in munis:
        if "island" in m:
            isl[m["island"]] = isl.get(m["island"], 0) + 1
    print("islands", isl)
    assert isl == {"gran-canaria": 21, "fuerteventura": 6, "lanzarote": 7, "tenerife": 31, "la-gomera": 6, "la-palma": 14,
                   "el-hierro": 3}, isl


def add_population(out):
    """`pop` (INE official population, data/tools/poblacion.json from fetch_poblacion.py) on every municipality."""
    p = ROOT / "data" / "tools" / "poblacion.json"
    if not p.exists():
        print("no data/tools/poblacion.json: run fetch_poblacion.py for `pop`")
        return
    pj = json.loads(p.read_text("utf-8"))
    for m in out["municipios"]:
        m["pop"] = pj["pop"][m["ine"]]
    out["population"] = pj["source"]
    out["fields"]["pop"] = f'población oficial INE a {pj["source"]["date"]} (padrón)'
    # lat/lon: Wikidata (CC0), data/tools/coords.json from fetch_coords.py (outliers already dropped there)
    c = ROOT / "data" / "tools" / "coords.json"
    if c.exists():
        cj = json.loads(c.read_text("utf-8"))
        for m in out["municipios"]:
            m.pop("lat", None), m.pop("lon", None)
            if m["ine"] in cj["coords"]:
                m["lat"], m["lon"] = cj["coords"][m["ine"]]
        out["coordinates"] = cj["source"]
        out["fields"]["lat"] = "latitud/longitud del municipio (Wikidata P625, CC0)"


def write_munis(out):
    head = json.dumps({k: v for k, v in out.items() if k != "municipios"}, ensure_ascii=False, indent=1)[:-2]
    lines = ",\n".join(json.dumps(m, ensure_ascii=False, separators=(",", ":")) for m in out["municipios"])
    (ROOT / "data" / "municipios.json").write_text(f'{head},\n "municipios": [\n{lines}\n]}}\n', "utf-8", newline="\n")


if __name__ == "__main__":
    if sys.argv[1] == "--pop":  # only add or refresh `pop` in the existing data/municipios.json (no xlsx needed)
        cur = json.loads((ROOT / "data" / "municipios.json").read_text("utf-8"))
        add_population(cur)
        write_munis(cur)
        print(len(cur["municipios"]), "municipios with pop")
    else:
        main(sys.argv[1])
