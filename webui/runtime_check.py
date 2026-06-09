from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from shutil import which as shutil_which
from typing import Callable, Iterable


@dataclass(frozen=True)
class RuntimeCheck:
    key: str
    title: str
    status: str
    message: str
    action: str = ""


@dataclass(frozen=True)
class PreflightReport:
    checks: list[RuntimeCheck]

    @property
    def has_blocker(self) -> bool:
        return any(check.status == "error" for check in self.checks)

    @property
    def summary(self) -> str:
        errors = sum(1 for check in self.checks if check.status == "error")
        warnings = sum(1 for check in self.checks if check.status == "warning")
        if errors:
            return f"{errors} 项需要先处理"
        if warnings:
            return f"{warnings} 项建议补充后体验更完整"
        return "基础环境已就绪"


def mask_secret(value: str) -> str:
    value = str(value or "")
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    if len(value) <= 8:
        return f"{value[:1]}****{value[-1:]}"
    return f"{value[:4]}****{value[-3:]}"


def _as_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, Iterable):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _provider_key(app_cfg: dict, provider: str) -> str:
    provider = (provider or "").lower()
    if provider == "ollama":
        return "local"
    return str(app_cfg.get(f"{provider}_api_key", "") or "")


def build_preflight_report(
    root_dir: Path,
    config_data: dict,
    which: Callable[[str], str | None] = shutil_which,
) -> PreflightReport:
    root_dir = Path(root_dir)
    app_cfg = config_data.get("app", {}) if config_data else {}
    ui_cfg = config_data.get("ui", {}) if config_data else {}

    checks: list[RuntimeCheck] = []

    config_path = root_dir / "config.toml"
    if config_path.exists():
        checks.append(
            RuntimeCheck(
                key="config_file",
                title="配置文件",
                status="ok",
                message="已找到 config.toml",
            )
        )
    else:
        checks.append(
            RuntimeCheck(
                key="config_file",
                title="配置文件",
                status="error",
                message="缺少 config.toml",
                action="复制 config.example.toml 为 config.toml 后再启动。",
            )
        )

    provider = str(app_cfg.get("llm_provider", "openai") or "openai").lower()
    provider_secret = _provider_key(app_cfg, provider)
    if provider_secret:
        checks.append(
            RuntimeCheck(
                key="llm",
                title="大模型",
                status="ok",
                message=f"{provider} 已配置",
            )
        )
    else:
        checks.append(
            RuntimeCheck(
                key="llm",
                title="大模型",
                status="warning",
                message=f"{provider} 还没有 API Key",
                action="如果要自动生成文案，请在基础设置里填写大模型 API Key；已有文案时可以先手动填写。",
            )
        )

    video_source = str(app_cfg.get("video_source", "local") or "local").lower()
    if video_source == "local":
        checks.append(
            RuntimeCheck(
                key="material_source",
                title="视频素材",
                status="ok",
                message="本地素材模式可直接上传图片或视频",
            )
        )
    elif video_source == "pixabay":
        keys = _as_list(app_cfg.get("pixabay_api_keys"))
        checks.append(
            RuntimeCheck(
                key="material_source",
                title="视频素材",
                status="ok" if keys else "warning",
                message="Pixabay Key 已配置" if keys else "Pixabay 在线素材需要 API Key",
                action="" if keys else "填写 Pixabay API Key，或切换到本地素材模式先跑通。",
            )
        )
    else:
        keys = _as_list(app_cfg.get("pexels_api_keys"))
        checks.append(
            RuntimeCheck(
                key="material_source",
                title="视频素材",
                status="ok" if keys else "warning",
                message="Pexels Key 已配置" if keys else "Pexels 在线素材需要 API Key",
                action="" if keys else "填写 Pexels API Key，或切换到本地素材模式先跑通。",
            )
        )

    tts_server = str(ui_cfg.get("tts_server", "azure-tts-v1") or "azure-tts-v1")
    if tts_server in {"azure-tts-v1", "azure-tts-v2"}:
        checks.append(
            RuntimeCheck(
                key="tts",
                title="语音合成",
                status="ok",
                message=f"{tts_server} 可作为默认 TTS",
            )
        )
    else:
        checks.append(
            RuntimeCheck(
                key="tts",
                title="语音合成",
                status="warning",
                message=f"{tts_server} 可能需要额外 API Key",
                action="如果试听失败，请检查对应 TTS 服务的 API Key。",
            )
        )

    ffmpeg_path = app_cfg.get("ffmpeg_path") or which("ffmpeg")
    checks.append(
        RuntimeCheck(
            key="ffmpeg",
            title="ffmpeg",
            status="ok" if ffmpeg_path else "warning",
            message="已检测到 ffmpeg" if ffmpeg_path else "未在系统 PATH 中检测到 ffmpeg",
            action="" if ffmpeg_path else "通常 imageio-ffmpeg 会兜底；如果合成失败，请安装 ffmpeg 或配置 ffmpeg_path。",
        )
    )

    imagemagick_path = app_cfg.get("imagemagick_path") or which("magick") or which("convert")
    checks.append(
        RuntimeCheck(
            key="imagemagick",
            title="ImageMagick",
            status="ok" if imagemagick_path else "warning",
            message="已检测到 ImageMagick" if imagemagick_path else "未检测到 ImageMagick",
            action="" if imagemagick_path else "字幕渲染异常时请安装 ImageMagick，macOS 可执行 brew install imagemagick。",
        )
    )

    return PreflightReport(checks=checks)
