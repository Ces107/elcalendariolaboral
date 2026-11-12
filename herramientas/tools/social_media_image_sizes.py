"""Image sizes for sellers and creators (Etsy, Pinterest, Instagram, YouTube, Amazon KDP and A+), with the centre crop of
your photo and the resize factor. Spanish twin: tamanos_imagen_redes.py. Data in _sellers.IMG."""
from herramientas.tools import _sellers as S


def blocks(ctx):
    return [
        ("Every size in one table", f"""
<p>These are the sizes each platform recommends as of November 2026, in pixels (width × height). Pick a destination above
and enter your photo's size: the tool tells you how much to trim from the sides or from top and bottom to hit the right
aspect ratio, and whether you then need to shrink it or are short of pixels.</p>
{S.img_table("en")}"""),
        ("Worked example: a phone photo", """
<p>Most phones shoot 4032 × 3024 px (4:3). For an <b>Etsy listing photo</b> at 4:3 nothing is cropped: shrink it to 66% to
get 2667 × 2000 and keep the file under 1 MB. For a <b>Pinterest pin</b> (2:3, portrait) you keep only a central strip of
2016 × 3024, throwing away half the picture, so shoot portrait from the start. For a <b>YouTube thumbnail</b> (16:9) you
trim 378 px from the top and the same from the bottom; if the photo were only 1920 × 1080 you would have to double it to
reach 3840 × 2160 and it would go soft, so start from a large image.</p>"""),
        ("Keep the important part safe", f"""
<p>Etsy shows the same photo cropped to square, portrait and landscape depending on the page, so leave space around the
product and never run text to the edges (<a href="{S.ETSY_IMG}" rel="noopener">Etsy's image guide</a>). On a YouTube banner
only the central 1,546 × 423 px shows on every device: logo and text go there. Instagram's profile grid shows posts cropped
to portrait, so keep the subject centred. For a Kindle eBook cover KDP recommends 1600 × 2560 px (<a href="{S.KDP_EBCOVER}"
rel="noopener">KDP help</a>), and A+ modules take JPG or PNG files up to 3 MB.</p>"""),
    ]


FAQ = [
    ("What size should Etsy listing photos be?",
     "At least 2,000 px wide and tall, with the first photo landscape or square. At 4:3, 2667 × 2000 px. Below 635 px Etsy "
     "ranks the listing lower."),
    ("What is the best Pinterest pin size?",
     "1000 × 1500 px, a 2:3 ratio. Wider pins may be cropped in the feed."),
    ("What size is a YouTube thumbnail?",
     "16:9; YouTube recommends 3840 × 2160 px with a minimum width of 640 px. From a phone the file can be at most 2 MB."),
    ("What size is an Instagram story?",
     "1080 × 1920 px, a 9:16 ratio, the same as reels."),
    ("What size is a KDP eBook cover?",
     "1600 × 2560 px (width × height), front cover only."),
]

JS = r"""
function (v, H, C) {
""" + S.IMG_JS + r"""
  var t = C.d[v.dest], tw = t[0], th = t[1], n = function (x) { return String(Math.round(x)).replace(/\B(?=(\d{3})+(?!\d))/g, ','); };
  var out = { label: H.esc(t[3]), big: n(tw) + ' × ' + n(th) + ' px', sub: 'Aspect ratio ' + (tw / th).toFixed(2) + ':1', n: { tw: tw, th: th } };
  if (t[2]) out.note = H.esc(t[2]);
  var iw = v.iw, ih = v.ih;
  if (!(iw > 0 && ih > 0)) return out;
  if (iw % 1 || ih % 1 || iw > 100000 || ih > 100000) return { err: 'Enter your image size in whole pixels.' };
  var c = crop(iw, ih, tw, th);
  out.rows = [['Centre crop', n(c.cw) + ' × ' + n(c.ch) + ' px'],
    ['Trimmed', c.lost < 0.001 ? 'Nothing' : Math.round(c.lost * 100) + '% · ' + (c.x ? n(c.x) + ' px each side' : n(c.y) + ' px top and bottom')],
    [c.k <= 1 ? 'Resize to' : 'Enlarge', c.k <= 1 ? Math.round(c.k * 100) + '%' : '× ' + c.k.toFixed(2) + ' · loses sharpness', c.k > 1 ? 'z' : 'tot']];
  out.html = cropSvg(iw, ih, c, 'Crop on your image');
  out.n.cw = c.cw; out.n.ch = c.ch; out.n.k = c.k;
  return out;
}
"""

TOOL = {
    "slug": "social-media-image-sizes",
    "lang": "en",
    "twin": "tamanos-imagen-redes",
    "cat": "sellers",
    "icon": "photo",
    "order": 90,
    "name": "Image size guide",
    "k": "etsy photo size pinterest pin instagram youtube thumbnail banner kdp a+ pixels",
    "title": "Image Sizes 2026: Etsy, Pinterest, Instagram, YouTube, KDP",
    "desc": "Pixel sizes for Etsy listing photos and banners, Pinterest pins, Instagram posts and stories, YouTube thumbnails and KDP covers, with your exact crop.",
    "h1": "Image sizes for Etsy, social media and KDP",
    "updated": "2026-11-12",
    "inputs": [
        {"id": "dest", "type": "select", "label": "Destination", "value": "etsy-foto", "options": [(r[0], r[1] + " · " + r[3]) for r in S.IMG]},
        {"id": "iw", "type": "number", "label": "Your width", "value": "4032", "unit": "px", "w": "s"},
        {"id": "ih", "type": "number", "label": "Your height", "value": "3024", "unit": "px", "w": "s"},
    ],
    "data": lambda ctx: S.img_data("en"),
    "js": JS,
    "css": S.IMG_CSS,
    "blocks": blocks,
    "faq": FAQ,
    "sources": [("Etsy · Image requirements", S.ETSY_IMG), ("Pinterest · Product specs", S.PINTEREST),
                ("YouTube · Custom thumbnails", S.YT_THUMB), ("Instagram · Photo resolution", S.INSTAGRAM),
                ("KDP · eBook cover", S.KDP_EBCOVER), ("KDP · A+ Content", S.KDP_APLUS)],
    "related": ["etsy-listing-checker", "kdp-cover-calculator", "etsy-fee-calculator"],
    "tests": [
        ({}, {"n.tw": 2667, "n.cw": 4032, "n.k": 0.661458}),
        ({"dest": "pin"}, {"n.cw": 2016, "n.ch": 3024}),
        ({"dest": "yt-thumb", "iw": "1920", "ih": "1080"}, {"n.k": 2}),
        ({"dest": "kdp-ebook", "iw": ""}, {"n.tw": 1600, "n.th": 2560}),
        ({"ih": "-5"}, {"n.tw": 2667}),
    ],
}
