"""Shared bits of the students and teachers pack (pack I, batch b1112): the hub category and two JavaScript snippets
pasted at the top of compute functions. Not a tool (leading underscore: the registry skips it).

    NUMS  nums(s): '7,5 6; 8.25, 9' -> [7.5, 6, 8.25, 9]; spaces or ';' separate, the comma is a decimal sign
          (a token with two commas, '7,5,6', or a trailing comma, '7.5,', is split on commas); junk -> NaN items
    RNG   seeded(str): a Mulberry32 generator seeded with the FNV-1a hash of str; rnd() in [0, 1), int(n) in [0, n)
          The same seed string always gives the same sheet, so a shared link reproduces it.
"""

CAT = ("estudios", "Estudiantes y docentes")

NUMS = r"""
  function nums(s) {
    var out = [];
    String(s == null ? '' : s).split(/[;\s|]+/).forEach(function (t) {
      t = t.replace(/^,+|,+$/g, '');
      if (!t) return;
      var parts = (t.match(/,/g) || []).length > 1 ? t.split(',') : [t];
      parts.forEach(function (p) { if (p) out.push(H.val(p)); });
    });
    return out;
  }
"""

RNG = r"""
  function seeded(str) {
    var h = 2166136261, i;
    for (i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 16777619) >>> 0; }
    function rnd() { h = (h + 0x6D2B79F5) >>> 0; var t = h; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }
    return { rnd: rnd, int: function (n) { return Math.floor(rnd() * n); } };
  }
  var NEWSEED = '<button type="button" class="btn" onclick="var s=document.getElementById(\'ficha\');s.value=1+Math.floor(Math.random()*9999);s.dispatchEvent(new Event(\'input\',{bubbles:true}))">Otra ficha</button>';
"""

MULBERRY = ("Mulberry32 PRNG (Tommy Ettinger)", "dominio público (CC0)", "https://gist.github.com/tommyettinger/46a874533244883189143505d203312c")


def js(body, *snips):
    """function (v, H, C) { <snippets> <body> }"""
    return "function (v, H, C) {\n" + "".join(snips) + body + "\n}"
