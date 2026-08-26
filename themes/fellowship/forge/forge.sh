#!/usr/bin/env bash
# Fellowship / Fellowship Dawn -- wallpaper and plate forge.
#
#   ./forge.sh            # rebuild every background, preview and emblem
#
# Five source illustrations feed the themes, in two shapes:
#
#   Fellowship.png   the company looking down on Rivendell at golden hour
#   Gandalf.png      the grey wanderer, on vellum
#   Balrog.png       Khazad-dum, the bridge, on vellum
#   Rohirrim.png     the riders of the Mark, on vellum
#   Tom.png          Bombadil by the Withywindle, on vellum
#
# All five are 3:2, so none fits a 16:9 panel or an ultrawide without help.
# The Fellowship scene is cropped -- its composition survives losing sky and
# foreground.  The four vellum posters cannot be cropped (it would take the
# subject's head off), so instead their empty left margin is *extended*: a
# noise-free vertical light profile is lifted from 80 real columns of
# parchment, stretched across the new margin, re-grained, and the poster is
# then cross-faded onto it over 1200px.
#
# Every poster carries a printed tengwar band along its foot whose script does
# not repeat cleanly, so it cannot be tiled to a wider canvas.  Each plate gets
# a fresh band instead, set in Tengwar Annatar and gilded like the printed one,
# carrying an inscription chosen for that picture.  The band is sized to cover
# the printed one exactly -- it is the bottom 83/1024 of every source -- so no
# remnant of the original shows beneath it.
#
# A sixth plate, Durin's Gate, is drawn from nothing by durin.py.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
THEMES="$HOME/.config/omarchy/themes"
DARK="$THEMES/fellowship"
LIGHT="$THEMES/fellowship-dawn"
SRC="${SRC_DIR:-$HOME/Pictures/Wallpapers/LOTR}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

TENGWAR_FONT=/usr/share/fonts/TTF/tngan.ttf

UW_W=3440; UW_H=1440             # 21:9, for the 3440x1440 panel
HD_W=3840; HD_H=2160             # 16:9, downscales cleanly to 2560x1440

# The printed band occupies the bottom 83 of the sources' 1024 rows.
BAND_NUM=83; BAND_DEN=1024

need() { [[ -e $1 ]] || { echo "missing: $1" >&2; exit 1; }; }
for f in Fellowship Gandalf Balrog Rohirrim Tom; do need "$SRC/$f.png"; done
need "$TENGWAR_FONT"

# Every tengwar string in the theme is transcribed by forge/tengwar.py, which
# checks itself against the transcription printed in the font's own manual
# before it will hand back anything.
python3 "$HERE/tengwar.py" >/dev/null

mkdir -p "$DARK/backgrounds" "$LIGHT/backgrounds"

