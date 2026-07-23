#!/usr/bin/env python3
"""Convierte una foto en avatar ASCII y duotone violeta (tema Eclipse)."""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

FONT_PATH = "/System/Library/Fonts/Menlo.ttc"
BG = (13, 1, 23)          # #0d0117 negro-violeta
# rampa de caracteres de oscuro -> claro
RAMP = " .:-=+*#%@"
# rampa de color violeta: oscuro -> neon -> claro
VIOLET = [(27, 15, 43), (59, 29, 94), (109, 40, 217), (168, 85, 247), (216, 180, 254), (240, 230, 255)]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def violet_ramp(v):  # v en 0..1
    if v <= 0:
        return VIOLET[0]
    if v >= 1:
        return VIOLET[-1]
    seg = v * (len(VIOLET) - 1)
    i = int(seg)
    return lerp(VIOLET[i], VIOLET[i + 1], seg - i)


CROP = None      # (left, top, right, bottom) o None
CONTRAST = 1.6


def _crop(img):
    return img.crop(CROP) if CROP else img


def prep(img, cols):
    g = ImageOps.grayscale(_crop(img))
    g = ImageOps.autocontrast(g, cutoff=3)
    g = ImageEnhance.Contrast(g).enhance(CONTRAST)
    w, h = g.size
    ratio = h / w
    rows = int(cols * ratio * 0.5)  # los chars son ~2x más altos que anchos
    return g.resize((cols, rows)), cols, rows


def make_ascii(src, out, cols=150):
    img = Image.open(src).convert("RGB")
    g, cols, rows = prep(img, cols)
    px = g.load()
    cw, ch = 9, 18
    font = ImageFont.truetype(FONT_PATH, 16)
    canvas = Image.new("RGB", (cols * cw + 40, rows * ch + 40), BG)
    d = ImageDraw.Draw(canvas)
    for y in range(rows):
        for x in range(cols):
            v = px[x, y] / 255
            ch_i = min(len(RAMP) - 1, int(v * len(RAMP)))
            c = RAMP[ch_i]
            if c == " ":
                continue
            d.text((20 + x * cw, 20 + y * ch), c, font=font, fill=violet_ramp(v))
    canvas.save(out)
    print("ascii ->", out, canvas.size)


def make_duotone(src, out, width=720):
    img = Image.open(src).convert("RGB")
    g = ImageOps.grayscale(_crop(img))
    g = ImageOps.autocontrast(g, cutoff=3)
    g = ImageEnhance.Contrast(g).enhance(CONTRAST)
    w, h = g.size
    nh = int(width * h / w)
    g = g.resize((width, nh))
    px = g.load()
    canvas = Image.new("RGB", (width, nh), BG)
    cpx = canvas.load()
    for y in range(nh):
        for x in range(width):
            cpx[x, y] = violet_ramp(px[x, y] / 255)
    canvas.save(out)
    print("duotone ->", out, canvas.size)


if __name__ == "__main__":
    src = sys.argv[1]
    stem = sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3] != "-":
        CROP = tuple(int(v) for v in sys.argv[3].split(","))
    print("size:", Image.open(src).size, "crop:", CROP)
    make_ascii(src, f"{stem}_ascii.png")
    make_duotone(src, f"{stem}_duotone.png")
