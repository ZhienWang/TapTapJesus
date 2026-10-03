const { app, BrowserWindow, ipcMain, screen, Tray, Menu, nativeImage, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const { uIOhook, UiohookKey: K } = require('uiohook-napi');
const apps = require('./apps');

const ROOT = path.join(__dirname, '..');

// Pin the data folder: adding productName for the Store build would otherwise move it from
// %APPDATA%\tap-tap-jesus to %APPDATA%\Tap Tap Jesus and the stats would appear to reset.
app.setPath('userData', path.join(app.getPath('appData'), 'tap-tap-jesus'));
const WIN_W = 300;
const WIN_H = 490;
// Your PayPal donation link, e.g. https://www.paypal.com/paypalme/yourname or https://www.paypal.com/donate/?hosted_button_id=XXXX
const DONATE_URL = 'https://www.paypal.com/donate/?hosted_button_id=BZ4MBPBK4MGE6';
// Each avatar is an SVG built like baby-jesus.svg: #handL/#handR with .pose-up/.pose-down groups,
// .mouth-closed/.mouth-open, an optional #bg and #holyGlow, and data-crop / data-counter-* on the root.
// Characters unlock in order: reach `unlock.taps` taps while playing as `unlock.after` to earn the next one.
const LEVEL_TAPS = 10_000;
const AVATARS = [
  { id: 'jesus', label: 'Baby Jesus', file: 'baby-jesus.svg' },
  { id: 'kitten', label: 'Kitty', file: path.join('avatars', 'kitten.svg'), unlock: { after: 'jesus', taps: LEVEL_TAPS } },
  { id: 'puppy', label: 'Puppy', file: path.join('avatars', 'puppy.svg'), unlock: { after: 'kitten', taps: LEVEL_TAPS } },
  { id: 'bunny', label: 'Bunny', file: path.join('avatars', 'bunny.svg'), unlock: { after: 'puppy', taps: LEVEL_TAPS } },
  { id: 'hamster', label: 'Hamster', file: path.join('avatars', 'hamster.svg'), unlock: { after: 'bunny', taps: LEVEL_TAPS } },
  { id: 'fox', label: 'Fox Cub', file: path.join('avatars', 'fox.svg'), unlock: { after: 'hamster', taps: LEVEL_TAPS } },
  // The final and hardest unlock.
  { id: 'panda', label: 'Panda', file: path.join('avatars', 'panda.svg'), unlock: { after: 'fox', taps: 25_000 } },
];
const avatarById = (id) => AVATARS.find((a) => a.id === id);
const isUnlocked = (id) => data.unlocked.includes(id);
const currentAvatar = () => (isUnlocked(data.avatar) && avatarById(data.avatar)) || AVATARS[0];
const MIN_SCALE = 0.5;
const MAX_SCALE = 3;
const SIZE_PRESETS = [
  { label: 'Tiny', scale: 0.5 },
  { label: 'Small', scale: 0.75 },
  { label: 'Normal', scale: 1 },
  { label: 'Large', scale: 1.5 },
  { label: 'Huge', scale: 2 },
];

// Keys on the left half of the keyboard slap with the left hand; everything else uses the right.
const LEFT_KEYS = new Set([
  K.Escape, K.F1, K.F2, K.F3, K.F4, K.F5, K.F6,
  K.Backquote, K[1], K[2], K[3], K[4], K[5],
  K.Tab, K.Q, K.W, K.E, K.R, K.T,
  K.CapsLock, K.A, K.S, K.D, K.F, K.G,
  K.Shift, K.Z, K.X, K.C, K.V, K.B,
  K.Ctrl, K.Meta, K.Alt,
]);
const MOUSE_LEFT = 1;
const MOUSE_RIGHT = 2;

let win = null;
let tray = null;
let trackerWin = null;

// ---------- Persistence ----------

const dataFile = () => path.join(app.getPath('userData'), 'companion.json');

function freshStats() {
  return { keystrokes: 0, leftClicks: 0, rightClicks: 0, mouseInches: 0, since: new Date().toISOString() };
}

// Saves from before the animal update used these character ids; each maps to the animal at the same level.
const RENAMED_AVATARS = { ninja: 'kitten', pirate: 'puppy', fighter: 'bunny', swordsman: 'hamster', guardian: 'fox', miku: 'panda' };
const renameAvatar = (id) => RENAMED_AVATARS[id] || id;

function migrateAvatarIds(d) {
  if (d.avatar) d.avatar = renameAvatar(d.avatar);
  if (Array.isArray(d.unlocked)) d.unlocked = [...new Set(d.unlocked.map(renameAvatar))];
  if (d.charTaps) {
    const taps = {};
    for (const [id, n] of Object.entries(d.charTaps)) taps[renameAvatar(id)] = (taps[renameAvatar(id)] || 0) + n;
    d.charTaps = taps;
  }
  return d;
}

function loadData() {
  try {
    const d = migrateAvatarIds(JSON.parse(fs.readFileSync(dataFile(), 'utf8')));
    const stats = { ...freshStats(), ...d.stats };
    return {
      stats, position: d.position || null, scale: d.scale || 1, avatar: d.avatar || 'jesus',
      apps: d.apps || {}, tracking: { autoTrackNew: true, ...d.tracking },
      // Before levels existed every tap was Baby Jesus's, so credit them to him.
      charTaps: d.charTaps || { jesus: stats.keystrokes + stats.leftClicks + stats.rightClicks },
      unlocked: d.unlocked || ['jesus'],
    };
  } catch {
    return {
      stats: freshStats(), position: null, scale: 1, avatar: 'jesus', apps: {}, tracking: { autoTrackNew: true },
      charTaps: {}, unlocked: ['jesus'],
    };
  }
}

let data;
let dirty = false;

function saveData() {
  if (!dirty) return;
  try {
    fs.mkdirSync(path.dirname(dataFile()), { recursive: true });
    fs.writeFileSync(dataFile(), JSON.stringify(data, null, 2));
    dirty = false;
  } catch (err) {
    console.error('Failed to save stats:', err);
  }
}

// ---------- Stats → renderer ----------

let statsPending = false;
function pushStats() {
  dirty = true;
  if (statsPending) return;
  statsPending = true;
  setTimeout(() => {
    statsPending = false;
    if (win && !win.isDestroyed()) {
      win.webContents.send('stats', data.stats);
      win.webContents.send('progress', progress());
    }
  }, 50);
}

// ---------- Levels ----------

function progress() {
  const active = currentAvatar();
  const next = AVATARS.find((a) => a.unlock && !isUnlocked(a.id));
  return {
    active: active.id,
    level: data.unlocked.length,
    maxLevel: AVATARS.length,
    activeTaps: data.charTaps[active.id] || 0,
    roster: AVATARS.map((a) => ({
      id: a.id, label: isUnlocked(a.id) ? a.label : null, unlocked: isUnlocked(a.id), taps: data.charTaps[a.id] || 0,
    })),
    next: next && {
      id: next.id,
      after: next.unlock.after,
      afterLabel: avatarById(next.unlock.after).label,
      taps: next.unlock.taps,
      have: Math.min(data.charTaps[next.unlock.after] || 0, next.unlock.taps),
    },
  };
}

function checkUnlocks() {
  for (const a of AVATARS) {
    if (!a.unlock || isUnlocked(a.id) || !isUnlocked(a.unlock.after)) continue;
    if ((data.charTaps[a.unlock.after] || 0) < a.unlock.taps) continue;
    data.unlocked.push(a.id);
    dirty = true;
    saveData();
    if (win && !win.isDestroyed()) win.webContents.send('unlocked', { id: a.id, label: a.label, level: data.unlocked.length });
    if (tray) tray.displayBalloon({ title: 'New character unlocked!', content: `${a.label} joined you. Switch in Unlocks.` });
    refreshTray();
  }
}

function creditCharTap() {
  const id = currentAvatar().id;
  data.charTaps[id] = (data.charTaps[id] || 0) + 1;
  const next = AVATARS.find((a) => a.unlock && a.unlock.after === id);
  if (next && !isUnlocked(next.id) && data.charTaps[id] >= next.unlock.taps) checkUnlocks();
}

// ---------- App usage ----------
// Time used = time an app's window is in the foreground while you're active (input within IDLE_MS).

const IDLE_MS = 2 * 60_000;
let lastInputAt = Date.now();
let lastTick = Date.now();
let currentApp = null; // exe name of the foreground app
const naming = new Set();

const noteActivity = () => { lastInputAt = Date.now(); };

function appEntry(app) {
  let e = data.apps[app.exe];
  if (!e) {
    e = data.apps[app.exe] = {
      name: app.exe.replace(/\.exe$/i, ''), seconds: 0, taps: 0, tracked: data.tracking.autoTrackNew,
    };
    dirty = true;
  }
  if (!e.named && !naming.has(app.exe)) {
    naming.add(app.exe);
    apps.friendlyName(app.path).then((name) => {
      if (!name) return; // keep the exe-based name; `naming` stops retries until next launch
      e.name = name;
      e.named = true;
      dirty = true;
      pushApps();
    });
  }
  return e;
}

function tickUsage() {
  const now = Date.now();
  const elapsed = Math.min(now - lastTick, 5000) / 1000; // cap so sleep/hibernate gaps never count
  lastTick = now;
  let fg = null;
  try { fg = apps.foregroundApp(); } catch {}
  currentApp = fg ? fg.exe : null;
  if (!fg) return;
  const e = appEntry(fg);
  if (e.tracked && now - lastInputAt < IDLE_MS) {
    e.seconds += elapsed;
    dirty = true;
  }
}

function creditTap() {
  const e = currentApp && data.apps[currentApp];
  if (e && e.tracked) e.taps++;
}

function topApps(n = 5) {
  const tracked = Object.entries(data.apps).filter(([, e]) => e.tracked && e.seconds >= 1);
  const totalSeconds = tracked.reduce((sum, [, e]) => sum + e.seconds, 0);
  const top = tracked
    .sort((a, b) => b[1].seconds - a[1].seconds)
    .slice(0, n)
    .map(([exe, e]) => ({ exe, name: e.name, seconds: e.seconds, taps: e.taps }));
  return { top, totalSeconds, trackedCount: tracked.length };
}

function trackerList() {
  let running = [];
  try { running = apps.windowedApps(); } catch {}
  running.forEach(appEntry); // running apps show up in the chooser even before they're used
  const runningSet = new Set(running.map((a) => a.exe));
  return {
    autoTrackNew: data.tracking.autoTrackNew,
    apps: Object.entries(data.apps).map(([exe, e]) => ({
      exe, name: e.name, seconds: e.seconds, tracked: e.tracked, running: runningSet.has(exe),
    })),
  };
}

function pushApps() {
  if (win && !win.isDestroyed()) win.webContents.send('apps', topApps());
}

function openTracker() {
  if (trackerWin && !trackerWin.isDestroyed()) {
    trackerWin.show();
    trackerWin.focus();
    return;
  }
  trackerWin = new BrowserWindow({
    width: 480,
    height: 620,
    minWidth: 380,
    minHeight: 400,
    title: 'Choose tracked apps',
    backgroundColor: '#14183a',
    icon: path.join(ROOT, 'assets', 'icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js') },
  });
  trackerWin.removeMenu();
  trackerWin.loadFile(path.join(__dirname, 'tracker.html'));
  trackerWin.on('closed', () => { trackerWin = null; });
}

