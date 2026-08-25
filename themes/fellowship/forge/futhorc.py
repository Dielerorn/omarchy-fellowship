#!/usr/bin/env python3
"""Anglo-Saxon futhorc transliteration.

Tolkien used the futhorc (not the Elder Futhark) for the dwarf-runes in
The Hobbit -- Thror's map and the moon-letters are futhorc with a handful of
his own extensions.  This maps modern English spelling to the futhorc rune
values, longest digraph first.
"""
import sys

RUNES = [
    ("th", "ᚦ"),   # thorn
    ("ng", "ᛝ"),   # ing
    ("ea", "ᛠ"),   # ear
    ("ae", "ᚫ"),   # aesc
    ("oe", "ᛟ"),   # ethel
    ("qu", "ᚳᚹ"),
    ("a", "ᚪ"), ("b", "ᛒ"), ("c", "ᚳ"), ("d", "ᛞ"),
    ("e", "ᛖ"), ("f", "ᚠ"), ("g", "ᚷ"), ("h", "ᚻ"),
    ("i", "ᛁ"), ("j", "ᛄ"), ("k", "ᚳ"), ("l", "ᛚ"),
    ("m", "ᛗ"), ("n", "ᚾ"), ("o", "ᚩ"), ("p", "ᛈ"),
    ("r", "ᚱ"), ("s", "ᛋ"), ("t", "ᛏ"), ("u", "ᚢ"),
    ("v", "ᚠ"), ("w", "ᚹ"), ("x", "ᛉ"), ("y", "ᚣ"),
    ("z", "ᛉ"),
]

def to_futhorc(text, sep="᛫"):
    out, words = [], text.lower().split()
    for w in words:
        buf, i = [], 0
        while i < len(w):
            for latin, rune in RUNES:
                if w.startswith(latin, i):
                    buf.append(rune); i += len(latin); break
            else:
                i += 1          # punctuation and anything unmapped is dropped
        out.append("".join(buf))
    return sep.join(out)

if __name__ == "__main__":
    print(to_futhorc(" ".join(sys.argv[1:])))
