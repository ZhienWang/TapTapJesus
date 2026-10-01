# TapTapBaby

A desktop companion for Windows, in the spirit of Bongo Cat. A chibi character sits above your taskbar and slaps the thing in front of it every time you type or click, in any app. It counts your taps, levels up, and unlocks new characters as you go.

## What it does

- **Reacts to every keystroke and click, everywhere.** Keys on the left half of the keyboard and left clicks use the left hand; the rest use the right. The character's mouth pops open mid-slap.
- **Counts your activity.** Keystrokes, left clicks and right clicks are counted separately, along with how many miles your mouse has travelled.
- **Shows your top apps.** It adds up the time used for each program (while its window is in front and you're active) and lists your top 5, plus the combined total. You choose which apps are tracked.
- **Levels up.** Each character has its own tap counter, painted on whatever it slaps. Reach 10,000 taps with a character to unlock the next one.
- **Stays out of your way.** It's always on top, clicks pass through the empty space around it, it never steals focus from what you're typing, and it lives in the system tray.

## Characters

| Level | Character | Unlocks after |
|---|---|---|
| 1 | Baby Jesus, in his manger | Available from the start |
| 2 | Ninja Kid, at a ramen counter | 10,000 taps as Baby Jesus |
| 3 | Straw Hat Captain, at a treasure chest | 10,000 taps as Ninja Kid |
| 4 | Power Fighter, at a stone slab | 10,000 taps as Straw Hat Captain |
| 5 | Sun Swordsman, at a taiko drum | 10,000 taps as Power Fighter |
| 6 | Moon Guardian, at a vanity desk | 10,000 taps as Sun Swordsman |
| 7 | Hatsune Miku, at a synth (the final unlock) | 25,000 taps as Moon Guardian |

Characters 2–6 are original chibi designs inspired by popular anime archetypes. Hatsune Miku is a character of Crypton Future Media, INC. ([piapro.net](https://piapro.net)) and appears here as fan art.

## Using it

- **Move it:** drag the character anywhere. Its position is remembered.
- **Resize it:** right-click it, then choose **Size** (50% to 200%). You can also hold **Ctrl** and scroll over it, for anywhere from 50% to 300%.
- **Details:** click the **☰** button next to the character.
  - **Stats:** keystrokes, left and right clicks, mouse miles and total taps.
  - **Apps:** your top 5 apps by time used, the total, and **Choose apps to track…**.
  - **Unlocks:** your level, every character (locked ones are silhouettes) and progress toward the next unlock. Click a character to switch.
- **Menu:** right-click the character or the tray icon for the character list, tracked apps, size, reset position, start with Windows (non-Store builds) and quit.
- **Reset:** clears the keystroke, click, mouse and app-time totals. Levels and unlocked characters are kept.

## Privacy

TapTapBaby counts *how many* keys and clicks you press. It never records *which* keys, what you type, or anything on screen. App tracking stores only program names and time used. Everything stays in a local file (`%APPDATA%\tap-tap-jesus\companion.json`), and nothing is sent anywhere. See [PRIVACY.md](PRIVACY.md).

## Running from source

Requires Windows 10 or 11 and Node.js 20 or later.

```sh
npm install
npm start
```

Or double-click [start.cmd](start.cmd), which runs the installed Electron directly, so Node doesn't need to be on your PATH.

> In a VS Code terminal, `ELECTRON_RUN_AS_NODE` may be set, which makes Electron start as plain Node and crash. `start.cmd` clears it; with `npm start`, unset it first.

## Building for the Microsoft Store

```sh
npm run dist:store
```

This writes unsigned x64 and ARM64 `.appx` packages to `dist/`, ready to upload to Partner Center (the Store signs them). The package identity is under `build.appx` in [package.json](package.json). Listing copy and the `runFullTrust` justification are in [STORE_LISTING.md](STORE_LISTING.md).

## Regenerating the artwork

All characters are hand-built SVGs. The scripts need Python with Playwright (`pip install playwright pillow`, then `playwright install chromium`).

| Command | What it makes |
|---|---|
| `python tools/make_characters.py` | The five unlockable characters in `avatars/` |
| `python tools/make_miku.py` | `avatars/miku.svg` |
| `python tools/make_thumbnails.py` | Unlock-tab thumbnails in `assets/avatars/` |
| `python tools/make_store_assets.py` | Store tile images in `build/appx/` |

Every avatar SVG follows the same structure as [baby-jesus.svg](baby-jesus.svg):
- `#handL` and `#handR`, each with `.pose-up` and `.pose-down` groups
- `.mouth-closed` and `.mouth-open`
- optional `#bg` and `#holyGlow`
- `data-crop` and `data-counter-*` attributes on the root, which say where the counter is painted

To add a character, follow that structure and add an entry to `AVATARS` in [src/main.js](src/main.js).

## Project layout

```
src/main.js          Electron main process: window, global input hook, stats, levels, app tracking, tray
src/apps.js          Windows calls (via koffi) for the foreground app, open windows and app names
src/preload.js       Bridge between the main process and the pages
src/companion.*      The character window and its details panel
src/tracker.*        The "Choose tracked apps" window
baby-jesus.svg       The starting character
avatars/             Unlockable characters
assets/              App icon and character thumbnails
build/appx/          Microsoft Store tile images
index.html           Browser-only version: reacts to input inside the page only
tools/               Artwork generators
```

## Built with

[Electron](https://www.electronjs.org/), [uiohook-napi](https://github.com/SnosMe/uiohook-napi) for global keyboard and mouse input, [koffi](https://koffi.dev/) for Windows API calls, and [electron-builder](https://www.electron.build/) for packaging.
