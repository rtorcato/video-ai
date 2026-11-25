#!/usr/bin/env bash
# Copy the Fusion title templates (fusion/*.setting) into DaVinci Resolve's Titles folder.
# After running it, restart Resolve: the titles appear under Effects → Titles → Fusion Titles.
#   ./install-fusion-templates.sh            install for the current user
#   RESOLVE_TITLES=/custom/path ./install-fusion-templates.sh
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Works from the skill's scripts/ folder or copied next to the .setting files.
if compgen -G "$here/*.setting" > /dev/null; then src="$here"; else src="$here/../fusion"; fi

if [[ -n "${RESOLVE_TITLES:-}" ]]; then
  dest="$RESOLVE_TITLES"
else
  case "$(uname -s)" in
    Darwin) dest="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Titles" ;;
    Linux)  dest="$HOME/.local/share/DaVinciResolve/Fusion/Templates/Edit/Titles" ;;
    MINGW*|MSYS*|CYGWIN*) dest="$APPDATA/Blackmagic Design/DaVinci Resolve/Support/Fusion/Templates/Edit/Titles" ;;
    *) echo "Unknown OS. Set RESOLVE_TITLES to Resolve's Fusion/Templates/Edit/Titles folder." >&2; exit 1 ;;
  esac
fi

mkdir -p "$dest"
shopt -s nullglob
count=0
for f in "$src"/*.setting; do
  cp "$f" "$dest/"
  echo "installed: $(basename "$f")"
  count=$((count + 1))
done
echo "$count template(s) → $dest"
echo "Restart DaVinci Resolve, then look under Effects → Titles → Fusion Titles."
