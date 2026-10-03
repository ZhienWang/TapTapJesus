# Microsoft Store submission: TapTapBaby

Copy each section into the matching field in Partner Center.

## Product name
TapTapBaby (must match the reserved app name exactly)

## Short description (up to 100 characters)
A tiny chibi desk buddy who slaps along every time you type or click.

## Description
Meet your new desktop companion! Tap Tap Baby sits on your screen, above the taskbar or wherever you drop it, and bounces its little fists every time you type or click, in any app.

Every keystroke and click counts. Watch the counter climb on your companion's manger, toy box or carrot crate, and level up to unlock new characters:

• Baby Jesus, your first companion, in a cozy manger
• Kitty, Puppy, Bunny, Hamster and Fox Cub, cute pets unlocked at every 10,000 taps
• A secret final animal friend for the most dedicated tappers

Track your day at a glance:
• Keystrokes, left clicks and right clicks, counted separately
• How far your mouse has travelled, in miles
• Your top 5 apps by time used, with the apps you choose to track

Made to stay out of your way:
• Clicks pass straight through the empty space around your companion
• Drag it anywhere, and resize it from Tiny to Huge
• Never steals focus from what you're typing
• Lives in the system tray

Privacy first: Tap Tap Baby only counts how many times you press keys and click. It never records which keys you press, what you type or what's on your screen. App tracking stores only program names and time used. Everything stays on your PC; nothing is sent anywhere.

## Features (one per line)
Animated chibi companion that reacts to every keystroke and click
Seven unlockable characters with a levelling system
Separate counters for keystrokes, left clicks and right clicks
Mouse distance tracker
Top 5 apps by time used, with a chooser for which apps to track
Drag anywhere, resize from 50% to 300%
Click-through, always-on-top, never steals focus
All data stays on your device

## Category
Entertainment (subcategory: none), or Personalization

## Privacy policy URL
<the public URL where you host PRIVACY.md>

## Restricted capability justification: runFullTrust
Tap Tap Baby is a desktop (Win32) app built with Electron and packaged as MSIX. It needs runFullTrust to run as a desktop process, to show a transparent always-on-top companion window, and to count system-wide keyboard and mouse presses with a low-level input hook, which animates the character and updates its counters. The app records only counts. It never records which keys are pressed or any typed text. It also reads the foreground window's program name once a second to total app time used, only for apps the user chooses to track. No data leaves the device.

## Notes for certification
The app has no main window. After launch, a small animated character appears above the taskbar at the bottom-right of the primary display, with a tray icon. Right-click the character or the tray icon for options. Click the ☰ button next to the character for stats, top apps and unlocks. Typing or clicking anywhere animates the character. No account or sign-in is required.

## Age rating questionnaire hints
No violence, no user-generated content shared with others, no in-app purchases, no ads, no data sharing.
The app contains an external link: "Donate with PayPal" opens PayPal in the browser.

## Packages to upload
dist/Tap Tap Jesus 1.0.0.appx (x64)
dist/Tap Tap Jesus 1.0.0 arm64.appx (ARM64)

## Screenshots
At least one is required (1366×768 or larger, PNG). Take them with the companion on a tidy desktop, ideally one with the ☰ details panel open.
