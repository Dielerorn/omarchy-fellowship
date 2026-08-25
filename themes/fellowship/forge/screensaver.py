#!/usr/bin/env python3
"""Build ~/.config/omarchy/branding/screensaver.txt.

A quiet inscription rather than a title card: thin rules, a single star, the
futhorc, and a letterspaced gloss, with air between every line. It is meant to
be read by a slow gold gradient drifting over it (see fellowship-screensaver),
not thrown around by a flashy effect.

Two constraints shape the size:

  - The narrowest panel here (2560x720 at scale 1.6) leaves about 18 rows at
    font size 18, and that is the budget.
  - Nothing monospaced covers the Runic block, so runes fall back to Noto Sans
    Runic and may not sit exactly one cell wide. They stay on their own centred
    line, where a width mismatch cannot pull artwork out of true.

`mellon` is Sindarin for "friend" -- the word that opens the Doors of Durin.
The runes are Anglo-Saxon futhorc, which is what Tolkien used for the dwarves.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from futhorc import to_futhorc

OUT = pathlib.Path.home() / ".config/omarchy/branding/screensaver.txt"

WIDTH = 56
RUNES = to_futhorc("Speak friend and enter")
GLOSS = "speak friend and enter"
WORD = "mellon"


def spaced(text):
    """Letterspace a line, the way an inscription breathes."""
    return "  ".join(text.replace(" ", " "))


def rule(width):
    inner = "─" * (width - 8)
    return f"✧ ─{inner}─ ✧"


def main():
    # riddle then answer: the runes ask, the gloss translates, mellon replies
    body = [
        rule(WIDTH),
        "",
        "✦".center(WIDTH),
        "",
        RUNES.center(WIDTH),
        "",
        GLOSS.center(WIDTH),
        "",
        spaced(WORD).center(WIDTH),
        "",
        rule(WIDTH),
    ]
    text = "\n".join(l.rstrip() for l in body) + "\n"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(text)
    print(f"-> {OUT}   {len(body)} rows x {WIDTH} cols")


if __name__ == "__main__":
    main()
