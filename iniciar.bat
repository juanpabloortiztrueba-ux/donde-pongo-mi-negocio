@echo off
REM Abre el tablero de "Donde pongo mi negocio" en Windows (doble clic).
REM   iniciar.bat            tablero local en http://127.0.0.1:8501
REM   iniciar.bat --red      tambien desde otras computadoras de tu red (cualquiera en tu Wi-Fi puede abrirlo)
REM   iniciar.bat --revisar  revision sin preguntas: uv sync, pruebas de la API, arranca en el 8599 y sale con 0 (ok) o 1
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"
set RED=0
set REVISAR=0
:args
if "%~1"=="" goto fin_args
if "%~1"=="--red" set RED=1
if "%~1"=="--revisar" set REVISAR=1
shift
goto args
:fin_args
set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"

where uv >nul 2>nul
if errorlevel 1 (
  echo Falta uv, el gestor de Python que usa este proyecto ^(https://docs.astral.sh/uv/^).
  if "%REVISAR%"=="1" ( echo REVISAR: falta uv & exit /b 1 )
  set /p R="Lo instalo ahora con el instalador oficial de PowerShell? [s/n] "
  if /i not "!R!"=="s" ( echo Sin uv no puedo seguir. Instalalo desde https://docs.astral.sh/uv/ & pause & exit /b 1 )
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
  where uv >nul 2>nul
  if errorlevel 1 ( echo No pude instalar uv. Cierra y vuelve a abrir esta ventana. & pause & exit /b 1 )
)

uv sync
if errorlevel 1 ( echo uv sync fallo. & (if not "%REVISAR%"=="1" pause) & exit /b 1 )

where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama no esta instalado: el tablero funciona en modo sin LLM ^(mapas, fichas, comparador y datos^). Para el chat, instalalo desde https://ollama.com
  goto fin_ollama
)
curl -s --max-time 2 http://127.0.0.1:11434/api/tags >nul 2>nul
if errorlevel 1 (
  echo Ollama esta instalado pero apagado. Abrelo ^(la app de Ollama^) si quieres usar el chat; si no, el tablero sigue en modo sin LLM.
  goto fin_ollama
)
for %%M in (qwen3:8b nomic-embed-text) do (
  ollama list 2>nul | findstr /b /c:"%%M" >nul
  if errorlevel 1 (
    echo Falta el modelo de Ollama %%M.
    if not "%REVISAR%"=="1" (
      set /p R="Lo descargo ahora con ollama pull? [s/n] "
      if /i "!R!"=="s" ollama pull %%M
    )
  )
)
:fin_ollama

if "%REVISAR%"=="1" goto revisar

set ARGS=
if "%RED%"=="1" set ARGS=--red
echo Arrancando el tablero ^(Ctrl+C para apagarlo^)...
uv run python -m app.servidor %ARGS%
goto :eof

:revisar
echo == pruebas de la API
uv run pytest -q tests/test_api_base.py tests/test_api_preguntar.py tests/test_api_explorar.py tests/test_api_contexto.py
if errorlevel 1 ( echo REVISAR: fallaron las pruebas & exit /b 1 )
echo == arrancando en el puerto 8599
start "tablero-revisar" /B uv run python -m app.servidor --puerto 8599 --sin-navegador
powershell -NoProfile -Command "$ok=$false; for($i=0;$i -lt 60;$i++){ try { Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8599/api/estado | Out-Null; $ok=$true; break } catch { Start-Sleep 1 } }; if(-not $ok){ exit 1 }; $h=(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8599/).Content; if($h -notmatch 'id=.root.'){ exit 2 }; $g=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8599/api/geo/agebs; if($g.RawContentLength -lt 100000){ exit 3 }"
set RES=%ERRORLEVEL%
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'app.servidor --puerto 8599' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
if not "%RES%"=="0" ( echo REVISAR: fallo ^(codigo %RES%^) & exit /b 1 )
echo REVISAR: todo bien
exit /b 0
