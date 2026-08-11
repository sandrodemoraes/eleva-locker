$ErrorActionPreference = "Stop"

$startup = [Environment]::GetFolderPath("Startup")
$atalho = Join-Path $startup "ELEVA LOCKER - Iniciar.lnk"
$bat = Join-Path $PSScriptRoot "iniciar-elevalocker.bat"
if (-not (Test-Path $bat)) {
    $bat = Join-Path $PSScriptRoot "iniciar_tudo.bat"
}
$workdir = Split-Path $PSScriptRoot -Parent

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($atalho)
$s.TargetPath = $bat
$s.WorkingDirectory = $workdir
$s.WindowStyle = 1
$s.Description = "ELEVA LOCKER - Docker WhatsApp + app.py"
$s.Save()

Write-Host "OK - Atalho criado em:"
Write-Host $atalho
