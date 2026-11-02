import json
import time
from typing import Dict, List, Any
from .paths import get_appdata_dir


class MessageHistory:
    """Persistent chat history saved to appdata JSON."""

    def __init__(self):
        self.history_file = get_appdata_dir() / "chat_history.json"
        self._history: Dict[str, List[Dict[str, Any]]] = {}  # peer_ip -> list of msgs
        self.load()

    def load(self):
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
            except Exception as e:
                print(f"Error loading chat history: {e}")
                self._history = {}

    def save(self):
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2)
        except Exception as e:
            print(f"Error saving chat history: {e}")

    def add_message(
        self,
        peer_ip: str,
        sender: str,
        text: str,
        is_outgoing: bool,
        msg_type: str = "text",
        file_info: Dict[str, Any] = None,
    ):
        """Adds a message to the peer's history."""
        if peer_ip not in self._history:
            self._history[peer_ip] = []

        entry = {
            "sender": sender,
            "text": text,
            "timestamp": time.time(),
            "is_outgoing": is_outgoing,
            "type": msg_type,
            "file_info": file_info or {},
        }
        self._history[peer_ip].append(entry)
        self.save()

    def get_messages(self, peer_ip: str) -> List[Dict[str, Any]]:
        return self._history.get(peer_ip, [])

    def clear_history(self, peer_ip: str):
        if peer_ip in self._history:
            self._history[peer_ip] = []
            self.save()


# Global singleton instance
history = MessageHistory()

