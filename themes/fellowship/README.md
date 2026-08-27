# Fellowship

Middle-earth at golden hour. The palette is lifted straight off
`Fellowship.png` — the company standing on the ridge above Rivendell with the
sun going down behind the Misty Mountains.

The ground is the near-black green of the foreground trees. The text is the
lamplit parchment of the sky. Everything else is somewhere in that picture:
the gold of Rivendell's stonework, the amber of autumn beeches, the mauve of
the far peaks, the verdigris of the falls.

`fellowship-dawn` is the same theme in daylight — vellum and oak-gall ink,
taken from the Gandalf poster instead. Both carry the same twelve plates,
ordered so each opens on a picture that suits it.

## Colours

| token | hex | where it comes from |
|---|---|---|
| `background` | `#1C2321` | Mirkwood shadow, the foreground trees |
| `foreground` | `#E7D6B6` | parchment, lamplit |
| `accent` | `#D6AC5C` | Rivendell gold — lamplight on white stone |
| `red` | `#B45641` | maple ember |
| `orange` | `#C4823C` | autumn beech |
| `green` | `#7E9663` | Shire meadow |
| `cyan` | `#7FA9A0` | verdigris on the falls |
| `blue` | `#6E8DA6` | the Misty Mountains |
| `magenta` | `#B08A97` | dawn on the far peaks |
| `brown` | `#6B4B2F` | Hobbiton oak |

A focused window is ringed in a gradient running gold leaf → mithril, and
carries a warm lamp-glow, as though lit from inside a Hobbit-hole. That lives
in `hyprland.lua`.

## Backgrounds

Six scenes, each at 16:9 (3840×2160) and 21:9 (3440×1440), so nothing has to
be cropped on the fly. Omarchy shows one wallpaper across every monitor and
fills each with `PreserveAspectCrop`, so a plate is only pixel-exact on a
panel of its own aspect: the 16:9 plate is exact on any 16:9 panel (2560×1440,
1920×1080, 4K), the ultrawide on a 3440×1440. A 16:9 plate shown on a 21:9
panel keeps the middle 74.4% of its height; on 32:9, the middle 50%.

| plate | source | treatment | inscription |
|---|---|---|---|
| Rivendell | `Fellowship.png` | cropped | *sinome maruvan* — here I will abide |
| Durin's Gate | drawn by `forge/durin.py` | — | futhorc, *speak friend and enter* |
| Balrog | `Balrog.png` | margin grown | *auta i lómë* — the night is passing |
| Gandalf | `Gandalf.png` | margin grown | *elen síla lúmenn' omentielvo* |
| Rohirrim | `Rohirrim.png` | margin grown | *utúlie'n aurë* — day has come |
| Tom | `Tom.png` | margin grown | *laurië lantar lassi* — golden fall the leaves |

The four vellum posters are 3:2 and cannot be cropped without taking the
subject's head off, so `forge/forge.sh` grows their empty left margin instead:
a noise-free vertical light profile is lifted from 80 real columns of
parchment, softened along its length, stretched across the new margin,
re-grained, and the poster cross-faded onto it over 1200px.

The softening matters. Averaging 80 columns gives a clean profile where the
margin really is empty parchment, as Gandalf's is; where it carries texture —
Balrog's smoke — an unsoftened profile stretches into hard horizontal streaks
across the whole plate.

The Rivendell scene has no printed band and survives losing sky and
foreground, so it is cropped rather than grown.

### The bands

Every poster carries a printed tengwar band along its foot whose script does
not repeat cleanly, so it cannot be tiled to a wider canvas. Each plate gets a
fresh one instead, ruled and gilded like the printed one and carrying an
inscription chosen for that picture.

The band is the bottom 83/1024 of every source, and the source is scaled to
the plate height, so it is the bottom 83/1024 of the plate too — sized that
way it covers the printed band exactly, with no remnant showing beneath. Its
interior rules and point size are proportional to its height, so it reads the
same on a 1440-row plate as on a 2160-row one.

