#!/usr/bin/env python3
"""The Durin's Gate plate: an arch of mithril on Mirkwood dark, ringed with
Anglo-Saxon futhorc -- the runes Tolkien used for the dwarves in The Hobbit."""
import math, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from futhorc import to_futhorc
from tengwar import transcribe

RUNIC   = "/usr/share/fonts/noto/NotoSansRunic-Regular.ttf"
TENGWAR = "/usr/share/fonts/TTF/tngan.ttf"

PALETTES = {
    # line colour, gilt, darkest field, lit field, warmth of the door-glow
    "dark":  dict(ink=(231, 214, 182), gilt=(214, 172,  92),
                  deep=(16, 20, 20), ground=(28, 35, 33),
                  glow=(214, 172, 92), glow_alpha=13, lift=1.35),
    "light": dict(ink=(107,  75,  47), gilt=(158, 111,  34),
                  deep=(222, 200, 160), ground=(245, 233, 206),
                  glow=(107, 75, 47), glow_alpha=15, lift=1.0),
}

S = 2  # supersample


def radial_ground(w, h, DEEP, GROUND, LIFT):
    """Mirkwood dark, lit faintly from behind the arch."""
    img = Image.new("RGB", (w, h), DEEP)
    px = img.load()
    cx, cy = w * 0.5, h * 0.60
    maxd = math.hypot(w * 0.5, h * 0.5)
    for y in range(h):
        for x in range(0, w, 4):
            d = math.hypot(x - cx, y - cy) / maxd
            t = max(0.0, 1.0 - d) ** 2.2
            c = tuple(min(255, int(DEEP[i] + (GROUND[i] - DEEP[i]) * t * LIFT))
                      for i in range(3))
            for k in range(4):
                if x + k < w:
                    px[x + k, y] = c
    return img


