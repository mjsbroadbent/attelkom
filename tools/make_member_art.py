"""Redraws a few images on member sites (October 2026):
- users/Marat4086/logo.gif: the Akyel Syndicate logo, done the way a 1998 office PC would in CorelDRAW
- users/Bolot7720/goat.gif and goat_small.gif: the KARA-BUURA goat as a bouncing cartoon clip-art GIF

    python3 tools/make_member_art.py
Needs the jarnama repo next to this one (its tools/banner.py and stock/akyel.png).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "..", "jarnama", "tools"))
from banner import *  # noqa
from PIL import Image, ImageChops, ImageDraw, ImageFilter

U = os.path.join(HERE, "users")


def akyel_logo():
    src = Image.open(os.path.join(HERE, "..", "jarnama", "stock", "akyel.png")).convert("RGB")
    alpha = trim(cutout(src, thresh=205)).getchannel("A").point(lambda v: 255 if v > 128 else 0)
    W, H, S = 170, 120, 3
    im = Image.new("RGB", (W * S, H * S))
    gradient(im, (0, 0, W * S, H * S), "#0e4d1e", "#03260c")
    d = ImageDraw.Draw(im)
    ov = (8 * S, 4 * S, (W - 8) * S, 82 * S)
    d.ellipse((ov[0] + 3 * S, ov[1] + 3 * S, ov[2] + 3 * S, ov[3] + 3 * S), fill="#011a07")
    d.ellipse(ov, fill="#d9b44a")
    d.ellipse((ov[0] + 3 * S, ov[1] + 3 * S, ov[2] - 3 * S, ov[3] - 3 * S), fill="#0b3a16")
    d.ellipse((ov[0] + 5 * S, ov[1] + 5 * S, ov[2] - 5 * S, ov[3] - 5 * S), outline="#8a6d1f", width=S)
    hh = 66 * S
    hw = round(alpha.width * hh / alpha.height)
    m = alpha.resize((hw, hh), Image.LANCZOS)
    gold = Image.new("RGB", (hw, hh))
    gradient(gold, (0, 0, hw, hh), "#fff2b0", "#b07a12")
    x0, y0 = (W * S - hw) // 2, 10 * S
    im.paste((20, 10, 0), (x0, y0), m.filter(ImageFilter.MaxFilter(7)))
    im.paste(gold, (x0, y0), m)
    hi = ImageChops.subtract(m, m.transform(m.size, Image.AFFINE, (1, 0, 4, 0, 1, 4))).filter(ImageFilter.GaussianBlur(2))
    im.paste((255, 255, 230), (x0, y0), hi)
    im = im.resize((W, H), Image.LANCZOS)
    text(im, (W // 2 + 2, 100), "AKYEL", font("timesb", 22), "#000000", anchor="mm")       # drop shadow
    gradient_text(im, (W // 2, 98), "AKYEL", font("timesb", 22), "#fff6c0", "#c08a00", outline="#3a2a00", anchor="mm")
    text(im, (W // 2, 114), "EQUINE  LOGISTICS  &  BREEDING", font("arial", 7, pixel=True), "#e8d48a", anchor="mm")
    im.convert("P", palette=Image.ADAPTIVE, colors=64, dither=Image.Dither.FLOYDSTEINBERG).save(os.path.join(U, "Marat4086", "logo.gif"))


def goat_frame(t, size, bg, bleat=False):
    """Cartoon clip-art goat: thick black outlines, flat fills, one highlight. Drawn at 4x."""
    S = 4
    w, h = size
    W, H = w * S, h * S
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)
    k = W / 440.0                                       # design space is 440 x 384
    hop = abs(math.sin(math.pi * t)) * 28
    def P(x, y):
        return (x * k, (y - hop) * k)
    def E(x0, y0, x1, y1, **kw):
        d.ellipse([*P(x0, y0), *P(x1, y1)], **kw)
    ol = dict(outline="#000000", width=int(7 * k))
    swing = 22 * math.sin(2 * math.pi * t)
    # shadow on the ground (does not hop)
    d.ellipse((110 * k, 345 * k, 330 * k, 372 * k), fill="#1a0000")
    # legs (back pair darker)
    for x, s, col in ((150, -1, "#cfc3a8"), (290, 1, "#cfc3a8"), (175, 1, "#f2ead6"), (265, -1, "#f2ead6")):
        dx = s * swing * 0.6
        d.line([P(x, 250), P(x + dx, 330)], fill="#000000", width=int(30 * k))
        d.line([P(x, 250), P(x + dx, 330)], fill=col, width=int(17 * k))
        E(x + dx - 16, 318, x + dx + 16, 342, fill="#3a2a1a", **ol)        # hooves
    # tail
    d.polygon([P(105, 175), P(70, 140 - swing * 0.5), P(98, 190)], fill="#f2ead6", outline="#000000")
    # body
    E(95, 150, 335, 275, fill="#f2ead6", **ol)
    E(150, 165, 230, 195, fill="#ffffff")                              # highlight
    E(200, 215, 250, 245, fill="#bfb090")                              # a brown patch
    # neck + head
    d.polygon([P(290, 175), P(330, 110), P(360, 120), P(335, 200)], fill="#f2ead6")
    E(305, 70, 405, 160, fill="#f2ead6", **ol)
    d.line([P(290, 175), P(330, 108)], fill="#000000", width=int(7 * k))
    # horns (curved back)
    for dx in (0, 22):
        d.arc([*P(300 + dx, 30), *P(360 + dx, 110)], 180, 300, fill="#000000", width=int(18 * k))
        d.arc([*P(300 + dx, 30), *P(360 + dx, 110)], 185, 295, fill="#a08850", width=int(9 * k))
    # ear
    d.polygon([P(318, 92), P(270, 98), P(312, 112)], fill="#d8cdb2", outline="#000000")
    # eye (blinks on the bleat frame)
    if bleat:
        d.line([P(352, 98), P(372, 98)], fill="#000000", width=int(6 * k))
    else:
        E(350, 86, 374, 112, fill="#ffffff", outline="#000000", width=int(4 * k))
        E(361, 94, 371, 106, fill="#000000")
    # beard
    d.polygon([P(370, 150), P(395, 150), P(380, 195)], fill="#e6dcc4", outline="#000000")
    # mouth / bleat
    if bleat:
        E(388, 128, 410, 148, fill="#7a1010", outline="#000000", width=int(4 * k))
    else:
        d.arc([*P(380, 125), *P(402, 142)], 20, 160, fill="#000000", width=int(4 * k))
    E(392, 112, 400, 120, fill="#000000")                              # nostril
    # hard-edged transparency: anything that isn't the key colour at 4x counts as goat
    key = Image.new("RGB", (W, H), bg)
    mask = ImageChops.difference(im, key).convert("L").point(lambda v: 255 if v > 8 else 0)
    halo = mask.filter(ImageFilter.MaxFilter(13 if w > 80 else 9))          # white sticker border, clip-art style
    matte = Image.new("RGB", (W, H), (255, 255, 255))
    matte.paste(im, (0, 0), mask)
    matte.paste((40, 0, 0), (0, 0), ImageChops.invert(halo))
    mask = halo
    im = matte.resize((w, h), Image.LANCZOS)
    mask = mask.resize((w, h), Image.BOX).point(lambda v: 255 if v > 110 else 0)
    im.putalpha(mask)
    if bleat and w > 80:
        text(im, (w - 4, 6), "MEEE!", font("verdanab", 10, pixel=True), "#cc0000", anchor="ra")
    return im


def goats():
    for name, size in (("goat.gif", (110, 96)), ("goat_small.gif", (55, 48))):
        frames = [goat_frame(i / 8, size, "#ff00ff", bleat=(i == 7)) for i in range(8)]
        # one shared palette, index 0 kept for transparency
        strip = Image.new("RGB", (size[0], size[1] * 8), (40, 0, 0))
        for i, f in enumerate(frames):
            strip.paste(f.convert("RGB"), (0, i * size[1]), f)
        pal = strip.quantize(31)
        out = []
        for f in frames:
            q = f.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE)
            q = q.point(lambda i: i + 1)
            q.putpalette([255, 0, 255] + pal.getpalette()[:31 * 3])
            q.paste(0, (0, 0), ImageChops.invert(f.getchannel("A")))
            out.append(q)
        out[0].save(os.path.join(U, "Bolot7720", name), save_all=True, append_images=out[1:],
                    duration=[110] * 7 + [500], loop=0, disposal=2, transparency=0)


if __name__ == "__main__":
    akyel_logo()
    goats()
    print("ok")
