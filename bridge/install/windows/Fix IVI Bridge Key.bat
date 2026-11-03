@echo off
rem Quit OrcaSlicer, then double-click after importing IVI3D.orca_printer. Writes the bridge key into Orca.
set "PY=%LOCALAPPDATA%\IVI3D Bridge\venv\Scripts\python.exe"
set "H=%~dp0app\ivi_setup_keys.py"
if not exist "%H%" set "H=%~dp0..\..\ivi_setup_keys.py"
if not exist "%H%" set "H=%LOCALAPPDATA%\IVI3D Bridge\app\ivi_setup_keys.py"
"%PY%" "%H%" --wait %*
pause