# ---------------------------------------------------------------- the band --
# A fresh tengwar band, ruled and gilded like the printed one, at any width and
# height.  All the interior rules and the point size are proportional to the
# band height, so it reads the same on a 1440-row plate as on a 2160-row one.
# The inscription is repeated as often as it fits with room to breathe.
band() {
  local out=$1 w=$2 h=$3 quenya=$4 tone=${5:-light}
  local pts rule_o rule_i dia uw uh period y i x cx cy draws="" n
  local bed_hi bed_lo rule_dk rule_lt ink
  # Vellum posters carry a parchment ribbon; the dark plates carry the same
  # ribbon cut in umber, so gilt script still reads against a dark foot.
  if [[ $tone == dark ]]; then
    bed_hi='#2A2119'; bed_lo='#1C1611'; rule_dk='#6B4B2F'; rule_lt='#8A6636'; ink='#C9A45C'
  else
    bed_hi='#E7CC9D'; bed_lo='#DBB984'; rule_dk='#BD8D50'; rule_lt='#D0A96E'; ink='#9C6B2C'
  fi
  pts=$(( h * 40 / 74 ))                      # the printed band was 74 rows at 40pt
  rule_o=$(( h * 3 / 74 )); (( rule_o < 1 )) && rule_o=1
  rule_i=$(( h * 7 / 74 )); (( rule_i < 2 )) && rule_i=2
  dia=$(( h * 8 / 74 ));    (( dia < 3 )) && dia=3

  python3 "$HERE/tengwar.py" "$quenya" >"$TMP/phrase.txt"
  magick -background none -fill "$ink" -font "$TENGWAR_FONT" -pointsize "$pts" \
    label:@"$TMP/phrase.txt" -trim +repage "$TMP/unit.png"
  uw=$(identify -format %w "$TMP/unit.png"); uh=$(identify -format %h "$TMP/unit.png")

  # As many repeats as fit with about as much air again between them.
  n=$(( w / (uw * 19 / 10) )); (( n < 1 )) && n=1

  magick -size "${w}x${h}" "gradient:${bed_hi}-${bed_lo}" -attenuate 0.5 +noise Gaussian "$out"
  magick "$out" -fill "$rule_dk" -draw "rectangle 0,0 ${w},${rule_o}" \
                 -draw "rectangle 0,$((h-rule_o-1)) ${w},$((h-1))" \
                 -fill "$rule_lt" -draw "rectangle 0,${rule_i} ${w},${rule_i}" \
                 -draw "rectangle 0,$((h-rule_i-1)) ${w},$((h-rule_i-1))" "$out"

  period=$(( w / n )); y=$(( (h - uh) / 2 ))
  local args=()
  for (( i = 0; i < n; i++ )); do
    x=$(( i * period + (period - uw) / 2 ))
    args+=( "$TMP/unit.png" -geometry "+${x}+${y}" -composite )
  done
  magick "$out" "${args[@]}" "$out"

  for (( i = 0; i < n; i++ )); do
    cx=$(( i * period )); cy=$(( h / 2 ))
    draws="$draws -draw \"polygon $cx,$((cy-dia)) $((cx+dia*3/4)),$cy $cx,$((cy+dia)) $((cx-dia*3/4)),$cy\""
  done
  eval magick "$out" -fill "'$rule_lt'" "$draws" "$out"
}

# ------------------------------------------------------------- the posters --
# Widen a vellum poster to `w`x`h` by growing its own empty left margin, then
# lay a fresh inscribed band over the printed one.
poster_plate() {
  local out=$1 w=$2 h=$3 src=$4 quenya=$5 tone=$6
  local pw px feather=1200 bh by
  magick "$src" -filter Lanczos -resize "x${h}" -unsharp 0x0.7+0.35+0.02 "$TMP/g.png"
  # drop the poster's own edge vignette, or it reappears in the middle of the plate
  magick "$TMP/g.png" -crop "$(( $(identify -format %w "$TMP/g.png") - 150 ))x${h}+150+0" +repage "$TMP/p.png"
  pw=$(identify -format %w "$TMP/p.png"); px=$((w - pw))

  # Lift a light profile from 80 real columns of the poster's own margin. It is
  # averaged to a single column and blurred along its length first: where the
  # margin carries texture rather than flat parchment -- Balrog's smoke -- an
  # unsoftened profile stretches into hard horizontal streaks.
  magick "$TMP/p.png" -crop "80x${h}+0+0" +repage -resize "1x${h}!" \
         -blur "0x$(( h / 48 ))" -resize "${w}x${h}!" \
         -attenuate 0.45 +noise Gaussian "$TMP/bed.png"
  magick -size "${h}x${feather}" gradient:black-white -rotate 270 -sigmoidal-contrast 4x50% "$TMP/f.png"
  magick -size "${pw}x${h}" xc:white "$TMP/f.png" -geometry +0+0 -composite "$TMP/m.png"
  magick "$TMP/p.png" "$TMP/m.png" -alpha off -compose CopyOpacity -composite "$TMP/pf.png"
  magick -size "${h}x$((w * 26 / 100))" gradient:'#00000022'-'#00000000' -rotate 270 "$TMP/v.png"

  # Cover the printed band exactly: it is the bottom 83/1024 of the source, and
  # the source was scaled to `h`, so it is the bottom 83/1024 of the plate too.
  bh=$(( (h * BAND_NUM + BAND_DEN - 1) / BAND_DEN ))
  by=$(( h - bh ))
  band "$TMP/band.png" "$w" "$bh" "$quenya" "$tone"
  magick "$TMP/bed.png" "$TMP/pf.png" -geometry "+${px}+0" -compose Over -composite \
         "$TMP/v.png" -geometry +0+0 -compose Over -composite \
         "$TMP/band.png" -geometry "+0+${by}" -compose Over -composite \
         -quality 94 -sampling-factor 1x1 "$out"
}

