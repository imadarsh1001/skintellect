@echo off
setlocal
set "PYTHONDONTWRITEBYTECODE=1"
cd /d "%~dp0"
set "PYTHONPATH=%CD%\src;%PYTHONPATH%"
if exist ".runtime" set "PYTHONPATH=%CD%\.runtime;%PYTHONPATH%"

set "PYTHON=python"
if exist ".venv\Scripts\python.exe" (
    set "PYTHON=%CD%\.venv\Scripts\python.exe"
)

echo Prepared study: http://127.0.0.1:8000/study
echo Preparation progress: http://127.0.0.1:8000/progress
echo Product research: http://127.0.0.1:8000/research
"%PYTHON%" -m uvicorn skintellect.api.app:app --host 127.0.0.1 --port 8000 --reload

pause
