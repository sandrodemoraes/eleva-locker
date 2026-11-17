@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo  ========================================
echo   ELEVA CAM — stream (MediaMTX + YouTube)
echo  ========================================
echo.

if not exist ".env.stream" (
  echo [ERRO] Crie tools\eleva-cam\.env.stream a partir de env.stream.example
  echo   copy env.stream.example .env.stream
  exit /b 1
)

for /f "usebackq eol=# tokens=1,* delims==" %%A in (".env.stream") do (
  if not "%%A"=="" set "%%A=%%B"
)

if "%YOUTUBE_STREAM_KEY%"=="" (
  echo [ERRO] YOUTUBE_STREAM_KEY vazio no .env.stream
  exit /b 1
)

if "%CAMERA_RTSP_URL%"=="" (
  echo [ERRO] CAMERA_RTSP_URL vazio no .env.stream
  exit /b 1
)

if "%YOUTUBE_RTMP_URL%"=="" set "YOUTUBE_RTMP_URL=rtmp://a.rtmp.youtube.com/live2"

if not exist "mediamtx.yml" (
  if exist "mediamtx.yml.example" copy /y mediamtx.yml.example mediamtx.yml >nul
)

if not exist "mediamtx.yml" (
  echo [ERRO] mediamtx.yml nao encontrado
  exit /b 1
)

powershell -NoProfile -Command ^
  "$c = Get-Content -Raw 'mediamtx.yml'; $c = $c.Replace('CAMERA_RTSP_URL', $env:CAMERA_RTSP_URL); Set-Content -Path 'mediamtx.runtime.yml' -Value $c"

set "MTX="
if exist "mediamtx\mediamtx.exe" set "MTX=%cd%\mediamtx\mediamtx.exe"
if exist "mediamtx.exe" set "MTX=%cd%\mediamtx.exe"
where mediamtx >nul 2>&1 && for /f "delims=" %%P in ('where mediamtx') do set "MTX=%%P"

if "%MTX%"=="" (
  echo [ERRO] mediamtx.exe nao encontrado.
  echo Baixe em https://github.com/bluenviron/mediamtx/releases
  echo e extraia para tools\eleva-cam\mediamtx\
  exit /b 1
)

where ffmpeg >nul 2>&1
if errorlevel 1 (
  echo [ERRO] ffmpeg nao esta no PATH.
  echo Windows: https://www.gyan.dev/ffmpeg/builds/
  exit /b 1
)

echo  RTSP: %CAMERA_RTSP_URL%
echo  Destino: YouTube Live
echo.
echo  Depois: painel /cameras → cole o ID da live + status online
echo.

start "ElevaCam-MediaMTX" "%MTX%" mediamtx.runtime.yml
timeout /t 3 /nobreak >nul

ffmpeg -rtsp_transport tcp -i "%CAMERA_RTSP_URL%" ^
  -c:v libx264 -preset veryfast -tune zerolatency -b:v 2500k -maxrate 2500k -bufsize 5000k ^
  -g 60 -c:a aac -b:a 128k -f flv "%YOUTUBE_RTMP_URL%/%YOUTUBE_STREAM_KEY%"

echo.
echo Stream encerrado.
endlocal
