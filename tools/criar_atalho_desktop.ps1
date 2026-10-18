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

function New-ElevaAtalho {
    param(
        [string]$CaminhoLnk,
        [string]$Descricao
    )

    $workdir = Get-ProjetoDir
    $bat = Join-Path $workdir "iniciar_elevalocker.bat"
    if (-not (Test-Path $bat)) {
        $bat = Join-Path $workdir "tools\iniciar_servidor.bat"
    }

    $dir = Split-Path $CaminhoLnk -Parent
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }

    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut($CaminhoLnk)
    $s.TargetPath = $bat
    $s.Arguments = ""
    $s.WorkingDirectory = $workdir
    $s.WindowStyle = 1
    $s.Description = $Descricao
    $s.IconLocation = "$env:SystemRoot\System32\imageres.dll,109"
    $s.Save()

    Write-Host "OK  $CaminhoLnk"
    Write-Host "    cmd /k `"$bat`""
    Write-Host "    Iniciar em: $workdir"
}

$desktop = [Environment]::GetFolderPath("Desktop")
$atalho = Join-Path $desktop "ELEVA LOCKER.lnk"
New-ElevaAtalho -CaminhoLnk $atalho -Descricao "ELEVA LOCKER - servidor porta 15000"
