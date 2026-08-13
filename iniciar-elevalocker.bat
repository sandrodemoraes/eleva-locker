@echo off
REM Alias (hifen) — mesmo que iniciar_elevalocker.bat
set "OFICIAL=C:\ElevaLocker"
if exist "%OFICIAL%\iniciar_elevalocker.bat" (
    if /i not "%~dp0"=="%OFICIAL%\" (
        call "%OFICIAL%\iniciar_elevalocker.bat"
        exit /b %ERRORLEVEL%
    )
)
cd /d "%~dp0"
call "%~dp0tools\iniciar_tudo.bat"
