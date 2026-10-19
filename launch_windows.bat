@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  set "PY=py -3"
) else (
  set "PY=python"
)
if not exist ".venv\Scripts\python.exe" (
  echo Setting up the CyberShield Python environment...
  %PY% -m venv .venv
  if errorlevel 1 goto :failed
)
call .venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :failed
.venv\Scripts\python.exe -m streamlit run app.py
exit /b %ERRORLEVEL%
:failed
echo Setup failed. Check your Python installation and internet connection.
pause
exit /b 1
