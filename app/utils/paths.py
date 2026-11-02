import os
import sys
from pathlib import Path


def get_base_dir() -> Path:
    """Returns the base directory of the application, handling PyInstaller packaging."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent.parent


def get_asset_path(filename: str) -> str:
    """Returns absolute path to an asset file in assets/."""
    base = get_base_dir()
    asset_file = base / "assets" / filename
    if asset_file.exists():
        return str(asset_file)
    # Fallback to local assets folder relative to current working directory
    local_asset = Path.cwd() / "assets" / filename
    return str(local_asset)


def get_appdata_dir() -> Path:
    """Returns a safe persistent app data directory for config and chat history."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        dir_path = Path(appdata) / "LANMessenger"
    else:
        dir_path = Path.home() / ".lanmessenger"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_default_download_dir() -> Path:
    """Returns the default download directory: Downloads/LANMessenger/."""
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        downloads = Path(user_profile) / "Downloads" / "LANMessenger"
    else:
        downloads = Path.home() / "Downloads" / "LANMessenger"
    downloads.mkdir(parents=True, exist_ok=True)
    return downloads

