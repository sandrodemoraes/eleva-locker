$ErrorActionPreference = "Stop"

function Get-ProjetoDir {
    $oficial = "C:\ElevaLocker"
    if (Test-Path (Join-Path $oficial "app.py")) {
        return $oficial
    }
    $pai = Split-Path $PSScriptRoot -Parent
    if (Test-Path (Join-Path $pai "app.py")) {
        return $pai
    }
    throw "app.py nao encontrado. Abra o projeto em C:\ElevaLocker"
}

$workdir = Get-ProjetoDir
$bat = Join-Path $workdir "iniciar_elevalocker.bat"
if (-not (Test-Path $bat)) {
    $bat = Join-Path $workdir "tools\iniciar_servidor.bat"
}

$startup = [Environment]::GetFolderPath("Startup")
$atalho = Join-Path $startup "ELEVA LOCKER - Iniciar.lnk"

$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut($atalho)
$s.TargetPath = $bat
$s.Arguments = ""
$s.WorkingDirectory = $workdir
$s.WindowStyle = 1
$s.Description = "ELEVA LOCKER - inicia ao ligar o Windows"
$s.IconLocation = "$env:SystemRoot\System32\imageres.dll,109"
$s.Save()

Write-Host "OK  $atalho"
Write-Host "    cmd /k `"$bat`""
Write-Host "    Inicia ao fazer logon no Windows"
