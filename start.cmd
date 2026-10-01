@echo off
rem Launch the Baby Jesus desktop companion (no Node.js on PATH required).
rem Terminals inside VS Code set this, which would make Electron run as plain Node.
set ELECTRON_RUN_AS_NODE=
start "" "%~dp0node_modules\electron\dist\electron.exe" "%~dp0."
