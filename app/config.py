import json
import os
import socket
from pathlib import Path
from typing import Dict, Any, List
from .utils.paths import get_appdata_dir, get_default_download_dir


class Config:
    def __init__(self):
        self.config_file = get_appdata_dir() / "config.json"
        self._data: Dict[str, Any] = {}
        self.load()

    def get_default_username(self) -> str:
        """Determines a friendly default username based on machine name."""
        user = os.environ.get("USERNAME", "")
        host = socket.gethostname()
        if user and user.lower() not in ["user", "administrator"]:
            return f"{user.capitalize()} ({host})"
        return host

    def load(self):
        default_config = {
            "username": self.get_default_username(),
            "email": "",
            "avatar_id": "gamer",
            "is_configured": False,
            "tcp_port": 9876,
            "udp_port": 9877,
            "download_dir": str(get_default_download_dir()),
            "saved_peers": ["192.168.100.8", "192.168.7.7"],
            "custom_subnets": ["192.168.100", "192.168.7"],
            "sound_enabled": True,
            "notifications_enabled": True,
            "minimize_to_tray": True,
            "theme": "dark",
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception as e:
                print(f"Error loading config.json: {e}")

        self._data = default_config
        self.save()

    def save(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    @property
    def username(self) -> str:
        return self._data.get("username", self.get_default_username())

    @username.setter
    def username(self, val: str):
        self._data["username"] = val.strip()
        self._data["is_configured"] = True
        self.save()

    @property
    def email(self) -> str:
        return self._data.get("email", "")

    @email.setter
    def email(self, val: str):
        self._data["email"] = val.strip()
        self.save()

    @property
    def avatar_id(self) -> str:
        return self._data.get("avatar_id", "gamer")

    @avatar_id.setter
    def avatar_id(self, val: str):
        self._data["avatar_id"] = val
        self.save()

    @property
    def is_configured(self) -> bool:
        return self._data.get("is_configured", False)

    @is_configured.setter
    def is_configured(self, val: bool):
        self._data["is_configured"] = val
        self.save()

    @property
    def tcp_port(self) -> int:
        return int(self._data.get("tcp_port", 9876))

    @property
    def udp_port(self) -> int:
        return int(self._data.get("udp_port", 9877))

    @property
    def download_dir(self) -> str:
        d = self._data.get("download_dir", str(get_default_download_dir()))
        Path(d).mkdir(parents=True, exist_ok=True)
        return d

    @download_dir.setter
    def download_dir(self, val: str):
        self._data["download_dir"] = val
        self.save()

    @property
    def saved_peers(self) -> List[str]:
        return self._data.get("saved_peers", [])

    def add_saved_peer(self, ip: str):
        peers = set(self._data.get("saved_peers", []))
        peers.add(ip.strip())
        self._data["saved_peers"] = list(peers)
        self.save()

    def remove_saved_peer(self, ip: str):
        peers = set(self._data.get("saved_peers", []))
        peers.discard(ip.strip())
        self._data["saved_peers"] = list(peers)
        self.save()

    @property
    def custom_subnets(self) -> List[str]:
        return self._data.get("custom_subnets", ["192.168.100", "192.168.7"])

    def add_custom_subnet(self, subnet_prefix: str):
        subnets = set(self._data.get("custom_subnets", []))
        subnets.add(subnet_prefix.strip())
        self._data["custom_subnets"] = list(subnets)
        self.save()

    @property
    def sound_enabled(self) -> bool:
        return self._data.get("sound_enabled", True)

    @sound_enabled.setter
    def sound_enabled(self, val: bool):
        self._data["sound_enabled"] = val
        self.save()

    @property
    def notifications_enabled(self) -> bool:
        return self._data.get("notifications_enabled", True)

    @notifications_enabled.setter
    def notifications_enabled(self, val: bool):
        self._data["notifications_enabled"] = val
        self.save()

    @property
    def minimize_to_tray(self) -> bool:
        return self._data.get("minimize_to_tray", True)

    @minimize_to_tray.setter
    def minimize_to_tray(self, val: bool):
        self._data["minimize_to_tray"] = val
        self.save()


# Global singleton instance
config = Config()

