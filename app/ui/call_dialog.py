import time
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from ..utils.avatars import get_avatar


class IncomingCallDialog(QDialog):
    """Popup when someone calls your PC."""

    def __init__(self, caller_name: str, caller_ip: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Incoming Voice Call — LAN Messenger")
        self.setFixedSize(360, 240)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | (self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        lbl_icon = QLabel("📞")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 36px;")
        layout.addWidget(lbl_icon)

        lbl_name = QLabel(f"Incoming Voice Call from<br><b>{caller_name}</b>")
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_name.setStyleSheet("font-size: 15px; color: #e9edef;")
        layout.addWidget(lbl_name)

        lbl_ip = QLabel(f"LAN IP: {caller_ip}")
        lbl_ip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ip.setStyleSheet("font-size: 11px; color: #8696a0;")
        layout.addWidget(lbl_ip)

        btn_row = QHBoxLayout()
        btn_accept = QPushButton("Accept 📞")
        btn_accept.setStyleSheet(
            "background-color: #00a884; color: #111b21; font-weight: bold; border-radius: 8px; padding: 10px;"
        )
        btn_accept.clicked.connect(self.accept)

        btn_decline = QPushButton("Decline ❌")
        btn_decline.setStyleSheet(
            "background-color: #ef5350; color: #ffffff; font-weight: bold; border-radius: 8px; padding: 10px;"
        )
        btn_decline.clicked.connect(self.reject)

        btn_row.addWidget(btn_decline)
        btn_row.addWidget(btn_accept)
        layout.addLayout(btn_row)


class ActiveCallDialog(QDialog):
    """Active in-call dialog with live timer, mute, and hangup."""

    sig_hangup = pyqtSignal()
    sig_toggle_mute = pyqtSignal(bool)

    def __init__(self, peer_name: str, avatar_id: str = "gamer", parent=None):
        super().__init__(parent)
        self.peer_name = peer_name
        self.setWindowTitle("Voice Call — LAN Messenger")
        self.setFixedSize(340, 320)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.start_time = time.time()
        self.is_muted = False

        self.init_ui(avatar_id)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._update_timer)
        self.timer.start()

    def init_ui(self, avatar_id: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        av = get_avatar(avatar_id)
        lbl_avatar = QLabel(av["icon"])
        lbl_avatar.setFixedSize(70, 70)
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_avatar.setStyleSheet(
            f"background-color: {av['bg']}; color: #ffffff; border-radius: 35px; font-size: 32px;"
        )
        layout.addWidget(lbl_avatar, alignment=Qt.AlignmentFlag.AlignCenter)

        lbl_peer = QLabel(self.peer_name)
        lbl_peer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_peer.setStyleSheet("font-size: 16px; font-weight: bold; color: #e9edef;")
        layout.addWidget(lbl_peer)

        self.lbl_time = QLabel("00:00")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_time.setStyleSheet(
            "font-size: 14px; color: #00a884; font-weight: bold;"
        )
        layout.addWidget(self.lbl_time)

        lbl_tip = QLabel("LAN Voice Stream • Crystal HD • 0 Internet Cost")
        lbl_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_tip.setStyleSheet("font-size: 11px; color: #8696a0;")
        layout.addWidget(lbl_tip)

        layout.addStretch()

        btn_row = QHBoxLayout()

        self.btn_mute = QPushButton("🎙️ Mute")
        self.btn_mute.clicked.connect(self._toggle_mute)
        btn_row.addWidget(self.btn_mute)

        btn_end = QPushButton("🔴 End Call")
        btn_end.setStyleSheet(
            "background-color: #ef5350; color: #fff; font-weight: bold; border-radius: 8px; padding: 10px;"
        )
        btn_end.clicked.connect(self._on_hangup)
        btn_row.addWidget(btn_end)

        layout.addLayout(btn_row)

    def _update_timer(self):
        elapsed = int(time.time() - self.start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        self.lbl_time.setText(f"{mins:02d}:{secs:02d}")

    def _toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.btn_mute.setText("🔇 Unmute")
            self.btn_mute.setStyleSheet("background-color: #ef5350; color: #fff;")
        else:
            self.btn_mute.setText("🎙️ Mute")
            self.btn_mute.setStyleSheet("")
        self.sig_toggle_mute.emit(self.is_muted)

    def _on_hangup(self):
        self.timer.stop()
        self.sig_hangup.emit()
        self.accept()

