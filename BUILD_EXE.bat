@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "SPEC_FILE=%PROJECT_DIR%HAOS_GAME_DECK.spec"

if not exist "%SPEC_FILE%" (
  echo.
  echo Missing build config:
  echo "%SPEC_FILE%"
  echo.
  echo Keep BUILD_EXE.bat and HAOS_GAME_DECK.spec in the project root.
  pause
  exit /b 1
)

pushd "%PROJECT_DIR%"
taskkill /F /T /IM HAOS_GAME_DECK.exe >nul 2>nul
timeout /T 2 /NOBREAK >nul
if exist "%PROJECT_DIR%dist\HAOS_GAME_DECK.exe" (
  del /F /Q "%PROJECT_DIR%dist\HAOS_GAME_DECK.exe" >nul 2>nul
)
if exist "%PROJECT_DIR%dist\HAOS_GAME_DECK.exe" (
  popd
  echo.
  echo Cannot replace the old EXE because it is still in use.
  echo Close HAOS_GAME_DECK.exe and run this build script again.
  pause
  exit /b 1
)
python -m PyInstaller --noconfirm --clean "%SPEC_FILE%"
if errorlevel 1 (
  popd
  echo.
  echo Build failed.
  pause
  exit /b 1
)
popd
echo.
echo Build complete:
echo "%PROJECT_DIR%dist\HAOS_GAME_DECK.exe"
pause
