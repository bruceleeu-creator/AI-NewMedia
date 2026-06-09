from __future__ import annotations

from webui.runtime_check import mask_secret


def recommended_source_for_mode(mode: str) -> str:
    mode = (mode or "").lower()
    if mode == "online":
        return "pexels"
    return "local"


def mode_for_video_source(video_source: str) -> str:
    video_source = (video_source or "").lower()
    if video_source in {"pexels", "pixabay"}:
        return "online"
    return "local"


def source_for_mode_change(previous_mode: str | None, current_mode: str) -> str | None:
    current_mode = (current_mode or "local").lower()
    previous_mode = (previous_mode or "").lower()
    if previous_mode == current_mode:
        return None
    return recommended_source_for_mode(current_mode)


def mask_key_list(keys: list[str]) -> list[str]:
    return [mask_secret(key) for key in keys if key]
