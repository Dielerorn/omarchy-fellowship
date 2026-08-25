#!/usr/bin/env python3
"""unlock.png -- the emblem the lock screen wears, and preview-unlock.png,
the mock of that screen used in theme listings."""
import sys, tomllib
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from tengwar import transcribe

RUNIC   = "/usr/share/fonts/noto/NotoSansRunic-Regular.ttf"
TENGWAR = "/usr/share/fonts/TTF/tngan.ttf"
MONO    = "/usr/share/fonts/TTF/IosevkaTermSlabNerdFontMono-Regular.ttf"
S = 3


def hexc(s):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def star(d, cx, cy, r, fill, width):
    import math
    for i in range(8):
        a = math.radians(i * 45 - 90)
        rr = r if i % 2 == 0 else r * 0.62
        d.line([cx, cy, cx + rr * math.cos(a), cy + rr * math.sin(a)], fill=fill, width=width)
    d.ellipse([cx - r * .12, cy - r * .12, cx + r * .12, cy + r * .12], fill=fill)


def emblem(c, out, W=820, H=300):
    """A star of Feanor over the elvish line, on nothing at all."""
    w, h = W * S, H * S
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = c["foreground"]
    gold = c["accent"]

    star(d, w // 2, int(h * 0.30), int(h * 0.22), gold + (255,), 3 * S)

    tg = ImageFont.truetype(TENGWAR, 54 * S)
    line = transcribe("sinome maruvan")
    tw = d.textlength(line, font=tg)
    d.text(((w - tw) / 2, int(h * 0.50)), line, font=tg, fill=ink + (255,))

    rf = ImageFont.truetype(RUNIC, 22 * S)
    from futhorc import to_futhorc
    runes = to_futhorc("Here I will abide")
    rw = d.textlength(runes, font=rf)
    d.text(((w - rw) / 2, int(h * 0.80)), runes, font=rf, fill=gold + (235,))

    y = int(h * 0.30)
    for sgn in (-1, 1):
        d.line([w // 2 + sgn * int(h * 0.30), y, w // 2 + sgn * int(w * 0.44), y],
               fill=gold + (110,), width=max(1, S))

    img.resize((W, H), Image.LANCZOS).save(out)
    print("wrote", out)


def lock_mock(c, art, out, W=1920, H=1080):
    """The lock screen as it actually renders: the wallpaper, blurred, with
    the password field standing in the middle of it."""
    im = Image.open(art).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2,
                  (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    im = im.filter(ImageFilter.GaussianBlur(26)).convert("RGBA")
    scrim = Image.new("RGBA", (W, H), c["background"] + (110,))
    img = Image.alpha_composite(im, scrim)
    d = ImageDraw.Draw(img)

    bw, bh = 520, 62
    bx, by = (W - bw) // 2, int(H * 0.56)
    d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=10,
                        fill=c["background"] + (205,), outline=c["accent"] + (235,), width=2)
    mono = ImageFont.truetype(MONO, 22)
    dots = "•" * 9
    d.text((bx + (bw - d.textlength(dots, font=mono)) / 2, by + 19), dots,
           font=mono, fill=c["foreground"] + (255,))

    clock = ImageFont.truetype(MONO, 96)
    t = "21:41"
    d.text(((W - d.textlength(t, font=clock)) / 2, int(H * 0.30)), t,
           font=clock, fill=c["bright_foreground"] + (255,))

    tg = ImageFont.truetype(TENGWAR, 44)
    line = transcribe("sinome maruvan")
    d.text(((W - d.textlength(line, font=tg)) / 2, int(H * 0.44)), line,
           font=tg, fill=c["accent"] + (200,))

    img.convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    raw = tomllib.loads(open(sys.argv[1]).read())
    c = {k: hexc(v) for k, v in raw.items() if isinstance(v, str) and v.startswith("#")}
    emblem(c, sys.argv[2])
    lock_mock(c, sys.argv[3], sys.argv[4])
