@echo off
cd /d "%~dp0"
echo == Veda AI setup ==
where py >nul 2>nul && (set PY=py) || (set PY=python)
%PY% -m pip install -r requirements.txt
if errorlevel 1 (echo Package install failed. Is Python installed and added to PATH? & pause & exit /b 1)
if not exist .env (copy .env.example .env >nul & echo Created .env - open it and paste your GROQ_API_KEY.)
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo ffmpeg not found. It is optional: only for unusual audio/video formats.
  winget install -e --id Gyan.FFmpeg
  where ffmpeg >nul 2>nul || %PY% -m pip install -r requirements-optional.txt
)
echo.
echo Done. Edit .env with Notepad, paste your key, then double-click start.bat
pause