// ---------- Hands ----------

const held = { left: new Set(), right: new Set() };
const heldSide = new Map(); // input id -> side
let lastHands = { left: false, right: false };
let spaceAlt = 0;

function sendHands() {
  const hands = { left: held.left.size > 0, right: held.right.size > 0 };
  if (hands.left === lastHands.left && hands.right === lastHands.right) return;
  lastHands = hands;
  if (win && !win.isDestroyed()) win.webContents.send('hands', hands);
}

function inputDown(id, side) {
  if (heldSide.has(id)) return false; // auto-repeat while held
  heldSide.set(id, side);
  held[side].add(id);
  sendHands();
  return true;
}

function inputUp(id) {
  const side = heldSide.get(id);
  if (!side) return;
  heldSide.delete(id);
  held[side].delete(id);
  sendHands();
}

// ---------- Global input hook ----------

let lastMouse = null;
let pxPerInch = 96;

function updatePxPerInch() {
  // Windows reports hook coordinates in physical pixels; 96 logical DPI × scale factor is the usual physical density.
  pxPerInch = 96 * screen.getPrimaryDisplay().scaleFactor;
}

function startHook() {
  uIOhook.on('keydown', (e) => {
    const side = e.keycode === K.Space ? (spaceAlt++ % 2 ? 'right' : 'left')
               : LEFT_KEYS.has(e.keycode) ? 'left' : 'right';
    noteActivity();
    if (inputDown('k' + e.keycode, side)) {
      data.stats.keystrokes++;
      creditTap();
      creditCharTap();
      pushStats();
    }
  });
  uIOhook.on('keyup', (e) => inputUp('k' + e.keycode));

  uIOhook.on('mousedown', (e) => {
    noteActivity();
    if (e.button === MOUSE_LEFT && inputDown('m1', 'left')) data.stats.leftClicks++;
    else if (e.button === MOUSE_RIGHT && inputDown('m2', 'right')) data.stats.rightClicks++;
    else return;
    creditTap();
    creditCharTap();
    pushStats();
  });
  uIOhook.on('mouseup', (e) => {
    inputUp('m' + e.button);
    if (e.button === MOUSE_LEFT) stopDrag();
  });

  uIOhook.on('wheel', noteActivity);
  uIOhook.on('mousemove', (e) => {
    noteActivity();
    if (lastMouse) {
      const d = Math.hypot(e.x - lastMouse.x, e.y - lastMouse.y);
      if (d > 0) {
        data.stats.mouseInches += d / pxPerInch;
        pushStats();
      }
    }
    lastMouse = { x: e.x, y: e.y };
  });

  uIOhook.start();
}

