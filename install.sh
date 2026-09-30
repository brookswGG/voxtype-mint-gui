#!/usr/bin/env bash
# Installs the Voxtype tray icon + recording overlay for Linux Mint (Cinnamon, X11).
# Voxtype itself must already be installed. Safe to re-run.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
log() { printf '\033[1;32m==>\033[0m %s\n' "$*"; }

log "Package dependencies"
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-xapp-1.0 gir1.2-gtk-3.0

log "Setting up the tray autostart"
mkdir -p ~/.config/autostart
sed "s|@TRAY@|$REPO_DIR/tray/voxtype-tray.py|" "$REPO_DIR/tray/voxtype-tray.desktop.in" \
    > ~/.config/autostart/voxtype-tray.desktop
pgrep -f voxtype-tray.py >/dev/null || nohup "$REPO_DIR/tray/voxtype-tray.py" >/dev/null 2>&1 &

log "Done."