# ----------------------------------------------------------------- scenes ---
# The Fellowship scene, cropped to an aspect and upscaled.  It carries no
# printed band, so it gets an inscribed one of the same proportion for company.
scene_plate() {
  local out=$1 w=$2 h=$3 src=$4 quenya=$5 tone=$6 ch off bh by
  ch=$((1536 * h / w))                     # crop height that gives the target aspect
  off=$(( (1024 - ch) * 42 / 100 ))        # bias upward: keep the company in frame
  (( off < 0 )) && off=0
  magick "$src" -crop "1536x${ch}+0+${off}" +repage \
    -filter Lanczos -resize "${w}x${h}!" -unsharp 0x0.7+0.35+0.02 "$TMP/s.png"
  bh=$(( (h * BAND_NUM + BAND_DEN - 1) / BAND_DEN ))
  by=$(( h - bh ))
  band "$TMP/band.png" "$w" "$bh" "$quenya" "$tone"
  # the scene is dark at the foot, so the band is dropped back a little
  magick "$TMP/s.png" \( "$TMP/band.png" -alpha set -channel A -evaluate multiply 0.88 +channel \) \
         -geometry "+0+${by}" -compose Over -composite \
         -quality 94 -sampling-factor 1x1 "$out"
}

# ------------------------------------------------------------------ plates --
# slug : source : treatment : band tone : the Quenya cut into its band
PLATES=(
  "rivendell:Fellowship:scene:dark:sinome maruvan"
  "gandalf:Gandalf:poster:light:elen síla lúmenn omentielvo"
  "balrog:Balrog:poster:dark:auta i lómë"
  "rohirrim:Rohirrim:poster:light:utúlien aurë"
  "tom:Tom:poster:light:laurië lantar lassi"
)

echo "==> backgrounds"
for spec in "${PLATES[@]}"; do
  IFS=: read -r slug src kind tone quenya <<<"$spec"
  echo "    $slug"
  "${kind}_plate" "$TMP/$slug-hd.jpg" "$HD_W" "$HD_H" "$SRC/$src.png" "$quenya" "$tone"
  "${kind}_plate" "$TMP/$slug-uw.jpg" "$UW_W" "$UW_H" "$SRC/$src.png" "$quenya" "$tone"
done

echo "==> Durin's Gate"
python3 "$HERE/durin.py" "$HD_W" "$HD_H" "$TMP/durin-hd.png"       dark
python3 "$HERE/durin.py" "$UW_W" "$UW_H" "$TMP/durin-uw.png"       dark
python3 "$HERE/durin.py" "$HD_W" "$HD_H" "$TMP/durin-hd-light.png" light
python3 "$HERE/durin.py" "$UW_W" "$UW_H" "$TMP/durin-uw-light.png" light

# omarchy takes backgrounds[0] the first time a theme is applied, and `omarchy
# theme bg next` walks them in sorted order, so the numbering is the running
# order.  The dark theme opens on the golden-hour scene and keeps the dark
# plates early; the light one opens on the vellum poster.
install_set() {
  local dir=$1; shift
  local i=1 spec name file
  # Clear the previous set first: the numbers are the running order, and a
  # renumbered plate left under its old name would be cycled through twice.
  find "$dir" -maxdepth 1 -type f \( -name '*.jpg' -o -name '*.png' \) -delete
  for spec in "$@"; do
    IFS=: read -r name file <<<"$spec"
    install -m644 "$TMP/$file" "$dir/$(printf '%02d' "$i")-$name"
    i=$((i + 1))
  done
}

