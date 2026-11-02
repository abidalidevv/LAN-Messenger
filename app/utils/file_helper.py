import os
import sys
import hashlib
import subprocess
from pathlib import Path


def format_size(size_bytes: int) -> str:
    """Formats bytes into human readable format (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def get_unique_filepath(target_dir: Path, filename: str) -> Path:
    """
    Prevents overwriting existing files by appending (1), (2), etc.
    Example: video.mp4 -> video (1).mp4
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    destination = target_dir / filename
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    counter = 1
    while destination.exists():
        destination = target_dir / f"{stem} ({counter}){suffix}"
        counter += 1
    return destination


def compute_file_sha256(filepath: str, chunk_size: int = 256 * 1024) -> str:
    """Computes SHA-256 hash in streaming chunks to maintain low memory usage."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_file_category(filename: str) -> str:
    """Classifies file type for UI icons and previews."""
    ext = Path(filename).suffix.lower()
    if ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico", ".svg"]:
        return "image"
    elif ext in [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"]:
        return "video"
    elif ext in [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"]:
        return "audio"
    elif ext in [".pdf"]:
        return "pdf"
    elif ext in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".iso"]:
        return "archive"
    elif ext in [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md"]:
        return "document"
    elif ext in [".exe", ".msi", ".bat", ".cmd", ".ps1"]:
        return "executable"
    return "file"


def open_file_default(filepath: str) -> bool:
    """Opens a file with its default Windows application."""
    path = Path(filepath).resolve()
    if not path.exists():
        return False
    try:
        if sys.platform == "win32":
            os.startfile(str(path))
        else:
            subprocess.Popen(["xdg-open", str(path)])
        return True
    except Exception as e:
        print(f"Error opening file {filepath}: {e}")
        return False


def show_in_file_manager(filepath: str) -> bool:
    """Opens Windows Explorer with the specific file selected/highlighted."""
    path = Path(filepath).resolve()
    if not path.exists():
        return False
    try:
        if sys.platform == "win32":
            subprocess.run(["explorer", f"/select,{str(path)}"], check=False)
        else:
            subprocess.Popen(["xdg-open", str(path.parent)])
        return True
    except Exception as e:
        print(f"Error showing in file manager {filepath}: {e}")
        return False

