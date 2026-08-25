#!/usr/bin/env python3
"""Quenya tehtar-mode tengwar, encoded for Tengwar Annatar.

Tengwar Annatar uses Daniel Smith's keyboard-position encoding: the tengwar
table from Appendix E is laid over a US qwerty keyboard, so the tengwa you
want is named by whatever key sits in its cell -- `5` is numen, `t` is malta.
The letters are in "the wrong places" by design (see the font's own README,
section 2.2), which is why a transcriber is worth having rather than typing
these strings by hand.

Mode: Quenya. The vowel is a tehta carried by the *preceding* consonant; a
vowel with no consonant before it, and every long vowel, rides a carrier of
its own.

    >>> transcribe("sinome maruvan")
    'iT5^t$ t#7UyE5'

That string is not one derived here -- it is the transcription printed in the
font's documentation (table 1), so it works as a fixture. `self_test()` checks
it, and forge.sh runs the check before it uses any of this.
"""
import sys
from bisect import bisect_right

# ---------------------------------------------------------------- tengwar --
# The four temar, as they fall on the keyboard: column I is dental, II labial,
# III palatal, IV labialized velar. Rows run tinco/ando/sule/anto/numen/ore.
TENGWAR = {
    "t": "1",  "nd": "2", "th": "3",  "nt": "4",  "n": "5",  "r-": "6",
    "p": "q",  "mb": "w", "f": "e",   "mp": "r",  "m": "t",  "v": "y",
    "c": "a",  "ng": "s", "h-": "d",  "nc": "f",  "ny-": "g", "y": "h",
    "qu": "z", "ngw": "x", "hw": "c", "nqu": "v", "nw": "b", "w": "n",
    "r": "7",  "rd": "u", "l": "j",   "ld": "m",
    "s": "8",  "s.": "i", "ss": "k",  "ss.": ",",
    "h": "9",  "hws": "o", "y-": "l",  "w-": ".",
}

# Quenya has six diphthongs and no more. The first vowel's tehta rides the
# glide: yanta carries the -i ones, ure the -u ones. Anything else that looks
# like two vowels really is two vowels, each on its own carrier.
DIPHTHONGS = {"ai": "y-", "oi": "y-", "ui": "y-",
              "au": "w-", "eu": "w-", "iu": "w-"}
SHORT_CARRIER = "`"
LONG_CARRIER = "~"

# A tehta is a zero-width mark drawn back over the tengwa it follows, so each
# one ships in several widths and the right one has to be picked by hand. The
# widths sort cleanly into three buckets when measured out of the font (see
# WIDTH_CLASS), and those buckets reproduce every letter of the fixture above.
TEHTAR = {
    "a": "#EDC",
    "e": "$RFV",
    "i": "%TGB",
    "o": "^YHN",
    "u": "&UJM",
}

# Advance-width cut points, in units of the em, measured from tngan.ttf. The
# wide (doubled-bow) tengwar land near 0.95em, the ordinary ones near 0.62em,
# and the two carriers near 0.30em; nothing falls in the gaps.
CLASS_CUTS = (0.45, 0.85)      # -> class index 2, 1, 0
FONT = "/usr/share/fonts/TTF/tngan.ttf"

_widths = {}


def _width(ch):
    """Advance width of one tengwa, in ems."""
    if not _widths:
        from PIL import ImageFont
        f = ImageFont.truetype(FONT, 1000)
        for c in set("".join(TENGWAR.values())) | {SHORT_CARRIER, LONG_CARRIER}:
            _widths[c] = f.getlength(c) / 1000.0
    return _widths[ch]


def _tehta(vowel, tengwa):
    """The variant of `vowel`'s tehta cut for a tengwa of this width."""
    forms = TEHTAR[vowel]
    return forms[2 - bisect_right(CLASS_CUTS, _width(tengwa))]


# ---------------------------------------------------------------- parsing --
VOWELS = "aeiou"
# Quenya spells long vowels with an acute; the diaeresis in "Nenime" only says
# the vowel is sounded, so it is folded away to the plain letter.
LONG = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u"}
FOLD = {"ë": "e", "ï": "i", "ä": "a", "ö": "o", "ü": "u", "k": "c"}

# Longest first, so "nqu" wins over "nc" and "qu" over "c".
CLUSTERS = ("nqu", "ngw", "nd", "nt", "nc", "ng", "mb", "mp", "ld", "rd",
            "ss", "qu", "hw", "nw", "th")


def _consonant(word, i):
    """Match the consonant at word[i]; returns (key, length) or None."""
    for cl in CLUSTERS:
        if word.startswith(cl, i):
            return cl, len(cl)
    ch = word[i]
    if ch in VOWELS:
        return None
    if ch == "r":
        # Romen initially and between vowels; ore when it closes a syllable.
        nxt = word[i + 1] if i + 1 < len(word) else ""
        return ("r" if nxt in VOWELS else "r-"), 1
    if ch == "h":
        return ("h" if i == 0 else "h-"), 1
    return ch, 1


def _word(word):
    out, i = [], 0
    while i < len(word):
        ch = word[i]
        d = DIPHTHONGS.get(word[i:i + 2])
        if d:
            glide = TENGWAR[d]
            out.append(glide + _tehta(ch, glide))
            i += 2
            continue
        if ch in VOWELS:
            # No consonant to carry it: it rides a carrier of its own.
            out.append(SHORT_CARRIER + _tehta(ch, SHORT_CARRIER))
            i += 1
            continue
        if ch in LONG:
            out.append(LONG_CARRIER + _tehta(LONG[ch], LONG_CARRIER))
            i += 1
            continue
        m = _consonant(word, i)
        if m is None:
            i += 1
            continue
        key, n = m
        i += n
        tengwa = TENGWAR[key]
        # A short vowel next rides this tengwa; a long one takes its own
        # carrier, and a diphthong its own glide, so the tengwa is left bare.
        if (i < len(word) and word[i] in VOWELS
                and word[i:i + 2] not in DIPHTHONGS):
            if key == "s":
                tengwa = TENGWAR["s."]      # silme nuquerna holds a tehta
            elif key == "ss":
                tengwa = TENGWAR["ss."]
            out.append(tengwa + _tehta(word[i], tengwa))
            i += 1
        else:
            out.append(tengwa)
    return "".join(out)


def transcribe(text):
    """Latin-spelt Quenya -> a Tengwar Annatar keying."""
    words = []
    for w in text.lower().split():
        w = "".join(FOLD.get(c, c) for c in w)
        w = "".join(c for c in w if c.isalpha() or c in LONG)
        if w:
            words.append(_word(w))
    return " ".join(words)


def self_test():
    got, want = transcribe("sinome maruvan"), "iT5^t$ t#7UyE5"
    if got != want:
        raise SystemExit("tengwar: fixture failed\n  want %r\n  got  %r" % (want, got))
    return True


if __name__ == "__main__":
    self_test()
    if len(sys.argv) > 1:
        print(transcribe(" ".join(sys.argv[1:])))
    else:
        print("ok: sinome maruvan -> " + transcribe("sinome maruvan"))