def arc_text(layer, text, font, cx, cy, r, start_deg, end_deg, fill, flip=False):
    """Set text along a circular arc, one glyph at a time."""
    d = ImageDraw.Draw(layer)
    widths = [d.textlength(ch, font=font) for ch in text]
    total = sum(widths)
    span = math.radians(end_deg - start_deg)
    ang = math.radians(start_deg)
    for ch, w in zip(text, widths):
        step = span * (w / total)
        a = ang + step / 2
        gx, gy = cx + r * math.cos(a), cy + r * math.sin(a)
        g = Image.new("RGBA", (int(w) + 40, font.size * 2), (0, 0, 0, 0))
        ImageDraw.Draw(g).text((20, font.size // 2), ch, font=font, fill=fill)
        rot = math.degrees(a) + (90 if flip else -90)
        g = g.rotate(-rot, resample=Image.BICUBIC, expand=True)
        layer.alpha_composite(g, (int(gx - g.width / 2), int(gy - g.height / 2)))
        ang += step


def star_of_feanor(d, cx, cy, r, fill, width):
    """Eight rays, the long four and the short four, as on the West-gate."""
    for i in range(8):
        a = math.radians(i * 45 - 90)
        rr = r if i % 2 == 0 else r * 0.62
        d.line([cx, cy, cx + rr * math.cos(a), cy + rr * math.sin(a)], fill=fill, width=width)
    d.ellipse([cx - r * .11, cy - r * .11, cx + r * .11, cy + r * .11], fill=fill)


def plate(W, H, out, variant="dark"):
    pal = PALETTES[variant]
    MITHRIL, GOLD, DEEP, GROUND, GLOW = (pal["ink"], pal["gilt"], pal["deep"],
                                         pal["ground"], pal["glow"])
    w, h = W * S, H * S
    base = radial_ground(W, H, DEEP, GROUND, pal["lift"]).resize((w, h), Image.BILINEAR)
    ink = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ink)

    cx = w // 2
    top_margin = int(h * 0.085)
    sill = int(h * 0.855)
    R = int(min((sill - top_margin) * 0.40, w * 0.16))
    spring = top_margin + R                 # y of the springing line
    lw = max(2, int(2.6 * S))

    # lamplight standing in the open door
    door = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dd = ImageDraw.Draw(door)
    ga = pal["glow_alpha"]
    dd.ellipse([cx - R, spring - R, cx + R, spring + R], fill=GLOW + (ga,))
    dd.rectangle([cx - R, spring, cx + R, sill], fill=GLOW + (ga,))
    door = door.filter(ImageFilter.GaussianBlur(int(80 * S)))
    ink.alpha_composite(door)

    silver = MITHRIL + (215,)
    faint = MITHRIL + (105,)
    gold = GOLD + (235,)

    # arch: the semicircular head, two jambs, and the threshold
    d.arc([cx - R, spring - R, cx + R, spring + R], 180, 360, fill=silver, width=lw)
    d.line([cx - R, spring, cx - R, sill], fill=silver, width=lw)
    d.line([cx + R, spring, cx + R, sill], fill=silver, width=lw)

    # a hand's breadth inside, a second line
    r2 = R - int(30 * S)
    d.arc([cx - r2, spring - r2, cx + r2, spring + r2], 180, 360, fill=faint, width=max(1, lw // 2))
    d.line([cx - r2, spring, cx - r2, sill], fill=faint, width=max(1, lw // 2))
    d.line([cx + r2, spring, cx + r2, sill], fill=faint, width=max(1, lw // 2))

    # threshold, running out past the jambs into the dark
    d.line([cx - int(R * 3.4), sill, cx + int(R * 3.4), sill], fill=faint, width=max(1, lw // 2))
    d.line([cx - int(R * 1.30), sill, cx + int(R * 1.30), sill], fill=silver, width=lw)

    # the Star of Feanor, centred in the head of the arch
    star_of_feanor(d, cx, spring - int(R * 0.34), int(R * 0.30), gold, max(2, int(2.2 * S)))

    # the seven stars of Durin, arcing beneath it
    for i in range(7):
        a = math.radians(196 + i * (148 / 6))
        sx = cx + (R * 0.74) * math.cos(a)
        sy = spring + (R * 0.74) * math.sin(a)
        star_of_feanor(d, sx, sy, int(R * 0.052), GOLD + (205,), max(1, int(1.5 * S)))

    # futhorc riding the outside of the arch
    rune_font = ImageFont.truetype(RUNIC, int(27 * S))
    arc_text(ink, to_futhorc("Speak friend and enter"), rune_font,
             cx, spring, R + int(46 * S), 181, 359, gold, flip=True)

    # and again down each jamb, the way a mason signs his door
    jamb_font = ImageFont.truetype(RUNIC, int(25 * S))
    jamb = to_futhorc("Durin", sep="")
    for sgn in (-1, 1):
        jd = ImageDraw.Draw(ink)
        y = spring + int(R * 0.55)
        for ch in jamb + "\u16eb" + to_futhorc("Deathless", sep=""):
            gw = jd.textlength(ch, font=jamb_font)
            jd.text((cx + sgn * (R + int(30 * S)) - gw / 2, y), ch, font=jamb_font, fill=GOLD + (170,))
            y += int(40 * S)

    fd = ImageDraw.Draw(ink)
    foot = to_futhorc("The doors of Durin Lord of Moria")
    foot_font = ImageFont.truetype(RUNIC, int(31 * S))
    fw = fd.textlength(foot, font=foot_font)
    fd.text((cx - fw / 2, sill + int(38 * S)), foot, font=foot_font, fill=GOLD + (195,))

    # the elvish line, in tengwar, under the runes
    tg = ImageFont.truetype(TENGWAR, int(46 * S))
    line = transcribe("sinome maruvan")
    tw = fd.textlength(line, font=tg)
    fd.text((cx - tw / 2, sill + int(96 * S)), line, font=tg, fill=MITHRIL + (145,))

    # every metal line gets a breath of glow
    glow = ink.filter(ImageFilter.GaussianBlur(9 * S))
    img = Image.alpha_composite(base.convert("RGBA"), glow)
    img = Image.alpha_composite(img, ink)
    img = img.convert("RGB").resize((W, H), Image.LANCZOS)

    noise = Image.effect_noise((W, H), 14).convert("L").point(lambda v: 128 + (v - 128) * 0.32)
    img = ImageChops.overlay(img, Image.merge("RGB", (noise,) * 3))
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse([-W * 0.34, -H * 0.52, W * 1.34, H * 1.52], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(W // 9))
    img = Image.composite(img, Image.new("RGB", (W, H), DEEP), vig)
    img.save(out)
    print("wrote", out, img.size)


if __name__ == "__main__":
    plate(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
          sys.argv[4] if len(sys.argv) > 4 else "dark")
