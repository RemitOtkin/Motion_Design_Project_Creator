"""Filesystem helpers: bundled resources, per-user app data, opening folders."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

APP_DIR_NAME = "ProjectCreator"


def app_root() -> Path:
    """Folder that holds `resources/` — the source tree, or PyInstaller's temp dir."""
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        return Path(bundle)
    return Path(__file__).resolve().parent.parent


def resource(*parts: str) -> Path:
    return app_root().joinpath("resources", *parts)


def app_data_dir() -> Path:
    """Per-user folder for settings (independent of where the app is launched from)."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    path = base / APP_DIR_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def open_in_file_manager(path: str | os.PathLike) -> bool:
    path = os.fspath(path)
    if not os.path.exists(path):
        return False
    try:
        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        return True
    except OSError:
        return False
