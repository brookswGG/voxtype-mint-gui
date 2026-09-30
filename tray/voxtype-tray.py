#!/usr/bin/env python3
"""Tray icon for Voxtype (Linux Mint / Cinnamon, XApp.StatusIcon).

Watches the Voxtype daemon's state file
($XDG_RUNTIME_DIR/voxtype/state) and shows the state as a microphone icon:

  idle           - the theme's microphone
  recording      - the same microphone tinted with the theme's error colour
  transcribing   - the same microphone tinted with the theme's warning colour
  (file missing) - idle icon, tooltip points out the inactive daemon

Left-click toggles recording (voxtype record toggle). While recording or
transcribing, overlay.py shows an on-screen level meter.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("XApp", "1.0")
from gi.repository import Gio, GLib, Gtk, XApp

try:
    import overlay as overlay_mod
except Exception as exc:
    print(f"voxtype overlay disabled: {type(exc).__name__}: {exc}", file=sys.stderr)
    overlay_mod = None

ICON_DIR = Path(__file__).resolve().parent / "icons"
STATE_FILE = Path(
    os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
) / "voxtype" / "state"

# Idle uses the theme's own symbolic microphone so it matches the other panel
# icons in size and colour. The active states are symbolic copies of it with
# the error/warning class set, so the panel sizes them identically and tints
# them with the theme's colours. Symbolic icons only get that treatment when
# resolved by name, so they are installed into the user's icon theme.
ICONS = {
    "idle": "audio-input-microphone-symbolic",
    "recording": "voxtype-recording-symbolic",
    "transcribing": "voxtype-transcribing-symbolic",
}
USER_ICON_DIR = Path.home() / ".local/share/icons/hicolor/symbolic/apps"


def install_icons():
    USER_ICON_DIR.mkdir(parents=True, exist_ok=True)
    changed = False
    for state, name in (("recording", "mic-recording"), ("transcribing", "mic-transcribing")):
        src = ICON_DIR / f"{name}-symbolic.svg"
        dst = USER_ICON_DIR / f"{ICONS[state]}.svg"
        if not dst.exists() or dst.read_bytes() != src.read_bytes():
            shutil.copyfile(src, dst)
            changed = True
    if changed:
        # Nudge icon-theme watchers so a running panel picks the files up.
        os.utime(USER_ICON_DIR.parents[2])
        subprocess.run(["gtk-update-icon-cache", "-f", "-t", str(USER_ICON_DIR.parents[2])],
                       capture_output=True)


TOOLTIPS = {
    "idle": "Voxtype ready — hold the hotkey to dictate, click to toggle",
    "recording": "Voxtype: recording …",
    "transcribing": "Voxtype: transcribing …",
}
TOOLTIP_OFF = "Voxtype daemon not running (systemctl --user start voxtype)"

class VoxtypeTray:
    def __init__(self):
        self.icon = XApp.StatusIcon()
        self.icon.set_name("voxtype")
        self.icon.connect("activate", self.on_activate)
        self.icon.set_secondary_menu(self.build_menu())
        self.current = None
        self._overlay = overlay_mod

        self.refresh()

        # Watch the directory: the state file is rewritten on every state
        # change and recreated when the daemon restarts.
        self.monitor = Gio.File.new_for_path(str(STATE_FILE.parent)).monitor_directory(
            Gio.FileMonitorFlags.NONE, None
        )
        self.monitor.connect("changed", self.on_fs_event)

        # Safety net in case a file monitor event gets lost
        GLib.timeout_add_seconds(10, self.refresh)

    def build_menu(self) -> Gtk.Menu:
        menu = Gtk.Menu()
        for label, cb in (
            ("Toggle recording", lambda *_: self.toggle()),
            ("Settings (voxtype configure)", lambda *_: self.run_bg(
                ["x-terminal-emulator", "-e", "voxtype configure"])),
            ("Restart Voxtype", lambda *_: self.run_bg(
                ["systemctl", "--user", "restart", "voxtype"])),
        ):
            item = Gtk.MenuItem(label=label)
            item.connect("activate", cb)
            menu.append(item)

        quit_item = Gtk.MenuItem(label="Quit tray")
        quit_item.connect("activate", lambda *_: Gtk.main_quit())
        menu.append(quit_item)

        menu.show_all()
        return menu

    # --- State handling ---------------------------------------------------

    def read_state(self) -> str | None:
        try:
            return STATE_FILE.read_text().strip() or "idle"
        except OSError:
            return None  # daemon not running

    def refresh(self, *_args) -> bool:
        state = self.read_state()
        if state != self.current:
            self.current = state
            key = state if state in ICONS else "idle"
            self.icon.set_icon_name(str(ICONS[key]))
            self.icon.set_tooltip_text(
                TOOLTIPS.get(state, TOOLTIPS["idle"]) if state else TOOLTIP_OFF
            )
            print(f"State: {state or 'daemon off'}", file=sys.stderr)
        if self._overlay is not None:
            try:
                self._overlay.set_state(state)
            except Exception as exc:
                print(
                    f"voxtype overlay disabled: {type(exc).__name__}: {exc}",
                    file=sys.stderr,
                )
                self._overlay = None
        return True  # keep the timeout alive

    def on_fs_event(self, _monitor, changed, _other, _event):
        if changed.get_basename() == "state":
            self.refresh()

    def on_activate(self, _icon, _button, _time):
        self.toggle()

    def toggle(self):
        self.run_bg(["voxtype", "record", "toggle"])

    @staticmethod
    def run_bg(cmd):
        try:
            subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except OSError as exc:
            print(f"Command failed: {cmd}: {exc}", file=sys.stderr)


def main():
    try:
        install_icons()
    except OSError as exc:
        print(f"could not install state icons: {exc}", file=sys.stderr)
    VoxtypeTray()
    Gtk.main()


if __name__ == "__main__":
    main()
