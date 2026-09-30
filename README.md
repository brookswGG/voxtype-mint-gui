# voxtype-mint-gui

A tray icon and on-screen recording overlay for [Voxtype](https://voxtype.io)
on **Linux Mint (Cinnamon, X11)**. Voxtype's own OSD needs Wayland
layer-shell, so this fills the gap on X11.

Both follow the active theme: the tray uses the icon theme's microphone (same
size and style as the other panel icons) and the overlay takes its card and
accent colours from the GTK theme.

## What you get

- **Tray icon** (`XApp.StatusIcon`): microphone = ready, red = recording,
  orange = transcribing. Left-click toggles recording; right-click opens a menu
  (toggle, `voxtype configure`, restart daemon, quit).
- **Overlay:** while recording, a small card at the bottom-center of the
  focused window's monitor with a scrolling waveform and a level meter with
  peak hold, fed by the daemon's audio level socket. It never takes focus and
  is click-through. Set `OVERLAY_ENABLED = False` in `tray/overlay.py` to turn
  it off.

## Requirements

- Linux Mint 22.x, Cinnamon on X11
- Voxtype installed and its daemon running (`systemctl --user status voxtype`)

## Install

```bash
git clone https://github.com/brookswGG/voxtype-mint-gui.git && cd voxtype-mint-gui
./install.sh
```

This installs the GTK/XApp Python bindings, adds an autostart entry and
starts the tray. The tray copies its recording/transcribing icons into
`~/.local/share/icons/hicolor/symbolic/apps/` on first start.

## Layout

- `tray/voxtype-tray.py` — tray icon; watches `$XDG_RUNTIME_DIR/voxtype/state`
- `tray/overlay.py` — the overlay (GTK3/Cairo)
- `tray/icons/` — bundled symbolic microphone (fallback) and its red/orange variants
- `tray/voxtype-tray.desktop.in` — autostart template

## Uninstall

```bash
rm ~/.config/autostart/voxtype-tray.desktop
rm ~/.local/share/icons/hicolor/symbolic/apps/voxtype-*-symbolic.svg
```

## Credits

Based on [voxtype-mint-setup](https://github.com/ralfkuh-lab/voxtype-mint-setup)
by Ralf Kuhlendahl, from which the tray icon and overlay come. This project
drops the original's Voxtype/ydotool setup and reworks the icons and overlay
to follow the Cinnamon theme. Voxtype itself is a separate project:
[voxtype.io](https://voxtype.io).

## License

[MIT](LICENSE) — original copyright Ralf Kuhlendahl, modifications Brooks Gill.
