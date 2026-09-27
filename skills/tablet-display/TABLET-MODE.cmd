@echo off
REM Double-click. No admin needed.
REM Turns the tablet into a full-screen kiosk display.
REM Asks for the URL, then sets it to launch on every sign-in.
REM Reverse it any time with TABLET-MODE-OFF.cmd
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tablet-mode.ps1"
pause
