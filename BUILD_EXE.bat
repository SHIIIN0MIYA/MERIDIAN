@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "SPEC_FILE=%PROJECT_DIR%MERIDIAN.spec"

if not exist "%SPEC_FILE%" (
  echo.
  echo Missing build config:
  echo "%SPEC_FILE%"
  echo.
  echo Keep BUILD_EXE.bat and MERIDIAN.spec in the project root.
  pause
  exit /b 1
)

pushd "%PROJECT_DIR%"
taskkill /F /T /IM MERIDIAN.exe >nul 2>nul
timeout /T 2 /NOBREAK >nul
if exist "%PROJECT_DIR%dist\MERIDIAN.exe" (
  del /F /Q "%PROJECT_DIR%dist\MERIDIAN.exe" >nul 2>nul
)
if exist "%PROJECT_DIR%dist\MERIDIAN.exe" (
  popd
  echo.
  echo Cannot replace the old EXE because it is still in use.
  echo Close MERIDIAN.exe and run this build script again.
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
echo "%PROJECT_DIR%dist\MERIDIAN.exe"
pause
