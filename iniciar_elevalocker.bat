@echo off
REM Launcher oficial — atalho desktop + Iniciar com Windows
set "OFICIAL=C:\ElevaLocker"
if exist "%OFICIAL%\tools\iniciar_servidor.bat" (
    if /i not "%~dp0"=="%OFICIAL%\" (
        call "%OFICIAL%\tools\iniciar_servidor.bat"
        exit /b %ERRORLEVEL%
    )
)
cd /d "%~dp0"
call "%~dp0tools\iniciar_servidor.bat"