echo "==> installing"
install_set "$DARK/backgrounds" \
  "rivendell.jpg:rivendell-hd.jpg"                "rivendell-ultrawide.jpg:rivendell-uw.jpg" \
  "durins-gate.png:durin-hd.png"                  "durins-gate-ultrawide.png:durin-uw.png" \
  "balrog.jpg:balrog-hd.jpg"                      "balrog-ultrawide.jpg:balrog-uw.jpg" \
  "gandalf.jpg:gandalf-hd.jpg"                    "gandalf-ultrawide.jpg:gandalf-uw.jpg" \
  "rohirrim.jpg:rohirrim-hd.jpg"                  "rohirrim-ultrawide.jpg:rohirrim-uw.jpg" \
  "tom.jpg:tom-hd.jpg"                            "tom-ultrawide.jpg:tom-uw.jpg"

install_set "$LIGHT/backgrounds" \
  "gandalf.jpg:gandalf-hd.jpg"                    "gandalf-ultrawide.jpg:gandalf-uw.jpg" \
  "tom.jpg:tom-hd.jpg"                            "tom-ultrawide.jpg:tom-uw.jpg" \
  "rohirrim.jpg:rohirrim-hd.jpg"                  "rohirrim-ultrawide.jpg:rohirrim-uw.jpg" \
  "durins-gate.png:durin-hd-light.png"            "durins-gate-ultrawide.png:durin-uw-light.png" \
  "rivendell.jpg:rivendell-hd.jpg"                "rivendell-ultrawide.jpg:rivendell-uw.jpg" \
  "balrog.jpg:balrog-hd.jpg"                      "balrog-ultrawide.jpg:balrog-uw.jpg"

echo "==> lock plates"
# Hewn stone for the lock screen. The emblem is drawn for a dark ground, and a
# bright wallpaper washes it out, so the lock screen gets a plate of its own
# rather than the desktop background pressed into service.
python3 "$HERE/moria.py" "$HD_W" "$HD_H" "$DARK/lockscreen.png"  dark
python3 "$HERE/moria.py" "$HD_W" "$HD_H" "$LIGHT/lockscreen.png" light

echo "==> previews and emblems"
python3 "$HERE/preview.py" "$DARK/colors.toml"  "$DARK/backgrounds/01-rivendell.jpg" \
        "$DARK/preview.png"  "Fellowship"      dark
python3 "$HERE/preview.py" "$LIGHT/colors.toml" "$LIGHT/backgrounds/01-gandalf.jpg" \
        "$LIGHT/preview.png" "Fellowship Dawn" light
python3 "$HERE/unlock.py"  "$DARK/colors.toml"  "$DARK/unlock.png" \
        "$DARK/backgrounds/01-rivendell.jpg"  "$DARK/preview-unlock.png"
python3 "$HERE/unlock.py"  "$LIGHT/colors.toml" "$LIGHT/unlock.png" \
        "$LIGHT/backgrounds/01-gandalf.jpg"   "$LIGHT/preview-unlock.png"

# `omarchy theme set` does not read the theme directory at paint time -- it
# copies it to ~/.local/state/omarchy/current/theme and everything downstream
# (the wallpaper, the background switcher and its thumbnails) reads that
# snapshot. Rebuilding the artwork here therefore changes nothing on screen
# until the theme is applied again, so if one of these two is current, do it.
current="$(cat "$HOME/.local/state/omarchy/current/theme.name" 2>/dev/null || true)"
if [[ $current == fellowship || $current == fellowship-dawn ]]; then
  echo "==> re-applying $current (the live copy is a snapshot, not a link)"
  # Applying resets the wallpaper, so put the same plate back afterwards.
  was="$(basename "$(readlink -f "$HOME/.local/state/omarchy/current/background" 2>/dev/null || true)")"
  omarchy theme set "$current" >/dev/null 2>&1 || echo "    could not re-apply; run: omarchy theme set $current" >&2
  if [[ -n $was && -f $HOME/.local/state/omarchy/current/theme/backgrounds/$was ]]; then
    omarchy theme bg set "$HOME/.local/state/omarchy/current/theme/backgrounds/$was" >/dev/null 2>&1 || true
  fi
  omarchy theme bg cache >/dev/null 2>&1 || true
else
  echo "==> apply a theme to see the new plates:  omarchy theme set fellowship"
fi

echo "==> done"
du -sh "$DARK" "$LIGHT"
