@echo off
set CURRENT_DIR=%CD%
echo ***** Current directory: %CURRENT_DIR% *****
set PYTHONPATH=%CURRENT_DIR%

rem ---------------------------------------------------------------------------
rem  Disable writing .pyc / __pycache__ files to avoid sandbox or permission
rem  errors in restricted environments (Desktop, OneDrive, etc.).
rem ---------------------------------------------------------------------------
set PYTHONDONTWRITEBYTECODE=1

rem ---------------------------------------------------------------------------
rem  imageio_ffmpeg bundles a portable ffmpeg binary inside the virtual env.
rem  Set IMAGEIO_FFMPEG_EXE explicitly so that sandboxed or restricted
rem  environments can still find it.
rem ---------------------------------------------------------------------------
if exist "%CURRENT_DIR%\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe" (
    set IMAGEIO_FFMPEG_EXE=%CURRENT_DIR%\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe
    echo ***** Using bundled ffmpeg: %IMAGEIO_FFMPEG_EXE% *****
) else (
    echo ***** WARNING: Bundled ffmpeg binary not found. Set IMAGEIO_FFMPEG_EXE manually if needed. *****
)

rem set HF_ENDPOINT=https://hf-mirror.com
streamlit run .\webui\Main.py --browser.gatherUsageStats=False --server.enableCORS=True
