@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Install Python 3.12 or newer and enable Add Python to PATH, then try again.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  python -m venv .venv
  if errorlevel 1 goto failed
)
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" setup_local.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" manage.py runserver
exit /b
:failed
echo.
echo Setup stopped. Read the error above. Your existing content has been kept.
pause
exit /b 1
