import os
import sys
import subprocess
from pathlib import Path

# Ensure UTF-8 console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

print("=" * 65)
print("[PyInstaller] Building Standalone LANMessenger.exe for Windows 10/11")
print("=" * 65)

icon_path = BASE_DIR / "assets" / "app_icon.ico"
entry_point = BASE_DIR / "LANMessenger.py"
assets_arg = f"{BASE_DIR / 'assets'}{os.pathsep}assets"

cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--onefile",  # Single portable .exe file
    "--windowed",  # No black cmd console popup
    f"--icon={icon_path}",
    f"--add-data={assets_arg}",
    "--name=LANMessenger",
    "--clean",
    str(entry_point),
]

print(f"Running command:\n{' '.join(cmd)}\n")
subprocess.run(cmd, check=True)

print("\n" + "=" * 65)
print("[SUCCESS] Build Complete! Executable is ready in dist/LANMessenger/")
print("=" * 65)
