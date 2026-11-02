import webbrowser
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QApplication,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class AboutDialog(QDialog):
    """About dialog highlighting Abid Developer, GitHub repository, and Playit.gg remote hub link."""

    sig_connect_hub = pyqtSignal(str)

    DEVELOPER_NAME = "Abid Developer"
    GITHUB_PROFILE = "https://github.com/abidalidevv"
    GITHUB_REPO = "https://github.com/abidalidevv/LAN-Messenger"
    REMOTE_HUB = "shrimp-cigars.tun.ply.gg"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About LAN Messenger & Developer")
        self.setFixedSize(520, 560)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        # Header with Logo & Title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        icon_badge = QLabel("💬")
        icon_badge.setStyleSheet(
            "font-size: 40px; background-color: #202c33; border-radius: 12px; padding: 10px;"
        )
        icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon_badge)

        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        lbl_app = QLabel("LAN Messenger")
        lbl_app.setStyleSheet("font-size: 20px; font-weight: bold; color: #00a884;")

        lbl_ver = QLabel("Version 2.5 • High-Speed LAN & WAN Communication")
        lbl_ver.setStyleSheet("color: #8696a0; font-size: 12px;")

        title_box.addWidget(lbl_app)
        title_box.addWidget(lbl_ver)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Developer Info Box
        dev_card = QFrame()
        dev_card.setStyleSheet(
            "background-color: #202c33; border: 1px solid #2a3942; border-radius: 10px; padding: 14px;"
        )
        card_layout = QVBoxLayout(dev_card)
        card_layout.setSpacing(10)

        dev_title = QLabel("👨‍💻 Lead Developer")
        dev_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #53bdeb;")
        card_layout.addWidget(dev_title)

        dev_name = QLabel(f"<b>{self.DEVELOPER_NAME}</b> (@abidalidevv)")
        dev_name.setStyleSheet("font-size: 15px; color: #e9edef;")
        card_layout.addWidget(dev_name)

        dev_bio = QLabel(
            "Crafted with modern Python & PyQt6 for zero-cloud, 100% private, "
            "ultra-fast LAN & remote file transfers, voice calling, and live screen sharing."
        )
        dev_bio.setWordWrap(True)
        dev_bio.setStyleSheet("color: #8696a0; font-size: 12px; line-height: 1.4;")
        card_layout.addWidget(dev_bio)

        layout.addWidget(dev_card)

        # Official Remote Hub Card
        hub_card = QFrame()
        hub_card.setStyleSheet(
            "background-color: #111b21; border: 1px dashed #00a884; border-radius: 10px; padding: 14px;"
        )
        hub_layout = QVBoxLayout(hub_card)
        hub_layout.setSpacing(8)

        hub_lbl = QLabel("🌐 Official Remote Server / Hub:")
        hub_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #00a884;")
        hub_layout.addWidget(hub_lbl)

        hub_val = QLabel(f"<b>{self.REMOTE_HUB}</b>")
        hub_val.setStyleSheet(
            "font-size: 14px; color: #e9edef; background: #202c33; padding: 8px 12px; border-radius: 6px; font-family: Consolas, monospace;"
        )
        hub_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        hub_layout.addWidget(hub_val)

        hub_desc = QLabel(
            "Connect instantly to Abid Developer across the internet without configuring routers or port forwarding."
        )
        hub_desc.setWordWrap(True)
        hub_desc.setStyleSheet("color: #8696a0; font-size: 11px;")
        hub_layout.addWidget(hub_desc)

        hub_btn_row = QHBoxLayout()
        btn_copy_hub = QPushButton("📋 Copy Link")
        btn_copy_hub.clicked.connect(self._copy_hub_link)
        hub_btn_row.addWidget(btn_copy_hub)

        btn_connect_hub = QPushButton("⚡ Connect to Hub")
        btn_connect_hub.setObjectName("primaryAction")
        btn_connect_hub.clicked.connect(self._connect_to_hub)
        hub_btn_row.addWidget(btn_connect_hub)

        hub_layout.addLayout(hub_btn_row)
        layout.addWidget(hub_card)

        # Developer Links Buttons
        links_layout = QHBoxLayout()
        links_layout.setSpacing(10)

        btn_gh_profile = QPushButton("🌐 GitHub Profile")
        btn_gh_profile.setToolTip(self.GITHUB_PROFILE)
        btn_gh_profile.clicked.connect(lambda: webbrowser.open(self.GITHUB_PROFILE))
        links_layout.addWidget(btn_gh_profile)

        btn_gh_repo = QPushButton("⭐ Star Repository")
        btn_gh_repo.setToolTip(self.GITHUB_REPO)
        btn_gh_repo.clicked.connect(lambda: webbrowser.open(self.GITHUB_REPO))
        links_layout.addWidget(btn_gh_repo)

        layout.addLayout(links_layout)

        # Close button
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def _copy_hub_link(self):
        cb = QApplication.clipboard()
        if cb:
            cb.setText(self.REMOTE_HUB)
            QMessageBox.information(
                self,
                "Copied!",
                f"Copied remote link to clipboard:\n\n{self.REMOTE_HUB}\n\nPaste this in 'Connect IP' to connect instantly!",
            )

    def _connect_to_hub(self):
        self.sig_connect_hub.emit(self.REMOTE_HUB)
        self.accept()