// ---------- Window ----------

// The page is laid out for WIN_W × WIN_H; scaling zooms the page and resizes the window to match.
function winSize(scale = data.scale) {
  return { width: Math.round(WIN_W * scale), height: Math.round(WIN_H * scale) };
}

function defaultPosition() {
  const wa = screen.getPrimaryDisplay().workArea;
  const { width, height } = winSize();
  return { x: wa.x + wa.width - width - 24, y: wa.y + wa.height - height };
}

function isOnScreen(pos) {
  const { width, height } = winSize();
  return pos && screen.getAllDisplays().some(({ workArea: a }) =>
    pos.x + width / 2 >= a.x && pos.x + width / 2 <= a.x + a.width &&
    pos.y + height / 2 >= a.y && pos.y + height / 2 <= a.y + a.height);
}

function moveTo(x, y) {
  // setBounds keeps the size fixed when crossing monitors with different scaling.
  win.setBounds({ x: Math.round(x), y: Math.round(y), ...winSize() });
}

function setScale(scale) {
  scale = Math.round(Math.min(MAX_SCALE, Math.max(MIN_SCALE, scale)) * 100) / 100;
  if (scale === data.scale) return;
  const old = win.getBounds();
  data.scale = scale;
  const { width, height } = winSize();
  // Grow and shrink from the bottom-left so he stays sitting where he was (e.g. on the taskbar).
  win.setBounds({ x: old.x, y: old.y + old.height - height, width, height });
  win.webContents.setZoomFactor(scale);
  data.position = { x: old.x, y: old.y + old.height - height };
  dirty = true;
  refreshTray();
}

