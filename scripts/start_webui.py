from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable

try:
    import toml
except ImportError:  # pragma: no cover - handled before normal app startup.
    toml = None


ROOT_DIR = Path(__file__).resolve().parent.parent


def ensure_project_root_on_path(root_dir: Path = ROOT_DIR) -> None:
    root_path = str(root_dir)
    if root_path not in sys.path:
        sys.path.insert(0, root_path)


ensure_project_root_on_path()


def find_available_port(
    start_port: int = 8501,
    host: str = "127.0.0.1",
    connect_ex: Callable[[tuple[str, int]], int] | None = None,
    max_attempts: int = 20,
) -> int:
    for offset in range(max_attempts):
        port = start_port + offset
        if connect_ex is not None:
            if connect_ex((host, port)) != 0:
                return port
            continue

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex((host, port)) != 0:
                return port
    raise RuntimeError(f"no available port found from {start_port}")


def prepare_config(root_dir: Path = ROOT_DIR) -> bool:
    config_path = root_dir / "config.toml"
    example_path = root_dir / "config.example.toml"
    if config_path.exists():
        return False
    if not example_path.exists():
        raise FileNotFoundError(f"missing {example_path}")
    shutil.copyfile(example_path, config_path)
    return True


def build_streamlit_command(
    root_dir: Path,
    port: int,
    uv_path: str | None,
    headless: bool = False,
) -> list[str]:
    base = [uv_path, "run"] if uv_path else [sys.executable, "-m"]
    headless_flag = f"--server.headless={str(headless).lower()}"
    if uv_path:
        return [
            *base,
            "streamlit",
            "run",
            "./webui/Main.py",
            headless_flag,
            f"--server.port={port}",
            "--browser.gatherUsageStats=false",
        ]
    return [
        *base,
        "streamlit",
        "run",
        "./webui/Main.py",
        headless_flag,
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]


def _load_config(root_dir: Path) -> dict:
    if toml is None:
        return {}
    config_path = root_dir / "config.toml"
    if not config_path.exists():
        return {}
    return toml.load(config_path)


def print_preflight(root_dir: Path) -> None:
    ensure_project_root_on_path(root_dir)
    from webui.runtime_check import build_preflight_report

    report = build_preflight_report(root_dir=root_dir, config_data=_load_config(root_dir))
    print("\nAI-NewMedia 启动预检")
    print("-" * 40)
    for check in report.checks:
        mark = {"ok": "OK", "warning": "WARN", "error": "ERR"}[check.status]
        print(f"[{mark}] {check.title}: {check.message}")
        if check.action:
            print(f"      -> {check.action}")
    print("-" * 40)
    print(report.summary)
    print("")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start AI-NewMedia WebUI.")
    parser.add_argument("--port", type=int, default=8501, help="Preferred Streamlit port.")
    parser.add_argument("--no-browser", action="store_true", help="Do not open the browser automatically.")
    args = parser.parse_args(argv)

    root_dir = ROOT_DIR
    ensure_project_root_on_path(root_dir)
    os.chdir(root_dir)
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

    created_config = prepare_config(root_dir)
    if created_config:
        print("已根据 config.example.toml 创建 config.toml。")

    print_preflight(root_dir)

    port = find_available_port(args.port)
    uv_path = shutil.which("uv")
    cmd = build_streamlit_command(
        root_dir=root_dir,
        port=port,
        uv_path=uv_path,
        headless=args.no_browser,
    )

    print(f"启动 WebUI: http://localhost:{port}")
    print("按 Ctrl+C 可停止服务。")
    try:
        return subprocess.call(cmd, cwd=root_dir)
    except KeyboardInterrupt:
        print("\nWebUI 已停止。")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
