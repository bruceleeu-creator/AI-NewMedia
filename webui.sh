# If you could not download the model from the official site, you can use the mirror site.
# Just remove the comment of the following line .
# 如果你无法从官方网站下载模型，你可以使用镜像网站。
# 只需要移除下面一行的注释即可。

# export HF_ENDPOINT=https://hf-mirror.com

# --------------------------------------------------------------------------
#  Disable writing .pyc / __pycache__ files to avoid sandbox or permission
#  errors in restricted environments.
# --------------------------------------------------------------------------
export PYTHONDONTWRITEBYTECODE=1

# --------------------------------------------------------------------------
#  imageio_ffmpeg bundles a portable ffmpeg binary.  Set the explicit path
#  so that sandboxed or restricted environments can still discover it.
# --------------------------------------------------------------------------
BUNDLED_FFMPEG="$(pwd)/.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.1"
if [ -f "$BUNDLED_FFMPEG" ]; then
    export IMAGEIO_FFMPEG_EXE="$BUNDLED_FFMPEG"
    echo "***** Using bundled ffmpeg: $IMAGEIO_FFMPEG_EXE *****"
else
    echo "***** WARNING: Bundled ffmpeg binary not found. Set IMAGEIO_FFMPEG_EXE manually if needed. *****"
fi

streamlit run ./webui/Main.py --browser.serverAddress="0.0.0.0" --server.enableCORS=True --browser.gatherUsageStats=False