function setAvatar(id) {
  if (id === currentAvatar().id || !isUnlocked(id)) return;
  data.avatar = id;
  dirty = true;
  saveData();
  win.webContents.send('avatar-changed'); // the page swaps the SVG in place
  pushStats();
  refreshTray();
}

function createWindow() {
  const pos = isOnScreen(data.position) ? data.position : defaultPosition();
  win = new BrowserWindow({
    ...winSize(),
    x: pos.x,
    y: pos.y,
    transparent: true,
    backgroundColor: '#00000000',
    frame: false,
    resizable: false,
    maximizable: false,
    fullscreenable: false,
    skipTaskbar: true,
    hasShadow: false,
    alwaysOnTop: true,
    focusable: false, // clicking him never steals focus from what you're typing in
    icon: path.join(ROOT, 'assets', 'icon.png'),
    webPreferences: { preload: path.join(__dirname, 'preload.js'), zoomFactor: data.scale },
  });
  // Zoom is per-origin in Chromium; re-apply after each load so it always matches the window size.
  win.webContents.on('did-finish-load', () => {
    win.webContents.setZoomFactor(data.scale);
    // Re-arm click-through with forwarding; a fresh page can't see the mouse otherwise.
    win.setIgnoreMouseEvents(true, { forward: true });
  });
  win.setAlwaysOnTop(true, 'screen-saver');
  win.setIgnoreMouseEvents(true, { forward: true });
  win.loadFile(path.join(__dirname, 'companion.html'));
}

