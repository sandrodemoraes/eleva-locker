# ELEVA LOCKER - Criar atalho na area de trabalho + inicio com Windows
$ErrorActionPreference = "Stop"

$projeto = Split-Path -Parent $PSScriptRoot
$alvo = Join-Path $projeto "iniciar_elevalocker.bat"

if (-not (Test-Path $alvo)) {
    Write-Host ""
    Write-Host "ERRO: Nao foi encontrado iniciar_elevalocker.bat"
    Write-Host "Pasta esperada: $projeto"
    Write-Host ""
    exit 1
}

Write-Host "============================================================"
Write-Host "   ELEVA LOCKER - Atalho na area de trabalho + inicio Windows"
Write-Host "============================================================"
Write-Host ""
Write-Host "Projeto: $projeto"
Write-Host ""

$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$startup = [Environment]::GetFolderPath("Startup")

$deskPath = Join-Path $desktop "ElevaLocker.lnk"
$d = $ws.CreateShortcut($deskPath)
$d.TargetPath = $alvo
$d.WorkingDirectory = $projeto
$d.WindowStyle = 1
$d.Description = "Iniciar sistema ELEVA LOCKER"
$d.Save()
Write-Host "Atalho area de trabalho: $deskPath"

$startPath = Join-Path $startup "ElevaLocker.lnk"
$s = $ws.CreateShortcut($startPath)
$s.TargetPath = $alvo
$s.Arguments = "/startup"
$s.WorkingDirectory = $projeto
$s.WindowStyle = 7
$s.Description = "Iniciar ELEVA LOCKER com o Windows"
$s.Save()
Write-Host "Inicio automatico Windows: $startPath"

Write-Host ""
Write-Host "Pronto:"
Write-Host " - Atalho ElevaLocker na area de trabalho"
Write-Host " - Inicio automatico com o Windows (janela minimizada)"
Write-Host ""
