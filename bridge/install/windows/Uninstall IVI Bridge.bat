@echo off
rem Double-click to remove the IVI Bridge. Add -Purge to also delete settings.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0uninstall.ps1" %*
pause
