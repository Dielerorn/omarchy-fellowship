# Fellowship

Two Middle-earth themes for [Omarchy](https://omarchy.org): **Fellowship**,
the company on the ridge above Rivendell with the sun going down behind the
Misty Mountains, and **Fellowship Dawn**, the same world in daylight — vellum
and oak-gall ink.

Twelve wallpapers apiece, each cut to fit the panel it is shown on and each
carrying its own inscription in tengwar; a lock screen hewn out of Moria
stone; and an elvish line that runs along the top bar with the clock standing
inside it.

![The tengwar either side of the clock](docs/bar.png)

That is Frodo's greeting to Gildor — *elen síla lúmenn' omentielvo*, "a star
shines upon the hour of our meeting". The clock sits exactly where *lúmenn'*,
"upon the hour", belongs, so the bar reads as one sentence with the time
inside it. Click either half to read it in Latin letters; hover for the whole
line and its gloss.

![The six plates](docs/plates.png)

---

## Install

```bash
git clone https://github.com/Dielerorn/omarchy-fellowship.git
cd omarchy-fellowship
./install.sh
```

That installs both themes, drops the tengwar bar module into
`~/.config/omarchy/bar/modules/`, places it either side of your clock, and
applies **Fellowship**. It never touches `/usr/share/omarchy`, and anything it
overwrites is backed up beside itself first.

```bash
./install.sh --help          # every option
./install.sh --no-wire       # install the bar module but leave shell.json alone
./install.sh --no-bar        # themes only
./install.sh --all           # also the Moria lock screen and the quiet screensaver
```

Then:

```bash
omarchy theme set fellowship        # Middle-earth at golden hour
omarchy theme set fellowship-dawn   # the same, in daylight
omarchy theme bg next               # walk the twelve plates
```

### Requirements

| | |
|---|---|
| Omarchy | any version with the Quickshell bar (`omarchy bar --help` works) |
| `ttf-tengwar-annatar` | **AUR** — `yay -S ttf-tengwar-annatar`. Needed for the bar module only. |
| `noto-fonts` | for the runes, if you rebuild the plates |
| ImageMagick + Python/Pillow | only to rebuild the plates |

The wallpapers have their inscriptions baked in, so they look right without
any font installed. The **bar module** cannot: Tengwar Annatar encodes the
tengwar at ordinary Latin code points, so without the font the line would
render as gibberish. It checks, and hides itself rather than show you that.

The font is freeware but its licence requires redistribution to carry the
whole original package unmodified, so it is **not** vendored here — install it
from the AUR.

---

## What is in the box

```
themes/fellowship/        the dark theme  — colours, 12 backgrounds, lock plate,
                          previews, hyprland.lua, and forge/ (the build pipeline)
themes/fellowship-dawn/   the light theme — the same twelve, reordered
bar/tengwar.qml           the bar module (generated; see forge/barwidget.py)
wallpapers/               the five source illustrations, 1536x1024
plugins/                  optional: the Moria lock screen and the quiet screensaver
bin/                      the screensaver launchers and the shell.json wiring helpers
```

---

## The wallpapers, and fitting them to a panel

Five source illustrations, all 3:2, plus a sixth plate — Durin's Gate — drawn
from nothing by `forge/durin.py`.

| plate | inscription | |
|---|---|---|
| Rivendell | *sinome maruvan* | here I will abide |
| Durin's Gate | ᛋᛈᛠᚳ᛫ᚠᚱᛁᛖᚾᛞ᛫ᚪᚾᛞ᛫ᛖᚾᛏᛖᚱ | speak friend and enter (futhorc) |
| Balrog | *auta i lómë* | the night is passing |
| Gandalf | *elen síla lúmenn' omentielvo* | a star shines upon the hour of our meeting |
| Rohirrim | *utúlie'n aurë* | day has come |
| Tom | *laurië lantar lassi* | golden fall the leaves |

Omarchy shows **one** wallpaper across every monitor and fills each with
`PreserveAspectCrop`, so a plate is only ever pixel-exact on panels of its own
aspect. Each scene therefore ships twice:

| file | pixels | fits |
|---|---|---|
| `NN-name.jpg` | 3840×2160 (16:9) | any 16:9 panel — 2560×1440, 1920×1080, 4K — with no crop at all |
| `NN-name-ultrawide.jpg` | 3440×1440 (21:9) | a 3440×1440 ultrawide exactly |

Pick whichever matches the monitor you care about and let the others crop. A
16:9 plate on a 21:9 panel keeps the middle 74.4% of its height; on a 32:9
panel, the middle 50%.

Nothing is cropped blind. The four vellum posters cannot lose any height — it
would take the subject's head off — so instead their own empty left margin is
*grown*: a light profile is lifted from 80 real columns of parchment, softened
along its length, stretched across the new margin, re-grained, and the poster
cross-faded onto it over 1200px. The Rivendell scene survives losing sky and
foreground, so that one is cropped.

Every poster carries a printed tengwar band whose script does not repeat
cleanly, so it cannot be tiled wider. Each plate gets a fresh band instead,
set in Tengwar Annatar, sized to cover the printed one exactly, and cut in
parchment or in umber depending on how dark the picture is.

---

## The writing

**Tengwar.** Quenya, in the tehtar mode: the vowel is a mark carried by the
*preceding* consonant, and long vowels and diphthongs ride carriers and glides
of their own.

Tengwar Annatar uses Daniel Smith's keyboard-position encoding — the tengwar
table from Appendix E laid over a US qwerty keyboard — so the strings are
deliberately "in the wrong places" and cannot sensibly be typed by hand.
`forge/tengwar.py` transcribes them instead, and refuses to hand anything back
until it has reproduced the transcription printed in the font's own manual:

```
sinome maruvan  ->  iT5^t$ t#7UyE5
```

which is the sample in table 1 of Johan Winge's documentation, not a string
derived here. Everything else in the theme — every band, the lock emblem, the
preview card, the bar — is transcribed through that same checked path.

Which tehta variant a vowel uses depends on how wide the tengwa beneath it is;
the widths were measured out of the font itself and fall into clean buckets,
and those buckets reproduce every letter of the fixture.

**Runes.** The dwarf-runes are Anglo-Saxon futhorc, which is what Tolkien
actually used for the dwarves in *The Hobbit* — Thrór's map and the
moon-letters are futhorc with a few of his own additions. Elder Futhark, the
usual stand-in, is the wrong alphabet.

---

## The bar module

`bar/tengwar.qml` is an ordinary Omarchy custom bar module. `install.sh` wires
it up for you; by hand it is two entries in `~/.config/omarchy/shell.json`
either side of `omarchy.clock`:

```json
{ "id": "tengwar-left",  "type": "qml",
  "source": "~/.config/omarchy/bar/modules/tengwar.qml",
  "phrase": "elen-sila" },
{ "id": "omarchy.clock", "format": "dddd HH:mm" },
{ "id": "tengwar-right", "type": "qml",
  "source": "~/.config/omarchy/bar/modules/tengwar.qml",
  "phrase": "omentielvo" }
```

`shell.json` hot-reloads, so there is nothing to restart.

| setting | |
|---|---|
| `phrase` | `elen-sila`, `omentielvo`, `sinome-maruvan`, `utulien-aure`, `auta-i-lome`, `namarie` |
| `size` | tengwar pixel size, default 17 |
| `opacity` | default 0.72 |
| `color` | defaults to the bar foreground |

To add a phrase of your own, put it in `PHRASES` in
`themes/fellowship/forge/barwidget.py` and regenerate:

```bash
python3 themes/fellowship/forge/barwidget.py ~/.config/omarchy/bar/modules/tengwar.qml
```

The module stands down — zero width, no gap — when the font is missing or the
bar is vertical.

---

## Optional extras

Both are clones of first-party Omarchy plugins, so installing them means that
part of your shell stops receiving upstream updates. Neither is installed
unless you ask.

```bash
./install.sh --with-lock    # the Moria lock plate + the tengwar emblem
./install.sh --with-idle    # a calm screensaver instead of the random effects
```

`--with-lock` is what makes `lockscreen.png` do anything: stock Omarchy blurs
the desktop wallpaper behind the lock screen, and this replaces it with a
plate of hewn stone shown sharp. It also stops the lock screen blanking the
displays after five seconds.

To go back to stock:

```bash
omarchy plugin remove "$USER.lock" && omarchy plugin enable omarchy.lock
omarchy restart shell
```

There is more on both, including a DPMS wake race worth knowing about on
NVIDIA, in [`themes/fellowship/README.md`](themes/fellowship/README.md).

---

## Rebuilding

```bash
cd themes/fellowship/forge
./forge.sh          # every background, preview and emblem, both themes
```

Needs ImageMagick, Python with Pillow, `ttf-tengwar-annatar`, `noto-fonts`,
and the five source illustrations in `~/Pictures/Wallpapers/LOTR/` (override
with `SRC_DIR=`, or `./install.sh --with-wallpapers` to put them there).

Editing the plates, their inscriptions or their band tone is one table near
the bottom of `forge.sh`:

```bash
PLATES=(
  "rivendell:Fellowship:scene:dark:sinome maruvan"
  "gandalf:Gandalf:poster:light:elen síla lúmenn omentielvo"
  ...
)
```

---

## Credits

The colours are lifted off the illustrations themselves; the palette, and
where each colour comes from, is documented in
[`themes/fellowship/README.md`](themes/fellowship/README.md).

- **Tengwar Annatar** — Johan Winge, 2005, freeware. Not redistributed here;
  install `ttf-tengwar-annatar` from the AUR.
- **Tengwar and futhorc** — J.R.R. Tolkien. A fan project, unaffiliated with
  and unendorsed by the Tolkien Estate.
- **Omarchy** — [omarchy.org](https://omarchy.org).

Everything in this repository that is mine is MIT; see [LICENSE](LICENSE). The
source illustrations in `wallpapers/` are included so the plates can be
rebuilt, and are not covered by it.
