// Windows helpers for app-usage tracking: which app is in the foreground, which apps have windows
// open, and a friendly display name for an exe. Uses koffi to call user32/kernel32 directly.
const { execFile } = require('child_process');
const path = require('path');
const koffi = require('koffi');

const user32 = koffi.load('user32.dll');
const kernel32 = koffi.load('kernel32.dll');

const GetForegroundWindow = user32.func('void* __stdcall GetForegroundWindow()');
const GetWindowThreadProcessId = user32.func('uint32 __stdcall GetWindowThreadProcessId(void* hWnd, _Out_ uint32* pid)');
const IsWindowVisible = user32.func('bool __stdcall IsWindowVisible(void* hWnd)');
const GetWindowTextLengthW = user32.func('int __stdcall GetWindowTextLengthW(void* hWnd)');
const GetWindow = user32.func('void* __stdcall GetWindow(void* hWnd, uint32 cmd)');
const EnumWindowsProc = koffi.proto('bool __stdcall EnumWindowsProc(void* hWnd, intptr_t lParam)');
const EnumWindows = user32.func('bool __stdcall EnumWindows(EnumWindowsProc* cb, intptr_t lParam)');

const OpenProcess = kernel32.func('void* __stdcall OpenProcess(uint32 access, bool inherit, uint32 pid)');
const QueryFullProcessImageNameW = kernel32.func('bool __stdcall QueryFullProcessImageNameW(void* h, uint32 flags, _Out_ uint16* name, _Inout_ uint32* size)');
const CloseHandle = kernel32.func('bool __stdcall CloseHandle(void* h)');

const PROCESS_QUERY_LIMITED_INFORMATION = 0x1000;
const GW_OWNER = 4;

// Shell surfaces and our own window; they aren't "apps you used".
const IGNORED = new Set([
  'electron.exe', 'tap tap jesus.exe', 'lockapp.exe', 'searchhost.exe', 'searchapp.exe',
  'startmenuexperiencehost.exe', 'shellexperiencehost.exe', 'textinputhost.exe',
  'applicationframehost.exe', 'systemsettingsbroker.exe',
]);

const pathCache = new Map(); // pid -> exe path (pids are reused, so entries expire)

function exePathForPid(pid) {
  const cached = pathCache.get(pid);
  if (cached && Date.now() - cached.at < 60_000) return cached.path;
  const h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, false, pid);
  if (!h) return null;
  try {
    const buf = Buffer.alloc(1024 * 2);
    const size = [1024];
    if (!QueryFullProcessImageNameW(h, 0, buf, size)) return null;
    const p = buf.toString('utf16le', 0, size[0] * 2);
    pathCache.set(pid, { path: p, at: Date.now() });
    return p;
  } finally {
    CloseHandle(h);
  }
}

function appForWindow(hwnd) {
  if (!hwnd) return null;
  const pid = [0];
  GetWindowThreadProcessId(hwnd, pid);
  if (!pid[0]) return null;
  const exePath = exePathForPid(pid[0]);
  if (!exePath) return null;
  const exe = path.basename(exePath);
  if (IGNORED.has(exe.toLowerCase())) return null;
  return { exe, path: exePath };
}

/** The app whose window is in the foreground, or null. */
function foregroundApp() {
  return appForWindow(GetForegroundWindow());
}

/** Apps that currently have a visible, titled, top-level window. */
function windowedApps() {
  const found = new Map();
  EnumWindows((hwnd) => {
    if (IsWindowVisible(hwnd) && GetWindowTextLengthW(hwnd) > 0 && !GetWindow(hwnd, GW_OWNER)) {
      const app = appForWindow(hwnd);
      if (app && !found.has(app.exe)) found.set(app.exe, app);
    }
    return true;
  }, 0);
  return [...found.values()];
}

/** Resolves the exe's FileDescription (e.g. "Visual Studio Code"), or null if it has none. */
function friendlyName(exePath) {
  return new Promise((resolve) => {
    // The path goes in through the environment: -Command splices extra arguments into the script unquoted.
    execFile('powershell.exe',
      ['-NoProfile', '-NonInteractive', '-Command', '(Get-Item -LiteralPath $env:TTJ_EXE).VersionInfo.FileDescription'],
      { windowsHide: true, timeout: 10_000, env: { ...process.env, TTJ_EXE: exePath } },
      (err, stdout) => resolve((!err && stdout.trim()) || null));
  });
}

module.exports = { foregroundApp, windowedApps, friendlyName };
