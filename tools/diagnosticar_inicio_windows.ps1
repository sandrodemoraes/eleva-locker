# Mostra para onde apontam Startup, Desktop e Tarefa agendada
$ErrorActionPreference = "SilentlyContinue"

function Ler-Atalho($path) {
    if (-not (Test-Path $path)) { return $null }
    $ws = New-Object -ComObject WScript.Shell
    $s = $ws.CreateShortcut($path)
    return @{
        Target = $s.TargetPath
        Args   = $s.Arguments
        Work   = $s.WorkingDirectory
    }
}

$oficial = "C:\ElevaLocker"
$startup = Join-Path ([Environment]::GetFolderPath("Startup")) "ELEVA LOCKER - Iniciar.lnk"
$desktop = Join-Path ([Environment]::GetFolderPath("Desktop")) "ElevaLocker.lnk"
$taskName = "ELEVA LOCKER - Iniciar"

Write-Host ""
Write-Host "=== Diagnostico inicio Windows ==="
Write-Host "Pasta oficial: $oficial $(if (Test-Path $oficial) {'(OK)'} else {'(NAO EXISTE)'})"
Write-Host ""

$st = Ler-Atalho $startup
Write-Host "Startup (Inicializar):"
if ($st) {
    Write-Host "  cmd $($st.Args)"
    Write-Host "  Iniciar em: $($st.Work)"
    if ($st.Work -ne $oficial) {
        Write-Host "  AVISO: nao e C:\ElevaLocker — rode reparar_inicio_windows.bat" -ForegroundColor Yellow
    }
} else {
    Write-Host "  (nenhum atalho ELEVA LOCKER - Iniciar.lnk)"
}

Write-Host ""
$dt = Ler-Atalho $desktop
Write-Host "Area de trabalho (ElevaLocker.lnk):"
if ($dt) {
    Write-Host "  cmd $($dt.Args)"
    Write-Host "  Iniciar em: $($dt.Work)"
} else {
    Write-Host "  (atalho nao encontrado)"
}

Write-Host ""
$t = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
Write-Host "Tarefa agendada ($taskName):"
if ($t) {
    $a = $t.Actions[0]
    Write-Host "  $($a.Execute) $($a.Arguments)"
    Write-Host "  Iniciar em: $($a.WorkingDirectory)"
    if ($a.WorkingDirectory -ne $oficial) {
        Write-Host "  AVISO: nao e C:\ElevaLocker" -ForegroundColor Yellow
    }
} else {
    Write-Host "  (nao instalada — opcional com PIN)"
}

Write-Host ""
