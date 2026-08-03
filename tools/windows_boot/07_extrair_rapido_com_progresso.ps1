# Extracao RAPIDA com progresso (robocopy visivel).
# Copia so o essencial; nao trava sem feedback.
param(
    [Parameter(Mandatory = $false)]
    [string]$OrigParent = "D:\backup pc fabio",

    [Parameter(Mandatory = $false)]
    [string]$Dest = "D:\Recuperado_Windows_Antigo",

    [Parameter(Mandatory = $false)]
    [switch]$IncluirAppData
)

$ErrorActionPreference = "Continue"

Write-Host "============================================================"
Write-Host " Extracao RAPIDA com progresso"
Write-Host "============================================================"
Write-Host "Origem pai: $OrigParent"
Write-Host "Destino:    $Dest"
Write-Host ""

if (-not (Test-Path -LiteralPath $OrigParent)) {
    Write-Host "ERRO: pasta nao existe: $OrigParent"
    exit 1
}

New-Item -ItemType Directory -Force -Path $Dest | Out-Null
$LogPath = Join-Path $Dest "RECUPERACAO_RAPIDA_LOG.txt"
$log = @()

function Invoke-Robo([string]$Label, [string]$Src, [string]$Dst, [string[]]$ExtraArgs = @()) {
    if (-not (Test-Path -LiteralPath $Src)) {
        $msg = "[  ] ausente: $Label ($Src)"
        Write-Host $msg
        $script:log += $msg
        return
    }
    Write-Host ""
    Write-Host ">>> $Label"
    Write-Host "    $Src"
    Write-Host "    -> $Dst"
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    $args = @($Src, $Dst, "/E", "/COPY:DAT", "/R:1", "/W:1", "/MT:8", "/BYTES", "/ETA") + $ExtraArgs
    & robocopy @args
    $rc = $LASTEXITCODE
    # robocopy: 0-7 = sucesso parcial/ok; >=8 = falha
    if ($rc -ge 8) {
        $msg = "[AVISO] $Label codigo robocopy=$rc"
    } else {
        $msg = "[OK] $Label codigo=$rc"
    }
    Write-Host $msg
    $script:log += $msg
}

$users = Join-Path $OrigParent "Users"
$skipUsers = @("Public", "Default", "Default User", "All Users")

# Pastas tipicas grandes que atrasam (excluidas por padrao do AppData)
$xdAppData = @("AppData", "Application Data", "Cookies", "Local Settings", "Ntoskrnl*", "Temp")

if (Test-Path -LiteralPath $users) {
    Get-ChildItem -LiteralPath $users -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        if ($skipUsers -contains $_.Name) { return }
        $name = $_.Name
        $u = $_.FullName
        $base = Join-Path $Dest "Users_extract\$name"

        Invoke-Robo "Desktop_$name" (Join-Path $u "Desktop") (Join-Path $base "Desktop")
        Invoke-Robo "Documents_$name" (Join-Path $u "Documents") (Join-Path $base "Documents")
        Invoke-Robo "Downloads_$name" (Join-Path $u "Downloads") (Join-Path $base "Downloads")
        Invoke-Robo "Arduino_$name" (Join-Path $u "Documents\Arduino") (Join-Path $base "Arduino")
        Invoke-Robo "eleva-locker_$name" (Join-Path $u "eleva-locker") (Join-Path $base "eleva-locker")
        Invoke-Robo "ElevaLocker_$name" (Join-Path $u "ElevaLocker") (Join-Path $base "ElevaLocker")

        if ($IncluirAppData) {
            Invoke-Robo "AppData_Roaming_$name" (Join-Path $u "AppData\Roaming") (Join-Path $base "AppData\Roaming")
        }
    }
} else {
    Write-Host "[  ] Sem pasta Users em $OrigParent"
}

Invoke-Robo "ElevaLocker_raiz" (Join-Path $OrigParent "ElevaLocker") (Join-Path $Dest "ElevaLocker")
Invoke-Robo "eleva-locker_raiz" (Join-Path $OrigParent "eleva-locker") (Join-Path $Dest "eleva-locker")

Write-Host ""
Write-Host "Buscando elevalocker.db (pode demorar um pouco)..."
$dbDst = Join-Path $Dest "databases"
New-Item -ItemType Directory -Force -Path $dbDst | Out-Null
Get-ChildItem -LiteralPath $OrigParent -Filter "elevalocker.db" -Recurse -ErrorAction SilentlyContinue |
    Select-Object -First 20 |
    ForEach-Object {
        Write-Host "[DB] $($_.FullName)"
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $dbDst $_.Name) -Force
        $script:log += "[DB] $($_.FullName)"
    }

@"
Recuperacao rapida $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
OrigParent=$OrigParent
Dest=$Dest

$($log -join "`r`n")
"@ | Set-Content -LiteralPath $LogPath -Encoding UTF8

Write-Host ""
Write-Host "============================================================"
Write-Host " Concluido."
Write-Host " Destino: $Dest"
Write-Host " Log:     $LogPath"
Write-Host "============================================================"
