@echo off
rem Double-click to install the IVI Bridge (no admin needed).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
pause
