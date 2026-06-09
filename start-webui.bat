@echo off
cd /d "%~dp0"

where uv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    uv run python scripts\start_webui.py %*
    exit /b %ERRORLEVEL%
)

python scripts\start_webui.py %*
exit /b %ERRORLEVEL%
