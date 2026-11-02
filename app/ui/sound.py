import sys
from ..config import config


def play_message_sound():
    """Plays a pleasant notification chime on new message."""
    if not config.sound_enabled:
        return
    try:
        if sys.platform == "win32":
            import winsound

            winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception:
        pass


def play_transfer_complete_sound():
    """Plays a confirmation chime on file transfer completion."""
    if not config.sound_enabled:
        return
    try:
        if sys.platform == "win32":
            import winsound

            winsound.MessageBeep(winsound.MB_OK)
    except Exception:
        pass

