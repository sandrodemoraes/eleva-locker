# Tarefa agendada: inicia apos login (util com PIN do Windows)
$ErrorActionPreference = "Stop"

$oficial = "C:\ElevaLocker"
if (Test-Path (Join-Path $oficial "app.py")) {
    $workdir = $oficial
} else {
    $workdir = Split-Path $PSScriptRoot -Parent
}

$bat = Join-Path $workdir "iniciar_elevalocker.bat"
if (-not (Test-Path $bat)) {
    $bat = Join-Path $workdir "tools\iniciar_servidor.bat"
}
if (-not (Test-Path $bat)) {
    Write-Host "ERRO: launcher nao encontrado em $workdir"
    exit 1
}

$taskName = "ELEVA LOCKER - Iniciar"
$cmd = $env:ComSpec
$taskArgs = "/k `"$bat`""

$action = New-ScheduledTaskAction -Execute $cmd -Argument $taskArgs -WorkingDirectory $workdir
$triggerLogon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$triggerLogon.Delay = "PT45S"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $triggerLogon -Settings $settings -Description "ELEVA LOCKER: py app.py apos login" -Force | Out-Null

Write-Host ""
Write-Host "OK  Tarefa: $taskName"
Write-Host "    Ao logon + 45s: cmd /k `"$bat`""
Write-Host "    Util se o PC pede PIN ao ligar."
