#!/usr/bin/env python3
"""Render a text file the way the screensaver terminal will show it.

foot runs the screensaver with JetBrainsMono Nerd Font at size 18 on black.
Nothing monospaced covers the Runic block, so runes fall back to Noto Sans
Runic -- this mirrors that by picking the font per codepoint, which is what
makes the preview worth trusting for alignment.

    ./ttypreview.py <textfile> <out.png> [cols] [rows]
"""
import sys
from PIL import Image, ImageDraw, ImageFont

MONO = "/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"
RUNIC = "/usr/share/fonts/noto/NotoSansRunic-Regular.ttf"
SYMBOL = "/usr/share/fonts/noto/NotoSansSymbols2-Regular.ttf"
SIZE = 18
FG, BG = (222, 222, 222), (0, 0, 0)


def is_runic(ch):
    return 0x16A0 <= ord(ch) <= 0x16FF


def is_symbol(ch):
    # dingbats and misc symbols, which the mono font does not carry either
    o = ord(ch)
    return 0x2600 <= o <= 0x27BF


def main(path, out, cols=110, rows=26):
    mono = ImageFont.truetype(MONO, SIZE)
    runic = ImageFont.truetype(RUNIC, SIZE)
    symbol = ImageFont.truetype(SYMBOL, SIZE)

    # cell metrics come from the monospace font, as the terminal's do
    probe = Image.new("RGB", (10, 10))
    d0 = ImageDraw.Draw(probe)
    cw = d0.textlength("M", font=mono)
    ch = int(SIZE * 1.32)

    W, H = int(cw * cols), ch * rows
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    lines = open(path, encoding="utf-8").read().split("\n")
    # the screensaver centres the block on the canvas
    top = max(0, (rows - len(lines)) // 2)
    widest = max((len(l) for l in lines), default=0)
    left = max(0, (cols - widest) // 2)

    for r, line in enumerate(lines):
        for c, chx in enumerate(line):
            if chx == " ":
                continue
            f = runic if is_runic(chx) else symbol if is_symbol(chx) else mono
            d.text(((left + c) * cw, (top + r) * ch), chx, font=f, fill=FG)

    img.save(out)
    print(f"{out}  {W}x{H}  ({cols}x{rows} cells)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 110,
         int(sys.argv[4]) if len(sys.argv) > 4 else 26)
