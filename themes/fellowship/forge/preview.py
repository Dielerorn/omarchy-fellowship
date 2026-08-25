#!/usr/bin/env python3
"""The theme-switcher card for Fellowship and Fellowship Dawn."""
import sys, tomllib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from futhorc import to_futhorc
from tengwar import transcribe

W, H = 1800, 1012
MONO   = "/usr/share/fonts/TTF/IosevkaTermSlabNerdFontMono-Regular.ttf"
MONOB  = "/usr/share/fonts/TTF/IosevkaTermSlabNerdFontMono-Bold.ttf"
SERIF  = "/usr/share/fonts/noto/NotoSerif-Italic.ttf"
RUNIC  = "/usr/share/fonts/noto/NotoSansRunic-Regular.ttf"
TENGWAR = "/usr/share/fonts/TTF/tngan.ttf"

TENGWAR_LINE = transcribe("sinome maruvan")   # "here I will abide"
RUNE_LINE = to_futhorc("Not all those who wander are lost")


def hexc(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def ground(art, c, dark):
    """The wallpaper, pushed back until it is only an atmosphere."""
    im = Image.open(art).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2,
                  (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    im = im.filter(ImageFilter.GaussianBlur(9))
    wash = Image.new("RGB", (W, H), c["background"])
    return Image.blend(im, wash, 0.74 if dark else 0.70)


def rounded(draw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def card(colors_toml, art, out, title, dark):
    raw = tomllib.loads(open(colors_toml).read())
    c = {k: hexc(v) for k, v in raw.items() if isinstance(v, str) and v.startswith("#")}

    img = ground(art, c, dark).convert("RGBA")
    d = ImageDraw.Draw(img)

    fg, accent, mute = c["foreground"], c["accent"], c["dark_foreground"]
    slug = title.lower().replace(" ", "-")

    # the elvish line across the head of the plate
    tg = ImageFont.truetype(TENGWAR, 46)
    tw = d.textlength(TENGWAR_LINE, font=tg)
    d.text(((W - tw) / 2, 44), TENGWAR_LINE, font=tg, fill=accent + (215,))
    for x0, x1 in ((150, (W - tw) / 2 - 46), ((W + tw) / 2 + 46, W - 150)):
        d.line([x0, 78, x1, 78], fill=accent + (75,), width=1)

    mono = ImageFont.truetype(MONO, 21)
    monob = ImageFont.truetype(MONOB, 21)
    small = ImageFont.truetype(MONO, 19)
    ser = ImageFont.truetype(SERIF, 24)

    PAD, BAR, ROW, SW = 40, 46, 34, 127
    body = (BAR + PAD + ROW + (ROW + 6) + 46
            + 2 * (SW * 0.52 + 14) + 20 + 28 + 24 + PAD)
    L = 300
    Rr = W - 300
    T = int((H - body) / 2) + 14
    B = T + body

    rounded(d, (L + 5, T + 6, Rr + 5, B + 6), 12, (0, 0, 0, 70))
    rounded(d, (L, T, Rr, B), 12,
            c["dark_background" if dark else "lighter_background"] + (242,), accent + (155,), 2)
    d.line([L + 2, T + BAR, Rr - 2, T + BAR], fill=accent + (85,), width=1)
    d.text((L + 24, T + 14), f"{slug} — ~/middle-earth", font=mono, fill=mute + (255,))

    # prompt
    x, y = L + PAD, T + BAR + PAD
    for txt, font, col in (("austin", monob, c["green"]), ("@omarchy ", mono, mute),
                           ("~/middle-earth ", monob, c["blue"]), ("main", mono, c["magenta"])):
        d.text((x, y), txt, font=font, fill=col + (255,))
        x += d.textlength(txt, font=font)
    y += ROW
    d.text((L + PAD, y), "❯", font=monob, fill=accent + (255,))
    d.text((L + PAD + d.textlength("❯ ", font=monob), y),
           f"omarchy theme set {slug}", font=mono, fill=fg + (255,))
    y += ROW + 6

    d.text((L + PAD, y), "# Sinome maruvan — here I will abide.", font=mono, fill=mute + (255,))
    y += 46

    # the palette, ordinary above, bright below
    keys = ["red", "orange", "yellow", "green", "cyan", "blue", "magenta", "brown"]
    bright = ["bright_red", "accent", "bright_yellow", "bright_green",
              "bright_cyan", "bright_blue", "bright_magenta", "muted"]
    for row, ks in enumerate((keys, bright)):
        for i, k in enumerate(ks):
            bx = L + PAD + i * (SW + 14)
            by = y + row * (SW * 0.52 + 14)
            rounded(d, (bx, by, bx + SW, by + SW * 0.52), 5, c[k] + (255,))
    y += 2 * (SW * 0.52 + 14) + 20

    names = ((("ground", "background"), ("parchment", "foreground")),
             (("gold", "accent"), ("ember", "red"))) if dark else \
            ((("vellum", "background"), ("ink", "foreground")),
             (("gilt", "accent"), ("ember", "red")))
    for r, pair in enumerate(names):
        for col, (label, key) in enumerate(pair):
            tx = L + PAD + col * 330
            d.text((tx, y + r * 28), label, font=small, fill=mute + (255,))
            d.text((tx + 130, y + r * 28), "#%02x%02x%02x" % c[key], font=small, fill=fg + (255,))

    note = "Rivendell at golden hour · tengwar & futhorc"
    d.text((Rr - PAD - d.textlength(note, font=ser), y + 14), note, font=ser, fill=mute + (255,))

    # dwarf-runes along the foot
    rf = ImageFont.truetype(RUNIC, 30)
    rw = d.textlength(RUNE_LINE, font=rf)
    d.text(((W - rw) / 2, H - 112), RUNE_LINE, font=rf, fill=accent + (155,))
    for x0, x1 in ((150, (W - rw) / 2 - 40), ((W + rw) / 2 + 40, W - 150)):
        d.line([x0, H - 97, x1, H - 97], fill=accent + (75,), width=1)

    img.convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    card(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] == "dark")
