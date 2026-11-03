# Stop and remove the IVI Bridge (Windows). Settings are kept unless -Purge is given.
param([switch]$Purge)
$Root = Join-Path $env:LOCALAPPDATA 'IVI3D Bridge'
$TaskName = 'IVI3D Bridge'
Stop-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
# pythonw keeps running after the task stops; end the bridge process too
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -like '*ivi_bridge.py*' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root 'app'), (Join-Path $Root 'venv')
if ($Purge) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $Root
    Write-Host 'IVI Bridge uninstalled (settings deleted).'
} else {
    Write-Host "IVI Bridge uninstalled (settings kept in $Root; -Purge deletes them)."
}
