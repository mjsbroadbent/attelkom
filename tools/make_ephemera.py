"""Draws the 1999-style buttons, counter and header for the old front page.

    python3 tools/make_ephemera.py
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
D = "/usr/share/fonts/truetype/dejavu/"
L = "/usr/share/fonts/truetype/liberation/"


def F(name, size):
    return ImageFont.truetype(name, size)


def draw(im):
    d = ImageDraw.Draw(im)
    d.fontmode = "1"                      # no antialiasing: jagged like the real thing
    return d


def bevel(d, w, h, light="#ffffff", dark="#404040"):
    d.line([(0, h - 1), (0, 0), (w - 1, 0)], fill=light)
    d.line([(1, h - 1), (w - 1, h - 1), (w - 1, 1)], fill=dark)


def save_gif(frames, path, ms):
    frames = [f.convert("P", palette=Image.ADAPTIVE, colors=32) for f in frames]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if len(frames) == 1:
        frames[0].save(path)
    else:
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=ms, loop=0)


def button(path, left_bg, left_text, right_bg, lines, right_fg="#000000", blink=None):
    """Classic 88x31 split button: a coloured box on the left, two lines on the right."""
    frames = []
    for k in range(2 if blink else 1):
        im = Image.new("RGB", (88, 31), right_bg)
        d = draw(im)
        d.rectangle((0, 0, 25, 30), fill=left_bg if not (blink and k) else blink)
        for i, t in enumerate(left_text):
            d.text((13, 9 + i * 12 if len(left_text) > 1 else 15), t, font=F(D + "DejaVuSansCondensed-Bold.ttf", 9), fill="#ffffff", anchor="mm")
        for i, t in enumerate(lines):
            d.text((29, 4 + i * 12), t, font=F(D + "DejaVuSansCondensed-Bold.ttf" if i == 0 else D + "DejaVuSansCondensed.ttf", 9), fill=right_fg)
        d.rectangle((0, 0, 87, 30), outline="#000000")
        frames.append(im)
    save_gif(frames, path, 500)


def counter(path, n="0041273"):
    w = 13 * len(n) + 4
    im = Image.new("RGB", (w, 20), "#000000")
    d = draw(im)
    for i, ch in enumerate(n):
        x = 2 + i * 13
        d.rectangle((x, 2, x + 11, 17), fill="#222222", outline="#555555")
        d.text((x + 6, 10), ch, font=F(L + "LiberationMono-Bold.ttf", 14), fill="#ff3030" if i == len(n) - 1 else "#33ff33", anchor="mm")
    save_gif([im], path, 0)


def header(path):
    """The 443x118 header the page has always asked for: teal bar, phone number, tagline."""
    im = Image.new("RGB", (443, 118), "#003333")
    d = ImageDraw.Draw(im)
    for y in range(118):
        d.line([(0, y), (442, y)], fill=(0, 51 + y // 4, 51 + y // 4))
    d.text((221, 34), "Attelkom Online", font=F(L + "LiberationSerif-BoldItalic.ttf", 36), fill="#FFCC00", anchor="mm")
    d.text((221, 72), "Irad's #1 Internet Service Provider", font=F(L + "LiberationSans-Bold.ttf", 15), fill="#ffffff", anchor="mm")
    d.text((221, 98), "Dial-up help 24 hrs:  2-19-96  |  Toll free 1-800-864-7378", font=F(L + "LiberationSans-Regular.ttf", 12), fill="#99dddd", anchor="mm")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, quality=60)                  # a little JPEG crunch


def spinning_globe(path):
    """A tiny 'internet' globe that turns: the most 1999 thing there is."""
    frames = []
    for k in range(8):
        im = Image.new("RGB", (32, 32), "#ffffff")
        d = ImageDraw.Draw(im)
        d.ellipse((2, 2, 29, 29), fill="#1060d0", outline="#003080")
        for j in range(3):                     # land blobs sliding across
            x = (k * 4 + j * 11) % 34 - 4
            d.ellipse((x, 6 + j * 7, x + 9, 12 + j * 7), fill="#30b030")
        mask = Image.new("L", (32, 32), 0)
        ImageDraw.Draw(mask).ellipse((2, 2, 29, 29), fill=255)
        bg = Image.new("RGB", (32, 32), "#ffffff")
        bg.paste(im, (0, 0), mask)
        ImageDraw.Draw(bg).ellipse((2, 2, 29, 29), outline="#003080")
        ImageDraw.Draw(bg).arc((8, 6, 16, 14), 180, 270, fill="#ffffff")
        frames.append(bg)
    save_gif(frames, path, 120)


def mailbox(path):
    frames = []
    for k in range(2):
        im = Image.new("RGB", (36, 26), "#ffffff")
        d = draw(im)
        d.rectangle((4, 6, 31, 22), fill="#ffffff", outline="#000080", width=2)
        d.line([(4, 6), (17, 15), (31, 6)], fill="#000080", width=2)
        if k:
            d.ellipse((26, 1, 35, 10), fill="#ff0000")
            d.text((30, 5), "1", font=F(D + "DejaVuSans-Bold.ttf", 8), fill="#ffffff", anchor="mm")
        frames.append(im)
    save_gif(frames, path, 500)


def main():
    b = os.path.join(IMG, "badges")
    button(os.path.join(b, "y2k.gif"), "#008000", ["Y2K"], "#ffffff", ["Y2K READY", "Attelkom"], blink="#00c000")
    button(os.path.join(b, "800x600.gif"), "#000080", ["800", "x600"], "#c0c0c0", ["Best seen", "800x600"])
    button(os.path.join(b, "v90.gif"), "#cc0000", ["56K"], "#ffff99", ["V.90 now", "in Talas!"], blink="#ff6600")
    button(os.path.join(b, "handmade.gif"), "#663300", ["</>"], "#ffffff", ["HTML by", "hand!"])
    button(os.path.join(b, "iradi.gif"), "#b0001e", ["IRAD"], "#ffffff", ["Proudly", "Iradi!"])
    button(os.path.join(b, "nofrontpage.gif"), "#404040", ["NO"], "#e0e0e0", ["No frames", "No Java"])
    counter(os.path.join(IMG, "counter.gif"))
    # the header image (images/header/header2.jpg) is left missing on purpose: a broken image is part of the look
    spinning_globe(os.path.join(IMG, "globe.gif"))
    mailbox(os.path.join(IMG, "mail.gif"))
    print("done")


if __name__ == "__main__":
    main()
