# Tarefa agendada: backup diario ELEVA LOCKER (11:00)
param(
    [string]$Hora = "11:00"
)

$ErrorActionPreference = "Stop"

$oficial = "C:\ElevaLocker"
if (Test-Path $oficial) {
    $workdir = $oficial
} else {
    $workdir = Split-Path $PSScriptRoot -Parent
}

$bat = Join-Path $workdir "tools\backup_diario.bat"
if (-not (Test-Path $bat)) {
    Write-Host "ERRO: backup_diario.bat nao encontrado em $workdir\tools"
    exit 1
}

$taskName = "ELEVA LOCKER - Backup diario"
$cmd = $env:ComSpec
$taskArgs = "/c `"$bat`""

$action = New-ScheduledTaskAction -Execute $cmd -Argument $taskArgs -WorkingDirectory $workdir
$trigger = New-ScheduledTaskTrigger -Daily -At $Hora
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $taskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "ELEVA LOCKER: backup banco + .env + disco D: todo dia as $Hora" `
    -Force | Out-Null

Write-Host ""
Write-Host "OK - Tarefa criada: $taskName"
Write-Host "  Horario: todo dia as $Hora"
Write-Host "  Comando: cmd /c $bat"
Write-Host "  Pasta:   $workdir"
Write-Host "  Log:     $workdir\logs\backup_diario.log"
Write-Host ""
Write-Host "Se o PC estiver desligado as $Hora, roda na proxima vez que ligar (StartWhenAvailable)."
Write-Host ""
Write-Host "Remover: tools\desinstalar_backup_diario_tarefa.bat"
Write-Host "Testar agora: tools\backup_diario.bat"
