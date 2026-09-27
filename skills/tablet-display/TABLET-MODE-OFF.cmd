@echo off
REM Double-click. No admin needed.
REM Removes the kiosk startup entry and returns the tablet to a normal desktop.
REM Changes nothing else - no power settings, no kiosk account, no registry.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tablet-mode.ps1" -Off
pause
