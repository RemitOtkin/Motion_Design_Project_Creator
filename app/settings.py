"""User settings, stored as JSON in the per-user app data folder."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .paths import app_data_dir


def _default_projects_dir() -> str:
    work = Path.home() / "Work"
    return str(work if work.is_dir() else Path.home())


DEFAULTS: dict[str, Any] = {
    "default_path": None,     # filled lazily so a missing ~/Work falls back to home
    "language": "en",
    "last_tools": [],
    "window_geometry": None,  # base64 string from QWidget.saveGeometry()
    "layout": None,           # edited folder structure; None = default
}


class Settings:
    def __init__(self, file: Path | None = None):
        self.file = file or app_data_dir() / "settings.json"
        self.data: dict[str, Any] = dict(DEFAULTS)
        try:
            loaded = json.loads(self.file.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.data.update({k: v for k, v in loaded.items() if k in DEFAULTS})
        except (OSError, ValueError):
            pass
        if not self.data["default_path"] or not Path(self.data["default_path"]).is_dir():
            self.data["default_path"] = _default_projects_dir()

    def get(self, key: str) -> Any:
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def save(self) -> None:
        try:
            self.file.parent.mkdir(parents=True, exist_ok=True)
            self.file.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass
