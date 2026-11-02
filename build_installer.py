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
print("[PyInstaller] Building Standalone LANMessenger_Setup.exe")
print("=" * 65)

icon_path = BASE_DIR / "assets" / "app_icon.ico"
entry_point = BASE_DIR / "installer.py"
assets_arg = f"{BASE_DIR / 'assets'}{os.pathsep}assets"

cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    f"--icon={icon_path}",
    f"--add-data={assets_arg}",
    "--name=LANMessenger_Setup",
    "--clean",
    str(entry_point),
]

print(f"Running command:\n{' '.join(cmd)}\n")
subprocess.run(cmd, check=True)

print("\n" + "=" * 65)
print("[SUCCESS] Setup Installer built! Output: dist/LANMessenger_Setup.exe")
print("=" * 65)

