#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

if command -v uv >/dev/null 2>&1; then
  exec uv run python scripts/start_webui.py "$@"
fi

exec python3 scripts/start_webui.py "$@"
