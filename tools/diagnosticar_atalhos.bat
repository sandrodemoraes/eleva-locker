@echo off
title ELEVA LOCKER - Diagnosticar atalhos
cd /d "%~dp0.."

echo Pasta projeto: %CD%
echo.

echo === Python ===
call "%~dp0encontrar_python.bat"
if defined ELEVA_PYTHON (echo OK  %ELEVA_PYTHON%) else (echo FALTA Python no PATH)
echo.

echo === Arquivos launcher ===
if exist "%CD%\iniciar_elevalocker.bat" (echo OK  iniciar_elevalocker.bat) else (echo FALTA iniciar_elevalocker.bat)
if exist "%CD%\tools\iniciar_servidor.bat" (echo OK  tools\iniciar_servidor.bat) else (echo FALTA tools\iniciar_servidor.bat)
echo.

echo === Atalho Area de Trabalho ===
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESK=%%D\ELEVA LOCKER.lnk"
if exist "%DESK%" (
    echo Existe: %DESK%
    powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%DESK%'); Write-Host '  Target:' $s.TargetPath; Write-Host '  Args:' $s.Arguments; Write-Host '  Dir:' $s.WorkingDirectory"
) else (
    echo FALTA — rode tools\instalar_inicio_windows.bat
)

echo.
echo === Atalho Iniciar Windows ===
set "ST=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ELEVA LOCKER - Iniciar.lnk"
if exist "%ST%" (
    echo Existe: %ST%
    powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%ST%'); Write-Host '  Target:' $s.TargetPath; Write-Host '  Args:' $s.Arguments; Write-Host '  Dir:' $s.WorkingDirectory"
) else (
    echo FALTA — rode tools\instalar_inicio_windows.bat
)

echo.
echo === Tarefa agendada ===
schtasks /Query /TN "ELEVA LOCKER - Iniciar" /FO LIST /V 2>nul | findstr /i "TaskName Status Task To Run"
if errorlevel 1 echo FALTA tarefa agendada

echo.
echo === Ultimo log ===
if exist logs\*.log (
    for /f %%F in ('dir /b /o-d logs\*.log 2^>nul') do (
        echo --- logs\%%F (ultimas 5 linhas) ---
        powershell -NoProfile -Command "Get-Content 'logs\%%F' -Tail 5"
        goto :logdone
    )
) else (
    echo Nenhum log ainda — servidor nunca iniciou pelo atalho.
)
:logdone

echo.
pause
