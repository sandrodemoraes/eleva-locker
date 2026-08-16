# Tarefa agendada: inicia ELEVA LOCKER apos login (util com PIN)
$ErrorActionPreference = "Stop"

$oficial = "C:\ElevaLocker"
if (Test-Path $oficial) {
    $workdir = $oficial
} else {
    $workdir = Split-Path $PSScriptRoot -Parent
}

$bat = Join-Path $workdir "iniciar_elevalocker.bat"
if (-not (Test-Path $bat)) {
    $bat = Join-Path $workdir "tools\iniciar_tudo.bat"
}
if (-not (Test-Path $bat)) {
    Write-Host "ERRO: iniciar_elevalocker.bat nao encontrado em $workdir"
    exit 1
}

$taskName = "ELEVA LOCKER - Iniciar"
$cmd = $env:ComSpec
$taskArgs = "/c `"$bat`""

$action = New-ScheduledTaskAction -Execute $cmd -Argument $taskArgs -WorkingDirectory $workdir
$triggerLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$triggerLogon.Delay = "PT45S"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggerLogon -Settings $settings -Description "ELEVA LOCKER: app.py + Docker apos login Windows" -Force | Out-Null

Write-Host ""
Write-Host "OK - Tarefa criada: $taskName"
Write-Host "  Dispara: ao fazer logon (usuario: $env:USERNAME)"
Write-Host "  Atraso: 45 segundos (rede + Docker)"
Write-Host "  Comando: cmd /c $bat"
Write-Host "  Pasta:   $workdir"
Write-Host ""
Write-Host "Com PIN: apos reiniciar, digite PIN uma vez - o servidor sobe em ~45s."
Write-Host "Para subir SEM PIN: veja docs\INICIO_AUTOMATICO_PIN.md (netplwiz)"
Write-Host ""
Write-Host "Remover: tools\desinstalar_inicio_automatico_tarefa.bat"
