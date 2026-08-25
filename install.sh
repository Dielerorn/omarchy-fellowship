#!/usr/bin/env bash
# Fellowship for Omarchy -- installer.
#
#   ./install.sh                 themes, the tengwar bar module, and wire it in
#   ./install.sh --help          everything it can do
#
# Nothing here touches /usr/share/omarchy. Everything lands in ~/.config/omarchy,
# and anything it overwrites is backed up next to itself first.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="$HOME/.config/omarchy"
SHELL_JSON="$CONF/shell.json"
STAMP="$(date +%s)"

APPLY_THEME=fellowship
DO_BAR=1
DO_WIRE=1
DO_LOCK=0
DO_IDLE=0
DO_WALLS=0

say()  { printf '\033[32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[33m warn\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[31merror\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<EOF
Fellowship for Omarchy

  ./install.sh [options]

  --no-bar          skip the tengwar bar module
  --no-wire         install the bar module but do not edit shell.json
  --with-lock       install the Moria lock screen (clones omarchy.lock)
  --with-idle       install the quiet screensaver (clones omarchy.idle)
  --with-wallpapers copy the source illustrations to ~/Pictures/Wallpapers/LOTR
  --theme NAME      apply NAME at the end (fellowship, fellowship-dawn, none)
  --all             everything above
  -h, --help        this

Default: both themes, the tengwar bar module, wired either side of the clock,
then apply "fellowship".
EOF
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --no-bar)          DO_BAR=0; DO_WIRE=0 ;;
    --no-wire)         DO_WIRE=0 ;;
    --with-lock)       DO_LOCK=1 ;;
    --with-idle)       DO_IDLE=1 ;;
    --with-wallpapers) DO_WALLS=1 ;;
    --all)             DO_LOCK=1; DO_IDLE=1; DO_WALLS=1 ;;
    --theme)           APPLY_THEME="${2:-}"; shift ;;
    -h|--help)         usage; exit 0 ;;
    *)                 die "unknown option: $1 (try --help)" ;;
  esac
  shift
done

command -v omarchy >/dev/null || die "omarchy not found -- this installs into an Omarchy system."
[[ -d $CONF ]] || die "$CONF does not exist -- is this Omarchy?"

backup() { [[ -e $1 ]] && cp -a "$1" "$1.bak.$STAMP" && warn "backed up $(basename "$1") -> $(basename "$1").bak.$STAMP"; return 0; }

# ------------------------------------------------------------------ themes --
say "themes"
mkdir -p "$CONF/themes"
for t in fellowship fellowship-dawn; do
  [[ -d $HERE/themes/$t ]] || die "missing themes/$t in the checkout"
  if [[ -d $CONF/themes/$t ]]; then
    rm -rf "$CONF/themes/$t.bak.$STAMP"
    mv "$CONF/themes/$t" "$CONF/themes/$t.bak.$STAMP"
    warn "existing $t moved aside to $t.bak.$STAMP"
  fi
  cp -a "$HERE/themes/$t" "$CONF/themes/$t"
  echo "    $t ($(find "$CONF/themes/$t/backgrounds" -maxdepth 1 -type f | wc -l) backgrounds)"
done

# ------------------------------------------------------------------- fonts --
have_font() { fc-list 2>/dev/null | grep -qi 'Tengwar Annatar'; }
if ! have_font; then
  warn "Tengwar Annatar is not installed."
  warn "  The wallpapers already have their inscriptions baked in, but the bar"
  warn "  module needs the font and will stay hidden without it:"
  warn "      yay -S ttf-tengwar-annatar     # or: paru -S ttf-tengwar-annatar"
fi
fc-list 2>/dev/null | grep -qi 'Noto Sans Runic' || \
  warn "Noto Sans Runic missing (pacman -S noto-fonts) -- only needed to rebuild plates."

# -------------------------------------------------------------- bar module --
if (( DO_BAR )); then
  say "tengwar bar module"
  mkdir -p "$CONF/bar/modules"
  backup "$CONF/bar/modules/tengwar.qml"
  install -m644 "$HERE/bar/tengwar.qml" "$CONF/bar/modules/tengwar.qml"
  echo "    $CONF/bar/modules/tengwar.qml"
fi

if (( DO_WIRE )); then
  say "placing it either side of the clock"
  [[ -f $SHELL_JSON ]] || { mkdir -p "$CONF"; echo '{"version":1}' >"$SHELL_JSON"; }
  backup "$SHELL_JSON"
  python3 "$HERE/bin/wire-bar.py" "$SHELL_JSON" || die "could not edit shell.json (restore the .bak if needed)"
fi

# ------------------------------------------------------- optional plugins --
clone_plugin() {
  local src=$1 want=$2 id="${USER}.${2#*.}"
  local dst="$CONF/plugins/$id"
  mkdir -p "$CONF/plugins"
  if [[ -d $dst ]]; then
    rm -rf "$dst.bak.$STAMP"; mv "$dst" "$dst.bak.$STAMP"
    warn "existing $id moved aside"
  fi
  cp -a "$HERE/plugins/$src" "$dst"
  # The plugin id must match its directory, and the directory is namespaced to
  # whoever is installing, so the shipped manifest id is rewritten here.
  python3 - "$dst/manifest.json" "$id" <<'PY'
import json, sys
p, pid = sys.argv[1], sys.argv[2]
m = json.load(open(p)); m["id"] = pid
json.dump(m, open(p, "w"), indent=2); open(p, "a").write("\n")
PY
  python3 "$HERE/bin/wire-plugin.py" "$SHELL_JSON" "$id" "${want}"
  echo "    $id (replaces $want)"
}

if (( DO_LOCK )); then
  say "Moria lock screen"
  clone_plugin fellowship.lock omarchy.lock
fi

if (( DO_IDLE )); then
  say "quiet screensaver"
  clone_plugin fellowship.idle omarchy.idle
  mkdir -p "$CONF/bin"
  install -m755 "$HERE/bin/fellowship-screensaver" "$HERE/bin/fellowship-launch-screensaver" "$CONF/bin/"
  if command -v python3 >/dev/null && [[ -f $HERE/themes/fellowship/forge/screensaver.py ]]; then
    ( cd "$HERE/themes/fellowship/forge" && python3 screensaver.py ) || warn "screensaver text not rebuilt"
  fi
fi

# --------------------------------------------------------------- wallpapers --
if (( DO_WALLS )); then
  say "source illustrations"
  mkdir -p "$HOME/Pictures/Wallpapers/LOTR"
  cp -n "$HERE"/wallpapers/*.png "$HOME/Pictures/Wallpapers/LOTR/" 2>/dev/null || true
  echo "    ~/Pictures/Wallpapers/LOTR"
fi

# -------------------------------------------------------------------- apply --
if [[ $APPLY_THEME != none ]]; then
  say "applying $APPLY_THEME"
  omarchy theme set "$APPLY_THEME" || warn "could not apply $APPLY_THEME -- run: omarchy theme set $APPLY_THEME"
fi

if (( DO_LOCK || DO_IDLE )); then
  say "restarting the shell"
  omarchy restart shell || warn "run: omarchy restart shell"
fi

cat <<EOF

Done.

  omarchy theme set fellowship         Middle-earth at golden hour
  omarchy theme set fellowship-dawn    the same, in daylight
  omarchy theme bg next                walk the twelve plates

The bar carries "elen sila" and "omentielvo" either side of the clock, so the
time stands where lumenn' -- "upon the hour" -- belongs. Click either to read
it in Latin letters; hover for the whole line.
EOF
