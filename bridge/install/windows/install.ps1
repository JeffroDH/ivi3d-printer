# IVI Bridge installer for Windows (no admin needed). Safe to re-run; keeps config and API key.
#   powershell -ExecutionPolicy Bypass -File install.ps1 [-NewKey] [-NoTask] [-NoOrca]
param([switch]$NewKey, [switch]$NoTask, [switch]$NoOrca)
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src  = Split-Path -Parent (Split-Path -Parent $Here)   # bridge\ (core code)
$Root = Join-Path $env:LOCALAPPDATA 'IVI3D Bridge'
$App  = Join-Path $Root 'app'
$Venv = Join-Path $Root 'venv'
$Cfg  = Join-Path $Root 'config.json'
$TaskName = 'IVI3D Bridge'

# 1. Python 3.8+ (py launcher first, then python on PATH; skip the Microsoft Store stub)
$Base = $null
foreach ($c in @(@('py', '-3'), @('python'), @('python3'))) {
    $exe = Get-Command $c[0] -ErrorAction SilentlyContinue
    if (-not $exe -or $exe.Source -like '*WindowsApps*') { continue }
    $pyArgs = @($c | Select-Object -Skip 1)
    # PS 5.1 turns redirected native stderr into errors under 'Stop', so probe with 'Continue'
    $ErrorActionPreference = 'Continue'
    & $exe.Source @pyArgs -c 'import sys; assert sys.version_info >= (3, 8)' 2>$null
    $rc = $LASTEXITCODE; $ErrorActionPreference = 'Stop'
    if ($rc -eq 0) { $Base = @($exe.Source) + $pyArgs; break }
}
if (-not $Base) {
    Write-Host 'Python 3.8+ is needed. Install it from https://www.python.org/downloads/ (or: winget install Python.Python.3.12), then run this again.'
    exit 1
}

# 2. venv + pyserial (the bridge needs pyserial on Windows for the USB/COM port)
New-Item -ItemType Directory -Force -Path $App | Out-Null
$BaseArgs = @($Base | Select-Object -Skip 1)
if (-not (Test-Path (Join-Path $Venv 'Scripts\python.exe'))) { & $Base[0] @BaseArgs -m venv $Venv }
$Py  = Join-Path $Venv 'Scripts\python.exe'
$PyW = Join-Path $Venv 'Scripts\pythonw.exe'
& $Py -m pip install -q --disable-pip-version-check --upgrade pyserial
if ($LASTEXITCODE -ne 0) { Write-Warning 'pyserial install failed; Wi-Fi works, USB printing needs: pip install pyserial' }

# 3. Copy the bridge
foreach ($f in 'ivi_bridge.py', 'ivi_setup_keys.py', 'ivi_add_header.py') { Copy-Item (Join-Path $Src $f) $App -Force }
foreach ($f in 'uninstall.ps1', 'Uninstall IVI Bridge.bat', 'Fix IVI Bridge Key.bat') {
    $p = Join-Path $Here $f; if (Test-Path $p) { Copy-Item $p $Root -Force }
}

# 4. Config (created once with defaults: port 5001, filtering off; never overwritten) + API key
$Info = & $Py (Join-Path $App 'ivi_bridge.py') --config $Cfg init-config | ConvertFrom-Json
$KeyArgs = @('--config', $Cfg, '--key-only', '--print-key'); if ($NewKey) { $KeyArgs += '--new-key' }
$Key = (& $Py (Join-Path $App 'ivi_setup_keys.py') @KeyArgs).Trim()
$HostPort = $Info.host
$Usb = if ($Info.usb_port) { $Info.usb_port } else { 'not plugged in (Wi-Fi will be used)' }

# 5. Scheduled Task at logon for this user (no admin), running pythonw (no console window)
if (-not $NoTask) {
    $Action  = New-ScheduledTaskAction -Execute $PyW -Argument "`"$(Join-Path $App 'ivi_bridge.py')`" --config `"$Cfg`" serve" -WorkingDirectory $Root
    $Trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
    $Set     = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
                 -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)
    $Prin    = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
    Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Set -Principal $Prin `
        -Description 'IVI3D Bridge (OctoPrint-compatible API for the IVI 3D printer)' -Force | Out-Null
    Start-ScheduledTask -TaskName $TaskName
}

$Ok = 'no'
if (-not $NoTask) {
    foreach ($i in 1..10) {
        try { Invoke-RestMethod -Uri "http://$HostPort/api/version" -Headers @{ 'X-Api-Key' = $Key } -TimeoutSec 2 | Out-Null; $Ok = 'yes'; break }
        catch { Start-Sleep -Seconds 1 }
    }
}
try { Set-Clipboard -Value $Key } catch { Write-Verbose 'clipboard unavailable' }

# 6. Orca: plugin + API key (%APPDATA%\OrcaSlicer)
$PluginNote = 'OrcaSlicer plugin: not installed'
$OrcaNote = 'Orca: skipped (-NoOrca)'
if (-not $NoOrca) {
    $OrcaDir = Join-Path $env:APPDATA 'OrcaSlicer'
    $PluginSrc = Join-Path $Src '..\orca\plugin\ivi3d_bridge_plugin.py'
    if ((Test-Path $PluginSrc) -and (Test-Path $OrcaDir)) {
        $Dest = Join-Path $OrcaDir 'orca_plugins\ivi3d_bridge_plugin.py'
        New-Item -ItemType Directory -Force -Path $Dest | Out-Null
        Copy-Item $PluginSrc $Dest -Force
        $PluginNote = "OrcaSlicer plugin copied to $Dest (restart Orca and enable it)"
    }
    & $Py (Join-Path $App 'ivi_setup_keys.py') --config $Cfg --orca-dir $OrcaDir
    switch ($LASTEXITCODE) {
        0 { $OrcaNote = "Orca: API key filled in ($OrcaDir)" }
        3 { $OrcaNote = "Orca: NOT updated (Orca was open). Quit Orca and run 'Fix IVI Bridge Key.bat' in $Root" }
        default { $OrcaNote = "Orca: key update failed; run 'Fix IVI Bridge Key.bat' in $Root" }
    }
}

$Msg = @"
IVI Bridge is installed and starts automatically at logon (Task Scheduler: '$TaskName').

$OrcaNote
Orca connection: Host type OctoPrint, Hostname/IP $HostPort
API key: copied to the clipboard (also in $Cfg)
USB printer: $Usb
Status page: http://$HostPort/
Running now: $Ok
$PluginNote
Firewall: the bridge listens on 127.0.0.1 only, so no rule is needed. If you set listen_host to 0.0.0.0
for phones/OctoApp, allow it once (admin):  New-NetFirewallRule -DisplayName 'IVI3D Bridge' -Direction Inbound -Protocol TCP -LocalPort 5001 -Action Allow
"@
Set-Content -Path (Join-Path $Root 'orca-settings.txt') -Value $Msg
Write-Host $Msg
