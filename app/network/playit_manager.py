import os
import subprocess
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any
from ..utils.paths import get_base_dir


class PlayitManager:
    """Manages local playit.gg tunnel binary for instant internet link sharing."""

    def __init__(self):
        self.bin_dir = get_base_dir() / "bin"
        self.exe_path = self.bin_dir / "playit.exe"
        self.playitd_path = self.bin_dir / "playitd.exe"

    def is_available(self) -> bool:
        return self.exe_path.exists()

    def get_status(self) -> Dict[str, Any]:
        """Queries the status of the local playit service."""
        if not self.is_available():
            return {"installed": False, "status": "not_installed"}

        try:
            res = subprocess.run(
                [str(self.exe_path), "status"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            out = res.stdout + res.stderr
            is_running = "PID:" in out
            is_configured = "Secret configured: true" in out

            return {
                "installed": True,
                "running": is_running,
                "configured": is_configured,
                "raw": out,
            }
        except Exception as e:
            return {"installed": True, "running": False, "error": str(e)}

    def get_claim_url(self) -> Optional[str]:
        """Runs claim generate/url or setup to retrieve an activation URL."""
        if not self.is_available():
            return None
        try:
            res = subprocess.run(
                [str(self.exe_path), "claim", "url"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            match = re.search(r"https://playit\.gg/claim/[a-zA-Z0-9]+", res.stdout)
            if match:
                return match.group(0)
        except Exception:
            pass
        return None


# Global singleton instance
playit_mgr = PlayitManager()

