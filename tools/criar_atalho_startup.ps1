$ErrorActionPreference = "Stop"

$startup = [Environment]::GetFolderPath("Startup")
$atalho = Join-Path $startup "ELEVA LOCKER - Iniciar.lnk"
$workdir = Split-Path $PSScriptRoot -Parent
$bat = Join-Path $workdir "iniciar_elevalocker.bat"
if (-not (Test-Path $bat)) {
    $bat = Join-Path $PSScriptRoot "iniciar_tudo.bat"
}

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($atalho)
# cmd /c evita abrir pasta em vez de executar o .bat
$s.TargetPath = "$env:ComSpec"
$s.Arguments = "/c `"$bat`""
$s.WorkingDirectory = $workdir
$s.WindowStyle = 1
$s.Description = "ELEVA LOCKER - Docker WhatsApp + app.py"
$s.Save()

Write-Host "OK - Atalho criado em:"
Write-Host $atalho
Write-Host "Destino: cmd /c $bat"
Write-Host "Iniciar em: $workdir"
