# ELEVA LOCKER - Remover inicio automatico com Windows
$startup = [Environment]::GetFolderPath("Startup")
$caminho = Join-Path $startup "ElevaLocker.lnk"

if (Test-Path $caminho) {
    Remove-Item -Force $caminho
    Write-Host "Removido: $caminho"
} else {
    Write-Host "Nenhum atalho de inicio automatico encontrado."
}
