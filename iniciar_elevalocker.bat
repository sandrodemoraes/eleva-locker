@echo off
REM Iniciar ELEVA LOCKER — atalho na raiz do projeto
REM Sempre usa C:\ElevaLocker se existir (evita Iniciar do Windows abrir clone azul)
set "OFICIAL=C:\ElevaLocker"
if exist "%OFICIAL%\iniciar_elevalocker.bat" (
    if /i not "%~dp0"=="%OFICIAL%\" (
        call "%OFICIAL%\iniciar_elevalocker.bat"
        exit /b %ERRORLEVEL%
    )
)
cd /d "%~dp0"
call "%~dp0tools\iniciar_tudo.bat"
