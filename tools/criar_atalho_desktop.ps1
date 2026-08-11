$ErrorActionPreference = "Stop"

$desktop = [Environment]::GetFolderPath("Desktop")
$atalho = Join-Path $desktop "ElevaLocker.lnk"
$workdir = Split-Path $PSScriptRoot -Parent
$bat = Join-Path $workdir "iniciar_elevalocker.bat"
if (-not (Test-Path $bat)) {
    $bat = Join-Path $PSScriptRoot "iniciar-elevalocker.bat"
}

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($atalho)
$s.TargetPath = "$env:ComSpec"
$s.Arguments = "/c `"$bat`""
$s.WorkingDirectory = $workdir
$s.WindowStyle = 1
$s.Description = "Iniciar ELEVA LOCKER + abrir navegador"
$s.Save()

Write-Host "OK - Atalho na Area de Trabalho:"
Write-Host $atalho
Write-Host ""
Write-Host "Destino:  cmd /c $bat"
Write-Host "Iniciar em: $workdir"