It comes in two tones, chosen per plate in the `PLATES` table: parchment for
the vellum posters, umber with gilt script for the dark ones, where a
parchment ribbon would be the brightest thing on the screen.

## The lock screen

The lock screen gets a plate of its own, `lockscreen.png` — hewn stone in the
manner of Moria, with the futhorc cut into it above and below. It is built by
`forge/moria.py` as a height field first (masonry courses, chisel bite, carved
runes), then lit from a single raking source so every recess casts its own
shadow; the colour goes on last, so the relief reads as stone rather than a
texture laid over a flat fill.

It exists because `unlock.png` is drawn for a dark ground and the golden-hour
wallpaper washed it out completely. Stock Omarchy blurs the desktop wallpaper
behind the lock screen; this plate replaces it and is shown sharp, since the
blur would only destroy the texture it was made to show. The rune bands sit at
20% and 77.5% of the height so they survive an ultrawide crop of a 16:9 plate
(only 12.8%–87.2% of it stays on a 21:9 panel).

**This needs the cloned lock plugin.** Stock Omarchy reads neither
`lockscreen.png` nor `unlock.png` at runtime. See "The lock plugin" below.

## The lock plugin

`~/.config/omarchy/plugins/austin.lock/` is a clone of `omarchy.lock` carrying
three changes:

- **the emblem** — draws `unlock.png` above the password field, scaled to fit
  a box (stock emblems run from 541×278 to 1108×523).
- **the plate** — prefers the theme's `lockscreen.png`, unblurred, and falls
  back to the blurred desktop wallpaper for themes without one.
- **no blanking** — `armBlankTimer()` is a no-op. Upstream sleeps the displays
  five seconds after the last input on the lock screen; only real input
  re-arms it, so it fires while you are still sitting there, and waking from
  it is unreliable on this NVIDIA box (see below).

To go back to stock: `omarchy plugin remove austin.lock && omarchy plugin
enable omarchy.lock`, then `omarchy restart shell`. Cloning means the lock
screen stops receiving upstream updates.

### The DPMS wake race

Worth recording, because it cost an evening. Omarchy sets
`misc.key_press_enables_dpms` and `misc.mouse_move_enables_dpms` true. When the
lock screen blanked the displays, the first mouse move made Hyprland flip
`dpmsStatus` back to true on its own; `omarchy-brightness-display on` then
skipped its DPMS enable *precisely because* every display already reported
lit, so no real modeset ever happened, and HDMI-A-1 (MAG27CQ at 1440p120 over
HDMI) stayed dark until forced:

```bash
hyprctl eval 'hl.monitor({ output = "HDMI-A-1", disabled = true })'; sleep 3; hyprctl reload
```

Both settings are now false in `~/.config/hypr/input.lua`. With blanking off
entirely the race is unreachable, but it still covers suspend/resume.

## The screensaver

`forge/screensaver.py` writes `~/.config/omarchy/branding/screensaver.txt`: a
quiet inscription — thin rules, a single star, the futhorc for *speak friend
and enter*, its gloss, and `mellon` letterspaced beneath as the answer. Air
between every line, 11 rows by 56 columns.

```bash
python3 forge/screensaver.py        # rebuild the text
omarchy branding screensaver reset  # back to the Omarchy logo
```

It is deliberately *not* called from `forge.sh`: the branding file is global,
not per-theme, so rebuilding the theme should not quietly redecorate the
screensaver.

Two constraints shaped the size, both worth knowing before editing:

- **The narrowest panel sets the budget.** 2560×720 at scale 1.6 leaves about
  18 rows at font size 18.
- **No monospace font covers the Runic block.** Runes fall back to Noto Sans
  Runic and are not guaranteed one cell wide, so they stay on their own centred
  line where a width mismatch cannot pull artwork out of true.

