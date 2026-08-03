# Extrai dados uteis de uma COPIA da pasta Windows antiga.
# NAO altera C:\Windows do sistema atual.
param(
    [Parameter(Mandatory = $true)]
    [string]$OrigWin,

    [Parameter(Mandatory = $false)]
    [string]$Dest = "D:\Recuperado_Windows_Antigo"
)

$ErrorActionPreference = "Continue"

function Write-Log([string]$Message) {
    $script:LogLines += $Message
    Write-Host $Message
}

$LogLines = @()

$OrigWin = $OrigWin.TrimEnd('\')
$Dest = $Dest.TrimEnd('\')

if (-not (Test-Path -LiteralPath (Join-Path $OrigWin "System32\ntoskrnl.exe"))) {
    Write-Host "ERRO: Nao achei System32\ntoskrnl.exe em:"
    Write-Host "  $OrigWin"
    exit 1
}

if ([string]::Equals($OrigWin, $env:SystemRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    Write-Host "ERRO: Voce apontou para o Windows ATUAL ($env:SystemRoot)."
    Write-Host "Use a pasta COPIADA."
    exit 1
}

$OrigParent = Split-Path -Parent $OrigWin

Write-Host "============================================================"
Write-Host " Extrair dados do Windows ANTIGO (copia)"
Write-Host "============================================================"
Write-Host "Origem Windows: $OrigWin"
Write-Host "Pasta pai:      $OrigParent"
Write-Host "Destino:        $Dest"
Write-Host ""
Write-Host "Isto NAO repara boot. So copia arquivos uteis."
Write-Host ""

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$LogPath = Join-Path $Dest "RECUPERACAO_LOG.txt"

function Copy-IfExists([string]$Label, [string]$Src, [string]$Dst) {
    if (-not (Test-Path -LiteralPath $Src)) {
        Write-Log "[  ] ausente: $Label  ($Src)"
        return
    }
    Write-Log "[OK] $Label"
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    & robocopy $Src $Dst /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
}

Copy-IfExists "Users_ao_lado" (Join-Path $OrigParent "Users") (Join-Path $Dest "Users")
Copy-IfExists "ElevaLocker_pai" (Join-Path $OrigParent "ElevaLocker") (Join-Path $Dest "ElevaLocker")
Copy-IfExists "eleva-locker_pai" (Join-Path $OrigParent "eleva-locker") (Join-Path $Dest "eleva-locker")

$usersRoot = Join-Path $OrigParent "Users"
$skip = @("Public", "Default", "Default User", "All Users", "desktop.ini")
if (Test-Path -LiteralPath $usersRoot) {
    Get-ChildItem -LiteralPath $usersRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        if ($skip -contains $_.Name) { return }
        $u = $_.FullName
        $name = $_.Name
        $base = Join-Path $Dest "Users_extract\$name"
        Copy-IfExists "Desktop_$name" (Join-Path $u "Desktop") (Join-Path $base "Desktop")
        Copy-IfExists "Documents_$name" (Join-Path $u "Documents") (Join-Path $base "Documents")
        Copy-IfExists "Downloads_$name" (Join-Path $u "Downloads") (Join-Path $base "Downloads")
        Copy-IfExists "Arduino_$name" (Join-Path $u "Documents\Arduino") (Join-Path $base "Arduino")
        Copy-IfExists "eleva-locker_$name" (Join-Path $u "eleva-locker") (Join-Path $base "eleva-locker")
        Copy-IfExists "ElevaLocker_$name" (Join-Path $u "ElevaLocker") (Join-Path $base "ElevaLocker")
        Copy-IfExists "cursor_$name" (Join-Path $u ".cursor") (Join-Path $base ".cursor")
    }
}

$config = Join-Path $OrigWin "System32\config"
if (Test-Path -LiteralPath (Join-Path $config "SOFTWARE")) {
    $hiveDst = Join-Path $Dest "config_hives"
    New-Item -ItemType Directory -Force -Path $hiveDst | Out-Null
    Write-Log "[OK] hives de registro"
    Copy-Item -LiteralPath (Join-Path $config "SOFTWARE") -Destination (Join-Path $hiveDst "SOFTWARE") -Force
    Copy-Item -LiteralPath (Join-Path $config "SYSTEM") -Destination (Join-Path $hiveDst "SYSTEM") -Force -ErrorAction SilentlyContinue
    Copy-Item -LiteralPath (Join-Path $config "SAM") -Destination (Join-Path $hiveDst "SAM") -Force -ErrorAction SilentlyContinue
}

Write-Log "Buscando elevalocker.db..."
$dbHits = Get-ChildItem -LiteralPath $OrigParent -Filter "elevalocker.db" -Recurse -ErrorAction SilentlyContinue
if ($dbHits) {
    $dbDst = Join-Path $Dest "databases"
    New-Item -ItemType Directory -Force -Path $dbDst | Out-Null
    foreach ($db in $dbHits) {
        Write-Log "[DB] $($db.FullName)"
        Copy-Item -LiteralPath $db.FullName -Destination (Join-Path $dbDst $db.Name) -Force
    }
}

@"
Recuperacao $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Origem=$OrigWin
Destino=$Dest

$($LogLines -join "`r`n")
"@ | Set-Content -LiteralPath $LogPath -Encoding UTF8

Write-Host ""
Write-Host "============================================================"
Write-Host " Concluido. Veja: $Dest"
Write-Host " Log: $LogPath"
Write-Host "============================================================"
Write-Host ""
Write-Host "Proximo:"
Write-Host " 1. Abra $Dest\Users_extract"
Write-Host " 2. Se tiver databases\elevalocker.db, use no ElevaLocker"
Write-Host " 3. NAO substitua C:\Windows pela pasta antiga"
exit 0
