#!/usr/bin/env python3
"""The lock screen plate: hewn stone, in the manner of Moria.

Built as a height field first -- masonry courses, chisel bite, carved runes --
then lit from a single raking source so every recess casts its own shadow.
The colour goes on last, so the relief reads as stone rather than as a texture
laid over a flat fill.
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RUNIC = "/usr/share/fonts/noto/NotoSansRunic-Regular.ttf"
sys.path.insert(0, __import__("os").path.dirname(os.path.abspath(__file__)))
from futhorc import to_futhorc

PALETTES = {
    # stone in shadow, stone in light, the warm lamp standing in the room
    "dark":  dict(low=(13, 17, 16), high=(74, 80, 74), lamp=(198, 156, 86),
                  lamp_strength=0.10, ambient=0.26, gamma=1.0),
    "light": dict(low=(108, 100, 84), high=(214, 204, 180), lamp=(158, 111, 34),
                  lamp_strength=0.09, ambient=0.50, gamma=0.94),
}


def value_noise(w, h, res, seed):
    """Smooth noise by upsampling a coarse random grid."""
    rng = np.random.default_rng(seed)
    small = rng.random((res + 1, res + 1))
    img = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(img, dtype=np.float64) / 255.0


def fbm(w, h, seed, octaves=6, res0=3):
    """Fractal noise: the rough shape of the rock."""
    out = np.zeros((h, w))
    amp, res, total = 1.0, res0, 0.0
    for o in range(octaves):
        out += amp * value_noise(w, h, res, seed + o * 101)
        total += amp
        amp *= 0.5
        res *= 2
    return out / total


def masonry(w, h, seed, courses=7):
    """Staggered courses of dressed blocks, mortar recessed between them."""
    rng = np.random.default_rng(seed)
    field = np.zeros((h, w))
    tone = np.ones((h, w))
    mortar = np.zeros((h, w), dtype=bool)
    ch = h // courses
    for c in range(courses + 1):
        y0, y1 = c * ch, min(h, (c + 1) * ch)
        if y0 >= h:
            break
        # each course sits a touch proud or shy of its neighbours
        field[y0:y1, :] += rng.uniform(-0.05, 0.05)
        mortar[max(0, y0 - 5):y0 + 5, :] = True
        x = -int(rng.uniform(0, 380))          # stagger the vertical joints
        while x < w:
            bw = int(rng.uniform(300, 620))
            if x > 0:
                mortar[y0:y1, max(0, x - 5):x + 5] = True
            # every block takes the chisel slightly differently
            field[y0:y1, max(0, x):min(w, x + bw)] += rng.uniform(-0.04, 0.04)
            tone[y0:y1, max(0, x):min(w, x + bw)] = rng.uniform(0.90, 1.10)
            x += bw
    return field, mortar, tone


def carve_runes(w, h, text, size, y, alpha=1.0):
    """A rune band as a mask, for subtracting from the height field."""
    layer = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(RUNIC, size)
    tw = d.textlength(text, font=f)
    d.text(((w - tw) / 2, y), text, font=f, fill=int(255 * alpha))
    return np.asarray(layer.filter(ImageFilter.GaussianBlur(2)), dtype=np.float64) / 255.0


def plate(W, H, out, variant="dark"):
    pal = PALETTES[variant]

    # ---- height field -------------------------------------------------
    rock = fbm(W, H, seed=11, octaves=7, res0=3)
    grit = fbm(W, H, seed=77, octaves=4, res0=140)      # fine chisel bite
    blocks, mortar, blocktone = masonry(W, H, seed=5)

    height = rock * 0.55 + grit * 0.22 + blocks
    height[mortar] -= 0.32                              # joints fall away

    # runes cut into the stone, high above and below the centre
    band_top = to_futhorc("The doors of Durin Lord of Moria")
    band_bot = to_futhorc("Speak friend and enter")
    height -= carve_runes(W, H, band_top, int(H * 0.036), int(H * 0.20), 0.9) * 0.42
    height -= carve_runes(W, H, band_bot, int(H * 0.036), int(H * 0.775), 0.9) * 0.42

    height = np.clip(height, 0, None)
    height = np.asarray(
        Image.fromarray((np.clip(height, 0, 1) * 255).astype(np.uint8))
        .filter(ImageFilter.GaussianBlur(1.1)), dtype=np.float64) / 255.0

    # ---- light it ------------------------------------------------------
    # A single raking source high on the left: recesses shadow, edges catch.
    gy, gx = np.gradient(height * 42.0)
    lx, ly, lz = -0.55, -0.68, 0.49
    norm = np.sqrt(gx * gx + gy * gy + 1.0)
    lam = np.clip((-gx * lx - gy * ly + lz) / norm, 0, 1)
    shade = pal["ambient"] + (1.0 - pal["ambient"]) * lam ** 1.35
    shade *= 0.80 + 0.34 * height                       # proud stone reads brighter

    # ---- colour --------------------------------------------------------
    low = np.array(pal["low"], dtype=np.float64)
    high = np.array(pal["high"], dtype=np.float64)
    rgb = low[None, None, :] + (high - low)[None, None, :] * shade[:, :, None]

    # a mineral drift across the wall so it is never one flat grey
    tint = fbm(W, H, seed=303, octaves=4, res0=2)[:, :, None]
    rgb *= 0.90 + 0.20 * tint
    # soften the per-block tone at its edges so the joints do not read as a grid
    bt = np.asarray(Image.fromarray((blocktone * 200).astype(np.uint8))
                    .filter(ImageFilter.GaussianBlur(9)), dtype=np.float64) / 200.0
    # ...and settle it back to plain stone across the middle, so a stray dark
    # block never lands behind the emblem and swallows the inscription.
    yy, xx = np.mgrid[0:H, 0:W]
    calm = np.clip(np.sqrt(((xx - W / 2) / (W * 0.26)) ** 2
                           + ((yy - H * 0.50) / (H * 0.40)) ** 2), 0, 1)
    bt = 1.0 + (bt - 1.0) * calm
    rgb *= bt[:, :, None]

    # ---- lamplight standing in the middle of the room -------------------
    r = np.sqrt(((xx - W * 0.42) / (W * 0.95)) ** 2 + ((yy - H * 0.30) / (H * 1.05)) ** 2)
    pool = np.clip(1.0 - r, 0, 1) ** 1.5
    lamp = np.array(pal["lamp"], dtype=np.float64)
    rgb += lamp[None, None, :] * (pool * pal["lamp_strength"])[:, :, None]

    # ---- vignette -------------------------------------------------------
    v = np.clip(1.0 - (np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2
                               + ((yy - H / 2) / (H * 0.72)) ** 2) - 0.55) * 0.95, 0.34, 1.0)
    rgb *= v[:, :, None]

    rgb = np.clip(rgb, 0, 255) ** pal["gamma"] if pal["gamma"] != 1.0 else np.clip(rgb, 0, 255)
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB")
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=45, threshold=3))
    img.save(out)
    print("wrote", out, img.size)


if __name__ == "__main__":
    plate(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
          sys.argv[4] if len(sys.argv) > 4 else "dark")