`forge/ttypreview.py` renders the file the way foot will, picking the font per
codepoint, so layout can be checked without hijacking every screen.

### Making it calm

Upstream runs `ttfx --random-effect`, which cycles all 34 effects — fireworks,
thunderstorm, VHS glitch — each with its own palette. Nothing about that is
reachable from the branding file, and `ttfx` defaults
`--existing-color-handling` to `ignore`, so ANSI colour in the text is
discarded too.

So the invocation itself had to change, in two copies kept under
`~/.config/omarchy/bin/`:

| file | copy of | change |
|---|---|---|
| `fellowship-screensaver` | `omarchy-screensaver` | pins `colorshift` in the theme's golds instead of `--random-effect` |
| `fellowship-launch-screensaver` | `omarchy-launch-screensaver` | spawns the above; per-monitor logic untouched |

`colorshift` was the right pick: it loops on its own (so no restart flicker
between cycles) and takes `--gradient-stops`, so the drift is Rivendell gold
running to parchment and back. `--cycles 100000` keeps it continuous; the
darkest stop is `6b5423` rather than something near-black, because the radial
travel dims the whole inscription at times and it has to stay legible then.

### The two ways in

Cloning the idle plugin only covers one of them. Going idle runs the
screensaver through `austin.idle`, but the menu's Screensaver row
(Super+Space) is a separate path that calls stock
`omarchy-launch-screensaver` — so the same inscription came up in ttfx's
random effect, rainbow rather than gold. The row is repointed in
`~/.config/omarchy/extensions/omarchy-menu.jsonc`, reusing the stock id so the
icon and label are inherited:

```jsonc
"system.screensaver": {"action":"$HOME/.config/omarchy/bin/fellowship-launch-screensaver force"},
```

`force` is upstream's own flag for "start even though the screensaver is
toggled off", and the Fellowship launcher handles it identically, being a copy.
Menu actions run through `bash -lc`, so `$HOME` expands.

`~/.config/omarchy/plugins/austin.idle/` is a clone of `omarchy.idle` whose
only change is calling the launcher above. It picks it by existence rather
than exit code — both scripts exit non-zero for benign reasons (screensaver
toggled off, one already running) and an `||` chain would answer those by
starting the stock flashy one.

To go back to stock: `omarchy plugin remove austin.idle && omarchy plugin
enable omarchy.idle`, then `omarchy restart shell`.

## The writing

**Tengwar.** Quenya, in the tehtar mode: the vowel is a mark carried by the
*preceding* consonant; long vowels ride a carrier of their own; and the six
Quenya diphthongs ride a glide — yanta for the *-i* ones, úrë for the *-u*.

It is set in Tengwar Annatar (Johan Winge, 2005; freeware,
`ttf-tengwar-annatar` in the AUR), which uses Daniel Smith's keyboard-position
encoding rather than Unicode: the tengwar table from Appendix E is laid over a
US qwerty keyboard, so `5` is númen and `t` is malta and the strings look like
line noise in any other font. They are not typed by hand.

`forge/tengwar.py` does the transcription, and checks itself before it will
hand anything back:

```
sinome maruvan  ->  iT5^t$ t#7UyE5
```

That is the transcription printed in table 1 of the font's own documentation
(`/usr/share/ttf-tengwar-annatar/README.pdf`) — not one derived here, so it
works as a fixture. `forge.sh` runs the check before it uses any of this, and
every tengwar string in the theme now comes through it: the bands, the lock
emblem, the preview card, the Durin's Gate plate, and the bar.

Which variant of a tehta a vowel takes depends on the width of the tengwa
beneath it. The widths were measured out of `tngan.ttf` rather than guessed:
they fall into three clean buckets — the doubled-bow tengwar near 0.95em, the
ordinary ones near 0.62em, the two carriers near 0.30em, with nothing in the
gaps — and those buckets reproduce every letter of the fixture.

