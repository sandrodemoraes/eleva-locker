@echo off
setlocal EnableDelayedExpansion
REM Localiza Python — funciona no CMD manual e no Iniciar do Windows (PATH reduzido)
set "PY="

where py >nul 2>&1 && set "PY=py" && goto :fim
where python >nul 2>&1 && set "PY=python" && goto :fim
where python3 >nul 2>&1 && set "PY=python3" && goto :fim

for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%ProgramFiles%\Python314\python.exe"
    "%ProgramFiles%\Python313\python.exe"
    "%ProgramFiles%\Python312\python.exe"
    "%ProgramFiles%\Python311\python.exe"
) do (
    if exist %%P set "PY=%%P" && goto :fim
)

for /d %%D in ("%LOCALAPPDATA%\Python\pythoncore-*") do (
    if exist "%%D\python.exe" set "PY=%%D\python.exe" && goto :fim
)

for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python3*") do (
    if exist "%%D\python.exe" set "PY=%%D\python.exe" && goto :fim
)

:fim
endlocal & set "ELEVA_PYTHON=%PY%"
exit /b 0