function resetPosition() {
  const p = defaultPosition();
  moveTo(p.x, p.y);
  data.position = p;
  dirty = true;
  win.showInactive();
}

// ---------- Dragging ----------

let dragTimer = null;

function startDrag() {
  if (dragTimer) return;
  const c = screen.getCursorScreenPoint();
  const [wx, wy] = win.getPosition();
  const off = { x: c.x - wx, y: c.y - wy };
  dragTimer = setInterval(() => {
    const p = screen.getCursorScreenPoint();
    moveTo(p.x - off.x, p.y - off.y);
  }, 16);
}

function stopDrag() {
  if (!dragTimer) return;
  clearInterval(dragTimer);
  dragTimer = null;
  const [x, y] = win.getPosition();
  data.position = { x, y };
  dirty = true;
}

// ---------- Tray & menus ----------

function openDonate() {
  if (/^https:\/\/(www\.)?paypal\.(com|me)\//.test(DONATE_URL)) shell.openExternal(DONATE_URL);
}

function buildMenu() {
  return Menu.buildFromTemplate([
    { label: `${win.isVisible() ? 'Hide' : 'Show'} ${currentAvatar().label}`, click: () => { win.isVisible() ? win.hide() : win.showInactive(); refreshTray(); } },
    {
      label: 'Avatar',
      submenu: AVATARS.map(({ id, label }, i) => ({
        label: isUnlocked(id) ? `Lv ${i + 1} · ${label}` : `Lv ${i + 1} · 🔒 Locked`,
        type: 'radio',
        enabled: isUnlocked(id),
        checked: currentAvatar().id === id,
        click: () => setAvatar(id),
      })),
    },
    { label: 'Choose tracked apps…', click: openTracker },
    { label: 'Reset position', click: resetPosition },
    {
      label: 'Size',
      submenu: [
        ...SIZE_PRESETS.map(({ label, scale }) => ({
          label: `${label} (${Math.round(scale * 100)}%)`,
          type: 'radio',
          checked: data.scale === scale,
          click: () => setScale(scale),
        })),
        { type: 'separator' },
        { label: `Current: ${Math.round(data.scale * 100)}%  (Ctrl + scroll on him to fine-tune)`, enabled: false },
      ],
    },
    {
      label: 'Start with Windows',
      visible: !process.windowsStore, // login items aren't supported inside Store (MSIX) packages
      type: 'checkbox',
      checked: app.getLoginItemSettings().openAtLogin,
      click: (item) => app.setLoginItemSettings({ openAtLogin: item.checked }),
    },
    { type: 'separator' },
    { label: 'Donate with PayPal ♥', click: openDonate },
    { type: 'separator' },
    { label: 'Quit', click: () => app.quit() },
  ]);
}

function refreshTray() {
  if (tray) tray.setContextMenu(buildMenu());
}

function createTray() {
  const icon = nativeImage.createFromPath(path.join(ROOT, 'assets', 'icon.png')).resize({ width: 32, height: 32 });
  tray = new Tray(icon);
  tray.setToolTip('Tap Tap Jesus');
  tray.on('click', () => { win.isVisible() ? win.hide() : win.showInactive(); refreshTray(); });
  refreshTray();
}

// ---------- IPC ----------

ipcMain.handle('get-svg', () => fs.readFileSync(path.join(ROOT, currentAvatar().file), 'utf8'));
ipcMain.handle('get-stats', () => data.stats);
ipcMain.on('set-ignore', (_e, ignore) => {
  if (win && !dragTimer) win.setIgnoreMouseEvents(ignore, { forward: true });
});
ipcMain.on('scale-by', (_e, factor) => setScale(data.scale * factor));
ipcMain.on('drag-start', startDrag);
ipcMain.on('drag-end', stopDrag);
ipcMain.on('context-menu', () => buildMenu().popup({ window: win }));
ipcMain.on('reset-stats', () => {
  data.stats = freshStats();
  for (const e of Object.values(data.apps)) { e.seconds = 0; e.taps = 0; } // keep names and tracked choices
  pushStats();
  pushApps();
  saveData();
});
ipcMain.handle('get-apps', () => topApps());
ipcMain.handle('get-progress', () => progress());
ipcMain.on('set-avatar', (_e, id) => setAvatar(id));
ipcMain.handle('get-tracker-list', () => trackerList());
ipcMain.on('open-tracker', openTracker);
ipcMain.on('set-app-tracked', (_e, exe, tracked) => {
  if (data.apps[exe]) data.apps[exe].tracked = !!tracked;
  dirty = true;
  pushApps();
});
ipcMain.on('set-all-tracked', (_e, tracked) => {
  for (const e of Object.values(data.apps)) e.tracked = !!tracked;
  dirty = true;
  pushApps();
});
ipcMain.on('set-auto-track', (_e, on) => {
  data.tracking.autoTrackNew = !!on;
  dirty = true;
});
ipcMain.on('hide', () => { win.hide(); refreshTray(); });
ipcMain.on('donate', openDonate);
ipcMain.on('quit', () => app.quit());

// ---------- Lifecycle ----------

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on('second-instance', () => win && win.showInactive());

  app.whenReady().then(() => {
    data = loadData();
    // Names saved by an earlier build that fell back to the exe name get looked up again.
    for (const [exe, e] of Object.entries(data.apps)) {
      if (e.named && e.name.toLowerCase() === exe.replace(/\.exe$/i, '').toLowerCase()) e.named = false;
    }
    updatePxPerInch();
    screen.on('display-metrics-changed', updatePxPerInch);
    createWindow();
    createTray();
    startHook();
    checkUnlocks(); // in case old data already qualifies
    data.avatar = currentAvatar().id; // a saved avatar that's still locked falls back to Baby Jesus
    setInterval(tickUsage, 1000);
    setInterval(pushApps, 2000);
    setInterval(saveData, 10_000);
  });

  app.on('before-quit', () => {
    try { uIOhook.stop(); } catch {}
    saveData();
  });
}