**Runes.** The dwarf-runes are Anglo-Saxon futhorc, which is what Tolkien
actually used for the dwarves in *The Hobbit* — Thrór's map and the
moon-letters are futhorc with a few of his own additions. Elder Futhark, the
usual stand-in, is the wrong alphabet. `forge/futhorc.py` does the
transliteration; every codepoint is in the Unicode Runic block and renders in
Noto Sans Runic.

- around Durin's Gate: ᛋᛈᛠᚳ᛫ᚠᚱᛁᛖᚾᛞ᛫ᚪᚾᛞ᛫ᛖᚾᛏᛖᚱ — *speak friend and enter*
- along its threshold: ᚦᛖ᛫ᛞᚩᚩᚱᛋ᛫ᚩᚠ᛫ᛞᚢᚱᛁᚾ᛫ᛚᚩᚱᛞ᛫ᚩᚠ᛫ᛗᚩᚱᛁᚪ
- down each jamb: ᛞᚢᚱᛁᚾ᛫ᛞᛠᚦᛚᛖᛋᛋ
- foot of the preview card: ᚾᚩᛏ᛫ᚪᛚᛚ᛫ᚦᚩᛋᛖ᛫ᚹᚻᚩ᛫ᚹᚪᚾᛞᛖᚱ᛫ᚪᚱᛖ᛫ᛚᚩᛋᛏ

## The bar

`forge/barwidget.py` writes a custom Omarchy bar module,
`~/.config/omarchy/bar/modules/tengwar.qml`, carrying one phrase either side
of the clock:

```
elen síla   ...   [ the clock ]   ...   omentielvo
```

*Elen síla lúmenn' omentielvo* — "a star shines upon the hour of our meeting",
Frodo's greeting to Gildor. The clock stands where *lúmenn'*, "upon the hour",
belongs, so the bar reads as one sentence with the time inside it. Click
either half to romanise it; hover for the gloss.

The keyings are baked into the generated QML: the bar loads custom modules as
plain QML with no way to run Python at paint time. They still come from
`tengwar.py`, so they are never hand-typed.

```bash
python3 forge/barwidget.py ~/.config/omarchy/bar/modules/tengwar.qml
```

The module hides itself — zero width, and the bar closes the gap — when
Tengwar Annatar is missing (the keying would otherwise render as Latin
gibberish) or when the bar is vertical, where 28px cannot hold the line.

## Rebuilding

```bash
./forge/forge.sh          # every background, preview and emblem, both themes
```

Needs ImageMagick, Python with Pillow, `ttf-tengwar-annatar`, `noto-fonts`,
and the five source illustrations in `~/Pictures/Wallpapers/LOTR/` (override
with `SRC_DIR=`).

The plates, their treatment, their band tone and their inscriptions are one
table near the bottom of `forge.sh`:

```bash
# slug : source : treatment : band tone : the Quenya cut into its band
PLATES=(
  "rivendell:Fellowship:scene:dark:sinome maruvan"
  "gandalf:Gandalf:poster:light:elen síla lúmenn omentielvo"
  ...
)
```

The numbering under `backgrounds/` is the running order `omarchy theme bg
next` walks, so `install_set` clears the directory before it writes: a
renumbered plate left behind under its old name would be cycled through
twice.

### Why a rebuild needs the theme re-applied

`omarchy theme set` does not read this directory at paint time. It copies the
whole theme to `~/.local/state/omarchy/current/theme` and *everything*
downstream reads that snapshot — the wallpaper, `omarchy theme bg next`, and
the background switcher with its thumbnail cache.

So rebuilding the artwork changes nothing on screen, and new plates do not
appear in the switcher, until the theme is applied again. `forge.sh` does that
for you when one of these two themes is current, putting the wallpaper you had
back afterwards (applying otherwise resets it) and refreshing the thumbnails.
By hand it is:

```bash
omarchy theme set fellowship
omarchy theme bg cache
```
