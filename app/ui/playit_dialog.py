import webbrowser
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QApplication,
    QMessageBox,
    QFrame,
)
from PyQt6.QtCore import Qt
from ..network.playit_manager import playit_mgr


class PlayitTunnelDialog(QDialog):
    """Dialog displaying the Playit.gg internet connection link."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🌐 Internet Link (Playit.gg) — Connect Worldwide")
        self.setFixedSize(520, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("🌐 1-Click Internet Link (Playit.gg)")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00a884;")
        layout.addWidget(title)

        desc = QLabel(
            "Share this permanent address with friends in other houses or cities.<br>"
            "They just type this address into <b>'➕ Connect IP'</b> in their LAN Messenger!"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8696a0; font-size: 13px;")
        layout.addWidget(desc)

        status_info = playit_mgr.get_status()

        card = QFrame()
        card.setStyleSheet(
            "background-color: #202c33; border-radius: 10px; padding: 14px;"
        )
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(10)

        lbl_state = QLabel(
            "🟢 <b>Status:</b> Playit Service is Active & Ready"
            if status_info.get("running")
            else "⚪ <b>Status:</b> Service Initializing"
        )
        lbl_state.setStyleSheet("font-size: 13px; color: #e9edef;")
        c_layout.addWidget(lbl_state)

        # Address Box
        addr_box = QHBoxLayout()
        self.addr_input = QLineEdit()
        self.addr_input.setPlaceholderText(
            "e.g. your-name.ply.gg:12345 (From Playit Dashboard)"
        )
        self.addr_input.setText(self._load_saved_link())

        btn_copy = QPushButton("Copy Address")
        btn_copy.setObjectName("primaryAction")
        btn_copy.clicked.connect(self._copy_address)

        addr_box.addWidget(self.addr_input, 1)
        addr_box.addWidget(btn_copy)
        c_layout.addLayout(addr_box)

        layout.addWidget(card)

        # Instructions / Buttons
        btn_row = QHBoxLayout()
        btn_hub = QPushButton("⚡ Insert Abid Developer Hub")
        btn_hub.clicked.connect(lambda: self.addr_input.setText("shrimp-cigars.tun.ply.gg"))
        btn_row.addWidget(btn_hub)

        btn_dash = QPushButton("🌐 Open Playit Dashboard (View Tunnels)")
        btn_dash.clicked.connect(
            lambda: webbrowser.open("https://playit.gg/manage")
        )
        btn_row.addWidget(btn_dash)

        layout.addLayout(btn_row)

        notes = QLabel(
            "<b>How your friend connects:</b><br>"
            "1. Friend downloads <code>LANMessenger.exe</code>.<br>"
            "2. Friend clicks <b>'➕ Connect IP'</b>.<br>"
            "3. Friend pastes your Playit address and clicks Connect!<br>"
            "<i>(Zero accounts needed for your friend!)</i>"
        )
        notes.setWordWrap(True)
        notes.setStyleSheet(
            "color: #8696a0; font-size: 12px; background:#111b21; padding:10px; border-radius:6px;"
        )
        layout.addWidget(notes)

        layout.addStretch()

        btn_save = QPushButton("Save & Close")
        btn_save.clicked.connect(self._save_and_close)
        layout.addWidget(btn_save)

    def _load_saved_link(self) -> str:
        # Load from config or temp
        return getattr(self, "_saved_playit_link", "")

    def _copy_address(self):
        text = self.addr_input.text().strip()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(
                self,
                "Address Copied",
                f"Playit Address copied to clipboard:\n{text}\n\nSend this address to your friend!",
            )

    def _save_and_close(self):
        self._saved_playit_link = self.addr_input.text().strip()
        self.accept()

