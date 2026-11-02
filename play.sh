#!/usr/bin/env bash
# Play Minecraft Java Edition 26.3 through Horizon — the Rust client — on macOS Intel,
# offline / cracked, using the Minecraft files a TLauncher install already has.
#
# No Microsoft account, no login, no TLauncher code. Horizon is a separate Rust game
# implementation; it only needs the version json, client jar, libraries and assets.
#
#   ./run-tlauncher-minecraft.sh                     # Steve, windowed, TLauncher's worlds
#   HORIZON_NAME=Notch ./run-tlauncher-minecraft.sh
#   ./run-tlauncher-minecraft.sh --world "New World" --creative
#
# Environment:
#   OXIDE_TLAUNCHER_DIR   TLauncher's game folder (default ~/Library/Application Support/minecraft)
#   HORIZON_NAME          Offline player name (default Steve)
#   HORIZON_GAME_DIR      Where saves/options live (default: the TLauncher folder)
#   HORIZON_HOME          Horizon's data folder (default: ./home next to this script)
set -euo pipefail

SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HORIZON_HOME="${HORIZON_LAUNCHER_HOME:-${HORIZON_HOME:-$SELF/home}}"
export HORIZON_LAUNCHER_HOME="$HORIZON_HOME"

say() { printf '\033[1;35mhorizon\033[0m %s\n' "$*"; }
die() { printf '\033[1;31mhorizon: %s\033[0m\n' "$*" >&2; exit 1; }

[ -d "$HORIZON_HOME/versions" ] || die "no Horizon install in $HORIZON_HOME (run the Horizon launcher once, or set HORIZON_HOME)"

# --- the installed Horizon version -------------------------------------------------
VERSION_DIR=""
if [ -f "$HORIZON_HOME/settings.json" ]; then
  selected="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("selected") or "")' "$HORIZON_HOME/settings.json" 2>/dev/null || true)"
  [ -n "$selected" ] && [ -x "$HORIZON_HOME/versions/$selected/horizon-client" ] && VERSION_DIR="$HORIZON_HOME/versions/$selected"
fi
if [ -z "$VERSION_DIR" ]; then
  VERSION_DIR="$(ls -1d "$HORIZON_HOME"/versions/*/ 2>/dev/null | sort | while read -r d; do [ -x "$d/horizon-client" ] && echo "${d%/}"; done | tail -1)"
fi
[ -n "$VERSION_DIR" ] || die "no Horizon version with horizon-client in $HORIZON_HOME/versions"
MC_VERSION="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["minecraft"]["version"])' "$VERSION_DIR/research-lock.json")"
RESOURCES="$VERSION_DIR/.local/horizon-client/$MC_VERSION"

# --- where Minecraft's own files are ------------------------------------------------
TLAUNCHER_DIR="${OXIDE_TLAUNCHER_DIR:-$HOME/Library/Application Support/minecraft}"
FIXTURE="$SELF/minecraft-tlauncher"

has_version() { [ -f "$1/versions/$MC_VERSION/$MC_VERSION.json" ] && [ -f "$1/versions/$MC_VERSION/$MC_VERSION.jar" ]; }

prepare() { # $1 = the folder to prepare from
  say "preparing Horizon $MC_VERSION resources from $1"
  local java_home=""
  java_home="$(find "$HORIZON_HOME/minecraft/runtime" -maxdepth 6 -type d -name Home -path '*/Contents/Home' 2>/dev/null | head -1)"
  local args=(--prepare --minecraft-dir "$1" --progress json)
  [ -f "$1/server-$MC_VERSION.jar" ] && args+=(--server-jar "$1/server-$MC_VERSION.jar")
  [ -n "$java_home" ] && args+=(--java-home "$java_home")
  ( cd "$VERSION_DIR" && ./horizon-prepare "${args[@]}" ) \
    | python3 -c '
import json, sys
for line in sys.stdin:
    try: event = json.loads(line)
    except ValueError: continue
    if "message" in event: print("  " + event["message"])
    elif "error" in event: sys.stderr.write("  " + event["error"] + "\n")
'
}

is_prepared() { ( cd "$VERSION_DIR" && ./horizon-prepare --check >/dev/null 2>&1 ); }

SOURCE=""
if has_version "$TLAUNCHER_DIR" && is_prepared; then
  SOURCE="$TLAUNCHER_DIR"
elif has_version "$TLAUNCHER_DIR"; then
  say "trying TLauncher's $TLAUNCHER_DIR"
  prepare "$TLAUNCHER_DIR" || true
  is_prepared && SOURCE="$TLAUNCHER_DIR"
fi

if [ -z "$SOURCE" ] && has_version "$FIXTURE" && is_prepared; then
  SOURCE="$FIXTURE"
fi

if [ -z "$SOURCE" ]; then
  if ! has_version "$FIXTURE"; then
    say "TLauncher has no usable $MC_VERSION files; fetching the identical Mojang files into $FIXTURE"
    python3 "$SELF/fetch-minecraft-26.3.py" "$FIXTURE" --version-dir "$VERSION_DIR"
  fi
  prepare "$FIXTURE"
  is_prepared || die "preparation did not complete; see the messages above"
  SOURCE="$FIXTURE"
fi
say "using Minecraft files from $SOURCE"

# --- play ---------------------------------------------------------------------------
NAME="${HORIZON_NAME:-Steve}"
if [ -n "${HORIZON_GAME_DIR:-}" ]; then
  GAME_DIR="$HORIZON_GAME_DIR"
elif [ -d "$TLAUNCHER_DIR" ]; then
  GAME_DIR="$TLAUNCHER_DIR"   # share worlds, options and resource packs with TLauncher
else
  GAME_DIR="$SOURCE"
fi
mkdir -p "$GAME_DIR/saves"
case "$NAME" in
  [A-Za-z0-9_]*[A-Za-z0-9_]*) ;;
  *) die "HORIZON_NAME must be 1-16 letters, digits or underscores: $NAME" ;;
esac

say "starting Horizon $MC_VERSION offline as $NAME (saves in $GAME_DIR)"
cd "$VERSION_DIR"
exec ./horizon-client \
  --resources "$RESOURCES" \
  --game-dir "$GAME_DIR" \
  --name "$NAME" \
  "$@"
